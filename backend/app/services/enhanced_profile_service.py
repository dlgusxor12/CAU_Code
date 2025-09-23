"""
Enhanced Profile Integration Service for CAU Code.
Handles automatic profile synchronization and data caching for solved.ac profiles.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.auth import User
from app.clients.solvedac_client import SolvedACClient
from app.core.exceptions import UserNotFoundError, SolvedACAPIError
from app.core.background_tasks import background_task_queue, TaskPriority

logger = logging.getLogger(__name__)


class EnhancedProfileService:
    """
    향상된 프로필 통합 서비스
    - solved.ac 프로필 데이터 자동 동기화
    - 캐싱 및 성능 최적화
    - 백그라운드 프로필 업데이트
    """

    def __init__(self):
        self.solvedac_client = SolvedACClient()
        self.sync_interval_hours = 6  # 6시간마다 프로필 동기화
        self.cache_duration_hours = 24  # 24시간 캐시 유지

    async def sync_user_profile(
        self,
        db: AsyncSession,
        user: User,
        force_sync: bool = False
    ) -> Dict:
        """
        사용자 프로필 동기화

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체
            force_sync: 강제 동기화 여부

        Returns:
            동기화 결과
        """
        try:
            # 인증되지 않은 사용자는 스킵
            if not user.profile_verified or not user.solvedac_username:
                return {
                    "status": "skipped",
                    "reason": "프로필 인증이 완료되지 않음"
                }

            # 최근 동기화 확인 (강제 동기화가 아닌 경우)
            if not force_sync and user.solvedac_last_synced:
                time_since_sync = datetime.now(timezone.utc) - user.solvedac_last_synced.replace(tzinfo=timezone.utc)
                if time_since_sync < timedelta(hours=self.sync_interval_hours):
                    return {
                        "status": "skipped",
                        "reason": f"최근 동기화됨 ({time_since_sync.total_seconds() / 3600:.1f}시간 전)"
                    }

            logger.info(f"프로필 동기화 시작: user_id={user.user_id}, username={user.solvedac_username}")

            # solved.ac 프로필 데이터 가져오기
            profile_data = await self.solvedac_client.get_user_profile(user.solvedac_username)

            if not profile_data:
                return {
                    "status": "failed",
                    "reason": "프로필 데이터를 가져올 수 없음"
                }

            # 프로필 데이터 업데이트
            sync_result = await self._update_user_profile_data(db, user, profile_data)

            logger.info(f"프로필 동기화 완료: user_id={user.user_id}, "
                       f"tier={sync_result.get('tier')}, "
                       f"rating={sync_result.get('rating')}")

            return {
                "status": "success",
                "data": sync_result,
                "synced_at": datetime.now(timezone.utc).isoformat()
            }

        except (UserNotFoundError, SolvedACAPIError) as e:
            logger.warning(f"프로필 동기화 실패 (API 오류): user_id={user.user_id}, error={str(e)}")
            return {
                "status": "failed",
                "reason": f"API 오류: {str(e)}"
            }
        except Exception as e:
            logger.error(f"프로필 동기화 중 예외: user_id={user.user_id}, error={str(e)}")
            return {
                "status": "error",
                "reason": str(e)
            }

    async def _update_user_profile_data(
        self,
        db: AsyncSession,
        user: User,
        profile_data: Dict
    ) -> Dict:
        """
        사용자 프로필 데이터 업데이트
        """
        try:
            # 기존 데이터와 비교하여 변경사항 확인
            changes = {}

            # 티어 업데이트
            new_tier = profile_data.get('tier')
            if new_tier and new_tier != user.solvedac_tier:
                changes['tier'] = {'old': user.solvedac_tier, 'new': new_tier}
                user.solvedac_tier = new_tier

            # 레이팅 업데이트
            new_rating = profile_data.get('rating')
            if new_rating is not None and new_rating != user.solvedac_rating:
                changes['rating'] = {'old': user.solvedac_rating, 'new': new_rating}
                user.solvedac_rating = new_rating

            # 해결한 문제 수 업데이트
            new_solved_count = profile_data.get('solvedCount')
            if new_solved_count is not None and new_solved_count != user.solvedac_solved_count:
                changes['solved_count'] = {'old': user.solvedac_solved_count, 'new': new_solved_count}
                user.solvedac_solved_count = new_solved_count

            # 클래스 업데이트
            new_class = profile_data.get('class')
            if new_class is not None and new_class != user.solvedac_class:
                changes['class'] = {'old': user.solvedac_class, 'new': new_class}
                user.solvedac_class = new_class

            # 전체 프로필 데이터 캐시 업데이트
            user.solvedac_profile_data = profile_data
            user.solvedac_last_synced = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)

            await db.commit()

            result = {
                "tier": user.solvedac_tier,
                "rating": user.solvedac_rating,
                "solved_count": user.solvedac_solved_count,
                "class": user.solvedac_class,
                "changes": changes,
                "profile_data": profile_data
            }

            if changes:
                logger.info(f"프로필 변경사항 감지: user_id={user.user_id}, changes={list(changes.keys())}")

            return result

        except Exception as e:
            await db.rollback()
            logger.error(f"프로필 데이터 업데이트 실패: {str(e)}")
            raise

    async def schedule_background_sync(
        self,
        user_id: int,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """
        백그라운드에서 프로필 동기화 작업 스케줄링
        """
        try:
            task_id = await background_task_queue.add_task(
                self._background_sync_task,
                user_id,
                name=f"profile_sync_user_{user_id}",
                priority=priority,
                max_retries=2,
                retry_delay=300,  # 5분
                timeout=60  # 1분
            )

            logger.info(f"백그라운드 프로필 동기화 작업 예약: user_id={user_id}, task_id={task_id}")
            return task_id

        except Exception as e:
            logger.error(f"백그라운드 동기화 작업 예약 실패: {str(e)}")
            raise

    async def _background_sync_task(self, user_id: int):
        """
        백그라운드 동기화 작업 (BackgroundTaskQueue에서 실행)
        """
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            # 사용자 조회
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"백그라운드 동기화: 사용자를 찾을 수 없음 (user_id={user_id})")
                return {"status": "failed", "reason": "사용자 없음"}

            # 프로필 동기화 실행
            return await self.sync_user_profile(db, user, force_sync=False)

    async def get_user_profile_cache(
        self,
        db: AsyncSession,
        user_id: int,
        include_raw_data: bool = False
    ) -> Optional[Dict]:
        """
        사용자 프로필 캐시 조회
        """
        try:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user or not user.profile_verified:
                return None

            # 캐시 만료 확인
            if user.solvedac_last_synced:
                cache_age = datetime.now(timezone.utc) - user.solvedac_last_synced.replace(tzinfo=timezone.utc)
                cache_expired = cache_age > timedelta(hours=self.cache_duration_hours)
            else:
                cache_expired = True

            profile_cache = {
                "user_id": user.user_id,
                "solvedac_username": user.solvedac_username,
                "tier": user.solvedac_tier,
                "rating": user.solvedac_rating,
                "solved_count": user.solvedac_solved_count,
                "class": user.solvedac_class,
                "last_synced": user.solvedac_last_synced.isoformat() if user.solvedac_last_synced else None,
                "cache_expired": cache_expired
            }

            if include_raw_data and user.solvedac_profile_data:
                profile_cache["raw_data"] = user.solvedac_profile_data

            return profile_cache

        except Exception as e:
            logger.error(f"프로필 캐시 조회 실패: {str(e)}")
            return None

    async def sync_all_verified_users(self, db: AsyncSession) -> Dict:
        """
        모든 인증된 사용자의 프로필 동기화 (스케줄러에서 호출)
        """
        try:
            logger.info("전체 사용자 프로필 동기화 시작")

            # 동기화가 필요한 사용자들 조회
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.sync_interval_hours)

            result = await db.execute(
                select(User).where(
                    User.profile_verified == True,
                    User.solvedac_username.isnot(None),
                    # 마지막 동기화가 오래되었거나 한 번도 동기화되지 않은 사용자
                    (User.solvedac_last_synced.is_(None)) | (User.solvedac_last_synced < cutoff_time)
                )
            )
            users_to_sync = result.scalars().all()

            if not users_to_sync:
                logger.info("동기화할 사용자 없음")
                return {"synced_users": 0, "scheduled_tasks": 0}

            logger.info(f"{len(users_to_sync)}명의 사용자 프로필 동기화 예약")

            # 백그라운드 작업으로 동기화 예약
            scheduled_tasks = 0
            for user in users_to_sync:
                try:
                    await self.schedule_background_sync(user.user_id, TaskPriority.LOW)
                    scheduled_tasks += 1
                except Exception as e:
                    logger.error(f"동기화 작업 예약 실패: user_id={user.user_id}, error={str(e)}")

            logger.info(f"전체 사용자 프로필 동기화 완료 - {scheduled_tasks}개 작업 예약")

            return {
                "synced_users": len(users_to_sync),
                "scheduled_tasks": scheduled_tasks
            }

        except Exception as e:
            logger.error(f"전체 사용자 동기화 중 오류: {str(e)}")
            return {"synced_users": 0, "scheduled_tasks": 0, "error": str(e)}

    async def cleanup_old_profile_cache(self, db: AsyncSession, days: int = 30) -> int:
        """
        오래된 프로필 캐시 정리
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            # 오래된 캐시 데이터 제거 (프로필 데이터만 NULL로 설정)
            result = await db.execute(
                update(User)
                .where(
                    User.solvedac_last_synced < cutoff_date,
                    User.solvedac_profile_data.isnot(None)
                )
                .values(solvedac_profile_data=None)
            )

            await db.commit()

            cleaned_count = result.rowcount
            if cleaned_count > 0:
                logger.info(f"오래된 프로필 캐시 {cleaned_count}개 정리 완료")

            return cleaned_count

        except Exception as e:
            logger.error(f"프로필 캐시 정리 실패: {str(e)}")
            await db.rollback()
            return 0


# 전역 Enhanced Profile Service 인스턴스
enhanced_profile_service = EnhancedProfileService()
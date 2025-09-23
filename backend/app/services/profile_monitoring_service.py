"""
Real-time profile monitoring service for solved.ac verification.
Handles automatic verification checking and profile synchronization.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.auth import User, ProfileVerification
from app.clients.solvedac_client import SolvedACClient
from app.core.exceptions import UserNotFoundError, SolvedACAPIError
from app.services.profile_verification_service import profile_verification_service
import re

logger = logging.getLogger(__name__)


class ProfileMonitoringService:
    """
    프로필 모니터링 서비스
    - pending 상태 인증 요청 자동 체크
    - solved.ac 프로필 변경 실시간 감지
    - 인증 완료 시 자동 처리
    """

    def __init__(self):
        self.solvedac_client = SolvedACClient()
        self.max_concurrent_checks = 10  # 동시 체크 최대 수
        self.check_retry_attempts = 3   # 실패 시 재시도 횟수
        self.retry_delay_seconds = 5    # 재시도 간격

    async def check_all_pending_verifications(self, db: AsyncSession) -> Dict[str, int]:
        """
        모든 pending 상태 인증 요청들을 체크
        """
        try:
            logger.info("모든 진행 중인 인증 요청 체크 시작")

            # 진행 중인 인증 요청 조회
            result = await db.execute(
                select(ProfileVerification)
                .options(selectinload(ProfileVerification.user))
                .where(
                    ProfileVerification.status == 'pending',
                    ProfileVerification.expires_at > datetime.now()
                )
                .order_by(ProfileVerification.created_at.desc())
            )
            pending_verifications = result.scalars().all()

            if not pending_verifications:
                logger.debug("체크할 진행 중인 인증 요청 없음")
                return {
                    "total_checked": 0,
                    "verified": 0,
                    "still_pending": 0,
                    "failed": 0,
                    "errors": 0
                }

            logger.info(f"{len(pending_verifications)}개 인증 요청 체크 시작")

            # 동시 처리를 위한 세마포어
            semaphore = asyncio.Semaphore(self.max_concurrent_checks)

            # 모든 인증 요청 동시 체크
            tasks = [
                self._check_single_verification_with_semaphore(db, verification, semaphore)
                for verification in pending_verifications
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 집계
            stats = {
                "total_checked": len(pending_verifications),
                "verified": 0,
                "still_pending": 0,
                "failed": 0,
                "errors": 0
            }

            for result in results:
                if isinstance(result, Exception):
                    stats["errors"] += 1
                    logger.error(f"인증 체크 중 예외 발생: {str(result)}")
                elif isinstance(result, dict):
                    stats[result.get("status", "errors")] += 1

            logger.info(f"인증 체크 완료 - 총 {stats['total_checked']}개, "
                       f"인증 완료: {stats['verified']}개, "
                       f"진행 중: {stats['still_pending']}개, "
                       f"실패: {stats['failed']}개, "
                       f"오류: {stats['errors']}개")

            return stats

        except Exception as e:
            logger.error(f"전체 인증 체크 중 오류: {str(e)}")
            return {
                "total_checked": 0,
                "verified": 0,
                "still_pending": 0,
                "failed": 0,
                "errors": 1
            }

    async def _check_single_verification_with_semaphore(
        self,
        db: AsyncSession,
        verification: ProfileVerification,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, str]:
        """
        세마포어를 사용한 단일 인증 체크 (동시성 제어)
        """
        async with semaphore:
            return await self._check_single_verification(db, verification)

    async def _check_single_verification(
        self,
        db: AsyncSession,
        verification: ProfileVerification
    ) -> Dict[str, str]:
        """
        단일 인증 요청 체크
        """
        try:
            logger.debug(f"인증 체크 시작: code={verification.verification_code}, "
                        f"username={verification.solvedac_username}")

            # 재시도 로직과 함께 프로필 체크
            for attempt in range(self.check_retry_attempts):
                try:
                    result = await self._check_profile_with_retry(verification)

                    if result["status"] == "verified":
                        # 인증 성공 처리
                        await self._handle_verification_success(db, verification, result)
                        return {"status": "verified"}

                    elif result["status"] == "failed":
                        # 인증 실패 처리
                        await self._handle_verification_failure(db, verification, result)
                        return {"status": "failed"}

                    else:
                        # 아직 pending 상태
                        logger.debug(f"인증 아직 진행 중: {verification.verification_code}")
                        return {"status": "still_pending"}

                except (UserNotFoundError, SolvedACAPIError) as e:
                    if attempt < self.check_retry_attempts - 1:
                        logger.warning(f"API 오류로 재시도 예정 (시도 {attempt + 1}/{self.check_retry_attempts}): {str(e)}")
                        await asyncio.sleep(self.retry_delay_seconds)
                        continue
                    else:
                        # 최종 실패
                        await self._handle_verification_api_failure(db, verification, str(e))
                        return {"status": "failed"}

            return {"status": "still_pending"}

        except Exception as e:
            logger.error(f"인증 체크 중 예외: {str(e)}")
            return {"status": "errors"}

    async def _check_profile_with_retry(self, verification: ProfileVerification) -> Dict:
        """
        solved.ac 프로필 체크 (재시도 로직 포함)
        """
        try:
            # solved.ac 프로필 조회
            profile_info = await self.solvedac_client.get_user_profile(verification.solvedac_username)
            current_bio = profile_info.get('bio', '')

            # bio에서 인증 코드 추출
            found_code = self._extract_verification_code(current_bio)

            if found_code == verification.verification_code:
                # 인증 성공!
                return {
                    "status": "verified",
                    "current_bio": current_bio,
                    "profile_info": profile_info
                }
            else:
                # 아직 인증 코드가 없거나 다름
                return {
                    "status": "pending",
                    "current_bio": current_bio
                }

        except (UserNotFoundError, SolvedACAPIError) as e:
            # API 오류 - 상위에서 재시도 처리
            raise

        except Exception as e:
            # 기타 오류
            return {
                "status": "failed",
                "error": str(e)
            }

    def _extract_verification_code(self, bio: str) -> Optional[str]:
        """
        bio에서 CAU-CODE- 패턴의 인증 코드 추출
        """
        if not bio:
            return None

        # CAU-CODE-로 시작하는 12자리 영숫자 패턴 찾기
        pattern = r'CAU-CODE-[A-Za-z0-9]{12}'
        match = re.search(pattern, bio)

        return match.group(0) if match else None

    async def _handle_verification_success(
        self,
        db: AsyncSession,
        verification: ProfileVerification,
        result: Dict
    ):
        """
        인증 성공 처리
        """
        try:
            # 인증 상태 업데이트
            verification.status = 'verified'
            verification.verified_at = datetime.now(timezone.utc)
            verification.bio_after_verification = result["current_bio"]

            # 사용자 프로필 인증 상태 업데이트
            user = verification.user
            user.profile_verified = True
            user.solvedac_username = verification.solvedac_username
            user.updated_at = datetime.now(timezone.utc)

            await db.commit()

            # Enhanced Profile Integration - solved.ac 프로필 데이터 동기화
            await self._sync_user_profile_data(db, user, result["profile_info"])

            logger.info(f"프로필 인증 성공 자동 처리 완료: "
                       f"user_id={user.user_id}, "
                       f"solvedac_username={verification.solvedac_username}")

        except Exception as e:
            await db.rollback()
            logger.error(f"인증 성공 처리 중 오류: {str(e)}")
            raise

    async def _handle_verification_failure(
        self,
        db: AsyncSession,
        verification: ProfileVerification,
        result: Dict
    ):
        """
        인증 실패 처리
        """
        try:
            verification.status = 'failed'
            verification.failed_reason = result.get("error", "알 수 없는 오류")
            await db.commit()

            logger.warning(f"인증 실패 처리: code={verification.verification_code}, "
                          f"reason={verification.failed_reason}")

        except Exception as e:
            await db.rollback()
            logger.error(f"인증 실패 처리 중 오류: {str(e)}")

    async def _handle_verification_api_failure(
        self,
        db: AsyncSession,
        verification: ProfileVerification,
        error_message: str
    ):
        """
        API 오류로 인한 인증 실패 처리
        """
        try:
            verification.status = 'failed'
            verification.failed_reason = f"API 오류: {error_message}"
            await db.commit()

            logger.warning(f"API 오류로 인한 인증 실패: code={verification.verification_code}, "
                          f"error={error_message}")

        except Exception as e:
            await db.rollback()
            logger.error(f"API 실패 처리 중 오류: {str(e)}")

    async def _sync_user_profile_data(
        self,
        db: AsyncSession,
        user: User,
        profile_info: Dict
    ):
        """
        solved.ac 프로필 데이터를 사용자 정보와 동기화
        Enhanced Profile Integration 사용
        """
        try:
            # Enhanced Profile Service를 사용한 프로필 동기화
            from app.services.enhanced_profile_service import enhanced_profile_service

            # 백그라운드에서 동기화 작업 예약 (즉시 처리 우선순위)
            from app.core.background_tasks import TaskPriority
            await enhanced_profile_service.schedule_background_sync(
                user.user_id,
                priority=TaskPriority.HIGH
            )

            logger.info(f"사용자 프로필 데이터 동기화 작업 예약: user_id={user.user_id}, "
                       f"tier={profile_info.get('tier')}, "
                       f"rating={profile_info.get('rating')}")

        except Exception as e:
            logger.error(f"프로필 데이터 동기화 중 오류: {str(e)}")

    async def get_monitoring_stats(self, db: AsyncSession) -> Dict:
        """
        모니터링 통계 조회
        """
        try:
            # 진행 중인 인증 요청 수
            pending_result = await db.execute(
                select(ProfileVerification)
                .where(
                    ProfileVerification.status == 'pending',
                    ProfileVerification.expires_at > datetime.now(timezone.utc)
                )
            )
            pending_count = len(pending_result.scalars().all())

            # 최근 24시간 인증 완료 수
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            verified_result = await db.execute(
                select(ProfileVerification)
                .where(
                    ProfileVerification.status == 'verified',
                    ProfileVerification.verified_at > yesterday
                )
            )
            verified_count = len(verified_result.scalars().all())

            return {
                "pending_verifications": pending_count,
                "verified_last_24h": verified_count,
                "last_check": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"모니터링 통계 조회 중 오류: {str(e)}")
            return {
                "pending_verifications": 0,
                "verified_last_24h": 0,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }


# 전역 프로필 모니터링 서비스 인스턴스
profile_monitoring_service = ProfileMonitoringService()
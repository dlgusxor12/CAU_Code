import uuid
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.auth import User, ProfileVerification
from app.clients.solvedac_client import SolvedACClient
from app.core.exceptions import UserNotFoundError, SolvedACAPIError
from app.utils.security import security_validator
import logging

logger = logging.getLogger(__name__)


class ProfileVerificationService:
    def __init__(self):
        self.solvedac_client = SolvedACClient()
        self.verification_code_expire_minutes = settings.verification_code_expire_minutes
        self.max_verification_attempts = settings.max_verification_attempts

    def generate_verification_code(self) -> str:
        """
        고유한 인증 코드 생성
        형식: CAU-CODE-{uuid4의 앞 12자리}
        """
        unique_id = str(uuid.uuid4()).replace('-', '')[:12].upper()
        return f"CAU-CODE-{unique_id}"

    def extract_verification_code(self, bio: str) -> Optional[str]:
        """
        bio에서 CAU-CODE- 패턴의 인증 코드 추출
        """
        if not bio:
            return None

        # CAU-CODE-로 시작하는 12자리 영숫자 패턴 찾기
        pattern = r'CAU-CODE-[A-Za-z0-9]{12}'
        match = re.search(pattern, bio)

        return match.group(0) if match else None

    async def create_verification_request(
        self,
        db: AsyncSession,
        user_id: int,
        solvedac_username: str
    ) -> Tuple[str, datetime]:
        """
        새로운 인증 요청 생성
        """
        try:
            # 입력 검증
            if not security_validator.validate_solvedac_username(solvedac_username):
                raise ValueError("유효하지 않은 solved.ac 사용자명입니다.")

            # 보안 검증
            if not security_validator.is_safe_string(solvedac_username, 20):
                raise ValueError("안전하지 않은 사용자명입니다.")
            # 사용자 조회
            user_result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")

            # solved.ac 사용자 존재 확인
            try:
                profile_info = await self.solvedac_client.get_user_profile(solvedac_username)
                bio_before = profile_info.get('bio', '')
            except (UserNotFoundError, SolvedACAPIError) as e:
                logger.error(f"solved.ac 사용자 조회 실패 ({solvedac_username}): {str(e)}")
                raise ValueError("존재하지 않는 solved.ac 사용자입니다.")

            # 인증 시도 횟수 확인
            if user.verification_attempts >= self.max_verification_attempts:
                time_since_last = datetime.now(timezone.utc) - (user.last_verification_attempt or datetime.min.replace(tzinfo=timezone.utc))
                if time_since_last < timedelta(hours=1):
                    raise ValueError("인증 시도 횟수가 초과되었습니다. 1시간 후 다시 시도해주세요.")
                else:
                    # 1시간이 지났으면 시도 횟수 리셋
                    user.verification_attempts = 0

            # 기존 진행 중인 인증 요청 만료 처리
            await db.execute(
                update(ProfileVerification)
                .where(
                    ProfileVerification.user_id == user_id,
                    ProfileVerification.status == 'pending'
                )
                .values(status='expired')
            )

            # 새 인증 코드 생성
            verification_code = self.generate_verification_code()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.verification_code_expire_minutes)

            # 인증 요청 생성
            verification = ProfileVerification(
                user_id=user_id,
                verification_code=verification_code,
                solvedac_username=solvedac_username,
                status='pending',
                bio_before_verification=bio_before,
                expires_at=expires_at
            )

            db.add(verification)

            # 사용자 인증 시도 횟수 업데이트
            user.verification_attempts += 1
            user.last_verification_attempt = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(verification)

            logger.info(f"인증 요청 생성: user_id={user_id}, solvedac_username={solvedac_username}, code={verification_code}")

            return verification_code, expires_at

        except Exception as e:
            await db.rollback()
            logger.error(f"인증 요청 생성 실패: {str(e)}")
            raise

    async def check_verification_status(
        self,
        db: AsyncSession,
        verification_code: str
    ) -> dict:
        """
        인증 상태 확인
        """
        try:
            # 인증 요청 조회
            result = await db.execute(
                select(ProfileVerification)
                .options(selectinload(ProfileVerification.user))
                .where(ProfileVerification.verification_code == verification_code)
            )
            verification = result.scalar_one_or_none()

            if not verification:
                return {
                    "status": "not_found",
                    "message": "인증 요청을 찾을 수 없습니다."
                }

            # 만료 확인
            if verification.expires_at < datetime.now(timezone.utc):
                if verification.status == 'pending':
                    verification.status = 'expired'
                    await db.commit()

                return {
                    "status": "expired",
                    "message": "인증 코드가 만료되었습니다."
                }

            # 이미 인증 완료된 경우
            if verification.status == 'verified':
                return {
                    "status": "verified",
                    "message": "이미 인증이 완료되었습니다.",
                    "verified_at": verification.verified_at
                }

            # 인증 실패한 경우
            if verification.status == 'failed':
                return {
                    "status": "failed",
                    "message": verification.failed_reason or "인증에 실패했습니다."
                }

            # pending 상태인 경우 - solved.ac 프로필 확인
            return await self._check_solvedac_profile(db, verification)

        except Exception as e:
            logger.error(f"인증 상태 확인 실패: {str(e)}")
            return {
                "status": "error",
                "message": "인증 상태 확인 중 오류가 발생했습니다."
            }

    async def _check_solvedac_profile(
        self,
        db: AsyncSession,
        verification: ProfileVerification
    ) -> dict:
        """
        solved.ac 프로필에서 인증 코드 확인
        """
        try:
            # solved.ac 프로필 조회
            profile_info = await self.solvedac_client.get_user_profile(verification.solvedac_username)
            current_bio = profile_info.get('bio', '')

            # bio에서 인증 코드 추출
            found_code = self.extract_verification_code(current_bio)

            if found_code == verification.verification_code:
                # 인증 성공!
                verification.status = 'verified'
                verification.verified_at = datetime.now(timezone.utc)
                verification.bio_after_verification = current_bio

                # 사용자 프로필 인증 상태 업데이트
                user = verification.user
                user.profile_verified = True
                user.solvedac_username = verification.solvedac_username
                user.updated_at = datetime.now(timezone.utc)

                await db.commit()

                logger.info(f"프로필 인증 성공: user_id={user.user_id}, solvedac_username={verification.solvedac_username}")

                return {
                    "status": "verified",
                    "message": "프로필 인증이 완료되었습니다!",
                    "verified_at": verification.verified_at,
                    "user_profile": {
                        "tier": profile_info.get('tier'),
                        "rating": profile_info.get('rating'),
                        "solved_count": profile_info.get('solvedCount'),
                        "class": profile_info.get('class')
                    }
                }
            else:
                # 아직 인증 코드가 없음
                return {
                    "status": "pending",
                    "message": "solved.ac 프로필 자기소개란에 인증 코드를 추가해주세요.",
                    "current_bio": current_bio,
                    "expires_at": verification.expires_at
                }

        except (UserNotFoundError, SolvedACAPIError) as e:
            logger.error(f"solved.ac 프로필 조회 실패: {str(e)}")

            verification.status = 'failed'
            verification.failed_reason = "solved.ac 프로필 조회에 실패했습니다."
            await db.commit()

            return {
                "status": "failed",
                "message": verification.failed_reason
            }
        except Exception as e:
            logger.error(f"프로필 확인 중 오류: {str(e)}")
            return {
                "status": "error",
                "message": "프로필 확인 중 오류가 발생했습니다."
            }

    async def get_user_verification_status(
        self,
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """
        사용자의 현재 인증 상태 조회
        """
        try:
            # 사용자 조회
            user_result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                return {"status": "user_not_found"}

            if user.profile_verified:
                return {
                    "status": "verified",
                    "solvedac_username": user.solvedac_username,
                    "message": "이미 인증이 완료된 사용자입니다."
                }

            # 진행 중인 인증 요청 확인
            verification_result = await db.execute(
                select(ProfileVerification)
                .where(
                    ProfileVerification.user_id == user_id,
                    ProfileVerification.status == 'pending',
                    ProfileVerification.expires_at > datetime.now(timezone.utc)
                )
                .order_by(ProfileVerification.created_at.desc())
            )
            verification = verification_result.scalar_one_or_none()

            if verification:
                return {
                    "status": "pending",
                    "verification_code": verification.verification_code,
                    "solvedac_username": verification.solvedac_username,
                    "expires_at": verification.expires_at,
                    "message": "진행 중인 인증 요청이 있습니다."
                }

            return {
                "status": "not_verified",
                "remaining_attempts": max(0, self.max_verification_attempts - user.verification_attempts),
                "message": "프로필 인증이 필요합니다."
            }

        except Exception as e:
            logger.error(f"사용자 인증 상태 조회 실패: {str(e)}")
            return {
                "status": "error",
                "message": "인증 상태 조회 중 오류가 발생했습니다."
            }

    async def cleanup_expired_verifications(self, db: AsyncSession) -> int:
        """
        만료된 인증 요청 정리
        """
        try:
            result = await db.execute(
                update(ProfileVerification)
                .where(
                    ProfileVerification.status == 'pending',
                    ProfileVerification.expires_at < datetime.now()
                )
                .values(status='expired')
            )
            await db.commit()

            cleaned_count = result.rowcount
            if cleaned_count > 0:
                logger.info(f"만료된 인증 요청 {cleaned_count}개 정리 완료")

            return cleaned_count

        except Exception as e:
            logger.error(f"만료된 인증 요청 정리 실패: {str(e)}")
            await db.rollback()
            return 0


# 전역 프로필 인증 서비스 인스턴스
profile_verification_service = ProfileVerificationService()
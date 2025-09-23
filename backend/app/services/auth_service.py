from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import uuid
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.auth import User, UserSession, ProfileVerification
from app.schemas.auth import TokenData, UserCreate, UserProfile
from app.database import AsyncSessionLocal


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def hash_token(self, token: str) -> str:
        """토큰을 해시화하여 저장"""
        return hashlib.sha256(token.encode()).hexdigest()

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Access Token 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        """Refresh Token 생성"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """토큰 검증 및 데이터 추출"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 토큰 타입 확인
            if payload.get("type") != token_type:
                return None

            user_id: int = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None or email is None:
                return None

            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None

    async def create_user_session(
        self,
        db: AsyncSession,
        user_id: int,
        access_token: str,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """사용자 세션 생성"""
        # 토큰 해시화
        access_token_hash = self.hash_token(access_token)
        refresh_token_hash = self.hash_token(refresh_token)

        # 만료 시간 계산
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)

        # 세션 생성
        session = UserSession(
            user_id=user_id,
            access_token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """사용자 ID로 사용자 조회"""
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_google_id(self, db: AsyncSession, google_id: str) -> Optional[User]:
        """Google ID로 사용자 조회"""
        result = await db.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """새 사용자 생성"""
        user = User(
            google_id=user_data.google_id,
            email=user_data.email,
            name=user_data.name,
            profile_image_url=user_data.profile_image_url
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_user_last_verification_attempt(self, db: AsyncSession, user_id: int):
        """사용자의 마지막 인증 시도 시간 업데이트"""
        await db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(
                verification_attempts=User.verification_attempts + 1,
                last_verification_attempt=datetime.now(timezone.utc)
            )
        )
        await db.commit()

    async def verify_session(self, db: AsyncSession, access_token: str) -> Optional[User]:
        """세션 검증 및 사용자 반환"""
        # 토큰 해시화
        token_hash = self.hash_token(access_token)

        # 세션 조회
        result = await db.execute(
            select(UserSession)
            .options(selectinload(UserSession.user))
            .where(
                UserSession.access_token_hash == token_hash,
                UserSession.expires_at > datetime.now(timezone.utc)
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            return None

        # 마지막 접근 시간 업데이트
        session.last_accessed = datetime.now(timezone.utc)
        await db.commit()

        return session.user

    async def revoke_session(self, db: AsyncSession, access_token: str) -> bool:
        """세션 무효화 (로그아웃)"""
        token_hash = self.hash_token(access_token)

        result = await db.execute(
            delete(UserSession).where(UserSession.access_token_hash == token_hash)
        )
        await db.commit()

        return result.rowcount > 0

    async def revoke_user_sessions(self, db: AsyncSession, user_id: int) -> int:
        """사용자의 모든 세션 무효화"""
        result = await db.execute(
            delete(UserSession).where(UserSession.user_id == user_id)
        )
        await db.commit()

        return result.rowcount

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """만료된 세션 정리"""
        result = await db.execute(
            delete(UserSession).where(UserSession.expires_at < datetime.now(timezone.utc))
        )
        await db.commit()

        return result.rowcount

    async def generate_tokens_for_user(self, user: User) -> tuple[str, str]:
        """사용자를 위한 토큰 쌍 생성"""
        token_data = {
            "sub": user.user_id,
            "email": user.email,
            "name": user.name
        }

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return access_token, refresh_token


# 전역 인증 서비스 인스턴스
auth_service = AuthService()
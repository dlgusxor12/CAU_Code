from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services.auth_service import auth_service
from app.models.auth import User
from app.schemas.auth import CurrentUser
from app.config import settings


# Database dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_settings():
    return settings


def verify_api_key():
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )


# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    선택적 인증 - 토큰이 있으면 사용자 반환, 없으면 None 반환
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = await auth_service.verify_session(db, token)
        return user
    except Exception:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    필수 인증 - 유효한 토큰과 사용자 필요
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        user = await auth_service.verify_session(db, token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 정보입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 처리 중 오류가 발생했습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    solved.ac 프로필 인증이 완료된 사용자만 허용
    """
    if not current_user.profile_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="solved.ac 프로필 인증이 필요합니다.",
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    관리자 권한이 필요한 엔드포인트용 (향후 확장)
    """
    # TODO: 관리자 권한 체크 로직 추가
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="관리자 권한이 필요합니다.",
    #     )
    return current_user


def get_client_ip(request: Request) -> str:
    """
    클라이언트 IP 주소 추출
    """
    # X-Forwarded-For 헤더 확인 (프록시 환경)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # X-Real-IP 헤더 확인
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 직접 연결된 클라이언트 IP
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    User-Agent 헤더 추출
    """
    return request.headers.get("User-Agent", "unknown")
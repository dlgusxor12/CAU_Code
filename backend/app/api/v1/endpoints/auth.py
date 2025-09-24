from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, get_client_ip, get_user_agent
from app.schemas.auth import (
    GoogleTokenRequest, GoogleTokenResponse, TokenResponse,
    UserProfile, LogoutResponse, AuthResponse, CurrentUser,
    ProfileVerificationRequest, ProfileVerificationResponse,
    ProfileVerificationStatus, ProfileVerificationCheck
)
from app.services.auth_service import auth_service
from app.services.profile_verification_service import profile_verification_service
from app.clients.google_oauth_client import google_oauth_client
from app.models.auth import User
from app.utils.rate_limiter import verification_rate_limit, auth_rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/google-login", response_model=GoogleTokenResponse)
@auth_rate_limit
async def google_login(
    request: Request,
    token_request: GoogleTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Google OAuth ID Token을 사용한 로그인/회원가입
    """
    try:
        # Google ID Token 검증
        user_info = await google_oauth_client.verify_token_and_get_user_info(
            token_request.id_token
        )

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 Google 토큰입니다."
            )

        # 기존 사용자 확인
        user = await auth_service.get_user_by_google_id(db, user_info['google_id'])

        if not user:
            # 새 사용자 생성
            from app.schemas.auth import UserCreate
            user_create = UserCreate(
                google_id=user_info['google_id'],
                email=user_info['email'],
                name=user_info['name'],
                profile_image_url=user_info.get('profile_image_url')
            )
            user = await auth_service.create_user(db, user_create)
            logger.info(f"새 사용자 생성: {user.email}")
        else:
            # 기존 사용자 정보 업데이트
            user.name = user_info['name']
            user.profile_image_url = user_info.get('profile_image_url')
            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"기존 사용자 로그인: {user.email}")

        # JWT 토큰 생성
        access_token, refresh_token = await auth_service.generate_tokens_for_user(user)

        # 세션 생성
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)

        await auth_service.create_user_session(
            db=db,
            user_id=user.user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=client_ip
        )

        # 응답 생성
        user_profile = UserProfile.model_validate(user)

        return GoogleTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            user=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google 로그인 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 로그아웃 (세션 무효화)
    """
    try:
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 헤더입니다."
            )

        access_token = auth_header.split(" ")[1]

        # 세션 무효화
        success = await auth_service.revoke_session(db, access_token)

        if success:
            logger.info(f"사용자 로그아웃: {current_user.email}")
            return LogoutResponse(
                success=True,
                message="성공적으로 로그아웃되었습니다."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="로그아웃 처리에 실패했습니다."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그아웃 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다."
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    """
    return UserProfile.model_validate(current_user)


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh Token을 사용하여 새로운 Access Token 발급
    """
    try:
        # Authorization 헤더에서 refresh token 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh Token이 필요합니다."
            )

        refresh_token = auth_header.split(" ")[1]

        # Refresh Token 검증
        token_data = auth_service.verify_token(refresh_token, token_type="refresh")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 Refresh Token입니다."
            )

        # 사용자 조회
        user = await auth_service.get_user_by_id(db, token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다."
            )

        # 새로운 토큰 쌍 생성
        new_access_token, new_refresh_token = await auth_service.generate_tokens_for_user(user)

        # 기존 세션 업데이트
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)

        # 기존 세션 무효화 후 새 세션 생성
        await auth_service.revoke_session(db, refresh_token)
        await auth_service.create_user_session(
            db=db,
            user_id=user.user_id,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            user_agent=user_agent,
            ip_address=client_ip
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            user=UserProfile.model_validate(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 갱신 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토큰 갱신 중 오류가 발생했습니다."
        )


@router.delete("/sessions", response_model=AuthResponse)
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자의 모든 세션 무효화 (모든 기기에서 로그아웃)
    """
    try:
        revoked_count = await auth_service.revoke_user_sessions(db, current_user.user_id)

        logger.info(f"사용자 {current_user.email}의 {revoked_count}개 세션 무효화")

        return AuthResponse(
            success=True,
            message=f"{revoked_count}개의 세션이 무효화되었습니다.",
            data={"revoked_sessions": revoked_count}
        )

    except Exception as e:
        logger.error(f"세션 무효화 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 무효화 중 오류가 발생했습니다."
        )


@router.post("/solvedac-verify", response_model=ProfileVerificationResponse)
@verification_rate_limit
async def request_solvedac_verification(
    request_data: ProfileVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    solved.ac 프로필 인증 요청
    """
    try:
        # 이미 인증된 사용자 확인
        if current_user.profile_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 프로필 인증이 완료된 사용자입니다."
            )

        # 인증 코드 생성
        verification_code, expires_at = await profile_verification_service.create_verification_request(
            db=db,
            user_id=current_user.user_id,
            solvedac_username=request_data.solvedac_username
        )

        return ProfileVerificationResponse(
            verification_code=verification_code,
            expires_at=expires_at,
            instructions=f"""
다음 단계를 따라 프로필 인증을 완료해주세요:

1. solved.ac에 로그인하세요
2. 프로필 설정으로 이동하세요
3. 자기소개란에 다음 인증 코드를 추가하세요: {verification_code}
4. 저장 후 "인증 확인" 버튼을 클릭하세요

⏰ 인증 코드는 {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC까지 유효합니다.
            """.strip()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"프로필 인증 요청 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 인증 요청 중 오류가 발생했습니다."
        )


@router.post("/check-verification", response_model=ProfileVerificationStatus)
@auth_rate_limit
async def check_profile_verification(
    check_data: ProfileVerificationCheck,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로필 인증 상태 확인
    """
    try:
        result = await profile_verification_service.check_verification_status(
            db=db,
            verification_code=check_data.verification_code
        )

        return ProfileVerificationStatus(
            status=result["status"],
            verification_code=check_data.verification_code if result["status"] == "verified" else None,
            expires_at=result.get("expires_at"),
            verified_at=result.get("verified_at"),
            failed_reason=result.get("message") if result["status"] in ["failed", "error"] else None
        )

    except Exception as e:
        logger.error(f"프로필 인증 확인 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 인증 확인 중 오류가 발생했습니다."
        )


@router.get("/verification-status", response_model=dict)
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 사용자의 인증 상태 조회
    """
    try:
        result = await profile_verification_service.get_user_verification_status(
            db=db,
            user_id=current_user.user_id
        )
        return result

    except Exception as e:
        logger.error(f"인증 상태 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 상태 조회 중 오류가 발생했습니다."
        )


@router.get("/verify-status/{verification_code}", response_model=ProfileVerificationStatus)
async def verify_status_by_code(
    verification_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    인증 코드로 인증 상태 확인 (토큰 없이 접근 가능)
    """
    try:
        result = await profile_verification_service.check_verification_status(
            db=db,
            verification_code=verification_code
        )

        return ProfileVerificationStatus(
            status=result["status"],
            verification_code=verification_code if result["status"] == "verified" else None,
            expires_at=result.get("expires_at"),
            verified_at=result.get("verified_at"),
            failed_reason=result.get("message") if result["status"] in ["failed", "error"] else None
        )

    except Exception as e:
        logger.error(f"인증 상태 확인 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 상태 확인 중 오류가 발생했습니다."
        )
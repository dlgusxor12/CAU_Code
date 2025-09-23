from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Token Schemas
class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserProfile"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    profile_image_url: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_image_url: Optional[str] = None
    solvedac_username: Optional[str] = None


class UserProfile(BaseModel):
    user_id: int
    google_id: str
    email: str
    name: str
    profile_image_url: Optional[str] = None
    solvedac_username: Optional[str] = None
    profile_verified: bool = False
    verification_attempts: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CurrentUser(BaseModel):
    user_id: int
    email: str
    name: str
    profile_image_url: Optional[str] = None
    solvedac_username: Optional[str] = None
    profile_verified: bool = False


# Google OAuth Schemas
class GoogleTokenRequest(BaseModel):
    id_token: str = Field(..., description="Google ID token from frontend")


class GoogleTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


# Profile Verification Schemas
class ProfileVerificationRequest(BaseModel):
    solvedac_username: str = Field(..., min_length=1, max_length=50, description="solved.ac 사용자명")


class ProfileVerificationResponse(BaseModel):
    verification_code: str = Field(..., description="자기소개란에 추가할 인증 코드")
    expires_at: datetime = Field(..., description="인증 코드 만료 시간")
    instructions: str = Field(..., description="인증 절차 안내")


class ProfileVerificationStatus(BaseModel):
    status: str = Field(..., description="인증 상태 (pending, verified, expired, failed)")
    verification_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    failed_reason: Optional[str] = None


class ProfileVerificationCheck(BaseModel):
    verification_code: str = Field(..., description="확인할 인증 코드")


# Session Schemas
class SessionInfo(BaseModel):
    session_id: UUID
    user_id: int
    expires_at: datetime
    last_accessed: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Response Schemas
class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class LogoutResponse(BaseModel):
    success: bool = True
    message: str = "로그아웃되었습니다."


# Error Schemas
class AuthError(BaseModel):
    error: str
    error_description: str
    error_code: Optional[int] = None


# Update forward references
TokenResponse.model_rebuild()
GoogleTokenResponse.model_rebuild()
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UUID, JSON
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    solvedac_username = Column(String(50), unique=True, nullable=True, index=True)
    profile_verified = Column(Boolean, default=False, index=True)
    verification_attempts = Column(Integer, default=0)
    last_verification_attempt = Column(DateTime(timezone=True), nullable=True)

    # solved.ac 프로필 동기화 데이터 (Phase 2.2 Enhanced Profile Integration)
    solvedac_tier = Column(String(20), nullable=True)  # 티어 (Bronze V, Silver III 등)
    solvedac_rating = Column(Integer, nullable=True)   # 레이팅
    solvedac_solved_count = Column(Integer, nullable=True)  # 해결한 문제 수
    solvedac_class = Column(Integer, nullable=True)    # 클래스
    solvedac_profile_data = Column(JSON, nullable=True)  # 추가 프로필 데이터 (캐시용)
    solvedac_last_synced = Column(DateTime(timezone=True), nullable=True)  # 마지막 동기화 시간

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    verification_records = relationship("ProfileVerification", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    access_token_hash = Column(String(255), nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(INET, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")


class ProfileVerification(Base):
    __tablename__ = "profile_verification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    verification_code = Column(String(100), unique=True, nullable=False, index=True)
    solvedac_username = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="pending", index=True)  # pending, verified, expired, failed
    bio_before_verification = Column(Text, nullable=True)
    bio_after_verification = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="verification_records")
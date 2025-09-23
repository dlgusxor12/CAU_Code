import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://caucode_user:dev_password_123@localhost:5432/caucode")

# Async PostgreSQL용 URL로 변환
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemy 엔진 생성
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# 세션 생성
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base 클래스
Base = declarative_base()

# DB 연결 테스트용 함수
async def test_db_connection():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            return {"status": "connected", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "error": str(e)}
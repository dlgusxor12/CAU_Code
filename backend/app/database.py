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

# DB 테이블 초기화 함수
async def init_database():
    """데이터베이스 테이블을 자동으로 생성"""
    try:
        # SQLAlchemy 모델들을 import해서 테이블 생성
        from app.models.auth import User, UserSession, ProfileVerification

        # 모든 테이블 생성
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 추가로 스키마 파일의 나머지 테이블들도 생성
        async with AsyncSessionLocal() as session:
            # user_activities 테이블
            await session.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    activity_type VARCHAR(20) NOT NULL,
                    problem_id INTEGER,
                    problem_title VARCHAR(200),
                    submission_id VARCHAR(100),
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 인덱스들 생성
            await session.execute("""
                CREATE INDEX IF NOT EXISTS idx_username_created ON user_activities (username, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_activity_type ON user_activities (activity_type);
                CREATE INDEX IF NOT EXISTS idx_problem_id ON user_activities (problem_id);
            """)

            await session.commit()

    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        raise
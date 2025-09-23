-- CAU Code 최적화된 DB 스키마

-- =============================================
-- AUTHENTICATION TABLES (Phase 1 추가)
-- =============================================

-- 1. 사용자 기본 정보 테이블 (Google OAuth + solved.ac Profile Integration)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    profile_image_url VARCHAR(500),
    solvedac_username VARCHAR(50) UNIQUE,
    profile_verified BOOLEAN DEFAULT FALSE,
    verification_attempts INTEGER DEFAULT 0,
    last_verification_attempt TIMESTAMP WITH TIME ZONE,

    -- solved.ac 프로필 동기화 데이터 (Phase 2.2 Enhanced Profile Integration)
    solvedac_tier VARCHAR(20),
    solvedac_rating INTEGER,
    solvedac_solved_count INTEGER,
    solvedac_class INTEGER,
    solvedac_profile_data JSONB,
    solvedac_last_synced TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_solvedac_username ON users (solvedac_username);
CREATE INDEX IF NOT EXISTS idx_users_verified ON users (profile_verified);

-- solved.ac 프로필 데이터 인덱스 (Phase 2.2)
CREATE INDEX IF NOT EXISTS idx_users_solvedac_tier ON users (solvedac_tier);
CREATE INDEX IF NOT EXISTS idx_users_solvedac_last_synced ON users (solvedac_last_synced);
CREATE INDEX IF NOT EXISTS idx_users_profile_data ON users USING GIN (solvedac_profile_data);

-- 2. 사용자 세션 관리 테이블 (JWT)
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    access_token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_agent VARCHAR(500),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 세션 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions (expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_access_token ON user_sessions (access_token_hash);

-- 3. solved.ac 프로필 인증 관리 테이블
CREATE TABLE IF NOT EXISTS profile_verification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    verification_code VARCHAR(100) NOT NULL UNIQUE,
    solvedac_username VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, verified, expired, failed
    bio_before_verification TEXT,
    bio_after_verification TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    failed_reason VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 프로필 인증 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_verification_user_id ON profile_verification (user_id);
CREATE INDEX IF NOT EXISTS idx_verification_code ON profile_verification (verification_code);
CREATE INDEX IF NOT EXISTS idx_verification_status ON profile_verification (status);
CREATE INDEX IF NOT EXISTS idx_verification_expires_at ON profile_verification (expires_at);
CREATE INDEX IF NOT EXISTS idx_verification_solvedac_username ON profile_verification (solvedac_username);

-- =============================================
-- EXISTING TABLES (기존 테이블들)
-- =============================================

-- 4. 사용자 활동 로그 테이블
CREATE TABLE IF NOT EXISTS user_activities (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    activity_type VARCHAR(20) NOT NULL, -- 'feedback_request', 'problem_solved'
    problem_id INTEGER,
    problem_title VARCHAR(200),
    submission_id VARCHAR(100), -- 피드백 요청 시 사용
    metadata JSONB, -- 추가 데이터 (난이도, 언어 등)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 최적화
CREATE INDEX IF NOT EXISTS idx_username_created ON user_activities (username, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_type ON user_activities (activity_type);
CREATE INDEX IF NOT EXISTS idx_problem_id ON user_activities (problem_id);

-- 2. 일별 추천 문제 테이블 (오늘의 문제 고정용)
CREATE TABLE IF NOT EXISTS daily_problems (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    username VARCHAR(50) NOT NULL,
    problem_type VARCHAR(20) NOT NULL, -- 'today', 'review'
    problem_id INTEGER NOT NULL,
    problem_title VARCHAR(200),
    problem_tags TEXT[], -- 전체 태그 배열
    tier VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 날짜+사용자+타입으로 유니크 제약
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_problems_unique ON daily_problems (date, username, problem_type, problem_id);
CREATE INDEX IF NOT EXISTS idx_date_username_type ON daily_problems (date, username, problem_type);

-- 3. solved.ac 문제 캐시 테이블 (API 호출 최적화)
CREATE TABLE IF NOT EXISTS problem_cache (
    problem_id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    tags TEXT[] NOT NULL, -- 전체 태그 배열
    tier VARCHAR(20),
    solved_count INTEGER,
    accepted_user_count INTEGER,
    average_tries DECIMAL(5,2),
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 캐시 만료 체크용 인덱스
CREATE INDEX IF NOT EXISTS idx_cached_at ON problem_cache (cached_at);

-- 4. 사용자 주간 통계 캐시 (solved.ac API 최적화)
CREATE TABLE IF NOT EXISTS user_weekly_stats (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    week_start DATE NOT NULL, -- 해당 주의 월요일
    problems_solved INTEGER DEFAULT 0,
    new_algorithms_learned INTEGER DEFAULT 0,
    consistency_score DECIMAL(3,1) DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_weekly_unique ON user_weekly_stats (username, week_start);
CREATE INDEX IF NOT EXISTS idx_username_week ON user_weekly_stats (username, week_start DESC);

-- 테스트 데이터 삽입
INSERT INTO user_activities (username, activity_type, problem_id, problem_title, metadata) VALUES
('dlgusxor12', 'feedback_request', 1000, '테스트 문제', '{"language": "python", "difficulty": "bronze"}'),
('dlgusxor12', 'problem_solved', 1001, '해결된 문제', '{"language": "cpp", "difficulty": "silver"}')
ON CONFLICT DO NOTHING;

INSERT INTO daily_problems (date, username, problem_type, problem_id, problem_title, problem_tags, tier) VALUES
(CURRENT_DATE, 'dlgusxor12', 'today', 30272, '가장 긴 증가하는 부분 수열 5', ARRAY['구현', '문자열', '많은 조건 분기'], 'Silver III'),
(CURRENT_DATE, 'dlgusxor12', 'today', 1463, '1로 만들기', ARRAY['다이나믹 프로그래밍'], 'Silver III')
ON CONFLICT DO NOTHING;

-- =============================================
-- MIGRATION SUPPORT & TEST DATA
-- =============================================

-- 임시 테스트 사용자 추가 (dlgusxor12 대체용)
INSERT INTO users (google_id, email, name, solvedac_username, profile_verified) VALUES
('test_google_id_dlgusxor12', 'dlgusxor12@test.com', '김중앙', 'dlgusxor12', TRUE)
ON CONFLICT (google_id) DO NOTHING;

-- 기존 username 기반 데이터를 user_id 기반으로 마이그레이션하기 위한 임시 컬럼 추가
-- TODO: Phase 2에서 실제 마이그레이션 스크립트 작성 예정

-- 향후 마이그레이션 시 username을 user_id로 변경할 예정:
-- ALTER TABLE user_activities ADD COLUMN user_id INTEGER REFERENCES users(user_id);
-- ALTER TABLE daily_problems ADD COLUMN user_id INTEGER REFERENCES users(user_id);
-- ALTER TABLE user_weekly_stats ADD COLUMN user_id INTEGER REFERENCES users(user_id);

-- 세션 정리용 함수 (만료된 세션 자동 삭제)
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
    DELETE FROM profile_verification WHERE expires_at < NOW() AND status = 'pending';
END;
$$ LANGUAGE plpgsql;

-- 자동 세션 정리를 위한 트리거 (선택적)
-- TODO: 프로덕션에서는 cron job으로 대체 예정
-- CAU Code 최적화된 DB 스키마

-- 1. 사용자 활동 로그 테이블
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
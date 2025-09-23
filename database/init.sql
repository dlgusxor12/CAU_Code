-- 테스트용 최소 테이블 정의
CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 테스트 데이터 삽입
INSERT INTO health_check (status) VALUES ('database_connected');
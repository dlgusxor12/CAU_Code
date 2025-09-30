-- Migration: Add organization column to users table
-- 랭킹 기능을 위해 사용자 소속 정보 추가

-- organization 컬럼 추가 (이미 존재하면 무시)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'organization'
    ) THEN
        ALTER TABLE users ADD COLUMN organization VARCHAR(100);

        -- 인덱스 추가 (소속별 랭킹 조회 최적화)
        CREATE INDEX idx_users_organization ON users (organization);

        -- 기존 사용자들에게 기본값 설정 (옵션)
        -- UPDATE users SET organization = '미분류' WHERE organization IS NULL;

        RAISE NOTICE 'organization column added to users table';
    ELSE
        RAISE NOTICE 'organization column already exists';
    END IF;
END $$;

-- 랭킹 조회 최적화를 위한 복합 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_users_verified_rating ON users (profile_verified, solvedac_rating DESC)
WHERE profile_verified = true AND solvedac_rating IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_org_verified_rating ON users (organization, profile_verified, solvedac_rating DESC)
WHERE profile_verified = true AND solvedac_rating IS NOT NULL;
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.utils.logging import LoggerMixin


class DatabaseService(LoggerMixin):
    """데이터베이스 서비스 클래스"""

    async def get_session(self) -> AsyncSession:
        """DB 세션 반환"""
        return AsyncSessionLocal()

    async def get_weekly_stats_from_db(self, username: str) -> Dict[str, Any]:
        """DB에서 이번 주 통계 조회"""
        try:
            async with await self.get_session() as session:
                # 1. 이번 주 해결한 문제 수
                problems_solved_query = text("""
                    SELECT COUNT(*) as count
                    FROM user_activities
                    WHERE username = :username
                    AND activity_type = 'problem_solved'
                    AND created_at >= date_trunc('week', CURRENT_DATE)
                """)

                # 2. 이번 주 새로운 알고리즘 학습 수
                new_algorithms_query = text("""
                    SELECT COUNT(DISTINCT tag) as count
                    FROM (
                        SELECT jsonb_array_elements_text(metadata->'tags') as tag
                        FROM user_activities
                        WHERE username = :username
                        AND activity_type = 'problem_solved'
                        AND created_at >= date_trunc('week', CURRENT_DATE)
                        AND metadata ? 'tags'
                    ) current_week_tags
                    WHERE tag NOT IN (
                        SELECT DISTINCT jsonb_array_elements_text(metadata->'tags')
                        FROM user_activities
                        WHERE username = :username
                        AND activity_type = 'problem_solved'
                        AND created_at < date_trunc('week', CURRENT_DATE)
                        AND metadata ? 'tags'
                    )
                """)

                # 3. 이번 주 피드백 요청 수
                feedback_requests_query = text("""
                    SELECT COUNT(*) as count
                    FROM user_activities
                    WHERE username = :username
                    AND activity_type = 'feedback_request'
                    AND created_at >= date_trunc('week', CURRENT_DATE)
                """)

                # 쿼리 실행
                problems_result = await session.execute(problems_solved_query, {"username": username})
                algorithms_result = await session.execute(new_algorithms_query, {"username": username})
                feedback_result = await session.execute(feedback_requests_query, {"username": username})

                problems_solved = problems_result.scalar() or 0
                new_algorithms = algorithms_result.scalar() or 0
                feedback_requests = feedback_result.scalar() or 0

                return {
                    "problems_solved": problems_solved,
                    "new_algorithms": new_algorithms,
                    "feedback_requests": feedback_requests
                }

        except Exception as e:
            self.log_error(f"DB weekly stats error for {username}", e)
            # DB 오류 시 기본값 반환
            return {
                "problems_solved": 0,
                "new_algorithms": 0,
                "feedback_requests": 0
            }

    async def get_daily_problems_from_db(self, username: str, problem_type: str, count: int = 2) -> List[Dict[str, Any]]:
        """DB에서 일별 고정 문제 조회"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    SELECT problem_id, problem_title, problem_tags, tier
                    FROM daily_problems
                    WHERE username = :username
                    AND problem_type = :problem_type
                    AND date = CURRENT_DATE
                    LIMIT :count
                """)

                result = await session.execute(query, {
                    "username": username,
                    "problem_type": problem_type,
                    "count": count
                })

                problems = []
                for row in result:
                    problems.append({
                        "problem_id": row.problem_id,
                        "title": row.problem_title,
                        "tags": row.problem_tags,  # 전체 태그 배열
                        "tier_name": row.tier
                    })

                return problems

        except Exception as e:
            self.log_error(f"DB daily problems error for {username}", e)
            return []

    async def get_recent_activities_from_db(self, username: str, limit: int = 3) -> List[Dict[str, Any]]:
        """DB에서 최근 활동 조회 (CAU Code 내 활동만)"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    SELECT activity_type, problem_id, problem_title, metadata, created_at
                    FROM user_activities
                    WHERE username = :username
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)

                result = await session.execute(query, {
                    "username": username,
                    "limit": limit
                })

                activities = []
                for row in result:
                    activity_text = ""
                    if row.activity_type == "feedback_request":
                        activity_text = f"코드 피드백을 요청했습니다: {row.problem_title}"
                    elif row.activity_type == "problem_solved":
                        activity_text = f"문제를 해결완료했습니다: {row.problem_title}"

                    activities.append({
                        "type": row.activity_type,
                        "problem_id": row.problem_id,
                        "description": activity_text,
                        "timestamp": row.created_at.isoformat(),
                        "metadata": row.metadata
                    })

                return activities

        except Exception as e:
            self.log_error(f"DB recent activities error for {username}", e)
            return []

    async def get_contribution_from_db(self, username: str, months: int = 6) -> List[Dict[str, Any]]:
        """DB에서 최근 N개월 해결 목록 조회 (CAU Code 활동만)"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    SELECT
                        DATE(created_at) as date,
                        COUNT(*) as solved_count
                    FROM user_activities
                    WHERE username = :username
                    AND activity_type = 'problem_solved'
                    AND created_at >= NOW() - INTERVAL :months MONTH
                    GROUP BY DATE(created_at)
                    ORDER BY date ASC
                """)

                result = await session.execute(query, {
                    "username": username,
                    "months": months
                })

                contribution_data = []
                for row in result:
                    contribution_data.append({
                        "date": row.date.isoformat(),
                        "solved_count": row.solved_count
                    })

                return contribution_data

        except Exception as e:
            self.log_error(f"DB contribution error for {username}", e)
            return []

    async def add_user_activity(self, username: str, activity_type: str, problem_id: int = None,
                              problem_title: str = None, submission_id: str = None,
                              metadata: Dict = None) -> bool:
        """사용자 활동 기록 추가"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    INSERT INTO user_activities
                    (username, activity_type, problem_id, problem_title, submission_id, metadata)
                    VALUES (:username, :activity_type, :problem_id, :problem_title, :submission_id, :metadata)
                """)

                await session.execute(query, {
                    "username": username,
                    "activity_type": activity_type,
                    "problem_id": problem_id,
                    "problem_title": problem_title,
                    "submission_id": submission_id,
                    "metadata": metadata
                })

                await session.commit()
                return True

        except Exception as e:
            self.log_error(f"Add user activity error for {username}", e)
            return False

    async def save_daily_problems_to_db(self, username: str, problem_type: str,
                                       problems: List[Dict[str, Any]]) -> bool:
        """오늘의 문제를 DB에 저장 (중복 방지)"""
        try:
            async with await self.get_session() as session:
                for problem in problems:
                    query = text("""
                        INSERT INTO daily_problems
                        (date, username, problem_type, problem_id, problem_title, problem_tags, tier)
                        VALUES (CURRENT_DATE, :username, :problem_type, :problem_id, :problem_title, :problem_tags, :tier)
                        ON CONFLICT (date, username, problem_type, problem_id) DO NOTHING
                    """)

                    await session.execute(query, {
                        "username": username,
                        "problem_type": problem_type,
                        "problem_id": problem.get("problem_id"),
                        "problem_title": problem.get("title"),
                        "problem_tags": problem.get("tags", []),
                        "tier": problem.get("tier_name")
                    })

                await session.commit()
                return True

        except Exception as e:
            self.log_error(f"Save daily problems error for {username}", e)
            return False

    async def get_global_ranking(self, limit: int = 100) -> List[Dict[str, Any]]:
        """전체 랭킹 조회 (solved.ac 레이팅 기준)"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    SELECT
                        u.solvedac_username,
                        u.organization,
                        u.solvedac_tier,
                        u.solvedac_rating,
                        u.solvedac_solved_count,
                        COALESCE(cau_solved.solved_count, 0) as cau_solved_count,
                        ROW_NUMBER() OVER (ORDER BY u.solvedac_rating DESC NULLS LAST) as rank
                    FROM users u
                    LEFT JOIN (
                        SELECT username, COUNT(*) as solved_count
                        FROM user_activities
                        WHERE activity_type = 'problem_solved'
                        GROUP BY username
                    ) cau_solved ON u.solvedac_username = cau_solved.username
                    WHERE u.profile_verified = true
                    AND u.solvedac_rating IS NOT NULL
                    ORDER BY u.solvedac_rating DESC
                    LIMIT :limit
                """)

                result = await session.execute(query, {"limit": limit})

                rankings = []
                for row in result:
                    rankings.append({
                        "rank": row.rank,
                        "username": row.solvedac_username,
                        "organization": row.organization or "미분류",
                        "tier": row.solvedac_tier or "Unrated",
                        "rating": row.solvedac_rating or 0,
                        "total_solved": row.solvedac_solved_count or 0,
                        "cau_solved": row.cau_solved_count
                    })

                return rankings

        except Exception as e:
            self.log_error("Get global ranking error", e)
            return []

    async def get_organization_ranking(self, organization: str, limit: int = 100) -> List[Dict[str, Any]]:
        """소속별 랭킹 조회"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    SELECT
                        u.solvedac_username,
                        u.organization,
                        u.solvedac_tier,
                        u.solvedac_rating,
                        u.solvedac_solved_count,
                        COALESCE(cau_solved.solved_count, 0) as cau_solved_count,
                        ROW_NUMBER() OVER (ORDER BY u.solvedac_rating DESC NULLS LAST) as rank
                    FROM users u
                    LEFT JOIN (
                        SELECT username, COUNT(*) as solved_count
                        FROM user_activities
                        WHERE activity_type = 'problem_solved'
                        GROUP BY username
                    ) cau_solved ON u.solvedac_username = cau_solved.username
                    WHERE u.profile_verified = true
                    AND u.organization = :organization
                    AND u.solvedac_rating IS NOT NULL
                    ORDER BY u.solvedac_rating DESC
                    LIMIT :limit
                """)

                result = await session.execute(query, {"organization": organization, "limit": limit})

                rankings = []
                for row in result:
                    rankings.append({
                        "rank": row.rank,
                        "username": row.solvedac_username,
                        "organization": row.organization or "미분류",
                        "tier": row.solvedac_tier or "Unrated",
                        "rating": row.solvedac_rating or 0,
                        "total_solved": row.solvedac_solved_count or 0,
                        "cau_solved": row.cau_solved_count
                    })

                return rankings

        except Exception as e:
            self.log_error(f"Get organization ranking error for {organization}", e)
            return []

    async def get_my_rank_info(self, username: str) -> Dict[str, Any]:
        """내 랭킹 정보 조회"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    WITH ranked_users AS (
                        SELECT
                            u.solvedac_username,
                            u.organization,
                            u.solvedac_tier,
                            u.solvedac_rating,
                            u.solvedac_solved_count,
                            ROW_NUMBER() OVER (ORDER BY u.solvedac_rating DESC NULLS LAST) as global_rank
                        FROM users u
                        WHERE u.profile_verified = true
                        AND u.solvedac_rating IS NOT NULL
                    )
                    SELECT * FROM ranked_users WHERE solvedac_username = :username
                """)

                result = await session.execute(query, {"username": username})
                row = result.first()

                if not row:
                    return {}

                return {
                    "username": row.solvedac_username,
                    "organization": row.organization or "미분류",
                    "tier": row.solvedac_tier or "Unrated",
                    "rating": row.solvedac_rating or 0,
                    "total_solved": row.solvedac_solved_count or 0,
                    "global_rank": row.global_rank
                }

        except Exception as e:
            self.log_error(f"Get my rank info error for {username}", e)
            return {}

    async def get_ranking_stats(self) -> Dict[str, Any]:
        """랭킹 통계 조회 (총 사용자 수, 평균 해결 문제 수 등)"""
        try:
            async with await self.get_session() as session:
                # 총 사용자 수
                total_users_query = text("""
                    SELECT COUNT(*) as count
                    FROM users
                    WHERE profile_verified = true
                """)

                # 평균 해결 문제 수
                avg_solved_query = text("""
                    SELECT AVG(solvedac_solved_count)::INTEGER as avg_solved
                    FROM users
                    WHERE profile_verified = true
                    AND solvedac_solved_count IS NOT NULL
                """)

                total_result = await session.execute(total_users_query)
                avg_result = await session.execute(avg_solved_query)

                total_users = total_result.scalar() or 0
                avg_solved = avg_result.scalar() or 0

                return {
                    "total_users": total_users,
                    "avg_solved_count": avg_solved
                }

        except Exception as e:
            self.log_error("Get ranking stats error", e)
            return {
                "total_users": 0,
                "avg_solved_count": 0
            }

    async def get_organization_user_count(self, organization: str) -> int:
        """특정 소속의 사용자 수 조회"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    SELECT COUNT(*) as count
                    FROM users
                    WHERE profile_verified = true
                    AND organization = :organization
                """)

                result = await session.execute(query, {"organization": organization})
                return result.scalar() or 0

        except Exception as e:
            self.log_error(f"Get organization user count error for {organization}", e)
            return 0

    async def update_user_solvedac_profile(self, username: str, tier: str, rating: int, solved_count: int) -> bool:
        """사용자의 solved.ac 프로필 정보 업데이트 (실시간 동기화)"""
        try:
            async with await self.get_session() as session:
                query = text("""
                    UPDATE users
                    SET solvedac_tier = :tier,
                        solvedac_rating = :rating,
                        solvedac_solved_count = :solved_count,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE solvedac_username = :username
                    AND profile_verified = true
                """)

                result = await session.execute(query, {
                    "username": username,
                    "tier": tier,
                    "rating": rating,
                    "solved_count": solved_count
                })

                await session.commit()

                if result.rowcount > 0:
                    self.logger.info(f"Updated solvedac profile for {username}: tier={tier}, rating={rating}, solved={solved_count}")
                    return True
                else:
                    self.logger.warning(f"No user found to update: {username}")
                    return False

        except Exception as e:
            self.log_error(f"Update user solvedac profile error for {username}", e)
            return False
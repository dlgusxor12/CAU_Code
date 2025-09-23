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
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from app.clients.solvedac_client import SolvedACClient
from app.utils.helpers import (
    format_solved_ac_user_data,
    format_solved_ac_problem_data,
    tier_id_to_name,
    generate_contribution_graph_data,
    calculate_tier_range_for_recommendations,
    estimate_problem_solving_time
)
from app.utils.cache import CacheManager
from app.utils.logging import LoggerMixin
from app.core.exceptions import UserNotFoundError, SolvedACAPIError


class SolvedACService(LoggerMixin):
    def __init__(self):
        self.client = SolvedACClient()
        self.cache = CacheManager()

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """사용자 정보 조회 (캐시 우선)"""
        try:
            # 캐시에서 먼저 확인
            cached_data = self.cache.get_user_info(username)
            if cached_data:
                self.log_performance("get_user_info_cached", 0.001, {"username": username})
                return cached_data

            start_time = datetime.now()

            # solved.ac API 호출
            raw_data = await self.client.get_user_info(username)
            user_data = format_solved_ac_user_data(raw_data)

            # 캐시에 저장 (10분)
            self.cache.set_user_info(username, user_data, ttl=600)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_user_info_api", duration, {"username": username})

            return user_data

        except Exception as e:
            self.log_error(f"Failed to get user info for {username}", e)
            raise

    async def get_user_solved_problems(self, username: str) -> List[Dict[str, Any]]:
        """사용자가 해결한 문제 목록"""
        try:
            cache_key = f"solved_problems_{username}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

            start_time = datetime.now()
            raw_data = await self.client.get_user_problems(username)

            problems = []
            for item in raw_data.get("items", []):
                problem_data = format_solved_ac_problem_data(item)
                problems.append(problem_data)

            # 캐시에 저장 (30분)
            self.cache.set(cache_key, problems, ttl=1800)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_user_solved_problems", duration, {
                "username": username,
                "problem_count": len(problems)
            })

            return problems

        except Exception as e:
            self.log_error(f"Failed to get solved problems for {username}", e)
            raise

    async def get_todays_problems(self, username: str, count: int = 2) -> List[Dict[str, Any]]:
        """오늘의 문제 추천"""
        try:
            user_info = await self.get_user_info(username)
            user_tier = user_info.get("tier", 0)
            tier_range = calculate_tier_range_for_recommendations(user_tier)

            # 사용자 티어 기반 문제 검색
            start_time = datetime.now()
            raw_problems = await self.client.search_problems(
                tier=tier_range,
                count=count * 3,  # 여분으로 더 가져와서 필터링
                sort="random"
            )

            recommended_problems = []
            for item in raw_problems.get("items", [])[:count]:
                problem_data = format_solved_ac_problem_data(item)

                # 추가 정보 계산
                problem_data.update({
                    "estimated_time": estimate_problem_solving_time(
                        problem_data["tier"], user_tier
                    ),
                    "recommendation_reason": self._generate_recommendation_reason(
                        problem_data, user_info
                    )
                })

                recommended_problems.append(problem_data)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_todays_problems", duration, {
                "username": username,
                "count": len(recommended_problems)
            })

            return recommended_problems

        except Exception as e:
            self.log_error(f"Failed to get today's problems for {username}", e)
            raise

    async def get_review_problems(self, username: str, count: int = 2) -> List[Dict[str, Any]]:
        """복습할 문제 추천"""
        try:
            user_info = await self.get_user_info(username)
            user_tier = user_info.get("tier", 0)

            # 틀린 문제 검색 시도
            start_time = datetime.now()

            try:
                # 시도했지만 해결하지 못한 문제 검색
                raw_problems = await self.client.get_user_unsolved_problems(username)

                review_problems = []
                for item in raw_problems.get("items", [])[:count]:
                    problem_data = format_solved_ac_problem_data(item)
                    problem_data.update({
                        "review_reason": "이전에 시도했던 문제입니다",
                        "last_attempt": None,  # 실제로는 API에서 가져와야 함
                        "mistake_count": random.randint(1, 3)  # 더미 데이터
                    })
                    review_problems.append(problem_data)

            except Exception:
                # 실패하면 비슷한 티어의 문제로 대체
                tier_range = f"s{max(1, user_tier-2)}..s{min(10, user_tier+1)}"
                raw_problems = await self.client.search_problems(
                    tier=tier_range,
                    count=count,
                    sort="random"
                )

                review_problems = []
                for item in raw_problems.get("items", []):
                    problem_data = format_solved_ac_problem_data(item)
                    problem_data.update({
                        "review_reason": "비슷한 유형의 문제를 연습해보세요",
                        "last_attempt": None,
                        "mistake_count": 0
                    })
                    review_problems.append(problem_data)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_review_problems", duration, {
                "username": username,
                "count": len(review_problems)
            })

            return review_problems

        except Exception as e:
            self.log_error(f"Failed to get review problems for {username}", e)
            raise

    async def get_contribution_graph(self, username: str, year: int = 2025) -> List[Dict[str, Any]]:
        """기여도 그래프 데이터"""
        try:
            cache_key = f"contribution_{username}_{year}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

            # 실제로는 solved.ac API에서 일별 해결 데이터를 가져와야 하지만
            # 현재 API 제한으로 더미 데이터 생성
            contribution_data = generate_contribution_graph_data(year)

            # 실제 사용자의 해결한 문제 수를 바탕으로 일부 날짜에 데이터 추가
            user_info = await self.get_user_info(username)
            solved_count = user_info.get("solved_count", 0)

            # 랜덤하게 일부 날짜에 문제 해결 데이터 배치
            dates_with_activity = random.sample(
                range(len(contribution_data)),
                min(solved_count, len(contribution_data) // 3)
            )

            for idx in dates_with_activity:
                contribution_data[idx]["solved_count"] = random.randint(1, 5)

            # 캐시에 저장 (1시간)
            self.cache.set(cache_key, contribution_data, ttl=3600)

            return contribution_data

        except Exception as e:
            self.log_error(f"Failed to get contribution graph for {username}", e)
            raise

    async def get_recent_activities(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 활동 내역"""
        try:
            # 실제로는 solved.ac API에서 최근 제출 내역을 가져와야 하지만
            # 현재 API 제한으로 더미 데이터 생성
            activities = []

            user_info = await self.get_user_info(username)
            solved_count = user_info.get("solved_count", 0)

            # 최근 활동 더미 데이터 생성
            for i in range(min(limit, 5)):
                activity_time = datetime.now() - timedelta(hours=random.randint(1, 72))

                if i % 2 == 0:
                    activities.append({
                        "type": "solved",
                        "description": f"문제 {1000 + random.randint(1, 999)} 해결",
                        "timestamp": activity_time,
                        "problem_id": 1000 + random.randint(1, 999)
                    })
                else:
                    activities.append({
                        "type": "feedback",
                        "description": f"문제 {1000 + random.randint(1, 999)} 코드 피드백",
                        "timestamp": activity_time,
                        "problem_id": 1000 + random.randint(1, 999)
                    })

            return activities

        except Exception as e:
            self.log_error(f"Failed to get recent activities for {username}", e)
            raise

    async def get_weekly_stats(self, username: str) -> Dict[str, Any]:
        """이번 주 통계"""
        try:
            cache_key = f"weekly_stats_{username}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

            user_info = await self.get_user_info(username)

            # 더미 데이터 생성 (실제로는 API에서 계산)
            stats = {
                "problems_solved": random.randint(3, 12),
                "new_algorithms": random.randint(1, 3),
                "average_difficulty": round(random.uniform(1.5, 4.5), 1),
                "consistency_score": round(random.uniform(0.6, 0.95), 2),
                "improvement_rate": round(random.uniform(0.05, 0.25), 2)
            }

            # 캐시에 저장 (1시간)
            self.cache.set(cache_key, stats, ttl=3600)

            return stats

        except Exception as e:
            self.log_error(f"Failed to get weekly stats for {username}", e)
            raise

    def _generate_recommendation_reason(self, problem_data: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """추천 이유 생성"""
        problem_tier = problem_data.get("tier", 0)
        user_tier = user_info.get("tier", 0)

        if problem_tier == user_tier:
            return "현재 티어에 적합한 문제입니다"
        elif problem_tier == user_tier + 1:
            return "다음 티어 도전을 위한 문제입니다"
        elif problem_tier == user_tier - 1:
            return "기본기 다지기에 좋은 문제입니다"
        else:
            return "새로운 유형의 문제에 도전해보세요"

    async def verify_problem_solved(self, username: str, problem_id: int) -> bool:
        """문제 해결 여부 검증"""
        try:
            return await self.client.verify_problem_solved(username, problem_id)
        except Exception as e:
            self.log_error(f"Failed to verify problem {problem_id} for {username}", e)
            return False

    async def get_problem_info(self, problem_id: int) -> Dict[str, Any]:
        """문제 정보 조회"""
        try:
            # 캐시에서 먼저 확인
            cached_data = self.cache.get_problem_info(problem_id)
            if cached_data:
                return cached_data

            start_time = datetime.now()
            raw_data = await self.client.get_problem_info(problem_id)
            problem_data = format_solved_ac_problem_data(raw_data)

            # 캐시에 저장 (1시간)
            self.cache.set_problem_info(problem_id, problem_data, ttl=3600)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_problem_info", duration, {"problem_id": problem_id})

            return problem_data

        except Exception as e:
            self.log_error(f"Failed to get problem info for {problem_id}", e)
            raise
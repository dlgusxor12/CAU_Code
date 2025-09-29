from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
import hashlib

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
            # 캐시에서 조회
            from app.utils.cache import cache_key_for_user, cache
            cache_key = cache_key_for_user(username, "solved_problems")
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            start_time = datetime.now()
            raw_data = await self.client.get_user_problems(username)

            problems = []
            for item in raw_data.get("items", []):
                problem_data = format_solved_ac_problem_data(item)
                problems.append(problem_data)

            # 캐시에 저장 (30분)
            cache.set(cache_key, problems, ttl_seconds=1800)

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

            # 사용자 티어 기반 문제 검색 (날짜별 고정)
            start_time = datetime.now()
            raw_problems = await self.client.search_problems(
                tier=tier_range,
                count=count * 10,  # 더 많이 가져와서 날짜 기반 선택
                sort="id"  # ID 순 정렬로 일관성 보장
            )

            # 날짜 기반 결정론적 문제 선택
            today = datetime.now().strftime("%Y-%m-%d")
            seed_string = f"{username}_{today}"
            seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

            available_problems = raw_problems.get("items", [])
            if len(available_problems) >= count:
                # 해시 기반으로 결정론적 선택
                selected_indices = []
                for i in range(count):
                    index = (seed_hash + i * 7) % len(available_problems)  # 7로 곱해서 분산
                    while index in selected_indices:  # 중복 방지
                        index = (index + 1) % len(available_problems)
                    selected_indices.append(index)

                selected_problems = [available_problems[i] for i in selected_indices]
            else:
                selected_problems = available_problems[:count]

            recommended_problems = []
            for item in selected_problems:
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
        """복습할 문제 추천 - 틀린 문제 개수에 따른 전략"""
        try:
            user_info = await self.get_user_info(username)
            user_tier = user_info.get("tier", 0)
            start_time = datetime.now()

            # 1. 틀린 문제들 가져오기
            unsolved_problems = []
            try:
                raw_unsolved = await self.client.get_user_unsolved_problems(username)
                unsolved_items = raw_unsolved.get("items", [])

                # 날짜 기반 결정론적 선택 (오늘의 문제와 동일 방식)
                if unsolved_items:
                    today = datetime.now().strftime("%Y-%m-%d")
                    seed_string = f"{username}_review_unsolved_{today}"
                    seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

                    # 틀린 문제들을 날짜별 고정 선택
                    selected_unsolved = []
                    for i in range(min(len(unsolved_items), count)):
                        index = (seed_hash + i * 5) % len(unsolved_items)
                        while index in [unsolved_items.index(item) for item in selected_unsolved]:
                            index = (index + 1) % len(unsolved_items)
                        selected_unsolved.append(unsolved_items[index])

                    for item in selected_unsolved:
                        problem_data = format_solved_ac_problem_data(item)
                        problem_data.update({
                            "review_reason": "이전에 시도했지만 틀린 문제입니다",
                            "review_type": "unsolved",
                            "last_attempt": None,
                            "mistake_count": random.randint(1, 3)
                        })
                        unsolved_problems.append(problem_data)

            except Exception as e:
                self.log_error(f"Failed to get unsolved problems for {username}", e)

            # 2. 해결한 문제들 가져오기 (부족한 경우 사용)
            solved_problems = []
            if len(unsolved_problems) < count:
                try:
                    raw_solved = await self.client.get_user_problems(username)
                    solved_items = raw_solved.get("items", [])

                    if solved_items:
                        today = datetime.now().strftime("%Y-%m-%d")
                        seed_string = f"{username}_review_solved_{today}"
                        seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

                        needed_count = count - len(unsolved_problems)
                        selected_solved = []

                        for i in range(min(len(solved_items), needed_count)):
                            index = (seed_hash + i * 11) % len(solved_items)
                            while index in [solved_items.index(item) for item in selected_solved]:
                                index = (index + 1) % len(solved_items)
                            selected_solved.append(solved_items[index])

                        for item in selected_solved:
                            problem_data = format_solved_ac_problem_data(item)
                            problem_data.update({
                                "review_reason": "이전에 해결한 문제를 다시 복습해보세요",
                                "review_type": "solved",
                                "last_attempt": None,
                                "mistake_count": 0
                            })
                            solved_problems.append(problem_data)

                except Exception as e:
                    self.log_error(f"Failed to get solved problems for {username}", e)

            # 3. 최종 결과 조합
            review_problems = unsolved_problems + solved_problems

            # 4. 여전히 부족한 경우 비슷한 티어 문제로 대체
            if len(review_problems) < count:
                remaining_count = count - len(review_problems)
                tier_range = calculate_tier_range_for_recommendations(user_tier)

                try:
                    raw_fallback = await self.client.search_problems(
                        tier=tier_range,
                        count=remaining_count * 5,
                        sort="id"
                    )

                    fallback_items = raw_fallback.get("items", [])
                    if fallback_items:
                        today = datetime.now().strftime("%Y-%m-%d")
                        seed_string = f"{username}_review_fallback_{today}"
                        seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

                        for i in range(min(len(fallback_items), remaining_count)):
                            index = (seed_hash + i * 13) % len(fallback_items)
                            item = fallback_items[index]
                            problem_data = format_solved_ac_problem_data(item)
                            problem_data.update({
                                "review_reason": "실력 향상을 위한 추천 문제입니다",
                                "review_type": "recommendation",
                                "last_attempt": None,
                                "mistake_count": 0
                            })
                            review_problems.append(problem_data)

                except Exception as e:
                    self.log_error(f"Failed to get fallback problems for {username}", e)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_review_problems", duration, {
                "username": username,
                "total_count": len(review_problems),
                "unsolved_count": len(unsolved_problems),
                "solved_count": len(solved_problems)
            })

            return review_problems[:count]  # 정확히 count 개수만 반환

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
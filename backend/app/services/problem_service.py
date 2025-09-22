from typing import Dict, List, Optional, Any
from datetime import datetime
import random

from app.clients.solvedac_client import SolvedACClient
from app.clients.openai_client import OpenAIClient
from app.services.solvedac_service import SolvedACService
from app.utils.helpers import (
    calculate_tier_range_for_recommendations,
    calculate_recommendation_accuracy,
    format_solved_ac_problem_data,
    tier_id_to_name
)
from app.utils.cache import CacheManager
from app.utils.logging import LoggerMixin
from app.schemas.problem import RecommendationMode, ProblemFilterRequest


class ProblemService(LoggerMixin):
    def __init__(self):
        self.solvedac_client = SolvedACClient()
        self.openai_client = OpenAIClient()
        self.solvedac_service = SolvedACService()
        self.cache = CacheManager()

    async def get_problem_recommendations(
        self,
        username: str,
        mode: RecommendationMode,
        count: int = 10,
        filters: Optional[ProblemFilterRequest] = None
    ) -> Dict[str, Any]:
        """문제 추천 (적응형, 유사, 도전 모드)"""
        try:
            # 캐시 키 생성
            filter_dict = filters.dict() if filters else {}
            cached_data = self.cache.get_recommendations(username, mode.value, filter_dict)
            if cached_data:
                self.log_performance("get_recommendations_cached", 0.001, {
                    "username": username, "mode": mode.value
                })
                return cached_data

            start_time = datetime.now()

            # 사용자 정보 조회
            user_info = await self.solvedac_service.get_user_info(username)
            user_tier = user_info.get("tier", 0)
            user_rating = user_info.get("rating", 0)
            solved_count = user_info.get("solved_count", 0)

            # 모드별 추천 로직
            if mode == RecommendationMode.ADAPTIVE:
                problems = await self._get_adaptive_recommendations(
                    user_tier, user_rating, solved_count, count, filters
                )
            elif mode == RecommendationMode.SIMILAR:
                problems = await self._get_similar_problems(
                    username, user_tier, count, filters
                )
            elif mode == RecommendationMode.CHALLENGE:
                problems = await self._get_challenge_problems(
                    user_tier, count, filters
                )
            else:
                problems = []

            # 추천 정확도 계산
            accuracy = calculate_recommendation_accuracy(user_tier, problems)

            result = {
                "problems": problems,
                "total_count": len(problems),
                "recommendation_accuracy": accuracy,
                "mode_used": mode,
                "filters_applied": filter_dict,
                "user_tier": user_tier,
                "user_tier_name": tier_id_to_name(user_tier)
            }

            # 캐시에 저장 (15분)
            self.cache.set_recommendations(username, mode.value, filter_dict, result, ttl=900)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_problem_recommendations", duration, {
                "username": username,
                "mode": mode.value,
                "count": len(problems)
            })

            return result

        except Exception as e:
            self.log_error(f"Failed to get recommendations for {username}", e)
            raise

    async def _get_adaptive_recommendations(
        self,
        user_tier: int,
        user_rating: int,
        solved_count: int,
        count: int,
        filters: Optional[ProblemFilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """AI 기반 적응형 추천"""
        try:
            # OpenAI로 추천 알고리즘 태그 받기
            recommended_tags = await self.openai_client.recommend_problems(
                user_tier, user_rating, solved_count, count
            )

            problems = []
            problems_per_tag = max(1, count // len(recommended_tags))

            for tag in recommended_tags[:5]:  # 최대 5개 태그
                try:
                    # 티어 범위 계산
                    tier_range = calculate_tier_range_for_recommendations(user_tier)

                    # 필터 적용
                    search_params = {
                        "algorithm": tag,
                        "tier": tier_range,
                        "count": problems_per_tag * 2,  # 여분으로 더 가져오기
                        "sort": "random"
                    }

                    # 사용자 정의 필터 적용
                    if filters:
                        search_params.update(self._apply_filters(filters, search_params))

                    # 문제 검색
                    raw_problems = await self.solvedac_client.search_problems(**search_params)

                    for item in raw_problems.get("items", [])[:problems_per_tag]:
                        problem_data = format_solved_ac_problem_data(item)
                        problem_data["recommendation_reason"] = f"AI가 추천하는 {tag} 유형 문제"
                        problem_data["confidence_score"] = random.uniform(0.7, 0.95)
                        problems.append(problem_data)

                        if len(problems) >= count:
                            break

                except Exception as e:
                    self.logger.warning(f"Failed to get problems for tag {tag}: {e}")
                    continue

                if len(problems) >= count:
                    break

            return problems[:count]

        except Exception as e:
            self.log_error("Failed to get adaptive recommendations", e)
            return []

    async def _get_similar_problems(
        self,
        username: str,
        user_tier: int,
        count: int,
        filters: Optional[ProblemFilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """유사한 유형 문제 추천"""
        try:
            # 사용자가 최근에 푼 문제들의 알고리즘 태그 분석
            solved_problems = await self.solvedac_service.get_user_solved_problems(username)

            # 최근 문제들에서 알고리즘 태그 추출
            recent_tags = set()
            for problem in solved_problems[-20:]:  # 최근 20개 문제
                tags = problem.get("tags", [])
                recent_tags.update(tags[:2])  # 상위 2개 태그만

            if not recent_tags:
                recent_tags = ["implementation", "math"]  # 기본 태그

            problems = []
            problems_per_tag = max(1, count // min(len(recent_tags), 3))

            for tag in list(recent_tags)[:3]:  # 최대 3개 태그
                try:
                    tier_range = f"s{max(1, user_tier-1)}..g{min(15, user_tier+2)}"

                    search_params = {
                        "algorithm": tag,
                        "tier": tier_range,
                        "count": problems_per_tag * 2,
                        "sort": "random"
                    }

                    if filters:
                        search_params.update(self._apply_filters(filters, search_params))

                    raw_problems = await self.solvedac_client.search_problems(**search_params)

                    for item in raw_problems.get("items", [])[:problems_per_tag]:
                        problem_data = format_solved_ac_problem_data(item)
                        problem_data["recommendation_reason"] = f"최근 푼 {tag} 유형과 유사한 문제"
                        problem_data["confidence_score"] = random.uniform(0.6, 0.85)
                        problems.append(problem_data)

                        if len(problems) >= count:
                            break

                except Exception as e:
                    self.logger.warning(f"Failed to get similar problems for tag {tag}: {e}")
                    continue

                if len(problems) >= count:
                    break

            return problems[:count]

        except Exception as e:
            self.log_error(f"Failed to get similar problems for {username}", e)
            return []

    async def _get_challenge_problems(
        self,
        user_tier: int,
        count: int,
        filters: Optional[ProblemFilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """도전 모드 (어려운 문제) 추천"""
        try:
            # 현재 티어보다 1-3티어 높은 문제들
            challenge_tier_min = user_tier + 1
            challenge_tier_max = min(30, user_tier + 3)

            tier_range = f"tier:{challenge_tier_min}..{challenge_tier_max}"

            search_params = {
                "tier": tier_range,
                "count": count * 2,
                "sort": "random"
            }

            if filters:
                search_params.update(self._apply_filters(filters, search_params))

            raw_problems = await self.solvedac_client.search_problems(**search_params)

            problems = []
            for item in raw_problems.get("items", [])[:count]:
                problem_data = format_solved_ac_problem_data(item)
                tier_diff = problem_data["tier"] - user_tier
                problem_data["recommendation_reason"] = f"현재 티어보다 {tier_diff}단계 높은 도전 문제"
                problem_data["confidence_score"] = random.uniform(0.4, 0.7)
                problems.append(problem_data)

            return problems

        except Exception as e:
            self.log_error("Failed to get challenge problems", e)
            return []

    def _apply_filters(
        self,
        filters: ProblemFilterRequest,
        search_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """필터 적용"""
        updated_params = {}

        # 티어 필터
        if filters.tier_min is not None or filters.tier_max is not None:
            tier_min = filters.tier_min or 0
            tier_max = filters.tier_max or 31
            updated_params["tier"] = f"tier:{tier_min}..{tier_max}"

        # 알고리즘 필터
        if filters.algorithm:
            updated_params["algorithm"] = filters.algorithm

        # 난이도 클래스 필터 (solved.ac에서는 class로 검색)
        if filters.difficulty_class:
            updated_params["query"] = f"class:{filters.difficulty_class}"

        # 해결자 수 필터
        if filters.solved_count_min is not None or filters.solved_count_max is not None:
            # solved.ac API에서는 직접 지원하지 않으므로 후처리에서 필터링
            pass

        return updated_params

    async def get_problem_stats(self, username: str) -> Dict[str, Any]:
        """문제 추천 통계"""
        try:
            user_info = await self.solvedac_service.get_user_info(username)
            user_tier = user_info.get("tier", 0)

            # 더미 통계 데이터
            stats = {
                "total_problems_available": random.randint(1000, 5000),
                "problems_recommended_this_week": random.randint(20, 50),
                "recommendation_accuracy": round(random.uniform(0.75, 0.95), 2),
                "user_tier_range": {
                    "min_tier": max(0, user_tier - 3),
                    "max_tier": min(31, user_tier + 3),
                    "current_tier": user_tier
                }
            }

            return stats

        except Exception as e:
            self.log_error(f"Failed to get problem stats for {username}", e)
            raise

    async def search_problems_with_filters(
        self,
        filters: ProblemFilterRequest,
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """필터를 적용한 문제 검색"""
        try:
            search_params = {
                "count": count,
                "sort": "random"
            }

            # 필터 적용
            search_params.update(self._apply_filters(filters, search_params))

            raw_problems = await self.solvedac_client.search_problems(**search_params)

            problems = []
            for item in raw_problems.get("items", []):
                problem_data = format_solved_ac_problem_data(item)

                # 해결자 수 필터링 (후처리)
                if filters.solved_count_min is not None:
                    if problem_data.get("accepted_user_count", 0) < filters.solved_count_min:
                        continue

                if filters.solved_count_max is not None:
                    if problem_data.get("accepted_user_count", 0) > filters.solved_count_max:
                        continue

                problems.append(problem_data)

            return problems

        except Exception as e:
            self.log_error("Failed to search problems with filters", e)
            raise

    async def get_filter_options(self) -> Dict[str, Any]:
        """필터 옵션 정보"""
        try:
            # 더미 데이터 (실제로는 solved.ac API에서 가져와야 함)
            options = {
                "available_tiers": [
                    {"tier_id": i, "tier_name": tier_id_to_name(i)}
                    for i in range(32)
                ],
                "available_algorithms": [
                    {"tag_name": "implementation", "problem_count": 1500},
                    {"tag_name": "math", "problem_count": 1200},
                    {"tag_name": "greedy", "problem_count": 800},
                    {"tag_name": "dp", "problem_count": 700},
                    {"tag_name": "graph", "problem_count": 600},
                    {"tag_name": "string", "problem_count": 500},
                    {"tag_name": "brute_force", "problem_count": 450}
                ],
                "difficulty_classes": [1, 2, 3, 4, 5],
                "min_problem_id": 1000,
                "max_problem_id": 30000
            }

            return options

        except Exception as e:
            self.log_error("Failed to get filter options", e)
            raise
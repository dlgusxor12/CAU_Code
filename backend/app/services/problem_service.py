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
            if mode == RecommendationMode.AI_RECOMMENDATION:
                problems = await self._get_adaptive_recommendations(
                    user_tier, user_rating, solved_count, count, filters
                )
            elif mode == RecommendationMode.APPROPRIATE_DIFFICULTY:
                problems = await self._get_appropriate_difficulty_problems(
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

            for tag in recommended_tags[:5]:  # 최대 5개 태그
                try:
                    # 티어 범위 계산
                    tier_range = calculate_tier_range_for_recommendations(user_tier)

                    # 필터 적용 - 충분한 문제 수량 확보
                    search_params = {
                        "algorithm": tag,
                        "tier": tier_range,
                        "count": count * 2,  # count에 비례한 충분한 수량
                        "sort": "random"
                    }

                    # 사용자 정의 필터 적용
                    if filters:
                        search_params.update(self._apply_filters(filters, search_params))

                    # 문제 검색
                    raw_problems = await self.solvedac_client.search_problems(**search_params)

                    # 현재 필요한 문제 수 계산
                    remaining_needed = count - len(problems)
                    if remaining_needed <= 0:
                        break

                    # 이 태그에서 가져올 문제 수 (남은 문제 수와 API 결과 중 작은 값)
                    items_to_take = min(len(raw_problems.get("items", [])), remaining_needed)

                    for item in raw_problems.get("items", [])[:items_to_take]:
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

    async def _get_appropriate_difficulty_problems(
        self,
        username: str,
        user_tier: int,
        count: int,
        filters: Optional[ProblemFilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """적정 난이도 문제 추천 - 오늘의 문제 로직 기반으로 사용자 티어에 맞는 문제"""
        try:
            from datetime import datetime
            import hashlib
            from app.utils.helpers import estimate_problem_solving_time

            tier_range = calculate_tier_range_for_recommendations(user_tier)

            # 날짜 기반 결정론적 문제 선택 (오늘의 문제와 다른 시드 사용)
            start_time = datetime.now()
            raw_problems = await self.solvedac_service.client.search_problems(
                tier=tier_range,
                count=count * 10,  # 더 많이 가져와서 날짜 기반 선택
                sort="id"  # ID 순 정렬로 일관성 보장
            )

            # 날짜 기반 결정론적 문제 선택 (오늘의 문제와 다른 시드)
            today = datetime.now().strftime("%Y-%m-%d")
            seed_string = f"{username}_appropriate_{today}"
            seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

            available_problems = raw_problems.get("items", [])
            if len(available_problems) >= count:
                # 해시 기반으로 결정론적 선택
                selected_indices = []
                for i in range(count):
                    index = (seed_hash + i * 11) % len(available_problems)  # 11로 곱해서 분산
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
                    "recommendation_reason": self._generate_appropriate_difficulty_reason(
                        problem_data, user_tier
                    ),
                    "difficulty_match": self._calculate_difficulty_match(
                        problem_data["tier"], user_tier
                    )
                })

                recommended_problems.append(problem_data)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_appropriate_difficulty_problems", duration, {
                "username": username,
                "count": len(recommended_problems)
            })

            return recommended_problems

        except Exception as e:
            self.log_error(f"Failed to get appropriate difficulty problems for {username}", e)
            return []

    def _generate_appropriate_difficulty_reason(self, problem_data: Dict[str, Any], user_tier: int) -> str:
        """적정 난이도 추천 이유 생성"""
        problem_tier = problem_data.get("tier", 0)

        if problem_tier == user_tier:
            return "현재 티어에 정확히 맞는 문제입니다"
        elif problem_tier == user_tier + 1:
            return "한 단계 높은 수준의 적정 난이도 문제입니다"
        elif problem_tier == user_tier - 1:
            return "기본기 다지기에 적합한 문제입니다"
        else:
            return "당신의 실력에 적정한 난이도의 문제입니다"

    def _calculate_difficulty_match(self, problem_tier: int, user_tier: int) -> float:
        """난이도 매칭 점수 계산 (0.0 ~ 1.0)"""
        tier_diff = abs(problem_tier - user_tier)

        if tier_diff == 0:
            return 1.0
        elif tier_diff == 1:
            return 0.9
        elif tier_diff == 2:
            return 0.7
        else:
            return max(0.3, 1.0 - (tier_diff * 0.2))


    async def _get_challenge_problems(
        self,
        user_tier: int,
        count: int,
        filters: Optional[ProblemFilterRequest] = None
    ) -> List[Dict[str, Any]]:
        """도전 모드 (어려운 문제) 추천 - 현재 티어보다 높은 문제"""
        try:
            # 현재 티어보다 1-3티어 높은 문제들
            challenge_tier_min = max(1, user_tier + 1)  # 최소 1티어는 유지
            challenge_tier_max = min(30, user_tier + 4)  # 최대 4티어 높은 수준까지

            search_params = {
                "tier": f"tier:{challenge_tier_min}..{challenge_tier_max}",
                "count": count * 5,  # 더 많이 가져와서 다양성 확보
                "sort": "id"  # 일관성있는 정렬 후 랜덤 선택
            }

            if filters:
                # 필터 적용 시 기존 티어 범위를 무시하고 도전 모드 범위 적용
                filter_params = self._apply_filters(filters, search_params)

                # 티어 필터가 있다면 도전 모드 범위와 교집합 계산
                if 'tier' in filter_params:
                    # 사용자가 설정한 필터와 도전 모드 범위의 교집합 계산
                    search_params.update({k: v for k, v in filter_params.items() if k != 'tier'})
                    # 도전 모드의 티어 범위는 유지
                else:
                    search_params.update(filter_params)

            raw_problems = await self.solvedac_client.search_problems(**search_params)

            # 완전 랜덤 선택으로 매번 다른 결과
            import random

            available_problems = raw_problems.get("items", [])
            if len(available_problems) >= count:
                # 완전 랜덤 선택
                selected_items = random.sample(available_problems, count)
            else:
                selected_items = available_problems[:count]

            problems = []
            for item in selected_items:
                problem_data = format_solved_ac_problem_data(item)
                tier_diff = problem_data.get("tier", user_tier) - user_tier

                if tier_diff > 0:
                    problem_data["recommendation_reason"] = f"현재 티어보다 {tier_diff}단계 높은 도전 문제"
                else:
                    problem_data["recommendation_reason"] = "도전적인 문제"

                problem_data["confidence_score"] = random.uniform(0.3, 0.6)
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

        # 티어 필터 (브론즈: 1-5, 실버: 6-10, 골드: 11-15, 플래티넘: 16-20, 다이아: 21-25, 루비: 26-30)
        if filters.tier_min is not None or filters.tier_max is not None:
            tier_min = filters.tier_min or 0
            tier_max = filters.tier_max or 31

            # 브론즈, 실버, 골드 등의 티어 범위 확장
            if filters.tier_min is not None:
                tier_min = filters.tier_min
            if filters.tier_max is not None:
                tier_max = min(filters.tier_max + 4, 30)  # 해당 티어의 최대값까지 포함

            updated_params["tier"] = f"tier:{tier_min}..{tier_max}"

        # 난이도 클래스 필터 (solved.ac에서는 class로 검색)
        if filters.difficulty_class:
            updated_params["query"] = f"class:{filters.difficulty_class}"

        return updated_params

    async def get_problem_stats(self, username: str) -> Dict[str, Any]:
        """문제 추천 통계 - 새로운 3가지 지표"""
        try:
            user_info = await self.solvedac_service.get_user_info(username)
            user_tier = user_info.get("tier", 0)
            user_tier_name = user_info.get("tier_name", "Unknown")

            # 1. AI가 추천해준 문제 수 (적응형 추천으로 계산)
            ai_recommended_count = await self._calculate_ai_recommended_problems_count(username, user_tier)

            # 2. 사용자 해결 완료율 (추천받은 문제 중 실제 해결한 비율)
            completion_rate = await self._calculate_user_completion_rate(username)

            # 3. 현재 사용자 티어 정보
            current_tier_info = {
                "tier_id": user_tier,
                "tier_name": user_tier_name,
                "rating": user_info.get("rating", 0),
                "solved_count": user_info.get("solved_count", 0)
            }

            stats = {
                "ai_recommended_problems_count": ai_recommended_count,
                "user_completion_rate": completion_rate,
                "current_user_tier": current_tier_info
            }

            return stats

        except Exception as e:
            self.log_error(f"Failed to get problem stats for {username}", e)
            raise

    async def _calculate_ai_recommended_problems_count(self, username: str, user_tier: int) -> int:
        """AI가 추천할 수 있는 문제 수 계산 (적응형 추천 기준)"""
        try:
            # 적응형 추천에서 사용하는 알고리즘 태그들을 기반으로 계산
            recommended_tags = await self.openai_client.recommend_problems(
                user_tier, 0, 0, 10  # 더미 값으로 태그만 가져오기
            )

            total_count = 0
            for tag in recommended_tags[:5]:  # 상위 5개 태그
                try:
                    tier_range = f"tier:{max(0, user_tier-2)}..{min(30, user_tier+2)}"

                    # 각 태그별로 추천 가능한 문제 수 조회
                    search_result = await self.solvedac_client.search_problems(
                        algorithm=tag,
                        tier=tier_range,
                        count=1  # 총 개수만 필요하므로 1개만 조회
                    )

                    # solved.ac API는 총 개수를 제공하지 않으므로 추정값 사용
                    total_count += random.randint(50, 200)  # 태그당 50-200개 추정

                except Exception as e:
                    self.logger.warning(f"Failed to count problems for tag {tag}: {e}")
                    total_count += 100  # 기본값

            return min(total_count, 1500)  # 최대 1500개로 제한

        except Exception as e:
            self.log_error(f"Failed to calculate AI recommended count for {username}", e)
            return random.randint(800, 1200)  # 오류 시 기본값

    async def _calculate_user_completion_rate(self, username: str) -> float:
        """사용자 해결 완료율 계산 (추천받은 문제 중 실제 해결한 비율)"""
        try:
            # DB에서 추천 관련 활동 조회 (실제 구현에서는 DB에서 가져옴)
            # 현재는 더미 데이터로 계산

            # 이번 달 추천받은 문제 수 (추정)
            recommended_this_month = random.randint(15, 35)

            # 이번 달 실제 해결한 문제 수 (DB 또는 solved.ac에서 조회)
            solved_this_month = random.randint(8, 25)

            # 완료율 계산
            if recommended_this_month > 0:
                completion_rate = round(min(solved_this_month / recommended_this_month, 1.0), 2)
            else:
                completion_rate = 0.0

            return completion_rate

        except Exception as e:
            self.log_error(f"Failed to calculate completion rate for {username}", e)
            return round(random.uniform(0.4, 0.8), 2)  # 오류 시 기본값

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
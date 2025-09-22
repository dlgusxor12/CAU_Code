from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.clients.openai_client import OpenAIClient
from app.utils.cache import CacheManager
from app.utils.logging import LoggerMixin


class GPTService(LoggerMixin):
    """OpenAI GPT 관련 서비스를 담당하는 클래스"""

    def __init__(self):
        self.openai_client = OpenAIClient()
        self.cache = CacheManager()

    async def generate_problem_recommendation_reasoning(
        self,
        user_profile: Dict[str, Any],
        problem_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """문제 추천 이유를 AI로 생성"""
        try:
            start_time = datetime.now()

            enhanced_problems = []

            for problem in problem_list:
                cache_key = f"recommendation_reason_{problem['problem_id']}_{user_profile['tier']}"
                cached_reason = self.cache.get(cache_key)

                if cached_reason:
                    problem["ai_recommendation_reason"] = cached_reason
                else:
                    # AI로 추천 이유 생성
                    reason = await self._generate_single_recommendation_reason(
                        user_profile, problem
                    )
                    problem["ai_recommendation_reason"] = reason

                    # 캐시에 저장 (2시간)
                    self.cache.set(cache_key, reason, ttl=7200)

                enhanced_problems.append(problem)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("generate_recommendation_reasoning", duration, {
                "problem_count": len(problem_list),
                "user_tier": user_profile.get("tier", 0)
            })

            return enhanced_problems

        except Exception as e:
            self.log_error("Failed to generate recommendation reasoning", e)
            # 실패 시 원본 리스트 반환
            return problem_list

    async def _generate_single_recommendation_reason(
        self,
        user_profile: Dict[str, Any],
        problem: Dict[str, Any]
    ) -> str:
        """단일 문제에 대한 추천 이유 생성"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """당신은 코딩 테스트 멘토입니다. 사용자의 프로필과 문제 정보를 바탕으로
                    왜 이 문제를 추천하는지 간단명료하게 설명해주세요. 50자 이내로 작성해주세요."""
                },
                {
                    "role": "user",
                    "content": f"""
                    사용자 정보:
                    - 티어: {user_profile.get('tier', 0)}
                    - 레이팅: {user_profile.get('rating', 0)}
                    - 해결 문제 수: {user_profile.get('solved_count', 0)}

                    추천 문제:
                    - 문제 번호: {problem.get('problem_id', 0)}
                    - 제목: {problem.get('title', 'Unknown')}
                    - 티어: {problem.get('tier', 0)}
                    - 알고리즘: {', '.join(problem.get('tags', [])[:2])}

                    이 문제를 추천하는 이유를 설명해주세요.
                    """
                }
            ]

            response = await self.openai_client._chat_completion(messages, temperature=0.5)
            return response[:50] if response else "현재 실력에 적합한 문제입니다"

        except Exception as e:
            self.logger.warning(f"Failed to generate reason for problem {problem.get('problem_id')}: {e}")
            return "현재 실력에 적합한 문제입니다"

    async def analyze_user_weakness(
        self,
        user_profile: Dict[str, Any],
        recent_submissions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """사용자의 약점 분석"""
        try:
            cache_key = f"weakness_analysis_{user_profile['handle']}"
            cached_analysis = self.cache.get(cache_key)
            if cached_analysis:
                return cached_analysis

            start_time = datetime.now()

            messages = [
                {
                    "role": "system",
                    "content": """당신은 코딩 실력 분석 전문가입니다. 사용자의 프로필과 최근 제출 기록을 분석하여
                    약점과 개선점을 찾아주세요. JSON 형태로 응답해주세요."""
                },
                {
                    "role": "user",
                    "content": f"""
                    사용자 정보:
                    - 티어: {user_profile.get('tier', 0)}
                    - 해결 문제 수: {user_profile.get('solved_count', 0)}
                    - 최근 제출 기록: {json.dumps(recent_submissions[:5], ensure_ascii=False)}

                    다음 형태로 분석해주세요:
                    {{
                        "weak_algorithms": ["부족한 알고리즘 1", "부족한 알고리즘 2"],
                        "recommended_practice": ["연습할 문제 유형 1", "연습할 문제 유형 2"],
                        "strength_areas": ["강한 분야 1", "강한 분야 2"],
                        "next_tier_requirements": "다음 티어를 위한 요구사항"
                    }}
                    """
                }
            ]

            response = await self.openai_client._chat_completion(messages, temperature=0.3)

            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # 파싱 실패 시 기본 분석 제공
                analysis = {
                    "weak_algorithms": ["다이나믹 프로그래밍", "그래프"],
                    "recommended_practice": ["DP 기초 문제", "DFS/BFS 문제"],
                    "strength_areas": ["구현", "수학"],
                    "next_tier_requirements": "더 복잡한 알고리즘 문제 해결 능력 향상"
                }

            # 분석 시간 추가
            analysis["analyzed_at"] = datetime.now()

            # 캐시에 저장 (6시간)
            self.cache.set(cache_key, analysis, ttl=21600)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("analyze_user_weakness", duration, {
                "username": user_profile.get('handle', 'unknown')
            })

            return analysis

        except Exception as e:
            self.log_error("Failed to analyze user weakness", e)
            # 실패 시 기본 분석 반환
            return {
                "weak_algorithms": ["알고리즘 분석 불가"],
                "recommended_practice": ["기본 문제 연습"],
                "strength_areas": ["분석 필요"],
                "next_tier_requirements": "꾸준한 문제 해결",
                "analyzed_at": datetime.now()
            }

    async def generate_study_plan(
        self,
        user_profile: Dict[str, Any],
        target_tier: int,
        weeks: int = 4
    ) -> Dict[str, Any]:
        """개인화된 학습 계획 생성"""
        try:
            cache_key = f"study_plan_{user_profile['handle']}_{target_tier}_{weeks}"
            cached_plan = self.cache.get(cache_key)
            if cached_plan:
                return cached_plan

            start_time = datetime.now()

            current_tier = user_profile.get('tier', 0)
            tier_gap = target_tier - current_tier

            messages = [
                {
                    "role": "system",
                    "content": """당신은 코딩 테스트 학습 계획 전문가입니다. 사용자의 현재 실력과 목표를 바탕으로
                    체계적인 학습 계획을 세워주세요. JSON 형태로 응답해주세요."""
                },
                {
                    "role": "user",
                    "content": f"""
                    현재 티어: {current_tier}
                    목표 티어: {target_tier}
                    계획 기간: {weeks}주
                    해결 문제 수: {user_profile.get('solved_count', 0)}

                    다음 형태로 학습 계획을 세워주세요:
                    {{
                        "weekly_goals": [
                            {{
                                "week": 1,
                                "focus_algorithms": ["알고리즘1", "알고리즘2"],
                                "target_problems": 10,
                                "difficulty_level": "현재 티어 기준",
                                "key_concepts": ["개념1", "개념2"]
                            }}
                        ],
                        "daily_routine": "일일 권장 학습량",
                        "milestone_checks": ["주간 체크포인트들"],
                        "success_probability": 0.8
                    }}
                    """
                }
            ]

            response = await self.openai_client._chat_completion(messages, temperature=0.4)

            try:
                plan = json.loads(response)
            except json.JSONDecodeError:
                # 파싱 실패 시 기본 계획 제공
                plan = self._generate_default_study_plan(current_tier, target_tier, weeks)

            # 계획 생성 시간 추가
            plan["created_at"] = datetime.now()
            plan["current_tier"] = current_tier
            plan["target_tier"] = target_tier

            # 캐시에 저장 (24시간)
            self.cache.set(cache_key, plan, ttl=86400)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("generate_study_plan", duration, {
                "username": user_profile.get('handle', 'unknown'),
                "tier_gap": tier_gap,
                "weeks": weeks
            })

            return plan

        except Exception as e:
            self.log_error("Failed to generate study plan", e)
            return self._generate_default_study_plan(
                user_profile.get('tier', 0), target_tier, weeks
            )

    def _generate_default_study_plan(
        self,
        current_tier: int,
        target_tier: int,
        weeks: int
    ) -> Dict[str, Any]:
        """기본 학습 계획 생성"""
        algorithms_by_tier = {
            1: ["구현", "수학"],
            5: ["그리디", "정렬"],
            10: ["다이나믹 프로그래밍", "그래프"],
            15: ["트리", "이분탐색"],
            20: ["세그먼트 트리", "플로우"]
        }

        weekly_goals = []
        for week in range(1, weeks + 1):
            # 난이도를 점진적으로 증가
            focus_tier = min(target_tier, current_tier + (week * (target_tier - current_tier) // weeks))

            # 해당 티어에 적합한 알고리즘 선택
            algorithms = algorithms_by_tier.get(focus_tier, ["구현", "수학"])

            weekly_goals.append({
                "week": week,
                "focus_algorithms": algorithms,
                "target_problems": 8 + week * 2,
                "difficulty_level": f"티어 {focus_tier} 기준",
                "key_concepts": algorithms
            })

        return {
            "weekly_goals": weekly_goals,
            "daily_routine": "매일 2-3문제 해결",
            "milestone_checks": [f"{week}주차 목표 달성 확인" for week in range(1, weeks + 1)],
            "success_probability": max(0.5, min(0.9, 1.0 - (target_tier - current_tier) * 0.1)),
            "created_at": datetime.now(),
            "current_tier": current_tier,
            "target_tier": target_tier
        }

    async def explain_solution_approach(
        self,
        problem_description: str,
        difficulty_tier: int
    ) -> Dict[str, Any]:
        """문제 해결 접근법 설명"""
        try:
            cache_key = f"solution_approach_{hash(problem_description)}_{difficulty_tier}"
            cached_explanation = self.cache.get(cache_key)
            if cached_explanation:
                return cached_explanation

            start_time = datetime.now()

            messages = [
                {
                    "role": "system",
                    "content": """당신은 코딩 문제 해결 전문가입니다. 문제를 분석하고 해결 접근법을 단계별로 설명해주세요."""
                },
                {
                    "role": "user",
                    "content": f"""
                    문제 설명: {problem_description}
                    난이도 티어: {difficulty_tier}

                    이 문제의 해결 접근법을 다음과 같이 설명해주세요:
                    1. 문제 핵심 파악
                    2. 적절한 알고리즘 선택
                    3. 단계별 해결 방법
                    4. 시간복잡도
                    5. 주의사항

                    각 항목을 간단명료하게 설명해주세요.
                    """
                }
            ]

            response = await self.openai_client._chat_completion(messages, temperature=0.3)

            explanation = {
                "approach_explanation": response,
                "difficulty_tier": difficulty_tier,
                "explained_at": datetime.now()
            }

            # 캐시에 저장 (2시간)
            self.cache.set(cache_key, explanation, ttl=7200)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("explain_solution_approach", duration, {
                "difficulty_tier": difficulty_tier
            })

            return explanation

        except Exception as e:
            self.log_error("Failed to explain solution approach", e)
            return {
                "approach_explanation": "문제 해결 접근법 설명을 생성할 수 없습니다.",
                "difficulty_tier": difficulty_tier,
                "explained_at": datetime.now()
            }
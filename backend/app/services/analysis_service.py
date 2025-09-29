from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.clients.openai_client import OpenAIClient
from app.services.solvedac_service import SolvedACService
from app.utils.helpers import format_time_complexity, generate_algorithm_explanation
from app.utils.cache import CacheManager, cache_get, cache_set
from app.utils.logging import LoggerMixin


class AnalysisService(LoggerMixin):
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.solvedac_service = SolvedACService()
        self.cache = CacheManager()

    async def analyze_code(
        self,
        code: str,
        problem_id: int,
        language: str,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """코드 분석 및 피드백 생성"""
        try:
            # 캐시에서 확인
            cached_analysis = self.cache.get_code_analysis(code, problem_id)
            if cached_analysis:
                self.log_performance("analyze_code_cached", 0.001, {
                    "problem_id": problem_id,
                    "language": language
                })
                return cached_analysis

            start_time = datetime.now()

            # 문제 정보 조회
            try:
                problem_info = await self.solvedac_service.get_problem_info(problem_id)
                problem_description = f"문제 번호: {problem_id}, 제목: {problem_info.get('title', 'Unknown')}"
            except Exception:
                problem_description = f"문제 번호: {problem_id}"

            # OpenAI로 코드 분석
            analysis_result = await self.openai_client.analyze_code(
                code, problem_description, language
            )

            # 분석 결과 후처리
            processed_result = self._process_analysis_result(
                analysis_result, code, problem_id, language
            )

            # 캐시에 저장 (30분)
            self.cache.set_code_analysis(code, problem_id, processed_result, ttl=1800)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("analyze_code", duration, {
                "problem_id": problem_id,
                "language": language,
                "code_length": len(code)
            })

            # 사용자 액션 로그
            if username:
                self.log_user_action(username, "code_analysis", {
                    "problem_id": problem_id,
                    "language": language,
                    "score": processed_result.get("score", 0)
                })

            return processed_result

        except Exception as e:
            self.log_error(f"Failed to analyze code for problem {problem_id}", e)
            raise

    def _process_analysis_result(
        self,
        raw_result: Dict[str, Any],
        code: str,
        problem_id: int,
        language: str
    ) -> Dict[str, Any]:
        """분석 결과 후처리"""
        # 기본값 설정
        score = max(0, min(100, raw_result.get("score", 75)))
        strengths = raw_result.get("strengths", "코드가 정상적으로 작동합니다")[:100]
        improvements = raw_result.get("improvements", "더 효율적인 알고리즘을 고려해보세요")[:100]
        time_complexity = format_time_complexity(
            raw_result.get("time_complexity", "O(n)")
        )
        algorithm_type = raw_result.get("algorithm_type", "구현")

        # AI로부터 받은 핵심 개념 사용 (하드코딩된 설명 대신)
        core_concept = raw_result.get("core_concept", generate_algorithm_explanation(algorithm_type))

        return {
            "score": score,
            "submitted_code": code,
            "strengths": strengths,
            "improvements": improvements,
            "core_concept": core_concept,
            "time_complexity": time_complexity,
            "algorithm_type": algorithm_type,
            "language": language,
            "analysis_timestamp": datetime.now(),
            "problem_id": problem_id
        }

    async def generate_optimized_code(
        self,
        problem_id: int,
        language: str,
        current_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """AI 최적 코드 생성"""
        try:
            start_time = datetime.now()

            # 캐시 키 생성
            cache_key = f"optimized_code_{problem_id}_{language}"
            if current_code:
                cache_key += f"_{hash(current_code)}"

            cached_result = cache_get(cache_key)
            if cached_result:
                self.log_performance("generate_optimized_code_cached", 0.001, {
                    "problem_id": problem_id,
                    "language": language
                })
                return cached_result

            # 문제 정보 조회
            try:
                problem_info = await self.solvedac_service.get_problem_info(problem_id)
                problem_description = f"""
                문제 번호: {problem_id}
                제목: {problem_info.get('title', 'Unknown')}
                티어: {problem_info.get('tier_name', 'Unknown')}
                """
            except Exception:
                problem_description = f"문제 번호: {problem_id}"

            # OpenAI로 최적 코드 생성
            optimization_result = await self.openai_client.generate_optimized_code(
                problem_description, language
            )

            # 결과 후처리
            processed_result = {
                "optimized_code": optimization_result.get("code", f"// {language} 최적화된 코드\n// 구현 중..."),
                "explanation": optimization_result.get("explanation", "최적화된 솔루션을 생성하는 중 오류가 발생했습니다."),
                "time_complexity": format_time_complexity("O(n)"),  # 기본값
                "space_complexity": "O(1)",  # 기본값
                "key_insights": [
                    "효율적인 알고리즘 선택",
                    "최적화된 자료구조 사용",
                    "시간복잡도 개선"
                ],
                "problem_id": problem_id,
                "language": language,
                "generated_at": datetime.now()
            }

            # 현재 코드와 비교 정보 추가
            if current_code:
                processed_result["performance_comparison"] = {
                    "original_estimated_complexity": "O(n²)",  # 더미 데이터
                    "optimized_complexity": "O(n log n)",
                    "estimated_improvement": "50%"
                }

            # 캐시에 저장 (1시간)
            cache_set(cache_key, processed_result, expire=3600)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("generate_optimized_code", duration, {
                "problem_id": problem_id,
                "language": language
            })

            return processed_result

        except Exception as e:
            self.log_error(f"Failed to generate optimized code for problem {problem_id}", e)
            raise

    async def get_algorithm_explanation(
        self,
        algorithm_type: str,
        difficulty_level: int = 3
    ) -> Dict[str, Any]:
        """알고리즘 설명"""
        try:
            cache_key = f"algorithm_explanation_{algorithm_type}_{difficulty_level}"
            cached_result = cache_get(cache_key)
            if cached_result:
                return cached_result

            start_time = datetime.now()

            # OpenAI로 알고리즘 설명 생성
            explanation = await self.openai_client.get_algorithm_explanation(algorithm_type)

            result = {
                "algorithm_type": algorithm_type,
                "explanation": explanation,
                "time_complexity": self._get_typical_complexity(algorithm_type),
                "use_cases": self._get_algorithm_use_cases(algorithm_type),
                "related_algorithms": self._get_related_algorithms(algorithm_type),
                "difficulty_rating": difficulty_level,
                "generated_at": datetime.now()
            }

            # 캐시에 저장 (2시간)
            cache_set(cache_key, result, expire=7200)

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("get_algorithm_explanation", duration, {
                "algorithm_type": algorithm_type
            })

            return result

        except Exception as e:
            self.log_error(f"Failed to get explanation for algorithm {algorithm_type}", e)
            raise

    def _get_typical_complexity(self, algorithm_type: str) -> str:
        """알고리즘 유형별 일반적인 시간복잡도"""
        complexity_map = {
            "구현": "O(n)",
            "수학": "O(1) ~ O(log n)",
            "그리디": "O(n log n)",
            "다이나믹 프로그래밍": "O(n²) ~ O(n³)",
            "그래프": "O(V + E)",
            "문자열": "O(n) ~ O(n²)",
            "브루트포스": "O(2ⁿ)",
            "이분탐색": "O(log n)",
            "정렬": "O(n log n)"
        }
        return complexity_map.get(algorithm_type, "O(n)")

    def _get_algorithm_use_cases(self, algorithm_type: str) -> List[str]:
        """알고리즘 활용 사례"""
        use_cases_map = {
            "구현": ["시뮬레이션 문제", "조건 분기 문제", "배열 조작"],
            "수학": ["수식 계산", "정수론", "기하학"],
            "그리디": ["최적화 문제", "스케줄링", "거스름돈 문제"],
            "다이나믹 프로그래밍": ["최적 부분 구조", "중복 부분 문제", "경우의 수"],
            "그래프": ["최단경로", "연결성 확인", "위상정렬"],
            "문자열": ["패턴 매칭", "문자열 처리", "파싱"],
            "브루트포스": ["완전 탐색", "백트래킹", "순열/조합"]
        }
        return use_cases_map.get(algorithm_type, ["일반적인 문제 해결"])

    def _get_related_algorithms(self, algorithm_type: str) -> List[str]:
        """관련 알고리즘"""
        related_map = {
            "구현": ["시뮬레이션", "완전탐색"],
            "수학": ["정수론", "기하학", "조합론"],
            "그리디": ["다이나믹 프로그래밍", "정렬"],
            "다이나믹 프로그래밍": ["그리디", "분할정복"],
            "그래프": ["DFS", "BFS", "다익스트라"],
            "문자열": ["KMP", "라빈카프", "트라이"],
            "브루트포스": ["백트래킹", "DFS", "BFS"]
        }
        return related_map.get(algorithm_type, [])

    async def get_feedback_summary(self, username: str) -> Dict[str, Any]:
        """사용자의 피드백 요약 통계"""
        try:
            # 실제로는 데이터베이스에서 사용자의 분석 기록을 조회해야 하지만
            # 현재는 더미 데이터 반환
            cache_key = f"feedback_summary_{username}"
            cached_result = cache_get(cache_key)
            if cached_result:
                return cached_result

            # 더미 통계 데이터
            summary = {
                "total_analyses": 15,
                "average_score": 78.5,
                "most_common_weaknesses": [
                    "시간복잡도 최적화 부족",
                    "코드 가독성 개선 필요",
                    "에러 처리 미흡"
                ],
                "improvement_trends": {
                    "score_trend": 5.2,
                    "complexity_improvement": 12.0,
                    "readability_improvement": 8.0
                },
                "recommended_study_topics": [
                    "다이나믹 프로그래밍",
                    "그래프 알고리즘",
                    "문자열 처리"
                ],
                "generated_at": datetime.now()
            }

            # 캐시에 저장 (1시간)
            cache_set(cache_key, summary, expire=3600)

            return summary

        except Exception as e:
            self.log_error(f"Failed to get feedback summary for {username}", e)
            raise

    async def compare_codes(
        self,
        original_code: str,
        improved_code: str,
        language: str,
        problem_id: int
    ) -> Dict[str, Any]:
        """코드 비교 분석"""
        try:
            start_time = datetime.now()

            # 각각 분석
            original_analysis = await self.analyze_code(original_code, problem_id, language)
            improved_analysis = await self.analyze_code(improved_code, problem_id, language)

            # 비교 결과 생성
            score_improvement = improved_analysis["score"] - original_analysis["score"]
            performance_gain = max(0, score_improvement / 100)

            comparison = {
                "original_analysis": {
                    "score": original_analysis["score"],
                    "time_complexity": original_analysis["time_complexity"],
                    "strengths": original_analysis["strengths"],
                    "improvements": original_analysis["improvements"]
                },
                "improved_analysis": {
                    "score": improved_analysis["score"],
                    "time_complexity": improved_analysis["time_complexity"],
                    "strengths": improved_analysis["strengths"],
                    "improvements": improved_analysis["improvements"]
                },
                "improvement_summary": f"점수가 {score_improvement}점 향상되었습니다.",
                "performance_gain": round(performance_gain, 2),
                "recommendation": "개선된 코드가 더 효율적입니다." if score_improvement > 0 else "추가 최적화가 필요합니다.",
                "analyzed_at": datetime.now()
            }

            duration = (datetime.now() - start_time).total_seconds()
            self.log_performance("compare_codes", duration, {
                "problem_id": problem_id,
                "language": language,
                "score_improvement": score_improvement
            })

            return comparison

        except Exception as e:
            self.log_error(f"Failed to compare codes for problem {problem_id}", e)
            raise
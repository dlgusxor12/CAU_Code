from openai import AsyncOpenAI
from typing import Dict, List, Optional, Any
from app.config import settings
from app.core.exceptions import OpenAIAPIError


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"

    async def _chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise OpenAIAPIError(f"Chat completion failed: {str(e)}")

    async def analyze_code(self, code: str, problem_description: str, language: str) -> Dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": """You are a coding expert who analyzes code quality and provides detailed feedback.
                Analyze the given code and return ONLY a valid JSON response with the following structure:
                {
                    "score": (integer 0-100),
                    "strengths": "구체적인 장점을 한국어로 설명 (최대 100자)",
                    "improvements": "구체적인 개선점을 한국어로 설명 (최대 100자)",
                    "time_complexity": "시간복잡도 (예: O(n), O(log n), O(n²))",
                    "algorithm_type": "알고리즘 유형을 한국어로 (예: 구현, 정렬, 탐색, 동적계획법)",
                    "core_concept": "이 문제를 해결하기 위한 핵심 접근법이나 추천 학습 방향을 한국어로 (최대 100자)"
                }

                Do not include any text outside the JSON response."""
            },
            {
                "role": "user",
                "content": f"""문제 설명: {problem_description}
                언어: {language}
                코드:
                ```{language}
                {code}
                ```

                위 코드를 분석하여 JSON 형태로 응답해주세요."""
            }
        ]

        response = await self._chat_completion(messages, temperature=0.3)

        try:
            import json
            # OpenAI 응답에서 JSON 부분만 추출
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]

            # JSON 파싱 시도
            parsed_response = json.loads(response_clean.strip())

            # 필수 필드 검증 및 기본값 설정
            return {
                "score": parsed_response.get("score", 75),
                "strengths": parsed_response.get("strengths", "코드 구조가 깔끔합니다"),
                "improvements": parsed_response.get("improvements", "변수명을 더 명확하게 작성해보세요"),
                "time_complexity": parsed_response.get("time_complexity", "O(n)"),
                "algorithm_type": parsed_response.get("algorithm_type", "구현"),
                "core_concept": parsed_response.get("core_concept", "문제의 핵심 개념을 파악하여 체계적으로 접근해보세요")
            }
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # 로깅 추가
            print(f"OpenAI JSON 파싱 오류: {e}")
            print(f"원본 응답: {response}")

            # 기본값 반환
            return {
                "score": 75,
                "strengths": "코드가 정상적으로 작동합니다",
                "improvements": "더 효율적인 알고리즘을 고려해보세요",
                "time_complexity": "O(n)",
                "algorithm_type": "구현",
                "core_concept": "문제의 핵심 개념을 파악하여 체계적으로 접근해보세요"
            }

    async def generate_optimized_code(self, problem_description: str, language: str) -> Dict[str, str]:
        messages = [
            {
                "role": "system",
                "content": """You are a competitive programming expert specializing in algorithm optimization.
                Generate the MOST TIME-EFFICIENT solution for the given problem.
                Focus on optimal time complexity, efficient algorithms, and clean implementation.

                IMPORTANT: Return ONLY a valid JSON response with this exact format:
                {
                    "code": "최적화된 완전한 코드 (주석 포함)",
                    "explanation": "시간복잡도와 핵심 알고리즘을 포함한 한국어 설명"
                }

                Do NOT include any text before or after the JSON. The response must be parseable JSON."""
            },
            {
                "role": "user",
                "content": f"""문제: {problem_description}
                언어: {language}

                이 문제에 대한 최적의 코드와 설명을 JSON 형태로 제공해주세요."""
            }
        ]

        response = await self._chat_completion(messages, temperature=0.1, max_tokens=2000)

        try:
            import json
            # OpenAI 응답 로깅 추가
            print(f"OpenAI Raw Response: {response}")

            # JSON 응답 정리 (markdown 코드 블록 제거 등)
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]

            return json.loads(response_clean.strip())
        except json.JSONDecodeError as e:
            # JSON 파싱 오류 상세 로깅
            print(f"JSON 파싱 오류: {e}")
            print(f"파싱 실패한 응답: {response}")
            return {
                "code": f"// {language} 최적화된 코드\n// 구현 중...",
                "explanation": "최적화된 솔루션을 생성하는 중 오류가 발생했습니다."
            }

    async def recommend_problems(
        self,
        user_tier: int,
        user_rating: int,
        solved_count: int,
        count: int = 10
    ) -> List[str]:
        messages = [
            {
                "role": "system",
                "content": """You are a competitive programming mentor.
                Based on user's tier, rating, and solved problems count, recommend problem types and algorithms.
                Return a JSON array of recommended algorithm tags for solved.ac API.
                Example: ["dp", "greedy", "graph", "implementation"]"""
            },
            {
                "role": "user",
                "content": f"""사용자 정보:
                - 티어: {user_tier}
                - 레이팅: {user_rating}
                - 해결한 문제 수: {solved_count}

                이 사용자에게 적합한 {count}개의 알고리즘 태그를 추천해주세요."""
            }
        ]

        response = await self._chat_completion(messages, temperature=0.5)

        try:
            import json
            tags = json.loads(response)
            return tags if isinstance(tags, list) else ["implementation", "math", "greedy"]
        except json.JSONDecodeError:
            return ["implementation", "math", "greedy", "dp", "brute_force"]

    async def get_algorithm_explanation(self, algorithm_type: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a programming education expert. Provide concise explanations of algorithms in Korean."
            },
            {
                "role": "user",
                "content": f"{algorithm_type} 알고리즘의 핵심 개념과 활용법을 간단히 설명해주세요. (200자 이내)"
            }
        ]

        return await self._chat_completion(messages, temperature=0.3)
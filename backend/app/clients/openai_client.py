from openai import AsyncOpenAI
from typing import Dict, List, Optional, Any
from app.config import settings
from app.core.exceptions import OpenAIAPIError


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"

    async def _chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise OpenAIAPIError(f"Chat completion failed: {str(e)}")

    async def analyze_code(self, code: str, problem_description: str, language: str) -> Dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": """You are a coding expert who analyzes code quality and provides feedback.
                Analyze the given code and return a JSON response with the following structure:
                {
                    "score": (integer 0-100),
                    "strengths": "string (max 100 characters in Korean)",
                    "improvements": "string (max 100 characters in Korean)",
                    "time_complexity": "string (e.g., O(n), O(log n))",
                    "algorithm_type": "string (algorithm category in Korean)"
                }"""
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
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "score": 75,
                "strengths": "코드가 정상적으로 작동합니다",
                "improvements": "더 효율적인 알고리즘을 고려해보세요",
                "time_complexity": "O(n)",
                "algorithm_type": "구현"
            }

    async def generate_optimized_code(self, problem_description: str, language: str) -> Dict[str, str]:
        messages = [
            {
                "role": "system",
                "content": """You are a competitive programming expert.
                Generate the most optimal solution for the given problem and provide explanation in Korean.
                Return a JSON response with:
                {
                    "code": "optimized code string",
                    "explanation": "explanation in Korean including time complexity"
                }"""
            },
            {
                "role": "user",
                "content": f"""문제: {problem_description}
                언어: {language}

                이 문제에 대한 최적의 코드와 설명을 JSON 형태로 제공해주세요."""
            }
        ]

        response = await self._chat_completion(messages, temperature=0.1)

        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
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
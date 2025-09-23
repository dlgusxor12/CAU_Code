import httpx
from typing import Dict, List, Optional, Any
from app.core.exceptions import SolvedACAPIError, UserNotFoundError, ProblemNotFoundError


class SolvedACClient:
    def __init__(self):
        self.base_url = "https://solved.ac/api/v3"
        self.timeout = 30.0

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, params=params)

                if response.status_code == 404:
                    raise UserNotFoundError("User or resource not found")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise SolvedACAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
            except httpx.RequestError as e:
                raise SolvedACAPIError(f"Request failed: {str(e)}")

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        return await self._request("GET", f"/user/show", params={"handle": username})

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """사용자 프로필 정보 조회 (bio 포함)"""
        return await self._request("GET", f"/user/show", params={"handle": username})

    async def get_user_problems(self, username: str) -> Dict[str, Any]:
        return await self._request("GET", f"/search/problem", params={
            "query": f"s@{username}",
            "sort": "id",
            "direction": "asc"
        })

    async def get_user_unsolved_problems(self, username: str) -> Dict[str, Any]:
        return await self._request("GET", f"/search/problem", params={
            "query": f"t@{username} -s@{username}",
            "sort": "random",
            "direction": "asc"
        })

    async def get_problem_info(self, problem_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/problem/show", params={"problemId": problem_id})

    async def search_problems(
        self,
        query: Optional[str] = None,
        tier: Optional[str] = None,
        algorithm: Optional[str] = None,
        sort: str = "random",
        direction: str = "asc",
        count: int = 10
    ) -> Dict[str, Any]:
        params = {
            "sort": sort,
            "direction": direction,
            "count": count
        }

        if query:
            params["query"] = query
        if tier:
            params["query"] = f"{params.get('query', '')} *{tier}".strip()
        if algorithm:
            params["query"] = f"{params.get('query', '')} #{algorithm}".strip()

        return await self._request("GET", f"/search/problem", params=params)

    async def get_problems_by_tier(self, tier: str, count: int = 10) -> Dict[str, Any]:
        return await self.search_problems(tier=tier, count=count)

    async def get_problems_by_algorithm(self, algorithm: str, count: int = 10) -> Dict[str, Any]:
        return await self.search_problems(algorithm=algorithm, count=count)

    async def get_recommended_problems_for_user(self, username: str, count: int = 10) -> Dict[str, Any]:
        user_info = await self.get_user_info(username)
        user_tier = user_info.get("tier", 0)

        if user_tier == 0:
            tier_range = "b5..b1"
        elif user_tier <= 5:
            tier_range = f"b{6-user_tier}..s5"
        elif user_tier <= 10:
            tier_range = f"b{11-user_tier}..s{15-user_tier}"
        elif user_tier <= 15:
            tier_range = f"s{16-user_tier}..g5"
        elif user_tier <= 20:
            tier_range = f"s{21-user_tier}..g{25-user_tier}"
        elif user_tier <= 25:
            tier_range = f"g{26-user_tier}..p5"
        elif user_tier <= 30:
            tier_range = f"g{31-user_tier}..p{35-user_tier}"
        else:
            tier_range = "p1..r"

        return await self.search_problems(tier=tier_range, count=count)

    async def verify_problem_solved(self, username: str, problem_id: int) -> bool:
        try:
            solved_problems = await self.get_user_problems(username)
            problem_ids = [p.get("problemId") for p in solved_problems.get("items", [])]
            return problem_id in problem_ids
        except Exception:
            return False
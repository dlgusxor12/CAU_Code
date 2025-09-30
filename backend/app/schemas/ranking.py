from pydantic import BaseModel
from typing import List, Optional


class RankingUser(BaseModel):
    """랭킹 사용자 정보"""
    rank: int
    username: str
    organization: str
    tier: str
    rating: int
    total_solved: int
    cau_solved: int


class GlobalRankingResponse(BaseModel):
    """전체 랭킹 응답"""
    rankings: List[RankingUser]
    total_count: int


class OrganizationRankingResponse(BaseModel):
    """소속 랭킹 응답"""
    organization: str
    rankings: List[RankingUser]
    total_count: int


class MyRankInfo(BaseModel):
    """내 랭킹 정보"""
    username: str
    organization: str
    tier: str
    rating: int
    total_solved: int
    global_rank: int


class RankingStats(BaseModel):
    """랭킹 통계"""
    total_users: int
    organization_users: int
    avg_solved_count: int
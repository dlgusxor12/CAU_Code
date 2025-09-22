from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    handle: str
    bio: Optional[str] = None
    verified: bool = False
    badge_id: Optional[str] = None
    background_id: Optional[str] = None
    profile_image_url: Optional[str] = None
    solved_count: int = 0
    vote_count: int = 0
    class_level: int = 0
    class_decoration: Optional[str] = None
    rival_count: int = 0
    reverse_rival_count: int = 0
    tier: int = 0
    rating: int = 0
    rating_by_problems_sum: int = 0
    rating_by_class: int = 0
    rating_by_solved_count: int = 0
    rating_by_vote_count: int = 0
    over_rating: int = 0
    over_rating_cutoff: int = 0
    arena_tier: int = 0
    arena_rating: int = 0
    arena_max_tier: int = 0
    arena_max_rating: int = 0
    arena_competed_round_count: int = 0
    max_streak: int = 0
    coins: int = 0
    stardusts: int = 0
    joined_at: datetime
    banned_until: Optional[datetime] = None
    pro_until: Optional[datetime] = None
    rank: int = 0
    is_rival: bool = False
    is_reverse_rival: bool = False
    blocked: bool = False
    reverse_blocked: bool = False


class UserStats(BaseModel):
    current_tier: int
    current_rating: int
    solved_problems: int
    rank: int
    max_streak: int


class ContributionData(BaseModel):
    date: str
    solved_count: int
    difficulty_distribution: dict


class RecentActivity(BaseModel):
    type: str  # "solved" or "feedback"
    description: str
    timestamp: datetime
    problem_id: Optional[int] = None


class WeeklyStats(BaseModel):
    total_solved: int
    new_algorithms: int
    difficulty_increase: float
    consistency_score: float
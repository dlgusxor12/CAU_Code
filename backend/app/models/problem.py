from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class Problem(BaseModel):
    problem_id: int
    title_ko: str
    title_en: Optional[str] = None
    is_solvable: bool = True
    is_partial: bool = False
    accepted_user_count: int = 0
    level: int = 0
    voted_user_count: int = 0
    sprout: bool = False
    gives_no_rating: bool = False
    is_level_locked: bool = False
    average_tries: float = 0.0
    official: bool = False
    tags: List[Dict] = []


class ProblemInfo(BaseModel):
    problem_id: int
    title: str
    description: Optional[str] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    submission_count: int = 0
    accepted_count: int = 0
    solved_count: int = 0
    correct_ratio: float = 0.0
    tier: int = 0
    algorithm_tags: List[str] = []
    difficulty_class: int = 0


class ProblemRecommendation(BaseModel):
    problem_id: int
    title: str
    tier: int
    algorithm_tags: List[str]
    difficulty: int
    reason: str
    confidence_score: float


class ProblemFilter(BaseModel):
    tier_min: Optional[int] = None
    tier_max: Optional[int] = None
    algorithm: Optional[str] = None
    difficulty_class: Optional[int] = None
    solved_count_min: Optional[int] = None
    solved_count_max: Optional[int] = None


class TodaysProblem(BaseModel):
    problem_id: int
    title: str
    tier: int
    algorithm_tags: List[str]
    estimated_time: int  # minutes
    recommendation_reason: str


class ReviewProblem(BaseModel):
    problem_id: int
    title: str
    tier: int
    algorithm_tags: List[str]
    last_attempt: Optional[datetime] = None
    mistake_count: int = 0
    review_reason: str
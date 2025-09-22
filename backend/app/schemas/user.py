from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserDashboardResponse(BaseModel):
    user_info: dict
    todays_problems: List[dict]
    review_problems: List[dict]
    contribution_graph: List[dict]
    recent_activities: List[dict]
    weekly_stats: dict


class UserStatsResponse(BaseModel):
    current_tier: int = Field(..., description="사용자 현재 티어")
    current_rating: int = Field(..., description="사용자 현재 레이팅")
    solved_problems: int = Field(..., description="해결한 문제 수")
    rank: int = Field(..., description="전체 순위")
    tier_name: str = Field(..., description="티어 이름")
    class_level: int = Field(..., description="클래스 레벨")


class ContributionGraphResponse(BaseModel):
    year: int = Field(..., description="년도")
    daily_data: List[dict] = Field(..., description="일별 해결 현황")
    total_solved_this_year: int = Field(..., description="올해 해결한 문제 수")
    longest_streak: int = Field(..., description="최장 연속 해결일")


class RecentActivityResponse(BaseModel):
    activities: List[dict] = Field(..., description="최근 활동 목록")
    total_count: int = Field(..., description="전체 활동 수")


class WeeklyStatsResponse(BaseModel):
    problems_solved: int = Field(..., description="이번 주 해결 문제 수")
    new_algorithms: int = Field(..., description="새로 학습한 알고리즘 수")
    average_difficulty: float = Field(..., description="평균 문제 난이도")
    consistency_score: float = Field(..., description="꾸준함 점수")
    improvement_rate: float = Field(..., description="실력 향상도")


class TodaysProblemsResponse(BaseModel):
    recommended_problems: List[dict] = Field(..., description="오늘의 추천 문제")
    total_count: int = Field(..., description="추천 문제 총 개수")
    difficulty_distribution: dict = Field(..., description="난이도 분포")


class ReviewProblemsResponse(BaseModel):
    review_problems: List[dict] = Field(..., description="복습할 문제 목록")
    total_count: int = Field(..., description="복습 문제 총 개수")
    priority_scores: List[float] = Field(..., description="우선순위 점수")


class UserProfileResponse(BaseModel):
    handle: str
    bio: Optional[str] = None
    tier: int
    rating: int
    solved_count: int
    class_level: int
    profile_image_url: Optional[str] = None
    joined_at: datetime
    rank: int
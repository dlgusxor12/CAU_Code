from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class RecommendationMode(str, Enum):
    AI_RECOMMENDATION = "ai_recommendation"
    APPROPRIATE_DIFFICULTY = "appropriate_difficulty"
    CHALLENGE = "challenge"


class ProblemTier(str, Enum):
    BRONZE_5 = "b5"
    BRONZE_4 = "b4"
    BRONZE_3 = "b3"
    BRONZE_2 = "b2"
    BRONZE_1 = "b1"
    SILVER_5 = "s5"
    SILVER_4 = "s4"
    SILVER_3 = "s3"
    SILVER_2 = "s2"
    SILVER_1 = "s1"
    GOLD_5 = "g5"
    GOLD_4 = "g4"
    GOLD_3 = "g3"
    GOLD_2 = "g2"
    GOLD_1 = "g1"
    PLATINUM_5 = "p5"
    PLATINUM_4 = "p4"
    PLATINUM_3 = "p3"
    PLATINUM_2 = "p2"
    PLATINUM_1 = "p1"
    DIAMOND_5 = "d5"
    DIAMOND_4 = "d4"
    DIAMOND_3 = "d3"
    DIAMOND_2 = "d2"
    DIAMOND_1 = "d1"
    RUBY_5 = "r5"
    RUBY_4 = "r4"
    RUBY_3 = "r3"
    RUBY_2 = "r2"
    RUBY_1 = "r1"


class ProblemRecommendationRequest(BaseModel):
    mode: RecommendationMode = Field(..., description="추천 모드")
    count: int = Field(default=10, ge=1, le=50, description="추천 문제 개수")
    tier: Optional[ProblemTier] = Field(None, description="원하는 티어")
    algorithm: Optional[str] = Field(None, description="알고리즘 유형")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="난이도 (1-5)")


class ProblemRecommendationResponse(BaseModel):
    problems: List[Dict] = Field(..., description="추천 문제 목록")
    total_count: int = Field(..., description="추천된 문제 수")
    recommendation_accuracy: float = Field(..., description="추천 정확도")
    mode_used: RecommendationMode = Field(..., description="사용된 추천 모드")
    filters_applied: Dict = Field(..., description="적용된 필터")


class ProblemInfoRequest(BaseModel):
    problem_id: int = Field(..., ge=1000, description="문제 번호")


class ProblemInfoResponse(BaseModel):
    problem_id: int = Field(..., description="문제 번호")
    title: str = Field(..., description="문제 제목")
    time_limit: Optional[int] = Field(None, description="시간 제한 (ms)")
    memory_limit: Optional[int] = Field(None, description="메모리 제한 (KB)")
    submission_count: int = Field(..., description="제출 횟수")
    accepted_count: int = Field(..., description="정답 횟수")
    solved_count: int = Field(..., description="해결한 사람 수")
    correct_ratio: float = Field(..., description="정답 비율")
    tier: int = Field(..., description="티어")
    tier_name: str = Field(..., description="티어 이름")
    algorithm_tags: List[str] = Field(..., description="알고리즘 태그")
    difficulty_class: int = Field(..., description="난이도 클래스")


class ProblemVerificationRequest(BaseModel):
    problem_id: int = Field(..., ge=1000, description="문제 번호")
    username: str = Field(..., description="사용자 이름")


class ProblemVerificationResponse(BaseModel):
    problem_id: int = Field(..., description="문제 번호")
    username: str = Field(..., description="사용자 이름")
    is_solved: bool = Field(..., description="해결 여부")
    solved_at: Optional[str] = Field(None, description="해결 시간")
    verification_time: str = Field(..., description="검증 시간")


class ProblemStatsResponse(BaseModel):
    ai_recommended_problems_count: int = Field(..., description="AI가 추천해준 문제 수")
    user_completion_rate: float = Field(..., description="사용자 해결 완료율")
    current_user_tier: Dict[str, Any] = Field(..., description="현재 사용자 티어 정보")


class ProblemFilterRequest(BaseModel):
    tier_min: Optional[int] = Field(None, ge=0, le=31, description="최소 티어")
    tier_max: Optional[int] = Field(None, ge=0, le=31, description="최대 티어")
    algorithm: Optional[str] = Field(None, description="알고리즘 유형")
    difficulty_class: Optional[int] = Field(None, ge=1, le=5, description="난이도 클래스")
    solved_count_min: Optional[int] = Field(None, ge=0, description="최소 해결자 수")
    solved_count_max: Optional[int] = Field(None, ge=0, description="최대 해결자 수")
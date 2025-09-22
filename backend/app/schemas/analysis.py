from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="분석할 코드")
    problem_id: int = Field(..., ge=1000, description="문제 번호")
    language: str = Field(..., description="프로그래밍 언어")


class CodeAnalysisResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="코드 품질 점수 (0-100)")
    submitted_code: str = Field(..., description="제출된 코드")
    strengths: str = Field(..., max_length=100, description="잘한 점 (100자 이내)")
    improvements: str = Field(..., max_length=100, description="개선 사항 (100자 이내)")
    core_concept: str = Field(..., description="핵심 설명")
    time_complexity: str = Field(..., description="시간 복잡도")
    algorithm_type: str = Field(..., description="알고리즘 유형")
    analysis_timestamp: datetime = Field(..., description="분석 시간")


class OptimizedCodeRequest(BaseModel):
    problem_id: int = Field(..., ge=1000, description="문제 번호")
    language: str = Field(..., description="프로그래밍 언어")
    current_code: Optional[str] = Field(None, description="현재 코드 (선택사항)")


class OptimizedCodeResponse(BaseModel):
    optimized_code: str = Field(..., description="AI가 제안하는 최적 코드")
    explanation: str = Field(..., description="코드 설명 (시간복잡도 포함)")
    time_complexity: str = Field(..., description="시간 복잡도")
    space_complexity: str = Field(..., description="공간 복잡도")
    key_insights: List[str] = Field(..., description="핵심 개념들")
    performance_comparison: Optional[Dict] = Field(None, description="성능 비교")


class FeedbackSummaryResponse(BaseModel):
    total_analyses: int = Field(..., description="총 분석 횟수")
    average_score: float = Field(..., description="평균 점수")
    most_common_weaknesses: List[str] = Field(..., description="가장 흔한 약점들")
    improvement_trends: Dict[str, float] = Field(..., description="개선 추이")
    recommended_study_topics: List[str] = Field(..., description="추천 학습 주제")


class CodeMetricsResponse(BaseModel):
    lines_of_code: int = Field(..., description="코드 라인 수")
    cyclomatic_complexity: Optional[int] = Field(None, description="순환 복잡도")
    maintainability_index: Optional[float] = Field(None, description="유지보수성 지수")
    readability_score: float = Field(..., description="가독성 점수")
    efficiency_rating: str = Field(..., description="효율성 등급")


class AlgorithmExplanationRequest(BaseModel):
    algorithm_type: str = Field(..., description="알고리즘 유형")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="설명 난이도")


class AlgorithmExplanationResponse(BaseModel):
    algorithm_type: str = Field(..., description="알고리즘 유형")
    explanation: str = Field(..., description="핵심 개념 설명")
    time_complexity: str = Field(..., description="일반적인 시간복잡도")
    use_cases: List[str] = Field(..., description="활용 사례")
    related_algorithms: List[str] = Field(..., description="관련 알고리즘")
    difficulty_rating: int = Field(..., description="난이도 평가")


class CodeComparisonRequest(BaseModel):
    original_code: str = Field(..., description="원본 코드")
    improved_code: str = Field(..., description="개선된 코드")
    language: str = Field(..., description="프로그래밍 언어")


class CodeComparisonResponse(BaseModel):
    original_analysis: Dict = Field(..., description="원본 코드 분석")
    improved_analysis: Dict = Field(..., description="개선된 코드 분석")
    improvement_summary: str = Field(..., description="개선 요약")
    performance_gain: float = Field(..., description="성능 향상도")
    recommendation: str = Field(..., description="추천 사항")
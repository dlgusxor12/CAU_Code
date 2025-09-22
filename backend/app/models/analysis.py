from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class CodeAnalysis(BaseModel):
    code: str
    language: str
    problem_id: int
    score: int  # 0-100
    strengths: str  # max 100 chars
    improvements: str  # max 100 chars
    time_complexity: str
    space_complexity: Optional[str] = None
    algorithm_type: str
    analysis_timestamp: datetime


class OptimizedCodeResponse(BaseModel):
    original_code: str
    optimized_code: str
    explanation: str
    time_complexity_before: str
    time_complexity_after: str
    improvements: List[str]
    estimated_performance_gain: float


class FeedbackResponse(BaseModel):
    score: int
    submitted_code: str
    strengths: str
    improvements: str
    core_concept: str
    time_complexity: str
    algorithm_explanation: str


class CodeFeedbackRequest(BaseModel):
    code: str
    problem_id: int
    language: str
    user_id: Optional[str] = None


class AIOptimizationRequest(BaseModel):
    problem_description: str
    language: str
    current_code: Optional[str] = None


class PerformanceMetrics(BaseModel):
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None
    test_cases_passed: int = 0
    total_test_cases: int = 0
    edge_cases_handled: bool = False
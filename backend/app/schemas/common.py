from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum


DataT = TypeVar('DataT')


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class APIResponse(BaseModel, Generic[DataT]):
    status: ResponseStatus = Field(..., description="응답 상태")
    message: str = Field(..., description="응답 메시지")
    data: Optional[DataT] = Field(None, description="응답 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")


class ErrorResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: str = Field(..., description="에러 코드")
    error_message: str = Field(..., description="에러 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="에러 세부사항")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시간")


class PaginationRequest(BaseModel):
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=20, ge=1, le=100, description="페이지 크기")
    sort_by: Optional[str] = Field(None, description="정렬 기준")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="정렬 순서")


class PaginationResponse(BaseModel, Generic[DataT]):
    items: List[DataT] = Field(..., description="아이템 목록")
    total: int = Field(..., description="전체 아이템 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="서비스 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="확인 시간")
    version: str = Field(..., description="서비스 버전")
    uptime: float = Field(..., description="가동 시간 (초)")
    dependencies: Dict[str, str] = Field(..., description="의존성 상태")


class TierInfo(BaseModel):
    tier_id: int = Field(..., description="티어 ID")
    tier_name: str = Field(..., description="티어 이름")
    tier_color: str = Field(..., description="티어 색상")
    tier_image_url: Optional[str] = Field(None, description="티어 이미지 URL")


class AlgorithmTag(BaseModel):
    tag_id: int = Field(..., description="태그 ID")
    tag_name_ko: str = Field(..., description="한국어 태그명")
    tag_name_en: str = Field(..., description="영어 태그명")
    problem_count: int = Field(..., description="해당 태그 문제 수")
    difficulty_avg: float = Field(..., description="평균 난이도")


class FilterOptions(BaseModel):
    available_tiers: List[TierInfo] = Field(..., description="사용 가능한 티어 목록")
    available_algorithms: List[AlgorithmTag] = Field(..., description="사용 가능한 알고리즘 목록")
    difficulty_classes: List[int] = Field(..., description="난이도 클래스 목록")
    min_problem_id: int = Field(..., description="최소 문제 번호")
    max_problem_id: int = Field(..., description="최대 문제 번호")


class SystemMetrics(BaseModel):
    api_requests_per_minute: int = Field(..., description="분당 API 요청 수")
    average_response_time: float = Field(..., description="평균 응답 시간 (ms)")
    solved_ac_api_status: str = Field(..., description="solved.ac API 상태")
    openai_api_status: str = Field(..., description="OpenAI API 상태")
    cache_hit_ratio: float = Field(..., description="캐시 적중률")
    memory_usage: float = Field(..., description="메모리 사용률")


class CacheInfo(BaseModel):
    cache_key: str = Field(..., description="캐시 키")
    hit_count: int = Field(..., description="적중 횟수")
    miss_count: int = Field(..., description="실패 횟수")
    cache_size: int = Field(..., description="캐시 크기")
    ttl: int = Field(..., description="TTL (초)")
    last_updated: datetime = Field(..., description="마지막 업데이트")
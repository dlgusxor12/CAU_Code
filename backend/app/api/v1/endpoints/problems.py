from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime

from app.services.problem_service import ProblemService
from app.services.solvedac_service import SolvedACService
from app.schemas.problem import (
    RecommendationMode,
    ProblemRecommendationResponse,
    ProblemInfoResponse,
    ProblemVerificationRequest,
    ProblemVerificationResponse,
    ProblemFilterRequest,
    ProblemStatsResponse
)
from app.schemas.common import APIResponse
from app.utils.logging import LoggerMixin
from app.core.exceptions import UserNotFoundError, ProblemNotFoundError

router = APIRouter()


class ProblemEndpoints(LoggerMixin):
    def __init__(self):
        self.problem_service = ProblemService()
        self.solvedac_service = SolvedACService()


problem_endpoints = ProblemEndpoints()


@router.get("/recommendations", response_model=APIResponse[ProblemRecommendationResponse])
async def get_problem_recommendations(
    username: str = Query(..., description="사용자명"),
    mode: RecommendationMode = Query(RecommendationMode.AI_RECOMMENDATION, description="추천 모드"),
    count: int = Query(10, ge=1, le=50, description="추천할 문제 개수"),
    tier_min: Optional[int] = Query(None, ge=0, le=31, description="최소 티어"),
    tier_max: Optional[int] = Query(None, ge=0, le=31, description="최대 티어"),
    algorithm: Optional[str] = Query(None, description="알고리즘 유형"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="난이도 클래스")
):
    """문제 추천 (적응형, 유사, 도전 모드)"""
    try:
        problem_endpoints.log_user_action(username, "request_recommendations", {
            "mode": mode.value,
            "count": count
        })

        # 필터 객체 생성
        filters = ProblemFilterRequest(
            tier_min=tier_min,
            tier_max=tier_max,
            algorithm=algorithm,
            difficulty_class=difficulty
        )

        # 문제 추천 서비스 호출
        recommendation_result = await problem_endpoints.problem_service.get_problem_recommendations(
            username=username,
            mode=mode,
            count=count,
            filters=filters
        )

        return APIResponse(
            status="success",
            message=f"{mode.value} 모드로 {len(recommendation_result['problems'])}개 문제를 추천했습니다",
            data=recommendation_result
        )

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"사용자 '{username}'을 찾을 수 없습니다")
    except Exception as e:
        problem_endpoints.log_error(f"Recommendation error for {username}", e)
        raise HTTPException(status_code=500, detail="문제 추천 중 오류가 발생했습니다")


@router.get("/stats", response_model=APIResponse[ProblemStatsResponse])
async def get_problem_stats(username: str = Query(..., description="사용자명")):
    """문제 추천 통계 정보"""
    try:
        stats = await problem_endpoints.problem_service.get_problem_stats(username)

        return APIResponse(
            status="success",
            message="문제 추천 통계를 성공적으로 조회했습니다",
            data=stats
        )

    except Exception as e:
        problem_endpoints.log_error(f"Problem stats error for {username}", e)
        raise HTTPException(status_code=500, detail="문제 통계 조회 중 오류가 발생했습니다")


@router.get("/filter-options")
async def get_filter_options():
    """필터 옵션 정보"""
    try:
        options = await problem_endpoints.problem_service.get_filter_options()

        return APIResponse(
            status="success",
            message="필터 옵션을 성공적으로 조회했습니다",
            data=options
        )

    except Exception as e:
        problem_endpoints.log_error("Filter options error", e)
        raise HTTPException(status_code=500, detail="필터 옵션 조회 중 오류가 발생했습니다")


@router.post("/search")
async def search_problems_with_filters(filters: ProblemFilterRequest):
    """필터를 적용한 문제 검색"""
    try:
        problems = await problem_endpoints.problem_service.search_problems_with_filters(
            filters=filters,
            count=20
        )

        return APIResponse(
            status="success",
            message=f"{len(problems)}개의 문제를 찾았습니다",
            data={
                "problems": problems,
                "total_count": len(problems),
                "filters_applied": filters.dict(exclude_none=True)
            }
        )

    except Exception as e:
        problem_endpoints.log_error("Problem search error", e)
        raise HTTPException(status_code=500, detail="문제 검색 중 오류가 발생했습니다")


@router.get("/{problem_id}", response_model=APIResponse[ProblemInfoResponse])
async def get_problem_info(problem_id: int):
    """특정 문제 정보 조회"""
    try:
        problem_info = await problem_endpoints.solvedac_service.get_problem_info(problem_id)

        # ProblemInfoResponse 형태로 변환
        problem_response = ProblemInfoResponse(
            problem_id=problem_info.get("problem_id", problem_id),
            title=problem_info.get("title", "Unknown"),
            time_limit=None,  # solved.ac API에서 제공하지 않음
            memory_limit=None,  # solved.ac API에서 제공하지 않음
            submission_count=0,  # solved.ac API에서 제공하지 않음
            accepted_count=problem_info.get("accepted_user_count", 0),
            solved_count=problem_info.get("accepted_user_count", 0),
            correct_ratio=0.0,  # 계산 필요
            tier=problem_info.get("tier", 0),
            tier_name=problem_info.get("tier_name", "Unknown"),
            algorithm_tags=problem_info.get("tags", []),
            difficulty_class=min(5, max(1, problem_info.get("tier", 0) // 5 + 1))  # 티어를 클래스로 변환
        )

        return APIResponse(
            status="success",
            message="문제 정보를 성공적으로 조회했습니다",
            data=problem_response
        )

    except ProblemNotFoundError:
        raise HTTPException(status_code=404, detail=f"문제 {problem_id}를 찾을 수 없습니다")
    except Exception as e:
        problem_endpoints.log_error(f"Problem info error for {problem_id}", e)
        raise HTTPException(status_code=500, detail="문제 정보 조회 중 오류가 발생했습니다")


@router.post("/{problem_id}/verify", response_model=APIResponse[ProblemVerificationResponse])
async def verify_problem_solved(problem_id: int, request: ProblemVerificationRequest):
    """문제 해결 여부 검증"""
    try:
        problem_endpoints.log_user_action(request.username, "verify_problem", {
            "problem_id": problem_id
        })

        is_solved = await problem_endpoints.solvedac_service.verify_problem_solved(
            request.username, problem_id
        )

        verification_response = ProblemVerificationResponse(
            problem_id=problem_id,
            username=request.username,
            is_solved=is_solved,
            solved_at=None,  # solved.ac API에서 제공하지 않음
            verification_time=str(datetime.now())
        )

        return APIResponse(
            status="success",
            message=f"문제 {problem_id} 해결 여부를 확인했습니다",
            data=verification_response
        )

    except Exception as e:
        problem_endpoints.log_error(f"Problem verification error for {problem_id}", e)
        raise HTTPException(status_code=500, detail="문제 해결 여부 확인 중 오류가 발생했습니다")


@router.get("/recommendations/adaptive")
async def get_adaptive_recommendations(
    username: str = Query(..., description="사용자명"),
    count: int = Query(10, ge=1, le=20, description="추천할 문제 개수")
):
    """AI 기반 적응형 추천"""
    try:
        recommendation_result = await problem_endpoints.problem_service.get_problem_recommendations(
            username=username,
            mode=RecommendationMode.ADAPTIVE,
            count=count
        )

        return APIResponse(
            status="success",
            message=f"AI 기반으로 {len(recommendation_result['problems'])}개 문제를 추천했습니다",
            data=recommendation_result
        )

    except Exception as e:
        problem_endpoints.log_error(f"Adaptive recommendations error for {username}", e)
        raise HTTPException(status_code=500, detail="적응형 추천 중 오류가 발생했습니다")


@router.get("/recommendations/similar")
async def get_similar_recommendations(
    username: str = Query(..., description="사용자명"),
    count: int = Query(10, ge=1, le=20, description="추천할 문제 개수")
):
    """유사한 유형 문제 추천"""
    try:
        recommendation_result = await problem_endpoints.problem_service.get_problem_recommendations(
            username=username,
            mode=RecommendationMode.SIMILAR,
            count=count
        )

        return APIResponse(
            status="success",
            message=f"유사한 유형의 {len(recommendation_result['problems'])}개 문제를 추천했습니다",
            data=recommendation_result
        )

    except Exception as e:
        problem_endpoints.log_error(f"Similar recommendations error for {username}", e)
        raise HTTPException(status_code=500, detail="유사 문제 추천 중 오류가 발생했습니다")


@router.get("/recommendations/challenge")
async def get_challenge_recommendations(
    username: str = Query(..., description="사용자명"),
    count: int = Query(10, ge=1, le=20, description="추천할 문제 개수")
):
    """도전 모드 (어려운 문제) 추천"""
    try:
        recommendation_result = await problem_endpoints.problem_service.get_problem_recommendations(
            username=username,
            mode=RecommendationMode.CHALLENGE,
            count=count
        )

        return APIResponse(
            status="success",
            message=f"도전용 {len(recommendation_result['problems'])}개 문제를 추천했습니다",
            data=recommendation_result
        )

    except Exception as e:
        problem_endpoints.log_error(f"Challenge recommendations error for {username}", e)
        raise HTTPException(status_code=500, detail="도전 문제 추천 중 오류가 발생했습니다")
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.services.analysis_service import AnalysisService
from app.services.guide_service import GuideService
from app.schemas.analysis import (
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    OptimizedCodeRequest,
    OptimizedCodeResponse,
    FeedbackSummaryResponse,
    AlgorithmExplanationRequest,
    AlgorithmExplanationResponse,
    CodeComparisonRequest,
    CodeComparisonResponse
)
from app.schemas.common import APIResponse, ResponseStatus
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

def get_analysis_service() -> AnalysisService:
    return AnalysisService()

def get_guide_service() -> GuideService:
    return GuideService()

@router.post("/feedback", response_model=APIResponse[CodeAnalysisResponse])
async def analyze_code(
    request: CodeAnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    코드 분석 및 피드백 생성
    AI를 통해 코드를 분석하고 100점 만점으로 점수를 산정합니다.
    """
    try:
        logger.info(f"Analyzing code for problem {request.problem_id}")

        # 코드 분석 실행
        analysis_result = await service.analyze_code(
            code=request.code,
            problem_id=request.problem_id,
            language=request.language,
            username="dlgusxor12"  # 현재 하드코딩된 사용자
        )

        # 응답 데이터 구성
        response_data = CodeAnalysisResponse(
            score=analysis_result["score"],
            submitted_code=analysis_result["submitted_code"],
            strengths=analysis_result["strengths"],
            improvements=analysis_result["improvements"],
            core_concept=analysis_result["core_concept"],
            time_complexity=analysis_result["time_complexity"],
            algorithm_type=analysis_result["algorithm_type"],
            language=analysis_result["language"],
            analysis_timestamp=analysis_result["analysis_timestamp"]
        )

        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="코드 분석이 완료되었습니다."
        )

    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail="코드 분석 중 오류가 발생했습니다.")

@router.post("/feedback/submission/{submission_id}", response_model=APIResponse[CodeAnalysisResponse])
async def analyze_submitted_code(
    submission_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    Guide 페이지에서 제출된 코드 분석
    submission_id를 통해 제출된 코드를 가져와 분석합니다.
    """
    try:
        logger.info(f"Analyzing submitted code: {submission_id}")

        # 제출된 코드 정보 가져오기
        submitted_data = guide_service.get_submitted_code(submission_id)
        if not submitted_data:
            raise HTTPException(status_code=404, detail="제출된 코드를 찾을 수 없습니다.")

        # 코드 분석 실행
        analysis_result = await analysis_service.analyze_code(
            code=submitted_data["code"],
            problem_id=submitted_data["problem_id"],
            language=submitted_data["language"],
            username="dlgusxor12"
        )

        # 응답 데이터 구성
        response_data = CodeAnalysisResponse(
            score=analysis_result["score"],
            submitted_code=analysis_result["submitted_code"],
            strengths=analysis_result["strengths"],
            improvements=analysis_result["improvements"],
            core_concept=analysis_result["core_concept"],
            time_complexity=analysis_result["time_complexity"],
            algorithm_type=analysis_result["algorithm_type"],
            language=analysis_result["language"],
            analysis_timestamp=analysis_result["analysis_timestamp"]
        )

        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="제출된 코드 분석이 완료되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing submitted code: {str(e)}")
        raise HTTPException(status_code=500, detail="제출된 코드 분석 중 오류가 발생했습니다.")

@router.post("/optimize", response_model=APIResponse[OptimizedCodeResponse])
async def get_optimized_code(
    request: OptimizedCodeRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    AI 최적 코드 생성
    AI가 생각하는 해당 문제의 최적화된 코드를 생성합니다.
    """
    try:
        logger.info(f"Generating optimized code for problem {request.problem_id}")

        # 최적화된 코드 생성
        optimization_result = await service.generate_optimized_code(
            problem_id=request.problem_id,
            language=request.language,
            current_code=request.current_code
        )

        # 응답 데이터 구성
        response_data = OptimizedCodeResponse(
            optimized_code=optimization_result["optimized_code"],
            explanation=optimization_result["explanation"],
            time_complexity=optimization_result["time_complexity"],
            space_complexity=optimization_result["space_complexity"],
            key_insights=optimization_result["key_insights"],
            performance_comparison=optimization_result.get("performance_comparison")
        )

        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="최적화된 코드가 생성되었습니다."
        )

    except Exception as e:
        logger.error(f"Error generating optimized code: {str(e)}")
        raise HTTPException(status_code=500, detail="최적화 코드 생성 중 오류가 발생했습니다.")

@router.get("/history/{username}", response_model=APIResponse[FeedbackSummaryResponse])
async def get_analysis_history(
    username: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    사용자 분석 이력 조회
    사용자의 코드 분석 통계와 개선 추이를 확인합니다.
    """
    try:
        logger.info(f"Fetching analysis history for user: {username}")

        # 피드백 요약 통계 조회
        summary_result = await service.get_feedback_summary(username)

        # 응답 데이터 구성
        response_data = FeedbackSummaryResponse(
            total_analyses=summary_result["total_analyses"],
            average_score=summary_result["average_score"],
            most_common_weaknesses=summary_result["most_common_weaknesses"],
            improvement_trends=summary_result["improvement_trends"],
            recommended_study_topics=summary_result["recommended_study_topics"]
        )

        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message=f"{username} 사용자의 분석 이력을 조회했습니다."
        )

    except Exception as e:
        logger.error(f"Error fetching analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail="분석 이력 조회 중 오류가 발생했습니다.")

@router.post("/algorithm/explain", response_model=APIResponse[AlgorithmExplanationResponse])
async def get_algorithm_explanation(
    request: AlgorithmExplanationRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    알고리즘 설명 조회
    특정 알고리즘 유형에 대한 핵심 개념과 설명을 제공합니다.
    """
    try:
        logger.info(f"Getting explanation for algorithm: {request.algorithm_type}")

        # 알고리즘 설명 조회
        explanation_result = await service.get_algorithm_explanation(
            algorithm_type=request.algorithm_type,
            difficulty_level=request.difficulty_level or 3
        )

        # 응답 데이터 구성
        response_data = AlgorithmExplanationResponse(
            algorithm_type=explanation_result["algorithm_type"],
            explanation=explanation_result["explanation"],
            time_complexity=explanation_result["time_complexity"],
            use_cases=explanation_result["use_cases"],
            related_algorithms=explanation_result["related_algorithms"],
            difficulty_rating=explanation_result["difficulty_rating"]
        )

        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message=f"{request.algorithm_type} 알고리즘 설명을 조회했습니다."
        )

    except Exception as e:
        logger.error(f"Error getting algorithm explanation: {str(e)}")
        raise HTTPException(status_code=500, detail="알고리즘 설명 조회 중 오류가 발생했습니다.")

@router.post("/compare", response_model=APIResponse[CodeComparisonResponse])
async def compare_codes(
    request: CodeComparisonRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    코드 비교 분석
    원본 코드와 개선된 코드를 비교하여 성능 향상도를 분석합니다.
    """
    try:
        logger.info("Comparing original and improved code")

        # 코드 비교 분석 실행 (더미 problem_id 사용)
        comparison_result = await service.compare_codes(
            original_code=request.original_code,
            improved_code=request.improved_code,
            language=request.language,
            problem_id=1000  # 더미 problem_id
        )

        # 응답 데이터 구성
        response_data = CodeComparisonResponse(
            original_analysis=comparison_result["original_analysis"],
            improved_analysis=comparison_result["improved_analysis"],
            improvement_summary=comparison_result["improvement_summary"],
            performance_gain=comparison_result["performance_gain"],
            recommendation=comparison_result["recommendation"]
        )

        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="코드 비교 분석이 완료되었습니다."
        )

    except Exception as e:
        logger.error(f"Error comparing codes: {str(e)}")
        raise HTTPException(status_code=500, detail="코드 비교 분석 중 오류가 발생했습니다.")

@router.get("/status")
async def get_analysis_status():
    """
    분석 서비스 상태 확인
    """
    try:
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            data={
                "service": "Analysis API",
                "status": "healthy",
                "features": [
                    "code_analysis",
                    "code_optimization",
                    "algorithm_explanation",
                    "code_comparison",
                    "analysis_history"
                ]
            },
            message="분석 서비스가 정상 작동 중입니다."
        )
    except Exception as e:
        logger.error(f"Error checking analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail="서비스 상태 확인 중 오류가 발생했습니다.")
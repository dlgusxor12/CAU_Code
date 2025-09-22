from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.services.guide_service import GuideService
from app.schemas.guide import (
    ProblemDetailResponse,
    CodeSubmissionRequest,
    CodeSubmissionResponse,
    LanguageInfo,
    LanguageListResponse,
    TemplateResponse,
    SolutionVerificationRequest,
    SolutionVerificationResponse,
    SyntaxCheckRequest,
    SyntaxCheckResponse
)
from app.schemas.common import APIResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

def get_guide_service() -> GuideService:
    return GuideService()

@router.get("/problem/{problem_id}", response_model=APIResponse[ProblemDetailResponse])
async def get_problem_detail(
    problem_id: int,
    service: GuideService = Depends(get_guide_service)
):
    """
    문제 상세 정보 조회
    solved.ac API를 통해 문제의 시간제한, 메모리제한, 정답률 등을 조회합니다.
    """
    try:
        logger.info(f"Fetching problem detail for problem_id: {problem_id}")

        problem_detail = await service.get_problem_detail(problem_id)

        return APIResponse(
            status="success",
            data=problem_detail,
            message="문제 정보를 성공적으로 조회했습니다."
        )

    except ValueError as e:
        logger.warning(f"Problem not found: {problem_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching problem detail: {str(e)}")
        raise HTTPException(status_code=500, detail="문제 정보 조회 중 오류가 발생했습니다.")

@router.post("/submit-code", response_model=APIResponse[CodeSubmissionResponse])
async def submit_code(
    request: CodeSubmissionRequest,
    service: GuideService = Depends(get_guide_service)
):
    """
    코드 제출 및 임시 저장
    사용자가 작성한 코드를 임시로 저장하고 피드백 페이지에서 사용할 수 있도록 합니다.
    """
    try:
        logger.info(f"Submitting code for problem {request.problem_id}")

        submission_id = service.submit_code(
            problem_id=request.problem_id,
            language=request.language,
            code=request.code
        )

        response_data = CodeSubmissionResponse(
            submission_id=submission_id,
            message="코드가 성공적으로 제출되었습니다."
        )

        return APIResponse(
            status="success",
            data=response_data,
            message="코드 제출이 완료되었습니다."
        )

    except ValueError as e:
        logger.warning(f"Invalid language or code submission: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting code: {str(e)}")
        raise HTTPException(status_code=500, detail="코드 제출 중 오류가 발생했습니다.")

@router.get("/languages", response_model=APIResponse[LanguageListResponse])
async def get_supported_languages(
    service: GuideService = Depends(get_guide_service)
):
    """
    지원하는 프로그래밍 언어 목록 조회
    """
    try:
        logger.info("Fetching supported languages")

        languages = service.get_supported_languages()
        response_data = LanguageListResponse(languages=languages)

        return APIResponse(
            status="success",
            data=response_data,
            message="지원 언어 목록을 조회했습니다."
        )

    except Exception as e:
        logger.error(f"Error fetching supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail="언어 목록 조회 중 오류가 발생했습니다.")

@router.get("/templates/{language}", response_model=APIResponse[TemplateResponse])
async def get_language_template(
    language: str,
    service: GuideService = Depends(get_guide_service)
):
    """
    언어별 기본 코드 템플릿 조회
    """
    try:
        logger.info(f"Fetching template for language: {language}")

        template = service.get_language_template(language)
        response_data = TemplateResponse(
            language=language,
            template=template
        )

        return APIResponse(
            status="success",
            data=response_data,
            message=f"{language} 템플릿을 조회했습니다."
        )

    except ValueError as e:
        logger.warning(f"Unsupported language requested: {language}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}")
        raise HTTPException(status_code=500, detail="템플릿 조회 중 오류가 발생했습니다.")

@router.post("/verify-solution", response_model=APIResponse[SolutionVerificationResponse])
async def verify_solution(
    request: SolutionVerificationRequest,
    service: GuideService = Depends(get_guide_service)
):
    """
    문제 해결 여부 검증
    solved.ac API를 통해 사용자가 해당 문제를 해결했는지 확인합니다.
    """
    try:
        logger.info(f"Verifying solution for problem {request.problem_id} by user {request.username}")

        verification_result = await service.verify_solution(
            problem_id=request.problem_id,
            username=request.username
        )

        return APIResponse(
            status="success",
            data=verification_result,
            message="문제 해결 여부를 확인했습니다."
        )

    except Exception as e:
        logger.error(f"Error verifying solution: {str(e)}")
        raise HTTPException(status_code=500, detail="해결 여부 확인 중 오류가 발생했습니다.")

@router.post("/check-syntax", response_model=APIResponse[SyntaxCheckResponse])
async def check_syntax(
    request: SyntaxCheckRequest,
    service: GuideService = Depends(get_guide_service)
):
    """
    코드 문법 검사
    기본적인 문법 오류를 검사합니다.
    """
    try:
        logger.info(f"Checking syntax for {request.language} code")

        result = service.check_syntax(request.language, request.code)
        response_data = SyntaxCheckResponse(
            is_valid=result["is_valid"],
            errors=result["errors"],
            warnings=result["warnings"]
        )

        return APIResponse(
            status="success",
            data=response_data,
            message="문법 검사가 완료되었습니다."
        )

    except Exception as e:
        logger.error(f"Error checking syntax: {str(e)}")
        raise HTTPException(status_code=500, detail="문법 검사 중 오류가 발생했습니다.")

@router.get("/submission/{submission_id}")
async def get_submitted_code(
    submission_id: str,
    service: GuideService = Depends(get_guide_service)
):
    """
    제출된 코드 조회 (피드백 페이지 연동용)
    """
    try:
        logger.info(f"Fetching submitted code: {submission_id}")

        code_data = service.get_submitted_code(submission_id)

        if not code_data:
            raise HTTPException(status_code=404, detail="제출된 코드를 찾을 수 없습니다.")

        return APIResponse(
            status="success",
            data=code_data,
            message="제출된 코드를 조회했습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching submitted code: {str(e)}")
        raise HTTPException(status_code=500, detail="코드 조회 중 오류가 발생했습니다.")

@router.post("/submit-for-analysis", response_model=APIResponse[CodeSubmissionResponse])
async def submit_code_for_analysis(
    request: CodeSubmissionRequest,
    service: GuideService = Depends(get_guide_service)
):
    """
    분석을 위한 코드 제출
    Guide 페이지에서 작성한 코드를 바로 피드백 분석으로 연결합니다.
    """
    try:
        logger.info(f"Submitting code for analysis - problem {request.problem_id}")

        submission_id = await service.submit_code_for_analysis(
            problem_id=request.problem_id,
            language=request.language,
            code=request.code
        )

        response_data = CodeSubmissionResponse(
            submission_id=submission_id,
            message="코드가 분석을 위해 제출되었습니다. 피드백 페이지에서 결과를 확인하세요."
        )

        return APIResponse(
            status="success",
            data=response_data,
            message="분석을 위한 코드 제출이 완료되었습니다."
        )

    except Exception as e:
        logger.error(f"Error submitting code for analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="분석용 코드 제출 중 오류가 발생했습니다.")

@router.get("/submission/{submission_id}/info")
async def get_submission_info(
    submission_id: str,
    service: GuideService = Depends(get_guide_service)
):
    """
    제출 정보 상세 조회
    """
    try:
        logger.info(f"Fetching submission info: {submission_id}")

        submission_info = service.get_submission_info(submission_id)

        if not submission_info:
            raise HTTPException(status_code=404, detail="제출 정보를 찾을 수 없습니다.")

        return APIResponse(
            status="success",
            data=submission_info,
            message="제출 정보를 조회했습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching submission info: {str(e)}")
        raise HTTPException(status_code=500, detail="제출 정보 조회 중 오류가 발생했습니다.")
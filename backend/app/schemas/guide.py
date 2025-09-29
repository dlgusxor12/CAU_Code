from typing import Optional, List
from pydantic import BaseModel
from .common import APIResponse

class ProblemDetailResponse(BaseModel):
    """문제 상세 정보 응답"""
    problem_id: int
    title: str
    description: str
    time_limit: int  # milliseconds
    memory_limit: int  # KB
    submission_count: int
    accepted_count: float
    solved_count: int
    success_rate: float
    tier: int
    algorithms: List[str]
    difficulty_class: int

class CodeSubmissionRequest(BaseModel):
    """코드 제출 요청"""
    problem_id: int
    language: str
    code: str

class CodeSubmissionResponse(BaseModel):
    """코드 제출 응답"""
    submission_id: str
    message: str

class LanguageInfo(BaseModel):
    """언어 정보"""
    language: str
    display_name: str
    extension: str
    compile_command: Optional[str]
    run_command: str

class LanguageListResponse(BaseModel):
    """지원 언어 목록 응답"""
    languages: List[LanguageInfo]

class TemplateResponse(BaseModel):
    """언어별 템플릿 응답"""
    language: str
    template: str

class SolutionVerificationRequest(BaseModel):
    """문제 해결 검증 요청"""
    problem_id: int
    username: str = "dlgusxor12"

class SolutionVerificationResponse(BaseModel):
    """문제 해결 검증 응답"""
    is_solved: bool
    message: str
    solved_date: Optional[str] = None

class SyntaxCheckRequest(BaseModel):
    """코드 문법 검사 요청"""
    language: str
    code: str

class SyntaxCheckResponse(BaseModel):
    """코드 문법 검사 응답"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
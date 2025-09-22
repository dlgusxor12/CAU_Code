from fastapi import HTTPException, status


class SolvedACAPIError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Solved.ac API Error: {detail}"
        )


class OpenAIAPIError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI API Error: {detail}"
        )


class UserNotFoundError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found on solved.ac"
        )


class ProblemNotFoundError(HTTPException):
    def __init__(self, problem_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem {problem_id} not found"
        )
import uuid
from typing import Dict, List, Optional
from app.clients.solvedac_client import SolvedACClient
from app.schemas.guide import (
    ProblemDetailResponse,
    LanguageInfo,
    SolutionVerificationResponse
)
from app.utils.cache import cache_get, cache_set
from app.utils.logging import get_logger

logger = get_logger(__name__)

class GuideService:
    def __init__(self):
        self.solvedac_client = SolvedACClient()
        self.supported_languages = {
            "python": LanguageInfo(
                language="python",
                display_name="Python 3",
                extension=".py",
                compile_command=None,
                run_command="python3 {file}"
            ),
            "java": LanguageInfo(
                language="java",
                display_name="Java",
                extension=".java",
                compile_command="javac {file}",
                run_command="java {class}"
            ),
            "cpp": LanguageInfo(
                language="cpp",
                display_name="C++",
                extension=".cpp",
                compile_command="g++ -o {output} {file}",
                run_command="./{output}"
            ),
            "c": LanguageInfo(
                language="c",
                display_name="C",
                extension=".c",
                compile_command="gcc -o {output} {file}",
                run_command="./{output}"
            ),
            "javascript": LanguageInfo(
                language="javascript",
                display_name="JavaScript (Node.js)",
                extension=".js",
                compile_command=None,
                run_command="node {file}"
            )
        }

        self.code_templates = {
            "python": '''# 문제를 해결하는 코드를 작성하세요
def solution():
    # 입력

    # 로직

    # 출력
    pass

if __name__ == "__main__":
    solution()''',

            "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // 입력

        // 로직

        // 출력

        sc.close();
    }
}''',

            "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // 입력

    // 로직

    // 출력

    return 0;
}''',

            "c": '''#include <stdio.h>
#include <stdlib.h>

int main() {
    // 입력

    // 로직

    // 출력

    return 0;
}''',

            "javascript": '''// 입력 처리
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (input) => {
    // 입력 처리

    // 로직

    // 출력

    rl.close();
});'''
        }

        # 임시 코드 저장소를 전역으로 공유 (실제로는 Redis나 DB 사용 권장)
        if not hasattr(GuideService, '_global_code_storage'):
            GuideService._global_code_storage: Dict[str, Dict] = {}
        self.code_storage = GuideService._global_code_storage

    async def get_problem_detail(self, problem_id: int) -> ProblemDetailResponse:
        """문제 상세 정보 조회"""
        try:
            cache_key = f"problem_detail_{problem_id}"
            cached_data = cache_get(cache_key)

            if cached_data:
                logger.info(f"Problem detail cache hit for problem {problem_id}")
                return ProblemDetailResponse(**cached_data)

            # solved.ac API로 문제 정보 조회
            problem_data = await self.solvedac_client.get_problem_info(problem_id)

            if not problem_data:
                raise ValueError(f"Problem {problem_id} not found")

            # 응답 데이터 구성
            accepted_user_count = problem_data.get("acceptedUserCount", 0)
            average_tries = problem_data.get("averageTries", 1.0)

            # 추정 제출 횟수 계산 (맞힌 사람 수 * 평균 시도 횟수)
            estimated_submission_count = int(accepted_user_count * average_tries) if accepted_user_count > 0 else 0

            # 정답률 계산 (실제로는 맞힌 사람 수 / 전체 시도한 사람 수 * 100)
            success_rate = round((accepted_user_count / max(estimated_submission_count, 1)) * 100, 2) if estimated_submission_count > 0 else 0

            detail = ProblemDetailResponse(
                problem_id=problem_data["problemId"],
                title=problem_data["titleKo"],
                description=problem_data.get("description", ""),
                time_limit=problem_data.get("timeLimit", 1000),
                memory_limit=problem_data.get("memoryLimit", 128000),
                submission_count=estimated_submission_count,
                accepted_count=estimated_submission_count,  # 총 정답 제출 횟수 (추정)
                solved_count=accepted_user_count,  # 맞힌 사람 수
                success_rate=success_rate,
                tier=problem_data.get("level", 0),
                algorithms=[tag["displayNames"][0]["name"] for tag in problem_data.get("tags", [])],
                difficulty_class=problem_data.get("level", 0) // 5 + 1
            )

            # 캐시 저장 (30분)
            cache_set(cache_key, detail.dict(), expire=1800)

            logger.info(f"Successfully fetched problem detail for {problem_id}")
            return detail

        except Exception as e:
            logger.error(f"Error fetching problem detail for {problem_id}: {str(e)}")
            raise

    def get_supported_languages(self) -> List[LanguageInfo]:
        """지원하는 언어 목록 반환"""
        return list(self.supported_languages.values())

    def get_language_template(self, language: str) -> str:
        """언어별 템플릿 반환"""
        if language not in self.code_templates:
            raise ValueError(f"Unsupported language: {language}")

        return self.code_templates[language]

    def submit_code(self, problem_id: int, language: str, code: str) -> str:
        """코드 제출 및 임시 저장"""
        try:
            if language not in self.supported_languages:
                raise ValueError(f"Unsupported language: {language}")

            # 고유 제출 ID 생성
            submission_id = str(uuid.uuid4())

            # 임시 저장
            self.code_storage[submission_id] = {
                "problem_id": problem_id,
                "language": language,
                "code": code,
                "timestamp": str(uuid.uuid1().time)
            }

            logger.info(f"Code submitted for problem {problem_id} with submission ID {submission_id}")
            return submission_id

        except Exception as e:
            logger.error(f"Error submitting code for problem {problem_id}: {str(e)}")
            raise

    def get_submitted_code(self, submission_id: str) -> Optional[Dict]:
        """제출된 코드 조회"""
        return self.code_storage.get(submission_id)

    async def submit_code_for_analysis(self, problem_id: int, language: str, code: str) -> str:
        """분석을 위한 코드 제출 (피드백 페이지 연동용)"""
        try:
            # 기존 submit_code 메서드 재사용
            submission_id = self.submit_code(problem_id, language, code)

            logger.info(f"Code submitted for analysis: {submission_id}")
            return submission_id

        except Exception as e:
            logger.error(f"Error submitting code for analysis: {str(e)}")
            raise

    def get_submission_info(self, submission_id: str) -> Optional[Dict]:
        """제출 정보 상세 조회 (분석 페이지용)"""
        submission_data = self.code_storage.get(submission_id)
        if not submission_data:
            return None

        return {
            "submission_id": submission_id,
            "problem_id": submission_data["problem_id"],
            "language": submission_data["language"],
            "code": submission_data["code"],
            "submitted_at": submission_data["timestamp"],
            "code_lines": len(submission_data["code"].split('\n')),
            "code_length": len(submission_data["code"])
        }

    async def verify_solution(self, problem_id: int, username: str = "dlgusxor12") -> SolutionVerificationResponse:
        """문제 해결 여부 검증"""
        try:
            # solved.ac API로 사용자가 해결한 문제 확인
            # query: s@username (solved by username)
            query = f"s@{username}"
            search_result = await self.solvedac_client.search_problems(query, problem_id)

            # 검색 결과에서 해당 문제 ID가 있는지 확인
            is_solved = False
            solved_date = None

            if search_result and "items" in search_result:
                for problem in search_result["items"]:
                    if problem.get("problemId") == problem_id:
                        is_solved = True
                        # solved.ac API에서는 정확한 해결 날짜를 제공하지 않으므로 현재 날짜 사용
                        solved_date = "2025-01-01"  # TODO: 실제 해결 날짜 구현 필요
                        break

            message = "문제를 해결하셨습니다!" if is_solved else "아직 문제를 해결하지 않으셨습니다."

            return SolutionVerificationResponse(
                is_solved=is_solved,
                message=message,
                solved_date=solved_date
            )

        except Exception as e:
            logger.error(f"Error verifying solution for problem {problem_id}: {str(e)}")
            return SolutionVerificationResponse(
                is_solved=False,
                message="검증 중 오류가 발생했습니다.",
                solved_date=None
            )

    def check_syntax(self, language: str, code: str) -> Dict:
        """간단한 문법 검사 (기본적인 검사만)"""
        try:
            errors = []
            warnings = []

            if language == "python":
                try:
                    compile(code, '<string>', 'exec')
                except SyntaxError as e:
                    errors.append(f"Syntax Error: {str(e)}")

            elif language in ["java", "cpp", "c"]:
                # 기본적인 괄호 매칭 검사
                brackets = {'(': ')', '[': ']', '{': '}'}
                stack = []
                for char in code:
                    if char in brackets:
                        stack.append(char)
                    elif char in brackets.values():
                        if not stack or brackets[stack.pop()] != char:
                            errors.append("Bracket mismatch detected")
                            break

                if stack:
                    errors.append("Unclosed brackets detected")

            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }

        except Exception as e:
            logger.error(f"Error checking syntax: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Syntax check failed: {str(e)}"],
                "warnings": []
            }
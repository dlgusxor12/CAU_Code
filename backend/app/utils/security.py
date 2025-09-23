import re
import html
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """보안 검증 유틸리티"""

    @staticmethod
    def sanitize_html(input_string: str) -> str:
        """HTML 태그 제거 및 이스케이프"""
        if not input_string:
            return ""

        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', input_string)
        # HTML 엔티티 이스케이프
        clean_text = html.escape(clean_text)
        return clean_text.strip()

    @staticmethod
    def validate_solvedac_username(username: str) -> bool:
        """
        solved.ac 사용자명 유효성 검증
        - 3-20자 길이
        - 영문, 숫자, 언더스코어만 허용
        - 첫 글자는 영문만 허용
        """
        if not username:
            return False

        # 길이 검증
        if not (3 <= len(username) <= 20):
            return False

        # 패턴 검증: 영문으로 시작, 영문/숫자/언더스코어 조합
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_verification_code(code: str) -> bool:
        """
        인증 코드 형식 검증
        형식: CAU-CODE-{12자리 영숫자}
        """
        if not code:
            return False

        pattern = r'^CAU-CODE-[A-Za-z0-9]{12}$'
        return bool(re.match(pattern, code))

    @staticmethod
    def is_safe_string(input_string: str, max_length: int = 1000) -> bool:
        """
        안전한 문자열인지 검증
        - SQL Injection 패턴 확인
        - Script 태그 확인
        - 길이 제한 확인
        """
        if not input_string:
            return True

        # 길이 검증
        if len(input_string) > max_length:
            return False

        # 위험한 패턴들
        dangerous_patterns = [
            r'<script.*?>.*?</script>',  # script 태그
            r'javascript:',  # javascript: 프로토콜
            r'on\w+\s*=',  # on* 이벤트 핸들러
            r'(union|select|insert|update|delete|drop|alter|create)\s+',  # SQL 키워드
            r'[\'"]\s*(or|and)\s+[\'"]\s*=\s*[\'"]',  # SQL injection 패턴
            r'exec\s*\(',  # 실행 함수
            r'eval\s*\(',  # eval 함수
        ]

        input_lower = input_string.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern} in input: {input_string[:100]}")
                return False

        return True

    @staticmethod
    def validate_bio_content(bio: str) -> dict:
        """
        solved.ac bio 내용 검증
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        if not bio:
            return result

        # 길이 검증 (solved.ac bio 제한: 500자)
        if len(bio) > 500:
            result["is_valid"] = False
            result["errors"].append("자기소개는 500자를 초과할 수 없습니다.")

        # 안전성 검증
        if not SecurityValidator.is_safe_string(bio, 500):
            result["is_valid"] = False
            result["errors"].append("안전하지 않은 내용이 포함되어 있습니다.")

        # 인증 코드 형식 확인 (경고)
        cau_code_pattern = r'CAU-CODE-[A-Za-z0-9]+'
        if re.search(cau_code_pattern, bio):
            codes = re.findall(cau_code_pattern, bio)
            for code in codes:
                if not SecurityValidator.validate_verification_code(code):
                    result["warnings"].append(f"인증 코드 형식이 올바르지 않습니다: {code}")

        return result

    @staticmethod
    def extract_client_info(request) -> dict:
        """
        클라이언트 정보 추출 (보안 로깅용)
        """
        info = {
            "ip": "unknown",
            "user_agent": "unknown",
            "forwarded_for": None,
            "real_ip": None
        }

        if not request:
            return info

        # IP 주소 추출
        if request.client:
            info["ip"] = request.client.host

        # 헤더 정보 추출
        headers = request.headers
        info["user_agent"] = headers.get("User-Agent", "unknown")
        info["forwarded_for"] = headers.get("X-Forwarded-For")
        info["real_ip"] = headers.get("X-Real-IP")

        # 실제 클라이언트 IP 결정
        if info["forwarded_for"]:
            info["ip"] = info["forwarded_for"].split(",")[0].strip()
        elif info["real_ip"]:
            info["ip"] = info["real_ip"]

        return info

    @staticmethod
    def log_security_event(event_type: str, details: dict, severity: str = "info"):
        """
        보안 이벤트 로깅
        """
        log_data = {
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "timestamp": "now"  # 실제로는 datetime 객체 사용
        }

        if severity == "warning":
            logger.warning(f"Security Event: {event_type} - {details}")
        elif severity == "error":
            logger.error(f"Security Event: {event_type} - {details}")
        else:
            logger.info(f"Security Event: {event_type} - {details}")


# 전역 보안 검증기 인스턴스
security_validator = SecurityValidator()
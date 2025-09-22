import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json


class JSONFormatter(logging.Formatter):
    """JSON 형태로 로그를 포맷팅하는 클래스"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # 예외 정보가 있으면 추가
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 추가 필드가 있으면 포함
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO", format_type: str = "json") -> None:
    """로깅 설정 초기화"""

    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 특정 로거 설정
    setup_specific_loggers(log_level)


def setup_specific_loggers(level: int) -> None:
    """특정 로거들 설정"""

    # uvicorn 로거 설정
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)

    # fastapi 로거 설정
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(level)

    # httpx 로거 설정 (외부 API 호출)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)  # httpx는 WARNING 이상만

    # 애플리케이션 로거 설정
    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)


class LoggerMixin:
    """로거 믹스인 클래스"""

    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)

    def log_api_call(self, method: str, url: str, response_time: float, status_code: int) -> None:
        """API 호출 로그"""
        extra_fields = {
            "api_method": method,
            "api_url": url,
            "response_time_ms": response_time * 1000,
            "status_code": status_code
        }

        # LogRecord에 extra_fields 추가
        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"API call: {method} {url}",
            args=(),
            exc_info=None
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)

    def log_error(self, message: str, error: Exception, context: Dict[str, Any] = None) -> None:
        """에러 로그"""
        extra_fields = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }

        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=(type(error), error, error.__traceback__)
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)

    def log_user_action(self, username: str, action: str, details: Dict[str, Any] = None) -> None:
        """사용자 액션 로그"""
        extra_fields = {
            "username": username,
            "action": action,
            "details": details or {}
        }

        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"User action: {username} - {action}",
            args=(),
            exc_info=None
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)

    def log_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None) -> None:
        """성능 로그"""
        extra_fields = {
            "operation": operation,
            "duration_ms": duration * 1000,
            "metadata": metadata or {}
        }

        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Performance: {operation} took {duration*1000:.2f}ms",
            args=(),
            exc_info=None
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)


# 글로벌 로거 인스턴스들
api_logger = get_logger("api")
service_logger = get_logger("service")
client_logger = get_logger("client")
cache_logger = get_logger("cache")


def log_startup_info() -> None:
    """서비스 시작 정보 로그"""
    app_logger = get_logger("app")
    app_logger.info("CAU Code Backend Service starting up")


def log_shutdown_info() -> None:
    """서비스 종료 정보 로그"""
    app_logger = get_logger("app")
    app_logger.info("CAU Code Backend Service shutting down")
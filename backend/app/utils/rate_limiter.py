import time
from typing import Dict, Optional
from collections import defaultdict, deque
import asyncio
from functools import wraps
from fastapi import HTTPException, status, Request
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """메모리 기반 Rate Limiter"""

    def __init__(self):
        # key: (client_id, endpoint) -> deque of timestamps
        self._requests: Dict[str, deque] = defaultdict(deque)
        # cleanup task를 위한 백그라운드 태스크
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """만료된 요청 기록 정리를 위한 백그라운드 태스크 시작"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_requests())

    async def _cleanup_expired_requests(self):
        """만료된 요청 기록 정리 (5분마다 실행)"""
        while True:
            try:
                await asyncio.sleep(300)  # 5분
                current_time = time.time()
                keys_to_remove = []

                for key, requests in self._requests.items():
                    # 1시간 이전 요청들 제거
                    while requests and current_time - requests[0] > 3600:
                        requests.popleft()

                    # 빈 deque 제거
                    if not requests:
                        keys_to_remove.append(key)

                for key in keys_to_remove:
                    del self._requests[key]

                logger.debug(f"Rate limiter cleanup: {len(keys_to_remove)} empty entries removed")

            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {str(e)}")
                await asyncio.sleep(60)  # 에러 시 1분 후 재시도

    def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Rate limit 확인

        Args:
            client_id: 클라이언트 식별자 (IP 또는 user_id)
            endpoint: API 엔드포인트
            max_requests: 허용 최대 요청 수
            window_seconds: 시간 윈도우 (초)

        Returns:
            True if allowed, False if rate limited
        """
        current_time = time.time()
        key = f"{client_id}:{endpoint}"

        requests = self._requests[key]

        # 시간 윈도우 밖의 요청들 제거
        while requests and current_time - requests[0] > window_seconds:
            requests.popleft()

        # 현재 요청 수 확인
        if len(requests) >= max_requests:
            return False

        # 현재 요청 기록
        requests.append(current_time)
        return True

    def get_remaining_requests(
        self,
        client_id: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int
    ) -> int:
        """남은 요청 수 조회"""
        current_time = time.time()
        key = f"{client_id}:{endpoint}"

        requests = self._requests[key]

        # 시간 윈도우 밖의 요청들 제거
        while requests and current_time - requests[0] > window_seconds:
            requests.popleft()

        return max(0, max_requests - len(requests))

    def get_reset_time(
        self,
        client_id: str,
        endpoint: str,
        window_seconds: int
    ) -> Optional[float]:
        """Rate limit 리셋 시간 조회"""
        key = f"{client_id}:{endpoint}"
        requests = self._requests[key]

        if not requests:
            return None

        return requests[0] + window_seconds


# 전역 rate limiter 인스턴스
rate_limiter = RateLimiter()


def rate_limit(
    max_requests: int,
    window_seconds: int,
    per_user: bool = False,
    key_func: Optional[callable] = None
):
    """
    Rate limiting decorator

    Args:
        max_requests: 허용 최대 요청 수
        window_seconds: 시간 윈도우 (초)
        per_user: True면 사용자별, False면 IP별 제한
        key_func: 커스텀 키 생성 함수
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # FastAPI의 Request 객체 찾기
            request = None
            current_user = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                # kwargs에서 찾기
                request = kwargs.get('request')

            # current_user 찾기 (per_user가 True인 경우)
            if per_user:
                current_user = kwargs.get('current_user')

            # 클라이언트 식별자 결정
            if key_func:
                client_id = key_func(request, current_user)
            elif per_user and current_user:
                client_id = f"user:{current_user.user_id}"
            else:
                # IP 기반
                client_ip = "unknown"
                if request:
                    # X-Forwarded-For 헤더 확인
                    forwarded_for = request.headers.get("X-Forwarded-For")
                    if forwarded_for:
                        client_ip = forwarded_for.split(",")[0].strip()
                    elif request.client:
                        client_ip = request.client.host
                client_id = f"ip:{client_ip}"

            endpoint = func.__name__

            # Rate limit 확인
            if not rate_limiter.check_rate_limit(
                client_id=client_id,
                endpoint=endpoint,
                max_requests=max_requests,
                window_seconds=window_seconds
            ):
                # Rate limit 정보 계산
                remaining = rate_limiter.get_remaining_requests(
                    client_id, endpoint, max_requests, window_seconds
                )
                reset_time = rate_limiter.get_reset_time(
                    client_id, endpoint, window_seconds
                )

                logger.warning(f"Rate limit exceeded: {client_id} -> {endpoint}")

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "max_requests": max_requests,
                        "window_seconds": window_seconds,
                        "remaining": remaining,
                        "reset_at": reset_time
                    }
                )

            # 요청 실행
            return await func(*args, **kwargs)

        return wrapper
    return decorator


# 사전 정의된 rate limiting 데코레이터들
def verification_rate_limit(func):
    """프로필 인증 요청 제한: 사용자당 시간당 3회"""
    return rate_limit(max_requests=3, window_seconds=3600, per_user=True)(func)


def auth_rate_limit(func):
    """인증 관련 제한: IP당 분당 10회"""
    return rate_limit(max_requests=10, window_seconds=60, per_user=False)(func)


def api_rate_limit(func):
    """일반 API 제한: IP당 분당 60회"""
    return rate_limit(max_requests=60, window_seconds=60, per_user=False)(func)
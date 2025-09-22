from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import json
import hashlib


class InMemoryCache:
    """간단한 인메모리 캐시 구현"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """캐시 항목이 만료되었는지 확인"""
        if entry.get("expires_at") is None:
            return False
        return datetime.now() > entry["expires_at"]

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값을 가져옴"""
        if key not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[key]
        if self._is_expired(entry):
            del self._cache[key]
            self._stats["misses"] += 1
            return None

        self._stats["hits"] += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """캐시에 값을 저장"""
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None

        self._cache[key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "ttl_seconds": ttl_seconds
        }
        self._stats["sets"] += 1

    def delete(self, key: str) -> bool:
        """캐시에서 키를 삭제"""
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
            return True
        return False

    def clear(self) -> None:
        """모든 캐시 항목 삭제"""
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self._cache),
            "memory_usage_mb": len(json.dumps(self._cache, default=str)) / (1024 * 1024)
        }

    def cleanup_expired(self) -> int:
        """만료된 캐시 항목들을 정리"""
        expired_keys = []
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


# 전역 캐시 인스턴스
cache = InMemoryCache()


def cache_get(key: str) -> Optional[Any]:
    """전역 캐시에서 값 가져오기"""
    return cache.get(key)


def cache_set(key: str, value: Any, expire: int = 300) -> None:
    """전역 캐시에 값 저장하기"""
    cache.set(key, value, expire)


def cache_key_for_user(username: str, operation: str) -> str:
    """사용자 관련 캐시 키 생성"""
    return f"user:{username}:{operation}"


def cache_key_for_problem(problem_id: int, operation: str) -> str:
    """문제 관련 캐시 키 생성"""
    return f"problem:{problem_id}:{operation}"


def cache_key_for_analysis(code_hash: str, problem_id: int) -> str:
    """코드 분석 관련 캐시 키 생성"""
    return f"analysis:{problem_id}:{code_hash}"


def generate_code_hash(code: str) -> str:
    """코드 해시 생성"""
    return hashlib.md5(code.encode('utf-8')).hexdigest()


def cache_key_for_recommendations(username: str, mode: str, filters: Dict[str, Any]) -> str:
    """문제 추천 관련 캐시 키 생성"""
    filter_hash = hashlib.md5(json.dumps(filters, sort_keys=True).encode()).hexdigest()
    return f"recommendations:{username}:{mode}:{filter_hash}"


class CacheManager:
    """캐시 관리자"""

    @staticmethod
    def get_user_info(username: str) -> Optional[Dict[str, Any]]:
        """사용자 정보 캐시에서 가져오기"""
        key = cache_key_for_user(username, "info")
        return cache.get(key)

    @staticmethod
    def set_user_info(username: str, user_info: Dict[str, Any], ttl: int = 600) -> None:
        """사용자 정보 캐시에 저장"""
        key = cache_key_for_user(username, "info")
        cache.set(key, user_info, ttl)

    @staticmethod
    def get_problem_info(problem_id: int) -> Optional[Dict[str, Any]]:
        """문제 정보 캐시에서 가져오기"""
        key = cache_key_for_problem(problem_id, "info")
        return cache.get(key)

    @staticmethod
    def set_problem_info(problem_id: int, problem_info: Dict[str, Any], ttl: int = 3600) -> None:
        """문제 정보 캐시에 저장"""
        key = cache_key_for_problem(problem_id, "info")
        cache.set(key, problem_info, ttl)

    @staticmethod
    def get_code_analysis(code: str, problem_id: int) -> Optional[Dict[str, Any]]:
        """코드 분석 결과 캐시에서 가져오기"""
        code_hash = generate_code_hash(code)
        key = cache_key_for_analysis(code_hash, problem_id)
        return cache.get(key)

    @staticmethod
    def set_code_analysis(code: str, problem_id: int, analysis: Dict[str, Any], ttl: int = 1800) -> None:
        """코드 분석 결과 캐시에 저장"""
        code_hash = generate_code_hash(code)
        key = cache_key_for_analysis(code_hash, problem_id)
        cache.set(key, analysis, ttl)

    @staticmethod
    def get_recommendations(username: str, mode: str, filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """문제 추천 결과 캐시에서 가져오기"""
        key = cache_key_for_recommendations(username, mode, filters)
        return cache.get(key)

    @staticmethod
    def set_recommendations(username: str, mode: str, filters: Dict[str, Any], recommendations: List[Dict[str, Any]], ttl: int = 900) -> None:
        """문제 추천 결과 캐시에 저장"""
        key = cache_key_for_recommendations(username, mode, filters)
        cache.set(key, recommendations, ttl)

    @staticmethod
    def invalidate_user_cache(username: str) -> None:
        """사용자 관련 모든 캐시 무효화"""
        # 실제로는 패턴 매칭으로 해당하는 모든 키를 찾아 삭제해야 함
        # 여기서는 주요 캐시만 삭제
        cache.delete(cache_key_for_user(username, "info"))
        cache.delete(cache_key_for_user(username, "problems"))
        cache.delete(cache_key_for_user(username, "stats"))

    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """캐시 통계 반환"""
        return cache.get_stats()

    @staticmethod
    def cleanup_cache() -> int:
        """만료된 캐시 정리"""
        return cache.cleanup_expired()
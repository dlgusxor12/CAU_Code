"""
Background task queue system for CAU Code.
Handles asynchronous task processing with retry logic and error handling.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
import uuid
import traceback

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """작업 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BackgroundTask:
    """백그라운드 작업 정의"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    func: Callable = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 300  # seconds (5 minutes)

    # 상태 관리
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    last_error: Optional[str] = None
    result: Any = None


class BackgroundTaskQueue:
    """
    백그라운드 작업 큐 관리 시스템
    - 우선순위 기반 작업 처리
    - 재시도 로직 및 exponential backoff
    - 작업 상태 추적 및 모니터링
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, BackgroundTask] = {}
        self.pending_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.workers: List[asyncio.Task] = []
        self.is_running = False

        # 통계
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retry_tasks": 0
        }

    async def start(self):
        """작업 큐 시작"""
        if self.is_running:
            logger.warning("백그라운드 작업 큐가 이미 실행 중입니다")
            return

        self.is_running = True

        # 워커 태스크들 시작
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]

        logger.info(f"백그라운드 작업 큐 시작됨 - {self.max_workers}개 워커")

    async def stop(self):
        """작업 큐 중지"""
        if not self.is_running:
            return

        self.is_running = False

        # 실행 중인 작업들 취소
        for task_id, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"작업 취소: {task_id}")

        # 워커들 종료
        for worker in self.workers:
            worker.cancel()

        # 워커들이 종료될 때까지 대기
        await asyncio.gather(*self.workers, return_exceptions=True)

        logger.info("백그라운드 작업 큐 중지됨")

    async def add_task(
        self,
        func: Callable,
        *args,
        name: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: int = 60,
        timeout: int = 300,
        **kwargs
    ) -> str:
        """
        작업을 큐에 추가

        Args:
            func: 실행할 함수
            *args: 함수 인자
            name: 작업 이름
            priority: 우선순위
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
            timeout: 타임아웃 (초)
            **kwargs: 함수 키워드 인자

        Returns:
            작업 ID
        """
        task = BackgroundTask(
            name=name or f"{func.__name__}",
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout
        )

        self.tasks[task.id] = task
        self.stats["total_tasks"] += 1

        # 우선순위 큐에 추가 (낮은 숫자가 높은 우선순위)
        priority_value = -priority.value  # 음수로 변환하여 높은 우선순위가 먼저 처리되도록
        await self.pending_queue.put((priority_value, task.created_at, task.id))

        logger.info(f"작업 큐에 추가: {task.name} (ID: {task.id}, 우선순위: {priority.name})")
        return task.id

    async def _worker(self, worker_name: str):
        """워커 태스크"""
        logger.info(f"{worker_name} 시작됨")

        while self.is_running:
            try:
                # 작업 가져오기 (타임아웃 설정)
                try:
                    priority, created_at, task_id = await asyncio.wait_for(
                        self.pending_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                task = self.tasks.get(task_id)
                if not task:
                    logger.warning(f"작업을 찾을 수 없음: {task_id}")
                    continue

                # 작업 실행
                await self._execute_task(worker_name, task)

            except asyncio.CancelledError:
                logger.info(f"{worker_name} 취소됨")
                break
            except Exception as e:
                logger.error(f"{worker_name} 예외 발생: {str(e)}")

        logger.info(f"{worker_name} 종료됨")

    async def _execute_task(self, worker_name: str, task: BackgroundTask):
        """작업 실행"""
        try:
            logger.info(f"{worker_name}에서 작업 실행 시작: {task.name} (ID: {task.id})")

            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)

            # 타임아웃과 함께 작업 실행
            task_coroutine = asyncio.create_task(task.func(*task.args, **task.kwargs))
            self.running_tasks[task.id] = task_coroutine

            try:
                task.result = await asyncio.wait_for(task_coroutine, timeout=task.timeout)

                # 성공 처리
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc)
                self.stats["completed_tasks"] += 1

                logger.info(f"작업 완료: {task.name} (ID: {task.id})")

            except asyncio.TimeoutError:
                task_coroutine.cancel()
                raise Exception(f"작업 타임아웃 ({task.timeout}초)")

            finally:
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]

        except Exception as e:
            # 실패 처리
            error_msg = str(e)
            task.last_error = error_msg
            task.retry_count += 1

            logger.error(f"작업 실패: {task.name} (ID: {task.id}, 시도: {task.retry_count}/{task.max_retries}) - {error_msg}")

            if task.retry_count < task.max_retries:
                # 재시도 스케줄링
                await self._schedule_retry(task)
            else:
                # 최종 실패
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)
                self.stats["failed_tasks"] += 1

                logger.error(f"작업 최종 실패: {task.name} (ID: {task.id})")

    async def _schedule_retry(self, task: BackgroundTask):
        """재시도 스케줄링 (exponential backoff)"""
        task.status = TaskStatus.RETRY
        self.stats["retry_tasks"] += 1

        # Exponential backoff: 기본 지연시간 * (2 ^ (재시도 횟수 - 1))
        delay = task.retry_delay * (2 ** (task.retry_count - 1))
        delay = min(delay, 3600)  # 최대 1시간

        logger.info(f"작업 재시도 예약: {task.name} (ID: {task.id}, {delay}초 후)")

        # 지연 후 큐에 다시 추가
        async def retry_task():
            await asyncio.sleep(delay)
            if self.is_running and task.status == TaskStatus.RETRY:
                task.status = TaskStatus.PENDING
                priority_value = -task.priority.value
                await self.pending_queue.put((priority_value, datetime.now(timezone.utc), task.id))

        asyncio.create_task(retry_task())

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """작업 상태 조회"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.name,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "last_error": task.last_error,
            "result": str(task.result) if task.result else None
        }

    def get_queue_stats(self) -> Dict:
        """큐 통계 조회"""
        return {
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "retry_tasks": self.stats["retry_tasks"],
            "pending_tasks": self.pending_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "workers": len(self.workers),
            "is_running": self.is_running
        }

    def get_running_tasks(self) -> List[Dict]:
        """실행 중인 작업 목록"""
        running = []
        for task_id in self.running_tasks:
            task = self.tasks.get(task_id)
            if task:
                running.append({
                    "id": task.id,
                    "name": task.name,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "priority": task.priority.name
                })
        return running

    async def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task_id in self.running_tasks:
            # 실행 중인 작업 취소
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc)

        logger.info(f"작업 취소됨: {task.name} (ID: {task_id})")
        return True

    def cleanup_old_tasks(self, days: int = 7):
        """오래된 작업 기록 정리"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
                and task.completed_at
                and task.completed_at < cutoff_date):
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]

        if to_remove:
            logger.info(f"{len(to_remove)}개 오래된 작업 기록 정리 완료")


# 전역 백그라운드 작업 큐 인스턴스
background_task_queue = BackgroundTaskQueue()
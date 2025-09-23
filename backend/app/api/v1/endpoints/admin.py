"""
Admin API endpoints for CAU Code backend monitoring.
Provides system monitoring and background task management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.auth import User
from app.core.background_tasks import background_task_queue
from app.core.scheduler import background_scheduler
from app.services.profile_monitoring_service import profile_monitoring_service
from app.services.enhanced_profile_service import enhanced_profile_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    관리자 권한 확인
    TODO: 실제 관리자 권한 시스템 구현 시 업데이트 필요
    """
    # 현재는 모든 인증된 사용자에게 관리자 권한 부여 (개발용)
    # 프로덕션에서는 실제 권한 확인 로직 구현 필요
    if not current_user.profile_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    return current_user


@router.get("/system/status")
async def get_system_status(
    admin_user: User = Depends(get_admin_user)
):
    """시스템 전체 상태 조회"""
    try:
        return {
            "system_status": "running",
            "background_services": {
                "task_queue": {
                    "running": background_task_queue.is_running,
                    "stats": background_task_queue.get_queue_stats(),
                    "running_tasks": background_task_queue.get_running_tasks()
                },
                "scheduler": {
                    "running": background_scheduler.scheduler.running if background_scheduler.scheduler else False,
                    "jobs": background_scheduler.get_jobs()
                }
            }
        }

    except Exception as e:
        logger.error(f"시스템 상태 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="시스템 상태 조회에 실패했습니다."
        )


@router.get("/tasks/queue/stats")
async def get_task_queue_stats(
    admin_user: User = Depends(get_admin_user)
):
    """백그라운드 작업 큐 통계"""
    try:
        return background_task_queue.get_queue_stats()

    except Exception as e:
        logger.error(f"작업 큐 통계 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 큐 통계 조회에 실패했습니다."
        )


@router.get("/tasks/running")
async def get_running_tasks(
    admin_user: User = Depends(get_admin_user)
):
    """실행 중인 작업 목록"""
    try:
        return {
            "running_tasks": background_task_queue.get_running_tasks(),
            "count": len(background_task_queue.get_running_tasks())
        }

    except Exception as e:
        logger.error(f"실행 중인 작업 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="실행 중인 작업 조회에 실패했습니다."
        )


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """특정 작업 상태 조회"""
    try:
        task_status = background_task_queue.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="작업을 찾을 수 없습니다."
            )

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작업 상태 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 상태 조회에 실패했습니다."
        )


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """작업 취소"""
    try:
        success = await background_task_queue.cancel_task(task_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="작업을 찾을 수 없거나 취소할 수 없습니다."
            )

        return {"message": "작업이 취소되었습니다.", "task_id": task_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작업 취소 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 취소에 실패했습니다."
        )


@router.get("/scheduler/jobs")
async def get_scheduler_jobs(
    admin_user: User = Depends(get_admin_user)
):
    """스케줄러 작업 목록"""
    try:
        return {
            "jobs": background_scheduler.get_jobs(),
            "scheduler_running": background_scheduler.scheduler.running if background_scheduler.scheduler else False
        }

    except Exception as e:
        logger.error(f"스케줄러 작업 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="스케줄러 작업 조회에 실패했습니다."
        )


@router.post("/scheduler/jobs/{job_id}/pause")
async def pause_scheduler_job(
    job_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """스케줄러 작업 일시정지"""
    try:
        background_scheduler.pause_job(job_id)
        return {"message": f"작업 '{job_id}'가 일시정지되었습니다."}

    except Exception as e:
        logger.error(f"작업 일시정지 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 일시정지에 실패했습니다."
        )


@router.post("/scheduler/jobs/{job_id}/resume")
async def resume_scheduler_job(
    job_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """스케줄러 작업 재시작"""
    try:
        background_scheduler.resume_job(job_id)
        return {"message": f"작업 '{job_id}'가 재시작되었습니다."}

    except Exception as e:
        logger.error(f"작업 재시작 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 재시작에 실패했습니다."
        )


@router.get("/monitoring/verification")
async def get_verification_monitoring_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """프로필 인증 모니터링 통계"""
    try:
        stats = await profile_monitoring_service.get_monitoring_stats(db)
        return stats

    except Exception as e:
        logger.error(f"인증 모니터링 통계 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 모니터링 통계 조회에 실패했습니다."
        )


@router.post("/monitoring/verification/check")
async def trigger_verification_check(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """수동 인증 확인 트리거"""
    try:
        stats = await profile_monitoring_service.check_all_pending_verifications(db)
        return {
            "message": "인증 확인이 완료되었습니다.",
            "stats": stats
        }

    except Exception as e:
        logger.error(f"수동 인증 확인 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 확인에 실패했습니다."
        )


@router.post("/profiles/sync-all")
async def trigger_profile_sync_all(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """모든 사용자 프로필 동기화 트리거"""
    try:
        result = await enhanced_profile_service.sync_all_verified_users(db)
        return {
            "message": "프로필 동기화가 시작되었습니다.",
            "result": result
        }

    except Exception as e:
        logger.error(f"프로필 동기화 트리거 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 동기화 시작에 실패했습니다."
        )


@router.get("/profiles/cache/{user_id}")
async def get_user_profile_cache(
    user_id: int,
    include_raw_data: bool = False,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """사용자 프로필 캐시 조회"""
    try:
        cache = await enhanced_profile_service.get_user_profile_cache(
            db, user_id, include_raw_data
        )

        if not cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 프로필 캐시를 찾을 수 없습니다."
            )

        return cache

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로필 캐시 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 캐시 조회에 실패했습니다."
        )


@router.post("/cleanup/tasks")
async def cleanup_old_tasks(
    days: int = 7,
    admin_user: User = Depends(get_admin_user)
):
    """오래된 작업 기록 정리"""
    try:
        background_task_queue.cleanup_old_tasks(days)
        return {"message": f"{days}일 이전 작업 기록이 정리되었습니다."}

    except Exception as e:
        logger.error(f"작업 기록 정리 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 기록 정리에 실패했습니다."
        )


@router.post("/cleanup/profile-cache")
async def cleanup_profile_cache(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """오래된 프로필 캐시 정리"""
    try:
        cleaned_count = await enhanced_profile_service.cleanup_old_profile_cache(db, days)
        return {
            "message": f"{days}일 이전 프로필 캐시 {cleaned_count}개가 정리되었습니다.",
            "cleaned_count": cleaned_count
        }

    except Exception as e:
        logger.error(f"프로필 캐시 정리 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 캐시 정리에 실패했습니다."
        )
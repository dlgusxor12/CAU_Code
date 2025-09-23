from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from app.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.app_name,
    description="Backend service for CAU Code platform with solved.ac integration and AI-powered features",
    version="1.0.0",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Phase 2.2: Background Services Integration
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 백그라운드 서비스 초기화"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("CAU Code 백엔드 서비스 시작 중...")

        # 백그라운드 작업 큐 시작
        from app.core.background_tasks import background_task_queue
        await background_task_queue.start()
        logger.info("백그라운드 작업 큐 시작됨")

        # 스케줄러 시작
        from app.core.scheduler import background_scheduler
        background_scheduler.start()
        logger.info("백그라운드 스케줄러 시작됨")

        logger.info("CAU Code 백엔드 서비스 시작 완료")

    except Exception as e:
        logger.error(f"백엔드 서비스 시작 중 오류: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 백그라운드 서비스 정리"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("CAU Code 백엔드 서비스 종료 중...")

        # 스케줄러 종료
        from app.core.scheduler import background_scheduler
        background_scheduler.shutdown()
        logger.info("백그라운드 스케줄러 종료됨")

        # 백그라운드 작업 큐 종료
        from app.core.background_tasks import background_task_queue
        await background_task_queue.stop()
        logger.info("백그라운드 작업 큐 종료됨")

        logger.info("CAU Code 백엔드 서비스 종료 완료")

    except Exception as e:
        logger.error(f"백엔드 서비스 종료 중 오류: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "CAU Code Backend Service is running",
        "version": "1.0.0",
        "features": [
            "solved.ac integration",
            "AI-powered analysis",
            "Problem recommendations",
            "Real-time profile monitoring",
            "Background task processing"
        ]
    }

@app.get("/health")
async def health_check():
    """서비스 상태 체크"""
    from app.core.background_tasks import background_task_queue
    from app.core.scheduler import background_scheduler

    return {
        "status": "healthy",
        "service": settings.app_name,
        "background_services": {
            "task_queue_running": background_task_queue.is_running,
            "scheduler_running": background_scheduler.scheduler.running if background_scheduler.scheduler else False,
            "task_queue_stats": background_task_queue.get_queue_stats()
        }
    }


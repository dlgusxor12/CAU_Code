"""
Background task scheduler for CAU Code authentication system.
Handles periodic verification monitoring and cleanup tasks.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore

from app.database import AsyncSessionLocal
from app.services.profile_verification_service import profile_verification_service
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """
    백그라운드 작업 스케줄러 관리 클래스
    - 인증 요청 모니터링
    - 만료된 세션/인증 정리
    - 프로필 동기화 작업
    """

    def __init__(self):
        # APScheduler 설정
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 30
        }

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )

        self._setup_jobs()

    def _setup_jobs(self):
        """스케줄러 작업들 설정"""

        # 1. 인증 요청 모니터링 (5분마다)
        self.scheduler.add_job(
            func=self._monitor_pending_verifications,
            trigger=IntervalTrigger(minutes=5),
            id='monitor_verifications',
            name='Monitor Pending Verifications',
            replace_existing=True
        )

        # 2. 만료된 세션 정리 (1시간마다)
        self.scheduler.add_job(
            func=self._cleanup_expired_sessions,
            trigger=IntervalTrigger(hours=1),
            id='cleanup_sessions',
            name='Cleanup Expired Sessions',
            replace_existing=True
        )

        # 3. 만료된 인증 요청 정리 (30분마다)
        self.scheduler.add_job(
            func=self._cleanup_expired_verifications,
            trigger=IntervalTrigger(minutes=30),
            id='cleanup_verifications',
            name='Cleanup Expired Verifications',
            replace_existing=True
        )

        # 4. 프로필 동기화 (6시간마다)
        self.scheduler.add_job(
            func=self._sync_user_profiles,
            trigger=IntervalTrigger(hours=6),
            id='sync_user_profiles',
            name='Sync User Profiles',
            replace_existing=True
        )

        # 5. 시스템 상태 체크 (매일 자정)
        self.scheduler.add_job(
            func=self._daily_system_check,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_system_check',
            name='Daily System Health Check',
            replace_existing=True
        )

        logger.info("백그라운드 스케줄러 작업 설정 완료")

    async def _monitor_pending_verifications(self):
        """
        진행 중인 인증 요청들을 모니터링하여 자동 처리
        """
        try:
            logger.info("인증 요청 모니터링 시작")

            async with AsyncSessionLocal() as db:
                # profile_monitoring_service import를 여기서 수행 (순환 import 방지)
                from app.services.profile_monitoring_service import profile_monitoring_service

                # 모든 진행 중인 인증 요청 자동 체크
                stats = await profile_monitoring_service.check_all_pending_verifications(db)

                logger.info(f"인증 모니터링 완료 - "
                           f"총 {stats['total_checked']}개 체크, "
                           f"인증 완료: {stats['verified']}개")

                # 추가로 만료된 인증 요청 정리
                cleaned_count = await profile_verification_service.cleanup_expired_verifications(db)

                if cleaned_count > 0:
                    logger.info(f"만료된 인증 요청 {cleaned_count}개 추가 정리")

        except Exception as e:
            logger.error(f"인증 요청 모니터링 중 오류: {str(e)}")

    async def _cleanup_expired_sessions(self):
        """만료된 사용자 세션 정리"""
        try:
            logger.info("만료된 세션 정리 시작")

            async with AsyncSessionLocal() as db:
                cleaned_count = await auth_service.cleanup_expired_sessions(db)

                if cleaned_count > 0:
                    logger.info(f"만료된 세션 {cleaned_count}개 정리 완료")
                else:
                    logger.debug("정리할 만료된 세션 없음")

        except Exception as e:
            logger.error(f"세션 정리 중 오류: {str(e)}")

    async def _cleanup_expired_verifications(self):
        """만료된 인증 요청 정리"""
        try:
            logger.info("만료된 인증 요청 정리 시작")

            async with AsyncSessionLocal() as db:
                cleaned_count = await profile_verification_service.cleanup_expired_verifications(db)

                if cleaned_count > 0:
                    logger.info(f"만료된 인증 요청 {cleaned_count}개 정리 완료")
                else:
                    logger.debug("정리할 만료된 인증 요청 없음")

        except Exception as e:
            logger.error(f"인증 요청 정리 중 오류: {str(e)}")

    async def _sync_user_profiles(self):
        """사용자 프로필 동기화 (6시간마다 실행)"""
        try:
            logger.info("사용자 프로필 동기화 시작")

            async with AsyncSessionLocal() as db:
                # enhanced_profile_service import를 여기서 수행 (순환 import 방지)
                from app.services.enhanced_profile_service import enhanced_profile_service

                # 모든 인증된 사용자의 프로필 동기화
                result = await enhanced_profile_service.sync_all_verified_users(db)

                logger.info(f"프로필 동기화 완료 - "
                           f"{result['synced_users']}명 대상, "
                           f"{result['scheduled_tasks']}개 작업 예약")

        except Exception as e:
            logger.error(f"사용자 프로필 동기화 중 오류: {str(e)}")

    async def _daily_system_check(self):
        """일일 시스템 상태 체크"""
        try:
            logger.info("일일 시스템 상태 체크 시작")

            async with AsyncSessionLocal() as db:
                # 세션 정리
                session_count = await auth_service.cleanup_expired_sessions(db)

                # 인증 요청 정리
                verification_count = await profile_verification_service.cleanup_expired_verifications(db)

                logger.info(f"일일 정리 완료 - 세션: {session_count}개, 인증 요청: {verification_count}개")

                # TODO: 추가 시스템 상태 체크 (DB 연결, API 상태 등)

        except Exception as e:
            logger.error(f"일일 시스템 체크 중 오류: {str(e)}")

    def start(self):
        """스케줄러 시작"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("백그라운드 스케줄러 시작됨")
            else:
                logger.warning("백그라운드 스케줄러가 이미 실행 중입니다")
        except Exception as e:
            logger.error(f"스케줄러 시작 실패: {str(e)}")
            raise

    def shutdown(self):
        """스케줄러 종료"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("백그라운드 스케줄러 종료됨")
        except Exception as e:
            logger.error(f"스케줄러 종료 중 오류: {str(e)}")

    def get_jobs(self):
        """현재 등록된 작업 목록 조회"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs

    def pause_job(self, job_id: str):
        """특정 작업 일시정지"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"작업 '{job_id}' 일시정지됨")
        except Exception as e:
            logger.error(f"작업 일시정지 실패: {str(e)}")
            raise

    def resume_job(self, job_id: str):
        """특정 작업 재시작"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"작업 '{job_id}' 재시작됨")
        except Exception as e:
            logger.error(f"작업 재시작 실패: {str(e)}")
            raise


# 전역 스케줄러 인스턴스
background_scheduler = BackgroundScheduler()
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.services.solvedac_service import SolvedACService
from app.services.gpt_service import GPTService
from app.schemas.user import (
    UserDashboardResponse,
    UserStatsResponse,
    ContributionGraphResponse,
    RecentActivityResponse,
    WeeklyStatsResponse,
    TodaysProblemsResponse,
    ReviewProblemsResponse
)
from app.schemas.common import APIResponse
from app.utils.logging import LoggerMixin
from app.core.exceptions import UserNotFoundError

router = APIRouter()


class UserEndpoints(LoggerMixin):
    def __init__(self):
        self.solvedac_service = SolvedACService()
        self.gpt_service = GPTService()


user_endpoints = UserEndpoints()


@router.get("/dashboard/{username}", response_model=APIResponse[UserDashboardResponse])
async def get_user_dashboard(username: str):
    """사용자 대시보드 정보 조회"""
    try:
        user_endpoints.log_user_action(username, "dashboard_access")

        # 병렬로 데이터 수집
        user_info = await user_endpoints.solvedac_service.get_user_info(username)
        todays_problems = await user_endpoints.solvedac_service.get_todays_problems(username, count=2)
        review_problems = await user_endpoints.solvedac_service.get_review_problems(username, count=2)
        contribution_graph = await user_endpoints.solvedac_service.get_contribution_graph(username, year=2025)
        recent_activities = await user_endpoints.solvedac_service.get_recent_activities(username, limit=5)
        weekly_stats = await user_endpoints.solvedac_service.get_weekly_stats(username)

        dashboard_data = UserDashboardResponse(
            user_info=user_info,
            todays_problems=todays_problems,
            review_problems=review_problems,
            contribution_graph=contribution_graph,
            recent_activities=recent_activities,
            weekly_stats=weekly_stats
        )

        return APIResponse(
            status="success",
            message="대시보드 정보를 성공적으로 조회했습니다",
            data=dashboard_data
        )

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"사용자 '{username}'을 찾을 수 없습니다")
    except Exception as e:
        user_endpoints.log_error(f"Dashboard error for {username}", e)
        raise HTTPException(status_code=500, detail="대시보드 정보 조회 중 오류가 발생했습니다")


@router.get("/stats/{username}", response_model=APIResponse[UserStatsResponse])
async def get_user_stats(username: str):
    """사용자 통계 정보 조회"""
    try:
        user_info = await user_endpoints.solvedac_service.get_user_info(username)

        stats_data = UserStatsResponse(
            current_tier=user_info.get("tier", 0),
            current_rating=user_info.get("rating", 0),
            solved_problems=user_info.get("solved_count", 0),
            rank=user_info.get("rank", 0),
            tier_name=user_info.get("tier_name", "Unrated"),
            class_level=user_info.get("class_level", 0)
        )

        return APIResponse(
            status="success",
            message="사용자 통계를 성공적으로 조회했습니다",
            data=stats_data
        )

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"사용자 '{username}'을 찾을 수 없습니다")
    except Exception as e:
        user_endpoints.log_error(f"Stats error for {username}", e)
        raise HTTPException(status_code=500, detail="사용자 통계 조회 중 오류가 발생했습니다")


@router.get("/contribution/{username}", response_model=APIResponse[ContributionGraphResponse])
async def get_contribution_graph(username: str, year: int = 2025):
    """기여도 그래프 데이터 조회"""
    try:
        contribution_data = await user_endpoints.solvedac_service.get_contribution_graph(username, year)

        # 통계 계산
        total_solved = sum(day["solved_count"] for day in contribution_data)
        longest_streak = 0
        current_streak = 0

        for day in contribution_data:
            if day["solved_count"] > 0:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0

        graph_data = ContributionGraphResponse(
            year=year,
            daily_data=contribution_data,
            total_solved_this_year=total_solved,
            longest_streak=longest_streak
        )

        return APIResponse(
            status="success",
            message="기여도 그래프 데이터를 성공적으로 조회했습니다",
            data=graph_data
        )

    except Exception as e:
        user_endpoints.log_error(f"Contribution graph error for {username}", e)
        raise HTTPException(status_code=500, detail="기여도 그래프 조회 중 오류가 발생했습니다")


@router.get("/activities/{username}", response_model=APIResponse[RecentActivityResponse])
async def get_recent_activities(username: str, limit: int = 10):
    """최근 활동 내역 조회"""
    try:
        activities = await user_endpoints.solvedac_service.get_recent_activities(username, limit)

        activity_data = RecentActivityResponse(
            activities=activities,
            total_count=len(activities)
        )

        return APIResponse(
            status="success",
            message="최근 활동 내역을 성공적으로 조회했습니다",
            data=activity_data
        )

    except Exception as e:
        user_endpoints.log_error(f"Activities error for {username}", e)
        raise HTTPException(status_code=500, detail="최근 활동 조회 중 오류가 발생했습니다")


@router.get("/weekly-stats/{username}", response_model=APIResponse[WeeklyStatsResponse])
async def get_weekly_stats(username: str):
    """이번 주 통계 조회"""
    try:
        stats = await user_endpoints.solvedac_service.get_weekly_stats(username)

        weekly_data = WeeklyStatsResponse(
            problems_solved=stats.get("problems_solved", 0),
            new_algorithms=stats.get("new_algorithms", 0),
            average_difficulty=stats.get("average_difficulty", 0.0),
            consistency_score=stats.get("consistency_score", 0.0),
            improvement_rate=stats.get("improvement_rate", 0.0)
        )

        return APIResponse(
            status="success",
            message="이번 주 통계를 성공적으로 조회했습니다",
            data=weekly_data
        )

    except Exception as e:
        user_endpoints.log_error(f"Weekly stats error for {username}", e)
        raise HTTPException(status_code=500, detail="주간 통계 조회 중 오류가 발생했습니다")


@router.get("/todays-problems/{username}", response_model=APIResponse[TodaysProblemsResponse])
async def get_todays_problems(username: str, count: int = 2):
    """오늘의 문제 추천"""
    try:
        problems = await user_endpoints.solvedac_service.get_todays_problems(username, count)

        # 난이도 분포 계산
        difficulty_distribution = {}
        for problem in problems:
            tier = problem.get("tier_name", "Unknown")
            difficulty_distribution[tier] = difficulty_distribution.get(tier, 0) + 1

        todays_data = TodaysProblemsResponse(
            recommended_problems=problems,
            total_count=len(problems),
            difficulty_distribution=difficulty_distribution
        )

        return APIResponse(
            status="success",
            message="오늘의 문제를 성공적으로 추천했습니다",
            data=todays_data
        )

    except Exception as e:
        user_endpoints.log_error(f"Today's problems error for {username}", e)
        raise HTTPException(status_code=500, detail="오늘의 문제 추천 중 오류가 발생했습니다")


@router.get("/review-problems/{username}", response_model=APIResponse[ReviewProblemsResponse])
async def get_review_problems(username: str, count: int = 2):
    """복습할 문제 추천"""
    try:
        problems = await user_endpoints.solvedac_service.get_review_problems(username, count)

        # 우선순위 점수 계산 (더미)
        priority_scores = [0.8, 0.6, 0.7, 0.9, 0.5][:len(problems)]

        review_data = ReviewProblemsResponse(
            review_problems=problems,
            total_count=len(problems),
            priority_scores=priority_scores
        )

        return APIResponse(
            status="success",
            message="복습할 문제를 성공적으로 추천했습니다",
            data=review_data
        )

    except Exception as e:
        user_endpoints.log_error(f"Review problems error for {username}", e)
        raise HTTPException(status_code=500, detail="복습 문제 추천 중 오류가 발생했습니다")


@router.get("/profile/{username}")
async def get_user_profile(username: str):
    """사용자 프로필 정보 조회"""
    try:
        user_info = await user_endpoints.solvedac_service.get_user_info(username)

        return APIResponse(
            status="success",
            message="사용자 프로필을 성공적으로 조회했습니다",
            data=user_info
        )

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"사용자 '{username}'을 찾을 수 없습니다")
    except Exception as e:
        user_endpoints.log_error(f"Profile error for {username}", e)
        raise HTTPException(status_code=500, detail="사용자 프로필 조회 중 오류가 발생했습니다")
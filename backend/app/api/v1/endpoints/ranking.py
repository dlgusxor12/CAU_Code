from fastapi import APIRouter, HTTPException
from typing import Optional

from app.services.database_service import DatabaseService
from app.services.solvedac_service import SolvedACService
from app.schemas.ranking import (
    GlobalRankingResponse,
    OrganizationRankingResponse,
    MyRankInfo,
    RankingStats
)
from app.schemas.common import APIResponse
from app.utils.logging import LoggerMixin

router = APIRouter()


class RankingEndpoints(LoggerMixin):
    def __init__(self):
        self.db_service = DatabaseService()
        self.solvedac_service = SolvedACService()


ranking_endpoints = RankingEndpoints()


@router.get("/global", response_model=APIResponse[GlobalRankingResponse])
async def get_global_ranking(limit: int = 100):
    """전체 랭킹 조회 (실시간 solved.ac API 데이터 사용 + DB 자동 동기화)"""
    try:
        # DB에서 인증된 사용자 목록과 CAU 해결 문제 수 조회
        db_rankings = await ranking_endpoints.db_service.get_global_ranking(limit)

        # 각 사용자의 실시간 solved.ac 정보 조회 및 병합
        rankings = []
        for rank, db_user in enumerate(db_rankings, start=1):
            try:
                # 실시간 solved.ac API 호출
                solvedac_user = await ranking_endpoints.solvedac_service.get_user_info(db_user["username"])

                # DB 프로필 정보 동기화 (백그라운드로 실행, 에러 무시)
                await ranking_endpoints.db_service.update_user_solvedac_profile(
                    username=db_user["username"],
                    tier=solvedac_user.get("tier_name", "Unrated"),
                    rating=solvedac_user.get("rating", 0),
                    solved_count=solvedac_user.get("solved_count", 0)
                )

                rankings.append({
                    "rank": rank,
                    "username": db_user["username"],
                    "organization": db_user["organization"],
                    "tier": solvedac_user.get("tier_name", "Unrated"),
                    "rating": solvedac_user.get("rating", 0),
                    "total_solved": solvedac_user.get("solved_count", 0),
                    "cau_solved": db_user["cau_solved"]
                })
            except Exception as api_error:
                ranking_endpoints.log_error(f"Failed to fetch real-time data for {db_user['username']}", api_error)
                # API 실패 시 DB 데이터 사용
                rankings.append({
                    "rank": rank,
                    "username": db_user["username"],
                    "organization": db_user["organization"],
                    "tier": db_user.get("tier", "Unrated"),
                    "rating": db_user.get("rating", 0),
                    "total_solved": db_user.get("total_solved", 0),
                    "cau_solved": db_user["cau_solved"]
                })

        response_data = GlobalRankingResponse(
            rankings=rankings,
            total_count=len(rankings)
        )

        return APIResponse(
            status="success",
            message="전체 랭킹을 성공적으로 조회했습니다",
            data=response_data
        )

    except Exception as e:
        ranking_endpoints.log_error("Global ranking error", e)
        raise HTTPException(status_code=500, detail="전체 랭킹 조회 중 오류가 발생했습니다")


@router.get("/organization/{organization}", response_model=APIResponse[OrganizationRankingResponse])
async def get_organization_ranking(organization: str, limit: int = 100):
    """소속별 랭킹 조회 (실시간 solved.ac API 데이터 사용 + DB 자동 동기화)"""
    try:
        # DB에서 소속별 사용자 목록과 CAU 해결 문제 수 조회
        db_rankings = await ranking_endpoints.db_service.get_organization_ranking(organization, limit)

        # 각 사용자의 실시간 solved.ac 정보 조회 및 병합
        rankings = []
        for rank, db_user in enumerate(db_rankings, start=1):
            try:
                # 실시간 solved.ac API 호출
                solvedac_user = await ranking_endpoints.solvedac_service.get_user_info(db_user["username"])

                # DB 프로필 정보 동기화 (백그라운드로 실행, 에러 무시)
                await ranking_endpoints.db_service.update_user_solvedac_profile(
                    username=db_user["username"],
                    tier=solvedac_user.get("tier_name", "Unrated"),
                    rating=solvedac_user.get("rating", 0),
                    solved_count=solvedac_user.get("solved_count", 0)
                )

                rankings.append({
                    "rank": rank,
                    "username": db_user["username"],
                    "organization": db_user["organization"],
                    "tier": solvedac_user.get("tier_name", "Unrated"),
                    "rating": solvedac_user.get("rating", 0),
                    "total_solved": solvedac_user.get("solved_count", 0),
                    "cau_solved": db_user["cau_solved"]
                })
            except Exception as api_error:
                ranking_endpoints.log_error(f"Failed to fetch real-time data for {db_user['username']}", api_error)
                # API 실패 시 DB 데이터 사용
                rankings.append({
                    "rank": rank,
                    "username": db_user["username"],
                    "organization": db_user["organization"],
                    "tier": db_user.get("tier", "Unrated"),
                    "rating": db_user.get("rating", 0),
                    "total_solved": db_user.get("total_solved", 0),
                    "cau_solved": db_user["cau_solved"]
                })

        response_data = OrganizationRankingResponse(
            organization=organization,
            rankings=rankings,
            total_count=len(rankings)
        )

        return APIResponse(
            status="success",
            message=f"{organization} 랭킹을 성공적으로 조회했습니다",
            data=response_data
        )

    except Exception as e:
        ranking_endpoints.log_error(f"Organization ranking error for {organization}", e)
        raise HTTPException(status_code=500, detail="소속 랭킹 조회 중 오류가 발생했습니다")


@router.get("/my-rank/{username}", response_model=APIResponse[MyRankInfo])
async def get_my_rank(username: str):
    """내 랭킹 정보 조회 (실시간 solved.ac API + DB organization)"""
    try:
        # DB에서 organization과 global_rank 조회
        db_rank_info = await ranking_endpoints.db_service.get_my_rank_info(username)

        if not db_rank_info:
            raise HTTPException(status_code=404, detail="사용자 랭킹 정보를 찾을 수 없습니다")

        # solved.ac API에서 실시간 사용자 정보 조회
        try:
            solvedac_user = await ranking_endpoints.solvedac_service.get_user_info(username)

            # 실시간 데이터와 DB 데이터 병합
            rank_info = {
                "username": username,
                "organization": db_rank_info.get("organization", "미분류"),
                "tier": solvedac_user.get("tier_name", "Unrated"),
                "rating": solvedac_user.get("rating", 0),
                "total_solved": solvedac_user.get("solved_count", 0),
                "global_rank": db_rank_info.get("global_rank", 0)
            }
        except Exception as api_error:
            ranking_endpoints.log_error(f"Failed to fetch real-time data for {username}, using DB data", api_error)
            # API 호출 실패 시 DB 데이터 사용
            rank_info = db_rank_info

        return APIResponse(
            status="success",
            message="내 랭킹 정보를 성공적으로 조회했습니다",
            data=MyRankInfo(**rank_info)
        )

    except HTTPException:
        raise
    except Exception as e:
        ranking_endpoints.log_error(f"My rank error for {username}", e)
        raise HTTPException(status_code=500, detail="내 랭킹 조회 중 오류가 발생했습니다")


@router.get("/stats", response_model=APIResponse[RankingStats])
async def get_ranking_stats(organization: Optional[str] = None):
    """랭킹 통계 조회"""
    try:
        stats = await ranking_endpoints.db_service.get_ranking_stats()

        # 소속별 사용자 수 조회
        org_users = 0
        if organization:
            org_users = await ranking_endpoints.db_service.get_organization_user_count(organization)

        response_data = RankingStats(
            total_users=stats["total_users"],
            organization_users=org_users,
            avg_solved_count=stats["avg_solved_count"]
        )

        return APIResponse(
            status="success",
            message="랭킹 통계를 성공적으로 조회했습니다",
            data=response_data
        )

    except Exception as e:
        ranking_endpoints.log_error("Ranking stats error", e)
        raise HTTPException(status_code=500, detail="랭킹 통계 조회 중 오류가 발생했습니다")
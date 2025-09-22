from fastapi import APIRouter

from app.api.v1.endpoints import problems, analysis, users, ranking, guide

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(problems.router, prefix="/problems", tags=["problems"])
api_router.include_router(guide.router, prefix="/guide", tags=["guide"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(ranking.router, prefix="/ranking", tags=["ranking"])
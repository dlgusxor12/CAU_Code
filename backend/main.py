from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {
        "message": "CAU Code Backend Service is running",
        "version": "1.0.0",
        "features": ["solved.ac integration", "AI-powered analysis", "Problem recommendations"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}


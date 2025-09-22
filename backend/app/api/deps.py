from fastapi import HTTPException, status
from app.config import settings


def get_settings():
    return settings


def verify_api_key():
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )
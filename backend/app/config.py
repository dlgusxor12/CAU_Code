import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    app_name: str = "CAU Code Backend"
    debug: bool = True
    cors_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173","https://caucode.vercel.app"]
    database_url: str = "postgresql://caucode_user:dev_password_123@cau-code-db:5432/caucode"

    # Authentication Settings
    secret_key: str = "your-secret-key-change-in-production-please-use-complex-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Google OAuth Settings
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Profile Verification Settings
    verification_code_expire_minutes: int = 5
    max_verification_attempts: int = 3

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

    def __init__(self, **kwargs):
        # 환경변수에서 직접 읽기
        if not kwargs.get("openai_api_key"):
            kwargs["openai_api_key"] = os.getenv("OPEN_AI_KEY", "")
        super().__init__(**kwargs)


settings = Settings()
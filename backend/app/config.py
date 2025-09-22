import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    app_name: str = "CAU Code Backend"
    debug: bool = True
    cors_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

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
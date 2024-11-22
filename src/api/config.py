from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings."""

    FIREBASE_PROJECT_ID: str = os.environ["FIREBASE_PROJECT_ID"]

    APP_NAME: str = "snellie"
    APP_DESCRIPTION: str = "secure receipt prediction microservice"
    APP_VERSION: str = "0.1.0"

    ALLOWED_ORIGINS: list[str] = ["https://localhost:8013"]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    ENABLE_SWAGGER: bool = True
    ENABLE_METRICS: bool = True

    AWS_ACCESS_KEY_ID: str = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY: str = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_S3_BUCKET_NAME: str = os.environ["AWS_S3_BUCKET_NAME"]
    AWS_REGION: str = os.environ["AWS_REGION"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True)


settings = Settings()

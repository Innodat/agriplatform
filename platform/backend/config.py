"""
Application configuration — loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(_REPO_ROOT / ".env"), str(_REPO_ROOT / ".env.local")],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Supabase
    supabase_url: str
    supabase_secret_key: str

    # JWT — Supabase signs JWTs with the project JWT secret
    supabase_jwt_secret: str = ""

    # App
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()

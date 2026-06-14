"""
Application configuration — loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(_BACKEND_DIR / ".env"), str(_BACKEND_DIR / ".env.local")],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""

    # JWT — Supabase signs JWTs with the project JWT secret
    supabase_jwt_secret: str = ""

    # App
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:5174", "http://localhost:3000"]


settings = Settings()

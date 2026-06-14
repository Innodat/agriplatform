"""
App Directory service configuration.
Generated from platform/builder-cli/templates/backend/config.py — vendored.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_SERVICE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(_SERVICE_DIR / ".env"), str(_SERVICE_DIR / ".env.local")],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Supabase (used for JWT verification only — no data CRUD)
    supabase_jwt_secret: str = ""

    # App
    app_env: str = "development"
    cors_origins: list[str] = [
        "http://localhost:5174",  # scribeswell dev
        "http://localhost:5175",  # future app dev
        "http://localhost:3000",
    ]

    # App URLs (override in production via env vars)
    app_url_scribeswell: str = "http://localhost:5174"
    app_url_system_engineering: str = "http://localhost:5175"
    app_url_budgeting: str = "http://localhost:5176"
    app_url_school_management: str = "http://localhost:5177"
    app_url_modelling_simulation: str = "http://localhost:5178"


settings = Settings()

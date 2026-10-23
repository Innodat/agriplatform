"""
Application configuration — loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import SecretStr, model_validator
from database import validate_url

_BACKEND_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(_BACKEND_DIR / ".env"), str(_BACKEND_DIR / ".env.local")],
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    # Supabase
    supabase_url: str = ""
    scribeswell_database_url: SecretStr
    supabase_secret_key: SecretStr = SecretStr("")
    supabase_service_role_key: SecretStr = SecretStr("")

    # Private Studies remains opt-in until controlled migration/qualification.
    scribeswell_studies_enabled: bool = False
    scribeswell_studies_database_url: SecretStr = SecretStr("")
    scribeswell_studies_access_url: str = ""
    scribeswell_studies_service_key: SecretStr = SecretStr("")

    # JWT — Supabase signs JWTs with the project JWT secret
    supabase_jwt_secret: str = ""

    # App
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:5174", "http://localhost:3000"]

    @model_validator(mode="after")
    def database_authority(self):
        if self.supabase_secret_key.get_secret_value() or self.supabase_service_role_key.get_secret_value():
            raise ValueError("Remove obsolete runtime service-key authority")
        validate_url(self.scribeswell_database_url.get_secret_value(), "scribeswell_runtime", self.app_env == "production")
        private = (self.scribeswell_studies_database_url.get_secret_value(), self.scribeswell_studies_access_url, self.scribeswell_studies_service_key.get_secret_value())
        if self.scribeswell_studies_enabled:
            if self.app_env == "production":
                raise ValueError("Studies production activation awaits migration and integration qualification")
            if not all(private): raise ValueError("Studies configuration incomplete")
            validate_url(private[0], "scribeswell_studies_runtime", False)
            from urllib.parse import urlsplit
            target=urlsplit(private[1])
            if target.scheme not in ("http","https") or not target.hostname or target.username or target.password or target.query or target.fragment:
                raise ValueError("Studies Access URL invalid")
        elif any(private):
            raise ValueError("Studies configuration requires explicit opt-in")
        return self


settings = Settings()

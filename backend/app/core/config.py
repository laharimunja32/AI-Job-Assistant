from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    app_name: str = Field(default="AI Job Assistant API")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./app.db")
    db_echo: bool = Field(default=False)
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173")

    secret_key: str = Field(default="change-this-secret-key", description="Secret key for JWT signing")
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    token_audience: str = Field(default="ai-job-assistant", description="JWT audience claim")
    access_token_expire_minutes: int = Field(default=15, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()

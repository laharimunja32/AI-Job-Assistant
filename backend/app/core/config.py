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

    walk_in_scheduler_enabled: bool = Field(default=False, description="Enable scheduled walk-in refresh")
    walk_in_refresh_interval_minutes: int = Field(default=60, description="Walk-in refresh interval in minutes")

    job_scheduler_enabled: bool = Field(default=False, description="Enable scheduled job aggregation")
    job_refresh_interval_minutes: int = Field(default=60, description="Job aggregation interval in minutes")
    aggregation_scheduler_enabled: bool = Field(default=False, description="Enable unified aggregation scheduler")
    dashboard_refresh_interval_minutes: int = Field(default=30, description="Dashboard cache refresh interval in minutes")
    dashboard_cache_ttl_seconds: int = Field(default=300, description="Dashboard response cache TTL in seconds")
    dashboard_default_page_size: int = Field(default=20, description="Default page size for dashboard endpoints")
    playwright_browser: str = Field(default="chromium", description="Default browser for Playwright sessions")
    playwright_headless: bool = Field(default=False, description="Run Playwright browsers in headless mode")
    playwright_timeout: int = Field(default=30000, description="Navigation timeout for Playwright in milliseconds")
    session_idle_timeout: int = Field(default=600, description="Idle timeout for browser sessions in seconds")
    max_browser_sessions: int = Field(default=5, description="Maximum concurrent browser sessions")

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

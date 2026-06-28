"""Application settings, loaded from environment / .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is two levels up from this file (backend/app/config.py -> repo root)
ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", "backend/.env"),
        env_prefix="",
        extra="ignore",
    )

    # App
    orbes_env: str = "development"
    orbes_secret_key: str = "dev-insecure-secret-change-me"
    orbes_access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    # Admin seed
    orbes_admin_email: str = "admin@example.com"
    orbes_admin_password: str = "change-me"

    # Database
    orbes_database_url: str = "sqlite:///./orbes.db"

    # LLM
    anthropic_api_key: str = ""
    orbes_llm_model: str = "claude-opus-4-8"
    orbes_llm_max_tokens: int = 2048

    # Tool integrations
    openweather_api_key: str = ""
    tavily_api_key: str = ""
    serpapi_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

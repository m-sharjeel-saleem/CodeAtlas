"""Typed application settings, loaded from the environment.

Secrets live only here, server-side. Never import these into anything that
ships to the browser.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    anthropic_api_key: str = ""
    model_reasoning: str = "claude-opus-4-8"
    model_fast: str = "claude-sonnet-4-6"

    # GitHub
    github_token: str = ""

    # Infra
    database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"

    # App
    cors_origins: str = "http://localhost:3000"
    session_cost_cap_usd: float = 1.00
    max_files_per_repo: int = 400

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so settings are parsed once per process."""
    return Settings()

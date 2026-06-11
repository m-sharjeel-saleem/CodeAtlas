"""Test fixtures.

Force keyless / no-DB mode for every test so the suite is fast, offline, and
deterministic — it validates wiring and pure logic, not live model output.
"""
import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def keyless_env(monkeypatch):
    # Env vars take priority over the .env file in pydantic-settings.
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("REDIS_URL", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

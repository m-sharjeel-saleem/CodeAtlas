"""Tiny cache + cost-counter wrapper.

Uses Redis when REDIS_URL is reachable; otherwise falls back to an in-process
dict so the app runs fine without Redis (e.g. local dev, keyless mode).
"""
from app.config import get_settings

_memory: dict[str, str] = {}
_client = None
_tried = False


def _redis():
    global _client, _tried
    if _tried:
        return _client
    _tried = True
    settings = get_settings()
    url = settings.redis_url
    if not url or url.startswith("redis://localhost"):
        # Don't hard-depend on a local server in keyless/dev mode.
        if not url:
            return None
    try:
        import redis

        client = redis.from_url(url, socket_connect_timeout=2, decode_responses=True)
        client.ping()
        _client = client
    except Exception:
        _client = None  # graceful fallback to memory
    return _client


def get(key: str) -> str | None:
    r = _redis()
    if r:
        try:
            return r.get(key)
        except Exception:
            pass
    return _memory.get(key)


def set(key: str, value: str, ttl: int | None = None) -> None:
    r = _redis()
    if r:
        try:
            r.set(key, value, ex=ttl)
            return
        except Exception:
            pass
    _memory[key] = value

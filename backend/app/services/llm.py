"""Anthropic Claude client wrapper.

Centralizes model selection and (soon) token/cost accounting so every agent
reports usage into the run trace. Reasoning-heavy steps use Opus; high-throughput
steps use Sonnet.
"""
from app.config import get_settings

# Approximate per-million-token USD pricing, used for the cost dashboard. Update
# from the pricing page; treated as an estimate, not billing truth.
_PRICING = {
    "claude-opus-4-8": {"in": 15.0, "out": 75.0},
    "claude-sonnet-4-6": {"in": 3.0, "out": 15.0},
}


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    p = _PRICING.get(model, {"in": 0.0, "out": 0.0})
    return (tokens_in / 1_000_000) * p["in"] + (tokens_out / 1_000_000) * p["out"]


def get_client():
    """Return an Anthropic client. Imported lazily so the package isn't required
    just to import the app (e.g. during health checks or tests)."""
    from anthropic import Anthropic

    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return Anthropic(api_key=settings.anthropic_api_key)


# TODO: complete(model, system, messages) -> (text, tokens_in, tokens_out) and a
# streaming variant that yields tokens for SSE.

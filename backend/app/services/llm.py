"""Google Gemini client wrapper.

Centralizes model selection and (soon) token/cost accounting so every agent
reports usage into the run trace. Reasoning-heavy steps use Gemini 2.5 Pro;
high-throughput steps use Gemini 2.5 Flash.
"""
from app.config import get_settings

# Approximate per-million-token USD pricing, used for the cost dashboard. Update
# from Google's pricing page; treated as an estimate, not billing truth.
_PRICING = {
    "gemini-2.5-pro": {"in": 1.25, "out": 10.0},
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50},
}


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    p = _PRICING.get(model, {"in": 0.0, "out": 0.0})
    return (tokens_in / 1_000_000) * p["in"] + (tokens_out / 1_000_000) * p["out"]


def get_client():
    """Return a configured Gemini client. Imported lazily so the package isn't
    required just to import the app (e.g. during health checks or tests)."""
    import google.generativeai as genai

    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    genai.configure(api_key=settings.gemini_api_key)
    return genai


# TODO: complete(model, system, contents) -> (text, tokens_in, tokens_out) and a
# streaming variant that yields tokens for SSE. Gemini reports usage via
# response.usage_metadata (prompt_token_count / candidates_token_count).

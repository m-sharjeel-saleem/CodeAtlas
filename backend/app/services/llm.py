"""Google Gemini wrapper — text generation + embeddings.

Designed to degrade gracefully: with no GEMINI_API_KEY set, `complete()` returns
a clear stub (so the whole app runs keyless for UI/demo) and `embed()` returns
None. With a key, it makes real Gemini calls and reports token usage + cost.
"""
from dataclasses import dataclass

from app.config import get_settings

# Approximate per-million-token USD pricing for the cost dashboard (estimate only).
_PRICING = {
    "gemini-2.5-pro": {"in": 1.25, "out": 10.0},
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50},
}

EMBED_DIM = 768  # text-embedding-004


@dataclass
class LLMResult:
    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    stub: bool = False


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    p = _PRICING.get(model, {"in": 0.0, "out": 0.0})
    return (tokens_in / 1_000_000) * p["in"] + (tokens_out / 1_000_000) * p["out"]


def _configured():
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        return genai
    except Exception:
        return None


def complete(system: str, prompt: str, *, model: str | None = None) -> LLMResult:
    """Single-shot completion. Returns a stub result if Gemini is not configured."""
    settings = get_settings()
    model = model or settings.model_fast
    genai = _configured()
    if genai is None:
        return LLMResult(
            text="[CodeAtlas is running without a Gemini key — set GEMINI_API_KEY to "
            "get a real, grounded answer here.]",
            stub=True,
        )
    gm = genai.GenerativeModel(model, system_instruction=system)
    resp = gm.generate_content(prompt)
    usage = getattr(resp, "usage_metadata", None)
    tin = getattr(usage, "prompt_token_count", 0) or 0
    tout = getattr(usage, "candidates_token_count", 0) or 0
    return LLMResult(
        text=resp.text or "",
        tokens_in=tin,
        tokens_out=tout,
        cost_usd=estimate_cost_usd(model, tin, tout),
    )


def complete_json(system: str, prompt: str, *, model: str | None = None) -> tuple[object, LLMResult]:
    """Completion constrained to JSON. Returns (parsed_or_None, LLMResult)."""
    import json

    settings = get_settings()
    model = model or settings.model_fast
    genai = _configured()
    if genai is None:
        return None, LLMResult(text="[]", stub=True)
    gm = genai.GenerativeModel(model, system_instruction=system)
    resp = gm.generate_content(
        prompt, generation_config={"response_mime_type": "application/json"}
    )
    usage = getattr(resp, "usage_metadata", None)
    tin = getattr(usage, "prompt_token_count", 0) or 0
    tout = getattr(usage, "candidates_token_count", 0) or 0
    result = LLMResult(
        text=resp.text or "",
        tokens_in=tin,
        tokens_out=tout,
        cost_usd=estimate_cost_usd(model, tin, tout),
    )
    try:
        return json.loads(resp.text), result
    except (json.JSONDecodeError, TypeError):
        return None, result


def embed(texts: list[str], *, task_type: str = "retrieval_document") -> list[list[float]] | None:
    """Embed a batch of texts with text-embedding-004. None if not configured."""
    genai = _configured()
    if genai is None or not texts:
        return None
    settings = get_settings()
    model = f"models/{settings.embedding_model}"
    out: list[list[float]] = []
    # Gemini embeds one document per call reliably; batch in a simple loop.
    for t in texts:
        res = genai.embed_content(model=model, content=t, task_type=task_type)
        out.append(res["embedding"])
    return out

"""Google Gemini wrapper — text generation + embeddings over the REST API.

Uses httpx directly (no SDK) against the Generative Language API. Degrades
gracefully: with no GEMINI_API_KEY, `complete()` returns a clear stub and
`embed()` returns None, so the whole app runs keyless for demos. With a key it
makes real calls and reports token usage + cost.
"""
from dataclasses import dataclass

import httpx

from app.config import get_settings

_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Approximate per-million-token USD pricing for the cost dashboard (estimate only).
_PRICING = {
    "gemini-2.5-pro": {"in": 1.25, "out": 10.0},
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50},
}

EMBED_DIM = 768  # requested output dimensionality for gemini-embedding-001


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


def _key() -> str | None:
    k = get_settings().gemini_api_key
    return k if k and not k.startswith("AIzaSyxxxx") else None


def _generate(system: str, prompt: str, model: str, json_mode: bool) -> LLMResult:
    key = _key()
    if not key:
        return LLMResult(text="[]" if json_mode else
                         "[CodeAtlas is running without a Gemini key — set GEMINI_API_KEY "
                         "to get a real, grounded answer here.]", stub=True)
    body: dict = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system}]},
    }
    if json_mode:
        body["generationConfig"] = {"response_mime_type": "application/json"}
    r = httpx.post(f"{_BASE}/models/{model}:generateContent",
                   params={"key": key}, json=body, timeout=90)
    r.raise_for_status()
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        text = ""
    usage = data.get("usageMetadata", {})
    tin = usage.get("promptTokenCount", 0)
    tout = usage.get("candidatesTokenCount", 0)
    return LLMResult(text=text, tokens_in=tin, tokens_out=tout,
                     cost_usd=estimate_cost_usd(model, tin, tout))


def complete(system: str, prompt: str, *, model: str | None = None) -> LLMResult:
    """Single-shot completion. Stub result if Gemini is not configured."""
    return _generate(system, prompt, model or get_settings().model_fast, json_mode=False)


def complete_json(system: str, prompt: str, *, model: str | None = None) -> tuple[object, LLMResult]:
    """Completion constrained to JSON. Returns (parsed_or_None, LLMResult)."""
    import json

    res = _generate(system, prompt, model or get_settings().model_fast, json_mode=True)
    try:
        return json.loads(res.text), res
    except (json.JSONDecodeError, TypeError):
        return None, res


def embed(texts: list[str], *, task_type: str = "retrieval_document") -> list[list[float]] | None:
    """Embed a batch with gemini-embedding-001 at EMBED_DIM dims. None if no key."""
    key = _key()
    if not key or not texts:
        return None
    model = get_settings().embedding_model
    out: list[list[float]] = []
    # batchEmbedContents in groups to stay within request limits.
    for i in range(0, len(texts), 100):
        batch = texts[i : i + 100]
        body = {
            "requests": [
                {
                    "model": f"models/{model}",
                    "content": {"parts": [{"text": t}]},
                    "taskType": task_type.upper(),
                    "outputDimensionality": EMBED_DIM,
                }
                for t in batch
            ]
        }
        r = httpx.post(f"{_BASE}/models/{model}:batchEmbedContents",
                       params={"key": key}, json=body, timeout=90)
        r.raise_for_status()
        out.extend(e["values"] for e in r.json().get("embeddings", []))
    return out

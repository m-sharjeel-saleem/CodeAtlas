"""Reviewer nodes — three specialist agents inspect retrieved code in parallel.

Each calls Gemini constrained to JSON and parses Finding[]. The state reducer
concatenates findings across the three agents. Respects the session cost cap.
"""
from app.agents.prompts import REVIEW_SYSTEM
from app.agents.state import AgentState, Finding
from app.config import get_settings
from app.core.guardrails import wrap_untrusted
from app.services import llm

_RUBRIC = {
    "security": "injection, auth flaws, secret handling, unsafe deserialization, OWASP Top 10",
    "performance": "N+1 queries, needless allocations, blocking I/O, missing caching, hot-path cost",
    "logic": "off-by-one, wrong conditionals, unhandled edge cases, incorrect state transitions",
}

_VALID_SEVERITY = {"low", "medium", "high", "critical"}


def _context(state: AgentState) -> str:
    chunks = state.get("chunks", [])
    if not chunks:
        return ""
    return "\n\n".join(f"# {c['file']}\n{wrap_untrusted(c['content'])}" for c in chunks)


def _parse(raw: object, lens: str) -> list[Finding]:
    if not isinstance(raw, list):
        return []
    findings: list[Finding] = []
    for item in raw:
        if not isinstance(item, dict) or "title" not in item:
            continue
        sev = str(item.get("severity", "medium")).lower()
        findings.append(
            {
                "agent": lens,
                "title": str(item.get("title", ""))[:200],
                "detail": str(item.get("detail", "")),
                "file": str(item.get("file", "")),
                "line": item.get("line") if isinstance(item.get("line"), int) else None,
                "severity": sev if sev in _VALID_SEVERITY else "medium",
                "verified": False,
            }
        )
    return findings


def _review(state: AgentState, lens: str) -> dict:
    cap = get_settings().session_cost_cap_usd
    context = _context(state)
    if not context or state.get("cost_usd", 0.0) >= cap:
        reason = "no context" if not context else "cost cap reached"
        return {"steps": [f"{lens} review → skipped ({reason})"]}

    system = REVIEW_SYSTEM.format(lens=lens, rubric=_RUBRIC[lens])
    prompt = f"Repository: {state.get('repo')}\n\nCode to review:\n{context}"
    parsed, res = llm.complete_json(system, prompt)
    findings = _parse(parsed, lens)
    return {
        "findings": findings,
        "cost_usd": res.cost_usd,
        "tokens_in": res.tokens_in,
        "tokens_out": res.tokens_out,
        "steps": [f"{lens} review → {len(findings)} candidate findings"],
    }


def security_review_node(state: AgentState) -> dict:
    return _review(state, "security")


def performance_review_node(state: AgentState) -> dict:
    return _review(state, "performance")


def logic_review_node(state: AgentState) -> dict:
    return _review(state, "logic")

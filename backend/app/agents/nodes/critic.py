"""Critic node — verifies each reviewer finding against the actual source.

The anti-hallucination gate: a finding is kept (`verified=True`) only if the
Critic can confirm it against the cited code. Writes the confirmed subset to
`verified_findings` (overwrite semantics, unlike the appended `findings`).
Bounded by a max count and the session cost cap.
"""
from app.agents.prompts import CRITIC_SYSTEM
from app.agents.state import AgentState, Finding
from app.config import get_settings
from app.core.guardrails import wrap_untrusted
from app.services import llm

_MAX_VERIFY = 12


def _source_for(state: AgentState, file: str) -> str:
    for c in state.get("chunks", []):
        if c["file"] == file:
            return c["content"]
    return ""


def critic_node(state: AgentState) -> dict:
    findings = state.get("findings", [])
    cap = get_settings().session_cost_cap_usd
    verified: list[Finding] = []
    running_cost = state.get("cost_usd", 0.0)  # cost so far across the run
    critic_cost = 0.0                           # cost this node adds (reducer sums it in)
    tokens_in = tokens_out = 0

    for f in findings[:_MAX_VERIFY]:
        if running_cost + critic_cost >= cap:
            break
        source = _source_for(state, f["file"])
        prompt = (
            f"Candidate finding: {f['title']} — {f['detail']}\n"
            f"File: {f['file']}\n\nSource:\n{wrap_untrusted(source)}"
        )
        parsed, res = llm.complete_json(CRITIC_SYSTEM, prompt)
        critic_cost += res.cost_usd
        tokens_in += res.tokens_in
        tokens_out += res.tokens_out
        if isinstance(parsed, dict) and parsed.get("verified") is True:
            verified.append({**f, "verified": True})

    return {
        "verified_findings": verified,
        "cost_usd": critic_cost,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "steps": [f"critic → {len(verified)}/{len(findings)} findings verified against source"],
    }

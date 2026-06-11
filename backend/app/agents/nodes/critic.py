"""Critic node — verifies each reviewer finding against the actual source.

This is the anti-hallucination gate: a finding is only kept (`verified=True`) if
the Critic can confirm it against the retrieved code. Reduces the false-positive
rate that makes naive LLM code review untrustworthy.
"""
from app.agents.state import AgentState


def critic_node(state: AgentState) -> dict:
    findings = state.get("findings", [])
    # TODO: for each finding, ask the LLM to confirm/refute it strictly against the
    # cited chunk; set verified accordingly. Placeholder marks none yet verified.
    verified = [f for f in findings if f.get("verified")]
    return {
        "steps": [
            f"critic → {len(verified)}/{len(findings)} findings verified against source"
        ],
    }

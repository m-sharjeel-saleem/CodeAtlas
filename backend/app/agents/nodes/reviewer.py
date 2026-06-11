"""Reviewer nodes — three specialist agents inspect retrieved code in parallel.

Each returns Finding[] which the state reducer concatenates. They share one
implementation parameterised by lens, so behaviour stays consistent.
"""
from app.agents.state import AgentState, Finding

_LENSES = {
    "security": "injection, auth flaws, secret handling, unsafe deserialization, OWASP Top 10",
    "performance": "N+1 queries, needless allocations, blocking I/O, missing caching, hot-path cost",
    "logic": "off-by-one, wrong conditionals, unhandled edge cases, incorrect state transitions",
}


def _review(state: AgentState, lens: str) -> dict:
    chunks = state.get("chunks", [])
    # TODO: prompt the LLM with the lens-specific rubric over the delimited chunks
    # and parse structured Finding[] (tool-call / JSON schema). Placeholder below.
    findings: list[Finding] = []
    return {
        "findings": findings,
        "steps": [f"{lens} review → {len(findings)} candidate findings ({_LENSES[lens]})"],
    }


def security_review_node(state: AgentState) -> dict:
    return _review(state, "security")


def performance_review_node(state: AgentState) -> dict:
    return _review(state, "performance")


def logic_review_node(state: AgentState) -> dict:
    return _review(state, "logic")

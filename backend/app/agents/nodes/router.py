"""Router node — classifies the user's request into an intent.

A small, cheap model is enough here. For the MVP we use a keyword heuristic so
the graph runs without an LLM key; swap in a classification call when ready.
"""
from app.agents.state import AgentState, Intent


def _classify(question: str) -> Intent:
    q = question.lower()
    if any(k in q for k in ("review", "audit", "security", "vulnerab", "bug")):
        return "review"
    if any(k in q for k in ("architecture", "structure", "overview", "how does", "map")):
        return "architecture"
    if any(k in q for k in ("docstring", "write tests", "generate test", "add docs")):
        return "generate"
    return "chat"


def router_node(state: AgentState) -> dict:
    intent = _classify(state.get("question", ""))
    return {"intent": intent, "steps": [f"router → intent={intent}"]}

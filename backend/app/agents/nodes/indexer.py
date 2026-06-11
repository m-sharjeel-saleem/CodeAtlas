"""Responder node — answers chat/architecture requests from retrieved context.

Builds a prompt from delimited (untrusted) chunks and calls Gemini. Writes the
answer plus token/cost accounting into the run trace. Falls back to a clear stub
when Gemini is not configured.
"""
from app.agents.prompts import ARCHITECTURE_SYSTEM, RESPONDER_SYSTEM
from app.agents.state import AgentState
from app.core.guardrails import wrap_untrusted
from app.services import llm


def _context(state: AgentState) -> str:
    chunks = state.get("chunks", [])
    if not chunks:
        return "(no indexed context found for this repository)"
    return "\n\n".join(
        f"# {c['file']}\n{wrap_untrusted(c['content'])}" for c in chunks
    )


def responder_node(state: AgentState) -> dict:
    is_arch = state.get("intent") == "architecture"
    system = ARCHITECTURE_SYSTEM if is_arch else RESPONDER_SYSTEM
    prompt = (
        f"Repository: {state.get('repo')}\n"
        f"Question: {state.get('question')}\n\n"
        f"Code context:\n{_context(state)}"
    )
    res = llm.complete(system, prompt)
    out: dict = {
        "cost_usd": res.cost_usd,
        "tokens_in": res.tokens_in,
        "tokens_out": res.tokens_out,
        "steps": ["responder → drafted grounded answer"],
    }
    if is_arch:
        out["architecture"] = res.text
    else:
        out["answer"] = res.text
    return out

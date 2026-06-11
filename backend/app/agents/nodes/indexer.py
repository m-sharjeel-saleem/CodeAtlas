"""Responder node — answers chat/architecture requests from retrieved context.

Named `indexer` historically; it now hosts the responder. Generates a grounded,
cited answer from the retrieved chunks. MVP returns a deterministic placeholder
so the graph is runnable without an LLM key.
"""
from app.agents.state import AgentState
from app.core.guardrails import wrap_untrusted


def responder_node(state: AgentState) -> dict:
    chunks = state.get("chunks", [])
    # Untrusted repo content is delimited before it ever reaches a prompt.
    _context = "\n\n".join(wrap_untrusted(c["content"]) for c in chunks)

    # TODO: call the LLM with the question + delimited context; stream tokens out;
    # record real cost/tokens. For now, a placeholder keeps the graph runnable.
    answer = (
        f"[placeholder] Would answer '{state.get('question')}' for "
        f"{state.get('repo')} using {len(chunks)} retrieved chunks."
    )
    return {"answer": answer, "steps": ["responder → drafted grounded answer"]}

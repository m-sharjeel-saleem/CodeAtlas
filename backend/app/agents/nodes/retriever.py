"""Retriever node — hybrid RAG over the indexed repo.

MVP: returns a placeholder so the graph runs end-to-end. The production version
queries pgvector (semantic) and combines with keyword matching, then re-ranks.
"""
from app.agents.state import AgentState


def retriever_node(state: AgentState) -> dict:
    # TODO: query pgvector for top-k chunks for state["question"], blend with
    # keyword search, re-rank, and return RetrievedChunk[].
    chunks: list = []
    return {
        "chunks": chunks,
        "steps": [f"retriever → {len(chunks)} chunks for repo={state.get('repo')}"],
    }

"""Retriever node — hybrid RAG over the indexed repo.

Embeds the question (when a key is available) and runs hybrid semantic+keyword
search in pgvector. Returns [] gracefully when nothing is indexed or services
are unavailable, so the graph still completes.
"""
from app.agents.state import AgentState
from app.services import llm, vectorstore


def retriever_node(state: AgentState) -> dict:
    question = state.get("question", "")
    repo = state.get("repo", "")

    q_emb = None
    embedded = llm.embed([question], task_type="retrieval_query")
    if embedded:
        q_emb = embedded[0]

    chunks = vectorstore.hybrid_search(repo, question, q_emb, k=6)
    return {
        "chunks": chunks,
        "steps": [f"retriever → {len(chunks)} chunks for repo={repo}"],
    }

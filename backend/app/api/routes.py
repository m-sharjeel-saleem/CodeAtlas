"""HTTP API for CodeAtlas."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.graph import graph
from app.services.github import normalize_repo

router = APIRouter(prefix="/api", tags=["codeatlas"])


class IngestRequest(BaseModel):
    repo: str = Field(..., examples=["facebook/react"])


class AnalyzeRequest(BaseModel):
    repo: str = Field(..., examples=["facebook/react"])
    question: str = Field(..., examples=["How does the reconciler schedule work?"])


@router.post("/ingest")
def ingest(req: IngestRequest) -> dict:
    """Resolve and (soon) index a public repo into the vector store."""
    try:
        repo = normalize_repo(req.repo)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    # TODO: enqueue indexing job (fetch files → chunk → embed → pgvector).
    return {"repo": repo, "status": "accepted", "indexed": False}


@router.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    """Run the agent graph for a question and return the result + run trace."""
    try:
        repo = normalize_repo(req.repo)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    result = graph.invoke({"repo": repo, "question": req.question})
    return {
        "repo": repo,
        "intent": result.get("intent"),
        "answer": result.get("answer"),
        "architecture": result.get("architecture"),
        "findings": result.get("findings", []),
        "trace": {
            "steps": result.get("steps", []),
            "cost_usd": round(result.get("cost_usd", 0.0), 6),
            "tokens_in": result.get("tokens_in", 0),
            "tokens_out": result.get("tokens_out", 0),
        },
    }

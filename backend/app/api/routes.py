"""HTTP API for CodeAtlas."""
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.agents.graph import graph
from app.services.github import normalize_repo
from app.services.ingest import ingest_repo

router = APIRouter(prefix="/api", tags=["codeatlas"])


class IngestRequest(BaseModel):
    repo: str = Field(..., examples=["facebook/react"])


class AnalyzeRequest(BaseModel):
    repo: str = Field(..., examples=["facebook/react"])
    question: str = Field(..., examples=["How does the reconciler schedule work?"])


def _repo_or_422(value: str) -> str:
    try:
        return normalize_repo(value)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/ingest")
def ingest(req: IngestRequest) -> dict:
    """Fetch a public repo, chunk, embed, and store it for retrieval."""
    repo = _repo_or_422(req.repo)
    report = ingest_repo(repo)
    return {
        "repo": report.repo,
        "files_indexed": report.files_indexed,
        "chunks": report.chunks,
        "embedded": report.embedded,
        "persisted": report.persisted,
        "error": report.error,
    }


def _shape(repo: str, result: dict) -> dict:
    findings = result.get("verified_findings") or result.get("findings", [])
    return {
        "repo": repo,
        "intent": result.get("intent"),
        "answer": result.get("answer"),
        "architecture": result.get("architecture"),
        "findings": findings,
        "trace": {
            "steps": result.get("steps", []),
            "cost_usd": round(result.get("cost_usd", 0.0), 6),
            "tokens_in": result.get("tokens_in", 0),
            "tokens_out": result.get("tokens_out", 0),
        },
    }


@router.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    """Run the agent graph for a question and return the result + run trace."""
    repo = _repo_or_422(req.repo)
    result = graph.invoke({"repo": repo, "question": req.question})
    return _shape(repo, result)


@router.post("/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    """Stream the run as Server-Sent Events: one `step` event per agent node,
    then a final `result` event with the full shaped payload."""
    repo = _repo_or_422(req.repo)

    async def gen():
        seen = 0
        final: dict = {}
        async for chunk in graph.astream(
            {"repo": repo, "question": req.question}, stream_mode="values"
        ):
            final = chunk
            steps = chunk.get("steps", [])
            for step in steps[seen:]:
                yield {"event": "step", "data": step}
            seen = len(steps)
        yield {"event": "result", "data": json.dumps(_shape(repo, final))}

    return EventSourceResponse(gen())

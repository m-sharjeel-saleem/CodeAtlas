"""Shared state passed between LangGraph nodes.

A single typed dict flows through the graph; each node reads what it needs and
writes its results back. Keeping it explicit makes traces and debugging clean.
"""
from operator import add
from typing import Annotated, Literal, TypedDict

Intent = Literal["chat", "architecture", "review", "generate"]


class Finding(TypedDict):
    """One issue raised by a reviewer agent."""
    agent: str            # "security" | "performance" | "logic"
    title: str
    detail: str
    file: str
    line: int | None
    severity: Literal["low", "medium", "high", "critical"]
    verified: bool        # set True only after the Critic confirms it against source


class RetrievedChunk(TypedDict):
    file: str
    content: str
    score: float


class AgentState(TypedDict, total=False):
    # Inputs
    repo: str                                   # "owner/name"
    question: str
    intent: Intent

    # Retrieval
    chunks: list[RetrievedChunk]

    # Outputs
    answer: str
    architecture: str
    findings: Annotated[list[Finding], add]     # reducer: reviewers append concurrently
    verified_findings: list[Finding]            # overwrite: critic's confirmed subset

    # Observability — accumulated across the run
    cost_usd: Annotated[float, add]
    tokens_in: Annotated[int, add]
    tokens_out: Annotated[int, add]
    steps: Annotated[list[str], add]            # human-readable trace breadcrumbs

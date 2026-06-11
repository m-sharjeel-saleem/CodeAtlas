"""Ingest orchestration: GitHub → chunk → embed → pgvector.

Returns a structured report used by the /ingest endpoint. Degrades clearly:
- no GitHub access → reports the error
- no Gemini key → chunks are stored without embeddings (keyword search still works)
- no database → nothing persisted, but the call still reports what it fetched
"""
import logging
from dataclasses import asdict, dataclass

from app.config import get_settings
from app.services import github, llm, vectorstore
from app.services.chunking import chunk_file

log = logging.getLogger("codeatlas.ingest")


@dataclass
class IngestReport:
    repo: str
    files_indexed: int
    chunks: int
    embedded: bool
    persisted: bool
    error: str | None = None


def ingest_repo(repo: str) -> IngestReport:
    settings = get_settings()
    try:
        paths = github.list_source_files(repo, max_files=settings.max_files_per_repo)
    except Exception as e:  # noqa: BLE001
        return IngestReport(repo, 0, 0, False, False, error=f"GitHub fetch failed: {e}")

    rows: list[dict] = []
    for path in paths:
        content = github.fetch_file(repo, path)
        if content:
            rows.extend(chunk_file(path, content))

    if not rows:
        return IngestReport(repo, len(paths), 0, False, False, error="No source content found")

    embeddings = llm.embed([r["content"] for r in rows])
    embedded = embeddings is not None
    if not embedded:
        # Store with zero-vectors so keyword search still works without a key.
        embeddings = [[0.0] * llm.EMBED_DIM for _ in rows]

    persisted = vectorstore.replace_repo_chunks(repo, rows, embeddings) > 0
    report = IngestReport(repo, len(paths), len(rows), embedded, persisted)
    log.info("ingest %s", asdict(report))
    return report

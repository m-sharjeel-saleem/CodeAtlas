"""pgvector-backed storage and hybrid retrieval for code chunks.

Degrades gracefully: if DATABASE_URL is unset or the database is unreachable,
every function logs and returns an empty/no-op result so the app still runs.
"""
import logging

from app.config import get_settings
from app.services.llm import EMBED_DIM

log = logging.getLogger("codeatlas.vectorstore")

_SCHEMA = f"""
create extension if not exists vector;
create table if not exists code_chunks (
    id          bigserial primary key,
    repo        text   not null,
    file        text   not null,
    start_line  int    not null default 1,
    content     text   not null,
    embedding   vector({EMBED_DIM})
);
create index if not exists code_chunks_repo_idx on code_chunks (repo);
"""


def _connect():
    """Return a psycopg connection with pgvector registered, or None."""
    url = get_settings().database_url
    if not url:
        return None
    try:
        import psycopg
        from pgvector.psycopg import register_vector

        conn = psycopg.connect(url, connect_timeout=8, autocommit=True)
        register_vector(conn)
        return conn
    except Exception as e:  # noqa: BLE001 — degrade on any connection error
        log.warning("Database unavailable, retrieval disabled: %s", e)
        return None


def ensure_schema() -> bool:
    conn = _connect()
    if conn is None:
        return False
    with conn, conn.cursor() as cur:
        cur.execute(_SCHEMA)
    conn.close()
    return True


def replace_repo_chunks(repo: str, rows: list[dict], embeddings: list[list[float]]) -> int:
    """Wipe and re-insert all chunks for a repo. Returns count stored."""
    conn = _connect()
    if conn is None:
        return 0
    stored = 0
    with conn, conn.cursor() as cur:
        cur.execute(_SCHEMA)
        cur.execute("delete from code_chunks where repo = %s", (repo,))
        for row, emb in zip(rows, embeddings):
            cur.execute(
                "insert into code_chunks (repo, file, start_line, content, embedding) "
                "values (%s, %s, %s, %s, %s)",
                (repo, row["file"], row.get("start_line", 1), row["content"], emb),
            )
            stored += 1
    conn.close()
    return stored


def hybrid_search(
    repo: str,
    query: str,
    query_embedding: list[float] | None,
    *,
    k: int = 6,
) -> list[dict]:
    """Top-k chunks blending semantic similarity (0.7) and keyword overlap (0.3).

    Falls back to keyword-only when there is no query embedding (e.g. keyless).
    Returns dicts: {file, content, score}.
    """
    conn = _connect()
    if conn is None:
        return []
    results: dict[tuple, dict] = {}
    with conn, conn.cursor() as cur:
        if query_embedding is not None:
            cur.execute(
                "select file, start_line, content, 1 - (embedding <=> %s::vector) as sim "
                "from code_chunks where repo = %s "
                "order by embedding <=> %s::vector limit %s",
                (query_embedding, repo, query_embedding, k * 2),
            )
            for file, line, content, sim in cur.fetchall():
                results[(file, line)] = {
                    "file": file,
                    "content": content,
                    "score": 0.7 * float(sim),
                }
        # Keyword overlap bonus (and primary signal when no embedding).
        like = f"%{query[:80]}%"
        cur.execute(
            "select file, start_line, content from code_chunks "
            "where repo = %s and content ilike %s limit %s",
            (repo, like, k * 2),
        )
        for file, line, content in cur.fetchall():
            key = (file, line)
            if key in results:
                results[key]["score"] += 0.3
            else:
                results[key] = {"file": file, "content": content, "score": 0.3}
    conn.close()
    ranked = sorted(results.values(), key=lambda r: r["score"], reverse=True)
    return ranked[:k]

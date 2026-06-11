"""Split source files into overlapping, line-aware chunks for embedding.

Line-based chunking keeps citations meaningful (we know the start line) and is
language-agnostic — good enough for retrieval across any repo.
"""
from typing import TypedDict

# Extensions we treat as source worth indexing.
SOURCE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".kt", ".go", ".rs", ".rb",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".swift", ".scala", ".sql",
    ".sh", ".yaml", ".yml", ".toml", ".md", ".mjs", ".cjs", ".vue", ".svelte",
}

# Paths we never index (vendored, generated, lockfiles, binaries).
SKIP_SEGMENTS = {
    "node_modules", "dist", "build", ".next", "vendor", "venv", ".venv",
    "__pycache__", ".git", "target", "coverage", "out", ".cache",
}


class Chunk(TypedDict):
    file: str
    content: str
    start_line: int


def is_source_file(path: str) -> bool:
    if any(f"/{seg}/" in f"/{path}/" for seg in SKIP_SEGMENTS):
        return False
    dot = path.rfind(".")
    return dot != -1 and path[dot:].lower() in SOURCE_EXTENSIONS


def chunk_file(path: str, content: str, *, size: int = 60, overlap: int = 10) -> list[Chunk]:
    """Split one file into chunks of ~`size` lines with `overlap` lines of context.

    `size`/`overlap` are in lines (not characters) so chunks align to code structure.
    """
    lines = content.splitlines()
    if not lines:
        return []
    step = max(1, size - overlap)
    chunks: list[Chunk] = []
    for start in range(0, len(lines), step):
        window = lines[start : start + size]
        if not window:
            break
        chunks.append(
            {"file": path, "content": "\n".join(window), "start_line": start + 1}
        )
        if start + size >= len(lines):
            break
    return chunks

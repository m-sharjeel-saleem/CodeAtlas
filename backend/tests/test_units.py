"""Unit tests for the pure logic added in the real implementation."""
from app.agents.nodes.reviewer import _parse
from app.services.chunking import chunk_file, is_source_file
from app.services.llm import estimate_cost_usd


def test_is_source_file():
    assert is_source_file("src/app/main.py")
    assert is_source_file("README.md")
    assert not is_source_file("node_modules/lib/index.js")  # skipped segment
    assert not is_source_file("image.png")                   # not a source ext


def test_chunk_file_overlaps_and_tracks_lines():
    content = "\n".join(f"line{i}" for i in range(1, 131))  # 130 lines
    chunks = chunk_file("a.py", content, size=60, overlap=10)
    assert len(chunks) >= 2
    assert chunks[0]["start_line"] == 1
    # step = size - overlap = 50, so the second chunk starts at line 51
    assert chunks[1]["start_line"] == 51
    assert all(c["file"] == "a.py" for c in chunks)


def test_chunk_file_empty():
    assert chunk_file("empty.py", "") == []


def test_review_parser_normalizes_and_filters():
    raw = [
        {"title": "SQL injection", "detail": "x", "file": "db.py", "line": 10, "severity": "CRITICAL"},
        {"detail": "no title -> dropped"},
        {"title": "weird sev", "file": "a.py", "line": "nope", "severity": "spicy"},
    ]
    out = _parse(raw, "security")
    assert len(out) == 2
    assert out[0]["severity"] == "critical"
    assert out[0]["agent"] == "security"
    assert out[0]["verified"] is False
    assert out[1]["severity"] == "medium"   # invalid severity -> default
    assert out[1]["line"] is None           # non-int line -> None


def test_review_parser_handles_non_list():
    assert _parse(None, "logic") == []
    assert _parse({"not": "a list"}, "logic") == []


def test_cost_estimate():
    c = estimate_cost_usd("gemini-2.5-flash", 1_000_000, 1_000_000)
    assert round(c, 2) == round(0.30 + 2.50, 2)

"""GitHub access — read public repositories via the REST API.

Uses the optional GITHUB_TOKEN for higher rate limits. All network calls are
synchronous httpx (the ingest runs in a worker context, not the request path).
"""
import re

import httpx

from app.config import get_settings
from app.services.chunking import is_source_file

_REPO_RE = re.compile(r"^[\w.-]+/[\w.-]+$")
_API = "https://api.github.com"


def normalize_repo(url_or_slug: str) -> str:
    """Accept a full URL or an owner/name slug; return 'owner/name'."""
    s = url_or_slug.strip().removesuffix(".git")
    s = re.sub(r"^https?://github\.com/", "", s)
    s = s.strip("/")
    if not _REPO_RE.match(s):
        raise ValueError(f"Not a valid 'owner/name' repo reference: {url_or_slug!r}")
    return s


def _headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = get_settings().github_token
    if token and not token.startswith("ghp_xxxx"):
        h["Authorization"] = f"Bearer {token}"
    return h


def _default_branch(client: httpx.Client, repo: str) -> str:
    r = client.get(f"{_API}/repos/{repo}", headers=_headers())
    r.raise_for_status()
    return r.json().get("default_branch", "main")


def list_source_files(repo: str, *, max_files: int) -> list[str]:
    """Return source-file paths in the repo's default branch (bounded)."""
    with httpx.Client(timeout=30) as client:
        branch = _default_branch(client, repo)
        r = client.get(
            f"{_API}/repos/{repo}/git/trees/{branch}",
            params={"recursive": "1"},
            headers=_headers(),
        )
        r.raise_for_status()
        tree = r.json().get("tree", [])
    files = [n["path"] for n in tree if n.get("type") == "blob" and is_source_file(n["path"])]
    return files[:max_files]


def fetch_file(repo: str, path: str) -> str | None:
    """Fetch a single file's text via the raw endpoint. None on failure/binary."""
    url = f"https://raw.githubusercontent.com/{repo}/HEAD/{path}"
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            r = client.get(url, headers=_headers())
            r.raise_for_status()
            # Skip very large or non-text payloads.
            if len(r.content) > 400_000 or b"\x00" in r.content[:1024]:
                return None
            return r.text
    except httpx.HTTPError:
        return None

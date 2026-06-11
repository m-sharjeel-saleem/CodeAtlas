"""GitHub access — read public repositories.

MVP exposes the surface the agents need (resolve a repo, list source files,
fetch file contents). Implementations call the GitHub REST API with the optional
token for higher rate limits. Wired in the ingest step next.
"""
import re

_REPO_RE = re.compile(r"^[\w.-]+/[\w.-]+$")


def normalize_repo(url_or_slug: str) -> str:
    """Accept a full URL or an owner/name slug; return 'owner/name'.

    Raises ValueError on anything that isn't a plausible public repo reference.
    """
    s = url_or_slug.strip().removesuffix(".git")
    s = re.sub(r"^https?://github\.com/", "", s)
    s = s.strip("/")
    if not _REPO_RE.match(s):
        raise ValueError(f"Not a valid 'owner/name' repo reference: {url_or_slug!r}")
    return s


# TODO: async list_source_files(repo) and fetch_file(repo, path) via the GitHub
# API, respecting MAX_FILES_PER_REPO and skipping binaries / vendored paths.

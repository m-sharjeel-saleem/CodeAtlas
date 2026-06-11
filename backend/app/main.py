"""FastAPI entry point for CodeAtlas."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="CodeAtlas API",
    version=__version__,
    description="Agentic codebase intelligence: ingest, chat, review, and observe.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "version": __version__}

"""FastAPI app factory. F00 exposes only /health (no auth, DB or AI calls)."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from meshvera import __version__
from meshvera.config import Settings, load_settings


class HealthResponse(BaseModel):
    status: str
    version: str
    app_env: str
    llm_mode: str


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings if settings is not None else load_settings()
    app = FastAPI(title="MeshVera API", version=__version__)
    app.state.settings = cfg

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        # Never include secrets or provider keys here.
        return HealthResponse(
            status="ok", version=__version__, app_env=cfg.app_env, llm_mode=cfg.llm_mode
        )

    return app

"""Pharma Cards API – App-Fabrik.

Start lokal:   uvicorn app.main:app --reload   (aus online-platform/backend)
Produktion:    siehe online-platform/README_DEPLOYMENT.md
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings, load_settings
from .db import Base, make_engine, make_sessionmaker
from .routers import cards, downloads, learn, meta, notes, review
from .services import Renderer

log = logging.getLogger("pharma_cards")


def _jwk_resolver(settings: Settings):
    if settings.auth_mode != "oidc":
        return None
    import jwt
    client = jwt.PyJWKClient(settings.oidc_jwks_url, cache_keys=True, lifespan=3600)
    return lambda token: client.get_signing_key_from_jwt(token).key


def create_app(settings: Settings | None = None, *, create_schema: bool = False,
               jwk_resolver=None) -> FastAPI:
    settings = settings or load_settings()
    settings.validate()
    if settings.show_unreviewed:
        log.warning("PHARMA_SHOW_UNREVIEWED aktiv: ungeprüfte Karten sind für ALLE sichtbar "
                    "(nur Entwicklung).")

    app = FastAPI(title="Pharma Cards API", version="0.1.0",
                  description="Online-Lernkartensystem Pharma Cards (Modul PH). "
                              "Ausbildungs- und Lernmaterial – keine Therapieanweisung.")
    engine = make_engine(settings.database_url)
    if create_schema:  # Tests/Entwicklung; Betrieb nutzt Alembic-Migrationen
        Base.metadata.create_all(engine)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)
    app.state.renderer = Renderer(settings)
    app.state.jwk_resolver = jwk_resolver or _jwk_resolver(settings)

    if settings.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                           allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
    for r in (meta.router, cards.router, learn.router, notes.router, review.router, downloads.router):
        app.include_router(r)

    dist = settings.frontend_dist
    if dist and Path(dist).is_dir():  # Einzelprozess-Betrieb (Entwicklung, E2E-Tests)
        app.mount("/_app", StaticFiles(directory=Path(dist) / "_app"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            f = Path(dist) / path
            return FileResponse(f if path and f.is_file() else Path(dist) / "index.html")

    return app


def __getattr__(name: str):  # `uvicorn app.main:app` erzeugt die App erst beim Zugriff
    if name == "app":
        return create_app()
    raise AttributeError(name)

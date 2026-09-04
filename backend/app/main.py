"""FastAPI application entrypoint for MedTimelineAI."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.db.seed import seed_canonical_tests
from app.db.session import get_engine, get_session_factory


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    # Dev-friendly: ensure tables exist for SQLite/local without forcing migrate.
    # PostgreSQL deployments should still run Alembic migrations.
    from app.db.base import Base

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    db = get_session_factory()()
    try:
        seed_canonical_tests(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        description=(
            "MedTimelineAI API — deterministic lab PDF parsing with persistence. "
            "No diagnosis or treatment recommendations."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()

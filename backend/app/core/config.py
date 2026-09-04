"""Application settings for the FastAPI backend."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    app_name: str = "MedTimelineAI"
    api_version: str = "0.3.0"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_bytes: int = 15 * 1024 * 1024  # 15 MiB
    # PostgreSQL example: postgresql+psycopg://user:pass@localhost:5432/medtimeline
    # Default SQLite keeps local/dev usable without a running Postgres.
    database_url: str = "sqlite:///./medtimeline_dev.db"
    storage_dir: str = "./storage/reports"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=_env("MEDTIMELINE_APP_NAME", "MedTimelineAI"),
        api_version=_env("MEDTIMELINE_API_VERSION", "0.3.0"),
        cors_origins=_env(
            "MEDTIMELINE_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ),
        max_upload_bytes=int(
            _env("MEDTIMELINE_MAX_UPLOAD_BYTES", str(15 * 1024 * 1024))
        ),
        database_url=_env(
            "DATABASE_URL",
            _env("MEDTIMELINE_DATABASE_URL", "sqlite:///./medtimeline_dev.db"),
        ),
        storage_dir=_env("MEDTIMELINE_STORAGE_DIR", "./storage/reports"),
    )

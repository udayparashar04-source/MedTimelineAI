from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_session_factory, reset_db_state
from app.main import create_app

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture()
def app_env(tmp_path, monkeypatch):
    """Isolated SQLite DB + local storage for each test (no production DB)."""
    db_file = tmp_path / "test.db"
    storage_dir = tmp_path / "storage"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("MEDTIMELINE_STORAGE_DIR", str(storage_dir))
    get_settings.cache_clear()
    reset_db_state()
    yield {"db_file": db_file, "storage_dir": storage_dir}
    reset_db_state()
    get_settings.cache_clear()


@pytest.fixture()
def client(app_env) -> TestClient:
    application = create_app()
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture()
def db_session(app_env, client) -> Session:
    """DB session bound to the same engine the TestClient app uses."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def patient_id(client: TestClient) -> int:
    response = client.post(
        "/patients",
        json={"display_name": "Fixture Patient", "notes": "test"},
    )
    assert response.status_code == 201
    return response.json()["id"]

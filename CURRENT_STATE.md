# MedTimelineAI — Current State

**As of:** 2026-09-04 (Milestone 3 — PostgreSQL-compatible persistence)

This file describes what **actually exists** in the repository. It does not describe planned features as if they were done.

## Summary

The repo has foundation docs, a deterministic lab PDF parser, a FastAPI API, and **real persistence** for patients, reports, and extracted results (SQLAlchemy 2.x + Alembic). PDF binaries are stored on local disk, not in the database. There is still **no** frontend, auth, OCR, AI, or timeline UI.

## What exists

### Backend — parser (Milestone 1)

Unchanged and independently testable under `backend/app/services/parser/`.

### Backend — FastAPI (Milestone 2)

Health + CORS + upload/parse flow (now persistence-aware).

### Backend — persistence (Milestone 3)

| Path | Role |
|------|------|
| `backend/app/db/` | SQLAlchemy models, session, seed |
| `backend/app/services/patients.py` | Patient CRUD |
| `backend/app/services/reports.py` | Validate → parse → store PDF → persist results |
| `backend/app/services/storage.py` | Local filesystem PDF storage (object-storage swappable) |
| `backend/alembic/` | Migration foundation (`0001_initial`) |
| `backend/.env.example` | DATABASE_URL / storage examples |

**ORM tables:** `patients`, `tests`, `reports`, `extracted_results`

**Report statuses:** `pending`, `processing`, `parsed`, `needs_review`, `needs_ocr`, `failed`

### API endpoints

| Method | Path | Behavior |
|--------|------|----------|
| `GET` | `/health` | Liveness |
| `POST` | `/patients` | Create patient |
| `GET` | `/patients` | List patients |
| `GET` | `/patients/{patient_id}` | Get patient |
| `POST` | `/reports/parse` | Form `patient_id` + PDF file → parse + persist |

### Still deferred

- React frontend
- Authentication
- Object storage (S3/etc.) — local disk only for now
- Timeline / trends UI
- OCR / AI

## How to run locally

From `backend/`:

```bash
python -m pip install -r requirements.txt

# Option A — zero-config SQLite (default DATABASE_URL)
uvicorn app.main:app --reload --app-dir .

# Option B — PostgreSQL
# set DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/medtimeline
alembic upgrade head
uvicorn app.main:app --reload --app-dir .

python -m pytest -q
```

Uploaded PDFs land under `MEDTIMELINE_STORAGE_DIR` (default `./storage/reports`).

API docs: `http://127.0.0.1:8000/docs`

## Test strategy

Tests use an **isolated temporary SQLite database per test** plus a temp storage directory. They do **not** require your production PostgreSQL instance.

**Last run:** 41 passed.

## Dependencies

- Runtime: `pypdf`, `fastapi`, `uvicorn`, `python-multipart`, `sqlalchemy`, `psycopg`, `alembic`
- Dev/test: `pytest`, `httpx`

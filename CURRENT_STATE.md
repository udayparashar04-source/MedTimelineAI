# MedTimelineAI — Current State

**As of:** 2026-09-04 (Milestone 2 — FastAPI backend foundation)

This file describes what **actually exists** in the repository. It does not describe planned features as if they were done.

## Summary

The repo has foundation docs, a **deterministic lab PDF parser**, and a **FastAPI API** that accepts PDF uploads and returns parser JSON. There is still **no** frontend, database, auth, OCR, or AI extraction.

## What exists

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Title only: `# MedTimelineAI` |
| `PROJECT_SPEC.md` | Product goals and constraints |
| `ARCHITECTURE.md` | Target system shape |
| `CURRENT_STATE.md` | This inventory |
| `TASKS.md` | Milestone plan |

### Backend — parser (Milestone 1)

| Path | Role |
|------|------|
| `backend/app/services/parser/` | Framework-independent deterministic parser |
| `backend/tests/fixtures/` | PDF fixtures |
| Parser tests | Still independently runnable |

### Backend — FastAPI (Milestone 2)

| Path | Role |
|------|------|
| `backend/app/main.py` | FastAPI app factory + CORS |
| `backend/app/core/config.py` | Settings (CORS origins, upload size) |
| `backend/app/api/` | Routers (`/health`, `/reports/parse`) |
| `backend/app/models/schemas.py` | Pydantic response schemas |
| `backend/app/services/reports.py` | Upload validation + parser orchestration |

**API endpoints:**

| Method | Path | Behavior |
|--------|------|----------|
| `GET` | `/health` | Liveness JSON |
| `POST` | `/reports/parse` | Multipart PDF upload → `ParsedReport` JSON |

**API rules in force:**

- PDF validation (extension/content-type + `%PDF` magic)
- Existing parser invoked via `parse_pdf_bytes` (values not altered)
- Missing tests omitted from `results` (never filled with `0`)
- CORS enabled for local Vite origins (`http://localhost:5173`, `http://127.0.0.1:5173`)

### Still empty / deferred

- `frontend/` — reserved only
- `backend/app/db/` — reserved only
- No authentication
- No PostgreSQL
- No timeline UI
- No OCR / AI

## How to run

From `backend/`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload --app-dir .
```

API docs (when server is running): `http://127.0.0.1:8000/docs`

## Test status

**Last run:** 33 passed (26 parser + 7 API), 2 dependency deprecation warnings unrelated to app logic.

## Dependencies

- Runtime: `pypdf`, `fastapi`, `uvicorn`, `python-multipart`
- Dev/test: `pytest`, `httpx`

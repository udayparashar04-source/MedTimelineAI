# MedTimelineAI — Current State

**As of:** 2026-09-04 (Milestone 1 — deterministic PDF parser core)

This file describes what **actually exists** in the repository. It does not describe planned features as if they were done.

## Summary

The repo has foundation docs plus a **working, tested deterministic lab PDF parser** under `backend/app/services/parser/`. There is still **no** FastAPI app, frontend, database, OCR, or AI extraction.

## What exists

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Title only: `# MedTimelineAI` |
| `PROJECT_SPEC.md` | Product goals and constraints |
| `ARCHITECTURE.md` | Target system shape |
| `CURRENT_STATE.md` | This inventory |
| `TASKS.md` | Milestone plan |

### Backend — parser (implemented)

| Path | Role |
|------|------|
| `backend/pyproject.toml` | Package metadata, pytest config, `pypdf` dependency |
| `backend/requirements.txt` | `pypdf`, `pytest` |
| `backend/app/services/parser/` | Framework-independent parser package |
| `backend/tests/` | Pytest suite + PDF fixtures |

**Parser capabilities (verified by tests):**

- Digital PDF text extraction via **pypdf** (no OCR)
- Report/collection **date detection**
- Maintainable **alias → canonical test name** catalog
- Extraction of **value + unit** with source page/line metadata
- Missing tests **omitted** (never fabricated as `0`)
- Public API: `parse_pdf`, `parse_pdf_bytes`, `parse_text_pages` → `ParsedReport`
- Parser version stamp: `PARSER_VERSION` (`0.1.0`)

### Directory scaffold (still empty placeholders)

- `frontend/` — reserved only
- `backend/app/api/`, `core/`, `models/`, `db/` — reserved only (`.gitkeep`)

## Explicitly not done yet

- FastAPI / HTTP API
- React + Vite frontend
- PostgreSQL
- Upload orchestration
- Timeline aggregation / UI
- Authentication
- OCR
- AI extraction
- Deployment

## How to run parser tests

From `backend/`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

**Last test run:** 26 passed.

## Dependencies present

- Runtime: `pypdf`
- Dev/test: `pytest`

No Node packages, no FastAPI, no database drivers.

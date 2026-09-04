# MedTimelineAI — Tasks (Milestone Plan)

---

## Milestone 0 — Foundation

**Status:** Complete

- [x] Inspect existing repository contents
- [x] Write `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `CURRENT_STATE.md`, `TASKS.md`
- [x] Reserve `frontend/` and `backend/` directory structure

---

## Milestone 1 — Deterministic PDF parser core

**Status:** Complete (2026-09-04)

- [x] Deterministic parser + fixtures + pytest (26 parser tests)

---

## Milestone 2 — FastAPI backend foundation (+ parser integration)

**Status:** Complete (2026-09-04)

- [x] FastAPI app, `/health`, `/reports/parse`, CORS, API tests

---

## Milestone 3 — PostgreSQL-compatible persistence

**Status:** Complete (2026-09-04)

**Goal:** Persist patients, reports, and extracted results in a real DB; store PDF files outside the database.

- [x] SQLAlchemy 2.x + `DATABASE_URL` configuration
- [x] Models: `patients`, `reports`, `extracted_results`, `tests`
- [x] Report status enum values: pending/processing/parsed/needs_review/needs_ocr/failed
- [x] Alembic migration foundation (`0001_initial`)
- [x] Patient API: create / list / get
- [x] `POST /reports/parse` requires `patient_id`, persists report + results
- [x] Local filesystem PDF storage (not in PostgreSQL)
- [x] Validation + transaction rollback on failure
- [x] Isolated SQLite test DB (no production DB required)
- [x] Full suite green (41 passed)

**Exit criteria:** Reports and extracted results survive via DB; PDFs on disk; tests pass. **Met.**

---

## Milestone 4 — Frontend skeleton (React + Vite)

**Goal:** Empty but real UI shell that can talk to the API.

- [ ] Scaffold React + Vite in `frontend/`
- [ ] Basic app shell / routing placeholder (no fake medical tables)
- [ ] Env-based API base URL
- [ ] Confirm local dev server starts

**Exit criteria:** Vite dev server loads a minimal branded shell; no mock lab grids.

---

## Milestone 5 — Domain contracts & retrieval APIs

**Goal:** Extend read APIs for stored reports/results.

- [ ] List/get reports for a patient
- [ ] Keep missing values absent—**never** default to `0`
- [ ] Document JSON examples for missing vs present values

**Exit criteria:** Clients can reload persisted parse data without re-uploading.

---

## Milestone 6 — Object storage readiness & hardening of uploads

**Goal:** Keep storage swappable and safer.

- [ ] Tighten file handling / retention
- [ ] Optional S3-compatible backend behind the storage interface

---

## Milestone 7 — Chronological timeline API

**Goal:** Backend aggregation for the product’s core view.

- [ ] Order observations by date across reports
- [ ] Align tests across dates; missing slots remain null/`"—"`-ready
- [ ] Include source metadata in responses

---

## Milestone 8 — Timeline UI (polished, useful)

**Goal:** Modern frontend for the chronological view—not a bare spreadsheet.

- [ ] Upload flow wired to backend
- [ ] Chronological visualization with `"—"` for missing values
- [ ] Source report/page inspection

---

## Milestone 9 — Hardening

- [ ] Logging/observability, README runbook, regression expansion

---

## Explicitly deferred (post-MVP)

- OCR for scanned PDFs
- AI / LLM extraction
- Diagnosis or treatment recommendations
- Multi-tenant auth (until core loop works)
- Fake demo patient datasets

---

## Working agreement

1. Implement **one milestone at a time** when explicitly requested.
2. Do not invent medical data or mock clinical features to look complete.
3. Prefer small, testable PRs over large speculative builds.
4. After each milestone, refresh `CURRENT_STATE.md`.

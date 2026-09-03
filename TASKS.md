# MedTimelineAI — Tasks (Milestone Plan)

Implementation of these milestones has **not** started. This file is the ordered plan only.

---

## Milestone 0 — Foundation (this pass)

**Status:** Documentation + empty architecture folders only.

- [x] Inspect existing repository contents
- [x] Write `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `CURRENT_STATE.md`, `TASKS.md`
- [x] Reserve `frontend/` and `backend/` directory structure
- [ ] *(Stop here until the next milestone is explicitly started)*

---

## Milestone 1 — Backend skeleton (FastAPI)

**Goal:** Runnable API shell with health check; no parser yet.

- [ ] Create Python project layout under `backend/` (`pyproject.toml` or `requirements.txt`)
- [ ] Add FastAPI app entrypoint and `GET /health`
- [ ] Add minimal config module under `backend/app/core/`
- [ ] Document how to run the API locally
- [ ] Add a smoke test for `/health`

**Exit criteria:** `uvicorn` (or equivalent) serves `/health` successfully.

---

## Milestone 2 — Frontend skeleton (React + Vite)

**Goal:** Empty but real UI shell that can talk to the API later.

- [ ] Scaffold React + Vite in `frontend/`
- [ ] Basic app shell / routing placeholder (no fake medical tables)
- [ ] Env-based API base URL
- [ ] Confirm local dev server starts

**Exit criteria:** Vite dev server loads a minimal branded shell; no mock lab grids.

---

## Milestone 3 — Domain models & missingness rules

**Goal:** Shared contracts that encode product rules before parsing.

- [ ] Define report / observation / timeline types (Pydantic or equivalent)
- [ ] Encode missing values as `null`/absent—**never** default to `0`
- [ ] Include fields for `source_report_id` and `source_page` on observations
- [ ] Document JSON examples for missing vs present values

**Exit criteria:** Models + unit tests proving missing ≠ `0`.

---

## Milestone 4 — Deterministic PDF text extraction (no OCR, no AI)

**Goal:** Reliable text pull from digital PDFs only.

- [ ] Choose and pin a PDF text-extraction library
- [ ] Implement page-aware text extraction API inside `services/parser/`
- [ ] Fixture folder for fixed PDFs/text snapshots (`backend/tests/fixtures/`)
- [ ] Tests: same file → same page text

**Exit criteria:** Deterministic text extraction with failing tests for regressions.

---

## Milestone 5 — Deterministic lab result parser

**Goal:** Map PDF text to structured tests without LLMs.

- [ ] Rule/structure-based parsing of test name, value, unit, date
- [ ] Explicit missing/unparsed handling (sentinel compatible with `"—"` in UI)
- [ ] Attach page (and later report id) to each extracted value
- [ ] Parser version stamp on output
- [ ] Comprehensive fixture-based tests

**Exit criteria:** Known fixtures parse stably; absent tests never become `0`.

---

## Milestone 6 — Upload & parse orchestration

**Goal:** End-to-end “file in → structured results out” without DB permanence yet (or with local file store).

- [ ] `POST` upload endpoint accepting PDF
- [ ] Store file on disk (or object store abstraction)
- [ ] Run parser pipeline; return structured JSON
- [ ] Error paths for non-PDF / non-text PDFs (clear messages; no silent OCR)

**Exit criteria:** Upload a text-layer PDF and receive deterministic structured JSON.

---

## Milestone 7 — PostgreSQL persistence

**Goal:** Durable reports and observations.

- [ ] Add PostgreSQL connection + migrations
- [ ] Tables for reports, parse runs, observations (NULL for missing—not `0`)
- [ ] Persist source report + page per observation
- [ ] Query endpoints for reports and timeline aggregation

**Exit criteria:** Restart API; previously parsed data still available.

---

## Milestone 8 — Chronological timeline API

**Goal:** Backend aggregation for the product’s core view.

- [ ] Order observations by date across reports
- [ ] Align tests across dates; missing slots remain null/`"—"`-ready
- [ ] Include source metadata in responses

**Exit criteria:** `GET /timeline` (or equivalent) returns chronologically correct, gap-safe data.

---

## Milestone 9 — Timeline UI (polished, useful)

**Goal:** Modern frontend for the chronological view—not a bare spreadsheet.

- [ ] Upload flow wired to backend
- [ ] Chronological visualization / comparison with clear hierarchy
- [ ] Missing values rendered as `"—"`
- [ ] Source report/page inspection for a selected value
- [ ] Responsive layout; no clinical advice copy

**Exit criteria:** Real upload → parse → readable timeline with traceability.

---

## Milestone 10 — Hardening

**Goal:** Production-minded quality without scope creep into AI/OCR.

- [ ] Parser regression suite expansion
- [ ] API validation and safer file handling
- [ ] Basic logging/observability
- [ ] README with accurate run instructions
- [ ] Update `CURRENT_STATE.md` to match reality

**Exit criteria:** Documented local run path; tests green; state docs accurate.

---

## Explicitly deferred (post-MVP)

Do **not** schedule into early milestones:

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

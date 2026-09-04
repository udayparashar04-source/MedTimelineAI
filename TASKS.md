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

**Goal:** Framework-independent, testable parser for digital lab PDFs (no AI, no OCR, no API/UI).

- [x] Create Python package layout under `backend/` with minimal deps (`pypdf`, `pytest`)
- [x] Implement page-aware PDF text extraction (`pypdf`)
- [x] Detect report/collection date
- [x] Maintainable alias catalog → canonical test names
- [x] Extract numeric/text values and units without inventing data
- [x] Omit missing tests (never coerce to `0`)
- [x] Preserve source page / line metadata + confidence/method fields
- [x] Public callables: `parse_pdf`, `parse_pdf_bytes`, `parse_text_pages`
- [x] Pytest coverage: success, dates, aliases, missingness, malformed/empty, units, multi-test
- [x] Small PDF fixtures under `backend/tests/fixtures/`

**Exit criteria:** Pytest green; parser callable from Python; missing ≠ 0. **Met (26 passed).**

---

## Milestone 2 — Backend skeleton (FastAPI)

**Goal:** Runnable API shell with health check; wire parser later.

- [ ] Add FastAPI app entrypoint and `GET /health`
- [ ] Minimal config under `backend/app/core/`
- [ ] Document how to run the API locally
- [ ] Smoke test for `/health`

**Exit criteria:** `uvicorn` (or equivalent) serves `/health` successfully.

---

## Milestone 3 — Frontend skeleton (React + Vite)

**Goal:** Empty but real UI shell that can talk to the API later.

- [ ] Scaffold React + Vite in `frontend/`
- [ ] Basic app shell / routing placeholder (no fake medical tables)
- [ ] Env-based API base URL
- [ ] Confirm local dev server starts

**Exit criteria:** Vite dev server loads a minimal branded shell; no mock lab grids.

---

## Milestone 4 — Domain models & API contracts

**Goal:** Shared contracts that encode product rules for the API layer.

- [ ] Align API schemas with `ParsedReport` / `ExtractedResult`
- [ ] Encode missing values as `null`/absent—**never** default to `0`
- [ ] Include `source_report_id` (when available) alongside page/line
- [ ] Document JSON examples for missing vs present values

**Exit criteria:** Models + tests proving missing ≠ `0` at the API boundary.

---

## Milestone 5 — Upload & parse orchestration

**Goal:** End-to-end “file in → structured results out” without DB permanence yet.

- [ ] `POST` upload endpoint accepting PDF
- [ ] Store file on disk (or object store abstraction)
- [ ] Run parser pipeline; return structured JSON
- [ ] Error paths for non-PDF / non-text PDFs (clear messages; no silent OCR)

**Exit criteria:** Upload a text-layer PDF and receive deterministic structured JSON.

---

## Milestone 6 — PostgreSQL persistence

**Goal:** Durable reports and observations.

- [ ] Add PostgreSQL connection + migrations
- [ ] Tables for reports, parse runs, observations (NULL for missing—not `0`)
- [ ] Persist source report + page per observation
- [ ] Query endpoints for reports and timeline aggregation

**Exit criteria:** Restart API; previously parsed data still available.

---

## Milestone 7 — Chronological timeline API

**Goal:** Backend aggregation for the product’s core view.

- [ ] Order observations by date across reports
- [ ] Align tests across dates; missing slots remain null/`"—"`-ready
- [ ] Include source metadata in responses

**Exit criteria:** `GET /timeline` (or equivalent) returns chronologically correct, gap-safe data.

---

## Milestone 8 — Timeline UI (polished, useful)

**Goal:** Modern frontend for the chronological view—not a bare spreadsheet.

- [ ] Upload flow wired to backend
- [ ] Chronological visualization / comparison with clear hierarchy
- [ ] Missing values rendered as `"—"`
- [ ] Source report/page inspection for a selected value
- [ ] Responsive layout; no clinical advice copy

**Exit criteria:** Real upload → parse → readable timeline with traceability.

---

## Milestone 9 — Hardening

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

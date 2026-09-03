# MedTimelineAI — Project Specification

## Product purpose

MedTimelineAI organizes medical and lab PDF reports into a clear chronological timeline. Users upload reports; the system extracts structured lab results and presents them so trends over time are easy to understand—without becoming a clinical decision tool.

## Core value

- Turn scattered PDF lab reports into a **chronological, comparable view** of tests.
- Extract **test names, values, units, and dates** reliably.
- Preserve **traceability**: every value should eventually point back to its source report and page.
- Keep the experience **modern, polished, and useful**—not a raw spreadsheet dump.

## In scope (product)

1. Upload and store medical/lab PDF reports.
2. Deterministic parsing of digital (text-extractable) PDFs into structured results.
3. Chronological organization of results across reports.
4. Display of extracted fields: test name, value, unit, date.
5. Explicit handling of missing tests as `"—"` (never coerced to `0` or invented numbers).
6. Source attribution path: report identity + page reference for each extracted value (foundation now; full UI later).
7. A frontend experience focused on clarity, timeline navigation, and trustworthy presentation of data.

## Out of scope (initial / MVP constraints)

| Constraint | Rule |
|------------|------|
| AI extraction | **Not** part of the initial parser. Parsing must be deterministic and rule/structure-based. |
| OCR | **Not** part of the initial MVP. Only text-layer PDFs are targeted first. |
| Clinical advice | **No** diagnosis, treatment recommendations, or interpretive medical guidance. |
| Fake data | No fabricated patient or lab datasets for demos. |
| Premature features | No mock product surfaces built only to look complete. |

## Non-negotiable data rules

1. **Missing ≠ zero.** If a test is absent from a report (or cannot be extracted), the UI and stored representation must use `"—"` (or an explicit null/missing sentinel)—**never** `0`.
2. **Determinism.** The same PDF input must always yield the same structured output under the same parser version.
3. **Testability.** Parser behavior must be covered by automated tests with fixed fixtures (real anonymized samples when available; no invented clinical narratives).
4. **Traceability.** Design storage and APIs so each extracted value can retain `source_report_id` and `source_page` (or equivalent).
5. **No clinical claims.** Copy and UI must not imply diagnosis or treatment.

## Primary user journey (eventual)

1. User uploads one or more lab/medical PDFs.
2. Backend stores the file and runs the deterministic parser.
3. Extracted results are normalized into a chronological model.
4. UI shows a timeline / comparison view with missing cells as `"—"`.
5. User can inspect a value and see which report/page it came from.

## Technical product boundaries

| Layer | Choice | Notes |
|-------|--------|--------|
| Frontend | React + Vite | Modern UI; timeline-first presentation. |
| Backend | FastAPI | Upload, parse orchestration, APIs. |
| Database | PostgreSQL (later) | Persist reports, extractions, timeline entities. |
| Parser | Deterministic PDF text parser | No LLM/OCR in MVP parser path. |

## Success criteria for the product direction

- Users can trust that numbers on screen came from their PDFs without silent fabrication.
- Gaps in testing history remain visibly empty (`"—"`), not misleading zeros.
- Architecture allows adding OCR or AI-assisted paths later **without** replacing the deterministic parser as the default trustworthy path.
- The UI feels like a focused medical timeline tool, not a spreadsheet pasted into a webpage.

## Documentation map

| File | Role |
|------|------|
| `PROJECT_SPEC.md` | Product goals and constraints (this file). |
| `ARCHITECTURE.md` | System shape, folders, and component boundaries. |
| `CURRENT_STATE.md` | What actually exists in the repo today. |
| `TASKS.md` | Milestone plan—implementation deferred. |

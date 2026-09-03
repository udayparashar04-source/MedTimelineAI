# MedTimelineAI — Architecture

## Goals of this architecture

- Separate **frontend**, **backend**, and **parser** concerns cleanly.
- Keep the PDF parser **deterministic, isolated, and testable**.
- Leave a clear place for **PostgreSQL** without requiring it on day one.
- Avoid premature frameworks, mock features, or dependency sprawl.

## High-level system shape

```
┌─────────────────┐         HTTP/JSON          ┌──────────────────────────┐
│  React + Vite   │ ◄────────────────────────► │  FastAPI backend         │
│  frontend/      │                            │  backend/app             │
└─────────────────┘                            │    ├─ api/               │
                                               │    ├─ services/parser/   │
                                               │    ├─ models/            │
                                               │    └─ db/ (later)        │
                                               └────────────┬─────────────┘
                                                            │
                                                            ▼
                                                   ┌────────────────┐
                                                   │  PostgreSQL    │
                                                   │  (planned)     │
                                                   └────────────────┘
```

## Repository layout (foundation)

```
MedTimelineAI/
├── README.md                 # Repo title (existing)
├── PROJECT_SPEC.md           # Product specification
├── ARCHITECTURE.md           # This file
├── CURRENT_STATE.md          # Accurate inventory of the repo
├── TASKS.md                  # Milestone plan (not yet implemented)
├── frontend/                 # React + Vite app (to be scaffolded in a later milestone)
└── backend/
    ├── app/                  # FastAPI application package
    │   ├── api/              # Route handlers / routers
    │   ├── core/             # Config, shared settings
    │   ├── models/           # Domain / schema types
    │   ├── services/
    │   │   └── parser/       # Deterministic PDF parser (no AI, no OCR in MVP)
    │   └── db/               # Persistence layer (PostgreSQL later)
    └── tests/                # Backend + parser tests
        └── fixtures/         # Fixed PDF/text fixtures for parser tests
```

Empty directories are reserved with `.gitkeep` so Git tracks the intended structure without shipping application code yet.

## Component responsibilities

### Frontend (`frontend/`)

- React + Vite SPA.
- Upload UX, chronological timeline / comparison views, source drill-down.
- Must render missing values as `"—"`, never as `0`.
- Talks only to backend HTTP APIs; no direct PDF parsing in the browser for the MVP path.

### Backend (`backend/app/`)

- FastAPI service: health, uploads, parse jobs, result queries (introduced by milestone).
- Orchestrates storage + parser; does not embed UI logic.
- Exposes clear JSON contracts that preserve missingness and source metadata.

### Deterministic parser (`backend/app/services/parser/`)

| Requirement | Implication |
|-------------|-------------|
| Deterministic | Pure, versioned rules over PDF text extraction; same input → same output. |
| Testable | Unit/integration tests with fixtures under `backend/tests/`. |
| No AI in MVP | No LLM calls in the default extraction path. |
| No OCR in MVP | Relies on existing PDF text layer only. |
| Traceability | Output includes (or can attach) report id + page for each value. |
| Missingness | Absent tests stay missing/`"—"`-compatible; never default numeric `0`. |

### Database (`backend/app/db/` + PostgreSQL later)

- Planned persistence for reports, parse results, and timeline entities.
- Schema design should treat missing lab values as NULL/absent, not `0`.
- Not required to run locally until a dedicated persistence milestone.

## Data principles (cross-cutting)

1. **Missing sentinel:** API and UI agree that missing = `null` / omitted / `"—"` display—not `0`.
2. **Source lineage:** `report_id` + `page` (minimum) travel with extracted values.
3. **Parser versioning:** Store parser version with results so re-parses are auditable.
4. **No clinical logic:** Backend must not emit diagnoses or treatment advice.

## Suggested API surface (planned, not implemented)

Illustrative only—actual routes land in later milestones:

- `POST /reports` — upload PDF
- `GET /reports` — list reports
- `GET /reports/{id}` — report metadata + parse status
- `GET /timeline` — chronological aggregated results
- `GET /health` — liveness

## Technology decisions

| Concern | Decision | Deferred |
|---------|----------|----------|
| UI | React + Vite | Component library, auth UI |
| API | FastAPI | Auth, rate limits |
| DB | PostgreSQL | Migrations, hosting |
| PDF text | Deterministic library choice in parser milestone | OCR, AI extraction |
| Auth | TBD | After core parse + timeline loop works |

## What this foundation deliberately does not include

- Installed Node/Python dependency trees
- Running app servers
- Database migrations or connection strings
- Sample patient/lab data
- Mock UI screens or stub “AI” endpoints

Those arrive only when the corresponding milestone in `TASKS.md` is executed.

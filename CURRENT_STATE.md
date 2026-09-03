# MedTimelineAI — Current State

**As of:** 2026-09-03 (foundation documentation pass)

This file describes what **actually exists** in the repository. It does not describe planned features as if they were done.

## Inspection findings (before foundation work)

| Item | Reality |
|------|---------|
| Git | Initialized; branch `main`; tracks `origin/main` |
| History | Single commit: `619f0c1` — “Initial commit” |
| Application code | **None** |
| Frontend | **Not present** |
| Backend | **Not present** |
| Database config | **Not present** |
| Parser | **Not present** |
| Dependencies | **None** (no `package.json`, `requirements.txt`, lockfiles, or virtualenvs) |
| Tests | **None** |
| CI | **None** |

### Files present on inspection

Only tracked project content:

- `README.md` — single line: `# MedTimelineAI`

No other project source or config files existed outside `.git/`.

## What exists after this foundation pass

### Documentation (created)

| File | Purpose |
|------|---------|
| `PROJECT_SPEC.md` | Product goals, constraints, non-negotiable data rules |
| `ARCHITECTURE.md` | Target system shape and folder responsibilities |
| `CURRENT_STATE.md` | This inventory |
| `TASKS.md` | Milestone plan (not implemented) |

### Directory scaffold (created, empty)

Intended layout only—**no application implementation**:

```
frontend/
backend/app/api/
backend/app/core/
backend/app/models/
backend/app/services/parser/
backend/app/db/
backend/tests/fixtures/
```

Each reserved directory contains a `.gitkeep` so the structure is tracked by Git.

### Unchanged

- `README.md` — still `# MedTimelineAI` only (not expanded in this pass)

## Explicitly not done yet

- React + Vite scaffolding
- FastAPI app entrypoint
- PDF parser implementation
- PostgreSQL schema or connection
- API routes
- UI screens
- Dependency installation
- Sample/fake medical data
- OCR or AI extraction

## Health check notes

Safe checks for this stage:

- Repository is a valid Git working tree.
- Documentation files are present and readable at the repo root.
- Scaffold directories exist as listed above.

There is nothing to build, lint, or test as an application until later milestones add real code.

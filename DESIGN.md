# DESIGN.md

Design decisions and rationale for the Activity Tracker + Weekly Review Dashboard.

## Problem Statement

The user performs several kinds of activities daily (coding, reading, language learning,
exercise) and wants to know, at the end of each week, how much time went into each and how
that compares to previous weeks. Doing this with a paper notebook is slow and manual. This
app's goal is to make logging fast and make the weekly analysis fully automatic.

## Goals

1. **Product goal:** a tool the user actually uses daily, that makes weekly review faster
   and more accurate than the paper notebook it replaces.
2. **Learning goal:** learn new tools (Django, DRF, and backend concepts in general) while
   building, not just apply existing knowledge. (TypeScript and Tailwind were originally part
   of this goal but were dropped — see "Frontend Decision" below.)
3. **Branding goal:** document the build process (including real challenges, not just
   successes) and publish regularly on LinkedIn; keep the code on GitHub as a portfolio piece.
4. **Long-term vision:** possible future multi-user product (not a current priority — it
   only informed the choice of PostgreSQL over SQLite for eventual deployment).

## Scope (MVP)

### Must Have
- Quick activity logging: pick a category + enter duration (minutes)
- Category management: default categories (Programming, Reading, Language Learning) +
  user-defined custom categories
- Daily view: list of entries logged that day
- Weekly dashboard: total time per category this week, compared to previous weeks
- Quick-add buttons for repeated activities (e.g. "+25 min Programming")
- Streak counter: consecutive days with an entry in a given category
- Optional short note field per entry

### Should/Could Have (next phase)
- Search entry history
- Multi-week trend chart
- Data export
- Per-category weekly goals with progress bar

### Won't Have (out of scope for now)
- AI-generated insights
- Multi-user / social features
- Live start/stop timer (entries are logged manually, after the fact)

## Data Model

### Category
| Field | Type | Notes |
|---|---|---|
| id | auto | primary key |
| name | string | **unique ignoring case** — prevents duplicate categories like "Gym" vs "gym" vs "gYm" (database constraint on `Lower('name')`, plus a check in the serializer) |
| is_default | boolean | distinguishes system-provided defaults from user-created categories |

### Entry
| Field | Type | Notes |
|---|---|---|
| id | auto | primary key |
| date | date | day of week is *computed* from this, never stored separately |
| category | foreign key → Category | `on_delete=PROTECT` (see rationale below) |
| duration | positive integer | minutes, validated to be between 1 and 1440 |
| note | text, optional | short context, not a journal field |

**Why a separate `Category` table instead of a plain text field on `Entry`?**
A plain text field risks data inconsistency — "Programming", "programming", and "Progaming"
would be counted as three different categories, silently breaking any aggregation (e.g. the
weekly dashboard's "total time per category"). A foreign key to a dedicated table guarantees
each category is stored exactly once. The original project spec's suggested `Categories`
model (with `isDefault`) already implied this design.

The remaining risk — a user typing a near-duplicate custom category (e.g. "Ready to
Interview" vs "Ready to Interview Part 2") — is treated as a **frontend/UX problem**, not a
database problem: solved with an autocomplete/combobox in the entry form that surfaces
existing categories as the user types, backed by the database's `unique` constraint as a
safety net.

**Why `on_delete=models.PROTECT` on `Entry.category`?**
Considered three options:
- `CASCADE` — deleting a category would silently delete every entry logged under it. Too
  risky for an app whose entire value is historical time-tracking data.
- `SET_NULL` — entries would survive deletion but lose their category, making them
  meaningless for the app's core purpose.
- `PROTECT` (chosen) — deleting a category that still has entries raises an error, forcing
  a deliberate decision (reassign or delete the entries first) instead of silent data loss.

## API Design

Built with Django REST Framework. Manual `APIView` classes were used deliberately (instead of
DRF's generic `ListCreateAPIView` etc.) so that each step — reading the DB, serializing,
validating, responding — is explicit and understood, not hidden behind framework defaults.

### Layering (and build order)

Within a feature, the pieces were built in **dependency order**, not request-flow order:

```
Serializer (depends on nothing but the model)
    ↓
View (depends on the Serializer)
    ↓
Router (depends on the View)
```

At request time, the flow runs the other direction: Router → View → Serializer → DB.

### Serializers
`ModelSerializer` is used (not the base `Serializer`) so fields stay in sync with the model
automatically. `fields` is always listed explicitly, never `'__all__'`, so new model fields
don't leak into API responses without a deliberate decision.

### Endpoints

| Method | URL | Behavior |
|---|---|---|
| GET | `/api/categories/` | List all categories, sorted by name |
| POST | `/api/categories/` | Create a category (name must be unique ignoring case) |
| GET | `/api/entries/` | List entries, newest first. Optional filters: `?date=`, `?from=`, `?to=` (YYYY-MM-DD, range is inclusive) and `?category=<id>`; invalid values return 400 |
| POST | `/api/entries/` | Create a new entry (validates via `EntrySerializer`) |
| GET | `/api/entries/<id>/` | Read a single entry (404 if missing) |
| PATCH | `/api/entries/<id>/` | Partially update an entry |
| DELETE | `/api/entries/<id>/` | Delete an entry (204 on success) |

Status codes follow REST convention deliberately (`200` for successful reads, `201` for
successful creation, `204` for successful deletion, `400` for invalid input, `404` for a
missing entry) so the frontend can branch on status rather than guessing from response content.

Validation: `duration` must be between 1 and 1440 minutes. Category names are unique ignoring
case; this is enforced by a database constraint (`Lower('name')`) and also checked in
`CategorySerializer`, because DRF does not enforce expression-based constraints itself and
would otherwise turn a duplicate into a 500 error instead of a clean 400.

Not yet built:
- A weekly summary endpoint (or equivalent) for the dashboard. The start of the week
  (e.g. Saturday vs Monday) needs to be decided first, since the totals depend on it.

Current limitation: the data model has no `user` field and the API has no authentication,
so all data is global. This is fine for single-user local development, but per-user data
ownership and authentication must be added before real outside users or a public deployment.

## Database Choice: SQLite now, PostgreSQL later

The original spec called for PostgreSQL (for the eventual multi-user vision and easier
deployment). SQLite is used for local development for now, following **YAGNI** — Postgres
requires a running server process with no benefit during early single-developer local
development. Because Django's ORM abstracts the database engine, switching to PostgreSQL
later is a small change in `settings.py`, not a rewrite.

Before any deployment, the settings also need to move from development defaults to
production-safe ones: `SECRET_KEY` read from an environment variable (not committed in the
repo), `DEBUG=False`, and a real `ALLOWED_HOSTS` instead of `["*"]`.

## Frontend Decision: Plain JavaScript React (Vite)

The original plan was React + TypeScript + Tailwind CSS v4, and an initial scaffold was
created that way. It was later replaced with a new frontend built from scratch using Vite +
React 19 in plain JavaScript, with plain CSS for styling. (Rationale for the change: not
recorded yet — add it here.)

The first frontend slice is built against what the backend already provides: the
`/api/entries/` endpoint (plus `/api/categories/` once added), following the vertical-slice
approach described below. It connects to the backend through an API base URL (env variable
or Vite dev proxy); the backend already allows CORS from `http://localhost:5173`.

## Build Strategy: Vertical Slices over Horizontal Layers

Two approaches were considered for build order:

- **Horizontal (layered):** finish the entire database layer, then the entire API layer,
  then the entire frontend. Risk: integration problems between layers aren't discovered
  until the very end, when they're expensive to fix.
- **Vertical (slice-based) — chosen:** build one feature end-to-end (DB → API → frontend)
  before starting the next. Surfaces integration issues early, and produces a working
  (if minimal) product sooner.

Vertical slices were chosen because Django/DRF were new to the developer — an early,
working end-to-end path was considered more valuable than a fully-designed but untested
backend.

This is distinct from **API-first / contract-first** design (agree on an API contract, then
build frontend and backend in parallel against mocks/the contract). That approach is valuable
mainly when separate frontend/backend teams need to work in parallel — not the case here,
since one person is building both.

## Git Workflow Notes

- Commit messages: full descriptive sentences, not Conventional Commits prefixes
  (`feat:`/`fix:`/etc.) — per explicit project preference.
- `db.sqlite3`, `venv/`, and `node_modules/` are gitignored — regenerated locally via
  `migrate` / `pip install` / `npm install`, never committed.

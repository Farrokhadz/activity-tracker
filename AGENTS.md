# AGENTS.md

Guidance for AI coding agents (and human contributors) working in this repository.

## Project Overview

Activity Tracker + Weekly Review Dashboard — a personal web app for quickly logging daily
activities (coding, reading, language learning, exercise, etc.) and automatically generating
a weekly review. It replaces a paper notebook the user previously used for weekly journaling.

This is a **structured quantified-self tracker**, not a free-form journal. Entries are
category + duration, with an optional short note — not long-form text.

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React 19 + plain JavaScript (Vite) | Rebuilt from scratch; the earlier TypeScript + Tailwind scaffold was replaced by a plain JS React app |
| Backend | Django + Django REST Framework (DRF) | Python is prior skill; Django/DRF is a learning goal |
| Database | SQLite (local dev) → PostgreSQL (production) | SQLite chosen for now per YAGNI; swap is a one-line settings change since we use Django's ORM |
| Frontend deploy | Vercel | Not yet configured |
| Backend deploy | Railway or Render | Not yet configured |

## Repository Structure

```
activity-tracker/
├── backend/
│   ├── config/          # Django project: settings, root urls
│   ├── tracker/         # Django app: models, serializers, views, app-level urls
│   └── manage.py
├── frontend/             # React (plain JavaScript) app, Vite
│   └── src/              # App.jsx, main.jsx, App.css, index.css
├── AGENTS.md
└── DESIGN.md
```

## Setup & Run

### Backend

```bash
cd backend
python3 -m venv venv
# Windows: venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate
pip install django djangorestframework django-cors-headers
python manage.py migrate
python manage.py runserver
```

API base URL in development: `http://127.0.0.1:8000/api/`

CORS: `django-cors-headers` is installed in `settings.py` and allows
`http://localhost:5173` (the Vite dev server).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dev server: `http://localhost:5173`

## Development Approach

This project is being built **incrementally, as a learning exercise**, using two guiding
principles — see `DESIGN.md` for full rationale:

1. **Vertical slices over horizontal layers.** Build one thin end-to-end feature (DB → API →
   frontend) at a time rather than completing an entire layer before moving to the next.
2. **Dependency-driven build order.** Within any layer, build the piece nothing else depends
   on first (e.g. Serializer before View before Router; Category model before Entry model).

When extending this project (adding a feature, fixing a bug), follow the same approach:
identify the smallest complete vertical slice, then order the sub-steps by dependency.

## Coding Conventions

- **Backend:** Manual `APIView` classes (not DRF generic views) are used intentionally for
  learning purposes — code should stay explicit rather than relying on framework magic, even
  if a generic view would be shorter.
- **Serializers:** Use `ModelSerializer`. Always list `fields` explicitly — never use
  `fields = '__all__'`.
- **Foreign keys:** Default to `on_delete=models.PROTECT` unless there's a specific reason
  for `CASCADE` or `SET_NULL` — this project prioritizes not silently losing historical data.
- **Frontend:** Plain JavaScript (`.jsx`) with React function components and hooks. Tailwind
  and TypeScript are no longer used; styling is done with plain CSS files.
- **Commit messages:** Full, descriptive, plain English sentences (not Conventional Commits
  style prefixes like `feat:`/`fix:`). Keep them accurate to the actual diff.

## Current Status

- ✅ Backend: `Category` and `Entry` models, migrations applied
- ✅ Backend: `/api/entries/` endpoint (GET list, POST create), manually tested via DRF's
  Browsable API
- ✅ Backend: CORS configured for the Vite dev server (`http://localhost:5173`)
- ✅ Frontend: rebuilt as a plain JavaScript React app with Vite (replaced the TypeScript +
  Tailwind scaffold); `App.jsx` is still an empty shell and not yet connected to the API
- ✅ Backend: `/api/categories/` endpoint (GET list sorted by name, POST create); `Category`
  and `Entry` are registered in the Django admin
- ✅ Backend: `/api/entries/` supports filtering (`?date=`, `?from=`, `?to=`, `?category=`) and
  returns entries newest first (`-date`, `-id`)
- ✅ Backend: `/api/entries/<id>/` (GET, PATCH, DELETE)
- ✅ Backend: duration must be between 1 and 1440 minutes; category names are unique ignoring
  case (database constraint plus a serializer check that returns a clean 400)
- ✅ Backend: automated tests in `backend/tracker/tests.py` (run with `python manage.py test`)
- ✅ Frontend: API base URL setup (Vite dev proxy for `/api`, `VITE_API_URL` for deployment)
  and a fetch helper in `frontend/src/api.js`
- 🔲 Frontend: fetch and display entries from `/api/entries/`
- 🔲 Frontend: form to create a new entry
- 🔲 Weekly dashboard, quick-add buttons, streak counter (see `DESIGN.md` for full scope)
- 🔲 Before external users / deployment: authentication and per-user data ownership
  (`Entry` has no `user` field yet), move `SECRET_KEY` to an environment variable, set
  `DEBUG=False` and a real `ALLOWED_HOSTS`, switch to PostgreSQL
- 🔲 Backend: a weekly summary endpoint for the dashboard (first decide the start of the week)

## Testing Changes

Backend tests exist in `backend/tracker/tests.py` and cover the categories and entries
endpoints. Run them with `python manage.py test`. Also verify changes manually:
- **Backend:** `python manage.py check`, then exercise the endpoint via DRF's Browsable API
  (`http://127.0.0.1:8000/api/entries/`) or Django's `django.test.Client` in a shell session.
- **Frontend:** `npm run lint` and `npm run build` should complete without errors; visually
  check `npm run dev` in the browser.

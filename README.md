# MindGuard AI

MindGuard AI is a student wellness companion that turns a short, counselor-like
conversation into a structured burnout assessment, a wellness snapshot, and a
practical recovery plan.

It is built as a layered system:

```
React frontend
   ↓  HTTPS / JSON (JWT)
Flask API
   ↓
AI interviewer (Groq LLM, deterministic fallback)
   ↓
Deterministic Burnout Engine (explainable, testable)
   ↓
SQLite (dev) / PostgreSQL (production)
```

The LLM only conducts the conversation. Every score is produced by the
deterministic engine, so the same facts always produce the same report.

---

## Features

- **AI check-in** — a multi-turn conversation (max 20 student turns) that asks
  about sleep, academic load, stress, mood, motivation, concentration, lifestyle,
  support, digital habits, and recent events.
- **Explainable report** — burnout score, wellness score, risk level, category
  health scores, primary contributors, and recovery suggestions.
- **Recovery planner** — suggested recovery tasks plus your own tasks, with
  priorities, due dates, and completion tracking.
- **Progress** — wellness/burnout/mood/sleep/stress trends, weekly planner
  completion, and recovery-goal completion.
- **Accounts** — registration, login, profile editing, password change,
  password reset (demo mode), data export, and account deletion.
- **Preferences** — notification toggles and AI conversation tone.

> MindGuard supports self-reflection and is **not** a substitute for
> professional care. If you are in crisis, contact local emergency services or
> a trusted professional.

---

## Repository layout

```
.
├── .github/workflows/deploy.yml     # Builds frontend and publishes to gh-pages
├── mindguard-backend/
│   ├── app.py                       # create_app() factory, error handlers, migrations
│   ├── config.py                    # Env-driven configuration
│   ├── Procfile                     # Render/Heroku start command (waitress)
│   ├── ai_engine/                   # LLM connector, conversation manager, extractor
│   ├── engine/                      # Schema, validators, normalizer, scoring, version
│   ├── routes/                      # auth, interview, dashboard, planner, progress, report
│   ├── models/                      # SQLAlchemy models
│   ├── utils/                       # JWT helpers, extensions
│   └── tests/                       # unittest suite (engine + API)
└── mindguard-frontend/
    ├── vite.config.js               # Dev proxy /api → :5000, build base /mindguard/
    ├── public/404.html              # GitHub Pages SPA fallback
    └── src/
        ├── pages/                   # Landing, auth, dashboard, chat, planner, progress, settings
        ├── components/              # Layout, landing sections, UI primitives
        ├── context/AuthContext.jsx  # Server-validated session
        └── services/api.js          # Single API client
```

---

## Getting started

### 1. Backend

```powershell
cd mindguard-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `mindguard-backend/.env`:

```ini
GROQ_API_KEY=gsk_...
SECRET_KEY=change-this-to-a-long-random-string
```

Run it:

```powershell
python app.py
# or
python -m flask --app app.py run --port=5000
```

The API starts on `http://localhost:5000` (health check: `/api/health`).
On first start the SQLite database is created at
`mindguard-backend/instance/mindguard.db`.

### 2. Frontend

```powershell
cd mindguard-frontend
npm install
npm run dev
```

Vite serves `http://localhost:5173` and proxies `/api` to the backend, so no
frontend env file is needed for local development.

To point at a deployed API, create `mindguard-frontend/.env.local`:

```ini
VITE_API_URL=https://your-backend.example.com/api
```

### 3. Run the tests

```powershell
cd mindguard-backend
python -m unittest discover -s tests -t . -v
```

The suite covers the schema/validator, normalizer, scoring, engine pipeline,
fact extractor, and the HTTP API (auth, settings, planner, interview, IDOR,
account deletion).

---

## How scoring works

The engine schema (`engine/schema.py`) is the single source of truth for
categories, field types, ranges, and orientation.

1. **Extract** — `ai_engine/extractor.py` records only facts the student
   explicitly stated. It never invents missing values, and a later correction
   ("actually I sleep 8 hours now") overrides an earlier statement.
2. **Validate** — `engine/validators.py` rejects unknown categories/fields,
   invalid labels, out-of-range numbers, and non-numeric continuous fields.
   Missing categories are allowed; partial reports are expected.
3. **Normalize** — every value becomes a **0–100 health score** (higher is
   better). Continuous fields are scaled between schema `min`/`max`, ordinal
   labels are mapped to scores, and negative-oriented fields are inverted.
4. **Score** — `engine/scoring.py` averages each category, applies
   `CATEGORY_WEIGHTS`, and renormalises weights across only the categories that
   were actually collected. An empty payload scores `0` burnout rather than a
   fabricated result.
5. **Classify** — risk thresholds come from `engine/config.py`
   (`Low < 35`, `Moderate < 65`, otherwise `High`).
6. **Explain** — the report includes the worst categories as primary
   contributors and maps them to recovery suggestions.

`engine/config.py` also exposes `ENGINE_VERSION`, which is stored with every
assessment so historical reports remain traceable.

---

## API

All routes are prefixed with `/api`. Protected routes require
`Authorization: Bearer <jwt>`.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Liveness probe |
| POST | `/register` | No | Create account, returns JWT + user |
| POST | `/login` | No | Log in, returns JWT + user |
| GET | `/me` | Yes | Current user |
| PUT | `/me` | Yes | Update name/email |
| DELETE | `/me` | Yes | Delete account and all data (password required) |
| POST | `/change-password` | Yes | Change password (current password required) |
| GET | `/me/export` | Yes | Export profile, assessments, goals, tasks |
| POST | `/forgot-password` | No | Request reset token/link |
| POST | `/reset-password` | No | Reset password with token |
| POST | `/interview` | Yes | Send a check-in message |
| GET | `/dashboard` | Yes | Latest snapshot, today's tasks, open goals |
| GET | `/planner` | Yes | List tasks |
| POST | `/planner` | Yes | Create task |
| PUT | `/planner/:id` | Yes | Update task (also syncs linked goal) |
| DELETE | `/planner/:id` | Yes | Delete task |
| GET | `/progress` | Yes | Assessment history + planner/goal completion |
| GET | `/report` | Yes | Latest full report + goals |
| GET | `/assessment/:id` | Yes | One assessment (owner only) |
| GET | `/settings` | Yes | Load preferences (creates defaults) |
| POST | `/settings` | Yes | Save preferences |

### Interview contract

```jsonc
// POST /api/interview  { "message": "...", "session_id": optional }
// Not finished:
{
  "complete": false,
  "reply": "How has your sleep been this week?",
  "session_id": 12,
  "missing_categories": ["sleep", "mood"],
  "round": 3
}

// Finished:
{
  "complete": true,
  "session_id": 12,
  "assessment_id": 4,
  "report": {
    "burnout_score": 62.4,
    "wellness_score": 37.6,
    "risk_level": "Moderate",
    "engine_version": "1.1.0",
    "categories_assessed": 9,
    "data_completeness": 0.56,
    "category_scores": { "sleep": 20.0 },
    "primary_contributors": ["sleep"],
    "recovery_focus_areas": ["..."],
    "category_summaries": { "sleep": "..." }
  }
}
```

If no usable facts were collected, the API returns `422` and keeps the session
open so the student can add more detail. A completed session returns `409`;
start a new conversation instead.

---

## Configuration

Backend (`mindguard-backend/.env`):

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | dev fallback | JWT signing key — **set in production** |
| `GROQ_API_KEY` | — | Groq API key; without it the interviewer uses deterministic fallback questions |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Interview model |
| `LLM_PROVIDER` | `groq` | `groq`, `openrouter`, or `hf` |
| `DATABASE_URL` | SQLite in `instance/` | `postgres://` is normalised to `postgresql://` |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed origins |
| `JWT_EXPIRES_DAYS` | `30` | Token lifetime |
| `RETURN_RESET_TOKEN` | `false` | Demo mode: return the reset token from `/forgot-password` because no mail provider is configured |
| `PORT` | `5000` | Development port |

Frontend (`mindguard-frontend/.env.production`):

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | API base URL including `/api` |
| `VITE_BASE_PATH` | Optional build base; defaults to `/mindguard/` for builds and `/` for dev |

---

## Deployment

- **Frontend** — `.github/workflows/deploy.yml` builds on pushes to `main` or
  `backup-f71dc85` and publishes `mindguard-frontend/dist` to the `gh-pages`
  branch. The Vite base is `/mindguard/`, and `public/404.html` redirects deep
  links back into the SPA.
- **Backend** — the included `Procfile` runs
  `waitress-serve --port=$PORT app:app`. On Render, set `SECRET_KEY`,
  `GROQ_API_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, and (for the demo)
  `RETURN_RESET_TOKEN=true`. `psycopg2-binary` is included for PostgreSQL.
- On startup `create_app()` runs `db.create_all()` plus additive schema upgrades
  for columns added after the first release.

---

## Notes and limitations

- Password reset has no email provider in this build. With
  `RETURN_RESET_TOKEN=true` the reset link is shown in the UI so the flow can be
  demonstrated end-to-end.
- The interface is dark-only by design; a light theme is not shipped.
- Notification preferences are stored but no push/email delivery is configured.

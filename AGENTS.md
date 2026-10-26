# MindGuard AI — Agent Context

## Purpose
Student burnout detection and recovery planning. Layer boundaries are strict:

```
frontend → Flask API → AI interviewer → deterministic Burnout Engine → DB
```

The LLM never scores. Scores always come from `engine/`.

## Project structure

```
mindguard-backend/
├── app.py                      # create_app(), error handlers, additive SCHEMA_UPGRADES
├── config.py                   # env-driven config (DATABASE_URL, CORS, JWT, reset demo)
├── Procfile                    # waitress-serve --port=$PORT app:app
├── models/
│   ├── user.py                 # User
│   ├── assessment.py           # BurnoutAssessment (+ engine_version, category_summaries)
│   ├── interview.py            # InterviewSession (collected_facts, conversation_history)
│   ├── planner.py              # PlannerTask (task_source, goal_id, completion_date)
│   ├── recovery_goal.py        # RecoveryGoal
│   └── settings.py             # UserSettings (unique user_id, ai_tone, notification_*)
├── routes/
│   ├── auth.py                 # register/login/me/change-password/export/delete/reset
│   ├── dashboard.py            # latest snapshot + today's tasks + open goals
│   ├── planner.py              # CRUD, owner-scoped, syncs linked goal completion
│   ├── progress.py             # assessment history + weekly planner + goal stats
│   ├── report.py               # latest report + goals
│   ├── interview.py            # multi-turn check-in → assessment → plan
│   ├── assessment.py           # single assessment (owner only)
│   └── settings.py             # GET/POST preferences
├── engine/
│   ├── schema.py               # single source of truth: categories/fields/types/ranges
│   ├── validators.py           # strict validation; missing categories allowed
│   ├── normalizer.py           # every value → 0–100 health score (+ orientation)
│   ├── scoring.py              # category scores, renormalised weights, burnout
│   ├── config.py               # CATEGORY_WEIGHTS, RISK_THRESHOLDS, ENGINE_VERSION
│   ├── recovery_mapper.py      # contributors → recovery suggestions
│   ├── burnout_engine.py       # pipeline entry point
│   └── version.py              # re-exports ENGINE_VERSION
├── ai_engine/
│   ├── llm_connector.py        # Groq/OpenRouter/HF + deterministic fallback questions
│   ├── conversation_manager.py # prompt + state + completion decision
│   ├── prompt_builder.py       # tone-aware prompt
│   ├── extractor.py            # explicit-fact extraction only (no fabrication)
│   └── state_manager.py        # categories/state helpers
├── utils/
│   ├── auth.py                 # JWT create/decode, jwt_required (rejects deleted users)
│   └── extensions.py           # bcrypt
├── tests/                      # unittest suite (69 tests)
│   ├── fixtures.py             # GOOD_PAYLOAD / BAD_PAYLOAD
│   ├── test_normalizer.py
│   ├── test_validator.py
│   ├── test_scoring.py
│   ├── test_engine.py
│   ├── test_extractor.py
│   └── test_api.py             # full HTTP flows
└── .vscode/tasks.json          # run tests / run API

mindguard-frontend/
├── vite.config.js              # dev proxy → :5000, build base /mindguard/
├── public/404.html             # GitHub Pages SPA fallback
└── src/
    ├── main.jsx                # BrowserRouter with BASE_URL-derived basename
    ├── App.jsx                 # routes, ProtectedRoute, ScrollManager
    ├── context/AuthContext.jsx # server-validated session, refreshUser
    ├── services/api.js         # single API client (JWT, errors, 401 handling)
    ├── pages/                  # Landing, Login, Register, Forgot/ResetPassword,
    │                           # Dashboard, AIChat, Planner, Progress, Settings, NotFound
    └── components/             # layout/, landing/, ui/
```

## Key decisions

1. **JWT auth** — bearer token in `localStorage`; `jwt_required` also verifies the
   user still exists. The frontend validates `/api/me` on load.
2. **Deterministic scoring** — normalize to 0–100 health values, apply weights,
   renormalise over collected categories only. Empty payload → 0 burnout.
3. **No fabricated facts** — the extractor records only what the student said;
   partial reports are valid (`validate_payload(require_all=False)`).
4. **Interview limits** — `MAX_INTERVIEW_ROUNDS = 20`, `MAX_MESSAGE_LENGTH = 4000`.
   Completed sessions return `409`; unusable sessions return `422`.
5. **Recovery plan generation** — the engine's focus areas become goals and
   planner tasks; duplicates are skipped.
6. **Demo reset** — no SMTP. `RETURN_RESET_TOKEN=true` makes `/forgot-password`
   return the token so the UI can show a reset link.
7. **Dark-only UI** — no broken light theme.
8. **Base-path aware frontend** — build base `/mindguard/`, dev base `/`.

## Commands

### Backend
```powershell
cd mindguard-backend
$env:FLASK_APP="app.py"; python -m flask run --port=5000
```

### Tests
```powershell
cd mindguard-backend
python -m unittest discover -s tests -t . -v
```

### Frontend
```powershell
cd mindguard-frontend
npm run dev
npm run build
```

## Environment (`.env`)
```
GROQ_API_KEY=gsk_...
SECRET_KEY=long-random-string
# optional
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://your-frontend.example.com
JWT_EXPIRES_DAYS=30
RETURN_RESET_TOKEN=false
```

## Interview flow
1. `POST /api/interview {message}` → `{session_id, reply, complete: false}`
2. Continue with `{message, session_id}` for up to 20 student turns.
3. On completion → report + assessment + recovery goals/tasks.
4. Subsequent messages to a completed session → `409`.
5. No usable facts → `422`, session stays open for more detail.

## API endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/health | No | Liveness |
| POST | /api/register | No | Register |
| POST | /api/login | No | Login |
| GET | /api/me | Yes | Current user |
| PUT | /api/me | Yes | Update profile |
| DELETE | /api/me | Yes | Delete account (password) |
| POST | /api/change-password | Yes | Change password |
| GET | /api/me/export | Yes | Export all user data |
| POST | /api/forgot-password | No | Request reset |
| POST | /api/reset-password | No | Reset password |
| GET | /api/dashboard | Yes | Latest snapshot |
| GET | /api/planner | Yes | List tasks |
| POST | /api/planner | Yes | Create task |
| PUT | /api/planner/:id | Yes | Update task |
| DELETE | /api/planner/:id | Yes | Delete task |
| GET | /api/progress | Yes | History + completion stats |
| GET | /api/report | Yes | Latest report + goals |
| GET | /api/assessment/:id | Yes | One assessment |
| GET | /api/settings | Yes | Get settings |
| POST | /api/settings | Yes | Save settings |
| POST | /api/interview | Yes | Check-in message |

## Score semantics
- All `*_score` category values are **health** scores: higher is better.
- `burnout_score` is the exception: higher is worse.
- `wellness_score = 100 - burnout_score`.
- `data_completeness` = collected categories / all categories.
- Frontend trend arrows must invert only `burnout_score`.

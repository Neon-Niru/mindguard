# MindGuard AI - Session Context

## Project Structure
```
D:\mindguard\
├── AGENTS.md
├── plan.md
├── mindguard-backend/
│   ├── app.py              # Flask entry point, blueprint registration
│   ├── config.py           # Flask config (SECRET_KEY, SQLAlchemy)
│   ├── requirements.txt
│   ├── .env                # GROQ_API_KEY, SECRET_KEY (not committed)
│   ├── models/
│   │   ├── user.py         # User model
│   │   ├── assessment.py   # BurnoutAssessment model
│   │   ├── session.py      # InterviewSession model
│   │   ├── planner.py      # PlannerTask model
│   │   ├── recovery.py     # RecoveryGoal model
│   │   └── settings.py     # UserSettings model
│   ├── routes/
│   │   ├── auth.py         # /api/register, /api/login, /api/me, /api/forgot-password
│   │   ├── dashboard.py    # /api/dashboard
│   │   ├── planner.py      # /api/planner (CRUD)
│   │   ├── progress.py     # /api/progress
│   │   ├── report.py       # /api/report
│   │   ├── interview.py    # /api/interview (multi-turn LLM chat)
│   │   ├── assessment.py   # /api/assessment/<id>
│   │   └── settings.py     # /api/settings (GET/POST)
│   ├── engine/
│   │   ├── __init__.py     # BurnoutEngine class and schemas
│   │   ├── schema.py       # ENGINE_SCHEMA with field types
│   │   ├── validators.py   # Validate payload against schema
│   │   ├── normalizer.py   # Ordinal→numeric conversion
│   │   ├── scoring.py      # Category scoring, burnout calc
│   │   ├── config.py       # CATEGORY_WEIGHTS, RISK_THRESHOLDS
│   │   └── burnout_engine.py # Main engine entry point
│   ├── ai_engine/
│   │   ├── llm_connector.py    # Groq API calls
│   │   ├── conversation_manager.py # Prompt builder, state mgmt
│   │   └── extractor.py        # Keyword extraction from conversation
│   ├── utils/
│   │   ├── auth.py         # generate_token, decode_token, jwt_required
│   │   └── extensions.py   # flask extensions (bcrypt, migrate)
│   └── tests/
│       ├── test_engine.py
│       ├── test_scoring.py
│       ├── test_normalizer.py
│       └── test_validator.py
└── mindguard-frontend/
    ├── vite.config.js      # Proxy /api → localhost:5000
    ├── src/
    │   ├── App.jsx          # Route setup, AuthProvider, ProtectedRoute
    │   ├── context/AuthContext.jsx
    │   ├── services/api.js  # All API endpoints with JWT
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   ├── ForgotPassword.jsx
    │   │   ├── Dashboard.jsx
    │   │   ├── AIChat.jsx   # Multi-turn interview UI
    │   │   ├── Planner.jsx
    │   │   ├── Progress.jsx
    │   │   ├── Settings.jsx
    │   │   └── Landing.jsx
    │   └── components/
    │       └── layout/AppLayout.jsx, AppSidebar.jsx
    └── tailwind.config.js
```

## Key Architecture Decisions
1. **JWT Auth**: Bearer tokens stored in localStorage, `jwt_required` decorator on protected routes
2. **Database**: SQLite (dev), all URLs prefixed with `/api`
3. **Interview**: Multi-turn conversation with Groq LLM, limited to 20 rounds (force-complete), states stored in DB per-turn
4. **Extraction**: Regex + keyword-based from full conversation history
5. **Scoring**: Ordinal→numeric mapping (Never=0, Rarely=25, Sometimes=50, Often=75, Always=100), continuous fields use raw values normalized to 0-100

## Useful Commands

### Backend
```powershell
cd mindguard-backend
$env:FLASK_APP="app.py"; python -m flask run --port=5000
```

### Frontend
```powershell
cd mindguard-frontend
npm run dev
```

### End-to-end test (backend)
```powershell
cd mindguard-backend
Remove-Item -LiteralPath "instance" -Recurse -Force
python test_interview.py   # Full flow: register → login → interview → dashboard
```

### Unit tests
```powershell
cd mindguard-backend
python tests/test_engine.py
python tests/test_scoring.py
python tests/test_normalizer.py
python tests/test_validator.py
```

## Environment Variables (`.env`)
```
GROQ_API_KEY=gsk_...
SECRET_KEY=your-secret-key-here
```

## Interview Flow
1. POST `/api/interview` with `{message: "..."}` → returns `session_id`, `reply`, `complete: false`
2. Continue with `{message: "...", session_id: "..."}` for up to 20 rounds
3. When `complete: true`, returns burnout report with scores
4. MAX_INTERVIEW_ROUNDS = 20 (in routes/interview.py)

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/register | No | Register user |
| POST | /api/login | No | Login, returns JWT |
| GET | /api/me | Yes | Current user info |
| POST | /api/forgot-password | No | Request reset |
| POST | /api/reset-password | No | Reset password |
| GET | /api/dashboard | Yes | Latest wellness data |
| GET | /api/planner | Yes | List tasks |
| POST | /api/planner | Yes | Create task |
| PUT | /api/planner/:id | Yes | Update task |
| DELETE | /api/planner/:id | Yes | Delete task |
| GET | /api/progress | Yes | Historical assessments |
| GET | /api/report | Yes | Latest report + goals |
| GET | /api/assessment/:id | Yes | Single assessment |
| GET | /api/settings | Yes | Get settings |
| POST | /api/settings | Yes | Save settings |
| POST | /api/interview | Yes | Send/receive chat message |

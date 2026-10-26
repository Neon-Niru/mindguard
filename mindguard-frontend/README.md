# MindGuard AI — Frontend

The React client for MindGuard AI. It handles the landing page, authentication,
the AI check-in, the recovery planner, progress charts, and account settings.
All persistence and scoring live in the Flask backend — this app only renders
data returned by the API.

## Stack

- React 18 + Vite 5
- React Router v6 (client-side routing, base-path aware)
- Tailwind CSS (design tokens in `tailwind.config.js`)
- Recharts (progress charts)
- lucide-react (icons)

## Getting started

```bash
npm install
npm run dev
```

Vite serves `http://localhost:5173` and proxies `/api` to
`http://localhost:5000`, so start the backend first.

## Environment

| Variable | Where | Purpose |
|---|---|---|
| `VITE_API_URL` | `.env.local` / `.env.production` | API base URL including `/api` |
| `VITE_BASE_PATH` | build env | Overrides the deployed base path |

Defaults:
- Dev base: `/` (with the `/api` proxy)
- Build base: `/mindguard/` (GitHub Pages); override with `VITE_BASE_PATH`
- Without `VITE_API_URL`, the client calls `/api` on the same origin

Production uses `.env.production`:

```ini
VITE_API_URL=https://mindguard-demo-ln8z.onrender.com/api
```

## Scripts

```bash
npm run dev       # Vite dev server
npm run build     # Production build to dist/
npm run preview   # Preview the production build
```

## Routes

| Route | Page |
|---|---|
| `/` | Landing (Hero, Features, How It Works, About, Contact footer) |
| `/login` | Login |
| `/register` | Register |
| `/forgot-password` | Request a reset link |
| `/reset-password?token=...` | Choose a new password |
| `/app/dashboard` | Latest wellness snapshot, today's planner progress, open goals |
| `/app/chat` | AI check-in and inline wellness report |
| `/app/planner` | Tasks and recovery goals |
| `/app/progress` | Assessment trends, weekly planner completion, goal completion |
| `/app/settings` | Profile, password, notifications, AI tone, privacy/export/delete |
| `*` | Not found |

## Implementation notes

- `src/services/api.js` is the only place that talks to the backend. It adds the
  JWT, normalises errors, and dispatches `mindguard:unauthorized` when the token
  is rejected so `AuthContext` can clear the session.
- `AuthContext` validates the stored token with `GET /api/me` on load, keeps the
  cached user when the device is offline, and exposes `refreshUser`.
- The router base comes from `import.meta.env.BASE_URL`, so the same build works
  at `/` and at `/mindguard/`.
- `public/404.html` redirects GitHub Pages deep links back into the SPA and
  stores the intended path in `sessionStorage`.
- Every score shown in the UI is a **health** score (higher is better) except
  burnout, which is explicitly inverted in trend labels.
- Settings saves are debounced, and planner actions are optimistic with rollback
  on API failure.
- The interface is dark-only by design.

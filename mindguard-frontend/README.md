# MindGuard AI — Frontend

This is **only the frontend (UI/UX layer)** of MindGuard AI, built to match `plan.md`'s
Level 1 — User Interface spec. It contains no backend, no AI logic, and no database code —
all data on these pages is static mock data in `src/data/mockData.js`, ready to be swapped
for real API calls later.

## Stack
- React 18 + Vite
- React Router v6 (client-side routing)
- Tailwind CSS (design tokens in `tailwind.config.js`)
- Recharts (Progress page trend charts)
- lucide-react (icons)

## Getting started
```bash
npm install
npm run dev
```
Then open the local URL Vite prints (usually http://localhost:5173).

## Pages
| Route | Page |
|---|---|
| `/` | Landing (Hero, Features, How It Works, About, Contact footer) |
| `/login` | Login |
| `/register` | Register |
| `/forgot-password` | Forgot Password |
| `/app/dashboard` | Dashboard (latest snapshot only, no history) |
| `/app/chat` | AI Wellness Chat + inline report |
| `/app/planner` | Recovery Planner (tasks + goals + progress bar) |
| `/app/progress` | Progress (historical trends via Recharts) |
| `/app/settings` | Settings (Profile, Password, Notifications, Theme, AI Config, Privacy) |

## Design system
- **Theme:** dark mode by default
- **Accent:** blue → purple → teal gradient (`bg-brand-gradient` / `.text-gradient`)
- **Style:** glassmorphism (`.glass` utility class — frosted, blurred, soft border), large
  rounded corners, soft glows, floating decorative icons, subtle motion
- Colors, fonts, and radii are defined once in `tailwind.config.js` / `src/index.css` and
  reused everywhere — every page pulls from the same tokens.

## Wiring up the real backend later
Replace the imports from `src/data/mockData.js` with real API calls (fetch/axios) inside
each page, matching the JSON shapes documented in `plan.md`'s backend module contracts.
Auth forms in `Login.jsx` / `Register.jsx` currently just navigate to `/app/dashboard` —
swap that for a real POST to your Flask auth endpoint.

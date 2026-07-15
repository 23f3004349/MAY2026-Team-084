# SocietyEase — Prototype

A self-contained, runnable prototype of **SocietyEase**, an apartment-society app. It keeps the full
**management core** (the original project's features) *and* a daily **community layer**, bound together by an
invisible **engagement engine** (points, levels, streaks, badges, celebrations) built on Nir Eyal's Hook Model —
so the app is both genuinely useful and genuinely habit-forming.

> Product thinking: [`docs/engagement-vision.md`](docs/engagement-vision.md).

---

## Features

**Community layer (daily engagement)**
- **For You** (`/app/home`) — the hub: greeting, daily **check-in + streak**, dues glance, community pulse, quick actions.
- **Community** (`/app/community`) — social wall: posts, reactions 👍❤️🎉🙏, threaded comments.
- **Events** (`/app/events`) — society events + RSVP with "N going" social proof.
- **Amenities** (`/app/amenities`) — book gym / pool / clubhouse / courts with live slots.
- **Marketplace** (`/app/marketplace`) — buy / sell / give-away within the society.
- **Rewards / You** (`/app/rewards`) — level ring + ladder, badge collection, leaderboard, Neighbour of the Month.

**Management core (the original project)**
- **Pay & Dues** (`/app/invoices`) — dues hero, one-tap pay → **persisted receipt + confetti + NP**.
- **Complaints** (`/app/complaints`) — raise + track on an OPEN→…→CLOSED lifecycle rail.
- **Notices** · **Polls** (one-tap vote → NP) · **Conflict Resolver** (anonymous) · **Visitor Parking**.
- **Admin:** Dashboard, Members, Expenses, Maintenance, Smart Equipment predictor, **Society Health Score** (live gauge).

Navigation is grouped (Community / Operations / Manage) in the desktop sidebar and collapses to a **mobile bottom
tab bar + "More" sheet** on phones.

---

## The engagement engine (why people don't want to quit)

**Hook Model** — **Trigger** (notification bell + nudges) → **Action** (one-tap: check in, pay, vote, RSVP, book,
react) → **Variable Reward** (fresh feed, surprise level-ups, confetti, social replies) → **Investment** (streaks,
points, badges, history you don't want to lose).

- **Neighbour Points (NP)** for civic + community actions (pay +50, vote +20, RSVP +10, post +15, book +8, check-in).
- **Levels** Newcomer → Neighbour → Good Neighbour → Community Star → Society Legend.
- **Streaks** (daily check-in 🔥, on-time payment), **badges**, a friendly **leaderboard**, and **celebrations** (confetti + reward cards).
- **Dark mode** + notification centre in the topbar. Ethical by design: no punishing streaks, no fake urgency on money.

---

## Run it

```bash
# 1. Backend (Flask) — port 5000
cd Backend
pip install -r requirements.txt
python app.py

# 2. Frontend (Vue 3 + Vite) — port 5173, new terminal
cd Frontend
npm install
npm run dev
```
Open http://localhost:5173. Vite proxies `/api` → `http://localhost:5000`.

### Demo accounts
| Role | Email | Password |
|---|---|---|
| Admin / Secretary | `admin@apt.com` | `Admin@123` |
| Worker | `worker@apt.com` | `Worker@123` |
| Owner / Resident | `owner@apt.com` | `Owner@123` (flat A-101, with a live due to pay) |

---

## Architecture

```
prototype/
├─ Backend/                Flask API (JWT auth, SQLite) — seeded societyease.db
│  └─ api/, auth/          blueprints
└─ Frontend/ src/
   ├─ components/          all screens (one design system)
   ├─ store/
   │  ├─ auth.js           session + role guards
   │  ├─ engagement.js     points/levels/streaks/badges (localStorage-persisted)
   │  └─ demo.js           reactive community demo data (wall/events/amenities/marketplace/leaderboard)
   ├─ composables/useCelebrate.js   confetti + toasts + reward() helper
   ├─ router/index.js      full /app/* routes + role guards
   └─ style.css            design tokens + components + dark theme + modern lift
```

**Design system:** one token set (`--se-*`) — Society Navy `#1B2A4A`, Community Teal `#0E7C7B`,
Ease Marigold `#F2A541` — over Bootstrap 5; dark mode is a `[data-theme="dark"]` remap; glassy topbar, soft depth,
sleek scrollbars. **Responsive:** grouped sidebar → mobile bottom tab bar + More sheet; forms → bottom sheets; ≥44px targets.

**Backend bug fixes (this pass):** the SQLite `Date` columns were being fed raw strings / `None`, 500-ing invoice
creation (`due_date`) and poll creation (`start_date`), and the pay endpoint was admin-only. Fixed with date parsing
+ sensible defaults, and `PUT /invoices/:id/pay` now lets a resident pay *their own* invoice — **payments persist
server-side** (survive reload). The community layer + engagement engine remain reactive client-side stores so every
interaction is live in the prototype.

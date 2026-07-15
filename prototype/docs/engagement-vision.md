# SocietyEase Prototype — Engagement & Modernization Vision

*How this prototype should function, the new features that modernize it, and the habit-forming mechanics that make residents open it every day.*

---

## 1. The shift: from "tool you're forced to use" to "place you want to be"

A society-management app is normally opened **only under duress** — a due is nagging, a complaint is stuck. That is a utility, and utilities are abandoned the moment the chore is done. To make people *not want to quit*, SocietyEase must add a **daily-life layer** on top of the management layer, so there is always a fresh reason to open it that has nothing to do with paying money.

Two layers, one app:

| Layer | Purpose | Frequency |
|---|---|---|
| **Management core** (existing) | dues, complaints, notices, polls, members, parking | monthly / on-event |
| **Community layer** (new) | social wall, events, amenity booking, marketplace, recognition | **daily** |
| **Engagement engine** (new, invisible) | points, levels, streaks, badges, notifications, celebrations | every session |

The engagement engine is the connective tissue: **every** action in either layer feeds points, streaks, and the Society Health Score, so even paying a bill becomes a rewarded, celebrated moment.

---

## 2. The Hook Model, applied (Nir Eyal: Trigger → Action → Variable Reward → Investment)

Habits form when a loop runs enough times that an **external trigger** is replaced by an **internal one** ("I'm bored / curious → open SocietyEase"). We engineer all four stages.

### Trigger
- **External:** notification center with unread badge; smart, well-timed nudges ("Poll closes in 2 h — 18 flats voted, add yours"; "3 new posts on the wall"; "Ravi RSVP'd to the Diwali party"). Tone is calm and specific, never nagging.
- **Internal:** we attach the app to existing emotions — *curiosity* (what's happening in my building?), *belonging* (am I part of this?), *FOMO* (an event/poll is closing), *pride* (my streak, my level).

### Action (Fogg: B = Motivation × Ability × Trigger — make it trivially easy)
- One-tap: react to a post, RSVP, cast a vote, pay a due, check in for the day. Every high-value action is ≤ 2 taps from the home feed.

### Variable Reward (the core of "addiction" — rewards of the Tribe, the Hunt, the Self)
- **Tribe** (social): reactions/comments on your posts, "Neighbor of the Month," leaderboard movement, appreciation from neighbors.
- **Hunt** (resources/info): a *fresh, never-identical* home feed each open; new posts, new events, changing Health Score, surprise perks.
- **Self** (mastery): points, level-ups, badges unlocking, a growing streak. Rewards are **variable** — a level-up or a surprise badge appears unpredictably, which is what sustains the behavior (intermittent reinforcement).

### Investment (stored value that makes leaving costly and the next trigger better)
- Users accumulate **streaks, points, badges, a completed profile, post history, RSVPs, payment record**. This stored value (a) they don't want to lose (loss aversion) and (b) makes the app more personalized/valuable over time. Investment also *loads the next trigger* — you posted, so you'll be notified when someone replies.

---

## 3. Engagement mechanics (the invisible engine)

Implemented once in a shared `store/engagement.js`, consumed by every feature. Persisted to `localStorage` so streaks/points feel alive across sessions.

- **Neighbour Points (NP):** awarded for civic + community actions — pay on time (+50), vote in a poll (+20), post on the wall (+15), RSVP an event (+10), react/comment (+3), resolve a complaint (worker, +30), daily check-in (+5, escalating with streak). Points are the universal currency of progress.
- **Levels:** NP thresholds map to identity-badges — **Newcomer → Neighbour → Good Neighbour → Community Star → Society Legend.** Level is shown as a ring around the avatar (progress to next level always visible = the "Zeigarnik" pull of an unfinished bar).
- **Streaks:** a **daily check-in streak** and a **consecutive-on-time-payment streak.** Streaks show a flame + count; breaking one hurts (loss aversion) — with a one-time "streak freeze" as a gentle, benevolent mechanic.
- **Badges / Achievements:** unlockable, some hidden ("First Post," "Early Bird" voter, "6-Month Streak," "Peacemaker" for using the Conflict Resolver, "Full House" profile). Grid of earned + locked (locked ones tease the next goal).
- **Leaderboard:** friendly, **block-vs-block and flat ranking** by NP this month — social comparison drives participation, framed positively ("your block is #2, 40 NP behind A-block").
- **Society Health Score:** the collective trophy — a live 0–100 gauge (payments, complaints resolved, participation, events). Everyone's actions move it; crossing into GREEN triggers a shareable celebration. This aligns individual habit with community good.
- **Notifications feed:** in-app center (bell + unread count) that aggregates triggers and *reciprocity hooks* (replies, reactions, mentions).
- **Celebrations:** confetti + a reward card on level-up, streak milestones, dues cleared, badge unlock, check-in. Delight is the felt "reward."

**Ethical guardrails (so it's habit-forming, not dark-pattern):** streaks never punish with real consequences; no manipulative countdowns on money; notifications are batched and mutable; recognition is positive-sum. The goal is a community people love, not compulsion they resent.

---

## 4. New features (modernize + create daily reasons to return)

Built as real, interactive Vue screens on the design system, wired to the engagement engine.

1. **Personalized Home Feed ("For You")** — replaces the static dashboard. A dynamic, greeting-led stream: streak + level chip, one hero next-action, daily check-in, then a mixed feed (a due, a closing poll, a new event, a hot wall post, a Health-Score nudge). *Never the same twice → the Hunt reward.*
2. **Community Wall** — the social heart: posts with categories (Announcement, Help, Recommend, Lost & Found, Celebration), one-tap **reactions** (👍 ❤️ 🎉 🙏), threaded **comments**, a composer. Reciprocity + Tribe rewards; the #1 daily-return driver (replaces the society WhatsApp chaos).
3. **Events & RSVP** — society events with cover, date, "**18 neighbours going**," one-tap RSVP, and social proof of who's attending. FOMO + calendar habit.
4. **Amenity Booking** — gym / clubhouse / pool / party-hall with **live slot availability** and instant booking. A genuinely daily utility (book the gym every morning) = frequency.
5. **Rewards & Recognition** — the profile: level ring, NP balance, streak flames, badge grid, and **leaderboard**. "Neighbour of the Month" spotlight. The Self reward, made visible.
6. **Marketplace / Classifieds** — buy/sell/give-away within the society (furniture, cycles, services). Recurring browsing habit + trust (verified neighbours).
7. **Notification Center + Dark Mode + Delight** — topbar bell with unread feed, a polished **dark theme** toggle (modernization signal), global confetti/toast celebration system.

*(Existing planned features — Neighbour Conflict Resolver, Smart Maintenance Predictor, Health Score — are kept and folded into the engine: Conflict use earns a "Peacemaker" badge; Health Score becomes the collective trophy.)*

---

## 5. How a day feels (the loop in practice)

> Morning: push — *"Gym slot 7 AM open."* Priya books it (habit utility). On the home feed she sees her **12-day check-in streak** (+ taps check-in, confetti, +5 NP), a **new wall post** about a water cut (reacts 🙏), and that the **solar poll closes tonight** (votes, +20 NP, nudged past a level threshold → **level-up celebration: "Community Star!"**). She notices her block slipped to #2 on the leaderboard and shares a post rallying neighbours. Evening: someone replied to her post → notification → she's back. No dues were involved all day — yet she opened the app four times.

That is the difference between a utility and a habit.

---

## 6. Build architecture (contracts for the feature agents)

- **Shared stores (built first, by the orchestrator):**
  - `store/engagement.js` — reactive: `points`, `level` (derived), `checkInStreak`, `paymentStreak`, `badges[]`, `notifications[]`; methods `award(np, reason)`, `checkIn()`, `unlock(badge)`, `notify(n)`, `hasCheckedInToday`; `localStorage` persistence + demo seed.
  - `store/demo.js` — reactive demo datasets: `wallPosts`, `events`, `amenities`, `leaderboard`, `marketplace`, `neighbourOfMonth`; mutation helpers.
  - `composables/useCelebrate.js` — `celebrate(type, payload)` → confetti + reward toast; `toast(msg, kind)`.
- **Design:** all colours via the existing `--se-*` tokens; **dark mode** via `[data-theme="dark"]` remap in `style.css`. Components use **scoped `<style>`** + tokens (no shared-CSS edits by agents → no conflicts).
- **Routing/nav/topbar** (bell, theme toggle, points chip) owned by the orchestrator in `router/index.js` + `DashboardLayout.vue`.
- **Each feature agent** owns exactly one page component, imports the shared stores/composable, and **awards points / fires celebrations** through them so the engine lights up end-to-end.

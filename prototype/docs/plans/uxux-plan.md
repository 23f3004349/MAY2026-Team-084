# SocietyEase — UI/UX Design System & Interface Plan
*UXLens · grounded in `Frontend/src` @ Milestone 2 · aligned with Main's canonicalization call (componenets/ app wins; tokens anchored on navy `#1B2A4A` / amber `#F2A541` / teal `#0E7C7B` / danger `#dc2626` / warn `#d97706`)*

---

## 0. Ground truth (what the repo actually contains)

Read before designing. Everything below was verified in-file:

| Fact | Evidence |
|---|---|
| `style.css` is the untouched Vite scaffold | Purple links `#646cff/#535bf2`, `#1a1a1a` buttons, `h1{font-size:3.2em}`, `body{display:flex;place-items:center}`, `.card{padding:2em}` colliding with Bootstrap's `.card` |
| Root color bug | `:root{ color: rgba(255,255,255,.87); background-color: white }` + `color-scheme: light dark` → white-ish text on white wherever Bootstrap doesn't override; OS dark mode produces random inversions |
| Two apps, two folders | `components/` = old Tenant/Association app (live via `routes.js`); `componenets/` (misspelled) = richer app: `DashboardLayout.vue` sidebar shell + Secretary/Resident/Worker dashboards + 12 feature pages, role guards — **not mounted** (`main.js` imports `./routes`, and `router/index.js` imports files from `../components/` that live in `../componenets/`) |
| ~20 orphan classes | The entire new app is styled against classes defined **nowhere**: `.sidebar`, `.sidebar-brand`, `.sidebar-nav`, `.nav-item`, `.sidebar-footer`, `.main-content`, `.topbar`, `.page-content`, `.stat-card`, `.stat-icon`, `.stat-value`, `.stat-label`, `.card-header-custom`, `.badge-custom` + 14 `badge-*` variants, `.alert-custom`/`.alert-error`/`.alert-success`, `.empty-state`, `.spinner`, `.table-custom`, `.modal-overlay`/`.modal-box`/`.modal-header`/`.modal-body`/`.modal-footer`, `.form-group`/`.form-label`/`.form-control-custom`, `.btn-primary-custom`, `.btn-accent`, `.progress-bar-custom`/`.progress-fill`, plus `.page-container` in `App.vue`. Grep for `.stat-card\s*{` returns zero. The new app currently renders as unstyled soup. |
| FontAwesome is loaded nowhere | Every page uses `fas fa-*`; no package in `package.json`, no CDN in `index.html`, no import in `main.js`. **All icons are invisible.** |
| Implicit palette already in markup | Navy `#1B2A4A` (sidebar/headings/₹ amounts/poll fill), amber `#F2A541` (brand glyph), teal `#0E7C7B` (success/available/completed), `#dc2626`, `#d97706`, Tailwind-lifted grays `#718096/#f1f5f9/#f8fafc`, greens `#065f46/#d1fae5`, reds `#991b1b/#fee2e2` — all inline `style=""` |
| Old app look (dies with it) | Powder-blue radial gradients `#f7fbff→#eef4ff`, baby-blue panels `#e5f2ff→#d6e8ff`, pure-black `#000` text everywhere, stray warm hovers (`#a68a72` mocha logo hover, `#bfafa1` beige placeholders), fake Google/Microsoft buttons that fire `alert('…coming soon!')` (`components/LoginPage.vue`) |
| State machines in code | Complaints: `OPEN → ASSIGNED → IN_PROGRESS → COMPLETED → CLOSED`, priority `LOW/MEDIUM/HIGH`, categories incl. `ELECTRICAL`; Invoices: `PAID/UNPAID/OVERDUE`; Parking: `AVAILABLE/OCCUPIED/RESERVED`; Polls: `ACTIVE/CLOSED` (currently reuses `badge-paid`/`badge-low` — smell) |
| Roles | `authStore`: admin = `ADMIN/TREASURER/COMMITTEE_MEMBER`, resident = `TENANT/OWNER`, worker = `WORKER` |
| `index.html` | `<title>frontend</title>`, Vite favicon, no fonts, no `theme-color` |
| Emoji-as-icon | Card headers use 📢 🔧 💰 ✅ 🧾 ⚡ 🏠 👤 — renders inconsistently across Windows/Android emoji fonts |
| en-IN formatting inconsistent | `toLocaleString('en-IN')` in dashboards, raw `₹{{ inv.amount }}` in `InvoicesPage.vue` |

**Strategic read:** the new app's markup already *believes* a design system exists — semantic class names, consistent structure. The fastest possible win is to **write the stylesheet the code already believes in**. No template rewrites needed to light up all 15 pages.

---

## 1. Design language & emotional hook

### The feeling: "My society, in order."
Housing-society software in India competes with a chaotic WhatsApp group and an opaque Excel sheet. The residents' baseline emotions are *distrust* (where does my maintenance money go?), *resignation* (complaints vanish into a black hole), and *noise*. The design's job is the opposite triad — **trust + calm + effortless** — delivered as: *the quiet confidence of a well-run society office, sunlit courtyard included.*

Aesthetic direction: **"Civic warmth"** — deep institutional navy (authority, permanence) on warm paper surfaces (home, not hospital), with marigold accents (auspicious, energetic, unmistakably Indian) and teal for everything that is *settled* (paid, resolved, available). Not a fintech clone, not a govt portal, not AI-gradient slop.

### The 5 signature moves

1. **One next action, always.** Every role's landing screen leads with a single hero card answering "what should I do right now?" — Resident: "₹2,400 due by 20 Jul → Pay now"; Secretary: "6 complaints waiting for assignment → Triage"; Worker: "Flat B-304, leaking tap → Start work". Zero-decision landings are how an app *feels* effortless before a single animation runs.
2. **Lifecycle rails, never lone status words.** Complaints and invoices always render their state as a position on a visible journey (`OPEN → ASSIGNED → IN_PROGRESS → COMPLETED → CLOSED` as a 4-stop progress rail with timestamps + actor names). The #1 trust killer in society apps is the complaint black hole; the rail makes progress *physically visible*.
3. **Money gets ceremony.** All ₹ amounts in tabular lining numerals, en-IN digit grouping (`₹1,23,450`), never mid-sentence. Payment confirmation renders as a **receipt artifact** — bordered, perforated-edge card with receipt number, teal check-draw animation, download action. Paying maintenance should feel like being handed a stamped receipt at the society office, not like a toast notification.
4. **Warm paper, navy ink.** Canvas is warm ivory `#F7F6F2`, cards are white with hairline borders and low navy-tinted shadows, headings are navy ink. No pure `#000`/`#fff` pairings, no gradients-as-decoration, no glass. The app reads as *printed and official*, which is exactly the trust register a society ledger needs.
5. **150ms acknowledgments.** Nothing mutates silently: buttons compress (`scale(.98)`), stat values count up once on load (600ms), the poll bar fills from 0, the complaint rail's next stop lights up, success states draw a check. All under 260ms except count-ups; all disabled under `prefers-reduced-motion`.

**Anti-goals** (explicitly rejected): auto dark mode (remove `color-scheme: light dark` — ship a deliberate light theme first), glassmorphism/blur cards, gradient headline text, cyan-purple AI palette, bounce easing, emoji as UI icons, every-button-primary.

---

## 2. Design tokens

All tokens live as CSS custom properties in `Frontend/src/style.css` (per Main's call: scaffold content deleted wholesale, replaced by this system — §6). Prefix `--se-` (SocietyEase).

### 2.1 Color — anchored on the palette already in the markup

Verdict on the "stray" teal `#0E7C7B`: **KEEP and promote.** It passes AA on white (5.0:1), it's already used everywhere the app means "settled/positive" (completed, available, collected), and per MarketingLens it's the ownable brand secondary (distinct from MyGate orange / ADDA blue). It becomes the anchor of a unified success ramp — which also retires the scattered off-system greens (`#065f46`, `#d1fae5`).

```css
:root {
  /* Brand — Society Navy (anchor #1B2A4A = 800) */
  --se-navy-950: #101B33;  --se-navy-900: #16233F;
  --se-navy-800: #1B2A4A;  /* base: sidebar, headings, primary buttons, ₹ figures */
  --se-navy-700: #253A66;  --se-navy-600: #30497F;  /* links, focus, active nav */
  --se-navy-500: #3E5A99;
  --se-navy-100: #DCE4F2;  --se-navy-50:  #EEF2F9;

  /* Brand — Ease Teal (anchor #0E7C7B = 600) · doubles as SUCCESS */
  --se-teal-800: #0A5251;  --se-teal-700: #0B6463;
  --se-teal-600: #0E7C7B;  /* base: success text/icons/buttons, AVAILABLE, PAID */
  --se-teal-100: #D5EDEC;  --se-teal-50:  #E9F6F5;

  /* Accent — Marigold (anchor #F2A541 = 400) · CTA fills + brand glyph only */
  --se-marigold-600: #B96F10; /* smallest allowed marigold text, on white only */
  --se-marigold-500: #E8941F; /* hover fill */
  --se-marigold-400: #F2A541; /* base fill — ALWAYS with navy-800 text (6.8:1) */
  --se-marigold-100: #FCE9CD; --se-marigold-50: #FDF4E4;

  /* Semantic — Danger (anchor #dc2626 = 600) */
  --se-danger-700: #B91C1C;  --se-danger-600: #DC2626; /* 4.8:1 on white */
  --se-danger-100: #FDE2E2;  --se-danger-50:  #FEF1F1;
  --se-danger-text-on-tint: #991B1B; /* already used in repo — kept */

  /* Semantic — Warning (anchor #d97706 = 600) */
  --se-warn-700: #B45309;    --se-warn-600: #D97706;  /* 3.2:1 — icons/large only */
  --se-warn-100: #FDEDD3;    --se-warn-50:  #FEF7EA;
  --se-warn-text-on-tint: #92400E;

  /* Neutrals — warm "stone" family (replaces #718096/#f1f5f9/#f8fafc + all #000) */
  --se-canvas:        #F7F6F2;  /* app background (warm paper)   */
  --se-surface:       #FFFFFF;  /* cards, modals, topbar          */
  --se-sunken:        #F1F0EB;  /* table heads, wells, code chips */
  --se-border:        #E6E5DF;  /* hairlines                      */
  --se-border-strong: #D2D1C9;  /* input borders                  */
  --se-ink:           #16233F;  /* headings (= navy-900), 14.9:1  */
  --se-text:          #353F51;  /* body, 9.9:1                    */
  --se-text-muted:    #5F6878;  /* secondary, 5.6:1               */
  --se-text-faint:    #98A0AE;  /* disabled/watermark ≥18px only  */
}
```

Rules: no hex anywhere outside `style.css` (acceptance gate in §6); marigold never carries text on light surfaces; `info` needs no sixth hue — use navy-600.

### 2.2 Typography

Two variable Google Fonts, both with ₹ glyphs **and Devanagari siblings** (regional-language expansion is a real roadmap concern for an Indian society product):

- **Display / headings: `Anek Latin`** (Indian Type Foundry; sibling `Anek Devanagari`) — weights 600–700, letter-spacing `-0.01em` at ≥20px. Characterful without being a meme font.
- **Body / UI: `IBM Plex Sans`** (sibling `IBM Plex Sans Devanagari`) — 400/500/600; true tabular figures via `font-feature-settings: "tnum"`.

```css
:root {
  --se-font-display: 'Anek Latin', system-ui, sans-serif;
  --se-font-body: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;

  --se-fs-2xs: 0.75rem;   /* 12 — pills, meta        */
  --se-fs-xs:  0.8125rem; /* 13 — labels, table meta */
  --se-fs-sm:  0.875rem;  /* 14 — dense UI, buttons  */
  --se-fs-md:  1rem;      /* 16 — body               */
  --se-fs-lg:  1.125rem;  /* 18 — card titles        */
  --se-fs-xl:  1.25rem;   /* 20 — section heads      */
  --se-fs-2xl: 1.5rem;    /* 24 — stat values        */
  --se-fs-3xl: 1.875rem;  /* 30 — page titles        */
  --se-fs-hero: 2.375rem; /* 38 — auth/marketing only */

  --se-lh-tight: 1.2; --se-lh-body: 1.55;
}
.se-num { font-feature-settings: "tnum"; } /* every ₹ figure and count */
```

Weights: 400 body · 500 form labels/nav · 600 buttons, card titles, pills · 700 stat values, page titles (display font). Micro-labels (stat-label, table heads): 12px, 600, `letter-spacing: .04em`, uppercase, `--se-text-muted`.

Load in `index.html` (self-host later): `<link rel="preconnect" href="https://fonts.googleapis.com">` + one CSS2 request for `Anek+Latin:wght@600..700` and `IBM+Plex+Sans:wght@400;500;600` with `display=swap`. Kill the scaffold's `h1{font-size:3.2em}`.

### 2.3 Spacing, radius, elevation, motion

```css
:root {
  /* 4px grid */
  --se-sp-1: 4px;  --se-sp-2: 8px;  --se-sp-3: 12px; --se-sp-4: 16px;
  --se-sp-5: 20px; --se-sp-6: 24px; --se-sp-7: 32px; --se-sp-8: 40px;
  --se-sp-9: 48px; --se-sp-10: 64px;
  /* usage law: card padding 20 (16 mobile) · gap between cards 16 · section gap 24 · page gutter 24 (16 mobile) */

  --se-r-sm: 6px;    /* chips, slot cards' inner bits */
  --se-r-md: 10px;   /* buttons, inputs, stat icons   */
  --se-r-lg: 14px;   /* cards, modals                 */
  --se-r-pill: 999px;

  /* navy-tinted, border-first (cards = 1px border + shadow-1, never blur) */
  --se-shadow-1: 0 1px 2px rgba(22,35,63,.05), 0 1px 3px rgba(22,35,63,.07);
  --se-shadow-2: 0 4px 12px rgba(22,35,63,.08);   /* hover lift, dropdowns */
  --se-shadow-3: 0 16px 40px rgba(22,35,63,.18);  /* modals only           */
  --se-ring: 0 0 0 3px rgba(48,73,127,.30);       /* focus halo            */

  --se-t-fast: 120ms;  /* hover/press color+transform */
  --se-t-med:  180ms;  /* pills, nav, inputs          */
  --se-t-slow: 260ms;  /* modal/card entrances        */
  --se-t-count: 600ms; /* stat count-up, bar fills — once, on load */
  --se-ease-out: cubic-bezier(.22,1,.36,1);   /* entrances */
  --se-ease-std: cubic-bezier(.4,0,.2,1);     /* everything else */
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

### 2.4 Wiring over Bootstrap 5.3 (no SCSS build needed)

`main.js` imports precompiled `bootstrap.min.css`; Bootstrap 5.3 exposes per-component CSS vars, so the theme layers on top in `style.css` **after** the import — zero build changes:

```css
:root {
  --bs-body-font-family: var(--se-font-body);
  --bs-body-bg: var(--se-canvas);
  --bs-body-color: var(--se-text);
  --bs-border-color: var(--se-border);
  --bs-border-radius: var(--se-r-md);
  --bs-primary-rgb: 27,42,74;    /* fixes .text-primary/.bg-primary utils */
  --bs-success-rgb: 14,124,123;
  --bs-danger-rgb: 220,38,38;
  --bs-warning-rgb: 217,119,6;
  --bs-link-color-rgb: 48,73,127;
}
.btn-primary { --bs-btn-bg: var(--se-navy-800); --bs-btn-border-color: var(--se-navy-800);
  --bs-btn-hover-bg: var(--se-navy-700); --bs-btn-hover-border-color: var(--se-navy-700);
  --bs-btn-active-bg: var(--se-navy-900); }
.btn-success { --bs-btn-bg: var(--se-teal-600); --bs-btn-border-color: var(--se-teal-600);
  --bs-btn-hover-bg: var(--se-teal-700); }
.btn-warning { --bs-btn-bg: var(--se-marigold-400); --bs-btn-color: var(--se-navy-800);
  --bs-btn-hover-bg: var(--se-marigold-500); }
.btn-outline-primary { --bs-btn-color: var(--se-navy-600); --bs-btn-border-color: var(--se-navy-600);
  --bs-btn-hover-bg: var(--se-navy-50); --bs-btn-hover-color: var(--se-navy-700); }
.modal-content { --bs-modal-border-radius: var(--se-r-lg); } /* if BS modals ever used */
```

This keeps every existing `btn btn-sm btn-outline-*` call site working, instantly recolored. (Optional Milestone-3: switch to SCSS `@import "bootstrap"` with `$primary` overrides to shrink CSS; not required now.)

---

## 3. Core component patterns — the orphan-class contract

**Current pain:** the component layer exists only as class names in markup (§0) plus inline `style=""` for anything colored. **The fix:** define every orphan class in `style.css` exactly as named — all 15 pages restyle with zero template edits — then strip inline hexes opportunistically (mechanical `style="background:#0E7C7B"` → class swaps).

Definitions (key values; Pratik implements verbatim):

### 3.1 App shell
- **`.sidebar`** — `width:248px; min-height:100vh; background:var(--se-navy-800); position:sticky; top:0; display:flex; flex-direction:column`. Subtle top-to-bottom deepening allowed via `linear-gradient(var(--se-navy-800), var(--se-navy-900))` (structural, not decorative).
- **`.sidebar-brand`** — padding `var(--se-sp-6) var(--se-sp-5)`; wordmark 18px/700 white; building glyph in `--se-marigold-400` (keep — it's the one warm spark on navy); role tag: 11px uppercase `.04em` `rgba(255,255,255,.55)`.
- **`.sidebar-nav .nav-item`** — `display:flex; gap:12px; align-items:center; padding:10px 20px; margin:2px 12px; border-radius:var(--se-r-md); color:rgba(255,255,255,.72); font-size:var(--se-fs-sm); font-weight:500; transition:background var(--se-t-med), color var(--se-t-med)`. Hover: `background:rgba(255,255,255,.06); color:#fff`. **Active (`.router-link-active`)**: `background:rgba(255,255,255,.10); color:#fff` + 3px marigold bar (`inset 3px 0 0 var(--se-marigold-400)` or `::before`). Icon fixed `width:20px; text-align:center`.
- **`.sidebar-footer`** — `margin-top:auto; padding:16px 20px; border-top:1px solid rgba(255,255,255,.08)`; logout = quiet button `rgba(255,255,255,.08)` → hover `.14`.
- **`.main-content`** — `flex:1; min-width:0; background:var(--se-canvas)`.
- **`.topbar`** — `height:64px; background:var(--se-surface); border-bottom:1px solid var(--se-border); display:flex; justify-content:space-between; align-items:center; padding:0 var(--se-sp-6); position:sticky; top:0; z-index:20`. Page title 20px/700 `--se-ink` (display font); date 13px `--se-text-muted`.
- **`.page-content`** — `padding:var(--se-sp-6); max-width:1200px` (16px on mobile).
- **`.page-container`** (App.vue) — plain `min-height:100vh` wrapper; also delete scaffold `body{display:flex;place-items:center}` which fights full-width layouts.

### 3.2 Cards & stat tiles
- **`.card`** (Bootstrap's, re-skinned; delete scaffold `.card{padding:2em}`) — `background:var(--se-surface); border:1px solid var(--se-border); border-radius:var(--se-r-lg); box-shadow:var(--se-shadow-1)`. Interactive cards (parking slots): hover `box-shadow:var(--se-shadow-2); translateY(-1px)`; never nest cards in cards.
- **`.card-header-custom`** — `padding:14px 20px; border-bottom:1px solid var(--se-border); font-weight:600; font-size:var(--se-fs-lg); color:var(--se-ink); display:flex; gap:10px; align-items:center`. **Replace emoji (📢🔧💰) with FA icons** in `--se-navy-600` at 16px — consistent cross-platform rendering. The one current variant `style="background:#0E7C7B"` (WorkerDashboard "Recently Completed") becomes modifier `.card-header-custom--success` (teal-50 bg, teal-800 text — tint, not fill).
- **`.stat-card`** — `display:flex; gap:14px; align-items:center; padding:var(--se-sp-5); background:var(--se-surface); border:1px solid var(--se-border); border-radius:var(--se-r-lg); box-shadow:var(--se-shadow-1)`.
- **`.stat-icon`** — `width:42px; height:42px; border-radius:var(--se-r-md); display:grid; place-items:center; color:#fff; font-size:1rem; flex-shrink:0`. Color modifiers replace today's inline hexes: `--navy`(members) `--danger`(complaints/dues) `--warn`(pending) `--teal`(polls/completed/available).
- **`.stat-value`** — `font-size:var(--se-fs-2xl); font-weight:700; color:var(--se-ink); font-feature-settings:"tnum"; line-height:1.1` + count-up on mount (600ms, ease-out, skipped under reduced-motion).
- **`.stat-label`** — 12px 600 uppercase `.04em` `--se-text-muted`.

### 3.3 Buttons
- **`.btn-primary-custom`** — navy fill: `background:var(--se-navy-800); color:#fff; border:0; border-radius:var(--se-r-md); padding:10px 18px; font-weight:600; font-size:var(--se-fs-sm); transition:background var(--se-t-fast), transform var(--se-t-fast)`. Hover `--se-navy-700`; **active `transform:scale(.98)`**; disabled `opacity:.55; cursor:not-allowed`. Min-height 40px desktop / 44px touch.
- **`.btn-accent`** — marigold CTA: `background:var(--se-marigold-400); color:var(--se-navy-800)` (6.8:1 — **never white text on marigold**, 1.9:1); hover `--se-marigold-500`. Reserved for the *money/primary-conversion* action per screen (Pay now, Bulk Generate) — max one visible per viewport.
- Quiet/tertiary = Bootstrap `.btn-light` re-skinned: `background:var(--se-sunken); color:var(--se-text); border:1px solid var(--se-border)`.
- Hierarchy law: one `.btn-accent` **or** `.btn-primary-custom` per view region; everything else outline/quiet. (Today's InvoicesPage shows both `btn-accent` + `btn-primary-custom` side by side — demote "Single Invoice" to outline.)

### 3.4 Status pills — one system for four state machines
- **`.badge-custom`** — `display:inline-flex; gap:6px; align-items:center; padding:3px 10px; border-radius:var(--se-r-pill); font-size:var(--se-fs-2xs); font-weight:600; letter-spacing:.02em`. **Always tint bg + dark same-hue text + leading 8px dot (or FA icon)** — color-blind safe by shape+text, no gray-on-color.
- Full variant map (all referenced in markup today):

| Class | bg | text | Semantics |
|---|---|---|---|
| `.badge-open` | `--se-danger-50` | `--se-danger-text-on-tint` | complaint OPEN |
| `.badge-assigned` | `--se-navy-50` | `--se-navy-700` | ASSIGNED |
| `.badge-in-progress` | `--se-warn-50` | `--se-warn-text-on-tint` | IN_PROGRESS |
| `.badge-completed`, `.badge-paid`, `.badge-available` | `--se-teal-50` | `--se-teal-800` | settled states |
| `.badge-closed` | `--se-sunken` | `--se-text-muted` | archived |
| `.badge-unpaid`, `.badge-overdue`, `.badge-occupied`, `.badge-high` | `--se-danger-50` | `--se-danger-text-on-tint` | urgent (overdue additionally 700-weight) |
| `.badge-reserved`, `.badge-medium` | `--se-warn-50` | `--se-warn-text-on-tint` | attention |
| `.badge-low` | `--se-sunken` | `--se-text-muted` | also current category-chip fallback |
| *new* `.badge-active` | `--se-teal-50` | `--se-teal-800` | polls (stop reusing `badge-paid`) |

### 3.5 Tables & lists
- **`.table-custom`** — full-width; `thead th`: 12px 600 uppercase `.04em` `--se-text-muted`, `background:var(--se-sunken)`, `padding:10px 20px`; `td`: `padding:12px 20px; border-top:1px solid var(--se-border); font-size:var(--se-fs-sm)`; row hover `background:var(--se-navy-50)`; numeric columns right-aligned + `tnum`. `<768px`: rows collapse to stacked cards (wrap table in `.table-responsive` now; card-collapse for the complaint table in P3).
- List rows currently hand-built with `style="border-bottom:1px solid #f1f5f9"` → class **`.list-row`** (`padding:14px 20px; border-top:1px solid var(--se-border)`; hover tint; last-child no border).

### 3.6 Forms
- **`.form-group`** — `margin-bottom:var(--se-sp-4)`.
- **`.form-label`** — 13px 500 `--se-ink`; required mark via `.is-required::after{content:" *"; color:var(--se-danger-600)}`.
- **`.form-control-custom`** — `width:100%; min-height:44px; padding:10px 14px; font-size:var(--se-fs-sm); color:var(--se-text); background:var(--se-surface); border:1px solid var(--se-border-strong); border-radius:var(--se-r-md); transition:border-color var(--se-t-med), box-shadow var(--se-t-med)`. Focus: `border-color:var(--se-navy-600); box-shadow:var(--se-ring); outline:none`. Error: `border-color:var(--se-danger-600)` + 13px danger message with icon below. Placeholder `--se-text-faint`. Selects get a navy chevron via inline SVG background.
- Inputs need `id` + `for` wiring (new `componenets/LoginPage.vue` lacks them) and real `<form @submit.prevent>` instead of `@keyup.enter` per field.

### 3.7 Empty states, loading, feedback
- **`.empty-state`** — `text-align:center; padding:var(--se-sp-8) var(--se-sp-6); color:var(--se-text-muted)`; icon 40px `--se-text-faint`; one line of *guidance*, then the action: "No complaints yet — raise one and track it to resolution here" + button when a create-action exists. Never a bare "No data".
- **`.spinner`** — retire the lone element for content areas; keep for buttons. Content loading = **`.skeleton`** (`background:linear-gradient(90deg, var(--se-sunken) 25%, #ECEBE6 50%, var(--se-sunken) 75%); background-size:200% 100%; animation:se-shimmer 1.2s linear infinite; border-radius:var(--se-r-sm)`) in stat/card shapes — kills layout shift (CLS < 0.1).
- **`.alert-custom`** (+ `.alert-error`, `.alert-success`) — tint bg, same-hue dark text, 4px left rail in the 600 hue, FA icon, `role="alert"`. Replaces the ✕-prefixed div in old login.
- *new* **`.toast-custom`** — fixed `bottom:24px; right:24px` (top-center on mobile), surface bg, `--se-shadow-3`, left rail semantic hue, auto-dismiss 4s, `aria-live="polite"`; slide-up 260ms `--se-ease-out`. Replaces every bare `alert()` (PollsPage vote failure) and silent `catch(e){}`.

### 3.8 Modals
- **`.modal-overlay`** — `position:fixed; inset:0; background:rgba(16,27,51,.48); display:grid; place-items:center; z-index:100; padding:16px`. No backdrop blur.
- **`.modal-box`** — `width:min(480px, 100%); background:var(--se-surface); border-radius:var(--se-r-lg); box-shadow:var(--se-shadow-3); max-height:90vh; overflow:auto`; entrance `scale(.97)→1` + fade 260ms. `role="dialog" aria-modal="true"`, focus-trap, Esc-close, focus first field (P3: tiny `useModal` composable; overlay click-to-close already wired via `@click.self`).
- **`.modal-header` / `.modal-body` / `.modal-footer`** — 16px 20px paddings; header 16px/600 ink + border-bottom; footer right-aligned actions, border-top, quiet Cancel + one primary.
- Mobile `<576px`: modal becomes bottom sheet (`align-items:end`, radius top-only, slide-up) — thumb-reach for the Raise Complaint and payment flows.

### 3.9 Progress
- **`.progress-bar-custom`** — `height:8px; background:var(--se-sunken); border-radius:var(--se-r-pill); overflow:hidden`.
- **`.progress-fill`** — `height:100%; border-radius:inherit; background:var(--se-navy-600); transition:width var(--se-t-count) var(--se-ease-out)` (fills from 0 on mount). Poll leader may use `--se-teal-600`; drop the inline `background:#1B2A4A`.
- *new* **`.se-rail`** — the lifecycle rail (§1 move 2): 4 dots + connecting line; done = teal fill + check, current = navy pulse (2 gentle iterations, then static), upcoming = `--se-border-strong`; labels 11px muted; `aria-label="Status: In progress, step 3 of 5"`.

---

## 4. Key screen redesigns

### 4.1 Login — `componenets/LoginPage.vue` (canonical; `components/LoginPage.vue` retires with the old app)
The new-app login is already the right skeleton (single card, demo-accounts hint, no fake OAuth — the old app's `alert('coming soon')` Google/Microsoft buttons are a trust liability and die with it). Redesign:
- **Layout:** warm canvas; ≥992px a 5/7 split — left panel `--se-navy-800` with marigold building glyph, wordmark, and three one-line value props (rupee/wrench/bullhorn icons: "Track every rupee" / "Complaints that resolve" / "One notice board"); right panel centered 400px card. `<992px`: card only, brand glyph on top.
- **Hierarchy:** wordmark → "Sign in to your society" (24px display) → fields → primary. Exactly one button: `.btn-primary-custom` full-width 48px "Sign in".
- **States:** inline field validation on blur; error `alert-custom` with `aria-live="assertive"`; loading = button spinner + "Signing in…" (exists — keep); success = 300ms teal check swap before route push.
- **Micro:** card fades/rises 8px on mount (260ms); logo glyph draws once; **no slideInLeft hero animation** (old app's 800ms entrance is noise).
- **Fix:** demo-accounts chip becomes collapsible `<details>` styled `--se-sunken` and is env-gated (`import.meta.env.DEV`) — never ship credentials to prod UI.

### 4.2 Register — canonical successor to `components/RegisterPage.vue` (rebuild in new app; `componenets/RegisterPage.vue` exists as base)
- **Two steps** with dot-progress: (1) You — name, email, phone, password + 3-segment strength meter (danger/warn/teal); (2) Your place — role as three selectable cards with icons (Owner `fa-key` / Tenant `fa-user` / Worker `fa-hard-hat`; 2px navy border + navy-50 fill when selected), flat number, move-in date.
- Submit → success empty-state: "Account created — the association will verify you" with teal check-draw. Primary per step: one navy button ("Continue" → "Create account").

### 4.3 Resident dashboard — `componenets/ResidentDashboard.vue`
Today: red full-width dues banner (panic register), two stat cards, two list cards. Redesign order:
1. **Greeting header:** "Good evening, Priya" (display 24px) + flat identity chip (`fa-home` B-304, pill, navy-50) — belonging, not admin UI.
2. **Hero next-action card** (replaces the alert banner): if dues — marigold-50 bg, marigold-400 4px left rail, "₹2,400 pending · due 20 Jul" (₹ 30px tabular), sub "Maintenance · Jul 2026", right-anchored `.btn-accent` "Pay now"; if clear — teal-50 card, check icon, "All dues clear. Nothing needs you today." Calm urgency, not alarm.
3. **Quick actions row:** 4 tiles 44px+ (Raise complaint / Book parking / Vote / Notices) — icon + label, surface bg, hover lift.
4. **Latest notices** (3, `.list-row`, relative dates "2d ago") and **My complaints** with mini `.se-rail` per row.
Micro: stat count-up; cards stagger-enter 40ms; complaint rail pulses current stop once.

### 4.4 Secretary/Manager dashboard — `componenets/SecretaryDashboard.vue`
Today: 4 stat cards + green/red collected/pending boxes + recent-complaints table. Redesign:
1. KPI row (4 `.stat-card`): Active members · Open complaints (sub-label "3 unassigned" in danger) · Unpaid invoices (₹ pending as sub-value) · Active polls.
2. **Collections module** replaces the twin green/red boxes (they double-encode one fact): single `.progress-bar-custom` teal fill — "₹1,23,000 of ₹1,80,000 collected · 68% · 12 flats pending", with quiet "Send reminders" action (backend permitting).
3. **Triage table** (the screen's real job): complaints with priority dot, age chip ("3d" — `--se-warn-600` >2d, danger >5d), flat, inline **Assign** (worker dropdown in popover). Primary action of the screen = clear the unassigned queue.
4. Quick actions: Bulk invoices (`.btn-accent`, its one conversion action) · Post notice · Create poll (outline).

### 4.5 Worker dashboard — `componenets/WorkerDashboard.vue`
A phone-in-the-field UI — design mobile-first:
- Header: "Today" + pending count pill; two stat tiles (Pending / Completed today) become compact chips on mobile.
- **Task queue:** cards sorted ASSIGNED-first with category icon chip, title 16px/600, flat number prominent (18px navy 700 — the field worker's key datum), priority pill, description 2-line clamp.
- **One thumb-sized action per card:** ASSIGNED → full-width 48px marigold "Start work"; IN_PROGRESS → teal "Mark done" (today's `btn-sm` ~31px is below the 44px floor — gloved thumbs).
- Completion modal → bottom sheet: remarks textarea + (P3) photo slot; confirm = teal check-draw + card slides to "Recently completed"; "Completed today" ticks up with a single scale pulse. Empty queue: teal check, "All caught up — nothing assigned right now."

### 4.6 Complaint lifecycle — `componenets/ComplaintsPage.vue` (+ Resident/Worker views)
States in code: `OPEN → ASSIGNED → IN_PROGRESS → COMPLETED → CLOSED`; priority LOW/MEDIUM/HIGH.
- **Raise (resident):** bottom-sheet form — category as icon chip-grid (Electrical, Plumbing, etc.), priority as 3-segment control (not a dropdown), title, description, (P3) photo. Submit → toast "Complaint #C-142 raised" + card appears with rail at stop 1.
- **Track:** every complaint card carries `.se-rail` + "last update 2h ago · assigned to Ramesh". Detail view = vertical timeline (actor, timestamp, remarks per transition) — the anti-black-hole. Status change → resident toast + notice entry.
- **Triage (manager):** filter pills above list (All / Open / Assigned / In progress / Completed — replaces the `<select>`); Assign inline; Delete demoted behind an ellipsis overflow menu with confirm (a naked always-visible trash button beside Assign invites misclicks).
- **Complete (worker):** §4.5 flow feeds the same rail; COMPLETED→CLOSED is the manager's explicit sign-off, labeled "Verify & close".

### 4.7 Invoice & payment — `componenets/InvoicesPage.vue`
States: `PAID / UNPAID / OVERDUE`.
- **Resident:** dues summary hero (total pending ₹, tabular, en-IN — fix the raw `₹{{ inv.amount }}`), then invoice cards: period, amount right-aligned 20px tabular navy, relative due chip ("Due in 5d" warn-tint; "Overdue 3d" danger); primary `.btn-accent` "Pay ₹2,400" → payment sheet: UPI-first (upi:// deep link / QR when backend lands; until then the existing admin-recorded UPI/Cash stays admin-side), then confirmation = **receipt artifact** (§1 move 3): bordered card, dashed perforation edge (`border-top:2px dashed var(--se-border-strong)`), receipt no. + flat + period + amount + mode rows (structure already in markup — restyle), teal check-draw header, Download action. Paid history collapses under "Earlier".
- **Admin:** Bulk Generate keeps `.btn-accent`; **add a preview step**: "This creates 42 invoices for 7/2026 · ₹63,000 total" with flat count before commit (bulk money actions never fire blind); single-invoice demotes to outline; mark-paid buttons live in a per-row overflow on mobile.

---

## 5. Accessibility & responsive

### Contrast (computed, WCAG 2.1)
| Pair | Ratio | Verdict |
|---|---|---|
| navy-800 `#1B2A4A` on white | 14.0:1 | AAA — body-safe |
| teal-600 `#0E7C7B` on white | 5.0:1 | AA text ✓ |
| marigold-400 `#F2A541` on white | 2.05:1 | **fails — never text/icon-alone on light** |
| navy-800 on marigold-400 | 6.8:1 | AA ✓ — the CTA pairing |
| danger-600 `#DC2626` on white | 4.8:1 | AA ✓ |
| warn-600 `#D97706` on white | 3.2:1 | large/icon only; small text uses `#92400E` on `--se-warn-50` |
| text-muted `#5F6878` on white | 5.6:1 | AA ✓ (replaces `#718096` @ 4.1:1, which fails at 13px) |
| sidebar item `rgba(255,255,255,.72)` on navy-800 | ~7.5:1 | AA ✓ |

### Non-negotiables
- **Focus:** global `:focus-visible { outline:2px solid var(--se-navy-600); outline-offset:2px }` + `--se-ring` on inputs; never `outline:none` bare (scaffold's `-webkit-focus-ring-color` rule dies).
- **Tap targets:** ≥44×44 for all resident/worker actions (audit every `btn-sm`: worker Start/Done, parking Reserve, invoice mark-paid).
- **Status = color + text + dot/icon** everywhere (pills §3.4, parking slot cards keep the 4px top border *plus* label).
- **Modals:** focus trap, Esc, `aria-modal`, initial focus, return focus on close. **Toasts/errors:** `aria-live`. **Forms:** visible labels (already the norm — keep), `id/for`, `autocomplete` on auth fields.
- **Kill auto dark-mode:** remove `color-scheme: light dark` + the `prefers-color-scheme` block and the white-on-white root bug with the scaffold. Deliberate light theme now; dark is a token remap later.
- **Language/format:** `<html lang="en">`, title "SocietyEase", en-IN dates (exists in topbar) and digit grouping everywhere; font stack ships Devanagari-ready siblings (§2.2).

### Responsive (residents live on phones)
- Breakpoints = Bootstrap's (576/768/992/1200). Mobile-first for Resident + Worker screens.
- **`<992px`: sidebar → bottom tab bar** (`.tabbar`, 56px + safe-area inset): Resident = Home / Pay / Complaints / More; Worker = Tasks / Notices / More; Admin keeps a hamburger drawer (12 items don't fit tabs). Topbar shrinks to 56px, title only.
- Stat grids: `col-6 col-md-3` already correct — keep; quick actions 2×2 on mobile.
- Tables → stacked cards `<768px` (§3.5); modals → bottom sheets `<576px` (§3.8); sticky bottom CTA on mobile forms (Pay / Submit complaint).
- Type floor 14px on mobile for interactive text; page gutter 16px.

---

## 6. Cleanup & migration (per Main's canonicalization call)

**Decision: the `componenets/` app is canonical. The `components/` old app + `routes.js` retire.** The physical folder fix and router fix are one elegant move:

1. **Retire old app:** delete (git history preserves; or park in `src/legacy/` for one sprint) `components/`: `Home.vue`, `HelloWorld.vue`, `TenantDashboard.vue`, `TenantNavbar.vue`, `TenantComplaint.vue`, `TenantComplaintDetails.vue`, `AssociationManager.vue`, `AssociationNavBar.vue`, `Associationcomplaint.vue`, `AssociationInvoice.vue`, `AddComplaint.vue`, `ComplaintDetail.vue`, `InvoiceDetail.vue`, `Members.vue`, `AddMember.vue`, `EditMember.vue`, `AddAnnouncement.vue`, `EditAnnouncement.vue`, and old `LoginPage.vue`/`RegisterPage.vue`.
2. **Move the 17 canonical files** `componenets/*` → `components/` (correct spelling), delete `componenets/`. **`router/index.js`'s imports (`../components/...`) become valid with zero edits** — the "broken" router was written for the correctly-spelled world.
3. **Swap routers:** `main.js`: `import router from './router'`; delete `routes.js`. The `/app/*` nested IA + role guards in `router/index.js` are the right architecture — keep. Verify old deep-links: add `{ path:'/tenant-dashboard', redirect:'/app/home' }`, `{ path:'/association_manager', redirect:'/app/dashboard' }`.
4. **`App.vue`:** delete the dead `import HelloWorld from './components/HelloWorld.vue'`; keep `<router-view/>`; `.page-container` defined per §3.1.
5. **`style.css`:** delete scaffold content wholesale; new content = §2 tokens + Bootstrap layer + §3 component classes (~500 lines, one file per Main's call; optional later split into `styles/tokens.css|components.css`).
6. **`index.html`:** `<title>SocietyEase</title>`, `<meta name="theme-color" content="#1B2A4A">`, font preconnect+load (§2.2), real favicon (navy rounded square, marigold building glyph — matches sidebar brand).
7. **Icons:** `npm i @fortawesome/fontawesome-free` + `import '@fortawesome/fontawesome-free/css/all.min.css'` in `main.js` — unbreaks every icon in the app today. (Later: self-host subset.)
8. **Inline-style purge:** mechanical sweep of `componenets/*.vue` replacing inline hexes with §3 classes/modifiers. **Acceptance gate: `grep '#[0-9a-fA-F]{6}' src/components/*.vue` → 0 matches** (all color lives in `style.css`).
9. Consolidate dup auth helpers (`store/auth.js` is canonical; `utils/auth.js`'s `getApiBase` moves to `api/index.js`).

### Team mapping & phasing (Milestone 2)
- **P0 (0.5d) — Mani Shankar:** steps 1–4, 7 (migration, router, icons). Unblocks everything; app finally *mounts* the good UI.
- **P1 (1d) — Pratik:** step 5–6 (style.css system §2–§3). All 15 pages light up.
- **P2 (1–1.5d) — Pratik:** shell + Login + three dashboards (§4.1–4.5) incl. inline-style purge on those files.
- **P3 (1–1.5d) — Pratik + Mani:** complaint rail + invoice/receipt flows (§4.6–4.7), toasts, bottom tabs; **Nikhilesh:** API fields the UI needs — status-transition timestamps/actor for the rail, receipt numbers, collection totals.
- **P4 (0.5d) — Praket:** a11y + visual QA against §5 checklist (axe pass, keyboard-only run, 360px viewport run); **Madhumathi:** Kanban phases, before/after screenshots for the Milestone-2 review doc.

### Success metrics
- Lighthouse Accessibility ≥ 95 on Login, Resident dashboard, Complaints; zero axe critical issues.
- CLS < 0.1 (skeletons), login → first meaningful action < 10s for a new resident.
- Grep gates: 0 inline hex in `.vue` files; 0 `alert(` calls; 0 emoji icons in card headers.
- Every text pair in the UI passes AA per §5 table.

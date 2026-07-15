<template>
  <div class="events-page">
    <!-- Header -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Upcoming events</h1>
        <p class="se-subtitle">
          <i class="fas fa-champagne-glasses" aria-hidden="true"></i>
          What's happening around your society
        </p>
      </div>

      <div class="header-chips">
        <span class="se-chip se-chip--navy">
          <i class="fas fa-calendar-days" aria-hidden="true"></i>
          <span class="se-num">{{ events.length }}</span> upcoming
        </span>
        <span v-if="attendingCount" class="se-chip se-chip--teal">
          <i class="fas fa-circle-check" aria-hidden="true"></i>
          Going to <span class="se-num">{{ attendingCount }}</span>
        </span>
      </div>
    </div>

    <!-- Event grid -->
    <div v-if="events.length" class="row g-3">
      <div v-for="(e, i) in events" :key="e.id" class="col-md-6">
        <article
          class="card event-card"
          :style="{ '--ev-accent': e.accent, '--ev-delay': (i * 70) + 'ms' }"
        >
          <!-- Accent cover band -->
          <div class="event-cover">
            <span class="cover-emoji" aria-hidden="true">{{ e.emoji }}</span>
            <span class="cover-chip se-num">{{ countdown(e.date) }}</span>
          </div>

          <div class="event-body">
            <h2 class="event-title">{{ e.title }}</h2>

            <ul class="event-meta">
              <li>
                <i class="fas fa-calendar" aria-hidden="true"></i>
                <span>{{ humanDate(e.date) }}</span>
              </li>
              <li>
                <i class="fas fa-clock" aria-hidden="true"></i>
                <span class="se-num">{{ e.time }}</span>
              </li>
              <li>
                <i class="fas fa-location-dot" aria-hidden="true"></i>
                <span>{{ e.venue }}</span>
              </li>
            </ul>

            <p class="event-desc">{{ e.desc }}</p>

            <div class="event-foot">
              <div class="going-row" :title="goingTitle(e)">
                <div class="going-stack" aria-hidden="true">
                  <span
                    v-for="(name, j) in e.going.slice(0, 4)"
                    :key="name + j"
                    class="se-avatar se-avatar--sm"
                    :class="avatarClass(j)"
                  >{{ initials(name) }}</span>
                  <span
                    v-if="extraGoing(e) > 0"
                    class="se-avatar se-avatar--sm going-stack__more se-num"
                  >+{{ extraGoing(e) }}</span>
                </div>
                <span class="going-count">
                  <strong class="se-num">{{ e.goingCount }}</strong> going
                </span>
              </div>

              <button
                type="button"
                class="rsvp-btn"
                :class="{ 'is-going': e.imAttending }"
                :aria-pressed="e.imAttending"
                :title="e.imAttending ? 'Tap to cancel your RSVP' : 'Reserve your spot'"
                @click="onRSVP(e)"
              >
                <i v-if="!e.imAttending" class="fas fa-user-plus" aria-hidden="true"></i>
                {{ e.imAttending ? 'Going ✓' : 'RSVP' }}
              </button>
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state card">
      <i class="fas fa-calendar-xmark"></i>
      <p>
        Nothing on the calendar yet.<br />
        New celebrations and meet-ups appear here the moment they're announced.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { demo } from '../store/demo'
import { useCelebrate } from '../composables/useCelebrate'

const { reward, toast } = useCelebrate()

// Soonest first — reactive against the shared store.
const events = computed(() => [...demo.events].sort((a, b) => a.date.localeCompare(b.date)))
const attendingCount = computed(() => demo.events.filter(e => e.imAttending).length)

// ── Avatar cluster helpers ────────────────────────────────────
const AVATAR_VARIANTS = ['', 'se-avatar--teal', 'se-avatar--marigold']
const avatarClass = (j) => AVATAR_VARIANTS[j % AVATAR_VARIANTS.length]
const initials = (name) => name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
const extraGoing = (e) => Math.max(0, e.goingCount - Math.min(e.going.length, 4))
const goingTitle = (e) =>
  'Going: ' + e.going.slice(0, 4).join(', ') + (extraGoing(e) ? ` and ${extraGoing(e)} more` : '')

// ── Date helpers ──────────────────────────────────────────────
function daysUntil(dateStr) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return Math.round((new Date(dateStr + 'T00:00:00') - today) / 86400000)
}
function countdown(dateStr) {
  const n = daysUntil(dateStr)
  if (n < 0) return 'Ended'
  if (n === 0) return 'Today'
  if (n === 1) return 'Tomorrow'
  return `in ${n} days`
}
// 'Sat, 25 Jul'
function humanDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-GB', { weekday: 'short' }) + ', ' +
    d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

// ── RSVP ──────────────────────────────────────────────────────
function onRSVP(e) {
  const attending = demo.toggleRSVP(e.id)
  if (attending) reward(10, 'RSVP’d to ' + e.title)
  else toast('RSVP cancelled', 'info')
}
</script>

<style scoped>
.se-subtitle {
  margin: 4px 0 0;
  color: var(--se-text-muted);
  font-size: var(--se-fs-sm);
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.se-subtitle i { color: var(--se-teal-600); }

.header-chips {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* ── Event card ─────────────────────────────────────── */
.event-card {
  padding: 0;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow var(--se-t-med) var(--se-ease-std),
              transform var(--se-t-med) var(--se-ease-out);
  animation: ev-enter var(--se-t-slow) var(--se-ease-out) both;
  animation-delay: var(--ev-delay, 0ms);
}
.event-card:hover {
  box-shadow: var(--se-shadow-2);
  transform: translateY(-3px);
}

/* ── Accent cover band ──────────────────────────────── */
.event-cover {
  position: relative;
  height: 96px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--se-sp-5);
  background:
    radial-gradient(120% 170% at 88% -30%, rgba(255, 255, 255, .30), transparent 55%),
    linear-gradient(135deg,
      var(--ev-accent, var(--se-navy-600)),
      color-mix(in srgb, var(--ev-accent, var(--se-navy-600)) 78%, var(--se-navy-950)));
}
.cover-emoji {
  font-size: 44px;
  line-height: 1;
  filter: drop-shadow(0 4px 8px rgba(16, 27, 51, .28));
  transition: transform var(--se-t-slow) var(--se-ease-out);
}
.event-card:hover .cover-emoji { transform: scale(1.12) rotate(-4deg); }
.cover-chip {
  background: rgba(255, 255, 255, .92);
  color: var(--se-navy-900); /* deliberate: stays ink-dark on the accent band in both themes */
  font-size: var(--se-fs-2xs);
  font-weight: 700;
  letter-spacing: .01em;
  padding: 5px 11px;
  border-radius: var(--se-r-pill);
  box-shadow: var(--se-shadow-1);
}

/* ── Body ───────────────────────────────────────────── */
.event-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: var(--se-sp-5);
}
.event-title {
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-lg);
  color: var(--se-ink);
  line-height: 1.25;
  margin: 0 0 var(--se-sp-3);
}
.event-meta {
  list-style: none;
  margin: 0 0 var(--se-sp-3);
  padding: 0;
  display: grid;
  gap: 6px;
}
.event-meta li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--se-fs-sm);
  color: var(--se-text);
}
.event-meta i {
  width: 18px;
  text-align: center;
  color: var(--se-teal-600);
  font-size: var(--se-fs-xs);
}
.event-desc {
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
  margin: 0 0 var(--se-sp-4);
}

/* ── Footer: going cluster + RSVP ───────────────────── */
.event-foot {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: var(--se-sp-4);
  border-top: 1px solid var(--se-border);
}
.going-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.going-stack { display: flex; align-items: center; }
.going-stack .se-avatar {
  box-shadow: 0 0 0 2px var(--se-surface); /* ring separates overlapped faces */
}
.going-stack .se-avatar + .se-avatar { margin-left: -9px; }
.going-stack__more {
  background: var(--se-sunken);
  color: var(--se-text-muted);
  font-size: 0.7rem;
  letter-spacing: -.02em;
}
.going-count {
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
  white-space: nowrap;
}
.going-count strong { color: var(--se-ink); font-weight: 700; }

.rsvp-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 10px 18px;
  border-radius: var(--se-r-md);
  border: 1px solid var(--se-navy-800);
  background: var(--se-navy-800);
  color: #fff;
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-sm);
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--se-t-med) var(--se-ease-std),
              border-color var(--se-t-med) var(--se-ease-std),
              box-shadow var(--se-t-med) var(--se-ease-std),
              transform var(--se-t-fast) var(--se-ease-out);
}
.rsvp-btn:hover {
  background: var(--se-navy-700);
  border-color: var(--se-navy-700);
  transform: translateY(-1px);
  box-shadow: var(--se-shadow-2);
}
.rsvp-btn:active { transform: scale(.97); }
.rsvp-btn:focus-visible { outline: 2px solid var(--se-teal-600); outline-offset: 2px; }
.rsvp-btn.is-going {
  background: var(--se-teal-600);
  border-color: var(--se-teal-600);
}
.rsvp-btn.is-going:hover {
  background: var(--se-teal-700);
  border-color: var(--se-teal-700);
}

/* ── Entrance motion ────────────────────────────────── */
@keyframes ev-enter {
  from { opacity: 0; transform: translateY(14px) scale(.98); }
  to   { opacity: 1; transform: none; }
}

/* ── Mobile ─────────────────────────────────────────── */
@media (max-width: 575.98px) {
  .rsvp-btn { width: 100%; }
}

@media (prefers-reduced-motion: reduce) {
  .event-card { animation: none; }
  .event-card:hover { transform: none; }
  .event-card:hover .cover-emoji { transform: none; }
}
</style>

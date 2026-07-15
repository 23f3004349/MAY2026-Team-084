<template>
  <div>
    <!-- ══ Skeleton — mirrors the real layout so nothing shifts ══ -->
    <div v-if="loading" role="status" aria-busy="true">
      <span class="visually-hidden">Loading your home feed…</span>

      <div class="home-hello" aria-hidden="true">
        <div>
          <div class="sk sk--title"></div>
          <div class="sk sk--sub"></div>
        </div>
        <div class="sk sk--chip"></div>
      </div>

      <div class="row g-3 mb-4" aria-hidden="true">
        <div class="col-12 col-lg-8 order-1"><div class="sk sk--hero"></div></div>
        <div class="col-12 order-2 order-lg-3"><div class="sk sk--bar"></div></div>
        <div class="col-12 col-lg-4 order-3 order-lg-2"><div class="sk sk--hero"></div></div>
      </div>

      <div class="sk sk--section mb-3" aria-hidden="true"></div>
      <div class="row g-3 mb-4" aria-hidden="true">
        <div v-for="n in 4" :key="n" class="col-6 col-lg-3"><div class="sk sk--tile"></div></div>
      </div>

      <div class="row g-3" aria-hidden="true">
        <div class="col-lg-7"><div class="sk sk--card"></div></div>
        <div class="col-lg-5"><div class="sk sk--card"></div></div>
      </div>
    </div>

    <div v-else>
      <!-- ══ Greeting ══════════════════════════════════════════ -->
      <header class="home-hello rise">
        <div>
          <h1 class="hello-title">Good {{ daypart }}, {{ user.first }} 👋</h1>
          <p class="hello-date">{{ todayLabel }}</p>
        </div>
        <span class="se-chip se-chip--navy"><i class="fas fa-home" aria-hidden="true"></i>Flat {{ user.flat }}</span>
      </header>

      <!-- ══ Heroes: check-in → dues → level (mobile order) ═════ -->
      <div class="row g-3 mb-4">
        <!-- Daily check-in -->
        <div class="col-12 col-lg-8 order-1 rise rise--1">
          <div class="card checkin-card" :class="engagement.hasCheckedInToday ? 'checkin-card--done' : 'checkin-card--due'">
            <template v-if="!engagement.hasCheckedInToday">
              <div class="checkin-icon"><i class="fas fa-fire flame" aria-hidden="true"></i></div>
              <div class="checkin-body">
                <p class="checkin-kicker">Daily check-in</p>
                <p class="checkin-title">
                  <template v-if="engagement.checkInStreak > 0">You’re on a {{ engagement.checkInStreak }}-day streak 🔥</template>
                  <template v-else>Start your streak today 🔥</template>
                </p>
                <p class="checkin-sub">Show up every day to earn Neighbour Points and streak badges.</p>
              </div>
              <button type="button" class="btn-primary-custom checkin-btn" @click="onCheckIn">
                <i class="fas fa-calendar-check" aria-hidden="true"></i>Check in
              </button>
            </template>
            <template v-else>
              <div class="checkin-icon"><i class="fas fa-circle-check" aria-hidden="true"></i></div>
              <div class="checkin-body">
                <p class="checkin-kicker">Daily check-in</p>
                <p class="checkin-title">Checked in today ✓</p>
                <p class="checkin-sub">Nice consistency! Come back tomorrow to keep the fire going.</p>
              </div>
              <span class="se-chip se-chip--teal checkin-chip"><i class="fas fa-fire flame" aria-hidden="true"></i>{{ engagement.checkInStreak }}-day streak</span>
            </template>
          </div>
        </div>

        <!-- Dues hero — THE next action when money is pending -->
        <div class="col-12 order-2 order-lg-3 rise rise--2">
          <div v-if="unpaidInvoices.length > 0" class="card dues-hero dues-hero--due">
            <div class="dues-icon"><i class="fas fa-file-invoice" aria-hidden="true"></i></div>
            <div class="dues-body">
              <p class="dues-amount"><span class="se-num">₹{{ unpaidTotal }}</span> pending</p>
              <p class="dues-sub">
                {{ unpaidInvoices.length }} unpaid invoice{{ unpaidInvoices.length === 1 ? '' : 's' }} —
                pay before the due date to protect your payment streak.
              </p>
            </div>
            <router-link to="/app/invoices" class="btn-accent dues-btn">Pay now<i class="fas fa-arrow-right" aria-hidden="true"></i></router-link>
          </div>
          <div v-else-if="!loadError" class="card dues-hero dues-hero--clear">
            <div class="dues-icon"><i class="fas fa-circle-check" aria-hidden="true"></i></div>
            <div class="dues-body">
              <p class="dues-amount">All dues clear</p>
              <p class="dues-sub">Nothing pending on your maintenance account — thanks for paying on time.</p>
            </div>
            <span class="se-chip se-chip--teal"><i class="fas fa-bolt" aria-hidden="true"></i>{{ engagement.paymentStreak }}-month streak</span>
          </div>
          <div v-else class="card dues-hero dues-hero--unknown">
            <div class="dues-icon"><i class="fas fa-cloud-arrow-down" aria-hidden="true"></i></div>
            <div class="dues-body">
              <p class="dues-amount">Couldn’t load your dues</p>
              <p class="dues-sub">The society server didn’t respond. Retry to see your latest invoices and complaints.</p>
            </div>
            <button type="button" class="btn-primary-custom dues-btn" @click="loadData">
              <i class="fas fa-rotate-right" aria-hidden="true"></i>Retry
            </button>
          </div>
        </div>

        <!-- Level mini-widget -->
        <div class="col-12 col-lg-4 order-3 order-lg-2 rise rise--3">
          <div class="card level-card">
            <div class="level-top">
              <div class="level-icon"><i :class="`fas ${engagement.level.icon}`" aria-hidden="true"></i></div>
              <div class="level-id">
                <span class="level-name">{{ engagement.level.name }}</span>
                <span class="level-points"><span class="se-num">{{ engagement.points }}</span> Neighbour Points</span>
              </div>
              <router-link to="/app/rewards" class="level-link" aria-label="Open rewards">
                <i class="fas fa-chevron-right" aria-hidden="true"></i>
              </router-link>
            </div>
            <div class="progress-bar-custom" role="progressbar" :aria-valuenow="Math.round(engagement.levelProgress)" aria-valuemin="0" aria-valuemax="100">
              <div class="progress-fill" :style="{ width: engagement.levelProgress + '%' }"></div>
            </div>
            <p v-if="engagement.nextLevel" class="level-next">
              <span class="se-num">{{ engagement.npToNext }}</span> NP to <strong>{{ engagement.nextLevel.name }}</strong>
            </p>
            <p v-else class="level-next">Top level reached — you’re a legend! 👑</p>
          </div>
        </div>
      </div>

      <!-- ══ Quick actions — the four pillars ═══════════════════ -->
      <div class="rise rise--4">
        <h2 class="se-section-title mb-3">Quick actions</h2>
        <div class="row g-3 mb-4">
          <div v-for="qa in quickActions" :key="qa.to" class="col-6 col-lg-3">
            <router-link :to="qa.to" class="qa-tile">
              <span class="qa-icon" :class="qa.tint"><i :class="`fas ${qa.icon}`" aria-hidden="true"></i></span>
              <span class="qa-text">
                <span class="qa-label">{{ qa.label }}</span>
                <span class="qa-hint">{{ qa.hint }}</span>
              </span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- ══ Society pulse + my complaints ══════════════════════ -->
      <div class="row g-3 rise rise--5">
        <div class="col-lg-7">
          <div class="card flow-card h-100 d-flex flex-column">
            <div class="card-header-custom"><span class="live-dot" aria-hidden="true"></span>Happening in your society</div>

            <div v-if="topPosts.length === 0" class="empty-state p-4">
              <i class="fas fa-comments" aria-hidden="true"></i>
              <p>All quiet right now — say hello and start the conversation.</p>
            </div>

            <router-link v-for="(p, i) in topPosts" :key="p.id" to="/app/community" class="feed-row">
              <span class="se-avatar se-avatar--sm" :class="i === 1 ? 'se-avatar--teal' : ''">{{ p.initials }}</span>
              <span class="feed-main">
                <span class="feed-line"><strong>{{ p.author }}</strong> <span class="feed-meta">· {{ p.flat }} · {{ p.time }}</span></span>
                <span class="feed-snippet">{{ snippet(p.text) }}</span>
                <span class="feed-stats">
                  <span><i class="fas fa-heart" aria-hidden="true"></i>{{ reactionsOf(p) }}</span>
                  <span><i class="fas fa-comment" aria-hidden="true"></i>{{ p.comments?.length || 0 }}</span>
                </span>
              </span>
              <i class="fas fa-chevron-right feed-go" aria-hidden="true"></i>
            </router-link>

            <router-link to="/app/community" class="card-footer-link mt-auto">Open community wall<i class="fas fa-chevron-right" aria-hidden="true"></i></router-link>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="card flow-card h-100 d-flex flex-column">
            <div class="card-header-custom d-flex justify-content-between align-items-center gap-2">
              <span>🔧 My complaints</span>
              <span v-if="openComplaints > 0" class="se-chip se-chip--marigold"><span class="se-num">{{ openComplaints }}</span> open</span>
            </div>

            <div v-if="myComplaints.length === 0" class="empty-state p-4">
              <template v-if="loadError">
                <i class="fas fa-triangle-exclamation" aria-hidden="true"></i>
                <p>Complaints couldn’t load — hit Retry above.</p>
              </template>
              <template v-else>
                <i class="fas fa-check-circle" style="color: var(--se-teal-600);" aria-hidden="true"></i>
                <p>No complaints — all good in your flat!</p>
              </template>
            </div>

            <div v-for="c in myComplaints.slice(0, 4)" :key="c.id" class="list-row">
              <div class="d-flex justify-content-between align-items-center gap-2">
                <p class="row-title">{{ c.title }}</p>
                <span class="badge-custom" :class="`badge-${c.status.toLowerCase().replace('_', '-')}`">{{ c.status.replace('_', ' ') }}</span>
              </div>
              <small class="row-date se-num">{{ c.created_at?.slice(0, 10) }}</small>
            </div>

            <router-link to="/app/complaints" class="card-footer-link mt-auto">View all complaints<i class="fas fa-chevron-right" aria-hidden="true"></i></router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { invoicesAPI, complaintsAPI } from '../api/index'
import { authStore } from '../store/auth'
import { engagement } from '../store/engagement'
import { demo, me } from '../store/demo'
import { useCelebrate } from '../composables/useCelebrate'

const { celebrate } = useCelebrate()

// ── Data fetching (invoices + complaints) ──────────────────────
const loading = ref(true)
const loadError = ref(false)
const unpaidInvoices = ref([])
const unpaidTotal = ref(0)
const myComplaints = ref([])

async function loadData() {
  loading.value = true
  loadError.value = false
  try {
    const [inv, comp] = await Promise.all([invoicesAPI.getAll(), complaintsAPI.getAll()])
    unpaidInvoices.value = inv.data.filter(i => i.status !== 'PAID')
    unpaidTotal.value = unpaidInvoices.value.reduce((s, i) => s + i.amount, 0).toLocaleString('en-IN')
    myComplaints.value = comp.data
  } catch (e) {
    loadError.value = true
  }
  loading.value = false
}
onMounted(loadData)

// ── Greeting ───────────────────────────────────────────────────
const daypart = (() => {
  const h = new Date().getHours()
  return h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening'
})()
const todayLabel = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })
const user = computed(() => ({
  first: (authStore.user?.name || me().name).split(' ')[0],
  flat: authStore.user?.flat_number || me().flat,
}))

// ── Daily check-in ─────────────────────────────────────────────
function onCheckIn() {
  const res = engagement.checkIn()
  if (res.already) return
  celebrate({ title: 'Checked in!', subtitle: `${res.streak}-day streak`, icon: 'fa-fire', points: res.gained })
}

// ── Society feed (community wall only — the kept pillar) ──────
const topPosts = computed(() => demo.wallPosts.slice(0, 2))
const snippet = (t, n = 96) => (t.length > n ? t.slice(0, n).trimEnd() + '…' : t)
const reactionsOf = (p) => Object.values(p.reactions || {}).reduce((a, b) => a + b, 0)

// ── Quick actions with live hints ──────────────────────────────
const openComplaints = computed(() =>
  myComplaints.value.filter(c => c.status !== 'RESOLVED' && c.status !== 'CLOSED').length)
const openSlots = computed(() =>
  demo.amenities.reduce((n, a) => n + a.slots.filter(s => s.status === 'available').length, 0))
const quickActions = computed(() => [
  { to: '/app/invoices', icon: 'fa-rupee-sign', label: 'Pay dues', tint: 'qa-icon--marigold',
    hint: unpaidInvoices.value.length ? `₹${unpaidTotal.value} pending` : loadError.value ? 'View invoices' : 'All clear' },
  { to: '/app/complaints', icon: 'fa-screwdriver-wrench', label: 'Raise complaint', tint: 'qa-icon--warn',
    hint: openComplaints.value ? `${openComplaints.value} open` : 'Report an issue' },
  { to: '/app/community', icon: 'fa-comments', label: 'Community', tint: 'qa-icon--teal',
    hint: `${demo.wallPosts.length} recent posts` },
  { to: '/app/amenities', icon: 'fa-calendar-check', label: 'Book amenity', tint: 'qa-icon--navy',
    hint: `${openSlots.value} slots open today` },
])
</script>

<style scoped>
/* ── Entrance stagger (uses global se-rise keyframes) ── */
.rise { animation: se-rise var(--se-t-slow) var(--se-ease-out) both; }
.rise--1 { animation-delay: 40ms; }
.rise--2 { animation-delay: 90ms; }
.rise--3 { animation-delay: 140ms; }
.rise--4 { animation-delay: 190ms; }
.rise--5 { animation-delay: 240ms; }

/* ── Skeleton (token-only, dark-mode safe) ── */
.sk {
  background: var(--se-sunken);
  border: 1px solid var(--se-border);
  border-radius: var(--se-r-lg);
  animation: sk-pulse 1.3s var(--se-ease-std) infinite;
}
@keyframes sk-pulse { 0%, 100% { opacity: .55; } 50% { opacity: 1; } }
.sk--title { width: min(280px, 60vw); height: 30px; border-radius: var(--se-r-md); }
.sk--sub { width: 170px; height: 14px; margin-top: 8px; border-radius: var(--se-r-md); }
.sk--chip { width: 96px; height: 32px; border-radius: var(--se-r-pill); }
.sk--hero { height: 118px; }
.sk--bar { height: 96px; }
.sk--section { width: 150px; height: 20px; border-radius: var(--se-r-md); }
.sk--tile { height: 118px; }
.sk--card { height: 248px; }

/* ── Greeting header ── */
.home-hello {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px 16px;
  flex-wrap: wrap;
  margin-bottom: var(--se-sp-5);
}
.hello-title { margin: 0; font-size: var(--se-fs-2xl); font-weight: 700; }
.hello-date { margin: 4px 0 0; color: var(--se-text-muted); font-size: var(--se-fs-sm); }

/* ── Daily check-in card ── */
.checkin-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: var(--se-sp-5);
  height: 100%;
  flex-wrap: wrap;
  transition: background-color var(--se-t-slow) var(--se-ease-std), border-color var(--se-t-slow) var(--se-ease-std);
}
.checkin-card--due { background: var(--se-marigold-50); border-color: var(--se-marigold-100); }
.checkin-card--done { background: var(--se-teal-50); border-color: var(--se-teal-100); }
.checkin-icon {
  width: 52px; height: 52px; border-radius: 50%;
  display: grid; place-items: center;
  font-size: 20px; flex-shrink: 0;
}
.checkin-card--due .checkin-icon { background: var(--se-marigold-400); color: var(--se-navy-800); }
.checkin-card--done .checkin-icon { background: var(--se-teal-600); color: #fff; }
.checkin-body { flex: 1; min-width: 220px; }
.checkin-kicker {
  margin: 0;
  font-size: var(--se-fs-2xs); font-weight: 700;
  letter-spacing: .06em; text-transform: uppercase;
  color: var(--se-marigold-600);
}
.checkin-card--done .checkin-kicker { color: var(--se-teal-800); }
.checkin-title {
  margin: 2px 0 0;
  font-family: var(--se-font-display); font-weight: 700;
  font-size: var(--se-fs-lg); color: var(--se-ink);
}
.checkin-sub { margin: 2px 0 0; font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.checkin-btn, .checkin-chip { flex-shrink: 0; }
.checkin-btn { min-height: 44px; }

/* ── Live flame flicker ── */
.flame {
  display: inline-block;
  transform-origin: 50% 82%;
  animation: flame-flicker 1.7s var(--se-ease-std) infinite;
}
@keyframes flame-flicker {
  0%, 100% { transform: scale(1) rotate(-3deg); }
  40%      { transform: scale(1.12) rotate(2deg); }
  70%      { transform: scale(1.05) rotate(-1deg); }
}

/* ── Level widget ── */
.level-card {
  padding: var(--se-sp-5);
  height: 100%;
  display: flex; flex-direction: column; justify-content: center;
  gap: 12px;
}
.level-top { display: flex; align-items: center; gap: 12px; }
.level-icon {
  width: 44px; height: 44px; border-radius: var(--se-r-md);
  background: var(--se-navy-50); color: var(--se-navy-700);
  display: grid; place-items: center; font-size: 18px; flex-shrink: 0;
}
.level-id { display: flex; flex-direction: column; min-width: 0; }
.level-name { font-family: var(--se-font-display); font-weight: 700; color: var(--se-ink); }
.level-points { font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.level-link {
  margin-left: auto;
  width: 44px; height: 44px; border-radius: 50%;
  display: grid; place-items: center;
  color: var(--se-text-faint); font-size: 12px; flex-shrink: 0;
  transition: background-color var(--se-t-fast) var(--se-ease-std), color var(--se-t-fast) var(--se-ease-std), transform var(--se-t-fast) var(--se-ease-out);
}
.level-link:hover { background: var(--se-sunken); color: var(--se-navy-700); transform: translateX(2px); }
.level-next { margin: 0; font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.level-card .progress-fill { animation: fill-grow .9s var(--se-ease-out) .35s both; }
@keyframes fill-grow { from { width: 0; } }

/* ── Dues hero ── */
.dues-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: var(--se-sp-5);
  flex-wrap: wrap;
  border-left: 4px solid transparent;
}
.dues-hero--due { background: var(--se-marigold-50); border-color: var(--se-marigold-100); border-left-color: var(--se-marigold-400); }
.dues-hero--clear { background: var(--se-teal-50); border-color: var(--se-teal-100); border-left-color: var(--se-teal-600); }
.dues-hero--unknown { border-left-color: var(--se-navy-700); }
.dues-icon {
  width: 46px; height: 46px; border-radius: var(--se-r-md);
  display: grid; place-items: center; font-size: 18px; flex-shrink: 0;
}
.dues-hero--due .dues-icon { background: var(--se-marigold-400); color: var(--se-navy-800); }
.dues-hero--clear .dues-icon { background: var(--se-teal-600); color: #fff; }
.dues-hero--unknown .dues-icon { background: var(--se-navy-50); color: var(--se-navy-700); }
.dues-body { flex: 1; min-width: 220px; }
.dues-amount { margin: 0; font-family: var(--se-font-display); font-weight: 700; font-size: var(--se-fs-xl); color: var(--se-ink); }
.dues-sub { margin: 2px 0 0; font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.dues-btn { flex-shrink: 0; min-height: 44px; }

/* ── Quick action tiles ── */
.qa-tile {
  display: flex; flex-direction: column; align-items: flex-start; gap: 12px;
  padding: var(--se-sp-4);
  background: var(--se-surface);
  border: 1px solid var(--se-border);
  border-radius: var(--se-r-lg);
  box-shadow: var(--se-shadow-1);
  height: 100%;
  min-height: 118px;
  color: var(--se-ink);
  transition: transform var(--se-t-fast) var(--se-ease-out), box-shadow var(--se-t-fast) var(--se-ease-out), border-color var(--se-t-fast) var(--se-ease-std);
}
.qa-tile:hover { transform: translateY(-2px); box-shadow: var(--se-shadow-2); border-color: var(--se-border-strong); color: var(--se-ink); }
.qa-tile:active { transform: translateY(0); }
.qa-icon {
  width: 44px; height: 44px; border-radius: var(--se-r-md);
  display: grid; place-items: center; font-size: 17px; flex-shrink: 0;
  transition: transform var(--se-t-fast) var(--se-ease-out);
}
.qa-tile:hover .qa-icon { transform: scale(1.07); }
.qa-icon--warn { background: var(--se-warn-50); color: var(--se-warn-700); }
.qa-icon--navy { background: var(--se-navy-50); color: var(--se-navy-700); }
.qa-icon--teal { background: var(--se-teal-50); color: var(--se-teal-800); }
.qa-icon--marigold { background: var(--se-marigold-100); color: var(--se-marigold-600); }
.qa-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; width: 100%; }
.qa-label { font-weight: 700; font-size: var(--se-fs-sm); }
.qa-hint {
  font-size: var(--se-fs-2xs); color: var(--se-text-muted);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* ── Society feed rows ── */
.flow-card { overflow: hidden; }
.live-dot {
  display: inline-block;
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--se-teal-600);
  margin-right: 10px;
  vertical-align: 1px;
  animation: live-pulse 2.2s var(--se-ease-std) infinite;
}
@keyframes live-pulse {
  0%, 100% { box-shadow: 0 0 0 0 var(--se-teal-100); }
  55%      { box-shadow: 0 0 0 6px transparent; }
}
.feed-row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px;
  min-height: 44px;
  color: inherit; font-weight: 400;
  transition: background-color var(--se-t-fast) var(--se-ease-std);
}
.feed-row + .feed-row { border-top: 1px solid var(--se-border); }
.feed-row:hover { background: var(--se-sunken); color: inherit; }
.feed-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.feed-line {
  font-size: var(--se-fs-sm); color: var(--se-ink);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.feed-line strong { font-weight: 600; }
.feed-meta { font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.feed-snippet {
  font-size: var(--se-fs-xs); color: var(--se-text-muted);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.feed-stats { display: flex; gap: 14px; font-size: var(--se-fs-2xs); color: var(--se-text-faint); margin-top: 2px; }
.feed-stats i { font-size: 10px; margin-right: 4px; }
.feed-go {
  color: var(--se-text-faint); font-size: 12px; flex-shrink: 0;
  transition: transform var(--se-t-fast) var(--se-ease-out), color var(--se-t-fast) var(--se-ease-std);
}
.feed-row:hover .feed-go { transform: translateX(3px); color: var(--se-teal-600); }

/* ── Compact list rows (complaints) ── */
.list-row { padding: 12px 20px; }
.list-row + .list-row { border-top: 1px solid var(--se-border); }
.row-title {
  margin: 0; font-weight: 600; font-size: var(--se-fs-sm); color: var(--se-ink);
  min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.row-date { color: var(--se-text-muted); font-size: var(--se-fs-2xs); flex-shrink: 0; }
.card-footer-link {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 12px 16px;
  min-height: 44px;
  border-top: 1px solid var(--se-border);
  font-size: var(--se-fs-xs); font-weight: 600;
}
.card-footer-link i { font-size: 10px; transition: transform var(--se-t-fast) var(--se-ease-out); }
.card-footer-link:hover i { transform: translateX(3px); }

/* ── Small screens — one column, thumb-friendly ── */
@media (max-width: 575.98px) {
  .hello-title { font-size: var(--se-fs-xl); }
  .checkin-btn, .dues-btn { width: 100%; }
  .qa-tile { min-height: 108px; }
}
</style>

<template>
  <div class="health-page">

    <!-- ══ Header ═══════════════════════════════════════════════ -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Society Health Score</h1>
        <p class="page-sub">One monthly pulse — payments, complaints, notices, polls &amp; upkeep.</p>
      </div>
      <button v-if="isAdmin" class="btn-primary-custom" :disabled="calculating" @click="calculate">
        <i class="fas" :class="calculating ? 'fa-spinner fa-spin' : 'fa-rotate-right'"></i>
        {{ calculating ? 'Calculating…' : 'Calculate this month' }}
      </button>
    </div>

    <!-- ══ Loading — skeletons mirror the final layout ══════════ -->
    <div v-if="loading" class="sk-wrap" aria-busy="true">
      <div class="card sk-hero">
        <div class="sk sk-ring"></div>
        <div class="sk-lines">
          <div class="sk sk-line sk-line--sm"></div>
          <template v-for="n in 4" :key="n">
            <div class="sk sk-line sk-line--md"></div>
            <div class="sk sk-track"></div>
          </template>
        </div>
      </div>
      <div v-for="n in 3" :key="`h${n}`" class="card sk-row">
        <div class="sk sk-line sk-line--sm"></div>
        <div class="sk sk-track sk-grow"></div>
        <div class="sk sk-pill"></div>
      </div>
    </div>

    <!-- ══ Load error — never a dead end ════════════════════════ -->
    <div v-else-if="loadError" class="card empty-state rise-in">
      <i class="fas fa-plug-circle-xmark"></i>
      <p>We couldn't fetch the society pulse. Check your connection and try again.</p>
      <button class="btn-primary-custom mt-3" @click="load"><i class="fas fa-rotate-right"></i>Retry</button>
    </div>

    <template v-else>
      <!-- ══ Hero — the community trophy ════════════════════════ -->
      <section v-if="current" class="card health-hero">
        <div class="gauge-col">
          <div class="gauge" role="img" :aria-label="`Society health score ${displayScore} out of 100 — grade ${current.grade}`">
            <svg viewBox="0 0 200 200" aria-hidden="true">
              <circle class="ring-track" cx="100" cy="100" r="84" />
              <circle
                class="ring-fill" :class="`ring--${gradeKey}`"
                cx="100" cy="100" r="84"
                :stroke-dasharray="CIRC" :stroke-dashoffset="dashOffset"
              />
            </svg>
            <div class="gauge-center">
              <span class="gauge-score se-num">{{ displayScore }}</span>
              <span class="gauge-max">out of 100</span>
            </div>
          </div>

          <span class="badge-custom" :class="`badge-${gradeKey}`">{{ current.grade }}</span>
          <p class="gauge-caption">{{ gradeCaption }}</p>
          <p class="gauge-month"><i class="fas fa-calendar-check"></i>{{ monthLabel(current.month, current.year) }}</p>

          <span
            v-if="delta !== null && Math.round(delta * 10) !== 0"
            class="se-chip" :class="delta > 0 ? 'se-chip--teal' : 'se-chip--flame'"
          >
            <i class="fas" :class="delta > 0 ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down'"></i>
            {{ delta > 0 ? '+' : '' }}{{ fmtN(delta) }} pts vs {{ monthLabel(prevScore.month, prevScore.year) }}
          </span>

          <div class="ring-legend" aria-hidden="true">
            <span><i class="dot dot--green"></i>71+ green</span>
            <span><i class="dot dot--yellow"></i>41–70</span>
            <span><i class="dot dot--red"></i>&lt;41</span>
          </div>
        </div>

        <div class="factors-col">
          <h2 class="col-title">What shaped it</h2>
          <div v-for="(f, i) in factors" :key="f.label" class="factor" :style="{ '--i': i }">
            <div class="factor-icon"><i class="fas" :class="f.icon"></i></div>
            <div class="factor-main">
              <div class="factor-head">
                <span class="factor-label">{{ f.label }}</span>
                <span class="factor-val se-num">{{ fmtN(f.score) }} <small>/ {{ f.max }}</small></span>
              </div>
              <div class="progress-bar-custom">
                <div
                  class="progress-fill" :class="`fill--${ratioKey(f)}`"
                  :style="{ width: drawn ? `${Math.min(100, (f.score / f.max) * 100)}%` : '0%' }"
                ></div>
              </div>
            </div>
          </div>

          <div class="alert-custom" :class="isHealthy ? 'alert-success' : 'alert-info'">
            <i class="fas" :class="isHealthy ? 'fa-circle-check' : 'fa-circle-info'"></i>
            <span>{{ current.alert_reason || 'All metrics healthy' }}</span>
          </div>
        </div>
      </section>

      <!-- ══ Empty — guide, don't dead-end ══════════════════════ -->
      <section v-else class="card empty-state rise-in">
        <i class="fas fa-heart-pulse"></i>
        <h2 class="empty-title">No score yet</h2>
        <p v-if="isAdmin">Calculate to see your score — collections, complaint resolution, engagement and upkeep, graded out of 100.</p>
        <p v-else>The committee hasn't taken this month's pulse yet. Check back soon!</p>
        <button v-if="isAdmin" class="btn-accent mt-3" :disabled="calculating" @click="calculate">
          <i class="fas" :class="calculating ? 'fa-spinner fa-spin' : 'fa-wand-magic-sparkles'"></i>
          {{ calculating ? 'Calculating…' : 'Calculate this month' }}
        </button>
      </section>

      <!-- ══ History — six-month trend ══════════════════════════ -->
      <section v-if="history.length" class="card history-card">
        <h2 class="col-title history-title"><i class="fas fa-chart-line"></i>Six-month trend</h2>
        <div class="hrows">
          <div
            v-for="(s, i) in history" :key="s.id ?? `${s.month}-${s.year}`"
            class="hrow" :style="{ '--i': i }" :title="s.alert_reason || ''"
          >
            <span class="hrow-month">{{ monthLabel(s.month, s.year) }}</span>
            <div class="progress-bar-custom hrow-track">
              <div
                class="progress-fill" :class="`fill--${String(s.grade || '').toLowerCase()}`"
                :style="{ width: drawn ? `${Math.min(100, Number(s.total_score) || 0)}%` : '0%' }"
              ></div>
            </div>
            <span class="hrow-score se-num">{{ Math.round(Number(s.total_score) || 0) }}</span>
            <span class="badge-custom hrow-badge" :class="`badge-${String(s.grade || '').toLowerCase()}`">{{ s.grade }}</span>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { healthAPI } from '../api/index'
import { authStore } from '../store/auth'
import { useCelebrate } from '../composables/useCelebrate'

const { celebrate, reward, toast } = useCelebrate()

const CIRC = 2 * Math.PI * 84
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const current = ref(null)
const history = ref([])
const loading = ref(true)
const loadError = ref(false)
const calculating = ref(false)
const drawn = ref(false)
const isAdmin = authStore.isAdmin

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = false
  try {
    history.value = (await healthAPI.history()).data || []
    if (history.value.length > 0) current.value = history.value[0]
  } catch (e) {
    loadError.value = true
  }
  loading.value = false
  armDraw()
}

/* Re-arm the entrance sweep: ring + bars animate from zero. */
function armDraw() {
  drawn.value = false
  requestAnimationFrame(() => requestAnimationFrame(() => { drawn.value = true }))
}

async function calculate() {
  calculating.value = true
  try {
    const now = new Date()
    const res = await healthAPI.calculate(now.getMonth() + 1, now.getFullYear())
    current.value = res.data
    const h = await healthAPI.history()
    history.value = h.data || []
    armDraw()
    if (res.data?.grade === 'GREEN') {
      celebrate({ title: 'GREEN this month!', subtitle: 'Payments, upkeep and participation — all thriving', icon: 'fa-heart-pulse', points: 25 })
      reward(25, 'Society hit a GREEN health month')
    } else if (res.data?.grade) {
      toast(`Score updated — ${monthLabel(res.data.month, res.data.year)} graded ${res.data.grade}`, 'success')
    }
  } catch (e) {
    toast('Could not calculate the score — please try again.', 'error')
  }
  calculating.value = false
}

const displayScore = computed(() => Math.round(Number(current.value?.total_score) || 0))
const gradeKey = computed(() => String(current.value?.grade || 'green').toLowerCase())
const isHealthy = computed(() => current.value?.grade === 'GREEN')

const dashOffset = computed(() => {
  const pct = drawn.value ? Math.min(100, Math.max(0, Number(current.value?.total_score) || 0)) : 0
  return CIRC * (1 - pct / 100)
})

const gradeCaption = computed(() => ({
  GREEN: 'Thriving — the society is in great shape.',
  YELLOW: 'Steady, but a few things need attention.',
  RED: 'At risk — time to rally the committee.',
}[current.value?.grade] || ''))

const factors = computed(() => {
  const s = current.value || {}
  return [
    { label: 'Payment collection', icon: 'fa-indian-rupee-sign', score: Number(s.payment_score) || 0, max: 30 },
    { label: 'Complaint resolution', icon: 'fa-screwdriver-wrench', score: Number(s.complaint_score) || 0, max: 25 },
    { label: 'Notice engagement', icon: 'fa-bullhorn', score: Number(s.notice_score) || 0, max: 15 },
    { label: 'Poll participation', icon: 'fa-check-to-slot', score: Number(s.poll_score) || 0, max: 15 },
    { label: 'Maintenance on-time', icon: 'fa-gears', score: Number(s.maintenance_score) || 0, max: 15 },
  ]
})

const prevScore = computed(() => current.value
  ? history.value.find(s => s.month !== current.value.month || s.year !== current.value.year) || null
  : null)

const delta = computed(() => (current.value && prevScore.value)
  ? (Number(current.value.total_score) || 0) - (Number(prevScore.value.total_score) || 0)
  : null)

function ratioKey(f) {
  const r = f.max ? f.score / f.max : 0
  return r >= 0.7 ? 'green' : r >= 0.4 ? 'yellow' : 'red'
}

function fmtN(v) {
  const n = Number(v) || 0
  return String(Math.abs(n % 1) < 0.05 ? Math.round(n) : Number(n.toFixed(1)))
}

function monthLabel(m, y) {
  return `${MONTHS[((Number(m) || 1) - 1 + 12) % 12]} ${y}`
}
</script>

<style scoped>
.page-sub { margin: 4px 0 0; font-size: var(--se-fs-sm); color: var(--se-text-muted); }
.col-title {
  margin: 0;
  font-family: var(--se-font-display);
  font-size: var(--se-fs-lg);
  font-weight: 700;
  color: var(--se-ink);
}

/* ══ Hero ════════════════════════════════════════════════════ */
.health-hero {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: var(--se-sp-7);
  padding: var(--se-sp-7);
  margin-bottom: var(--se-sp-4);
  animation: rise var(--se-t-slow) var(--se-ease-out) both;
}
.gauge-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}
.gauge { position: relative; width: 200px; }
.gauge svg { display: block; width: 100%; height: auto; transform: rotate(-90deg); }
.ring-track { fill: none; stroke: var(--se-sunken); stroke-width: 16; }
.ring-fill {
  fill: none;
  stroke-width: 16;
  stroke-linecap: round;
  transition: stroke-dashoffset 900ms var(--se-ease-out), stroke var(--se-t-med) var(--se-ease-std);
}
.ring--green { stroke: var(--se-teal-600); }
.ring--yellow { stroke: var(--se-warn-600); }
.ring--red { stroke: var(--se-danger-600); }
.gauge-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}
.gauge-score {
  font-family: var(--se-font-display);
  font-size: 3.1rem;
  font-weight: 800;
  line-height: 1;
  color: var(--se-ink);
}
.gauge-max {
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--se-text-faint);
}
.gauge-caption { margin: 2px 0 0; font-size: var(--se-fs-sm); color: var(--se-text-muted); }
.gauge-month {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-text-faint);
}
.ring-legend {
  display: flex;
  gap: 14px;
  margin-top: 2px;
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  color: var(--se-text-faint);
}
.ring-legend span { display: inline-flex; align-items: center; gap: 5px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot--green { background: var(--se-teal-600); }
.dot--yellow { background: var(--se-warn-600); }
.dot--red { background: var(--se-danger-600); }

/* ══ Factors ═════════════════════════════════════════════════ */
.factors-col { display: flex; flex-direction: column; gap: var(--se-sp-4); min-width: 0; }
.factor {
  display: flex;
  align-items: center;
  gap: 12px;
  animation: rise var(--se-t-slow) var(--se-ease-out) both;
  animation-delay: calc(var(--i, 0) * 55ms + 90ms);
}
.factor-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: var(--se-r-md);
  background: var(--se-navy-50);
  color: var(--se-navy-700);
  font-size: .85rem;
}
[data-theme="dark"] .factor-icon { color: var(--se-ink); }
.factor-main { flex: 1; min-width: 0; }
.factor-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
  font-size: var(--se-fs-sm);
}
.factor-label { font-weight: 600; color: var(--se-text); }
.factor-val { font-weight: 700; color: var(--se-ink); white-space: nowrap; }
.factor-val small { font-weight: 500; font-size: var(--se-fs-2xs); color: var(--se-text-faint); }
.factor .progress-fill, .hrow .progress-fill { transition: width 800ms var(--se-ease-out); }
.fill--green { background: var(--se-teal-600); }
.fill--yellow { background: var(--se-warn-600); }
.fill--red { background: var(--se-danger-600); }
.factors-col .alert-custom { margin-top: var(--se-sp-2); }

/* ══ Empty hero ══════════════════════════════════════════════ */
.empty-title {
  margin: 4px 0 6px;
  font-family: var(--se-font-display);
  font-size: var(--se-fs-xl);
  font-weight: 700;
  color: var(--se-ink);
}

/* ══ History ═════════════════════════════════════════════════ */
.history-card {
  padding: var(--se-sp-6);
  animation: rise var(--se-t-slow) var(--se-ease-out) both;
  animation-delay: 140ms;
}
.history-title { display: flex; align-items: center; gap: 10px; margin-bottom: var(--se-sp-5); }
.history-title i { color: var(--se-text-faint); font-size: .9em; }
.hrows { display: flex; flex-direction: column; gap: 16px; }
.hrow {
  display: grid;
  grid-template-columns: 88px 1fr 40px 96px;
  align-items: center;
  gap: 12px;
  animation: rise var(--se-t-slow) var(--se-ease-out) both;
  animation-delay: calc(var(--i, 0) * 45ms + 180ms);
}
.hrow-month { font-size: var(--se-fs-xs); font-weight: 600; color: var(--se-text-muted); }
.hrow-score { text-align: right; font-size: var(--se-fs-sm); font-weight: 700; color: var(--se-ink); }
.hrow-badge { justify-self: start; }

/* ══ Skeletons (shimmer, tokenized — dark mode safe) ═════════ */
.sk-wrap { display: flex; flex-direction: column; gap: var(--se-sp-3); }
.sk {
  position: relative;
  overflow: hidden;
  background: var(--se-sunken);
  border-radius: var(--se-r-sm);
}
.sk::after {
  content: "";
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, var(--se-border), transparent);
  animation: sk-shimmer 1.3s var(--se-ease-std) infinite;
}
.sk-hero {
  display: flex;
  align-items: center;
  gap: var(--se-sp-7);
  padding: var(--se-sp-7);
  margin-bottom: var(--se-sp-2);
}
.sk-ring { width: 200px; height: 200px; border-radius: 50%; flex-shrink: 0; }
.sk-lines { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.sk-line { height: 12px; }
.sk-line--md { width: 40%; }
.sk-line--sm { width: 26%; }
.sk-track { height: 8px; width: 100%; border-radius: var(--se-r-pill); }
.sk-grow { flex: 1; }
.sk-row {
  display: flex;
  align-items: center;
  gap: var(--se-sp-4);
  min-height: 64px;
  padding: var(--se-sp-4) var(--se-sp-5);
}
.sk-row .sk-line--sm { width: 72px; flex-shrink: 0; }
.sk-pill { width: 84px; height: 26px; border-radius: var(--se-r-pill); flex-shrink: 0; }
@keyframes sk-shimmer { to { transform: translateX(100%); } }

/* ══ Entrance motion ═════════════════════════════════════════ */
.rise-in { animation: rise var(--se-t-slow) var(--se-ease-out) both; }
@keyframes rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}

/* ══ Small screens ═══════════════════════════════════════════ */
@media (max-width: 767.98px) {
  .health-hero { grid-template-columns: 1fr; gap: var(--se-sp-6); padding: var(--se-sp-5); }
}
@media (max-width: 575.98px) {
  .se-page-actions > .btn-primary-custom { width: 100%; }
  .gauge { width: 168px; }
  .gauge-score { font-size: 2.6rem; }
  .sk-hero { flex-direction: column; }
  .sk-ring { width: 160px; height: 160px; }
  .hrow { grid-template-columns: 64px 1fr 36px; }
  .hrow-badge { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .health-hero, .factor, .hrow, .history-card, .rise-in { animation: none; }
  .ring-fill, .factor .progress-fill, .hrow .progress-fill { transition: none; }
  .sk::after { animation: none; }
}
</style>

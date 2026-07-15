<template>
  <div class="conflicts-page">
    <!-- ── Header ──────────────────────────────────────────────── -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Conflict Resolver</h1>
        <p class="page-sub">
          <template v-if="loading">Fetching reports…</template>
          <template v-else-if="isAdmin">
            <i class="fas fa-scale-balanced"></i>
            <span v-if="openCount"><strong class="se-num">{{ openCount }}</strong> awaiting mediation · <strong class="se-num">{{ counts.RESOLVED }}</strong> resolved</span>
            <span v-else-if="conflicts.length">All settled — <strong class="se-num">{{ counts.RESOLVED }}</strong> resolved</span>
            <span v-else>Nothing awaiting mediation</span>
          </template>
          <template v-else>
            <i class="fas fa-user-lock"></i>
            <span>Private — only you and the secretary can see these</span>
          </template>
        </p>
      </div>
    </div>

    <!-- ── Trust promise: the lead of the page ─────────────────── -->
    <section class="card trust-hero">
      <div class="th-main">
        <div class="th-shield" aria-hidden="true"><i class="fas fa-shield-halved"></i></div>
        <div class="th-copy">
          <h2 class="th-title">Your identity stays anonymous from the reported flat</h2>
          <p class="th-sub">Raise it privately — the other flat sees the concern, never your name. Only the secretary knows who filed it, so both sides get a fair hearing.</p>
        </div>
        <button class="btn-primary-custom th-cta" @click="openReport">
          <i class="fas fa-feather"></i><span>Report a concern</span>
        </button>
      </div>
      <div class="th-steps">
        <span class="th-step"><span class="th-step-ico"><i class="fas fa-feather"></i></span>You report privately</span>
        <i class="fas fa-arrow-right-long th-arrow" aria-hidden="true"></i>
        <span class="th-step"><span class="th-step-ico"><i class="fas fa-comments"></i></span>They share their side</span>
        <i class="fas fa-arrow-right-long th-arrow" aria-hidden="true"></i>
        <span class="th-step"><span class="th-step-ico"><i class="fas fa-scale-balanced"></i></span>The secretary mediates</span>
      </div>
    </section>

    <!-- ── Filter chips (only once there’s something to filter) ── -->
    <div v-if="!loading && !loadFailed && conflicts.length" class="filter-row" role="group" aria-label="Filter reports">
      <button
        v-for="f in FILTERS"
        :key="f.key"
        type="button"
        class="fchip"
        :class="{ 'is-on': filter === f.key }"
        :aria-pressed="filter === f.key"
        @click="filter = f.key"
      >
        {{ f.label }}
        <span class="fchip-n se-num">{{ counts[f.key] }}</span>
      </button>
    </div>

    <!-- ── Loading: skeletons, no layout shift ─────────────────── -->
    <div v-if="loading" class="clist" aria-hidden="true">
      <div v-for="n in 2" :key="n" class="card skel">
        <div class="sk-row">
          <span class="sk sk-ico"></span>
          <span class="sk sk-line sk-line--w40"></span>
          <span class="sk sk-pill sk-pill--end"></span>
        </div>
        <span class="sk sk-line"></span>
        <span class="sk sk-line sk-line--w70"></span>
        <span class="sk sk-rail"></span>
      </div>
    </div>

    <!-- ── Load error: never a dead end ────────────────────────── -->
    <div v-else-if="loadFailed" class="card empty-state">
      <i class="fas fa-triangle-exclamation"></i>
      <h3 class="empty-title">Couldn’t load the reports</h3>
      <p>Check your connection, then give it another go.</p>
      <button class="btn-primary-custom mt-3" @click="load"><i class="fas fa-rotate-right"></i>Try again</button>
    </div>

    <!-- ── Warm empty state ────────────────────────────────────── -->
    <div v-else-if="conflicts.length === 0" class="card empty-state">
      <i class="fas fa-dove"></i>
      <h3 class="empty-title">Zero disputes on record — a rare and beautiful thing</h3>
      <p v-if="isAdmin">No flat has raised a concern. May it stay that way.</p>
      <p v-else>Nothing you’ve raised — and hopefully nothing you’ll need to. If something’s ever bothering you, report it above; your name stays out of it.</p>
    </div>

    <!-- ── Filter came up empty ────────────────────────────────── -->
    <div v-else-if="filtered.length === 0" class="card empty-state">
      <i class="fas fa-inbox"></i>
      <p>{{ currentFilter.empty }}</p>
      <button class="ghost-btn mt-3" @click="filter = 'ALL'">Show all</button>
    </div>

    <!-- ── Concern cards ───────────────────────────────────────── -->
    <TransitionGroup v-else name="clist" tag="div" class="clist" appear>
      <article v-for="c in filtered" :key="c.id" class="card cr-card">
        <div class="cr-top">
          <div class="cr-ico" aria-hidden="true"><i :class="['fas', catInfo(c).icon]"></i></div>
          <div class="cr-head">
            <h3 class="cr-title">{{ catInfo(c).label }}</h3>
            <div class="cr-meta">
              <span><i class="fas fa-house"></i>About Flat {{ c.reported_flat || '—' }}</span>
              <span>{{ fmtDate(c.created_at) }}</span>
              <span v-if="isAdmin && c.reported_by_name" class="cr-reporter">
                <i class="fas fa-user-lock"></i>{{ c.reported_by_name }} · visible only to committee
              </span>
            </div>
          </div>
          <span class="badge-custom cr-status" :class="statusBadge(c.status)">{{ statusLabel(c.status) }}</span>
        </div>

        <p class="cr-desc" :class="{ 'cr-desc--clamp': isLong(c) && !expanded.has(c.id) }">{{ c.description }}</p>
        <button v-if="isLong(c)" type="button" class="cr-more" @click="toggleDesc(c.id)">
          {{ expanded.has(c.id) ? 'Show less' : 'Show more' }}
        </button>

        <!-- Fair-process rail: Reported → Their side → Resolved -->
        <div class="rail" role="img" :aria-label="'Status: ' + statusLabel(c.status)">
          <div
            v-for="(label, i) in RAIL"
            :key="label"
            class="rail-stop"
            :class="stopDone(c, i) ? 'is-done' : i === stageIdx(c) ? 'is-current' : 'is-next'"
            aria-hidden="true"
          >
            <span v-if="i > 0" class="rail-line" :class="{ 'rail-line--done': i <= stageIdx(c) }"></span>
            <span class="rail-dot"><i v-if="stopDone(c, i)" class="fas fa-check"></i></span>
            <span class="rail-label">{{ label }}</span>
          </div>
        </div>

        <div v-if="c.reported_flat_response" class="note-block">
          <div class="nb-label">
            <i class="fas fa-comment-dots"></i>Their side
            <span v-if="c.response_submitted_at" class="nb-when">· {{ fmtDate(c.response_submitted_at) }}</span>
          </div>
          <p>{{ c.reported_flat_response }}</p>
        </div>

        <div v-if="c.resolution_note" class="note-block note-block--res">
          <div class="nb-label">
            <i class="fas fa-handshake"></i>Resolution
            <span v-if="c.resolved_at" class="nb-when">· {{ fmtDate(c.resolved_at) }}</span>
          </div>
          <p>{{ c.resolution_note }}</p>
        </div>

        <!-- Secretary closes it out -->
        <div v-if="isAdmin && c.status !== 'RESOLVED'" class="cr-resolve">
          <label class="visually-hidden" :for="'res-' + c.id">Resolution note</label>
          <input
            :id="'res-' + c.id"
            v-model="resolveNote[c.id]"
            class="form-control-custom"
            maxlength="240"
            placeholder="How was it settled? e.g. Spoke with both flats — agreed on quiet hours"
            @keyup.enter="resolveReport(c)"
          />
          <button class="btn-primary-custom" :disabled="resolvingId === c.id" @click="resolveReport(c)">
            <i v-if="resolvingId === c.id" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-check"></i>
            Mark resolved
          </button>
        </div>
      </article>
    </TransitionGroup>

    <!-- ── Report sheet (modal on desktop, bottom sheet on mobile) ── -->
    <Teleport to="body">
      <div v-if="showReport" class="sheet-overlay" @click.self="showReport = false">
        <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="report-title">
          <div class="sheet-grip" aria-hidden="true"></div>
          <div class="sheet-head">
            <h2 class="sheet-title" id="report-title">Report a concern</h2>
            <button class="sheet-x" aria-label="Close" @click="showReport = false"><i class="fas fa-xmark"></i></button>
          </div>
          <div class="sheet-body">
            <div class="trust-note">
              <i class="fas fa-shield-halved"></i>
              <span>The flat will see the concern — <strong>never your name</strong>. Only the secretary knows who filed it.</span>
            </div>
            <div v-if="formError" class="alert-custom alert-error mb-3">{{ formError }}</div>

            <div class="form-group">
              <label class="form-label">What’s it about? *</label>
              <div class="cat-grid" role="group" aria-label="Category">
                <button
                  v-for="cat in CATEGORIES"
                  :key="cat.value"
                  type="button"
                  class="cat-chip"
                  :class="{ 'is-on': form.category === cat.value }"
                  :aria-pressed="form.category === cat.value"
                  @click="form.category = cat.value"
                >
                  <i :class="['fas', cat.icon]"></i><span>{{ cat.label }}</span>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="cf-flat">Which flat? *</label>
              <select id="cf-flat" v-model="form.reported_apartment_id" class="form-control-custom">
                <option value="" disabled>Select the flat</option>
                <option v-for="a in selectableApartments" :key="a.id" :value="a.id">Flat {{ a.flat_number }}</option>
              </select>
              <p v-if="!apartments.length" class="field-hint">
                Couldn’t load the flat list.
                <button type="button" class="link-btn" @click="loadApartments">Retry</button>
              </p>
            </div>

            <div class="form-group mb-0">
              <label class="form-label" for="cf-desc">What’s been happening? *</label>
              <textarea
                id="cf-desc"
                v-model="form.description"
                class="form-control-custom"
                rows="4"
                maxlength="600"
                placeholder="Stick to the facts — dates, times, what you observed. It helps the secretary mediate fairly."
              ></textarea>
            </div>
          </div>
          <div class="sheet-foot">
            <button class="btn-primary-custom w-100" :disabled="!canSubmit || saving" @click="submitReport">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-feather"></i>
              {{ saving ? 'Sending privately…' : 'Send privately' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { conflictsAPI, membersAPI } from '../api/index'
import { authStore } from '../store/auth'
import { useCelebrate } from '../composables/useCelebrate'

const { toast, reward } = useCelebrate()

// ── Domain constants (exact backend enums) ─────────────────────
const RAIL = ['Reported', 'Their side', 'Resolved']
const STATUS_LABELS = { OPEN: 'Open', UNDER_REVIEW: 'Under review', RESOLVED: 'Resolved' }
const CATEGORIES = [
  { value: 'NOISE', label: 'Noise', icon: 'fa-volume-high' },
  { value: 'PARKING', label: 'Parking', icon: 'fa-car' },
  { value: 'GARBAGE', label: 'Garbage', icon: 'fa-trash-can' },
  { value: 'COMMON_AREA_MISUSE', label: 'Common areas', icon: 'fa-people-roof' },
  { value: 'PETS', label: 'Pets', icon: 'fa-paw' },
  { value: 'OTHER', label: 'Something else', icon: 'fa-ellipsis' },
]
const FILTERS = [
  { key: 'ALL', label: 'All', empty: '' },
  { key: 'OPEN', label: 'Open', empty: 'No open reports — everything’s been picked up.' },
  { key: 'UNDER_REVIEW', label: 'Under review', empty: 'Nothing under review right now.' },
  { key: 'RESOLVED', label: 'Resolved', empty: 'Nothing resolved yet.' },
]

// ── State ──────────────────────────────────────────────────────
const conflicts = ref([])
const apartments = ref([])
const loading = ref(true)
const loadFailed = ref(false)
const filter = ref('ALL')
const expanded = ref(new Set())
const resolveNote = ref({})
const resolvingId = ref(null)

const showReport = ref(false)
const saving = ref(false)
const formError = ref('')
const form = ref({ reported_apartment_id: '', category: '', description: '' })

const isAdmin = computed(() => authStore.isAdmin)

// ── Derived ────────────────────────────────────────────────────
const counts = computed(() => ({
  ALL: conflicts.value.length,
  OPEN: conflicts.value.filter(c => c.status === 'OPEN').length,
  UNDER_REVIEW: conflicts.value.filter(c => c.status === 'UNDER_REVIEW').length,
  RESOLVED: conflicts.value.filter(c => c.status === 'RESOLVED').length,
}))
const openCount = computed(() => counts.value.OPEN + counts.value.UNDER_REVIEW)
const filtered = computed(() =>
  filter.value === 'ALL' ? conflicts.value : conflicts.value.filter(c => c.status === filter.value)
)
const currentFilter = computed(() => FILTERS.find(f => f.key === filter.value) || FILTERS[0])
const selectableApartments = computed(() =>
  apartments.value.filter(a => a.id !== authStore.user?.apartment_id)
)
const canSubmit = computed(() =>
  !!form.value.category && !!form.value.reported_apartment_id && form.value.description.trim().length > 0
)

// ── Display helpers ────────────────────────────────────────────
const statusLabel = s => STATUS_LABELS[s] || String(s || 'Open')
const statusBadge = s => ({ OPEN: 'badge-open', UNDER_REVIEW: 'badge-progress', RESOLVED: 'badge-resolved' }[s] || 'badge-low')
const stageIdx = c => Math.max(0, ['OPEN', 'UNDER_REVIEW', 'RESOLVED'].indexOf(c.status))
const stopDone = (c, i) => c.status === 'RESOLVED' || i < stageIdx(c)
const catInfo = c => CATEGORIES.find(x => x.value === c.category)
  || { label: String(c.category || 'Other').replace(/_/g, ' ').toLowerCase().replace(/^\w/, ch => ch.toUpperCase()), icon: 'fa-ellipsis' }
const isLong = c => (c.description || '').length > 180

function toggleDesc(id) {
  expanded.value.has(id) ? expanded.value.delete(id) : expanded.value.add(id)
}

function fmtDate(iso) {
  if (!iso) return ''
  const d = new Date(String(iso).replace(' ', 'T'))
  if (isNaN(d)) return String(iso).slice(0, 10)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const that = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  const days = Math.round((today - that) / 864e5)
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  const s = d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
  return d.getFullYear() === now.getFullYear() ? s : s + ' ' + d.getFullYear()
}

// ── Data ───────────────────────────────────────────────────────
async function load() {
  loading.value = true
  loadFailed.value = false
  try {
    const res = await conflictsAPI.getAll()
    conflicts.value = res.data || []
  } catch (e) {
    loadFailed.value = true
  }
  loading.value = false
}

async function loadQuiet() {
  try {
    const res = await conflictsAPI.getAll()
    conflicts.value = res.data || []
  } catch (e) {}
}

async function loadApartments() {
  try {
    const res = await membersAPI.getApartments()
    apartments.value = res.data || []
  } catch (e) {}
}

onMounted(() => { load(); loadApartments() })

// ── Report a concern ───────────────────────────────────────────
function openReport() {
  formError.value = ''
  if (!apartments.value.length) loadApartments()
  showReport.value = true
}

async function submitReport() {
  if (!canSubmit.value || saving.value) return
  saving.value = true
  formError.value = ''
  const flat = apartments.value.find(a => a.id === form.value.reported_apartment_id)
  try {
    await conflictsAPI.raise({
      reported_apartment_id: form.value.reported_apartment_id,
      category: form.value.category,
      description: form.value.description.trim(),
    })
    await loadQuiet()
    showReport.value = false
    form.value = { reported_apartment_id: '', category: '', description: '' }
    filter.value = 'ALL'
    toast(
      flat
        ? 'Filed privately — Flat ' + flat.flat_number + ' will be notified anonymously'
        : 'Filed privately — the flat will be notified anonymously',
      'success'
    )
  } catch (e) {
    formError.value = e.response?.data?.error || 'Couldn’t send the report. Please try again.'
  }
  saving.value = false
}

// ── Resolve (secretary) ────────────────────────────────────────
async function resolveReport(c) {
  if (resolvingId.value) return
  resolvingId.value = c.id
  try {
    const res = await conflictsAPI.resolve(c.id, {
      resolution_note: (resolveNote.value[c.id] || '').trim() || 'Resolved by secretary',
    })
    const updated = res.data?.report
    if (updated) {
      const i = conflicts.value.findIndex(x => x.id === c.id)
      if (i > -1) conflicts.value[i] = { ...conflicts.value[i], ...updated }
    } else {
      await loadQuiet()
    }
    delete resolveNote.value[c.id]
    reward(12, 'Helped neighbours find common ground')
  } catch (e) {
    toast('Couldn’t resolve — try again', 'error')
  }
  resolvingId.value = null
}

// ── Sheet ergonomics: Esc closes, body scroll locks ────────────
function onKey(e) {
  if (e.key === 'Escape') showReport.value = false
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
watch(showReport, open => {
  document.body.style.overflow = open ? 'hidden' : ''
})
</script>

<style scoped>
/* ── Header ─────────────────────────────────────────────────── */
.page-sub {
  margin: 4px 0 0;
  color: var(--se-text-muted);
  font-size: var(--se-fs-sm);
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.page-sub i { color: var(--se-teal-600); }
.page-sub strong { color: var(--se-navy-700); font-weight: 700; }

/* ── Trust hero ─────────────────────────────────────────────── */
.trust-hero {
  padding: var(--se-sp-5);
  margin-bottom: var(--se-sp-5);
  background: linear-gradient(135deg, var(--se-teal-50), var(--se-surface) 60%);
  border-color: var(--se-teal-100);
}
.th-main {
  display: flex;
  align-items: center;
  gap: var(--se-sp-4);
  flex-wrap: wrap;
}
.th-shield {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--se-teal-600);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 22px;
  flex-shrink: 0;
  box-shadow: 0 6px 16px rgba(14, 124, 123, 0.28);
}
.th-copy { flex: 1; min-width: 240px; }
.th-title {
  font-size: var(--se-fs-lg);
  font-weight: 700;
  margin: 0 0 4px;
  line-height: 1.25;
}
.th-sub {
  margin: 0;
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
  max-width: 62ch;
}
.th-cta { flex-shrink: 0; }

.th-steps {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: var(--se-sp-4);
  padding-top: var(--se-sp-4);
  border-top: 1px dashed var(--se-border);
}
.th-step {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-text-muted);
}
.th-step-ico {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--se-surface);
  border: 1px solid var(--se-teal-100);
  color: var(--se-teal-700);
  display: grid;
  place-items: center;
  font-size: 11px;
  flex-shrink: 0;
}
.th-arrow { color: var(--se-text-faint); font-size: 12px; }

@media (max-width: 767.98px) {
  .th-cta { flex: 1 1 100%; min-height: 48px; font-size: var(--se-fs-md); }
}
@media (max-width: 575.98px) {
  .th-steps { flex-direction: column; align-items: flex-start; gap: 8px; }
  .th-arrow { display: none; }
}

/* ── Filter chips ───────────────────────────────────────────── */
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: var(--se-sp-5);
}
.fchip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 7px 14px;
  border-radius: var(--se-r-pill);
  border: 1px solid var(--se-border-strong);
  background: var(--se-surface);
  color: var(--se-text-muted);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--se-t-fast) var(--se-ease-std),
              border-color var(--se-t-fast),
              color var(--se-t-fast);
}
.fchip:hover { border-color: var(--se-navy-600); color: var(--se-navy-700); background: var(--se-navy-50); }
.fchip.is-on { background: var(--se-navy-50); border-color: var(--se-navy-600); color: var(--se-navy-700); }
.fchip-n {
  min-width: 22px;
  padding: 1px 7px;
  border-radius: var(--se-r-pill);
  background: var(--se-sunken);
  font-size: var(--se-fs-2xs);
  text-align: center;
}
.fchip.is-on .fchip-n { background: var(--se-navy-100); }

/* ── List ───────────────────────────────────────────────────── */
.clist { display: flex; flex-direction: column; gap: var(--se-sp-3); }
.clist-enter-active { transition: opacity var(--se-t-slow) var(--se-ease-out), transform var(--se-t-slow) var(--se-ease-out); }
.clist-enter-from { opacity: 0; transform: translateY(8px); }
.clist-leave-active { transition: opacity var(--se-t-fast); }
.clist-leave-to { opacity: 0; }
.clist-move { transition: transform var(--se-t-med) var(--se-ease-out); }

/* ── Concern card ───────────────────────────────────────────── */
.cr-card { padding: var(--se-sp-5); }
.cr-card:hover { box-shadow: var(--se-shadow-2); transform: translateY(-2px); }

.cr-top { display: flex; align-items: flex-start; gap: 12px; }
.cr-ico {
  width: 40px;
  height: 40px;
  border-radius: var(--se-r-md);
  background: var(--se-navy-50);
  color: var(--se-navy-700);
  display: grid;
  place-items: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}
.cr-head { flex: 1; min-width: 0; }
.cr-title {
  font-family: var(--se-font-display);
  font-size: var(--se-fs-md);
  font-weight: 700;
  color: var(--se-ink);
  margin: 0 0 3px;
  line-height: 1.25;
}
.cr-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px 12px;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}
.cr-meta i { font-size: 0.85em; margin-right: 4px; }
.cr-reporter { color: var(--se-navy-700); font-weight: 600; }
.cr-status { flex-shrink: 0; }

.cr-desc {
  font-size: var(--se-fs-sm);
  color: var(--se-text);
  margin: 10px 0 0;
  white-space: pre-line;
  overflow-wrap: anywhere;
}
.cr-desc--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cr-more {
  background: none;
  border: 0;
  padding: 2px 0 0;
  color: var(--se-navy-600);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
}
.cr-more:hover { color: var(--se-navy-700); text-decoration: underline; }

/* ── Fair-process rail (3 stops) ────────────────────────────── */
.rail {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  margin-top: var(--se-sp-4);
  max-width: 420px;
}
.rail-stop {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  min-width: 0;
}
.rail-line {
  position: absolute;
  top: 7px;
  left: calc(-50% + 10px);
  width: calc(100% - 20px);
  height: 2px;
  border-radius: 1px;
  background: var(--se-border-strong);
  transition: background var(--se-t-slow) var(--se-ease-std);
}
.rail-line--done { background: var(--se-teal-600); }
.rail-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--se-surface);
  border: 2px solid var(--se-border-strong);
  z-index: 1;
  font-size: 8px;
  color: #fff;
  transition: background var(--se-t-med), border-color var(--se-t-med);
}
.is-done .rail-dot { background: var(--se-teal-600); border-color: var(--se-teal-600); }
.is-current .rail-dot {
  background: var(--se-navy-700);
  border-color: var(--se-navy-700);
  animation: rail-pulse 2.2s var(--se-ease-std) infinite;
}
.is-current .rail-dot::after { content: ""; width: 5px; height: 5px; border-radius: 50%; background: #fff; }
.rail-label {
  font-size: var(--se-fs-2xs);
  line-height: 1.15;
  text-align: center;
  color: var(--se-text-faint);
  transition: color var(--se-t-med);
}
.is-done .rail-label { color: var(--se-text-muted); }
.is-current .rail-label { color: var(--se-ink); font-weight: 700; }
@keyframes rail-pulse {
  0% { box-shadow: 0 0 0 0 rgba(62, 90, 153, 0.38); }
  70% { box-shadow: 0 0 0 7px rgba(62, 90, 153, 0); }
  100% { box-shadow: 0 0 0 0 rgba(62, 90, 153, 0); }
}

/* ── Their side / resolution blocks ─────────────────────────── */
.note-block {
  margin-top: var(--se-sp-3);
  padding: 12px 14px;
  border-radius: var(--se-r-md);
  background: var(--se-sunken);
}
.note-block p {
  margin: 4px 0 0;
  font-size: var(--se-fs-sm);
  color: var(--se-text);
  white-space: pre-line;
  overflow-wrap: anywhere;
}
.nb-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: var(--se-fs-2xs);
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--se-text-muted);
}
.nb-when { font-weight: 500; letter-spacing: 0; text-transform: none; }
.note-block--res { background: var(--se-teal-50); }
.note-block--res .nb-label { color: var(--se-teal-800); }
.note-block--res p { color: var(--se-teal-800); }

/* ── Resolve footer (secretary) ─────────────────────────────── */
.cr-resolve {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: var(--se-sp-4);
  padding-top: var(--se-sp-3);
  border-top: 1px dashed var(--se-border);
}
.cr-resolve input { flex: 1; min-width: 220px; }
.cr-resolve .btn-primary-custom { flex-shrink: 0; }
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
@media (max-width: 575.98px) {
  .cr-resolve .btn-primary-custom { flex: 1 1 100%; min-height: 48px; }
}

/* ── Empty / error states ───────────────────────────────────── */
.empty-title { font-size: var(--se-fs-lg); margin: 0 0 4px; }
.empty-state .fa-dove { color: var(--se-teal-600); }
.ghost-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 9px 16px;
  border-radius: var(--se-r-md);
  border: 1px solid var(--se-navy-600);
  background: transparent;
  color: var(--se-navy-700);
  font-size: var(--se-fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--se-t-fast);
}
.ghost-btn:hover { background: var(--se-navy-50); }

/* ── Skeletons (mirror card anatomy → no layout shift) ──────── */
.skel {
  padding: var(--se-sp-5);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.sk {
  border-radius: var(--se-r-sm);
  background: linear-gradient(90deg, var(--se-sunken) 25%, var(--se-border) 45%, var(--se-sunken) 65%);
  background-size: 300% 100%;
  animation: sk-sweep 1.4s linear infinite;
}
.sk-row { display: flex; align-items: center; gap: 10px; }
.sk-ico { width: 40px; height: 40px; border-radius: var(--se-r-md); flex-shrink: 0; }
.sk-line { height: 12px; flex: 1; }
.sk-line--w40 { flex: 0 0 40%; }
.sk-line--w70 { flex: 0 0 70%; }
.sk-pill { width: 84px; height: 24px; border-radius: var(--se-r-pill); }
.sk-pill--end { margin-left: auto; }
.sk-rail { height: 34px; max-width: 420px; }
@keyframes sk-sweep {
  from { background-position: 100% 0; }
  to { background-position: -200% 0; }
}

/* ── Sheet: centered dialog → bottom sheet under 576px ──────── */
.sheet-overlay {
  position: fixed;
  inset: 0;
  z-index: 1100;
  background: rgba(16, 27, 51, 0.48);
  display: grid;
  place-items: center;
  padding: var(--se-sp-4);
  animation: ov-in var(--se-t-med) var(--se-ease-std);
}
.sheet {
  width: min(540px, 100%);
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  background: var(--se-surface);
  border: 1px solid var(--se-border);
  border-radius: var(--se-r-lg);
  box-shadow: var(--se-shadow-3);
  animation: sheet-in var(--se-t-slow) var(--se-ease-out);
}
.sheet-grip { display: none; }
.sheet-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: var(--se-sp-5) var(--se-sp-5) var(--se-sp-3);
}
.sheet-title { font-size: var(--se-fs-lg); font-weight: 700; margin: 0; flex: 1; min-width: 0; }
.sheet-x {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border: 0;
  border-radius: var(--se-r-md);
  background: var(--se-sunken);
  color: var(--se-text-muted);
  display: grid;
  place-items: center;
  font-size: 15px;
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast);
}
.sheet-x:hover { background: var(--se-border); color: var(--se-ink); }
.sheet-body { padding: var(--se-sp-2) var(--se-sp-5) var(--se-sp-4); overflow-y: auto; }
.sheet-foot { padding: var(--se-sp-4) var(--se-sp-5); border-top: 1px solid var(--se-border); }
@keyframes ov-in { from { opacity: 0; } }
@keyframes sheet-in { from { opacity: 0; transform: translateY(14px) scale(0.985); } }

@media (max-width: 575.98px) {
  .sheet-overlay { padding: 0; align-items: end; justify-items: stretch; }
  .sheet {
    width: 100%;
    max-height: 92dvh;
    border-radius: var(--se-r-lg) var(--se-r-lg) 0 0;
    border-left: 0;
    border-right: 0;
    border-bottom: 0;
    padding-bottom: env(safe-area-inset-bottom);
    animation: sheet-up var(--se-t-slow) var(--se-ease-out);
  }
  .sheet-grip {
    display: block;
    width: 44px;
    height: 4px;
    flex-shrink: 0;
    border-radius: var(--se-r-pill);
    background: var(--se-border-strong);
    margin: 10px auto 0;
  }
}
@keyframes sheet-up { from { transform: translateY(100%); } }

/* ── Sheet form: trust note + category chips ────────────────── */
.trust-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: var(--se-r-md);
  background: var(--se-teal-50);
  color: var(--se-teal-800);
  font-size: var(--se-fs-xs);
  margin-bottom: var(--se-sp-4);
}
.trust-note i { margin-top: 2px; flex-shrink: 0; }

.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
}
.cat-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 46px;
  padding: 8px 10px;
  border-radius: var(--se-r-md);
  border: 1px solid var(--se-border-strong);
  background: var(--se-surface);
  color: var(--se-text);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--se-t-fast) var(--se-ease-std),
              border-color var(--se-t-fast),
              color var(--se-t-fast);
}
.cat-chip i { color: var(--se-text-muted); transition: color var(--se-t-fast); }
.cat-chip:hover { border-color: var(--se-navy-600); background: var(--se-navy-50); }
.cat-chip.is-on { background: var(--se-navy-700); border-color: var(--se-navy-700); color: #fff; }
.cat-chip.is-on i { color: var(--se-marigold-400); }

.field-hint { margin: 6px 0 0; font-size: var(--se-fs-2xs); color: var(--se-text-muted); }
.link-btn {
  border: 0;
  background: none;
  padding: 0;
  color: var(--se-navy-600);
  font-weight: 600;
  font-size: inherit;
  cursor: pointer;
  text-decoration: underline;
}
.link-btn:hover { color: var(--se-navy-700); }

@media (max-width: 767.98px) {
  .fchip { min-height: 44px; }
}
</style>

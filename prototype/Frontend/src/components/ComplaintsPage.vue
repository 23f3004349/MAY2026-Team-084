<template>
  <div class="complaints-page">
    <!-- ── Header: one obvious primary action ─────────────────── -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Complaints</h1>
        <p class="page-sub">
          <template v-if="loading">Checking on things…</template>
          <template v-else-if="activeCount">
            <i class="fas fa-screwdriver-wrench"></i>
            <span><strong class="se-num">{{ activeCount }}</strong> being handled · <strong class="se-num">{{ resolvedCount }}</strong> resolved</span>
          </template>
          <template v-else>
            <i class="fas fa-circle-check"></i>
            <span>All clear — nothing pending right now</span>
          </template>
        </p>
      </div>
      <button class="btn-primary-custom raise-btn" @click="openRaise">
        <i class="fas fa-plus"></i><span>Raise a complaint</span>
      </button>
    </div>

    <!-- ── Filter chips ────────────────────────────────────────── -->
    <div class="filter-row" role="group" aria-label="Filter complaints">
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
        <span v-if="!loading" class="fchip-n se-num">{{ counts[f.key] }}</span>
      </button>
    </div>

    <!-- ── Loading: skeletons, no layout shift ─────────────────── -->
    <div v-if="loading" class="clist" aria-hidden="true">
      <div v-for="n in 3" :key="n" class="card skel">
        <div class="sk-row">
          <span class="sk sk-ico"></span>
          <span class="sk sk-line sk-line--w40"></span>
          <span class="sk sk-pill sk-pill--end"></span>
        </div>
        <span class="sk sk-line"></span>
        <span class="sk sk-rail"></span>
        <div class="sk-row">
          <span class="sk sk-pill"></span>
          <span class="sk sk-pill"></span>
        </div>
      </div>
    </div>

    <!-- ── Load error: never a dead end ────────────────────────── -->
    <div v-else-if="loadFailed" class="card empty-state">
      <i class="fas fa-triangle-exclamation"></i>
      <h3 class="empty-title">Couldn’t load complaints</h3>
      <p>Check your connection, then give it another go.</p>
      <button class="btn-primary-custom mt-3" @click="load"><i class="fas fa-rotate-right"></i>Try again</button>
    </div>

    <!-- ── Empty: guide the first action ───────────────────────── -->
    <div v-else-if="complaints.length === 0" class="card empty-state">
      <i class="fas fa-clipboard-check"></i>
      <h3 class="empty-title">All quiet in the society</h3>
      <p>Nothing’s been reported yet. Spotted something that needs fixing?</p>
      <button class="btn-primary-custom mt-3" @click="openRaise"><i class="fas fa-plus"></i>Raise the first one</button>
    </div>

    <!-- ── Filter came up empty ────────────────────────────────── -->
    <div v-else-if="filtered.length === 0" class="card empty-state">
      <i class="fas fa-inbox"></i>
      <p>{{ currentFilter.empty }}</p>
      <button class="ghost-btn mt-3" @click="filter = 'ALL'">Show all</button>
    </div>

    <!-- ── Complaint cards with lifecycle rail ─────────────────── -->
    <TransitionGroup v-else name="clist" tag="div" class="clist">
      <article
        v-for="c in filtered"
        :key="c.id"
        class="card complaint-card"
        :class="'prio-' + (c.priority || 'medium').toLowerCase()"
      >
        <div class="cc-top">
          <div class="cat-ico" :class="'cat--' + (c.category || 'other').toLowerCase()" aria-hidden="true">
            <i :class="['fas', catInfo(c).icon]"></i>
          </div>
          <div class="cc-head">
            <h3 class="cc-title">{{ c.title }}</h3>
            <div class="cc-meta">
              <span><i class="fas fa-house"></i>{{ c.flat_number || '—' }}</span>
              <span>{{ raiserLabel(c) }}</span>
              <span>{{ fmtDate(c.created_at) }}</span>
              <span v-if="c.assigned_worker_name" class="cc-worker">
                <i class="fas fa-user-gear"></i>{{ c.assigned_worker_name }}
              </span>
            </div>
          </div>
          <span class="badge-custom cc-status" :class="statusBadge(c)">{{ statusLabel(c.status) }}</span>
        </div>

        <p v-if="c.description" class="cc-desc" :class="{ 'cc-desc--clamp': isLong(c) && !expanded.has(c.id) }">{{ c.description }}</p>
        <button v-if="isLong(c)" type="button" class="cc-more" @click="toggleDesc(c.id)">
          {{ expanded.has(c.id) ? 'Show less' : 'Show more' }}
        </button>

        <!-- Lifecycle rail: OPEN → ASSIGNED → IN_PROGRESS → COMPLETED → CLOSED -->
        <div class="rail" role="img" :aria-label="'Status: ' + statusLabel(c.status) + ' · step ' + (stageIdx(c) + 1) + ' of 5'">
          <div
            v-for="(s, i) in STATUS_FLOW"
            :key="s"
            class="rail-stop"
            :class="i < stageIdx(c) ? 'is-done' : i === stageIdx(c) ? 'is-current' : 'is-next'"
            aria-hidden="true"
          >
            <span v-if="i > 0" class="rail-line" :class="{ 'rail-line--done': i <= stageIdx(c) }"></span>
            <span class="rail-dot"><i v-if="i < stageIdx(c)" class="fas fa-check"></i></span>
            <span class="rail-label">{{ statusLabel(s) }}</span>
          </div>
        </div>

        <div class="cc-foot">
          <div class="cc-pills">
            <span class="se-chip se-chip--navy"><i :class="['fas', catInfo(c).icon]"></i>{{ catInfo(c).label }}</span>
            <span class="badge-custom" :class="'badge-' + (c.priority || 'medium').toLowerCase()">{{ prioLabel(c) }} priority</span>
          </div>

          <!-- Role actions: admin assigns + advances, worker starts + finishes -->
          <div v-if="isAdmin || isWorker" class="cc-actions">
            <template v-if="isAdmin">
              <button v-if="c.status === 'OPEN'" class="act-btn" @click="openAssign(c)">
                <i class="fas fa-user-plus"></i>Assign
              </button>
              <button v-if="c.status === 'ASSIGNED'" class="act-btn" @click="setStatus(c, 'IN_PROGRESS')">
                <i class="fas fa-play"></i>Start work
              </button>
              <button v-if="c.status === 'IN_PROGRESS'" class="act-btn" @click="setStatus(c, 'COMPLETED')">
                <i class="fas fa-check"></i>Mark completed
              </button>
              <button v-if="c.status === 'COMPLETED'" class="act-btn" @click="setStatus(c, 'CLOSED')">
                <i class="fas fa-box-archive"></i>Close
              </button>
              <button class="act-btn act-btn--icon" aria-label="Delete complaint" @click="removeComplaint(c)">
                <i class="fas fa-trash"></i>
              </button>
            </template>
            <template v-else>
              <button v-if="c.status === 'ASSIGNED'" class="act-btn" @click="setStatus(c, 'IN_PROGRESS')">
                <i class="fas fa-play"></i>Start work
              </button>
              <button v-if="c.status === 'IN_PROGRESS'" class="act-btn" @click="setStatus(c, 'COMPLETED')">
                <i class="fas fa-check"></i>Mark done
              </button>
            </template>
          </div>
        </div>
      </article>
    </TransitionGroup>

    <!-- ── Raise sheet (modal on desktop, bottom sheet on mobile) ── -->
    <Teleport to="body">
      <div v-if="showRaise" class="sheet-overlay" @click.self="showRaise = false">
        <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="raise-title">
          <div class="sheet-grip" aria-hidden="true"></div>
          <div class="sheet-head">
            <h2 class="sheet-title" id="raise-title">Raise a complaint</h2>
            <span v-if="myFlat" class="se-chip"><i class="fas fa-house"></i>{{ myFlat }}</span>
            <button class="sheet-x" aria-label="Close" @click="showRaise = false"><i class="fas fa-xmark"></i></button>
          </div>
          <div class="sheet-body">
            <div v-if="formError" class="alert-custom alert-error mb-3">{{ formError }}</div>

            <div class="form-group">
              <label class="form-label">What needs fixing? *</label>
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
              <label class="form-label">How urgent is it?</label>
              <div class="seg" role="group" aria-label="Priority">
                <button
                  v-for="p in PRIORITIES"
                  :key="p.value"
                  type="button"
                  class="seg-btn"
                  :class="{ 'is-on': form.priority === p.value }"
                  :aria-pressed="form.priority === p.value"
                  @click="form.priority = p.value"
                >
                  <span class="seg-dot" :class="'seg-dot--' + p.value.toLowerCase()"></span>{{ p.label }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="c-title">Give it a short title *</label>
              <input
                id="c-title"
                v-model="form.title"
                class="form-control-custom"
                maxlength="120"
                placeholder="e.g. Corridor light flickering on floor 3"
                @keyup.enter="submitRaise"
              />
            </div>

            <div class="form-group mb-0">
              <label class="form-label" for="c-desc">Details <span class="opt">(optional)</span></label>
              <textarea
                id="c-desc"
                v-model="form.description"
                class="form-control-custom"
                rows="3"
                placeholder="Anything that helps the team fix it faster"
              ></textarea>
            </div>
          </div>
          <div class="sheet-foot">
            <button class="btn-primary-custom w-100" :disabled="!canSubmit || saving" @click="submitRaise">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-paper-plane"></i>
              {{ saving ? 'Raising…' : 'Raise complaint' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Assign sheet (admin) ────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showAssign" class="sheet-overlay" @click.self="showAssign = false">
        <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="assign-title">
          <div class="sheet-grip" aria-hidden="true"></div>
          <div class="sheet-head">
            <h2 class="sheet-title" id="assign-title">Assign to the team</h2>
            <button class="sheet-x" aria-label="Close" @click="showAssign = false"><i class="fas fa-xmark"></i></button>
          </div>
          <div class="sheet-body">
            <div v-if="selected" class="assign-ctx">
              <div class="cat-ico" :class="'cat--' + (selected.category || 'other').toLowerCase()" aria-hidden="true">
                <i :class="['fas', catInfo(selected).icon]"></i>
              </div>
              <div class="ctx-text">
                <div class="ctx-title">{{ selected.title }}</div>
                <div class="ctx-sub">{{ selected.flat_number || '—' }} · {{ prioLabel(selected) }} priority</div>
              </div>
            </div>
            <div class="form-group mb-0">
              <label class="form-label" for="a-note">Note for the worker <span class="opt">(optional)</span></label>
              <textarea
                id="a-note"
                v-model="assignNote"
                class="form-control-custom"
                rows="2"
                placeholder="e.g. Best time to visit is after 4 pm"
              ></textarea>
            </div>
          </div>
          <div class="sheet-foot">
            <button class="btn-primary-custom w-100" :disabled="assigning" @click="doAssign">
              <i v-if="assigning" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-user-plus"></i>
              {{ assigning ? 'Assigning…' : 'Assign complaint' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { complaintsAPI } from '../api/index'
import { authStore } from '../store/auth'
import { useCelebrate } from '../composables/useCelebrate'

const { toast } = useCelebrate()

// ── Domain constants (exact backend enums) ─────────────────────
const STATUS_FLOW = ['OPEN', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED']
const STATUS_LABELS = { OPEN: 'Open', ASSIGNED: 'Assigned', IN_PROGRESS: 'In progress', COMPLETED: 'Completed', CLOSED: 'Closed' }
const CATEGORIES = [
  { value: 'PLUMBING', label: 'Plumbing', icon: 'fa-faucet-drip' },
  { value: 'ELECTRICAL', label: 'Electrical', icon: 'fa-bolt' },
  { value: 'CLEANING', label: 'Cleaning', icon: 'fa-broom' },
  { value: 'SECURITY', label: 'Security', icon: 'fa-shield-halved' },
  { value: 'OTHER', label: 'Other', icon: 'fa-toolbox' },
]
const PRIORITIES = [
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
]
const FILTERS = [
  { key: 'ALL', label: 'All', empty: '' },
  { key: 'OPEN', label: 'Open', empty: 'Nothing’s waiting — every report has been picked up.' },
  { key: 'IN_PROGRESS', label: 'In progress', empty: 'Nothing’s being worked on right now.' },
  { key: 'DONE', label: 'Completed', empty: 'Nothing’s been completed yet — check back soon.' },
]
const GROUPS = { OPEN: ['OPEN', 'ASSIGNED'], IN_PROGRESS: ['IN_PROGRESS'], DONE: ['COMPLETED', 'CLOSED'] }

// ── State ──────────────────────────────────────────────────────
const complaints = ref([])
const loading = ref(true)
const loadFailed = ref(false)
const saving = ref(false)
const assigning = ref(false)
const showRaise = ref(false)
const showAssign = ref(false)
const selected = ref(null)
const filter = ref('ALL')
const formError = ref('')
const expanded = ref(new Set())
const form = ref({ title: '', description: '', category: '', priority: 'MEDIUM' })
const assignNote = ref('')

const isAdmin = computed(() => authStore.isAdmin)
const isWorker = computed(() => authStore.user?.role === 'WORKER')
const myFlat = computed(() => authStore.user?.flat_number || '')

// ── Derived ────────────────────────────────────────────────────
const inFilter = (c, key) => key === 'ALL' || (GROUPS[key] || []).includes(c.status)
const filtered = computed(() => complaints.value.filter(c => inFilter(c, filter.value)))
const counts = computed(() => Object.fromEntries(FILTERS.map(f => [f.key, complaints.value.filter(c => inFilter(c, f.key)).length])))
const currentFilter = computed(() => FILTERS.find(f => f.key === filter.value) || FILTERS[0])
const activeCount = computed(() => complaints.value.filter(c => ['OPEN', 'ASSIGNED', 'IN_PROGRESS'].includes(c.status)).length)
const resolvedCount = computed(() => counts.value.DONE)
const canSubmit = computed(() => form.value.title.trim().length > 0 && !!form.value.category)

// ── Display helpers ────────────────────────────────────────────
const sentence = s => { const t = String(s || '').replace(/_/g, ' ').toLowerCase(); return t.charAt(0).toUpperCase() + t.slice(1) }
const statusLabel = s => STATUS_LABELS[s] || sentence(s || 'Open')
const statusBadge = c => 'badge-' + (c.status || 'open').toLowerCase().replace(/_/g, '-')
const prioLabel = c => sentence(c.priority || 'Medium')
const stageIdx = c => Math.max(0, STATUS_FLOW.indexOf(c.status))
const catInfo = c => CATEGORIES.find(x => x.value === c.category) || { label: sentence(c.category || 'Other'), icon: 'fa-toolbox' }
const raiserLabel = c => (c.raised_by_name && c.raised_by_name === authStore.user?.name) ? 'You' : (c.raised_by_name || 'Resident')
const isLong = c => (c.description || '').length > 160

function toggleDesc(id) {
  expanded.value.has(id) ? expanded.value.delete(id) : expanded.value.add(id)
}

function fmtDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
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
    const res = await complaintsAPI.getAll()
    complaints.value = res.data || []
  } catch (e) {
    loadFailed.value = true
  }
  loading.value = false
}
onMounted(load)

function mergeLocal(id, data) {
  if (!data) return
  const i = complaints.value.findIndex(x => x.id === id)
  if (i > -1) complaints.value[i] = { ...complaints.value[i], ...data }
}

// ── Raise ──────────────────────────────────────────────────────
function openRaise() {
  formError.value = ''
  showRaise.value = true
}

async function submitRaise() {
  if (!canSubmit.value || saving.value) return
  saving.value = true
  formError.value = ''
  const payload = {
    title: form.value.title.trim(),
    description: form.value.description.trim(),
    category: form.value.category,
    priority: form.value.priority,
    apartment_id: authStore.user?.apartment_id || 1,
  }
  try {
    const res = await complaintsAPI.raise(payload)
    // POST response may omit joined display fields — fill sensible defaults first.
    complaints.value.unshift({
      id: 'tmp-' + Date.now(),
      status: 'OPEN',
      flat_number: myFlat.value || '—',
      raised_by_name: authStore.user?.name || 'You',
      created_at: new Date().toISOString(),
      ...payload,
      ...(res.data || {}),
    })
    filter.value = 'ALL' // make sure the new card is visible
    showRaise.value = false
    form.value = { title: '', description: '', category: '', priority: 'MEDIUM' }
    toast('Complaint raised · we’ll keep you posted', 'success')
  } catch (e) {
    formError.value = e.response?.data?.error || 'Could not raise the complaint. Please try again.'
  }
  saving.value = false
}

// ── Status advance (admin + worker) — optimistic ───────────────
async function setStatus(c, status) {
  const prev = c.status
  c.status = status
  try {
    const res = await complaintsAPI.updateStatus(c.id, { status })
    mergeLocal(c.id, res.data)
    if (status === 'IN_PROGRESS') toast('Marked in progress', 'success')
    else if (status === 'COMPLETED') toast('Marked completed · great work', 'success')
    else if (status === 'CLOSED') toast('Complaint closed', 'info')
  } catch (e) {
    c.status = prev
    toast('Couldn’t update — try again', 'error')
  }
}

// ── Assign (admin) ─────────────────────────────────────────────
function openAssign(c) {
  selected.value = c
  assignNote.value = ''
  showAssign.value = true
}

async function doAssign() {
  if (assigning.value || !selected.value) return
  assigning.value = true
  try {
    const res = await complaintsAPI.assign(selected.value.id, { worker_id: null, remarks: assignNote.value.trim() })
    mergeLocal(selected.value.id, { status: 'ASSIGNED', ...(res.data || {}) })
    showAssign.value = false
    toast('Assigned · the team is on it', 'success')
  } catch (e) {
    toast('Couldn’t assign — try again', 'error')
  }
  assigning.value = false
}

// ── Delete (admin) ─────────────────────────────────────────────
async function removeComplaint(c) {
  if (!confirm('Delete this complaint for good?')) return
  try {
    await complaintsAPI.delete(c.id)
    complaints.value = complaints.value.filter(x => x.id !== c.id)
    toast('Complaint deleted', 'info')
  } catch (e) {
    toast('Couldn’t delete — try again', 'error')
  }
}

// ── Sheet ergonomics: Esc closes, body scroll locks ────────────
function onKey(e) {
  if (e.key === 'Escape') { showRaise.value = false; showAssign.value = false }
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
watch([showRaise, showAssign], ([a, b]) => {
  document.body.style.overflow = (a || b) ? 'hidden' : ''
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

@media (max-width: 575.98px) {
  .raise-btn { flex: 1 1 100%; min-height: 48px; font-size: var(--se-fs-md); }
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
.clist-enter-from { opacity: 0; transform: translateY(-8px); }
.clist-leave-active { transition: opacity var(--se-t-fast); }
.clist-leave-to { opacity: 0; }
.clist-move { transition: transform var(--se-t-med) var(--se-ease-out); }

/* ── Complaint card ─────────────────────────────────────────── */
.complaint-card { padding: var(--se-sp-5); }
.prio-high { box-shadow: inset 3px 0 0 var(--se-danger-600), var(--se-shadow-1); }
.prio-medium { box-shadow: inset 3px 0 0 var(--se-warn-600), var(--se-shadow-1); }

.cc-top { display: flex; align-items: flex-start; gap: 12px; }
.cc-head { flex: 1; min-width: 0; }
.cc-title {
  font-family: var(--se-font-display);
  font-size: var(--se-fs-md);
  font-weight: 700;
  color: var(--se-ink);
  margin: 0 0 3px;
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.cc-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px 12px;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}
.cc-meta i { font-size: 0.85em; margin-right: 4px; }
.cc-worker { color: var(--se-teal-700); font-weight: 600; }
.cc-status { flex-shrink: 0; }

.cat-ico {
  width: 40px;
  height: 40px;
  border-radius: var(--se-r-md);
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 0.95rem;
  flex-shrink: 0;
}
.cat--plumbing { background: var(--se-navy-600); }
.cat--electrical { background: var(--se-marigold-400); color: var(--se-navy-800); }
.cat--cleaning { background: var(--se-teal-600); }
.cat--security { background: var(--se-navy-800); }
.cat--other { background: var(--se-text-muted); }

.cc-desc {
  font-size: var(--se-fs-sm);
  color: var(--se-text);
  margin: 10px 0 0;
  white-space: pre-line;
}
.cc-desc--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cc-more {
  background: none;
  border: 0;
  padding: 2px 0 0;
  color: var(--se-navy-600);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
}
.cc-more:hover { color: var(--se-navy-700); text-decoration: underline; }

/* ── Lifecycle rail ─────────────────────────────────────────── */
.rail {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  margin-top: var(--se-sp-4);
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
@media (max-width: 575.98px) {
  .rail-label { font-size: 0.66rem; }
}

/* ── Card footer: pills + role actions ──────────────────────── */
.cc-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: var(--se-sp-4);
  padding-top: var(--se-sp-3);
  border-top: 1px dashed var(--se-border);
}
.cc-pills { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.cc-pills .se-chip i { font-size: 0.8em; }
.cc-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-left: auto; }

.act-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 38px;
  padding: 8px 14px;
  border-radius: var(--se-r-md);
  border: 1px solid var(--se-border-strong);
  background: var(--se-surface);
  color: var(--se-navy-700);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--se-t-fast) var(--se-ease-std),
              border-color var(--se-t-fast),
              color var(--se-t-fast);
}
.act-btn:hover { border-color: var(--se-navy-600); background: var(--se-navy-50); }
.act-btn i { font-size: 0.85em; }
.act-btn--icon {
  width: 38px;
  padding: 0;
  border-color: transparent;
  color: var(--se-text-faint);
}
.act-btn--icon:hover { background: var(--se-danger-50); border-color: var(--se-danger-100); color: var(--se-danger-ink); }

@media (max-width: 767.98px) {
  .fchip { min-height: 44px; }
  .act-btn { min-height: 44px; }
}
@media (max-width: 575.98px) {
  .cc-actions { width: 100%; margin-left: 0; }
  .cc-actions .act-btn { flex: 1; }
  .cc-actions .act-btn--icon { flex: 0 0 44px; width: 44px; }
}

/* ── Empty / error states ───────────────────────────────────── */
.empty-title {
  font-size: var(--se-fs-lg);
  margin: 0 0 4px;
}
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
.sk-pill { width: 84px; height: 24px; border-radius: var(--se-r-pill); }
.sk-pill--end { margin-left: auto; }
.sk-rail { height: 34px; }
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
.sheet-head .se-chip { flex-shrink: 0; }
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

/* ── Form: category chips + priority segment ────────────────── */
.opt { color: var(--se-text-faint); font-weight: 400; }

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

.seg {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-md);
  overflow: hidden;
  background: var(--se-surface);
}
.seg-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 46px;
  border: 0;
  background: transparent;
  color: var(--se-text-muted);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast);
}
.seg-btn + .seg-btn { border-left: 1px solid var(--se-border-strong); }
.seg-btn:hover { background: var(--se-navy-50); color: var(--se-navy-700); }
.seg-btn.is-on { background: var(--se-navy-700); color: #fff; }
.seg-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.seg-dot--low { background: var(--se-text-faint); }
.seg-dot--medium { background: var(--se-warn-600); }
.seg-dot--high { background: var(--se-danger-600); }

/* ── Assign sheet context row ───────────────────────────────── */
.assign-ctx {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--se-sunken);
  border-radius: var(--se-r-md);
  margin-bottom: var(--se-sp-4);
}
.ctx-text { min-width: 0; }
.ctx-title {
  font-weight: 700;
  color: var(--se-ink);
  font-size: var(--se-fs-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ctx-sub { font-size: var(--se-fs-xs); color: var(--se-text-muted); }
</style>

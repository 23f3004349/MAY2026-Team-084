<template>
  <div class="parking-page">
    <!-- ── Header: title + live availability + admin action ───── -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Visitor Parking</h1>
        <p class="page-sub">
          <template v-if="loading">Checking the lot…</template>
          <template v-else-if="loadFailed">Couldn’t reach the lot right now</template>
          <template v-else-if="slots.length === 0">No visitor slots set up yet</template>
          <template v-else-if="counts.AVAILABLE > 0">
            <i class="fas fa-circle-check"></i>
            <span><strong class="se-num">{{ counts.AVAILABLE }}</strong> of <strong class="se-num">{{ slots.length }}</strong> slots free right now</span>
          </template>
          <template v-else>
            <i class="fas fa-circle-exclamation"></i>
            <span>Lot’s full — all <strong class="se-num">{{ slots.length }}</strong> slots are taken</span>
          </template>
        </p>
      </div>
      <button v-if="isAdmin" class="btn-primary-custom add-btn" @click="openAdd">
        <i class="fas fa-plus"></i><span>Add slot</span>
      </button>
    </div>

    <!-- ── Lot at a glance: occupancy meter + filter chips ─────── -->
    <section v-if="loading" class="card lot-card" aria-hidden="true">
      <span class="sk sk-track"></span>
      <div class="sk-row lot-sk-row">
        <span class="sk sk-pill"></span>
        <span class="sk sk-pill"></span>
        <span class="sk sk-pill"></span>
        <span class="sk sk-pill"></span>
      </div>
    </section>
    <section v-else-if="!loadFailed && slots.length" class="card lot-card">
      <div
        class="occ-track"
        role="img"
        :aria-label="counts.AVAILABLE + ' available, ' + counts.RESERVED + ' reserved, ' + counts.OCCUPIED + ' occupied of ' + slots.length + ' slots'"
      >
        <span v-if="counts.AVAILABLE" class="occ-seg occ-seg--available" :style="{ flexBasis: pct(counts.AVAILABLE) }"></span>
        <span v-if="counts.RESERVED" class="occ-seg occ-seg--reserved" :style="{ flexBasis: pct(counts.RESERVED) }"></span>
        <span v-if="counts.OCCUPIED" class="occ-seg occ-seg--occupied" :style="{ flexBasis: pct(counts.OCCUPIED) }"></span>
      </div>
      <div class="filter-row" role="group" aria-label="Filter slots">
        <button
          v-for="f in FILTERS"
          :key="f.key"
          type="button"
          class="fchip"
          :class="{ 'is-on': filter === f.key }"
          :aria-pressed="filter === f.key"
          @click="filter = f.key"
        >
          <span v-if="f.dot" class="dot" :class="'dot--' + f.dot" aria-hidden="true"></span>
          {{ f.label }}
          <span class="fchip-n se-num">{{ f.key === 'ALL' ? slots.length : counts[f.key] }}</span>
        </button>
      </div>
    </section>

    <!-- ── Loading: skeleton tiles, no layout shift ────────────── -->
    <div v-if="loading" class="slot-grid" aria-hidden="true">
      <div v-for="n in 8" :key="n" class="card slot-tile skel">
        <div class="sk-row">
          <span class="sk sk-num"></span>
          <span class="sk sk-pill sk-pill--end"></span>
        </div>
        <span class="sk sk-line"></span>
        <span class="sk sk-btn"></span>
      </div>
    </div>

    <!-- ── Load error: never a dead end ────────────────────────── -->
    <div v-else-if="loadFailed" class="card empty-state">
      <i class="fas fa-triangle-exclamation"></i>
      <h3 class="empty-title">Couldn’t load the parking lot</h3>
      <p>Check your connection, then give it another go.</p>
      <button class="btn-primary-custom mt-3" @click="load()"><i class="fas fa-rotate-right"></i>Try again</button>
    </div>

    <!-- ── Empty: guide the first action ───────────────────────── -->
    <div v-else-if="slots.length === 0" class="card empty-state">
      <i class="fas fa-square-parking"></i>
      <h3 class="empty-title">No visitor slots yet</h3>
      <p v-if="isAdmin">Set up the lot — add the first slot and residents can start booking for their guests.</p>
      <p v-else>The committee hasn’t added visitor slots yet. Check back soon.</p>
      <button v-if="isAdmin" class="btn-primary-custom mt-3" @click="openAdd"><i class="fas fa-plus"></i>Add the first slot</button>
    </div>

    <!-- ── Filter came up empty ────────────────────────────────── -->
    <div v-else-if="filtered.length === 0" class="card empty-state">
      <i class="fas fa-inbox"></i>
      <p>{{ currentFilter.empty }}</p>
      <button class="ghost-btn mt-3" @click="filter = 'ALL'">Show all slots</button>
    </div>

    <!-- ── Slot grid ───────────────────────────────────────────── -->
    <TransitionGroup v-else name="grid" tag="div" class="slot-grid" appear>
      <article v-for="s in filtered" :key="s.id" class="card slot-tile" :class="'st--' + stat(s)">
        <div class="st-head">
          <span class="st-num se-num">{{ s.slot_number }}</span>
          <span class="badge-custom" :class="'badge-' + stat(s)">{{ statusLabel(s) }}</span>
        </div>

        <p v-if="stat(s) === 'available'" class="st-hint">Open for guests</p>
        <ul v-else class="st-info">
          <li v-if="s.visitor_name"><i class="fas fa-user"></i><span>{{ s.visitor_name }}</span></li>
          <li v-if="s.visitor_vehicle_number"><i class="fas fa-car"></i><span class="se-num">{{ s.visitor_vehicle_number }}</span></li>
          <li v-if="s.flat_number"><i class="fas fa-house"></i><span>Host · {{ s.flat_number }}</span></li>
          <li v-if="stat(s) === 'reserved' && s.expected_arrival_time"><i class="fas fa-clock"></i><span>Due {{ fmtWhen(s.expected_arrival_time) }}</span></li>
          <li v-else-if="stat(s) === 'occupied' && s.occupied_since"><i class="fas fa-clock"></i><span>In since {{ fmtWhen(s.occupied_since) }}</span></li>
        </ul>

        <div class="st-actions">
          <button
            v-if="stat(s) === 'available'"
            class="tile-btn tile-btn--book"
            @click="openBook(s)"
          >
            <i class="fas fa-car-side"></i>Book
          </button>
          <button
            v-if="stat(s) === 'reserved' && isAdmin"
            class="tile-btn tile-btn--arrive"
            :disabled="busy === s.id"
            @click="markArrived(s)"
          >
            <i :class="busy === s.id && busyAct === 'arrive' ? 'fas fa-spinner fa-spin' : 'fas fa-flag-checkered'"></i>Arrived
          </button>
          <button
            v-if="stat(s) !== 'available'"
            class="tile-btn"
            :disabled="busy === s.id"
            @click="releaseSlot(s)"
          >
            <i :class="busy === s.id && busyAct === 'release' ? 'fas fa-spinner fa-spin' : 'fas fa-rotate-left'"></i>Release
          </button>
          <button
            v-if="isAdmin"
            class="tile-btn tile-btn--del"
            :disabled="busy === s.id"
            :aria-label="'Remove slot ' + s.slot_number"
            @click="removeSlot(s)"
          >
            <i :class="busy === s.id && busyAct === 'delete' ? 'fas fa-spinner fa-spin' : 'fas fa-trash'"></i>
          </button>
        </div>
      </article>
    </TransitionGroup>

    <!-- ── Book sheet (modal on desktop, bottom sheet on mobile) ── -->
    <Teleport to="body">
      <div v-if="showBook" class="sheet-overlay" @click.self="showBook = false">
        <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="book-title">
          <div class="sheet-grip" aria-hidden="true"></div>
          <div class="sheet-head">
            <h2 class="sheet-title" id="book-title">Book slot {{ selected?.slot_number }}</h2>
            <span class="se-chip se-chip--teal"><i class="fas fa-circle-check"></i>Free now</span>
            <button class="sheet-x" aria-label="Close" @click="showBook = false"><i class="fas fa-xmark"></i></button>
          </div>
          <div class="sheet-body">
            <div v-if="bookError" class="alert-custom alert-error mb-3">{{ bookError }}</div>

            <div class="form-group">
              <label class="form-label" for="v-name">Visitor’s name *</label>
              <input
                id="v-name"
                v-model="bookForm.visitor_name"
                class="form-control-custom"
                maxlength="80"
                placeholder="e.g. Asha Mehta"
                @keyup.enter="submitBook"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="v-veh">Vehicle number <span class="opt">(optional)</span></label>
              <input
                id="v-veh"
                v-model="bookForm.visitor_vehicle_number"
                class="form-control-custom veh-input"
                maxlength="14"
                placeholder="MH12AB1234"
              />
            </div>
            <div class="form-group mb-0">
              <label class="form-label" for="v-eta">Expected arrival <span class="opt">(optional)</span></label>
              <input
                id="v-eta"
                v-model="bookForm.expected_arrival_time"
                type="datetime-local"
                class="form-control-custom"
              />
            </div>

            <p class="sheet-note">
              <i class="fas fa-circle-info"></i>
              <span>The guard sees this booking — your guest just mentions the slot number at the gate.</span>
            </p>
          </div>
          <div class="sheet-foot">
            <button class="btn-primary-custom w-100" :disabled="!canBook || booking" @click="submitBook">
              <i v-if="booking" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-car-side"></i>
              {{ booking ? 'Booking…' : 'Reserve slot ' + (selected?.slot_number || '') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Add slot sheet (admin) ──────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showAdd" class="sheet-overlay" @click.self="showAdd = false">
        <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="add-title">
          <div class="sheet-grip" aria-hidden="true"></div>
          <div class="sheet-head">
            <h2 class="sheet-title" id="add-title">Add a parking slot</h2>
            <button class="sheet-x" aria-label="Close" @click="showAdd = false"><i class="fas fa-xmark"></i></button>
          </div>
          <div class="sheet-body">
            <div v-if="addError" class="alert-custom alert-error mb-3">{{ addError }}</div>
            <div class="form-group mb-0">
              <label class="form-label" for="slot-num">Slot number *</label>
              <input
                id="slot-num"
                v-model="addForm.slot_number"
                class="form-control-custom"
                maxlength="12"
                placeholder="e.g. V-01"
                @keyup.enter="submitAdd"
              />
              <p class="field-hint">Short codes work best — they’re what guests see at the gate.</p>
            </div>
          </div>
          <div class="sheet-foot">
            <button class="btn-primary-custom w-100" :disabled="!canAdd || adding" @click="submitAdd">
              <i v-if="adding" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-plus"></i>
              {{ adding ? 'Adding…' : 'Add slot' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { parkingAPI } from '../api/index'
import { authStore } from '../store/auth'
import { useCelebrate } from '../composables/useCelebrate'

const { toast, reward } = useCelebrate()

// ── Domain constants (exact backend enums) ─────────────────────
const STATUS_LABELS = { AVAILABLE: 'Free', RESERVED: 'Reserved', OCCUPIED: 'In use' }
const FILTERS = [
  { key: 'ALL', label: 'All', dot: '', empty: '' },
  { key: 'AVAILABLE', label: 'Free', dot: 'available', empty: 'Nothing free right now — check back in a bit.' },
  { key: 'RESERVED', label: 'Reserved', dot: 'reserved', empty: 'No reservations at the moment.' },
  { key: 'OCCUPIED', label: 'In use', dot: 'occupied', empty: 'No visitors parked right now.' },
]

// ── State ──────────────────────────────────────────────────────
const slots = ref([])
const loading = ref(true)
const loadFailed = ref(false)
const filter = ref('ALL')
const busy = ref(null)      // slot id with an action in flight
const busyAct = ref('')     // 'arrive' | 'release' | 'delete'

const showBook = ref(false)
const booking = ref(false)
const bookError = ref('')
const selected = ref(null)
const bookForm = ref({ visitor_name: '', visitor_vehicle_number: '', expected_arrival_time: '' })

const showAdd = ref(false)
const adding = ref(false)
const addError = ref('')
const addForm = ref({ slot_number: '' })

const isAdmin = computed(() => authStore.isAdmin)

// ── Derived ────────────────────────────────────────────────────
const stat = s => String(s.status || '').toLowerCase()
const statusLabel = s => STATUS_LABELS[String(s.status || '').toUpperCase()] || s.status
const counts = computed(() => ({
  AVAILABLE: slots.value.filter(s => stat(s) === 'available').length,
  RESERVED: slots.value.filter(s => stat(s) === 'reserved').length,
  OCCUPIED: slots.value.filter(s => stat(s) === 'occupied').length,
}))
const filtered = computed(() =>
  filter.value === 'ALL' ? slots.value : slots.value.filter(s => stat(s) === filter.value.toLowerCase())
)
const currentFilter = computed(() => FILTERS.find(f => f.key === filter.value) || FILTERS[0])
const canBook = computed(() => bookForm.value.visitor_name.trim().length > 0)
const canAdd = computed(() => addForm.value.slot_number.trim().length > 0)
const pct = n => (slots.value.length ? (n / slots.value.length) * 100 + '%' : '0%')

// ── Display helpers ────────────────────────────────────────────
function fmtWhen(v) {
  if (!v) return ''
  const d = new Date(String(v).replace(' ', 'T'))
  if (isNaN(d)) return String(v).slice(0, 16)
  const t = d.toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit' })
  if (d.toDateString() === new Date().toDateString()) return t
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) + ', ' + t
}

function sortSlots(arr) {
  return [...arr].sort((a, b) =>
    String(a.slot_number).localeCompare(String(b.slot_number), undefined, { numeric: true, sensitivity: 'base' })
  )
}

function updateSlot(updated) {
  if (!updated) return
  const i = slots.value.findIndex(s => s.id === updated.id)
  if (i > -1) slots.value[i] = updated
}

// ── Data ───────────────────────────────────────────────────────
async function load(silent = false) {
  if (!silent) { loading.value = true; loadFailed.value = false }
  try {
    const res = await parkingAPI.getAll()
    slots.value = sortSlots(res.data || [])
    loadFailed.value = false
  } catch (e) {
    if (!silent) loadFailed.value = true
  }
  loading.value = false
}
onMounted(load)

// ── Book (resident reserves for a visitor) ─────────────────────
function openBook(s) {
  selected.value = s
  bookForm.value = { visitor_name: '', visitor_vehicle_number: '', expected_arrival_time: '' }
  bookError.value = ''
  showBook.value = true
}

async function submitBook() {
  if (!canBook.value || booking.value || !selected.value) return
  booking.value = true
  bookError.value = ''
  const payload = {
    visitor_name: bookForm.value.visitor_name.trim(),
    visitor_vehicle_number: bookForm.value.visitor_vehicle_number.trim().toUpperCase() || null,
    expected_arrival_time: bookForm.value.expected_arrival_time || null,
  }
  try {
    const res = await parkingAPI.reserve(selected.value.id, payload)
    updateSlot(res.data?.slot)
    showBook.value = false
    reward(8, 'Slot ' + selected.value.slot_number + ' booked for ' + payload.visitor_name)
  } catch (e) {
    bookError.value = e.response?.data?.error || 'Couldn’t book this slot. Please try again.'
    if (e.response?.status === 400) load(true) // someone beat us to it — resync quietly
  }
  booking.value = false
}

// ── Mark arrived (admin, guard flow) ───────────────────────────
async function markArrived(s) {
  if (busy.value) return
  busy.value = s.id
  busyAct.value = 'arrive'
  try {
    const res = await parkingAPI.occupy(s.id, {})
    updateSlot(res.data?.slot)
    toast('Visitor checked in · slot ' + s.slot_number, 'success')
  } catch (e) {
    toast('Couldn’t update the slot — try again', 'error')
  }
  busy.value = null
  busyAct.value = ''
}

// ── Release ────────────────────────────────────────────────────
async function releaseSlot(s) {
  if (busy.value) return
  busy.value = s.id
  busyAct.value = 'release'
  try {
    const res = await parkingAPI.release(s.id)
    updateSlot(res.data?.slot)
    toast('Slot ' + s.slot_number + ' is free again', 'success')
  } catch (e) {
    toast('Couldn’t release the slot — try again', 'error')
  }
  busy.value = null
  busyAct.value = ''
}

// ── Add / remove (admin) ───────────────────────────────────────
function openAdd() {
  addForm.value = { slot_number: '' }
  addError.value = ''
  showAdd.value = true
}

async function submitAdd() {
  if (!canAdd.value || adding.value) return
  adding.value = true
  addError.value = ''
  try {
    const res = await parkingAPI.add({ slot_number: addForm.value.slot_number.trim() })
    slots.value = sortSlots([...slots.value, res.data])
    showAdd.value = false
    toast('Slot ' + (res.data?.slot_number || '') + ' added to the lot', 'success')
  } catch (e) {
    addError.value = e.response?.data?.error || 'Couldn’t add the slot. Please try again.'
  }
  adding.value = false
}

async function removeSlot(s) {
  if (!confirm('Remove slot ' + s.slot_number + ' from the lot?')) return
  busy.value = s.id
  busyAct.value = 'delete'
  try {
    await parkingAPI.delete(s.id)
    slots.value = slots.value.filter(x => x.id !== s.id)
    toast('Slot ' + s.slot_number + ' removed', 'info')
  } catch (e) {
    toast('Couldn’t remove the slot — try again', 'error')
  }
  busy.value = null
  busyAct.value = ''
}

// ── Sheet ergonomics: Esc closes, body scroll locks ────────────
function onKey(e) {
  if (e.key === 'Escape') { showBook.value = false; showAdd.value = false }
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
watch([showBook, showAdd], ([a, b]) => {
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
.page-sub .fa-circle-exclamation { color: var(--se-warn-600); }
.page-sub strong { color: var(--se-navy-700); font-weight: 700; }

@media (max-width: 575.98px) {
  .add-btn { flex: 1 1 100%; min-height: 48px; font-size: var(--se-fs-md); }
}

/* ── Lot at a glance ────────────────────────────────────────── */
.lot-card {
  padding: var(--se-sp-4) var(--se-sp-5);
  margin-bottom: var(--se-sp-5);
}
.occ-track {
  display: flex;
  gap: 3px;
  height: 10px;
  border-radius: var(--se-r-pill);
  background: var(--se-sunken);
  overflow: hidden;
}
.occ-seg {
  min-width: 6px;
  border-radius: var(--se-r-pill);
  transition: flex-basis var(--se-t-slow) var(--se-ease-out);
}
.occ-seg--available { background: var(--se-teal-600); }
.occ-seg--reserved { background: var(--se-warn-600); }
.occ-seg--occupied { background: var(--se-danger-600); }

/* ── Filter chips (legend + filter in one) ──────────────────── */
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: var(--se-sp-4) 0 0;
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
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot--available { background: var(--se-teal-600); }
.dot--reserved { background: var(--se-warn-600); }
.dot--occupied { background: var(--se-danger-600); }

/* ── Slot grid ──────────────────────────────────────────────── */
.slot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(168px, 1fr));
  gap: var(--se-sp-3);
}
@media (max-width: 575.98px) {
  .slot-grid { grid-template-columns: repeat(auto-fill, minmax(148px, 1fr)); }
}

.grid-enter-active { transition: opacity var(--se-t-slow) var(--se-ease-out), transform var(--se-t-slow) var(--se-ease-out); }
.grid-enter-from { opacity: 0; transform: translateY(8px) scale(0.98); }
.grid-leave-active { position: absolute; transition: opacity var(--se-t-fast); }
.grid-leave-to { opacity: 0; }
.grid-move { transition: transform var(--se-t-med) var(--se-ease-out); }

/* ── Slot tile ──────────────────────────────────────────────── */
.slot-tile {
  display: flex;
  flex-direction: column;
  padding: var(--se-sp-4);
}
.slot-tile:hover { box-shadow: var(--se-shadow-2); transform: translateY(-2px); }
.st--available { box-shadow: inset 0 3px 0 var(--se-teal-600), var(--se-shadow-1); }
.st--reserved { box-shadow: inset 0 3px 0 var(--se-warn-600), var(--se-shadow-1); }
.st--occupied { box-shadow: inset 0 3px 0 var(--se-danger-600), var(--se-shadow-1); }
.st--available:hover { box-shadow: inset 0 3px 0 var(--se-teal-600), var(--se-shadow-2); }
.st--reserved:hover { box-shadow: inset 0 3px 0 var(--se-warn-600), var(--se-shadow-2); }
.st--occupied:hover { box-shadow: inset 0 3px 0 var(--se-danger-600), var(--se-shadow-2); }

.st-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}
.st-num {
  font-family: var(--se-font-display);
  font-size: var(--se-fs-2xl);
  font-weight: 700;
  color: var(--se-ink);
  line-height: 1.1;
  overflow-wrap: anywhere;
}
.st-hint {
  margin: 8px 0 0;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}
.st-info {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.st-info li {
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
  min-width: 0;
}
.st-info li span { overflow-wrap: anywhere; }
.st-info i {
  width: 14px;
  text-align: center;
  font-size: 0.75rem;
  color: var(--se-text-faint);
  flex-shrink: 0;
}

/* ── Tile actions ───────────────────────────────────────────── */
.st-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto;
  padding-top: var(--se-sp-3);
}
.tile-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 40px;
  padding: 8px 10px;
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
              color var(--se-t-fast),
              transform var(--se-t-fast);
}
.tile-btn:hover { border-color: var(--se-navy-600); background: var(--se-navy-50); }
.tile-btn:active { transform: scale(0.98); }
.tile-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.tile-btn i { font-size: 0.85em; }

.tile-btn--book {
  background: var(--se-teal-600);
  border-color: var(--se-teal-600);
  color: #fff;
}
.tile-btn--book:hover { background: var(--se-teal-700); border-color: var(--se-teal-700); color: #fff; }

.tile-btn--arrive { color: var(--se-warn-700); }
.tile-btn--arrive:hover { border-color: var(--se-warn-600); background: var(--se-warn-50); color: var(--se-warn-ink); }

.tile-btn--del {
  flex: 0 0 40px;
  width: 40px;
  padding: 0;
  border-color: transparent;
  color: var(--se-text-faint);
}
.tile-btn--del:hover { background: var(--se-danger-50); border-color: var(--se-danger-100); color: var(--se-danger-ink); }

@media (max-width: 767.98px) {
  .fchip { min-height: 44px; }
  .tile-btn { min-height: 44px; }
  .tile-btn--del { flex: 0 0 44px; width: 44px; }
}

/* ── Empty / error states ───────────────────────────────────── */
.empty-title { font-size: var(--se-fs-lg); margin: 0 0 4px; }
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

/* ── Skeletons (mirror tile anatomy → no layout shift) ──────── */
.skel { gap: 12px; }
.sk {
  border-radius: var(--se-r-sm);
  background: linear-gradient(90deg, var(--se-sunken) 25%, var(--se-border) 45%, var(--se-sunken) 65%);
  background-size: 300% 100%;
  animation: sk-sweep 1.4s linear infinite;
}
.sk-row { display: flex; align-items: center; gap: 10px; }
.lot-sk-row { margin-top: var(--se-sp-4); }
.sk-num { width: 56px; height: 26px; }
.sk-line { height: 12px; }
.sk-pill { width: 84px; height: 24px; border-radius: var(--se-r-pill); }
.sk-pill--end { margin-left: auto; }
.sk-btn { height: 40px; border-radius: var(--se-r-md); }
.sk-track { display: block; height: 10px; border-radius: var(--se-r-pill); }
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
  width: min(480px, 100%);
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

/* ── Form details ───────────────────────────────────────────── */
.opt { color: var(--se-text-faint); font-weight: 400; }
.veh-input { text-transform: uppercase; }
.veh-input::placeholder { text-transform: none; }
.field-hint { margin: 6px 0 0; font-size: var(--se-fs-2xs); color: var(--se-text-muted); }
.sheet-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: var(--se-sp-4) 0 0;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}
.sheet-note i { margin-top: 2px; color: var(--se-navy-600); }
</style>

<template>
  <div class="notices-page">

    <!-- ══ Header ═══════════════════════════════════════════════ -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Notice board</h1>
        <p class="page-sub">Official announcements from your society committee.</p>
      </div>
      <button v-if="isAdmin" class="btn-primary-custom" @click="openAdd">
        <i class="fas fa-bullhorn"></i>Post notice
      </button>
    </div>

    <!-- ══ Loading — skeleton feed, no layout shift ═════════════ -->
    <div v-if="loading" class="sk-wrap" aria-busy="true">
      <div v-for="n in 3" :key="n" class="card sk-card">
        <div class="sk sk-icon"></div>
        <div class="sk-lines">
          <div class="sk sk-line sk-line--sm"></div>
          <div class="sk sk-line sk-line--lg"></div>
          <div class="sk sk-line sk-line--md"></div>
        </div>
      </div>
    </div>

    <!-- ══ Load error — never a dead end ════════════════════════ -->
    <div v-else-if="loadError" class="card empty-state rise-in">
      <i class="fas fa-plug-circle-xmark"></i>
      <p>We couldn't reach the notice board. Check your connection and try again.</p>
      <button class="btn-primary-custom mt-3" @click="load"><i class="fas fa-rotate-right"></i>Retry</button>
    </div>

    <!-- ══ Empty board ══════════════════════════════════════════ -->
    <div v-else-if="notices.length === 0" class="card empty-state rise-in">
      <i class="fas fa-bullhorn"></i>
      <h2 class="empty-title">All quiet for now</h2>
      <p v-if="isAdmin">Nothing on the board yet — post the first notice and keep every resident in the loop.</p>
      <p v-else>When the committee posts an announcement, it lands here first.</p>
      <button v-if="isAdmin" class="btn-accent mt-3" @click="openAdd">
        <i class="fas fa-bullhorn"></i>Post the first notice
      </button>
    </div>

    <template v-else>
      <!-- ══ Category chips ═════════════════════════════════════ -->
      <div class="filter-row" aria-label="Filter notices by category">
        <button
          v-for="c in chips" :key="c.key"
          class="filter-chip" :class="{ 'filter-chip--active': filter === c.key }"
          :aria-pressed="filter === c.key ? 'true' : 'false'"
          @click="filter = c.key"
        >
          <i v-if="c.icon" class="fas" :class="c.icon"></i>{{ c.label }}
          <span class="chip-n se-num">{{ c.count }}</span>
        </button>
      </div>

      <!-- ══ Feed ═══════════════════════════════════════════════ -->
      <TransitionGroup v-if="visible.length" tag="div" class="nlist" name="nlist" appear>
        <article
          v-for="(n, i) in visible" :key="n.id"
          class="card notice-card"
          :class="{ 'notice-card--emergency': n.category === 'EMERGENCY' }"
          :style="{ '--i': Math.min(i, 8) }"
        >
          <div class="notice-icon" :class="`tint--${catKey(n.category)}`">
            <i class="fas" :class="catMeta(n.category).icon"></i>
          </div>
          <div class="notice-main">
            <div class="notice-top">
              <span class="badge-custom" :class="catMeta(n.category).badge">{{ catMeta(n.category).label }}</span>
              <span v-if="isNew(n)" class="se-chip se-chip--marigold notice-new">New</span>
              <time class="notice-when" :datetime="n.created_at" :title="fmtFull(n.created_at)">{{ timeAgo(n.created_at) }}</time>
            </div>
            <h3 class="notice-title">{{ n.title }}</h3>
            <p class="notice-text" :class="{ 'notice-text--clamp': isLong(n) && !expanded.includes(n.id) }">{{ n.content }}</p>
            <button v-if="isLong(n)" class="notice-more" @click="toggleExpand(n.id)">
              {{ expanded.includes(n.id) ? 'Show less' : 'Read more' }}
              <i class="fas" :class="expanded.includes(n.id) ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </button>
            <div class="notice-foot">
              <span class="se-avatar se-avatar--sm">{{ initials(n.published_by_name) }}</span>
              <span class="notice-author">{{ n.published_by_name || 'Committee' }}</span>
              <div v-if="isAdmin" class="notice-actions">
                <button class="act-btn" aria-label="Edit notice" title="Edit" @click="openEdit(n)">
                  <i class="fas fa-pen"></i>
                </button>
                <button
                  class="act-btn"
                  :class="{ 'act-btn--armed': confirmId === n.id }"
                  :aria-label="confirmId === n.id ? 'Tap again to confirm removal' : 'Remove notice'"
                  :title="confirmId === n.id ? 'Tap again to confirm' : 'Remove'"
                  @click="askDelete(n)"
                >
                  <i class="fas" :class="confirmId === n.id ? 'fa-triangle-exclamation' : 'fa-trash-can'"></i>
                  <span v-if="confirmId === n.id">Sure?</span>
                </button>
              </div>
            </div>
          </div>
        </article>
      </TransitionGroup>

      <!-- ══ Nothing in this category ═══════════════════════════ -->
      <div v-else class="card empty-state rise-in">
        <i class="fas" :class="catMeta(filter).icon"></i>
        <p>No {{ catMeta(filter).label.toLowerCase() }} notices right now.</p>
        <button class="btn-ghost mt-3" @click="filter = 'ALL'">
          <i class="fas fa-filter-circle-xmark"></i>Show all notices
        </button>
      </div>
    </template>

    <!-- ══ Post / edit sheet (bottom sheet on mobile) ═══════════ -->
    <transition name="sheet">
      <div v-if="sheetOpen" class="se-overlay" @click.self="closeSheet">
        <div class="se-sheet" role="dialog" aria-modal="true" :aria-label="editingId ? 'Edit notice' : 'Post notice'">
          <div class="sheet-grab" aria-hidden="true"></div>
          <header class="sheet-head">
            <h6><i class="fas fa-bullhorn me-2"></i>{{ editingId ? 'Edit notice' : 'Post a notice' }}</h6>
            <button class="sheet-close" :disabled="saving" aria-label="Close" @click="closeSheet"><i class="fas fa-times"></i></button>
          </header>
          <div class="sheet-body">
            <div class="form-group">
              <label class="form-label" for="notice-title">Title</label>
              <input
                id="notice-title" v-model.trim="form.title" class="form-control-custom"
                maxlength="140" placeholder="e.g. Water shutdown on Saturday" @keyup.enter="submit"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="notice-content">Message</label>
              <textarea
                id="notice-content" v-model.trim="form.content" class="form-control-custom" rows="4"
                placeholder="Write the full announcement — what, when, and what residents should do."
              ></textarea>
            </div>
            <div class="form-label" id="cat-label">Category</div>
            <div class="cat-seg" role="radiogroup" aria-labelledby="cat-label">
              <button
                v-for="c in CAT_KEYS" :key="c" type="button"
                class="cat-btn" :class="{ 'cat-btn--active': form.category === c }"
                role="radio" :aria-checked="form.category === c ? 'true' : 'false'"
                @click="form.category = c"
              >
                <i class="fas" :class="CATS[c].icon"></i>{{ CATS[c].label }}
              </button>
            </div>
            <p class="cat-hint">{{ CATS[form.category]?.hint }}</p>
            <div v-if="formError" class="alert-custom alert-error">
              <i class="fas fa-circle-exclamation"></i><span>{{ formError }}</span>
            </div>
          </div>
          <footer class="sheet-foot">
            <button class="btn-ghost" :disabled="saving" @click="closeSheet">Cancel</button>
            <button class="btn-primary-custom sheet-cta" :disabled="saving || !canSubmit" @click="submit">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? (editingId ? 'Saving…' : 'Posting…') : (editingId ? 'Save changes' : 'Post notice') }}
            </button>
          </footer>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { noticesAPI } from '../api/index'
import { authStore } from '../store/auth'
import { useCelebrate } from '../composables/useCelebrate'

const { reward, toast } = useCelebrate()

const CATS = {
  GENERAL: { label: 'General', icon: 'fa-circle-info', badge: 'badge-low', hint: 'Day-to-day updates for every resident.' },
  FINANCIAL: { label: 'Financial', icon: 'fa-indian-rupee-sign', badge: 'badge-open', hint: 'Dues, budgets, audits and society finances.' },
  MAINTENANCE: { label: 'Maintenance', icon: 'fa-screwdriver-wrench', badge: 'badge-medium', hint: 'Repairs, shutdowns and scheduled upkeep.' },
  EMERGENCY: { label: 'Emergency', icon: 'fa-triangle-exclamation', badge: 'badge-urgent', hint: 'Time-critical alerts — use sparingly.' },
}
const CAT_KEYS = Object.keys(CATS)

const notices = ref([])
const loading = ref(true)
const loadError = ref(false)
const saving = ref(false)
const sheetOpen = ref(false)
const editingId = ref(null)
const filter = ref('ALL')
const confirmId = ref(null)
const expanded = ref([])
const formError = ref('')
const form = ref({ title: '', content: '', category: 'GENERAL' })
const isAdmin = authStore.isAdmin
let confirmTimer = null

onMounted(load)
onBeforeUnmount(() => clearTimeout(confirmTimer))

async function load() {
  loading.value = true
  loadError.value = false
  try {
    notices.value = (await noticesAPI.getAll()).data || []
  } catch (e) {
    loadError.value = true
  }
  loading.value = false
}

const chips = computed(() => {
  const base = [{ key: 'ALL', label: 'All', icon: null, count: notices.value.length }]
  for (const k of CAT_KEYS) {
    const count = notices.value.filter(n => n.category === k).length
    if (count) base.push({ key: k, label: CATS[k].label, icon: CATS[k].icon, count })
  }
  return base
})

const visible = computed(() => filter.value === 'ALL'
  ? notices.value
  : notices.value.filter(n => n.category === filter.value))

const canSubmit = computed(() => !!form.value.title && !!form.value.content)

function openAdd() {
  editingId.value = null
  form.value = { title: '', content: '', category: 'GENERAL' }
  formError.value = ''
  sheetOpen.value = true
}

function openEdit(n) {
  editingId.value = n.id
  form.value = { title: n.title, content: n.content, category: CATS[n.category] ? n.category : 'GENERAL' }
  formError.value = ''
  sheetOpen.value = true
}

function closeSheet() {
  if (saving.value) return
  sheetOpen.value = false
}

async function submit() {
  if (!canSubmit.value || saving.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      const res = await noticesAPI.update(editingId.value, { ...form.value })
      const i = notices.value.findIndex(n => n.id === editingId.value)
      if (i !== -1) notices.value[i] = res.data
      toast('Notice updated', 'success')
    } else {
      const res = await noticesAPI.add({ ...form.value })
      notices.value.unshift(res.data)
      filter.value = 'ALL'
      reward(10, 'Kept the community informed')
    }
    sheetOpen.value = false
  } catch (e) {
    formError.value = e.response?.data?.error || 'Could not save the notice — please try again.'
  }
  saving.value = false
}

/* Two-tap delete: first tap arms the button, second confirms. */
function askDelete(n) {
  if (confirmId.value === n.id) {
    clearTimeout(confirmTimer)
    confirmId.value = null
    doDelete(n)
    return
  }
  confirmId.value = n.id
  clearTimeout(confirmTimer)
  confirmTimer = setTimeout(() => { confirmId.value = null }, 3500)
}

async function doDelete(n) {
  try {
    await noticesAPI.delete(n.id)
    notices.value = notices.value.filter(x => x.id !== n.id)
    toast('Notice removed from the board', 'info')
  } catch (e) {
    toast('Could not remove the notice — try again.', 'error')
  }
}

function toggleExpand(id) {
  const i = expanded.value.indexOf(id)
  i === -1 ? expanded.value.push(id) : expanded.value.splice(i, 1)
}

function isLong(n) { return String(n.content || '').length > 220 }

function catMeta(c) {
  return CATS[c] || { label: c ? String(c).toLowerCase() : 'general', icon: 'fa-circle-info', badge: 'badge-low' }
}

function catKey(c) { return (CATS[c] ? c : 'GENERAL').toLowerCase() }

function initials(name) {
  if (!name) return 'SE'
  return name.trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

/* Backend sends naive-UTC "YYYY-MM-DD HH:MM:SS.ffffff" strings. */
function parseDT(v) {
  if (!v) return null
  const raw = String(v).trim()
  if (/(Z|[+-]\d\d:?\d\d)$/.test(raw)) {
    const d = new Date(raw)
    return isNaN(d.getTime()) ? null : d
  }
  let s = raw.includes('T') ? raw : raw.replace(' ', 'T')
  if (s.length > 19) s = s.slice(0, 19)
  if (!s.includes('T')) s += 'T00:00:00'
  const d = new Date(s + 'Z')
  return isNaN(d.getTime()) ? null : d
}

function timeAgo(v) {
  const d = parseDT(v)
  if (!d) return String(v || '').slice(0, 10)
  const secs = Math.max(0, (Date.now() - d.getTime()) / 1000)
  if (secs < 60) return 'just now'
  const m = Math.floor(secs / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  if (days === 1) return 'yesterday'
  if (days < 7) return `${days}d ago`
  const opts = { day: 'numeric', month: 'short' }
  if (d.getFullYear() !== new Date().getFullYear()) opts.year = 'numeric'
  return d.toLocaleDateString('en-IN', opts)
}

function fmtFull(v) {
  const d = parseDT(v)
  return d
    ? d.toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' })
    : String(v || '')
}

function isNew(n) {
  const d = parseDT(n.created_at)
  return !!d && (Date.now() - d.getTime()) < 48 * 3600 * 1000
}
</script>

<style scoped>
.page-sub { margin: 4px 0 0; font-size: var(--se-fs-sm); color: var(--se-text-muted); }
.empty-title {
  margin: 4px 0 6px;
  font-family: var(--se-font-display);
  font-size: var(--se-fs-xl);
  font-weight: 700;
  color: var(--se-ink);
}

/* ══ Category chips ══════════════════════════════════════════ */
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: var(--se-sp-4); }
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 8px 14px;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-pill);
  background: var(--se-surface);
  color: var(--se-text-muted);
  font-weight: 600;
  font-size: var(--se-fs-sm);
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast), border-color var(--se-t-fast);
}
.filter-chip:hover { border-color: var(--se-navy-500); color: var(--se-navy-700); }
[data-theme="dark"] .filter-chip:hover { color: var(--se-ink); }
.filter-chip--active { background: var(--se-navy-800); border-color: var(--se-navy-800); color: #fff; }
.filter-chip--active:hover { color: #fff; }
.chip-n {
  font-size: var(--se-fs-2xs);
  padding: 1px 8px;
  border-radius: var(--se-r-pill);
  background: var(--se-sunken);
  color: var(--se-text-muted);
}
.filter-chip--active .chip-n { background: rgba(255, 255, 255, .16); color: #fff; }

/* ══ Feed ════════════════════════════════════════════════════ */
.nlist { position: relative; display: flex; flex-direction: column; gap: var(--se-sp-3); }
.notice-card {
  display: flex;
  gap: 14px;
  padding: var(--se-sp-5);
}
.notice-card:hover { box-shadow: var(--se-shadow-2); transform: translateY(-2px); }
.notice-card--emergency { border-left: 3px solid var(--se-danger-600); }
.notice-icon {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: var(--se-r-md);
  font-size: 1rem;
}
.tint--general { background: var(--se-sunken); color: var(--se-text-muted); }
.tint--financial { background: var(--se-navy-50); color: var(--se-navy-700); }
.tint--maintenance { background: var(--se-warn-50); color: var(--se-warn-ink); }
.tint--emergency { background: var(--se-danger-50); color: var(--se-danger-ink); }
[data-theme="dark"] .tint--financial { color: var(--se-ink); }
[data-theme="dark"] .tint--maintenance { color: var(--se-warn-600); }
[data-theme="dark"] .tint--emergency { color: var(--se-danger-600); }

.notice-main { flex: 1; min-width: 0; }
.notice-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.notice-new { padding: 3px 9px; font-size: var(--se-fs-2xs); text-transform: uppercase; letter-spacing: .05em; }
.notice-when {
  margin-left: auto;
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  white-space: nowrap;
  color: var(--se-text-faint);
}
.notice-title {
  margin: 10px 0 4px;
  font-family: var(--se-font-display);
  font-size: var(--se-fs-lg);
  font-weight: 700;
  color: var(--se-ink);
  overflow-wrap: anywhere;
}
.notice-text {
  margin: 0;
  font-size: var(--se-fs-sm);
  color: var(--se-text);
  white-space: pre-line;
  overflow-wrap: anywhere;
}
.notice-text--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.notice-more {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 4px 0;
  border: 0;
  background: none;
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-navy-600);
  cursor: pointer;
}
.notice-more:hover { color: var(--se-navy-700); text-decoration: underline; }
[data-theme="dark"] .notice-more { color: var(--se-text-muted); }
[data-theme="dark"] .notice-more:hover { color: var(--se-ink); }
.notice-foot {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: var(--se-sp-3);
  padding-top: var(--se-sp-3);
  border-top: 1px solid var(--se-border);
}
.notice-author { font-size: var(--se-fs-xs); font-weight: 600; color: var(--se-text-muted); }
.notice-actions { display: flex; gap: 6px; margin-left: auto; }
.act-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 38px;
  height: 38px;
  padding: 0 10px;
  border: 0;
  border-radius: var(--se-r-md);
  background: var(--se-sunken);
  color: var(--se-text-muted);
  font-size: var(--se-fs-xs);
  font-weight: 700;
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast);
}
.act-btn:hover { background: var(--se-border); color: var(--se-ink); }
.act-btn--armed, .act-btn--armed:hover { background: var(--se-danger-50); color: var(--se-danger-ink); }
[data-theme="dark"] .act-btn--armed, [data-theme="dark"] .act-btn--armed:hover { color: var(--se-danger-600); }

/* feed enter / leave / reorder */
.nlist-enter-active {
  transition: opacity var(--se-t-slow) var(--se-ease-out), transform var(--se-t-slow) var(--se-ease-out);
  transition-delay: calc(var(--i, 0) * 45ms);
}
.nlist-enter-from { opacity: 0; transform: translateY(10px); }
.nlist-leave-active {
  position: absolute;
  width: 100%;
  transition: opacity var(--se-t-fast) var(--se-ease-std), transform var(--se-t-fast) var(--se-ease-std);
}
.nlist-leave-to { opacity: 0; transform: scale(.98); }
.nlist-move { transition: transform var(--se-t-med) var(--se-ease-out); }

/* ══ Ghost button (secondary, 44px target) ═══════════════════ */
.btn-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 10px 16px;
  background: transparent;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-md);
  color: var(--se-text);
  font-family: var(--se-font-body);
  font-weight: 600;
  font-size: var(--se-fs-sm);
  cursor: pointer;
  transition: background var(--se-t-fast), border-color var(--se-t-fast);
}
.btn-ghost:hover { background: var(--se-sunken); }
.btn-ghost:disabled { opacity: .55; cursor: not-allowed; }

/* ══ Overlay + sheet (dialog on desktop, bottom sheet <576px) ═ */
.se-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--se-sp-4);
  background: rgba(16, 27, 51, .55);
}
.se-sheet {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 460px;
  max-height: min(88vh, 720px);
  background: var(--se-surface);
  border: 1px solid var(--se-border);
  border-radius: var(--se-r-lg);
  box-shadow: var(--se-shadow-3);
}
.sheet-grab { display: none; }
.sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: var(--se-sp-4) var(--se-sp-5);
  border-bottom: 1px solid var(--se-border);
}
.sheet-head h6 { margin: 0; font-weight: 700; font-size: var(--se-fs-md); }
.sheet-close {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: var(--se-r-md);
  background: var(--se-sunken);
  color: var(--se-text-muted);
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast);
}
.sheet-close:hover { background: var(--se-border); color: var(--se-ink); }
.sheet-close:disabled { opacity: .55; cursor: not-allowed; }
.sheet-body { padding: var(--se-sp-5); overflow-y: auto; }
.sheet-foot {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: var(--se-sp-4) var(--se-sp-5);
  border-top: 1px solid var(--se-border);
}
.sheet-cta { min-height: 44px; }
.sheet-body .alert-custom { margin-top: var(--se-sp-4); }

/* category segment */
.cat-seg { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.cat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-md);
  background: var(--se-surface);
  color: var(--se-text-muted);
  font-family: var(--se-font-body);
  font-weight: 600;
  font-size: var(--se-fs-sm);
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast), border-color var(--se-t-fast);
}
.cat-btn:hover { border-color: var(--se-navy-500); color: var(--se-navy-700); }
.cat-btn--active, .cat-btn--active:hover { border-color: var(--se-navy-700); background: var(--se-navy-50); color: var(--se-navy-700); }
[data-theme="dark"] .cat-btn:hover, [data-theme="dark"] .cat-btn--active, [data-theme="dark"] .cat-btn--active:hover { color: var(--se-ink); }
.cat-hint { margin: 8px 0 0; min-height: 1.3em; font-size: var(--se-fs-xs); color: var(--se-text-muted); }

/* sheet transition: fade backdrop, rise dialog / slide-up sheet */
.sheet-enter-active, .sheet-leave-active { transition: opacity var(--se-t-med) var(--se-ease-std); }
.sheet-enter-active .se-sheet, .sheet-leave-active .se-sheet { transition: transform var(--se-t-slow) var(--se-ease-out); }
.sheet-enter-from, .sheet-leave-to { opacity: 0; }
.sheet-enter-from .se-sheet, .sheet-leave-to .se-sheet { transform: translateY(14px); }

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
.sk-card {
  display: flex;
  gap: 14px;
  min-height: 132px;
  padding: var(--se-sp-5);
}
.sk-icon { width: 42px; height: 42px; border-radius: var(--se-r-md); flex-shrink: 0; }
.sk-lines { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.sk-line { height: 12px; }
.sk-line--lg { width: 58%; height: 18px; }
.sk-line--md { width: 82%; }
.sk-line--sm { width: 20%; }
@keyframes sk-shimmer { to { transform: translateX(100%); } }

/* ══ Entrance motion ═════════════════════════════════════════ */
.rise-in { animation: rise var(--se-t-slow) var(--se-ease-out) both; }
@keyframes rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}

/* ══ Small screens — thumbs first ════════════════════════════ */
@media (max-width: 575.98px) {
  .se-page-actions > .btn-primary-custom { width: 100%; }
  .notice-card { padding: var(--se-sp-4); }
  .act-btn { min-width: 44px; height: 44px; }

  /* dialogs become bottom sheets */
  .se-overlay { align-items: flex-end; padding: 0; }
  .se-sheet {
    max-width: none;
    max-height: 92dvh;
    border-bottom: 0;
    border-radius: var(--se-r-lg) var(--se-r-lg) 0 0;
  }
  .sheet-grab {
    display: block;
    width: 44px;
    height: 4px;
    margin: 10px auto 0;
    border-radius: var(--se-r-pill);
    background: var(--se-border-strong);
  }
  .sheet-foot { padding-bottom: calc(var(--se-sp-4) + env(safe-area-inset-bottom)); }
  .sheet-foot > button { flex: 1; }
  .sheet-enter-from .se-sheet, .sheet-leave-to .se-sheet { transform: translateY(100%); }
}

@media (prefers-reduced-motion: reduce) {
  .rise-in { animation: none; }
  .notice-card:hover { transform: none; }
  .nlist-enter-active, .nlist-leave-active, .nlist-move,
  .sheet-enter-active, .sheet-leave-active,
  .sheet-enter-active .se-sheet, .sheet-leave-active .se-sheet { transition: none; }
  .sk::after { animation: none; }
}
</style>

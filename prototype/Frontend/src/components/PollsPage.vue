<template>
  <div class="polls-page">
    <!-- ── Header: title, live summary, one primary action ─────── -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Polls</h1>
        <p class="page-sub">
          <template v-if="loading">Opening the ballot box…</template>
          <template v-else-if="loadFailed">Having trouble reaching the server</template>
          <template v-else-if="activeCount">
            <i class="fas fa-check-to-slot" aria-hidden="true"></i>
            <span><strong class="se-num">{{ activeCount }}</strong> open for voting · <strong class="se-num">{{ closedCount }}</strong> closed</span>
          </template>
          <template v-else>
            <i class="fas fa-circle-check" aria-hidden="true"></i>
            <span>No open polls — nothing needs your vote right now</span>
          </template>
        </p>
      </div>
      <button v-if="isAdmin" type="button" class="btn-primary-custom new-btn" @click="openCreate">
        <i class="fas fa-plus" aria-hidden="true"></i><span>New poll</span>
      </button>
    </div>

    <!-- ── Filter chips ────────────────────────────────────────── -->
    <div v-if="!loading && !loadFailed && polls.length" class="filter-row" role="group" aria-label="Filter polls">
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

    <!-- ── Loading: skeletons mirror the card anatomy ──────────── -->
    <div v-if="loading" class="plist" aria-hidden="true">
      <div v-for="n in 2" :key="n" class="card skel">
        <div class="sk-row">
          <span class="sk sk-pill"></span>
          <span class="sk sk-pill sk-pill--end"></span>
        </div>
        <span class="sk sk-line sk-line--w60"></span>
        <span class="sk sk-line sk-line--w40"></span>
        <div v-for="r in 3" :key="r" class="sk-opt">
          <span class="sk sk-line" :class="r % 2 ? 'sk-line--w30' : 'sk-line--w40'"></span>
          <span class="sk sk-rail"></span>
        </div>
      </div>
    </div>

    <!-- ── Load error: never a dead end ────────────────────────── -->
    <div v-else-if="loadFailed" class="card empty-state">
      <i class="fas fa-triangle-exclamation" aria-hidden="true"></i>
      <h3 class="empty-title">Couldn’t load the polls</h3>
      <p>Check your connection, then give it another go.</p>
      <button type="button" class="btn-primary-custom mt-3" @click="load">
        <i class="fas fa-rotate-right" aria-hidden="true"></i>Try again
      </button>
    </div>

    <!-- ── Empty: guide the first action ───────────────────────── -->
    <div v-else-if="polls.length === 0" class="card empty-state">
      <i class="fas fa-square-poll-vertical" aria-hidden="true"></i>
      <h3 class="empty-title">No polls yet</h3>
      <p v-if="isAdmin">Put a question to the society — voting takes residents a single tap.</p>
      <p v-else>The committee hasn’t opened any votes yet. Check back soon.</p>
      <button v-if="isAdmin" type="button" class="btn-primary-custom mt-3" @click="openCreate">
        <i class="fas fa-plus" aria-hidden="true"></i>Create the first poll
      </button>
    </div>

    <template v-else>
      <!-- filtered-out empty -->
      <div v-if="filtered.length === 0" class="card empty-state">
        <i class="fas fa-filter-circle-xmark" aria-hidden="true"></i>
        <p>{{ filter === 'ACTIVE' ? 'No active polls — everything’s been decided.' : 'No closed polls yet.' }}</p>
      </div>

      <!-- ── Poll cards ──────────────────────────────────────────── -->
      <div class="plist">
        <article v-for="(p, i) in filtered" :key="p.id" class="card poll-card" :style="{ '--i': i }">
          <header class="poll-head">
            <span class="badge-custom" :class="p.status === 'ACTIVE' ? 'badge-active' : 'badge-closed'">{{ statusLabel(p) }}</span>
            <div v-if="isAdmin" class="poll-tools">
              <button
                v-if="p.status === 'ACTIVE'"
                type="button"
                class="tool-btn"
                :disabled="closingId === p.id"
                @click="closePoll(p)"
              >
                <i class="fas" :class="closingId === p.id ? 'fa-spinner fa-spin' : 'fa-lock'" aria-hidden="true"></i>
                <span>Close poll</span>
              </button>
              <button
                type="button"
                class="tool-btn tool-btn--danger"
                :class="{ 'is-armed': armedDelete === p.id }"
                :disabled="deletingId === p.id"
                :aria-label="armedDelete === p.id ? 'Tap again to confirm delete' : 'Delete poll'"
                @click="armedDelete === p.id ? confirmDelete(p) : askDelete(p)"
              >
                <i class="fas" :class="deletingId === p.id ? 'fa-spinner fa-spin' : 'fa-trash-can'" aria-hidden="true"></i>
                <span v-if="armedDelete === p.id">Sure?</span>
              </button>
            </div>
          </header>

          <h2 class="poll-title">{{ p.title }}</h2>
          <p v-if="p.description" class="poll-desc">{{ p.description }}</p>

          <!-- One-tap voting (active + not voted yet) -->
          <div v-if="!showResults(p)" class="vote-list" role="group" :aria-label="`Vote: ${p.title}`">
            <button
              v-for="opt in p.options"
              :key="opt.id"
              type="button"
              class="vote-opt"
              :disabled="votingPoll === p.id"
              :aria-label="`Vote for ${opt.text}`"
              @click="castVote(p, opt)"
            >
              <span class="vote-ring" aria-hidden="true">
                <i v-if="votingPoll === p.id && votingOpt === opt.id" class="fas fa-spinner fa-spin"></i>
              </span>
              <span class="vote-text">{{ opt.text }}</span>
              <span class="vote-go" aria-hidden="true"><i class="fas fa-arrow-right"></i></span>
            </button>
            <p class="vote-hint">
              <i class="fas fa-bolt" aria-hidden="true"></i>
              One tap to vote · earns <span class="se-num">+20</span> NP
            </p>
          </div>

          <!-- Results (voted or closed) -->
          <div v-else class="result-list">
            <div v-for="(opt, bi) in p.options" :key="opt.id" class="result" :class="{ 'is-mine': myChoice(p) === opt.id }">
              <div class="result-row">
                <span class="result-label">
                  <i v-if="myChoice(p) === opt.id" class="fas fa-circle-check" aria-hidden="true"></i>
                  <span v-if="myChoice(p) === opt.id" class="visually-hidden">Your vote —</span>
                  {{ opt.text }}
                  <span v-if="p.status === 'CLOSED' && isLeading(p, opt)" class="se-chip se-chip--marigold result-win">
                    <i class="fas fa-crown" aria-hidden="true"></i>Winner
                  </span>
                </span>
                <span class="result-nums se-num">{{ votesLabel(opt.votes) }} · {{ pct(opt) }}%</span>
              </div>
              <div class="progress-bar-custom" aria-hidden="true">
                <div
                  class="progress-fill res-fill"
                  :class="{ 'res-fill--lead': isLeading(p, opt) }"
                  :style="{ width: pct(opt) + '%', '--bi': bi }"
                ></div>
              </div>
            </div>
            <p v-if="hasVoted(p) && p.status === 'ACTIVE'" class="vote-hint vote-hint--done">
              <i class="fas fa-circle-check" aria-hidden="true"></i>
              Your vote is in — results update as neighbours vote
            </p>
          </div>

          <footer class="poll-meta">
            <span><i class="fas fa-users" aria-hidden="true"></i>{{ votesLabel(p.total_votes) }}</span>
            <span v-if="p.status === 'ACTIVE' && p.end_date"><i class="fas fa-calendar-day" aria-hidden="true"></i>Ends {{ fmtDate(p.end_date) }}</span>
            <span v-if="p.created_at"><i class="fas fa-clock" aria-hidden="true"></i>Started {{ fmtDate(p.created_at) }}</span>
          </footer>
        </article>
      </div>
    </template>

    <!-- ── Create sheet (modal on desktop → bottom sheet <576px) ── -->
    <Teleport to="body">
      <div v-if="showCreate" class="sheet-overlay" @click.self="showCreate = false">
        <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="poll-sheet-title">
          <div class="sheet-grip" aria-hidden="true"></div>
          <div class="sheet-head">
            <h2 class="sheet-title" id="poll-sheet-title">Create a poll</h2>
            <button type="button" class="sheet-x" aria-label="Close" @click="showCreate = false"><i class="fas fa-xmark"></i></button>
          </div>
          <div class="sheet-body">
            <div v-if="formError" class="alert-custom alert-error mb-3">{{ formError }}</div>

            <div class="form-group">
              <label class="form-label" for="poll-q">Question <span class="req">*</span></label>
              <input
                id="poll-q"
                v-model="form.title"
                class="form-control-custom"
                maxlength="140"
                placeholder="e.g. Should we get an AMC for the generator?"
                autofocus
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="poll-d">Description <span class="optional">(optional)</span></label>
              <textarea
                id="poll-d"
                v-model="form.description"
                class="form-control-custom"
                rows="2"
                maxlength="280"
                placeholder="A line of context helps people decide"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Options <span class="optional">(at least 2)</span></label>
              <div v-for="(o, i) in form.options" :key="i" class="opt-row">
                <input
                  v-model="form.options[i]"
                  class="form-control-custom"
                  maxlength="80"
                  :placeholder="`Option ${i + 1}`"
                  :aria-label="`Option ${i + 1}`"
                  @keyup.enter="i === form.options.length - 1 && addOption()"
                />
                <button
                  v-if="form.options.length > 2"
                  type="button"
                  class="opt-del"
                  :aria-label="`Remove option ${i + 1}`"
                  @click="removeOption(i)"
                ><i class="fas fa-xmark"></i></button>
              </div>
              <button type="button" class="opt-add" @click="addOption">
                <i class="fas fa-plus" aria-hidden="true"></i>Add option
              </button>
            </div>

            <div class="form-group mb-0">
              <label class="form-label" for="poll-end">Voting ends <span class="optional">(optional)</span></label>
              <input id="poll-end" v-model="form.end_date" type="date" class="form-control-custom" :min="today" />
            </div>
          </div>
          <div class="sheet-foot">
            <button type="button" class="btn-primary-custom w-100" :disabled="!canCreate || saving" @click="createPoll">
              <i class="fas" :class="saving ? 'fa-spinner fa-spin' : 'fa-paper-plane'" aria-hidden="true"></i>
              {{ saving ? 'Publishing…' : 'Publish poll' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { pollsAPI } from '../api/index'
import { authStore } from '../store/auth'
import { useCelebrate } from '../composables/useCelebrate'

const { reward, toast } = useCelebrate()

const polls = ref([])
const loading = ref(true)
const loadFailed = ref(false)
const isAdmin = computed(() => authStore.isAdmin)

const FILTERS = [
  { key: 'ALL', label: 'All' },
  { key: 'ACTIVE', label: 'Active' },
  { key: 'CLOSED', label: 'Closed' },
]
const filter = ref('ALL')

// ── My votes — remembered per user so the highlight survives reloads
const VOTES_KEY = `se-poll-votes:${authStore.user?.id ?? 'anon'}`
const myVotes = ref({})
try { myVotes.value = JSON.parse(localStorage.getItem(VOTES_KEY) || '{}') } catch { myVotes.value = {} }
function rememberVote(pollId, optionId) {
  myVotes.value = { ...myVotes.value, [pollId]: optionId }
  try { localStorage.setItem(VOTES_KEY, JSON.stringify(myVotes.value)) } catch { /* storage full/blocked — session state still holds */ }
}

// ── Load
async function load() {
  loading.value = true
  loadFailed.value = false
  try {
    polls.value = (await pollsAPI.getAll()).data
  } catch (e) {
    loadFailed.value = true
  }
  loading.value = false
}
onMounted(load)

// ── Derived
const activeCount = computed(() => polls.value.filter(p => p.status === 'ACTIVE').length)
const closedCount = computed(() => polls.value.length - activeCount.value)
const counts = computed(() => ({ ALL: polls.value.length, ACTIVE: activeCount.value, CLOSED: closedCount.value }))
const filtered = computed(() => (filter.value === 'ALL' ? polls.value : polls.value.filter(p => p.status === filter.value)))

function hasVoted(p) { return !!myVotes.value[p.id] }
function myChoice(p) { return myVotes.value[p.id] }
function showResults(p) { return p.status !== 'ACTIVE' || hasVoted(p) }
function statusLabel(p) { return p.status === 'ACTIVE' ? 'Active' : 'Closed' }
function votesLabel(n) { return n === 1 ? '1 vote' : `${n || 0} votes` }
function pct(opt) { return Math.round(opt.percentage || 0) }
function maxVotes(p) { return Math.max(0, ...p.options.map(o => o.votes || 0)) }
function isLeading(p, opt) { const m = maxVotes(p); return m > 0 && (opt.votes || 0) === m }
function fmtDate(s) {
  if (!s) return ''
  const d = new Date(String(s).replace(' ', 'T'))
  return isNaN(d.getTime()) ? '' : d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

// ── One-tap voting
const votingPoll = ref(null)
const votingOpt = ref(null)

async function castVote(p, opt) {
  if (p.status !== 'ACTIVE' || hasVoted(p) || votingPoll.value) return
  votingPoll.value = p.id
  votingOpt.value = opt.id
  try {
    const res = await pollsAPI.vote(p.id, { option_id: opt.id })
    const idx = polls.value.findIndex(x => x.id === p.id)
    if (idx > -1) polls.value[idx] = res.data.poll
    rememberVote(p.id, opt.id)
    reward(20, 'Voted in a poll')
  } catch (e) {
    if (e.response?.status === 409) {
      // voted earlier (another session/device) — lock it in locally too
      rememberVote(p.id, true)
      toast('You have already voted in this poll', 'info')
    } else {
      toast(e.response?.data?.error || 'Could not record your vote — try again', 'error')
    }
  }
  votingPoll.value = null
  votingOpt.value = null
}

// ── Admin: close
const closingId = ref(null)
async function closePoll(p) {
  if (closingId.value) return
  closingId.value = p.id
  try {
    const res = await pollsAPI.close(p.id)
    const idx = polls.value.findIndex(x => x.id === p.id)
    if (idx > -1) polls.value[idx] = res.data.poll
    toast('Poll closed — results are final', 'info')
  } catch (e) {
    toast(e.response?.data?.error || 'Could not close the poll', 'error')
  }
  closingId.value = null
}

// ── Admin: delete (two-tap confirm, no browser dialogs)
const armedDelete = ref(null)
const deletingId = ref(null)
let armTimer = null
function askDelete(p) {
  clearTimeout(armTimer)
  armedDelete.value = p.id
  armTimer = setTimeout(() => { armedDelete.value = null }, 3500)
}
async function confirmDelete(p) {
  clearTimeout(armTimer)
  armedDelete.value = null
  deletingId.value = p.id
  try {
    await pollsAPI.delete(p.id)
    polls.value = polls.value.filter(x => x.id !== p.id)
    toast('Poll deleted', 'info')
  } catch (e) {
    toast(e.response?.data?.error || 'Could not delete the poll', 'error')
  }
  deletingId.value = null
}
onBeforeUnmount(() => clearTimeout(armTimer))

// ── Admin: create
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const form = ref({ title: '', description: '', options: ['', ''], end_date: '' })
const today = new Date().toISOString().slice(0, 10)

function openCreate() {
  form.value = { title: '', description: '', options: ['', ''], end_date: '' }
  formError.value = ''
  showCreate.value = true
}
const cleanOptions = computed(() => form.value.options.map(o => o.trim()).filter(Boolean))
const canCreate = computed(() => form.value.title.trim().length > 0 && cleanOptions.value.length >= 2)
function addOption() { form.value.options.push('') }
function removeOption(i) { if (form.value.options.length > 2) form.value.options.splice(i, 1) }

async function createPoll() {
  if (!canCreate.value || saving.value) return
  saving.value = true
  formError.value = ''
  try {
    const payload = { ...form.value, title: form.value.title.trim(), options: cleanOptions.value }
    const res = await pollsAPI.create(payload)
    polls.value.unshift(res.data)
    showCreate.value = false
    filter.value = 'ALL'
    toast('Poll is live — residents can vote now', 'success')
    form.value = { title: '', description: '', options: ['', ''], end_date: '' }
  } catch (e) {
    formError.value = e.response?.data?.error || 'Could not create the poll — check the fields and try again'
  }
  saving.value = false
}
</script>

<style scoped>
.polls-page {
  max-width: 760px;
  margin-inline: auto;
}

/* ── Header ─────────────────────────────────────────────────── */
.page-sub {
  margin: 4px 0 0;
  color: var(--se-text-muted);
  font-size: var(--se-fs-sm);
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-sub i { color: var(--se-teal-600); }
.page-sub strong { color: var(--se-navy-700); font-weight: 700; }

/* ── Filter chips ───────────────────────────────────────────── */
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: var(--se-sp-4);
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
  text-align: center;
}
.fchip.is-on .fchip-n { background: var(--se-navy-100); }

/* ── Poll cards ─────────────────────────────────────────────── */
.plist {
  display: flex;
  flex-direction: column;
  gap: var(--se-sp-4);
}
.poll-card {
  padding: var(--se-sp-5);
  animation: se-rise var(--se-t-slow) var(--se-ease-out) both;
  animation-delay: calc(var(--i, 0) * 45ms);
}
.poll-card:hover {
  box-shadow: var(--se-shadow-2);
  transform: translateY(-2px);
}
.poll-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: var(--se-sp-3);
}
.poll-tools { margin-left: auto; display: flex; gap: 8px; }
.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 6px 12px;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-pill);
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
.tool-btn:hover { border-color: var(--se-navy-600); color: var(--se-navy-700); background: var(--se-navy-50); }
.tool-btn:disabled { opacity: .55; cursor: default; }
.tool-btn--danger:hover { border-color: var(--se-danger-600); color: var(--se-danger-ink); background: var(--se-danger-50); }
.tool-btn--danger.is-armed {
  border-color: var(--se-danger-600);
  color: var(--se-danger-ink);
  background: var(--se-danger-50);
}

.poll-title {
  margin: 0 0 2px;
  font-size: var(--se-fs-lg);
  font-weight: 700;
  line-height: 1.3;
  overflow-wrap: anywhere;
}
.poll-desc {
  margin: 0;
  color: var(--se-text-muted);
  font-size: var(--se-fs-sm);
  overflow-wrap: anywhere;
}

/* ── One-tap voting rows ────────────────────────────────────── */
.vote-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: var(--se-sp-4);
}
.vote-opt {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-height: 48px;
  padding: 12px 14px;
  text-align: left;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-md);
  background: var(--se-surface);
  color: var(--se-ink);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition: border-color var(--se-t-fast) var(--se-ease-std),
              background var(--se-t-fast) var(--se-ease-std),
              transform var(--se-t-fast) var(--se-ease-std),
              box-shadow var(--se-t-fast) var(--se-ease-std);
}
.vote-opt:hover:not(:disabled) {
  border-color: var(--se-navy-600);
  background: var(--se-navy-50);
  transform: translateY(-1px);
  box-shadow: var(--se-shadow-1);
}
.vote-opt:active:not(:disabled) { transform: scale(.99); }
.vote-opt:disabled { opacity: .6; cursor: wait; }
.vote-ring {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  border: 2px solid var(--se-border-strong);
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 11px;
  color: var(--se-navy-600);
  transition: border-color var(--se-t-fast);
}
.vote-opt:hover:not(:disabled) .vote-ring { border-color: var(--se-navy-600); }
.vote-text { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.vote-go {
  color: var(--se-text-faint);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity var(--se-t-fast) var(--se-ease-std),
              transform var(--se-t-fast) var(--se-ease-std);
}
.vote-opt:hover:not(:disabled) .vote-go { opacity: 1; transform: none; }
.vote-hint {
  margin: 2px 0 0;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--se-fs-2xs);
  color: var(--se-text-faint);
}
.vote-hint i { color: var(--se-marigold-500); }
.vote-hint--done i { color: var(--se-teal-600); }

/* ── Result bars ────────────────────────────────────────────── */
.result-list {
  display: flex;
  flex-direction: column;
  gap: var(--se-sp-3);
  margin-top: var(--se-sp-4);
}
.result-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}
.result-label {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
  font-size: var(--se-fs-sm);
  font-weight: 600;
  color: var(--se-text);
  overflow-wrap: anywhere;
}
.result-label i { color: var(--se-teal-600); }
.result.is-mine .result-label { color: var(--se-ink); font-weight: 700; }
.result-nums {
  flex-shrink: 0;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
  white-space: nowrap;
}
.result-win { padding: 2px 8px; font-size: var(--se-fs-2xs); }
.res-fill {
  background: var(--se-navy-500);
  animation: bar-grow .6s var(--se-ease-out) backwards;
  animation-delay: calc(var(--bi, 0) * 60ms);
}
.res-fill--lead { background: var(--se-teal-600); }
@keyframes bar-grow { from { width: 0; } }

/* ── Card meta ──────────────────────────────────────────────── */
.poll-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--se-sp-4);
  margin-top: var(--se-sp-4);
  padding-top: var(--se-sp-3);
  border-top: 1px solid var(--se-border);
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}
.poll-meta span { display: inline-flex; align-items: center; gap: 6px; }
.poll-meta i { color: var(--se-text-faint); }

/* ── Empty / error ──────────────────────────────────────────── */
.empty-title {
  margin: 0 0 4px;
  font-size: var(--se-fs-lg);
  color: var(--se-ink);
}

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
.sk-pill { width: 84px; height: 24px; border-radius: var(--se-r-pill); }
.sk-pill--end { margin-left: auto; }
.sk-line { height: 12px; width: 100%; }
.sk-line--w60 { width: 60%; }
.sk-line--w40 { width: 40%; }
.sk-line--w30 { width: 30%; }
.sk-opt { display: flex; flex-direction: column; gap: 8px; }
.sk-rail { height: 8px; border-radius: var(--se-r-pill); }
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
  width: min(520px, 100%);
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
.sheet-title {
  flex: 1;
  min-width: 0;
  margin: 0;
  font-size: var(--se-fs-lg);
  font-weight: 700;
}
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

/* ── Form extras ────────────────────────────────────────────── */
.req { color: var(--se-danger-600); }
.optional { color: var(--se-text-faint); font-weight: 400; }
.opt-row { display: flex; gap: 8px; margin-bottom: 8px; }
.opt-del {
  width: 42px;
  flex-shrink: 0;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-md);
  background: var(--se-surface);
  color: var(--se-text-muted);
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast), border-color var(--se-t-fast);
}
.opt-del:hover { border-color: var(--se-danger-600); color: var(--se-danger-ink); background: var(--se-danger-50); }
.opt-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
  min-height: 40px;
  padding: 8px 12px;
  border: 1px dashed var(--se-border-strong);
  border-radius: var(--se-r-md);
  background: none;
  color: var(--se-navy-600);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--se-t-fast), border-color var(--se-t-fast);
}
.opt-add:hover { border-color: var(--se-navy-600); background: var(--se-navy-50); }

/* ── Responsive ─────────────────────────────────────────────── */
@media (max-width: 767.98px) {
  .fchip { min-height: 44px; }
  .tool-btn { min-height: 44px; }
}
@media (max-width: 575.98px) {
  .new-btn { flex: 1 1 100%; min-height: 48px; justify-content: center; font-size: var(--se-fs-md); }
  .poll-card { padding: var(--se-sp-4); }
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
</style>

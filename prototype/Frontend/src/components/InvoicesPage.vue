<template>
  <div class="invoices-page">

    <!-- ══ Loading — skeletons mirror the final layout (no shift) ══ -->
    <div v-if="loading" class="sk-wrap" aria-busy="true">
      <div class="card sk-hero">
        <div class="sk sk-icon"></div>
        <div class="sk-lines">
          <div class="sk sk-line sk-line--sm"></div>
          <div class="sk sk-line sk-line--lg"></div>
          <div class="sk sk-line sk-line--md"></div>
        </div>
        <div class="sk sk-pill"></div>
      </div>
      <div v-for="n in 3" :key="n" class="card sk-row">
        <div class="sk-lines">
          <div class="sk sk-line sk-line--md"></div>
          <div class="sk sk-line sk-line--sm"></div>
        </div>
        <div class="sk sk-amount"></div>
        <div class="sk sk-pill"></div>
      </div>
    </div>

    <!-- ══ Load error — never a dead end ══ -->
    <div v-else-if="loadError" class="card empty-state">
      <i class="fas fa-plug-circle-xmark"></i>
      <p>We couldn't reach the society office. Check your connection and try again.</p>
      <button class="btn-primary-custom mt-3" @click="load"><i class="fas fa-rotate-right"></i>Retry</button>
    </div>

    <!-- ══ RESIDENT — dues hero + pay flow ══ -->
    <template v-else-if="!isAdmin">

      <div v-if="invoices.length === 0" class="card empty-state">
        <i class="fas fa-file-invoice"></i>
        <p>No invoices yet — your society hasn't raised any dues for {{ flat }}.<br />Check back after the 1st of the month.</p>
      </div>

      <template v-else>
        <!-- Dues hero: pending -->
        <section v-if="pending.length" class="card dues-hero dues-hero--due mb-4">
          <div class="dues-icon"><i class="fas fa-file-invoice"></i></div>
          <div class="dues-figures">
            <span class="dues-label">Total pending · {{ flat }}</span>
            <span class="dues-amount se-num">₹{{ fmt(pendingTotal) }}</span>
            <span class="dues-sub">
              {{ pending.length }} invoice{{ pending.length === 1 ? '' : 's' }}
              <template v-if="overdueCount"> · <strong>{{ overdueCount }} overdue — clear soon to keep your streak</strong></template>
              <template v-else-if="nextDue"> · next due {{ fmtDate(nextDue) }}</template>
            </span>
          </div>
          <button class="btn-accent dues-cta" @click="openPay(pending)">
            Pay{{ pending.length > 1 ? ' all' : '' }} ₹{{ fmt(pendingTotal) }}<i class="fas fa-arrow-right"></i>
          </button>
        </section>

        <!-- Dues hero: all clear -->
        <section v-else class="card dues-hero dues-hero--clear mb-4">
          <div class="dues-icon"><i class="fas fa-circle-check"></i></div>
          <div class="dues-figures">
            <span class="dues-label">Maintenance · {{ flat }}</span>
            <span class="dues-amount">All dues clear</span>
            <span class="dues-sub">Nothing pending — thanks for paying on time.</span>
          </div>
          <span class="se-chip se-chip--teal dues-streak"><i class="fas fa-bolt"></i>{{ engagement.paymentStreak }}-month streak</span>
        </section>

        <!-- To pay -->
        <template v-if="pending.length">
          <h2 class="list-heading">To pay <span class="se-chip se-chip--marigold se-num">{{ pending.length }}</span></h2>
          <div class="inv-list">
            <article
              v-for="inv in pending" :key="inv.id"
              class="card inv-card" :class="{ 'inv-card--overdue': isOverdue(inv) }"
            >
              <div class="inv-period">
                <span class="inv-month">{{ period(inv) }}</span>
                <span class="inv-meta">
                  <span class="badge-custom" :class="badgeClass(inv)">{{ statusLabel(inv) }}</span>
                  <span v-if="inv.due_date" class="inv-note">due {{ fmtDate(inv.due_date) }}</span>
                </span>
              </div>
              <div class="inv-amount se-num">₹{{ fmt(inv.amount) }}</div>
              <button class="btn-accent inv-pay" @click="openPay(inv)">Pay ₹{{ fmt(inv.amount) }}</button>
            </article>
          </div>
        </template>

        <!-- Earlier · Paid (collapsed) -->
        <section v-if="paid.length">
          <button class="paid-toggle" @click="showPaid = !showPaid" :aria-expanded="showPaid ? 'true' : 'false'">
            <i class="fas fa-chevron-right paid-chev" :class="{ 'paid-chev--open': showPaid }"></i>
            <span>Earlier · Paid</span>
            <span class="se-chip se-chip--teal se-num">{{ paid.length }}</span>
          </button>
          <div v-show="showPaid" class="inv-list">
            <article v-for="inv in paid" :key="inv.id" class="card inv-card inv-card--paid">
              <div class="inv-period">
                <span class="inv-month">{{ period(inv) }}</span>
                <span class="inv-meta">
                  <span class="badge-custom badge-paid">Paid</span>
                  <span v-if="inv.payment_date" class="inv-note">{{ fmtDate(inv.payment_date) }}</span>
                  <span v-if="inv.payment_method" class="inv-note">· {{ modeLabel(inv.payment_method) }}</span>
                </span>
              </div>
              <div class="inv-amount inv-amount--paid se-num">₹{{ fmt(inv.amount) }}</div>
              <button class="btn-ghost" @click="viewReceipt(inv)" :disabled="receiptLoading === inv.id">
                <i class="fas" :class="receiptLoading === inv.id ? 'fa-spinner fa-spin' : 'fa-receipt'"></i>Receipt
              </button>
            </article>
          </div>
        </section>
      </template>
    </template>

    <!-- ══ ADMIN — collections at a glance + generate ══ -->
    <template v-else>
      <div class="se-page-actions">
        <div>
          <h1 class="se-section-title">Dues &amp; invoices</h1>
          <p class="page-sub">Raise maintenance invoices and track collections across the society.</p>
        </div>
        <div class="admin-actions">
          <button class="btn-ghost" @click="showAdd = true"><i class="fas fa-plus"></i>Single invoice</button>
          <button class="btn-accent" @click="showBulk = true"><i class="fas fa-bolt"></i>Bulk generate</button>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-12 col-md-4">
          <div class="stat-card">
            <div class="stat-icon tint-marigold"><i class="fas fa-hourglass-half"></i></div>
            <div><div class="stat-value se-num">₹{{ fmt(pendingTotal) }}</div><div class="stat-label">Outstanding</div></div>
          </div>
        </div>
        <div class="col-6 col-md-4">
          <div class="stat-card">
            <div class="stat-icon tint-danger"><i class="fas fa-triangle-exclamation"></i></div>
            <div><div class="stat-value se-num">{{ overdueCount }}</div><div class="stat-label">Overdue</div></div>
          </div>
        </div>
        <div class="col-6 col-md-4">
          <div class="stat-card">
            <div class="stat-icon tint-teal"><i class="fas fa-circle-check"></i></div>
            <div><div class="stat-value se-num">{{ paid.length }}</div><div class="stat-label">Paid</div></div>
          </div>
        </div>
      </div>

      <div class="filter-row" role="group" aria-label="Filter invoices by status">
        <button
          v-for="f in FILTERS" :key="f.key"
          class="filter-chip" :class="{ 'filter-chip--active': filterStatus === f.key }"
          @click="filterStatus = f.key"
        >
          {{ f.label }}<span class="chip-n se-num">{{ filterCount(f.key) }}</span>
        </button>
      </div>

      <div v-if="adminList.length === 0" class="card empty-state">
        <i class="fas fa-file-invoice"></i>
        <p v-if="invoices.length === 0">No invoices yet — generate this month's dues for every flat in one tap.</p>
        <p v-else>Nothing matches this filter.</p>
        <button v-if="invoices.length === 0" class="btn-accent mt-3" @click="showBulk = true">
          <i class="fas fa-bolt"></i>Bulk generate
        </button>
      </div>

      <div v-else class="inv-list">
        <article
          v-for="inv in adminList" :key="inv.id"
          class="card inv-card" :class="{ 'inv-card--overdue': isOverdue(inv), 'inv-card--paid': inv.status === 'PAID' }"
        >
          <span class="flat-tag se-num">{{ inv.flat_number }}</span>
          <div class="inv-period">
            <span class="inv-month">{{ period(inv) }}</span>
            <span class="inv-meta">
              <span class="badge-custom" :class="badgeClass(inv)">{{ statusLabel(inv) }}</span>
              <span v-if="inv.status === 'PAID' && inv.payment_date" class="inv-note">{{ fmtDate(inv.payment_date) }}</span>
              <span v-else-if="inv.due_date" class="inv-note">due {{ fmtDate(inv.due_date) }}</span>
            </span>
          </div>
          <div class="inv-amount se-num" :class="{ 'inv-amount--paid': inv.status === 'PAID' }">₹{{ fmt(inv.amount) }}</div>
          <button v-if="inv.status === 'PAID'" class="btn-ghost" @click="viewReceipt(inv)" :disabled="receiptLoading === inv.id">
            <i class="fas" :class="receiptLoading === inv.id ? 'fa-spinner fa-spin' : 'fa-receipt'"></i>Receipt
          </button>
          <button v-else class="btn-primary-custom inv-pay" @click="openPay(inv)">
            <i class="fas fa-indian-rupee-sign"></i>Record payment
          </button>
        </article>
      </div>
    </template>

    <!-- ══ Payment sheet (bottom sheet on mobile) ══ -->
    <transition name="sheet">
      <div v-if="paySheet" class="se-overlay" @click.self="closePay">
        <div class="se-sheet" role="dialog" aria-modal="true" :aria-label="isAdmin ? 'Record payment' : 'Confirm payment'">
          <div class="sheet-grab" aria-hidden="true"></div>
          <header class="sheet-head">
            <h6>{{ isAdmin ? 'Record payment' : 'Confirm payment' }}</h6>
            <button class="sheet-close" :disabled="paying" aria-label="Close" @click="closePay"><i class="fas fa-times"></i></button>
          </header>
          <div class="sheet-body">
            <ul class="pay-lines">
              <li v-for="it in paySheet.items" :key="it.id">
                <span>{{ period(it) }} <small v-if="isAdmin">· {{ it.flat_number }}</small></span>
                <span class="se-num">₹{{ fmt(it.amount) }}</span>
              </li>
            </ul>
            <div class="pay-total"><span>Total</span><span class="se-num">₹{{ fmt(paySheet.total) }}</span></div>

            <div class="form-label" id="pay-mode-label">Payment mode</div>
            <div class="mode-seg" role="radiogroup" aria-labelledby="pay-mode-label">
              <button
                type="button" class="mode-btn" :class="{ 'mode-btn--active': payMode === 'UPI' }"
                role="radio" :aria-checked="payMode === 'UPI' ? 'true' : 'false'" @click="payMode = 'UPI'"
              ><i class="fas fa-mobile-screen-button"></i>UPI</button>
              <button
                type="button" class="mode-btn" :class="{ 'mode-btn--active': payMode === 'CASH' }"
                role="radio" :aria-checked="payMode === 'CASH' ? 'true' : 'false'" @click="payMode = 'CASH'"
              ><i class="fas fa-money-bill-wave"></i>Cash</button>
            </div>
            <p class="mode-hint">
              {{ payMode === 'UPI'
                ? 'Instant confirmation — your receipt lands right away.'
                : 'Hand the cash to the society office; we log it against your flat now.' }}
            </p>
          </div>
          <footer class="sheet-foot">
            <button class="btn-accent sheet-cta" :disabled="paying" @click="confirmPay">
              <i v-if="paying" class="fas fa-spinner fa-spin"></i>
              {{ paying ? 'Processing…' : (isAdmin ? `Record ₹${fmt(paySheet.total)} as paid` : `Pay ₹${fmt(paySheet.total)}`) }}
            </button>
          </footer>
        </div>
      </div>
    </transition>

    <!-- ══ Receipt ══ -->
    <transition name="sheet">
      <div v-if="receipt" class="se-overlay" @click.self="receipt = null">
        <div class="se-sheet" role="dialog" aria-modal="true" aria-label="Payment receipt">
          <div class="sheet-grab" aria-hidden="true"></div>
          <header class="sheet-head">
            <h6>Payment receipt</h6>
            <button class="sheet-close" aria-label="Close" @click="receipt = null"><i class="fas fa-times"></i></button>
          </header>
          <div class="sheet-body receipt-body">
            <div class="receipt-check"><i class="fas fa-check"></i></div>
            <p class="receipt-title">Payment confirmed</p>
            <p class="receipt-amount se-num">₹{{ fmt(receipt.amount) }}</p>
            <dl class="receipt-rows">
              <div><dt>Receipt no.</dt><dd class="se-num">{{ receipt.receipt_number }}</dd></div>
              <div><dt>Flat</dt><dd>{{ receipt.flat_number }}</dd></div>
              <div><dt>Period</dt><dd>{{ receipt.periodLabel }}</dd></div>
              <div><dt>Mode</dt><dd>{{ modeLabel(receipt.payment_method) }}</dd></div>
              <div><dt>Date</dt><dd>{{ fmtDate(receipt.payment_date) }}</dd></div>
            </dl>
            <p class="receipt-org">SocietyEase · Apartment Association</p>
          </div>
          <footer class="sheet-foot">
            <button class="btn-primary-custom sheet-cta" @click="receipt = null">Done</button>
          </footer>
        </div>
      </div>
    </transition>

    <!-- ══ Bulk generate (admin) ══ -->
    <transition name="sheet">
      <div v-if="showBulk" class="se-overlay" @click.self="showBulk = false">
        <div class="se-sheet" role="dialog" aria-modal="true" aria-label="Bulk generate invoices">
          <div class="sheet-grab" aria-hidden="true"></div>
          <header class="sheet-head">
            <h6><i class="fas fa-bolt me-2"></i>Bulk generate</h6>
            <button class="sheet-close" aria-label="Close" @click="showBulk = false"><i class="fas fa-times"></i></button>
          </header>
          <div class="sheet-body">
            <div v-if="bulkMsg" class="alert-custom alert-error mb-3">{{ bulkMsg }}</div>
            <p class="sheet-note">One maintenance invoice for <strong>every flat</strong> in the selected month.</p>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label" for="bulk-month">Month</label>
                <select id="bulk-month" v-model="bulkForm.month" class="form-control-custom">
                  <option v-for="m in 12" :key="m" :value="m">{{ monthName(m) }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="bulk-year">Year</label>
                <input id="bulk-year" v-model="bulkForm.year" type="number" class="form-control-custom" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="bulk-amount">Amount per flat (₹)</label>
              <input id="bulk-amount" v-model="bulkForm.amount" type="number" min="0" class="form-control-custom" placeholder="1500" />
            </div>
            <div class="form-group mb-0">
              <label class="form-label" for="bulk-due">Due date</label>
              <input id="bulk-due" v-model="bulkForm.due_date" type="date" class="form-control-custom" />
            </div>
          </div>
          <footer class="sheet-foot">
            <button class="btn-ghost" @click="showBulk = false">Cancel</button>
            <button class="btn-accent sheet-grow" :disabled="saving || !bulkForm.amount" @click="doBulk">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Generating…' : 'Generate for all flats' }}
            </button>
          </footer>
        </div>
      </div>
    </transition>

    <!-- ══ Single invoice (admin) ══ -->
    <transition name="sheet">
      <div v-if="showAdd" class="se-overlay" @click.self="showAdd = false">
        <div class="se-sheet" role="dialog" aria-modal="true" aria-label="Generate single invoice">
          <div class="sheet-grab" aria-hidden="true"></div>
          <header class="sheet-head">
            <h6>Single invoice</h6>
            <button class="sheet-close" aria-label="Close" @click="showAdd = false"><i class="fas fa-times"></i></button>
          </header>
          <div class="sheet-body">
            <div v-if="addMsg" class="alert-custom alert-error mb-3">{{ addMsg }}</div>
            <div class="form-group">
              <label class="form-label" for="add-flat">Flat</label>
              <select id="add-flat" v-model="addForm.apartment_id" class="form-control-custom">
                <option value="">Select flat</option>
                <option v-for="a in apartments" :key="a.id" :value="a.id">{{ a.flat_number }}</option>
              </select>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label" for="add-month">Month</label>
                <select id="add-month" v-model="addForm.month" class="form-control-custom">
                  <option v-for="m in 12" :key="m" :value="m">{{ monthName(m) }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="add-year">Year</label>
                <input id="add-year" v-model="addForm.year" type="number" class="form-control-custom" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="add-amount">Amount (₹)</label>
              <input id="add-amount" v-model="addForm.amount" type="number" min="0" class="form-control-custom" placeholder="1500" />
            </div>
            <div class="form-group mb-0">
              <label class="form-label" for="add-due">Due date</label>
              <input id="add-due" v-model="addForm.due_date" type="date" class="form-control-custom" />
            </div>
          </div>
          <footer class="sheet-foot">
            <button class="btn-ghost" @click="showAdd = false">Cancel</button>
            <button class="btn-primary-custom sheet-grow" :disabled="saving || !addForm.apartment_id || !addForm.amount" @click="doAdd">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Creating…' : 'Create invoice' }}
            </button>
          </footer>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { invoicesAPI, membersAPI } from '../api/index'
import { authStore } from '../store/auth'
import { me } from '../store/demo'
import { engagement } from '../store/engagement'
import { useCelebrate } from '../composables/useCelebrate'

const { celebrate, reward, toast } = useCelebrate()

// ── state ─────────────────────────────────────────────────────
const invoices = ref([])
const apartments = ref([])
const loading = ref(true)
const loadError = ref(false)
const saving = ref(false)
const showBulk = ref(false)
const showAdd = ref(false)
const showPaid = ref(false)
const bulkMsg = ref(null)
const addMsg = ref(null)
const filterStatus = ref('ALL')
const paySheet = ref(null)          // { items: [...invoices], total }
const payMode = ref('UPI')
const paying = ref(false)
const receipt = ref(null)           // normalized: { receipt_number, flat_number, periodLabel, amount, payment_method, payment_date }
const receiptLoading = ref(null)
const localReceipts = new Map()     // invoice id → receipt synthesized this session

const isAdmin = computed(() => authStore.isAdmin)
const flat = computed(() => me().flat)

const now = new Date()
const bulkForm = ref({ month: now.getMonth() + 1, year: now.getFullYear(), amount: 1500, due_date: '' })
const addForm = ref({ apartment_id: '', month: now.getMonth() + 1, year: now.getFullYear(), amount: 1500, due_date: '' })

// ── formatting ────────────────────────────────────────────────
const fmt = (n) => Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })
const monthName = (m, style = 'long') => new Date(2000, (Number(m) || 1) - 1, 1).toLocaleString('en', { month: style })
const period = (inv) => `${monthName(inv.month)} ${inv.year}`
const fmtDate = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
const modeLabel = (m) => m === 'CASH' ? 'Cash' : (m || 'UPI')

// ── status helpers ────────────────────────────────────────────
const startOfToday = () => { const t = new Date(); t.setHours(0, 0, 0, 0); return t }
const isOverdue = (inv) =>
  inv.status !== 'PAID' && (inv.status === 'OVERDUE' || (inv.due_date && new Date(inv.due_date) < startOfToday()))
const displayStatus = (inv) => inv.status === 'PAID' ? 'paid' : (isOverdue(inv) ? 'overdue' : 'unpaid')
// Paid = teal, Due = navy (informational), Overdue = danger — global badge system.
const badgeClass = (inv) => ({ paid: 'badge-paid', overdue: 'badge-overdue', unpaid: 'badge-open' }[displayStatus(inv)])
const statusLabel = (inv) => ({ paid: 'Paid', overdue: 'Overdue', unpaid: 'Due' }[displayStatus(inv)])

// ── derived lists ─────────────────────────────────────────────
const periodKey = (inv) => (Number(inv.year) || 0) * 100 + (Number(inv.month) || 0)
const pending = computed(() =>
  invoices.value.filter(i => i.status !== 'PAID').sort((a, b) => periodKey(a) - periodKey(b))
)
const paid = computed(() =>
  invoices.value.filter(i => i.status === 'PAID').sort((a, b) => periodKey(b) - periodKey(a))
)
const pendingTotal = computed(() => pending.value.reduce((s, i) => s + Number(i.amount || 0), 0))
const overdueCount = computed(() => pending.value.filter(isOverdue).length)
const nextDue = computed(() => {
  const dated = pending.value.filter(i => i.due_date)
  if (!dated.length) return null
  return dated.reduce((min, i) => new Date(i.due_date) < new Date(min.due_date) ? i : min).due_date
})

// ── admin filter ──────────────────────────────────────────────
const FILTERS = [
  { key: 'ALL', label: 'All' },
  { key: 'UNPAID', label: 'Due' },
  { key: 'OVERDUE', label: 'Overdue' },
  { key: 'PAID', label: 'Paid' },
]
const filterCount = (key) =>
  key === 'ALL' ? invoices.value.length : invoices.value.filter(i => displayStatus(i) === key.toLowerCase()).length
const adminList = computed(() => {
  const list = filterStatus.value === 'ALL'
    ? [...invoices.value]
    : invoices.value.filter(i => displayStatus(i) === filterStatus.value.toLowerCase())
  return list.sort((a, b) => (periodKey(b) - periodKey(a)) || String(a.flat_number).localeCompare(String(b.flat_number)))
})

// ── load ──────────────────────────────────────────────────────
async function load() {
  loading.value = true
  loadError.value = false
  try {
    const jobs = [invoicesAPI.getAll()]
    if (isAdmin.value) jobs.push(membersAPI.getApartments())
    const [inv, apt] = await Promise.all(jobs)
    invoices.value = inv.data || []
    if (apt) apartments.value = apt.data || []
  } catch (e) {
    loadError.value = true
  }
  loading.value = false
}
onMounted(load)

// ── payment flow ──────────────────────────────────────────────
// PUT /invoices/:id/pay persists the payment on the backend. The invoice is
// marked PAID locally only after the call succeeds; on failure it stays unpaid
// and the server error is surfaced. Receipts prefer the server's response.
function openPay(target) {
  const items = Array.isArray(target) ? target : [target]
  if (!items.length) return
  paySheet.value = { items, total: items.reduce((s, i) => s + Number(i.amount || 0), 0) }
  payMode.value = 'UPI'
}
function closePay() {
  if (!paying.value) paySheet.value = null
}

function makeReceipt(items, total) {
  const first = items[0], last = items[items.length - 1]
  return {
    receipt_number: 'SE-' + Date.now().toString(36).toUpperCase(),
    flat_number: first.flat_number || flat.value,
    periodLabel: items.length === 1
      ? period(first)
      : `${monthName(first.month, 'short')} ${first.year} – ${monthName(last.month, 'short')} ${last.year} · ${items.length} invoices`,
    amount: total,
    payment_method: payMode.value,
    payment_date: new Date().toISOString(),
  }
}

function normalizeReceipt(raw, inv) {
  const fallback = makeReceipt([inv], Number(inv.amount || 0))
  if (!raw) return fallback
  return {
    receipt_number: raw.receipt_number || fallback.receipt_number,
    flat_number: raw.flat_number || fallback.flat_number,
    periodLabel: fallback.periodLabel,
    amount: raw.amount ?? fallback.amount,
    payment_method: raw.payment_method || fallback.payment_method,
    payment_date: raw.payment_date || fallback.payment_date,
  }
}

async function confirmPay() {
  if (!paySheet.value || paying.value) return
  paying.value = true

  const { items } = paySheet.value
  const paidItems = []
  const receiptsById = new Map()
  let lastError = null

  // Persist each invoice to the backend; mark PAID locally only on success.
  for (const it of items) {
    try {
      const res = await invoicesAPI.markPaid(it.id, { payment_method: payMode.value })
      const rec = normalizeReceipt(res.data?.receipt, it)
      receiptsById.set(it.id, rec)
      localReceipts.set(it.id, rec)
      const idx = invoices.value.findIndex(i => i.id === it.id)
      if (idx > -1) invoices.value[idx] = {
        ...invoices.value[idx],
        status: 'PAID',
        payment_method: rec.payment_method,
        payment_date: rec.payment_date,
      }
      paidItems.push(it)
    } catch (e) {
      lastError = e
    }
  }

  paying.value = false

  // Nothing went through — leave every invoice unpaid and surface the error.
  if (!paidItems.length) {
    toast(lastError?.response?.data?.error || 'Payment could not be completed', 'error')
    return
  }

  paySheet.value = null

  // Receipt card: real server receipt for a single invoice, combined summary for a batch.
  const paidTotal = paidItems.reduce((s, i) => s + Number(i.amount || 0), 0)
  receipt.value = paidItems.length === 1
    ? receiptsById.get(paidItems[0].id)
    : makeReceipt(paidItems, paidTotal)

  // Partial batch failure — some invoices still owe.
  if (lastError) toast(lastError.response?.data?.error || 'Some invoices could not be paid', 'error')

  if (!isAdmin.value) {
    if (pending.value.length === 0) {           // last due cleared → extend the streak
      engagement.paymentStreak += 1
      engagement.save()
    }
    celebrate({ title: 'Dues cleared!', subtitle: `₹${fmt(paidTotal)} paid · receipt on its way`, icon: 'fa-receipt', points: 50 })
    reward(50, 'Cleared your maintenance dues')
  } else {
    toast('Payment recorded · receipt generated', 'success')
  }
}

// ── receipts for already-paid invoices ────────────────────────
async function viewReceipt(inv) {
  if (localReceipts.has(inv.id)) { receipt.value = localReceipts.get(inv.id); return }
  receiptLoading.value = inv.id
  const fallback = {
    receipt_number: 'SE-' + String(inv.id).padStart(6, '0'),
    flat_number: inv.flat_number || flat.value,
    periodLabel: period(inv),
    amount: inv.amount,
    payment_method: inv.payment_method || 'UPI',
    payment_date: inv.payment_date || null,
  }
  try {
    const res = await invoicesAPI.getReceipt(inv.id)
    const r = res.data || {}
    receipt.value = {
      receipt_number: r.receipt_number || fallback.receipt_number,
      flat_number: r.flat_number || fallback.flat_number,
      periodLabel: fallback.periodLabel,
      amount: r.amount ?? fallback.amount,
      payment_method: r.payment_method || fallback.payment_method,
      payment_date: r.payment_date || fallback.payment_date,
    }
  } catch (e) {
    receipt.value = fallback
  }
  receiptLoading.value = null
}

// ── admin: generate invoices ──────────────────────────────────
async function doBulk() {
  saving.value = true
  bulkMsg.value = null
  try {
    const res = await invoicesAPI.bulkGenerate(bulkForm.value)
    showBulk.value = false
    toast(res.data?.message || 'Invoices generated for all flats', 'success')
    const fresh = await invoicesAPI.getAll()
    invoices.value = fresh.data || []
  } catch (e) {
    bulkMsg.value = e.response?.data?.error || 'Could not generate invoices. Try again.'
  }
  saving.value = false
}

async function doAdd() {
  saving.value = true
  addMsg.value = null
  try {
    const res = await invoicesAPI.create(addForm.value)
    invoices.value.unshift(res.data)
    showAdd.value = false
    toast('Invoice created', 'success')
  } catch (e) {
    addMsg.value = e.response?.data?.error || 'Could not create the invoice.'
  }
  saving.value = false
}

// ── overlay ergonomics: Esc closes, body scroll locks ─────────
function onKeydown(e) {
  if (e.key !== 'Escape') return
  if (receipt.value) receipt.value = null
  else if (paySheet.value) closePay()
  else if (showBulk.value) showBulk.value = false
  else if (showAdd.value) showAdd.value = false
}
const overlayOpen = computed(() => !!(paySheet.value || receipt.value || showBulk.value || showAdd.value))
watch(overlayOpen, v => { document.body.style.overflow = v ? 'hidden' : '' })
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ══ Dues hero ═══════════════════════════════════════════════ */
.dues-hero {
  display: flex;
  align-items: center;
  gap: var(--se-sp-5);
  flex-wrap: wrap;
  padding: var(--se-sp-6);
  border-left: 4px solid transparent;
  animation: se-rise var(--se-t-slow) var(--se-ease-out);
}
.dues-hero--due {
  background:
    radial-gradient(420px 240px at 100% 0, var(--se-marigold-100), transparent 70%),
    var(--se-marigold-50);
  border-color: var(--se-marigold-100);
  border-left-color: var(--se-marigold-400);
}
.dues-hero--clear {
  background:
    radial-gradient(420px 240px at 100% 0, var(--se-teal-100), transparent 70%),
    var(--se-teal-50);
  border-color: var(--se-teal-100);
  border-left-color: var(--se-teal-600);
}
.dues-icon {
  width: 46px; height: 46px;
  border-radius: var(--se-r-md);
  display: grid; place-items: center;
  font-size: 18px;
  flex-shrink: 0;
}
.dues-hero--due .dues-icon { background: var(--se-marigold-400); color: var(--se-navy-800); }
.dues-hero--clear .dues-icon { background: var(--se-teal-600); color: #fff; }
.dues-figures { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 2px; }
.dues-label {
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--se-text-muted);
}
.dues-amount {
  font-family: var(--se-font-display);
  font-size: var(--se-fs-3xl);
  font-weight: 800;
  line-height: 1.1;
  color: var(--se-ink);
}
.dues-sub { font-size: var(--se-fs-sm); color: var(--se-text-muted); }
.dues-sub strong { font-weight: 600; color: var(--se-marigold-600); }
[data-theme="dark"] .dues-sub strong { color: var(--se-marigold-400); }
.dues-cta {
  min-height: 48px;
  padding: 12px 22px;
  font-size: var(--se-fs-md);
}
.dues-streak { align-self: center; }

/* ══ Section headings & lists ════════════════════════════════ */
.list-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: var(--se-sp-6) 0 var(--se-sp-3);
  font-size: var(--se-fs-lg);
  font-weight: 700;
}
.inv-list { display: flex; flex-direction: column; gap: var(--se-sp-3); }

.paid-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: 48px;
  margin: var(--se-sp-6) 0 var(--se-sp-3);
  padding: 6px 8px;
  background: none;
  border: 0;
  border-radius: var(--se-r-md);
  cursor: pointer;
  text-align: left;
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-lg);
  color: var(--se-ink);
  transition: background var(--se-t-fast);
}
.paid-toggle:hover { background: var(--se-sunken); }
.paid-chev {
  font-size: 12px;
  color: var(--se-text-muted);
  transition: transform var(--se-t-med) var(--se-ease-out);
}
.paid-chev--open { transform: rotate(90deg); }

/* ══ Invoice cards ═══════════════════════════════════════════ */
.inv-card {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--se-sp-4);
  padding: var(--se-sp-4) var(--se-sp-5);
  transition: box-shadow var(--se-t-med) var(--se-ease-std), transform var(--se-t-med) var(--se-ease-out);
}
.inv-card:hover { box-shadow: var(--se-shadow-2); transform: translateY(-1px); }
.inv-card--overdue { box-shadow: inset 3px 0 0 var(--se-danger-600), var(--se-shadow-1); }
.inv-card--overdue:hover { box-shadow: inset 3px 0 0 var(--se-danger-600), var(--se-shadow-2); }
.inv-period { flex: 1; min-width: 150px; display: flex; flex-direction: column; gap: 4px; }
.inv-month {
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-md);
  color: var(--se-ink);
}
.inv-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.inv-note { font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.inv-amount {
  margin-left: auto;
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-xl);
  color: var(--se-ink);
  text-align: right;
}
.inv-amount--paid { color: var(--se-text-muted); font-weight: 600; }
.inv-card--paid .inv-month { font-weight: 600; }
.inv-pay { min-height: 44px; white-space: nowrap; }

.flat-tag {
  min-width: 58px;
  padding: 7px 10px;
  text-align: center;
  border-radius: var(--se-r-md);
  background: var(--se-navy-50);
  color: var(--se-navy-700);
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-xs);
  flex-shrink: 0;
}
[data-theme="dark"] .flat-tag { color: #A9C0EE; }

/* ghost / secondary button (44px touch target) */
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
.btn-ghost:hover { background: var(--se-sunken); border-color: var(--se-border-strong); }
.btn-ghost:disabled { opacity: .55; cursor: not-allowed; }

/* ══ Admin bits ══════════════════════════════════════════════ */
.page-sub { margin: 4px 0 0; font-size: var(--se-fs-sm); color: var(--se-text-muted); }
.admin-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.tint-marigold { background: var(--se-marigold-400); color: var(--se-navy-800); }
.tint-danger { background: var(--se-danger-600); }
.tint-teal { background: var(--se-teal-600); }

.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: var(--se-sp-4); }
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 8px 16px;
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
  max-width: 440px;
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
  width: 36px; height: 36px;
  display: grid; place-items: center;
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
.sheet-note { margin: 0 0 var(--se-sp-4); font-size: var(--se-fs-sm); color: var(--se-text-muted); }
.sheet-foot {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: var(--se-sp-4) var(--se-sp-5);
  border-top: 1px solid var(--se-border);
}
.sheet-cta { width: 100%; min-height: 48px; font-size: var(--se-fs-md); }
.sheet-grow { flex: 1; min-height: 44px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

/* payment sheet internals */
.pay-lines {
  list-style: none;
  margin: 0 0 var(--se-sp-3);
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 180px;
  overflow-y: auto;
}
.pay-lines li { display: flex; justify-content: space-between; gap: 12px; font-size: var(--se-fs-sm); }
.pay-lines li small { color: var(--se-text-muted); }
.pay-total {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: var(--se-sp-3);
  margin-bottom: var(--se-sp-5);
  border-top: 1px dashed var(--se-border-strong);
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-lg);
  color: var(--se-ink);
}
.mode-seg {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 4px;
  background: var(--se-sunken);
  border-radius: var(--se-r-md);
}
.mode-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  border: 0;
  border-radius: calc(var(--se-r-md) - 3px);
  background: transparent;
  color: var(--se-text-muted);
  font-family: var(--se-font-body);
  font-weight: 600;
  font-size: var(--se-fs-sm);
  cursor: pointer;
  transition: background var(--se-t-fast), color var(--se-t-fast), box-shadow var(--se-t-fast);
}
.mode-btn--active { background: var(--se-surface); color: var(--se-navy-700); box-shadow: var(--se-shadow-1); }
[data-theme="dark"] .mode-btn--active { color: var(--se-ink); }
.mode-hint {
  margin: 10px 0 0;
  min-height: 2.6em;
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}

/* receipt */
.receipt-body { text-align: center; }
.receipt-check {
  width: 64px; height: 64px;
  margin: 4px auto 12px;
  display: grid; place-items: center;
  border-radius: 50%;
  border: 1.5px solid var(--se-teal-100);
  background: var(--se-teal-50);
  color: var(--se-teal-700);
  font-size: 1.5rem;
  animation: receipt-pop var(--se-t-slow) var(--se-ease-out);
}
[data-theme="dark"] .receipt-check { color: #63E3E0; }
.receipt-title {
  margin: 0;
  font-family: var(--se-font-display);
  font-weight: 700;
  color: var(--se-teal-700);
}
[data-theme="dark"] .receipt-title { color: #63E3E0; }
.receipt-amount {
  margin: 2px 0 0;
  font-family: var(--se-font-display);
  font-size: var(--se-fs-3xl);
  font-weight: 800;
  color: var(--se-ink);
}
.receipt-rows {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: var(--se-sp-4) 0 0;
  padding-top: var(--se-sp-4);
  border-top: 1px dashed var(--se-border-strong);
  text-align: left;
}
.receipt-rows > div { display: flex; justify-content: space-between; gap: 12px; }
.receipt-rows dt { margin: 0; font-size: var(--se-fs-xs); font-weight: 500; color: var(--se-text-muted); }
.receipt-rows dd { margin: 0; font-size: var(--se-fs-sm); font-weight: 600; color: var(--se-ink); text-align: right; }
.receipt-org {
  margin: var(--se-sp-4) 0 0;
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: var(--se-text-faint);
}
@keyframes receipt-pop {
  from { transform: scale(.6); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

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
.sk-hero {
  display: flex;
  align-items: center;
  gap: var(--se-sp-5);
  min-height: 122px;
  margin-bottom: var(--se-sp-2);
  padding: var(--se-sp-6);
}
.sk-row {
  display: flex;
  align-items: center;
  gap: var(--se-sp-4);
  min-height: 84px;
  padding: var(--se-sp-4) var(--se-sp-5);
}
.sk-icon { width: 46px; height: 46px; border-radius: var(--se-r-md); flex-shrink: 0; }
.sk-lines { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.sk-line { height: 12px; }
.sk-line--lg { width: 55%; height: 24px; }
.sk-line--md { width: 38%; }
.sk-line--sm { width: 24%; }
.sk-amount { width: 72px; height: 22px; }
.sk-pill { width: 118px; height: 44px; border-radius: var(--se-r-md); flex-shrink: 0; }
@keyframes sk-shimmer { to { transform: translateX(100%); } }

/* ══ Small screens — thumbs first ════════════════════════════ */
@media (max-width: 575.98px) {
  .dues-hero { padding: var(--se-sp-5); }
  .dues-amount { font-size: var(--se-fs-2xl); }
  .dues-cta { width: 100%; }
  .dues-streak { align-self: flex-start; }

  .inv-pay { flex-basis: 100%; }
  .sk-pill { display: none; }

  .admin-actions { width: 100%; }
  .admin-actions > button { flex: 1; }

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
</style>

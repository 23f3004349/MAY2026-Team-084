<template>
  <div class="admin-wrapper">
    <AssociationNavBar />
    <div class="admin-container">
      <div class="invoices-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Invoices</h2>
            <p class="card-subtitle">Generate, mark paid, and manage receipts.</p>
          </div>
          <div class="header-actions">
            <div class="filter-row">
              <select v-model.number="filterMonth">
                <option value="">All months</option>
                <option v-for="m in 12" :key="m" :value="m">{{ m }}</option>
              </select>
              <select v-model.number="filterYear">
                <option value="">All years</option>
                <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
              </select>
              <button class="btn-filter" @click="applyFilter">Filter</button>
            </div>
            <button class="btn-add" @click="openGenerateSingle">Generate</button>
            <button class="btn-add-outline" @click="openBulkGenerate">Generate All</button>
            <button class="btn-filter" @click="showPending = !showPending">{{ showPending ? 'Show All' : 'Show Pending' }}</button>
          </div>
        </div>

        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading invoices…</div>
          <div v-else>
            <div v-if="invoicesToShow.length === 0" class="empty-state">No invoices found</div>
            <div v-else class="invoice-table-wrap">
              <table class="invoice-table">
                <thead>
                  <tr>
                    <th>Flat</th>
                    <th>Month</th>
                    <th>Year</th>
                    <th>Amount</th>
                    <th>Due</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="inv in invoicesToShow" :key="inv.id">
                    <td>{{ inv.flat_number }}</td>
                    <td>{{ inv.month }}</td>
                    <td>{{ inv.year }}</td>
                    <td>{{ inv.amount.toFixed(2) }}</td>
                    <td>{{ inv.due_date || 'N/A' }}</td>
                    <td>{{ inv.status }}</td>
                    <td class="td-actions">
                      <button class="btn-view" @click="viewDetail(inv)">View</button>
                      <button class="btn-pay" :disabled="inv.status==='PAID'" @click="openMarkPaid(inv)">Mark Paid</button>
                      <button class="btn-download" @click="downloadReceipt(inv)">Download</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div v-if="genSingle" class="modal-overlay" @click.self="closeGenerateSingle">
      <div class="modal">
        <h3>Generate Invoice</h3>
        <select v-model="genApartmentId">
          <option disabled value="">Select apartment</option>
          <option v-for="a in apartments" :key="a.id" :value="a.id">{{ a.flat_number }} · Block {{ a.block || 'N/A' }}</option>
        </select>
        <div class="grid-2">
          <input type="number" v-model.number="genMonth" placeholder="Month (1-12)" />
          <input type="number" v-model.number="genYear" placeholder="Year" />
        </div>
        <input type="number" v-model.number="genAmount" placeholder="Amount" />
        <input type="date" v-model="genDueDate" />
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeGenerateSingle">Cancel</button>
          <button class="btn-submit" @click="submitGenerateSingle">Generate</button>
        </div>
      </div>
    </div>

    <div v-if="genBulk" class="modal-overlay" @click.self="closeBulkGenerate">
      <div class="modal">
        <h3>Generate Invoices For All Apartments</h3>
        <div class="grid-2">
          <input type="number" v-model.number="bulkMonth" placeholder="Month (1-12)" />
          <input type="number" v-model.number="bulkYear" placeholder="Year" />
        </div>
        <input type="number" v-model.number="bulkAmount" placeholder="Amount" />
        <input type="date" v-model="bulkDueDate" />
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeBulkGenerate">Cancel</button>
          <button class="btn-submit" @click="submitBulkGenerate">Generate All</button>
        </div>
      </div>
    </div>

    <div v-if="paying" class="modal-overlay" @click.self="closeMarkPaid">
      <div class="modal">
        <h3>Mark Invoice As Paid</h3>
        <p>Invoice: <strong>{{ activeInvoice.flat_number }} — {{ activeInvoice.month }}/{{ activeInvoice.year }}</strong></p>
        <select v-model="paymentMethod">
          <option value="CASH">CASH</option>
          <option value="ONLINE">ONLINE</option>
          <option value="CHEQUE">CHEQUE</option>
        </select>
        <input v-model="transactionRef" placeholder="Transaction reference (optional)" />
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeMarkPaid">Cancel</button>
          <button class="btn-submit" @click="submitMarkPaid">Mark Paid</button>
        </div>
      </div>
    </div>

    <!-- Receipt Modal -->
    <div v-if="showReceipt" class="modal-overlay" @click.self="closeReceipt">
      <div class="modal">
        <h3>Receipt</h3>
        <pre class="receipt-block">{{ receiptData ? JSON.stringify(receiptData, null, 2) : 'No receipt available' }}</pre>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeReceipt">Close</button>
          <button class="btn-submit" @click="downloadReceiptData">Download</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AssociationNavBar from './AssociationNavBar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const router = useRouter()
const API_BASE = getApiBase()

const invoices = ref([])
const loading = ref(true)
const showPending = ref(false)

// generate single
const genSingle = ref(false)
const genApartmentId = ref('')
const genMonth = ref(new Date().getMonth()+1)
const genYear = ref(new Date().getFullYear())
const genAmount = ref(0)
const genDueDate = ref(null)

// bulk
const genBulk = ref(false)
const bulkMonth = ref(new Date().getMonth()+1)
const bulkYear = ref(new Date().getFullYear())
const bulkAmount = ref(0)
const bulkDueDate = ref(null)

// mark paid
const paying = ref(false)
const activeInvoice = ref({})
const paymentMethod = ref('CASH')
const transactionRef = ref('')

// receipt
const showReceipt = ref(false)
const receiptData = ref(null)

const apartments = ref([])
const filterMonth = ref('')
const filterYear = ref('')
const years = Array.from({length:8}, (_,i) => new Date().getFullYear() - 3 + i)

onMounted(async () => {
  await fetchInvoices()
  await loadApartments()
})

async function fetchInvoices() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/invoices/`, { headers: auth })
    invoices.value = resp.data || []
  } catch (err) {
    console.error('Failed to fetch invoices', err)
    invoices.value = []
  } finally {
    loading.value = false
  }
}

async function loadApartments() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) return
    const resp = await axios.get(`${API_BASE}/api/members/apartments`, { headers: auth })
    apartments.value = resp.data || []
  } catch (err) { apartments.value = [] }
}

const invoicesToShow = computed(() => {
  let list = showPending.value ? invoices.value.filter(i => i.status !== 'PAID') : invoices.value
  if (filterMonth.value) list = list.filter(i => Number(i.month) === Number(filterMonth.value))
  if (filterYear.value) list = list.filter(i => Number(i.year) === Number(filterYear.value))
  return list
})

function applyFilter() { /* triggers computed to update */ }

function viewDetail(inv) { router.push(`/invoices/${inv.id}/detail`) }

function openGenerateSingle() { genSingle.value = true }
function closeGenerateSingle() { genSingle.value = false }
async function submitGenerateSingle() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const payload = { apartment_id: genApartmentId.value, month: genMonth.value, year: genYear.value, amount: genAmount.value, due_date: genDueDate.value }
    await axios.post(`${API_BASE}/api/invoices/`, payload, { headers: auth })
    await fetchInvoices()
    genSingle.value = false
  } catch (err) { console.error(err); alert('Failed to generate invoice') }
}

function openBulkGenerate() { genBulk.value = true }
function closeBulkGenerate() { genBulk.value = false }
async function submitBulkGenerate() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const payload = { month: bulkMonth.value, year: bulkYear.value, amount: bulkAmount.value, due_date: bulkDueDate.value }
    const resp = await axios.post(`${API_BASE}/api/invoices/bulk`, payload, { headers: auth })
    alert(resp.data.message || 'Bulk generation complete')
    await fetchInvoices()
    genBulk.value = false
  } catch (err) { console.error(err); alert('Failed to bulk generate') }
}

function openMarkPaid(inv) { activeInvoice.value = inv; paying.value = true }
function closeMarkPaid() { paying.value = false }
async function submitMarkPaid() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const payload = { payment_method: paymentMethod.value, transaction_reference: transactionRef.value }
    const resp = await axios.put(`${API_BASE}/api/invoices/${activeInvoice.value.id}/pay`, payload, { headers: auth })
    alert(resp.data.message || 'Marked paid')
    await fetchInvoices()
    closeMarkPaid()
  } catch (err) { console.error(err); alert('Failed to mark paid') }
}

async function viewReceipt(inv) {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/invoices/${inv.id}/receipt`, { headers: auth })
    receiptData.value = resp.data
    showReceipt.value = true
  } catch (err) { console.error(err); alert('Receipt not available') }
}
function closeReceipt() { showReceipt.value = false; receiptData.value = null }

async function downloadReceipt(inv) {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/invoices/${inv.id}/receipt`, { headers: auth })
    const data = resp.data
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `receipt-${inv.id}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) { console.error(err); alert('Failed to download receipt') }
}

function downloadReceiptData() {
  if (!receiptData.value) return
  const blob = new Blob([JSON.stringify(receiptData.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `receipt.json`
  a.click()
  URL.revokeObjectURL(url)
}

</script>

<style scoped>
* { box-sizing: border-box; margin:0; padding:0 }
.admin-wrapper { min-height:100vh; background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%); }
.admin-container { max-width:1200px; margin:1.5rem auto; padding:1rem }

.invoices-card { background:white; border-radius:1.25rem; box-shadow:0 12px 40px rgba(0,0,0,0.06); overflow:hidden }
.invoices-card .card-header { padding:1.25rem 1.5rem; background: linear-gradient(145deg,#e5f2ff 0%, #d6e8ff 100%); border-bottom:1px solid rgba(34,49,63,0.04); display:flex; align-items:center; justify-content:space-between }
.card-title { font-weight:800; color:#0f2540 }
.card-subtitle { color:#556c86 }
.header-actions { display:flex; gap:0.6rem }
.btn-add { padding:0.6rem 0.95rem; border-radius:12px; background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; font-weight:800 }
.btn-add-outline { padding:0.6rem 0.95rem; border-radius:12px; background: transparent; border:1px solid rgba(43,126,247,0.12); color:#0f2540; font-weight:800 }
.btn-filter { padding:0.55rem 0.9rem; border-radius:12px; background:#fbfdff; border:1px solid rgba(129,167,210,0.12); font-weight:700 ; color:black}

.card-body { padding:1.25rem }
.invoice-table-wrap { overflow-x:auto }
.invoice-table { width:100%; border-collapse:collapse }
.invoice-table thead th { text-align:left; padding:0.9rem 1rem; background:#f5f9ff; color:#0f2540; font-weight:800; border-bottom:1px solid rgba(34,49,63,0.06) }
.invoice-table tbody td { padding:0.75rem 1rem; border-bottom:1px solid rgba(34,49,63,0.04) }
.td-actions { display:flex; gap:0.5rem }
.btn-view { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color: white; border: none; padding:0.4rem 0.6rem; border-radius:8px; font-weight:700;color:black }
.btn-pay { background: linear-gradient(90deg,#10b981,#059669); color:white; border:none; padding:0.4rem 0.6rem; border-radius:8px ; color:black}
.btn-download { background:#fff3bf; color:#92400e; border:1px solid rgba(146,64,14,0.08); padding:0.4rem 0.6rem; border-radius:8px; font-weight:700;color:black }

.modal-overlay { position:fixed; inset:0; background: rgba(3,6,23,0.5); display:flex; align-items:center; justify-content:center }
.modal { background:white; padding:1.25rem; border-radius:12px; width:420px; max-width:90vw }
.modal input, .modal select { width:100%; margin-top:0.5rem; padding:0.6rem; border-radius:8px; border:1px solid rgba(129,167,210,0.18); background:#f8fbff }
.grid-2 { display:flex; gap:0.5rem }
.grid-2 input { flex:1 }
.modal-actions { display:flex; justify-content:flex-end; gap:0.75rem; margin-top:0.75rem }
.btn-cancel { background:white; border:1px solid rgba(129,167,210,0.18); padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:700;color:black }
.btn-submit { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:800 }

.receipt-block { max-height:300px; overflow:auto; background:#fbfdff; padding:0.8rem; border-radius:8px; border:1px solid rgba(129,167,210,0.06) }

@media (max-width:768px) { .invoice-table thead { display:none } .invoice-table tbody td { display:block; width:100% } }
</style>
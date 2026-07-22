<template>
  <div class="admin-wrapper">
    <AssociationNavBar />
    <div class="admin-container">
      <div class="detail-card">
        <div class="card-header">
          <h2 class="card-title">Invoice Detail</h2>
          <div class="card-actions">
            <button class="btn-print" @click="printReceipt">Print</button>
            <button class="btn-download" @click="downloadReceiptData">Download</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading…</div>
          <div v-else>
            <div v-if="!invoice.id" class="empty-state">Invoice not found</div>
            <div v-else class="invoice-detail">
              <h3>Invoice for {{ invoice.flat_number }}</h3>
              <div class="meta-row">
                <div><strong>Month:</strong> {{ invoice.month }}</div>
                <div><strong>Year:</strong> {{ invoice.year }}</div>
                <div><strong>Amount:</strong> {{ invoice.amount.toFixed(2) }}</div>
              </div>
              <div class="meta-row">
                <div><strong>Due:</strong> {{ invoice.due_date || 'N/A' }}</div>
                <div><strong>Status:</strong> {{ invoice.status }}</div>
                <div><strong>Generated:</strong> {{ formatDate(invoice.created_at) }}</div>
              </div>

              <div class="receipt-section" ref="receiptArea">
                <h4>Receipt</h4>
                <div v-if="receipt">
                  <div><strong>Receipt #:</strong> {{ receipt.receipt_number }}</div>
                  <div><strong>Flat:</strong> {{ receipt.flat_number }}</div>
                  <div><strong>Amount:</strong> {{ receipt.amount.toFixed(2) }}</div>
                  <div><strong>Payment Method:</strong> {{ receipt.payment_method }}</div>
                  <div><strong>Transaction Ref:</strong> {{ receipt.transaction_reference || 'N/A' }}</div>
                  <div><strong>Paid At:</strong> {{ formatDate(receipt.payment_date) }}</div>
                </div>
                <div v-else class="empty-state">No receipt available</div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import AssociationNavBar from './AssociationNavBar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const API_BASE = getApiBase()
const invoice = ref({})
const receipt = ref(null)
const loading = ref(true)

onMounted(async () => {
  await loadInvoice()
  await loadReceipt()
})

async function loadInvoice() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/invoices/`, { headers: auth })
    const inv = (resp.data || []).find(i => i.id === Number(id))
    invoice.value = inv || {}
  } catch (err) {
    console.error('Failed to load invoice', err)
    invoice.value = {}
  } finally { loading.value = false }
}

async function loadReceipt() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) return
    const resp = await axios.get(`${API_BASE}/api/invoices/${id}/receipt`, { headers: auth })
    receipt.value = resp.data
  } catch (err) {
    receipt.value = null
  }
}

function formatDate(d) { if (!d) return 'N/A'; return new Date(d).toLocaleString() }

function downloadReceiptData() {
  if (!receipt.value) return alert('No receipt to download')
  const blob = new Blob([JSON.stringify(receipt.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `receipt-${id}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function printReceipt() {
  // open a new window with receipt html and call print
  const content = document.createElement('div')
  const title = document.createElement('h2')
  title.innerText = `Receipt ${receipt.value ? receipt.value.receipt_number : ''}`
  content.appendChild(title)
  const pre = document.createElement('pre')
  pre.innerText = receipt.value ? JSON.stringify(receipt.value, null, 2) : 'No receipt'
  content.appendChild(pre)
  const w = window.open('', '_blank')
  if (!w) return alert('Popup blocked')
  w.document.body.appendChild(content)
  w.document.close()
  w.print()
  w.close()
}
</script>

<style scoped>
* { box-sizing: border-box; margin:0; padding:0 }
.admin-wrapper { min-height:100vh; background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%); }
.admin-container { max-width:900px; margin:1.5rem auto; padding:1rem }
.detail-card { background:white; border-radius:1.25rem; box-shadow:0 12px 40px rgba(0,0,0,0.06); overflow:hidden }
.detail-card .card-header { padding:1.25rem 1.5rem; background: linear-gradient(145deg,#e5f2ff 0%, #d6e8ff 100%); border-bottom:1px solid rgba(34,49,63,0.04); display:flex; justify-content:space-between; align-items:center }
.card-title { font-weight:800; color:#0f2540 }
.card-actions { display:flex; gap:0.5rem }
.btn-print { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.5rem 0.8rem; border-radius:8px }
.btn-download { background:#fff3bf; color:#92400e; border:1px solid rgba(146,64,14,0.08); padding:0.5rem 0.8rem; border-radius:8px }
.card-body { padding:1.25rem }
.meta-row { display:flex; gap:1rem; margin-top:0.6rem }
.receipt-section { margin-top:1rem }
.empty-state { text-align:center; padding:1rem; color:#6d7b86; background:#fbfdff; border-radius:8px }

@media (max-width:768px) { .meta-row { flex-direction:column } }
</style>
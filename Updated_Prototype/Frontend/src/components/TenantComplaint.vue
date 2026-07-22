<template>
  <div class="admin-wrapper">
    <TenantNavbar />

    <div class="admin-container">
      <div class="complaints-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">My Complaints</h2>
            <p class="card-subtitle">Raise a complaint, track its progress, and view the latest updates.</p>
          </div>
          <button type="button" class="btn-add" @click="goToRaiseComplaint">Raise Complaint</button>
        </div>

        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading complaints…</div>
          <div v-else>
            <div v-if="complaints.length === 0" class="empty-state">You have not raised any complaints yet.</div>
            <div v-else class="complaint-grid">
              <div v-for="c in complaints" :key="c.id" class="complaint-card">
                <div class="complaint-main">
                  <div class="complaint-top">
                    <div>
                      <h3 class="complaint-title">{{ c.title }}</h3>
                      <div class="complaint-meta">{{ c.category }} • {{ c.priority }} • Flat {{ c.flat_number }}</div>
                    </div>
                    <span class="status-pill" :class="statusClass(c.status)">{{ c.status }}</span>
                  </div>
                  <p class="complaint-desc">{{ summarize(c.description) }}</p>
                  <div class="complaint-foot">
                    <span>Raised {{ formatDate(c.created_at) }}</span>
                    <span v-if="c.assigned_worker_name">Assigned to {{ c.assigned_worker_name }}</span>
                  </div>
                </div>
                <div class="complaint-actions">
                  <button class="btn-view" @click="viewComplaint(c)">View</button>
                </div>
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
import { useRouter } from 'vue-router'
import axios from 'axios'
import TenantNavbar from './TenantNavbar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const router = useRouter()
const API_BASE = getApiBase()
const complaints = ref([])
const loading = ref(true)

onMounted(async () => {
  await fetchComplaints()
})

async function fetchComplaints() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) {
      router.push('/login')
      return
    }
    const resp = await axios.get(`${API_BASE}/api/complaints/`, { headers: auth })
    complaints.value = resp.data || []
  } catch (err) {
    console.error('Failed to fetch complaints:', err)
    complaints.value = []
  } finally {
    loading.value = false
  }
}

function goToRaiseComplaint() {
  router.push('/raise-complaint')
}

function viewComplaint(item) {
  router.push(`/tenant-complaints/${item.id}`)
}

function summarize(text) {
  if (!text) return 'No description provided.'
  return text.length > 170 ? text.slice(0, 170) + '…' : text
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function statusClass(status) {
  switch (status) {
    case 'COMPLETED':
    case 'CLOSED':
      return 'status-complete'
    case 'IN_PROGRESS':
      return 'status-progress'
    case 'ASSIGNED':
      return 'status-assigned'
    default:
      return 'status-open'
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0 }

.admin-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%);
}

.admin-container {
  max-width: 1400px;
  margin: 1.5rem auto;
  padding: 1rem;
  width: 100%;
}

.complaints-card {
  background: #ffffff;
  border-radius: 1.25rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  width: 100%;
}

.complaints-card .card-header {
  padding: 1.25rem 1.5rem;
  background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%);
  border-bottom: 1px solid rgba(34, 49, 63, 0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.card-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f2540;
}

.card-subtitle {
  margin-top: 0.35rem;
  color: #556c86;
  font-size: 0.95rem;
}

.card-body {
  padding: 1.5rem;
}

.btn-add {
  padding: 0.6rem 1rem;
  border-radius: 10px;
  background: linear-gradient(90deg, #2b7ef7, #0b63e6);
  color: white;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.complaint-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.complaint-card {
  background: #fbfdff;
  border-radius: 1rem;
  padding: 1rem;
  box-shadow: 0 10px 28px rgba(34, 49, 63, 0.04);
  border: 1px solid rgba(129, 167, 210, 0.12);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.complaint-main {
  flex: 1;
}

.complaint-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.complaint-title {
  margin: 0;
  color: #0f2540;
  font-weight: 800;
}

.complaint-meta {
  margin-top: 0.35rem;
  color: #475b71;
  font-size: 0.92rem;
  font-weight: 700;
}

.complaint-desc {
  margin-top: 0.7rem;
  color: #2b3b4a;
  line-height: 1.5;
}

.complaint-foot {
  margin-top: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: #556c86;
  font-size: 0.9rem;
}

.status-pill {
  padding: 0.4rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-open {
  background: rgba(39, 133, 253, 0.12);
  color: #1c64f2;
}

.status-assigned {
  background: rgba(249, 115, 22, 0.14);
  color: #c2410c;
}

.status-progress {
  background: rgba(245, 158, 11, 0.16);
  color: #b45309;
}

.status-complete {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.btn-view {
  padding: 0.5rem 0.8rem;
  border-radius: 10px;
  border: none;
  background: linear-gradient(90deg, #2b7ef7, #0b63e6);
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 1.5rem;
  color: #6d7b86;
  font-style: italic;
  background: #fbfdff;
  border-radius: 12px;
}

@media (max-width: 768px) {
  .complaints-card .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .complaint-card {
    flex-direction: column;
  }
}
</style>

<template>
  <div class="admin-wrapper">
    <TenantNavbar />

    <div class="admin-container">
      <div class="detail-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Complaint Details</h2>
            <p class="card-subtitle">Track the status and see the full history for this complaint.</p>
          </div>
        </div>

        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading complaint…</div>
          <div v-else>
            <div class="detail-grid">
              <div class="detail-main">
                <h3 class="detail-title">{{ complaint.title }}</h3>
                <p class="detail-desc">{{ complaint.description || 'No description provided.' }}</p>

                <div class="meta-grid">
                  <div class="meta-item"><span class="meta-label">Category</span><span>{{ complaint.category }}</span></div>
                  <div class="meta-item"><span class="meta-label">Priority</span><span>{{ complaint.priority }}</span></div>
                  <div class="meta-item"><span class="meta-label">Status</span><span>{{ complaint.status }}</span></div>
                  <div class="meta-item"><span class="meta-label">Flat Number</span><span>{{ complaint.flat_number }}</span></div>
                  <div class="meta-item"><span class="meta-label">Raised By</span><span>{{ complaint.raised_by_name || 'You' }}</span></div>
                  <div class="meta-item"><span class="meta-label">Assigned Worker</span><span>{{ complaint.assigned_worker_name || 'Pending' }}</span></div>
                  <div class="meta-item"><span class="meta-label">Created Date</span><span>{{ formatDate(complaint.created_at) }}</span></div>
                  <div class="meta-item"><span class="meta-label">Resolved Date</span><span>{{ complaint.resolved_at ? formatDate(complaint.resolved_at) : 'Not resolved yet' }}</span></div>
                </div>

                <div class="history-card">
                  <h4>Complaint History</h4>
                  <div v-if="complaint.updates && complaint.updates.length" class="history-list">
                    <div v-for="u in complaint.updates" :key="u.id" class="history-item">
                      <div class="history-head">
                        <strong>{{ u.updated_by_name || 'System' }}</strong>
                        <span>{{ formatDate(u.updated_at) }}</span>
                      </div>
                      <div class="history-status">Status: {{ u.status }}</div>
                      <div class="history-remarks">{{ u.remarks || 'No remarks provided.' }}</div>
                    </div>
                  </div>
                  <div v-else class="empty-state">No history updates yet.</div>
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
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import TenantNavbar from './TenantNavbar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const API_BASE = getApiBase()
const complaint = ref({})
const loading = ref(true)

onMounted(async () => {
  await loadComplaint()
})

async function loadComplaint() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) {
      router.push('/login')
      return
    }
    const resp = await axios.get(`${API_BASE}/api/complaints/${route.params.id}`, { headers: auth })
    complaint.value = resp.data || {}
  } catch (err) {
    console.error('Failed to load complaint:', err)
    complaint.value = {}
  } finally {
    loading.value = false
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
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
  max-width: 1200px;
  margin: 1.5rem auto;
  padding: 1rem;
  width: 100%;
}

.detail-card {
  background: #ffffff;
  border-radius: 1.25rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.detail-card .card-header {
  padding: 1.25rem 1.5rem;
  background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%);
  border-bottom: 1px solid rgba(34, 49, 63, 0.04);
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

.detail-title {
  color: #0f2540;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.detail-desc {
  color: #2b3b4a;
  line-height: 1.6;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
  margin-top: 1rem;
}

.meta-item {
  background: #fbfdff;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  border: 1px solid rgba(129, 167, 210, 0.12);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.meta-label {
  color: #475b71;
  font-size: 0.85rem;
  font-weight: 700;
}

.history-card {
  margin-top: 1.3rem;
  background: #fbfdff;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(129, 167, 210, 0.12);
}

.history-card h4 {
  color: #0f2540;
  margin-bottom: 0.75rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  background: #ffffff;
  border-radius: 10px;
  padding: 0.8rem;
  border: 1px solid rgba(129, 167, 210, 0.08);
}

.history-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  color: #0f2540;
  margin-bottom: 0.25rem;
}

.history-status {
  color: #475b71;
  font-weight: 700;
  margin-bottom: 0.2rem;
}

.history-remarks {
  color: #2b3b4a;
}

.empty-state {
  text-align: center;
  padding: 1.25rem;
  color: #6d7b86;
  font-style: italic;
  background: #fbfdff;
  border-radius: 12px;
}
</style>

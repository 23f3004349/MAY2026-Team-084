<template>
  <div class="admin-wrapper">
    <AssociationNavBar />
    <div class="admin-container">
      <div class="detail-card">
        <div class="card-header">
          <h2 class="card-title">Complaint Details</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading…</div>
          <div v-else>
            <div class="detail-grid">
              <div class="detail-main">
                <h3>{{ complaint.title }}</h3>
                <p class="desc">{{ complaint.description }}</p>

                <div class="meta-row">
                  <div><strong>Category:</strong> {{ complaint.category }}</div>
                  <div><strong>Priority:</strong> {{ complaint.priority }}</div>
                  <div><strong>Status:</strong> {{ complaint.status }}</div>
                </div>

                <div class="meta-row">
                  <div><strong>Flat Number:</strong> {{ complaint.flat_number }}</div>
                  <div><strong>Raised By:</strong> {{ complaint.raised_by_name }}</div>
                  <div><strong>Assigned Worker:</strong> {{ complaint.assigned_worker_name || 'N/A' }}</div>
                </div>

                <div class="meta-row">
                  <div><strong>Created:</strong> {{ formatDate(complaint.created_at) }}</div>
                  <div><strong>Resolved:</strong> {{ complaint.resolved_at ? formatDate(complaint.resolved_at) : 'N/A' }}</div>
                </div>

                <div class="history">
                  <h4>History & Updates</h4>
                  <div v-if="complaint.updates && complaint.updates.length">
                    <div v-for="u in complaint.updates" :key="u.id" class="update-item">
                      <div class="update-head">
                        <strong>{{ u.updated_by_name || 'System' }}</strong>
                        <span class="update-time">{{ formatDate(u.updated_at) }}</span>
                      </div>
                      <div class="update-body">
                        <div><strong>Status:</strong> {{ u.status }}</div>
                        <div><strong>Remarks:</strong> {{ u.remarks || '—' }}</div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-state">No updates yet.</div>
                </div>

              </div>

              <div class="detail-actions">
                <button class="btn-assign" @click="openAssign">Assign</button>
                <button class="btn-status" @click="openStatus">Update Status</button>
                <button class="btn-delete" @click="deleteComplaint">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- reuse modals from associationcomplaint via scoped logic -->
    <div v-if="assigning" class="modal-overlay" @click.self="closeAssign">
      <div class="modal">
        <h3>Assign Worker</h3>
        <select v-model="assignWorkerId">
          <option v-for="w in workers" :key="w.id" :value="w.id">{{ w.name }} — {{ w.email }}</option>
        </select>
        <textarea v-model="assignRemarks" placeholder="Remarks (optional)"></textarea>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeAssign">Cancel</button>
          <button class="btn-submit" @click="submitAssign">Assign</button>
        </div>
      </div>
    </div>

    <div v-if="statusing" class="modal-overlay" @click.self="closeStatus">
      <div class="modal">
        <h3>Update Status</h3>
        <select v-model="newStatus">
          <option value="OPEN">OPEN</option>
          <option value="ASSIGNED">ASSIGNED</option>
          <option value="IN_PROGRESS">IN_PROGRESS</option>
          <option value="COMPLETED">COMPLETED</option>
          <option value="CLOSED">CLOSED</option>
        </select>
        <textarea v-model="statusRemarks" placeholder="Remarks (optional)"></textarea>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeStatus">Cancel</button>
          <button class="btn-submit" @click="submitStatus">Update</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import AssociationNavBar from './AssociationNavBar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const router = useRouter()
const route = useRoute()
const API_BASE = getApiBase()
const complaint = ref({})
const loading = ref(true)
const assigning = ref(false)
const statusing = ref(false)
const workers = ref([])
const assignWorkerId = ref(null)
const assignRemarks = ref('')
const newStatus = ref('')
const statusRemarks = ref('')

const id = route.params.id

onMounted(async () => {
  await loadComplaint()
  await fetchWorkers()
})

async function loadComplaint() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/complaints/${id}`, { headers: auth })
    complaint.value = resp.data || {}
  } catch (err) {
    console.error('Failed to load complaint', err)
    complaint.value = {}
  } finally {
    loading.value = false
  }
}

async function fetchWorkers() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) return
    const resp = await axios.get(`${API_BASE}/api/members/`, { headers: auth })
    workers.value = (resp.data || []).filter(m => m.role === 'WORKER')
  } catch (err) {
    console.error('Failed to fetch workers', err)
    workers.value = []
  }
}

function openAssign() {
  assignWorkerId.value = complaint.value.assigned_worker_id || null
  assignRemarks.value = ''
  assigning.value = true
}
function closeAssign() { assigning.value = false }
async function submitAssign() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    await axios.put(`${API_BASE}/api/complaints/${id}/assign`, { worker_id: assignWorkerId.value, remarks: assignRemarks.value }, { headers: auth })
    await loadComplaint()
    assigning.value = false
  } catch (err) {
    console.error(err)
    alert('Failed to assign')
  }
}

function openStatus() { newStatus.value = complaint.value.status || 'OPEN'; statusRemarks.value = ''; statusing.value = true }
function closeStatus() { statusing.value = false }
async function submitStatus() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    await axios.put(`${API_BASE}/api/complaints/${id}/status`, { status: newStatus.value, remarks: statusRemarks.value }, { headers: auth })
    await loadComplaint()
    statusing.value = false
  } catch (err) {
    console.error(err)
    alert('Failed to update status')
  }
}

async function deleteComplaint() {
  if (!confirm('Delete this complaint?')) return
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    await axios.delete(`${API_BASE}/api/complaints/${id}`, { headers: auth })
    router.push('/complaints')
  } catch (err) {
    console.error(err)
    alert('Failed to delete')
  }
}

function formatDate(d) { if (!d) return 'N/A'; return new Date(d).toLocaleString() }
</script>

<style scoped>
* { box-sizing: border-box; margin:0; padding:0 }
.admin-wrapper { min-height:100vh; background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%); }
.admin-container { max-width:1200px; margin:1.5rem auto; padding:1rem }
.detail-card { background:white; border-radius:1.25rem; box-shadow:0 12px 40px rgba(0,0,0,0.06); overflow:hidden }
.detail-card .card-header { padding:1.25rem 1.5rem; background: linear-gradient(145deg,#e5f2ff 0%, #d6e8ff 100%); border-bottom:1px solid rgba(34,49,63,0.04) }
.card-title { font-weight:800; color:#0f2540 }
.card-body { padding:1.5rem }
.detail-grid { display:flex; gap:1.5rem }
.detail-main { flex:1 }
.detail-actions { width:220px; display:flex; flex-direction:column; gap:0.75rem }
.desc { color:#2b3b4a }
.meta-row { display:flex; gap:1rem; margin-top:0.8rem }
.history { margin-top:1rem }
.update-item { background:#fbfdff; border-radius:8px; padding:0.8rem; margin-bottom:0.6rem; border:1px solid rgba(129,167,210,0.06) }
.update-head { display:flex; justify-content:space-between; align-items:center }
.update-time { color:#556c86; font-size:0.9rem }

.btn-assign { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.6rem; border-radius:12px; font-weight:800 }
.btn-status { background:#fff3bf; border:1px solid rgba(146,64,14,0.08); color:#92400e; padding:0.6rem; border-radius:12px; font-weight:800 }
.btn-delete { background:white; border:1px solid rgba(220,38,38,0.12); color:#c53030; padding:0.6rem; border-radius:12px; font-weight:800 }

.modal-overlay { position:fixed; inset:0; background: rgba(3,6,23,0.5); display:flex; align-items:center; justify-content:center }
.modal { background:white; padding:1.25rem; border-radius:12px; width:420px; max-width:90vw }
.modal textarea, .modal select { width:100%; margin-top:0.5rem; padding:0.6rem; border-radius:8px; border:1px solid rgba(129,167,210,0.18); background:#f8fbff }
.modal-actions { display:flex; justify-content:flex-end; gap:0.75rem; margin-top:0.75rem }
.btn-cancel { background:white; border:1px solid rgba(129,167,210,0.18); padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:700;color:black }
.btn-submit { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:800 }

@media (max-width: 768px) {
  .detail-grid { flex-direction:column }
}
</style>
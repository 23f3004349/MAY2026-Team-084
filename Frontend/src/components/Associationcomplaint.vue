<template>
  <div class="admin-wrapper">
    <AssociationNavBar />

    <div class="admin-container">
      <div class="complaints-card">
        <div class="card-header">
          <h2 class="card-title">Complaints</h2>
          <button class="btn-add" @click="addComplaint">Add Complaint</button>
        </div>

        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading complaints…</div>
          <div v-else>
            <div v-if="complaints.length === 0" class="empty-state">No complaints found</div>
            <div v-else class="complaint-grid">
              <div v-for="c in complaints" :key="c.id" class="complaint-card">
                <div class="complaint-row">
                  <div>
                    <h3 class="complaint-title">{{ c.title }}</h3>
                    <div class="complaint-meta">{{ c.category }} · {{ c.priority }} · {{ c.flat_number }}</div>
                    <p class="complaint-desc">{{ (c.description && c.description.length > 180) ? c.description.slice(0,180) + '…' : c.description }}</p>
                  </div>

                  <div class="complaint-actions">
                    <button class="btn-view" @click="viewComplaint(c)">View</button>
                    <button class="btn-assign" @click="openAssign(c)">Assign</button>
                    <button class="btn-status" @click="openStatus(c)">Status</button>
                    <button class="btn-delete" @click="deleteComplaint(c)">Delete</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign modal -->
    <div v-if="assigning" class="modal-overlay" @click.self="closeAssign">
      <div class="modal">
        <h3>Assign Worker</h3>
        <select v-model="assignWorkerId">
          <option v-for="w in workers" :key="w.id" :value="w.id">{{ w.name }} — {{ w.phone || 'N/A' }}</option>
        </select>
        <textarea v-model="assignRemarks" placeholder="Remarks (optional)"></textarea>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeAssign">Cancel</button>
          <button class="btn-submit" @click="submitAssign">Assign</button>
        </div>
      </div>
    </div>

    <!-- Status modal -->
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
import { useRouter } from 'vue-router'
import axios from 'axios'
import AssociationNavBar from './AssociationNavBar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const router = useRouter()
const complaints = ref([])
const loading = ref(true)
const API_BASE = getApiBase()

const assigning = ref(false)
const statusing = ref(false)
const current = ref(null)
const assignWorkerId = ref(null)
const assignRemarks = ref('')
const workers = ref([])
const newStatus = ref('')
const statusRemarks = ref('')

onMounted(async () => {
  await fetchComplaints()
  await fetchWorkers()
})

async function fetchComplaints() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/complaints/`, { headers: auth })
    complaints.value = resp.data || []
  } catch (err) {
    console.error('Failed to fetch complaints:', err)
    complaints.value = []
  } finally {
    loading.value = false
  }
}

async function fetchWorkers() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { return }
    const resp = await axios.get(`${API_BASE}/api/members/`, { headers: auth })
    // treat residents with role WORKER as workers
    workers.value = (resp.data || []).filter(m => m.role === 'WORKER')
  } catch (err) {
    console.error('Failed to fetch workers', err)
    workers.value = []
  }
}

function addComplaint() {
  router.push('/add-complaint')
}

function viewComplaint(c) {
  router.push(`/complaints/${c.id}`)
}

function openAssign(c) {
  current.value = c
  assignWorkerId.value = c.assigned_worker_id || null
  assignRemarks.value = ''
  assigning.value = true
}

function closeAssign() { assigning.value = false }

async function submitAssign() {
  if (!current.value) return
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    await axios.put(`${API_BASE}/api/complaints/${current.value.id}/assign`, { worker_id: assignWorkerId.value, remarks: assignRemarks.value }, { headers: auth })
    await fetchComplaints()
    assigning.value = false
  } catch (err) {
    console.error('Failed to assign worker', err)
    alert('Failed to assign worker')
  }
}

function openStatus(c) {
  current.value = c
  newStatus.value = c.status || 'OPEN'
  statusRemarks.value = ''
  statusing.value = true
}

function closeStatus() { statusing.value = false }

async function submitStatus() {
  if (!current.value) return
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    await axios.put(`${API_BASE}/api/complaints/${current.value.id}/status`, { status: newStatus.value, remarks: statusRemarks.value }, { headers: auth })
    await fetchComplaints()
    statusing.value = false
  } catch (err) {
    console.error('Failed to update status', err)
    alert('Failed to update status')
  }
}

async function deleteComplaint(c) {
  if (!confirm('Delete this complaint?')) return
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    await axios.delete(`${API_BASE}/api/complaints/${c.id}`, { headers: auth })
    await fetchComplaints()
  } catch (err) {
    console.error('Failed to delete complaint', err)
    alert('Failed to delete complaint')
  }
}

</script>

<style scoped>
* { box-sizing: border-box; margin:0; padding:0 }
.admin-wrapper { display:flex; flex-direction:column; min-height:100vh; background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%); }
.admin-container { max-width:2000px; margin:1.5rem auto; padding:1rem }

.complaints-card { background:#ffffff; border-radius:1.25rem; box-shadow:0 12px 40px rgba(0,0,0,0.06); overflow:hidden; width:90vw; max-width:none; margin:1.5rem auto }
.complaints-card .card-header { padding:1.25rem 1.5rem; background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%); border-bottom:1px solid rgba(34,49,63,0.04); display:flex; align-items:center; justify-content:space-between }
.card-title { font-size:1.4rem; font-weight:800; color:#0f2540 }
.card-body { padding:1.75rem 2rem }
.btn-add { padding: 0.5rem 0.9rem; border-radius: 8px; font-weight:700; cursor:pointer; border: none; background: linear-gradient(90deg,#2b7ef7,#0b63e6); color: white }
.btn-add:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(43,126,247,0.18) }

.complaint-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1rem }
.complaint-card { background:#fbfdff; padding:1rem; border-radius:12px; box-shadow:0 10px 28px rgba(34,49,63,0.04); display:flex; align-items:flex-start; justify-content:space-between }
.complaint-row { display:flex; justify-content:space-between; gap:1rem; width:100% }
.complaint-title { margin:0; color:#0f2540; font-weight:800 }
.complaint-meta { color:#475b71; font-weight:700; margin-top:0.35rem }
.complaint-desc { color:#2b3b4a; margin-top:0.6rem }

.complaint-actions { display:flex; flex-direction:column; gap:0.5rem }
.btn-view, .btn-assign, .btn-status, .btn-delete { padding:0.45rem 0.75rem; border-radius:8px; font-weight:700; cursor:pointer; border:1px solid rgba(15,37,64,0.08); background:white }
.btn-assign { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none }
.btn-status { background:#fff3bf; color:#92400e; border-color: rgba(146,64,14,0.08) }
.btn-delete { border-color: rgba(220,38,38,0.12); color:#c53030 }

.modal-overlay { position:fixed; inset:0; background: rgba(3,6,23,0.5); display:flex; align-items:center; justify-content:center }
.modal { background:white; padding:1.25rem; border-radius:12px; width:420px; max-width:90vw }
.modal textarea, .modal select { width:100%; margin-top:0.5rem; padding:0.6rem; border-radius:8px; border:1px solid rgba(129,167,210,0.18); background:#f8fbff }
.modal-actions { display:flex; justify-content:flex-end; gap:0.75rem; margin-top:0.75rem }
.btn-cancel { background:white; border:1px solid rgba(129,167,210,0.18); padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:700;color:black }
.btn-submit { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:800 }

@media (max-width: 768px) {
  .complaint-row { flex-direction:column }
  .complaint-actions { flex-direction:row }
}
</style>
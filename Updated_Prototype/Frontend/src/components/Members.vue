<template>
  <div class="admin-wrapper">
    <AssociationNavBar />

    <div class="admin-container">
      <div class="members-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Community Members</h2>
            <p class="card-subtitle">Manage resident details, tenancy status, and account activity.</p>
          </div>
        </div>

        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading members…</div>
          <div v-else>
            <div v-if="members.length === 0" class="empty-state">No members found.</div>
            <div v-else class="member-grid">
              <div v-for="member in members" :key="member.id" class="member-card">
                <div class="member-card-header">
                  <div>
                    <h3>{{ member.name }}</h3>
                    <p class="member-role">{{ member.role }}</p>
                  </div>
                  <span :class="['status-pill', member.is_active ? 'status-active' : 'status-inactive']">
                    {{ member.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>

                <div class="member-details">
                  <div class="member-detail"><span class="detail-label">Email</span><span>{{ member.email }}</span></div>
                  <div class="member-detail"><span class="detail-label">Phone Number</span><span>{{ member.phone || 'N/A' }}</span></div>
                  <div class="member-detail"><span class="detail-label">Flat Number</span><span>{{ member.flat_number }}</span></div>
                  <div class="member-detail"><span class="detail-label">Block</span><span>{{ member.block || 'N/A' }}</span></div>
                  <div class="member-detail"><span class="detail-label">Floor</span><span>{{ member.floor || 'N/A' }}</span></div>
                  <div class="member-detail"><span class="detail-label">Tenant Status</span><span>{{ member.is_owner ? 'Owner' : 'Tenant' }}</span></div>
                  <div class="member-detail"><span class="detail-label">Move in Date</span><span>{{ formatDate(member.move_in_date) }}</span></div>
                  <div class="member-detail"><span class="detail-label">Move out Date</span><span>{{ formatDate(member.move_out_date) }}</span></div>
                </div>

                <div class="member-actions">
                  <button class="btn-edit" @click="editMember(member)">Edit</button>
                  <button class="btn-deactivate" :disabled="!member.is_active" @click="deactivateMember(member)">Deactivate</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card-footer">
          <button class="btn-add-member" @click="addMember">Add Member</button>
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
const members = ref([])
const loading = ref(true)
const API_BASE = getApiBase()

onMounted(async () => {
  await fetchMembers()
})

async function fetchMembers() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) {
      router.push('/login')
      return
    }
    const resp = await axios.get(`${API_BASE}/api/members/`, { headers: auth })
    members.value = resp.data || []
  } catch (err) {
    console.error('Failed to fetch members:', err)
    members.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function editMember(member) {
  router.push(`/edit-member/${member.id}`)
}

async function deactivateMember(member) {
  if (!member.is_active) return
  if (!confirm(`Deactivate ${member.name}?`)) return
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) {
      router.push('/login')
      return
    }
    await axios.delete(`${API_BASE}/api/members/${member.id}`, { headers: auth })
    await fetchMembers()
  } catch (err) {
    console.error('Failed to deactivate member:', err)
    alert('Failed to deactivate member')
  }
}

function addMember() {
  router.push('/add-member')
}
</script>

<style scoped>
* { box-sizing: border-box; margin:0; padding:0 }

.admin-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%);
}

.admin-container {
  max-width: 2000px;
  margin: 1.5rem auto;
  padding: 1rem;
}

.members-card {
  background: #ffffff;
  border-radius: 1.5rem;
  box-shadow: 0 12px 40px rgba(0,0,0,0.06);
  overflow: hidden;
  width: 90vw;
  max-width: none;
  margin: 1.5rem auto;
}

.members-card .card-header {
  padding: 1.5rem 2rem;
  background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%);
  border-bottom: 1px solid rgba(34,49,63,0.04);
}

.card-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #0f2540;
}

.card-subtitle {
  margin-top: 0.35rem;
  color: #556c86;
  font-size: 0.95rem;
}

.card-body {
  padding: 1.75rem 2rem;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.member-card {
  background: #fbfdff;
  border-radius: 1.25rem;
  box-shadow: 0 10px 28px rgba(34,49,63,0.04);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.member-card-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.member-card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #0f2540;
}

.member-role {
  margin-top: 0.35rem;
  color: #475b71;
  font-size: 0.95rem;
}

.status-pill {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
}

.status-active {
  background: rgba(39, 133, 253, 0.12);
  color: #1c64f2;
}

.status-inactive {
  background: rgba(220, 38, 38, 0.12);
  color: #c53030;
}

.member-details {
  display: grid;
  gap: 0.9rem;
}

.member-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  background: #ffffff;
  border: 1px solid rgba(129,167,210,0.15);
}

.detail-label {
  color: #475b71;
  font-weight: 700;
  min-width: 120px;
}

.member-detail span:last-child {
  color: #0f2540;
  text-align: right;
  word-break: break-word;
}

.member-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.btn-edit,
.btn-deactivate,
.btn-add-member {
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  padding: 0.7rem 1rem;
  transition: all 0.2s ease;
}

.btn-edit {
  background: linear-gradient(90deg, #2b7ef7, #0b63e6);
  color: white;
}

.btn-edit:hover {
  transform: translateY(-1px);
}

.btn-deactivate {
  background: white;
  border: 1px solid rgba(220, 38, 38, 0.16);
  color: #c53030;
}

.btn-deactivate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-footer {
  padding: 1.5rem 2rem 2rem;
  display: flex;
  justify-content: center;
}

.btn-add-member {
  background: linear-gradient(90deg,#2b7ef7,#0b63e6);
  color: white;
  padding: 0.9rem 1.4rem;
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
  .admin-container { margin: 1rem; padding: 0.75rem }
  .member-card { padding: 1.25rem }
}
</style>

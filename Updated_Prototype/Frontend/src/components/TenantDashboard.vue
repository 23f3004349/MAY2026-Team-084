<template>
  <div class="admin-wrapper">
    <TenantNavbar />

    <div class="admin-container">
      <div class="announcement-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Announcements</h2>
            <p class="card-subtitle">Stay updated with the latest community notices.</p>
          </div>
        </div>

        <div class="card-body">
          <div v-if="loading" class="empty-state">Loading announcements…</div>
          <div v-else>
            <div v-if="filteredAnnouncements.length === 0" class="empty-state">No announcements found.</div>
            <div v-else class="announcement-list">
              <div v-for="item in filteredAnnouncements" :key="item.id" class="announcement-item">
                <div class="ann-top">
                  <div>
                    <h3 class="ann-title">{{ item.title }}</h3>
                    <p class="ann-meta">{{ item.category }} • {{ formatDate(item.created_at) }}</p>
                  </div>
                  <span class="status-pill" :class="item.is_active ? 'status-active' : 'status-inactive'">
                    {{ item.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <p class="ann-content">{{ item.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import TenantNavbar from './TenantNavbar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const API_BASE = getApiBase()

const announcements = ref([])
const loading = ref(true)

onMounted(async () => {
  await fetchAnnouncements()
})

async function fetchAnnouncements() {
  loading.value = true
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) {
      router.push('/login')
      return
    }
    const resp = await axios.get(`${API_BASE}/api/notices/`, { headers: auth })
    announcements.value = resp.data || []
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    announcements.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const filteredAnnouncements = computed(() => {
  const query = (route.query.search || '').toString().trim().toLowerCase()
  if (!query) return announcements.value

  return announcements.value.filter((item) => {
    const title = (item.title || '').toLowerCase()
    const content = (item.content || '').toLowerCase()
    const category = (item.category || '').toLowerCase()
    return title.includes(query) || content.includes(query) || category.includes(query)
  })
})
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

.announcement-card {
  background: #ffffff;
  border-radius: 1.25rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  width: 100%;
}

.announcement-card .card-header {
  padding: 1.25rem 1.5rem;
  background: linear-gradient(145deg, #e5f2ff 0%, #d6e8ff 100%);
  border-bottom: 1px solid rgba(34, 49, 63, 0.04);
}

.card-title {
  font-size: 1.5rem;
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

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.announcement-item {
  background: #fbfdff;
  border-radius: 1rem;
  padding: 1.1rem 1.2rem;
  box-shadow: 0 10px 28px rgba(34, 49, 63, 0.04);
  border: 1px solid rgba(129, 167, 210, 0.12);
}

.ann-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.55rem;
}

.ann-title {
  font-size: 1.08rem;
  font-weight: 800;
  color: #0f2540;
}

.ann-meta {
  margin-top: 0.25rem;
  color: #556c86;
  font-size: 0.9rem;
}

.status-pill {
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-active {
  background: rgba(39, 133, 253, 0.12);
  color: #1c64f2;
}

.status-inactive {
  background: rgba(220, 38, 38, 0.12);
  color: #c53030;
}

.ann-content {
  color: #2b3b4a;
  line-height: 1.6;
  white-space: pre-wrap;
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
  .admin-container {
    margin: 1rem;
    padding: 0.75rem;
  }

  .card-body {
    padding: 1rem;
  }

  .ann-top {
    flex-direction: column;
  }
}
</style>

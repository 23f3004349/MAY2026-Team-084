<template>
  <nav class="navbar navbar-expand-lg navbar-light custom-navbar">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">Tenant</a>

      <div class="search-container">
        <form class="search-form" @submit.prevent="handleSearch">
          <input
            v-model="searchQuery"
            class="search-input"
            type="search"
            placeholder="Search announcements"
            aria-label="Search announcements"
          />
          <button class="btn-search" type="submit">Search</button>
        </form>
      </div>

      <div class="navbar-nav ms-auto nav-links">
        <button @click="goToDashboard" class="nav-link btn btn-link me-2">Dashboard</button>
        <button @click="goToComplaints" class="nav-link btn btn-link me-2">Complaints</button>
        <button @click="goToInfo" class="nav-link btn btn-link me-2">Info</button>
        <button @click="goToPayments" class="nav-link btn btn-link me-2">Payments</button>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

function handleSearch() {
  if (!searchQuery.value.trim()) {
    router.push('/tenant-dashboard')
    return
  }
  router.push({ path: '/tenant-dashboard', query: { search: searchQuery.value } })
}

function goToDashboard() {
  searchQuery.value = ''
  router.push('/tenant-dashboard')
}
function goToPayments() {
  searchQuery.value = ''
  router.push('/payments')
}
function goToComplaints() {
  searchQuery.value = ''
  router.push('/tenant-complaints')
}
function goToInfo() {
  searchQuery.value = ''
  router.push('/info')
}
function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>

<style scoped>
.custom-navbar {
  padding: 1rem 0 !important;
  box-shadow: 0 10px 30px rgba(132, 170, 210, 0.04);
  background: #ffffff !important;
  border-bottom: 1px solid rgba(135, 172, 210, 0.12);
}

.navbar-brand {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f2540 !important;
  margin-right: 1.5rem;
  letter-spacing: -0.02em;
}

.search-container {
  flex-grow: 1;
  display: flex;
  justify-content: flex-start;
  padding: 0 1rem;
}

.search-form {
  display: flex;
  gap: 0.5rem;
  width: 100%;
  max-width: 500px;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #d7e5f5;
  border-radius: 16px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: #f8fbff;
  color: #0f2540;
}

.search-input:focus {
  outline: none;
  border-color: #aac9ed;
  box-shadow: 0 0 0 4px rgba(170, 201, 237, 0.15);
  background: #ffffff;
}

.search-input::placeholder {
  color: #7c8fa1;
}

.nav-link {
  color: #0f2540 !important;
  font-weight: 700;
  transition: all 0.2s ease;
  padding: 0.5rem 1rem !important;
}

.nav-link:hover {
  color: #2b7ef7 !important;
}

.btn-search {
  padding: 0.6rem 1.25rem;
  background: linear-gradient(135deg, #2b7ef7 0%, #0b63e6 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 0.95rem;
}

.btn-search:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(43, 126, 247, 0.18);
}

.btn-logout {
  padding: 0.6rem 1.25rem;
  background: transparent;
  color: #2f5f83;
  border: 2px solid rgba(47, 95, 131, 0.12);
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 0.95rem;
}

.btn-logout:hover {
  background: #eef6ff;
  color: #2f5f83;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(47, 95, 131, 0.08);
}

@media (max-width: 768px) {
  .search-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .search-form {
    max-width: 100%;
  }

  .custom-navbar {
    padding: 1rem 0 !important;
  }
}
</style>

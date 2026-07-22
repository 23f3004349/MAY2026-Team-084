<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light custom-navbar">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">Associate Manager</a>
      
      <div class="search-container">
        <form class="search-form" @submit.prevent="handleSearch">
          <input 
            v-model="searchQuery" 
            class="search-input" 
            type="search" 
            placeholder="Search announcement categories..."
            aria-label="Search announcement category"
          />
          <button class="btn-search" type="submit">Search</button>
        </form>
      </div>

      <div class="navbar-nav ms-auto">
        <button @click="goToMembers" class="nav-link btn btn-link me-2">Members</button>
        <button @click="goToComplaints" class="nav-link btn btn-link me-2">Complaints</button>
        <button @click="goToInvoices" class="nav-link btn btn-link me-2">Invoices</button>
        <button @click="goToDashboard" class="nav-link btn btn-link me-2">Dashboard</button>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getApiBase, getAuthHeader } from '../utils/auth'

const router = useRouter()
const API_BASE = getApiBase()
const searchQuery = ref('')

function handleSearch() {
  if (!searchQuery.value.trim()) {
    router.push('/association_manager')
    return
  }
  router.push({ path: '/association_manager', query: { category: searchQuery.value } })
}

function goToDashboard() {
  searchQuery.value = ''
  router.push('/associate_manager')
}
function goToMembers() {
  searchQuery.value = ''
  router.push('/members')
}
function goToComplaints() {
  searchQuery.value = ''
  router.push('/complaints')
}
function goToInvoices() {
  searchQuery.value = ''
  router.push('/invoices')
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
  color: #000000 !important;
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
  color: #000000;
}

.search-input:focus {
  outline: none;
  border-color: #aac9ed;
  box-shadow: 0 0 0 4px rgba(170, 201, 237, 0.15);
  background: #ffffff;
}

.search-input::placeholder {
  color: #bfafa1;
}

.nav-link {
  color: #000000 !important;
  font-weight: 700;
  transition: all 0.2s ease;
  padding: 0.5rem 1rem !important;
}

.nav-link:hover { color: #5c92df !important; }

.btn-search {
  padding: 0.6rem 1.25rem;
  background: linear-gradient(135deg,#5c92df 0%, #84b5f1 100%);
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
  box-shadow: 0 8px 20px rgba(92,146,223,0.18);
}

.btn-logout {
  padding: 0.6rem 1.25rem;
  background: transparent;
  color: #2f5f83;
  border: 2px solid rgba(47,95,131,0.12);
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
  box-shadow: 0 8px 20px rgba(47,95,131,0.08);
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

  .navbar-menu {
    width: 100%;
    justify-content: space-between;
  }

  .custom-navbar {
    padding: 1rem 0 !important;
  }
}
</style>

<template>
  <div class="add-ann-wrapper">
    <AssociationNavBar />
    <div class="form-card">
      <h2>Add Member</h2>
      <form @submit.prevent="submit">
        <label>Name</label>
        <input v-model="name" type="text" placeholder="Full name" required />

        <label>Email</label>
        <input v-model="email" type="email" placeholder="Email address" required />

        <label>Phone Number</label>
        <input v-model="phone" type="text" placeholder="Phone number" />

        <label>Role</label>
        <select v-model="role">
          <option value="RESIDENT">Resident</option>
          <option value="ADMIN">Admin</option>
        </select>

        <label>Apartment</label>
        <select v-model="apartmentId">
          <option disabled value="">Select apartment</option>
          <option v-for="apt in apartments" :key="apt.id" :value="apt.id">
            {{ apt.flat_number }} · Block {{ apt.block || 'N/A' }} · Floor {{ apt.floor || 'N/A' }}
          </option>
        </select>

        <label>Tenant Status</label>
        <select v-model="isOwner">
          <option :value="true">Owner</option>
          <option :value="false">Tenant</option>
        </select>

        <label>Move in Date</label>
        <input v-model="moveInDate" type="date" />

        <label>Password</label>
        <input v-model="password" type="password" placeholder="Password" required />

        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="cancel">Cancel</button>
          <button type="submit" class="btn-submit">Create</button>
        </div>
      </form>
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
const name = ref('')
const email = ref('')
const phone = ref('')
const role = ref('RESIDENT')
const apartmentId = ref('')
const isOwner = ref(true)
const moveInDate = ref('')
const password = ref('')
const apartments = ref([])
const API_BASE = getApiBase()

onMounted(async () => {
  await loadApartments()
})

async function loadApartments() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/members/apartments`, { headers: auth })
    apartments.value = resp.data || []
  } catch (err) {
    console.error('Failed to load apartments', err)
    apartments.value = []
  }
}

async function submit() {
  if (!name.value.trim() || !email.value.trim() || !password.value.trim() || !apartmentId.value) {
    return alert('Name, email, password, and apartment are required')
  }

  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const payload = {
      name: name.value,
      email: email.value,
      phone: phone.value,
      role: role.value,
      apartment_id: apartmentId.value,
      is_owner: isOwner.value,
      move_in_date: moveInDate.value,
      password: password.value
    }
    await axios.post(`${API_BASE}/api/members/`, payload, { headers: auth })
    router.push('/members')
  } catch (err) {
    console.error('Failed to add member', err)
    alert('Failed to add member')
  }
}

function cancel() {
  router.back()
}
</script>

<style scoped>
* { box-sizing: border-box; margin:0; padding:0 }
.add-ann-wrapper { min-height:100vh; background: radial-gradient(circle at top center, #f7fbff 0%, #f2f7ff 45%, #eef4ff 100%); padding-bottom:2rem }
.form-card { max-width:820px; margin:2rem auto; background:#ffffff; padding:2rem; border-radius:2rem; box-shadow:0 10px 30px rgba(132,170,210,0.08); overflow:hidden }
.form-card h2 { margin-bottom:0.6rem; color:#000000; font-weight:800 }
label { display:block; margin-top:0.9rem; color:#264863; font-weight:700 }
input[type="text"], input[type="email"], input[type="password"], input[type="date"], textarea, select { width:100%; padding:0.75rem 0.9rem; margin-top:0.45rem; border-radius:12px; border:1px solid rgba(129,167,210,0.18); background:#f8fbff;color:black }
.form-actions { display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.25rem }
.btn-cancel { background:white; border:1px solid rgba(129,167,210,0.18); padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:700;color:black }
.btn-submit { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:800 }

@media (max-width: 768px) {
  .form-card { margin:1rem; padding:1rem }
  input[type="text"], input[type="email"], input[type="password"], input[type="date"], textarea, select { padding:0.6rem }
}
</style>

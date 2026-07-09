<template>
  <div class="add-ann-wrapper">
    <AssociationNavBar />
    <div class="form-card">
      <h2>Edit Member</h2>
      <form @submit.prevent="submit">
        <label>Name</label>
        <input v-model="name" type="text" placeholder="Full name" required />

        <label>Email</label>
        <input v-model="email" type="email" disabled />

        <label>Phone Number</label>
        <input v-model="phone" type="text" placeholder="Phone number" />

        <label>Role</label>
        <input v-model="role" type="text" disabled />

        <label>Tenant Status</label>
        <select v-model="isOwner">
          <option :value="true">Owner</option>
          <option :value="false">Tenant</option>
        </select>

        <label>Move in Date</label>
        <input v-model="moveInDate" type="date" />

        <label>Move out Date</label>
        <input v-model="moveOutDate" type="date" />

        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="cancel">Cancel</button>
          <button type="submit" class="btn-submit">Save</button>
        </div>
      </form>
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
const memberId = route.params.id
const name = ref('')
const email = ref('')
const phone = ref('')
const role = ref('')
const isOwner = ref(true)
const moveInDate = ref('')
const moveOutDate = ref('')
const API_BASE = getApiBase()

onMounted(async () => {
  await loadMember()
})

async function loadMember() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const resp = await axios.get(`${API_BASE}/api/members/${memberId}`, { headers: auth })
    const member = resp.data
    name.value = member.name
    email.value = member.email
    phone.value = member.phone
    role.value = member.role
    isOwner.value = member.is_owner
    moveInDate.value = member.move_in_date || ''
    moveOutDate.value = member.move_out_date || ''
  } catch (err) {
    console.error('Failed to load member', err)
    alert('Failed to load member')
    router.push('/members')
  }
}

async function submit() {
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const payload = {
      name: name.value,
      phone: phone.value,
      is_owner: isOwner.value,
      move_in_date: moveInDate.value || null,
      move_out_date: moveOutDate.value || null
    }
    await axios.put(`${API_BASE}/api/members/${memberId}`, payload, { headers: auth })
    router.push('/members')
  } catch (err) {
    console.error('Failed to update member', err)
    alert('Failed to update member')
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
input[type="text"], input[type="email"], input[type="date"], textarea, select { width:100%; padding:0.75rem 0.9rem; margin-top:0.45rem; border-radius:12px; border:1px solid rgba(129,167,210,0.18); background:#f8fbff;color:black }
.form-actions { display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.25rem }
.btn-cancel { background:white; border:1px solid rgba(129,167,210,0.18); padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:700;color:black }
.btn-submit { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:800 }

@media (max-width: 768px) {
  .form-card { margin:1rem; padding:1rem }
  input[type="text"], input[type="email"], input[type="date"], textarea, select { padding:0.6rem }
}
</style>

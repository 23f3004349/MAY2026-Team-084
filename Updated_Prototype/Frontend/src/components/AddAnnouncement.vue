<template>
  <div class="add-ann-wrapper">
    <AssociationNavBar />
    <div class="form-card">
      <h2>Add Announcement</h2>
      <form @submit.prevent="submit">
        <label>Title</label>
        <input v-model="title" type="text" placeholder="Announcement title" required />

        <label>Category</label>
        <select v-model="category">
          <option value="GENERAL">General</option>
          <option value="FINANCIAL">Financial</option>
          <option value="MAINTENANCE">Maintenance</option>
          <option value="EMERGENCY">Emergency</option>
        </select>

        <label>Content</label>
        <textarea v-model="content" rows="8" placeholder="Write the announcement content" required></textarea>

        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="cancel">Cancel</button>
          <button type="submit" class="btn-submit">Create</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AssociationNavBar from './AssociationNavBar.vue'
import { getApiBase, getAuthHeader } from '../utils/auth'

const router = useRouter()
const title = ref('')
const content = ref('')
const category = ref('GENERAL')
const API_BASE = getApiBase()

async function submit() {
  if (!title.value.trim() || !content.value.trim()) return alert('Title and content are required')
  try {
    const auth = getAuthHeader()
    if (!auth.Authorization) { router.push('/login'); return }
    const payload = { title: title.value, content: content.value, category: category.value }
    await axios.post(`${API_BASE}/api/notices/`, payload, { headers: auth })
    router.push('/association_manager')
  } catch (err) {
    console.error('Failed to create announcement', err)
    alert('Failed to create announcement')
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
input[type="text"], textarea, select { width:100%; padding:0.75rem 0.9rem; margin-top:0.45rem; border-radius:12px; border:1px solid rgba(129,167,210,0.18); background:#f8fbff;color:black }
.form-actions { display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.25rem }
.btn-cancel { background:white; border:1px solid rgba(129,167,210,0.18); padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:700;color:black }
.btn-submit { background: linear-gradient(90deg,#2b7ef7,#0b63e6); color:white; border:none; padding:0.55rem 0.95rem; border-radius:12px; cursor:pointer; font-weight:800 }

@media (max-width: 768px) {
  .form-card { margin:1rem; padding:1rem }
  input[type="text"], textarea, select { padding:0.6rem }
}
</style>

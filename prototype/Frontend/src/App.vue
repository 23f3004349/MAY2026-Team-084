<script setup>
import { onMounted } from 'vue'
import CelebrationHost from './components/CelebrationHost.vue'

onMounted(() => {
  const saved = localStorage.getItem('se_theme')
  if (saved) document.documentElement.setAttribute('data-theme', saved)
})
</script>

<template>
  <div class="page-container">
    <router-view />
    <CelebrationHost />
  </div>
</template>

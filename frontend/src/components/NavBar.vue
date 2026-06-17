<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <RouterLink to="/dashboard">Segmentation</RouterLink>
    </div>
    <div class="navbar-links">
      <RouterLink to="/dashboard">Dashboard</RouterLink>
      <RouterLink to="/profiles">Profiles</RouterLink>
      <RouterLink to="/tags">Tags</RouterLink>
      <RouterLink to="/rules">Rules</RouterLink>
      <RouterLink to="/results">Results</RouterLink>
    </div>
    <div class="navbar-actions">
      <button class="btn btn-secondary" @click="handleLogout">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  background: #2c3e50;
  color: white;
  gap: 24px;
}

.navbar-brand a {
  color: white;
  text-decoration: none;
  font-size: 18px;
  font-weight: 700;
}

.navbar-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.navbar-links a {
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.navbar-links a:hover,
.navbar-links a.router-link-active {
  color: white;
  background: rgba(255,255,255,0.15);
}
</style>

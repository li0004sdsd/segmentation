import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
  }

  async function register(username, email, password) {
    await api.post('/auth/register/', { username, email, password })
  }

  function logout() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { accessToken, user, isAuthenticated, login, register, logout }
})

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h1>Create Account</h1>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Username</label>
          <input v-model="form.username" type="text" required />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="form.password" type="password" required minlength="6" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <p v-if="success" class="success-msg">{{ success }}</p>
        <button class="btn btn-primary" type="submit" :disabled="loading" style="width:100%">
          {{ loading ? 'Creating...' : 'Create Account' }}
        </button>
      </form>
      <p style="margin-top:16px;text-align:center;font-size:14px">
        Already have an account? <RouterLink to="/login">Sign in</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', email: '', password: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await authStore.register(form.value.username, form.value.email, form.value.password)
    success.value = 'Account created! Redirecting...'
    setTimeout(() => router.push('/login'), 1200)
  } catch (e) {
    const data = e.response?.data
    error.value = data?.username?.[0] || data?.email?.[0] || data?.password?.[0] || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.auth-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  width: 100%;
  max-width: 400px;
}

.auth-card h1 {
  margin-bottom: 28px;
  text-align: center;
  font-size: 22px;
}
</style>

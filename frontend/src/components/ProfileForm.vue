<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2>{{ profile ? 'Edit Profile' : 'New Profile' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" type="text" required />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" required />
        </div>
        <div class="form-group">
          <label>Phone</label>
          <input v-model="form.phone" type="text" />
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="form-group">
            <label>Age</label>
            <input v-model.number="form.age" type="number" min="0" max="150" />
          </div>
          <div class="form-group">
            <label>Gender</label>
            <select v-model="form.gender">
              <option value="">— Select —</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="form-group">
            <label>City</label>
            <input v-model="form.city" type="text" />
          </div>
          <div class="form-group">
            <label>Country</label>
            <input v-model="form.country" type="text" />
          </div>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ profile: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const form = ref({ name: '', email: '', phone: '', age: null, gender: '', city: '', country: '' })
const error = ref('')
const loading = ref(false)

watch(() => props.profile, (p) => {
  if (p) {
    form.value = { name: p.name, email: p.email, phone: p.phone || '', age: p.age, gender: p.gender || '', city: p.city || '', country: p.country || '' }
  } else {
    form.value = { name: '', email: '', phone: '', age: null, gender: '', city: '', country: '' }
  }
}, { immediate: true })

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    emit('saved', { ...form.value })
  } finally {
    loading.value = false
  }
}
</script>

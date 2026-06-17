<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2>{{ tag ? 'Edit Tag' : 'New Tag' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" type="text" required />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" rows="3"></textarea>
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

const props = defineProps({ tag: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const form = ref({ name: '', description: '' })
const error = ref('')
const loading = ref(false)

watch(() => props.tag, (t) => {
  if (t) form.value = { name: t.name, description: t.description }
  else form.value = { name: '', description: '' }
}, { immediate: true })

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    emit('saved', { ...form.value })
  } catch (e) {
    error.value = 'Failed to save'
  } finally {
    loading.value = false
  }
}
</script>

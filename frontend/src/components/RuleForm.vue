<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2>{{ rule ? 'Edit Rule' : 'New Rule' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" type="text" required />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" rows="2"></textarea>
        </div>
        <ConditionBuilder v-model="form.conditions" />
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
import ConditionBuilder from './ConditionBuilder.vue'

const props = defineProps({ rule: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const form = ref({ name: '', description: '', conditions: {} })
const error = ref('')
const loading = ref(false)

watch(() => props.rule, (r) => {
  if (r) form.value = { name: r.name, description: r.description, conditions: { ...r.conditions } }
  else form.value = { name: '', description: '', conditions: {} }
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

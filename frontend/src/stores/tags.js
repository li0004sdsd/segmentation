import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useTagsStore = defineStore('tags', () => {
  const tags = ref([])

  async function fetchAll() {
    const { data } = await api.get('/tags/')
    tags.value = data
  }

  async function create(payload) {
    const { data } = await api.post('/tags/', payload)
    tags.value.unshift(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await api.put(`/tags/${id}/`, payload)
    const idx = tags.value.findIndex(t => t.id === id)
    if (idx !== -1) tags.value[idx] = data
    return data
  }

  async function remove(id) {
    await api.delete(`/tags/${id}/`)
    tags.value = tags.value.filter(t => t.id !== id)
  }

  return { tags, fetchAll, create, update, remove }
})

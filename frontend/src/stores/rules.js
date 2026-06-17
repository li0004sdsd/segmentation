import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useRulesStore = defineStore('rules', () => {
  const rules = ref([])
  const current = ref(null)

  async function fetchAll() {
    const { data } = await api.get('/rules/')
    rules.value = data
  }

  async function fetchOne(id) {
    const { data } = await api.get(`/rules/${id}/`)
    current.value = data
    return data
  }

  async function create(payload) {
    const { data } = await api.post('/rules/', payload)
    rules.value.unshift(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await api.put(`/rules/${id}/`, payload)
    const idx = rules.value.findIndex(r => r.id === id)
    if (idx !== -1) rules.value[idx] = data
    current.value = data
    return data
  }

  async function remove(id) {
    await api.delete(`/rules/${id}/`)
    rules.value = rules.value.filter(r => r.id !== id)
  }

  async function run(id) {
    const { data } = await api.post(`/rules/${id}/run/`)
    return data
  }

  return { rules, current, fetchAll, fetchOne, create, update, remove, run }
})

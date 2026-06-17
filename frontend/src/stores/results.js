import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useResultsStore = defineStore('results', () => {
  const results = ref([])
  const current = ref(null)

  async function fetchAll() {
    const { data } = await api.get('/results/')
    results.value = data
  }

  async function fetchOne(id) {
    const { data } = await api.get(`/results/${id}/`)
    current.value = data
    return data
  }

  return { results, current, fetchAll, fetchOne }
})

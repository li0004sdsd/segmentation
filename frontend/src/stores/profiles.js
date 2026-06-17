import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useProfilesStore = defineStore('profiles', () => {
  const profiles = ref([])
  const current = ref(null)

  async function fetchAll() {
    const { data } = await api.get('/profiles/')
    profiles.value = data
  }

  async function fetchOne(id) {
    const { data } = await api.get(`/profiles/${id}/`)
    current.value = data
    return data
  }

  async function create(payload) {
    const { data } = await api.post('/profiles/', payload)
    profiles.value.unshift(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await api.put(`/profiles/${id}/`, payload)
    const idx = profiles.value.findIndex(p => p.id === id)
    if (idx !== -1) profiles.value[idx] = data
    current.value = data
    return data
  }

  async function remove(id) {
    await api.delete(`/profiles/${id}/`)
    profiles.value = profiles.value.filter(p => p.id !== id)
  }

  async function addTag(profileId, tagId) {
    await api.post(`/profiles/${profileId}/tags/`, { tag_id: tagId })
    await fetchOne(profileId)
  }

  async function removeTag(profileId, tagId) {
    await api.delete(`/profiles/${profileId}/tags/${tagId}/`)
    await fetchOne(profileId)
  }

  return { profiles, current, fetchAll, fetchOne, create, update, remove, addTag, removeTag }
})

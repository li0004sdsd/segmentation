<template>
  <div v-if="profile">
    <div class="page-header">
      <h1>{{ profile.name }}</h1>
      <div style="display:flex;gap:8px">
        <button class="btn btn-secondary" @click="openEdit">Edit</button>
        <RouterLink to="/profiles" class="btn btn-secondary">Back</RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="detail-grid">
        <div class="detail-item"><span class="detail-label">Email</span><span>{{ profile.email }}</span></div>
        <div class="detail-item"><span class="detail-label">Phone</span><span>{{ profile.phone || '—' }}</span></div>
        <div class="detail-item"><span class="detail-label">Age</span><span>{{ profile.age || '—' }}</span></div>
        <div class="detail-item"><span class="detail-label">Gender</span><span>{{ profile.gender || '—' }}</span></div>
        <div class="detail-item"><span class="detail-label">City</span><span>{{ profile.city || '—' }}</span></div>
        <div class="detail-item"><span class="detail-label">Country</span><span>{{ profile.country || '—' }}</span></div>
      </div>
    </div>

    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h2 style="font-size:16px">Tags</h2>
        <div style="display:flex;gap:8px;align-items:center">
          <select v-model="selectedTagId" style="padding:6px 10px;border:1px solid #dce1e7;border-radius:6px;font-size:14px">
            <option value="">Select a tag...</option>
            <option v-for="t in availableTags" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
          <button class="btn btn-primary" :disabled="!selectedTagId" @click="handleAddTag">Add</button>
        </div>
      </div>
      <div>
        <span
          v-for="t in profile.tags"
          :key="t.id"
          class="tag-chip"
          style="cursor:pointer"
          @click="handleRemoveTag(t.id)"
          :title="`Click to remove ${t.name}`"
        >{{ t.name }} ×</span>
        <p v-if="!profile.tags.length" style="color:#999;font-size:14px">No tags assigned.</p>
      </div>
    </div>

    <ProfileForm
      v-if="showEdit"
      :profile="profile"
      @close="showEdit = false"
      @saved="handleSaved"
    />
  </div>
  <div v-else style="padding:40px;text-align:center;color:#999">Loading...</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProfilesStore } from '../stores/profiles.js'
import { useTagsStore } from '../stores/tags.js'
import ProfileForm from '../components/ProfileForm.vue'

const route = useRoute()
const profilesStore = useProfilesStore()
const tagsStore = useTagsStore()

const profile = computed(() => profilesStore.current)
const selectedTagId = ref('')
const showEdit = ref(false)

const availableTags = computed(() => {
  const assigned = new Set(profile.value?.tags.map(t => t.id) || [])
  return tagsStore.tags.filter(t => !assigned.has(t.id))
})

onMounted(async () => {
  await tagsStore.fetchAll()
  await profilesStore.fetchOne(Number(route.params.id))
})

function openEdit() { showEdit.value = true }

async function handleSaved(payload) {
  await profilesStore.update(profile.value.id, payload)
  showEdit.value = false
}

async function handleAddTag() {
  if (!selectedTagId.value) return
  await profilesStore.addTag(profile.value.id, selectedTagId.value)
  selectedTagId.value = ''
}

async function handleRemoveTag(tagId) {
  if (confirm('Remove this tag?')) await profilesStore.removeTag(profile.value.id, tagId)
}
</script>

<style scoped>
.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>

<template>
  <div>
    <div class="page-header">
      <h1>User Profiles</h1>
      <button class="btn btn-primary" @click="openCreate">+ New Profile</button>
    </div>
    <div class="card">
      <table v-if="profilesStore.profiles.length">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Age</th><th>City</th><th>Tags</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in profilesStore.profiles" :key="p.id">
            <td>
              <RouterLink :to="`/profiles/${p.id}`">{{ p.name }}</RouterLink>
            </td>
            <td>{{ p.email }}</td>
            <td>{{ p.age || '—' }}</td>
            <td>{{ p.city || '—' }}</td>
            <td>
              <span v-for="t in p.tags" :key="t.id" class="tag-chip">{{ t.name }}</span>
            </td>
            <td>
              <button class="btn btn-secondary" style="margin-right:8px" @click="openEdit(p)">Edit</button>
              <button class="btn btn-danger" @click="handleDelete(p.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else style="color:#999;font-size:14px">No profiles yet.</p>
    </div>

    <ProfileForm
      v-if="showForm"
      :profile="editingProfile"
      @close="closeForm"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProfilesStore } from '../stores/profiles.js'
import ProfileForm from '../components/ProfileForm.vue'

const profilesStore = useProfilesStore()
const showForm = ref(false)
const editingProfile = ref(null)

onMounted(() => profilesStore.fetchAll())

function openCreate() { editingProfile.value = null; showForm.value = true }
function openEdit(p) { editingProfile.value = p; showForm.value = true }
function closeForm() { showForm.value = false; editingProfile.value = null }

async function handleSaved(payload) {
  if (editingProfile.value) {
    await profilesStore.update(editingProfile.value.id, payload)
  } else {
    await profilesStore.create(payload)
  }
  closeForm()
}

async function handleDelete(id) {
  if (confirm('Delete this profile?')) await profilesStore.remove(id)
}
</script>

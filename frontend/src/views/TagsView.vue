<template>
  <div>
    <div class="page-header">
      <h1>Tags</h1>
      <button class="btn btn-primary" @click="openCreate">+ New Tag</button>
    </div>
    <div class="card">
      <table v-if="tagsStore.tags.length">
        <thead>
          <tr><th>Name</th><th>Description</th><th>Created</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="tag in tagsStore.tags" :key="tag.id">
            <td><span class="tag-chip">{{ tag.name }}</span></td>
            <td>{{ tag.description || '—' }}</td>
            <td>{{ new Date(tag.created_at).toLocaleDateString() }}</td>
            <td>
              <button class="btn btn-secondary" style="margin-right:8px" @click="openEdit(tag)">Edit</button>
              <button class="btn btn-danger" @click="handleDelete(tag.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else style="color:#999;font-size:14px">No tags yet.</p>
    </div>

    <TagForm
      v-if="showForm"
      :tag="editingTag"
      @close="closeForm"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTagsStore } from '../stores/tags.js'
import TagForm from '../components/TagForm.vue'

const tagsStore = useTagsStore()
const showForm = ref(false)
const editingTag = ref(null)

onMounted(() => tagsStore.fetchAll())

function openCreate() {
  editingTag.value = null
  showForm.value = true
}

function openEdit(tag) {
  editingTag.value = tag
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingTag.value = null
}

async function handleSaved(payload) {
  if (editingTag.value) {
    await tagsStore.update(editingTag.value.id, payload)
  } else {
    await tagsStore.create(payload)
  }
  closeForm()
}

async function handleDelete(id) {
  if (confirm('Delete this tag?')) {
    await tagsStore.remove(id)
  }
}
</script>

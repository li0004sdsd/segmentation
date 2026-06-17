<template>
  <div>
    <div class="page-header">
      <h1>Segmentation Rules</h1>
      <button class="btn btn-primary" @click="openCreate">+ New Rule</button>
    </div>
    <div class="card">
      <table v-if="rulesStore.rules.length">
        <thead>
          <tr><th>Name</th><th>Description</th><th>Created</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in rulesStore.rules" :key="r.id">
            <td><RouterLink :to="`/rules/${r.id}`">{{ r.name }}</RouterLink></td>
            <td>{{ r.description || '—' }}</td>
            <td>{{ new Date(r.created_at).toLocaleDateString() }}</td>
            <td style="display:flex;gap:6px;flex-wrap:wrap">
              <button class="btn btn-success" @click="handleRun(r.id)">Run</button>
              <button class="btn btn-secondary" @click="openEdit(r)">Edit</button>
              <button class="btn btn-danger" @click="handleDelete(r.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else style="color:#999;font-size:14px">No rules yet.</p>
    </div>

    <RuleForm
      v-if="showForm"
      :rule="editingRule"
      @close="closeForm"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRulesStore } from '../stores/rules.js'
import { useTagsStore } from '../stores/tags.js'
import RuleForm from '../components/RuleForm.vue'

const router = useRouter()
const rulesStore = useRulesStore()
const tagsStore = useTagsStore()
const showForm = ref(false)
const editingRule = ref(null)

onMounted(async () => {
  await Promise.all([rulesStore.fetchAll(), tagsStore.fetchAll()])
})

function openCreate() { editingRule.value = null; showForm.value = true }
function openEdit(r) { editingRule.value = r; showForm.value = true }
function closeForm() { showForm.value = false; editingRule.value = null }

async function handleSaved(payload) {
  if (editingRule.value) await rulesStore.update(editingRule.value.id, payload)
  else await rulesStore.create(payload)
  closeForm()
}

async function handleDelete(id) {
  if (confirm('Delete this rule?')) await rulesStore.remove(id)
}

async function handleRun(id) {
  const result = await rulesStore.run(id)
  router.push(`/results/${result.id}`)
}
</script>

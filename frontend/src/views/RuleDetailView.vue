<template>
  <div v-if="rule">
    <div class="page-header">
      <h1>{{ rule.name }}</h1>
      <div style="display:flex;gap:8px">
        <button class="btn btn-success" @click="handleRun">Run Segmentation</button>
        <button class="btn btn-secondary" @click="openEdit">Edit</button>
        <RouterLink to="/rules" class="btn btn-secondary">Back</RouterLink>
      </div>
    </div>

    <div class="card">
      <p style="color:#7f8c8d;margin-bottom:20px">{{ rule.description || 'No description.' }}</p>
      <h3 style="font-size:14px;font-weight:600;margin-bottom:12px">Conditions</h3>
      <div class="condition-list">
        <div v-if="rule.conditions.age_min !== undefined" class="condition-item">
          <span class="condition-key">Min Age</span>
          <span class="condition-val">{{ rule.conditions.age_min }}</span>
        </div>
        <div v-if="rule.conditions.age_max !== undefined" class="condition-item">
          <span class="condition-key">Max Age</span>
          <span class="condition-val">{{ rule.conditions.age_max }}</span>
        </div>
        <div v-if="rule.conditions.gender" class="condition-item">
          <span class="condition-key">Gender</span>
          <span class="condition-val">{{ rule.conditions.gender }}</span>
        </div>
        <div v-if="rule.conditions.city" class="condition-item">
          <span class="condition-key">City</span>
          <span class="condition-val">{{ rule.conditions.city }}</span>
        </div>
        <div v-if="rule.conditions.country" class="condition-item">
          <span class="condition-key">Country</span>
          <span class="condition-val">{{ rule.conditions.country }}</span>
        </div>
        <div v-if="rule.conditions.tags?.length" class="condition-item">
          <span class="condition-key">Tags</span>
          <span class="condition-val">IDs: {{ rule.conditions.tags.join(', ') }}</span>
        </div>
        <p v-if="!hasConditions" style="color:#999;font-size:14px">No conditions set — will match all profiles.</p>
      </div>
    </div>

    <div class="card" v-if="recentResults.length">
      <h2 style="font-size:16px;margin-bottom:16px">Recent Runs</h2>
      <table>
        <thead><tr><th>Matched</th><th>Ran At</th><th></th></tr></thead>
        <tbody>
          <tr v-for="r in recentResults" :key="r.id">
            <td>{{ r.matched_count }}</td>
            <td>{{ new Date(r.ran_at).toLocaleString() }}</td>
            <td><RouterLink :to="`/results/${r.id}`">View</RouterLink></td>
          </tr>
        </tbody>
      </table>
    </div>

    <RuleForm v-if="showEdit" :rule="rule" @close="showEdit = false" @saved="handleSaved" />
  </div>
  <div v-else style="padding:40px;text-align:center;color:#999">Loading...</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRulesStore } from '../stores/rules.js'
import { useTagsStore } from '../stores/tags.js'
import { useResultsStore } from '../stores/results.js'
import RuleForm from '../components/RuleForm.vue'

const route = useRoute()
const router = useRouter()
const rulesStore = useRulesStore()
const tagsStore = useTagsStore()
const resultsStore = useResultsStore()

const rule = computed(() => rulesStore.current)
const showEdit = ref(false)

const recentResults = computed(() =>
  resultsStore.results.filter(r => r.rule?.id === Number(route.params.id)).slice(0, 5)
)

const hasConditions = computed(() => {
  if (!rule.value) return false
  const c = rule.value.conditions
  return Object.keys(c).some(k => c[k] !== undefined && c[k] !== null && (Array.isArray(c[k]) ? c[k].length > 0 : c[k] !== ''))
})

onMounted(async () => {
  await Promise.all([
    tagsStore.fetchAll(),
    rulesStore.fetchOne(Number(route.params.id)),
    resultsStore.fetchAll(),
  ])
})

async function handleSaved(payload) {
  await rulesStore.update(rule.value.id, payload)
  showEdit.value = false
}

async function handleRun() {
  const result = await rulesStore.run(rule.value.id)
  router.push(`/results/${result.id}`)
}

function openEdit() { showEdit.value = true }
</script>

<style scoped>
.condition-list { display: flex; flex-direction: column; gap: 10px; }
.condition-item { display: flex; gap: 12px; align-items: center; }
.condition-key {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  min-width: 100px;
}
.condition-val { font-size: 14px; color: #2c3e50; }
</style>

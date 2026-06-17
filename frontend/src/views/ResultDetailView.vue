<template>
  <div v-if="result">
    <div class="page-header">
      <h1>Result: {{ result.rule?.name }}</h1>
      <RouterLink to="/results" class="btn btn-secondary">Back</RouterLink>
    </div>

    <div class="card">
      <div class="result-meta">
        <div class="meta-item">
          <span class="meta-label">Rule</span>
          <RouterLink :to="`/rules/${result.rule?.id}`">{{ result.rule?.name }}</RouterLink>
        </div>
        <div class="meta-item">
          <span class="meta-label">Matched Users</span>
          <span class="meta-big">{{ result.matched_count }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Ran At</span>
          <span>{{ new Date(result.ran_at).toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 style="font-size:16px;margin-bottom:16px">Matched Profiles ({{ result.matched_profiles?.length }})</h2>
      <table v-if="result.matched_profiles?.length">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Age</th><th>Gender</th><th>City</th><th>Country</th><th>Tags</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in result.matched_profiles" :key="p.id">
            <td><RouterLink :to="`/profiles/${p.id}`">{{ p.name }}</RouterLink></td>
            <td>{{ p.email }}</td>
            <td>{{ p.age || '—' }}</td>
            <td>{{ p.gender || '—' }}</td>
            <td>{{ p.city || '—' }}</td>
            <td>{{ p.country || '—' }}</td>
            <td>
              <span v-for="t in p.tags" :key="t.id" class="tag-chip">{{ t.name }}</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else style="color:#999;font-size:14px">No users matched this rule.</p>
    </div>
  </div>
  <div v-else style="padding:40px;text-align:center;color:#999">Loading...</div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useResultsStore } from '../stores/results.js'

const route = useRoute()
const resultsStore = useResultsStore()

const result = computed(() => resultsStore.current)

onMounted(() => resultsStore.fetchOne(Number(route.params.id)))
</script>

<style scoped>
.result-meta {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-big {
  font-size: 32px;
  font-weight: 700;
  color: #3498db;
}
</style>

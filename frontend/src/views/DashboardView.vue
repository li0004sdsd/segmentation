<template>
  <div>
    <div class="page-header">
      <h1>Dashboard</h1>
    </div>
    <div class="stats-grid">
      <div class="card stat-card">
        <div class="stat-number">{{ profilesStore.profiles.length }}</div>
        <div class="stat-label">User Profiles</div>
        <RouterLink to="/profiles" class="stat-link">View all</RouterLink>
      </div>
      <div class="card stat-card">
        <div class="stat-number">{{ tagsStore.tags.length }}</div>
        <div class="stat-label">Tags</div>
        <RouterLink to="/tags" class="stat-link">View all</RouterLink>
      </div>
      <div class="card stat-card">
        <div class="stat-number">{{ rulesStore.rules.length }}</div>
        <div class="stat-label">Segmentation Rules</div>
        <RouterLink to="/rules" class="stat-link">View all</RouterLink>
      </div>
      <div class="card stat-card">
        <div class="stat-number">{{ resultsStore.results.length }}</div>
        <div class="stat-label">Analysis Results</div>
        <RouterLink to="/results" class="stat-link">View all</RouterLink>
      </div>
    </div>
    <div class="card" style="margin-top:24px">
      <h2 style="margin-bottom:16px;font-size:16px">Recent Results</h2>
      <table v-if="resultsStore.results.length">
        <thead>
          <tr><th>Rule</th><th>Matched</th><th>Ran At</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="r in resultsStore.results.slice(0,5)" :key="r.id">
            <td>{{ r.rule?.name }}</td>
            <td>{{ r.matched_count }}</td>
            <td>{{ new Date(r.ran_at).toLocaleString() }}</td>
            <td><RouterLink :to="`/results/${r.id}`">View</RouterLink></td>
          </tr>
        </tbody>
      </table>
      <p v-else style="color:#999;font-size:14px">No results yet. Run a segmentation rule to get started.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useProfilesStore } from '../stores/profiles.js'
import { useTagsStore } from '../stores/tags.js'
import { useRulesStore } from '../stores/rules.js'
import { useResultsStore } from '../stores/results.js'

const profilesStore = useProfilesStore()
const tagsStore = useTagsStore()
const rulesStore = useRulesStore()
const resultsStore = useResultsStore()

onMounted(async () => {
  await Promise.all([
    profilesStore.fetchAll(),
    tagsStore.fetchAll(),
    rulesStore.fetchAll(),
    resultsStore.fetchAll(),
  ])
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 40px;
  font-weight: 700;
  color: #3498db;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
  margin: 4px 0 12px;
}

.stat-link {
  font-size: 13px;
  color: #3498db;
  text-decoration: none;
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>

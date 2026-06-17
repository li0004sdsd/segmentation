<template>
  <div>
    <div class="page-header">
      <h1>Segmentation Results</h1>
    </div>
    <div class="card">
      <table v-if="resultsStore.results.length">
        <thead>
          <tr><th>Rule</th><th>Matched Users</th><th>Ran At</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in resultsStore.results" :key="r.id">
            <td>
              <RouterLink :to="`/rules/${r.rule?.id}`">{{ r.rule?.name }}</RouterLink>
            </td>
            <td>{{ r.matched_count }}</td>
            <td>{{ new Date(r.ran_at).toLocaleString() }}</td>
            <td>
              <RouterLink :to="`/results/${r.id}`" class="btn btn-secondary">View</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else style="color:#999;font-size:14px">No results yet. Run a rule from the Rules page.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useResultsStore } from '../stores/results.js'

const resultsStore = useResultsStore()

onMounted(() => resultsStore.fetchAll())
</script>

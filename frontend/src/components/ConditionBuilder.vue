<template>
  <div class="condition-builder">
    <h3 style="font-size:14px;font-weight:600;margin-bottom:12px">Conditions</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label>Min Age</label>
        <input type="number" min="0" :value="local.age_min ?? ''" @input="set('age_min', $event.target.value ? +$event.target.value : undefined)" />
      </div>
      <div class="form-group">
        <label>Max Age</label>
        <input type="number" min="0" :value="local.age_max ?? ''" @input="set('age_max', $event.target.value ? +$event.target.value : undefined)" />
      </div>
      <div class="form-group">
        <label>Gender</label>
        <select :value="local.gender ?? ''" @change="set('gender', $event.target.value || undefined)">
          <option value="">Any</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      </div>
      <div class="form-group">
        <label>City (contains)</label>
        <input type="text" :value="local.city ?? ''" @input="set('city', $event.target.value || undefined)" />
      </div>
      <div class="form-group">
        <label>Country (contains)</label>
        <input type="text" :value="local.country ?? ''" @input="set('country', $event.target.value || undefined)" />
      </div>
    </div>
    <div class="form-group" style="margin-top:8px">
      <label>Required Tags (profiles must have ALL selected)</label>
      <div class="tag-select-grid">
        <label
          v-for="tag in allTags"
          :key="tag.id"
          class="tag-checkbox"
          :class="{ active: selectedTagIds.has(tag.id) }"
        >
          <input
            type="checkbox"
            :checked="selectedTagIds.has(tag.id)"
            @change="toggleTag(tag.id)"
          />
          {{ tag.name }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTagsStore } from '../stores/tags.js'

const props = defineProps({ modelValue: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:modelValue'])

const tagsStore = useTagsStore()
const allTags = computed(() => tagsStore.tags)

const local = ref({ ...props.modelValue })

watch(() => props.modelValue, (v) => { local.value = { ...v } }, { deep: true })

const selectedTagIds = computed(() => new Set(local.value.tags || []))

function set(key, value) {
  if (value === undefined) {
    const copy = { ...local.value }
    delete copy[key]
    local.value = copy
  } else {
    local.value = { ...local.value, [key]: value }
  }
  emit('update:modelValue', { ...local.value })
}

function toggleTag(id) {
  const current = new Set(local.value.tags || [])
  if (current.has(id)) current.delete(id)
  else current.add(id)
  const tags = [...current]
  if (tags.length === 0) {
    set('tags', undefined)
  } else {
    set('tags', tags)
  }
}
</script>

<style scoped>
.tag-select-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border: 1px solid #dce1e7;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.tag-checkbox.active {
  background: #e8f4fd;
  border-color: #3498db;
  color: #2980b9;
}

.tag-checkbox input {
  display: none;
}
</style>

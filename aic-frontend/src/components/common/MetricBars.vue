<script setup>
import { computed } from 'vue'

const props = defineProps({
  pi: { type: Number, default: null },
  ui: { type: Number, default: null },
  oi: { type: Number, default: null },
  topic: { type: Number, default: null },
  compareValues: { type: Object, default: null },
})

const items = computed(() => [
  { key: 'pi', label: 'PI', color: 'var(--color-pi)', value: props.pi, compare: props.compareValues?.pi },
  { key: 'ui', label: 'UI', color: 'var(--color-ui)', value: props.ui, compare: props.compareValues?.ui },
  { key: 'oi', label: 'OI', color: 'var(--color-oi)', value: props.oi, compare: props.compareValues?.oi },
  { key: 'topic', label: 'Topic', color: 'var(--color-topic)', value: props.topic, compare: props.compareValues?.topic },
])
</script>

<template>
  <div class="metric-bars">
    <div v-for="item in items" :key="item.key" class="metric-bar-row">
      <div class="metric-bar-label">
        <span class="metric-dot" :style="{ background: item.color }"></span>
        {{ item.label }}
      </div>
      <div class="metric-bar-track">
        <div class="metric-bar-fill" :style="{ width: (item.value || 0) + '%', background: item.color }"></div>
        <div
          v-if="compareValues && item.compare != null"
          class="metric-bar-compare"
          :style="{ left: item.compare + '%' }"
        ></div>
      </div>
      <div class="metric-bar-score">{{ item.value ?? '-' }}</div>
    </div>
  </div>
</template>

<style scoped>
.metric-bars {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.metric-bar-row {
  display: grid;
  grid-template-columns: 80px 1fr 40px;
  align-items: center;
  gap: 0.5rem;
}

.metric-bar-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  font-weight: 500;
}

.metric-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.metric-bar-track {
  position: relative;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.metric-bar-compare {
  position: absolute;
  top: -4px;
  width: 2px;
  height: 16px;
  background: #374151;
  border-radius: 1px;
  transform: translateX(-50%);
}

.metric-bar-score {
  font-size: var(--text-sm);
  font-weight: 600;
  text-align: right;
  color: var(--text-primary);
}
</style>

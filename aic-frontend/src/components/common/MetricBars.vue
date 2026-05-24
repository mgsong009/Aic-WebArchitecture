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
  <div class="score-bar-group">
    <div v-for="item in items" :key="item.key" class="score-bar-item">
      <div class="score-bar-label" :style="{ color: item.color }">
        {{ item.label }}
      </div>
      <div class="score-bar-track">
        <div class="score-bar-fill" :style="{ width: (item.value || 0) + '%', background: item.color }"></div>
        <div
          v-if="compareValues && item.compare != null"
          class="score-bar-compare"
          :style="{ left: item.compare + '%' }"
        ></div>
      </div>
      <div class="score-bar-value">{{ item.value ?? '-' }}</div>
    </div>
  </div>
</template>

<style scoped>
.score-bar-track {
  position: relative;
}
.score-bar-compare {
  position: absolute;
  top: -4px;
  width: 2px;
  height: 16px;
  background: var(--color-gray-700);
  border-radius: 1px;
  transform: translateX(-50%);
}
</style>

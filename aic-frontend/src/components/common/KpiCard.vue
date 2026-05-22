<script setup>
defineProps({
  label: String,
  value: { type: [Number, String], default: null },
  delta: { type: Number, default: null },
  color: { type: String, default: 'var(--color-aic)' },
  unit: { type: String, default: '' },
})
</script>

<template>
  <div class="kpi-card" :style="{ '--card-color': color }">
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">
      {{ value !== null ? value : '—' }}<span v-if="unit" class="kpi-unit">{{ unit }}</span>
    </div>
    <div v-if="delta !== null" class="kpi-delta" :class="delta >= 0 ? 'delta-up' : 'delta-down'">
      {{ delta >= 0 ? '↑' : '↓' }} {{ Math.abs(delta) }}
    </div>
  </div>
</template>

<style scoped>
.kpi-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  border-top: 3px solid var(--card-color);
  box-shadow: var(--shadow-sm);
}
.kpi-label { font-size: var(--text-xs); color: var(--text-secondary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: var(--text-3xl); font-weight: 700; color: var(--text-primary); margin-top: 0.25rem; }
.kpi-unit { font-size: var(--text-sm); font-weight: 400; margin-left: 2px; }
.kpi-delta { font-size: var(--text-sm); margin-top: 0.25rem; font-weight: 500; }
.delta-up { color: var(--color-oi); }
.delta-down { color: #ef4444; }
</style>

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
    <div class="kpi-header">
      <div class="kpi-icon" :style="{ background: `${color}18`, color }">●</div>
      <div v-if="delta !== null" class="kpi-change" :class="delta >= 0 ? 'up' : 'down'">
        {{ delta >= 0 ? '↑' : '↓' }} {{ Math.abs(delta) }}
      </div>
    </div>
    <div class="kpi-value">
      {{ value !== null ? value : '-' }}<span v-if="unit" class="kpi-unit">{{ unit }}</span>
    </div>
    <div class="kpi-label">{{ label }}</div>
  </div>
</template>

<style scoped>
.kpi-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: var(--bg-surface);
  transition: box-shadow var(--transition-base), transform var(--transition-fast);
}
.kpi-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.kpi-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: var(--card-color);
}
.kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  font-size: 9px;
}
.kpi-unit { font-size: var(--text-sm); font-weight: 500; margin-left: 2px; color: var(--text-muted); }
</style>

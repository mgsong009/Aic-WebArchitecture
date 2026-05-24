<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  subText: { type: String, default: '' },
  status: { type: String, default: 'neutral' }, // success | warning | danger | neutral
})
</script>

<template>
  <div class="kpi-card" :class="`kpi-card--${status}`">
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">{{ value }}</div>
    <div v-if="subText" class="kpi-sub">{{ subText }}</div>
  </div>
</template>

<style scoped>
.kpi-card {
  padding: var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  border-left: 3px solid var(--border-default);
}

.kpi-card--success { border-left-color: var(--color-success); }
.kpi-card--warning { border-left-color: var(--color-warning); }
.kpi-card--danger  { border-left-color: var(--color-danger); }
.kpi-card--neutral { border-left-color: var(--color-aic); }

.kpi-label {
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
}

.kpi-value {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
}

.kpi-card--success .kpi-value { color: var(--color-success); }
.kpi-card--warning .kpi-value { color: var(--color-warning); }
.kpi-card--danger  .kpi-value { color: var(--color-danger); }

.kpi-sub {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
</style>

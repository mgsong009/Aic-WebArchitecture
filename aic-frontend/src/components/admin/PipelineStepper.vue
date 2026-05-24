<script setup>
defineProps({
  steps: { type: Array, required: true },
})

function iconFor(status) {
  if (status === 'success') return '✓'
  if (status === 'warning') return '!'
  if (status === 'failed')  return '✕'
  return '○'
}
</script>

<template>
  <div class="stepper-card">
    <div class="card-title">Pipeline Stepper</div>
    <div class="stepper">
      <template v-for="(step, i) in steps" :key="step.name">
        <div class="step" :class="`step--${step.status}`">
          <div class="step-icon">{{ iconFor(step.status) }}</div>
          <div class="step-name">{{ step.name }}</div>
          <div class="step-time">{{ step.seconds }}s</div>
        </div>
        <div v-if="i < steps.length - 1" class="step-connector" />
      </template>
    </div>
    <div v-if="steps.some(s => s.status === 'warning')" class="warning-note">
      <span class="warn-icon">!</span>
      rating 보유율이 70% 미만이므로 검증 해석에 주의가 필요합니다.
    </div>
  </div>
</template>

<style scoped>
.stepper-card {
  padding: var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
}

.stepper {
  display: flex;
  align-items: flex-start;
  gap: 0;
  overflow-x: auto;
  padding-bottom: var(--space-2);
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  min-width: 80px;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: var(--font-size-sm);
  border: 2px solid transparent;
}

.step--success .step-icon { background: #d1fae5; color: #065f46; border-color: var(--color-success); }
.step--warning .step-icon { background: #fef3c7; color: #92400e; border-color: var(--color-warning); }
.step--failed  .step-icon { background: #fee2e2; color: #991b1b; border-color: var(--color-danger); }
.step--pending .step-icon { background: var(--color-gray-100); color: var(--text-muted); border-color: var(--border-default); }

.step-name {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-secondary);
  text-align: center;
}

.step-time {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.step-connector {
  flex: 1;
  height: 2px;
  background: var(--border-light);
  margin-top: 15px;
  min-width: 20px;
}

.warning-note {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: #fef3c7;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: #92400e;
}

.warn-icon {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-full);
  background: #f59e0b;
  color: white;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 11px;
  flex-shrink: 0;
}
</style>

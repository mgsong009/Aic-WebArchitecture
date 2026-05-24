<script setup>
defineProps({
  readiness: { type: Object, required: true },
})

const statusMap = {
  ready:   { label: 'Ready',   cls: 'status-ready',   bg: '#d1fae5', color: '#065f46' },
  caution: { label: 'Caution', cls: 'status-caution', bg: '#fef3c7', color: '#92400e' },
  blocked: { label: 'Blocked', cls: 'status-blocked', bg: '#fee2e2', color: '#991b1b' },
}
</script>

<template>
  <div class="card" :class="statusMap[readiness.status]?.cls">
    <div class="card-header">
      <span class="card-title">Service Readiness</span>
      <span
        class="status-badge"
        :style="{ background: statusMap[readiness.status]?.bg, color: statusMap[readiness.status]?.color }"
      >
        {{ statusMap[readiness.status]?.label }}
      </span>
    </div>

    <p class="reason">{{ readiness.reason }}</p>

    <div class="actions">
      <div class="actions-label">권장 조치</div>
      <ol class="actions-list">
        <li v-for="(action, i) in readiness.actions" :key="i">{{ action }}</li>
      </ol>
    </div>

    <div class="criteria">
      <div class="criteria-label">상태 기준</div>
      <div class="criteria-row"><span class="dot dot-ok" /> Ready: 성공률 ≥98%, rating ≥70%, fallback 없음</div>
      <div class="criteria-row"><span class="dot dot-warn" /> Caution: 분석 완료, 일부 데이터 품질 미달</div>
      <div class="criteria-row"><span class="dot dot-danger" /> Blocked: 분석 실패 또는 필수 컬럼 누락</div>
    </div>
  </div>
</template>

<style scoped>
.card {
  padding: var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.status-caution { border-top: 3px solid var(--color-warning); }
.status-ready   { border-top: 3px solid var(--color-success); }
.status-blocked { border-top: 3px solid var(--color-danger); }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
}

.status-badge {
  font-size: var(--font-size-xs);
  font-weight: 800;
  padding: 3px 10px;
  border-radius: var(--radius-full);
}

.reason {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.actions-label,
.criteria-label {
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.actions-list {
  padding-left: var(--space-5);
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.actions-list li {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.criteria {
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
}

.criteria-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-bottom: var(--space-1);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.dot-ok     { background: var(--color-success); }
.dot-warn   { background: var(--color-warning); }
.dot-danger { background: var(--color-danger); }
</style>

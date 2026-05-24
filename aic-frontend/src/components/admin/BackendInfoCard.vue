<script setup>
defineProps({
  backend: { type: Object, required: true },
})

function fallbackColor(val) {
  if (val === 'None') return 'badge-ok'
  if (val === 'TF-IDF') return 'badge-warn'
  return 'badge-danger'
}
</script>

<template>
  <div class="card">
    <div class="card-title">System / Backend Info</div>

    <div class="info-rows">
      <div class="info-row">
        <span class="info-key">Embedding Backend</span>
        <span class="info-val">{{ backend.embeddingBackend }}</span>
      </div>
      <div class="info-row">
        <span class="info-key">Model</span>
        <span class="info-val model-name">{{ backend.model }}</span>
      </div>
      <div class="info-row">
        <span class="info-key">Fallback</span>
        <span class="badge" :class="fallbackColor(backend.fallback)">{{ backend.fallback }}</span>
      </div>
      <div class="info-row">
        <span class="info-key">Metric Version</span>
        <span class="info-val">{{ backend.metricVersion }}</span>
      </div>
      <div class="info-row">
        <span class="info-key">Pipeline Version</span>
        <span class="info-val">{{ backend.pipelineVersion }}</span>
      </div>
      <div class="info-row">
        <span class="info-key">Config Hash</span>
        <code class="info-code">{{ backend.configHash }}</code>
      </div>
      <div class="info-row">
        <span class="info-key">Created At</span>
        <span class="info-val">{{ backend.createdAt }}</span>
      </div>
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

.card-title {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
}

.info-rows {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
}

.info-key  { color: var(--text-muted); font-weight: 600; }
.info-val  { color: var(--text-primary); font-weight: 600; text-align: right; }
.model-name { font-size: var(--font-size-xs); color: var(--text-secondary); }

.info-code {
  font-family: monospace;
  font-size: var(--font-size-xs);
  background: var(--color-gray-100);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.badge {
  font-size: var(--font-size-xs);
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.badge-ok     { background: #d1fae5; color: #065f46; }
.badge-warn   { background: #fef3c7; color: #92400e; }
.badge-danger { background: #fee2e2; color: #991b1b; }
</style>

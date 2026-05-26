<script setup>
import { computed } from 'vue'
import BarChart from '@/components/charts/BarChart.vue'

const props = defineProps({
  steps: { type: Array, required: true },
})

const hasSteps = computed(() => props.steps.length > 0)
const total = computed(() => props.steps.reduce((s, st) => s + st.seconds, 0))
const dominantStep = computed(() => {
  if (!hasSteps.value) return null
  return props.steps.reduce((a, b) => (a.seconds > b.seconds ? a : b))
})

const chartConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: props.steps.map(s => s.name),
    datasets: [{
      label: '처리시간 (초)',
      data: props.steps.map(s => s.seconds),
      backgroundColor: props.steps.map(s =>
        s.status === 'warning' ? 'rgba(245,158,11,0.7)' :
        s.status === 'failed'  ? 'rgba(239,68,68,0.7)' :
        'rgba(59,130,246,0.7)'
      ),
      borderRadius: 4,
    }],
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ` ${ctx.raw}s`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(0,0,0,0.05)' },
        ticks: { font: { size: 11 }, callback: v => `${v}s` },
      },
      y: {
        grid: { display: false },
        ticks: { font: { size: 11 } },
      },
    },
  },
}))
</script>

<template>
  <div class="chart-card">
    <div class="card-title">Runtime Breakdown</div>
    <div v-if="hasSteps" class="chart-wrap">
      <BarChart :config="chartConfig" />
    </div>
    <div v-else class="empty-note">단계별 runtime metadata가 아직 없습니다.</div>
    <div v-if="dominantStep" class="insight">
      <span class="insight-icon">i</span>
      <span>
        <strong>{{ dominantStep.name }}</strong> 단계가 전체 처리시간의
        <strong>{{ ((dominantStep.seconds / total) * 100).toFixed(1) }}%</strong>를 차지합니다.
        대용량 분석 시 비동기 처리 또는 배치 처리 최적화가 필요합니다.
      </span>
    </div>
  </div>
</template>

<style scoped>
.chart-card {
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

.chart-wrap {
  height: 220px;
  position: relative;
}

.empty-note {
  min-height: 220px;
  display: grid;
  place-items: center;
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

.insight {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--color-pi-pale);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}

.insight-icon { flex-shrink: 0; }
</style>

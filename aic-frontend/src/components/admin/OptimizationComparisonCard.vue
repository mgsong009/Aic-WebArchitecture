<script setup>
import { computed } from 'vue'
import BarChart from '@/components/charts/BarChart.vue'

const props = defineProps({
  comparison: { type: Object, required: true },
})

const performanceRows = computed(() => props.comparison.performanceRows || [])
const scoreRows = computed(() => props.comparison.scoreRows || [])

const statusLabel = computed(() => {
  if (props.comparison.qualityPassed === false) return '회귀 확인 필요'
  if (props.comparison.qualityPassed === true) return '허용 오차 통과'
  return '기준 데이터 필요'
})

const statusClass = computed(() => {
  if (props.comparison.qualityPassed === false) return 'badge-danger'
  if (props.comparison.qualityPassed === true) return 'badge-success'
  return 'badge-warning'
})

const chartConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: performanceRows.value.map((row) => row.label),
    datasets: [
      {
        label: 'Before',
        data: performanceRows.value.map((row) => row.baseline),
        backgroundColor: 'rgba(107, 114, 128, 0.7)',
        borderRadius: 4,
      },
      {
        label: 'After',
        data: performanceRows.value.map((row) => row.optimized),
        backgroundColor: 'rgba(16, 185, 129, 0.75)',
        borderRadius: 4,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const row = performanceRows.value[ctx.dataIndex]
            return ` ${ctx.dataset.label}: ${formatValue(ctx.raw, row?.unit)}`
          },
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 11 } } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
    },
  },
}))

function formatValue(value, unit = '') {
  if (value === null || value === undefined) return '-'
  const number = Number(value)
  const formatted = Number.isFinite(number) ? number.toLocaleString(undefined, { maximumFractionDigits: 3 }) : value
  return unit ? `${formatted} ${unit}` : formatted
}

function formatDelta(value) {
  if (value === null || value === undefined) return '-'
  const number = Number(value)
  if (!Number.isFinite(number)) return '-'
  return `${number > 0 ? '+' : ''}${number.toFixed(1)}%`
}

function deltaClass(row) {
  if (row.deltaPct === null || row.deltaPct === undefined) return 'delta-neutral'
  const improved = row.betterDirection === 'up' ? row.deltaPct >= 0 : row.deltaPct <= 0
  return improved ? 'delta-good' : 'delta-bad'
}

function scoreClass(row) {
  if (row.passed === null || row.passed === undefined) return 'badge-warning'
  return row.passed ? 'badge-success' : 'badge-danger'
}
</script>

<template>
  <section class="comparison-card">
    <div class="comparison-header">
      <div>
        <h2 class="comparison-title">Optimization Comparison</h2>
        <p class="comparison-subtitle">
          {{ comparison.baselineVersion || 'baseline' }} → {{ comparison.optimizedVersion || 'optimized' }}
        </p>
      </div>
      <span class="badge" :class="statusClass">{{ statusLabel }}</span>
    </div>

    <div class="comparison-grid">
      <div class="metric-card" v-for="row in performanceRows" :key="row.key">
        <div class="metric-label">{{ row.label }}</div>
        <div class="metric-values">
          <span>{{ formatValue(row.baseline, row.unit) }}</span>
          <span class="arrow">→</span>
          <strong>{{ formatValue(row.optimized, row.unit) }}</strong>
        </div>
        <div class="metric-delta" :class="deltaClass(row)">{{ formatDelta(row.deltaPct) }}</div>
      </div>
    </div>

    <div class="comparison-body">
      <div class="chart-panel">
        <div class="panel-title">Before / After Performance</div>
        <div class="chart-wrap">
          <BarChart :config="chartConfig" />
        </div>
      </div>

      <div class="score-panel">
        <div class="panel-title">Quality Score Delta</div>
        <div class="score-table-wrap">
          <table class="score-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Before</th>
                <th>After</th>
                <th>Delta</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in scoreRows" :key="row.key">
                <td class="score-name">{{ row.label }}</td>
                <td>{{ formatValue(row.baseline) }}</td>
                <td>{{ formatValue(row.optimized) }}</td>
                <td>{{ formatValue(row.delta) }}</td>
                <td>
                  <span class="badge" :class="scoreClass(row)">
                    {{ row.passed === null ? '미측정' : row.passed ? '통과' : '초과' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="tolerance-note">
          허용 오차: ±{{ comparison.scoreTolerance }}. 원문 텍스트나 개인정보 없이 집계 지표만 저장합니다.
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.comparison-card {
  padding: var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.comparison-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.comparison-title,
.panel-title {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
}

.comparison-subtitle {
  margin-top: var(--space-1);
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.metric-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  background: var(--color-gray-50);
  min-width: 0;
}

.metric-label {
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.metric-values {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.metric-values strong {
  color: var(--text-primary);
}

.arrow {
  color: var(--text-muted);
}

.metric-delta {
  margin-top: var(--space-2);
  font-size: var(--font-size-xl);
  font-weight: 800;
}

.delta-good { color: var(--color-success); }
.delta-bad { color: var(--color-danger); }
.delta-neutral { color: var(--text-muted); }

.comparison-body {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: var(--space-4);
}

.chart-panel,
.score-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.chart-wrap {
  height: 260px;
  position: relative;
}

.score-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
}

.score-table {
  width: 100%;
  min-width: 520px;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.score-table th,
.score-table td {
  padding: var(--space-3);
  border-bottom: 1px solid var(--border-light);
  text-align: left;
  white-space: nowrap;
}

.score-table th {
  background: var(--color-gray-50);
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-transform: uppercase;
}

.score-table tr:last-child td {
  border-bottom: 0;
}

.score-name {
  font-weight: 800;
  color: var(--text-primary);
}

.tolerance-note {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  line-height: 1.5;
}

@media (max-width: 900px) {
  .comparison-grid,
  .comparison-body {
    grid-template-columns: 1fr;
  }
}
</style>

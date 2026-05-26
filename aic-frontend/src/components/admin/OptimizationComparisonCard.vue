<script setup>
import { computed } from 'vue'
import BarChart from '@/components/charts/BarChart.vue'

const props = defineProps({
  comparison: { type: Object, required: true },
})

const SCORE_KEYS = ['pi', 'ui', 'oi', 'aic']
const causeText = {
  pi: 'Prompt Insight 계산 경로, 질문 토큰화 기준, 기준선 데이터 매칭을 확인하세요.',
  ui: 'User Intervention 계산 경로, 수정 거리 산식, before/after 텍스트 매칭을 확인하세요.',
  oi: 'Originality Index 계산 경로, 임베딩 backend, TopicScore 입력 분포를 확인하세요.',
  aic: 'AIC 가중 합산, 반올림 위치, 세부 지표 delta 전파 여부를 확인하세요.',
}

const performanceRows = computed(() => props.comparison.performanceRows || [])
const scoreRows = computed(() => props.comparison.scoreRows || [])
const sampleCount = computed(() => Number(props.comparison.sampleCount || 0))
const minSampleCount = computed(() => Number(props.comparison.minSampleCount || 10))
const regressionRows = computed(() => scoreRows.value.filter((row) => row.passed === false))
const unmeasuredRows = computed(() => scoreRows.value.filter((row) => row.passed === null || row.passed === undefined))
const isSampleInsufficient = computed(() => sampleCount.value > 0 && sampleCount.value < minSampleCount.value)
const hasScoreCoverage = computed(() => SCORE_KEYS.every((key) => scoreRows.value.some((row) => row.key === key && row.delta !== null && row.delta !== undefined)))

const confidence = computed(() => {
  if (!hasScoreCoverage.value || sampleCount.value <= 0 || isSampleInsufficient.value) {
    return {
      label: '측정 신뢰도 낮음',
      badge: 'badge-danger',
      status: 'low',
      detail: `표본 ${sampleCount.value || 0}건 · 최소 ${minSampleCount.value}건 권장`,
    }
  }
  if (props.comparison.bootstrapPassed === false || props.comparison.bootstrapPassed === null || props.comparison.bootstrapPassed === undefined) {
    return {
      label: '측정 신뢰도 확인 필요',
      badge: 'badge-warning',
      status: 'medium',
      detail: props.comparison.bootstrapPassed === false ? 'Bootstrap 검증 미통과' : 'Bootstrap 검증 결과 없음',
    }
  }
  return {
    label: '측정 신뢰도 양호',
    badge: 'badge-success',
    status: 'high',
    detail: `표본 ${sampleCount.value}건 · Bootstrap 통과`,
  }
})

const deploymentState = computed(() => {
  if (regressionRows.value.length) {
    return {
      label: '배포 보류',
      badge: 'badge-danger',
      title: '회귀 경고',
      detail: `${regressionRows.value.map((row) => row.label).join(', ')} delta가 허용 오차를 넘었습니다.`,
    }
  }
  if (confidence.value.status !== 'high') {
    return {
      label: '추가 측정 필요',
      badge: 'badge-warning',
      title: '측정 신뢰도 주의',
      detail: '품질 회귀는 감지되지 않았지만 표본 수 또는 검증 근거가 부족합니다.',
    }
  }
  return {
    label: '배포 반영 가능',
    badge: 'badge-success',
    title: '정상 범위',
    detail: 'PI/UI/OI/AIC delta가 허용 오차 안에 있고 측정 신뢰도가 충분합니다.',
  }
})

const causeCandidates = computed(() => {
  if (regressionRows.value.length) {
    return regressionRows.value.map((row) => ({
      key: row.key,
      label: row.label,
      text: causeText[row.key] || '해당 지표의 기준선과 최적화 후 입력/출력 매핑을 확인하세요.',
    }))
  }
  if (isSampleInsufficient.value) {
    return [{ key: 'sample', label: 'Sample', text: `표본 ${sampleCount.value}건은 최소 권장 ${minSampleCount.value}건보다 적어 delta 해석이 불안정할 수 있습니다.` }]
  }
  if (unmeasuredRows.value.length) {
    return [{ key: 'coverage', label: 'Coverage', text: `${unmeasuredRows.value.map((row) => row.label).join(', ')} delta 측정값이 없어 회귀 여부를 확정할 수 없습니다.` }]
  }
  if (props.comparison.bootstrapPassed !== true) {
    return [{ key: 'bootstrap', label: 'Bootstrap', text: 'Bootstrap 검증 결과가 통과 상태로 확인되어야 배포 판단 신뢰도가 높아집니다.' }]
  }
  return [{ key: 'ready', label: 'Ready', text: '정상 범위입니다. 추가 회귀 신호가 없으면 배포 반영 가능 상태로 볼 수 있습니다.' }]
})

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
      <div class="status-stack">
        <span class="badge" :class="deploymentState.badge">{{ deploymentState.label }}</span>
        <span class="badge" :class="statusClass">{{ statusLabel }}</span>
      </div>
    </div>

    <div class="assurance-panel" :class="`assurance-panel--${confidence.status}`">
      <div class="assurance-main">
        <span class="badge" :class="confidence.badge">{{ confidence.label }}</span>
        <div>
          <div class="assurance-title">{{ deploymentState.title }}</div>
          <p class="assurance-copy">{{ deploymentState.detail }}</p>
        </div>
      </div>
      <div class="assurance-meta">
        <span>허용 오차 ±{{ comparison.scoreTolerance }}</span>
        <span>{{ confidence.detail }}</span>
      </div>
    </div>

    <div class="cause-panel">
      <div class="panel-title">Warning Signals & Candidate Causes</div>
      <div class="cause-list">
        <div v-for="item in causeCandidates" :key="item.key" class="cause-item">
          <span class="cause-label">{{ item.label }}</span>
          <span class="cause-text">{{ item.text }}</span>
        </div>
      </div>
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
                <th>Tolerance</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in scoreRows" :key="row.key">
                <td class="score-name">{{ row.label }}</td>
                <td>{{ formatValue(row.baseline) }}</td>
                <td>{{ formatValue(row.optimized) }}</td>
                <td>{{ formatValue(row.delta) }}</td>
                <td>±{{ formatValue(row.tolerance) }}</td>
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

.status-stack {
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  gap: var(--space-2);
  flex-shrink: 0;
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

.assurance-panel {
  border: 1px solid var(--border-light);
  border-left: 4px solid var(--color-warning);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  background: var(--color-gray-50);
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}

.assurance-panel--high { border-left-color: var(--color-success); }
.assurance-panel--low { border-left-color: var(--color-danger); }

.assurance-main {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  min-width: 0;
}

.assurance-title {
  font-size: var(--font-size-sm);
  font-weight: 800;
  color: var(--text-primary);
}

.assurance-copy {
  margin-top: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

.assurance-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-1);
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

.cause-panel {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.cause-list {
  display: grid;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.cause-item {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: var(--space-3);
  align-items: start;
  font-size: var(--font-size-sm);
}

.cause-label {
  font-weight: 800;
  color: var(--text-primary);
}

.cause-text {
  color: var(--text-secondary);
  line-height: 1.5;
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

  .comparison-header,
  .assurance-panel,
  .assurance-main {
    flex-direction: column;
  }

  .status-stack,
  .assurance-meta {
    align-items: flex-start;
  }

  .assurance-meta {
    white-space: normal;
  }
}

@media (max-width: 520px) {
  .cause-item {
    grid-template-columns: 1fr;
    gap: var(--space-1);
  }
}
</style>

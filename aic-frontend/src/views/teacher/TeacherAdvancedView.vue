<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import BarChart from '@/components/charts/BarChart.vue'
import ScatterChart from '@/components/charts/ScatterChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const loading = ref(true)
const error = ref('')
const scatterData = ref([])
const correlationMatrix = ref({})

// Temporary advanced-analysis placeholders. Replace this block when backend
// exposes cluster, effort, and draft-similarity contracts.
const temporaryAdvancedInsights = {
  clusters: [
    { label: '고역량', count: 7, color: '#10B981', points: [{ x: 82, y: 78 }, { x: 88, y: 84 }, { x: 76, y: 82 }, { x: 91, y: 76 }] },
    { label: '중상위', count: 10, color: '#3B82F6', points: [{ x: 66, y: 68 }, { x: 72, y: 61 }, { x: 64, y: 74 }, { x: 70, y: 70 }] },
    { label: '성장형', count: 7, color: '#F97316', points: [{ x: 42, y: 58 }, { x: 48, y: 63 }, { x: 39, y: 52 }, { x: 51, y: 56 }] },
    { label: '위험군', count: 4, color: '#EF4444', points: [{ x: 28, y: 32 }, { x: 34, y: 29 }, { x: 25, y: 39 }, { x: 37, y: 35 }] },
  ],
  strategies: [
    { key: 'expert', title: 'Expert', desc: '질문과 수정 모두 높음', count: 7, tone: 'blue' },
    { key: 'thinker', title: 'Thinker', desc: '질문은 높고 수정은 낮음', count: 6, tone: 'yellow' },
    { key: 'editor', title: 'Editor', desc: '질문은 낮고 수정은 높음', count: 11, tone: 'orange' },
    { key: 'passive', title: 'Passive', desc: '질문과 수정 모두 낮음', count: 4, tone: 'red' },
  ],
  effortSamples: [
    { x: 3, y: 42 }, { x: 5, y: 48 }, { x: 7, y: 58 }, { x: 8, y: 61 },
    { x: 10, y: 69 }, { x: 12, y: 73 }, { x: 15, y: 81 }, { x: 17, y: 86 },
  ],
  similarityBands: [
    { label: '유형 A', value: 38 },
    { label: '유형 B', value: 52 },
    { label: '유형 C', value: 64 },
    { label: '유형 D', value: 81 },
    { label: '유형 E', value: 89 },
  ],
}

onMounted(async () => {
  await loadAdvancedAnalytics()
})

async function loadAdvancedAnalytics() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/teacher/analytics/advanced')
    scatterData.value = Array.isArray(data.scatter_data) ? data.scatter_data : []
    correlationMatrix.value = data.correlation_matrix && typeof data.correlation_matrix === 'object'
      ? data.correlation_matrix
      : {}
  } catch (err) {
    scatterData.value = []
    correlationMatrix.value = {}
    error.value = err.response?.data?.detail || '심화 분석 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function scoreValue(value) {
  return value === null || value === undefined ? null : Number(value)
}

function formatScore(value) {
  const score = scoreValue(value)
  return Number.isFinite(score) ? score.toFixed(1) : '-'
}

function formatCorrelation(value) {
  const score = Number(value)
  if (!Number.isFinite(score)) return '-'
  return score.toFixed(2)
}

const metricLabels = {
  pi: 'PI',
  ui: 'UI',
  oi: 'OI',
  aic: 'AIC',
}

const hasScatterData = computed(() => scatterData.value.length > 0)

const averageScores = computed(() => {
  const totals = { pi: 0, ui: 0, oi: 0, aic: 0 }
  const counts = { pi: 0, ui: 0, oi: 0, aic: 0 }

  scatterData.value.forEach((row) => {
    Object.keys(totals).forEach((key) => {
      const value = scoreValue(row[key])
      if (Number.isFinite(value)) {
        totals[key] += value
        counts[key] += 1
      }
    })
  })

  return Object.keys(totals).map((key) => ({
    key,
    label: metricLabels[key],
    value: counts[key] ? totals[key] / counts[key] : null,
  }))
})

const scatterConfig = computed(() => {
  if (!hasScatterData.value) return null
  return {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: '학생',
          data: scatterData.value
            .filter((d) => Number.isFinite(scoreValue(d.pi)) && Number.isFinite(scoreValue(d.ui)))
            .map((d) => ({ x: d.pi, y: d.ui, student: d })),
          backgroundColor: 'rgba(59, 130, 246, 0.72)',
          borderColor: '#1D4ED8',
          borderWidth: 1,
          pointRadius: 6,
          pointHoverRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      parsing: false,
      scales: {
        x: { min: 0, max: 100, title: { display: true, text: 'PI 점수' } },
        y: { min: 0, max: 100, title: { display: true, text: 'UI 점수' } },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(context) {
              const student = context.raw.student
              return `${student.name}: PI ${formatScore(student.pi)}, UI ${formatScore(student.ui)}, OI ${formatScore(student.oi)}, AIC ${formatScore(student.aic)}`
            },
          },
        },
      },
    },
  }
})

const clusterConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: temporaryAdvancedInsights.clusters.map((cluster) => ({
      label: cluster.label,
      data: cluster.points,
      backgroundColor: cluster.color,
      borderColor: cluster.color,
      borderWidth: 1,
      pointRadius: 6,
      pointHoverRadius: 8,
    })),
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { min: 0, max: 100, title: { display: true, text: 'PCA 1' } },
      y: { min: 0, max: 100, title: { display: true, text: 'PCA 2' } },
    },
    plugins: {
      legend: { position: 'bottom' },
    },
  },
}))

const effortConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: [
      {
        label: '수정 횟수 vs AIC',
        data: temporaryAdvancedInsights.effortSamples,
        backgroundColor: 'rgba(16, 185, 129, 0.72)',
        borderColor: '#047857',
        borderWidth: 1,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    parsing: false,
    scales: {
      x: { min: 0, max: 20, title: { display: true, text: '수정 횟수' } },
      y: { min: 0, max: 100, title: { display: true, text: 'AIC 점수' } },
    },
    plugins: {
      legend: { display: false },
    },
  },
}))

const similarityConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: temporaryAdvancedInsights.similarityBands.map((item) => item.label),
    datasets: [
      {
        label: '초안 유사도',
        data: temporaryAdvancedInsights.similarityBands.map((item) => item.value),
        backgroundColor: temporaryAdvancedInsights.similarityBands.map((item) => (
          item.value >= 80 ? '#EF4444' : item.value >= 60 ? '#F97316' : '#10B981'
        )),
        borderRadius: 6,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { min: 0, max: 100, title: { display: true, text: '유사도' } },
    },
    plugins: {
      legend: { display: false },
    },
  },
}))

const heatmapRows = computed(() => {
  const keys = ['pi', 'ui', 'oi', 'aic']
  return keys.map((rowKey) => ({
    key: rowKey,
    label: metricLabels[rowKey],
    cells: keys.map((colKey) => {
      const value = rowKey === colKey ? 1 : correlationMatrix.value[`${rowKey}_${colKey}`] ?? correlationMatrix.value[`${colKey}_${rowKey}`]
      return {
        key: colKey,
        value,
        intensity: Math.min(Math.abs(Number(value) || 0), 1),
        positive: Number(value) >= 0,
      }
    }),
  }))
})
</script>

<template>
  <AppLayout title="심화 분석" subtitle="산점도와 상관관계 분석">
    <div v-if="loading" class="card loading-state">불러오는 중...</div>

    <div v-else-if="error" class="card card-body empty-state">
      <p>{{ error }}</p>
      <button class="btn btn-secondary btn-sm" type="button" @click="loadAdvancedAnalytics">다시 시도</button>
    </div>

    <div v-else-if="!hasScatterData" class="card card-body empty-state">
      <p>표시할 최신 분석 데이터가 없습니다.</p>
    </div>

    <div v-else class="advanced-grid">
      <section class="card card-body chart-card scatter-panel">
        <div class="card-heading">
          <h3>PI/UI 산점도</h3>
          <span class="muted-row">{{ scatterData.length }}명</span>
        </div>
        <ScatterChart v-if="scatterConfig" :config="scatterConfig" />
      </section>

      <section class="card card-body">
        <div class="card-heading">
          <h3>평균 지표</h3>
          <span class="muted-row">최신 제출 기준</span>
        </div>
        <div class="score-summary">
          <div v-for="score in averageScores" :key="score.key" class="score-chip" :class="score.key">
            <span>{{ score.label }}</span>
            <strong>{{ formatScore(score.value) }}</strong>
          </div>
        </div>
      </section>

      <section class="card card-body chart-card">
        <div class="card-heading">
          <h3>학생 군집 분석</h3>
          <span class="muted-row">4개 유형</span>
        </div>
        <ScatterChart :config="clusterConfig" />
        <div class="cluster-legend">
          <div v-for="cluster in temporaryAdvancedInsights.clusters" :key="cluster.label" class="legend-item">
            <span class="legend-dot" :style="{ background: cluster.color }"></span>
            {{ cluster.label }} {{ cluster.count }}명
          </div>
        </div>
      </section>

      <section class="card card-body">
        <div class="card-heading">
          <h3>협업 전략 유형</h3>
          <span class="muted-row">PI/UI 기준</span>
        </div>
        <div class="strategy-grid">
          <div
            v-for="strategy in temporaryAdvancedInsights.strategies"
            :key="strategy.key"
            class="strategy-cell"
            :class="strategy.tone"
          >
            <div>
              <strong>{{ strategy.title }}</strong>
              <span>{{ strategy.desc }}</span>
            </div>
            <b>{{ strategy.count }}</b>
          </div>
        </div>
      </section>

      <section class="card card-body heatmap-panel">
        <div class="card-heading">
          <h3>상관관계 히트맵</h3>
          <span class="muted-row">Pearson r</span>
        </div>
        <div class="heatmap" role="table" aria-label="지표 상관관계">
          <div class="heatmap-corner"></div>
          <div v-for="label in ['PI', 'UI', 'OI', 'AIC']" :key="`col-${label}`" class="heatmap-axis">
            {{ label }}
          </div>
          <template v-for="row in heatmapRows" :key="row.key">
            <div class="heatmap-axis row-label">{{ row.label }}</div>
            <div
              v-for="cell in row.cells"
              :key="`${row.key}-${cell.key}`"
              class="heatmap-cell"
              :class="{ negative: !cell.positive }"
              :style="{ '--intensity': cell.intensity }"
              :title="`${row.label}/${metricLabels[cell.key]}: ${formatCorrelation(cell.value)}`"
            >
              {{ formatCorrelation(cell.value) }}
            </div>
          </template>
        </div>
      </section>

      <section class="card card-body chart-card">
        <div class="card-heading">
          <h3>Effort vs AIC</h3>
          <span class="muted-row">r = 0.74</span>
        </div>
        <ScatterChart :config="effortConfig" />
      </section>

      <section class="card card-body chart-card">
        <div class="card-heading">
          <h3>초안 유사도</h3>
          <span class="muted-row">낮을수록 개입 높음</span>
        </div>
        <BarChart :config="similarityConfig" />
      </section>

      <section class="card card-body full">
        <div class="card-heading">
          <h3>개별 데이터</h3>
          <span class="muted-row">AIC 내림차순 참고</span>
        </div>
        <div class="data-table-wrapper">
          <table class="data-table">
          <thead>
            <tr>
              <th>학생</th>
              <th>PI</th>
              <th>UI</th>
              <th>OI</th>
              <th>AIC</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in scatterData" :key="s.student_id">
              <td>{{ s.name }}</td>
              <td>{{ formatScore(s.pi) }}</td>
              <td>{{ formatScore(s.ui) }}</td>
              <td>{{ formatScore(s.oi) }}</td>
              <td>
                <div class="aic-cell">
                  <span>{{ formatScore(s.aic) }}</span>
                  <StatusBadge :score="s.aic" />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.advanced-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: var(--space-4);
}

.scatter-panel {
  min-height: 360px;
}

.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.score-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.score-chip {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--color-gray-50);
  border: 1px solid var(--border-light);
}

.score-chip span {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  font-weight: 700;
}

.score-chip strong {
  color: var(--text-primary);
  font-size: var(--font-size-xl);
}

.score-chip.pi { border-left: 4px solid var(--color-pi); }
.score-chip.ui { border-left: 4px solid var(--color-ui); }
.score-chip.oi { border-left: 4px solid var(--color-oi); }
.score-chip.aic { border-left: 4px solid var(--color-aic); }

.cluster-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-4);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.strategy-cell {
  min-height: 118px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  background: var(--color-gray-50);
}

.strategy-cell strong,
.strategy-cell b {
  display: block;
  color: var(--text-primary);
  font-size: var(--font-size-lg);
}

.strategy-cell span {
  display: block;
  margin-top: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  line-height: 1.45;
}

.strategy-cell.blue { border-left: 4px solid var(--color-pi); }
.strategy-cell.yellow { border-left: 4px solid #EAB308; }
.strategy-cell.orange { border-left: 4px solid var(--color-ui); }
.strategy-cell.red { border-left: 4px solid var(--color-danger); }

.heatmap {
  display: grid;
  grid-template-columns: 56px repeat(4, minmax(58px, 1fr));
  gap: var(--space-2);
  align-items: stretch;
}

.heatmap-axis,
.heatmap-corner,
.heatmap-cell {
  min-height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: 700;
}

.heatmap-axis {
  color: var(--text-secondary);
  background: var(--color-gray-50);
}

.row-label {
  justify-content: flex-start;
  padding-left: var(--space-3);
}

.heatmap-cell {
  color: var(--text-primary);
  background: rgba(59, 130, 246, calc(0.12 + (var(--intensity) * 0.55)));
  border: 1px solid rgba(59, 130, 246, calc(0.18 + (var(--intensity) * 0.35)));
}

.heatmap-cell.negative {
  background: rgba(239, 68, 68, calc(0.12 + (var(--intensity) * 0.5)));
  border-color: rgba(239, 68, 68, calc(0.18 + (var(--intensity) * 0.35)));
}

.aic-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.full {
  grid-column: 1 / -1;
}

@media (max-width: 1024px) {
  .advanced-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .score-summary {
    grid-template-columns: 1fr;
  }

  .strategy-grid {
    grid-template-columns: 1fr;
  }

  .heatmap {
    grid-template-columns: 44px repeat(4, minmax(48px, 1fr));
    gap: var(--space-1);
  }

  .heatmap-axis,
  .heatmap-corner,
  .heatmap-cell {
    min-height: 38px;
    font-size: 11px;
  }
}
</style>

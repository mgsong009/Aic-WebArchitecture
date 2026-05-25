<script setup>
import { computed, onMounted, ref } from 'vue'
import { getTeacherAdvancedAnalytics } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import BarChart from '@/components/charts/BarChart.vue'
import ScatterChart from '@/components/charts/ScatterChart.vue'

const loading = ref(true)
const error = ref('')
const scatterData = ref([])
const correlationMatrix = ref({})
const clusters = ref([])
const strategies = ref([])
const effortSamples = ref([])
const effortCorrelation = ref(null)
const topicOiSamples = ref([])
const similarityBands = ref([])
const activeTab = ref('군집 분석')
const tabs = ['군집 분석', '상관관계', '전략 유형', 'Effort vs Score']

onMounted(loadAdvancedAnalytics)

async function loadAdvancedAnalytics() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherAdvancedAnalytics()
    scatterData.value = data.scatter_data
    correlationMatrix.value = data.correlation_matrix
    clusters.value = data.clusters
    strategies.value = data.strategies
    effortSamples.value = data.effort_samples
    effortCorrelation.value = data.effort_correlation
    topicOiSamples.value = data.topic_oi_samples
    similarityBands.value = data.similarity_bands
  } catch (err) {
    scatterData.value = []
    correlationMatrix.value = {}
    clusters.value = []
    strategies.value = []
    effortSamples.value = []
    effortCorrelation.value = null
    topicOiSamples.value = []
    similarityBands.value = []
    error.value = err.response?.data?.detail || '심화 분석 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function chartOptions({ min = 0, max = 100, legend = true, xTitle = '', yTitle = '' } = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    parsing: false,
    plugins: { legend: { display: legend, position: 'top', labels: { boxWidth: 10, font: { size: 10 } } } },
    scales: {
      x: { min, max, title: { display: Boolean(xTitle), text: xTitle }, grid: { color: '#F3F4F6' } },
      y: { min, max, title: { display: Boolean(yTitle), text: yTitle }, grid: { color: '#F3F4F6' } },
    },
  }
}

const clusterConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: clusters.value.map((cluster) => ({
      label: cluster.label,
      data: cluster.points,
      backgroundColor: cluster.color,
      pointRadius: cluster.label === '위험군' ? 8 : 6,
    })),
  },
  options: chartOptions({ min: -1, max: 1, xTitle: 'PCA 1', yTitle: 'PCA 2' }),
}))

const effortConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: [{
      label: '수정 강도 vs AIC',
      data: effortSamples.value,
      backgroundColor: '#3B82F6',
      pointRadius: 7,
    }],
  },
  options: chartOptions({ min: 0, max: 100, legend: false, xTitle: '수정 강도', yTitle: 'AIC Score' }),
}))

const topicOiConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: [{
      label: 'TopicScore vs OI',
      data: topicOiSamples.value,
      backgroundColor: '#10B981',
      pointRadius: 7,
    }],
  },
  options: chartOptions({ min: 40, max: 95, legend: false, xTitle: 'TopicScore', yTitle: 'OI' }),
}))

const similarityConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: similarityBands.value.map((item) => item.label),
    datasets: [{
      label: '초안 유사도',
      data: similarityBands.value.map((item) => item.value),
      backgroundColor: similarityBands.value.map((item) => item.value >= 80 ? '#EF4444' : item.value >= 60 ? '#F97316' : '#10B981'),
      borderRadius: 6,
    }],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { min: 0, max: 100, title: { display: true, text: '유사도' }, grid: { color: '#F3F4F6' } },
      x: { grid: { display: false } },
    },
  },
}))

const heatmapKeys = ['pi', 'ui', 'oi', 'topic', 'aic']
const heatmapLabels = { pi: 'PI', ui: 'UI', oi: 'OI', topic: 'TS', aic: 'AIC' }

const heatmapRows = computed(() => heatmapKeys.map((rowKey) => ({
  key: rowKey,
  label: heatmapLabels[rowKey],
  cells: heatmapKeys.map((colKey) => {
    const value = rowKey === colKey ? 1 : correlationMatrix.value[`${rowKey}_${colKey}`] ?? correlationMatrix.value[`${colKey}_${rowKey}`] ?? 0
    return { key: colKey, value, intensity: Math.min(Math.abs(Number(value)), 1), positive: Number(value) >= 0 }
  }),
})))

function formatCorrelation(value) {
  const next = Number(value)
  return Number.isFinite(next) ? next.toFixed(2) : '-'
}

const effortCorrelationLabel = computed(() => {
  const value = Number(effortCorrelation.value)
  return Number.isFinite(value) ? value.toFixed(2) : '-'
})
</script>

<template>
  <AppLayout title="심화 데이터 분석" subtitle="학생 군집, 지표 상관관계, 협업 전략 유형 분석" :show-page-header="false">
    <template #actions>
      <button class="btn btn-secondary btn-sm" type="button">데이터 내보내기</button>
    </template>

    <div v-if="error" class="alert alert-warning mb-4">{{ error }}</div>
    <div v-if="loading" class="card loading-state">불러오는 중...</div>

    <div v-else>
      <section class="adv-hero">
        <div class="ah-tag">Data Science View</div>
        <h1 class="ah-title">심화 데이터 분석</h1>
        <p class="ah-sub">학생 군집, 지표 상관관계, 협업 전략 유형 분석</p>
        <div class="ah-tabs">
          <button v-for="tab in tabs" :key="tab" type="button" class="ah-tab" :class="{ active: activeTab === tab }" @click="activeTab = tab">{{ tab }}</button>
        </div>
      </section>

      <div class="grid-2 section-gap">
        <section class="card">
          <div class="card-header"><div><div class="card-title">학생 군집 분석 (PCA Scatter)</div><div class="card-subtitle">PI/UI/OI/AIC 기반 2D 축소 - 4개 군집 탐지</div></div></div>
          <div class="card-body">
            <div class="chart-box tall"><ScatterChart :config="clusterConfig" /></div>
            <div class="cluster-legend">
              <div v-for="cluster in clusters" :key="cluster.label" class="cl-item">
                <span class="cl-dot" :style="{ background: cluster.color }"></span>{{ cluster.label }} ({{ cluster.count }}명)
              </div>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-header"><div><div class="card-title">협업 전략 유형 지도</div><div class="card-subtitle">PI vs UI 기준 - 4가지 학습 전략 유형</div></div></div>
          <div class="card-body">
            <div class="strategy-axis"><span></span><strong>UI 높음 →</strong></div>
            <div class="strategy-wrap">
              <div class="y-axis">← PI 높음</div>
              <div class="strategy-grid">
                <div v-for="strategy in strategies" :key="strategy.key" class="strategy-cell" :class="strategy.tone">
                  <div><strong>{{ strategy.title }}</strong><span>{{ strategy.desc }}</span></div>
                  <div><b>{{ strategy.count }}</b><small>학생</small></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="grid-2 section-gap">
        <section class="card">
          <div class="card-header"><div><div class="card-title">지표 상관관계 히트맵</div><div class="card-subtitle">Pearson correlation coefficient</div></div></div>
          <div class="card-body">
            <div class="heatmap">
              <div></div>
              <div v-for="key in heatmapKeys" :key="key" class="heatmap-label">{{ heatmapLabels[key] }}</div>
              <template v-for="row in heatmapRows" :key="row.key">
                <div class="heatmap-label row">{{ row.label }}</div>
                <div v-for="cell in row.cells" :key="cell.key" class="heatmap-cell" :class="{ negative: !cell.positive }" :style="{ '--intensity': cell.intensity }">{{ formatCorrelation(cell.value) }}</div>
              </template>
            </div>
            <div class="heatmap-scale"><span></span>-1.0 (역상관) - 0 - +1.0 (정상관)</div>
          </div>
        </section>

        <section class="card">
          <div class="card-header"><div><div class="card-title">Effort vs AIC Score</div><div class="card-subtitle">X: 수정 강도, Y: AIC - 노력-성과 상관관계</div></div></div>
          <div class="card-body">
            <div class="chart-box tall"><ScatterChart :config="effortConfig" /></div>
            <div class="correlation-note"><strong>r = {{ effortCorrelationLabel }}</strong> - 실제 제출 metric 기반 수정 강도와 AIC 점수의 상관관계</div>
          </div>
        </section>
      </div>

      <div class="grid-2 section-gap">
        <section class="card">
          <div class="card-header"><div><div class="card-title">TopicScore vs OI</div><div class="card-subtitle">주제 적합성과 독창성의 관계</div></div></div>
          <div class="card-body"><div class="chart-box"><ScatterChart :config="topicOiConfig" /></div></div>
        </section>
        <section class="card">
          <div class="card-header"><div><div class="card-title">Draft Similarity Matrix</div><div class="card-subtitle">초안 vs 최종본 유사도 (낮을수록 개입 많음)</div></div></div>
          <div class="card-body">
            <div class="chart-box"><BarChart :config="similarityConfig" /></div>
            <div class="similarity-legend"><span class="low">■</span> 낮은 유사도 = 높은 개입 <span class="high">■</span> 높은 유사도 = 낮은 개입</div>
          </div>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.adv-hero { padding: var(--space-6); border-radius: var(--radius-xl); background: linear-gradient(135deg, var(--color-aic) 0%, #2C5282 60%, #3B82F6 100%); color: white; box-shadow: var(--shadow-sm); }
.ah-tag { display: inline-flex; padding: 3px 10px; border-radius: var(--radius-full); background: rgba(255,255,255,0.16); font-size: var(--font-size-xs); font-weight: 800; text-transform: uppercase; }
.ah-title { margin-top: var(--space-3); font-size: var(--font-size-4xl); line-height: 1.15; }
.ah-sub { margin-top: var(--space-1); color: rgba(255,255,255,0.78); font-size: var(--font-size-sm); }
.ah-tabs { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-5); }
.ah-tab { padding: var(--space-2) var(--space-4); border-radius: var(--radius-full); color: rgba(255,255,255,0.76); background: rgba(255,255,255,0.12); font-size: var(--font-size-xs); font-weight: 800; }
.ah-tab.active { color: var(--color-aic); background: white; }
.section-gap { margin-top: var(--space-6); }
.chart-box { height: 220px; }
.chart-box.tall { height: 250px; }
.cluster-legend { display: flex; flex-wrap: wrap; gap: var(--space-3); margin-top: var(--space-4); color: var(--text-secondary); font-size: var(--font-size-xs); }
.cl-item { display: inline-flex; align-items: center; gap: var(--space-2); }
.cl-dot { width: 10px; height: 10px; border-radius: var(--radius-full); }
.strategy-axis { display: grid; grid-template-columns: 20px 1fr; gap: 4px; margin-bottom: var(--space-2); color: var(--text-muted); font-size: 10px; text-align: center; }
.strategy-wrap { display: grid; grid-template-columns: 20px 1fr; gap: 4px; }
.y-axis { display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 10px; font-weight: 800; writing-mode: vertical-rl; transform: rotate(180deg); }
.strategy-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px; }
.strategy-cell { min-height: 130px; display: flex; flex-direction: column; justify-content: space-between; padding: var(--space-4); border-radius: var(--radius-md); border: 1px solid var(--border-light); }
.strategy-cell strong, .strategy-cell b { display: block; font-size: var(--font-size-lg); }
.strategy-cell span, .strategy-cell small { display: block; margin-top: var(--space-1); color: var(--text-secondary); font-size: var(--font-size-xs); line-height: 1.45; }
.strategy-cell.blue { background: var(--color-pi-pale); color: #1D4ED8; }
.strategy-cell.yellow { background: #FEF9C3; color: #A16207; }
.strategy-cell.orange { background: var(--color-ui-pale); color: #C2410C; }
.strategy-cell.red { background: #FEE2E2; color: #B91C1C; }
.heatmap { max-width: 340px; display: grid; grid-template-columns: 50px repeat(5, 1fr); gap: 3px; margin: 0 auto; }
.heatmap-label { display: grid; place-items: center; min-height: 34px; color: var(--text-muted); font-size: 10px; font-weight: 800; }
.heatmap-label.row { justify-content: end; padding-right: var(--space-2); }
.heatmap-cell { display: grid; place-items: center; min-height: 42px; border-radius: var(--radius-sm); color: var(--text-primary); font-size: 10px; font-weight: 800; background: rgba(30,58,95, calc(0.08 + var(--intensity) * 0.58)); }
.heatmap-cell.negative { background: rgba(239,68,68, calc(0.08 + var(--intensity) * 0.54)); }
.heatmap-scale { display: flex; align-items: center; justify-content: center; gap: var(--space-2); margin-top: var(--space-4); color: var(--text-muted); font-size: 10px; }
.heatmap-scale span { width: 60px; height: 8px; border-radius: var(--radius-full); background: linear-gradient(90deg,#EF4444,#FCA5A5,#E5E7EB,#93C5FD,#1E3A5F); }
.correlation-note { margin-top: var(--space-3); padding: 10px 12px; border-radius: var(--radius-md); color: var(--color-pi); background: var(--color-pi-pale); font-size: var(--font-size-xs); }
.similarity-legend { display: flex; flex-wrap: wrap; gap: var(--space-3); margin-top: var(--space-3); color: var(--text-muted); font-size: var(--font-size-xs); }
.similarity-legend .low { color: var(--color-oi); font-weight: 800; }
.similarity-legend .high { color: var(--color-danger); font-weight: 800; }
@media (max-width: 920px) {
  .grid-2 { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .strategy-grid { grid-template-columns: 1fr; }
  .heatmap { grid-template-columns: 38px repeat(5, minmax(38px, 1fr)); }
  .heatmap-cell { min-height: 36px; font-size: 9px; }
}
</style>

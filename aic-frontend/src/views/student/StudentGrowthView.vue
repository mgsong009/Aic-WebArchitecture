<script setup>
import { computed, ref, onMounted } from 'vue'
import { getStudentGrowth } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import LineChart from '@/components/charts/LineChart.vue'
import RadarChart from '@/components/charts/RadarChart.vue'

const loading = ref(true)
const error = ref('')
const activePeriod = ref('all')
const growth = ref({ assignments: [], class_avg_trend: [] })

const periods = [
  { key: 'recent', label: '1개월' },
  { key: 'all', label: '전체' },
  { key: 'semester', label: '학기' },
]

const metricKeys = [
  { key: 'aic', label: 'AIC', name: 'AIC 총 성장', short: 'AIC', color: '#1E3A5F', pale: 'var(--color-aic-pale)', icon: '↗' },
  { key: 'pi', label: 'PI', name: 'PI 성장', short: 'PI', color: '#3B82F6', pale: 'var(--color-pi-pale)', icon: '?' },
  { key: 'ui', label: 'UI', name: 'UI 성장', short: 'UI', color: '#F97316', pale: 'var(--color-ui-pale)', icon: '+' },
  { key: 'oi', label: 'OI', name: 'OI 성장', short: 'OI', color: '#10B981', pale: 'var(--color-oi-pale)', icon: '*' },
]

onMounted(async () => {
  await loadGrowth()
})

async function loadGrowth() {
  loading.value = true
  error.value = ''
  try {
    growth.value = await getStudentGrowth()
  } catch {
    error.value = '성장 분석 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function score(value) {
  return Number.isFinite(Number(value)) ? Number(value) : null
}

function formatScore(value, fallback = '-') {
  const next = score(value)
  return next == null ? fallback : Number.isInteger(next) ? next : next.toFixed(1)
}

function formatDelta(value) {
  if (value == null) return '변화 없음'
  const rounded = Number.isInteger(value) ? value : value.toFixed(1)
  return `${value >= 0 ? '+' : ''}${rounded}`
}

const assignments = computed(() => growth.value.assignments)
const classAvgTrend = computed(() => growth.value.class_avg_trend)
const hasAssignments = computed(() => assignments.value.length > 0)

const filteredAssignments = computed(() => {
  if (activePeriod.value === 'recent') return assignments.value.slice(-3)
  if (activePeriod.value === 'semester') return assignments.value.slice(-6)
  return assignments.value
})

const filteredClassTrend = computed(() => {
  if (activePeriod.value === 'recent') return classAvgTrend.value.slice(-3)
  if (activePeriod.value === 'semester') return classAvgTrend.value.slice(-6)
  return classAvgTrend.value
})

const first = computed(() => filteredAssignments.value[0] || null)
const latest = computed(() => filteredAssignments.value.at(-1) || null)
const previous = computed(() => filteredAssignments.value.length > 1 ? filteredAssignments.value.at(-2) : null)

const latestDelta = computed(() => {
  if (!latest.value || !previous.value) return {}
  return metricKeys.reduce((acc, metric) => {
    const next = score(latest.value?.[metric.key])
    const prev = score(previous.value?.[metric.key])
    acc[metric.key] = next != null && prev != null ? next - prev : null
    return acc
  }, {})
})

const totalGrowth = computed(() => {
  if (!latest.value || !first.value) return {}
  return metricKeys.reduce((acc, metric) => {
    const next = score(latest.value?.[metric.key])
    const start = score(first.value?.[metric.key])
    acc[metric.key] = next != null && start != null ? next - start : null
    return acc
  }, {})
})

const growthStats = computed(() => metricKeys.map((metric) => ({
  ...metric,
  value: totalGrowth.value[metric.key],
  delta: `${formatScore(first.value?.[metric.key])} → ${formatScore(latest.value?.[metric.key])}`,
  isBest: metric.key !== 'aic' && totalGrowth.value[metric.key] === strongestGrowth.value?.value,
})))

const strongestGrowth = computed(() => {
  const candidates = metricKeys
    .filter((metric) => metric.key !== 'aic')
    .map((metric) => ({ ...metric, value: totalGrowth.value[metric.key] }))
    .filter((metric) => metric.value != null)
    .sort((a, b) => b.value - a.value)
  return candidates[0] || null
})

const weakestLatest = computed(() => {
  const candidates = metricKeys
    .filter((metric) => metric.key !== 'aic')
    .map((metric) => ({ ...metric, value: score(latest.value?.[metric.key]) }))
    .filter((metric) => metric.value != null)
    .sort((a, b) => a.value - b.value)
  return candidates[0] || null
})

const latestClassAvg = computed(() => filteredClassTrend.value.at(-1) || null)
const classGap = computed(() => {
  const mine = score(latest.value?.aic)
  const average = score(latestClassAvg.value?.aic)
  return mine != null && average != null ? mine - average : null
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: { min: 0, max: 100, grid: { color: '#F3F4F6' }, ticks: { font: { size: 10 } } },
    x: { grid: { display: false }, ticks: { font: { size: 11 } } },
  },
  plugins: {
    legend: { display: true, position: 'top', labels: { font: { size: 11 }, boxWidth: 12 } },
  },
}

const aicCompareConfig = computed(() => {
  if (!filteredAssignments.value.length) return null
  return {
    type: 'line',
    data: {
      labels: filteredAssignments.value.map((a) => a.label),
      datasets: [
        {
          label: '내 AIC',
          data: filteredAssignments.value.map((a) => score(a.aic)),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30,58,95,0.08)',
          borderWidth: 2.5,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#1E3A5F',
          pointRadius: 5,
        },
        {
          label: '반 평균',
          data: filteredClassTrend.value.map((a) => score(a.aic)),
          borderColor: '#D1D5DB',
          borderDash: [5, 5],
          borderWidth: 1.5,
          tension: 0.4,
          pointRadius: 0,
        },
      ],
    },
    options: {
      ...chartOptions,
      scales: {
        ...chartOptions.scales,
        y: { ...chartOptions.scales.y, min: 40, max: 90, ticks: { font: { size: 10 }, stepSize: 10 } },
      },
    },
  }
})

const metricTrendConfig = computed(() => {
  if (!filteredAssignments.value.length) return null
  return {
    type: 'line',
    data: {
      labels: filteredAssignments.value.map((a) => a.label),
      datasets: metricKeys.filter((metric) => metric.key !== 'aic').map((metric) => ({
        label: metric.label,
        data: filteredAssignments.value.map((a) => score(a[metric.key])),
        borderColor: metric.color,
        backgroundColor: metric.color,
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: metric.color,
      })),
    },
    options: {
      ...chartOptions,
      scales: {
        ...chartOptions.scales,
        y: { ...chartOptions.scales.y, min: 40, max: 90 },
      },
    },
  }
})

const stackedAreaConfig = computed(() => {
  if (!filteredAssignments.value.length) return null
  return {
    type: 'line',
    data: {
      labels: filteredAssignments.value.map((a) => a.label),
      datasets: metricKeys.filter((metric) => metric.key !== 'aic').map((metric) => ({
        label: metric.label,
        data: filteredAssignments.value.map((a) => score(a[metric.key])),
        backgroundColor: `${metric.color}33`,
        borderColor: metric.color,
        borderWidth: 1.5,
        fill: true,
        tension: 0.4,
        pointRadius: 2,
      })),
    },
    options: chartOptions,
  }
})

const radarConfig = computed(() => {
  if (!latest.value) return null
  return {
    type: 'radar',
    data: {
      labels: ['PI', 'UI', 'OI', 'Topic'],
      datasets: [
        {
          label: latest.value.title || latest.value.label,
          data: [latest.value.pi || 0, latest.value.ui || 0, latest.value.oi || 0, latest.value.topic || 0],
          backgroundColor: 'rgba(30,58,95,0.12)',
          borderColor: '#1E3A5F',
          pointBackgroundColor: '#1E3A5F',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { r: { min: 0, max: 100, ticks: { display: false } } },
      plugins: { legend: { display: false } },
    },
  }
})

const contributionBars = computed(() => metricKeys.filter((metric) => metric.key !== 'aic').map((metric) => ({
  ...metric,
  value: score(latest.value?.[metric.key]) || 0,
  delta: latestDelta.value[metric.key],
})))

const insights = computed(() => {
  const next = []
  if (strongestGrowth.value) {
    next.push({
      tone: 'success',
      icon: '*',
      title: `${strongestGrowth.value.label} 최고 성장 (${formatDelta(strongestGrowth.value.value)})`,
      desc: `${strongestGrowth.value.name.replace(' 성장', '')} 지표가 선택 기간에서 가장 빠르게 개선되었습니다. 다음 과제에서도 이 전략을 유지하세요.`,
    })
  }
  if (weakestLatest.value) {
    next.push({
      tone: weakestLatest.value.key === 'ui' ? 'warning' : 'info',
      icon: weakestLatest.value.key === 'ui' ? '!' : '?',
      title: `${weakestLatest.value.label} 보강 포인트`,
      desc: `현재 ${weakestLatest.value.label}는 ${formatScore(weakestLatest.value.value)}점입니다. 가장 낮은 지표를 한 단계 끌어올리면 AIC 종합 성장도 안정됩니다.`,
    })
  }
  if (classGap.value != null) {
    next.push({
      tone: classGap.value >= 0 ? 'info' : 'warning',
      icon: classGap.value >= 0 ? '+' : '!',
      title: classGap.value >= 0 ? `반 평균보다 ${formatDelta(classGap.value)}점 앞섬` : `반 평균보다 ${Math.abs(classGap.value).toFixed(1)}점 낮음`,
      desc: classGap.value >= 0
        ? '최근 AIC가 반 평균보다 높습니다. 강점 지표를 유지하면서 낮은 지표를 보완하세요.'
        : '최근 AIC가 반 평균보다 낮습니다. 다음 과제에서는 가장 낮은 세부 지표 하나를 집중 개선하는 편이 좋습니다.',
    })
  }
  return next
})

function exportCsv() {
  const header = ['label', 'title', 'aic', 'pi', 'ui', 'oi', 'topic']
  const rows = filteredAssignments.value.map((item) =>
    header.map((key) => `"${String(item[key] ?? '').replaceAll('"', '""')}"`).join(',')
  )
  const blob = new Blob([[header.join(','), ...rows].join('\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'aic-growth.csv'
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <AppLayout title="성장 분석" subtitle="과제별 AIC 지표 변화 및 AI 활용 역량 성장 추이">
    <template #actions>
      <div class="period-filter" aria-label="성장 분석 기간">
        <button
          v-for="period in periods"
          :key="period.key"
          class="period-btn"
          :class="{ active: activePeriod === period.key }"
          type="button"
          @click="activePeriod = period.key"
        >
          {{ period.label }}
        </button>
      </div>
      <button class="btn btn-secondary btn-sm export-btn" type="button" :disabled="!hasAssignments" @click="exportCsv">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7,10 12,15 17,10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        내보내기
      </button>
    </template>

    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="132px" />
      <LoadingSkeleton height="340px" />
      <LoadingSkeleton height="260px" />
    </div>

    <div v-else-if="error" class="card card-body empty-state">
      <strong>{{ error }}</strong>
      <button class="btn btn-secondary btn-sm mt-4" type="button" @click="loadGrowth">다시 시도</button>
    </div>

    <div v-else-if="!hasAssignments" class="card card-body empty-state">
      아직 성장 추이를 계산할 제출 데이터가 없습니다.
    </div>

    <div v-else class="growth-page">
      <section class="growth-hero stagger" aria-label="성장 요약">
        <article v-for="stat in growthStats" :key="stat.key" class="growth-stat animate-fade-in-up">
          <div class="growth-stat-icon" :style="{ background: stat.pale, color: stat.color }">{{ stat.icon }}</div>
          <div class="growth-stat-val" :style="{ color: stat.color }">{{ formatDelta(stat.value) }}</div>
          <div class="growth-stat-label">{{ stat.name }}</div>
          <div class="growth-stat-delta" :class="{ success: (stat.value ?? 0) >= 0 }">
            {{ stat.delta }} <span v-if="stat.isBest">최고 성장</span>
          </div>
        </article>
      </section>

      <section class="card chart-card section-gap">
        <div class="card-header">
          <div>
            <div class="card-title">AIC 종합 성장 추이</div>
            <div class="card-subtitle">과제별 내 AIC vs 반 평균</div>
          </div>
          <div class="legend-row" aria-hidden="true">
            <span><i class="legend-line mine"></i>내 AIC</span>
            <span><i class="legend-line class"></i>반 평균</span>
          </div>
        </div>
        <div class="card-body chart-shell tall">
          <LineChart v-if="aicCompareConfig" :config="aicCompareConfig" />
        </div>
      </section>

      <section class="grid-2 section-gap">
        <article class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">PI / UI / OI 변화 추이</div>
              <div class="card-subtitle">지표별 시계열 비교</div>
            </div>
          </div>
          <div class="card-body chart-shell">
            <LineChart v-if="metricTrendConfig" :config="metricTrendConfig" />
          </div>
        </article>

        <article class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">최신 지표 구성</div>
              <div class="card-subtitle">{{ latest?.label }} 기준 PI/UI/OI 프로파일</div>
            </div>
          </div>
          <div class="card-body profile-grid">
            <div class="dependency-bar-group">
              <div v-for="item in contributionBars" :key="item.key" class="dep-item">
                <div class="dep-label" :style="{ color: item.color }">{{ item.label }}</div>
                <div class="dep-track">
                  <div class="dep-fill" :style="{ width: `${item.value}%`, background: item.color }">
                    {{ formatScore(item.value) }}
                  </div>
                </div>
                <div class="dep-num" :class="{ up: (item.delta ?? 0) >= 0, down: (item.delta ?? 0) < 0 }">
                  {{ formatDelta(item.delta) }}
                </div>
              </div>
            </div>
            <div class="trend-analysis">
              <span class="trend-icon">{{ classGap != null && classGap >= 0 ? '+' : '!' }}</span>
              <div class="trend-body">
                <div class="trend-title">
                  {{ classGap == null ? '반 평균 비교 데이터 없음' : classGap >= 0 ? '반 평균 대비 우위' : '반 평균 대비 보강 필요' }}
                </div>
                <div class="trend-desc">
                  <template v-if="classGap == null">반 평균 AIC가 제공되면 최신 과제 기준 비교를 표시합니다.</template>
                  <template v-else>최신 AIC {{ formatScore(latest?.aic) }}점, 반 평균 {{ formatScore(latestClassAvg?.aic) }}점으로 차이는 {{ formatDelta(classGap) }}점입니다.</template>
                </div>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="grid-2 section-gap">
        <article class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">AIC 구성 누적 면적 차트</div>
              <div class="card-subtitle">PI/UI/OI 기여 변화</div>
            </div>
          </div>
          <div class="card-body chart-shell">
            <LineChart v-if="stackedAreaConfig" :config="stackedAreaConfig" />
          </div>
        </article>

        <article class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">최신 프로파일</div>
              <div class="card-subtitle">{{ latest?.title || latest?.label }}</div>
            </div>
          </div>
          <div class="card-body chart-shell">
            <RadarChart v-if="radarConfig" :config="radarConfig" />
          </div>
        </article>
      </section>

      <section class="grid-2-1 section-gap">
        <article class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">성장 인사이트</div>
              <div class="card-subtitle">데이터 기반 분석</div>
            </div>
          </div>
          <div class="card-body insight-list">
            <div v-for="item in insights" :key="item.title" class="trend-analysis" :class="item.tone">
              <span class="trend-icon">{{ item.icon }}</span>
              <div class="trend-body">
                <div class="trend-title">{{ item.title }}</div>
                <div class="trend-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </article>

        <div class="data-table-wrapper">
          <table class="data-table compact-table">
            <thead>
              <tr>
                <th>과제</th>
                <th>AIC</th>
                <th>PI</th>
                <th>UI</th>
                <th>OI</th>
                <th>Topic</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in filteredAssignments" :key="a.assignment_id">
                <td>
                  <strong>{{ a.title }}</strong>
                  <div class="text-xs text-muted">{{ a.label }}</div>
                </td>
                <td>{{ formatScore(a.aic) }}</td>
                <td>{{ formatScore(a.pi) }}</td>
                <td>{{ formatScore(a.ui) }}</td>
                <td>{{ formatScore(a.oi) }}</td>
                <td>{{ formatScore(a.topic) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-wrap,
.growth-page,
.insight-list {
  display: grid;
  gap: var(--space-4);
}

.period-filter {
  display: flex;
  align-items: center;
  gap: 2px;
  background: var(--color-gray-100);
  padding: 3px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.period-btn {
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--text-muted);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.period-btn.active {
  background: white;
  color: var(--text-primary);
  box-shadow: var(--shadow-xs);
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.growth-hero {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-4);
}

.growth-stat {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.growth-stat-icon {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  margin-bottom: 8px;
  font-weight: 800;
}

.growth-stat-val {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
  line-height: 1;
}

.growth-stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: var(--space-2);
}

.growth-stat-delta {
  font-size: var(--font-size-xs);
  font-weight: 700;
  margin-top: 4px;
  color: var(--text-muted);
}

.growth-stat-delta.success {
  color: var(--color-success);
}

.section-gap {
  margin-bottom: var(--space-2);
}

.legend-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.legend-row span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.legend-line {
  width: 14px;
  height: 3px;
  display: inline-block;
  border-radius: var(--radius-full);
}

.legend-line.mine {
  background: var(--color-aic);
}

.legend-line.class {
  background: #d1d5db;
  border-top: 1px dashed #9ca3af;
}

.chart-shell {
  height: 260px;
}

.chart-shell.tall {
  height: 300px;
}

.profile-grid {
  display: grid;
  gap: var(--space-4);
}

.dependency-bar-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dep-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dep-label {
  width: 26px;
  font-size: var(--font-size-xs);
  font-weight: 800;
  flex-shrink: 0;
}

.dep-track {
  flex: 1;
  height: 22px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.dep-fill {
  height: 100%;
  min-width: 34px;
  border-radius: var(--radius-full);
  color: white;
  display: flex;
  align-items: center;
  padding-left: var(--space-2);
  font-size: 10px;
  font-weight: 800;
}

.dep-num {
  width: 42px;
  text-align: right;
  font-size: var(--font-size-xs);
  font-weight: 800;
}

.dep-num.up {
  color: var(--color-success);
}

.dep-num.down {
  color: var(--color-danger);
}

.trend-analysis {
  background: var(--color-gray-50);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
}

.trend-analysis.success {
  background: var(--color-oi-pale);
  border-color: rgba(16, 185, 129, 0.2);
}

.trend-analysis.info {
  background: var(--color-pi-pale);
  border-color: rgba(59, 130, 246, 0.2);
}

.trend-analysis.warning {
  background: var(--color-ui-pale);
  border-color: rgba(249, 115, 22, 0.2);
}

.trend-icon {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-md);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: var(--color-aic);
  font-weight: 800;
  box-shadow: var(--shadow-xs);
  flex-shrink: 0;
}

.trend-body {
  flex: 1;
}

.trend-title {
  font-size: var(--font-size-sm);
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.trend-desc {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  line-height: 1.6;
}

.compact-table {
  min-width: 620px;
}

@media (max-width: 1100px) {
  .growth-hero {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .growth-hero,
  .grid-2,
  .grid-2-1 {
    grid-template-columns: 1fr;
  }

  .period-filter {
    order: 2;
    width: 100%;
  }

  .period-btn {
    flex: 1;
  }

  .legend-row {
    display: none;
  }
}
</style>

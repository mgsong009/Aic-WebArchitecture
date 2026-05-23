<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeacherAssignmentAnalytics } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { referenceAssignments } from './teacherReferenceData'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const selectedLabel = ref(route.params.id ? `A${route.params.id}` : 'ALL')
const assignmentRows = ref(referenceAssignments)
const selectedAnalytics = ref(null)

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  selectedAnalytics.value = null
  if (!route.params.id) {
    loading.value = false
    return
  }
  try {
    selectedAnalytics.value = await getTeacherAssignmentAnalytics(Number(route.params.id))
  } catch (err) {
    error.value = err.response?.data?.detail || '과제별 API 데이터 대신 reference 비교 fallback을 표시합니다.'
  } finally {
    loading.value = false
  }
}

function handleFilter(next) {
  selectedLabel.value = next
  if (next === 'ALL') {
    router.push('/teacher/analytics/assignment')
  } else {
    router.push(`/teacher/analytics/assignment/${next.replace('A', '')}`)
  }
}

const rows = computed(() => assignmentRows.value)
const labels = computed(() => rows.value.map((row) => row.label))
const averageAic = computed(() => rows.value.reduce((sum, row) => sum + row.aic, 0) / rows.value.length)
const hardest = computed(() => rows.value.reduce((lowest, row) => row.aic < lowest.aic ? row : lowest, rows.value[0]))
const easiest = computed(() => rows.value.reduce((highest, row) => row.aic > highest.aic ? row : highest, rows.value[0]))
const averageDeviation = computed(() => rows.value.reduce((sum, row) => sum + row.deviation, 0) / rows.value.length)

const statCards = computed(() => [
  { label: '총 과제 수', value: rows.value.length, sub: `${labels.value[0]}~${labels.value.at(-1)}` },
  { label: '전체 평균 AIC', value: averageAic.value.toFixed(1), sub: `${rows.value.length}개 과제 평균`, tone: 'aic' },
  { label: '최고 난이도', value: hardest.value.label, sub: `평균 AIC ${hardest.value.aic} (최저)`, tone: 'danger' },
  { label: '최저 난이도', value: easiest.value.label, sub: `평균 AIC ${easiest.value.aic} (최고)`, tone: 'success' },
  { label: '평균 표준편차', value: averageDeviation.value.toFixed(1), sub: 'AIC 분포 폭' },
])

const avgAicConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: labels.value,
    datasets: [{
      label: '평균 AIC',
      data: rows.value.map((row) => row.aic),
      backgroundColor: rows.value.map((row) => row.aic < 61 ? 'rgba(239,68,68,0.7)' : row.aic < 65 ? 'rgba(249,115,22,0.7)' : 'rgba(30,58,95,0.7)'),
      borderRadius: 6,
    }],
  },
  options: chartOptions({ min: 50, max: 75, legend: false }),
}))

const boxConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: labels.value,
    datasets: [
      { label: 'IQR (25-75)', data: rows.value.map((row) => [row.q1, row.q3]), backgroundColor: 'rgba(59,130,246,0.3)', borderColor: '#3B82F6', borderWidth: 1.5, borderRadius: 4 },
      { label: '중앙값', data: rows.value.map((row) => [row.median - 1, row.median + 1]), backgroundColor: '#1E3A5F', borderRadius: 2 },
    ],
  },
  options: chartOptions({ min: 30, max: 90 }),
}))

const metricsConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: labels.value,
    datasets: [
      { label: 'PI', data: rows.value.map((row) => row.pi), backgroundColor: 'rgba(59,130,246,0.75)', borderRadius: 4 },
      { label: 'UI', data: rows.value.map((row) => row.ui), backgroundColor: 'rgba(249,115,22,0.75)', borderRadius: 4 },
      { label: 'OI', data: rows.value.map((row) => row.oi), backgroundColor: 'rgba(16,185,129,0.75)', borderRadius: 4 },
    ],
  },
  options: chartOptions({ min: 50, max: 80 }),
}))

const deviationConfig = computed(() => ({
  type: 'line',
  data: {
    labels: labels.value,
    datasets: [{
      label: '표준편차',
      data: rows.value.map((row) => row.deviation),
      borderColor: '#8B5CF6',
      backgroundColor: 'rgba(139,92,246,0.1)',
      fill: true,
      tension: 0.4,
      borderWidth: 2.5,
      pointBackgroundColor: '#8B5CF6',
      pointRadius: 5,
    }],
  },
  options: chartOptions({ min: 10, max: 20 }),
}))

function chartOptions({ min, max, legend = true }) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: legend, position: 'top', labels: { boxWidth: 10, font: { size: 10 } } } },
    scales: {
      y: { min, max, grid: { color: '#F3F4F6' }, ticks: { font: { size: 10 } } },
      x: { grid: { display: false }, ticks: { font: { size: 11 } } },
    },
  }
}

function difficultyClass(value) {
  return value === '어려움' ? 'badge-danger' : value === '쉬움' ? 'badge-success' : 'badge-warning'
}
</script>

<template>
  <AppLayout title="과제 분석" subtitle="CS101 · Assignment #1~#5 분포 및 난이도 분석">
    <template #actions>
      <select class="header-select" :value="selectedLabel" @change="handleFilter($event.target.value)">
        <option value="ALL">CS101 전체</option>
        <option v-for="row in rows" :key="row.label" :value="row.label">{{ row.label }} · {{ row.title }}</option>
      </select>
      <button class="btn btn-secondary btn-sm" type="button">내보내기</button>
    </template>

    <div v-if="error" class="alert alert-warning mb-4">{{ error }}</div>
    <div v-if="loading" class="card loading-state">불러오는 중...</div>

    <div v-else>
      <div class="assign-stat-grid">
        <div v-for="card in statCards" :key="card.label" class="assign-stat-card">
          <div class="asc-label">{{ card.label }}</div>
          <div class="asc-val" :class="card.tone">{{ card.value }}</div>
          <div class="asc-sub">{{ card.sub }}</div>
        </div>
      </div>

      <div class="grid-2 section-gap">
        <section class="card">
          <div class="card-header"><div><div class="card-title">과제별 평균 AIC</div><div class="card-subtitle">A1~A5 비교</div></div></div>
          <div class="card-body"><div class="chart-box"><BarChart :config="avgAicConfig" /></div></div>
        </section>
        <section class="card">
          <div class="card-header"><div><div class="card-title">과제별 분포 (Box Plot)</div><div class="card-subtitle">최솟값, 25th, 중앙값, 75th, 최댓값</div></div></div>
          <div class="card-body"><div class="chart-box"><BarChart :config="boxConfig" /></div></div>
        </section>
      </div>

      <div class="grid-2 section-gap">
        <section class="card">
          <div class="card-header"><div><div class="card-title">과제별 PI / UI / OI 평균</div></div></div>
          <div class="card-body"><div class="chart-box"><BarChart :config="metricsConfig" /></div></div>
        </section>
        <section class="card">
          <div class="card-header"><div><div class="card-title">과제별 편차</div><div class="card-subtitle">표준편차 시각화</div></div></div>
          <div class="card-body"><div class="chart-box"><BarChart :config="deviationConfig" /></div></div>
        </section>
      </div>

      <section v-if="selectedAnalytics" class="card section-gap">
        <div class="card-header"><div><div class="card-title">선택 과제 API 요약</div><div class="card-subtitle">{{ selectedAnalytics.assignment.title }}</div></div></div>
        <div class="api-summary">
          <div>AIC 평균 <strong>{{ selectedAnalytics.class_avg.aic ?? '-' }}</strong></div>
          <div>난이도 <strong>{{ Math.round((selectedAnalytics.difficulty || 0) * 100) }}%</strong></div>
          <div>상위 {{ selectedAnalytics.top5.length }}명 · 하위 {{ selectedAnalytics.bottom5.length }}명</div>
        </div>
      </section>

      <section class="card section-gap">
        <div class="card-header"><div><div class="card-title">과제별 상세 요약</div></div></div>
        <div class="table-scroll">
          <table class="assign-compare-table">
            <thead>
              <tr>
                <th>과제</th><th>주제</th><th>평균 AIC</th><th>평균 PI</th><th>평균 UI</th><th>평균 OI</th><th>표준편차</th><th>위험군 비율</th><th>난이도</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.label">
                <td><span class="badge badge-neutral">{{ row.label }}</span></td>
                <td>{{ row.title }}</td>
                <td class="aic">{{ row.aic }}</td>
                <td class="pi">{{ row.pi }}</td>
                <td class="ui">{{ row.ui }}</td>
                <td class="oi">{{ row.oi }}</td>
                <td>{{ row.deviation }}</td>
                <td :class="{ danger: row.riskRate >= 25 }">{{ row.riskRate }}%</td>
                <td><span class="badge" :class="difficultyClass(row.difficulty)">{{ row.difficulty }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.header-select { padding: 6px 10px; border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: var(--font-size-sm); background: white; outline: none; }
.assign-stat-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: var(--space-4); }
.assign-stat-card { padding: var(--space-5); border: 1px solid var(--border-light); border-radius: var(--radius-xl); background: var(--bg-surface); box-shadow: var(--shadow-sm); }
.asc-label { color: var(--text-muted); font-size: var(--font-size-xs); font-weight: 800; text-transform: uppercase; }
.asc-val { margin-top: var(--space-2); color: var(--text-primary); font-size: 30px; font-weight: 800; line-height: 1; }
.asc-val.aic { color: var(--color-aic); }
.asc-val.danger { color: var(--color-danger); }
.asc-val.success { color: var(--color-success); }
.asc-sub { margin-top: var(--space-2); color: var(--text-muted); font-size: var(--font-size-xs); }
.section-gap { margin-top: var(--space-6); }
.chart-box { height: 220px; }
.api-summary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-3); padding: var(--space-5); color: var(--text-secondary); }
.api-summary strong { color: var(--color-aic); }
.table-scroll { overflow-x: auto; }
.assign-compare-table { width: 100%; min-width: 860px; border-collapse: collapse; font-size: var(--font-size-sm); }
.assign-compare-table th { padding: 10px 14px; background: var(--color-gray-50); border-bottom: 2px solid var(--border-light); color: var(--text-muted); font-size: var(--font-size-xs); text-align: left; text-transform: uppercase; }
.assign-compare-table td { padding: 12px 14px; border-bottom: 1px solid var(--color-gray-100); color: var(--text-primary); }
.assign-compare-table tr:hover td { background: var(--color-gray-50); }
.aic { color: var(--color-aic); font-weight: 800; }
.pi { color: var(--color-pi); }
.ui { color: var(--color-ui); }
.oi { color: var(--color-oi); }
.danger { color: var(--color-danger); font-weight: 800; }
@media (max-width: 1100px) {
  .assign-stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .grid-2, .api-summary { grid-template-columns: 1fr; }
  .assign-stat-grid { grid-template-columns: 1fr; }
}
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTeacherRiskStudents } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import BarChart from '@/components/charts/BarChart.vue'
import ScatterChart from '@/components/charts/ScatterChart.vue'
import { referenceStudents, referenceDashboard } from './teacherReferenceData'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const riskStudents = ref([])

onMounted(loadRiskStudents)

async function loadRiskStudents() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherRiskStudents()
    riskStudents.value = data.length ? data : referenceDashboard.risk_students
  } catch (err) {
    riskStudents.value = referenceDashboard.risk_students
    error.value = err.response?.data?.detail || 'API 데이터 대신 reference 위험군 fallback을 표시합니다.'
  } finally {
    loading.value = false
  }
}

const displayedStudents = computed(() => riskStudents.value.length ? riskStudents.value : referenceDashboard.risk_students)
const classAverage = computed(() => referenceDashboard.class_avg)

function scoreValue(student, key) {
  return Number(student[key] ?? student.latest_metrics?.[key] ?? 0)
}

function studentCode(student) {
  return student.user_id_str || `STU${String(student.id || 0).padStart(3, '0')}`
}

function riskLabels(student) {
  const raw = Array.isArray(student.risk_types) ? student.risk_types : []
  if (raw.length) {
    return raw.map((type) => ({
      label: type === 'all' ? 'All Low' : type === 'pi' ? 'PI Low' : type === 'ui' ? 'UI Low' : type === 'oi' ? 'OI Low' : type,
      tone: type === 'pi' ? 'pi' : type === 'ui' ? 'ui' : type === 'oi' ? 'oi' : 'all',
    }))
  }
  if (scoreValue(student, 'aic') < 50 && scoreValue(student, 'pi') < 45 && scoreValue(student, 'ui') < 45) return [{ label: 'All Low', tone: 'all' }]
  if (scoreValue(student, 'pi') < 45) return [{ label: 'PI Low', tone: 'pi' }]
  if (scoreValue(student, 'ui') < 50) return [{ label: 'UI Low', tone: 'ui' }]
  if (scoreValue(student, 'oi') < 50) return [{ label: 'OI Low', tone: 'oi' }]
  return [{ label: 'AIC Low', tone: 'all' }]
}

const riskSummary = computed(() => {
  const students = displayedStudents.value
  const aicScores = students.map((student) => scoreValue(student, 'aic')).filter(Boolean)
  return {
    all: students.filter((student) => riskLabels(student).some((label) => label.tone === 'all')).length,
    pi: students.filter((student) => riskLabels(student).some((label) => label.tone === 'pi')).length,
    ui: students.filter((student) => riskLabels(student).some((label) => label.tone === 'ui')).length,
    dependency: students.filter((student) => aiDependency(student) >= 70).length,
    count: students.length,
    min: aicScores.length ? Math.min(...aicScores) : 0,
    avg: aicScores.length ? (aicScores.reduce((sum, score) => sum + score, 0) / aicScores.length).toFixed(1) : '0.0',
  }
})

function aiDependency(student) {
  const aic = scoreValue(student, 'aic')
  return Math.max(20, Math.min(82, Math.round(92 - aic * 0.45)))
}

const scatterConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: [
      { label: '위험군', data: displayedStudents.value.map((student) => ({ x: aiDependency(student), y: scoreValue(student, 'aic'), student })), backgroundColor: '#EF4444', pointRadius: 8, pointHoverRadius: 10 },
      { label: '주의', data: referenceStudents.slice(12, 16).map((student) => ({ x: aiDependency(student), y: student.aic, student })), backgroundColor: '#F97316', pointRadius: 6 },
      { label: '평균', data: referenceStudents.slice(5, 12).map((student) => ({ x: aiDependency(student), y: student.aic, student })), backgroundColor: '#3B82F6', pointRadius: 5 },
      { label: '우수', data: referenceStudents.slice(0, 5).map((student) => ({ x: aiDependency(student), y: student.aic, student })), backgroundColor: '#10B981', pointRadius: 6 },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    parsing: false,
    plugins: { legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10 } } } },
    scales: {
      x: { min: 15, max: 85, title: { display: true, text: 'AI 의존도 (%)' }, grid: { color: '#F3F4F6' } },
      y: { min: 30, max: 95, title: { display: true, text: 'AIC Score' }, grid: { color: '#F3F4F6' } },
    },
  },
}))

const riskBarConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: [...displayedStudents.value.map((student) => student.name), '반 평균'],
    datasets: [
      { label: 'PI', data: [...displayedStudents.value.map((student) => scoreValue(student, 'pi')), classAverage.value.pi], backgroundColor: 'rgba(59,130,246,0.75)', borderRadius: 4 },
      { label: 'UI', data: [...displayedStudents.value.map((student) => scoreValue(student, 'ui')), classAverage.value.ui], backgroundColor: 'rgba(249,115,22,0.75)', borderRadius: 4 },
      { label: 'OI', data: [...displayedStudents.value.map((student) => scoreValue(student, 'oi')), classAverage.value.oi], backgroundColor: 'rgba(16,185,129,0.75)', borderRadius: 4 },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10 } } } },
    scales: {
      y: { min: 0, max: 80, grid: { color: '#F3F4F6' } },
      x: { grid: { display: false } },
    },
  },
}))
</script>

<template>
  <AppLayout title="위험군 학생 관리" subtitle="AIC 50점 미만 또는 특정 지표 기준 이하 학생">
    <template #actions>
      <button class="btn btn-secondary btn-sm" type="button">CSV 내보내기</button>
      <button class="btn btn-danger btn-sm" type="button">일괄 피드백 전송</button>
    </template>

    <div v-if="error" class="alert alert-warning mb-4">{{ error }}</div>

    <section class="risk-hero">
      <div>
        <div class="rh-title">위험군 학생 관리</div>
        <div class="rh-sub">AIC 50점 미만 또는 특정 지표 기준 이하 학생</div>
        <div class="hero-tags">
          <span class="risk-tag risk-all">All Low ({{ riskSummary.all }}명)</span>
          <span class="risk-tag risk-pi">PI Low ({{ riskSummary.pi }}명)</span>
          <span class="risk-tag risk-ui">UI Low ({{ riskSummary.ui }}명)</span>
          <span class="risk-tag risk-dep">고의존도 ({{ riskSummary.dependency }}명)</span>
        </div>
      </div>
      <div class="rh-stats">
        <div class="rh-stat"><div class="rh-stat-val">{{ riskSummary.count }}</div><div class="rh-stat-label">위험군</div></div>
        <div class="rh-stat"><div class="rh-stat-val">{{ riskSummary.min }}</div><div class="rh-stat-label">최저 AIC</div></div>
        <div class="rh-stat"><div class="rh-stat-val">{{ riskSummary.avg }}</div><div class="rh-stat-label">위험군 평균</div></div>
      </div>
    </section>

    <div v-if="loading" class="card loading-state">불러오는 중...</div>
    <div v-else class="risk-card-grid">
      <article v-for="student in displayedStudents" :key="student.id" class="risk-card" @click="router.push(`/teacher/students/${student.id}`)">
        <div class="rc-header">
          <div class="rc-avatar">{{ student.name?.slice(0, 1) }}</div>
          <div>
            <div class="rc-name">{{ student.name }}</div>
            <div class="rc-id">{{ studentCode(student) }} · CS101</div>
          </div>
          <div class="rc-aic">{{ scoreValue(student, 'aic') }}</div>
        </div>
        <div class="rc-tags">
          <span v-for="label in riskLabels(student)" :key="label.label" class="risk-tag" :class="`risk-${label.tone}`">{{ label.label }}</span>
          <span v-if="aiDependency(student) >= 70" class="risk-tag risk-dep">고의존도 ({{ aiDependency(student) }}%)</span>
          <StatusBadge :score="student.aic" />
        </div>
        <div class="rc-bars">
          <div v-for="metric in ['pi', 'ui', 'oi']" :key="metric" class="rc-bar-item">
            <span class="rc-bar-label" :class="metric">{{ metric.toUpperCase() }}</span>
            <div class="rc-bar-track"><div class="rc-bar-fill" :class="metric" :style="{ width: `${scoreValue(student, metric)}%` }"></div></div>
            <span class="rc-bar-val" :class="metric">{{ scoreValue(student, metric) }}</span>
          </div>
        </div>
        <div class="rc-action">
          <button class="btn btn-danger btn-sm" type="button" @click.stop>피드백 작성</button>
          <button class="btn btn-secondary btn-sm" type="button" @click.stop="router.push(`/teacher/students/${student.id}`)">상세 보기</button>
        </div>
      </article>
    </div>

    <div class="grid-2 section-gap">
      <section class="card">
        <div class="card-header"><div><div class="card-title">Effort vs AI Dependency Scatter</div><div class="card-subtitle">X: AI 의존도, Y: AIC Score - 위험군 탐지</div></div></div>
        <div class="card-body"><div class="chart-box"><ScatterChart :config="scatterConfig" /></div></div>
      </section>
      <section class="card">
        <div class="card-header"><div><div class="card-title">위험군 AIC 비교</div><div class="card-subtitle">위험군 학생 vs 반 평균</div></div></div>
        <div class="card-body"><div class="chart-box"><BarChart :config="riskBarConfig" /></div></div>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.risk-hero {
  display: flex;
  justify-content: space-between;
  gap: var(--space-6);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, #FEF2F2 0%, #FFF7ED 100%);
  border: 1px solid #FECACA;
}
.rh-title { color: var(--color-danger); font-size: var(--font-size-3xl); font-weight: 800; line-height: 1.2; }
.rh-sub { margin-top: var(--space-1); color: var(--text-secondary); font-size: var(--font-size-sm); }
.hero-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-3); }
.rh-stats { display: grid; grid-template-columns: repeat(3, minmax(88px, 1fr)); gap: var(--space-3); min-width: 320px; }
.rh-stat { padding: var(--space-4); border-radius: var(--radius-lg); background: rgba(255,255,255,0.72); text-align: center; border: 1px solid rgba(239,68,68,0.14); }
.rh-stat-val { color: var(--color-danger); font-size: 28px; font-weight: 800; line-height: 1; }
.rh-stat-label { margin-top: var(--space-1); color: var(--text-muted); font-size: var(--font-size-xs); font-weight: 700; }
.risk-card-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
.risk-card { padding: var(--space-5); background: var(--bg-surface); border: 1px solid var(--border-light); border-left: 4px solid var(--color-danger); border-radius: var(--radius-xl); box-shadow: var(--shadow-sm); cursor: pointer; }
.risk-card:hover { box-shadow: var(--shadow-md); }
.rc-header { display: grid; grid-template-columns: 42px 1fr auto; align-items: center; gap: var(--space-3); }
.rc-avatar { display: grid; place-items: center; width: 42px; height: 42px; border-radius: var(--radius-full); background: var(--color-danger); color: white; font-weight: 800; }
.rc-name { color: var(--text-primary); font-weight: 800; }
.rc-id { color: var(--text-muted); font-size: var(--font-size-xs); }
.rc-aic { color: var(--color-danger); font-size: 30px; font-weight: 800; line-height: 1; }
.rc-tags { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2); margin: var(--space-4) 0; }
.risk-tag { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: var(--radius-full); font-size: var(--font-size-xs); font-weight: 700; }
.risk-all, .risk-dep { color: #B91C1C; background: #FEE2E2; }
.risk-pi { color: #1D4ED8; background: #DBEAFE; }
.risk-ui { color: #C2410C; background: #FFEDD5; }
.risk-oi { color: #047857; background: #D1FAE5; }
.rc-bars { display: grid; gap: var(--space-2); }
.rc-bar-item { display: grid; grid-template-columns: 32px 1fr 34px; align-items: center; gap: var(--space-2); }
.rc-bar-label, .rc-bar-val { font-size: var(--font-size-xs); font-weight: 800; text-align: right; }
.rc-bar-label.pi, .rc-bar-val.pi { color: var(--color-pi); }
.rc-bar-label.ui, .rc-bar-val.ui { color: var(--color-ui); }
.rc-bar-label.oi, .rc-bar-val.oi { color: var(--color-oi); }
.rc-bar-track { height: 7px; overflow: hidden; border-radius: var(--radius-full); background: var(--color-gray-100); }
.rc-bar-fill { height: 100%; border-radius: var(--radius-full); }
.rc-bar-fill.pi { background: var(--color-pi); }
.rc-bar-fill.ui { background: var(--color-ui); }
.rc-bar-fill.oi { background: var(--color-oi); }
.rc-action { display: flex; justify-content: flex-end; gap: var(--space-2); margin-top: var(--space-4); }
.section-gap { margin-top: var(--space-6); }
.chart-box { height: 240px; }
@media (max-width: 920px) {
  .risk-hero { flex-direction: column; }
  .rh-stats { min-width: 0; }
  .risk-card-grid, .grid-2 { grid-template-columns: 1fr; }
}
@media (max-width: 520px) {
  .rh-stats { grid-template-columns: 1fr; }
}
</style>

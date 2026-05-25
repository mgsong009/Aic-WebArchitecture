<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTeacherStore } from '@/stores/teacher'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { referenceActivities, referenceDashboard, scoreColor } from './teacherReferenceData'

const router = useRouter()
const teacherStore = useTeacherStore()
const loading = ref(true)
const error = ref('')

const distributionLabels = ['30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
const liveDashboard = computed(() => teacherStore.dashboard)
const hasLiveData = computed(() => {
  const data = liveDashboard.value
  if (!data) return false
  return data.trend?.length || data.risk_students?.length || data.top_students?.length || data.aic_distribution?.some((count) => count > 0)
})
const dashboard = computed(() => (hasLiveData.value ? liveDashboard.value : referenceDashboard))
const cls = computed(() => dashboard.value.cls || referenceDashboard.cls)
const classAvg = computed(() => ({ ...referenceDashboard.class_avg, ...(dashboard.value.class_avg || {}) }))
const riskStudents = computed(() => dashboard.value.risk_students?.length ? dashboard.value.risk_students : referenceDashboard.risk_students)
const topStudents = computed(() => {
  const source = dashboard.value.top_students?.length ? dashboard.value.top_students : referenceDashboard.top_students
  return [...source]
    .filter((student) => student.aic != null)
    .sort((a, b) => Number(b.aic || 0) - Number(a.aic || 0))
    .slice(0, 5)
})
const distribution = computed(() => dashboard.value.aic_distribution?.length ? dashboard.value.aic_distribution : referenceDashboard.aic_distribution)
const trend = computed(() => dashboard.value.trend?.length ? dashboard.value.trend : referenceDashboard.trend)
const analyzedCount = computed(() => dashboard.value.analyzed_count || cls.value.analyzed_count || 25)

onMounted(loadDashboard)

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    await teacherStore.fetchDashboard()
  } catch {
    error.value = '실시간 교사 데이터를 불러오지 못해 reference fallback을 표시합니다.'
  } finally {
    loading.value = false
  }
}

function goStudent(student) {
  router.push(`/teacher/students/${student.id || 6}`)
}

const distributionConfig = computed(() => ({
  type: 'bar',
  data: {
    labels: distributionLabels,
    datasets: [{
      label: '학생 수',
      data: distribution.value,
      backgroundColor: ['#FCA5A5', '#FDBA74', '#FDE68A', '#93C5FD', '#6EE7B7', '#A78BFA', '#D1D5DB'],
      borderRadius: 6,
    }],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#F3F4F6' }, ticks: { precision: 0, font: { size: 10 } } },
      x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    },
  },
}))

const trendConfig = computed(() => ({
  type: 'line',
  data: {
    labels: trend.value.map((point) => point.label),
    datasets: [
      { label: '반 평균 AIC', data: trend.value.map((point) => point.aic), borderColor: '#1E3A5F', backgroundColor: 'rgba(30,58,95,0.07)', borderWidth: 2.5, fill: true, tension: 0.4, pointRadius: 4 },
      { label: '상위 25%', data: trend.value.map((point) => point.top ?? point.aic + 12), borderColor: '#3B82F6', borderWidth: 1.5, borderDash: [4, 4], tension: 0.4, pointRadius: 0 },
      { label: '하위 25%', data: trend.value.map((point) => point.bottom ?? point.aic - 16), borderColor: '#EF4444', borderWidth: 1.5, borderDash: [4, 4], tension: 0.4, pointRadius: 0 },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true, position: 'top', labels: { font: { size: 10, family: 'Inter' }, boxWidth: 10 } } },
    scales: {
      y: { min: 30, max: 90, grid: { color: '#F3F4F6' }, ticks: { font: { size: 10 }, stepSize: 10 } },
      x: { grid: { display: false }, ticks: { font: { size: 11 } } },
    },
  },
}))

const metricItems = computed(() => [
  { label: 'PI', key: 'pi', color: 'var(--color-pi)', value: classAvg.value.pi },
  { label: 'UI', key: 'ui', color: 'var(--color-ui)', value: classAvg.value.ui },
  { label: 'OI', key: 'oi', color: 'var(--color-oi)', value: classAvg.value.oi },
  { label: 'TS', key: 'topic', color: 'var(--color-topic)', value: classAvg.value.topic },
  { label: 'AIC', key: 'aic', color: 'var(--color-aic)', value: classAvg.value.aic },
])
</script>

<template>
  <AppLayout title="Dashboard" :show-page-header="false">
    <div class="teacher-page animate-fade-in">
      <p v-if="error" class="fallback-note">{{ error }}</p>

      <section class="class-summary">
        <div>
          <div class="cs-label">현재 수업</div>
          <div class="cs-class">{{ cls.code || 'CS101' }} · {{ cls.name || '컴퓨터과학 개론' }}</div>
          <div class="cs-meta">Assignment #5 분석 완료 · 최종 업데이트: 오늘</div>
          <div class="cs-tags">
            <span>Teacher View</span>
            <span>분석 완료 {{ analyzedCount }}/{{ cls.student_count || 28 }}</span>
          </div>
        </div>
        <div class="cs-stats">
          <div class="cs-stat"><strong>{{ cls.student_count || 28 }}</strong><span>전체 학생</span></div>
          <div class="cs-stat success"><strong>{{ analyzedCount }}</strong><span>분석 완료</span></div>
          <div class="cs-stat warning"><strong>{{ dashboard.risk_count ?? 4 }}</strong><span>위험 학생</span></div>
          <div class="cs-stat"><strong>{{ classAvg.aic ?? '-' }}</strong><span>반 평균 AIC</span></div>
        </div>
      </section>

      <div class="kpi-grid stagger">
        <article class="kpi-card aic-card animate-fade-in-up">
          <div class="kpi-header"><div class="kpi-icon aic">AIC</div><span class="kpi-change up">+2.1</span></div>
          <div class="kpi-value">{{ classAvg.aic }}</div><div class="kpi-label">반 평균 AIC</div>
        </article>
        <article class="kpi-card pi-card animate-fade-in-up">
          <div class="kpi-header"><div class="kpi-icon pi">PI</div><span class="kpi-change up">+1.8</span></div>
          <div class="kpi-value pi-text">{{ classAvg.pi }}</div><div class="kpi-label">평균 PI</div>
        </article>
        <article class="kpi-card ui-card animate-fade-in-up">
          <div class="kpi-header"><div class="kpi-icon ui">UI</div><span class="kpi-change down">-0.5</span></div>
          <div class="kpi-value ui-text">{{ classAvg.ui }}</div><div class="kpi-label">평균 UI</div>
        </article>
        <article class="kpi-card oi-card animate-fade-in-up">
          <div class="kpi-header"><div class="kpi-icon oi">OI</div><span class="kpi-change up">+3.2</span></div>
          <div class="kpi-value oi-text">{{ classAvg.oi }}</div><div class="kpi-label">평균 OI</div>
        </article>
        <article class="kpi-card animate-fade-in-up risk-kpi">
          <div class="kpi-header"><div class="kpi-icon danger">!</div><span class="kpi-change down">주의</span></div>
          <div class="kpi-value danger-text">{{ dashboard.risk_count ?? riskStudents.length }}</div><div class="kpi-label">위험군 학생 수</div>
        </article>
      </div>

      <div class="dashboard-grid top-grid">
        <section class="card chart-panel">
          <div class="card-header"><div><div class="card-title">AIC 점수 분포</div><div class="card-subtitle">반 전체 히스토그램</div></div></div>
          <div class="card-body chart-body"><BarChart :config="distributionConfig" /></div>
        </section>

        <section class="card">
          <div class="card-header"><div><div class="card-title">지표 평균</div><div class="card-subtitle">반 전체 평균</div></div></div>
          <div class="card-body metric-stack">
            <div v-for="item in metricItems" :key="item.key">
              <div class="metric-row"><strong :style="{ color: item.color }">{{ item.label }}</strong><span>{{ item.value }}</span></div>
              <div class="score-bar-track"><div class="score-bar-fill" :style="{ width: `${item.value || 0}%`, background: item.color }"></div></div>
            </div>
          </div>
        </section>

        <section class="risk-summary">
          <div class="rs-title">위험군 학생 ({{ riskStudents.length }}명)</div>
          <button v-for="student in riskStudents" :key="student.id || student.name" class="rs-item" type="button" @click="goStudent(student)">
            <span class="rs-avatar">{{ student.name?.slice(0, 1) }}</span>
            <span class="rs-name">{{ student.name }}</span>
            <strong class="rs-score">{{ student.aic ?? '-' }}</strong>
          </button>
          <button class="link-button danger-text" type="button" @click="router.push('/teacher/risk')">전체 위험군 보기 →</button>
        </section>
      </div>

      <div class="dashboard-grid mid-grid">
        <section class="card chart-panel">
          <div class="card-header">
            <div><div class="card-title">반 전체 AIC 추이</div><div class="card-subtitle">과제별 평균 AIC 변화</div></div>
            <button class="link-button" type="button" @click="router.push('/teacher/analytics/assignment')">과제 분석 →</button>
          </div>
          <div class="card-body chart-body"><LineChart :config="trendConfig" /></div>
        </section>

        <section class="card">
          <div class="card-header"><div><div class="card-title">최근 활동</div><div class="card-subtitle">오늘 기준</div></div></div>
          <div class="card-body activity-feed">
            <div v-for="item in referenceActivities" :key="`${item.name}-${item.time}`" class="activity-item">
              <span class="act-dot" :style="{ background: item.color }"></span>
              <span class="act-text"><strong>{{ item.name }}</strong> {{ item.text }}</span>
              <span class="act-time">{{ item.time }}</span>
            </div>
          </div>
        </section>
      </div>

      <div class="grid-2">
        <section class="card">
          <div class="card-header"><div><div class="card-title">상위 5명</div><div class="card-subtitle">AIC 점수 순</div></div><button class="link-button" type="button" @click="router.push('/teacher/students')">전체 보기 →</button></div>
          <div class="card-body table-body">
            <table class="mini-table">
              <thead><tr><th>순위</th><th>학생</th><th>AIC</th><th>PI</th><th>UI</th><th>OI</th><th>상태</th></tr></thead>
              <tbody>
                <tr v-for="(student, index) in topStudents" :key="student.id || student.name" @click="goStudent(student)">
                  <td>{{ index + 1 }}</td><td>{{ student.name }}</td>
                  <td :style="{ color: scoreColor(student.aic) }"><strong>{{ student.aic }}</strong></td>
                  <td>{{ student.pi ?? '-' }}</td><td>{{ student.ui ?? '-' }}</td><td>{{ student.oi ?? '-' }}</td>
                  <td><StatusBadge :score="student.aic" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="card">
          <div class="card-header"><div><div class="card-title">주의 필요 학생</div><div class="card-subtitle">AIC 50점 미만</div></div><button class="link-button danger-text" type="button" @click="router.push('/teacher/risk')">위험군 보기 →</button></div>
          <div class="card-body table-body">
            <table class="mini-table">
              <thead><tr><th>학생</th><th>AIC</th><th>PI</th><th>UI</th><th>OI</th><th>위험유형</th></tr></thead>
              <tbody>
                <tr v-for="student in riskStudents" :key="student.id || student.name" @click="goStudent(student)">
                  <td>{{ student.name }}</td><td class="danger-text"><strong>{{ student.aic }}</strong></td>
                  <td>{{ student.pi ?? '-' }}</td><td>{{ student.ui ?? '-' }}</td><td>{{ student.oi ?? '-' }}</td>
                  <td><span class="badge" :class="student.aic < 45 ? 'badge-danger' : 'badge-warning'">{{ student.risk_types?.join(', ') || 'AIC Low' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.teacher-page { display: grid; gap: var(--space-6); }
.fallback-note { padding: var(--space-3) var(--space-4); background: var(--color-ui-pale); border: 1px solid rgba(249, 115, 22, 0.2); border-radius: var(--radius-lg); color: var(--text-secondary); font-size: var(--text-sm); }
.class-summary { background: linear-gradient(135deg, #1a2438, #2d3748); border-radius: var(--radius-xl); padding: 24px 28px; display: flex; align-items: center; justify-content: space-between; gap: 20px; color: white; overflow: hidden; position: relative; }
.class-summary::before { content: ''; position: absolute; right: -40px; top: -40px; width: 180px; height: 180px; background: rgba(249, 115, 22, 0.08); border-radius: 50%; }
.cs-label { font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 0.8px; }
.cs-class { font-size: 20px; font-weight: 800; letter-spacing: -0.3px; }
.cs-meta { font-size: 12px; color: rgba(255,255,255,0.55); }
.cs-tags { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px; }
.cs-tags span { padding: 4px 10px; background: rgba(249,115,22,0.2); border-radius: 999px; font-size: 11px; font-weight: 700; color: #FDBA74; }
.cs-tags span + span { background: rgba(16,185,129,0.15); color: #6EE7B7; }
.cs-stats { display: flex; gap: 32px; z-index: 1; }
.cs-stat { text-align: center; }
.cs-stat strong { display: block; font-size: 28px; line-height: 1; }
.cs-stat span { font-size: 10px; color: rgba(255,255,255,0.45); text-transform: uppercase; }
.cs-stat.success strong { color: #6EE7B7; }
.cs-stat.warning strong { color: #FDBA74; }
.pi-text { color: var(--color-pi); }
.ui-text { color: var(--color-ui); }
.oi-text { color: var(--color-oi); }
.danger-text { color: var(--color-danger); }
.kpi-icon { font-size: 11px; font-weight: 800; }
.kpi-icon.danger { background: #FEF2F2; color: var(--color-danger); }
.risk-kpi::before { background: transparent; }
.dashboard-grid { display: grid; gap: var(--space-4); }
.top-grid { grid-template-columns: 2fr 1fr 1fr; }
.mid-grid { grid-template-columns: 2fr 1fr; }
.chart-body { height: 240px; }
.metric-stack { display: grid; gap: 14px; }
.metric-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
.risk-summary { background: #FFF5F5; border: 1px solid #FECACA; border-radius: var(--radius-xl); padding: 20px; display: grid; gap: 6px; align-content: start; }
.rs-title { font-size: 12px; font-weight: 800; color: #B91C1C; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.rs-item { display: flex; align-items: center; gap: 8px; padding: 6px 8px; background: white; border: 1px solid #FEE2E2; border-radius: var(--radius-md); text-align: left; }
.rs-avatar { width: 24px; height: 24px; border-radius: 50%; background: #FCA5A5; display: grid; place-items: center; font-size: 10px; font-weight: 800; color: #B91C1C; }
.rs-name { flex: 1; font-size: 12px; font-weight: 700; color: var(--text-primary); }
.rs-score { font-size: 14px; color: var(--color-danger); }
.link-button { color: var(--color-pi); font-size: 12px; font-weight: 700; }
.activity-feed { padding: 8px 12px; }
.activity-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: var(--radius-md); }
.activity-item:hover { background: var(--color-gray-50); }
.act-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.act-text { flex: 1; font-size: 12px; color: var(--text-secondary); }
.act-text strong { color: var(--text-primary); }
.act-time { font-size: 11px; color: var(--text-muted); }
.table-body { padding: 0; overflow-x: auto; }
.mini-table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 540px; }
.mini-table th { font-size: 10px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; padding: 8px 10px; text-align: left; background: var(--color-gray-50); }
.mini-table td { padding: 9px 10px; border-bottom: 1px solid var(--color-gray-50); }
.mini-table tr { cursor: pointer; }
.mini-table tr:hover td { background: var(--color-gray-50); }
@media (max-width: 1100px) { .top-grid, .mid-grid { grid-template-columns: 1fr; } .cs-stats { gap: 18px; } }
@media (max-width: 768px) { .class-summary { align-items: flex-start; flex-direction: column; } .cs-stats { width: 100%; display: grid; grid-template-columns: repeat(2, 1fr); } }
</style>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTeacherStore } from '@/stores/teacher'
import AppLayout from '@/components/layout/AppLayout.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'

const router = useRouter()
const teacherStore = useTeacherStore()
const loading = ref(true)
const error = ref('')

const distributionLabels = ['<40', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
const dashboard = computed(() => teacherStore.dashboard || null)
const cls = computed(() => dashboard.value?.cls || {})
const classAvg = computed(() => dashboard.value?.class_avg || {})
const trend = computed(() => dashboard.value?.trend || [])
const distribution = computed(() =>
  dashboard.value?.aic_distribution
    ? distributionLabels.map((_, index) => Number(dashboard.value.aic_distribution[index] || 0))
    : []
)
const riskStudents = computed(() =>
  dashboard.value?.risk_students || []
)
const topStudents = computed(() =>
  dashboard.value?.top_students || []
)
const hasTrend = computed(() => trend.value.some((point) => point.aic !== null || point.pi !== null))
const hasDistribution = computed(() => distribution.value.some((count) => count > 0))
const hasDashboardData = computed(() =>
  hasTrend.value
  || hasDistribution.value
  || riskStudents.value.length > 0
  || topStudents.value.length > 0
  || Object.values(classAvg.value).some((value) => value !== null && value !== undefined)
)
const subtitle = computed(() => {
  if (!dashboard.value) return ''
  const code = cls.value.code || ''
  const name = cls.value.name || ''
  const summary = `${cls.value.student_count ?? 0}명 · 과제 ${cls.value.assignment_count ?? 0}개`
  return [code, name, summary].filter(Boolean).join(' ')
})

onMounted(async () => {
  await loadDashboard()
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    await teacherStore.fetchDashboard()
  } catch {
    error.value = '교사 대시보드를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const trendConfig = computed(() => {
  if (!hasTrend.value) return null
  return {
    type: 'line',
    data: {
      labels: trend.value.map((point) => point.label),
      datasets: [
        {
          label: 'AIC 평균',
          data: trend.value.map((point) => point.aic),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30,58,95,0.08)',
          fill: true,
          tension: 0.3,
          spanGaps: true,
        },
        {
          label: 'PI 평균',
          data: trend.value.map((point) => point.pi),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59,130,246,0.08)',
          tension: 0.3,
          spanGaps: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { min: 0, max: 100 } },
    },
  }
})

const distributionConfig = computed(() => {
  if (!hasDistribution.value) return null
  return {
    type: 'bar',
    data: {
      labels: distributionLabels,
      datasets: [
        {
          label: '학생 수',
          data: distribution.value,
          backgroundColor: '#1E3A5F',
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  }
})
</script>

<template>
  <AppLayout title="교사 대시보드" :subtitle="subtitle">
    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="118px" />
      <LoadingSkeleton height="320px" />
      <LoadingSkeleton height="220px" />
    </div>

    <div v-else-if="error" class="card card-body empty-state">
      <strong>{{ error }}</strong>
      <button class="btn btn-secondary btn-sm mt-4" type="button" @click="loadDashboard">다시 시도</button>
    </div>

    <div v-else-if="!dashboard || !hasDashboardData" class="card card-body empty-state">
      아직 대시보드에 표시할 분석 데이터가 없습니다.
    </div>

    <div v-else class="dashboard-page">
      <div class="kpi-grid">
        <KpiCard label="반 평균 AIC" :value="classAvg.aic" color="var(--color-aic)" />
        <KpiCard label="반 평균 PI" :value="classAvg.pi" color="var(--color-pi)" />
        <KpiCard label="반 평균 UI" :value="classAvg.ui" color="var(--color-ui)" />
        <KpiCard label="반 평균 OI" :value="classAvg.oi" color="var(--color-oi)" />
        <KpiCard label="위험군" :value="dashboard.risk_count ?? 0" color="var(--color-danger)" unit="명" />
        <KpiCard label="우수" :value="dashboard.excellent_count ?? 0" color="var(--color-success)" unit="명" />
      </div>

      <div class="grid-2">
        <section class="card card-body chart-card">
          <h3>성장 추세</h3>
          <LineChart v-if="trendConfig" :config="trendConfig" />
          <div v-else class="empty-state compact">성장 추세 데이터가 없습니다.</div>
        </section>

        <section class="card card-body chart-card">
          <h3>AIC 분포</h3>
          <BarChart v-if="distributionConfig" :config="distributionConfig" />
          <div v-else class="empty-state compact">AIC 분포 데이터가 없습니다.</div>
        </section>
      </div>

      <div class="grid-2">
        <section class="card card-body">
          <div class="section-heading">
            <h3>위험군 학생</h3>
            <button class="btn btn-ghost btn-sm" type="button" @click="router.push('/teacher/risk')">전체 보기</button>
          </div>
          <div v-if="riskStudents.length">
            <div
              v-for="student in riskStudents"
              :key="student.id"
              class="interactive-row"
              @click="router.push(`/teacher/students/${student.id}`)"
            >
              <div>
                <strong>{{ student.name }}</strong>
                <div class="risk-types">{{ student.risk_types?.join(', ') || 'AIC' }}</div>
              </div>
              <div class="row-right">
                <span>{{ student.aic ?? '-' }}</span>
                <StatusBadge :score="student.aic" />
              </div>
            </div>
          </div>
          <div v-else class="empty-state compact">현재 위험군 학생이 없습니다.</div>
        </section>

        <section class="card card-body">
          <div class="section-heading">
            <h3>상위 학생</h3>
            <button class="btn btn-ghost btn-sm" type="button" @click="router.push('/teacher/students')">학생 목록</button>
          </div>
          <div v-if="topStudents.length">
            <div
              v-for="student in topStudents"
              :key="student.id"
              class="interactive-row"
              @click="router.push(`/teacher/students/${student.id}`)"
            >
              <div>
                <strong>{{ student.name }}</strong>
                <div class="risk-types">PI {{ student.pi ?? '-' }} · UI {{ student.ui ?? '-' }} · OI {{ student.oi ?? '-' }}</div>
              </div>
              <div class="row-right">
                <span>{{ student.aic ?? '-' }}</span>
                <StatusBadge :score="student.aic" />
              </div>
            </div>
          </div>
          <div v-else class="empty-state compact">상위 학생 데이터가 없습니다.</div>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-wrap,
.dashboard-page {
  display: grid;
  gap: var(--space-4);
}

.chart-card {
  min-height: 340px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

h3 {
  margin: 0;
}

.risk-types {
  margin-top: 2px;
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.row-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  white-space: nowrap;
}

.compact {
  padding: var(--space-6);
}

@media (max-width: 640px) {
  .section-heading,
  .interactive-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .row-right {
    justify-content: space-between;
    width: 100%;
  }
}
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import DonutChart from '@/components/common/DonutChart.vue'
import MetricBars from '@/components/common/MetricBars.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'

const router = useRouter()
const dashboard = ref(null)
const loading = ref(true)
const error = ref('')

const subMetrics = [
  { key: 'pi', label: 'PI', color: '#3B82F6' },
  { key: 'ui', label: 'UI', color: '#F97316' },
  { key: 'oi', label: 'OI', color: '#10B981' },
  { key: 'topic', label: 'Topic', color: '#8B5CF6' },
]

function normalizeDashboard(data = {}) {
  return {
    student: data.student || {},
    latest_metrics: data.latest_metrics || {},
    latest_delta: data.latest_delta || {},
    class_avg: data.class_avg || {},
    rank: data.rank ?? null,
    total_students: data.total_students ?? 0,
    trend: Array.isArray(data.trend) ? data.trend : [],
    recent_assignments: Array.isArray(data.recent_assignments) ? data.recent_assignments : [],
    metrics_history: Array.isArray(data.metrics_history) ? data.metrics_history : [],
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/student/dashboard')
    dashboard.value = normalizeDashboard(res.data)
  } catch (e) {
    error.value = '대시보드 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})

const student = computed(() => dashboard.value?.student || {})
const latestMetrics = computed(() => dashboard.value?.latest_metrics || {})
const latestDelta = computed(() => dashboard.value?.latest_delta || {})
const classAvg = computed(() => dashboard.value?.class_avg || {})
const trend = computed(() => dashboard.value?.trend || [])
const metricsHistory = computed(() => dashboard.value?.metrics_history || [])
const recentAssignments = computed(() => dashboard.value?.recent_assignments || [])
const hasAnyMetrics = computed(() => Object.values(latestMetrics.value).some((value) => value !== null && value !== undefined))
const hasTrend = computed(() => trend.value.length > 0)
const hasMetricHistory = computed(() => metricsHistory.value.length > 0)
const hasRecentAssignments = computed(() => recentAssignments.value.length > 0)

const lineConfig = computed(() => {
  if (!hasTrend.value) return null
  const labels = trend.value.map((t) => t.label)
  return {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '나의 AIC',
          data: trend.value.map((t) => t.aic),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30,58,95,0.08)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
        },
        {
          label: '반 평균',
          data: trend.value.map((t) => t.class_avg),
          borderColor: '#94a3b8',
          borderDash: [5, 5],
          tension: 0.3,
          fill: false,
          pointRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      scales: { y: { min: 0, max: 100 } },
      plugins: { legend: { position: 'bottom' } },
    },
  }
})

const barConfig = computed(() => {
  if (!hasMetricHistory.value) return null
  const labels = metricsHistory.value.map((h) => h.label)
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'PI', data: metricsHistory.value.map((h) => h.pi), backgroundColor: '#3B82F6' },
        { label: 'UI', data: metricsHistory.value.map((h) => h.ui), backgroundColor: '#F97316' },
        { label: 'OI', data: metricsHistory.value.map((h) => h.oi), backgroundColor: '#10B981' },
      ],
    },
    options: {
      responsive: true,
      scales: { y: { min: 0, max: 100 } },
      plugins: { legend: { position: 'bottom' } },
    },
  }
})
</script>

<template>
  <AppLayout title="내 대시보드" :subtitle="dashboard ? `${student.class_code || '소속 반'} 최신 분석` : ''">
    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="160px" />
      <LoadingSkeleton height="380px" />
    </div>

    <div v-else-if="error" class="card card-body empty-state">
      <strong>{{ error }}</strong>
      <button class="btn btn-secondary btn-sm mt-4" type="button" @click="router.go(0)">다시 시도</button>
    </div>

    <div v-else-if="dashboard">
      <div class="hero-banner">
        <div>
          <div class="hero-greeting">안녕하세요, {{ student.name || '학생' }}님</div>
          <div class="hero-sub">{{ student.class_code || '반 정보 없음' }}</div>
        </div>
        <div class="hero-score">
          <div class="score-big">{{ latestMetrics.aic ?? '-' }}</div>
          <div class="score-label">AIC</div>
          <div v-if="dashboard.rank" class="score-rank">
            {{ dashboard.rank }}위 / {{ dashboard.total_students }}명
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <KpiCard label="AIC 종합" :value="latestMetrics.aic" :delta="latestDelta.aic" color="var(--color-aic)" />
        <KpiCard label="PI" :value="latestMetrics.pi" :delta="latestDelta.pi" color="var(--color-pi)" />
        <KpiCard label="UI" :value="latestMetrics.ui" :delta="latestDelta.ui" color="var(--color-ui)" />
        <KpiCard label="OI" :value="latestMetrics.oi" :delta="latestDelta.oi" color="var(--color-oi)" />
        <KpiCard label="Topic" :value="latestMetrics.topic" color="var(--color-topic)" />
      </div>

      <div v-if="!hasAnyMetrics && !hasTrend && !hasRecentAssignments" class="card card-body empty-state">
        아직 분석된 제출 데이터가 없습니다. 과제를 제출하면 이곳에 AIC 지표와 성장 추이가 표시됩니다.
      </div>

      <div class="grid-3 mb-4">
        <div class="card card-body chart-card">
          <h3 class="chart-title">AIC 도넛</h3>
          <div class="donut-row">
            <DonutChart :score="latestMetrics.aic || 0" color="var(--color-aic)" label="AIC" :size="130" />
            <div class="donut-details">
              <div v-for="m in subMetrics" :key="m.key" class="metric-line">
                <span class="dot" :style="{ background: m.color }"></span>
                <span>{{ m.label }}</span>
                <strong>{{ latestMetrics[m.key] ?? '-' }}</strong>
              </div>
            </div>
          </div>
        </div>

        <div class="card card-body chart-card">
          <h3 class="chart-title">나와 반 평균 비교</h3>
          <MetricBars
            :pi="latestMetrics.pi"
            :ui="latestMetrics.ui"
            :oi="latestMetrics.oi"
            :topic="latestMetrics.topic"
            :compare-values="classAvg"
          />
        </div>

        <div class="card card-body chart-card">
          <h3 class="chart-title">최근 과제</h3>
          <div v-if="hasRecentAssignments" class="recent-list">
            <div
              v-for="a in recentAssignments"
              :key="a.id"
              class="interactive-row"
              @click="router.push(`/student/assignments/${a.id}`)"
            >
              <div class="recent-title">{{ a.title }}</div>
              <div class="recent-meta">
                <span>{{ a.submitted_at || '-' }}</span>
                <StatusBadge :score="a.aic" />
              </div>
            </div>
          </div>
          <div v-else class="empty-state compact">최근 과제가 없습니다.</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card card-body chart-card" v-if="lineConfig">
          <h3 class="chart-title">AIC 성장 추이</h3>
          <LineChart :config="lineConfig" />
        </div>
        <div v-else class="card card-body chart-card empty-state compact">성장 추이 데이터가 없습니다.</div>
        <div class="card card-body chart-card" v-if="barConfig">
          <h3 class="chart-title">PI UI OI 추이</h3>
          <BarChart :config="barConfig" />
        </div>
        <div v-else class="card card-body chart-card empty-state compact">세부 지표 추이 데이터가 없습니다.</div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-wrap {
  display: grid;
  gap: 1rem;
}

.hero-banner {
  background: linear-gradient(135deg, var(--color-aic), var(--color-aic-light));
  border-radius: var(--radius-xl);
  padding: var(--space-6) var(--space-8);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
  box-shadow: var(--shadow-md);
}

.hero-greeting {
  font-size: var(--text-lg);
  font-weight: 600;
}

.hero-sub {
  opacity: 0.75;
  font-size: var(--text-sm);
}

.score-big {
  font-size: 2.8rem;
  font-weight: 800;
  text-align: center;
}

.score-label,
.score-rank {
  text-align: center;
  font-size: var(--text-xs);
  opacity: 0.8;
}

.chart-title {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: 0.9rem;
}

.donut-row {
  display: flex;
  gap: 1.2rem;
  align-items: center;
}

.donut-details {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.metric-line {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: var(--text-sm);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.recent-title {
  font-size: var(--text-sm);
  font-weight: 500;
}

.recent-meta {
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.compact {
  padding: var(--space-6);
}

@media (max-width: 1200px) {
  .hero-banner {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>

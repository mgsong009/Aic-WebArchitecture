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

const subMetrics = [
  { key: 'pi', label: 'PI', color: '#3B82F6' },
  { key: 'ui', label: 'UI', color: '#F97316' },
  { key: 'oi', label: 'OI', color: '#10B981' },
  { key: 'topic', label: 'Topic', color: '#8B5CF6' },
]

onMounted(async () => {
  try {
    const res = await api.get('/student/dashboard')
    dashboard.value = res.data
  } finally {
    loading.value = false
  }
})

const lineConfig = computed(() => {
  if (!dashboard.value) return null
  const labels = dashboard.value.trend.map((t) => t.label)
  return {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '나의 AIC',
          data: dashboard.value.trend.map((t) => t.aic),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30,58,95,0.08)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
        },
        {
          label: '반 평균',
          data: dashboard.value.trend.map((t) => t.class_avg),
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
  if (!dashboard.value) return null
  const labels = dashboard.value.metrics_history.map((h) => h.label)
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'PI', data: dashboard.value.metrics_history.map((h) => h.pi), backgroundColor: '#3B82F6' },
        { label: 'UI', data: dashboard.value.metrics_history.map((h) => h.ui), backgroundColor: '#F97316' },
        { label: 'OI', data: dashboard.value.metrics_history.map((h) => h.oi), backgroundColor: '#10B981' },
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
  <AppLayout title="내 대시보드" :subtitle="dashboard ? `${dashboard.student.class_code} 최신 분석` : ''">
    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="160px" />
      <LoadingSkeleton height="380px" />
    </div>

    <div v-else-if="dashboard">
      <div class="hero-banner">
        <div>
          <div class="hero-greeting">안녕하세요, {{ dashboard.student.name }} 학생</div>
          <div class="hero-sub">{{ dashboard.student.class_code }}</div>
        </div>
        <div class="hero-score">
          <div class="score-big">{{ dashboard.latest_metrics.aic ?? '-' }}</div>
          <div class="score-label">AIC</div>
          <div v-if="dashboard.rank" class="score-rank">
            {{ dashboard.rank }}위 / {{ dashboard.total_students }}명
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <KpiCard label="AIC 종합" :value="dashboard.latest_metrics.aic" :delta="dashboard.latest_delta.aic" color="var(--color-aic)" />
        <KpiCard label="PI" :value="dashboard.latest_metrics.pi" :delta="dashboard.latest_delta.pi" color="var(--color-pi)" />
        <KpiCard label="UI" :value="dashboard.latest_metrics.ui" :delta="dashboard.latest_delta.ui" color="var(--color-ui)" />
        <KpiCard label="OI" :value="dashboard.latest_metrics.oi" :delta="dashboard.latest_delta.oi" color="var(--color-oi)" />
        <KpiCard label="Topic" :value="dashboard.latest_metrics.topic" color="var(--color-topic)" />
      </div>

      <div class="chart-grid">
        <div class="chart-card">
          <h3 class="chart-title">AIC 도넛</h3>
          <div class="donut-row">
            <DonutChart :score="dashboard.latest_metrics.aic || 0" color="var(--color-aic)" label="AIC" :size="130" />
            <div class="donut-details">
              <div v-for="m in subMetrics" :key="m.key" class="metric-line">
                <span class="dot" :style="{ background: m.color }"></span>
                <span>{{ m.label }}</span>
                <strong>{{ dashboard.latest_metrics[m.key] ?? '-' }}</strong>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">나와 반 평균 비교</h3>
          <MetricBars
            :pi="dashboard.latest_metrics.pi"
            :ui="dashboard.latest_metrics.ui"
            :oi="dashboard.latest_metrics.oi"
            :topic="dashboard.latest_metrics.topic"
            :compare-values="dashboard.class_avg"
          />
        </div>

        <div class="chart-card">
          <h3 class="chart-title">최근 과제</h3>
          <div class="recent-list">
            <div
              v-for="a in dashboard.recent_assignments"
              :key="a.id"
              class="recent-item"
              @click="router.push(`/student/assignments/${a.id}`)"
            >
              <div class="recent-title">{{ a.title }}</div>
              <div class="recent-meta">
                <span>{{ a.submitted_at || '-' }}</span>
                <StatusBadge :score="a.aic" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row-grid">
        <div class="chart-card" v-if="lineConfig">
          <h3 class="chart-title">AIC 성장 추이</h3>
          <LineChart :config="lineConfig" />
        </div>
        <div class="chart-card" v-if="barConfig">
          <h3 class="chart-title">PI UI OI 추이</h3>
          <BarChart :config="barConfig" />
        </div>
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
  background: linear-gradient(135deg, #1e3a5f, #1a4a3a);
  border-radius: var(--radius-lg);
  padding: 1.5rem 2rem;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.row-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.chart-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.2rem;
  box-shadow: var(--shadow-sm);
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
  gap: 0.5rem;
}

.recent-item {
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-md);
  padding: 0.7rem;
  cursor: pointer;
}

.recent-item:hover {
  background: #f9fafb;
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

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-grid,
  .row-grid {
    grid-template-columns: 1fr;
  }
}
</style>

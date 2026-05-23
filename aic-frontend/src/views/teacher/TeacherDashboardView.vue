<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useTeacherStore } from '@/stores/teacher'
import AppLayout from '@/components/layout/AppLayout.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'

const router = useRouter()
const teacherStore = useTeacherStore()
const loading = ref(true)
const dashboard = ref(null)

onMounted(async () => {
  try {
    await teacherStore.fetchDashboard()
    dashboard.value = teacherStore.dashboard
  } finally {
    loading.value = false
  }
})

const trendConfig = computed(() => {
  if (!dashboard.value) return null
  return {
    type: 'line',
    data: {
      labels: dashboard.value.trend.map((t) => t.label),
      datasets: [
        {
          label: 'AIC 평균',
          data: dashboard.value.trend.map((t) => t.aic),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30,58,95,0.08)',
          fill: true,
          tension: 0.3,
        },
        {
          label: 'PI 평균',
          data: dashboard.value.trend.map((t) => t.pi),
          borderColor: '#3B82F6',
          tension: 0.3,
        },
      ],
    },
    options: { responsive: true, scales: { y: { min: 0, max: 100 } } },
  }
})

const distributionConfig = computed(() => {
  if (!dashboard.value) return null
  return {
    type: 'bar',
    data: {
      labels: ['<40', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'],
      datasets: [
        {
          label: '학생 수',
          data: dashboard.value.aic_distribution,
          backgroundColor: '#1E3A5F',
        },
      ],
    },
    options: { responsive: true },
  }
})
</script>

<template>
  <AppLayout title="교사 대시보드" :subtitle="dashboard ? `${dashboard.cls.code} ${dashboard.cls.name}` : ''">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="dashboard">
      <div class="kpi-grid">
        <KpiCard label="반 평균 AIC" :value="dashboard.class_avg.aic" color="var(--color-aic)" />
        <KpiCard label="반 평균 PI" :value="dashboard.class_avg.pi" color="var(--color-pi)" />
        <KpiCard label="반 평균 UI" :value="dashboard.class_avg.ui" color="var(--color-ui)" />
        <KpiCard label="반 평균 OI" :value="dashboard.class_avg.oi" color="var(--color-oi)" />
        <KpiCard label="위험군 수" :value="dashboard.risk_count" color="#dc2626" />
      </div>

      <div class="grid">
        <div class="card">
          <h3>클래스 추이</h3>
          <LineChart v-if="trendConfig" :config="trendConfig" />
        </div>
        <div class="card">
          <h3>AIC 분포</h3>
          <BarChart v-if="distributionConfig" :config="distributionConfig" />
        </div>
      </div>

      <div class="grid">
        <div class="card">
          <h3>위험군 학생</h3>
          <div v-for="s in dashboard.risk_students" :key="s.id" class="row" @click="router.push(`/teacher/students/${s.id}`)">
            <span>{{ s.name }}</span>
            <div class="row-right">
              <span>{{ s.aic ?? '-' }}</span>
              <StatusBadge :score="s.aic" />
            </div>
          </div>
        </div>
        <div class="card">
          <h3>우수 학생</h3>
          <div v-for="s in dashboard.top_students" :key="s.id" class="row" @click="router.push(`/teacher/students/${s.id}`)">
            <span>{{ s.name }}</span>
            <div class="row-right">
              <span>{{ s.aic ?? '-' }}</span>
              <StatusBadge :score="s.aic" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
}

.row {
  padding: var(--space-3);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-2);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}

.row:hover {
  background: var(--color-gray-50);
  border-color: var(--border-default);
}

.row-right {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

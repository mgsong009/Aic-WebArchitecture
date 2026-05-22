<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import LineChart from '@/components/charts/LineChart.vue'
import RadarChart from '@/components/charts/RadarChart.vue'

const loading = ref(true)
const growth = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/student/growth')
    growth.value = data
  } finally {
    loading.value = false
  }
})

const trendConfig = computed(() => {
  if (!growth.value) return null
  const labels = growth.value.assignments.map((a) => a.label)
  return {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'AIC',
          data: growth.value.assignments.map((a) => a.aic),
          borderColor: '#1E3A5F',
          tension: 0.3,
        },
        {
          label: '반 평균 AIC',
          data: growth.value.class_avg_trend.map((a) => a.aic),
          borderColor: '#94a3b8',
          borderDash: [5, 5],
          tension: 0.3,
        },
      ],
    },
    options: { responsive: true, scales: { y: { min: 0, max: 100 } } },
  }
})

const radarConfig = computed(() => {
  if (!growth.value?.assignments?.length) return null
  const latest = growth.value.assignments[growth.value.assignments.length - 1]
  return {
    type: 'radar',
    data: {
      labels: ['PI', 'UI', 'OI', 'Topic'],
      datasets: [
        {
          label: latest.title,
          data: [latest.pi || 0, latest.ui || 0, latest.oi || 0, latest.topic || 0],
          backgroundColor: 'rgba(30,58,95,0.12)',
          borderColor: '#1E3A5F',
        },
      ],
    },
    options: { scales: { r: { min: 0, max: 100 } } },
  }
})
</script>

<template>
  <AppLayout title="성장 분석" subtitle="과제별 성장 추이와 최신 프로파일">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="growth" class="grid">
      <div class="card">
        <h3>AIC 추이</h3>
        <LineChart v-if="trendConfig" :config="trendConfig" />
      </div>
      <div class="card">
        <h3>최신 지표 레이더</h3>
        <RadarChart v-if="radarConfig" :config="radarConfig" />
      </div>
      <div class="card full">
        <h3>과제별 점수</h3>
        <table class="table">
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
            <tr v-for="a in growth.assignments" :key="a.assignment_id">
              <td>{{ a.title }}</td>
              <td>{{ a.aic ?? '-' }}</td>
              <td>{{ a.pi ?? '-' }}</td>
              <td>{{ a.ui ?? '-' }}</td>
              <td>{{ a.oi ?? '-' }}</td>
              <td>{{ a.topic ?? '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.2rem;
  box-shadow: var(--shadow-sm);
}

.full {
  grid-column: 1 / -1;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.table th,
.table td {
  border-bottom: 1px solid #e5e7eb;
  padding: 0.6rem;
  text-align: left;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

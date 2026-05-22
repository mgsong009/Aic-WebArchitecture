<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import ScatterChart from '@/components/charts/ScatterChart.vue'

const loading = ref(true)
const analytics = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/teacher/analytics/advanced')
    analytics.value = data
  } finally {
    loading.value = false
  }
})

const scatterConfig = computed(() => {
  if (!analytics.value) return null
  return {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'PI vs UI',
          data: analytics.value.scatter_data.map((d) => ({ x: d.pi, y: d.ui })),
          backgroundColor: '#3B82F6',
        },
        {
          label: 'PI vs OI',
          data: analytics.value.scatter_data.map((d) => ({ x: d.pi, y: d.oi })),
          backgroundColor: '#10B981',
        },
      ],
    },
    options: {
      scales: {
        x: { min: 0, max: 100, title: { display: true, text: 'PI' } },
        y: { min: 0, max: 100, title: { display: true, text: 'Score' } },
      },
    },
  }
})
</script>

<template>
  <AppLayout title="심화 분석" subtitle="산점도와 상관관계 분석">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="analytics" class="grid">
      <div class="card">
        <h3>지표 산점도</h3>
        <ScatterChart v-if="scatterConfig" :config="scatterConfig" />
      </div>
      <div class="card">
        <h3>상관관계 행렬</h3>
        <table class="table">
          <tbody>
            <tr v-for="(v, k) in analytics.correlation_matrix" :key="k">
              <td>{{ k }}</td>
              <td>{{ v }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card full">
        <h3>개별 데이터</h3>
        <table class="table">
          <thead>
            <tr>
              <th>학생</th>
              <th>PI</th>
              <th>UI</th>
              <th>OI</th>
              <th>AIC</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in analytics.scatter_data" :key="s.student_id">
              <td>{{ s.name }}</td>
              <td>{{ s.pi }}</td>
              <td>{{ s.ui }}</td>
              <td>{{ s.oi }}</td>
              <td>{{ s.aic }}</td>
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
  grid-template-columns: 1.2fr 1fr;
  gap: 1rem;
}

.card {
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1rem;
}

.full {
  grid-column: 1 / -1;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.table td,
.table th {
  border-bottom: 1px solid #e5e7eb;
  padding: 0.55rem;
  text-align: left;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

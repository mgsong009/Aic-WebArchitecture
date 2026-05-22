<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import BarChart from '@/components/charts/BarChart.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = ref(Number(route.params.id))
const loading = ref(true)
const analytics = ref(null)

watch(
  () => route.params.id,
  async (nextId) => {
    assignmentId.value = Number(nextId)
    await load()
  },
)

onMounted(async () => {
  await load()
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/teacher/analytics/assignment/${assignmentId.value}`)
    analytics.value = data
  } finally {
    loading.value = false
  }
}

const distributionConfig = computed(() => {
  if (!analytics.value) return null
  return {
    type: 'bar',
    data: {
      labels: ['<40', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'],
      datasets: [
        {
          label: '학생 수',
          data: analytics.value.distribution,
          backgroundColor: '#1E3A5F',
        },
      ],
    },
    options: { responsive: true },
  }
})
</script>

<template>
  <AppLayout title="과제 분석" :subtitle="analytics?.assignment?.title || ''">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="analytics" class="grid">
      <div class="card">
        <h3>평균 점수</h3>
        <div class="meta">AIC: {{ analytics.class_avg.aic }}</div>
        <div class="meta">PI: {{ analytics.class_avg.pi }}</div>
        <div class="meta">UI: {{ analytics.class_avg.ui }}</div>
        <div class="meta">OI: {{ analytics.class_avg.oi }}</div>
        <div class="meta">난이도: {{ analytics.difficulty }}</div>
      </div>
      <div class="card">
        <h3>AIC 분포</h3>
        <BarChart v-if="distributionConfig" :config="distributionConfig" />
      </div>
      <div class="card">
        <h3>상위 5명</h3>
        <div v-for="s in analytics.top5" :key="s.name" class="row">
          <span>{{ s.name }}</span>
          <strong>{{ s.aic }}</strong>
        </div>
      </div>
      <div class="card">
        <h3>하위 5명</h3>
        <div v-for="s in analytics.bottom5" :key="s.name" class="row">
          <span>{{ s.name }}</span>
          <strong>{{ s.aic }}</strong>
        </div>
      </div>
    </div>
    <div class="actions">
      <button class="btn-secondary" @click="router.push('/teacher/dashboard')">대시보드</button>
    </div>
  </AppLayout>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1rem;
}

.card {
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1rem;
}

.meta {
  margin-bottom: 0.35rem;
  font-size: var(--text-sm);
}

.row {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.45rem 0;
  font-size: var(--text-sm);
}

.actions {
  margin-top: 1rem;
}

.btn-secondary {
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  cursor: pointer;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

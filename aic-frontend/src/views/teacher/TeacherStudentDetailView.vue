<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import MetricBars from '@/components/common/MetricBars.vue'
import LineChart from '@/components/charts/LineChart.vue'

const route = useRoute()
const router = useRouter()
const studentId = Number(route.params.id)
const loading = ref(true)
const detail = ref(null)
const feedbackText = ref('')

onMounted(async () => {
  await load()
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/teacher/students/${studentId}`)
    detail.value = data
    feedbackText.value = data.teacher_feedback?.content || ''
  } finally {
    loading.value = false
  }
}

async function saveFeedback() {
  if (!detail.value?.assignments?.length) return
  const latest = detail.value.assignments[detail.value.assignments.length - 1]
  await api.post('/teacher/feedback', {
    assignment_id: latest.id,
    student_id: studentId,
    content: feedbackText.value,
  })
  await load()
}

const trendConfig = computed(() => {
  if (!detail.value) return null
  return {
    type: 'line',
    data: {
      labels: detail.value.trend.map((t) => t.label),
      datasets: [
        {
          label: 'AIC',
          data: detail.value.trend.map((t) => t.aic),
          borderColor: '#1E3A5F',
          tension: 0.3,
        },
      ],
    },
    options: { scales: { y: { min: 0, max: 100 } } },
  }
})
</script>

<template>
  <AppLayout title="학생 상세" :subtitle="detail ? `${detail.student.name} (${detail.student.user_id_str})` : ''">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="detail" class="grid">
      <div class="card">
        <h3>최신 점수</h3>
        <MetricBars
          :pi="detail.latest_metrics.pi"
          :ui="detail.latest_metrics.ui"
          :oi="detail.latest_metrics.oi"
          :topic="null"
        />
        <div class="weak">
          약한 지표: {{ detail.weak_metrics.length ? detail.weak_metrics.join(', ') : '없음' }}
        </div>
      </div>

      <div class="card">
        <h3>AIC 추이</h3>
        <LineChart v-if="trendConfig" :config="trendConfig" />
      </div>

      <div class="card full">
        <h3>과제 이력</h3>
        <table class="table">
          <thead>
            <tr>
              <th>과제</th>
              <th>AIC</th>
              <th>PI</th>
              <th>UI</th>
              <th>OI</th>
              <th>제출일</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in detail.assignments" :key="a.id">
              <td>{{ a.title }}</td>
              <td>{{ a.aic ?? '-' }}</td>
              <td>{{ a.pi ?? '-' }}</td>
              <td>{{ a.ui ?? '-' }}</td>
              <td>{{ a.oi ?? '-' }}</td>
              <td>{{ a.submitted_at ?? '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card full">
        <h3>교사 피드백</h3>
        <textarea v-model="feedbackText" rows="5"></textarea>
        <div class="actions">
          <button class="btn-primary" @click="saveFeedback">저장</button>
          <button class="btn-secondary" @click="router.push('/teacher/students')">목록</button>
        </div>
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
  box-shadow: var(--shadow-sm);
  padding: 1.2rem;
}

.full {
  grid-column: 1 / -1;
}

.weak {
  margin-top: 0.8rem;
  font-size: var(--text-sm);
}

textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.7rem;
}

.actions {
  margin-top: 0.8rem;
  display: flex;
  gap: 0.5rem;
}

.btn-primary {
  border: none;
  background: var(--color-aic);
  color: #fff;
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  cursor: pointer;
}

.btn-secondary {
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  cursor: pointer;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.table th,
.table td {
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  padding: 0.6rem;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

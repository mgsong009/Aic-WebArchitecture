<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()
const loading = ref(true)
const riskStudents = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/teacher/risk-students')
    riskStudents.value = data.risk_students
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppLayout title="위험군 관리" subtitle="즉시 코칭이 필요한 학생 목록">
    <div class="card">
      <div v-if="loading">불러오는 중...</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>학생</th>
            <th>AIC</th>
            <th>PI</th>
            <th>UI</th>
            <th>OI</th>
            <th>위험 타입</th>
            <th>최근 제출</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in riskStudents" :key="s.id">
            <td>{{ s.name }}</td>
            <td>{{ s.aic ?? '-' }}</td>
            <td>{{ s.pi ?? '-' }}</td>
            <td>{{ s.ui ?? '-' }}</td>
            <td>{{ s.oi ?? '-' }}</td>
            <td>{{ s.risk_types.join(', ') || '-' }}</td>
            <td>{{ s.last_submitted || '-' }}</td>
            <td>
              <button class="btn-ghost" @click="router.push(`/teacher/students/${s.id}`)">상세</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="summary">총 위험군: {{ riskStudents.length }}명</div>
    </div>
  </AppLayout>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1rem;
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

.btn-ghost {
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 6px;
  padding: 0.3rem 0.55rem;
  cursor: pointer;
}

.summary {
  margin-top: 0.8rem;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>

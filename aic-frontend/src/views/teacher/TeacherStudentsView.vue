<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()
const loading = ref(true)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(20)

const filters = ref({
  search: '',
  status: '',
  sort: 'aic_desc',
})

onMounted(async () => {
  await fetchStudents()
})

async function fetchStudents() {
  loading.value = true
  try {
    const { data } = await api.get('/teacher/students', {
      params: {
        search: filters.value.search,
        status: filters.value.status,
        sort: filters.value.sort,
        page: page.value,
        per_page: perPage.value,
      },
    })
    rows.value = data.students
    total.value = data.total
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout title="학생 목록" subtitle="검색, 정렬, 상태 필터">
    <div class="card">
      <div class="toolbar">
        <input v-model="filters.search" placeholder="이름 또는 ID 검색" />
        <select v-model="filters.status">
          <option value="">전체 상태</option>
          <option value="excellent">Excellent</option>
          <option value="good">Good</option>
          <option value="average">Average</option>
          <option value="risk">Risk</option>
          <option value="pending">Pending</option>
        </select>
        <select v-model="filters.sort">
          <option value="aic_desc">AIC 높은 순</option>
          <option value="aic_asc">AIC 낮은 순</option>
          <option value="name_asc">이름 오름차순</option>
        </select>
        <button class="btn" @click="fetchStudents">조회</button>
      </div>

      <div v-if="loading" class="loading">불러오는 중...</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>이름</th>
            <th>ID</th>
            <th>AIC</th>
            <th>PI</th>
            <th>UI</th>
            <th>OI</th>
            <th>상태</th>
            <th>제출 수</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in rows" :key="s.id">
            <td>{{ s.name }}</td>
            <td>{{ s.user_id_str }}</td>
            <td>{{ s.aic ?? '-' }}</td>
            <td>{{ s.pi ?? '-' }}</td>
            <td>{{ s.ui ?? '-' }}</td>
            <td>{{ s.oi ?? '-' }}</td>
            <td><StatusBadge :score="s.aic" /></td>
            <td>{{ s.submission_count }}</td>
            <td>
              <button class="btn-ghost" @click="router.push(`/teacher/students/${s.id}`)">상세</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="paging">
        <span>총 {{ total }}명</span>
      </div>
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

.toolbar {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr 0.8fr auto;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
}

input,
select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.55rem 0.65rem;
}

.btn {
  border: none;
  background: var(--color-aic);
  color: #fff;
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  cursor: pointer;
}

.btn-ghost {
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 6px;
  padding: 0.3rem 0.55rem;
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

.loading,
.paging {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.paging {
  margin-top: 0.8rem;
}

@media (max-width: 1024px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
}
</style>

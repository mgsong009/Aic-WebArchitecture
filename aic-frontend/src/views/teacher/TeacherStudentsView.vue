<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTeacherStudents } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
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

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))
const pageStart = computed(() => (total.value ? (page.value - 1) * perPage.value + 1 : 0))
const pageEnd = computed(() => Math.min(page.value * perPage.value, total.value))

async function fetchStudents() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherStudents({
      search: filters.value.search,
      status: filters.value.status,
      sort: filters.value.sort,
      page: page.value,
      per_page: perPage.value,
    })
    rows.value = data.students
    total.value = data.total
    if (page.value > totalPages.value) {
      page.value = totalPages.value
      await fetchStudents()
    }
  } catch (err) {
    rows.value = []
    total.value = 0
    error.value = err.response?.data?.detail || '학생 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function applyFilters() {
  page.value = 1
  await fetchStudents()
}

async function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value || nextPage === page.value) return
  page.value = nextPage
  await fetchStudents()
}
</script>

<template>
  <AppLayout title="학생 목록" subtitle="검색, 정렬, 상태 필터">
    <div class="card">
      <div class="toolbar">
        <input v-model.trim="filters.search" class="form-control" placeholder="이름 또는 ID 검색" @keyup.enter="applyFilters" />
        <select v-model="filters.status" class="form-control" @change="applyFilters">
          <option value="">전체 상태</option>
          <option value="excellent">Excellent</option>
          <option value="good">Good</option>
          <option value="average">Average</option>
          <option value="risk">Risk</option>
          <option value="pending">Pending</option>
        </select>
        <select v-model="filters.sort" class="form-control" @change="applyFilters">
          <option value="aic_desc">AIC 높은 순</option>
          <option value="aic_asc">AIC 낮은 순</option>
          <option value="name_asc">이름 오름차순</option>
        </select>
        <button class="btn btn-primary" type="button" @click="applyFilters">조회</button>
      </div>

      <div v-if="loading" class="loading-state">불러오는 중...</div>
      <div v-else-if="error" class="alert alert-danger">
        <span>{{ error }}</span>
        <button class="btn btn-secondary btn-sm" type="button" @click="fetchStudents">다시 시도</button>
      </div>
      <div v-else-if="!rows.length" class="empty-state">조건에 맞는 학생이 없습니다.</div>
      <div v-else class="data-table-wrapper">
        <table class="data-table">
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
            <tr v-for="s in rows" :key="s.id" @click="router.push(`/teacher/students/${s.id}`)">
              <td>{{ s.name }}</td>
              <td>{{ s.user_id_str }}</td>
              <td>{{ s.aic ?? '-' }}</td>
              <td>{{ s.pi ?? '-' }}</td>
              <td>{{ s.ui ?? '-' }}</td>
              <td>{{ s.oi ?? '-' }}</td>
              <td><StatusBadge :score="s.aic" /></td>
              <td>{{ s.submission_count }}</td>
              <td>
                <button class="btn btn-ghost btn-sm" type="button" @click.stop="router.push(`/teacher/students/${s.id}`)">상세</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="paging">
        <span>총 {{ total }}명<span v-if="total"> · {{ pageStart }}-{{ pageEnd }} 표시</span></span>
        <div class="page-controls">
          <button class="btn btn-secondary btn-sm" type="button" :disabled="page <= 1 || loading" @click="changePage(page - 1)">이전</button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button class="btn btn-secondary btn-sm" type="button" :disabled="page >= totalPages || loading" @click="changePage(page + 1)">다음</button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
}

.toolbar {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr 0.8fr auto;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

input,
select {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  outline: none;
}

.paging {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.paging {
  margin-top: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.page-controls {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  white-space: nowrap;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

@media (max-width: 1024px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .paging {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>

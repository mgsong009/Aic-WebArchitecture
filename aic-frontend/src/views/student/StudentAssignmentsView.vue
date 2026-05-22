<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()
const assignments = ref([])
const loading = ref(true)

onMounted(async () => {
  const { data } = await api.get('/student/assignments')
  assignments.value = data.assignments
  loading.value = false
})
</script>

<template>
  <AppLayout title="과제 목록" subtitle="제출한 모든 과제와 점수를 확인하세요">
    <div v-if="loading" class="loading-state">로딩 중...</div>
    <div v-else class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>과제명</th><th>마감일</th><th>제출일</th>
            <th>AIC</th><th>PI</th><th>UI</th><th>OI</th><th>상태</th><th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in assignments" :key="a.id">
            <td>{{ a.title }}</td>
            <td>{{ a.due_date || '—' }}</td>
            <td>{{ a.submitted_at || '—' }}</td>
            <td><strong>{{ a.aic ?? '—' }}</strong></td>
            <td style="color: var(--color-pi)">{{ a.pi ?? '—' }}</td>
            <td style="color: var(--color-ui)">{{ a.ui ?? '—' }}</td>
            <td style="color: var(--color-oi)">{{ a.oi ?? '—' }}</td>
            <td><StatusBadge :score="a.aic" /></td>
            <td>
              <button class="btn-view" @click="router.push(`/student/assignments/${a.id}`)">보기</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-state { padding: 3rem; text-align: center; color: var(--text-secondary); }
.card { background: #fff; border-radius: var(--radius-lg); padding: 1.5rem; box-shadow: var(--shadow-sm); }
.data-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.data-table th { text-align: left; padding: 0.65rem 0.75rem; background: #f9fafb; color: var(--text-secondary); font-weight: 600; font-size: var(--text-xs); text-transform: uppercase; border-bottom: 1px solid #e5e7eb; }
.data-table td { padding: 0.75rem; border-bottom: 1px solid #f3f4f6; }
.btn-view { padding: 0.3rem 0.75rem; border: 1px solid var(--color-aic); color: var(--color-aic); background: transparent; border-radius: 6px; cursor: pointer; font-size: var(--text-xs); }
</style>

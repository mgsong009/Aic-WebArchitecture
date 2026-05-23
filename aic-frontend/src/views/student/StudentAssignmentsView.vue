<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudentAssignments } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const router = useRouter()
const assignments = ref([])
const loading = ref(true)
const error = ref('')

const hasAssignments = computed(() => assignments.value.length > 0)

onMounted(async () => {
  await loadAssignments()
})

async function loadAssignments() {
  loading.value = true
  error.value = ''
  try {
    assignments.value = await getStudentAssignments()
  } catch {
    error.value = '과제 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout title="과제 목록" subtitle="제출한 모든 과제와 점수를 확인하세요">
    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="72px" />
      <LoadingSkeleton height="260px" />
    </div>
    <div v-else-if="error" class="card card-body empty-state">
      <strong>{{ error }}</strong>
      <button class="btn btn-secondary btn-sm mt-4" type="button" @click="loadAssignments">다시 시도</button>
    </div>
    <div v-else-if="!hasAssignments" class="card card-body empty-state">
      아직 표시할 과제가 없습니다.
    </div>
    <div v-else class="data-table-wrapper">
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
              <button class="btn btn-secondary btn-sm" type="button" @click="router.push(`/student/assignments/${a.id}`)">보기</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-wrap {
  display: grid;
  gap: var(--space-4);
}
</style>

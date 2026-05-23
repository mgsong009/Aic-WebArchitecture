<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeacherStudentDetail, saveTeacherFeedback } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import MetricBars from '@/components/common/MetricBars.vue'
import LineChart from '@/components/charts/LineChart.vue'

const route = useRoute()
const router = useRouter()
const studentId = Number(route.params.id)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saveMessage = ref('')
const detail = ref(null)
const feedbackText = ref('')
const selectedAssignmentId = ref('')

onMounted(async () => {
  await load()
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherStudentDetail(studentId)
    detail.value = data
    const assignments = detail.value.assignments
    const latest = assignments[assignments.length - 1]
    selectedAssignmentId.value = selectedAssignmentId.value || (latest?.id ? String(latest.id) : '')
    feedbackText.value = data.teacher_feedback?.content || ''
  } catch (err) {
    detail.value = null
    error.value = err.response?.data?.detail || '학생 상세 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function saveFeedback() {
  if (!selectedAssignmentId.value || saving.value) return
  saving.value = true
  error.value = ''
  saveMessage.value = ''
  try {
    await saveTeacherFeedback({
      assignment_id: Number(selectedAssignmentId.value),
      student_id: studentId,
      content: feedbackText.value.trim(),
    })
    saveMessage.value = '피드백을 저장했습니다.'
  } catch (err) {
    error.value = err.response?.data?.detail || '피드백을 저장하지 못했습니다.'
  } finally {
    saving.value = false
  }
}

const trendConfig = computed(() => {
  if (!detail.value?.trend?.length) return null
  return {
    type: 'line',
    data: {
      labels: detail.value.trend.map((t) => t.label),
      datasets: [
        {
          label: 'AIC',
          data: detail.value.trend.map((t) => t.aic),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30, 58, 95, 0.08)',
          tension: 0.3,
          pointRadius: 4,
        },
      ],
    },
    options: { scales: { y: { min: 0, max: 100 } } },
  }
})

const selectedAssignment = computed(() => (
  detail.value?.assignments?.find((assignment) => String(assignment.id) === String(selectedAssignmentId.value)) || null
))

const canSaveFeedback = computed(() => Boolean(selectedAssignmentId.value) && Boolean(feedbackText.value.trim()) && !saving.value)
</script>

<template>
  <AppLayout title="학생 상세" :subtitle="detail ? `${detail.student.name} (${detail.student.user_id_str})` : ''">
    <div v-if="loading" class="card loading-state">불러오는 중...</div>
    <div v-else-if="error && !detail" class="card">
      <div class="alert alert-danger">
        <span>{{ error }}</span>
        <button class="btn btn-secondary btn-sm" type="button" @click="load">다시 시도</button>
      </div>
    </div>
    <div v-else-if="detail" class="grid">
      <div class="card">
        <div class="card-heading">
          <h3>최신 점수</h3>
          <strong>{{ detail.latest_metrics.aic ?? '-' }}</strong>
        </div>
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
        <div v-else class="empty-state compact">표시할 추이 데이터가 없습니다.</div>
      </div>

      <div class="card full">
        <h3>과제 이력</h3>
        <div v-if="!detail.assignments.length" class="empty-state compact">제출 이력이 없습니다.</div>
        <div v-else class="data-table-wrapper">
          <table class="data-table">
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
              <tr
                v-for="a in detail.assignments"
                :key="a.id"
                :class="{ selected: String(a.id) === String(selectedAssignmentId) }"
                @click="selectedAssignmentId = String(a.id)"
              >
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
      </div>

      <div class="card full">
        <div class="feedback-header">
          <div>
            <h3>교사 피드백</h3>
            <p v-if="selectedAssignment" class="muted-row">{{ selectedAssignment.title }} 대상</p>
          </div>
          <select v-model="selectedAssignmentId" class="form-control" :disabled="!detail.assignments.length">
            <option value="" disabled>과제 선택</option>
            <option v-for="a in detail.assignments" :key="a.id" :value="String(a.id)">
              {{ a.title }}
            </option>
          </select>
        </div>
        <textarea v-model="feedbackText" rows="5" :disabled="!selectedAssignmentId || saving"></textarea>
        <div v-if="error" class="alert alert-danger mt-4">{{ error }}</div>
        <div v-else-if="saveMessage" class="alert alert-success mt-4">{{ saveMessage }}</div>
        <div class="actions">
          <button class="btn btn-primary" type="button" :disabled="!canSaveFeedback" @click="saveFeedback">
            {{ saving ? '저장 중...' : '저장' }}
          </button>
          <button class="btn btn-secondary" type="button" @click="router.push('/teacher/students')">목록</button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
}

.card-heading,
.feedback-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.card-heading strong {
  color: var(--color-aic);
  font-size: var(--text-2xl);
  line-height: 1;
}

.full {
  grid-column: 1 / -1;
}

.weak {
  margin-top: 0.8rem;
  font-size: var(--text-sm);
}

.compact {
  padding: var(--space-6);
}

textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  outline: none;
}

textarea:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}

textarea:disabled {
  background: var(--color-gray-50);
  color: var(--text-muted);
  cursor: not-allowed;
}

.actions {
  margin-top: 0.8rem;
  display: flex;
  gap: 0.5rem;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.data-table tbody tr.selected {
  background: var(--color-aic-pale);
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .card-heading,
  .feedback-header,
  .actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>

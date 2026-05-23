<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudentAssignmentDetail, submitStudentSubmission } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import MetricBars from '@/components/common/MetricBars.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import { useJobPoller } from '@/composables/useJobPoller'

const route = useRoute()
const router = useRouter()
const assignmentId = Number(route.params.id)

const loading = ref(true)
const submitting = ref(false)
const loadError = ref('')
const submitError = ref('')
const payload = ref(null)
const form = ref({
  chatgpt_before: '',
  user_prompt: '',
  essay: '',
})

const { status, metrics, error, startPolling, stop } = useJobPoller()

const assignment = computed(() => payload.value?.assignment || null)
const submission = computed(() => payload.value?.submission || null)
const resultMetrics = computed(() => metrics.value || payload.value?.metrics || null)
const classAvg = computed(() => payload.value?.class_avg || null)
const hasResult = computed(() => !!resultMetrics.value)
const isPolling = computed(() => status.value === 'pending' || status.value === 'running')
const canSubmit = computed(() =>
  form.value.chatgpt_before.trim()
  && form.value.user_prompt.trim()
  && form.value.essay.trim()
  && !submitting.value
  && !isPolling.value
)

onMounted(async () => {
  await load()
})

onUnmounted(() => {
  stop()
})

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const data = await getStudentAssignmentDetail(assignmentId)
    payload.value = data
    if (data.submission) {
      form.value = {
        chatgpt_before: data.submission.chatgpt_before || '',
        user_prompt: data.submission.user_prompt || '',
        essay: data.submission.essay || '',
      }
    }
  } catch {
    loadError.value = '과제 상세 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function submitEssay() {
  submitError.value = ''
  if (!canSubmit.value) {
    submitError.value = 'AI 초안, 학생 프롬프트, 최종 에세이를 모두 입력하세요.'
    return
  }
  const body = {
    assignment_id: assignmentId,
    chatgpt_before: form.value.chatgpt_before,
    user_prompt: form.value.user_prompt,
    essay: form.value.essay,
  }
  submitting.value = true
  try {
    const data = await submitStudentSubmission(body)
    await startPolling(data.job_id)
  } catch {
    submitError.value = '제출을 저장하지 못했습니다.'
  } finally {
    submitting.value = false
  }
}

watch(status, async (nextStatus) => {
  if (nextStatus === 'done') {
    stop()
    await load()
  }
})
</script>

<template>
  <AppLayout :title="assignment?.title || '과제 상세'" subtitle="제출 내용과 분석 결과">
    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="120px" />
      <LoadingSkeleton height="420px" />
    </div>
    <div v-else-if="loadError" class="card card-body empty-state">
      <strong>{{ loadError }}</strong>
      <div class="actions justify-center">
        <button class="btn btn-secondary btn-sm" type="button" @click="load">다시 시도</button>
        <button class="btn btn-ghost btn-sm" type="button" @click="router.push('/student/assignments')">목록으로</button>
      </div>
    </div>
    <div v-else-if="payload" class="grid-2-1">
      <div class="card card-body">
        <div class="card-heading">
          <div>
            <h3>제출 작성/수정</h3>
            <p class="text-secondary text-sm">{{ submission ? '기존 제출 내용을 수정해 다시 분석할 수 있습니다.' : '제출 후 자동으로 분석이 시작됩니다.' }}</p>
          </div>
        </div>
        <div class="field">
          <label>AI 초안 (chatgpt_before)</label>
          <textarea v-model="form.chatgpt_before" rows="6" :disabled="submitting || isPolling"></textarea>
        </div>
        <div class="field">
          <label>학생 프롬프트 (user_prompt)</label>
          <textarea v-model="form.user_prompt" rows="4" :disabled="submitting || isPolling"></textarea>
        </div>
        <div class="field">
          <label>최종 에세이 (essay)</label>
          <textarea v-model="form.essay" rows="10" :disabled="submitting || isPolling"></textarea>
        </div>
        <div v-if="submitError" class="alert alert-danger">{{ submitError }}</div>
        <div class="actions">
          <button class="btn btn-primary" type="button" :disabled="!canSubmit" @click="submitEssay">
            {{ submitting ? '저장 중...' : isPolling ? '분석 중...' : '제출하고 분석 시작' }}
          </button>
          <button class="btn btn-secondary" type="button" @click="router.push('/student/assignments')">목록으로</button>
        </div>
        <div v-if="status !== 'idle'" class="job-status">
          분석 상태: <strong>{{ status }}</strong>
          <span v-if="error" class="error-text"> - {{ error }}</span>
          <span v-if="metrics"> - AIC: {{ metrics.aic ?? '-' }}</span>
        </div>
      </div>

      <div class="card card-body">
        <h3>분석 결과</h3>
        <div v-if="isPolling" class="empty-state compact">
          분석이 진행 중입니다. 완료되면 결과가 자동으로 반영됩니다.
        </div>
        <div v-else-if="status === 'failed'" class="alert alert-danger">
          {{ error || '분석에 실패했습니다. 내용을 확인한 뒤 다시 제출해 주세요.' }}
        </div>
        <template v-else-if="hasResult">
          <MetricBars
            :pi="resultMetrics.pi"
            :ui="resultMetrics.ui"
            :oi="resultMetrics.oi"
            :topic="resultMetrics.topic"
            :compare-values="classAvg"
          />
          <div class="meta">
            <div>AIC: {{ resultMetrics.aic ?? '-' }}</div>
            <div>반 평균 AIC: {{ classAvg?.aic ?? '-' }}</div>
          </div>
          <div class="actions">
            <button class="btn btn-secondary" type="button" @click="router.push(`/student/feedback/${assignmentId}`)">
              피드백 보기
            </button>
          </div>
        </template>
        <div v-else class="empty-state compact">
          아직 분석 결과가 없습니다. 제출을 완료하면 결과가 이곳에 표시됩니다.
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-wrap {
  display: grid;
  gap: var(--space-4);
}

h3 {
  margin-bottom: 0.8rem;
}

.field {
  margin-bottom: 0.75rem;
}

label {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
}

textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
}

textarea:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}

textarea:disabled {
  background: var(--color-gray-50);
  color: var(--text-secondary);
}

.actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.8rem;
}

.btn:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.job-status {
  margin-top: 0.8rem;
  font-size: var(--text-sm);
}

.error-text {
  color: #dc2626;
}

.meta {
  margin-top: 1rem;
  display: grid;
  gap: 0.3rem;
  font-size: var(--text-sm);
}

.compact {
  padding: var(--space-6);
}
</style>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import MetricBars from '@/components/common/MetricBars.vue'
import { useJobPoller } from '@/composables/useJobPoller'

const route = useRoute()
const router = useRouter()
const assignmentId = Number(route.params.id)

const loading = ref(true)
const payload = ref(null)
const form = ref({
  chatgpt_before: '',
  user_prompt: '',
  essay: '',
})

const { status, metrics, error, startPolling, stop } = useJobPoller()

onMounted(async () => {
  await load()
})

onUnmounted(() => {
  stop()
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/student/assignments/${assignmentId}`)
    payload.value = data
    if (data.submission) {
      form.value = {
        chatgpt_before: data.submission.chatgpt_before || '',
        user_prompt: data.submission.user_prompt || '',
        essay: data.submission.essay || '',
      }
    }
  } finally {
    loading.value = false
  }
}

async function submitEssay() {
  const body = {
    assignment_id: assignmentId,
    chatgpt_before: form.value.chatgpt_before,
    user_prompt: form.value.user_prompt,
    essay: form.value.essay,
  }
  const { data } = await api.post('/submissions', body)
  await startPolling(data.job_id)
}

async function refreshAfterDone() {
  if (status.value === 'done') {
    stop()
    await load()
  }
}
</script>

<template>
  <AppLayout :title="payload?.assignment?.title || '과제 상세'" subtitle="제출 내용과 분석 결과">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="payload" class="grid">
      <div class="card">
        <h3>제출 작성/수정</h3>
        <div class="field">
          <label>AI 초안 (chatgpt_before)</label>
          <textarea v-model="form.chatgpt_before" rows="6"></textarea>
        </div>
        <div class="field">
          <label>학생 프롬프트 (user_prompt)</label>
          <textarea v-model="form.user_prompt" rows="4"></textarea>
        </div>
        <div class="field">
          <label>최종 에세이 (essay)</label>
          <textarea v-model="form.essay" rows="10"></textarea>
        </div>
        <div class="actions">
          <button class="btn-primary" @click="submitEssay">제출하고 분석 시작</button>
          <button class="btn-secondary" @click="router.push('/student/assignments')">목록으로</button>
        </div>
        <div v-if="status !== 'idle'" class="job-status">
          분석 상태: <strong>{{ status }}</strong>
          <span v-if="error" class="error-text"> - {{ error }}</span>
          <span v-if="metrics"> - AIC: {{ metrics.aic }}</span>
          <button v-if="status === 'done'" class="btn-mini" @click="refreshAfterDone">결과 반영</button>
        </div>
      </div>

      <div class="card">
        <h3>분석 결과</h3>
        <MetricBars
          :pi="payload.metrics?.pi"
          :ui="payload.metrics?.ui"
          :oi="payload.metrics?.oi"
          :topic="payload.metrics?.topic"
          :compare-values="payload.class_avg"
        />
        <div class="meta">
          <div>AIC: {{ payload.metrics?.aic ?? '-' }}</div>
          <div>반 평균 AIC: {{ payload.class_avg?.aic ?? '-' }}</div>
        </div>
        <div class="actions">
          <button class="btn-secondary" @click="router.push(`/student/feedback/${assignmentId}`)">
            피드백 보기
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: var(--space-4);
}

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
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

.actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.8rem;
}

.btn-primary {
  background: var(--color-aic);
  color: #fff;
  border: 1px solid var(--color-aic);
  border-radius: var(--radius-md);
  padding: 0.55rem 0.8rem;
  cursor: pointer;
  font-weight: 600;
}

.btn-secondary {
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.55rem 0.8rem;
  cursor: pointer;
  font-weight: 600;
}

.btn-mini {
  margin-left: 0.5rem;
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  padding: 0.25rem 0.4rem;
  cursor: pointer;
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

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

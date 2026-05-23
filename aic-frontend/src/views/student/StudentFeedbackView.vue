<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const route = useRoute()
const router = useRouter()

const assignments = ref([])
const feedback = ref(null)
const assignmentsLoading = ref(true)
const feedbackLoading = ref(false)
const assignmentsError = ref('')
const feedbackError = ref('')

const assignmentId = computed(() => {
  const id = Number(route.params.assignmentId)
  return Number.isFinite(id) && id > 0 ? id : null
})
const hasAssignmentId = computed(() => assignmentId.value !== null)
const selectedAssignment = computed(() =>
  assignments.value.find((assignment) => assignment.id === assignmentId.value) || null
)
const submittedAssignments = computed(() =>
  assignments.value.filter((assignment) => assignment.status !== 'not_submitted')
)
const guide = computed(() => {
  const autoGuide = feedback.value?.auto_guide || {}
  return {
    strengths: Array.isArray(autoGuide.strengths) ? autoGuide.strengths : [],
    improvements: Array.isArray(autoGuide.improvements) ? autoGuide.improvements : [],
    tips: Array.isArray(autoGuide.tips) ? autoGuide.tips : [],
  }
})
const teacherFeedback = computed(() => feedback.value?.teacher_feedback || null)
const pageTitle = computed(() => selectedAssignment.value?.title || '피드백')
const pageSubtitle = computed(() =>
  hasAssignmentId.value
    ? '교사 피드백과 자동 개선 가이드를 확인하세요'
    : '피드백을 확인할 과제를 선택하세요'
)

onMounted(async () => {
  await loadAssignments()
  if (hasAssignmentId.value) {
    await loadFeedback()
  }
})

watch(assignmentId, async (nextId, previousId) => {
  if (nextId === previousId) return
  feedback.value = null
  feedbackError.value = ''
  if (nextId) {
    await loadFeedback()
  }
})

async function loadAssignments() {
  assignmentsLoading.value = true
  assignmentsError.value = ''
  try {
    const { data } = await api.get('/student/assignments')
    assignments.value = Array.isArray(data.assignments) ? data.assignments : []
  } catch {
    assignmentsError.value = '과제 목록을 불러오지 못했습니다.'
  } finally {
    assignmentsLoading.value = false
  }
}

async function loadFeedback() {
  if (!assignmentId.value) return
  feedbackLoading.value = true
  feedbackError.value = ''
  try {
    const { data } = await api.get(`/student/feedback/${assignmentId.value}`)
    feedback.value = data
  } catch {
    feedbackError.value = '피드백을 불러오지 못했습니다.'
  } finally {
    feedbackLoading.value = false
  }
}

function openFeedback(id) {
  router.push(`/student/feedback/${id}`)
}

function openAssignment(id = assignmentId.value) {
  if (id) {
    router.push(`/student/assignments/${id}`)
  } else {
    router.push('/student/assignments')
  }
}
</script>

<template>
  <AppLayout :title="pageTitle" :subtitle="pageSubtitle">
    <div class="feedback-page">
      <section class="card card-body selector-card">
        <div>
          <h3>과제 선택</h3>
          <p class="text-secondary text-sm">제출한 과제의 교사 코멘트와 자동 개선 가이드를 볼 수 있습니다.</p>
        </div>

        <div v-if="assignmentsLoading" class="selector-loading">
          <LoadingSkeleton height="40px" />
        </div>
        <div v-else-if="assignmentsError" class="selector-error">
          <span>{{ assignmentsError }}</span>
          <button class="btn btn-secondary btn-sm" type="button" @click="loadAssignments">다시 시도</button>
        </div>
        <div v-else class="selector-controls">
          <select :value="assignmentId || ''" @change="openFeedback(Number($event.target.value))">
            <option value="" disabled>과제를 선택하세요</option>
            <option v-for="assignment in submittedAssignments" :key="assignment.id" :value="assignment.id">
              {{ assignment.title }}
            </option>
          </select>
          <button class="btn btn-secondary" type="button" @click="openAssignment()">과제 상세</button>
        </div>
      </section>

      <div v-if="!hasAssignmentId && !assignmentsLoading && !assignmentsError" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>과제명</th>
              <th>제출일</th>
              <th>AIC</th>
              <th>상태</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="assignment in submittedAssignments" :key="assignment.id" @click="openFeedback(assignment.id)">
              <td>{{ assignment.title }}</td>
              <td>{{ assignment.submitted_at || '-' }}</td>
              <td><strong>{{ assignment.aic ?? '-' }}</strong></td>
              <td><StatusBadge :score="assignment.aic" /></td>
              <td>
                <button class="btn btn-secondary btn-sm" type="button" @click.stop="openFeedback(assignment.id)">
                  피드백 보기
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!assignmentsLoading && submittedAssignments.length === 0" class="empty-state compact">
          피드백을 확인할 제출 과제가 없습니다.
        </div>
      </div>

      <div v-else-if="feedbackLoading" class="loading-wrap">
        <LoadingSkeleton height="180px" />
        <LoadingSkeleton height="220px" />
      </div>

      <div v-else-if="feedbackError" class="card card-body empty-state">
        <strong>{{ feedbackError }}</strong>
        <div class="actions justify-center">
          <button class="btn btn-secondary btn-sm" type="button" @click="loadFeedback">다시 시도</button>
          <button class="btn btn-ghost btn-sm" type="button" @click="openAssignment()">과제 상세</button>
        </div>
      </div>

      <div v-else-if="feedback" class="feedback-grid">
        <section class="card card-body teacher-card">
          <div class="card-topline">
            <h3>교사 피드백</h3>
            <span v-if="teacherFeedback?.created_at" class="date">{{ teacherFeedback.created_at }}</span>
          </div>
          <p v-if="teacherFeedback?.content" class="feedback-body">
            {{ teacherFeedback.content }}
          </p>
          <div v-else class="empty-state compact">
            아직 등록된 교사 피드백이 없습니다.
          </div>
        </section>

        <section class="card card-body guide-card">
          <h3>강점</h3>
          <ul class="guide-list">
            <li v-for="(item, index) in guide.strengths" :key="`strength-${index}`">{{ item }}</li>
            <li v-if="guide.strengths.length === 0" class="muted-item">강점 항목이 아직 없습니다.</li>
          </ul>
        </section>

        <section class="card card-body guide-card">
          <h3>개선 포인트</h3>
          <ul class="guide-list">
            <li v-for="(item, index) in guide.improvements" :key="`improvement-${index}`">{{ item }}</li>
            <li v-if="guide.improvements.length === 0" class="muted-item">개선 포인트가 아직 없습니다.</li>
          </ul>
        </section>

        <section class="card card-body guide-card">
          <h3>실행 팁</h3>
          <ul class="guide-list">
            <li v-for="(item, index) in guide.tips" :key="`tip-${index}`">{{ item }}</li>
            <li v-if="guide.tips.length === 0" class="muted-item">실행 팁이 아직 없습니다.</li>
          </ul>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.feedback-page {
  display: grid;
  gap: var(--space-4);
}

.selector-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 420px);
  align-items: end;
  gap: var(--space-4);
}

h3 {
  margin-bottom: 0.35rem;
}

.selector-loading,
.selector-error,
.selector-controls {
  min-width: 0;
}

.selector-error,
.selector-controls {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.selector-error {
  justify-content: flex-end;
  color: var(--color-danger);
  font-size: var(--text-sm);
}

select {
  width: 100%;
  min-width: 0;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  color: var(--text-primary);
  background: var(--bg-surface);
}

.loading-wrap {
  display: grid;
  gap: var(--space-4);
}

.feedback-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-4);
}

.teacher-card {
  grid-column: 1 / -1;
}

.card-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.date {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  white-space: nowrap;
}

.feedback-body {
  line-height: 1.7;
  font-size: var(--text-sm);
  white-space: pre-wrap;
}

.guide-list {
  display: grid;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.guide-list li {
  position: relative;
  padding-left: var(--space-4);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.guide-list li::before {
  content: '';
  position: absolute;
  top: 0.65em;
  left: 0;
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--color-pi);
}

.guide-list .muted-item {
  color: var(--text-secondary);
}

.guide-list .muted-item::before {
  background: var(--color-gray-300);
}

.actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.justify-center {
  justify-content: center;
}

.compact {
  padding: var(--space-6);
}

@media (max-width: 1024px) {
  .selector-card,
  .feedback-grid {
    grid-template-columns: 1fr;
  }

  .teacher-card {
    grid-column: auto;
  }
}

@media (max-width: 640px) {
  .selector-controls,
  .selector-error {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>

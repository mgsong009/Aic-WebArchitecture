<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudentAssignments, getStudentFeedback } from '@/api'
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
const checkedPlanItems = ref(new Set())

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
const pageTitle = computed(() => selectedAssignment.value ? 'Feedback Guide' : '피드백')
const pageSubtitle = computed(() =>
  hasAssignmentId.value
    ? '점수를 행동으로 연결하는 구체적인 개선 방법을 확인하세요'
    : '피드백을 확인할 과제를 선택하세요'
)

const metricMeta = {
  pi: {
    key: 'pi',
    label: 'PI',
    full: 'Prompt Insight',
    subtitle: '질문의 깊이와 비판성',
    color: '#3B82F6',
    pale: 'var(--color-pi-pale)',
    icon: 'PI',
    desc: '프롬프트의 구체성, 관점 요청, 비판적 사고를 요구하는 정도를 보여줍니다.',
    steps: [
      ['심화 질문어 사용하기', '"왜", "어떻게", "한계는 무엇인가" 같은 질문어를 매 프롬프트에 포함하세요.'],
      ['다각도 관점 요청', '찬성/반대, 장점/위험처럼 여러 관점을 동시에 요청하세요.'],
      ['구체적 제약 조건 명시', '분량, 독자 수준, 근거 형식 같은 조건을 먼저 정하면 답변 품질이 안정됩니다.'],
    ],
  },
  ui: {
    key: 'ui',
    label: 'UI',
    full: 'User Intervention',
    subtitle: 'AI 초안 수정 개입 정도',
    color: '#F97316',
    pale: 'var(--color-ui-pale)',
    icon: 'UI',
    desc: 'AI 초안을 그대로 제출하지 않고 구조, 근거, 문장 수준에서 얼마나 개입했는지 보여줍니다.',
    steps: [
      ['단락 순서 재배치', 'AI가 제안한 구조를 자신의 논리 흐름에 맞게 다시 배열하세요.'],
      ['새 정보 추가', 'AI 답변에 없던 예시, 수치, 개인 경험을 본문에 직접 추가하세요.'],
      ['불필요한 문장 삭제', '일반적이거나 반복적인 문장은 과감히 줄이고 핵심 주장만 남기세요.'],
    ],
  },
  oi: {
    key: 'oi',
    label: 'OI',
    full: 'Originality Index',
    subtitle: '자기 관점과 독창성',
    color: '#10B981',
    pale: 'var(--color-oi-pale)',
    icon: 'OI',
    desc: '글에 자신의 경험, 판단, 독립적인 관점이 얼마나 드러나는지 보여줍니다.',
    steps: [
      ['개인 경험 연결', '주제와 연결되는 자신의 경험이나 관찰을 구체적으로 적으세요.'],
      ['반대 의견 포함', '내 주장에 반하는 시각을 인정하고 직접 반박하는 구조를 넣어보세요.'],
      ['외부 자료 직접 연결', 'AI가 준 내용 밖의 기사, 논문, 수업 자료를 직접 찾아 연결하세요.'],
    ],
  },
}

const metricGuides = computed(() => ['pi', 'ui', 'oi'].map((key) => {
  const meta = metricMeta[key]
  const score = metricScore(selectedAssignment.value?.[key])
  return {
    ...meta,
    score,
    status: score == null ? 'Pending' : score >= 75 ? 'Excellent' : score >= 65 ? 'Good' : '개선 필요',
    statusTone: score == null ? 'neutral' : score >= 75 ? 'excellent' : score >= 65 ? 'good' : 'risk',
  }
}))

const teacherComments = computed(() => {
  if (!selectedAssignment.value || !teacherFeedback.value?.content) return []
  return [
    {
      id: selectedAssignment.value.id,
      assignmentLabel: assignmentLabel(selectedAssignment.value),
      title: selectedAssignment.value.title,
      date: teacherFeedback.value.created_at || selectedAssignment.value.submitted_at || '-',
      content: teacherFeedback.value.content,
    },
  ]
})

const nextPlanItems = computed(() => {
  const items = []
  const lowMetric = [...metricGuides.value]
    .filter((item) => item.score != null)
    .sort((a, b) => a.score - b.score)[0]
  if (lowMetric) {
    items.push(`${lowMetric.label} 보강: ${lowMetric.steps[0][1]}`)
  }
  items.push(...guide.value.improvements.slice(0, 2))
  items.push(...guide.value.tips.slice(0, 2))
  items.push('최종 제출 전 AI 초안과 비교해 내가 바꾼 근거를 표시하기')
  return [...new Set(items)].slice(0, 6)
})

const targetScore = computed(() => {
  const current = metricScore(selectedAssignment.value?.aic)
  if (current == null) return 75
  return Math.min(100, Math.max(75, current + 5))
})

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
  checkedPlanItems.value = new Set()
  if (nextId) {
    await loadFeedback()
  }
})

async function loadAssignments() {
  assignmentsLoading.value = true
  assignmentsError.value = ''
  try {
    assignments.value = await getStudentAssignments()
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
    feedback.value = await getStudentFeedback(assignmentId.value)
  } catch {
    feedbackError.value = '피드백을 불러오지 못했습니다.'
  } finally {
    feedbackLoading.value = false
  }
}

function metricScore(value) {
  const next = Number(value)
  return Number.isFinite(next) ? next : null
}

function formatScore(value, fallback = '-') {
  const next = metricScore(value)
  return next == null ? fallback : Number.isInteger(next) ? next : next.toFixed(1)
}

function assignmentLabel(assignment) {
  const index = submittedAssignments.value.findIndex((item) => item.id === assignment?.id)
  return index >= 0 ? `A${index + 1}` : `#${assignment?.id || '-'}`
}

function openFeedback(id) {
  if (id) router.push(`/student/feedback/${id}`)
}

function openAssignment(id = assignmentId.value) {
  if (id) {
    router.push(`/student/assignments/${id}`)
  } else {
    router.push('/student/assignments')
  }
}

function goDashboard() {
  router.push('/student/dashboard')
}

function togglePlanItem(index) {
  const next = new Set(checkedPlanItems.value)
  if (next.has(index)) {
    next.delete(index)
  } else {
    next.add(index)
  }
  checkedPlanItems.value = next
}
</script>

<template>
  <AppLayout :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
      <button class="btn btn-primary btn-sm" type="button" @click="goDashboard">← Dashboard</button>
    </template>

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
              {{ assignmentLabel(assignment) }} · {{ assignment.title }}
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
              <td>
                <strong>{{ assignment.title }}</strong>
                <div class="text-xs text-muted">{{ assignmentLabel(assignment) }}</div>
              </td>
              <td>{{ assignment.submitted_at || '-' }}</td>
              <td><strong>{{ formatScore(assignment.aic) }}</strong></td>
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
        <LoadingSkeleton height="128px" />
        <LoadingSkeleton height="330px" />
        <LoadingSkeleton height="220px" />
      </div>

      <div v-else-if="feedbackError" class="card card-body empty-state">
        <strong>{{ feedbackError }}</strong>
        <div class="actions justify-center">
          <button class="btn btn-secondary btn-sm" type="button" @click="loadFeedback">다시 시도</button>
          <button class="btn btn-ghost btn-sm" type="button" @click="openAssignment()">과제 상세</button>
        </div>
      </div>

      <div v-else-if="feedback && selectedAssignment" class="guide-shell">
        <section class="feedback-hero">
          <div class="fh-tag">
            {{ assignmentLabel(selectedAssignment) }} · {{ selectedAssignment.submitted_at || selectedAssignment.due_date || '제출일 없음' }}
          </div>
          <div class="fh-title">{{ selectedAssignment.title }} — 개선 가이드</div>
          <div class="fh-sub">
            AIC {{ formatScore(selectedAssignment.aic) }}점 · 점수를 행동으로 연결하는 구체적인 개선 방법을 확인하세요
          </div>
        </section>

        <section class="metric-guide-grid" aria-label="지표별 개선 가이드">
          <article v-for="metric in metricGuides" :key="metric.key" class="metric-guide-card">
            <div class="mgc-header">
              <div class="mgc-icon" :style="{ background: metric.pale, color: metric.color }">{{ metric.icon }}</div>
              <div class="mgc-title-wrap">
                <div class="mgc-title" :style="{ color: metric.color }">
                  {{ metric.label }} · {{ metric.full }}
                </div>
                <div class="mgc-subtitle">{{ metric.subtitle }}</div>
              </div>
              <div class="mgc-score-badge">
                <div class="mgc-score" :style="{ color: metric.color }">{{ formatScore(metric.score) }}</div>
                <div class="mgc-status" :class="metric.statusTone">{{ metric.status }}</div>
              </div>
            </div>
            <div class="mgc-body">
              <div class="mgc-score-bar">
                <div
                  class="mgc-score-bar-fill"
                  :style="{ width: `${metric.score || 0}%`, background: metric.color }"
                />
              </div>
              <p class="mgc-desc">{{ metric.desc }}</p>
              <div class="action-steps">
                <div v-for="step in metric.steps" :key="step[0]" class="action-step">
                  <span class="as-icon" :style="{ color: metric.color }">•</span>
                  <div class="as-body">
                    <div class="as-title">{{ step[0] }}</div>
                    <div class="as-desc">{{ step[1] }}</div>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </section>

        <section class="grid-2 section-gap">
          <div>
            <div class="section-heading">교사 피드백 전체 이력</div>
            <div class="teacher-comments">
              <article v-for="comment in teacherComments" :key="comment.id" class="tc-item">
                <div class="tc-header">
                  <div class="tc-avatar">T</div>
                  <div>
                    <div class="tc-name">담당 교사</div>
                    <div class="tc-date">{{ comment.date }}</div>
                  </div>
                  <span class="tc-assign">{{ comment.assignmentLabel }}</span>
                </div>
                <div class="tc-body">{{ comment.content }}</div>
              </article>
              <article v-if="teacherComments.length === 0" class="tc-item muted-comment">
                <div class="tc-header">
                  <div class="tc-avatar muted">T</div>
                  <div>
                    <div class="tc-name">담당 교사</div>
                    <div class="tc-date">{{ selectedAssignment.submitted_at || '-' }}</div>
                  </div>
                  <span class="tc-assign">{{ assignmentLabel(selectedAssignment) }}</span>
                </div>
                <div class="tc-body">아직 등록된 교사 피드백이 없습니다. 자동 개선 가이드를 먼저 참고하세요.</div>
              </article>
            </div>
          </div>

          <div>
            <div class="section-heading">다음 과제 실천 체크리스트</div>
            <div class="next-plan">
              <div class="np-title">다음 과제 준비 행동 계획</div>
              <div class="np-checklist">
                <button
                  v-for="(item, index) in nextPlanItems"
                  :key="`${index}-${item}`"
                  class="np-check-item"
                  type="button"
                  @click="togglePlanItem(index)"
                >
                  <span class="np-check" :class="{ checked: checkedPlanItems.has(index) }" />
                  <span class="np-check-label">{{ item }}</span>
                </button>
              </div>
              <div class="target-progress">
                <div class="target-copy">
                  목표: AIC {{ targetScore }}점 이상 달성 (현재 {{ formatScore(selectedAssignment.aic) }}점)
                </div>
                <div class="target-track">
                  <div class="target-fill" :style="{ width: `${metricScore(selectedAssignment.aic) || 0}%` }" />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="card card-body tip-section">
          <div>
            <div class="section-heading no-margin">개선 팁</div>
            <p class="text-secondary text-sm">자동 가이드가 추출한 강점과 개선 포인트입니다.</p>
          </div>
          <div class="tip-grid">
            <div class="tip-card success">
              <h3>강점</h3>
              <ul>
                <li v-for="(item, index) in guide.strengths" :key="`strength-${index}`">{{ item }}</li>
                <li v-if="guide.strengths.length === 0">아직 강점 항목이 없습니다.</li>
              </ul>
            </div>
            <div class="tip-card warning">
              <h3>개선 포인트</h3>
              <ul>
                <li v-for="(item, index) in guide.improvements" :key="`improvement-${index}`">{{ item }}</li>
                <li v-if="guide.improvements.length === 0">현재 지표에서 큰 위험 신호는 없습니다.</li>
              </ul>
            </div>
            <div class="tip-card info">
              <h3>실행 팁</h3>
              <ul>
                <li v-for="(item, index) in guide.tips" :key="`tip-${index}`">{{ item }}</li>
                <li v-if="guide.tips.length === 0">다음 과제 제출 후 실행 팁이 표시됩니다.</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.feedback-page,
.guide-shell,
.loading-wrap {
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

.feedback-hero {
  background: linear-gradient(135deg, #1E3A5F, #2C5282);
  border-radius: var(--radius-xl);
  padding: 28px 32px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.feedback-hero::after {
  content: '?';
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 72px;
  font-weight: 800;
  opacity: 0.14;
}

.fh-tag {
  font-size: var(--font-size-xs);
  font-weight: 800;
  color: rgba(255, 255, 255, 0.58);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: var(--space-2);
}

.fh-title {
  font-size: 22px;
  font-weight: 800;
  color: white;
  margin-bottom: 6px;
  letter-spacing: -0.3px;
  padding-right: 78px;
}

.fh-sub {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.66);
  padding-right: 78px;
}

.metric-guide-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-4);
}

.metric-guide-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.mgc-header {
  padding: 20px 24px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid var(--border-light);
}

.mgc-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: 800;
  flex-shrink: 0;
}

.mgc-title-wrap {
  min-width: 0;
}

.mgc-title {
  font-size: var(--font-size-base);
  font-weight: 800;
  line-height: 1.3;
}

.mgc-subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.mgc-score-badge {
  margin-left: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}

.mgc-score {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  line-height: 1;
}

.mgc-status {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  margin-top: 4px;
}

.mgc-status.excellent {
  color: var(--color-success);
}

.mgc-status.good {
  color: var(--color-pi);
}

.mgc-status.risk {
  color: var(--color-danger);
}

.mgc-status.neutral {
  color: var(--text-muted);
}

.mgc-body {
  padding: 20px 24px;
}

.mgc-score-bar {
  height: 6px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-3);
}

.mgc-score-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
}

.mgc-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.65;
  margin-bottom: var(--space-4);
}

.action-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-step {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: var(--space-3);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.action-step:hover {
  background: white;
  box-shadow: var(--shadow-sm);
  transform: translateX(2px);
}

.as-icon {
  font-size: var(--font-size-lg);
  line-height: 1;
  flex-shrink: 0;
  margin-top: 1px;
}

.as-body {
  flex: 1;
}

.as-title {
  font-size: var(--font-size-xs);
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.as-desc {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  line-height: 1.5;
}

.section-gap {
  margin-bottom: var(--space-2);
}

.section-heading {
  font-size: var(--font-size-base);
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.section-heading.no-margin {
  margin-bottom: 2px;
}

.teacher-comments {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.tc-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.tc-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: var(--space-3);
}

.tc-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, #3B82F6, #10B981);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: var(--font-size-xs);
  color: white;
  flex-shrink: 0;
}

.tc-avatar.muted {
  background: var(--color-gray-300);
}

.tc-name {
  font-size: var(--font-size-xs);
  font-weight: 800;
  color: var(--text-primary);
}

.tc-date {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.tc-assign {
  font-size: 10px;
  background: var(--color-gray-100);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  color: var(--text-muted);
  font-weight: 700;
  margin-left: auto;
}

.tc-body {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.7;
}

.muted-comment .tc-body {
  color: var(--text-muted);
}

.next-plan {
  background: linear-gradient(135deg, var(--color-oi-pale), var(--color-pi-pale));
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-xl);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.np-title {
  font-size: var(--font-size-md);
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.np-checklist {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.np-check-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  text-align: left;
  width: 100%;
}

.np-check {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-oi);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
  margin-top: 1px;
}

.np-check.checked {
  background: var(--color-oi);
}

.np-check.checked::after {
  content: '✓';
  color: white;
  font-size: var(--font-size-xs);
  font-weight: 800;
}

.np-check-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

.target-progress {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.target-copy {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.target-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.78);
  border-radius: var(--radius-full);
  margin-top: 6px;
  overflow: hidden;
}

.target-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-aic), var(--color-pi));
  border-radius: var(--radius-full);
}

.tip-section {
  display: grid;
  gap: var(--space-4);
}

.tip-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-4);
}

.tip-card {
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  border: 1px solid var(--border-light);
}

.tip-card.success {
  background: var(--color-oi-pale);
  border-color: rgba(16, 185, 129, 0.2);
}

.tip-card.warning {
  background: var(--color-ui-pale);
  border-color: rgba(249, 115, 22, 0.2);
}

.tip-card.info {
  background: var(--color-pi-pale);
  border-color: rgba(59, 130, 246, 0.2);
}

.tip-card h3 {
  font-size: var(--font-size-sm);
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.tip-card ul {
  display: grid;
  gap: var(--space-2);
}

.tip-card li {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.55;
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

@media (max-width: 1180px) {
  .metric-guide-grid,
  .tip-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .selector-card,
  .grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .selector-controls,
  .selector-error {
    align-items: stretch;
    flex-direction: column;
  }

  .feedback-hero {
    padding: var(--space-6);
  }

  .feedback-hero::after {
    display: none;
  }

  .fh-title,
  .fh-sub {
    padding-right: 0;
  }

  .mgc-header {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .mgc-score-badge {
    width: 100%;
    align-items: flex-start;
    margin-left: 58px;
  }
}
</style>

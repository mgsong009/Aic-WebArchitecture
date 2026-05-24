<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getStudentAssignmentDetail,
  getStudentAssignments,
  getStudentFeedback,
  submitStudentSubmission,
} from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import RadarChart from '@/components/charts/RadarChart.vue'
import { useJobPoller } from '@/composables/useJobPoller'

const route = useRoute()
const router = useRouter()
const assignmentId = computed(() => Number(route.params.id))

const loading = ref(true)
const submitting = ref(false)
const loadError = ref('')
const submitError = ref('')
const payload = ref(null)
const assignmentList = ref([])
const feedbackPayload = ref(null)
const form = ref({
  chatgpt_before: '',
  user_prompt: '',
  essay: '',
})

const { status, metrics, error, startPolling, stop } = useJobPoller()

const metricInfo = [
  { key: 'pi', label: 'PI', name: 'Prompt Insight', color: 'var(--color-pi)', desc: '질문 깊이와 비판성' },
  { key: 'ui', label: 'UI', name: 'User Intervention', color: 'var(--color-ui)', desc: '학생 수정 개입도' },
  { key: 'oi', label: 'OI', name: 'Originality Index', color: 'var(--color-oi)', desc: '독창성과 새 관점' },
  { key: 'topic', label: 'TopicScore', name: 'Topic Relevance', color: 'var(--color-topic)', desc: '주제 적합성' },
]

const assignment = computed(() => payload.value?.assignment || null)
const submission = computed(() => payload.value?.submission || null)
const resultMetrics = computed(() => metrics.value || payload.value?.metrics || null)
const classAvg = computed(() => payload.value?.class_avg || null)
const feedback = computed(() => feedbackPayload.value?.teacher_feedback || null)
const autoGuide = computed(() => feedbackPayload.value?.auto_guide || [])
const selectedAssignment = computed(() => assignmentList.value.find((item) => item.id === assignmentId.value) || null)
const hasResult = computed(() => !!resultMetrics.value)
const isPolling = computed(() => status.value === 'pending' || status.value === 'running')
const canSubmit = computed(() =>
  form.value.chatgpt_before.trim()
  && form.value.user_prompt.trim()
  && form.value.essay.trim()
  && !submitting.value
  && !isPolling.value
)

const assignmentNumber = computed(() => {
  const index = assignmentList.value.findIndex((item) => item.id === assignmentId.value)
  return index >= 0 ? index + 1 : assignmentId.value
})
const assignmentTitle = computed(() => assignment.value?.title || `과제 ${assignmentId.value}`)
const courseCode = computed(() => assignment.value?.course_code || 'CS101')
const submittedDate = computed(() => selectedAssignment.value?.submitted_at || '미제출')
const dueDate = computed(() => selectedAssignment.value?.due_date || '-')
const essayLength = computed(() => `${form.value.essay.trim().length.toLocaleString()}자`)
const promptCount = computed(() => {
  const text = form.value.user_prompt.trim()
  if (!text) return 0
  return Math.max(1, text.split(/\n+|[?？]/).filter((part) => part.trim()).length)
})
const aicScore = computed(() => resultMetrics.value?.aic ?? null)
const scoreLabel = computed(() => {
  const score = Number(aicScore.value)
  if (!Number.isFinite(score)) return 'Pending'
  if (score >= 85) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 55) return 'Average'
  return 'Needs Work'
})
const scoreClass = computed(() => {
  const score = Number(aicScore.value)
  if (!Number.isFinite(score)) return 'status-pending'
  if (score >= 85) return 'status-excellent'
  if (score >= 70) return 'status-good'
  if (score >= 55) return 'status-average'
  return 'status-risk'
})
const aiStructurePct = computed(() => Math.max(25, 100 - revisionPct.value))
const revisionPct = computed(() => {
  const distance = Number(resultMetrics.value?.ui_distance)
  if (Number.isFinite(distance) && distance > 0) return clamp(Math.round(distance * 100), 10, 90)
  const ui = Number(resultMetrics.value?.ui)
  if (Number.isFinite(ui)) return clamp(Math.round(ui / 2), 12, 70)
  return 34
})
const meaningStudentPct = computed(() => {
  const value = Number(resultMetrics.value?.ui)
  if (Number.isFinite(value)) return clamp(Math.round(value * 0.7), 20, 80)
  return 48
})
const newInfoPct = computed(() => {
  const ratio = Number(resultMetrics.value?.ui_newinfo_ratio)
  if (Number.isFinite(ratio) && ratio > 0) return clamp(Math.round(ratio * 100), 5, 95)
  const oi = Number(resultMetrics.value?.oi)
  if (Number.isFinite(oi)) return clamp(Math.round(oi * 0.8), 20, 90)
  return 60
})
const scoreItems = computed(() => metricInfo.map((item) => {
  const value = resultMetrics.value?.[item.key]
  return {
    ...item,
    value,
    desc: scoreDescription(item.key, value),
    className: `sb-${item.key === 'topic' ? 'ts' : item.key}`,
  }
}))
const radarConfig = computed(() => ({
  type: 'radar',
  data: {
    labels: ['깊이', '비판성', '복잡도', '구체성', '창의성'],
    datasets: [
      {
        label: '내 점수',
        data: [
          normalizeDetailScore(resultMetrics.value?.pi_depth_tokens, resultMetrics.value?.pi, 1.8),
          normalizeRatioScore(resultMetrics.value?.pi_critical_ratio, resultMetrics.value?.pi),
          normalizeDetailScore(resultMetrics.value?.pi_complexity, resultMetrics.value?.pi, 18),
          resultMetrics.value?.topic ?? resultMetrics.value?.pi ?? 0,
          resultMetrics.value?.oi ?? resultMetrics.value?.pi ?? 0,
        ],
        backgroundColor: 'rgba(59,130,246,0.15)',
        borderColor: '#3B82F6',
        borderWidth: 2,
        pointBackgroundColor: '#3B82F6',
        pointRadius: 3,
      },
      {
        label: '반 평균',
        data: [
          classAvg.value?.pi ?? 0,
          classAvg.value?.pi ?? 0,
          classAvg.value?.pi ?? 0,
          classAvg.value?.aic ?? 0,
          classAvg.value?.oi ?? 0,
        ],
        backgroundColor: 'rgba(156,163,175,0.1)',
        borderColor: '#D1D5DB',
        borderWidth: 1.5,
        borderDash: [4, 4],
        pointRadius: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'top', labels: { font: { size: 10 }, boxWidth: 10, padding: 8 } },
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { font: { size: 9 }, backdropColor: 'transparent', stepSize: 20 },
        grid: { color: '#F3F4F6' },
        pointLabels: { font: { size: 10, weight: '600' } },
      },
    },
  },
}))
const detailCards = computed(() => [
  {
    label: 'Prompt Depth',
    value: formatNumber(resultMetrics.value?.pi_depth_tokens),
    desc: '프롬프트 깊이 토큰',
    color: 'var(--color-pi)',
  },
  {
    label: 'Critical Ratio',
    value: formatPercent(resultMetrics.value?.pi_critical_ratio),
    desc: '비판적 요청 비율',
    color: 'var(--color-pi)',
  },
  {
    label: 'Semantic Distance',
    value: formatPercent(resultMetrics.value?.ui_distance),
    desc: 'AI 초안 대비 의미 변화',
    color: 'var(--color-ui)',
  },
  {
    label: 'New Info',
    value: formatPercent(resultMetrics.value?.ui_newinfo_ratio),
    desc: '학생이 추가한 새 정보',
    color: 'var(--color-oi)',
  },
])
const guideSteps = computed(() => {
  if (autoGuide.value.length) {
    return autoGuide.value.map((item, index) => ({
      title: item.title || `개선 단계 ${index + 1}`,
      desc: item.description || item.desc || item,
    }))
  }
  return [
    {
      title: 'AI 초안의 단락 순서 바꾸기',
      desc: 'AI가 제안한 단락 구조를 그대로 사용하지 말고, 자신의 논리 흐름에 맞게 재배치하세요.',
    },
    {
      title: '개인 사례 및 경험 추가',
      desc: '추상적인 AI 답변에 자신의 구체적 경험이나 사례를 1~2개 추가하면 OI가 올라갑니다.',
    },
    {
      title: '프롬프트에 "반박해줘" 추가',
      desc: '반론, 대안, 한계점을 요청하면 PI 깊이와 비판성이 함께 높아집니다.',
    },
    {
      title: '초안 대비 30% 이상 수정 목표',
      desc: '단어 교체보다 문장 수준의 의미 변화를 늘리면 UI 점수가 크게 개선됩니다.',
    },
  ]
})
const stageDraft = computed(() => excerpt(form.value.chatgpt_before, 'AI 초안이 아직 없습니다. 제출 폼에 초안을 입력하면 비교 영역에 반영됩니다.'))
const stageRevision = computed(() => buildRevisionText())
const stageFinal = computed(() => excerpt(form.value.essay, '최종 에세이가 아직 없습니다. 제출 후 분석 결과와 함께 확인할 수 있습니다.'))

onMounted(async () => {
  await load()
})

onUnmounted(() => {
  stop()
})

watch(() => route.params.id, async () => {
  stop()
  status.value = 'idle'
  await load()
})

watch(status, async (nextStatus) => {
  if (nextStatus === 'done') {
    stop()
    await load()
  }
})

async function load() {
  loading.value = true
  loadError.value = ''
  submitError.value = ''
  feedbackPayload.value = null
  try {
    const [detail, assignments] = await Promise.all([
      getStudentAssignmentDetail(assignmentId.value),
      getStudentAssignments().catch(() => []),
    ])
    payload.value = detail
    assignmentList.value = assignments
    if (detail.submission) {
      form.value = {
        chatgpt_before: detail.submission.chatgpt_before || '',
        user_prompt: detail.submission.user_prompt || '',
        essay: detail.submission.essay || '',
      }
      feedbackPayload.value = await getStudentFeedback(assignmentId.value).catch(() => null)
    } else {
      form.value = { chatgpt_before: '', user_prompt: '', essay: '' }
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
    assignment_id: assignmentId.value,
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

function goAssignment(id) {
  router.push(`/student/assignments/${id}`)
}

function printReport() {
  window.print()
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function scoreDescription(key, value) {
  if (value == null) return '분석 대기'
  if (key === 'pi') return value >= 70 ? '질문 깊이 ↑' : '비판적 질문 보강'
  if (key === 'ui') return value >= 70 ? '개입도 충분' : '구조 재배치 필요'
  if (key === 'oi') return value >= 70 ? '독창성 ↑ 우수' : '개인 관점 추가'
  return value >= 70 ? '주제 적합성 높음' : '주제 연결 보강'
}

function normalizeRatioScore(value, fallback) {
  const ratio = Number(value)
  if (Number.isFinite(ratio)) return clamp(Math.round(ratio * 100), 0, 100)
  return fallback ?? 0
}

function normalizeDetailScore(value, fallback, divisor) {
  const number = Number(value)
  if (Number.isFinite(number)) return clamp(Math.round(number / divisor), 0, 100)
  return fallback ?? 0
}

function formatNumber(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number.toLocaleString() : '-'
}

function formatPercent(value) {
  const number = Number(value)
  if (!Number.isFinite(number)) return '-'
  return `${Math.round(number * 100)}%`
}

function excerpt(value, fallback) {
  const text = (value || '').trim().replace(/\s+/g, ' ')
  if (!text) return fallback
  return text.length > 180 ? `${text.slice(0, 180)}...` : text
}

function buildRevisionText() {
  const prompt = excerpt(form.value.user_prompt, '')
  if (prompt) {
    return `학생 프롬프트: ${prompt}`
  }
  return '학생 프롬프트가 아직 없습니다. AI 초안에 어떤 방향을 요청했는지 입력하면 이 단계가 채워집니다.'
}
</script>

<template>
  <AppLayout :title="assignmentTitle" :show-page-header="false">
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

    <div v-else-if="payload" class="assignment-page animate-fade-in">
      <div class="selector-bar">
        <div class="selector-left">
          <button class="btn btn-secondary btn-sm" type="button" @click="router.push('/student/dashboard')">
            ← Back
          </button>
          <div v-if="assignmentList.length" class="tabs assignment-tabs" aria-label="과제 선택">
            <button
              v-for="(item, index) in assignmentList"
              :key="item.id"
              class="tab-item"
              :class="{ active: item.id === assignmentId }"
              type="button"
              @click="goAssignment(item.id)"
            >
              A{{ index + 1 }}
            </button>
          </div>
        </div>
        <button class="btn btn-secondary btn-sm" type="button" @click="printReport">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7,10 12,15 17,10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          리포트 다운로드
        </button>
      </div>

      <section class="assign-hero">
        <div class="assign-hero-info">
          <div class="assign-hero-tag">Assignment #{{ assignmentNumber }} · {{ courseCode }}</div>
          <h1 class="assign-hero-title">{{ assignmentTitle }}</h1>
          <div class="assign-hero-meta">
            <span class="meta-item">제출일: {{ submittedDate }}</span>
            <span class="meta-item">마감일: {{ dueDate }}</span>
            <span class="meta-item">최종 글자 수: {{ essayLength }}</span>
            <span class="meta-item">AI 초안 대비 변경률: {{ revisionPct }}%</span>
            <span class="meta-item">프롬프트 수: {{ promptCount }}회</span>
          </div>
        </div>
        <div class="hero-score">
          <div class="score-label">AIC Score</div>
          <div class="score-big">{{ aicScore ?? '-' }}</div>
          <span class="status-badge" :class="scoreClass">
            {{ scoreLabel }}
          </span>
        </div>
      </section>

      <section class="section-gap">
        <div class="section-title">지표별 점수 분석</div>
        <div class="score-breakdown">
          <div v-for="item in scoreItems" :key="item.key" class="sb-item" :class="item.className">
            <div class="sb-label">{{ item.label }}</div>
            <div class="sb-score" :style="{ color: item.color }">{{ item.value ?? '-' }}</div>
            <div class="sb-bar">
              <div class="sb-bar-fill" :style="{ width: `${item.value ?? 0}%`, background: item.color }"></div>
            </div>
            <div class="sb-desc">{{ item.desc }}</div>
          </div>
        </div>
      </section>

      <section class="grid-2 section-gap">
        <div class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">AI vs 학생 기여도</div>
              <div class="card-subtitle">최종 에세이 기준</div>
            </div>
          </div>
          <div class="card-body">
            <div class="contrib-section">
              <div class="contrib-row">
                <div class="contrib-caption">
                  <span>구성 기여도</span>
                  <span>AI {{ aiStructurePct }}% / 학생 {{ revisionPct }}%</span>
                </div>
                <div class="contrib-bar-wrap">
                  <div class="contrib-ai" :style="{ width: `${aiStructurePct}%` }">AI {{ aiStructurePct }}%</div>
                  <div class="contrib-human">학생 {{ revisionPct }}%</div>
                </div>
              </div>
              <div class="contrib-row">
                <div class="contrib-caption">
                  <span>의미 변화량</span>
                  <span>AI {{ 100 - meaningStudentPct }}% / 학생 {{ meaningStudentPct }}%</span>
                </div>
                <div class="contrib-bar-wrap">
                  <div class="contrib-ai" :style="{ width: `${100 - meaningStudentPct}%` }">{{ 100 - meaningStudentPct }}%</div>
                  <div class="contrib-human">{{ meaningStudentPct }}%</div>
                </div>
              </div>
              <div class="contrib-row">
                <div class="contrib-caption">
                  <span>새 정보 비율</span>
                  <span>AI {{ 100 - newInfoPct }}% / 학생 {{ newInfoPct }}%</span>
                </div>
                <div class="contrib-bar-wrap">
                  <div class="contrib-ai" :style="{ width: `${100 - newInfoPct}%` }">{{ 100 - newInfoPct }}%</div>
                  <div class="contrib-human contrib-green">학생 {{ newInfoPct }}%</div>
                </div>
              </div>
            </div>
            <div class="contrib-legend">
              <div class="contrib-legend-item"><span class="legend-dot ai"></span>AI 기여</div>
              <div class="contrib-legend-item"><span class="legend-dot human"></span>학생 기여</div>
            </div>
          </div>
        </div>

        <div class="card chart-card">
          <div class="card-header">
            <div>
              <div class="card-title">PI 세부 분석</div>
              <div class="card-subtitle">Prompt Insight 구성 요소</div>
            </div>
          </div>
          <div class="card-body">
            <div class="radar-wrap">
              <RadarChart :config="radarConfig" />
            </div>
            <div class="pi-mini-grid">
              <div class="pi-mini">
                <div class="pi-mini-value">{{ formatNumber(resultMetrics?.pi_depth_tokens) }}</div>
                <div class="pi-mini-label">깊이</div>
              </div>
              <div class="pi-mini">
                <div class="pi-mini-value">{{ formatPercent(resultMetrics?.pi_critical_ratio) }}</div>
                <div class="pi-mini-label">비판성</div>
              </div>
              <div class="pi-mini">
                <div class="pi-mini-value">{{ formatNumber(resultMetrics?.pi_complexity) }}</div>
                <div class="pi-mini-label">복잡도</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="card section-gap">
        <div class="card-header">
          <div>
            <div class="card-title">글 변화 과정 (Essay Evolution)</div>
            <div class="card-subtitle">AI 초안 → 학생 프롬프트 → 최종 제출본 비교</div>
          </div>
        </div>
        <div class="card-body">
          <div class="essay-stages">
            <article class="essay-stage">
              <div class="essay-stage-label muted">AI 초안 (Draft 0)</div>
              <p>{{ stageDraft }}</p>
            </article>
            <div class="essay-stage-arrow">→</div>
            <article class="essay-stage">
              <div class="essay-stage-label ui">학생 개입 (Prompt)</div>
              <p>{{ stageRevision }}</p>
            </article>
            <div class="essay-stage-arrow">→</div>
            <article class="essay-stage">
              <div class="essay-stage-label oi">최종 제출 (Final)</div>
              <p>{{ stageFinal }}</p>
            </article>
          </div>
          <div class="stage-legend">
            <span><span class="legend-chip add"></span>학생 추가/수정 방향</span>
            <span><span class="legend-chip del"></span>AI 초안 대비 변화</span>
          </div>
        </div>
      </section>

      <section class="grid-2 section-gap">
        <div class="card card-body submit-card">
          <div class="card-heading">
            <div>
              <h3>제출 작성/수정</h3>
              <p class="text-secondary text-sm">
                {{ submission ? '기존 제출 내용을 수정해 다시 분석할 수 있습니다.' : '제출 후 자동으로 분석이 시작됩니다.' }}
              </p>
            </div>
            <StatusBadge :score="aicScore" />
          </div>
          <div class="field">
            <label>AI 초안 (chatgpt_before)</label>
            <textarea v-model="form.chatgpt_before" rows="5" :disabled="submitting || isPolling"></textarea>
          </div>
          <div class="field">
            <label>학생 프롬프트 (user_prompt)</label>
            <textarea v-model="form.user_prompt" rows="4" :disabled="submitting || isPolling"></textarea>
          </div>
          <div class="field">
            <label>최종 에세이 (essay)</label>
            <textarea v-model="form.essay" rows="7" :disabled="submitting || isPolling"></textarea>
          </div>
          <div v-if="submitError" class="alert alert-danger">{{ submitError }}</div>
          <div class="actions">
            <button class="btn btn-primary" type="button" :disabled="!canSubmit" @click="submitEssay">
              {{ submitting ? '저장 중...' : isPolling ? '분석 중...' : submission ? '재제출하고 재분석' : '제출하고 분석 시작' }}
            </button>
            <button class="btn btn-secondary" type="button" @click="router.push('/student/assignments')">목록으로</button>
          </div>
          <div v-if="status !== 'idle'" class="job-status">
            분석 상태: <strong>{{ status }}</strong>
            <span v-if="error" class="error-text"> - {{ error }}</span>
            <span v-if="metrics"> - AIC: {{ metrics.aic ?? '-' }}</span>
          </div>
        </div>

        <div class="analysis-stack">
          <div class="card card-body">
            <h3>상세 분석 카드</h3>
            <div v-if="isPolling" class="empty-state compact">분석이 진행 중입니다. 완료되면 결과가 자동으로 반영됩니다.</div>
            <div v-else-if="status === 'failed'" class="alert alert-danger">
              {{ error || '분석에 실패했습니다. 내용을 확인한 뒤 다시 제출해 주세요.' }}
            </div>
            <div v-else-if="hasResult" class="detail-grid">
              <div v-for="item in detailCards" :key="item.label" class="detail-card">
                <div class="detail-label">{{ item.label }}</div>
                <div class="detail-value" :style="{ color: item.color }">{{ item.value }}</div>
                <div class="detail-desc">{{ item.desc }}</div>
              </div>
            </div>
            <div v-else class="empty-state compact">아직 분석 결과가 없습니다. 제출을 완료하면 결과가 이곳에 표시됩니다.</div>
          </div>

          <div class="card card-body">
            <h3>반 평균 비교</h3>
            <div class="compare-list">
              <div v-for="item in metricInfo.slice(0, 3)" :key="item.key" class="compare-row">
                <span class="compare-label" :style="{ color: item.color }">{{ item.label }}</span>
                <div class="compare-track">
                  <span class="compare-fill mine" :style="{ width: `${resultMetrics?.[item.key] ?? 0}%`, background: item.color }"></span>
                  <span class="compare-fill avg" :style="{ width: `${classAvg?.[item.key] ?? 0}%` }"></span>
                </div>
                <span class="compare-value">{{ resultMetrics?.[item.key] ?? '-' }} / {{ classAvg?.[item.key] ?? '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="grid-2 section-gap">
        <div>
          <div class="section-title">교사 피드백</div>
          <div class="teacher-feedback-card">
            <div class="tf-header">
              <div class="tf-avatar">김</div>
              <div>
                <div class="tf-name">담당 교사</div>
                <div class="tf-date">{{ feedback?.created_at || '피드백 대기' }}</div>
              </div>
              <span class="status-badge" :class="feedback ? 'status-good' : 'status-pending'">
                {{ feedback ? 'Good' : 'Pending' }}
              </span>
            </div>
            <div class="tf-body">
              {{ feedback?.content || '아직 등록된 교사 피드백이 없습니다. 분석 결과를 바탕으로 자동 개선 가이드를 먼저 확인하세요.' }}
            </div>
          </div>
        </div>

        <div>
          <div class="section-title">자동 개선 가이드</div>
          <div class="guide-list">
            <div v-for="(step, index) in guideSteps" :key="`${step.title}-${index}`" class="guide-step">
              <div class="guide-step-num">{{ index + 1 }}</div>
              <div class="guide-step-body">
                <div class="guide-step-title">{{ step.title }}</div>
                <div class="guide-step-desc">{{ step.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.loading-wrap {
  display: grid;
  gap: var(--space-4);
}

.assignment-page {
  min-width: 0;
}

.selector-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.selector-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.assignment-tabs .tab-item {
  border: 0;
}

.assign-hero {
  background: linear-gradient(135deg, #f0f4f8, #ebf4ff);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: 24px 28px;
  margin-bottom: var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.assign-hero-info {
  min-width: 0;
}

.assign-hero-tag {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-pi);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 6px;
}

.assign-hero-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0;
  margin-bottom: 8px;
  line-height: 1.25;
}

.assign-hero-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 12px;
  color: var(--text-muted);
}

.hero-score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.score-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.score-big {
  font-size: 44px;
  font-weight: 800;
  color: var(--color-aic);
  letter-spacing: 0;
  line-height: 1;
}

.section-gap {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.score-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.sb-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.sb-item::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
}

.sb-pi::before { background: var(--color-pi); }
.sb-ui::before { background: var(--color-ui); }
.sb-oi::before { background: var(--color-oi); }
.sb-ts::before { background: var(--color-topic); }

.sb-score {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 0;
  margin-bottom: 2px;
}

.sb-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.sb-bar {
  height: 4px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: 4px;
}

.sb-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
}

.sb-desc {
  font-size: 10px;
  color: var(--text-muted);
}

.contrib-section {
  display: grid;
  gap: 12px;
}

.contrib-caption {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.contrib-bar-wrap {
  height: 40px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  overflow: hidden;
  display: flex;
}

.contrib-ai,
.contrib-human {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  padding: 0 8px;
  font-size: 12px;
  font-weight: 700;
  color: white;
  white-space: nowrap;
}

.contrib-ai {
  background: linear-gradient(90deg, #6b7280, #9ca3af);
}

.contrib-human {
  flex: 1;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.contrib-green {
  background: linear-gradient(90deg, #10b981, #059669);
}

.contrib-legend {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 12px;
}

.contrib-legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.ai { background: #9ca3af; }
.legend-dot.human { background: #3b82f6; }

.radar-wrap {
  height: 200px;
}

.pi-mini-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
}

.pi-mini {
  text-align: center;
  padding: 8px;
  background: var(--color-gray-50);
  border-radius: 8px;
}

.pi-mini-value {
  font-size: 16px;
  font-weight: 800;
  color: var(--color-pi);
}

.pi-mini-label {
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 600;
}

.essay-stages {
  display: flex;
  gap: 8px;
}

.essay-stage {
  flex: 1;
  min-width: 0;
  background: var(--color-gray-50);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 12px;
  font-size: 11px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.essay-stage-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.essay-stage-label.muted { color: var(--text-muted); }
.essay-stage-label.ui { color: var(--color-ui); }
.essay-stage-label.oi { color: var(--color-oi); }

.essay-stage-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 18px;
  padding: 0 4px;
}

.stage-legend {
  margin-top: 12px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 11px;
  color: var(--text-secondary);
}

.stage-legend span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.legend-chip {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  display: inline-block;
}

.legend-chip.add {
  background: #dcfce7;
  border: 1px solid #86efac;
}

.legend-chip.del {
  background: #fee2e2;
  border: 1px solid #fca5a5;
}

.submit-card h3,
.analysis-stack h3 {
  margin-bottom: 0.2rem;
}

.card-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
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
  resize: vertical;
}

textarea:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

textarea:disabled {
  background: var(--color-gray-50);
  color: var(--text-secondary);
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

.analysis-stack {
  display: grid;
  gap: var(--space-4);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.detail-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--color-gray-50);
  padding: var(--space-3);
}

.detail-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  margin-top: 4px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
}

.detail-desc {
  margin-top: 6px;
  font-size: 11px;
  color: var(--text-secondary);
}

.compare-list {
  display: grid;
  gap: var(--space-3);
}

.compare-row {
  display: grid;
  grid-template-columns: 36px 1fr 68px;
  align-items: center;
  gap: var(--space-2);
  font-size: 11px;
}

.compare-label {
  font-weight: 800;
}

.compare-track {
  position: relative;
  height: 10px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.compare-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  border-radius: var(--radius-full);
}

.compare-fill.avg {
  height: 3px;
  top: auto;
  bottom: 0;
  background: rgba(31, 41, 55, 0.35);
}

.compare-value {
  color: var(--text-muted);
  text-align: right;
}

.compact {
  padding: var(--space-6);
}

.teacher-feedback-card {
  background: linear-gradient(135deg, #eff6ff, #f0fdf4);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-xl);
  padding: 20px 24px;
}

.tf-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.tf-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--color-pi), var(--color-oi));
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: white;
}

.tf-header .status-badge {
  margin-left: auto;
}

.tf-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.tf-date {
  font-size: 11px;
  color: var(--text-muted);
}

.tf-body {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  white-space: pre-line;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guide-step {
  display: flex;
  gap: 12px;
  padding: 14px;
  border-radius: var(--radius-md);
  background: var(--color-gray-50);
  border: 1px solid var(--border-light);
  transition: all var(--transition-fast);
}

.guide-step:hover {
  background: white;
  box-shadow: var(--shadow-sm);
}

.guide-step-num {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--color-aic);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
}

.guide-step-body {
  flex: 1;
}

.guide-step-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 3px;
}

.guide-step-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .score-breakdown {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .selector-bar,
  .assign-hero {
    align-items: stretch;
    flex-direction: column;
  }

  .hero-score {
    align-items: flex-start;
  }

  .essay-stages {
    flex-direction: column;
  }

  .essay-stage-arrow {
    transform: rotate(90deg);
    padding: 0;
  }
}

@media (max-width: 560px) {
  .score-breakdown,
  .detail-grid,
  .pi-mini-grid {
    grid-template-columns: 1fr;
  }

  .compare-row {
    grid-template-columns: 32px 1fr;
  }

  .compare-value {
    grid-column: 2;
    text-align: left;
  }
}
</style>

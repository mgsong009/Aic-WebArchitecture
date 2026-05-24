<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeacherStudentDetail, saveTeacherFeedback } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import DonutChart from '@/components/common/DonutChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { referenceStudentDetail, scoreColor, scoreTone } from './teacherReferenceData'

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

onMounted(load)

const displayDetail = computed(() => detail.value || referenceStudentDetail)
const student = computed(() => displayDetail.value.student || referenceStudentDetail.student)
const metrics = computed(() => ({ ...referenceStudentDetail.latest_metrics, ...(displayDetail.value.latest_metrics || {}) }))
const assignments = computed(() => displayDetail.value.assignments?.length ? displayDetail.value.assignments : referenceStudentDetail.assignments)
const selectedAssignment = computed(() => assignments.value.find((assignment) => String(assignment.id) === String(selectedAssignmentId.value)) || assignments.value[0])
const previousFeedback = computed(() => displayDetail.value.previous_feedback || referenceStudentDetail.previous_feedback)
const weakMetrics = computed(() => displayDetail.value.weak_metrics?.length ? displayDetail.value.weak_metrics : referenceStudentDetail.weak_metrics)
const classAvg = computed(() => displayDetail.value.class_avg || referenceStudentDetail.class_avg)
const canSaveFeedback = computed(() => Boolean(selectedAssignmentId.value) && Boolean(feedbackText.value.trim()) && !saving.value && Boolean(detail.value))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherStudentDetail(studentId)
    detail.value = data
    selectedAssignmentId.value = String(data.assignments?.at(-1)?.id || data.assignments?.[0]?.id || referenceStudentDetail.assignments[0].id)
    feedbackText.value = data.teacher_feedback?.content || referenceStudentDetail.teacher_feedback.content
  } catch {
    detail.value = null
    selectedAssignmentId.value = String(referenceStudentDetail.assignments[0].id)
    feedbackText.value = referenceStudentDetail.teacher_feedback.content
    error.value = '실시간 학생 상세를 불러오지 못해 reference fallback을 표시합니다.'
  } finally {
    loading.value = false
  }
}

async function saveFeedback() {
  if (!canSaveFeedback.value) return
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

const trendConfig = computed(() => ({
  type: 'line',
  data: {
    labels: (displayDetail.value.trend || referenceStudentDetail.trend).map((point) => point.label),
    datasets: [
      { label: 'AIC', data: (displayDetail.value.trend || referenceStudentDetail.trend).map((point) => point.aic), borderColor: '#1E3A5F', backgroundColor: 'rgba(30,58,95,0.07)', fill: true, tension: 0.4, borderWidth: 2.5, pointRadius: 4 },
      { label: 'PI', data: (displayDetail.value.trend || referenceStudentDetail.trend).map((point) => point.pi), borderColor: '#3B82F6', tension: 0.4, borderWidth: 1.5, pointRadius: 0 },
      { label: 'UI', data: (displayDetail.value.trend || referenceStudentDetail.trend).map((point) => point.ui), borderColor: '#F97316', tension: 0.4, borderWidth: 1.5, pointRadius: 0 },
      { label: 'OI', data: (displayDetail.value.trend || referenceStudentDetail.trend).map((point) => point.oi), borderColor: '#10B981', tension: 0.4, borderWidth: 1.5, pointRadius: 0 },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true, position: 'top', labels: { font: { size: 10, family: 'Inter' }, boxWidth: 10 } } },
    scales: { y: { min: 40, max: 90, grid: { color: '#F3F4F6' }, ticks: { font: { size: 10 } } }, x: { grid: { display: false }, ticks: { font: { size: 11 } } } },
  },
}))

const weaknessCards = computed(() => [
  { key: 'pi', label: 'PI', value: metrics.value.pi, avg: classAvg.value.pi, color: 'var(--color-pi)', text: '비판적 질문과 문제 정의의 명확성을 더 높이면 상위권 안정화가 가능합니다.' },
  { key: 'ui', label: 'UI', value: metrics.value.ui, avg: classAvg.value.ui, color: 'var(--color-ui)', text: 'AI 초안의 논리 구조를 더 적극적으로 재배치하면 의미 있는 개선이 커집니다.' },
  { key: 'oi', label: 'OI', value: metrics.value.oi, avg: classAvg.value.oi, color: 'var(--color-oi)', text: '독창적 관점 서술이 강점입니다. 사례 근거를 더 붙이면 설득력이 좋아집니다.' },
])
</script>

<template>
  <AppLayout :title="student.name || 'Student Detail'" :subtitle="`${student.user_id_str || 'STU006'} · CS101 · 컴퓨터과학 개론`" :show-page-header="false">
    <template #actions>
      <button class="btn btn-secondary btn-sm" type="button" @click="router.push('/teacher/students')">← 목록으로</button>
      <button class="btn btn-secondary btn-sm" type="button">이전 학생</button>
      <button class="btn btn-secondary btn-sm" type="button">다음 학생</button>
    </template>

    <div class="detail-page animate-fade-in">
      <p v-if="error" class="fallback-note">{{ error }}</p>

      <section class="student-profile-card">
        <div class="sp-avatar">{{ student.name?.slice(1, 2) || student.name?.slice(0, 1) || '민' }}</div>
        <div class="sp-info">
          <h1 class="sp-name">{{ student.name || '김민준' }}</h1>
          <div class="sp-meta">
            <span>{{ student.user_id_str || 'STU006' }}</span>
            <span>CS101 · 컴퓨터과학 개론</span>
            <span>{{ selectedAssignment?.label || 'Assignment #5' }} 제출</span>
            <span>{{ selectedAssignment?.submitted_at || '2025.03.18' }}</span>
          </div>
          <div class="sp-badges">
            <StatusBadge :score="metrics.aic" />
            <span class="badge badge-pi">PI {{ metrics.pi }}</span>
            <span class="badge badge-ui">UI {{ metrics.ui }}</span>
            <span class="badge badge-oi">OI {{ metrics.oi }}</span>
            <span class="badge badge-topic">TS {{ metrics.topic ?? '-' }}</span>
            <span class="badge badge-warning">{{ weakMetrics.join(', ') }} 개선 필요</span>
          </div>
        </div>
        <div class="sp-aic-display">
          <div class="sp-aic-label">AIC Score</div>
          <strong class="sp-aic-val">{{ metrics.aic ?? '-' }}</strong>
          <span class="growth-text">↑ +5 (A4→A5)</span>
          <span class="rank-text">상위 25% · {{ displayDetail.rank || 7 }}위/{{ displayDetail.total_students || 28 }}명</span>
        </div>
      </section>

      <div class="detail-grid score-grid">
        <section class="card">
          <div class="card-header"><div class="card-title">AIC Score</div></div>
          <div class="card-body donut-card">
            <DonutChart :score="Number(metrics.aic || 0)" label="AIC" :size="140" color="var(--color-aic)" />
            <div class="metric-mini-grid">
              <div class="mini pi"><strong>{{ metrics.pi }}</strong><span>PI</span></div>
              <div class="mini ui"><strong>{{ metrics.ui }}</strong><span>UI</span></div>
              <div class="mini oi"><strong>{{ metrics.oi }}</strong><span>OI</span></div>
              <div class="mini topic"><strong>{{ metrics.topic ?? '-' }}</strong><span>TS</span></div>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-header"><div><div class="card-title">지표 vs 반 평균</div></div></div>
          <div class="card-body metric-bars">
            <div v-for="item in weaknessCards" :key="item.key" class="metric-bar-item">
              <span :style="{ color: item.color }">{{ item.label }}</span>
              <div class="score-bar-track">
                <div class="score-bar-fill avg" :style="{ width: `${item.avg || 0}%` }"></div>
                <div class="score-bar-fill" :style="{ width: `${item.value || 0}%`, background: item.color }"></div>
              </div>
              <strong>{{ item.value }}</strong>
            </div>
            <div class="rank-list">
              <div><b class="pi-text">PI</b> 반에서 <strong>9위</strong>/28명 <span class="badge badge-pi">상위 32%</span></div>
              <div><b class="ui-text">UI</b> 반에서 <strong>13위</strong>/28명 <span class="badge badge-warning">하위 50%</span></div>
              <div><b class="oi-text">OI</b> 반에서 <strong>6위</strong>/28명 <span class="badge badge-oi">상위 21%</span></div>
            </div>
          </div>
        </section>

        <section class="card weakness-panel">
          <div class="card-header"><div><div class="card-title">취약 지표 분석</div><div class="card-subtitle">개선 우선순위</div></div></div>
          <div class="card-body weakness-grid">
            <article v-for="item in weaknessCards" :key="item.label" class="weakness-card" :class="`tone-${scoreTone(item.value)}`">
              <div class="weakness-head"><span :style="{ color: item.color }">{{ item.label }}</span><strong :style="{ color: item.color }">{{ item.value }}</strong></div>
              <div class="score-bar-track"><div class="score-bar-fill" :style="{ width: `${item.value || 0}%`, background: item.color }"></div></div>
              <p>반 평균({{ item.avg ?? '-' }}) 대비 {{ item.value - item.avg >= 0 ? '+' : '' }}{{ Math.round((item.value || 0) - (item.avg || 0)) }}. {{ item.text }}</p>
            </article>
          </div>
        </section>
      </div>

      <div class="grid-2">
        <section class="card">
          <div class="card-header"><div><div class="card-title">성장 추이</div><div class="card-subtitle">전체 과제 기준</div></div></div>
          <div class="card-body chart-body"><LineChart :config="trendConfig" /></div>
        </section>

        <section class="card">
          <div class="card-header"><div class="card-title">과제 이력</div></div>
          <div class="card-body assignment-history">
            <button v-for="assignment in assignments" :key="assignment.id" class="ah-item" :class="{ active: String(assignment.id) === String(selectedAssignmentId) }" type="button" @click="selectedAssignmentId = String(assignment.id)">
              <span class="ah-num">{{ assignment.label || `A${assignment.id}` }}</span>
              <span class="ah-info"><strong>{{ assignment.title }}</strong><small>{{ assignment.submitted_at || '-' }}</small></span>
              <StatusBadge :score="assignment.aic" />
              <strong class="ah-aic" :style="{ color: scoreColor(assignment.aic) }">{{ assignment.aic ?? '-' }}</strong>
            </button>
          </div>
        </section>
      </div>

      <div class="grid-2">
        <section>
          <h2 class="section-label">교사 피드백 작성</h2>
          <div class="feedback-editor">
            <div class="fe-header">
              <strong>{{ selectedAssignment?.label || 'Assignment #5' }} 피드백</strong>
              <span class="badge badge-ui">UI 개선 중점</span>
            </div>
            <textarea v-model="feedbackText" class="fe-textarea" :disabled="saving" placeholder="학생 피드백을 작성하세요..."></textarea>
            <div class="fe-footer">
              <span v-if="saveMessage" class="success-text">{{ saveMessage }}</span>
              <span v-else class="fe-info">{{ detail ? '저장 가능' : 'fallback 미리보기' }}</span>
              <div class="actions">
                <button class="btn btn-secondary btn-sm" type="button" :disabled="!detail">임시저장</button>
                <button class="btn btn-primary btn-sm" type="button" :disabled="!canSaveFeedback" @click="saveFeedback">{{ saving ? '전송 중...' : '피드백 전송' }}</button>
              </div>
            </div>
          </div>
        </section>

        <section>
          <h2 class="section-label">이전 피드백 이력</h2>
          <div class="prev-feedback">
            <article v-for="item in previousFeedback" :key="`${item.assignment}-${item.date}`" class="pf-item">
              <div class="pf-header"><strong>{{ item.assignment }}</strong><span>{{ item.date }}</span></div>
              <p>{{ item.body }}</p>
            </article>
          </div>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.detail-page { display: grid; gap: var(--space-4); min-width: 0; }
.fallback-note { padding: var(--space-3) var(--space-4); background: var(--color-ui-pale); border: 1px solid rgba(249, 115, 22, 0.2); border-radius: var(--radius-lg); color: var(--text-secondary); font-size: var(--text-sm); }
.student-profile-card { background: white; border: 1px solid var(--border-light); border-radius: var(--radius-xl); padding: 24px 28px; display: flex; align-items: center; gap: 20px; box-shadow: var(--shadow-sm); min-width: 0; }
.sp-avatar { width: 64px; height: 64px; border-radius: 999px; display: grid; place-items: center; font-size: 24px; font-weight: 800; color: white; background: linear-gradient(135deg, #3B82F6, #10B981); flex-shrink: 0; }
.sp-info { flex: 1; min-width: 0; }
.sp-name { font-size: 22px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.3px; margin: 0 0 4px; }
.sp-meta, .sp-badges { display: flex; gap: 8px 16px; flex-wrap: wrap; }
.sp-meta { font-size: 13px; color: var(--text-muted); }
.sp-badges { margin-top: 8px; }
.sp-aic-display { text-align: right; display: grid; gap: 2px; min-width: 0; }
.sp-aic-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; }
.sp-aic-val { font-size: 44px; font-weight: 800; color: var(--color-aic); letter-spacing: -2px; line-height: 1; }
.growth-text { font-size: 11px; color: var(--color-success); }
.rank-text { font-size: 11px; color: var(--text-muted); }
.detail-grid { display: grid; gap: var(--space-4); }
.score-grid { grid-template-columns: 1fr 1fr 2fr; }
.donut-card { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.metric-mini-grid { width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.mini { padding: 8px; border-radius: 8px; text-align: center; }
.mini strong { display: block; font-size: 16px; }
.mini span { font-size: 10px; color: var(--text-muted); }
.mini.pi { background: var(--color-pi-pale); color: var(--color-pi); }
.mini.ui { background: var(--color-ui-pale); color: var(--color-ui); }
.mini.oi { background: var(--color-oi-pale); color: var(--color-oi); }
.mini.topic { background: var(--color-topic-pale); color: var(--color-topic); }
.metric-bars { display: grid; gap: 12px; }
.metric-bar-item { display: grid; grid-template-columns: 32px 1fr 32px; align-items: center; gap: 10px; font-size: 12px; }
.metric-bar-item > span, .metric-bar-item > strong { font-weight: 800; }
.score-bar-track { position: relative; height: 8px; background: var(--color-gray-100); border-radius: 999px; overflow: hidden; }
.score-bar-fill { position: absolute; inset: 0 auto 0 0; border-radius: inherit; }
.score-bar-fill.avg { background: var(--color-gray-300); }
.rank-list { display: grid; gap: 6px; margin-top: 6px; font-size: 12px; color: var(--text-muted); }
.pi-text { color: var(--color-pi); }
.ui-text { color: var(--color-ui); }
.oi-text { color: var(--color-oi); }
.weakness-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.weakness-card { background: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-lg); padding: 16px; border-top: 3px solid var(--color-warning); }
.weakness-card.tone-risk { border-top-color: var(--color-danger); }
.weakness-card.tone-good, .weakness-card.tone-excellent { border-top-color: var(--color-oi); }
.weakness-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.weakness-head span, .weakness-head strong { font-size: 20px; font-weight: 800; }
.weakness-card p { margin-top: 8px; font-size: 11px; color: var(--text-muted); line-height: 1.55; }
.chart-body { height: 240px; }
.assignment-history { padding: 8px 12px; display: grid; gap: 4px; }
.ah-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: var(--radius-md); background: var(--color-gray-50); border: 1px solid var(--border-light); text-align: left; }
.ah-item.active, .ah-item:hover { background: white; box-shadow: var(--shadow-sm); }
.ah-num { font-size: 11px; font-weight: 800; color: var(--text-muted); width: 24px; }
.ah-info { flex: 1; min-width: 0; }
.ah-info strong { display: block; font-size: 12px; color: var(--text-primary); }
.ah-info small { font-size: 10px; color: var(--text-muted); }
.ah-aic { font-size: 16px; }
.section-label { font-size: 14px; font-weight: 800; margin: 0 0 12px; }
.feedback-editor { background: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-xl); overflow: hidden; }
.fe-header { padding: 16px 20px; border-bottom: 1px solid var(--border-light); display: flex; align-items: center; justify-content: space-between; }
.fe-textarea { width: 100%; min-height: 154px; padding: 16px 20px; border: 0; resize: vertical; line-height: 1.6; outline: 0; color: var(--text-primary); }
.fe-footer { padding: 10px 16px; border-top: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center; background: var(--color-gray-50); gap: var(--space-3); }
.fe-info { font-size: 11px; color: var(--text-muted); }
.success-text { font-size: 12px; color: var(--color-success); font-weight: 700; }
.prev-feedback { display: grid; gap: 8px; }
.pf-item { padding: 12px 14px; background: var(--color-gray-50); border-radius: var(--radius-md); border: 1px solid var(--border-light); }
.pf-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 11px; }
.pf-header strong { color: var(--color-pi); }
.pf-header span { color: var(--text-muted); }
.pf-item p { font-size: 12px; color: var(--text-secondary); line-height: 1.55; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
@media (max-width: 1100px) { .score-grid { grid-template-columns: 1fr; } .weakness-grid { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .student-profile-card { align-items: flex-start; flex-direction: column; } .sp-aic-display { width: 100%; text-align: left; } .sp-meta, .sp-badges, .fe-header { gap: 6px; } .fe-footer { align-items: stretch; flex-direction: column; } }
</style>

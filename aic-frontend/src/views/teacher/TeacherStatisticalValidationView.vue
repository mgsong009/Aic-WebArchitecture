<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeacherStatisticsValidation } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { key: 'fairness', label: '공정성 검증', title: '공정성 검증: 과제 난이도 보정 AIC' },
  { key: 'confidence', label: '신뢰성 검증', title: '신뢰성 검증: AIC 신뢰구간' },
  { key: 'anomaly', label: '해석 안정성 검증', title: '해석 안정성 검증: 이상패턴 감지' },
]
const validTabKeys = tabs.map((tab) => tab.key)

const loading = ref(true)
const error = ref('')
const activeTab = ref(validTabKeys.includes(route.query.tab) ? route.query.tab : 'fairness')
const selectedConfidenceTarget = ref('overall')
const showRules = ref(false)
const difficultyAdjusted = ref({ overall_mean_aic: null, summary: [], students: [], method_note: '' })
const confidenceIntervals = ref([])
const anomalyDetection = ref({
  items: [],
  summary_counts: { total: 0, high: 0, caution: 0, low: 0 },
  rule_counts: [],
  method_note: '',
})

onMounted(loadStatistics)

watch(
  () => route.query.tab,
  (tab) => {
    activeTab.value = validTabKeys.includes(tab) ? tab : 'fairness'
  }
)

watch(activeTab, (tab) => {
  if (route.query.tab !== tab) {
    router.replace({ query: { ...route.query, tab } })
  }
})

async function loadStatistics() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherStatisticsValidation()
    difficultyAdjusted.value = data.difficulty_adjusted_aic
    confidenceIntervals.value = data.confidence_intervals
    anomalyDetection.value = data.anomaly_detection
    selectedConfidenceTarget.value = confidenceOptions.value[0]?.value || 'overall'
  } catch (err) {
    difficultyAdjusted.value = { overall_mean_aic: null, summary: [], students: [], method_note: '' }
    confidenceIntervals.value = []
    anomalyDetection.value = {
      items: [],
      summary_counts: { total: 0, high: 0, caution: 0, low: 0 },
      rule_counts: [],
      method_note: '',
    }
    error.value = err.response?.data?.detail || '통계 검증 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const currentTab = computed(() => tabs.find((tab) => tab.key === activeTab.value) || tabs[0])
const difficultySummary = computed(() => difficultyAdjusted.value.summary || [])
const overallMeanAic = computed(() => difficultyAdjusted.value.overall_mean_aic ?? difficultySummary.value[0]?.overall_mean_aic ?? null)
const hardestAssignment = computed(() => difficultySummary.value.filter((item) => Number(item.adjustment_offset) > 0).sort((a, b) => Number(b.adjustment_offset) - Number(a.adjustment_offset))[0] || null)
const easiestAssignment = computed(() => difficultySummary.value.filter((item) => Number(item.adjustment_offset) < 0).sort((a, b) => Number(a.adjustment_offset) - Number(b.adjustment_offset))[0] || null)
const confidenceRows = computed(() => confidenceIntervals.value || [])
const confidenceOptions = computed(() => confidenceRows.value.map((row) => ({
  value: confidenceValue(row),
  label: row.target_type === 'overall' ? '전체 AIC' : row.target_title || `과제 #${row.target_id}`,
})))
const selectedConfidence = computed(() => confidenceRows.value.find((row) => confidenceValue(row) === selectedConfidenceTarget.value) || confidenceRows.value[0] || null)
const selectedConfidenceLabel = computed(() => selectedConfidence.value?.target_type === 'overall' ? '전체 AIC' : selectedConfidence.value?.target_title || `과제 #${selectedConfidence.value?.target_id}`)
const assignmentConfidenceRows = computed(() => confidenceRows.value.filter((row) => row.target_type === 'assignment'))
const anomalyItems = computed(() => anomalyDetection.value.items || [])
const anomalyTopItems = computed(() => anomalyItems.value.slice(0, 5))
const anomalySummary = computed(() => anomalyDetection.value.summary_counts || { total: 0, high: 0, caution: 0, low: 0 })
const ruleCounts = computed(() => anomalyDetection.value.rule_counts || [])
const mostCommonRule = computed(() => [...ruleCounts.value].sort((a, b) => Number(b.count) - Number(a.count))[0] || null)
const ciCurve = computed(() => buildCiCurve(selectedConfidence.value))

function setActiveTab(tab) {
  activeTab.value = tab
}

function confidenceValue(row) {
  return row?.target_type === 'overall' ? 'overall' : `assignment-${row?.target_id}`
}

function selectConfidence(row) {
  selectedConfidenceTarget.value = confidenceValue(row)
}

function formatNumber(value, digits = 1) {
  const next = Number(value)
  return Number.isFinite(next) ? next.toFixed(digits) : '-'
}

function formatSigned(value) {
  const next = Number(value)
  if (!Number.isFinite(next)) return '-'
  return `${next > 0 ? '+' : ''}${next.toFixed(1)}`
}

function formatInterval(row) {
  if (!row || row.lower == null || row.upper == null) return '표본 부족'
  return `${formatNumber(row.lower)} ~ ${formatNumber(row.upper)}`
}

function reliabilityText(label) {
  return {
    stable: '안정',
    caution: '주의',
    unstable: '불안정',
  }[label] || '확인'
}

function severityText(label) {
  return {
    high: 'High',
    caution: 'Caution',
    low: 'Low',
  }[label] || label
}

function difficultyText(label) {
  return {
    hard: '어려움',
    easy: '쉬움',
    normal: '보통',
    typical: '보통',
  }[label] || '보통'
}

function difficultyInterpretation(item) {
  if (item?.interpretation) return item.interpretation
  if (item?.difficulty_label === 'hard') return '상향 보정 참고'
  if (item?.difficulty_label === 'easy') return '원점수 보수 해석'
  return '일반 해석'
}

function metricLabel(value, suffix = '') {
  return value == null ? '-' : `${formatNumber(value)}${suffix}`
}

function buildCiCurve(row) {
  const mean = Number(row?.mean)
  const lower = Number(row?.lower)
  const upper = Number(row?.upper)
  if (!Number.isFinite(mean)) {
    return null
  }

  const ciWidth = Number.isFinite(lower) && Number.isFinite(upper) ? upper - lower : 10
  const sidePadding = Math.max(ciWidth * 0.65, 3)
  const minValue = Math.max(0, Math.floor((Number.isFinite(lower) ? lower : mean - 10) - sidePadding))
  const maxValue = Math.min(100, Math.ceil((Number.isFinite(upper) ? upper : mean + 10) + sidePadding))
  const range = Math.max(maxValue - minValue, 1)
  const toX = (value) => 34 + ((value - minValue) / range) * 532
  const meanX = toX(mean)
  const lowerX = Number.isFinite(lower) ? toX(lower) : null
  const upperX = Number.isFinite(upper) ? toX(upper) : null
  const spread = Math.max(Number(row?.margin) || Number(row?.std) || range / 6, 4)
  const baselineY = 126
  const peakY = 42
  const axisY = 146
  const samples = []

  for (let i = 0; i <= 80; i += 1) {
    const value = minValue + (range * i) / 80
    const x = toX(value)
    const y = baselineY - Math.exp(-((value - mean) ** 2) / (2 * spread ** 2)) * (baselineY - peakY)
    samples.push({ value, x, y })
  }

  const curvePoints = samples.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`)
  const ciSamples = lowerX != null && upperX != null
    ? samples.filter((point) => point.value >= lower && point.value <= upper)
    : []
  const ciAreaPoints = ciSamples.length
    ? [
      `${lowerX.toFixed(1)},${baselineY}`,
      ...ciSamples.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`),
      `${upperX.toFixed(1)},${baselineY}`,
    ].join(' ')
    : ''

  return {
    minValue,
    maxValue,
    baselineY,
    peakY,
    axisY,
    meanX,
    lowerX,
    upperX,
    points: curvePoints.join(' '),
    ciAreaPoints,
  }
}

const detectionRules = [
  ['AI 초안 의존 가능성', 'ui_cos_similarity >= 0.85 and UI < 50'],
  ['주제 이탈형 독창성', 'OI >= 70 and TopicScore < 50'],
  ['무의미한 대량 수정 가능성', 'UI >= 70 and TopicScore < 50'],
  ['지표 편중 고득점', 'assignment_z >= 2 and max(PI, UI, OI) - min(PI, UI, OI) >= 40'],
  ['전반적 협업 저하', 'PI < 40 and UI < 40 and OI < 40'],
]
</script>

<template>
  <AppLayout title="AIC 통계 검증" subtitle="AIC Index의 공정성, 신뢰성, 해석 안정성 검증" :show-page-header="false">
    <div v-if="error" class="alert alert-warning mb-4">{{ error }}</div>
    <div v-if="loading" class="card loading-state">불러오는 중...</div>

    <div v-else>
      <section class="stats-hero">
        <div class="ah-tag">Statistical Validation</div>
        <h1 class="ah-title">AIC 통계 검증</h1>
        <p class="ah-sub">AIC Index의 공정성, 신뢰성, 해석 안정성을 검증합니다. 분석 결과는 AIC 점수를 대체하지 않고 점수 해석의 타당성을 보조합니다.</p>
        <div class="ah-tabs" role="tablist" aria-label="AIC 통계 검증 탭">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="ah-tab"
            :class="{ active: activeTab === tab.key }"
            :aria-selected="activeTab === tab.key"
            @click="setActiveTab(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>
      </section>

      <section class="validation-panel section-gap">
        <div class="panel-heading">
          <div>
            <div class="section-eyebrow">{{ currentTab.label }}</div>
            <h2>{{ currentTab.title }}</h2>
          </div>
        </div>

        <template v-if="activeTab === 'fairness'">
          <p class="purpose-copy">과제별 평균 AIC가 전체 평균보다 낮으면 어려운 과제로 보고 상향 보정하며, 전체 평균보다 높으면 쉬운 과제로 보고 보수적으로 해석합니다.</p>

          <div class="metric-grid">
            <article class="metric-card">
              <span>분석 기준</span>
              <strong>{{ metricLabel(overallMeanAic) }}</strong>
              <small>전체 평균 AIC</small>
            </article>
            <article class="metric-card">
              <span>가장 어려운 과제</span>
              <strong>{{ hardestAssignment?.assignment_title || '-' }}</strong>
              <small>{{ hardestAssignment ? `상향 보정 ${formatSigned(hardestAssignment.adjustment_offset)}점` : '분석 가능한 데이터가 없습니다.' }}</small>
            </article>
            <article class="metric-card">
              <span>가장 쉬운 과제</span>
              <strong>{{ easiestAssignment?.assignment_title || '-' }}</strong>
              <small>{{ easiestAssignment ? `보수 해석 ${formatSigned(easiestAssignment.adjustment_offset)}점` : '분석 가능한 데이터가 없습니다.' }}</small>
            </article>
          </div>

          <div v-if="difficultySummary.length" class="stat-table-wrap section-gap compact-gap">
            <table class="stat-table">
              <thead>
                <tr><th>과제</th><th>n</th><th>과제 평균 AIC</th><th>전체 평균 AIC</th><th>보정폭</th><th>난이도</th><th>해석</th></tr>
              </thead>
              <tbody>
                <tr v-for="item in difficultySummary" :key="item.assignment_id">
                  <td>{{ item.assignment_title }}</td>
                  <td>{{ item.n }}</td>
                  <td>{{ formatNumber(item.assignment_mean_aic) }}</td>
                  <td>{{ formatNumber(item.overall_mean_aic) }}</td>
                  <td>{{ formatSigned(item.adjustment_offset) }}</td>
                  <td><span class="mini-badge">{{ difficultyText(item.difficulty_label) }}</span></td>
                  <td>{{ difficultyInterpretation(item) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-note section-gap compact-gap">분석 가능한 데이터가 없습니다.</div>

          <div class="method-note">Method: {{ difficultyAdjusted.method_note || 'adjusted_aic = raw_aic + (overall_mean_aic - assignment_mean_aic)' }}</div>
        </template>

        <template v-else-if="activeTab === 'confidence'">
          <p class="purpose-copy">평균 AIC는 표본 수와 학생 간 편차에 따라 불안정할 수 있습니다. 95% 신뢰구간을 통해 평균 점수의 해석 안정성을 확인합니다.</p>

          <label class="target-select">
            <span>분석 대상 선택</span>
            <select v-model="selectedConfidenceTarget">
              <option v-for="option in confidenceOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>

          <div class="metric-grid">
            <article class="metric-card">
              <span>평균 AIC</span>
              <strong>{{ metricLabel(selectedConfidence?.mean) }}</strong>
              <small>n = {{ selectedConfidence?.n ?? '-' }}</small>
            </article>
            <article class="metric-card">
              <span>95% 신뢰구간</span>
              <strong>{{ formatInterval(selectedConfidence) }}</strong>
              <small>CI 폭 {{ selectedConfidence?.ci_width == null ? '-' : formatNumber(selectedConfidence.ci_width) }}</small>
            </article>
            <article class="metric-card">
              <span>해석 신뢰도</span>
              <strong>{{ reliabilityText(selectedConfidence?.reliability_label) }}</strong>
              <small>{{ selectedConfidence?.reliability_label || '확인' }}</small>
            </article>
          </div>

          <section class="ci-graph-card section-gap compact-gap">
            <div class="ci-graph-title">
              <div>
                <strong>선택 대상의 AIC 신뢰구간</strong>
                <span>{{ selectedConfidenceLabel }}의 평균 AIC는 {{ formatNumber(selectedConfidence?.mean) }}이며, 95% CI는 {{ formatInterval(selectedConfidence) }}입니다. CI 폭이 넓을수록 평균 해석의 불확실성이 큽니다.</span>
              </div>
            </div>
            <div v-if="ciCurve" class="ci-svg-wrap">
              <svg viewBox="0 0 600 190" role="img" aria-label="AIC 신뢰구간 곡선">
                <polygon v-if="ciCurve.ciAreaPoints" :points="ciCurve.ciAreaPoints" class="ci-range-fill" />
                <polyline :points="ciCurve.points" class="curve-line" />
                <line x1="34" :y1="ciCurve.axisY" x2="566" :y2="ciCurve.axisY" class="x-axis-line" />
                <g v-if="ciCurve.lowerX != null && ciCurve.upperX != null">
                  <line :x1="ciCurve.lowerX" y1="36" :x2="ciCurve.lowerX" :y2="ciCurve.baselineY" class="ci-boundary-line" />
                  <line :x1="ciCurve.upperX" y1="36" :x2="ciCurve.upperX" :y2="ciCurve.baselineY" class="ci-boundary-line" />
                  <line :x1="ciCurve.lowerX" :y1="ciCurve.axisY" :x2="ciCurve.upperX" :y2="ciCurve.axisY" class="ci-bracket-line" />
                  <line :x1="ciCurve.lowerX" y1="137" :x2="ciCurve.lowerX" y2="153" class="ci-bracket-line" />
                  <line :x1="ciCurve.upperX" y1="137" :x2="ciCurve.upperX" y2="153" class="ci-bracket-line" />
                  <text :x="(ciCurve.lowerX + ciCurve.upperX) / 2" y="141" class="axis-text center">95% 범위</text>
                </g>
                <line :x1="ciCurve.meanX" :y1="ciCurve.peakY" :x2="ciCurve.meanX" :y2="ciCurve.baselineY" class="mean-line" />
                <circle :cx="ciCurve.meanX" :cy="ciCurve.baselineY" r="4.5" class="mean-dot" />
                <text x="34" y="172" class="axis-text">{{ ciCurve.minValue }}</text>
                <text x="566" y="172" class="axis-text end">{{ ciCurve.maxValue }}</text>
                <g v-if="ciCurve.lowerX != null" class="ci-bottom-label">
                  <text :x="ciCurve.lowerX" y="172" class="value-text center">{{ formatNumber(selectedConfidence?.lower) }}</text>
                  <text :x="ciCurve.lowerX" y="185" class="axis-text center">하한</text>
                </g>
                <g class="ci-bottom-label">
                  <text :x="ciCurve.meanX" y="172" class="value-text center">{{ formatNumber(selectedConfidence?.mean) }}</text>
                  <text :x="ciCurve.meanX" y="185" class="axis-text center">평균</text>
                </g>
                <g v-if="ciCurve.upperX != null" class="ci-bottom-label">
                  <text :x="ciCurve.upperX" y="172" class="value-text center">{{ formatNumber(selectedConfidence?.upper) }}</text>
                  <text :x="ciCurve.upperX" y="185" class="axis-text center">상한</text>
                </g>
              </svg>
            </div>
            <div v-else class="empty-note">분석 가능한 데이터가 없습니다.</div>
          </section>

          <div v-if="assignmentConfidenceRows.length" class="stat-table-wrap section-gap compact-gap">
            <table class="stat-table">
              <thead>
                <tr><th>과제</th><th>n</th><th>평균 AIC</th><th>95% CI</th><th>CI 폭</th><th>신뢰도</th></tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in assignmentConfidenceRows"
                  :key="confidenceValue(row)"
                  class="clickable-row"
                  :class="{ selected: confidenceValue(row) === selectedConfidenceTarget }"
                  @click="selectConfidence(row)"
                >
                  <td>{{ row.target_title || `과제 #${row.target_id}` }}</td>
                  <td>{{ row.n }}</td>
                  <td>{{ formatNumber(row.mean) }}</td>
                  <td>{{ formatInterval(row) }}</td>
                  <td>{{ row.ci_width == null ? '-' : formatNumber(row.ci_width) }}</td>
                  <td><span class="mini-badge" :class="row.reliability_label">{{ reliabilityText(row.reliability_label) }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-note section-gap compact-gap">분석 가능한 데이터가 없습니다.</div>

          <div class="method-note">Method: 평균 AIC의 95% 신뢰구간은 t-interval로 계산합니다. 표본 수가 적거나 점수 분산이 클수록 CI 폭이 넓어져 평균 해석에 주의가 필요합니다.</div>
        </template>

        <template v-else>
          <p class="purpose-copy">PI, UI, OI, TopicScore 조합을 기반으로 AIC 해석에 주의가 필요한 신호를 탐지합니다. 본 결과는 자동 판정이 아니라 교사 확인을 돕는 해석 보조 신호입니다.</p>

          <div class="metric-grid">
            <article class="metric-card">
              <span>해석 주의 신호</span>
              <strong>{{ anomalySummary.total || anomalyItems.length }}</strong>
              <small>총 이상패턴 건수</small>
            </article>
            <article class="metric-card">
              <span>우선 확인 항목</span>
              <strong>{{ anomalySummary.high || 0 }}</strong>
              <small>high severity</small>
            </article>
            <article class="metric-card">
              <span>가장 많은 유형</span>
              <strong>{{ mostCommonRule?.label || '-' }}</strong>
              <small>{{ mostCommonRule ? `${mostCommonRule.count}건` : '감지된 신호 없음' }}</small>
            </article>
          </div>

          <div class="rule-board section-gap compact-gap">
            <article v-for="rule in ruleCounts" :key="rule.rule_key" class="rule-card">
              <span>{{ rule.label }}</span>
              <strong>{{ rule.count }}건</strong>
              <small>{{ rule.evidence_summary }}</small>
            </article>
            <div v-if="!ruleCounts.length" class="empty-note">분석 가능한 데이터가 없습니다.</div>
          </div>

          <div v-if="anomalyTopItems.length" class="stat-table-wrap section-gap compact-gap">
            <table class="stat-table">
              <thead>
                <tr><th>학생</th><th>과제</th><th>유형</th><th>심각도</th><th>근거</th><th>확인 권장</th></tr>
              </thead>
              <tbody>
                <tr v-for="item in anomalyTopItems" :key="`${item.student_id}-${item.assignment_id}-${item.rule_key}`">
                  <td>{{ item.student_name }}</td>
                  <td>{{ item.assignment_title }}</td>
                  <td>{{ item.label }}</td>
                  <td><span class="mini-badge" :class="item.severity">{{ severityText(item.severity) }}</span></td>
                  <td>{{ item.evidence }}</td>
                  <td>{{ item.teacher_action }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-note section-gap compact-gap">분석 가능한 데이터가 없습니다.</div>

          <div class="rules-toggle">
            <button type="button" class="btn btn-secondary btn-sm" @click="showRules = !showRules">{{ showRules ? '탐지 규칙 닫기' : '탐지 규칙 보기' }}</button>
          </div>
          <div v-if="showRules" class="rules-panel">
            <div v-for="[title, rule] in detectionRules" :key="title" class="rule-line">
              <strong>{{ title }}</strong>
              <span>{{ rule }}</span>
            </div>
          </div>

          <div class="caution-note">본 결과는 자동 판정이 아니라 해석 보조 신호입니다. 최종 판단은 학생의 작성 과정, 피드백 이력, 과제 맥락을 함께 고려해야 합니다.</div>
        </template>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.stats-hero { padding: var(--space-6); border-radius: var(--radius-xl); background: linear-gradient(135deg, var(--color-aic) 0%, #2C5282 60%, #3B82F6 100%); color: white; box-shadow: var(--shadow-sm); }
.ah-tag { display: inline-flex; padding: 3px 10px; border-radius: var(--radius-full); background: rgba(255,255,255,0.16); font-size: var(--font-size-xs); font-weight: 800; text-transform: uppercase; }
.ah-title { margin-top: var(--space-3); font-size: var(--font-size-4xl); line-height: 1.15; }
.ah-sub { max-width: 760px; margin-top: var(--space-1); color: rgba(255,255,255,0.78); font-size: var(--font-size-sm); line-height: 1.6; }
.ah-tabs { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-5); }
.ah-tab { padding: var(--space-2) var(--space-4); border-radius: var(--radius-full); color: rgba(255,255,255,0.76); background: rgba(255,255,255,0.12); font-size: var(--font-size-xs); font-weight: 800; }
.ah-tab.active { color: var(--color-aic); background: white; }
.section-gap { margin-top: var(--space-6); }
.compact-gap { margin-top: var(--space-4); }
.validation-panel { padding: var(--space-5); border: 1px solid var(--border-light); border-radius: var(--radius-xl); background: white; box-shadow: var(--shadow-sm); }
.panel-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); }
.section-eyebrow { color: var(--color-pi); font-size: 10px; font-weight: 900; letter-spacing: 0; text-transform: uppercase; }
.panel-heading h2 { margin-top: var(--space-1); color: var(--text-primary); font-size: var(--font-size-2xl); line-height: 1.25; }
.purpose-copy { max-width: 860px; margin-top: var(--space-3); color: var(--text-secondary); font-size: var(--font-size-sm); line-height: 1.65; }
.metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-4); margin-top: var(--space-5); }
.metric-card { min-height: 118px; padding: var(--space-4); border: 1px solid var(--border-light); border-radius: var(--radius-md); background: #F8FAFC; }
.metric-card span, .metric-card small { display: block; color: var(--text-muted); font-size: var(--font-size-xs); font-weight: 700; }
.metric-card strong { display: block; margin-top: var(--space-2); color: var(--color-aic); font-size: var(--font-size-2xl); line-height: 1.18; overflow-wrap: anywhere; }
.metric-card small { margin-top: var(--space-1); font-weight: 600; line-height: 1.45; }
.target-select { display: flex; align-items: center; gap: var(--space-3); margin-top: var(--space-4); color: var(--text-secondary); font-size: var(--font-size-sm); font-weight: 800; }
.target-select select { min-width: 220px; padding: 9px 12px; border: 1px solid var(--border-light); border-radius: var(--radius-md); background: white; color: var(--text-primary); font: inherit; }
.stat-table-wrap { overflow-x: auto; }
.stat-table { width: 100%; border-collapse: collapse; min-width: 720px; font-size: var(--font-size-xs); }
.stat-table th { color: var(--text-muted); font-weight: 800; text-align: left; border-bottom: 1px solid var(--border-light); padding: var(--space-2); white-space: nowrap; }
.stat-table td { color: var(--text-secondary); border-bottom: 1px solid var(--border-light); padding: var(--space-2); vertical-align: top; }
.stat-table td:first-child { color: var(--text-primary); font-weight: 700; }
.clickable-row { cursor: pointer; }
.clickable-row:hover td, .clickable-row.selected td { background: #F8FAFC; }
.clickable-row.selected td:first-child { box-shadow: inset 3px 0 0 var(--color-aic); }
.mini-badge { display: inline-flex; align-items: center; justify-content: center; min-width: 44px; padding: 3px 8px; border-radius: var(--radius-full); color: var(--color-pi); background: var(--color-pi-pale); font-size: 10px; font-weight: 800; white-space: nowrap; }
.mini-badge.stable, .mini-badge.low { color: var(--color-oi); background: var(--color-oi-pale); }
.mini-badge.caution { color: #A16207; background: #FEF3C7; }
.mini-badge.unstable, .mini-badge.high { color: var(--color-danger); background: #FEE2E2; }
.method-note { margin-top: var(--space-4); padding: var(--space-3); border-radius: var(--radius-md); color: var(--text-secondary); background: #F8FAFC; font-size: var(--font-size-xs); line-height: 1.55; }
.empty-note { display: grid; place-items: center; min-height: 120px; color: var(--text-muted); font-size: var(--font-size-sm); text-align: center; background: #F8FAFC; border-radius: var(--radius-md); }
.ci-graph-card { padding: var(--space-3); border: 1px solid var(--border-light); border-radius: var(--radius-md); background: #F8FAFC; }
.ci-graph-title strong, .ci-graph-title span { display: block; }
.ci-graph-title strong { color: var(--text-primary); font-size: var(--font-size-sm); }
.ci-graph-title span { margin-top: 4px; color: var(--text-muted); font-size: var(--font-size-xs); line-height: 1.5; }
.ci-svg-wrap { margin-top: var(--space-2); border-radius: var(--radius-md); background: white; overflow: hidden; }
.ci-svg-wrap svg { display: block; width: 100%; height: 240px; max-height: 260px; }
.ci-range-fill { fill: rgba(56, 189, 248, 0.22); stroke: none; }
.curve-line { fill: none; stroke: var(--color-aic); stroke-width: 2.8; stroke-linecap: round; stroke-linejoin: round; }
.x-axis-line { stroke: var(--color-gray-300); stroke-width: 1.5; stroke-linecap: round; }
.ci-boundary-line { stroke: #38BDF8; stroke-width: 1.7; stroke-dasharray: 5 6; stroke-linecap: round; }
.ci-bracket-line { stroke: var(--color-aic); stroke-width: 3; stroke-linecap: round; }
.mean-line { stroke: var(--color-aic); stroke-width: 2; stroke-linecap: round; opacity: 0.72; }
.mean-dot { fill: var(--color-aic); }
.axis-text { fill: var(--text-muted); font-size: 11px; font-weight: 800; }
.axis-text.center { text-anchor: middle; }
.axis-text.end { text-anchor: end; }
.value-text { fill: var(--text-primary); font-size: 13px; font-weight: 900; }
.value-text.center { text-anchor: middle; }
.rule-board { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-3); }
.rule-card { padding: var(--space-4); border: 1px solid var(--border-light); border-radius: var(--radius-md); background: #F8FAFC; }
.rule-card span, .rule-card strong, .rule-card small { display: block; }
.rule-card span { color: var(--text-primary); font-size: var(--font-size-sm); font-weight: 800; }
.rule-card strong { margin-top: var(--space-2); color: var(--color-aic); font-size: var(--font-size-2xl); }
.rule-card small { margin-top: var(--space-1); color: var(--text-muted); font-size: var(--font-size-xs); line-height: 1.45; }
.rules-toggle { margin-top: var(--space-4); }
.rules-panel { display: grid; gap: var(--space-2); margin-top: var(--space-3); padding: var(--space-4); border-radius: var(--radius-md); background: #F8FAFC; }
.rule-line strong, .rule-line span { display: block; }
.rule-line strong { color: var(--text-primary); font-size: var(--font-size-xs); }
.rule-line span { margin-top: 3px; color: var(--text-muted); font-size: var(--font-size-xs); line-height: 1.45; }
.caution-note { margin-top: var(--space-4); padding: var(--space-4); border-radius: var(--radius-md); color: #A16207; background: #FEF3C7; font-size: var(--font-size-sm); line-height: 1.6; }
@media (max-width: 920px) {
  .metric-grid, .rule-board { grid-template-columns: 1fr; }
  .target-select { align-items: stretch; flex-direction: column; }
  .target-select select { width: 100%; min-width: 0; }
}
@media (max-width: 560px) {
  .stats-hero, .validation-panel { padding: var(--space-4); }
  .ah-title { font-size: var(--font-size-3xl); }
  .metric-card strong { font-size: var(--font-size-xl); }
}
</style>

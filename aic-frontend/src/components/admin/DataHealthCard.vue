<script setup>
import { computed } from 'vue'

const props = defineProps({
  dataHealth: { type: Object, required: true },
})

const scoreClass = computed(() => {
  const s = props.dataHealth.score
  if (s >= 90) return 'score-ok'
  if (s >= 70) return 'score-warn'
  return 'score-danger'
})

const requiredFields = ['chatgpt_before', 'user', 'essay']
const missingFields = computed(() => Array.isArray(props.dataHealth.missingFields) ? props.dataHealth.missingFields : [])
const fieldStatus = (field) => missingFields.value.includes(field) ? 'warn' : 'ok'
const fieldLabel = (field) => missingFields.value.includes(field) ? `${field} 값 누락` : `${field} 값 정상`
const ratingLabel = computed(() => (
  props.dataHealth.ratingCoverage == null ? 'N/A' : `${props.dataHealth.ratingCoverage}%`
))
const ratingChecklistLabel = computed(() => {
  if (props.dataHealth.ratingMissingRows == null) return 'rating 데이터 없음'
  return `rating 결측 ${props.dataHealth.ratingMissingRows}건`
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Data Health</span>
      <span class="score-badge" :class="scoreClass">{{ dataHealth.score }} / 100</span>
    </div>

    <div class="metric-rows">
      <div class="metric-row">
        <span class="metric-name">결측 데이터</span>
        <span class="metric-val warn">{{ dataHealth.missingRows }}건</span>
      </div>
      <div class="metric-row">
        <span class="metric-name">중복 제출</span>
        <span class="metric-val warn">{{ dataHealth.duplicateRows }}건</span>
      </div>
      <div class="metric-row">
        <span class="metric-name">텍스트 길이 이상치</span>
        <span class="metric-val warn">{{ dataHealth.textOutliers }}건</span>
      </div>
      <div class="metric-row">
        <span class="metric-name">rating 보유율</span>
        <span class="metric-val" :class="dataHealth.ratingCoverage == null || dataHealth.ratingCoverage >= 70 ? 'ok' : 'warn'">
          {{ ratingLabel }}
        </span>
      </div>
      <div class="metric-row">
        <span class="metric-name">표본 부족 과목</span>
        <span class="metric-val warn">{{ dataHealth.lowSampleCourses }}개</span>
      </div>
    </div>

    <div class="checklist">
      <div v-for="field in requiredFields" :key="field" class="check-item" :class="fieldStatus(field)">
        <span class="check-icon">{{ fieldStatus(field) === 'ok' ? '✓' : '!' }}</span>
        <span>{{ fieldLabel(field) }}</span>
      </div>
      <div class="check-item ok">
        <span class="check-icon">✓</span>
        <span>{{ ratingChecklistLabel }}</span>
      </div>
      <div class="check-item warn">
        <span class="check-icon">!</span>
        <span>course별 표본 부족 {{ dataHealth.lowSampleCourses }}개</span>
      </div>
    </div>
  </div>
</template>


<style scoped>
.card {
  padding: var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
}

.score-badge {
  font-size: var(--font-size-sm);
  font-weight: 800;
  padding: 3px 10px;
  border-radius: var(--radius-full);
}

.score-ok     { background: #d1fae5; color: #065f46; }
.score-warn   { background: #fef3c7; color: #92400e; }
.score-danger { background: #fee2e2; color: #991b1b; }

.metric-rows {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.metric-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
}

.metric-name { color: var(--text-secondary); }
.metric-val  { font-weight: 700; }
.metric-val.ok   { color: var(--color-success); }
.metric-val.warn { color: var(--color-warning); }

.checklist {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
}

.check-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
}

.check-icon {
  width: 18px;
  height: 18px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-full);
  font-weight: 800;
  font-size: 10px;
  flex-shrink: 0;
}

.check-item.ok   .check-icon { background: #d1fae5; color: #065f46; }
.check-item.warn .check-icon { background: #fef3c7; color: #92400e; }
.check-item.ok   { color: var(--text-secondary); }
.check-item.warn { color: var(--color-warning); }
</style>

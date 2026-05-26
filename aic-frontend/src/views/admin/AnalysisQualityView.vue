<script setup>
import { onMounted, computed, ref } from 'vue'
import { useAdminAnalysisStore } from '@/stores/adminAnalysisStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import AdminKpiCard from '@/components/admin/AdminKpiCard.vue'
import DataHealthCard from '@/components/admin/DataHealthCard.vue'
import BackendInfoCard from '@/components/admin/BackendInfoCard.vue'
import OptimizationComparisonCard from '@/components/admin/OptimizationComparisonCard.vue'
import PipelineStepper from '@/components/admin/PipelineStepper.vue'
import RuntimeBreakdownChart from '@/components/admin/RuntimeBreakdownChart.vue'
import ServiceReadinessCard from '@/components/admin/ServiceReadinessCard.vue'

const store = useAdminAnalysisStore()
const selectedRunId = ref('')

onMounted(() => store.fetchLatestRun())

const run = computed(() => store.run)

const hasComparison = computed(() => {
  const comparison = run.value?.comparison
  return comparison?.performanceRows?.length || comparison?.scoreRows?.length
})

function fetchSelectedRun() {
  store.fetchRun(selectedRunId.value.trim())
}

function fetchLatestRun() {
  selectedRunId.value = ''
  store.fetchLatestRun()
}

function formatSeconds(value) {
  return value === null || value === undefined ? '-' : `${value}s`
}

const kpis = computed(() => {
  if (!run.value) return []
  const r = run.value
  return [
    {
      label: '처리 행 수',
      value: r.processedRows.toLocaleString(),
      subText: `유효: ${r.validRows.toLocaleString()}건`,
      status: 'neutral',
    },
    {
      label: '분석 성공률',
      value: `${r.successRate}%`,
      subText: r.successRate >= 98 ? '정상 범위' : '기준치 미달 (98% 이상 필요)',
      status: r.successRate >= 98 ? 'success' : 'warning',
    },
    {
      label: '총 처리시간',
      value: formatSeconds(r.totalRuntimeSec),
      subText: '파이프라인 전체 소요',
      status: r.totalRuntimeSec !== null && r.totalRuntimeSec < 300 ? 'success' : 'warning',
    },
    {
      label: '실행 상태',
      value: r.status === 'success' ? '완료' : r.status === 'failed' ? '실패' : '확인 필요',
      subText: `Run ID: ${r.runId}`,
      status: r.status === 'success' ? 'success' : r.status === 'failed' ? 'danger' : 'warning',
    },
  ]
})
</script>

<template>
  <AppLayout title="AIC 분석 품질 모니터" subtitle="최근 AIC 분석 실행 결과 및 데이터 품질 검증">
    <div class="run-selector">
      <input
        v-model="selectedRunId"
        class="run-input"
        type="text"
        placeholder="Analysis run ID"
        @keyup.enter="fetchSelectedRun"
      />
      <button class="selector-btn" :disabled="store.loading || !selectedRunId.trim()" @click="fetchSelectedRun">
        조회
      </button>
      <button class="selector-btn selector-btn--secondary" :disabled="store.loading" @click="fetchLatestRun">
        최신 실행
      </button>
    </div>

    <div v-if="store.loading" class="loading-state">분석 데이터를 불러오는 중...</div>
    <div v-else-if="store.error" class="error-state">{{ store.error }}</div>

    <template v-else-if="run">
      <!-- KPI Grid -->
      <div class="kpi-grid">
        <AdminKpiCard
          v-for="kpi in kpis"
          :key="kpi.label"
          :label="kpi.label"
          :value="kpi.value"
          :sub-text="kpi.subText"
          :status="kpi.status"
        />
      </div>

      <!-- Data Health + Backend Info -->
      <div class="grid-2">
        <DataHealthCard :data-health="run.dataHealth" />
        <BackendInfoCard :backend="run.backend" />
      </div>

      <OptimizationComparisonCard
        v-if="hasComparison"
        :comparison="run.comparison"
      />

      <!-- Pipeline Stepper -->
      <PipelineStepper :steps="run.pipelineSteps" />

      <!-- Runtime Chart + Service Readiness -->
      <div class="grid-2">
        <RuntimeBreakdownChart :steps="run.pipelineSteps" />
        <ServiceReadinessCard :readiness="run.readiness" />
      </div>

      <!-- Reprocess Action -->
      <div class="action-bar">
        <button
          class="reprocess-btn"
          :disabled="store.reprocessing"
          @click="store.reprocessRun(run.runId)"
        >
          {{ store.reprocessing ? '재실행 중...' : '분석 재실행' }}
        </button>
        <span class="action-note">재실행 시 기존 결과를 덮어씁니다.</span>
      </div>
    </template>
  </AppLayout>
</template>

<style scoped>
.loading-state,
.error-state {
  padding: var(--space-8);
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.error-state { color: var(--color-danger); }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.run-selector {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.run-input {
  width: min(360px, 100%);
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.selector-btn {
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary, var(--color-aic));
  color: white;
  border: 1px solid var(--color-primary, var(--color-aic));
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.selector-btn--secondary {
  color: var(--text-primary);
  background: var(--bg-surface);
  border-color: var(--border-default);
}

.selector-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.action-bar {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) 0;
}

.reprocess-btn {
  padding: var(--space-2) var(--space-5);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
}

.reprocess-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reprocess-btn:not(:disabled):hover {
  filter: brightness(1.1);
}

.action-note {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .grid-2   { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .run-selector { align-items: stretch; flex-direction: column; }
  .run-input,
  .selector-btn { width: 100%; }
}
</style>

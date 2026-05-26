<script setup>
import { onMounted, computed } from 'vue'
import { useAdminAnalysisStore } from '@/stores/adminAnalysisStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import AdminKpiCard from '@/components/admin/AdminKpiCard.vue'
import DataHealthCard from '@/components/admin/DataHealthCard.vue'
import BackendInfoCard from '@/components/admin/BackendInfoCard.vue'
import PipelineStepper from '@/components/admin/PipelineStepper.vue'
import RuntimeBreakdownChart from '@/components/admin/RuntimeBreakdownChart.vue'
import ServiceReadinessCard from '@/components/admin/ServiceReadinessCard.vue'

const store = useAdminAnalysisStore()

onMounted(() => store.fetchLatestRun())

const run = computed(() => store.run)

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
      value: `${r.totalRuntimeSec}s`,
      subText: '파이프라인 전체 소요',
      status: r.totalRuntimeSec < 300 ? 'success' : 'warning',
    },
    {
      label: '실행 상태',
      value: r.status === 'completed' ? '완료' : r.status === 'failed' ? '실패' : '실행 중',
      subText: `Run ID: ${r.runId}`,
      status: r.status === 'completed' ? 'success' : r.status === 'failed' ? 'danger' : 'neutral',
    },
  ]
})
</script>

<template>
  <AppLayout title="AIC 분석 품질 모니터" subtitle="최근 AIC 분석 실행 결과 및 데이터 품질 검증">
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
}
</style>

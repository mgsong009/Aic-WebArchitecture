<script setup>
import { computed, ref, onMounted } from 'vue'
import { getStudentGrowth } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import LineChart from '@/components/charts/LineChart.vue'
import RadarChart from '@/components/charts/RadarChart.vue'

const loading = ref(true)
const error = ref('')
const growth = ref({ assignments: [], class_avg_trend: [] })

const metricKeys = [
  { key: 'aic', label: 'AIC', color: '#1E3A5F' },
  { key: 'pi', label: 'PI', color: '#3B82F6' },
  { key: 'ui', label: 'UI', color: '#F97316' },
  { key: 'oi', label: 'OI', color: '#10B981' },
]

onMounted(async () => {
  await loadGrowth()
})

async function loadGrowth() {
  loading.value = true
  error.value = ''
  try {
    growth.value = await getStudentGrowth()
  } catch {
    error.value = '성장 분석 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const assignments = computed(() => growth.value.assignments)
const classAvgTrend = computed(() => growth.value.class_avg_trend)
const hasAssignments = computed(() => assignments.value.length > 0)
const latest = computed(() => assignments.value.at(-1) || null)
const previous = computed(() => assignments.value.length > 1 ? assignments.value.at(-2) : null)

const latestDelta = computed(() => {
  if (!latest.value || !previous.value) return null
  return metricKeys.reduce((acc, metric) => {
    const next = latest.value?.[metric.key]
    const prev = previous.value?.[metric.key]
    acc[metric.key] = next != null && prev != null ? next - prev : null
    return acc
  }, {})
})

const trendConfig = computed(() => {
  if (!hasAssignments.value) return null
  return {
    type: 'line',
    data: {
      labels: assignments.value.map((a) => a.label),
      datasets: metricKeys.map((metric) => ({
        label: metric.label,
        data: assignments.value.map((a) => a[metric.key]),
        borderColor: metric.color,
        backgroundColor: `${metric.color}14`,
        tension: 0.3,
        fill: metric.key === 'aic',
        pointRadius: 4,
      })),
    },
    options: {
      responsive: true,
      scales: { y: { min: 0, max: 100 } },
      plugins: { legend: { position: 'bottom' } },
    },
  }
})

const classCompareConfig = computed(() => {
  if (!hasAssignments.value || !classAvgTrend.value.length) return null
  return {
    type: 'line',
    data: {
      labels: assignments.value.map((a) => a.label),
      datasets: [
        {
          label: '나의 AIC',
          data: assignments.value.map((a) => a.aic),
          borderColor: '#1E3A5F',
          backgroundColor: 'rgba(30,58,95,0.08)',
          fill: true,
          tension: 0.3,
        },
        {
          label: '반 평균 AIC',
          data: classAvgTrend.value.map((a) => a.aic),
          borderColor: '#94A3B8',
          borderDash: [5, 5],
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      scales: { y: { min: 0, max: 100 } },
      plugins: { legend: { position: 'bottom' } },
    },
  }
})

const radarConfig = computed(() => {
  if (!latest.value) return null
  return {
    type: 'radar',
    data: {
      labels: ['PI', 'UI', 'OI', 'Topic'],
      datasets: [
        {
          label: latest.value.title || latest.value.label,
          data: [latest.value.pi || 0, latest.value.ui || 0, latest.value.oi || 0, latest.value.topic || 0],
          backgroundColor: 'rgba(30,58,95,0.12)',
          borderColor: '#1E3A5F',
        },
      ],
    },
    options: {
      responsive: true,
      scales: { r: { min: 0, max: 100 } },
      plugins: { legend: { position: 'bottom' } },
    },
  }
})
</script>

<template>
  <AppLayout title="성장 분석" subtitle="과제별 성장 추이와 최신 프로파일">
    <div v-if="loading" class="loading-wrap">
      <LoadingSkeleton height="120px" />
      <LoadingSkeleton height="320px" />
      <LoadingSkeleton height="240px" />
    </div>

    <div v-else-if="error" class="card card-body empty-state">
      <strong>{{ error }}</strong>
      <button class="btn btn-secondary btn-sm mt-4" type="button" @click="loadGrowth">다시 시도</button>
    </div>

    <div v-else-if="!hasAssignments" class="card card-body empty-state">
      아직 성장 추이를 계산할 제출 데이터가 없습니다.
    </div>

    <div v-else>
      <div class="kpi-grid">
        <div v-for="metric in metricKeys" :key="metric.key" class="card card-body growth-kpi">
          <span class="kpi-label">{{ metric.label }}</span>
          <strong class="kpi-value" :style="{ color: metric.color }">{{ latest?.[metric.key] ?? '-' }}</strong>
          <span class="kpi-change" :class="(latestDelta?.[metric.key] ?? 0) >= 0 ? 'up' : 'down'">
            {{ latestDelta?.[metric.key] == null ? '변화 없음' : `${latestDelta[metric.key] >= 0 ? '+' : ''}${latestDelta[metric.key]}` }}
          </span>
        </div>
      </div>

      <div class="grid-2 mb-4">
        <div class="card card-body chart-card">
          <h3>AIC/PI/UI/OI 추세</h3>
          <LineChart v-if="trendConfig" :config="trendConfig" />
        </div>
        <div class="card card-body chart-card">
          <h3>나와 반 평균 AIC</h3>
          <LineChart v-if="classCompareConfig" :config="classCompareConfig" />
          <div v-else class="empty-state compact">반 평균 비교 데이터가 없습니다.</div>
        </div>
      </div>

      <div class="grid-2-1">
        <div class="data-table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>과제</th>
                <th>AIC</th>
                <th>PI</th>
                <th>UI</th>
                <th>OI</th>
                <th>Topic</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in assignments" :key="a.assignment_id">
                <td>
                  <strong>{{ a.title }}</strong>
                  <div class="text-xs text-muted">{{ a.label }}</div>
                </td>
                <td>{{ a.aic ?? '-' }}</td>
                <td>{{ a.pi ?? '-' }}</td>
                <td>{{ a.ui ?? '-' }}</td>
                <td>{{ a.oi ?? '-' }}</td>
                <td>{{ a.topic ?? '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card card-body chart-card">
          <h3>최신 지표 프로파일</h3>
          <RadarChart v-if="radarConfig" :config="radarConfig" />
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

.growth-kpi {
  display: grid;
  gap: var(--space-2);
}

.growth-kpi .kpi-label {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  font-weight: 800;
}

.growth-kpi .kpi-value {
  font-size: var(--font-size-3xl);
  line-height: 1;
}

h3 {
  margin-bottom: var(--space-4);
}

.compact {
  padding: var(--space-6);
}

@media (max-width: 768px) {
  .grid-2,
  .grid-2-1 {
    grid-template-columns: 1fr;
  }
}
</style>

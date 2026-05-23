<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTeacherRiskStudents } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ScatterChart from '@/components/charts/ScatterChart.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const riskStudents = ref([])

onMounted(async () => {
  await loadRiskStudents()
})

async function loadRiskStudents() {
  loading.value = true
  error.value = ''
  try {
    riskStudents.value = await getTeacherRiskStudents()
  } catch (err) {
    riskStudents.value = []
    error.value = err.response?.data?.detail || '위험군 학생 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const riskLabelMap = {
  all: '전 지표',
  pi: 'PI',
  ui: 'UI',
  oi: 'OI',
}

function riskLabels(types = []) {
  const labels = types.map((type) => riskLabelMap[type] || type.toUpperCase())
  return labels.length ? labels : ['AIC']
}

const riskSummary = computed(() => {
  const counts = { all: 0, pi: 0, ui: 0, oi: 0, aic: 0 }
  riskStudents.value.forEach((student) => {
    const types = Array.isArray(student.risk_types) ? student.risk_types : []
    if (!types.length) counts.aic += 1
    types.forEach((type) => {
      if (counts[type] !== undefined) counts[type] += 1
    })
  })
  return counts
})

const scatterConfig = computed(() => ({
  type: 'scatter',
  data: {
    datasets: [
      {
        label: '위험군',
        data: riskStudents.value
          .filter((student) => student.pi !== null && student.pi !== undefined && student.ui !== null && student.ui !== undefined)
          .map((student) => ({
            x: student.pi,
            y: student.ui,
            student,
          })),
        backgroundColor: 'rgba(239, 68, 68, 0.72)',
        borderColor: '#B91C1C',
        borderWidth: 1,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    parsing: false,
    scales: {
      x: {
        min: 0,
        max: 100,
        title: { display: true, text: 'PI 점수' },
      },
      y: {
        min: 0,
        max: 100,
        title: { display: true, text: 'UI 점수' },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label(context) {
            const student = context.raw.student
            return `${student.name}: PI ${student.pi ?? '-'}, UI ${student.ui ?? '-'}, AIC ${student.aic ?? '-'}`
          },
        },
      },
    },
  },
}))
</script>

<template>
  <AppLayout title="위험군 관리" subtitle="즉시 코칭이 필요한 학생 목록">
    <div class="risk-grid">
      <section class="card">
        <div class="card-heading">
          <h3>위험군 분포</h3>
          <span class="summary">총 {{ riskStudents.length }}명</span>
        </div>
        <div v-if="loading" class="loading-state">불러오는 중...</div>
        <div v-else-if="error" class="alert alert-danger">
          <span>{{ error }}</span>
          <button class="btn btn-secondary btn-sm" type="button" @click="loadRiskStudents">다시 시도</button>
        </div>
        <div v-else-if="!riskStudents.length" class="empty-state">현재 위험군 학생이 없습니다.</div>
        <div v-else class="chart-box">
          <ScatterChart :config="scatterConfig" />
        </div>
      </section>

      <section class="card">
        <div class="card-heading">
          <h3>위험 유형</h3>
        </div>
        <div class="type-list">
          <div class="type-row">
            <span>전 지표</span>
            <strong>{{ riskSummary.all }}</strong>
          </div>
          <div class="type-row">
            <span>PI</span>
            <strong>{{ riskSummary.pi }}</strong>
          </div>
          <div class="type-row">
            <span>UI</span>
            <strong>{{ riskSummary.ui }}</strong>
          </div>
          <div class="type-row">
            <span>OI</span>
            <strong>{{ riskSummary.oi }}</strong>
          </div>
          <div class="type-row">
            <span>AIC 단독</span>
            <strong>{{ riskSummary.aic }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="card mt-4">
      <div class="card-heading">
        <h3>학생별 위험군 목록</h3>
      </div>
      <div v-if="loading" class="loading-state">불러오는 중...</div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="!riskStudents.length" class="empty-state">표시할 학생이 없습니다.</div>
      <div v-else class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>학생</th>
              <th>AIC</th>
              <th>PI</th>
              <th>UI</th>
              <th>OI</th>
              <th>위험 타입</th>
              <th>최근 제출</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in riskStudents" :key="s.id" @click="router.push(`/teacher/students/${s.id}`)">
              <td>{{ s.name }}</td>
              <td>{{ s.aic ?? '-' }}</td>
              <td>{{ s.pi ?? '-' }}</td>
              <td>{{ s.ui ?? '-' }}</td>
              <td>{{ s.oi ?? '-' }}</td>
              <td>
                <span v-for="label in riskLabels(s.risk_types)" :key="label" class="badge badge-danger risk-tag">
                  {{ label }}
                </span>
              </td>
              <td>{{ s.last_submitted || '-' }}</td>
              <td>
                <button class="btn btn-ghost btn-sm" type="button" @click.stop="router.push(`/teacher/students/${s.id}`)">상세</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.risk-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(240px, 1fr);
  gap: var(--space-4);
}

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
}

.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.chart-box {
  height: 320px;
}

.type-list {
  display: grid;
  gap: var(--space-2);
}

.type-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: var(--color-gray-50);
}

.type-row span {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.type-row strong {
  color: var(--text-primary);
  font-size: var(--text-lg);
}

.risk-tag + .risk-tag {
  margin-left: var(--space-1);
}

.summary {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

@media (max-width: 1024px) {
  .risk-grid {
    grid-template-columns: 1fr;
  }
}
</style>

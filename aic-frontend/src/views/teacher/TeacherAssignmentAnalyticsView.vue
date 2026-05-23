<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import BarChart from '@/components/charts/BarChart.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = ref(Number(route.params.id))
const loading = ref(true)
const error = ref('')
const analytics = ref(null)

watch(
  () => route.params.id,
  async (nextId) => {
    assignmentId.value = Number(nextId)
    await load()
  },
)

onMounted(async () => {
  await load()
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/teacher/analytics/assignment/${assignmentId.value}`)
    analytics.value = {
      ...data,
      assignment: data.assignment || { id: assignmentId.value, title: `과제 ${assignmentId.value}` },
      class_avg: data.class_avg || {},
      distribution: Array.isArray(data.distribution) ? data.distribution : [],
      top5: Array.isArray(data.top5) ? data.top5 : [],
      bottom5: Array.isArray(data.bottom5) ? data.bottom5 : [],
      difficulty: Number(data.difficulty || 0),
    }
  } catch (err) {
    analytics.value = null
    error.value = err.response?.data?.detail || '과제 분석 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const distributionConfig = computed(() => {
  if (!analytics.value?.distribution?.length) return null
  return {
    type: 'bar',
    data: {
      labels: ['<40', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'],
      datasets: [
        {
          label: '학생 수',
          data: analytics.value.distribution,
          backgroundColor: ['#EF4444', '#F97316', '#F59E0B', '#EAB308', '#3B82F6', '#10B981', '#1E3A5F'],
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
      plugins: {
        legend: { display: false },
      },
    },
  }
})

const metricCards = computed(() => {
  const avg = analytics.value?.class_avg || {}
  return [
    { key: 'aic', label: 'AIC 평균', value: avg.aic, className: 'aic-card' },
    { key: 'pi', label: 'PI 평균', value: avg.pi, className: 'pi-card' },
    { key: 'ui', label: 'UI 평균', value: avg.ui, className: 'ui-card' },
    { key: 'oi', label: 'OI 평균', value: avg.oi, className: 'oi-card' },
  ]
})

const difficultyPercent = computed(() => Math.round((analytics.value?.difficulty || 0) * 100))

function scoreText(score) {
  return score ?? '-'
}
</script>

<template>
  <AppLayout title="과제 분석" :subtitle="analytics?.assignment?.title || ''">
    <div v-if="loading" class="card loading-state">불러오는 중...</div>

    <div v-else-if="error" class="card">
      <div class="alert alert-danger">
        <span>{{ error }}</span>
        <button class="btn btn-secondary btn-sm" type="button" @click="load">다시 시도</button>
      </div>
      <div class="actions">
        <button class="btn btn-secondary" type="button" @click="router.push('/teacher/dashboard')">대시보드</button>
      </div>
    </div>

    <div v-else-if="analytics" class="analytics-stack">
      <div class="kpi-grid">
        <div v-for="metric in metricCards" :key="metric.key" class="kpi-card" :class="metric.className">
          <div class="kpi-label">{{ metric.label }}</div>
          <div class="kpi-value">{{ scoreText(metric.value) }}</div>
        </div>
        <div class="kpi-card topic-card">
          <div class="kpi-label">난이도 지표</div>
          <div class="kpi-value">{{ difficultyPercent }}%</div>
        </div>
      </div>

      <div class="grid">
        <section class="card">
          <div class="card-heading">
            <h3>AIC 분포</h3>
            <span class="muted-row">점수 구간별 제출 학생 수</span>
          </div>
          <div v-if="distributionConfig" class="chart-box">
            <BarChart :config="distributionConfig" />
          </div>
          <div v-else class="empty-state compact">분포 데이터가 없습니다.</div>
        </section>

        <section class="card">
          <div class="card-heading">
            <h3>난이도 해석</h3>
          </div>
          <div class="difficulty">
            <div class="difficulty-value">{{ difficultyPercent }}%</div>
            <div class="difficulty-track">
              <div class="difficulty-fill" :style="{ width: `${difficultyPercent}%` }"></div>
            </div>
            <p class="muted-row">AIC 평균이 낮을수록 난이도 지표가 높아집니다.</p>
          </div>
        </section>
      </div>

      <div class="grid">
        <section class="card">
          <div class="card-heading">
            <h3>상위 5명</h3>
          </div>
          <div v-if="!analytics.top5.length" class="empty-state compact">상위 학생 데이터가 없습니다.</div>
          <div v-else class="rank-list">
            <div v-for="(s, index) in analytics.top5" :key="`${s.name}-${index}`" class="rank-row">
              <span>{{ index + 1 }}</span>
              <strong>{{ s.name }}</strong>
              <em>{{ scoreText(s.aic) }}</em>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-heading">
            <h3>하위 5명</h3>
          </div>
          <div v-if="!analytics.bottom5.length" class="empty-state compact">하위 학생 데이터가 없습니다.</div>
          <div v-else class="rank-list">
            <div v-for="(s, index) in analytics.bottom5" :key="`${s.name}-${index}`" class="rank-row">
              <span>{{ index + 1 }}</span>
              <strong>{{ s.name }}</strong>
              <em>{{ scoreText(s.aic) }}</em>
            </div>
          </div>
        </section>
      </div>

      <div class="actions">
        <button class="btn btn-secondary" type="button" @click="router.push('/teacher/dashboard')">대시보드</button>
      </div>
    </div>

    <div v-else class="card">
      <div class="empty-state">과제 분석 데이터가 없습니다.</div>
      <div class="actions">
        <button class="btn btn-secondary" type="button" @click="router.push('/teacher/dashboard')">대시보드</button>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.analytics-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
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
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.chart-box {
  height: 300px;
}

.compact {
  padding: var(--space-6);
}

.difficulty {
  display: grid;
  gap: var(--space-4);
}

.difficulty-value {
  color: var(--color-aic);
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
}

.difficulty-track {
  height: 10px;
  overflow: hidden;
  border-radius: var(--radius-full);
  background: var(--color-gray-100);
}

.difficulty-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: linear-gradient(90deg, var(--color-oi), var(--color-ui), var(--color-danger));
}

.rank-list {
  display: grid;
  gap: var(--space-2);
}

.rank-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  justify-content: space-between;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  font-size: var(--text-sm);
}

.rank-row span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--color-gray-100);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 700;
}

.rank-row strong {
  flex: 1;
}

.rank-row em {
  color: var(--color-aic);
  font-style: normal;
  font-weight: 800;
}

.actions {
  margin-top: 1rem;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

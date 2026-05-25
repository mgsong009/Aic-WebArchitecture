<script setup>
import { computed, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAdminStore } from '@/stores/admin'

const admin = useAdminStore()

const totalLearningRecords = computed(() => admin.stats?.submissions?.total ?? null)
const totalStudents = computed(() => admin.stats?.users?.students ?? null)
const averageLogsPerStudent = computed(() => {
  if (totalLearningRecords.value === null || totalStudents.value === null) {
    return null
  }

  const recordCount = Number(totalLearningRecords.value)
  const studentCount = Number(totalStudents.value)

  if (!Number.isFinite(recordCount) || !Number.isFinite(studentCount) || studentCount === 0) {
    return null
  }

  return recordCount / studentCount
})

onMounted(() => {
  admin.fetchStats()
})

function fmt(val) {
  return val !== null && val !== undefined ? val : '—'
}

function fmtFixed(val, digits = 2) {
  return val !== null && val !== undefined && Number.isFinite(Number(val))
    ? Number(val).toFixed(digits)
    : '—'
}
</script>

<template>
  <AppLayout title="시스템 현황" subtitle="전체 플랫폼 운영 현황을 한눈에 확인합니다.">
    <div v-if="admin.loading" class="admin-loading">데이터를 불러오는 중...</div>
    <div v-else-if="admin.error" class="admin-error">{{ admin.error }}</div>

    <template v-else-if="admin.stats">
      <!-- Section 1: 사용자 현황 -->
      <section class="admin-section">
        <h2 class="section-title">사용자 현황</h2>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">전체 사용자</div>
            <div class="stat-value">{{ fmt(admin.stats.users?.total) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">학생</div>
            <div class="stat-value">{{ fmt(admin.stats.users?.students) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">교사</div>
            <div class="stat-value">{{ fmt(admin.stats.users?.teachers) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">관리자</div>
            <div class="stat-value">{{ fmt(admin.stats.users?.admins) }}</div>
          </div>
        </div>
      </section>

      <!-- Section 2: 학습 현황 -->
      <section class="admin-section">
        <h2 class="section-title">학습 현황</h2>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">클래스 수</div>
            <div class="stat-value">{{ fmt(admin.stats.classes?.total) }}</div>
            <div class="stat-sub">평균 {{ fmt(admin.stats.classes?.avg_students_per_class) }}명/클래스</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">학습 과정 기록</div>
            <div class="stat-value">{{ fmt(totalLearningRecords) }}<span class="stat-unit">건</span></div>
            <div class="stat-sub">프롬프트·초안·최종본 기준</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">학생당 평균 로그</div>
            <div class="stat-value">{{ fmtFixed(averageLogsPerStudent) }}<span class="stat-unit">건</span></div>
            <div class="stat-sub">{{ fmt(totalLearningRecords) }}건 / {{ fmt(totalStudents) }}명</div>
          </div>
          <div class="stat-card stat-card--success">
            <div class="stat-label">분석 완료율</div>
            <div class="stat-value">{{ fmt(admin.stats.submissions?.analysis_rate) }}<span class="stat-unit">%</span></div>
            <div class="stat-sub">분석 {{ fmt(admin.stats.submissions?.analyzed) }}건</div>
          </div>
        </div>
      </section>

      <!-- Section 3: 파이프라인 잡 현황 -->
      <section class="admin-section">
        <h2 class="section-title">파이프라인 잡 현황</h2>
        <div class="stat-grid">
          <div class="stat-card stat-card--warning">
            <div class="stat-label">대기 중 (Pending)</div>
            <div class="stat-value">{{ fmt(admin.stats.jobs?.pending) }}</div>
          </div>
          <div class="stat-card stat-card--info">
            <div class="stat-label">실행 중 (Running)</div>
            <div class="stat-value">{{ fmt(admin.stats.jobs?.running) }}</div>
          </div>
          <div class="stat-card stat-card--success">
            <div class="stat-label">완료 (Done)</div>
            <div class="stat-value">{{ fmt(admin.stats.jobs?.done) }}</div>
          </div>
          <div class="stat-card stat-card--danger">
            <div class="stat-label">실패 (Failed)</div>
            <div class="stat-value">{{ fmt(admin.stats.jobs?.failed) }}</div>
            <div class="stat-sub">완료율 {{ fmt(admin.stats.jobs?.completion_rate) }}%</div>
          </div>
        </div>
      </section>

      <!-- Section 4: 성적 요약 -->
      <section class="admin-section">
        <h2 class="section-title">시스템 평균 점수</h2>
        <div class="stat-grid">
          <div class="stat-card stat-card--aic">
            <div class="stat-label">AIC 종합</div>
            <div class="stat-value">{{ fmt(admin.stats.scores?.avg_aic) }}</div>
            <div class="stat-sub">전체 평균</div>
          </div>
          <div class="stat-card stat-card--pi">
            <div class="stat-label">PI (Prompt Insight)</div>
            <div class="stat-value">{{ fmt(admin.stats.scores?.avg_pi) }}</div>
          </div>
          <div class="stat-card stat-card--ui">
            <div class="stat-label">UI (User Intervention)</div>
            <div class="stat-value">{{ fmt(admin.stats.scores?.avg_ui) }}</div>
          </div>
          <div class="stat-card stat-card--oi">
            <div class="stat-label">OI (Originality Index)</div>
            <div class="stat-value">{{ fmt(admin.stats.scores?.avg_oi) }}</div>
          </div>
        </div>
        <div class="feedback-row">
          <span class="feedback-label">교사 피드백 총 건수</span>
          <span class="feedback-value">{{ fmt(admin.stats.feedback?.total) }}건</span>
        </div>
      </section>
    </template>
  </AppLayout>
</template>

<style scoped>
.admin-loading,
.admin-error {
  padding: var(--space-8);
  text-align: center;
  color: var(--text-muted);
  font-size: var(--font-size-base);
}

.admin-error {
  color: #b91c1c;
}

.admin-section {
  margin-bottom: var(--space-8);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.stat-card {
  padding: var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0;
  color: var(--text-muted);
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
}

.stat-unit {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-left: 2px;
}

.stat-sub {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}

.stat-card--aic .stat-value { color: var(--color-aic); }
.stat-card--aic { border-left: 3px solid var(--color-aic); }

.stat-card--pi { border-top: 3px solid var(--color-pi); }
.stat-card--pi .stat-value { color: var(--color-pi); }

.stat-card--ui { border-top: 3px solid var(--color-ui); }
.stat-card--ui .stat-value { color: var(--color-ui); }

.stat-card--oi { border-top: 3px solid var(--color-oi); }
.stat-card--oi .stat-value { color: var(--color-oi); }

.stat-card--warning { border-left: 3px solid var(--color-warning); }
.stat-card--warning .stat-value { color: var(--color-warning); }

.stat-card--info { border-left: 3px solid var(--color-info); }
.stat-card--info .stat-value { color: var(--color-info); }

.stat-card--success { border-left: 3px solid var(--color-success); }
.stat-card--success .stat-value { color: var(--color-success); }

.stat-card--danger { border-left: 3px solid var(--color-danger); }
.stat-card--danger .stat-value { color: var(--color-danger); }

.feedback-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  margin-top: var(--space-4);
}

.feedback-label {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: 600;
}

.feedback-value {
  font-size: var(--font-size-lg);
  font-weight: 800;
  color: var(--text-primary);
}

@media (max-width: 900px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>

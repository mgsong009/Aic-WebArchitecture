<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getTeacherStudents } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { referenceStudents, scoreColor } from './teacherReferenceData'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const rows = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(15)
const filters = ref({ search: '', status: '', sort: 'aic_desc', chip: 'all' })

onMounted(fetchStudents)

const fallbackRows = computed(() => {
  let next = [...referenceStudents]
  const query = filters.value.search.trim().toLowerCase()
  if (query) {
    next = next.filter((student) => student.name.includes(query) || student.user_id_str.toLowerCase().includes(query))
  }
  if (filters.value.status) {
    next = next.filter((student) => statusKey(student.aic) === filters.value.status)
  }
  if (filters.value.chip === 'ai') next = next.filter((student) => student.ui < 60 || student.pi < 60)
  if (filters.value.chip === 'pi') next = next.filter((student) => student.pi < 60)
  if (filters.value.chip === 'oi') next = next.filter((student) => student.oi < 60)
  next.sort((a, b) => filters.value.sort === 'aic_asc' ? a.aic - b.aic : b.aic - a.aic)
  return next
})
const displayRows = computed(() => rows.value.length ? rows.value : fallbackRows.value.slice((page.value - 1) * perPage.value, page.value * perPage.value))
const displayTotal = computed(() => rows.value.length ? total.value : fallbackRows.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(displayTotal.value / perPage.value)))
const pageStart = computed(() => displayTotal.value ? (page.value - 1) * perPage.value + 1 : 0)
const pageEnd = computed(() => Math.min(page.value * perPage.value, displayTotal.value))
const summary = computed(() => {
  const source = rows.value.length ? rows.value : referenceStudents
  return {
    total: source.length || 28,
    strong: source.filter((student) => student.aic >= 65).length || 11,
    average: source.filter((student) => student.aic >= 50 && student.aic < 65).length || 13,
    risk: source.filter((student) => student.aic < 50).length || 4,
  }
})

async function fetchStudents() {
  loading.value = true
  error.value = ''
  try {
    const data = await getTeacherStudents({
      search: filters.value.search,
      status: filters.value.status,
      sort: filters.value.sort,
      page: page.value,
      per_page: perPage.value,
    })
    rows.value = data.students
    total.value = data.total
  } catch {
    rows.value = []
    total.value = 0
    error.value = '실시간 학생 목록을 불러오지 못해 reference fallback을 표시합니다.'
  } finally {
    loading.value = false
  }
}

function statusKey(score) {
  if (score == null) return 'pending'
  if (score >= 80) return 'excellent'
  if (score >= 65) return 'good'
  if (score >= 50) return 'average'
  return 'risk'
}

async function applyFilters() {
  page.value = 1
  await fetchStudents()
}

function setChip(chip) {
  filters.value.chip = chip
  page.value = 1
}

async function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value || nextPage === page.value) return
  page.value = nextPage
  if (rows.value.length) await fetchStudents()
}

function goStudent(student) {
  router.push(`/teacher/students/${student.id || 6}`)
}
</script>

<template>
  <AppLayout title="Student List" subtitle="CS101 · Assignment #5 · 28명 중 25명 분석 완료">
    <template #actions>
      <button class="btn btn-secondary btn-sm" type="button">CSV 내보내기</button>
      <button class="btn btn-primary btn-sm" type="button">+ 학생 추가</button>
    </template>

    <div class="students-page animate-fade-in">
      <p v-if="error" class="fallback-note">{{ error }}</p>

      <div class="summary-grid">
        <div class="summary-card"><strong>{{ summary.total }}</strong><span>전체</span></div>
        <div class="summary-card good"><strong>{{ summary.strong }}</strong><span>Excellent/Good</span></div>
        <div class="summary-card average"><strong>{{ summary.average }}</strong><span>Average</span></div>
        <div class="summary-card risk"><strong>{{ summary.risk }}</strong><span>Risk</span></div>
      </div>

      <section class="filter-bar">
        <label class="filter-search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
          <input v-model.trim="filters.search" type="search" placeholder="학생 이름 또는 ID 검색..." @keyup.enter="applyFilters">
        </label>
        <select v-model="filters.status" class="filter-select" @change="applyFilters">
          <option value="">전체 상태</option>
          <option value="excellent">Excellent</option>
          <option value="good">Good</option>
          <option value="average">Average</option>
          <option value="risk">Risk</option>
        </select>
        <select v-model="filters.sort" class="filter-select" @change="applyFilters">
          <option value="aic_desc">Assignment #5 · AIC 높은 순</option>
          <option value="aic_asc">Assignment #5 · AIC 낮은 순</option>
        </select>
        <button class="filter-chip" :class="{ active: filters.chip === 'all' }" type="button" @click="setChip('all')">전체</button>
        <button class="filter-chip" :class="{ active: filters.chip === 'ai' }" type="button" @click="setChip('ai')">AI 의존도 높음</button>
        <button class="filter-chip" :class="{ active: filters.chip === 'pi' }" type="button" @click="setChip('pi')">PI 낮음</button>
        <button class="filter-chip" :class="{ active: filters.chip === 'oi' }" type="button" @click="setChip('oi')">OI 낮음</button>
      </section>

      <div class="data-table-wrapper">
        <table class="data-table students-table">
          <thead>
            <tr>
              <th>학생</th><th>Student ID</th><th>AIC ↓</th><th>PI</th><th>UI</th><th>OI</th><th>TopicScore</th><th>상태</th><th>과제</th><th>액션</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && !displayRows.length"><td colspan="10" class="loading-cell">불러오는 중...</td></tr>
            <tr v-for="student in displayRows" :key="student.id || student.user_id_str" @click="goStudent(student)">
              <td>
                <div class="student-cell">
                  <span class="student-avatar" :style="{ background: student.color || 'linear-gradient(135deg,#F97316,#8B5CF6)' }">{{ student.name?.slice(0, 1) }}</span>
                  <span><strong>{{ student.name }}</strong><small>{{ student.user_id_str || `STU${student.id}` }}</small></span>
                </div>
              </td>
              <td class="muted">{{ student.user_id_str || `STU${student.id}` }}</td>
              <td>
                <div class="score-cell">
                  <strong class="aic-score" :style="{ color: scoreColor(student.aic) }">{{ student.aic ?? '-' }}</strong>
                  <span class="mini-bar-track"><span class="mini-bar-fill" :style="{ width: `${student.aic || 0}%` }"></span></span>
                </div>
              </td>
              <td class="pi-text">{{ student.pi ?? '-' }}</td>
              <td class="ui-text">{{ student.ui ?? '-' }}</td>
              <td class="oi-text">{{ student.oi ?? '-' }}</td>
              <td class="topic-text">{{ student.topic ?? student.topic_score ?? '-' }}</td>
              <td><StatusBadge :score="student.aic" /></td>
              <td><span class="badge badge-neutral">{{ student.assignment || `A${student.submission_count || 5}` }}</span></td>
              <td><button class="btn btn-ghost btn-sm" type="button" @click.stop="goStudent(student)">보기</button></td>
            </tr>
          </tbody>
        </table>
        <div class="pagination">
          <span>{{ displayTotal }}명 중 {{ pageStart }}-{{ pageEnd }} 표시</span>
          <div class="pag-btns">
            <button class="pag-btn" type="button" :disabled="page <= 1" @click="changePage(page - 1)">←</button>
            <span class="pag-btn active">{{ page }}</span>
            <button class="pag-btn" type="button" :disabled="page >= totalPages" @click="changePage(page + 1)">→</button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.students-page { display: grid; gap: var(--space-4); }
.fallback-note { padding: var(--space-3) var(--space-4); background: var(--color-ui-pale); border: 1px solid rgba(249, 115, 22, 0.2); border-radius: var(--radius-lg); color: var(--text-secondary); font-size: var(--text-sm); }
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }
.summary-card { background: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-lg); padding: 14px; text-align: center; }
.summary-card strong { display: block; font-size: 20px; color: var(--color-aic); }
.summary-card span { font-size: 11px; color: var(--text-muted); }
.summary-card.good { background: var(--color-oi-pale); border-color: rgba(16,185,129,0.2); }
.summary-card.good strong { color: var(--color-oi); }
.summary-card.average { background: #FEF9C3; border-color: rgba(234,179,8,0.2); }
.summary-card.average strong { color: #A16207; }
.summary-card.risk { background: #FEF2F2; border-color: rgba(239,68,68,0.2); }
.summary-card.risk strong { color: var(--color-danger); }
.filter-bar { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; }
.filter-search { flex: 1; min-width: 220px; display: flex; align-items: center; gap: 8px; background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: var(--radius-md); padding: 8px 12px; }
.filter-search input { border: 0; outline: 0; background: transparent; flex: 1; min-width: 0; }
.filter-select { padding: 8px 12px; border: 1px solid var(--border-default); border-radius: var(--radius-md); background: var(--bg-surface); color: var(--text-primary); }
.filter-chip { display: inline-flex; align-items: center; padding: 5px 12px; background: var(--color-gray-100); border: 1px solid var(--border-light); border-radius: var(--radius-full); font-size: 12px; font-weight: 700; color: var(--text-secondary); }
.filter-chip.active { background: var(--color-aic-pale); border-color: var(--color-pi); color: var(--color-pi); }
.students-table { min-width: 980px; }
.student-cell { display: flex; align-items: center; gap: 8px; }
.student-cell small { display: block; font-size: 11px; color: var(--text-muted); }
.student-avatar { width: 32px; height: 32px; border-radius: 999px; display: grid; place-items: center; color: white; font-size: 12px; font-weight: 800; flex-shrink: 0; }
.score-cell { display: flex; align-items: center; gap: 8px; }
.aic-score { min-width: 24px; font-size: 16px; }
.mini-bar-track { width: 60px; height: 5px; background: var(--color-gray-100); border-radius: 999px; overflow: hidden; }
.mini-bar-fill { display: block; height: 100%; background: var(--color-aic); border-radius: inherit; }
.muted { color: var(--text-muted); font-size: 12px; }
.pi-text { color: var(--color-pi); font-weight: 700; }
.ui-text { color: var(--color-ui); font-weight: 700; }
.oi-text { color: var(--color-oi); font-weight: 700; }
.topic-text { color: var(--color-topic); font-weight: 700; }
.loading-cell { text-align: center; color: var(--text-muted); padding: var(--space-8) !important; }
.pagination { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-top: 1px solid var(--border-light); font-size: 12px; color: var(--text-muted); }
.pag-btns { display: flex; gap: 4px; align-items: center; }
.pag-btn { min-width: 30px; height: 30px; display: grid; place-items: center; border: 1px solid var(--border-light); border-radius: var(--radius-sm); background: white; color: var(--text-muted); font-weight: 700; }
.pag-btn.active { background: var(--color-aic); border-color: var(--color-aic); color: white; padding: 0 10px; }
.pag-btn:disabled { opacity: 0.45; cursor: not-allowed; }
@media (max-width: 768px) { .summary-grid { grid-template-columns: repeat(2, 1fr); } .pagination { align-items: flex-start; flex-direction: column; gap: var(--space-3); } }
</style>

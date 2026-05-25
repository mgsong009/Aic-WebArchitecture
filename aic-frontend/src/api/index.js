import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export const api = axios.create({ baseURL: '/api/v1' })

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function asObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {}
}

function asNumber(value, fallback = 0) {
  const next = Number(value)
  return Number.isFinite(next) ? next : fallback
}

export function normalizeStudentDashboard(data = {}) {
  return {
    student: asObject(data.student),
    latest_metrics: asObject(data.latest_metrics),
    latest_delta: asObject(data.latest_delta),
    class_avg: asObject(data.class_avg),
    rank: data.rank ?? null,
    total_students: data.total_students ?? 0,
    trend: asArray(data.trend),
    recent_assignments: asArray(data.recent_assignments),
    metrics_history: asArray(data.metrics_history),
  }
}

export function normalizeStudentGrowth(data = {}) {
  return {
    assignments: asArray(data.assignments),
    class_avg_trend: asArray(data.class_avg_trend),
  }
}

export function normalizeTeacherAssignmentAnalytics(data = {}, assignmentId) {
  return {
    ...data,
    assignment: asObject(data.assignment).id
      ? data.assignment
      : { id: assignmentId, title: `과제 ${assignmentId}` },
    class_avg: asObject(data.class_avg),
    distribution: asArray(data.distribution),
    top5: asArray(data.top5),
    bottom5: asArray(data.bottom5),
    difficulty: asNumber(data.difficulty),
  }
}

export function normalizeTeacherDashboard(data = {}) {
  return {
    ...data,
    cls: asObject(data.cls),
    class_avg: asObject(data.class_avg),
    trend: asArray(data.trend),
    risk_students: asArray(data.risk_students),
    top_students: asArray(data.top_students),
    aic_distribution: asArray(data.aic_distribution),
    risk_count: data.risk_count ?? 0,
    excellent_count: data.excellent_count ?? 0,
  }
}

export function normalizeTeacherStudentDetail(data = {}) {
  return {
    ...data,
    student: asObject(data.student),
    trend: asArray(data.trend),
    assignments: asArray(data.assignments),
    weak_metrics: asArray(data.weak_metrics),
    latest_metrics: asObject(data.latest_metrics),
    teacher_feedback: data.teacher_feedback || null,
  }
}

export function normalizeTeacherAdvancedAnalytics(data = {}) {
  const difficultyAdjusted = asObject(data.difficulty_adjusted_aic)
  const anomalyDetection = asObject(data.anomaly_detection)

  return {
    scatter_data: asArray(data.scatter_data),
    correlation_matrix: asObject(data.correlation_matrix),
    clusters: asArray(data.clusters),
    strategies: asArray(data.strategies),
    effort_samples: asArray(data.effort_samples),
    effort_correlation: data.effort_correlation ?? null,
    topic_oi_samples: asArray(data.topic_oi_samples),
    similarity_bands: asArray(data.similarity_bands),
    difficulty_adjusted_aic: {
      overall_mean_aic: difficultyAdjusted.overall_mean_aic ?? null,
      summary: asArray(difficultyAdjusted.summary),
      students: asArray(difficultyAdjusted.students),
      method_note: difficultyAdjusted.method_note || '',
    },
    confidence_intervals: asArray(data.confidence_intervals),
    anomaly_detection: {
      items: asArray(anomalyDetection.items),
      summary_counts: asObject(anomalyDetection.summary_counts),
      rule_counts: asArray(anomalyDetection.rule_counts),
      method_note: anomalyDetection.method_note || '',
    },
  }
}

export function normalizeTeacherStatisticsValidation(data = {}) {
  const difficultyAdjusted = asObject(data.difficulty_adjusted_aic)
  const anomalyDetection = asObject(data.anomaly_detection)

  return {
    difficulty_adjusted_aic: {
      overall_mean_aic: difficultyAdjusted.overall_mean_aic ?? null,
      summary: asArray(difficultyAdjusted.summary),
      students: asArray(difficultyAdjusted.students),
      method_note: difficultyAdjusted.method_note || '',
    },
    confidence_intervals: asArray(data.confidence_intervals),
    anomaly_detection: {
      items: asArray(anomalyDetection.items),
      summary_counts: {
        total: asNumber(asObject(anomalyDetection.summary_counts).total),
        high: asNumber(asObject(anomalyDetection.summary_counts).high),
        caution: asNumber(asObject(anomalyDetection.summary_counts).caution),
        low: asNumber(asObject(anomalyDetection.summary_counts).low),
      },
      rule_counts: asArray(anomalyDetection.rule_counts),
      method_note: anomalyDetection.method_note || '',
    },
  }
}

export function normalizeTeacherAssignmentList(data = {}) {
  return asArray(data.assignments).map((assignment) => ({
    id: assignment.id,
    title: assignment.title || `과제 ${assignment.id}`,
    course_code: assignment.course_code || '',
    due_date: assignment.due_date || null,
    submission_count: asNumber(assignment.submission_count),
    analyzed_submission_count: asNumber(assignment.analyzed_submission_count),
  }))
}

export async function getStudentDashboard() {
  const { data } = await api.get('/student/dashboard')
  return normalizeStudentDashboard(data)
}

export async function getStudentAssignments() {
  const { data } = await api.get('/student/assignments')
  return asArray(data.assignments)
}

export async function getStudentAssignmentDetail(assignmentId) {
  const { data } = await api.get(`/student/assignments/${assignmentId}`)
  return data
}

export async function getStudentGrowth() {
  const { data } = await api.get('/student/growth')
  return normalizeStudentGrowth(data)
}

export async function getStudentFeedback(assignmentId) {
  const { data } = await api.get(`/student/feedback/${assignmentId}`)
  return data
}

export async function submitStudentSubmission(body) {
  const { data } = await api.post('/submissions', body)
  return data
}

export async function getJobStatus(jobId) {
  const { data } = await api.get(`/jobs/${jobId}/status`)
  return data
}

export async function getTeacherDashboard() {
  const { data } = await api.get('/teacher/dashboard')
  return normalizeTeacherDashboard(data)
}

export async function getTeacherStudents(params = {}) {
  const { data } = await api.get('/teacher/students', { params })
  return {
    total: asNumber(data.total),
    students: asArray(data.students),
  }
}

export async function getTeacherStudentDetail(studentId) {
  const { data } = await api.get(`/teacher/students/${studentId}`)
  return normalizeTeacherStudentDetail(data)
}

export async function getTeacherRiskStudents() {
  const { data } = await api.get('/teacher/risk-students')
  return asArray(data.risk_students)
}

export async function getTeacherAssignments() {
  const { data } = await api.get('/teacher/assignments')
  return normalizeTeacherAssignmentList(data)
}

export async function saveTeacherFeedback(body) {
  const { data } = await api.post('/teacher/feedback', body)
  return data
}

export async function getTeacherAssignmentAnalytics(assignmentId) {
  const { data } = await api.get(`/teacher/analytics/assignment/${assignmentId}`)
  return normalizeTeacherAssignmentAnalytics(data, assignmentId)
}

export async function getTeacherAdvancedAnalytics() {
  const { data } = await api.get('/teacher/analytics/advanced')
  return normalizeTeacherAdvancedAnalytics(data)
}

export async function getTeacherStatisticsValidation() {
  const { data } = await api.get('/teacher/statistics/validation')
  return normalizeTeacherStatisticsValidation(data)
}

export async function getAdminDashboard() {
  const { data } = await api.get('/admin/dashboard')
  return data
}

api.interceptors.request.use((cfg) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    cfg.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return cfg
})

let refreshing = false
let refreshPromise = null

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status !== 401) {
      return Promise.reject(err)
    }

    const original = err.config || {}
    const isRefreshRequest = (original.url || '').includes('/auth/refresh')
    if (original._retry || isRefreshRequest) {
      const auth = useAuthStore()
      await auth.logout()
      window.location.href = '/login'
      return Promise.reject(err)
    }

    try {
      if (!refreshPromise) {
        refreshing = true
        const auth = useAuthStore()
        refreshPromise = auth.refresh().then(() => auth.accessToken).finally(() => {
          refreshing = false
          refreshPromise = null
        })
      }

      const token = await refreshPromise
      const retryConfig = {
        ...original,
        _retry: true,
        headers: {
          ...(original.headers || {}),
          Authorization: `Bearer ${token}`,
        },
      }
      return api(retryConfig)
    } catch (refreshErr) {
      const auth = useAuthStore()
      await auth.logout()
      window.location.href = '/login'
      return Promise.reject(refreshErr)
    }
  }
)

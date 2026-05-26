// Admin Analysis Quality API
// Mock data 반환 — 실제 FastAPI 연결 시 아래 주석 엔드포인트로 교체
//   GET /api/v1/admin/analysis-runs/latest
//   GET /api/v1/admin/analysis-runs/{runId}/quality
//   GET /api/v1/admin/analysis-runs/{runId}/pipeline-steps
//   GET /api/v1/admin/analysis-runs/{runId}/runtime
//   POST /api/v1/admin/analysis-runs/{runId}/reprocess

const mockRun = {
  runId: 'RUN-20251123-233424',
  course: 'CS101',
  assignment: 'Assignment #5',
  status: 'success',
  processedRows: 1913,
  validRows: 1888,
  successRate: 98.7,
  totalRuntimeSec: 421.8,
  avgRuntimePerSample: 0.22,

  dataHealth: {
    score: 87,
    requiredColumns: 'normal',
    missingRows: 37,
    duplicateRows: 12,
    textOutliers: 18,
    ratingCoverage: 65.2,
    lowSampleCourses: 2,
  },

  backend: {
    embeddingBackend: 'SBERT',
    model: 'paraphrase-multilingual-mpnet-base-v2',
    fallback: 'None',
    metricVersion: 'v1.0.3',
    pipelineVersion: '2025.11.23',
    configHash: 'a7f91c2',
    createdAt: '2025-11-23 23:34:24',
  },

  pipelineSteps: [
    { name: 'Data Load',  status: 'success', seconds: 1.2 },
    { name: 'Preprocess', status: 'success', seconds: 0.9 },
    { name: 'PI',         status: 'success', seconds: 0.8 },
    { name: 'Embedding',  status: 'success', seconds: 390.4 },
    { name: 'UI/OI',      status: 'success', seconds: 10.3 },
    { name: 'Validation', status: 'warning', seconds: 3.4 },
    { name: 'Save',       status: 'success', seconds: 1.1 },
  ],

  readiness: {
    status: 'caution',
    reason: 'rating 보유율이 65.2%로 낮아 검증 지표 해석 시 주의가 필요합니다.',
    actions: [
      '다음 분석 전 rating 수집률을 70% 이상으로 개선',
      'course별 최소 표본 수 미달 과제 확인',
      'Embedding 단계 처리시간 최적화 검토',
    ],
  },
}

export async function getLatestAnalysisRun() {
  // return (await api.get('/admin/analysis-runs/latest')).data
  return mockRun
}

export async function getAnalysisQuality(runId) {
  // return (await api.get(`/admin/analysis-runs/${runId}/quality`)).data
  return mockRun
}

export async function reprocessAnalysisRun(runId) {
  // return (await api.post(`/admin/analysis-runs/${runId}/reprocess`)).data
  return { ok: true, runId }
}

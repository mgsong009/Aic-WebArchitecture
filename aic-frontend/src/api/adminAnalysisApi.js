import { api } from '@/api/index'

export async function getLatestAnalysisRun() {
  const { data } = await api.get('/admin/analysis-runs/latest')
  return data
}

export async function getAnalysisQuality(runId) {
  const { data } = await api.get(`/admin/analysis-runs/${runId}/quality`)
  return data
}

export async function getAnalysisPipelineSteps(runId) {
  const { data } = await api.get(`/admin/analysis-runs/${runId}/pipeline-steps`)
  return data
}

export async function getAnalysisRuntime(runId) {
  const { data } = await api.get(`/admin/analysis-runs/${runId}/runtime`)
  return data
}

export async function reprocessAnalysisRun(runId) {
  const { data } = await api.post(`/admin/analysis-runs/${runId}/reprocess`)
  return data
}

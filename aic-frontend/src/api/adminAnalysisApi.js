import { api } from '@/api/index'

export async function createBenchmarkRun(body = {}) {
  const { data } = await api.post('/admin/benchmarks', body)
  return data
}

export async function listBenchmarkRuns(limit = 20) {
  const { data } = await api.get('/admin/benchmarks', { params: { limit } })
  return data
}

export async function getBenchmarkRun(runId) {
  const { data } = await api.get(`/admin/benchmarks/${runId}`)
  return data
}

export async function compareBenchmarkRuns(baselineRunId, optimizedRunId) {
  const { data } = await api.get('/admin/benchmarks/compare', {
    params: { baselineRunId, optimizedRunId },
  })
  return data
}

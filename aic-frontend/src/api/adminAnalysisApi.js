import { api } from '@/api'

const emptyDataHealth = {
  score: 0,
  requiredColumns: 'unknown',
  missingRows: 0,
  missingFields: [],
  duplicateRows: 0,
  textOutliers: 0,
  ratingCoverage: null,
  ratingMissingRows: null,
  lowSampleCourses: 0,
}

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

function normalizePerformanceRows(rows = []) {
  return asArray(rows).map((row) => ({
    key: row.key,
    label: row.label || row.key,
    unit: row.unit || '',
    baseline: row.baseline ?? null,
    optimized: row.optimized ?? null,
    deltaPct: row.deltaPct ?? null,
    betterDirection: row.betterDirection || 'down',
  }))
}

function normalizeScoreRows(rows = []) {
  return asArray(rows).map((row) => ({
    key: row.key,
    label: row.label || String(row.key || '').toUpperCase(),
    baseline: row.baseline ?? null,
    optimized: row.optimized ?? null,
    delta: row.delta ?? null,
    tolerance: row.tolerance ?? 0.01,
    passed: row.passed ?? null,
  }))
}

export function normalizeAnalysisRun(data = {}) {
  const comparison = asObject(data.comparison)

  return {
    ...data,
    processedRows: asNumber(data.processedRows),
    validRows: asNumber(data.validRows),
    successRate: asNumber(data.successRate),
    totalRuntimeSec: data.totalRuntimeSec ?? null,
    avgRuntimePerSample: data.avgRuntimePerSample ?? null,
    dataHealth: {
      ...emptyDataHealth,
      ...asObject(data.dataHealth),
    },
    backend: asObject(data.backend),
    pipelineSteps: asArray(data.pipelineSteps),
    readiness: {
      status: 'caution',
      reason: '분석 품질 상태를 확인할 수 없습니다.',
      actions: [],
      ...asObject(data.readiness),
    },
    comparison: {
      metricVersion: comparison.metricVersion || null,
      baselineVersion: comparison.baselineVersion || null,
      optimizedVersion: comparison.optimizedVersion || null,
      measurementMode: comparison.measurementMode || 'unknown',
      population: comparison.population || null,
      sampleCount: comparison.sampleCount ?? data.validRows ?? data.processedRows ?? null,
      minSampleCount: comparison.minSampleCount ?? 10,
      runtimeMs: comparison.runtimeMs ?? null,
      baselineRuntimeMs: comparison.baselineRuntimeMs ?? null,
      runtimeDeltaPct: comparison.runtimeDeltaPct ?? null,
      memoryPeakKb: comparison.memoryPeakKb ?? null,
      baselineMemoryPeakKb: comparison.baselineMemoryPeakKb ?? null,
      memoryDeltaPct: comparison.memoryDeltaPct ?? null,
      throughputPerSec: comparison.throughputPerSec ?? null,
      baselineThroughputPerSec: comparison.baselineThroughputPerSec ?? null,
      throughputDeltaPct: comparison.throughputDeltaPct ?? null,
      scoreDeltas: asObject(comparison.scoreDeltas),
      baselineScores: asObject(comparison.baselineScores),
      currentScores: asObject(comparison.currentScores),
      baselineAvailable: Boolean(comparison.baselineAvailable),
      performanceRows: normalizePerformanceRows(comparison.performanceRows),
      scoreRows: normalizeScoreRows(comparison.scoreRows),
      scoreTolerance: comparison.scoreTolerance ?? 0.01,
      qualityPassed: comparison.qualityPassed ?? null,
      bootstrapPassed: comparison.bootstrapPassed ?? null,
      measuredAt: comparison.measuredAt || null,
    },
  }
}

export async function getLatestAnalysisRun() {
  const { data } = await api.get('/admin/analysis-runs/latest')
  return normalizeAnalysisRun(data)
}

export async function getAnalysisQuality(runId) {
  const { data } = await api.get(`/admin/analysis-runs/${runId}/quality`)
  return normalizeAnalysisRun(data)
}

export async function reprocessAnalysisRun(runId) {
  const { data } = await api.post(`/admin/analysis-runs/${runId}/reprocess`)
  return data
}

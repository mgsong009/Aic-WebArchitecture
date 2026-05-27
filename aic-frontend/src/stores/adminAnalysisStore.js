import { defineStore } from 'pinia'
import {
  compareBenchmarkRuns,
  createBenchmarkRun,
  getBenchmarkRun,
  listBenchmarkRuns,
} from '@/api/adminAnalysisApi'

export const useAdminAnalysisStore = defineStore('adminAnalysis', {
  state: () => ({
    runs: [],
    selectedRun: null,
    comparison: null,
    baselineRunId: '',
    optimizedRunId: '',
    loading: false,
    detailLoading: false,
    comparing: false,
    starting: false,
    error: null,
  }),
  getters: {
    runningRun: (state) => state.runs.find((run) => run.status === 'running' || run.status === 'pending') || null,
    completedRuns: (state) => state.runs.filter((run) => run.status === 'completed'),
  },
  actions: {
    async fetchRuns() {
      this.loading = true
      this.error = null
      try {
        const data = await listBenchmarkRuns(30)
        this.runs = data.runs || []
        this._ensureSelection()
      } catch {
        this.error = 'benchmark 실행 목록을 불러오지 못했습니다.'
      } finally {
        this.loading = false
      }
    },
    async fetchRunDetail(runId) {
      if (!runId) return
      this.detailLoading = true
      this.error = null
      try {
        this.selectedRun = await getBenchmarkRun(runId)
      } catch {
        this.error = 'benchmark 상세 결과를 불러오지 못했습니다.'
      } finally {
        this.detailLoading = false
      }
    },
    async startBenchmark() {
      this.starting = true
      this.error = null
      try {
        const created = await createBenchmarkRun({
          label: `Benchmark ${new Date().toLocaleString()}`,
          sample_limit: 50,
          warmup_count: 1,
        })
        await this.fetchRuns()
        this.optimizedRunId = created.run_id
        await this.fetchRunDetail(created.run_id)
      } catch {
        this.error = 'benchmark 실행 요청에 실패했습니다.'
      } finally {
        this.starting = false
      }
    },
    async compareSelectedRuns() {
      if (!this.baselineRunId || !this.optimizedRunId) return
      this.comparing = true
      this.error = null
      try {
        this.comparison = await compareBenchmarkRuns(this.baselineRunId, this.optimizedRunId)
      } catch {
        this.error = 'benchmark 비교 결과를 불러오지 못했습니다.'
      } finally {
        this.comparing = false
      }
    },
    _ensureSelection() {
      const completed = this.runs.filter((run) => run.status === 'completed')
      if (!this.optimizedRunId && completed[0]) this.optimizedRunId = completed[0].run_id
      if (!this.baselineRunId && completed[1]) this.baselineRunId = completed[1].run_id
      if (!this.selectedRun && this.runs[0]) this.fetchRunDetail(this.runs[0].run_id)
    },
  },
})

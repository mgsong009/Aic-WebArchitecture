import { defineStore } from 'pinia'
import { getLatestAnalysisRun, reprocessAnalysisRun } from '@/api/adminAnalysisApi'

export const useAdminAnalysisStore = defineStore('adminAnalysis', {
  state: () => ({
    run: null,
    loading: false,
    error: null,
    reprocessing: false,
  }),
  actions: {
    async fetchLatestRun() {
      this.loading = true
      this.error = null
      try {
        this.run = await getLatestAnalysisRun()
      } catch {
        this.error = '분석 실행 데이터를 불러오지 못했습니다.'
      } finally {
        this.loading = false
      }
    },
    async reprocessRun() {
      if (!this.run) return
      this.reprocessing = true
      try {
        await reprocessAnalysisRun(this.run.runId)
        await this.fetchLatestRun()
      } catch {
        this.error = '재분석 요청에 실패했습니다.'
      } finally {
        this.reprocessing = false
      }
    },
  },
})

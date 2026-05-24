import { defineStore } from 'pinia'
import { getAdminDashboard } from '@/api/index'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    stats: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchStats() {
      this.loading = true
      this.error = null
      try {
        this.stats = await getAdminDashboard()
      } catch (e) {
        this.error = '데이터를 불러오지 못했습니다.'
      } finally {
        this.loading = false
      }
    },
  },
})

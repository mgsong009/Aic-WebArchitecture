import { defineStore } from 'pinia'
import { api } from '@/api'

export const useStudentStore = defineStore('student', {
  state: () => ({
    dashboard: null,
    assignments: [],
    growth: null,
  }),
  actions: {
    async fetchDashboard() {
      const { data } = await api.get('/student/dashboard')
      this.dashboard = data
    },
    async fetchAssignments() {
      const { data } = await api.get('/student/assignments')
      this.assignments = data.assignments
    },
    async fetchGrowth() {
      const { data } = await api.get('/student/growth')
      this.growth = data
    },
  },
})

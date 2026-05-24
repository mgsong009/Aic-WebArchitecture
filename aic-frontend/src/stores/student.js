import { defineStore } from 'pinia'
import { getStudentAssignments, getStudentDashboard, getStudentGrowth } from '@/api'

export const useStudentStore = defineStore('student', {
  state: () => ({
    dashboard: null,
    assignments: [],
    growth: null,
  }),
  actions: {
    async fetchDashboard() {
      this.dashboard = await getStudentDashboard()
    },
    async fetchAssignments() {
      this.assignments = await getStudentAssignments()
    },
    async fetchGrowth() {
      this.growth = await getStudentGrowth()
    },
  },
})

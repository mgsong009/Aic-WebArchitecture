import { defineStore } from 'pinia'
import { getTeacherDashboard, getTeacherStudents } from '@/api'

export const useTeacherStore = defineStore('teacher', {
  state: () => ({
    dashboard: null,
    studentList: null,
    riskCount: 0,
  }),
  actions: {
    async fetchDashboard() {
      const data = await getTeacherDashboard()
      this.dashboard = data
      this.riskCount = data.risk_count || 0
    },
    async fetchStudents(params = {}) {
      this.studentList = await getTeacherStudents(params)
    },
  },
})

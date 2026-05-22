import { defineStore } from 'pinia'
import { api } from '@/api'

export const useTeacherStore = defineStore('teacher', {
  state: () => ({
    dashboard: null,
    studentList: null,
    riskCount: 0,
  }),
  actions: {
    async fetchDashboard() {
      const { data } = await api.get('/teacher/dashboard')
      this.dashboard = data
      this.riskCount = data.risk_count || 0
    },
    async fetchStudents(params = {}) {
      const { data } = await api.get('/teacher/students', { params })
      this.studentList = data
    },
  },
})

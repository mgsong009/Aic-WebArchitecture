import { defineStore } from 'pinia'
import { getTeacherAssignments, getTeacherDashboard, getTeacherStudents } from '@/api'

export const useTeacherStore = defineStore('teacher', {
  state: () => ({
    dashboard: null,
    studentList: null,
    assignments: [],
    riskCount: 0,
  }),
  getters: {
    firstAssignmentId: (state) => state.assignments[0]?.id || null,
  },
  actions: {
    async fetchDashboard() {
      const data = await getTeacherDashboard()
      this.dashboard = data
      this.riskCount = data.risk_count || 0
    },
    async fetchStudents(params = {}) {
      this.studentList = await getTeacherStudents(params)
    },
    async fetchAssignments() {
      this.assignments = await getTeacherAssignments()
      return this.assignments
    },
  },
})

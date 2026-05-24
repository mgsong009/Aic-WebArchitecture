import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', component: () => import('@/views/LandingView.vue'), meta: { public: true } },
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  // Student routes
  { path: '/student/dashboard', component: () => import('@/views/student/StudentDashboardView.vue'), meta: { role: 'student' } },
  { path: '/student/assignments', component: () => import('@/views/student/StudentAssignmentsView.vue'), meta: { role: 'student' } },
  { path: '/student/assignments/:id', component: () => import('@/views/student/StudentAssignmentDetailView.vue'), meta: { role: 'student' } },
  { path: '/student/growth', component: () => import('@/views/student/StudentGrowthView.vue'), meta: { role: 'student' } },
  { path: '/student/feedback', component: () => import('@/views/student/StudentFeedbackView.vue'), meta: { role: 'student' } },
  { path: '/student/feedback/:assignmentId', component: () => import('@/views/student/StudentFeedbackView.vue'), meta: { role: 'student' } },
  // Teacher routes
  { path: '/teacher/dashboard', component: () => import('@/views/teacher/TeacherDashboardView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/students', component: () => import('@/views/teacher/TeacherStudentsView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/students/:id', component: () => import('@/views/teacher/TeacherStudentDetailView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/risk', component: () => import('@/views/teacher/TeacherRiskView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/analytics/assignment', component: () => import('@/views/teacher/TeacherAssignmentAnalyticsView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/analytics/assignment/:id', component: () => import('@/views/teacher/TeacherAssignmentAnalyticsView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/advanced', component: () => import('@/views/teacher/TeacherAdvancedView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/statistics', component: () => import('@/views/teacher/TeacherStatisticalValidationView.vue'), meta: { role: 'teacher' } },
  // Fallback
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
  if (to.meta.role && auth.user?.role !== to.meta.role) return '/login'
})

export default router

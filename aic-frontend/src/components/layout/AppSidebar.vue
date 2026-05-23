<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTeacherStore } from '@/stores/teacher'

defineProps({
  open: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const teacherStore = useTeacherStore()

const role = computed(() => auth.user?.role)
const studentNav = [
  { label: '대시보드', path: '/student/dashboard', icon: '▦' },
  { label: '과제 목록', path: '/student/assignments', icon: '□' },
  { label: '성장 분석', path: '/student/growth', icon: '↗' },
]
const teacherNav = [
  { label: '대시보드', path: '/teacher/dashboard', icon: '▦' },
  { label: '학생 목록', path: '/teacher/students', icon: '◎' },
  { label: '위험군 관리', path: '/teacher/risk', icon: '!' , badge: true },
  { label: '과제 분석', path: '/teacher/analytics/assignment/1', match: '/teacher/analytics/assignment', icon: '□' },
  { label: '심화 분석', path: '/teacher/advanced', icon: '◇' },
]
const navItems = computed(() => (role.value === 'teacher' ? teacherNav : studentNav))
const homePath = computed(() => (role.value === 'teacher' ? '/teacher/dashboard' : '/student/dashboard'))

function isActive(item) {
  return route.path === item.path || route.path.startsWith(item.match || `${item.path}/`)
}

function goHome() {
  router.push(homePath.value)
  emit('close')
}

async function handleLogout() {
  await auth.logout()
  emit('close')
  router.push('/login')
}
</script>

<template>
  <aside class="app-sidebar" :class="{ open }">
    <div class="sidebar-logo" @click="goHome">
      <span class="sidebar-logo-icon">AI</span>
      <span class="sidebar-logo-text">AIC <span>Index</span></span>
    </div>
    <div class="sidebar-role-badge">{{ role === 'teacher' ? 'Teacher Workspace' : 'Student Workspace' }}</div>
    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item) }"
        @click="emit('close')"
      >
        <span class="nav-item-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge && teacherStore.riskCount > 0" class="nav-badge">
          {{ teacherStore.riskCount }}
        </span>
      </RouterLink>
    </nav>
    <div class="sidebar-user">
      <div class="user-avatar">{{ (auth.user?.name || 'A').slice(0, 1) }}</div>
      <div class="user-info">
        <div class="user-name">{{ auth.user?.name || '사용자' }}</div>
        <div class="user-role">{{ role === 'teacher' ? '교사' : '학생' }}</div>
      </div>
      <button class="logout-btn" title="로그아웃" @click.stop="handleLogout">↪</button>
    </div>
  </aside>
</template>

<style scoped>
.nav-label {
  flex: 1;
}

.logout-btn {
  width: 30px;
  height: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.78);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  cursor: pointer;
  flex-shrink: 0;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>

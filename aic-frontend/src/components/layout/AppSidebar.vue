<script setup>
import { computed, onMounted } from 'vue'
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
  { label: 'Dashboard', path: '/student/dashboard', icon: '▦' },
  { label: 'Assignment Detail', path: '/student/assignments', icon: '▤' },
  { label: 'Growth Analysis', path: '/student/growth', icon: '↗' },
  { label: 'Feedback Guide', path: '/student/feedback', icon: '♧' },
]
const teacherNav = [
  { label: '대시보드', path: '/teacher/dashboard', icon: '▦' },
  { label: '학생 목록', path: '/teacher/students', icon: '◎' },
  { label: '위험군 관리', path: '/teacher/risk', icon: '!' , badge: true },
  { label: '과제 분석', path: '/teacher/analytics/assignment', dynamicPath: true, match: '/teacher/analytics/assignment', icon: '□' },
  { label: '심화 분석', path: '/teacher/advanced', icon: '◇' },
]
const navItems = computed(() => (role.value === 'teacher' ? teacherNav : studentNav))
const homePath = computed(() => (role.value === 'teacher' ? '/teacher/dashboard' : '/student/dashboard'))

onMounted(() => {
  if (role.value === 'teacher' && !teacherStore.assignments.length) {
    teacherStore.fetchAssignments().catch(() => {})
  }
})

function itemPath(item) {
  if (item.dynamicPath && teacherStore.firstAssignmentId) {
    return `/teacher/analytics/assignment/${teacherStore.firstAssignmentId}`
  }
  return item.path
}

function isActive(item) {
  const path = itemPath(item)
  return route.path === path || route.path.startsWith(item.match || `${path}/`)
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
      <span class="sidebar-logo-icon">AIC</span>
      <span class="sidebar-logo-text">AIC <span>Index</span></span>
    </div>
    <div class="sidebar-role-badge">{{ role === 'teacher' ? 'Teacher' : 'Student' }}</div>
    <nav class="sidebar-nav">
      <div class="nav-section-label">Navigation</div>
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="itemPath(item)"
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
        <div class="user-role">{{ role === 'teacher' ? 'Teacher' : `Student · ${auth.user?.class_code || 'CS101'}` }}</div>
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

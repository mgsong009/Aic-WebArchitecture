<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTeacherStore } from '@/stores/teacher'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const teacherStore = useTeacherStore()

const role = computed(() => auth.user?.role)
const studentNav = [
  { label: '대시보드', path: '/student/dashboard', icon: 'D' },
  { label: '과제 목록', path: '/student/assignments', icon: 'A' },
  { label: '성장 분석', path: '/student/growth', icon: 'G' },
]
const teacherNav = [
  { label: '대시보드', path: '/teacher/dashboard', icon: 'D' },
  { label: '학생 목록', path: '/teacher/students', icon: 'S' },
  { label: '위험군 관리', path: '/teacher/risk', icon: 'R', badge: true },
  { label: '과제 분석', path: '/teacher/analytics/assignment/1', icon: 'A' },
  { label: '심화 분석', path: '/teacher/advanced', icon: 'X' },
]
const navItems = computed(() => (role.value === 'teacher' ? teacherNav : studentNav))

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar" :class="role === 'teacher' ? 'sidebar--teacher' : ''">
    <div class="sidebar-logo">
      <span class="logo-text">AIC</span>
      <span class="logo-sub">Index Platform</span>
    </div>
    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: route.path.startsWith(item.path) }"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge && teacherStore.riskCount > 0" class="nav-badge">
          {{ teacherStore.riskCount }}
        </span>
      </RouterLink>
    </nav>
    <div class="sidebar-user">
      <div class="user-name">{{ auth.user?.name || '사용자' }}</div>
      <div class="user-role">{{ role === 'teacher' ? '교사' : '학생' }}</div>
      <button class="logout-btn" @click="handleLogout">로그아웃</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  min-height: 100vh;
  background: var(--color-aic);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar--teacher {
  background: #1a2438;
}

.sidebar-logo {
  padding: 0.5rem 0 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  margin-bottom: 1.5rem;
}

.logo-text {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: 0.1em;
}

.logo-sub {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-md);
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all 0.15s;
}

.nav-item:hover,
.nav-item.active {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.nav-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.35);
  display: grid;
  place-items: center;
  font-size: 0.7rem;
  font-weight: 700;
}

.nav-label {
  flex: 1;
}

.nav-badge {
  background: #ef4444;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 9999px;
  min-width: 18px;
  text-align: center;
}

.sidebar-user {
  padding-top: 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.user-name {
  font-weight: 600;
  color: #fff;
  font-size: var(--text-sm);
}

.user-role {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.75rem;
}

.logout-btn {
  width: 100%;
  padding: 0.45rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.85);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  cursor: pointer;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

@media (max-width: 1024px) {
  .sidebar {
    position: static;
    width: 100%;
    min-height: auto;
    border-radius: 0;
  }
}
</style>

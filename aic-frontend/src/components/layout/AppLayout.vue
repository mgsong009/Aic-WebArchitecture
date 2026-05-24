<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from './AppSidebar.vue'

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  showPageHeader: { type: Boolean, default: true },
})

const auth = useAuthStore()
const isSidebarOpen = ref(false)

const roleLabel = computed(() => {
  const r = auth.user?.role
  if (r === 'admin') return 'Admin'
  return r === 'teacher' ? 'Teacher' : 'Student'
})
const currentTitle = computed(() => props.title || 'AIC Index')
const searchPlaceholder = computed(() => (auth.user?.role === 'teacher' ? '학생 검색...' : '과제 검색...'))

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value
}

function closeSidebar() {
  isSidebarOpen.value = false
}

async function handleLogout() {
  await auth.logout()
  window.location.href = '/login'
}
</script>

<template>
  <div class="app-layout" :class="{ 'sidebar-open': isSidebarOpen }">
    <AppSidebar :open="isSidebarOpen" @close="closeSidebar" />
    <button
      v-if="isSidebarOpen"
      class="sidebar-backdrop"
      type="button"
      aria-label="사이드바 닫기"
      @click="closeSidebar"
    />
    <main class="app-main">
      <div class="app-header">
        <button
          class="mobile-menu-btn"
          type="button"
          :aria-expanded="isSidebarOpen"
          aria-label="메뉴 열기"
          @click="toggleSidebar"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <div class="header-breadcrumb">
          <span class="breadcrumb-item">{{ roleLabel }}</span>
          <span v-if="title" class="breadcrumb-sep">›</span>
          <span class="breadcrumb-item active">{{ currentTitle }}</span>
        </div>
        <div class="header-actions">
          <label class="header-search" for="layout-search">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input id="layout-search" type="search" :placeholder="searchPlaceholder" />
          </label>
          <button class="icon-btn" type="button" aria-label="알림">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <span class="badge"></span>
          </button>
          <button class="icon-btn" type="button" aria-label="로그아웃" @click="handleLogout">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16,17 21,12 16,7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </button>
          <slot name="actions" />
        </div>
      </div>
      <section class="page-content">
        <header v-if="title && showPageHeader" class="page-header">
          <div>
            <h1 class="page-title">{{ title }}</h1>
            <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
          </div>
        </header>
        <slot />
      </section>
    </main>
  </div>
</template>

<style scoped>
.mobile-menu-btn {
  display: none;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-full);
  background: var(--color-gray-100);
  color: var(--text-primary);
  flex-shrink: 0;
}

.mobile-menu-btn span {
  width: 16px;
  height: 2px;
  border-radius: var(--radius-full);
  background: currentColor;
}

.sidebar-backdrop {
  display: none;
}

.header-search {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: inline-flex;
  }

  .app-header {
    padding: 0 var(--space-4);
  }

  .header-breadcrumb {
    min-width: 0;
  }

  .breadcrumb-item:not(.active),
  .breadcrumb-sep {
    display: none;
  }

  .breadcrumb-item.active {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 90;
    background: rgba(17, 24, 39, 0.36);
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 920px) {
  .header-search {
    display: none;
  }
}
</style>

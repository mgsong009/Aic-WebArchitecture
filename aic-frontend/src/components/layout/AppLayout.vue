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

const roleLabel = computed(() => (auth.user?.role === 'teacher' ? 'Teacher' : 'Student'))
const currentTitle = computed(() => props.title || 'AIC Index')

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value
}

function closeSidebar() {
  isSidebarOpen.value = false
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
          <span class="breadcrumb-item">AIC Index</span>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-item">{{ roleLabel }}</span>
          <span v-if="title" class="breadcrumb-sep">/</span>
          <span class="breadcrumb-item active">{{ currentTitle }}</span>
        </div>
        <div class="header-actions">
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
</style>

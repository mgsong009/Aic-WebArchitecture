<script setup>
import AppSidebar from './AppSidebar.vue'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-content">
      <header v-if="title" class="page-header">
        <h1 class="page-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
      </header>
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-content {
  margin-left: 240px;
  flex: 1;
  padding: 2rem;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  margin-top: 0.25rem;
}

@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
    padding: 1.25rem;
  }
}
</style>

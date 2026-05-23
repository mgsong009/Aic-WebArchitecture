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
    <main class="app-main">
      <div class="app-header">
        <div class="header-breadcrumb">
          <span class="breadcrumb-item">AIC Index</span>
          <span v-if="title" class="breadcrumb-sep">/</span>
          <span v-if="title" class="breadcrumb-item active">{{ title }}</span>
        </div>
      </div>
      <section class="page-content">
        <header v-if="title" class="page-header">
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
@media (max-width: 1024px) {
  .app-main {
    margin-left: 0;
  }

  .app-header {
    display: none;
  }
}
</style>

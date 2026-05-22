<template>
  <div class="skeleton" :style="{ height }"></div>
</template>

<script setup>
defineProps({
  height: { type: String, default: '120px' },
})
</script>

<style scoped>
.skeleton {
  width: 100%;
  border-radius: var(--radius-lg);
  background: linear-gradient(90deg, #eef2f7 25%, #e4e9f1 50%, #eef2f7 75%);
  background-size: 200% 100%;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>

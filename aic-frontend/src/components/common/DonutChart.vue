<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: 0 },
  maxScore: { type: Number, default: 100 },
  color: { type: String, default: 'var(--color-aic)' },
  label: { type: String, default: '' },
  size: { type: Number, default: 120 },
})

const radius = computed(() => props.size / 2 - 10)
const circumference = computed(() => 2 * Math.PI * radius.value)
const dash = computed(() => (props.score / props.maxScore) * circumference.value)
const gap = computed(() => circumference.value - dash.value)
</script>

<template>
  <div class="donut-wrap" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- Track -->
      <circle
        :cx="size / 2" :cy="size / 2" :r="radius"
        fill="none" stroke="var(--color-gray-100)" :stroke-width="10"
      />
      <!-- Value arc -->
      <circle
        :cx="size / 2" :cy="size / 2" :r="radius"
        fill="none" :stroke="color" :stroke-width="10"
        stroke-linecap="round"
        :stroke-dasharray="`${dash} ${gap}`"
        stroke-dashoffset="0"
        transform-origin="center"
        :transform="`rotate(-90 ${size / 2} ${size / 2})`"
        style="transition: stroke-dasharray 0.6s ease"
      />
      <!-- Score text -->
      <text
        :x="size / 2" :y="size / 2 - 4"
        text-anchor="middle"
        font-size="22" font-weight="800"
        :fill="color"
      >{{ score }}</text>
      <text
        v-if="label"
        :x="size / 2" :y="size / 2 + 16"
        text-anchor="middle"
        font-size="10" font-weight="700"
        fill="var(--text-muted)"
      >{{ label }}</text>
    </svg>
  </div>
</template>

<style scoped>
.donut-wrap { position: relative; display: inline-flex; flex-direction: column; align-items: center; }
</style>

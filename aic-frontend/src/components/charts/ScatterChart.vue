<script setup>
import { computed, ref } from 'vue'
import { useChart } from '@/composables/useChart'

const props = defineProps({
  config: { type: Object, required: true },
})

const canvasRef = ref(null)
const chartConfig = computed(() => props.config)

useChart(canvasRef, chartConfig, [chartConfig])
</script>

<template>
  <canvas ref="canvasRef"></canvas>
</template>

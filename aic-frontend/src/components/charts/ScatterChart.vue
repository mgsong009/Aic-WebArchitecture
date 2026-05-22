<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  config: { type: Object, required: true },
})

const canvasRef = ref(null)
let chart = null

function build() {
  if (chart) chart.destroy()
  if (!canvasRef.value) return
  chart = new Chart(canvasRef.value, props.config)
}

onMounted(build)
watch(() => props.config, build, { deep: true })
onUnmounted(() => {
  if (chart) chart.destroy()
})
</script>

<template>
  <canvas ref="canvasRef"></canvas>
</template>

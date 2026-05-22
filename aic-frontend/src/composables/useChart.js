import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export function useChart(canvasRef, config, deps = []) {
  const chart = ref(null)

  function destroy() {
    if (chart.value) {
      chart.value.destroy()
      chart.value = null
    }
  }

  function build(cfg) {
    destroy()
    if (!canvasRef.value) return
    chart.value = new Chart(canvasRef.value, cfg)
  }

  onMounted(() => build(config.value || config))

  if (deps.length) {
    watch(deps, () => build(config.value || config), { deep: true })
  }

  onUnmounted(destroy)

  return { chart, build, destroy }
}

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const chartCanvasBackground = {
  id: 'chartCanvasBackground',
  beforeDraw(chart, _args, options) {
    const { ctx, width, height } = chart
    ctx.save()
    ctx.globalCompositeOperation = 'destination-over'
    ctx.fillStyle = options.color || '#fff'
    ctx.fillRect(0, 0, width, height)
    ctx.restore()
  },
}

Chart.register(chartCanvasBackground)

export function useChart(canvasRef, config, deps = []) {
  const chart = ref(null)

  function destroy() {
    if (chart.value) {
      chart.value.stop()
      chart.value.destroy()
      chart.value = null
    }
  }

  function build(cfg) {
    destroy()
    if (!canvasRef.value) return
    chart.value = new Chart(canvasRef.value, {
      ...cfg,
      options: {
        animation: false,
        ...(cfg.options || {}),
        plugins: {
          ...(cfg.options?.plugins || {}),
          chartCanvasBackground: cfg.options?.plugins?.chartCanvasBackground || { color: '#fff' },
        },
      },
    })
  }

  onMounted(() => build(config.value || config))

  if (deps.length) {
    watch(deps, () => build(config.value || config), { deep: true })
  }

  onUnmounted(destroy)

  return { chart, build, destroy }
}

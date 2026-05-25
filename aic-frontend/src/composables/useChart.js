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

function collectAxisValues(config) {
  const values = { x: [], y: [] }

  for (const dataset of config?.data?.datasets || []) {
    for (const point of dataset.data || []) {
      if (Array.isArray(point)) {
        for (const value of point) {
          const next = Number(value)
          if (Number.isFinite(next)) values.y.push(next)
        }
      } else if (point && typeof point === 'object') {
        const x = Number(point.x)
        const y = Number(point.y)
        if (Number.isFinite(x)) values.x.push(x)
        if (Number.isFinite(y)) values.y.push(y)
      } else {
        const next = Number(point)
        if (Number.isFinite(next)) values.y.push(next)
      }
    }
  }

  return values
}

function paddedBounds(values, fallbackSpan) {
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = Math.max(max - min, fallbackSpan)
  const padding = Math.max(span * 0.08, fallbackSpan * 0.02)
  return { min: min - padding, max: max + padding }
}

function withExpandedScales(cfg) {
  const scales = cfg?.options?.scales
  if (!scales) return cfg

  const values = collectAxisValues(cfg)
  const nextScales = { ...scales }
  let changed = false

  for (const axis of ['x', 'y']) {
    const scale = scales[axis]
    const axisValues = values[axis]
    if (!scale || !axisValues.length) continue

    const configuredMin = Number(scale.min)
    const configuredMax = Number(scale.max)
    if (!Number.isFinite(configuredMin) || !Number.isFinite(configuredMax)) continue

    const { min, max } = paddedBounds(axisValues, configuredMax - configuredMin || 10)
    const expandedMin = Math.min(configuredMin, min)
    const expandedMax = Math.max(configuredMax, max)

    if (expandedMin !== configuredMin || expandedMax !== configuredMax) {
      nextScales[axis] = { ...scale, min: expandedMin, max: expandedMax }
      changed = true
    }
  }

  if (!changed) return cfg
  return {
    ...cfg,
    options: {
      ...(cfg.options || {}),
      scales: nextScales,
    },
  }
}

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
    const nextCfg = withExpandedScales(cfg)
    chart.value = new Chart(canvasRef.value, {
      ...nextCfg,
      options: {
        animation: false,
        ...(nextCfg.options || {}),
        plugins: {
          ...(nextCfg.options?.plugins || {}),
          chartCanvasBackground: nextCfg.options?.plugins?.chartCanvasBackground || { color: '#fff' },
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

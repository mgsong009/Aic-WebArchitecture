import { ref } from 'vue'
import { api } from '@/api'

export function useJobPoller() {
  const status = ref('idle')
  const metrics = ref(null)
  const error = ref(null)
  let intervalId = null

  async function startPolling(jobId) {
    status.value = 'pending'
    metrics.value = null
    error.value = null

    intervalId = setInterval(async () => {
      try {
        const { data } = await api.get(`/jobs/${jobId}/status`)
        status.value = data.status
        if (data.status === 'done') {
          metrics.value = data.metrics
          clearInterval(intervalId)
        } else if (data.status === 'failed') {
          error.value = data.error || '분석 실패'
          clearInterval(intervalId)
        }
      } catch {
        clearInterval(intervalId)
        status.value = 'failed'
        error.value = '네트워크 오류'
      }
    }, 3000)
  }

  function stop() {
    if (intervalId) clearInterval(intervalId)
  }

  return { status, metrics, error, startPolling, stop }
}

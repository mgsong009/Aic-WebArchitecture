import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use((cfg) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    cfg.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return cfg
})

let refreshing = false
let refreshPromise = null

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status !== 401) {
      return Promise.reject(err)
    }

    const original = err.config || {}
    const isRefreshRequest = (original.url || '').includes('/auth/refresh')
    if (original._retry || isRefreshRequest) {
      const auth = useAuthStore()
      await auth.logout()
      window.location.href = '/login'
      return Promise.reject(err)
    }

    try {
      if (!refreshPromise) {
        refreshing = true
        const auth = useAuthStore()
        refreshPromise = auth.refresh().then(() => auth.accessToken).finally(() => {
          refreshing = false
          refreshPromise = null
        })
      }

      const token = await refreshPromise
      const retryConfig = {
        ...original,
        _retry: true,
        headers: {
          ...(original.headers || {}),
          Authorization: `Bearer ${token}`,
        },
      }
      return api(retryConfig)
    } catch (refreshErr) {
      const auth = useAuthStore()
      await auth.logout()
      window.location.href = '/login'
      return Promise.reject(refreshErr)
    }
  }
)

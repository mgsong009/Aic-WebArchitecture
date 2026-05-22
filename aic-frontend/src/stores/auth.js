import { defineStore } from 'pinia'
import { api } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,        // { id, name, role, class_code }
    accessToken: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.accessToken,
  },
  actions: {
    async login(userId, password, role) {
      const { data } = await api.post('/auth/login', { user_id: userId, password, role })
      this.accessToken = data.access_token
      this.user = data.user
    },
    async refresh() {
      const { data } = await api.post('/auth/refresh')
      this.accessToken = data.access_token
    },
    async logout() {
      try {
        await api.post('/auth/logout')
      } catch {}
      this.accessToken = null
      this.user = null
    },
  },
  persist: true,
})

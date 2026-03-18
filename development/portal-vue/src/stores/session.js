import { defineStore } from 'pinia'

export const useSessionStore = defineStore('session', {
  state: () => ({
    logged_user: null,
    full_name: '',
    user_image: '',
    roles: [],
    allowed_modules: [],
    loaded: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.logged_user && state.logged_user !== 'Guest',
    hasRole: (state) => (role) => state.roles.includes(role),
    hasAnyRole: (state) => (roleList) => roleList.some((r) => state.roles.includes(r)),
  },

  actions: {
    async fetchSession() {
      try {
        const res = await fetch(
          '/api/method/university_erp.university_portals.api.portal_api.get_session_info',
          { headers: { Accept: 'application/json', 'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '' } }
        )
        if (res.status === 401 || res.status === 403) {
          this.loaded = true
          return
        }
        const data = await res.json()
        const info = data.message || {}
        this.logged_user = info.logged_user || null
        this.full_name = info.full_name || ''
        this.user_image = info.user_image || ''
        this.roles = info.roles || []
        this.allowed_modules = info.allowed_modules || []
      } catch (err) {
        this.error = err.message
      } finally {
        this.loaded = true
      }
    },

    reset() {
      this.logged_user = null
      this.full_name = ''
      this.user_image = ''
      this.roles = []
      this.allowed_modules = []
      this.loaded = false
      this.error = null
    },
  },
})

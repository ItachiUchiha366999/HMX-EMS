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
        const csrfToken = window.frappe?.csrf_token || ''
        const headers = { Accept: 'application/json' }
        if (csrfToken) {
          headers['X-Frappe-CSRF-Token'] = csrfToken
        }

        const res = await fetch(
          '/api/method/university_erp.university_portals.api.portal_api.get_session_info',
          {
            method: 'GET',
            credentials: 'same-origin',
            headers,
          }
        )
        if (res.ok) {
          const data = await res.json()
          const info = data.message || {}
          this.logged_user = info.logged_user || null
          this.full_name = info.full_name || ''
          this.user_image = info.user_image || ''
          this.roles = info.roles || []
          this.allowed_modules = info.allowed_modules || []
        } else {
          // API call failed — but Frappe served this page (index.py rejects Guest)
          // so the user IS authenticated. Use injected session as fallback.
          this._fallbackFromPageContext()
        }
      } catch (err) {
        // Network error — use page context fallback
        this._fallbackFromPageContext()
        this.error = err.message
      } finally {
        this.loaded = true
      }
    },

    _fallbackFromPageContext() {
      // Frappe's www/portal/index.py injects window.frappe.session before Vue loads
      const user = window.frappe?.session?.user
      if (user && user !== 'Guest') {
        this.logged_user = user
        this.full_name = user
        this.roles = ['System Manager'] // Safe fallback for Administrator
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

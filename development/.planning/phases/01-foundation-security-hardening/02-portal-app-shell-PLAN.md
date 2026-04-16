---
phase: 01-foundation-security-hardening
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - portal-vue/package.json
  - portal-vue/index.html
  - portal-vue/vite.config.js
  - portal-vue/src/main.js
  - portal-vue/src/App.vue
  - portal-vue/src/stores/session.js
  - portal-vue/src/router/index.js
  - portal-vue/src/config/navigation.js
  - portal-vue/src/layouts/PortalLayout.vue
  - portal-vue/src/components/Sidebar.vue
  - frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py
  - frappe-bench/apps/university_erp/university_erp/www/portal/index.py
  - frappe-bench/apps/university_erp/university_erp/www/portal/index.html
autonomous: true
requirements:
  - FOUND-05
  - FOUND-06
  - FOUND-07
  - FOUND-08

must_haves:
  truths:
    - "A standalone portal-vue/ Vite project exists at /workspace/development/portal-vue/ and can be built with npm run build"
    - "Pinia session store fetches {logged_user, full_name, user_image, roles[], allowed_modules[]} in a single API call on app boot"
    - "Router beforeEach guard checks session store — no per-route frappe.auth.get_logged_user API call"
    - "Sidebar renders only items whose roles[] array intersects the user's active roles"
    - "Visiting /portal/ as Guest redirects to /login?redirect-to=/portal/"
    - "get_session_info() backend endpoint exists and returns user info + roles + allowed_modules"
  artifacts:
    - path: "portal-vue/src/stores/session.js"
      provides: "Pinia session store with fetchSession() action"
      exports: ["useSessionStore"]
    - path: "portal-vue/src/router/index.js"
      provides: "Vue Router with beforeEach guard using session store"
      contains: "useSessionStore"
    - path: "portal-vue/src/config/navigation.js"
      provides: "Role-to-route mapping config array"
      exports: ["navItems"]
    - path: "portal-vue/src/components/Sidebar.vue"
      provides: "Sidebar with role-filtered navigation items"
      contains: "roles"
    - path: "frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py"
      provides: "get_session_info() whitelisted endpoint"
      exports: ["get_session_info"]
    - path: "frappe-bench/apps/university_erp/university_erp/www/portal/index.py"
      provides: "Frappe www page SPA shell for /portal/"
      contains: "get_context"
    - path: "frappe-bench/apps/university_erp/university_erp/www/portal/index.html"
      provides: "HTML SPA shell loading Vite assets"
      contains: "vue_js"
  key_links:
    - from: "portal-vue/src/main.js"
      to: "session store fetchSession()"
      via: "await sessionStore.fetchSession() before router.isReady()"
      pattern: "fetchSession"
    - from: "portal-vue/src/router/index.js beforeEach"
      to: "session store isAuthenticated"
      via: "sessionStore.isAuthenticated check, redirect to /login if false"
      pattern: "isAuthenticated"
    - from: "portal-vue/src/components/Sidebar.vue"
      to: "navigation.js navItems"
      via: "computed filter: item.roles.some(r => sessionStore.roles.includes(r))"
      pattern: "navItems"
    - from: "frappe-bench/apps/university_erp/university_erp/www/portal/index.py"
      to: "public/portal/.vite/manifest.json"
      via: "get_vite_manifest() reads manifest, passes vue_js and vue_css to template context"
      pattern: "manifest"
---

<objective>
Build the standalone portal-vue/ Vite project that serves as the unified portal app shell. This includes the Pinia session store (one-time boot fetch), Vue Router with role-aware guard, sidebar with role-filtered navigation, and the Frappe www page that mounts the SPA at /portal/.

Purpose: Every subsequent portal module (faculty, management, parent, HOD) will be a Vue route inside this shell. This plan builds the container — no module-specific views, only the infrastructure that module plans will drop views into.

Output:
- portal-vue/ project (buildable with npm run build)
- get_session_info() backend endpoint in portal_api.py
- www/portal/index.py and index.html (SPA mount point for Frappe)
</objective>

<execution_context>
@/workspace/development/.claude/get-shit-done/workflows/execute-plan.md
@/workspace/development/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/workspace/development/.planning/ROADMAP.md
@/workspace/development/.planning/REQUIREMENTS.md
@/workspace/development/.planning/phases/01-foundation-security-hardening/01-CONTEXT.md
@/workspace/development/.planning/phases/01-foundation-security-hardening/01-RESEARCH.md

<interfaces>
<!-- Patterns to replicate — confirmed from direct code inspection -->

From student-portal-vue/vite.config.js (template to adapt):
```javascript
export default defineConfig({
  plugins: [vue()],
  base: '/assets/university_erp/student-portal-spa/',
  build: {
    outDir: path.resolve(__dirname, '../frappe-bench/apps/university_erp/university_erp/public/student-portal-spa'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: { input: path.resolve(__dirname, 'index.html') },
  },
})
// For portal-vue: base = '/assets/university_erp/portal/'
// For portal-vue: outDir = '../frappe-bench/apps/university_erp/university_erp/public/portal'
```

From www/student_portal/index.py (exact pattern to replicate for /portal/):
```python
def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to=/portal{frappe.local.request.path.replace('/portal', '') or '/'}"
        )
        raise frappe.Redirect
    context.no_cache = 1
    context.show_sidebar = False
    manifest = get_vite_manifest()
    context.vue_js = manifest.get("js", "")
    context.vue_css = manifest.get("css", "")
    return context

def get_vite_manifest():
    manifest_path = frappe.get_app_path("university_erp", "public", "portal", ".vite", "manifest.json")
    # ... same pattern, but with "portal" instead of "student-portal-spa"
    base = "/assets/university_erp/portal/"
```

From www/student_portal/index.html (exact template to adapt):
```html
<!-- Use same spinner CSS, same #app div, same Jinja conditionals -->
<!-- Change title to "University Portal | EduPortal" -->
<!-- Change fallback message to refer to portal-vue/ directory -->
```

From student-portal-vue/src/router/index.js (the anti-pattern to replace):
```javascript
// OLD: per-route API call — DO NOT replicate
router.beforeEach(async (to) => {
  const res = await fetch('/api/method/frappe.auth.get_logged_user', ...)
  // This fires on EVERY route change
})
// NEW: check Pinia store which was populated once at boot
router.beforeEach((to) => {
  const sessionStore = useSessionStore()
  if (!sessionStore.isAuthenticated) {
    window.location.href = `/login?redirect-to=/portal${to.fullPath}`
    return false
  }
})
```

From university_portals/api/portal_api.py (whitelisted endpoint pattern):
```python
@frappe.whitelist()
def get_session_info():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(frappe._("Not logged in"), frappe.AuthenticationError)
    # return user info + roles + allowed_modules
```

Roles known to exist (from fixtures/role.json + new additions from Plan 01):
- University Admin, University Registrar, University Finance, University HR Admin,
  University HOD, University Exam Cell, University Faculty, University Student,
  University Librarian, University Warden, University Placement Officer,
  University VC, University Dean

Student-portal-vue uses student-portal-spa as build target — portal-vue MUST use a DIFFERENT
output directory. Do NOT write to student-portal-spa/.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Scaffold portal-vue/ project and backend get_session_info() endpoint</name>
  <files>
    portal-vue/package.json,
    portal-vue/index.html,
    portal-vue/vite.config.js,
    portal-vue/src/main.js,
    portal-vue/src/App.vue,
    portal-vue/src/stores/session.js,
    portal-vue/src/config/navigation.js,
    frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py
  </files>
  <action>
    All files are created at `/workspace/development/portal-vue/` (sibling of `student-portal-vue/`).

    ---

    **portal-vue/package.json:**
    ```json
    {
      "name": "portal-vue",
      "version": "0.1.0",
      "private": true,
      "scripts": {
        "dev": "vite",
        "build": "vite build",
        "preview": "vite preview"
      },
      "dependencies": {
        "pinia": "^2.1.7",
        "vue": "^3.4.0",
        "vue-router": "^4.3.0"
      },
      "devDependencies": {
        "@vitejs/plugin-vue": "^5.0.0",
        "vite": "^5.0.0"
      }
    }
    ```

    **portal-vue/index.html:**
    Standard Vite entry point:
    ```html
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>University Portal</title>
      </head>
      <body>
        <div id="app"></div>
        <script type="module" src="/src/main.js"></script>
      </body>
    </html>
    ```

    **portal-vue/vite.config.js:**
    ```javascript
    import { defineConfig } from 'vite'
    import vue from '@vitejs/plugin-vue'
    import path from 'path'

    export default defineConfig({
      plugins: [vue()],
      base: '/assets/university_erp/portal/',
      build: {
        outDir: path.resolve(__dirname, '../frappe-bench/apps/university_erp/university_erp/public/portal'),
        emptyOutDir: true,
        manifest: true,
        rollupOptions: {
          input: path.resolve(__dirname, 'index.html'),
        },
      },
    })
    ```

    **portal-vue/src/stores/session.js:**

    Flat Pinia store (not module split — simpler for a single-concern store):
    ```javascript
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
              { headers: { Accept: 'application/json', 'X-Frappe-CSRF-Token': frappe?.csrf_token || '' } }
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
    ```

    Note: `frappe?.csrf_token` references the global `frappe` object that Frappe injects into every www page. The Vite dev server won't have it, but production builds served by Frappe will.

    **portal-vue/src/config/navigation.js:**

    Config array driving sidebar items. Each item has `roles[]` — if the user holds ANY of those roles, the item is visible. Phase 3–6 will add entries to this file; for now, include placeholder routes for all personas.

    ```javascript
    /**
     * Portal navigation configuration.
     * Each item:
     *   - path: Vue Router route path
     *   - label: Display name
     *   - icon: Material Symbols icon name (or any icon identifier)
     *   - roles: Frappe roles that grant access to this item
     *
     * Multi-role users see the UNION of all items their roles permit.
     * This file is the single source of truth for sidebar items AND route meta.
     */
    export const navItems = [
      // Management
      {
        path: '/management',
        label: 'Management Dashboard',
        icon: 'dashboard',
        roles: ['University Admin', 'University VC', 'University Dean', 'University Registrar'],
      },
      // Faculty
      {
        path: '/faculty',
        label: 'My Teaching',
        icon: 'school',
        roles: ['University Faculty', 'University HOD'],
      },
      {
        path: '/faculty/attendance',
        label: 'Mark Attendance',
        icon: 'fact_check',
        roles: ['University Faculty', 'University HOD'],
      },
      {
        path: '/faculty/grades',
        label: 'Enter Grades',
        icon: 'grade',
        roles: ['University Faculty', 'University HOD'],
      },
      // HOD
      {
        path: '/hod',
        label: 'Department Overview',
        icon: 'corporate_fare',
        roles: ['University HOD'],
      },
      // Student
      {
        path: '/student',
        label: 'My Dashboard',
        icon: 'home',
        roles: ['University Student'],
      },
      // Finance
      {
        path: '/finance',
        label: 'Finance',
        icon: 'account_balance',
        roles: ['University Finance', 'University Admin'],
      },
      // Admin
      {
        path: '/admin/health',
        label: 'System Health',
        icon: 'monitor_heart',
        roles: ['University Admin'],
      },
    ]
    ```

    **portal-vue/src/App.vue:**

    Minimal root component — router-view is the only content:
    ```vue
    <template>
      <RouterView />
    </template>

    <script setup>
    import { RouterView } from 'vue-router'
    </script>
    ```

    **portal-vue/src/main.js:**

    Initializes Pinia, fetches session once, then mounts. The router's beforeEach guard reads from the already-populated store:
    ```javascript
    import { createApp } from 'vue'
    import { createPinia } from 'pinia'
    import App from './App.vue'
    import router from './router/index.js'
    import { useSessionStore } from './stores/session.js'

    const app = createApp(App)
    const pinia = createPinia()

    app.use(pinia)
    app.use(router)

    // One-time boot fetch — populate session store before first route render
    const sessionStore = useSessionStore()
    sessionStore.fetchSession().then(() => {
      app.mount('#app')
    })
    ```

    ---

    **frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py — APPEND get_session_info() to end of file:**

    Do NOT overwrite the existing file. Read it first, then append this function after the last existing function:

    ```python

    # ==================== Unified Portal APIs ====================

    @frappe.whitelist()
    def get_session_info():
        """
        Get current session info for the unified portal app shell.

        Called once at boot by the Pinia session store (portal-vue/src/stores/session.js).
        Returns user identity, roles, and allowed modules in a single response.

        Returns:
            dict: {logged_user, full_name, user_image, roles[], allowed_modules[]}
        """
        user = frappe.session.user
        if not user or user == "Guest":
            frappe.throw(frappe._("Not logged in"), frappe.AuthenticationError)

        user_doc = frappe.db.get_value(
            "User",
            user,
            ["full_name", "user_image"],
            as_dict=True,
        ) or {}

        roles = frappe.get_roles(user)

        # Determine allowed portal modules based on roles held
        # This list grows as Phase 3–6 add new portal modules
        module_role_map = {
            "management": ["University Admin", "University VC", "University Dean", "University Registrar"],
            "faculty": ["University Faculty", "University HOD"],
            "hod": ["University HOD"],
            "student": ["University Student"],
            "finance": ["University Finance", "University Admin"],
        }
        allowed_modules = [
            module for module, required_roles in module_role_map.items()
            if any(r in roles for r in required_roles)
        ]

        return {
            "logged_user": user,
            "full_name": user_doc.get("full_name", ""),
            "user_image": user_doc.get("user_image", ""),
            "roles": roles,
            "allowed_modules": allowed_modules,
        }
    ```
  </action>
  <verify>
    <automated>cd /workspace/development && python -c "
import os, json

# Verify project structure
assert os.path.exists('portal-vue/package.json'), 'package.json missing'
assert os.path.exists('portal-vue/vite.config.js'), 'vite.config.js missing'
assert os.path.exists('portal-vue/index.html'), 'index.html missing'
assert os.path.exists('portal-vue/src/main.js'), 'main.js missing'
assert os.path.exists('portal-vue/src/App.vue'), 'App.vue missing'
assert os.path.exists('portal-vue/src/stores/session.js'), 'session.js missing'
assert os.path.exists('portal-vue/src/config/navigation.js'), 'navigation.js missing'

# Verify vite.config.js targets the correct output directory
with open('portal-vue/vite.config.js') as f: vc = f.read()
assert 'portal' in vc and 'student-portal-spa' not in vc, 'vite.config.js targets wrong outDir'
assert \"base: '/assets/university_erp/portal/'\" in vc, 'Wrong base URL in vite.config.js'

# Verify session store has required fields
with open('portal-vue/src/stores/session.js') as f: ss = f.read()
assert 'fetchSession' in ss, 'fetchSession action missing'
assert 'isAuthenticated' in ss, 'isAuthenticated getter missing'
assert 'roles' in ss, 'roles field missing from store'
assert 'allowed_modules' in ss, 'allowed_modules field missing from store'

# Verify navigation config
with open('portal-vue/src/config/navigation.js') as f: nc = f.read()
assert 'navItems' in nc, 'navItems export missing'
assert 'roles' in nc, 'roles arrays missing from navigation config'

# Verify backend endpoint
with open('frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py') as f: api = f.read()
assert 'get_session_info' in api, 'get_session_info missing from portal_api.py'
assert 'allowed_modules' in api, 'allowed_modules missing from get_session_info'
assert 'frappe.get_roles' in api, 'frappe.get_roles call missing'
print('PASS: portal-vue scaffold and backend endpoint verified')
"
    </automated>
  </verify>
  <done>
    - portal-vue/ directory exists with package.json, index.html, vite.config.js
    - vite.config.js: base='/assets/university_erp/portal/', outDir points to public/portal/
    - session.js Pinia store has: state (logged_user, full_name, user_image, roles, allowed_modules, loaded, error), getters (isAuthenticated, hasRole, hasAnyRole), actions (fetchSession, reset)
    - navigation.js exports navItems array with path/label/icon/roles for all planned personas
    - App.vue renders RouterView only
    - main.js: creates pinia, calls fetchSession() before mount
    - get_session_info() appended to portal_api.py, returns {logged_user, full_name, user_image, roles[], allowed_modules[]}
  </done>
</task>

<task type="auto">
  <name>Task 2: Vue Router, PortalLayout, Sidebar, and Frappe www page</name>
  <files>
    portal-vue/src/router/index.js,
    portal-vue/src/layouts/PortalLayout.vue,
    portal-vue/src/components/Sidebar.vue,
    frappe-bench/apps/university_erp/university_erp/www/portal/index.py,
    frappe-bench/apps/university_erp/university_erp/www/portal/index.html
  </files>
  <action>
    **portal-vue/src/router/index.js:**

    The beforeEach guard reads from the already-populated Pinia store (populated in main.js before mount). No per-route API call.

    ```javascript
    import { createRouter, createWebHistory } from 'vue-router'
    import { useSessionStore } from '../stores/session.js'
    import { navItems } from '../config/navigation.js'
    import PortalLayout from '../layouts/PortalLayout.vue'

    // Placeholder views — Phases 3–6 replace these with real implementations
    const NotFound = { template: '<div style="padding:2rem"><h2>Page Not Found</h2></div>' }
    const ComingSoon = {
      props: ['moduleName'],
      template: '<div style="padding:2rem"><h2>{{ moduleName || \'Module\' }}</h2><p style="color:#64748b">Coming in a future phase.</p></div>',
    }

    const routes = [
      {
        path: '/',
        component: PortalLayout,
        children: [
          // Default redirect based on roles — handled in PortalLayout's onMounted
          { path: '', name: 'home', component: ComingSoon, props: { moduleName: 'Dashboard' } },
          { path: 'management', name: 'management', component: ComingSoon, props: { moduleName: 'Management Dashboard' } },
          { path: 'faculty', name: 'faculty', component: ComingSoon, props: { moduleName: 'My Teaching' } },
          { path: 'faculty/attendance', name: 'faculty-attendance', component: ComingSoon, props: { moduleName: 'Mark Attendance' } },
          { path: 'faculty/grades', name: 'faculty-grades', component: ComingSoon, props: { moduleName: 'Enter Grades' } },
          { path: 'hod', name: 'hod', component: ComingSoon, props: { moduleName: 'Department Overview' } },
          { path: 'student', name: 'student', component: ComingSoon, props: { moduleName: 'My Dashboard' } },
          { path: 'finance', name: 'finance', component: ComingSoon, props: { moduleName: 'Finance' } },
          { path: 'admin/health', name: 'admin-health', component: ComingSoon, props: { moduleName: 'System Health' } },
        ],
      },
      { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound },
    ]

    const router = createRouter({
      history: createWebHistory('/portal/'),
      routes,
    })

    // Auth guard — reads from Pinia store populated at boot (no API call)
    router.beforeEach((to) => {
      const sessionStore = useSessionStore()

      // If session hasn't loaded yet (edge case), allow — fetchSession already ran before mount
      if (!sessionStore.loaded) return true

      if (!sessionStore.isAuthenticated) {
        // Redirect to Frappe login, passing the intended destination
        window.location.href = `/login?redirect-to=/portal${to.fullPath}`
        return false
      }

      return true
    })

    export default router
    ```

    ---

    **portal-vue/src/layouts/PortalLayout.vue:**

    Shell layout: sidebar on the left, main content area (router-view) on the right. Minimal styling using inline styles — no external CSS framework dependency in this phase.

    ```vue
    <template>
      <div class="portal-shell">
        <Sidebar />
        <main class="portal-main">
          <RouterView />
        </main>
      </div>
    </template>

    <script setup>
    import { RouterView } from 'vue-router'
    import Sidebar from '../components/Sidebar.vue'
    </script>

    <style scoped>
    .portal-shell {
      display: flex;
      height: 100vh;
      overflow: hidden;
      font-family: 'Lexend', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #f8fafc;
    }

    .portal-main {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem 2rem;
    }
    </style>
    ```

    ---

    **portal-vue/src/components/Sidebar.vue:**

    Sidebar renders only the navigation items whose `roles[]` array intersects the current user's roles. Multi-role users see the union of all permitted items — no switcher, no priority. Active route item is highlighted.

    ```vue
    <template>
      <aside class="portal-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-logo">EduPortal</span>
        </div>

        <div class="sidebar-user">
          <img
            v-if="session.user_image"
            :src="session.user_image"
            class="user-avatar"
            alt="User"
          />
          <div v-else class="user-avatar user-avatar--placeholder">
            {{ initials }}
          </div>
          <div class="user-info">
            <span class="user-name">{{ session.full_name || session.logged_user }}</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <RouterLink
            v-for="item in visibleItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            active-class="nav-item--active"
          >
            <span class="nav-icon material-symbols-outlined">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </RouterLink>
        </nav>

        <div class="sidebar-footer">
          <a href="/logout" class="nav-item nav-item--logout">
            <span class="nav-icon material-symbols-outlined">logout</span>
            <span class="nav-label">Sign out</span>
          </a>
        </div>
      </aside>
    </template>

    <script setup>
    import { computed } from 'vue'
    import { RouterLink } from 'vue-router'
    import { useSessionStore } from '../stores/session.js'
    import { navItems } from '../config/navigation.js'

    const session = useSessionStore()

    // Show only items where the user holds at least one of the required roles
    const visibleItems = computed(() =>
      navItems.filter((item) =>
        item.roles.some((role) => session.roles.includes(role))
      )
    )

    const initials = computed(() => {
      const name = session.full_name || session.logged_user || '?'
      return name
        .split(' ')
        .slice(0, 2)
        .map((w) => w[0]?.toUpperCase() ?? '')
        .join('')
    })
    </script>

    <style scoped>
    .portal-sidebar {
      width: 240px;
      min-width: 240px;
      background: #0f172a;
      color: #e2e8f0;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
    }

    .sidebar-header {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid #1e293b;
    }

    .sidebar-logo {
      font-size: 1.1rem;
      font-weight: 700;
      color: #fff;
      letter-spacing: -0.02em;
    }

    .sidebar-user {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem 1.5rem;
      border-bottom: 1px solid #1e293b;
    }

    .user-avatar {
      width: 2rem;
      height: 2rem;
      border-radius: 50%;
      object-fit: cover;
    }

    .user-avatar--placeholder {
      background: #334155;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 600;
      color: #94a3b8;
    }

    .user-name {
      font-size: 0.85rem;
      font-weight: 500;
      color: #f1f5f9;
    }

    .sidebar-nav {
      flex: 1;
      padding: 0.5rem 0;
    }

    .sidebar-footer {
      padding: 0.5rem 0;
      border-top: 1px solid #1e293b;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.625rem 1.5rem;
      color: #94a3b8;
      text-decoration: none;
      font-size: 0.875rem;
      transition: background 0.15s, color 0.15s;
      border-radius: 0;
    }

    .nav-item:hover {
      background: #1e293b;
      color: #f1f5f9;
    }

    .nav-item--active {
      background: #1e3a8a;
      color: #fff;
    }

    .nav-item--logout {
      color: #64748b;
    }

    .nav-item--logout:hover {
      background: #1e293b;
      color: #f87171;
    }

    .nav-icon {
      font-size: 1.25rem;
      flex-shrink: 0;
    }
    </style>
    ```

    ---

    **frappe-bench/apps/university_erp/university_erp/www/portal/index.py (NEW FILE):**

    Create the `www/portal/` directory and this file. Mirrors www/student_portal/index.py exactly, adapted for the portal build output path.

    ```python
    # Copyright (c) 2026, University and contributors
    # For license information, please see license.txt

    import json
    import os

    import frappe
    from frappe import _


    def get_context(context):
        """SPA shell for the unified Vue 3 Portal — serves all roles at /portal/"""
        if frappe.session.user == "Guest":
            frappe.local.flags.redirect_location = (
                f"/login?redirect-to=/portal{frappe.local.request.path.replace('/portal', '') or '/'}"
            )
            raise frappe.Redirect

        context.no_cache = 1
        context.show_sidebar = False

        # Read Vite manifest to get hashed asset filenames
        manifest = get_vite_manifest()
        context.vue_js = manifest.get("js", "")
        context.vue_css = manifest.get("css", "")

        return context


    def get_vite_manifest():
        """Read the Vite build manifest to get hashed filenames for the unified portal."""
        manifest_path = frappe.get_app_path(
            "university_erp", "public", "portal", ".vite", "manifest.json"
        )

        if not os.path.exists(manifest_path):
            frappe.log_error(
                "Portal Vite manifest not found. Run: cd portal-vue && npm install && npm run build",
                "Portal Setup"
            )
            return {"js": "", "css": ""}

        with open(manifest_path) as f:
            manifest = json.load(f)

        entry = manifest.get("index.html", {})
        base = "/assets/university_erp/portal/"

        result = {
            "js": base + entry.get("file", "") if entry.get("file") else "",
            "css": "",
        }

        css_files = entry.get("css", [])
        if css_files:
            result["css"] = base + css_files[0]

        return result
    ```

    ---

    **frappe-bench/apps/university_erp/university_erp/www/portal/index.html (NEW FILE):**

    Adapt from www/student_portal/index.html with portal-specific content:

    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>University Portal | EduPortal</title>

        <!-- Fonts — same as student portal for consistency -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">

        {% if vue_css %}
        <link rel="stylesheet" href="{{ vue_css }}">
        {% endif %}

        <style>
            /* Loading spinner before Vue mounts */
            body { margin: 0; }
            #app:empty {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                background: #f8fafc;
                font-family: 'Lexend', sans-serif;
            }
            #app:empty::after {
                content: '';
                width: 32px;
                height: 32px;
                border: 3px solid #e2e8f0;
                border-top-color: #135bec;
                border-radius: 50%;
                animation: spin 0.6s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
            @media (prefers-color-scheme: dark) {
                #app:empty { background: #0d121b; }
                #app:empty::after { border-color: #334155; border-top-color: #135bec; }
            }
        </style>
    </head>
    <body>
        <div id="app"></div>

        {% if vue_js %}
        <script type="module" src="{{ vue_js }}"></script>
        {% else %}
        <script>
            document.getElementById('app').innerHTML = '<div style="text-align:center;padding:80px 20px;font-family:Lexend,sans-serif;color:#64748b;"><h2 style="color:#0f172a;">University Portal</h2><p>Build assets not found. Please run <code>cd portal-vue && npm install && npm run build</code></p></div>';
        </script>
        {% endif %}
    </body>
    </html>
    ```
  </action>
  <verify>
    <automated>cd /workspace/development && python -c "
import os

# Verify router
with open('portal-vue/src/router/index.js') as f: router = f.read()
assert 'useSessionStore' in router, 'Router does not import useSessionStore'
assert 'frappe.auth.get_logged_user' not in router, 'Old per-route auth pattern still present'
assert 'isAuthenticated' in router, 'isAuthenticated check missing from beforeEach'
assert \"createWebHistory('/portal/')\" in router, 'Wrong history base in router'

# Verify PortalLayout
assert os.path.exists('portal-vue/src/layouts/PortalLayout.vue'), 'PortalLayout.vue missing'
with open('portal-vue/src/layouts/PortalLayout.vue') as f: layout = f.read()
assert 'Sidebar' in layout, 'Sidebar not included in PortalLayout'
assert 'RouterView' in layout, 'RouterView missing from PortalLayout'

# Verify Sidebar
with open('portal-vue/src/components/Sidebar.vue') as f: sidebar = f.read()
assert 'visibleItems' in sidebar, 'visibleItems computed missing'
assert 'navItems' in sidebar, 'navItems import missing'
assert 'session.roles' in sidebar or 'roles' in sidebar, 'roles check missing from Sidebar'

# Verify Frappe www page
assert os.path.exists('frappe-bench/apps/university_erp/university_erp/www/portal/index.py'), 'www/portal/index.py missing'
assert os.path.exists('frappe-bench/apps/university_erp/university_erp/www/portal/index.html'), 'www/portal/index.html missing'

with open('frappe-bench/apps/university_erp/university_erp/www/portal/index.py') as f: ip = f.read()
assert 'get_context' in ip, 'get_context missing from www/portal/index.py'
assert 'frappe.Redirect' in ip, 'Guest redirect missing from index.py'
assert 'get_vite_manifest' in ip, 'get_vite_manifest missing from index.py'
assert \"public\", \"portal\"\" in ip or 'portal' in ip, 'Wrong manifest path'

with open('frappe-bench/apps/university_erp/university_erp/www/portal/index.html') as f: ih = f.read()
assert 'vue_js' in ih, 'vue_js template variable missing'
assert '#app' in ih, '#app mount point missing'
print('PASS: Router, layout, sidebar, and www page verified')
"
    </automated>
  </verify>
  <done>
    - router/index.js: createWebHistory('/portal/'), beforeEach reads sessionStore.isAuthenticated (no API call)
    - PortalLayout.vue: flex layout with Sidebar + RouterView
    - Sidebar.vue: visibleItems computed = navItems filtered by session.roles intersection
    - www/portal/index.py: get_context() redirects Guest, reads Vite manifest, sets vue_js/vue_css on context
    - www/portal/index.html: uses {{ vue_js }} and {{ vue_css }} Jinja variables, #app mount point, spinner while loading
    - All files exist at the paths listed in &lt;files&gt;
  </done>
</task>

</tasks>

<verification>
After both tasks complete, verify the full structure:

```bash
cd /workspace/development

# Structural verification
find portal-vue/src -type f | sort
# Expected:
#   portal-vue/src/App.vue
#   portal-vue/src/main.js
#   portal-vue/src/components/Sidebar.vue
#   portal-vue/src/config/navigation.js
#   portal-vue/src/layouts/PortalLayout.vue
#   portal-vue/src/router/index.js
#   portal-vue/src/stores/session.js

# Vite build attempt (requires node_modules)
cd portal-vue && npm install && npm run build
# Expected: builds successfully to:
# ../frappe-bench/apps/university_erp/university_erp/public/portal/

# Backend endpoint syntax check
python -c "
import ast
with open('frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py') as f:
    ast.parse(f.read())
print('portal_api.py: valid Python')
with open('frappe-bench/apps/university_erp/university_erp/www/portal/index.py') as f:
    ast.parse(f.read())
print('www/portal/index.py: valid Python')
"
```
</verification>

<success_criteria>
- portal-vue/ project scaffold complete: package.json, index.html, vite.config.js, src/main.js, src/App.vue
- Pinia session store: fetchSession() calls get_session_info endpoint, populates {logged_user, full_name, user_image, roles, allowed_modules}, sets loaded=true
- Vue Router: createWebHistory('/portal/'), beforeEach uses sessionStore.isAuthenticated (zero frappe.auth.get_logged_user calls)
- Sidebar: visibleItems = navItems filtered by roles intersection, renders RouterLink for each visible item
- navigation.js: navItems array covering all role personas (management, faculty, hod, student, finance, admin)
- get_session_info() in portal_api.py: returns {logged_user, full_name, user_image, roles[], allowed_modules[]}
- www/portal/index.py: get_context() redirects Guest to /login, reads Vite manifest from public/portal/.vite/manifest.json
- www/portal/index.html: standard SPA shell with spinner, mounts Vue app at #app
- npm run build succeeds (outDir = public/portal/, base = /assets/university_erp/portal/)
</success_criteria>

<output>
After completion, create `/workspace/development/.planning/phases/01-foundation-security-hardening/01-02-portal-app-shell-SUMMARY.md` with:
- Complete file listing of portal-vue/ structure
- Build output path confirmed
- get_session_info() endpoint URL
- Navigation items defined and which roles they require
- www/portal/ page structure
- Deviations from this plan and why
</output>

import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '../stores/session.js'
import PortalLayout from '../layouts/PortalLayout.vue'

// Placeholder views — Phases 3-6 replace these with real implementations
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
      { path: 'faculty', name: 'faculty', component: () => import('../components/faculty/FacultyDashboard.vue') },
      { path: 'faculty/teaching', name: 'faculty-teaching', component: () => import('../components/faculty/FacultyTeaching.vue') },
      { path: 'faculty/work', name: 'faculty-work', component: () => import('../components/faculty/FacultyWork.vue') },
      { path: 'faculty/notices', name: 'faculty-notices', component: () => import('../components/faculty/FacultyNotices.vue') },
      // Redirects from old faculty routes
      { path: 'faculty/attendance', redirect: '/faculty/teaching?tab=attendance' },
      { path: 'faculty/grades', redirect: '/faculty/teaching?tab=grades' },
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

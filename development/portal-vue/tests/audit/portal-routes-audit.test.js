/**
 * Portal Routes Render Audit
 *
 * Verifies that all portal-vue routes render without errors.
 * Tests each route's component can mount with mocked dependencies.
 *
 * This is an audit test -- it documents which routes work and which fail,
 * but does NOT fix broken routes (fixes are in separate plans).
 */
import { describe, it, expect, vi, afterAll } from 'vitest'
import { mount } from '@vue/test-utils'
import { writeFileSync } from 'fs'
import { resolve } from 'path'

// ============================================================================
// Mocks -- must be before component imports
// ============================================================================

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: {}, params: {}, fullPath: '/faculty' }),
  RouterView: { template: '<div data-testid="router-view"></div>' },
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
}))

// Mock useFrappe
vi.mock('../../src/composables/useFrappe.js', () => ({
  useFrappe: () => ({
    call: vi.fn(() => Promise.resolve({ message: {} })),
    getList: vi.fn(() => Promise.resolve([])),
  }),
}))

// Mock useThemeColors
vi.mock('../../src/composables/useThemeColors.js', () => ({
  useThemeColors: () => ({
    colors: { value: {
      primary: '#4F46E5',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#3B82F6',
      secondary: '#9333EA',
    }},
  }),
}))

// Mock useToast
vi.mock('../../src/composables/useToast.js', () => ({
  useToast: () => ({
    toasts: { value: [] },
    addToast: vi.fn(),
    removeToast: vi.fn(),
  }),
}))

// Mock useReportRunner
vi.mock('../../src/composables/useReportRunner.js', () => ({
  useReportRunner: () => ({
    loadReportMeta: vi.fn(),
    runReport: vi.fn(),
    columns: { value: [] },
    rows: { value: [] },
    filters: { value: [] },
    loading: { value: false },
    error: { value: null },
  }),
}))

// Mock useExportPdf and useExportExcel
vi.mock('../../src/composables/useExportPdf.js', () => ({
  useExportPdf: () => ({ exportToPdf: vi.fn() }),
}))
vi.mock('../../src/composables/useExportExcel.js', () => ({
  useExportExcel: () => ({ exportToExcel: vi.fn() }),
}))

// Mock useFacultyApi
vi.mock('../../src/composables/useFacultyApi.js', () => ({
  useFacultyApi: () => ({
    call: vi.fn(() => Promise.resolve({ message: {} })),
    getDashboard: vi.fn(() => Promise.resolve({
      today_classes: [],
      pending_tasks: { unmarked_attendance: 0, pending_grades: 0, pending_leave_requests: 0, classes_today: 0 },
      recent_notices: [],
    })),
    getTimetable: vi.fn(() => Promise.resolve({ schedule: [] })),
    getNotices: vi.fn(() => Promise.resolve([])),
    getLeaveBalance: vi.fn(() => Promise.resolve([])),
    getLeaveRequests: vi.fn(() => Promise.resolve([])),
    getStudents: vi.fn(() => Promise.resolve({ students: [], total: 0 })),
    getCourses: vi.fn(() => Promise.resolve([])),
    getGrades: vi.fn(() => Promise.resolve({ students: [], columns: [] })),
    submitGrades: vi.fn(() => Promise.resolve({})),
    submitAttendance: vi.fn(() => Promise.resolve({})),
    getWorkloadSummary: vi.fn(() => Promise.resolve({ personal: {}, department_avg: {} })),
    getResearchPublications: vi.fn(() => Promise.resolve([])),
    getObeAttainment: vi.fn(() => Promise.resolve({})),
    getLmsCourses: vi.fn(() => Promise.resolve([])),
    getPerformanceAnalytics: vi.fn(() => Promise.resolve({})),
    loading: { value: false },
    error: { value: null },
  }),
}))

// Mock vue3-apexcharts
vi.mock('vue3-apexcharts', () => ({
  default: {
    name: 'apexchart',
    template: '<div class="apexcharts-mock" role="img" aria-label="Chart visualization"></div>',
    props: ['type', 'options', 'series', 'height'],
  },
}))

// Mock session store
vi.mock('../../src/stores/session.js', () => ({
  useSessionStore: () => ({
    user: 'admin@test.com',
    fullName: 'Test Admin',
    roles: ['System Manager', 'University Faculty'],
    isAuthenticated: true,
    loaded: true,
  }),
}))

// ============================================================================
// Component imports
// ============================================================================
import FacultyDashboard from '../../src/components/faculty/FacultyDashboard.vue'
import FacultyTeaching from '../../src/components/faculty/FacultyTeaching.vue'
import FacultyWork from '../../src/components/faculty/FacultyWork.vue'
import FacultyNotices from '../../src/components/faculty/FacultyNotices.vue'

// ============================================================================
// Audit results collection
// ============================================================================
const routeResults = []

const globalStubs = {
  stubs: {
    apexchart: { template: '<div role="img" aria-label="Chart"></div>' },
    RouterView: { template: '<div></div>' },
    RouterLink: { template: '<a><slot /></a>', props: ['to'] },
    KpiCard: { template: '<div class="stat-card" role="group"><slot /></div>', props: ['label', 'value', 'trend', 'status', 'icon', 'loading'] },
    ChartWrapper: { template: '<div role="img" aria-label="Chart"></div>', props: ['type', 'series', 'categories', 'title', 'height', 'loading', 'error'] },
    DataTable: { template: '<div role="table"><slot /></div>', props: ['columns', 'data', 'totalRows', 'loading', 'title', 'pageSize', 'searchable'] },
    FilterBar: { template: '<div role="search"><slot /></div>', props: ['academicYears', 'departments', 'programs', 'loading'] },
    NotificationPanel: { template: '<div><slot /></div>', props: ['items', 'loading'] },
    SkeletonLoader: { template: '<div aria-hidden="true"></div>', props: ['width', 'height', 'circle', 'borderRadius'] },
    TabLayout: { template: '<div role="tablist"><slot /></div>', props: ['tabs', 'activeTab'] },
    TimetableToday: { template: '<div></div>' },
    GradeAnalyticsPanel: { template: '<div></div>', props: ['data'] },
    StudentDetailPanel: { template: '<div></div>', props: ['student'] },
    LeaveApplyForm: { template: '<div></div>' },
    LmsContentForm: { template: '<div></div>' },
    LmsCourseList: { template: '<div></div>' },
    LmsContentManager: { template: '<div></div>' },
    ObeAttainment: { template: '<div></div>' },
    PerformanceAnalytics: { template: '<div></div>' },
    ResearchPublications: { template: '<div></div>' },
    AttendanceMarker: { template: '<div></div>' },
    TimetableGrid: { template: '<div></div>' },
    LeaveBalanceCards: { template: '<div></div>' },
    StudentLeaveQueue: { template: '<div></div>' },
    WorkloadSummary: { template: '<div></div>' },
    FacultyGradeGrid: { template: '<div></div>' },
    StudentListView: { template: '<div></div>' },
  },
}

async function testRoute(routePath, componentName, Component) {
  try {
    const wrapper = mount(Component, { global: globalStubs })
    const html = wrapper.html()

    if (!html || html.trim() === '') {
      routeResults.push({
        route: routePath,
        component: componentName,
        status: 'WARN',
        notes: 'Component rendered but produced empty HTML',
      })
      return
    }

    // Check for error state indicators
    const text = wrapper.text()
    const hasError = /error|failed|exception/i.test(text) && !/error_text|error-text/i.test(html)

    routeResults.push({
      route: routePath,
      component: componentName,
      status: hasError ? 'WARN' : 'PASS',
      notes: hasError ? 'Component rendered but contains error text' : 'Renders successfully',
    })
  } catch (err) {
    routeResults.push({
      route: routePath,
      component: componentName,
      status: 'FAIL',
      notes: `Mount error: ${err.message}`.substring(0, 200),
    })
  }
}

// ============================================================================
// Route Tests
// ============================================================================
describe('Portal Route Render Audit', () => {
  describe('Faculty Routes', () => {
    it('/faculty (FacultyDashboard) renders', async () => {
      await testRoute('/faculty', 'FacultyDashboard', FacultyDashboard)
      const result = routeResults.find(r => r.route === '/faculty')
      expect(result).toBeDefined()
      expect(result.status).not.toBe('FAIL')
    })

    it('/faculty/teaching (FacultyTeaching) renders', async () => {
      await testRoute('/faculty/teaching', 'FacultyTeaching', FacultyTeaching)
      const result = routeResults.find(r => r.route === '/faculty/teaching')
      expect(result).toBeDefined()
      expect(result.status).not.toBe('FAIL')
    })

    it('/faculty/work (FacultyWork) renders', async () => {
      await testRoute('/faculty/work', 'FacultyWork', FacultyWork)
      const result = routeResults.find(r => r.route === '/faculty/work')
      expect(result).toBeDefined()
      expect(result.status).not.toBe('FAIL')
    })

    it('/faculty/notices (FacultyNotices) renders', async () => {
      await testRoute('/faculty/notices', 'FacultyNotices', FacultyNotices)
      const result = routeResults.find(r => r.route === '/faculty/notices')
      expect(result).toBeDefined()
      expect(result.status).not.toBe('FAIL')
    })
  })

  describe('Placeholder Routes (ComingSoon)', () => {
    // These routes use inline ComingSoon component -- test that the pattern works
    const ComingSoon = {
      props: ['moduleName'],
      template: '<div style="padding:2rem"><h2>{{ moduleName || \'Module\' }}</h2><p style="color:#64748b">Coming in a future phase.</p></div>',
    }

    it('/ (home) placeholder renders', async () => {
      await testRoute('/', 'ComingSoon (home)', ComingSoon)
      const result = routeResults.find(r => r.route === '/')
      expect(result).toBeDefined()
      expect(result.status).toBe('PASS')
    })

    it('/management placeholder renders', async () => {
      const wrapper = mount(ComingSoon, { props: { moduleName: 'Management Dashboard' }, global: globalStubs })
      routeResults.push({
        route: '/management',
        component: 'ComingSoon',
        status: wrapper.html() ? 'PASS' : 'FAIL',
        notes: 'Placeholder -- future phase',
      })
      expect(wrapper.html()).toBeTruthy()
    })

    it('/hod placeholder renders', async () => {
      const wrapper = mount(ComingSoon, { props: { moduleName: 'Department Overview' }, global: globalStubs })
      routeResults.push({
        route: '/hod',
        component: 'ComingSoon',
        status: wrapper.html() ? 'PASS' : 'FAIL',
        notes: 'Placeholder -- future phase',
      })
      expect(wrapper.html()).toBeTruthy()
    })

    it('/student placeholder renders', async () => {
      const wrapper = mount(ComingSoon, { props: { moduleName: 'My Dashboard' }, global: globalStubs })
      routeResults.push({
        route: '/student',
        component: 'ComingSoon',
        status: wrapper.html() ? 'PASS' : 'FAIL',
        notes: 'Placeholder -- future phase',
      })
      expect(wrapper.html()).toBeTruthy()
    })

    it('/finance placeholder renders', async () => {
      const wrapper = mount(ComingSoon, { props: { moduleName: 'Finance' }, global: globalStubs })
      routeResults.push({
        route: '/finance',
        component: 'ComingSoon',
        status: wrapper.html() ? 'PASS' : 'FAIL',
        notes: 'Placeholder -- future phase',
      })
      expect(wrapper.html()).toBeTruthy()
    })

    it('/admin/health placeholder renders', async () => {
      const wrapper = mount(ComingSoon, { props: { moduleName: 'System Health' }, global: globalStubs })
      routeResults.push({
        route: '/admin/health',
        component: 'ComingSoon',
        status: wrapper.html() ? 'PASS' : 'FAIL',
        notes: 'Placeholder -- future phase',
      })
      expect(wrapper.html()).toBeTruthy()
    })
  })
})

// ============================================================================
// POST-TEST: Write results
// ============================================================================
afterAll(() => {
  try {
    const outPath = resolve(__dirname, 'route-audit-results.json')
    writeFileSync(outPath, JSON.stringify(routeResults, null, 2))

    console.log('\n=== PORTAL ROUTE AUDIT SUMMARY ===')
    console.log(`Total routes tested: ${routeResults.length}`)
    const pass = routeResults.filter(r => r.status === 'PASS').length
    const warn = routeResults.filter(r => r.status === 'WARN').length
    const fail = routeResults.filter(r => r.status === 'FAIL').length
    console.log(`PASS: ${pass}`)
    console.log(`WARN: ${warn}`)
    console.log(`FAIL: ${fail}`)
    if (fail > 0) {
      console.log('\nFailed routes:')
      routeResults.filter(r => r.status === 'FAIL').forEach(r => {
        console.log(`  ${r.route} (${r.component}): ${r.notes}`)
      })
    }
    console.log('===================================\n')
  } catch (e) {
    console.warn('Could not write route-audit-results.json:', e.message)
  }
})

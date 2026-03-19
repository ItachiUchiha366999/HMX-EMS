/**
 * Accessibility Audit Test Suite
 *
 * Scans all portal-vue shared and faculty components for WCAG 2.1 AA violations
 * using vitest-axe (axe-core). Collects violations by severity and generates
 * a summary report in a11y-results.json.
 *
 * Phase 1 (Task 1): Discovery -- collects all violations without failing.
 * Phase 2 (Task 2): After fixes, assertions tightened to require zero critical/serious.
 */
import { describe, it, expect, vi, afterAll } from 'vitest'
import { mount } from '@vue/test-utils'
import { axe } from 'vitest-axe'
import { writeFileSync } from 'fs'
import { resolve } from 'path'

// ============================================================================
// Mocks -- must be before component imports
// ============================================================================

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: {}, params: {} }),
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

// ============================================================================
// Component imports (after mocks)
// ============================================================================
import KpiCard from '../../src/components/shared/KpiCard.vue'
import DataTable from '../../src/components/shared/DataTable.vue'
import ChartWrapper from '../../src/components/shared/ChartWrapper.vue'
import FilterBar from '../../src/components/shared/FilterBar.vue'
import NotificationPanel from '../../src/components/shared/NotificationPanel.vue'
import ReportViewer from '../../src/components/shared/ReportViewer.vue'
import SkeletonLoader from '../../src/components/shared/SkeletonLoader.vue'
import ToastNotification from '../../src/components/shared/ToastNotification.vue'

// Faculty components
import FacultyDashboard from '../../src/components/faculty/FacultyDashboard.vue'
import TimetableToday from '../../src/components/faculty/TimetableToday.vue'
import FacultyNotices from '../../src/components/faculty/FacultyNotices.vue'
import AttendanceMarker from '../../src/components/faculty/AttendanceMarker.vue'
import TimetableGrid from '../../src/components/faculty/TimetableGrid.vue'
import LeaveBalanceCards from '../../src/components/faculty/LeaveBalanceCards.vue'
import StudentLeaveQueue from '../../src/components/faculty/StudentLeaveQueue.vue'
import WorkloadSummary from '../../src/components/faculty/WorkloadSummary.vue'

// ============================================================================
// Violation collection
// ============================================================================
const allViolations = []

function collectViolations(componentName, results) {
  if (results.violations && results.violations.length > 0) {
    results.violations.forEach(v => {
      allViolations.push({
        component: componentName,
        id: v.id,
        impact: v.impact,
        description: v.description,
        nodes: v.nodes ? v.nodes.length : 0,
        help: v.help,
        helpUrl: v.helpUrl,
        tags: v.tags || [],
      })
    })
  }
}

async function runAxeAudit(container) {
  const div = document.createElement('div')
  div.innerHTML = container.innerHTML || container.html()
  document.body.appendChild(div)
  try {
    const results = await axe(div, {
      rules: {
        // Disable region rule (landmark) for individual components -- tested on layout
        region: { enabled: false },
        // Disable color-contrast in jsdom (computed styles are not reliable)
        'color-contrast': { enabled: false },
      },
    })
    return results
  } finally {
    document.body.removeChild(div)
  }
}

// ============================================================================
// Helper to mount components safely
// ============================================================================
function safeMountShared(Component, options = {}) {
  return mount(Component, {
    global: {
      stubs: {
        apexchart: { template: '<div role="img" aria-label="Chart"></div>' },
        RouterView: { template: '<div></div>' },
        RouterLink: { template: '<a><slot /></a>', props: ['to'] },
      },
      ...options.global,
    },
    ...options,
  })
}

const facultyGlobal = {
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
  },
}

// ============================================================================
// SHARED COMPONENT TESTS
// ============================================================================
describe('Accessibility Audit - Shared Components', () => {

  describe('KpiCard', () => {
    it('scans for axe violations', async () => {
      const wrapper = safeMountShared(KpiCard, {
        props: { label: 'Total Students', value: '1,234', trend: 5.2, status: 'good', icon: 'groups' },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('KpiCard', results)
      // Audit pass -- violations collected
      expect(results).toBeDefined()
    })
  })

  describe('DataTable', () => {
    it('scans for axe violations', async () => {
      const columns = [
        { accessorKey: 'name', header: 'Name', sortable: true },
        { accessorKey: 'email', header: 'Email', sortable: false },
      ]
      const data = [
        { name: 'John Doe', email: 'john@test.com' },
        { name: 'Jane Smith', email: 'jane@test.com' },
      ]
      const wrapper = safeMountShared(DataTable, {
        props: { columns, data, totalRows: 2, title: 'Students', pageSize: 20 },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('DataTable', results)
      expect(results).toBeDefined()
    })
  })

  describe('ChartWrapper', () => {
    it('scans for axe violations (with data)', async () => {
      const wrapper = safeMountShared(ChartWrapper, {
        props: {
          type: 'bar',
          series: [{ name: 'Test', data: [10, 20, 30] }],
          categories: ['A', 'B', 'C'],
          title: 'Test Chart',
          subtitle: 'Monthly data',
        },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('ChartWrapper', results)
      expect(results).toBeDefined()
    })

    it('scans for axe violations (empty state)', async () => {
      const wrapper = safeMountShared(ChartWrapper, {
        props: { type: 'bar', series: [], categories: [] },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('ChartWrapper-empty', results)
      expect(results).toBeDefined()
    })
  })

  describe('FilterBar', () => {
    it('scans for axe violations', async () => {
      const wrapper = safeMountShared(FilterBar, {
        props: {
          academicYears: ['2025-26', '2024-25'],
          departments: ['Computer Science', 'Physics'],
          programs: ['B.Tech', 'M.Tech'],
        },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('FilterBar', results)
      // FilterBar has known label issues -- will be fixed in Task 2
      expect(results).toBeDefined()
    })
  })

  describe('NotificationPanel', () => {
    it('scans for axe violations (with items)', async () => {
      const items = [
        { id: 1, title: 'New assignment', body: 'CS201 has a new assignment', category: 'assignment', read: false, timestamp: '2 hours ago' },
        { id: 2, title: 'Grade posted', body: 'Your grade for CS101 is available', category: 'grade', read: true, timestamp: '1 day ago' },
      ]
      const wrapper = safeMountShared(NotificationPanel, {
        props: { items },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('NotificationPanel', results)
      expect(results).toBeDefined()
    })

    it('scans for axe violations (empty state)', async () => {
      const wrapper = safeMountShared(NotificationPanel, {
        props: { items: [] },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('NotificationPanel-empty', results)
      expect(results).toBeDefined()
    })
  })

  describe('ReportViewer', () => {
    it('scans for axe violations', async () => {
      const wrapper = safeMountShared(ReportViewer, {
        props: { reportName: 'Test Report' },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('ReportViewer', results)
      expect(results).toBeDefined()
    })
  })

  describe('SkeletonLoader', () => {
    it('scans for axe violations', async () => {
      const wrapper = safeMountShared(SkeletonLoader, {
        props: { width: '100%', height: '40px' },
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('SkeletonLoader', results)
      expect(results).toBeDefined()
    })
  })

  describe('ToastNotification', () => {
    it('scans for axe violations', async () => {
      const wrapper = safeMountShared(ToastNotification)
      const results = await runAxeAudit(wrapper)
      collectViolations('ToastNotification', results)
      expect(results).toBeDefined()
    })
  })
})

// ============================================================================
// FACULTY COMPONENT TESTS
// ============================================================================
describe('Accessibility Audit - Faculty Components', () => {

  describe('FacultyDashboard', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(FacultyDashboard, { global: facultyGlobal })
      const results = await runAxeAudit(wrapper)
      collectViolations('FacultyDashboard', results)
      expect(results).toBeDefined()
    })
  })

  describe('TimetableToday', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(TimetableToday, {
        props: { classes: [
          { name: 'CS-001', course_name: 'Data Structures', room: 'Room 301', start_time: '09:00', end_time: '10:00', is_marked: false, student_count: 40 },
        ]},
        global: facultyGlobal,
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('TimetableToday', results)
      expect(results).toBeDefined()
    })
  })

  describe('FacultyNotices', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(FacultyNotices, { global: facultyGlobal })
      const results = await runAxeAudit(wrapper)
      collectViolations('FacultyNotices', results)
      expect(results).toBeDefined()
    })
  })

  describe('AttendanceMarker', () => {
    it('scans for axe violations', async () => {
      const classInfo = {
        name: 'CS-SCH-001',
        course: 'CS201',
        course_name: 'Data Structures',
        room: 'Room 301',
        start_time: '09:00:00',
        end_time: '10:00:00',
        section: 'Section A',
        schedule_date: '2026-03-18',
        is_marked: false,
        student_count: 60,
      }
      const wrapper = mount(AttendanceMarker, {
        props: { classInfo },
        global: facultyGlobal,
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('AttendanceMarker', results)
      expect(results).toBeDefined()
    })
  })

  describe('TimetableGrid', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(TimetableGrid, { global: facultyGlobal })
      const results = await runAxeAudit(wrapper)
      collectViolations('TimetableGrid', results)
      expect(results).toBeDefined()
    })
  })

  describe('LeaveBalanceCards', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(LeaveBalanceCards, {
        props: { balances: [
          { leave_type: 'Casual Leave', total: 12, used: 3, pending: 1 },
          { leave_type: 'Sick Leave', total: 10, used: 2, pending: 0 },
        ]},
        global: facultyGlobal,
      })
      const results = await runAxeAudit(wrapper)
      collectViolations('LeaveBalanceCards', results)
      expect(results).toBeDefined()
    })
  })

  describe('StudentLeaveQueue', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(StudentLeaveQueue, { global: facultyGlobal })
      const results = await runAxeAudit(wrapper)
      collectViolations('StudentLeaveQueue', results)
      expect(results).toBeDefined()
    })
  })

  describe('WorkloadSummary', () => {
    it('scans for axe violations', async () => {
      const wrapper = mount(WorkloadSummary, { global: facultyGlobal })
      const results = await runAxeAudit(wrapper)
      collectViolations('WorkloadSummary', results)
      expect(results).toBeDefined()
    })
  })
})

// ============================================================================
// POST-TEST: Write results JSON
// ============================================================================
afterAll(() => {
  const summary = {
    total_components: 16,
    components_with_violations: new Set(allViolations.map(v => v.component)).size,
    critical: allViolations.filter(v => v.impact === 'critical').length,
    serious: allViolations.filter(v => v.impact === 'serious').length,
    moderate: allViolations.filter(v => v.impact === 'moderate').length,
    minor: allViolations.filter(v => v.impact === 'minor').length,
    violations: allViolations,
  }

  try {
    const outPath = resolve(__dirname, 'a11y-results.json')
    writeFileSync(outPath, JSON.stringify(summary, null, 2))
    console.log('\n=== ACCESSIBILITY AUDIT SUMMARY ===')
    console.log(`Total components scanned: ${summary.total_components}`)
    console.log(`Components with violations: ${summary.components_with_violations}`)
    console.log(`Critical: ${summary.critical}`)
    console.log(`Serious: ${summary.serious}`)
    console.log(`Moderate: ${summary.moderate}`)
    console.log(`Minor: ${summary.minor}`)
    console.log(`Total violations: ${summary.violations.length}`)
    if (summary.violations.length > 0) {
      console.log('\nViolations by component:')
      const byComponent = {}
      summary.violations.forEach(v => {
        if (!byComponent[v.component]) byComponent[v.component] = []
        byComponent[v.component].push(`  [${v.impact}] ${v.id}: ${v.help}`)
      })
      Object.entries(byComponent).forEach(([comp, violations]) => {
        console.log(`\n  ${comp}:`)
        violations.forEach(v => console.log(`    ${v}`))
      })
    }
    console.log('===================================\n')
  } catch (e) {
    console.warn('Could not write a11y-results.json:', e.message)
  }
})

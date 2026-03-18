---
phase: 03-faculty-portal
plan: 01
subsystem: ui
tags: [vue3, frappe-api, faculty-portal, attendance, timetable, vitest, dark-mode, tab-layout]

# Dependency graph
requires:
  - phase: 01-foundation-security-hardening
    provides: portal-vue scaffold, session store, router, CSS design system, auth guards
  - phase: 02-shared-component-library
    provides: KpiCard, ChartWrapper, DataTable, FilterBar, NotificationPanel, SkeletonLoader, ToastNotification, useFrappe, useToast
provides:
  - faculty_api.py backend with 6 active endpoints + 21 stub endpoints for Plans 02/03
  - useFacultyApi.js composable wrapping all 27 faculty endpoints
  - TabLayout.vue reusable tab component with ARIA accessibility
  - FacultyDashboard.vue with 4 KPI pending-task cards and today's classes
  - TimetableToday.vue with class list, current class highlighting, mark/marked states
  - TimetableGrid.vue with Mon-Fri weekly grid, mobile day-at-a-time, week navigation
  - AttendanceMarker.vue with present-by-default checkboxes, submit with live counts, idempotency protection
  - FacultyNotices.vue with category filtering, emergency highlighting, pagination
  - FacultyTeaching.vue with 4-tab layout (Timetable, Attendance, Grades, Students)
  - Updated navigation.js (Dashboard, Teaching, My Work, Notices) and router with redirects
  - CSS --error-tint and --primary-tint variables with dark mode rgba equivalents
  - faculty-setup.js test fixtures with mock data and mockUseFacultyApi
affects: [03-02-faculty-portal, 03-03-faculty-portal, 04-hod-portal]

# Tech tracking
tech-stack:
  added: []
  patterns: [smart-dumb-component-split, tab-based-page-organization, present-by-default-attendance, faculty-api-pattern, query-param-tab-selection]

key-files:
  created:
    - frappe-bench/apps/university_erp/university_erp/university_portals/api/faculty_api.py
    - portal-vue/src/composables/useFacultyApi.js
    - portal-vue/src/components/faculty/TabLayout.vue
    - portal-vue/src/components/faculty/FacultyDashboard.vue
    - portal-vue/src/components/faculty/TimetableToday.vue
    - portal-vue/src/components/faculty/TimetableGrid.vue
    - portal-vue/src/components/faculty/AttendanceMarker.vue
    - portal-vue/src/components/faculty/FacultyNotices.vue
    - portal-vue/src/components/faculty/FacultyTeaching.vue
    - portal-vue/src/components/faculty/FacultyWork.vue
    - portal-vue/src/components/faculty/__tests__/faculty-setup.js
    - portal-vue/src/composables/__tests__/useFacultyApi.test.js
    - portal-vue/src/components/faculty/__tests__/FacultyDashboard.test.js
    - portal-vue/src/components/faculty/__tests__/TimetableToday.test.js
    - portal-vue/src/components/faculty/__tests__/FacultyNotices.test.js
    - portal-vue/src/components/faculty/__tests__/AttendanceMarker.test.js
    - portal-vue/src/components/faculty/__tests__/TimetableGrid.test.js
  modified:
    - portal-vue/src/config/navigation.js
    - portal-vue/src/router/index.js
    - frappe-bench/apps/university_erp/university_erp/public/css/theme/variables.css

key-decisions:
  - "faculty_api.py contains ALL phase endpoints (6 active + 21 stubs) to avoid modifying the same file across plans"
  - "get_current_faculty() maps user -> Employee with custom_is_faculty=1 check, following portal_api.py pattern"
  - "submit_attendance uses frappe.db.count idempotency check before creating Student Attendance records"
  - "Tab-based page organization: 4 sidebar items (Dashboard, Teaching, My Work, Notices) with sub-tabs per page"
  - "Old /faculty/attendance and /faculty/grades routes redirect to /faculty/teaching?tab=attendance and ?tab=grades"
  - "AttendanceMarker: all students pre-checked as Present (present-by-default per user decision)"
  - "TimetableGrid: Teaching Assignment Schedule as primary data source (NOT Course Schedule)"

patterns-established:
  - "Smart/dumb component split: page components fetch data, child components receive via props"
  - "Tab-based navigation: TabLayout with modelValue prop, query param ?tab= for deep-linking"
  - "Faculty API pattern: get_current_faculty() at top of every endpoint, then data fetch"
  - "Present-by-default attendance: boolean array initialized to all true, toggle to mark absent"
  - "Category filtering: filter buttons with active/inactive state, server-side filter params"

requirements-completed: [FCTY-01, FCTY-02, FCTY-05, FCTY-06]

# Metrics
duration: 13min
completed: 2026-03-18
---

# Phase 3 Plan 01: Faculty Portal Core Summary

**Faculty dashboard with 4 pending-task KPIs, daily timetable with attendance marking (present-by-default for 60 students), weekly grid, and category-filtered announcements -- 27 backend endpoints + 32 new tests**

## Performance

- **Duration:** 13 min
- **Started:** 2026-03-18T21:16:49Z
- **Completed:** 2026-03-18T21:30:00Z
- **Tasks:** 3
- **Files modified:** 21

## Accomplishments
- Backend faculty_api.py with get_current_faculty helper, 6 active endpoints (dashboard, today_classes, weekly_timetable, students_for_attendance, submit_attendance, announcements), and 21 stub endpoints for Plans 02/03
- FacultyDashboard with 4 clickable KpiCard pending tasks (classes today, unmarked attendance, pending grades, pending leave) + TimetableToday embedded component
- Bulk attendance marking with present-by-default checkboxes, select-all toggle, live present/absent/percentage counter, submit with idempotency check, already-marked banner
- Weekly timetable grid with Mon-Fri columns, occupied slots highlighted in primary-tint, current-time pulsing dot, mobile day-at-a-time with day selector pills
- Category-filtered announcements page with emergency highlighting (error-tint background, red border), pagination
- TabLayout reusable component with role=tablist/tab/tabpanel ARIA accessibility
- Full test suite: 69 tests passing (37 Phase 2 + 32 new), zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Backend faculty_api.py + useFacultyApi.js composable + test fixtures** - `ae4831e5` (feat)
2. **Task 2: TabLayout + navigation/routing + FacultyDashboard + TimetableToday + FacultyNotices + CSS tint vars** - `933b1c99` (feat)
3. **Task 3: AttendanceMarker + TimetableGrid + FacultyTeaching page wiring** - `b2ac3763` (feat)

## Files Created/Modified
- `frappe-bench/.../university_portals/api/faculty_api.py` - All faculty portal backend endpoints (27 whitelisted functions)
- `portal-vue/src/composables/useFacultyApi.js` - Frontend API wrapper for all faculty endpoints
- `portal-vue/src/components/faculty/TabLayout.vue` - Reusable tab container with ARIA roles
- `portal-vue/src/components/faculty/FacultyDashboard.vue` - Landing page with KPIs + today's classes
- `portal-vue/src/components/faculty/TimetableToday.vue` - Compact today class list with mark/marked states
- `portal-vue/src/components/faculty/TimetableGrid.vue` - Weekly grid with mobile responsive layout
- `portal-vue/src/components/faculty/AttendanceMarker.vue` - Bulk attendance with present-by-default
- `portal-vue/src/components/faculty/FacultyNotices.vue` - Filtered announcements with emergency styling
- `portal-vue/src/components/faculty/FacultyTeaching.vue` - Teaching page with 4 tabs
- `portal-vue/src/components/faculty/FacultyWork.vue` - Placeholder for Plan 03
- `portal-vue/src/config/navigation.js` - Updated faculty sidebar (Dashboard, Teaching, My Work, Notices)
- `portal-vue/src/router/index.js` - Lazy-loaded faculty routes + old path redirects
- `frappe-bench/.../public/css/theme/variables.css` - --error-tint, --primary-tint dark mode vars
- `portal-vue/src/components/faculty/__tests__/faculty-setup.js` - Shared mock fixtures
- `portal-vue/src/composables/__tests__/useFacultyApi.test.js` - 7 composable API tests
- `portal-vue/src/components/faculty/__tests__/FacultyDashboard.test.js` - 5 dashboard tests
- `portal-vue/src/components/faculty/__tests__/TimetableToday.test.js` - 6 timetable today tests
- `portal-vue/src/components/faculty/__tests__/FacultyNotices.test.js` - 4 notices tests
- `portal-vue/src/components/faculty/__tests__/AttendanceMarker.test.js` - 6 attendance tests
- `portal-vue/src/components/faculty/__tests__/TimetableGrid.test.js` - 4 grid tests

## Decisions Made
- faculty_api.py contains ALL phase endpoints (6 active + 21 stubs) to avoid modifying the same file across plans
- get_current_faculty() maps user -> Employee with custom_is_faculty=1 check, consistent with portal_api.py student pattern
- submit_attendance uses frappe.db.count idempotency check before creating Student Attendance records
- Tab-based page organization with 4 sidebar items replacing original 3 (adds My Work and Notices)
- Old /faculty/attendance and /faculty/grades routes redirect to new tab-based paths
- AttendanceMarker: all students pre-checked as Present (fastest for typical 90%+ attendance)
- TimetableGrid uses Teaching Assignment Schedule as primary data source (has instructor mapping)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 02 (grade entry grid, student list, performance analytics) can proceed -- FacultyTeaching tabs have Grades and Students placeholders ready for replacement
- Plan 03 (leave, LMS, research, OBE, workload) can proceed -- FacultyWork.vue placeholder ready, stub endpoints in faculty_api.py
- TabLayout, TimetableToday, and faculty-setup.js fixtures available for reuse in Plans 02/03
- 69 tests provide regression safety for continued development

---
*Phase: 03-faculty-portal*
*Completed: 2026-03-18*

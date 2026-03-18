# Phase 3: Faculty Portal - Research

**Researched:** 2026-03-18
**Domain:** Vue 3 SPA faculty portal with Frappe Python backend APIs
**Confidence:** HIGH

## Summary

Phase 3 builds the faculty-facing portal -- 12 requirements (FCTY-01 through FCTY-12) covering timetable viewing, bulk attendance marking, spreadsheet-like grade entry, student lists with performance analytics, pending tasks dashboard, announcements, leave management (faculty's own + student approval), LMS course content CRUD, research publications, OBE CO/PO attainment, and workload summary.

The foundation is solid: Phase 1 delivered the Vue app shell with Pinia session store, role-based routing, and auth guards. Phase 2 delivered 8 shared components (KpiCard, ChartWrapper, DataTable, FilterBar, NotificationPanel, ReportViewer, SkeletonLoader, ToastNotification) and 6 composables (useFrappe, useExportPdf, useExportExcel, useReportRunner, useThemeColors, useToast). The backend has extensive existing doctypes and API patterns -- Teaching Assignment, Faculty Profile, Faculty Publication, Student Attendance, Assessment Result, Leave Application, CO/PO attainment calculator, and a faculty workload summary report.

**Primary recommendation:** Split into backend API creation (faculty_api.py following portal_api.py pattern) then frontend Vue pages/components, with the custom FacultyGradeGrid as the highest-complexity item requiring isolated implementation. Use tab-based page organization with 4 sidebar items (Dashboard, Teaching, My Work, Notices) to minimize navigation complexity.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Attendance Flow:** All students start as Present (default). Faculty unchecks the 2-5 absent students. "Mark Attendance" button per class on today's timetable. Explicit "Submit Attendance" button. Post-submit toast with counts: "54 Present, 6 Absent (90%)". Uses DataTable multi-select checkboxes from Phase 2.
- **Grade Entry:** Custom editable grid component (FacultyGradeGrid) -- NOT the read-only DataTable. Spreadsheet-like with Tab/Enter navigation. Auto-save drafts per cell (500ms debounce, green checkmark). Plus explicit "Submit Grades" button to finalize/lock. Supports both numeric marks and direct grade letters. Side panel with live analytics (grade distribution bar chart, class average, pass/fail, at-risk students).
- **Dashboard Layout:** Combined landing page -- pending tasks section at top with KPI cards (classes today, unmarked attendance, pending grades, pending leave requests), then overview below. Clickable KPIs navigate to relevant views.
- **Navigation:** Tab-based page organization. 3-4 sidebar items. "Teaching" page has Timetable/Attendance/Grades/Students tabs.
- **Student Leave Approval:** DataTable with inline Approve/Reject buttons per row. Bulk approve via multi-select.
- **LMS Management:** Full inline CRUD -- create/edit course content, assignments, quizzes within portal. NOT read-only. Full CRUD against Frappe LMS doctypes.
- **Research Publications:** Interactive drill-down. List with counts by type. Click publication for full details.
- **OBE CO/PO:** Interactive drill-down. CO-PO attainment table. Click CO to drill into student-level data.
- **Announcements:** NotificationPanel for real-time + dedicated archive page with search/filters. Filter by category with color-coded emergency notices.
- **Student List:** DataTable with avatar, name, roll, enrollment, attendance %, grade. Inline expandable row for detail. Server-side pagination.
- **Performance Analytics:** Full suite -- grade distribution, attendance correlation, trend over assessments, batch comparison. Multiple charts per course.
- **Workload Summary:** KPI cards (hours/week, courses, credits, students) + weekly heatmap. Each KPI shows personal vs department average.

### Claude's Discretion
- Faculty leave form layout and UX details
- Exact tab groupings and sidebar item labels
- Empty states for all views
- Loading/error states
- API endpoint naming and response structure
- LMS CRUD form design details
- Mobile responsive breakpoints

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FCTY-01 | Faculty can view today's classes with room, time, and course details | TimetableGenerator.get_timetable() by Instructor + Teaching Assignment doctype with schedule child table provide all data. Backend API wraps these for current user. |
| FCTY-02 | Faculty can mark attendance with bulk-select UI (60 students in under 2 minutes) | AttendanceManager.mark_attendance() creates Student Attendance docs. Present-by-default checkbox approach with DataTable multi-select minimizes clicks. |
| FCTY-03 | Faculty can enter grades in spreadsheet-like grid | Custom FacultyGradeGrid component. Backend saves via Assessment Result doctype. UniversityAssessmentResult override auto-calculates grade points. |
| FCTY-04 | Faculty can view enrolled student list per course/section | Course Enrollment doctype + Student doctype provide data. DataTable with server-side pagination. |
| FCTY-05 | Faculty can see pending tasks dashboard | Aggregation API combining: unmarked Course Schedules, unsubmitted Assessment Results, pending Leave Applications. KpiCard components. |
| FCTY-06 | Faculty can view announcements and notices | Notice Board doctype + NotificationPanel component. Archive page with FilterBar + DataTable. |
| FCTY-07 | Faculty can view per-course student performance analytics | Assessment Result data aggregated into grade distribution, trends, correlations. ChartWrapper components. |
| FCTY-08 | Faculty can approve/reject student leave requests | Student Leave Application doctype (or custom). DataTable with inline action buttons. Bulk approve via multi-select. |
| FCTY-09 | Faculty can manage LMS content, assignments, view quiz results | Frappe LMS doctypes (LMS Course, LMS Assignment, LMS Quiz). Full CRUD API endpoints needed. |
| FCTY-10 | Faculty can view research publications and OBE CO/PO data | Faculty Publication doctype + COPOAttainmentCalculator + get_copo_matrix() API. ChartWrapper heatmap for CO-PO matrix. |
| FCTY-11 | Faculty can view leave balance and submit leave requests | HRMS Leave Application doctype + leave balance API. Form submission + DataTable for history. |
| FCTY-12 | Faculty can view teaching workload summary | faculty_workload_summary report + Teaching Assignment data. KpiCard + ChartWrapper heatmap. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vue 3 | ^3.4.0 | Frontend framework | Already installed, Phase 1/2 foundation |
| Pinia | ^2.1.7 | State management | Already installed, session store in use |
| Vue Router | ^4.3.0 | Client-side routing | Already installed, routes scaffolded |
| Frappe (Python) | v15 | Backend framework | Project stack, all doctypes live here |

### Supporting (Already Installed)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| ApexCharts + vue3-apexcharts | ^5.10.4 / ^1.11.1 | Charts (grade distribution, heatmap, trends) | All analytics views via ChartWrapper |
| @tanstack/vue-table | ^8.21.3 | Table logic (attendance, student list, leave queue) | All DataTable instances |
| jsPDF + jspdf-autotable | ^4.2.1 / ^5.0.7 | PDF export | DataTable export buttons |
| ExcelJS | ^4.4.0 | Excel export | DataTable export buttons |

### No New Dependencies
Phase 3 requires zero new npm packages. The FacultyGradeGrid is a custom Vue component using native HTML `<input>` elements with keyboard event handlers -- no third-party spreadsheet library needed.

## Architecture Patterns

### Recommended Project Structure
```
portal-vue/src/
  components/
    shared/               # Phase 2 components (DO NOT MODIFY)
    faculty/              # Phase 3 faculty-specific components
      FacultyDashboard.vue      # /faculty landing page
      FacultyTeaching.vue       # /faculty/teaching (tabs: Timetable, Attendance, Grades, Students)
      FacultyWork.vue           # /faculty/work (tabs: Leave, Workload, Research, OBE)
      FacultyNotices.vue        # /faculty/notices
      TimetableGrid.vue         # Weekly timetable grid
      TimetableToday.vue        # Today's compact class list
      AttendanceMarker.vue      # Bulk attendance marking
      FacultyGradeGrid.vue      # Spreadsheet-like grade entry (custom, NOT DataTable)
      GradeAnalyticsPanel.vue   # Side panel with live grade stats
      StudentListView.vue       # Student DataTable with expandable rows
      StudentDetailPanel.vue    # Expanded row content (attendance, marks, trend)
      PerformanceAnalytics.vue  # Full analytics page (multiple charts)
      LeaveBalanceCards.vue     # Faculty's own leave balances
      LeaveApplyForm.vue        # Slide-over leave application form
      StudentLeaveQueue.vue     # Student leave approval DataTable
      LmsCourseList.vue         # LMS course card list
      LmsContentManager.vue     # Lesson/assignment/quiz CRUD
      LmsContentForm.vue        # Slide-over CRUD form
      ResearchPublications.vue  # Publication list with drill-down
      ObeAttainment.vue         # CO-PO heatmap with drill-down
      WorkloadSummary.vue       # KPI cards + heatmap
      TabLayout.vue             # Reusable tab container component
  composables/
    useFacultyApi.js            # Faculty-specific API calls (wraps useFrappe)

frappe-bench/apps/university_erp/university_erp/
  university_portals/api/
    faculty_api.py              # All faculty portal API endpoints
```

### Pattern 1: Smart/Dumb Component Split
**What:** Page-level "smart" components (FacultyDashboard, FacultyTeaching, etc.) fetch data via useFacultyApi and pass as props to "dumb" presentational components (TimetableGrid, AttendanceMarker, etc.).
**When to use:** Every view.
**Example:**
```javascript
// FacultyTeaching.vue (smart component)
import { useFacultyApi } from '@/composables/useFacultyApi'
const { getTodayClasses, markAttendance } = useFacultyApi()
const classes = ref([])
onMounted(async () => { classes.value = await getTodayClasses() })
// Passes data down to TimetableToday, AttendanceMarker as props
```

### Pattern 2: Backend API Pattern (follow portal_api.py)
**What:** All faculty portal endpoints go in a single `faculty_api.py` file with `@frappe.whitelist()` decorators. Each function starts by identifying the current faculty member, then fetches/mutates data.
**When to use:** Every backend endpoint.
**Example:**
```python
# faculty_api.py
@frappe.whitelist()
def get_faculty_dashboard():
    """Get faculty dashboard data"""
    employee = get_current_faculty()
    if not employee:
        frappe.throw(_("Faculty profile not found"), frappe.PermissionError)

    return {
        "today_classes": get_today_classes(employee),
        "pending_tasks": get_pending_tasks(employee),
        "announcements": get_recent_announcements()
    }
```

### Pattern 3: Tab-Based Page Organization
**What:** Each page (Teaching, My Work) uses a TabLayout component. Router defines the top-level route; active tab is managed via query param or Vue reactive state (not sub-routes).
**When to use:** FacultyTeaching (4 tabs), FacultyWork (4 tabs), FacultyDashboard (2 tabs).
**Example:**
```vue
<!-- TabLayout.vue -->
<template>
  <div class="tab-layout">
    <div class="tab-bar" role="tablist">
      <button v-for="tab in tabs" :key="tab.id"
        role="tab" :aria-selected="activeTab === tab.id"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id">
        {{ tab.label }}
      </button>
    </div>
    <div class="tab-content" role="tabpanel">
      <slot :name="activeTab" />
    </div>
  </div>
</template>
```

### Pattern 4: Faculty Identification
**What:** The backend needs to map the logged-in Frappe user to their Employee record and Teaching Assignments. The session store already has `logged_user`. The backend resolves this to Employee via `frappe.db.get_value("Employee", {"user_id": frappe.session.user})`, then to Instructor via `custom_is_faculty` flag.
**When to use:** Every faculty API endpoint.

### Pattern 5: Grade Auto-Save with Debounce
**What:** Each grade cell input fires a debounced save (500ms). The save calls a backend endpoint that creates/updates an Assessment Result in draft state. A separate "Submit Grades" action finalizes all drafts for that course/assessment.
**When to use:** FacultyGradeGrid only.
**Example:**
```javascript
// In FacultyGradeGrid.vue
function onCellInput(student, assessment, value) {
  cellStates[`${student}-${assessment}`] = 'saving'
  debouncedSave(student, assessment, value)
}

const debouncedSave = debounce(async (student, assessment, value) => {
  await saveDraftGrade({ student, assessment, value })
  cellStates[`${student}-${assessment}`] = 'saved'
  setTimeout(() => { cellStates[`${student}-${assessment}`] = 'idle' }, 1500)
}, 500)
```

### Anti-Patterns to Avoid
- **Using DataTable for grade entry:** DataTable is read-only by design. The grade grid needs editable `<input>` elements with keyboard navigation. Build FacultyGradeGrid from scratch.
- **Sub-routes for tabs:** Using `/faculty/teaching/attendance` as a sub-route adds routing complexity. Keep tabs as reactive state within the page component; use `?tab=attendance` query params for deep-linking if needed.
- **Separate API calls per KPI card:** Dashboard loads all pending-task counts in a single API call (`get_faculty_dashboard`), not 4 separate calls.
- **Client-side attendance calculation:** All attendance percentages must be calculated server-side to be authoritative. Never compute them in Vue.
- **Direct doctype manipulation from frontend:** Always go through whitelisted API methods, never use `frappe.client.get_list` directly for mutations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data tables with sort/page/search | Custom table rendering | Phase 2 DataTable (TanStack) | Already tested, handles server-side pagination |
| Chart rendering | Canvas/SVG drawing | Phase 2 ChartWrapper (ApexCharts) | Heatmap, bar, line all supported |
| KPI display | Custom stat cards | Phase 2 KpiCard | Consistent styling, status colors |
| PDF/Excel export | Custom file generation | Phase 2 useExportPdf/useExportExcel | Already wired into DataTable |
| Toast notifications | Custom notification system | Phase 2 ToastNotification + useToast | Consistent position, timing, styling |
| API calls with CSRF | Custom fetch wrappers | Phase 1 useFrappe composable | Handles auth redirect, CSRF token, error parsing |
| Grading calculation | Custom grade logic | UniversityAssessmentResult.validate() | 10-point grading scale already implemented server-side |
| CO/PO attainment | Custom attainment math | COPOAttainmentCalculator | NBA/NAAC-compliant calculation already exists |
| Leave balance | Custom leave tracking | HRMS Leave Application + Frappe leave balance API | HRMS handles accrual, carry-forward, all edge cases |
| Workload calculation | Custom hours aggregation | faculty_workload_summary report | Already computes utilization categories |

## Common Pitfalls

### Pitfall 1: Faculty-to-Employee Mapping
**What goes wrong:** The logged-in user may not have an Employee record, or may have one but without `custom_is_faculty = 1`. API fails silently or throws unhelpful errors.
**Why it happens:** Faculty users are linked via User -> Employee -> custom_is_faculty flag. If any link is missing, the chain breaks.
**How to avoid:** `get_current_faculty()` helper must check all three: (1) user exists, (2) Employee exists with matching `user_id`, (3) `custom_is_faculty` is set. Return clear error message for each failure case.
**Warning signs:** API returns empty data for a known faculty member.

### Pitfall 2: Attendance Double-Submission
**What goes wrong:** Faculty submits attendance, refreshes page, submits again. Creates duplicate Student Attendance records.
**Why it happens:** No idempotency check in the attendance marking API.
**How to avoid:** Before creating attendance records, check if Student Attendance already exists for that student + course_schedule + date. The existing `mark_attendance` function in attendance.py uses `frappe.new_doc` without checking -- the faculty API must add this check.
**Warning signs:** Student attendance count exceeds total classes.

### Pitfall 3: Grade Grid Performance with Large Classes
**What goes wrong:** A class of 120+ students with 6+ assessments creates 720+ editable cells. Rendering becomes slow, and debounced saves create API pressure.
**Why it happens:** Vue reactivity tracking every cell individually + many concurrent API calls.
**How to avoid:** Use `shallowRef` for the grade matrix data. Batch auto-save calls (save all dirty cells in one API call, not one per cell). Use `v-memo` or virtualized rendering if row count exceeds 100.
**Warning signs:** Typing lag in grade cells, browser memory usage above 200MB.

### Pitfall 4: Timetable Data Shape Mismatch
**What goes wrong:** TimetableGenerator returns data organized by day name (Monday, Tuesday...) from Course Schedule records, but the Teaching Assignment Schedule child table has its own day/time format. Faculty portal needs data from Teaching Assignment (which has instructor mapping), not generic Course Schedule.
**Why it happens:** Two different data sources for timetable -- Course Schedule (Education module) and Teaching Assignment Schedule (university_erp).
**How to avoid:** Use Teaching Assignment Schedule as the primary source for faculty timetable. It directly links instructor -> course -> schedule. The `get_instructor_schedule()` function in teaching_assignment.py already does this correctly.
**Warning signs:** Timetable shows wrong instructor or missing classes.

### Pitfall 5: LMS Doctype Availability
**What goes wrong:** LMS doctypes (LMS Course, LMS Assignment, LMS Quiz) may not exist or may have different field names depending on the Education module version.
**Why it happens:** Frappe LMS was refactored; older Education module versions have different LMS structures.
**How to avoid:** Check doctype existence with `frappe.db.exists("DocType", "LMS Course")` in the API before attempting CRUD operations. Provide graceful fallback if LMS module is not installed.
**Warning signs:** "DocType not found" errors when accessing LMS features.

### Pitfall 6: Leave Application Doctype Differences
**What goes wrong:** Student leave applications and faculty leave applications may use different doctypes or workflows. Student Leave Application may be a custom doctype in university_erp, while faculty uses HRMS Leave Application.
**Why it happens:** HRMS Leave Application is for employees (faculty). Students have a separate mechanism.
**How to avoid:** Faculty's own leave (FCTY-11) uses HRMS Leave Application. Student leave approval (FCTY-08) needs to identify the correct student leave doctype -- check for "Student Leave Application" or similar custom doctype in university_erp.
**Warning signs:** Leave queries return wrong records or permission errors.

### Pitfall 7: Navigation Config Must Be Updated
**What goes wrong:** Phase 3 changes the sidebar structure from 3 items (My Teaching, Mark Attendance, Enter Grades) to 4 items (Dashboard, Teaching, My Work, Notices) with different paths.
**Why it happens:** navigation.js from Phase 1 has different entries than the Phase 3 UI-SPEC requires.
**How to avoid:** Update navigation.js entries and corresponding router routes in the same task. Ensure old paths (/faculty/attendance, /faculty/grades) redirect to new tab-based paths (/faculty/teaching?tab=attendance).
**Warning signs:** 404 errors on faculty routes after navigation update.

## Code Examples

### Backend: get_current_faculty helper
```python
# Source: follows portal_api.py pattern for get_current_student
def get_current_faculty():
    """Get current logged-in faculty's employee record"""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)

    employee = frappe.db.get_value("Employee",
        {"user_id": user, "custom_is_faculty": 1, "status": "Active"},
        ["name", "employee_name", "department", "designation", "user_id"],
        as_dict=True
    )

    if not employee:
        frappe.throw(_("No active faculty profile found for this user"), frappe.PermissionError)

    return employee
```

### Backend: Attendance marking with idempotency
```python
# Source: wraps existing AttendanceManager with duplicate prevention
@frappe.whitelist()
def submit_attendance(course_schedule, attendance_data):
    """Submit attendance for a class with duplicate prevention"""
    if isinstance(attendance_data, str):
        import json
        attendance_data = json.loads(attendance_data)

    faculty = get_current_faculty()

    # Verify this faculty teaches this course
    schedule = frappe.get_doc("Course Schedule", course_schedule)
    if schedule.instructor != faculty.name:
        frappe.throw(_("You are not the instructor for this class"))

    # Check for existing attendance
    existing = frappe.db.count("Student Attendance", {
        "course_schedule": course_schedule,
        "date": schedule.schedule_date
    })
    if existing > 0:
        frappe.throw(_("Attendance already submitted for this class"))

    manager = AttendanceManager()
    result = manager.mark_attendance(course_schedule, attendance_data)

    present = sum(1 for s in attendance_data if s.get("status") == "Present")
    absent = len(attendance_data) - present
    total = len(attendance_data)

    return {
        **result,
        "present": present,
        "absent": absent,
        "percentage": round((present / total) * 100, 1) if total > 0 else 0
    }
```

### Frontend: FacultyGradeGrid cell with keyboard navigation
```vue
<!-- Core concept for grade grid editable cell -->
<input
  type="text"
  :value="getCellValue(student, assessment)"
  @input="onCellInput(student, assessment, $event.target.value)"
  @keydown.tab.prevent="moveToNextCell(student, assessment, 'right')"
  @keydown.enter.prevent="moveToNextCell(student, assessment, 'down')"
  @focus="activateCell(student, assessment)"
  :class="{
    'cell--saving': cellState === 'saving',
    'cell--saved': cellState === 'saved',
    'cell--error': cellState === 'error',
    'cell--at-risk': isAtRisk(student)
  }"
  role="gridcell"
  :aria-label="`${assessment} for ${student.name}`"
/>
```

### Frontend: useFacultyApi composable pattern
```javascript
// composables/useFacultyApi.js
import { useFrappe } from './useFrappe'

export function useFacultyApi() {
  const { call, loading, error } = useFrappe()
  const BASE = 'university_erp.university_portals.api.faculty_api'

  async function getDashboard() {
    return call(`${BASE}.get_faculty_dashboard`, {}, { method: 'GET' })
  }

  async function getTodayClasses() {
    return call(`${BASE}.get_today_classes`, {}, { method: 'GET' })
  }

  async function submitAttendance(courseSchedule, attendanceData) {
    return call(`${BASE}.submit_attendance`, {
      course_schedule: courseSchedule,
      attendance_data: JSON.stringify(attendanceData)
    })
  }

  async function saveDraftGrade(data) {
    return call(`${BASE}.save_draft_grade`, data)
  }

  async function submitGrades(course, assessmentPlan) {
    return call(`${BASE}.submit_grades`, { course, assessment_plan: assessmentPlan })
  }

  return {
    getDashboard, getTodayClasses, submitAttendance,
    saveDraftGrade, submitGrades, loading, error
  }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Course Schedule for timetable | Teaching Assignment Schedule | Phase 6 (faculty_management) | Use Teaching Assignment as primary timetable source for faculty |
| Individual Student Attendance inserts | Bulk insert pattern | Current | mark_attendance() already handles bulk, but needs idempotency wrapper |
| Direct Assessment Result creation | Draft/submit two-phase | Phase 3 (new) | Grade grid auto-saves as drafts; explicit submit finalizes |

**Existing and ready:**
- Teaching Assignment doctype with schedule child table, conflict checking, workload calculation
- Faculty Profile doctype with employee link
- AttendanceManager with mark_attendance and percentage calculation
- UniversityAssessmentResult with 10-point grading override
- COPOAttainmentCalculator with get_copo_matrix API
- faculty_workload_summary report with utilization categories
- 8 shared Vue components + 6 composables from Phase 2

## Open Questions

1. **Student Leave Application Doctype**
   - What we know: Faculty's own leave uses HRMS Leave Application. Students need a different mechanism.
   - What's unclear: Is there a "Student Leave Application" custom doctype in university_erp? Or does student leave flow through a different channel?
   - Recommendation: Check for existing doctype during implementation. If none exists, create a minimal Student Leave Application doctype with: student, from_date, to_date, reason, status, approved_by fields.

2. **LMS Doctype Structure**
   - What we know: CONTEXT.md says "Full CRUD against Frappe LMS doctypes (LMS Course, LMS Assignment, LMS Quiz)".
   - What's unclear: Whether Frappe Education's LMS module is installed and which exact doctypes/fields are available.
   - Recommendation: During Wave 0, verify LMS doctype availability. Build API layer with graceful degradation if LMS module is not present. The LMS CRUD forms should be the last feature implemented to allow time for doctype verification.

3. **Course Schedule vs Teaching Assignment for Attendance**
   - What we know: AttendanceManager.mark_attendance takes `course_schedule` (from Education module's Course Schedule doctype). Teaching Assignment Schedule is a separate child table.
   - What's unclear: Whether Course Schedule records are being created from Teaching Assignments or independently.
   - Recommendation: The faculty API should accept Teaching Assignment as context but resolve to Course Schedule for the actual Student Attendance records, since Student Attendance has a `course_schedule` field linking to Education's Course Schedule.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest 3.2.4 + @vue/test-utils 2.4.6 |
| Config file | `portal-vue/vitest.config.js` |
| Quick run command | `cd portal-vue && npx vitest run --reporter=verbose` |
| Full suite command | `cd portal-vue && npx vitest run` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FCTY-01 | Timetable displays today's classes | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/TimetableToday.test.js -x` | Wave 0 |
| FCTY-02 | Attendance bulk-select and submit | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/AttendanceMarker.test.js -x` | Wave 0 |
| FCTY-03 | Grade grid cell editing, Tab/Enter nav, auto-save | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/FacultyGradeGrid.test.js -x` | Wave 0 |
| FCTY-04 | Student list with expandable rows | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/StudentListView.test.js -x` | Wave 0 |
| FCTY-05 | Dashboard KPI cards with pending task counts | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/FacultyDashboard.test.js -x` | Wave 0 |
| FCTY-06 | Announcements display and filtering | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/FacultyNotices.test.js -x` | Wave 0 |
| FCTY-07 | Performance analytics charts render with data | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/PerformanceAnalytics.test.js -x` | Wave 0 |
| FCTY-08 | Student leave approve/reject actions | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/StudentLeaveQueue.test.js -x` | Wave 0 |
| FCTY-09 | LMS course list and content CRUD | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/LmsContentManager.test.js -x` | Wave 0 |
| FCTY-10 | Research publications + OBE heatmap | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/ObeAttainment.test.js -x` | Wave 0 |
| FCTY-11 | Leave balance display + submission | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/LeaveBalanceCards.test.js -x` | Wave 0 |
| FCTY-12 | Workload KPIs + heatmap render | unit | `cd portal-vue && npx vitest run src/components/faculty/__tests__/WorkloadSummary.test.js -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd portal-vue && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd portal-vue && npx vitest run`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `portal-vue/src/components/faculty/__tests__/` -- directory and all test files for 12 requirements
- [ ] `portal-vue/src/components/faculty/__tests__/faculty-setup.js` -- shared fixtures (mock faculty data, timetable data, attendance data, grade data)
- [ ] Framework install: none needed -- vitest already configured and passing 37 tests from Phase 2

## Sources

### Primary (HIGH confidence)
- Existing codebase: `university_portals/api/portal_api.py` -- established API pattern
- Existing codebase: `university_academics/attendance.py` -- AttendanceManager with mark_attendance
- Existing codebase: `university_academics/timetable.py` -- TimetableGenerator with get_timetable
- Existing codebase: `faculty_management/doctype/teaching_assignment/teaching_assignment.py` -- schedule conflicts, workload calculation
- Existing codebase: `overrides/assessment_result.py` -- UniversityAssessmentResult with grading logic
- Existing codebase: `accreditation/attainment_calculator.py` -- COPOAttainmentCalculator
- Existing codebase: `faculty_management/report/faculty_workload_summary/` -- workload report
- Phase 2 output: 8 shared components + 6 composables (all tested)
- Phase 3 UI-SPEC: `03-UI-SPEC.md` -- complete visual contracts

### Secondary (MEDIUM confidence)
- Faculty leave events: `faculty_management/leave_events.py` -- leave impact calculation pattern
- Teaching Assignment JSON schema -- field definitions verified

### Tertiary (LOW confidence)
- LMS doctype availability -- needs runtime verification
- Student Leave Application doctype existence -- needs verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already installed and tested in Phase 2
- Architecture: HIGH -- follows established portal_api.py pattern, all doctypes verified in codebase
- Pitfalls: HIGH -- identified from actual code review (duplicate attendance, data source mismatch, grade grid performance)
- LMS integration: LOW -- LMS doctype structure needs runtime verification

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable -- no external dependencies changing)

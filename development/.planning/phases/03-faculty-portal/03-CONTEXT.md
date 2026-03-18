# Phase 3: Faculty Portal - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Faculty can manage their complete daily teaching workflow from the portal without needing Frappe desk. This covers: timetable viewing, attendance marking (bulk), grade entry (spreadsheet grid), student lists, pending tasks dashboard, leave management, student leave approval, LMS course content management, research publications, OBE CO/PO attainment, workload summary, and institutional announcements. 12 requirements (FCTY-01 through FCTY-12).

</domain>

<decisions>
## Implementation Decisions

### Attendance Marking Flow (FCTY-01, FCTY-02)
- **Default state**: All students start as Present. Faculty unchecks the 2–5 absent students. Fastest for typical 90%+ attendance days.
- **Class selection**: Primary flow is today's timetable list with "Mark Attendance" button per class. Classes already marked are greyed out. A "Mark for another date" option allows backdating/manual course+date selection.
- **Submission**: Explicit "Submit Attendance" button — one API call, clear confirmation. Faculty can undo before submit.
- **Post-submit feedback**: Toast notification with counts: "54 Present, 6 Absent (90%)". Non-blocking — faculty can move to next class immediately.
- **Component**: Uses DataTable multi-select checkboxes from Phase 2 with present-by-default pre-selection.

### Grade Entry (FCTY-03, FCTY-07)
- **Grid type**: Custom editable grid component (FacultyGradeGrid) — NOT the read-only DataTable. Spreadsheet-like: student rows, assessment columns, editable cells. Tab/Enter navigation between cells. Google Sheets feel.
- **Save strategy**: Auto-save drafts per cell (500ms debounce, green checkmark per cell). Plus explicit "Submit Grades" button to finalize/lock. Two states: draft (editable) and submitted (locked).
- **Mark types**: Supports both numeric marks (78/100) and direct grade letters depending on assessment type. System shows computed grade in adjacent read-only column for marks-based entries.
- **Analytics**: Side panel updates live as faculty enters grades — grade distribution bar chart, class average, pass/fail count, at-risk students (below threshold). Uses ChartWrapper from Phase 2.

### Dashboard & Navigation Layout (FCTY-05)
- **Landing page (/faculty)**: Combined layout — pending tasks section at top with action buttons (KPI cards: classes today, unmarked attendance count, pending grades, pending leave requests), then overview section below with charts/summaries.
- **Pending tasks**: Clickable with direct navigation. "Unmarked attendance (3)" clicks → goes to attendance page filtered to today's unmarked classes.
- **Navigation structure**: Tab-based page organization. Fewer top-level sidebar items (3–4), each page uses tabs for sub-features. E.g., "Teaching" page has Timetable/Attendance/Grades/Students tabs.
- **Timetable**: Embedded in dashboard as today's compact class list AND available as a dedicated /faculty/timetable page showing full weekly grid.

### Leave Management (FCTY-08, FCTY-11)
- **Faculty's own leave**: Claude's discretion — balance display + submission form using existing HRMS Leave Application doctype.
- **Student leave approval queue**: DataTable with inline Approve/Reject buttons per row. Student name, dates, reason columns. Bulk approve via multi-select checkboxes.

### LMS Course Management (FCTY-09)
- **Depth**: Full inline management — create/edit course content, assignments, quizzes all within the portal. Full CRUD against Frappe LMS doctypes. NOT read-only, NOT link-to-Frappe.

### Research & OBE Views (FCTY-10)
- **Research publications**: Interactive with drill-down. List of publications with counts by type. Click a publication to see full details (authors, journal, year, citations).
- **OBE CO/PO attainment**: Interactive drill-down. CO-PO attainment table for faculty's courses. Click a CO to drill into student-level attainment data.

### Announcements & Notices (FCTY-06)
- **Display**: NotificationPanel (Phase 2) for recent/unread alerts in real-time + dedicated archive page with search and filters.
- **Categorization**: Filter by category (academic, administrative, emergency). Color-code emergency notices red. Uses Notice Board doctype categories.

### Student List & Performance (FCTY-04, FCTY-07)
- **Student list**: DataTable with student photo/avatar, name, roll number, enrollment number, attendance %, current grade. Server-side pagination.
- **Student detail**: Inline expandable row — click to expand and show attendance history, all assessment marks, grade trend. No page navigation.
- **Performance analytics**: Full suite — grade distribution bar chart, attendance correlation, trend over assessments, comparison with previous batches. Multiple charts per course.

### Workload Summary (FCTY-12)
- **Visualization**: KPI cards at top (total hours/week, total courses, total credits, total students) + weekly heatmap (day × timeslot) showing teaching load.
- **Comparison**: Each KPI card shows personal value alongside department average ("You: 18hrs | Dept avg: 16hrs"). Data from existing faculty_workload_summary report.

### Claude's Discretion
- Faculty leave form layout and UX details
- Exact tab groupings and sidebar item labels
- Empty states for all views
- Loading/error states
- API endpoint naming and response structure
- LMS CRUD form design details
- Mobile responsive breakpoints

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — FCTY-01 through FCTY-12 (all 12 faculty portal requirements)

### Portal foundation (Phase 1 output)
- `portal-vue/src/main.js` — App bootstrap; Pinia + Vue Router initialization
- `portal-vue/src/stores/session.js` — Pinia session store; `roles[]` and `allowed_modules[]`
- `portal-vue/src/config/navigation.js` — Single source of truth for sidebar/route items; faculty routes already scaffolded
- `portal-vue/src/router/index.js` — Route definitions; faculty routes at `/faculty`, `/faculty/attendance`, `/faculty/grades` as ComingSoon placeholders
- `portal-vue/src/layouts/PortalLayout.vue` — Shell layout; components slot into `<main>` area
- `portal-vue/src/composables/useFrappe.js` — Frappe API wrapper for data fetching

### Shared components (Phase 2 output)
- `portal-vue/src/components/shared/KpiCard.vue` — KPI counter card (value, label, trend, status color)
- `portal-vue/src/components/shared/ChartWrapper.vue` — ApexCharts (Line, Bar, Heatmap) with drill-down events
- `portal-vue/src/components/shared/DataTable.vue` — TanStack Table with server-side pagination, multi-select, export
- `portal-vue/src/components/shared/FilterBar.vue` — Date range, academic year, department, program selectors
- `portal-vue/src/components/shared/NotificationPanel.vue` — Notification panel with read/unread/dismiss
- `portal-vue/src/components/shared/ReportViewer.vue` — Frappe report viewer with dynamic filters
- `portal-vue/src/components/shared/SkeletonLoader.vue` — Loading skeleton component
- `portal-vue/src/composables/useExportPdf.js` — PDF export via jsPDF
- `portal-vue/src/composables/useExportExcel.js` — Excel export via ExcelJS
- `portal-vue/src/composables/useReportRunner.js` — Frappe report API wrapper

### Faculty management module (backend)
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/teaching_assignment/` — Teaching assignment doctype (course, instructor, schedule)
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/faculty_profile/` — Faculty profile with employee link
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/faculty_publication/` — Publications doctype
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/faculty_research_project/` — Research projects
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/faculty_award/` — Awards
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/employee_qualification/` — Qualifications
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/student_feedback/` — Student feedback
- `frappe-bench/apps/university_erp/university_erp/faculty_management/doctype/workload_distributor/` — Workload distribution
- `frappe-bench/apps/university_erp/university_erp/faculty_management/leave_events.py` — Leave event handlers

### Faculty reports (existing)
- `frappe-bench/apps/university_erp/university_erp/faculty_management/report/faculty_workload_summary/` — Workload summary report (used for FCTY-12 comparison data)
- `frappe-bench/apps/university_erp/university_erp/faculty_management/report/faculty_directory/` — Faculty directory report
- `frappe-bench/apps/university_erp/university_erp/faculty_management/report/leave_utilization_report/` — Leave utilization report
- `frappe-bench/apps/university_erp/university_erp/faculty_management/report/department_hr_summary/` — Department HR summary

### Academics module (attendance, timetable, CBCS)
- `frappe-bench/apps/university_erp/university_erp/university_academics/attendance.py` — Attendance logic
- `frappe-bench/apps/university_erp/university_erp/university_academics/timetable.py` — Timetable logic
- `frappe-bench/apps/university_erp/university_erp/university_academics/cbcs.py` — CBCS/credit system logic

### Existing portal API pattern
- `frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py` — Student portal API pattern (get_student_dashboard, get_student_timetable, etc.); faculty API should follow same pattern

### Assessment & grading
- `frappe-bench/apps/university_erp/university_erp/overrides/assessment_result.py` — Assessment result override (grading logic)
- `frappe-bench/apps/university_erp/university_erp/overrides/course.py` — Course override

### OBE / Accreditation
- `frappe-bench/apps/university_erp/university_erp/university_erp/accreditation/attainment_calculator.py` — CO/PO attainment calculation

### CSS/design tokens
- `frappe-bench/apps/university_erp/university_erp/public/css/theme/variables.css` — CSS custom properties
- `.planning/phases/02-shared-component-library/02-UI-SPEC.md` — UI design contract (typography: 12/14/16/24px, weights: 400/600, colors, dark mode)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **8 shared components** from Phase 2: KpiCard, ChartWrapper, DataTable, FilterBar, NotificationPanel, ReportViewer, SkeletonLoader, ToastNotification — all tested and ready
- **6 composables**: useFrappe (API calls), useExportPdf, useExportExcel, useReportRunner, useThemeColors, useToast
- **Pinia session store**: `roles[]` available — can check `University Faculty` role for auth guards
- **Navigation config**: Faculty routes already scaffolded at `/faculty`, `/faculty/attendance`, `/faculty/grades` — need to replace ComingSoon placeholders with real components and add new routes

### Established Patterns
- **Props-only components**: All Phase 2 shared components are dumb/presentational. Faculty views (smart components) fetch data via useFrappe and pass as props.
- **DataTable multi-select + selection-change event**: Ready for bulk attendance marking — parent component handles the submit action.
- **ChartWrapper drill-down events**: Charts emit drill-down event; parent handles navigation — ready for analytics drill-downs.
- **FilterBar filter-change events**: Emit filter state; parent passes to data fetch — ready for academic year/date filtering.
- **CSS custom properties**: All components use `var(--*)` tokens from variables.css — dark mode works automatically.

### Integration Points
- Faculty routes replace ComingSoon components in `portal-vue/src/router/index.js`
- Navigation items for faculty already exist in `portal-vue/src/config/navigation.js` — may need restructuring for tab-based layout
- Backend API endpoints needed: new faculty-specific whitelisted methods in `university_portals/api/` following the `portal_api.py` student pattern
- Attendance uses Education app's `Student Attendance` doctype
- Grades use Education app's `Assessment Result` doctype
- Leave uses HRMS `Leave Application` doctype
- LMS uses Education app's LMS doctypes (LMS Course, LMS Assignment, LMS Quiz)
- Timetable data from `university_academics/timetable.py` and `Teaching Assignment` doctype

</code_context>

<specifics>
## Specific Ideas

- Combined landing page: pending tasks (action-oriented) at top, overview charts below — faculty sees what needs doing NOW before browsing analytics.
- Tab-based page organization — fewer sidebar items, sub-features as tabs within each page. E.g., a "Teaching" page with Timetable/Attendance/Grades/Students tabs.
- Grade entry grid should feel like Google Sheets — tab between cells, auto-save, immediate visual feedback.
- Full inline LMS management — this is NOT read-only. Faculty should be able to create and edit course content, assignments, and quizzes entirely within the portal.
- Interactive drill-down for research publications and OBE CO/PO — not just summary tables.
- Workload KPI cards show personal vs department average for context.
- Full analytics suite per course — grade distribution, attendance correlation, assessment trends, batch comparison.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-faculty-portal*
*Context gathered: 2026-03-18*

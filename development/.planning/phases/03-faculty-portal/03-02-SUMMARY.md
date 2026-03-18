---
phase: 03-faculty-portal
plan: 02
subsystem: ui
tags: [vue3, frappe-api, faculty-portal, grade-grid, student-list, analytics, vitest, tdd]

# Dependency graph
requires:
  - phase: 03-faculty-portal
    plan: 01
    provides: faculty_api.py with stub endpoints, useFacultyApi.js, TabLayout, FacultyTeaching with placeholder tabs, faculty-setup.js
provides:
  - FacultyGradeGrid.vue spreadsheet-like editable grade grid with Tab/Enter keyboard navigation, 500ms debounced auto-save, at-risk row highlighting, submit/lock
  - GradeAnalyticsPanel.vue side panel with grade distribution bar chart, class average, pass/fail/at-risk KPIs
  - StudentListView.vue paginated student table with avatar, attendance % color coding, expandable detail rows
  - StudentDetailPanel.vue inline expandable panel with attendance history chart, assessment marks table, grade trend chart
  - PerformanceAnalytics.vue 4-chart analytics page (grade distribution, attendance correlation, assessment trend, batch comparison)
  - Backend 7 active endpoints replacing stubs (get_students_for_grading, save_draft_grade, submit_grades, get_grade_analytics, get_student_list, get_student_detail, get_performance_analytics)
  - FacultyTeaching.vue Grades and Students tabs wired with live components replacing placeholders
  - Mock fixtures: mockStudentsForGrading, mockGradeAnalytics, mockStudentList, mockStudentDetail, mockPerformanceAnalytics
affects: [03-03-faculty-portal, 04-hod-portal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - shallowRef/shallowReactive for grade matrix performance (avoid deep reactivity on large data)
    - debounced auto-save per cell with state Map tracking idle/saving/saved/error
    - ref-based cell registry for keyboard navigation between grid cells
    - attendance percentage color coding with 75/60 threshold breakpoints

# Key files
key-files:
  created:
    - portal-vue/src/components/faculty/FacultyGradeGrid.vue
    - portal-vue/src/components/faculty/GradeAnalyticsPanel.vue
    - portal-vue/src/components/faculty/StudentListView.vue
    - portal-vue/src/components/faculty/StudentDetailPanel.vue
    - portal-vue/src/components/faculty/PerformanceAnalytics.vue
    - portal-vue/src/components/faculty/__tests__/FacultyGradeGrid.test.js
    - portal-vue/src/components/faculty/__tests__/StudentListView.test.js
    - portal-vue/src/components/faculty/__tests__/PerformanceAnalytics.test.js
  modified:
    - frappe-bench/apps/university_erp/university_erp/university_portals/api/faculty_api.py
    - portal-vue/src/components/faculty/FacultyTeaching.vue
    - portal-vue/src/components/faculty/__tests__/faculty-setup.js

# Decisions
decisions:
  - FacultyGradeGrid is a custom component (not DataTable) for spreadsheet-like editing with cell-level auto-save
  - _verify_faculty_teaches_course helper centralizes Teaching Assignment authorization check for all grade/student endpoints
  - Grade analytics side panel receives data via prop from parent (FacultyTeaching refetches on each save event)
  - StudentListView uses manual pagination with direct SQL for server-side student list with attendance enrichment
  - PerformanceAnalytics uses attendance bucket ranges for correlation chart instead of scatter plot

# Metrics
metrics:
  duration: 18min
  completed: 2026-03-18
  tasks_completed: 2
  tasks_total: 2
  tests_added: 16
  tests_total: 102
  files_created: 8
  files_modified: 3
---

# Phase 3 Plan 02: Grade Grid, Student Lists & Performance Analytics Summary

Spreadsheet-like grade entry grid with Tab/Enter keyboard navigation, debounced auto-save, and live analytics side panel; student list with expandable detail rows and attendance color coding; 4-chart performance analytics page -- all wired into FacultyTeaching Grades and Students tabs replacing placeholders.

## Tasks Completed

### Task 1: Backend grade/student endpoints + FacultyGradeGrid + GradeAnalyticsPanel

**Commit:** `e53ab03e`

- Replaced 7 stub endpoints in faculty_api.py with full implementations using parameterized SQL
- Added `_verify_faculty_teaches_course()` authorization helper
- Created FacultyGradeGrid.vue (283 lines): custom editable grid with `role="grid"`, `role="gridcell"`, `@keydown.tab.prevent`, `@keydown.enter.prevent`, 500ms debounced saveDraftGrade via shallowReactive cell state Map, green checkmark saved indicator with fade animation, at-risk row highlighting (< 40% threshold with `--error-tint`), "Submit Grades" with lock state and toast, "Grades have been submitted and are now locked for editing" banner
- Created GradeAnalyticsPanel.vue (92 lines): ChartWrapper bar chart with grade distribution, class average, pass/fail/at-risk KPI text
- Added mock fixtures to faculty-setup.js: mockStudentsForGrading, mockGradeAnalytics, mockStudentList, mockStudentDetail, mockPerformanceAnalytics
- 9 tests: grid rendering, keyboard nav, debounce, saved indicator, submit/lock, at-risk, computed grade, chart wrapper, KPI text

### Task 2: StudentListView + StudentDetailPanel + PerformanceAnalytics + FacultyTeaching tab wiring

**Commit:** `3c67a2bc`

- Created StudentListView.vue (357 lines): manual server-side pagination, avatar with initials fallback, attendance % color coding (>= 75 success, >= 60 warning, < 60 error), `expand_more` icon with expandable StudentDetailPanel inline, search with 300ms debounce, "View Analytics" button
- Created StudentDetailPanel.vue (176 lines): attendance history line chart, assessment marks compact table, grade trend spark-line, 3-section desktop layout stacking on mobile
- Created PerformanceAnalytics.vue (146 lines): 4 ChartWrapper instances in 2x2 grid (grade distribution bar, attendance correlation bar, assessment trend line, batch comparison bar), "Back to Students" button
- Updated FacultyTeaching.vue: imported FacultyGradeGrid, GradeAnalyticsPanel, StudentListView, PerformanceAnalytics; replaced Grades tab placeholder with grid + analytics side-by-side flex layout; replaced Students tab placeholder with StudentListView + PerformanceAnalytics toggle; added shared course state and analytics refresh handler
- 7 tests: student list rendering, expand panel, attendance color coding, detail panel chart + marks, 4-chart count, back button, API call verification

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

```
All Plan 02 tests pass: 16/16
Full suite passes: 102/102 across 22 files
Grade grid keyboard navigation count: 2 (tab + enter)
Backend grade endpoints count: 7/7
FacultyTeaching "coming soon" placeholders: 0
```

## Self-Check: PASSED

All files exist and all commits verified.

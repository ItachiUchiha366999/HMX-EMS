---
phase: 03-faculty-portal
plan: 03
subsystem: ui, api
tags: [vue, frappe, leave-management, lms, research, obe, workload, heatmap]

requires:
  - phase: 02-shared-component-library
    provides: KpiCard, ChartWrapper, DataTable, SkeletonLoader shared components
  - phase: 03-faculty-portal (plan 01)
    provides: faculty_api.py scaffold with all 27 endpoints, useFacultyApi composable, TabLayout, faculty-setup.js test fixtures

provides:
  - 14 backend endpoints replacing Plan 03 stubs (leave, LMS, research, OBE, workload)
  - 10 Vue components for leave/LMS/research/OBE/workload features
  - FacultyWork page with 4 functional tabs (Leave, Workload, Research, OBE)
  - Plan 03 mock fixtures for all new data shapes

affects: [04-management-dashboards, 05-parent-guardian-portal]

tech-stack:
  added: []
  patterns:
    - "Child table publication query via Faculty Profile parent"
    - "COPOAttainmentCalculator integration for OBE heatmap"
    - "Department average calculation from faculty_workload_summary report"
    - "Graceful degradation via frappe.db.exists for optional doctypes (LMS, Student Leave Application)"
    - "Inline reject reason input pattern for destructive actions"

key-files:
  created:
    - portal-vue/src/components/faculty/LeaveBalanceCards.vue
    - portal-vue/src/components/faculty/LeaveApplyForm.vue
    - portal-vue/src/components/faculty/StudentLeaveQueue.vue
    - portal-vue/src/components/faculty/LmsCourseList.vue
    - portal-vue/src/components/faculty/LmsContentManager.vue
    - portal-vue/src/components/faculty/LmsContentForm.vue
    - portal-vue/src/components/faculty/ResearchPublications.vue
    - portal-vue/src/components/faculty/ObeAttainment.vue
    - portal-vue/src/components/faculty/WorkloadSummary.vue
    - portal-vue/src/components/faculty/__tests__/LeaveBalanceCards.test.js
    - portal-vue/src/components/faculty/__tests__/StudentLeaveQueue.test.js
    - portal-vue/src/components/faculty/__tests__/LmsContentManager.test.js
    - portal-vue/src/components/faculty/__tests__/ObeAttainment.test.js
    - portal-vue/src/components/faculty/__tests__/WorkloadSummary.test.js
  modified:
    - frappe-bench/apps/university_erp/university_erp/university_portals/api/faculty_api.py
    - portal-vue/src/components/faculty/FacultyWork.vue
    - portal-vue/src/components/faculty/__tests__/faculty-setup.js

key-decisions:
  - "Faculty Publication queried as child table on Faculty Profile (istable=1), not standalone doctype"
  - "get_copo_matrix uses COPOAttainmentCalculator from accreditation module with graceful fallback"
  - "get_workload_summary computes department average by running faculty_workload_summary report for all dept faculty"
  - "Student leave approval uses Student Leave Application doctype with exists() guard"
  - "LMS endpoints check for LMS Course/Lesson/Assignment/Quiz doctypes individually for granular degradation"
  - "WorkloadSummary warning threshold at 1.1x department average (10% above)"

patterns-established:
  - "Inline reject pattern: click Reject shows text input + Confirm Reject button below row"
  - "Bulk action pattern: multi-select checkboxes + action bar above table"
  - "Slide-over form pattern: 320-480px panel from right with form fields and Submit/Discard buttons"
  - "Heatmap drill-down: click row to fetch student-level data, Back to Matrix button to return"

metrics:
  duration: 12min
  completed: "2026-03-18T21:48:00Z"
  tasks_completed: 2
  tasks_total: 2
  tests_added: 17
  tests_total: 95
  files_created: 14
  files_modified: 3
---

# Phase 3 Plan 03: Leave/LMS/Research/OBE/Workload Summary

Faculty leave balance with color-coded progress bars, student leave approval queue with inline reject and bulk approve, LMS content CRUD with delete confirmation, research publications with type KPIs and detail expansion, CO-PO heatmap with student drill-down, workload KPIs with department average comparison and weekly heatmap -- all wired into FacultyWork 4-tab page.

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | 413b1f3b | feat(03-03): backend leave/LMS/research/OBE/workload endpoints + leave components + student leave queue |
| 2 | b2a2c56c | feat(03-03): LMS content management, research publications, OBE attainment, workload summary, FacultyWork page |

## Task 1: Backend endpoints + Leave components + StudentLeaveQueue

**Commit:** 413b1f3b

Replaced all 14 Plan 03 stub endpoints in faculty_api.py with full implementations:
- `get_leave_balance` queries Leave Allocation and Leave Application for used/total per leave type
- `apply_leave` creates Leave Application with status Open
- `get_leave_history` returns paginated leave applications for current faculty
- `get_student_leave_requests` / `approve_student_leave` / `reject_student_leave` for student leave workflow
- `get_lms_courses` / `get_lms_course_content` / `save_lms_content` / `delete_lms_content` with LMS doctype existence checks
- `get_publications` queries Faculty Publication child table on Faculty Profile
- `get_copo_matrix` / `get_copo_student_detail` using COPOAttainmentCalculator
- `get_workload_summary` with personal KPIs + department averages + weekly heatmap

Created 3 Vue components:
- **LeaveBalanceCards.vue**: 3-column grid with progress bars (green < 75%, warning 75-90%, red > 90%)
- **LeaveApplyForm.vue**: Slide-over panel (320px) with Leave Type/Date/Reason form
- **StudentLeaveQueue.vue**: Custom table with inline approve/reject, bulk approve, empty state

**Tests:** 8 passing (LeaveBalanceCards: 3, StudentLeaveQueue: 5)

## Task 2: LMS + Research + OBE + Workload views + FacultyWork page

**Commit:** b2a2c56c

Created 7 Vue components:
- **LmsCourseList.vue**: Course cards with content counts and Manage Content button
- **LmsContentManager.vue**: Sectioned content list with Add/Edit/Delete per type, delete confirmation modal
- **LmsContentForm.vue**: Slide-over (480px) with dynamic fields per content type (Lesson/Assignment/Quiz)
- **ResearchPublications.vue**: Type count KPIs (KpiCard) + expandable publication list with DOI links
- **ObeAttainment.vue**: Course selector + ChartWrapper heatmap + CO row click for student drill-down
- **WorkloadSummary.vue**: 4 KpiCards with dept avg comparison + weekly teaching heatmap (ChartWrapper)
- **FacultyWork.vue**: Replaced placeholder with TabLayout (Leave/Workload/Research/OBE tabs)

**Tests:** 9 passing (LmsContentManager: 3, ObeAttainment: 3, WorkloadSummary: 3)

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- All 95 tests pass across 20 test files (full regression)
- 27 @frappe.whitelist endpoints in faculty_api.py
- 0 "Coming soon" placeholders in FacultyWork.vue
- LMS graceful degradation via frappe.db.exists confirmed (14 existence checks)

## Self-Check: PASSED

All 15 created files verified present. Both commits (413b1f3b, b2a2c56c) verified in git log.

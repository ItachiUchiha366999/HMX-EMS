---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: completed
stopped_at: Phase 3 complete (gaps resolved)
last_updated: "2026-03-18T22:19:34.474Z"
last_activity: 2026-03-18 - Completed 03-03-PLAN.md (Leave/LMS/Research/OBE/Workload with 95 passing tests)
progress:
  total_phases: 7
  completed_phases: 3
  total_plans: 8
  completed_plans: 8
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-17)

**Core value:** University leadership can make data-driven decisions through real-time dashboards with drill-down capability, while faculty, HODs, and parents have self-service portal access to the information and actions relevant to their role.
**Current focus:** Phase 3: Faculty Portal

## Current Position

Phase: 3 of 7 (Faculty Portal)
Plan: 3 of 3 in current phase (COMPLETE)
Status: Phase 03 Complete
Last activity: 2026-03-18 - Completed 03-03-PLAN.md (Leave/LMS/Research/OBE/Workload with 95 passing tests)

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Average duration: 9min
- Total execution time: 1.2 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation-security-hardening | 3 | 20min | 7min |
| 02-shared-component-library | 2 | 16min | 8min |
| 03-faculty-portal | 3 | 37min | 12min |

**Recent Trend:**
- Last 5 plans: 8min, 8min, 13min, 12min, 12min
- Trend: stable (Phase 3 at ~12min per plan)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: 7 phases derived from 57 requirements; Phases 3/4/5 can parallelize after Phase 2
- [Roadmap]: ANLT-01/02 mapped to Phase 7 (cross-portal export verification) vs COMP-05/06 in Phase 2 (component build)
- [Roadmap]: MGMT-10 mapped to Phase 7 (scheduled reports) alongside ANLT-05 since both are email delivery
- [01-01]: Used frappe.db.sql(query, values=dict) for parameterized SQL -- standard Frappe pattern
- [01-01]: Permission check uses KPI Definition doctype for KPI endpoints, Custom Dashboard for get_quick_stats
- [01-01]: Kept mock/fallback data in executive_dashboard.py for graceful degradation when doctypes missing
- [01-02]: Pinia session store fetches once at boot (main.js), router guard reads store synchronously -- no per-route API calls
- [01-02]: portal-vue/ build output committed to public/portal/ matching student-portal-spa pattern
- [01-02]: navigation.js is single source of truth for sidebar items and route definitions -- future phases add entries here
- [01-03]: All 8 FOUND-XX requirements verified complete through automated + human browser verification
- [01-03]: Integration plan pattern: automated checks first, then human-verify in browser
- [02-01]: useFrappe adapted from student-portal: removed PORTAL_API prefix, call() uses /api/method/ directly, added getList()
- [02-01]: useThemeColors resolves CSS vars via getComputedStyle for ApexCharts (needs hex, not var() references)
- [02-01]: KpiCard uses --font-semibold (not --font-bold) per UI-SPEC typography contract
- [02-01]: ChartWrapper registers vue3-apexcharts locally, not globally in main.js
- [02-01]: TDD red-green cycle: tests committed first as failing, then components committed to pass
- [02-02]: TanStack Table with manualPagination and manualSorting for server-side data control
- [02-02]: ExcelJS loaded via dynamic import() to avoid 500KB bundle penalty
- [02-02]: useReportRunner normalizes both string and object column formats from Frappe
- [02-02]: vi.hoisted() pattern for mock variable references in vitest factory mocks
- [03-01]: faculty_api.py contains ALL 27 endpoints (6 active + 21 stubs) to avoid multi-plan file conflicts
- [03-01]: get_current_faculty() maps user -> Employee with custom_is_faculty=1, following portal_api.py pattern
- [03-01]: submit_attendance uses frappe.db.count idempotency check before creating Student Attendance records
- [03-01]: Tab-based navigation: 4 sidebar items (Dashboard, Teaching, My Work, Notices) with sub-tabs per page
- [03-01]: Old /faculty/attendance and /faculty/grades redirect to /faculty/teaching?tab=attendance and ?tab=grades
- [03-01]: AttendanceMarker pre-checks all students as Present (present-by-default per user decision)
- [03-01]: TimetableGrid uses Teaching Assignment Schedule as primary data source (has instructor mapping)
- [03-02]: FacultyGradeGrid is custom component (not DataTable) with shallowRef/shallowReactive for grade matrix performance
- [03-02]: _verify_faculty_teaches_course helper centralizes Teaching Assignment auth check for all grade/student endpoints
- [03-02]: Grade analytics side panel receives data via prop from parent (FacultyTeaching refetches on save)
- [03-02]: StudentListView uses manual pagination with server-side SQL for attendance-enriched student list
- [03-02]: PerformanceAnalytics uses attendance bucket ranges for correlation chart
- [03-03]: Faculty Publication queried as child table on Faculty Profile (istable=1 in doctype JSON)
- [03-03]: get_copo_matrix integrates COPOAttainmentCalculator with graceful ImportError fallback
- [03-03]: get_workload_summary runs faculty_workload_summary report for dept average calculation
- [03-03]: LMS endpoints use frappe.db.exists per-doctype (LMS Course, Lesson, Assignment, Quiz) for granular degradation
- [03-03]: WorkloadSummary uses 1.1x threshold for warning status when personal > department avg

### Roadmap Evolution

- Phase 3.1 inserted after Phase 3: Cross-App Integration Audit & Accessibility Testing (URGENT) — audit duplicate doctypes across Education/ERPNext/university_erp, test all cross-app connections, verify doctype/report availability, test dashboard/report data flows, and verify UI accessibility

### Pending Todos

None yet.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260317-sz1 | Seed demo data per DEMO_SEED_PLAN.md and fill missing doctype data (CO-PO mapping etc) | 2026-03-17 | n/a | [260317-sz1-seed-demo-data-per-demo-seed-plan-md-and](.planning/quick/260317-sz1-seed-demo-data-per-demo-seed-plan-md-and/) |

### Blockers/Concerns

- [Phase 1]: ~~SQL injection in dashboard_engine.py is a production blocker~~ RESOLVED in 01-01
- [Phase 4]: Management role names (VC, Registrar, etc.) need verification against actual Frappe Role definitions
- [Phase 6]: Frappe workflow engine integration for HOD approval queues needs API-level verification

## Session Continuity

Last session: 2026-03-18T22:19:34.452Z
Stopped at: Phase 3 complete (gaps resolved)
Resume file: .planning/phases/03-faculty-portal/03-VERIFICATION.md

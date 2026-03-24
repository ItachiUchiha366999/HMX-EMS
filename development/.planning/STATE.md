---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
stopped_at: Completed 03.3-04-PLAN.md (verified and finalized)
last_updated: "2026-03-24T16:11:47.069Z"
progress:
  total_phases: 11
  completed_phases: 5
  total_plans: 18
  completed_plans: 18
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-19)

**Core value:** University leadership can make data-driven decisions through real-time dashboards with drill-down capability, while students, faculty, HODs, and parents have self-service portal access through a unified portal UI.
**Current focus:** Phase 03.3 — erpnext-accounts-fork

## Current Position

Phase: 03.4
Plan: Not started

## Performance Metrics

**Velocity:**

- Total plans completed: 9
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
| Phase 03.1 P06 | 16min | 3 tasks | 57 files |
| Phase 03.3 P01 | 20min | 2 tasks | 1053 files |
| Phase 03.3 P03 | 2min | 2 tasks | 78 files |
| Phase 03.3 P02 | 9min | 2 tasks | 219 files |
| Phase 03.3 P04 | 32min | 3 tasks | 11 files |

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
- [03.1-01]: Scripts in university_erp/university_erp/scripts/ (inner package) for Frappe bench execute module resolution
- [03.1-01]: Disk-based scanning (os.walk + json.load) for all doctypes including dead/overridden ones not in DB
- [03.1-01]: Semantic overlap threshold: 60% with 3+ shared targets (reduced 1259 to 260 actionable pairs)
- [03.1-02]: Report audit tests ALL 279 registered reports across all apps, not just university_erp's 59
- [03.1-02]: Faculty API audit discovers endpoints via regex on source (future-proof vs hardcoded list)
- [03.1-02]: custom_is_faculty column missing from Employee table -- root cause of all 27 faculty API endpoint failures
- [03.1-02]: Two-pass report testing: empty filters first, then JS-parsed mandatory filter defaults
- [03.1-03]: vitest-axe axe() used directly (toHaveNoViolations not exported); color-contrast/region disabled in jsdom
- [03.1-03]: --text-muted changed gray-400 to gray-500 for 4.76:1 WCAG AA contrast ratio
- [03.1-03]: New --success-text, --warning-text, --error-text, --info-text CSS vars for accessible text on white backgrounds
- [03.1-04]: Custom fields migrated via explicit script (not hooks.py fixtures) for idempotent rerunnability
- [03.1-04]: Fees.paid_amount derived as (grand_total - outstanding_amount) -- no paid_amount column on Fees doctype
- [03.1-04]: Report parent directories need __init__.py for Frappe module resolution -- created in all 9 dirs
- [03.1-04]: SQL % in string literals must be escaped as %% when using .format() + parameterized queries
- [03.1-05]: GET endpoints tested no-args as Administrator; ACTION/OTHER import-verified only (no data mutation)
- [03.1-05]: 4/9 roles have test users (Admin, Student, Parent, Registrar); 5 need creation for complete coverage
- [03.1-05]: 2 HIGH security findings: Student can access get_dashboard_stats and get_available_dashboards without role checks
- [Phase 03.1]: 488 @whitelist endpoints audited with zero import failures; 2 HIGH security findings: Student can access admin APIs (get_dashboard_stats, get_available_dashboards)
- [03.1-06]: SQL .format() pattern for conditions is acceptable when values use parameterized dict (consistent with Frappe report pattern)
- [03.1-06]: INFO-level SQL findings (table name interpolation in audit/seed scripts) left unfixed -- controlled source values
- [03.1-06]: Education authoritative for Fees, Assessment Result, Student Attendance, Student; university_erp extends via override
- [03.1-06]: Attendance domain MEDIUM risk: dual input channels (Student Attendance Tool vs faculty_api) -- idempotency check exists
- [Phase 03.3]: Stock/warehouse functions stubbed (return empty/0) since university has no inventory
- [Phase 03.3]: allow_regional simplified to no-op passthrough; get_exchange_rate queries Currency Exchange with 1.0 fallback
- [Phase 03.3]: Non-accounts erpnext imports (setup/utilities/stock/buying/selling) stubbed as comments to preserve code structure
- [03.3-03]: Archived 18 report dirs + non_billed_report.py to _archived_reports/ (not deleted) for reversibility
- [03.3-03]: Report title relabeling via report_name JSON field: Customer->Student, Supplier->Vendor, Accounts Receivable->Fee Receivable, Accounts Payable->Vendor Payable
- [Phase 03.3]: Stock/selling/buying imports stubbed as inline functions (not just comments) for runtime safety
- [Phase 03.3]: temporary_flag re-implemented as contextmanager, eliminating erpnext.utilities.regional dependency
- [Phase 03.3]: 57 unused doctype directories archived to _archived/ (POS, Dunning, Subscription, Share, Loyalty, etc.)
- [Phase 03.3]: Payment webhook uses ORM pattern (frappe.get_doc) -- no erpnext.accounts imports needed
- [Phase 03.3]: Archived doctype imports stubbed inline (subscription_plan, loyalty_program) rather than restoring archived dirs
- [Phase 03.3]: JE/PE accounting approval workflows not yet configured -- deferred to Phase 03.4 backend audit

### Roadmap Evolution

- Phase 3.1 inserted after Phase 3: Cross-App Integration Audit (initial audit executed, 3/5 SC passed)
- **Phase 03.1 expanded (2026-03-19)**: Comprehensive System Audit & Fix — full system testing including permissions, ALL APIs, desk/portal UI, SQL scan, business logic duplicates. 10 success criteria (up from 5). Plans 04-06 added.
- **Phase 03.2 inserted: Student Portal Recreation** — recreate all 11 student views in portal-vue with shared components
- **Phase 03.3 inserted: ERPNext Accounts Module Fork** — fork entire Accounts module with student-centric terminology
- **Strategic pivot (2026-03-19)**: Frappe Desk = admin-only backend, portal-vue = frontend for ALL users. ERPNext Accounts being forked. Student portal being recreated in unified portal. Roadmap expanded from 8 to 10 phases.

### Pending Todos

None yet.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260317-sz1 | Seed demo data per DEMO_SEED_PLAN.md and fill missing doctype data (CO-PO mapping etc) | 2026-03-17 | n/a | [260317-sz1-seed-demo-data-per-demo-seed-plan-md-and](.planning/quick/260317-sz1-seed-demo-data-per-demo-seed-plan-md-and/) |

### Blockers/Concerns

- [Phase 1]: ~~SQL injection in dashboard_engine.py is a production blocker~~ RESOLVED in 01-01
- [Phase 03.1]: ~~Employee custom fields not migrated to DB~~ RESOLVED in 03.1-04 (24 custom fields migrated)
- [Phase 03.1]: ~~10 university_erp reports with schema errors~~ RESOLVED in 03.1-04 (all 14 reports fixed)
- [Phase 03.1]: ~~Permission testing never done for any role — unknown gaps~~ RESOLVED in 03.1-05 (9 roles tested, 2 security findings)
- [Phase 03.1]: ~~SQL injection risks in university_erp~~ RESOLVED in 03.1-06 (44 CRITICAL + 18 WARNING remediated to 0)
- [Phase 03.3]: Accounts fork is massive (200+ files) — highest risk phase in the project
- [Phase 4]: Management role names (VC, Registrar, etc.) need verification against actual Frappe Role definitions
- [Phase 6]: Frappe workflow engine integration for HOD approval queues needs API-level verification

## Session Continuity

Last session: 2026-03-24T16:11:47.041Z
Stopped at: Completed 03.3-04-PLAN.md (verified and finalized)
Resume file: None

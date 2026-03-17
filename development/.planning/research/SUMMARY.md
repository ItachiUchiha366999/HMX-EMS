# Project Research Summary

**Project:** University ERP Dashboards, Analytics & Role-Based Portals
**Domain:** Multi-role SPA portal on Frappe v15 / ERPNext (Indian higher education)
**Researched:** 2026-03-17
**Confidence:** HIGH

## Executive Summary

This project extends an existing Frappe v15 + Vue 3 university ERP system with a unified multi-role portal covering faculty, HOD, parent, and management dashboards. The recommended approach is a single Vue 3 SPA with role-based routing and code-splitting — NOT separate apps per role. The existing student portal becomes the `student` module inside a unified app shell, with new modules added alongside it. The significant advantage here is that substantial backend infrastructure already exists: dashboard engine, analytics APIs, KPI system, 58 reports, and portal API scaffolding for all roles. Most of the work is wiring up Vue frontend views to existing Python APIs rather than building from scratch.

The recommended stack additions are minimal and purpose-fit: ApexCharts + vue3-apexcharts for charting, TanStack Vue Table (headless) for data tables, jsPDF + autotable and ExcelJS for exports, and VueUse for composable utilities. These fit cleanly with the existing Tailwind-first approach. The existing Frappe polling pattern (using `useIntervalFn`) is preferred over WebSocket for dashboard KPIs; Socket.IO is reserved for genuine event notifications (approvals, alerts) where it already operates in the codebase.

The highest-risk area is not feature complexity but security and data integrity. Three issues in the existing codebase require remediation before any dashboard goes to production: SQL injection in `dashboard_engine.py`, missing role checks on whitelisted analytics APIs, and N+1 query patterns in `executive_dashboard.py`. Additionally, the parent portal must implement guardian-to-student ownership verification (IDOR risk), and cross-app data consistency must be verified before dashboard data can be trusted. These are Phase 1 blockers.

## Key Findings

### Recommended Stack

The existing stack (Frappe v15, Vue 3, Vue Router 4, Tailwind CSS 3, Vite, MariaDB, Redis) is locked in and the right foundation. New additions are deliberately narrow. ApexCharts (v5.10.4, ~130KB gzipped) handles all chart types needed for management dashboards with declarative Vue integration via vue3-apexcharts. TanStack Vue Table is headless and zero-opinion, making it the correct choice over AG Grid or PrimeVue DataTable which conflict with the Tailwind-first approach. ExcelJS replaces SheetJS entirely — the npm version of SheetJS is 4 years stale with known CVEs. Export libraries (jsPDF, ExcelJS: ~600KB combined) are lazy-loaded on demand. Total always-loaded bundle addition is ~160KB gzipped.

**Core technologies:**
- ApexCharts + vue3-apexcharts: SVG chart rendering — best DX/aesthetics balance for university-scale datasets (never hits 10K+ points where ECharts would win)
- @tanstack/vue-table: Headless data table logic — full Tailwind compatibility, no style conflicts
- jsPDF + jspdf-autotable: Client-side PDF export — deterministic output vs. html2pdf's inconsistent browser rendering
- ExcelJS: Excel generation — proper npm package, full formatting; SheetJS is explicitly excluded (stale, insecure on npm)
- @vueuse/core: VueUse composables — covers auto-refresh, localStorage persistence, visibility-pause, network status out of the box
- Frappe @whitelist() APIs: Backend endpoints — existing pattern in portal_api.py, reuse throughout
- Vue Router meta + guards: Role-based routing — no additional library; meta.roles + beforeEach guard is the standard pattern

### Expected Features

The feature set is well-understood from both the existing codebase and Indian ERP competitor analysis (MasterSoft, Academia, Camu, MyLeadingCampus). The defining insight is that most backend APIs already exist — what is missing are the Vue frontend views and several data aggregation APIs that are currently mocked or incomplete.

**Must have (table stakes) for v1:**
- Role-based auth and routing — gate everything; `get_user_portal_type()` exists but needs management role extension (VC, Registrar, Finance Officer, Dean)
- Shared component library — KPI card, chart wrapper, data table with export, filter bar; reused across every portal
- Faculty portal: timetable, attendance marking, grade entry, pending tasks — APIs scaffolded in portal_api.py
- Management dashboard: 6-8 KPI counters, enrollment trend chart, financial summary, department comparison table, alert panel — backend in executive_dashboard.py (needs N+1 fixes and real aggregation replacing mocked data)
- Parent portal: child selector, attendance summary, grades, fee status — APIs exist or reuse student portal
- Academic year / semester filter on all views
- PDF and Excel export on all data tables

**Should have (differentiators) for v1.x:**
- HOD portal: department analytics, approval workflows, faculty workload, CO-PO attainment views
- Management drill-down navigation (summary -> department -> program -> student) — rare among Indian ERPs, genuine differentiator
- Scheduled reports with email delivery — ScheduledReport doctype is 80% complete
- Parent online fee payment — payment gateway exists for student portal, needs parent-context wrapper
- Comparative year-over-year analytics
- Real-time alert thresholds with WhatsApp notifications

**Defer to v2+:**
- NAAC/NIRF auto-report generation — high value at accreditation time, high complexity
- Student risk scoring (dropout prediction) — requires algorithm design and outcome validation
- Customizable drag-and-drop dashboard widgets — doctypes exist, frontend is complex
- Faculty performance scorecards — requires institutional buy-in on metrics before building

### Architecture Approach

The unified SPA architecture is non-negotiable. A single Vue 3 app at `/portal/` serves all roles via role-based routing with lazy-loaded modules (one Vite chunk per role). `RoleResolver.vue` runs at app boot to determine the user's role and redirect to the correct module. A shared layer of composables and components (`useAuth`, `useFrappe`, `useRole`, `useRealtime`, `useExport`, chart components, KPI cards, data tables) is consumed by all modules. Each role module owns its routes, layouts, views, and composables. The HOD module extends the faculty module — HOD sees all faculty views plus department-level additions.

**Major components:**
1. Unified Portal SPA (`portal-vue/`) — single Vue 3 app, role-based routing, lazy module loading; existing student portal absorbed as `modules/student/`
2. Shared Layer (`shared/`) — composables (useFrappe, useAuth, useRole, useRealtime, useExport), chart components, KPI cards, DataTable, FilterBar; consumed by all role modules
3. Role Modules (`modules/faculty/`, `modules/hod/`, `modules/parent/`, `modules/management/`) — each owns views, composables, routes; HOD extends faculty
4. Portal API Facades (backend per-role Python files) — one aggregated API call per page load; existing `portal_api.py` pattern extended to HOD and management
5. Dashboard Engine (`dashboard_engine.py`) — widget data assembly for management dashboards; drives configuration-based layouts via `Custom Dashboard` doctype
6. Analytics API (`analytics/api.py`) — KPI calculation, trend queries, report execution; pre-computed KPI values stored in `KPI Value` doctype for expensive aggregations

### Critical Pitfalls

1. **SQL injection in dashboard_engine.py** — `query.replace()` string substitution in `_execute_query()` is textbook SQL injection. Replace with parameterized `frappe.db.sql(query, values_dict)` before ANY dashboard reaches production. Phase 1 blocker.

2. **Missing role checks on @frappe.whitelist() analytics APIs** — `get_executive_dashboard_data()` has zero role checks; any authenticated student can call it and see financial data. Add `frappe.only_for(["Vice Chancellor", "Registrar", ...])` or a `@require_role` decorator to every analytics endpoint. Phase 1 blocker.

3. **N+1 query patterns in executive_dashboard.py** — `get_department_performance()` fires 40+ DB queries per dashboard load (per-department loops). Replace with single `GROUP BY` aggregation queries. Dashboard load must stay under 15 queries and 2 seconds with production data. Phase 2 blocker.

4. **Parent portal IDOR vulnerability** — if parent APIs accept `student_id` without verifying the parent-student guardian link, any parent can see any student's data. Build `get_guardian_students(user)` verification utility first; every parent API must cross-reference Student Guardian. Phase 5 blocker.

5. **Cross-app data inconsistency** — 6 Education doctype class overrides plus HRMS/ERPNext integrations create silent data mismatches (Employee count vs. Instructor count, Fees paid_amount vs. GL Entry totals). Run a verification script before building any dashboard that queries across these boundaries. Phase 1 blocker.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation, Security Hardening & Cross-App Verification
**Rationale:** Three security vulnerabilities in the existing codebase (SQL injection, missing permission checks, cross-app data inconsistency) must be resolved before building on top. Building dashboards on a broken foundation creates compounding problems. This phase also restructures the frontend directory for the unified app and establishes the role routing shell — everything else depends on it.
**Delivers:** Secure analytics backend (SQL injection fix, permission decorator), verified data model (cross-app verification script), unified app shell with role-based routing, existing student portal moved into module structure, management role detection (VC/Registrar/Finance Officer/Dean)
**Addresses:** Role-based auth and routing (P1 feature), academic year filter foundation
**Avoids:** SQL injection (CRITICAL), missing permission checks (CRITICAL), cross-app data inconsistency (CRITICAL), mock data shipping to production
**Research flag:** SKIP — patterns are well-documented; this is remediation and structural work with clear specifications from PITFALLS.md and ARCHITECTURE.md

### Phase 2: Shared Component Library & Dashboard Foundations
**Rationale:** Shared components (KPI cards, chart wrappers, data tables, filter bars) are consumed by every role module. Building them once before any module means each module gets consistent, tested primitives. Also addresses the auth caching pitfall (auth fires once on app load, not per-route) and the N+1 query performance issue in the management dashboard backend.
**Delivers:** KPI card, chart wrapper (bar/line/pie/gauge via ApexCharts), DataTable with TanStack, FilterBar, ExportButton, LoadingState/ErrorBoundary/EmptyState, useFrappe/useAuth/useRole composables, N+1 queries fixed in executive_dashboard.py with GROUP BY aggregations
**Uses:** ApexCharts, vue3-apexcharts, @tanstack/vue-table, @vueuse/core from STACK.md
**Implements:** Shared Layer from ARCHITECTURE.md, Pattern 4 (polling stale-while-revalidate for KPIs)
**Avoids:** N+1 query problem, Vue auth guard per-route overhead
**Research flag:** SKIP — ApexCharts, TanStack Table, VueUse are well-documented with clear integration patterns

### Phase 3: Faculty Portal
**Rationale:** Faculty portal is the highest-frequency user touchpoint (daily attendance marking, grade entry). APIs are mostly scaffolded in portal_api.py. Building it after the shared component library means using proven primitives. HOD portal depends on faculty portal, so this must come first.
**Delivers:** FacultyLayout, FacultyDashboard (pending tasks), MyTimetable, AttendanceMarking (bulk-select UI), GradeEntry (spreadsheet-like grid), StudentList per course, LeaveApproval views
**Addresses:** All P1 faculty features
**Implements:** Role module pattern, Backend API Facade pattern (ARCHITECTURE.md Pattern 2)
**Avoids:** N+1 API calls from frontend — one aggregated `get_faculty_dashboard()` call per page load
**Research flag:** SKIP — faculty portal patterns are standard; APIs are scaffolded. Note: HRMS Leave Application integration needs a pre-implementation spike to confirm the cross-app API is accessible.

### Phase 4: Management Dashboards
**Rationale:** Management dashboards have the most existing backend support (DashboardEngine, Analytics APIs, KPI system, executive_dashboard.py all exist) and require only shared chart components (Phase 2) to render. This is the highest-visibility deliverable for stakeholders. Drill-down navigation is a genuine differentiator worth including here.
**Delivers:** ManagementLayout, ExecutiveDashboard (KPI counters, enrollment trend, financial summary, department comparison, alert panel), FinanceDashboard, AcademicDashboard, DrillDown navigation (summary -> dept -> program -> student), ReportViewer with export
**Uses:** DashboardEngine widget composition (ARCHITECTURE.md Pattern 3), polling SWR (Pattern 4), drill-down via route params (Pattern 5)
**Avoids:** Hardcoded dashboard layouts (use Custom Dashboard doctype configuration), WebSocket for KPI polling
**Research flag:** MAY NEED RESEARCH — management role names (VC, Registrar, Finance Officer, Dean) need verification against actual Frappe Role definitions in the live system; the mapping may not be 1:1 with business titles.

### Phase 5: Parent Portal
**Rationale:** Parent portal is independent of Faculty/HOD modules and can be parallelized with Phases 3-4 if team capacity allows. The guardian-student SQL bug in portal_api.py must be fixed before any parent-facing API is built.
**Delivers:** ParentLayout, ParentDashboard, child selector (multi-child support), ChildAcademics (attendance calendar, grades), ChildFinance (fee status, payment history, online fee payment), announcements, timetable read-only view
**Addresses:** All P1 parent features; P2 online fee payment (Razorpay/PayU already integrated in student portal)
**Implements:** Guardian ownership verification utility (IDOR prevention) as the first thing built in this phase
**Avoids:** Parent IDOR vulnerability — `get_guardian_students(user)` verification required before any data API returns
**Research flag:** SKIP — Razorpay/PayU integration already exists; parent auth pattern is well-understood. Note: Student Guardian child table schema needs confirmation before building the guardian-student join.

### Phase 6: HOD Portal
**Rationale:** HOD portal is a superset of the faculty portal — it inherits all faculty views and adds department-level analytics and approval workflows. Must come after Phase 3 (faculty portal is stable). HOD-specific APIs (department analytics aggregations, approval queues) need building.
**Delivers:** HODLayout (extends FacultyLayout), HODDashboard, DepartmentAnalytics (attendance by course, pass rates, at-risk students), FacultyManagement (workload summary), Approvals queue, CO-PO attainment heatmap view
**Addresses:** All P2 HOD features; CO-PO attainment visualization (NAAC differentiator)
**Avoids:** HOD seeing data outside their department — department scoping must be enforced in every HOD API
**Research flag:** MAY NEED RESEARCH — Frappe workflow engine integration for approval queues (leave approvals, academic requests) needs API-level verification; the workflow doctype configuration for programmatic portal access is not fully documented in research.

### Phase 7: Export, Scheduled Reports & Advanced Analytics
**Rationale:** Report scheduling requires a working report viewer (Phase 4). Async export infrastructure is a cross-cutting concern best established after core portals are stable and realistic data volumes are known. Comparative YoY analytics and alert thresholds are P2 features that add value once baseline is validated.
**Delivers:** Async export pattern (frappe.enqueue for >1000 rows, OOM prevention), scheduled report configuration UI, comparative YoY trend views, real-time alert thresholds with WhatsApp notifications, "Last updated" timestamps on all dashboards, parent-faculty messaging
**Addresses:** P2 scheduled reports, P2 comparative analytics, P2 alert thresholds, P2 parent-faculty messaging
**Implements:** Background job export pattern (PITFALLS.md — avoids OOM crashes on large datasets)
**Avoids:** Export OOM crashes — async job pattern from the start, not retrofit
**Research flag:** SKIP — ScheduledReport doctype is 80% built; WhatsApp integration already exists; background job pattern via frappe.enqueue is well-documented.

### Phase Ordering Rationale

- Phase 1 before everything: SQL injection and missing permission checks are not cosmetic. Shipping dashboards with these vulnerabilities in the existing code would be catastrophic.
- Phase 2 before Phases 3-6: shared components are depended on by every subsequent module. Building them twice wastes effort and creates inconsistency.
- Phase 3 before Phase 6: HOD inherits all faculty views; faculty module must be stable first.
- Phases 4 and 5 can be parallelized with Phase 3: management dashboards and parent portal do not depend on the faculty module.
- Phase 7 last: it enhances completed portals rather than enabling them, and realistic export volumes only become clear once portals are in use.

### Research Flags

Phases needing deeper research during planning:
- **Phase 4 (Management Dashboards):** Management role names (VC, Registrar, Finance Officer, Dean) need verification against actual Frappe role definitions in the live system. The mapping between business titles and Frappe role names may not be 1:1.
- **Phase 6 (HOD Portal):** Frappe workflow engine integration for approval queues (leave approvals, academic requests) needs API-level verification — the workflow doctype configuration for programmatic portal access is not fully documented in current research.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Security remediation follows clear specifications from PITFALLS.md; structural refactoring follows ARCHITECTURE.md blueprint exactly.
- **Phase 2:** ApexCharts, TanStack Table, VueUse are all officially documented with clear Vue 3 integration examples.
- **Phase 3:** Faculty portal APIs are scaffolded in portal_api.py; patterns extend the proven student portal structure.
- **Phase 5:** Parent portal auth pattern is well-understood; payment gateway integration is already live.
- **Phase 7:** ScheduledReport doctype is nearly complete; backend patterns are established.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All npm packages verified at exact versions (March 2026). Bundle size data confirmed. Rationale supported by capability comparisons. Existing stack locked in and proven in production. SheetJS exclusion confirmed by community issue tracker. |
| Features | HIGH | Based on direct codebase analysis of 700+ line portal_api.py, executive_dashboard.py, 58 backend reports, Custom Dashboard / KPI doctypes, plus competitor research across 4 Indian ERP vendors. MVP boundary is well-defined and conservative. |
| Architecture | HIGH | Based on direct codebase analysis of existing Vue SPA structure, composables, router, and all analytics Python modules. Recommended patterns extend proven patterns already in use in the codebase — no speculative architecture. |
| Pitfalls | HIGH | Critical pitfalls (SQL injection, missing permissions) are verified in the actual source code with specific file and method references. N+1 patterns directly observed in executive_dashboard.py. Performance pitfalls verified against Frappe security bulletins and community documentation. |

**Overall confidence:** HIGH

### Gaps to Address

- **Management role-to-Frappe-role mapping:** The business titles (VC, Registrar, Finance Officer, Dean) may map to non-obvious Frappe role names or custom roles specific to this installation. Needs verification during Phase 4 planning against the live system's Role list before writing any `frappe.only_for()` checks.
- **Department attendance aggregation API:** `get_department_performance()` currently returns mocked attendance and pass rates. The real SQL aggregation logic against actual Student Attendance and Assessment Result doctypes needs to be designed and validated before Phase 4 builds on it.
- **Guardian-student join bug:** ARCHITECTURE.md flags a SQL bug in portal_api.py where the guardian-student join uses the wrong column. The exact column name discrepancy needs confirmation during Phase 5 implementation before writing the `get_guardian_students()` utility.
- **HOD approval workflow configuration:** The Frappe workflow engine configuration for leave/academic approvals in the HOD context is not documented in the research. Phase 6 planning needs a pre-implementation spike to identify which workflow states and transitions are pre-configured in the live system.
- **HRMS integration for faculty leave data:** The Leave Application doctype lives in HRMS, listed as "integration untested" in architecture research. Faculty leave views in Phase 3 need a pre-implementation spike to confirm HRMS API accessibility from the portal's auth context.
- **ApexCharts-to-PDF chart embedding:** The pattern for embedding ApexCharts chart images in jsPDF-generated PDFs (using `.dataURI()`) needs prototyping in Phase 7 to verify quality and browser compatibility before committing to the approach.

## Sources

### Primary (HIGH confidence — codebase analysis)

- `/workspace/development/student-portal-vue/` — existing Vue 3 SPA structure, composables, router patterns
- `frappe-bench/apps/university_erp/.../portal_api.py` — 700+ line portal API (student, faculty, parent endpoints)
- `frappe-bench/apps/university_erp/.../analytics/dashboard_engine.py` — SQL injection vulnerability confirmed in `_execute_query()`
- `frappe-bench/apps/university_erp/.../analytics/executive_dashboard.py` — N+1 patterns and missing permission checks confirmed
- `frappe-bench/apps/university_erp/.../analytics/api.py` — Analytics API and KPI system
- University Analytics doctypes: Custom Dashboard, Dashboard Widget, KPI Definition, KPI Value, Scheduled Report

### Primary (HIGH confidence — official documentation)

- [vue3-apexcharts npm](https://www.npmjs.com/package/vue3-apexcharts) — v1.11.1 verified, last published March 2026
- [apexcharts npm](https://www.npmjs.com/package/apexcharts) — v5.10.4 verified
- [@tanstack/vue-table npm](https://www.npmjs.com/package/@tanstack/vue-table) — v8.21.3 verified
- [jsPDF npm](https://www.npmjs.com/package/jspdf) — v4.2.1 verified, v4.0 security overhaul noted
- [jspdf-autotable npm](https://www.npmjs.com/package/jspdf-autotable) — v5.0.7 verified
- [ExcelJS npm](https://www.npmjs.com/package/exceljs) — v4.4.0 verified
- [@vueuse/core npm](https://www.npmjs.com/package/@vueuse/core) — v14.2.1 verified
- [Frappe Realtime API docs](https://docs.frappe.io/framework/user/en/api/realtime) — publish_realtime, socket.io architecture
- [Vue Router Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html) — meta-based role routing pattern
- [Frappe Security Bulletin](https://frappe.io/security-bulletin) — CVEs for SQL injection and permission bypass in whitelisted methods

### Secondary (MEDIUM confidence — competitor / community research)

- [MasterSoft VC Dashboard Features](https://www.iitms.co.in/blog/how-university-dashboard-can-help-vice-chancellors-to-leverage-decision-making.html) — competitor feature set for management dashboards
- [MyLeadingCampus Complete ERP Guide 2026](https://www.myleadingcampus.com/blogview/what-is-college-university-erp-a-complete-practical-guide-for-autonomous-colleges-and-deemed-universities-2025-edition) — Indian ERP market context
- [Camu University Management Software](https://camudigitalcampus.com/university-management-erp-software/) — competitor analytics and portal features
- [Academia ERP University Management](https://www.academiaerp.com/university-management-system-software/) — competitor feature matrix
- [Scaling ERPNext: Query Optimization](https://medium.com/@abdelwahab.00964/scaling-erpnext-query-optimization-techniques-for-high-performance-frappe-apps-6aa4b6bb5b20) — aggregation query patterns
- [ERPNext Performance Tuning Wiki](https://github.com/frappe/erpnext/wiki/ERPNext-Performance-Tuning) — indexing, query optimization
- [MariaDB Slow Queries in Frappe Cloud](https://docs.frappe.io/cloud/faq/mariadb-slow-queries-in-your-site) — slow query detection

### Tertiary (LOW confidence — single source or needs validation)

- [SheetJS npm warning](https://git.sheetjs.com/sheetjs/sheetjs/issues/3098) — stale npm version, security issues (confirm current status)
- [Kerala KREAP HOD Approval Process](https://kerala.kreap.co.in/user/pages/files/hodapproval.pdf) — HOD workflow reference for an external system, may differ from local configuration

---
*Research completed: 2026-03-17*
*Ready for roadmap: yes*

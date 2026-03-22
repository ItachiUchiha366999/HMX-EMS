# Roadmap: University ERP — Dashboards, Analytics & Role-Based Portals

## Overview

This roadmap delivers management dashboards, analytics, and role-based portals (student, faculty, HOD, parent, management) on top of an existing Frappe v15 university ERP with 275+ doctypes. Strategy: **backend-first** — the complete Frappe Desk backend (accounts fork, workflows, data integrity) must be fully working before any Vue portal frontend work begins. All portal UIs will be designed and built fresh once the backend is stable, ensuring no rework.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation & Security Hardening** - Fix critical vulnerabilities, verify cross-app data, scaffold unified Vue app shell with role routing
- [x] **Phase 2: Shared Component Library** - Build reusable KPI cards, charts, data tables, filters, and export components consumed by all portals
- [x] **Phase 3: Faculty Portal** - Faculty can manage daily teaching workflow (timetable, attendance, grades, leave, LMS, research)
- [x] **Phase 03.1: Comprehensive System Audit & Fix** (INSERTED) - Full system testing: fix custom fields, fix reports, fix permissions, test ALL APIs, test desk/portal UI, fix SQL errors, audit duplicate business logic (completed 2026-03-19)
- [ ] **Phase 03.3: ERPNext Accounts Module Fork** - Fork Accounts module into university_erp/university_finance, relabel with student-centric terminology, archive unused doctypes/reports, wire GL posting through forked module
- [ ] **Phase 03.4: Post-Fork Backend Audit & Fix** (INSERTED) - Complete system test after accounts fork, verify all Frappe Desk UI works, fix any issues, ensure backend stability before frontend
- [ ] **Phase 4: Portal Redesign & Build** - Redesign complete Vue portal from scratch for all user types (Student, Faculty, HOD, Parent, Management) with proper design system, now that backend is stable
- [ ] **Phase 5: Management Dashboards** - University leadership can view KPIs, trends, drill-down analytics, and reports by role
- [ ] **Phase 6: Parent Portal** - Parents can monitor child academics, finances, hostel/transport, and communicate with faculty
- [ ] **Phase 7: HOD Portal** - HODs can oversee department performance, manage faculty, and handle approvals
- [ ] **Phase 8: Scheduled Reports & Cross-Portal Polish** - Scheduled email delivery, export integration verification, and cross-cutting enhancements

## Phase Details

### Phase 1: Foundation & Security Hardening
**Goal**: The analytics backend is secure, cross-app data is verified consistent, and the unified Vue app shell routes users to the correct portal based on their role
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, FOUND-06, FOUND-07, FOUND-08
**Success Criteria** (what must be TRUE):
  1. All analytics and dashboard API endpoints reject unauthorized users (a student calling executive dashboard API gets a permission error, not data)
  2. Dashboard engine queries use parameterized SQL — no string interpolation in any query path
  3. Cross-app data verification script runs clean (Employee count matches Instructor count, Fees paid_amount matches GL Entry totals, all 6 Education overrides verified)
  4. A logged-in user visiting /portal/ is automatically routed to the correct role module (student, faculty, HOD, parent, or management) based on their Frappe roles
  5. Academic year/semester filter is available as a global context that all data views can consume
**Plans**: 3 plans

Plans:
- [x] 01-backend-security-PLAN.md — Fix SQL injection, permission guards, N+1 queries; create health_check.py; add University VC and University Dean roles
- [x] 02-portal-app-shell-PLAN.md — Standalone portal-vue/ Vite project with Pinia session store, Vue Router, role-filtered sidebar, get_session_info() endpoint, Frappe www/portal/ page
- [x] 03-integration-wiring-PLAN.md — Build Vue app, verify Frappe routing, confirm endpoint access control, human smoke test

### Phase 2: Shared Component Library
**Goal**: Reusable UI components exist and are verified in isolation so every portal module can compose dashboards, tables, charts, and exports from proven primitives
**Depends on**: Phase 1
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04, COMP-05, COMP-06, COMP-07, COMP-08
**Success Criteria** (what must be TRUE):
  1. A KPI counter card renders a value, label, trend indicator, and status color — and is used identically across faculty, management, and HOD views
  2. Charts (line, bar, pie, heatmap) render real data from Frappe APIs via a single chart wrapper component backed by ApexCharts
  3. Data tables support sorting, pagination, search, and inline PDF/Excel export using TanStack Table
  4. A filter bar with date range, academic year, department, and program selectors can be dropped into any view and its state drives data queries
  5. The existing 54+ backend reports can be browsed and executed through a report viewer component inside the portal
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md — Wave 0 infra (vitest, dark mode tokens, useFrappe) + KPI card, chart wrapper, filter bar, notification panel
- [x] 02-02-PLAN.md — DataTable with TanStack + server-side pagination, PDF/Excel export composables, report viewer with Frappe report API

### Phase 3: Faculty Portal
**Goal**: Faculty can manage their complete daily teaching workflow from the portal without needing to access Frappe desk
**Depends on**: Phase 2
**Requirements**: FCTY-01, FCTY-02, FCTY-03, FCTY-04, FCTY-05, FCTY-06, FCTY-07, FCTY-08, FCTY-09, FCTY-10, FCTY-11, FCTY-12
**Success Criteria** (what must be TRUE):
  1. Faculty can see today's classes and mark attendance for 60 students in under 2 minutes using bulk-select UI
  2. Faculty can enter grades in a spreadsheet-like grid and view per-course grade distribution and at-risk student analytics
  3. Faculty can view their pending tasks dashboard (unmarked attendance, unsubmitted grades, pending leave requests) and take action on each
  4. Faculty can approve/reject student leave requests, view their own leave balance, submit leave requests, and see their teaching workload summary
  5. Faculty can manage LMS course content, view research publications, and view OBE CO/PO attainment data
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Backend faculty API + dashboard + timetable + attendance marking + announcements (Wave 1)
- [x] 03-02-PLAN.md — Spreadsheet grade grid + student lists + performance analytics (Wave 2)
- [x] 03-03-PLAN.md — Leave management + LMS CRUD + research + OBE CO/PO + workload summary (Wave 2)

### Phase 03.1: Comprehensive System Audit & Fix (INSERTED)

**Goal:** The entire ERP system is fully tested and all issues fixed — every API endpoint works, every report runs, permissions are correct for all roles, no SQL errors, no broken desk/portal links, and duplicate business logic between apps is documented with clear recommendations
**Depends on:** Phase 3
**Requirements**: AUDIT-DUP, AUDIT-CONN, AUDIT-RPT, AUDIT-API, AUDIT-A11Y, GAP-01, GAP-02, GAP-03, GAP-04, GAP-05
**Success Criteria** (what must be TRUE):
  1. All Employee custom fields (13) and Leave Application custom fields (9) migrated to DB and verified in schema
  2. ALL university_erp reports execute without error (10 previously failing reports fixed + re-verified)
  3. All 27 faculty API endpoints return valid responses with cross-app data resolution verified
  4. ALL @whitelist API endpoints across university_erp tested and working (not just faculty_api)
  5. Permission matrix verified for all roles (Admin, Faculty, Student, Parent, HOD, VC, Dean, Registrar, Finance Officer) — no unauthorized access, no missing access
  6. All Frappe Desk workspace links, dashboard pages, and sidebar links resolve without 404 errors
  7. All portal-vue routes render without errors
  8. No SQL injection risks in any university_erp .py file (zero f-string interpolation in frappe.db.sql calls)
  9. Duplicate business logic between apps documented (Fees vs Fee Payment, Exams vs Exams) with authoritative source identified
  10. Portal UI maintains zero critical and zero serious WCAG 2.1 AA violations
**Plans**: 6 plans (3 initial audit + 3 gap closure/expansion)

Plans (initial audit — completed):
- [x] 03.1-01-PLAN.md — Duplicate doctype audit + cross-app link integrity testing
- [x] 03.1-02-PLAN.md — Report/dashboard verification + faculty API integration testing
- [x] 03.1-03-PLAN.md — Accessibility audit with vitest-axe + fix critical/serious violations

Plans (gap closure + expansion — planned):
- [x] 03.1-04-PLAN.md — Custom field migration + report fixes + dashboard fix + re-verify
- [x] 03.1-05-PLAN.md — Comprehensive API audit + permission matrix testing for all roles
- [ ] 03.1-06-PLAN.md — Desk UI link verification + portal UI verification + SQL injection scan + business logic duplicate audit

### Phase 03.3: ERPNext Accounts Module Fork

**Goal:** The entire ERPNext Accounts module is forked into university_erp as university_finance with student-centric terminology, unnecessary doctypes/reports archived, controller hierarchy forked and stripped of stock/selling/buying dependencies, and all existing finance flows (fee->GL, payment gateway) work through the forked module
**Depends on:** Phase 03.1 (working finance reports first)
**Requirements**: ACCT-01, ACCT-02, ACCT-03, ACCT-04, ACCT-05, ACCT-06, ACCT-07
**Success Criteria** (what must be TRUE):
  1. Full ERPNext Accounts module copied into university_erp/university_finance/ with all doctypes, reports, and controllers
  2. All doctype labels relabeled: Customer->Student, Sales Invoice->Fee Invoice, Supplier->Vendor, Sales Order->Fee Order, Purchase Invoice->Procurement Invoice
  3. Unnecessary files, workflows, and unused doctypes removed from forked module
  4. New university-specific workflows set up for fee collection, refunds, and financial approvals
  5. GL Entry, Journal Entry, Payment Entry, Bank Reconciliation CRUD operations work through forked module
  6. Fee collection -> GL posting -> Payment Entry flow verified end-to-end
  7. Payment gateway webhooks (Razorpay/PayU) create Payment Entries through forked module
  8. All university_erp finance reports use forked module
  9. No remaining import references to erpnext.accounts in university_erp code
**Plans**: 4 plans

Plans:
- [ ] 03.3-01-PLAN.md — Fork infrastructure: compat shim, exceptions, fork script, execute file copy, JSON module updates, import rewriting (Wave 1)
- [ ] 03.3-02-PLAN.md — Controller fork: StatusUpdater/TransactionBase/AccountsController hierarchy, strip stock/selling/buying, rewrite invoice controllers, archive 56 unused doctypes (Wave 2)
- [ ] 03.3-03-PLAN.md — Relabeling + reports: workspace with university terminology, rename report titles, archive 16 unused reports, verify report imports (Wave 2)
- [ ] 03.3-04-PLAN.md — Integration wiring: redirect GLPostingManager import, run bench migrate, verify module registration, create smoke tests (Wave 3)

### Phase 03.4: Post-Fork Backend Audit & Fix (INSERTED)

**Goal:** After the accounts fork, the entire ERP backend is fully re-tested — every doctype accessible in Frappe Desk, every report running, every workflow functional, all cross-app connections verified — ensuring complete backend stability before any frontend portal work begins
**Depends on:** Phase 03.3
**Requirements**: AUDIT-BACKEND-01, AUDIT-BACKEND-02, AUDIT-BACKEND-03, AUDIT-BACKEND-04
**Success Criteria** (what must be TRUE):
  1. All university_erp doctypes are accessible and CRUD-functional in Frappe Desk (no 404s, no schema errors)
  2. All reports across university_erp execute without error (extending Phase 03.1 audit with post-fork verification)
  3. All workflows (fee collection, leave approval, admission, grade submission) operate correctly end-to-end in Frappe Desk
  4. All cross-app data connections verified (Student<->Enrollment, Fees<->GL, Employee<->Faculty, Academic Year consistency)
  5. Permission matrix re-verified for all 9 roles after accounts fork changes
  6. Comprehensive demo data seeded so all Desk views show meaningful content
**Plans**: TBD

### Phase 4: Portal Redesign & Build

**Goal:** The complete Vue portal is redesigned from scratch with a proper design system and built for all user types (Student, Faculty, HOD, Parent, Management), now that the backend is stable and proven in Frappe Desk
**Depends on:** Phase 03.4 (backend must be fully working first)
**Requirements**: PORTAL-01, PORTAL-02, PORTAL-03, PORTAL-04, PORTAL-05
**Success Criteria** (what must be TRUE):
  1. New design system chosen and implemented (discuss during /gsd:discuss-phase)
  2. Student portal: all 11 views recreated with proper styling, data, and UX
  3. Faculty portal: existing views redesigned to match new design system
  4. HOD portal: department overview, faculty management, approvals
  5. Parent portal: child academics, fees, hostel/transport, messaging
  6. Management portal: role-specific dashboards for VC, Registrar, Finance Officer, Dean
  7. All portals share consistent design system, components, and dark mode support
**Plans**: TBD

### Phase 5: Management Dashboards
**Goal**: University leadership (VC, Registrar, Finance Officer, Dean) can make data-driven decisions through role-specific dashboards with drill-down from summary to student level
**Depends on**: Phase 4 (portal redesign provides the dashboard views)
**Requirements**: MGMT-01, MGMT-02, MGMT-03, MGMT-04, MGMT-05, MGMT-06, MGMT-07, MGMT-08, MGMT-09, MGMT-10, MGMT-11, ANLT-03, ANLT-04
**Success Criteria** (what must be TRUE):
  1. VC, Registrar, Finance Officer, and Dean each see a dashboard tailored to their role with real aggregated KPIs (not mocked data)
  2. All dashboards show enrollment trend charts and financial collection vs target visualization with year-over-year comparative data
  3. User can drill down from university summary to department to program to individual student on any KPI
  4. Department comparison table shows real aggregated data (attendance, pass rates, fee collection) across all departments
  5. Alert panel shows actionable items needing attention (overdue fees, SLA breaches, low attendance) and report viewer exposes existing 54+ reports with filters
**Plans**: TBD

Plans:
- [ ] 05-01: Management layout, role-specific dashboards (VC, Registrar, Finance, Dean)
- [ ] 05-02: Drill-down navigation, department comparison, trend charts, alert panel
- [ ] 05-03: Report viewer integration, year-over-year analytics

### Phase 6: Parent Portal
**Goal**: Parents can monitor their child's complete university life (academics, finances, hostel, transport) and communicate with faculty, all within a secure guardian-verified context
**Depends on**: Phase 4 (portal redesign provides parent views)
**Requirements**: PRNT-01, PRNT-02, PRNT-03, PRNT-04, PRNT-05, PRNT-06, PRNT-07, PRNT-08, PRNT-09, PRNT-10
**Success Criteria** (what must be TRUE):
  1. Parent with multiple enrolled children can switch between them via a child context selector, and every view scopes data to the selected child with guardian ownership verification (no IDOR)
  2. Parent can view child's attendance summary with calendar heatmap, current semester grades, exam results, and class timetable
  3. Parent can view fee status, payment history, pending dues, and pay fees online through Razorpay/PayU in parent auth context
  4. Parent can view child's hostel allocation, hostel attendance, mess details, transport route, and bus allocation
  5. Parent can view institutional announcements and send messages to child's faculty members and receive replies
**Plans**: TBD

Plans:
- [ ] 06-01: Parent layout, child selector with guardian verification, academics views
- [ ] 06-02: Finance views with online payment, hostel/transport, announcements, messaging

### Phase 7: HOD Portal
**Goal**: HODs can oversee their entire department's academic performance, manage faculty workload, and process approvals without leaving the portal
**Depends on**: Phase 4 (portal redesign provides HOD views)
**Requirements**: HOD-01, HOD-02, HOD-03, HOD-04, HOD-05, HOD-06, HOD-07, HOD-08
**Success Criteria** (what must be TRUE):
  1. HOD can access all faculty portal features for their own courses (inherits faculty module views)
  2. HOD can view department-wide attendance overview (course-wise, faculty-wise) and faculty workload distribution
  3. HOD can approve/reject faculty leave requests, course registrations, and academic requests from an approval queue
  4. HOD can view department student performance summary (pass rates, fail rates, at-risk students) and department KPIs with targets
  5. HOD can view CO-PO attainment heatmap for department programs and department budget utilization status
**Plans**: TBD

Plans:
- [ ] 07-01: HOD layout extending faculty, department analytics, faculty workload
- [ ] 07-02: Approval workflows, CO-PO heatmap, budget views, department KPIs

### Phase 8: Scheduled Reports & Cross-Portal Polish
**Goal**: Stakeholders receive automated reports on schedule, and export/analytics capabilities work consistently across all portals
**Depends on**: Phase 5, Phase 6, Phase 7
**Requirements**: ANLT-01, ANLT-02, ANLT-05, MGMT-10
**Success Criteria** (what must be TRUE):
  1. PDF and Excel export works on every data table and report view across all portals (student, faculty, HOD, parent, management)
  2. Any report can be scheduled for daily/weekly/monthly email delivery to configured recipients
  3. Scheduled reports are delivered on time with correct data scoping (department-scoped for HOD, university-wide for VC, etc.)
**Plans**: TBD

Plans:
- [ ] 08-01: Export integration verification, scheduled report configuration and email delivery

## Progress

**Execution Order (Backend-First):**
Phases execute: 1 -> 2 -> 3 -> 03.1 -> **03.3 (accounts fork) -> 03.4 (backend audit)** -> 4 (portal redesign) -> 5 -> 6 -> 7 -> 8
Key principle: Backend must be fully working in Frappe Desk before any Vue portal work. Phase 4 redesigns all portals from scratch once backend is stable.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Security Hardening | 3/3 | Complete | 2026-03-18 |
| 2. Shared Component Library | 2/2 | Complete | 2026-03-18 |
| 3. Faculty Portal | 3/3 | Complete | 2026-03-18 |
| 03.1. System Audit & Fix | 6/6 | Complete | 2026-03-19 |
| 03.3. ERPNext Accounts Fork | 0/4 | Not started | - |
| 03.4. Post-Fork Backend Audit | 0/TBD | Not started | - |
| 4. Portal Redesign & Build | 0/TBD | Not started | - |
| 5. Management Dashboards | 0/TBD | Not started | - |
| 6. Parent Portal | 0/TBD | Not started | - |
| 7. HOD Portal | 0/TBD | Not started | - |
| 8. Scheduled Reports & Polish | 0/TBD | Not started | - |

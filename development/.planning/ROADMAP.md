# Roadmap: University ERP — Dashboards, Analytics & Role-Based Portals

## Overview

This roadmap delivers management dashboards, analytics, and role-based portals (faculty, HOD, parent) on top of an existing Frappe v15 university ERP with 275+ doctypes. The work begins with security remediation and cross-app verification (the existing codebase has SQL injection, missing permission checks, and untested cross-app data flows), then builds a shared component library consumed by all portals, then delivers each portal as a vertical slice (faculty, management, parent, HOD), and finishes with scheduled reports and export integration across all views.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation & Security Hardening** - Fix critical vulnerabilities, verify cross-app data, scaffold unified Vue app shell with role routing
- [x] **Phase 2: Shared Component Library** - Build reusable KPI cards, charts, data tables, filters, and export components consumed by all portals
- [ ] **Phase 3: Faculty Portal** - Faculty can manage daily teaching workflow (timetable, attendance, grades, leave, LMS, research)
- [ ] **Phase 4: Management Dashboards** - University leadership can view KPIs, trends, drill-down analytics, and reports by role
- [ ] **Phase 5: Parent Portal** - Parents can monitor child academics, finances, hostel/transport, and communicate with faculty
- [ ] **Phase 6: HOD Portal** - HODs can oversee department performance, manage faculty, and handle approvals
- [ ] **Phase 7: Scheduled Reports & Cross-Portal Polish** - Scheduled email delivery, export integration verification, and cross-cutting enhancements

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
- [ ] 03-01-PLAN.md — Backend faculty API + dashboard + timetable + attendance marking + announcements (Wave 1)
- [ ] 03-02-PLAN.md — Spreadsheet grade grid + student lists + performance analytics (Wave 2)
- [ ] 03-03-PLAN.md — Leave management + LMS CRUD + research + OBE CO/PO + workload summary (Wave 2)

### Phase 4: Management Dashboards
**Goal**: University leadership (VC, Registrar, Finance Officer, Dean) can make data-driven decisions through role-specific dashboards with drill-down from summary to student level
**Depends on**: Phase 2
**Requirements**: MGMT-01, MGMT-02, MGMT-03, MGMT-04, MGMT-05, MGMT-06, MGMT-07, MGMT-08, MGMT-09, MGMT-10, MGMT-11, ANLT-03, ANLT-04
**Success Criteria** (what must be TRUE):
  1. VC, Registrar, Finance Officer, and Dean each see a dashboard tailored to their role with real aggregated KPIs (not mocked data)
  2. All dashboards show enrollment trend charts and financial collection vs target visualization with year-over-year comparative data
  3. User can drill down from university summary to department to program to individual student on any KPI
  4. Department comparison table shows real aggregated data (attendance, pass rates, fee collection) across all departments
  5. Alert panel shows actionable items needing attention (overdue fees, SLA breaches, low attendance) and report viewer exposes existing 54+ reports with filters
**Plans**: TBD

Plans:
- [ ] 04-01: Management layout, role-specific dashboards (VC, Registrar, Finance, Dean)
- [ ] 04-02: Drill-down navigation, department comparison, trend charts, alert panel
- [ ] 04-03: Report viewer integration, year-over-year analytics

### Phase 5: Parent Portal
**Goal**: Parents can monitor their child's complete university life (academics, finances, hostel, transport) and communicate with faculty, all within a secure guardian-verified context
**Depends on**: Phase 2
**Requirements**: PRNT-01, PRNT-02, PRNT-03, PRNT-04, PRNT-05, PRNT-06, PRNT-07, PRNT-08, PRNT-09, PRNT-10
**Success Criteria** (what must be TRUE):
  1. Parent with multiple enrolled children can switch between them via a child context selector, and every view scopes data to the selected child with guardian ownership verification (no IDOR)
  2. Parent can view child's attendance summary with calendar heatmap, current semester grades, exam results, and class timetable
  3. Parent can view fee status, payment history, pending dues, and pay fees online through Razorpay/PayU in parent auth context
  4. Parent can view child's hostel allocation, hostel attendance, mess details, transport route, and bus allocation
  5. Parent can view institutional announcements and send messages to child's faculty members and receive replies
**Plans**: TBD

Plans:
- [ ] 05-01: Parent layout, child selector with guardian verification, academics views
- [ ] 05-02: Finance views with online payment, hostel/transport, announcements, messaging

### Phase 6: HOD Portal
**Goal**: HODs can oversee their entire department's academic performance, manage faculty workload, and process approvals without leaving the portal
**Depends on**: Phase 3
**Requirements**: HOD-01, HOD-02, HOD-03, HOD-04, HOD-05, HOD-06, HOD-07, HOD-08
**Success Criteria** (what must be TRUE):
  1. HOD can access all faculty portal features for their own courses (inherits faculty module views)
  2. HOD can view department-wide attendance overview (course-wise, faculty-wise) and faculty workload distribution
  3. HOD can approve/reject faculty leave requests, course registrations, and academic requests from an approval queue
  4. HOD can view department student performance summary (pass rates, fail rates, at-risk students) and department KPIs with targets
  5. HOD can view CO-PO attainment heatmap for department programs and department budget utilization status
**Plans**: TBD

Plans:
- [ ] 06-01: HOD layout extending faculty, department analytics, faculty workload
- [ ] 06-02: Approval workflows, CO-PO heatmap, budget views, department KPIs

### Phase 7: Scheduled Reports & Cross-Portal Polish
**Goal**: Stakeholders receive automated reports on schedule, and export/analytics capabilities work consistently across all portals
**Depends on**: Phase 4, Phase 5, Phase 6
**Requirements**: ANLT-01, ANLT-02, ANLT-05, MGMT-10
**Success Criteria** (what must be TRUE):
  1. PDF and Excel export works on every data table and report view across all portals (faculty, HOD, parent, management)
  2. Any report can be scheduled for daily/weekly/monthly email delivery to configured recipients
  3. Scheduled reports are delivered on time with correct data scoping (department-scoped for HOD, university-wide for VC, etc.)
**Plans**: TBD

Plans:
- [ ] 07-01: Export integration verification, scheduled report configuration and email delivery

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7
Note: Phases 3, 4, and 5 can execute in parallel after Phase 2 completes. Phase 6 requires Phase 3.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Security Hardening | 3/3 | Complete | 2026-03-18 |
| 2. Shared Component Library | 2/2 | Complete | 2026-03-18 |
| 3. Faculty Portal | 0/3 | Not started | - |
| 4. Management Dashboards | 0/3 | Not started | - |
| 5. Parent Portal | 0/2 | Not started | - |
| 6. HOD Portal | 0/2 | Not started | - |
| 7. Scheduled Reports & Cross-Portal Polish | 0/1 | Not started | - |

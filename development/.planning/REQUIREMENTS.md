# Requirements: University ERP — Dashboards, Analytics & Role-Based Portals

**Defined:** 2026-03-17
**Core Value:** University leadership can make data-driven decisions through real-time dashboards with drill-down capability, while faculty, HODs, and parents have self-service portal access to the information and actions relevant to their role.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Foundation & Security

- [x] **FOUND-01**: Cross-app data consistency verified (ERPNext <> HRMS <> Education <> university_erp) with documented integration points
- [x] **FOUND-02**: SQL injection vulnerability in dashboard_engine.py fixed with parameterized queries
- [x] **FOUND-03**: Permission checks enforced on all analytics and dashboard API endpoints (role-based access)
- [x] **FOUND-04**: N+1 query patterns in executive_dashboard.py resolved with aggregation queries
- [x] **FOUND-05**: Unified Vue app shell with role-based routing (student, faculty, HOD, parent, management)
- [x] **FOUND-06**: Auth guard with cached session (eliminate per-route API call for logged-in user check)
- [x] **FOUND-07**: Academic year / semester filter available on all data views
- [x] **FOUND-08**: Management role detection added (VC, Registrar, Finance Officer, Dean) beyond existing student/faculty/parent

### Shared Components

- [x] **COMP-01**: KPI counter card component (value, label, trend indicator, status color)
- [x] **COMP-02**: Chart wrapper component (line, bar, pie, heatmap) using ApexCharts
- [x] **COMP-03**: Data table component with sorting, pagination, and search using TanStack Table
- [x] **COMP-04**: Filter bar component (date range, academic year, department, program selectors)
- [x] **COMP-05**: PDF export on any data table or report view using jsPDF
- [x] **COMP-06**: Excel export on any data table or report view using ExcelJS
- [x] **COMP-07**: Report viewer component to expose existing 54+ backend reports in portal
- [x] **COMP-08**: Notification/alert panel component (reusable across portals)

### Faculty Portal

- [x] **FCTY-01**: Faculty can view today's classes with room, time, and course details
- [x] **FCTY-02**: Faculty can mark attendance for a class with bulk-select UI (mark 60 students in under 2 minutes)
- [x] **FCTY-03**: Faculty can enter grades/marks in a spreadsheet-like grid for their courses
- [x] **FCTY-04**: Faculty can view enrolled student list per course/section
- [x] **FCTY-05**: Faculty can see a pending tasks dashboard (unmarked attendance, unsubmitted grades, pending leave requests)
- [x] **FCTY-06**: Faculty can view institutional announcements and notices
- [x] **FCTY-07**: Faculty can view per-course student performance analytics (grade distribution, at-risk students)
- [x] **FCTY-08**: Faculty can approve/reject student leave requests from the portal
- [x] **FCTY-09**: Faculty can manage LMS course content, assignments, and view quiz results
- [x] **FCTY-10**: Faculty can view their research publications and OBE CO/PO attainment data
- [x] **FCTY-11**: Faculty can view their own leave balance and submit leave requests
- [x] **FCTY-12**: Faculty can view their teaching workload summary

### HOD Portal

- [ ] **HOD-01**: HOD can access all faculty portal features for their own courses
- [ ] **HOD-02**: HOD can view department-wide attendance overview (course-wise, faculty-wise)
- [ ] **HOD-03**: HOD can view faculty workload distribution across the department
- [ ] **HOD-04**: HOD can approve/reject faculty leave requests, course registrations, and academic requests
- [ ] **HOD-05**: HOD can view department student performance summary (pass rates, fail rates, at-risk students by course)
- [ ] **HOD-06**: HOD can view department-level KPIs with targets (attendance rate, pass rate, fee collection)
- [ ] **HOD-07**: HOD can view CO-PO attainment heatmap visualization for department programs
- [ ] **HOD-08**: HOD can view department budget utilization and procurement request status

### Parent Portal

- [ ] **PRNT-01**: Parent can select between multiple enrolled children (child context selector)
- [ ] **PRNT-02**: Parent can view child's attendance summary with calendar heatmap
- [ ] **PRNT-03**: Parent can view child's current semester grades and exam results
- [ ] **PRNT-04**: Parent can view child's fee status, payment history, and pending dues
- [ ] **PRNT-05**: Parent can view institutional announcements and notices
- [ ] **PRNT-06**: Parent can view child's class timetable (read-only)
- [ ] **PRNT-07**: Parent can pay fees online through Razorpay/PayU in parent auth context
- [ ] **PRNT-08**: Parent can view child's hostel allocation, hostel attendance, and mess details
- [ ] **PRNT-09**: Parent can view child's transport route and bus allocation
- [ ] **PRNT-10**: Parent can send messages to child's faculty members and receive replies

### Management Dashboards

- [ ] **MGMT-01**: VC dashboard shows university-wide KPIs (total enrollment, fee collection, attendance rate, pass rate, faculty count, grievances)
- [ ] **MGMT-02**: Registrar dashboard shows admissions pipeline, examination status, student lifecycle metrics
- [ ] **MGMT-03**: Finance Officer dashboard shows daily/monthly/yearly collection, outstanding dues, budget utilization
- [ ] **MGMT-04**: Dean/Director dashboard shows program-level academics, placement statistics, research output
- [ ] **MGMT-05**: All dashboards show enrollment trend chart (monthly/yearly)
- [ ] **MGMT-06**: All dashboards show financial summary with collection vs target visualization
- [ ] **MGMT-07**: Department comparison table with real aggregated data (not mocked)
- [ ] **MGMT-08**: Alert/notification panel showing items needing attention (overdue fees, SLA breaches, low attendance)
- [ ] **MGMT-09**: Drill-down navigation from summary to department to program to student level on all KPIs
- [ ] **MGMT-10**: Scheduled reports delivered via email (daily/weekly/monthly) to configured stakeholders
- [ ] **MGMT-11**: Year-over-year comparative analytics (enrollment, collection, pass rates, placement) with trend visualization

### Student Portal (Unified)

- [ ] **STUD-01**: Student dashboard showing today's classes, pending tasks, announcements, and key metrics
- [ ] **STUD-02**: Student can view academics — timetable, attendance summary with calendar heatmap, grades/marks per course
- [ ] **STUD-03**: Student can view finance — fee status, payment history, pending dues, online payment via Razorpay/PayU
- [ ] **STUD-04**: Student can view examinations — exam schedule, hall tickets, results
- [ ] **STUD-05**: Student can view hostel — room allocation, hostel attendance, mess details
- [ ] **STUD-06**: Student can view transport — route, bus allocation, schedule
- [ ] **STUD-07**: Student can view library — borrowed books, fines, catalog search
- [ ] **STUD-08**: Student can view placement — company listings, application status, placement statistics
- [ ] **STUD-09**: Student can submit grievances and track resolution status
- [ ] **STUD-10**: Student can view notifications and announcements
- [ ] **STUD-11**: Student can view and edit their profile

### Accounts Module Fork

- [ ] **ACCT-01**: Full ERPNext Accounts module forked into university_erp as university_accounts
- [ ] **ACCT-02**: All doctype labels relabeled with student-centric terminology (Customer→Student, Sales Invoice→Fee Invoice, Supplier→Vendor)
- [ ] **ACCT-03**: GL Entry, Journal Entry, Payment Entry, Bank Reconciliation working through forked module
- [ ] **ACCT-04**: Fee collection → GL posting flow verified end-to-end through forked module
- [ ] **ACCT-05**: Payment gateway integration (Razorpay/PayU) working through forked module
- [ ] **ACCT-06**: All university_erp finance reports updated to use forked module references
- [ ] **ACCT-07**: Original ERPNext Accounts module dependencies removed or redirected

### Gap Closure (Phase 03.1)

- [x] **GAP-01**: Employee custom fields (custom_is_faculty, custom_employee_category, etc.) migrated to database
- [x] **GAP-02**: Leave Application custom fields (custom_total_classes_affected, etc.) migrated to database
- [x] **GAP-03**: 10 failing university_erp reports fixed (schema errors + broken imports)
- [x] **GAP-04**: Executive dashboard get_overview_metrics() status column fix
- [x] **GAP-05**: All 27 faculty API endpoints verified working after custom field migration

### Analytics & Export

- [ ] **ANLT-01**: PDF export available on all data tables and report views
- [ ] **ANLT-02**: Excel export available on all data tables and report views
- [ ] **ANLT-03**: Portal-accessible report viewer exposing existing 54+ backend reports with filters
- [ ] **ANLT-04**: Date range, department, and program filters available on all report views
- [ ] **ANLT-05**: Scheduled email delivery of any report to configured recipients on configurable frequency

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Analytics

- **ADV-01**: Student risk scoring (dropout prediction based on attendance + grades + fees)
- **ADV-02**: Customizable dashboard widgets with drag-and-drop layout
- **ADV-03**: NAAC/NIRF accreditation auto-report generation from live data
- **ADV-04**: Faculty performance scorecards (teaching effectiveness + research + feedback)
- **ADV-05**: Real-time alert thresholds with WhatsApp/push notification delivery

### Additional Portals

- **PORT-01**: HR staff portal (employee self-service, payroll, leave management)
- **PORT-02**: Accounts staff portal (voucher entry, reconciliation, budget management)
- **PORT-03**: Alumni portal (networking, mentoring, donation, event registration)
- **PORT-04**: PWA manifest for mobile home-screen installation

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time chat/messaging system | Massive infrastructure scope; not core to decision-making. Use existing WhatsApp integration |
| Custom report builder in portal | Security risk (SQL injection surface), non-technical users create broken reports. Expose curated 54+ reports instead |
| Mobile native app | Separate codebase and distribution. Responsive Vue SPA covers mobile. PWA deferred to v2 |
| AI-powered predictive analytics | Requires ML pipeline, training data, model maintenance. Rule-based risk scoring deferred to v2 |
| Multi-campus real-time sync | Single university deployment. Multi-campus is a deployment concern, not a portal feature |
| Granular per-user permission builder | Exponential complexity. Role-based defaults cover 95% of needs |
| Sub-5-second dashboard auto-refresh | University data doesn't change that fast. Refresh on load + manual refresh sufficient |
| Full BI/OLAP engine | Frappe/MariaDB is OLTP. Pre-computed KPI values via cron gets 80% of value at 10% of cost |
| New doctype creation | All doctypes already exist. Focus is on views, analytics, and accounts fork |
| Removing unused ERPNext modules | Keep hidden via block_modules, don't uninstall — dependency risk |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Complete |
| FOUND-02 | Phase 1 | Complete |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 1 | Complete |
| FOUND-05 | Phase 1 | Complete |
| FOUND-06 | Phase 1 | Complete |
| FOUND-07 | Phase 1 | Complete |
| FOUND-08 | Phase 1 | Complete |
| COMP-01 | Phase 2 | Complete |
| COMP-02 | Phase 2 | Complete |
| COMP-03 | Phase 2 | Complete |
| COMP-04 | Phase 2 | Complete |
| COMP-05 | Phase 2 | Complete |
| COMP-06 | Phase 2 | Complete |
| COMP-07 | Phase 2 | Complete |
| COMP-08 | Phase 2 | Complete |
| FCTY-01 | Phase 3 | Complete |
| FCTY-02 | Phase 3 | Complete |
| FCTY-03 | Phase 3 | Complete |
| FCTY-04 | Phase 3 | Complete |
| FCTY-05 | Phase 3 | Complete |
| FCTY-06 | Phase 3 | Complete |
| FCTY-07 | Phase 3 | Complete |
| FCTY-08 | Phase 3 | Complete |
| FCTY-09 | Phase 3 | Complete |
| FCTY-10 | Phase 3 | Complete |
| FCTY-11 | Phase 3 | Complete |
| FCTY-12 | Phase 3 | Complete |
| HOD-01 | Phase 6 | Pending |
| HOD-02 | Phase 6 | Pending |
| HOD-03 | Phase 6 | Pending |
| HOD-04 | Phase 6 | Pending |
| HOD-05 | Phase 6 | Pending |
| HOD-06 | Phase 6 | Pending |
| HOD-07 | Phase 6 | Pending |
| HOD-08 | Phase 6 | Pending |
| PRNT-01 | Phase 5 | Pending |
| PRNT-02 | Phase 5 | Pending |
| PRNT-03 | Phase 5 | Pending |
| PRNT-04 | Phase 5 | Pending |
| PRNT-05 | Phase 5 | Pending |
| PRNT-06 | Phase 5 | Pending |
| PRNT-07 | Phase 5 | Pending |
| PRNT-08 | Phase 5 | Pending |
| PRNT-09 | Phase 5 | Pending |
| PRNT-10 | Phase 5 | Pending |
| MGMT-01 | Phase 4 | Pending |
| MGMT-02 | Phase 4 | Pending |
| MGMT-03 | Phase 4 | Pending |
| MGMT-04 | Phase 4 | Pending |
| MGMT-05 | Phase 4 | Pending |
| MGMT-06 | Phase 4 | Pending |
| MGMT-07 | Phase 4 | Pending |
| MGMT-08 | Phase 4 | Pending |
| MGMT-09 | Phase 4 | Pending |
| MGMT-10 | Phase 7 | Pending |
| MGMT-11 | Phase 4 | Pending |
| ANLT-01 | Phase 7 | Pending |
| ANLT-02 | Phase 7 | Pending |
| ANLT-03 | Phase 4 | Pending |
| ANLT-04 | Phase 4 | Pending |
| ANLT-05 | Phase 7 | Pending |

| STUD-01 | Phase 03.2 | Pending |
| STUD-02 | Phase 03.2 | Pending |
| STUD-03 | Phase 03.2 | Pending |
| STUD-04 | Phase 03.2 | Pending |
| STUD-05 | Phase 03.2 | Pending |
| STUD-06 | Phase 03.2 | Pending |
| STUD-07 | Phase 03.2 | Pending |
| STUD-08 | Phase 03.2 | Pending |
| STUD-09 | Phase 03.2 | Pending |
| STUD-10 | Phase 03.2 | Pending |
| STUD-11 | Phase 03.2 | Pending |
| ACCT-01 | Phase 03.3 | Pending |
| ACCT-02 | Phase 03.3 | Pending |
| ACCT-03 | Phase 03.3 | Pending |
| ACCT-04 | Phase 03.3 | Pending |
| ACCT-05 | Phase 03.3 | Pending |
| ACCT-06 | Phase 03.3 | Pending |
| ACCT-07 | Phase 03.3 | Pending |
| GAP-01 | Phase 03.1 (gaps) | Complete |
| GAP-02 | Phase 03.1 (gaps) | Complete |
| GAP-03 | Phase 03.1 (gaps) | Complete |
| GAP-04 | Phase 03.1 (gaps) | Complete |
| GAP-05 | Phase 03.1 (gaps) | Complete |

**Coverage:**
- v1 requirements: 85 total (62 original + 11 student + 7 accounts + 5 gap closure)
- Mapped to phases: 85
- Unmapped: 0

---
*Requirements defined: 2026-03-17*
*Last updated: 2026-03-19 after strategic pivot (accounts fork + student portal + gap closure)*

# Feature Research: University ERP Dashboards, Analytics & Role-Based Portals

**Domain:** University ERP management dashboards and multi-role portal system (Indian higher education context)
**Researched:** 2026-03-17
**Confidence:** HIGH (based on existing codebase analysis + competitor research + Indian ERP market analysis)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete or gets rejected during evaluation.

#### Management Dashboards

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Real-time KPI counters (enrollment, fee collection, attendance today) | Every competitor (MasterSoft, Academia, Camu) shows these on landing page. Leadership opens dashboard to see "how is today going" | LOW | Backend exists in `executive_dashboard.py` with `get_overview_metrics()`. Frontend widget rendering needed |
| Enrollment trend chart (monthly/yearly) | Decision-makers need to see trajectory, not just current state. Standard in MasterSoft VC dashboard | LOW | Backend exists in `get_enrollment_trend()`. Chart component needed |
| Financial summary (monthly collection, yearly collection, outstanding) | Finance Officer needs this daily. Fee collection is the lifeblood metric for Indian private universities | LOW | Backend exists in `get_financial_summary()`. Needs currency formatting, period selectors |
| Department-wise comparison table | VCs and Deans compare departments constantly. MasterSoft explicitly targets this for VC decision-making | MEDIUM | Backend scaffold exists in `get_department_performance()` but attendance/pass rate are mocked. Needs real data aggregation |
| Alert/notification panel on dashboard | Overdue fees, SLA breaches, low attendance departments -- leadership needs "what needs my attention now" | LOW | Backend exists in `get_alerts()`. Frontend notification component needed |
| Academic year / semester filter on all views | Data without context is noise. Users must be able to filter by period | LOW | Filter parameter exists on backend. Needs consistent UI filter bar |
| Role-based dashboard routing | VC sees different KPIs than Finance Officer. Every competitor does persona-based dashboards | MEDIUM | `get_user_portal_type()` exists for portal routing. Needs management role detection (VC, Registrar, Finance Officer, Dean) and per-role widget configuration |

#### Faculty Portal

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Today's classes / timetable view | Faculty opens portal in the morning to see "what do I teach today". Table stakes across all competitors | LOW | `get_today_classes()` API exists in portal_api.py. Needs Vue view |
| Attendance marking interface | Primary faculty action. Must be fast (mark 60 students in < 2 minutes). MyLeadingCampus and MasterSoft highlight this as key faculty feature | MEDIUM | `mark_attendance()` API exists. Needs efficient bulk-select UI (select-all, toggle absent) |
| Grade / marks entry | Second most common faculty action. Assessment result submission per course | MEDIUM | `submit_assessment_results()` API exists. Needs spreadsheet-like grid entry UI |
| Student list per course/section | Faculty needs "who is in my class" -- basic reference data | LOW | Requires API to fetch enrolled students by course schedule |
| Leave request view and approval | Faculty approves student leave. Already an expected workflow in Indian university ERPs | LOW | `approve_leave_request()` API exists. Needs list + action UI |
| Pending tasks summary | "What needs my action" -- attendance not marked, grades not submitted, leave requests pending | LOW | `get_pending_tasks()` API exists. Dashboard widget needed |
| Announcements / notices | Faculty needs to see institutional announcements. Standard across all portals | LOW | `get_faculty_announcements()` API exists. Read-only list view |

#### HOD Portal

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Everything in Faculty Portal | HOD is a faculty member first. Must see own classes, mark own attendance, enter own grades | LOW | Inherit faculty portal routes. HOD flag triggers additional menu items |
| Department attendance overview | HOD monitors which courses have low attendance in their department | MEDIUM | Needs aggregation query: attendance by course/faculty within department |
| Faculty workload summary | HOD assigns workload. Needs to see who is over/under-loaded | LOW | `faculty_workload_summary` report exists in backend. Needs portal view |
| Approval workflows (leave, academic requests) | HODs approve faculty leave, student requests, academic proposals. SAMARTH ERP and Kerala KREAP both document HOD approval as core | MEDIUM | Frappe workflow engine available. Needs portal UI for pending approvals queue |
| Department student performance summary | Pass rates, fail rates, at-risk students by course within department | MEDIUM | Needs aggregation API. `student_performance_analysis` report exists as starting point |
| Department-level KPIs | Attendance rate, pass rate, fee collection for the HOD's department vs targets | MEDIUM | Subset of executive dashboard data filtered to one department. KPI Definition doctype supports this |

#### Parent Portal

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Child selector (for parents with multiple children) | Parents may have 2-3 children enrolled. Must switch context | LOW | `get_linked_children()` API exists. Dropdown component needed |
| Attendance summary and calendar | Parents want to know if their child is attending class. Highlighted by every Indian ERP vendor | LOW | Reuse student portal attendance API via `get_child_attendance_summary()`. Calendar heatmap view |
| Current semester grades / results | "How is my child performing?" -- primary parent concern | LOW | Reuse student results API with parent auth wrapper |
| Fee status and payment history | "What do I owe, what have I paid?" -- direct financial concern | LOW | `get_child_fee_summary()` exists. Add payment history list |
| Online fee payment | Parents pay fees online. Razorpay/PayU integration already exists. Competitors all offer this | MEDIUM | Payment gateway integration exists for student portal. Needs parent-auth wrapper and child-context payment flow |
| Announcements and notices | Parents want institutional communications | LOW | Reuse announcement API |
| Timetable view (read-only) | Parents want to know their child's schedule | LOW | Reuse student timetable API |

#### Analytics & Reporting

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| PDF export of any report | Users need to print or email reports. Universal expectation | LOW | Frappe has built-in PDF generation. Needs export button on report views |
| Excel export of any report | Finance teams live in Excel. Non-negotiable | LOW | Frappe has built-in CSV/Excel export. Needs export button |
| Pre-built reports (fee defaulters, attendance summary, placement stats) | 58 reports already exist in backend. Exposing them through portal is table stakes | LOW | Reports exist. Need portal-accessible report viewer component |
| Date range / period filters on reports | Every report needs "from when to when" | LOW | Standard filter pattern |
| Department / program filters on reports | Users need to narrow data scope | LOW | Standard filter pattern |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but create "wow" moments and competitive advantage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Drill-down navigation (summary -> department -> program -> student) | Most Indian ERPs show flat tables. Interactive drill-down from institutional summary to individual student is rare. MasterSoft mentions it but few implement it well | HIGH | Requires hierarchical data architecture. Each KPI widget links to detail view, which links to individual records. Complex routing + data loading |
| Scheduled reports via email | Automate "Monday morning VC report" delivery. Only premium ERPs (Ellucian, Camu) offer this. Backend doctype `ScheduledReport` already exists with frequency/recipient/email support | MEDIUM | Backend is 80% complete (doctype + scheduler logic). Needs configuration UI and report template formatting |
| NAAC/NIRF accreditation report generation | Indian universities spend months compiling accreditation data. Auto-generating criterion-wise NAAC reports from live data is a major differentiator. MasterSoft advertises "300 NAAC-ready reports" | HIGH | OBE module has `naac_criterion_progress` and `nirf_parameter_report`. Needs compilation into submission-ready format with evidence links |
| CO-PO attainment visualization in HOD/faculty portal | Outcome-Based Education compliance is mandatory for NAAC A+ grade. Visual CO-PO heatmaps in portal (not just Frappe desk reports) differentiate | MEDIUM | `co_po_attainment`, `co_po_mapping_matrix` reports exist. Needs visual heatmap component in Vue portal |
| Comparative analytics (year-over-year, batch-over-batch) | "Are we improving?" is the strategic question. Trend comparison across academic years is powerful for leadership | MEDIUM | Needs time-series data architecture. `get_enrollment_trend()` is a prototype. Extend pattern to all KPIs |
| Real-time alert thresholds with notifications | KPI breaches trigger WhatsApp/email alerts to relevant stakeholders. Goes beyond passive dashboards to proactive monitoring | MEDIUM | KPI Definition has threshold fields (red/yellow/green). WhatsApp integration exists. Connect threshold breach -> notification |
| Faculty performance analytics (teaching effectiveness, research output, feedback scores) | Helps HODs and Deans make data-driven faculty evaluation decisions. `faculty_feedback_report` and `faculty_research_output` reports exist | MEDIUM | Aggregate feedback scores + research output + workload into faculty scorecard view |
| Student risk scoring (dropout prediction based on attendance + grades + fees) | Proactively identify at-risk students before they drop out. Rare in Indian ERPs outside Camu | HIGH | Requires composite scoring algorithm from attendance, academic performance, and fee payment patterns. No existing backend |
| Customizable dashboard widgets (drag-and-drop layout) | Let VCs/Registrars arrange their own dashboard. `Custom Dashboard` and `Dashboard Widget` doctypes already exist | HIGH | Backend doctypes exist for widget configuration. Needs drag-and-drop Vue grid layout (complex frontend) |
| Parent-faculty messaging through portal | Direct communication channel. Only some competitors offer this. `send_message_to_faculty()` API already exists | LOW | API exists. Needs chat-like UI in parent portal and notification in faculty portal |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time chat/messaging system | "WhatsApp-like communication" between all stakeholders | Massive infrastructure (WebSocket, message storage, read receipts, moderation). Not core to decision-making. Already out of scope per PROJECT.md | Use existing WhatsApp integration for notifications. Use Frappe Communication for formal messages. Messaging is a product, not a feature |
| Custom report builder in portal | "Let any user create their own reports" | Report building requires understanding data models. Non-technical users create broken/slow reports. Security risk (SQL injection surface). Maintenance nightmare | Expose the 58 existing curated reports with filters. Add new reports by request through admin. Use Frappe Query Report for power users in desk |
| Mobile native app | "We need an app on Play Store" | Separate codebase, app store approval cycles, update distribution lag. Already out of scope per PROJECT.md | Responsive Vue SPA works on mobile browsers. Add PWA manifest for "Add to Home Screen" experience. Covers 95% of mobile use cases |
| AI-powered predictive analytics | "AI predicts enrollment, revenue, student success" | Requires ML pipeline, training data, model maintenance. Overpromises and underdelivers with small datasets typical of single universities | Simple rule-based risk scoring (attendance < 60% + 2+ backlogs = at-risk). Trend lines with linear projection. Honest about limitations |
| Multi-campus real-time sync | "Unified view across all campuses with real-time data" | If this is a single-university deployment, not needed. If multi-campus, adds massive complexity (data isolation, cross-campus permissions, network latency) | Single database serves single university. Multi-campus is a separate deployment concern, not a portal feature |
| Granular permission builder in portal | "Each user should configure what they see" | Exponential permission combinations, testing nightmare, support burden. Users don't want to configure, they want sensible defaults | Role-based defaults (VC sees everything, HOD sees department, Faculty sees own courses). Fixed permission model covers 95% of needs |
| Dashboard that refreshes every 5 seconds | "Real-time like a stock ticker" | Unnecessary DB load. University data doesn't change that fast. 60 students marked present doesn't need sub-second updates | Refresh on page load + manual refresh button. Auto-refresh every 5 minutes is more than sufficient. Stale-while-revalidate caching pattern |
| Full BI/OLAP engine | "Build a data warehouse with cube definitions" | Massive scope, wrong tool. Frappe/MariaDB is OLTP, not OLAP. Would require separate infrastructure | Pre-computed KPI values stored in KPI Value doctype (already exists), refreshed by cron. Gets 80% of BI value at 10% of cost |

## Feature Dependencies

```
[Role-based Auth & Routing]
    |
    +--requires--> [User-to-Role Mapping] (Student/Faculty/HOD/Parent/Management detection)
    |                  |
    |                  +--exists--> get_user_portal_type() in portal_api.py
    |
    +--enables--> [Faculty Portal]
    |                 |
    |                 +--requires--> [Timetable View] (today's classes)
    |                 +--requires--> [Attendance Marking UI]
    |                 +--requires--> [Grade Entry UI]
    |                 +--enhances--> [Student Performance View]
    |
    +--enables--> [HOD Portal]
    |                 |
    |                 +--requires--> [Faculty Portal] (HOD is superset of Faculty)
    |                 +--requires--> [Department Data Aggregation APIs]
    |                 +--requires--> [Approval Workflow UI]
    |                 +--enhances--> [CO-PO Attainment Visualization]
    |
    +--enables--> [Parent Portal]
    |                 |
    |                 +--requires--> [Child Selector Component]
    |                 +--requires--> [Student Data APIs with Parent Auth]
    |                 +--enhances--> [Online Fee Payment (parent context)]
    |                 +--enhances--> [Parent-Faculty Messaging]
    |
    +--enables--> [Management Dashboards]
                      |
                      +--requires--> [KPI Widget Components]
                      +--requires--> [Chart Components (line, bar, pie)]
                      +--requires--> [Data Aggregation APIs]
                      +--enhances--> [Drill-Down Navigation]
                      +--enhances--> [Scheduled Reports]
                      +--enhances--> [NAAC Report Generation]

[Shared Component Library]
    |
    +--enables--> [KPI Card Widget]
    +--enables--> [Chart Wrapper (line, bar, pie, heatmap)]
    +--enables--> [Data Table with Export]
    +--enables--> [Filter Bar (date range, department, program)]
    +--enables--> [Report Viewer]
```

### Dependency Notes

- **HOD Portal requires Faculty Portal:** HOD inherits all faculty features plus adds department-level views and approvals. Build faculty first, then layer HOD on top.
- **Management Dashboards require Data Aggregation APIs:** Dashboard widgets need backend APIs that aggregate across departments/programs. These APIs serve both dashboards and drill-down views.
- **Drill-Down requires KPI Widgets + Detail Views:** Each KPI counter must link to a breakdown view. Both the counter component and the detail view must exist.
- **Parent Portal requires Student Data APIs with auth wrapper:** Reuses student portal data but needs guardian authentication and child-context scoping. Student APIs must be refactored to accept student ID parameter (currently they auto-detect logged-in student).
- **Scheduled Reports requires Report Viewer:** Must be able to render reports in PDF/Excel format for email attachment. Report viewer component is needed first.
- **NAAC Reports enhances but does not block Management Dashboards:** Accreditation reporting is valuable but not needed for initial dashboard launch.

## MVP Definition

### Launch With (v1)

Minimum viable product -- what's needed to demonstrate value and get daily usage.

- [ ] **Role-based auth and routing** -- Gate everything. Without this, nothing works. Detect user type, route to correct portal
- [ ] **Shared component library** -- KPI card, chart wrapper, data table with export, filter bar. These are reused across every portal
- [ ] **Faculty Portal: Timetable + Attendance Marking + Grade Entry** -- The three actions faculty do daily/weekly. Most API scaffolding exists
- [ ] **Faculty Portal: Pending tasks dashboard** -- "What needs my action today" summary landing page
- [ ] **Management Dashboard: KPI counters (6-8 key metrics)** -- Total students, fee collection today/month, attendance rate, pending grievances, pass rate, faculty count. Executive dashboard backend exists
- [ ] **Management Dashboard: Enrollment trend chart + Financial summary** -- Two charts to show trajectory. Backend exists
- [ ] **Management Dashboard: Department comparison table** -- Needs real data aggregation (currently mocked)
- [ ] **Management Dashboard: Alert panel** -- What needs attention. Backend exists
- [ ] **Parent Portal: Child selector + attendance + grades + fees** -- Core "how is my child doing" view. APIs exist or can reuse student portal
- [ ] **Shared: Academic year/semester filter** -- Without context filters, data is meaningless
- [ ] **Shared: PDF and Excel export on all data tables** -- Use Frappe built-in export. Low effort, high value

### Add After Validation (v1.x)

Features to add once core portals are in daily use and feedback is gathered.

- [ ] **HOD Portal: Department analytics + approval workflows** -- Add when faculty portal is stable. HOD is faculty + department views
- [ ] **HOD Portal: Faculty workload + CO-PO attainment views** -- When OBE/NAAC prep ramps up
- [ ] **Management Dashboard: Drill-down navigation** -- Add when users complain about lack of detail behind KPI counters
- [ ] **Scheduled Reports** -- Add when leadership asks "can I get this emailed every Monday". Backend doctype ready
- [ ] **Parent Portal: Online fee payment** -- Add when parents request it. Payment gateway exists for student portal
- [ ] **Faculty Portal: Student performance analytics per course** -- Add when faculty want "which students are struggling in my class"
- [ ] **Comparative analytics (YoY trends)** -- Add when leadership asks "are we improving from last year"
- [ ] **Parent-Faculty messaging** -- Add when parents request direct communication. API exists
- [ ] **Real-time alert thresholds with WhatsApp notifications** -- Add when passive dashboard is not enough

### Future Consideration (v2+)

Features to defer until product-market fit is established and v1.x is stable.

- [ ] **NAAC/NIRF auto-report generation** -- Complex compilation. Defer until accreditation cycle approaches
- [ ] **Student risk scoring** -- Requires scoring algorithm design and validation against real outcomes
- [ ] **Customizable dashboard widgets (drag-drop)** -- Backend doctypes exist but frontend is complex. Defer until role-based defaults prove insufficient
- [ ] **Faculty performance scorecards** -- Sensitive. Needs institutional buy-in and metric agreement before building
- [ ] **PWA manifest for mobile home screen** -- Low effort but defer until responsive design is validated on real devices

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Role-based auth & routing | HIGH | MEDIUM | P1 |
| Shared component library (KPI card, chart, table, filter) | HIGH | MEDIUM | P1 |
| Faculty: timetable view | HIGH | LOW | P1 |
| Faculty: attendance marking | HIGH | MEDIUM | P1 |
| Faculty: grade entry | HIGH | MEDIUM | P1 |
| Faculty: pending tasks dashboard | HIGH | LOW | P1 |
| Mgmt: KPI counters | HIGH | LOW | P1 |
| Mgmt: enrollment trend + financial chart | MEDIUM | LOW | P1 |
| Mgmt: department comparison table | HIGH | MEDIUM | P1 |
| Mgmt: alert panel | MEDIUM | LOW | P1 |
| Parent: child selector + summary | HIGH | LOW | P1 |
| Parent: attendance view | HIGH | LOW | P1 |
| Parent: grades/results view | HIGH | LOW | P1 |
| Parent: fee status | HIGH | LOW | P1 |
| Shared: academic year/semester filter | HIGH | LOW | P1 |
| Shared: PDF/Excel export | HIGH | LOW | P1 |
| HOD: department analytics | HIGH | MEDIUM | P2 |
| HOD: approval workflows | HIGH | MEDIUM | P2 |
| HOD: faculty workload view | MEDIUM | LOW | P2 |
| Mgmt: drill-down navigation | HIGH | HIGH | P2 |
| Scheduled reports | MEDIUM | MEDIUM | P2 |
| Parent: online fee payment | HIGH | MEDIUM | P2 |
| Faculty: student performance analytics | MEDIUM | MEDIUM | P2 |
| CO-PO visualization | MEDIUM | MEDIUM | P2 |
| Comparative YoY analytics | MEDIUM | MEDIUM | P2 |
| Parent-faculty messaging | LOW | LOW | P2 |
| Alert thresholds + WhatsApp | MEDIUM | MEDIUM | P2 |
| NAAC report generation | HIGH (at accreditation time) | HIGH | P3 |
| Student risk scoring | MEDIUM | HIGH | P3 |
| Customizable dashboard widgets | LOW | HIGH | P3 |
| Faculty performance scorecards | MEDIUM | HIGH | P3 |
| PWA manifest | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for launch -- daily usage features
- P2: Should have -- add in subsequent releases based on feedback
- P3: Nice to have -- defer until clear demand

## Competitor Feature Analysis

| Feature | MasterSoft CCMS | Academia ERP | Camu | MyLeadingCampus | Our Approach |
|---------|----------------|--------------|------|-----------------|--------------|
| VC Dashboard with KPIs | Yes, AI-powered BI. Graphical formats (pie, bar, tables) | Yes, real-time analytics | Yes, one-click analytics | Yes, real-time metrics | Role-based Vue dashboards with drill-down. Leverage existing 58 reports + KPI Definition doctype |
| Faculty Portal | Attendance, gradebook, timetable, lesson planning | Attendance, marks, timetable | Course mgmt, attendance, grades | Mark upload, attendance, CO mapping | Vue SPA: timetable + attendance + grades + pending tasks. APIs already scaffolded |
| Parent Portal | Attendance, fees, results, WhatsApp alerts | Attendance, fees, performance | Attendance, fees, notices | Attendance, fees, performance, notices | Vue SPA: child selector + reuse student portal data APIs + fee payment |
| HOD Portal | Department oversight, faculty workload | Student progression, CO-PO | Department analytics | Academic oversight, compliance | Faculty portal + department aggregation + approval queue |
| NAAC Reports | 300+ NAAC-ready reports, SSR auto-generation | NAAC/NBA/AISHE reports | Simplified accreditation | Criterion-wise NAAC data | 7 OBE/accreditation reports exist. Compilation into submission format is P3 |
| Scheduled Reports | Available | Available, automated notifications | Built-in | Auto-generated | ScheduledReport doctype exists with email delivery. Needs config UI (P2) |
| Drill-Down | Mentioned for VC dashboard | Drill into student profiles, retention, budgets | Not highlighted | Not highlighted | Our differentiator: summary -> dept -> program -> student navigation (P2) |
| Export | Excel, PDF | Excel, PDF | Excel, PDF | Excel, PDF | Frappe built-in export. Table stakes (P1) |
| Mobile App | Native app | Mobile responsive + app | Cloud-based responsive | App-based | Responsive Vue SPA, PWA later. Web-first per project constraints |

## Existing Backend Assets (Advantage)

The codebase has significant backend infrastructure already built. This shifts implementation effort from "build from scratch" to "wire up frontend views to existing APIs":

**Already implemented:**
- Executive dashboard API with overview metrics, enrollment trend, financial summary, department performance, alerts, KPI summary
- KPI Definition doctype with threshold-based status (Green/Yellow/Red), multiple calculation methods (SQL, Python, Formula)
- Scheduled Report doctype with frequency scheduling (daily/weekly/monthly/quarterly), recipient management, email delivery
- Custom Dashboard and Dashboard Widget doctypes for configurable dashboards
- 58 backend reports across finance, academics, placement, library, hostel, OBE, inventory, research, transport
- Portal API with student (13 endpoints), faculty (4 endpoints), parent (4 endpoints) methods
- User-to-role detection (`get_user_portal_type()`)
- Student portal Vue app with 11 pages (reference architecture for new portals)

**Needs building:**
- Vue frontend components for faculty, HOD, parent, management portals
- Department-level data aggregation APIs (currently mocked in executive dashboard)
- Real attendance/pass rate calculations (hardcoded in department performance)
- HOD-specific APIs (department analytics, approval queues)
- Management role detection (VC, Registrar, Finance Officer, Dean -- currently only Student/Faculty/Parent/Alumni)
- Shared component library (KPI cards, charts, filter bars, data tables with export)

## Sources

- [MasterSoft VC Dashboard Features](https://www.iitms.co.in/blog/how-university-dashboard-can-help-vice-chancellors-to-leverage-decision-making.html)
- [MyLeadingCampus Complete ERP Guide 2026](https://www.myleadingcampus.com/blogview/what-is-college-university-erp-a-complete-practical-guide-for-autonomous-colleges-and-deemed-universities-2025-edition)
- [Top 5 College ERP Systems India 2026](https://www.myleadingcampus.com/blogview/top-5-college-management-erp-systems-in-india-what-makes-them-the-best-in-2025)
- [MasterSoft NAAC Accreditation Module](https://www.iitms.co.in/products/naac-accreditation/)
- [Camu University Management Software](https://camudigitalcampus.com/university-management-erp-software/)
- [Academia ERP University Management](https://www.academiaerp.com/university-management-system-software/)
- [Kerala KREAP HOD Approval Process](https://kerala.kreap.co.in/user/pages/files/hodapproval.pdf)
- [Ellucian Reporting & Analytics](https://www.ellucian.com/products/platform/reporting-analytics)
- [Education KPI Dashboard Examples](https://www.simplekpi.com/KPI-Dashboard-Examples/Education-KPI-Dashboard-Example)
- [EDUCAUSE: Dean's Information Challenge](https://er.educause.edu/articles/2016/11/the-deans-information-challenge-from-data-to-dashboard)
- Existing codebase analysis: `executive_dashboard.py`, `portal_api.py`, `kpi_definition.py`, `scheduled_report.py`, 58 backend reports

---
*Feature research for: University ERP Dashboards, Analytics & Role-Based Portals*
*Researched: 2026-03-17*

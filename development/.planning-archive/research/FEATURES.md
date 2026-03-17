# Feature Research

**Domain:** University ERP — Dashboards, Analytics & KPIs across 21 modules
**Researched:** 2026-03-17
**Confidence:** HIGH (based on direct codebase analysis of all 21 modules + DocType inventory)

---

## Research Method

All findings are derived from direct inspection of the codebase:
- DocType inventory across all 21 modules (source data available for each KPI)
- Existing report files already present per module (what the team already valued)
- Scheduled task definitions (what metrics are computed nightly)
- Hooks and overrides (what events generate trackable data)

No WebSearch was available. Confidence is HIGH because KPI choices are grounded in what data the system actually stores — not speculation about a generic ERP.

---

## Module Inventory (All 21)

| # | Module Key | Module Name | Primary DocTypes |
|---|-----------|-------------|-----------------|
| 1 | university_erp | University ERP (core/settings) | Settings, Announcement, Alumni |
| 2 | university_academics | University Academics | Course Registration, Teaching Assignment, Timetable Slot |
| 3 | university_admissions | University Admissions | Admission Cycle, Merit List, Seat Matrix, Admission Criteria |
| 4 | university_student_info | University Student Info | Student Status Log, University Alumni, University Announcement |
| 5 | university_examinations | University Examinations | Online Exam, Hall Ticket, Answer Sheet, Question Bank, Internal Assessment, Revaluation Request, Student Transcript |
| 6 | university_finance | University Finance | Fees (override), Bulk Fee Generator, Fee Category, Fee Payment, Fee Refund, Scholarship |
| 7 | university_payments | University Payments | Payment Order, Bank Transaction, Razorpay/PayU Settings, Webhook Log |
| 8 | faculty_management | Faculty Management | Faculty Profile, Teaching Assignment, Leave Affected Course, Faculty Publication, Workload Distributor |
| 9 | university_hostel | University Hostel | Hostel Building, Hostel Room, Hostel Allocation, Hostel Attendance, Mess Menu, Maintenance Request, Visitor |
| 10 | university_transport | University Transport | Transport Vehicle, Transport Route, Transport Route Stop, Transport Allocation, Trip Log |
| 11 | university_library | University Library | Library Article, Library Transaction, Library Fine, Book Reservation, Library Member |
| 12 | university_placement | University Placement | Placement Drive, Placement Company, Placement Job Opening, Placement Application, Placement Round |
| 13 | university_lms | University LMS | LMS Course, LMS Content, LMS Assignment, LMS Quiz, Content Progress, Discussion |
| 14 | university_research | University Research | Research Project, Research Grant, Research Publication, Grant Utilization |
| 15 | university_obe | University OBE | Course Outcome, Program Outcome, CO Attainment, PO Attainment, Accreditation Cycle, Survey |
| 16 | university_integrations | University Integrations | SMS Log, WhatsApp Log, Push Notification Log, Email Queue, Biometric Log, Certificate |
| 17 | university_portals | University Portals | Alumni, Alumni Donation, Alumni Event, Job Posting, Announcement |
| 18 | university_inventory | University Inventory | Lab Equipment, Inventory Item, Asset, Stock Ledger, Purchase Order, Material Request |
| 19 | university_grievance | University Grievance | Grievance, Grievance Action, SLA Escalation Log, Committee |
| 20 | university_analytics | University Analytics | KPI Definition, KPI Value, Custom Dashboard, Dashboard Widget, Scheduled Report |
| 21 | university_feedback | University Feedback | Feedback Form, Feedback Response, Feedback Course Filter, Section Score |

---

## Feature Landscape

### Table Stakes (Users Expect These)

These are the KPIs and dashboard features that any university administrator opening this ERP expects to see. Missing them makes the product feel incomplete or unfinished.

#### Module 1: University ERP (Core / Settings Dashboard)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total active students (KPI card) | Every ERP opens with headcount | LOW | Count from Student DocType where status = Active |
| Total faculty / staff count (KPI card) | Companion to student count | LOW | Count from Employee DocType, filter by department_type |
| Current academic year + active programs (KPI card) | Orientation, confirms system state | LOW | From Academic Year + Program |
| Recent announcements list | Admins post announcements; need visibility | LOW | From University Announcement DocType |
| System health indicators | Scheduled task success/fail | MEDIUM | From background job logs — how many tasks ran/failed today |

#### Module 2: University Academics

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total course registrations this semester (KPI card) | Enrollment pulse | LOW | Count Course Registration by academic term |
| Attendance rate (institution-wide %) (KPI card) | Regulatory compliance; mandatory in most universities | MEDIUM | Aggregate from Student Attendance DocType |
| Courses with attendance below threshold (KPI card) | Immediate action list | MEDIUM | Join Course Schedule + Attendance, threshold from settings |
| Attendance trend — monthly line chart | Track if attendance is improving or declining | MEDIUM | Group Student Attendance by month |
| Program-wise enrollment bar chart | Which programs are most enrolled | LOW | Group Course Registration by program |
| Department-wise course count | Load distribution visibility | LOW | Group Teaching Assignment by department |
| Students at risk (attendance < 75%) count | Regulatory requirement (India: 75% mandatory) | MEDIUM | Count students below threshold |
| Timetable slot utilization table | Are classrooms/slots being used | MEDIUM | Timetable Slot counts vs total available |

#### Module 3: University Admissions

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total applicants this cycle (KPI card) | First number everyone asks | LOW | Count Student Applicant by admission cycle |
| Conversion rate: applicants → enrolled (KPI card) | Core admissions funnel metric | LOW | Enrolled count / total applicants |
| Program-wise seat fill rate (bar chart) | Which programs filled, which didn't | MEDIUM | Merit List + Seat Matrix comparison |
| Applicant funnel chart (applied → shortlisted → offered → enrolled) | Classic admissions funnel | MEDIUM | Stage-wise count from Student Applicant workflow |
| Category-wise applicant breakdown (pie chart) | SC/ST/OBC/General splits mandatory for NAAC | MEDIUM | Group Student Applicant by category |
| Merit list status summary table | How many shortlisted per program | LOW | Count Merit List Applicant by status |
| Applications over time (line chart) | When do applications peak | LOW | Group Student Applicant by creation date |
| Program-wise acceptance rate table | Selectivity indicator | LOW | Offered/Applied per program |

#### Module 4: University Student Info

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Active vs. inactive student breakdown (KPI cards) | Lifecycle tracking | LOW | Count from Student Status Log |
| Student category distribution (pie chart) | Required for regulatory reports | LOW | Group Student by category |
| Program-wise student headcount (bar chart) | Load distribution | LOW | Group Student by program |
| Batch/year-wise distribution table | Longitudinal visibility | LOW | Group Student by batch year |
| New students this month (KPI card) | Enrollment momentum | LOW | Count Student where creation >= first of month |
| Dropout / withdrawal count this year (KPI card) | Retention metric | MEDIUM | Count status changes to Inactive/Withdrawn |
| Alumni count (KPI card) | Outcome metric | LOW | Count University Alumni DocType |

#### Module 5: University Examinations

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Exams scheduled this month (KPI card) | Calendar awareness | LOW | Count Exam Schedule by date range |
| Hall tickets generated vs. eligible students (KPI card) | Process completion | LOW | Count Hall Ticket vs eligible course registrations |
| Pass rate (overall %) (KPI card) | Most-watched academic metric | MEDIUM | Count Assessment Result: pass/total |
| Average score by subject (bar chart) | Performance by course | MEDIUM | Aggregate Assessment Result by course |
| Grade distribution pie chart (A/B/C/D/F) | Result pattern | MEDIUM | Group Assessment Result by grade bucket |
| Internal vs. external assessment comparison (bar chart) | Academic quality indicator | MEDIUM | Internal Assessment Score vs final |
| Revaluation requests count (KPI card) | Process metric | LOW | Count Revaluation Request by status |
| Online exam completion rate (KPI card) | For courses using Online Examination | LOW | Online Exam Student: submitted/enrolled |
| Result publication status table (per exam) | Admin action list | LOW | Exam Schedule by result_published flag |
| Rank list / topper by program table | Ceremonial but expected | MEDIUM | Top-N by CGPA per program |

#### Module 6: University Finance

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total fee collection this month (KPI card, currency) | Primary revenue metric | LOW | Sum Fees.grand_total where paid, current month |
| Total outstanding dues (KPI card, currency) | Cash position | LOW | Sum Fees where outstanding_amount > 0 |
| Collection rate % (KPI card) | Collected / billed ratio | LOW | Derived from above two |
| Fee collection trend — monthly bar chart | Seasonal patterns | LOW | Group Fees by month, sum amount |
| Program-wise fee collection table | Which programs paying | MEDIUM | Group Fees by student program |
| Fee defaulters count (KPI card, drill-down) | Collections action list | LOW | Existing fee_defaulters report |
| Scholarship disbursement total (KPI card) | Financial aid tracking | LOW | Sum Student Scholarship by status |
| Fee category breakdown (pie chart) | Tuition vs hostel vs transport | MEDIUM | Group Fee Payment by fee category |
| Refund processing status table | Process compliance | LOW | Count Fee Refund by status |

#### Module 7: University Payments

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Online payments today (KPI card, count + amount) | Gateway monitoring | LOW | Count Payment Order by date, sum amount |
| Gateway success rate % (KPI card) | Transaction health | LOW | Successful / total Payment Transactions |
| Pending reconciliation count (KPI card) | Accounts action item | LOW | Bank Transaction where unreconciled |
| Daily collection chart (line, last 30 days) | Revenue trend | LOW | Group Payment Order by creation date |
| Gateway-wise breakdown (pie: Razorpay vs PayU) | Which gateway used more | LOW | Group Payment Order by gateway |
| Failed transaction count (KPI card) | Problem indicator | LOW | Count Payment Transaction where status = Failed |
| Webhook delivery log summary table | Integration health | MEDIUM | Count Webhook Log by status today |

#### Module 8: Faculty Management

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total faculty count (KPI card) | Staff roster baseline | LOW | Count Employee where department_type = Academic |
| Faculty-to-student ratio (KPI card) | Regulatory requirement | LOW | Total students / total faculty |
| Leave utilization rate % (KPI card) | HR planning | LOW | Existing leave_utilization_report |
| Department-wise faculty headcount (bar chart) | Staffing distribution | LOW | Group Employee by department |
| Teaching workload summary (hours/faculty) (table) | Equity and compliance | MEDIUM | Existing faculty_workload_summary report |
| Pending leave applications (KPI card) | Action queue | LOW | Count Leave Application where status = Open |
| Faculty publications this year (KPI card) | Research output | LOW | Count Faculty Publication by year |
| Performance metric: avg student feedback score (KPI card) | Teaching quality indicator | MEDIUM | Average Feedback Response score by faculty |
| Temporary teaching assignment count (KPI card) | Ad-hoc staffing visibility | LOW | Count Temporary Teaching Assignment |

#### Module 9: University Hostel

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total rooms vs. occupied rooms (KPI cards) | Occupancy baseline | LOW | Hostel Room count vs Hostel Allocation active |
| Occupancy rate % (KPI card) | Core metric | LOW | Allocated / total rooms |
| Building-wise occupancy breakdown (bar chart) | Which buildings are full | LOW | Group Hostel Allocation by hostel_building |
| Pending maintenance requests (KPI card) | Facilities action queue | LOW | Count Hostel Maintenance Request where status = Open |
| Hostel attendance rate (% present today) | Safety / compliance | MEDIUM | Hostel Attendance for today |
| Visitor log count this week (KPI card) | Security metric | LOW | Count Hostel Visitor by date range |
| Mess menu coverage days (KPI card) | Operational completeness | LOW | Count Mess Menu by date |
| Available room slots by type (table) | Admission team needs | LOW | Hostel Room by room_type where occupancy < capacity |

#### Module 10: University Transport

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total vehicles (KPI card) | Fleet baseline | LOW | Count Transport Vehicle |
| Students using transport (KPI card) | Utilization baseline | LOW | Count Transport Allocation |
| Route-wise student count (bar chart) | Route load distribution | LOW | Existing route_wise_students report |
| Vehicle utilization rate % (KPI card) | Fleet efficiency | LOW | Existing vehicle_utilization report |
| Transport fee collection (KPI card, currency) | Revenue from transport | LOW | Existing transport_fee_collection report |
| Active routes count (KPI card) | Operational footprint | LOW | Count Transport Route where status = Active |
| Trip log compliance (trips completed / scheduled) | Operational reliability | MEDIUM | Trip Log count vs expected trips |

#### Module 11: University Library

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total books / articles in collection (KPI card) | Collection baseline | LOW | Count Library Article |
| Books currently issued (KPI card) | Circulation snapshot | LOW | Count Library Transaction where return_date IS NULL |
| Overdue books count (KPI card) | Action queue for reminders | LOW | Existing overdue_books report |
| Total fines collected this month (KPI card, currency) | Revenue + compliance | LOW | Sum Library Fine where paid, current month |
| Active library members count (KPI card) | Engagement | LOW | Count Library Member where status = Active |
| Books issued per day (line chart, 30 days) | Circulation trend | LOW | Group Library Transaction by date |
| Most-borrowed books (table, top 10) | Collection insights | LOW | Count Library Transaction by article |
| Subject-wise collection breakdown (pie chart) | Collection diversity | LOW | Group Library Article by subject/category |
| Book reservations pending (KPI card) | Demand signal | LOW | Count Book Reservation where status = Pending |

#### Module 12: University Placement

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total students placed this year (KPI card) | #1 metric for placement cell | LOW | Count Placement Application where status = Selected |
| Placement rate % of eligible students (KPI card) | Outcome metric for rankings | MEDIUM | Placed / eligible graduates |
| Average CTC (KPI card, currency) | Compensation benchmark | MEDIUM | Average from Placement Application where selected |
| Highest CTC this year (KPI card, currency) | Marketing metric | LOW | Max CTC from selected applications |
| Companies visited (KPI card) | Recruitment activity | LOW | Count Placement Drive by academic year |
| Program-wise placement rate (bar chart) | Which programs place well | MEDIUM | Existing program_wise_placement report |
| Company-wise placements (bar chart, top 10) | Employer relationships | LOW | Existing company_wise_placement report |
| Placement trend by year (line chart) | Year-on-year progress | MEDIUM | Existing placement_trend report |
| Unplaced eligible students count (KPI card) | Action list | MEDIUM | Eligible students minus placed |
| Open job drives count (KPI card) | Active pipeline | LOW | Count Placement Drive where status = Active |

#### Module 13: University LMS

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total LMS courses published (KPI card) | Content baseline | LOW | Count LMS Course where status = Published |
| Active learners this week (KPI card) | Engagement metric | LOW | Count distinct students with Content Progress update |
| Course completion rate % (KPI card) | Learning effectiveness | MEDIUM | Existing course_progress report |
| Quiz average score (KPI card) | Assessment quality | MEDIUM | Average Quiz Attempt score |
| Assignment submission rate % (KPI card) | Participation | LOW | Existing assignment_submission_report |
| Course-wise enrollment (bar chart, top 10) | Popularity | LOW | Count LMS Content Progress by course |
| Discussion activity (posts per week) (line chart) | Community engagement | LOW | Count LMS Discussion by creation date |
| Content type breakdown (pie: video/document/quiz) | Content mix | LOW | Group LMS Content by content_type |

#### Module 14: University Research

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Active research projects count (KPI card) | Research activity baseline | LOW | Count Research Project where status = Active |
| Total grant funding secured (KPI card, currency) | Funding momentum | LOW | Sum Research Grant.amount |
| Publications this year (KPI card) | Output metric (NAAC/NIRF) | LOW | Count Research Publication by year |
| Grant utilization rate % (KPI card) | Financial accountability | MEDIUM | Existing grant_utilization_report |
| Department-wise publications (bar chart) | Research distribution | LOW | Count Research Publication by department |
| Funding agency breakdown (pie chart) | Diversification | LOW | Group Research Grant by funding_agency |
| Faculty research output table (publications per faculty) | Individual accountability | MEDIUM | Existing faculty_research_output report |
| Patent/IP count (KPI card) | Innovation metric | LOW | Derived from Publication type = Patent |

#### Module 15: University OBE (Outcomes-Based Education)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Average CO attainment % (KPI card) | Core OBE metric | HIGH | Existing co_attainment_report |
| Average PO attainment % (KPI card) | Program-level outcome | HIGH | Existing po_attainment_report |
| CO-PO mapping coverage % (KPI card) | Compliance completeness | MEDIUM | Courses with CO-PO mapping vs total |
| Accreditation cycle status (KPI card: active/pending) | NAAC/NBA awareness | LOW | Accreditation Cycle where status = Active |
| Survey response rate % (KPI card) | Data quality for OBE | MEDIUM | Existing survey_analysis_report |
| Program-wise attainment summary table | Which programs meet targets | HIGH | Existing program_attainment_summary |
| NAAC criterion progress (bar chart) | Accreditation readiness | HIGH | Existing naac_criterion_progress report |
| CO attainment trend by semester (line chart) | Improvement tracking | HIGH | CO Attainment by term |

#### Module 16: University Integrations

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| SMS sent today / this month (KPI cards, count) | Communication volume | LOW | Count SMS Log by date |
| SMS delivery rate % (KPI card) | Gateway health | LOW | Existing sms_delivery_report |
| WhatsApp messages sent this month (KPI card) | Channel comparison | LOW | Count WhatsApp Log by date |
| Email queue depth (KPI card) | System health | LOW | Count Email Queue Extended where status = Queued |
| Push notification sends this month (KPI card) | Mobile engagement | LOW | Count Push Notification Log |
| Certificate requests status table | Student service metric | LOW | Existing certificate_issuance_report |
| Biometric attendance sync status (KPI card) | Device health | MEDIUM | Count Biometric Log by date vs expected |
| Failed communication attempts (KPI card) | Error monitoring | LOW | Count SMS/WhatsApp Log where status = Failed |

#### Module 17: University Portals

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Portal active users today (KPI card) | Engagement baseline | MEDIUM | Session data — requires custom tracking |
| Alumni registered count (KPI card) | Alumni engagement | LOW | Count Alumni DocType |
| Alumni donations this year (KPI card, currency) | Fundraising metric | LOW | Sum Alumni Donation by year |
| Upcoming alumni events (KPI card + list) | Event awareness | LOW | Count Alumni Event where date >= today |
| Job postings active (KPI card) | Alumni network value | LOW | Count Job Posting where status = Active |
| Announcement views (KPI card) | Communication reach | LOW | Count Announcement by reads (if tracked) |

#### Module 18: University Inventory

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Low stock items count (KPI card) | Procurement trigger | LOW | Existing low_stock_items report |
| Pending purchase orders (KPI card, count + value) | Procurement pipeline | LOW | Existing purchase_order_status report |
| Lab equipment booked today (KPI card) | Utilization | LOW | Existing lab_equipment_utilization report |
| Assets under maintenance (KPI card) | Operational availability | LOW | Count Asset Maintenance where status = Open |
| Stock value on hand (KPI card, currency) | Inventory position | MEDIUM | Existing stock_balance report |
| Department-wise asset count (table) | Asset distribution | LOW | Existing asset_register report |
| Upcoming maintenance due (KPI card, this week) | Preventive action | LOW | Asset Maintenance by next_due_date |

#### Module 19: University Grievance

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Open grievances count (KPI card) | Action queue | LOW | Count Grievance where status = Open |
| Grievances resolved this month (KPI card) | Throughput | LOW | Count Grievance where resolved_date in month |
| Average resolution time (days) (KPI card) | SLA performance | MEDIUM | Existing sla_compliance_report |
| SLA breach count (KPI card, red indicator) | Compliance metric | MEDIUM | Existing sla_compliance_report |
| Grievance type breakdown (pie chart) | Root cause visibility | LOW | Existing grievance_summary report |
| Pending vs. resolved trend (line chart) | Queue health | LOW | Group Grievance by status, by month |
| Escalated grievances count (KPI card) | Severity signal | LOW | Count Grievance Escalation Log |

#### Module 20: University Analytics

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Scheduled report run status (table: last run, success/fail) | System health | LOW | Count Scheduled Report by last_run_status |
| KPI alerts triggered this week (KPI card) | Exception monitoring | LOW | Count KPI Definition where alert triggered |
| Dashboard count by module (table) | Coverage visibility | LOW | Count Custom Dashboard by module |
| Cross-module student performance summary | Executive overview | HIGH | Aggregate CGPA + attendance + placement |
| Communication analytics summary (SMS/email/push) | Operational awareness | LOW | Existing communication_analytics report |

#### Module 21: University Feedback

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Active feedback forms count (KPI card) | Collection pulse | LOW | Count Feedback Form where status = Active |
| Total responses collected this month (KPI card) | Participation | LOW | Count Feedback Response by date |
| Average feedback score — institution-wide (KPI card) | Teaching quality indicator | MEDIUM | Average Feedback Section Score |
| Faculty-wise feedback scores (table, ranked) | Actionable for HR | MEDIUM | Existing faculty_feedback_report |
| Department-wise average score (bar chart) | Department comparison | MEDIUM | Group Feedback Response by department |
| Response rate by program (table) | Participation equity | MEDIUM | Existing feedback_analysis report |
| Score trend over semesters (line chart) | Improvement tracking | MEDIUM | Feedback score by academic term |

---

### Differentiators (Competitive Advantage)

Features that go beyond what basic university ERP analytics offer. These provide genuine value without being obviously necessary.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cross-module "at-risk student" composite KPI | Combines attendance + CGPA + fee default + grievance into one risk score per student | HIGH | Requires joining Student, Attendance, Fees, Grievance; alerts faculty proactively |
| Centralized Executive Dashboard (multi-module summary) | VP/Registrar sees entire university on one page — no module hopping | HIGH | Single Frappe workspace with Number Cards from all 21 modules |
| NAAC/NIRF data readiness gauge | Shows percentage of NAAC/NBA criteria with sufficient data, with red/amber/green — accreditation teams need this | HIGH | Joins OBE attainment, research output, student-faculty ratio, placement data |
| Fee collection forecasting (trend line + projection) | Finance team can predict month-end collection before month ends | MEDIUM | Linear projection based on collection rate curve |
| Attendance anomaly detection (sudden drops) | Flags courses/batches where attendance dropped >10% from prior week | MEDIUM | Computes delta from previous week's attendance aggregate |
| Placement vs. branch demand correlation chart | Shows which programs produce placed graduates — admissions insight | MEDIUM | Join Program + Placement Application |
| Faculty workload equity heatmap | Surfaces overloaded vs. underloaded faculty before semester starts | MEDIUM | Teaching Assignment hours by faculty, color-coded |
| CO/PO Bloom's taxonomy distribution chart | Shows if assessments cover all cognitive levels per program | HIGH | Bloom Distribution Rule + Assessment data |
| Library engagement index (issues/member) | Books-per-student metric identifies underutilized library | LOW | Library Transaction count / Library Member count |
| Communication channel effectiveness comparison | Compares response-to-action rates for SMS vs WhatsApp vs email (fee payments prompted) | HIGH | Correlates notification sends with subsequent Fees payments |
| Research grant pipeline value (applied vs. awarded) | R&D fundraising funnel — useful for VP Research | MEDIUM | Research Grant by status (applied/under review/awarded) |
| LMS vs classroom attendance correlation | Does online content access correlate with physical attendance? | HIGH | Correlate Content Progress with Student Attendance by student |
| Grievance root cause Pareto chart | 80/20 view of grievance types — top 20% of types causing 80% volume | LOW | Count Grievance by type, sorted descending |
| Student cohort retention analysis | Of 2022 batch, how many are still active vs dropped — year by year | HIGH | Student Status Log temporal analysis by batch |
| Module-level dashboard for each workspace | Every module workspace has its own summary view rather than list-only | MEDIUM | Frappe Dashboard embedded in each module workspace |

---

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time dashboard auto-refresh (every 30 sec) | "Live" feels modern | Frappe Number Cards use scheduled refresh; forcing real-time requires polling that overloads MariaDB with aggregation queries | Use Frappe's built-in auto-refresh (15-min interval) — sufficient for all KPIs except exam submission |
| Student-facing analytics in Vue SPA | Students want to see their rank/percentile | Scope creep — PROJECT.md explicitly rules this out; student portal analytics is a separate milestone | Deliver admin-side dashboards now; student analytics is next milestone's scope |
| AI/ML predictive analytics (churn prediction, etc.) | Looks impressive in demos | Requires training data pipeline, model serving, MLOps — massively out of scope for a dashboard milestone | Use rule-based thresholds (attendance < 75% = at-risk) — delivers 80% of the value at 5% of the cost |
| Custom dashboard builder for non-technical users | Drag-and-drop KPI builder for department heads | Frappe already has this natively (Dashboard DocType) — rebuilding it wastes time | Use Frappe's native Dashboard + Report Builder — show users how to customize existing dashboards |
| Export to custom-branded PDF | Registrar wants university-letterhead PDF reports | Complex: requires PDF templating, wkhtmltopdf config, image embedding — weeks of work | Use Frappe's built-in Print Format + existing export-to-PDF — good enough for operational use |
| Email scheduled report delivery to external addresses | Monthly reports emailed to management | Frappe's Scheduled Report DocType (already in university_analytics) does exactly this natively | Configure Scheduled Report DocType recipients — no new code needed |
| Mobile-optimized dashboard | "Mobile-first analytics" | Frappe Desk is not mobile-optimized; dashboards in Frappe Desk are desktop tools | The Vue student portal already handles mobile — admin analytics are desktop-appropriate |
| Separate BI tool integration (Metabase, Superset) | Enterprise BI tools have better charts | Introduces a separate service, auth sync, another database connection — scope explosion | Frappe's built-in charts (frappe.Chart) cover bar, line, pie, donut — sufficient for all identified KPIs |

---

## Feature Dependencies

```
[Frappe Number Card (KPI card)] ──requires──> [Report or direct DocType query]
    └── Every KPI card depends on underlying data being clean/seeded

[Cross-module Executive Dashboard]
    └──requires──> [Individual module dashboards complete]
                       └──requires──> [Module-level Number Cards defined]

[At-Risk Student Composite KPI]
    ──requires──> [Attendance data]
    ──requires──> [CGPA data (Academics)]
    ──requires──> [Fee outstanding data (Finance)]
    ──requires──> [Grievance data]

[NAAC/NIRF Readiness Gauge]
    ──requires──> [OBE attainment data (Module 15)]
    ──requires──> [Research output data (Module 14)]
    ──requires──> [Placement rate data (Module 12)]
    ──requires──> [Faculty-student ratio (Modules 2 + 8)]

[Faculty Feedback Average]
    ──requires──> [Feedback Form responses submitted]
    ──requires──> [Feedback Form linked to faculty/course]

[Placement Rate %]
    ──requires──> [Eligible graduate list (Student status = Alumni/Graduated)]
    ──requires──> [Placement Application status = Selected]

[CO/PO Attainment Charts]
    ──requires──> [Assessment Results for the semester]
    ──requires──> [CO-PO Mapping defined per course]

[LMS vs Classroom Correlation] ──conflicts──> [MVP scope]
    ─ Requires significant data science work; defer to post-MVP
```

### Dependency Notes

- **Number Cards require underlying data:** All KPI cards depend on demo data being populated. The PROJECT.md confirms demo data exists — so cards will show real values, not zeros.
- **Cross-module dashboard requires individual modules first:** Build per-module dashboards in phases, then assemble the executive dashboard. Attempting the executive view first creates a dependency hell.
- **OBE attainment requires CO-PO mapping first:** If CO-PO mappings were not created in demo data, attainment KPIs will be empty. Verify during implementation.
- **Placement rate % requires graduated cohort:** Students must be in a "graduated" or "alumni" status for the denominator to be meaningful. The Student Status Log DocType tracks this.
- **Feedback scores require feedback forms to be completed:** Check whether demo data includes Feedback Responses, not just Feedback Forms.

---

## MVP Definition

This milestone adds dashboards to an existing, functionally complete ERP. MVP = every module has at minimum a workspace with KPI cards and one summary chart. The product is already built — the gaps are visibility, not functionality.

### Launch With (v1 — All 21 Modules, Minimum Coverage)

Each module gets:
- [ ] 3–5 Number Cards (KPI cards) representing the most-watched metrics — *achieves "every module has actionable dashboards"*
- [ ] 1 summary chart (bar or line) embedded in the workspace — *achieves "KPI cards, trend charts, comparisons"*
- [ ] 1 filterable data table linking to an existing or new Script Report — *achieves "filterable data tables with export"*

Specific required MVP items per module:

- [ ] **Core (Module 1):** Active student count + faculty count + current academic year cards
- [ ] **Academics (Module 2):** Attendance rate + at-risk students + program enrollment chart
- [ ] **Admissions (Module 3):** Total applicants + conversion rate + applicant funnel chart
- [ ] **Student Info (Module 4):** Active/inactive breakdown + category distribution
- [ ] **Examinations (Module 5):** Pass rate + hall tickets issued + grade distribution chart
- [ ] **Finance (Module 6):** Collection this month + outstanding dues + collection trend chart
- [ ] **Payments (Module 7):** Online payments today + gateway success rate + daily collection chart
- [ ] **Faculty Management (Module 8):** Faculty count + faculty-student ratio + workload table
- [ ] **Hostel (Module 9):** Occupancy rate + pending maintenance + building occupancy chart
- [ ] **Transport (Module 10):** Vehicle count + students on transport + route load chart
- [ ] **Library (Module 11):** Books issued + overdue count + daily circulation chart
- [ ] **Placement (Module 12):** Students placed + placement rate + company-wise chart
- [ ] **LMS (Module 13):** Active courses + completion rate + course enrollment chart
- [ ] **Research (Module 14):** Active projects + publications + grant funding total
- [ ] **OBE (Module 15):** CO attainment % + PO attainment % + NAAC progress chart
- [ ] **Integrations (Module 16):** SMS sent + delivery rate + channel comparison chart
- [ ] **Portals (Module 17):** Alumni count + donations this year + event list
- [ ] **Inventory (Module 18):** Low stock count + pending POs + equipment utilization
- [ ] **Grievance (Module 19):** Open grievances + avg resolution time + type breakdown chart
- [ ] **Analytics (Module 20):** Scheduled report status + KPI alerts triggered
- [ ] **Feedback (Module 21):** Average score + response count + faculty ranking table

### Add After Validation (v1.x)

- [ ] **Cross-module Executive Dashboard** — one workspace with top 3 KPIs from each module; add after all module dashboards work
- [ ] **At-risk student composite KPI** — add after attendance + finance + academic dashboards are proven accurate
- [ ] **NAAC/NIRF readiness gauge** — add after OBE + Research + Placement dashboards validate their data
- [ ] **Centralized analytics workspace** — a single "University Analytics" workspace linking to all module dashboards

### Future Consideration (v2+)

- [ ] **Student-facing analytics in Vue SPA** — explicitly out of scope per PROJECT.md; next milestone candidate
- [ ] **Predictive analytics / cohort retention** — requires full historical dataset and data science work
- [ ] **LMS vs classroom attendance correlation** — interesting but requires complex join; defer
- [ ] **Communication effectiveness correlation** — multi-table statistical analysis; defer

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Per-module Number Cards (KPI cards) — all 21 modules | HIGH | LOW | P1 |
| Per-module summary chart embedded in workspace | HIGH | LOW | P1 |
| Finance: collection + outstanding KPIs | HIGH | LOW | P1 |
| Academics: attendance rate + at-risk students | HIGH | LOW | P1 |
| Placement: placed count + placement rate | HIGH | LOW | P1 |
| Examinations: pass rate + grade distribution | HIGH | LOW | P1 |
| Admissions: applicant funnel chart | HIGH | MEDIUM | P1 |
| Cross-module Executive Dashboard | HIGH | MEDIUM | P2 |
| At-risk student composite KPI | HIGH | HIGH | P2 |
| NAAC/NIRF readiness gauge | HIGH | HIGH | P2 |
| OBE: CO/PO attainment charts | MEDIUM | HIGH | P2 |
| Faculty workload equity heatmap | MEDIUM | MEDIUM | P2 |
| Fee collection forecasting (trend projection) | MEDIUM | MEDIUM | P3 |
| Research grant pipeline chart | MEDIUM | LOW | P3 |
| LMS vs classroom correlation | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (deliver in first implementation phases)
- P2: Should have, add when P1 is complete
- P3: Nice to have, future consideration or v2+

---

## KPI Quick Reference (Flat List)

This is a flat list of all table-stakes KPIs for implementation reference.

### Count KPIs (simple COUNT queries)
- Total active students
- Total faculty count
- Total applicants this cycle
- Hall tickets generated
- Exams scheduled this month
- Revaluation requests pending
- Books currently issued
- Overdue books count
- Active library members
- Open grievances
- Active research projects
- Publications this year
- Active LMS courses
- Pending maintenance requests (hostel + inventory)
- Low stock items
- SMS sent today
- WhatsApp messages sent this month
- Open placement drives
- Pending leave applications

### Amount KPIs (SUM queries with currency formatting)
- Total fee collection this month
- Total outstanding dues
- Online payments today (amount)
- Total grant funding secured
- Transport fee collection
- Library fines collected this month
- Alumni donations this year
- Stock value on hand
- Pending purchase order value

### Rate / Ratio KPIs (derived calculations)
- Collection rate % (collected / billed)
- Attendance rate % (present / scheduled)
- Pass rate % (passed / appeared)
- Placement rate % (placed / eligible)
- Occupancy rate % (allocated rooms / total rooms)
- Gateway success rate % (successful / total transactions)
- SMS delivery rate % (delivered / sent)
- Course completion rate % (completed / enrolled)
- CO attainment % (average across courses)
- PO attainment % (average across programs)
- Faculty-to-student ratio
- Survey response rate %
- SLA compliance rate %
- Seat fill rate % (enrolled / sanctioned seats per program)

### Time-Series Charts (trend lines, bar by period)
- Monthly fee collection trend (12 months)
- Attendance trend by month
- Applications received by week (admissions season)
- Daily payment gateway transactions
- Books issued per day (library)
- Grievances opened/closed per month
- Placement drives per year
- Publications per year (research)
- Communication sends by day (SMS/WhatsApp)

### Distribution Charts (bar/pie breakdown)
- Program-wise enrollment
- Department-wise faculty count
- Grade distribution (A/B/C/D/F)
- Category-wise applicants (SC/ST/OBC/General)
- Building-wise hostel occupancy
- Route-wise transport students
- Fee category breakdown (tuition/hostel/transport)
- Grievance type breakdown
- Subject-wise library collection
- Gateway-wise payment breakdown (Razorpay / PayU)
- Company-wise placements

---

## Sources

- Direct DocType inventory: `/workspace/development/frappe-bench/apps/university_erp/university_erp/` (all 21 module directories)
- Existing report inventory: per-module `/report/` directories — 40+ existing reports already built
- Scheduled task definitions: `hooks.py` scheduler_events — confirms which metrics are computed automatically
- Project scope: `.planning/PROJECT.md` — constraints and out-of-scope items
- Architecture: `.planning/codebase/ARCHITECTURE.md` — module boundaries and data flow patterns
- Existing analytics: `university_analytics/report/student_performance_analysis.py` — demonstrates pattern for KPI computation

---

*Feature research for: University ERP Dashboards & Analytics Milestone*
*Researched: 2026-03-17*
*Confidence: HIGH — grounded in codebase DocType analysis, not generic ERP speculation*

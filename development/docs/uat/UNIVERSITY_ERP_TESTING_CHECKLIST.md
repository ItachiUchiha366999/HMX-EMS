# University ERP — Production Manual Testing Checklist

**Site:** `ems.hanumatrix.com`
**App version:** `university_erp 0.0.1` (branch `main`)
**Companion apps:** `frappe 15.94.0`, `erpnext 15.93.1`, `hrms 15.54.2`, `education 15.0.0`
**Generated from:** production container `ems-backend` on 2026-04-29
**Purpose:** Track manual testing of every DocType and Report exposed via workspaces on the **production** site.

> **This file replaces the earlier local-only checklist.** It reflects what's actually deployed on `ems.hanumatrix.com` — most importantly, the lean **University Finance** module (no ERPNext fork). For the architectural diff and known bugs from static analysis, see [PRODUCTION_ANALYSIS.md](PRODUCTION_ANALYSIS.md).

## How to use this file
- For each item, set the **Status** to `PASS`, `FAIL`, or `NEEDS-CHANGE` after testing on `ems.hanumatrix.com`.
- Use the **Notes / Issues** column to describe bugs, missing fields, UX issues, or required changes.
- Items grouped under each workspace match what the user sees in the Frappe desk sidebar **on production**.
- An **(Orphan)** section per module lists DocTypes/Reports that exist in code but are not linked from any workspace card.

## Known issues already flagged (verify during testing)
- ✅ ~~🔴 **BUG-1:** Finance workspace shortcut **`Fee Payment`** links to a non-existent DocType.~~ **RESOLVED 2026-04-30** — Finance workspace JSON updated, broken shortcut removed.
- ✅ ~~🟠 **BUG-2:** Two `Fee Refund` DocTypes — one in `university_finance`, one in `university_payments`. Schema collision.~~ **RESOLVED 2026-04-30** — orphan `university_finance/doctype/fee_refund/` directory removed from prod. Live DocType remains in `university_payments` module.
- ✅ ~~🟠 **BUG-3:** Finance workspace label `Accounts Settings` resolves to `University Accounts Settings` — confusing.~~ **RESOLVED 2026-04-30** — both labels listed separately and clearly.
- ✅ ~~🟡 **ISSUE-4:** `SMS Gateway` card on Integrations workspace has no links.~~ **RESOLVED 2026-04-30** — added 4 links to SMS Gateway card: `University SMS Settings`, `SMS Template`, `SMS Log`, `SMS Queue`.
- ✅ ~~🟡 **ISSUE-5:** OBE workspace puts `Assessment Rubric` (a DocType) inside the Reports card.~~ **RESOLVED 2026-04-30** — moved `Assessment Rubric` link from end-of-Reports to under `Outcome Definitions` card (after Course Outcome).
- 🟡 **ISSUE-6:** `university_portals` DocTypes have no workspace.

---

## UAT findings (2026-04-30, Ruchik manual test pass on `ems.hanumatrix.com`)

These are aggregated findings from the manual UAT round. Each is also annotated against the specific DocType/Report row below.

### UAT-1 — Missing `Student` link field on data-bearing DocTypes 🔴
Many transactional DocTypes that obviously belong to a student have **no `Student` Link field**, so records can't be filtered or rolled up per student. Affected:
- **Finance:** Fee Refund, Bulk Fee Generator, Student Scholarship, Payment Order
- **Academics:** Course Registration, Student Status Log
- **Portals:** Alumni
- **Examinations:** Hall Ticket, Answer Sheet, Student Transcript, (Practical/Internal) Evaluation Results
- **Placement:** Student Resume, Placement Application
- **LMS:** LMS Content Progress, Assignment Submission, LMS Discussion
- **Reports:** Course Progress Report, Quiz Analytics

**Action:** add a `Student` Link field (`options: Student`, in_standard_filter, mandatory where appropriate). Update list views and standard reports to filter by it.

### UAT-2 — Fee Refund does not fetch the original Fee 🔴 ✅ RESOLVED 2026-04-30
~~The Fee Refund DocType has no working link to the originating Fees / Sales Invoice / Fee Schedule.~~

**Investigation (2026-04-30):** Inspection of the live JSON showed the Fee Refund DocType already had:
- `fees` Link field labeled "Original Fee" (Link to Fees)
- `fetch_from` wired for `program` (← `fees.program`), `original_amount` (← `fees.grand_total`), `paid_amount` (← `fees.paid_amount`)
- `student.student_name` fetch_from for `student_name`

So the schema/wiring was already in place. The UAT symptom — "doesn't pull original fee" — was caused by:
1. No Student records existed at UAT time (post-wipe)
2. The Fees dropdown showed all Fees, not filtered by selected Student → confusing UX

**Fix applied:**
- Added `fee_refund.js` client script that filters the Fees dropdown to only show fees of the currently-selected Student (and clears stale Fee selection if Student changes).
- Auto-computes `net_refund = refund_amount - deduction_amount` on the form.
- Removed orphan `university_finance/doctype/fee_refund/` directory from production (BUG-2).

### UAT-3 — Naming series not set / wrong on key DocTypes 🟠
Course Registration and several Examination DocTypes (Hall Ticket, Answer Sheet, Internal Assessment, Practical Examination, Student Transcript, Online Examination, Generated Question Paper) need an explicit naming_series with a clear prefix (e.g. `CR-.YYYY.-`, `HT-.YYYY.-`, `AS-.YYYY.-`).
**Action:** add `naming_series` field with sensible default + autoname rule; backfill series counters.

### UAT-4 — Elective Course Group field clarity 🟡
Unclear what `group_name` and `elective_type` represent on Elective Course Group. Need labels + `description`/help text + permitted values. Confirm whether `elective_type` should be a Link to a master (e.g. Open / Department / Specialization) or a Select with fixed options.
**Action:** clarify intent with product owner, then update labels + add help text. Consider converting to Select if values are bounded.

### UAT-5 — Merge Question Bank into Generated Papers + Online Examinations 🟠 ✅ WON'T FIX
~~Question Bank DocType is redundant. Items should live directly inside Generated Question Paper / Online Examination.~~

**Decision (2026-04-30): KEEP Question Bank as-is.** Rationale:
- Question Bank is a reusable question pool, not a transactional record. Authors questions once, reused across papers/exams/courses/years.
- Drives Question Paper Template auto-pick by Bloom level / CO / PO / unit distribution.
- Provides cross-paper analytics: `times_used`, `average_score_percentage` per question.
- Question Bank Analysis report would lose its data source.
- Standard LMS / exam-system architecture (Moodle, Canvas, ERPNext Education) all keep a separate question bank.

The UAT tester likely interpreted "we have a separate Question Bank screen plus a Generated Paper screen" as redundancy. The right UX improvement is to make question authoring smoother (e.g., add a "+ Add Question" inline button on Generated Paper that opens a Question Bank quick-create dialog), but the schema separation should stay.

### UAT-6 — Grievance Committee form is incomplete 🟠
"New Grievance Committee" form lacks required fields/links. Cannot complete creation.
**Action:** audit DocType JSON. Likely missing: members child table linking to User/Employee, scope (Department/Program), escalation_to, contact_email, active flag.

### UAT-7 — Multiple reports have no usable filters/links/data 🔴
Reports flagged: SLA Compliance, Faculty Feedback Report, Feedback Analysis, SMS Delivery Report, **all** University Transport reports, **all** University Library reports, **all** University Placement reports, **all** University LMS reports.

Common defects:
- No default filters wired (no Date Range / Academic Year / Department / Program filter)
- Cross-DocType joins missing — report can't reach the related Student / Employee / Course / Program
- Output columns don't have meaningful labels or aggregations
- No data even when underlying records exist

**Action:** for each report, redesign filter set + column list + JOIN strategy. Add a "filters required" mandatory pattern where appropriate.

### UAT-8 — Communication Analytics report is broken 🔴
Workspace links to `Communication Analytics` but the report opens "Not Found" or empty page. The implementation file may not exist, or the report DocType row references a path/method that's missing.
**Action:** verify `apps/university_erp/university_erp/university_analytics/report/communication_analytics/communication_analytics.{json,py}` exists and is registered. Either implement, or remove the workspace link.

### UAT-9 — Placement DocType missing 🔴 ✅ RESOLVED 2026-04-30
~~University Placement reports need a "Placement" / "Placement Outcome" DocType — currently absent.~~

**Investigation (2026-04-30):** `Placement Application` already has every field a Placement Outcome would need: `student`, `company` (Link to Placement Company), `job_opening` (Link to Placement Job Opening), `offered_ctc`, `offer_letter`, `placement_date`, `joining_date`, plus a `status` Select with `Placed` / `Selected` values. The 4 placement reports correctly filter `WHERE status IN ('Placed','Selected')`. No new DocType is needed — the schema is fine.

**Real bugs that made the reports look broken:**
- 3 of 4 reports had a SQL join bug: `LEFT JOIN tabPlacement Application pa ON pa.placement_drive = pd.name` — but `placement_drive` is NOT a field on Placement Application. The correct link chain is via `job_opening`. Reports silently returned 0 rows.
- 4 of 4 reports had hardcoded fiscal-year defaults (`"2025-2026"`, `"2026-03-01"`).

**Fix applied:**
- Replaced bad `pa.placement_drive` joins with correct `pa.company = pc.name` (company_wise) or `pd.job_opening = pa.job_opening` (program_wise, placement_trend).
- Replaced hardcoded date defaults with `frappe.defaults.get_user_default("academic_year")` and dynamic relative dates.
- Added missing filters (Industry Type, Program, Group By).

### UAT-10 — Research module currently only tracks faculty 🟠
Research Project / Research Publication / Research Grant only link to faculty. Need to also support student-led research (UG/PG projects, student first-author publications, student grants).
**Action:** on Research Project/Publication/Grant — add a "Researcher Type" Select (`Faculty` / `Student` / `Mixed`), make either `faculty` OR `student` required (not both mandatory), and add a Researchers child table that supports both.

---

## Workspace: University Home
**Module:** University ERP &nbsp;•&nbsp; Path: `university_erp/workspace/university_home`

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Student | Student Management |  |  |
| 2 | Student Applicant | Student Management |  |  |
| 3 | Program | Academics |  |  |
| 4 | Course | Academics |  |  |
| 5 | Assessment Result | Examinations |  |  |
| 6 | Fees | Finance |  |  |
| 7 | University Department | Masters |  |  |
| 8 | Academic Year | Masters |  |  |
| 9 | University Settings | Settings |  |  |

### Reports
_None linked in this workspace._

---

## Workspace: University Academics
**Module:** University Academics

### DocTypes
| # | DocType | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Course Registration | Academics | FIXED | **UAT-1**: Student Link existed, was not in standard filter. **UAT-3**: `autoname` was `hash`. | ✅ `student` field now `in_standard_filter`. ✅ `autoname` changed from `hash` to `format:CR-{YYYY}-{#####}`. |
| 2 | Elective Course Group | Academics | FIXED | **UAT-4**: clarify `group_name` + `elective_type` (intent, allowed values, link target). | ✅ Added `description` to both `group_name` and `elective_type`. ✅ Expanded `elective_type` options from 4 (DSE/GE/SEC/AEC) to 7 with full NEP-2020 names: DSE, GE, SEC, AEC, VAC, OE, MOOC. ✅ Added `in_standard_filter` to `elective_type`. |
| 3 | Timetable Slot | Academics |  |  |  |
| 4 | Admission Cycle | Admissions |  |  |  |
| 5 | Admission Criteria | Admissions |  |  |  |
| 6 | Merit List | Admissions |  |  |  |
| 7 | Seat Matrix | Admissions |  |  |  |
| 8 | Student Status Log | Student Info | FIXED | **UAT-1**: Student Link existed but not in standard filter. **UAT-3** (extra): `autoname` was `hash`. | ✅ `student` field now `in_standard_filter`. ✅ `autoname` changed from `hash` to `format:SSL-{YYYY}-{#####}`. |
| 9 | University Alumni | Student Info | FIXED | **UAT-1**: Student Link existed but not in standard filter. | ✅ `student` field now `in_standard_filter`. (Naming kept as `hash` — not flagged in UAT.) |
| 10 | University Announcement | Student Info |  |  |  |

### Reports
_None linked in this workspace._

### Orphan child DocTypes (in code, not on workspace)
- `Course Prerequisite`, `Course Registration Item`, `Elective Course Group Item`, `Teaching Assignment` (academics module — duplicate name with faculty_management one), `Admission Cycle Program`, `Merit List Applicant`

---

## Workspace: Faculty Management
**Module:** Faculty Management

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Employee | HR Management |  | _ERPNext core_ |
| 2 | Faculty Profile | HR Management |  |  |
| 3 | Teaching Assignment | HR Management |  |  |
| 4 | Leave Application | HR Management |  | _ERPNext / HRMS core_ |
| 5 | Workload Distributor | HR Management |  |  |
| 6 | Student Feedback | Performance & Feedback |  |  |
| 7 | Temporary Teaching Assignment | Reports (misplaced) |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Faculty Directory | Reports |  |  |
| 2 | Faculty Workload Summary | Reports |  |  |
| 3 | Department HR Summary | Reports |  |  |
| 4 | Leave Utilization Report | Reports |  |  |

### Orphan DocTypes
- `Employee Qualification`, `Faculty Award`, `Faculty Publication`, `Faculty Research Project`, `Leave Affected Course` (child), `Teaching Assignment Schedule` (child)

---

## Workspace: University Examinations
**Module:** University Examinations

### DocTypes
| # | DocType | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Exam Schedule | Exam Scheduling | FIXED | **UAT-3**: `autoname` was `hash`. | ✅ `autoname` → `format:ES-{YYYY}-{#####}`. |
| 2 | Hall Ticket | Exam Scheduling | FIXED | **UAT-1**: Student Link existed but not in standard filter. **UAT-3**: naming was already `format:HT-{YYYY}-{#####}`. | ✅ `student` field now `in_standard_filter`. (Naming was already correct.) |
| 3 | External Examiner | Exam Scheduling |  |  |  |
| 4 | Question Bank | Question Bank | WON'T FIX | **UAT-5**: tester proposed REMOVE. **Decision (2026-04-30): KEEP** — Question Bank is a reusable question pool that drives Question Paper Template auto-pick (Bloom/CO/PO distribution rules), `times_used` and `average_score_percentage` analytics, and the Question Bank Analysis report. Inline-only authoring would duplicate questions per paper, break CO/PO outcome traceability, and remove cross-paper analytics. Standard LMS / question-paper architecture preserves a separate bank. | ✅ Kept by design. UAT-5 marked Won't Fix with rationale. |
| 5 | Question Tag | Question Bank | WON'T FIX | **UAT-5**: keep with Question Bank decision above. | ✅ Kept. |
| 6 | Question Paper Template | Question Bank | WON'T FIX | **UAT-5**: keep — Template orchestrates which questions get pulled from the Bank by section / Bloom / CO / unit distribution rules. Cannot work without a Bank. | ✅ Kept. |
| 7 | Generated Question Paper | Question Bank |  | **UAT-3**: naming already `format:QP-.YYYY.-.#####`. **UAT-5**: still references Question Bank — kept by design. | (No change needed; naming already correct.) |
| 8 | Online Examination | Online Examinations |  | **UAT-3**: naming already `format:OE-.YYYY.-.#####`. **UAT-5**: still consumes Generated Question Paper — kept by design. | (No change needed; naming already correct.) |
| 9 | Student Exam Attempt | Online Examinations |  | Student Link already in standard filter. |  |
| 10 | Answer Sheet | Online Examinations |  | Student Link already in standard filter. Naming already `AS-.YYYY.-.#####`. | (No change needed.) |
| 11 | Internal Assessment | Internal Assessment |  | Internal Assessment is a class/cohort exam; per-student scores live in child `Internal Assessment Score`. **UAT-1 not applicable** — architecturally correct. Naming already `IA-.YYYY.-.#####`. | (No change needed — architecture is correct.) |
| 12 | Practical Examination | Internal Assessment |  | Same as Internal Assessment; per-student scores in child `Practical Exam Student Score`. Naming already `PRAC-.YYYY.-.#####`. | (No change needed — architecture is correct.) |
| 13 | Student Transcript | Results & Transcripts | FIXED | **UAT-1**: Student Link existed but not in standard filter. **UAT-3**: naming was already `format:TR-{YYYY}-{#####}`. | ✅ `student` field now `in_standard_filter`. (Naming was already correct.) |
| 14 | Revaluation Request | Results & Transcripts |  | Student Link already in standard filter. Naming already `RR-.YYYY.-.#####`. | (No change needed.) |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Examination Result Analysis | Reports |  |  |  |
| 2 | Internal Assessment Summary | Reports |  |  |  |
| 3 | Question Bank Analysis | Reports |  | **UAT-5**: kept — depends on Question Bank which is being preserved by design. | ✅ Kept. |

### Orphan DocTypes (mostly child tables)
Answer Sheet Score, Answer Sheet Tracking Log, Exam Invigilator, Hall Ticket Exam, Internal Assessment Score, Online Exam Student, Practical Evaluation Criteria, Practical Exam Examiner, Practical Exam Slot, Practical Exam Student Score, Question Option, Question Paper Content Section, Question Paper Question Item, Question Paper Section, Question Tag Link, Student Answer, Transcript Semester Result.

---

## Workspace: University Finance ⚠️ (different from local)
**Module:** University Finance

> **Production architecture (revised 2026-04-30):** University Finance workspace now mirrors the local rich layout — references DocTypes from `erpnext` app (Sales Invoice, Payment Entry, Journal Entry, Bank Account, GL Entry, etc.) AND from `university_erp` (Fee Category, Fee Refund, Bulk Fee Generator, Scholarship). No code/schema changes — only the workspace JSON references existing ERPNext app DocTypes for one-stop UX.

### Workspace shortcuts (top of page)
| # | Shortcut | Resolves to | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Fee Invoice | Sales Invoice | FIXED | Was `Fee Category` only. | ✅ Now `Fee Invoice` → `Sales Invoice` (ERPNext app). |
| 2 | Payment Entry | Payment Entry | FIXED | Was broken `Fee Payment` shortcut → 404 page. | ✅ 🔴 **BUG-1 RESOLVED**. Replaced with `Payment Entry` (ERPNext app). |
| 3 | Journal Entry | Journal Entry | FIXED | Was `Fee Refund`. | ✅ Now `Journal Entry` (ERPNext app). |
| 4 | Fees | Fees | FIXED | Was `Razorpay Settings`. | ✅ Now `Fees` (Education app — direct fee entry). |

### DocTypes (workspace cards)
| # | Card | DocType | link_to | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|---|
| 1 | Fee Management | Fee Invoice | Sales Invoice |  | _added 2026-04-30_ | ✅ |
| 2 | Fee Management | Fee Order | Sales Order |  | _added_ | ✅ |
| 3 | Fee Management | Fees | Fees |  | _added (Education app)_ | ✅ |
| 4 | Fee Management | Fee Structure | Fee Structure |  | _added (Education app)_ | ✅ |
| 5 | Fee Management | Fee Schedule | Fee Schedule |  | _added (Education app)_ | ✅ |
| 6 | Fee Management | Fee Category | Fee Category |  |  |  |
| 7 | Fee Management | Fee Refund | Fee Refund | FIXED | 🟠 **BUG-2** (duplicate dirs across finance + payments). **UAT-2**: no link to original Fee. | ✅ 🟠 **BUG-2 RESOLVED** — orphan `university_finance/doctype/fee_refund/` directory removed from prod (live DocType is in `university_payments`). ✅ **UAT-2 verified** — `fees` Link field labeled "Original Fee" already exists with `fetch_from` for `program`, `original_amount`, `paid_amount`. Added `fee_refund.js` client script: filters Fees dropdown to selected Student's fees only, auto-computes `net_refund = refund_amount - deduction_amount`. |
| 8 | Fee Management | Bulk Fee Generator | Bulk Fee Generator | WON'T FIX | **UAT-1**: tester wanted parent-level Student link. **Architecturally incorrect** — Bulk Fee Generator is a one-to-many bulk operation: filters Program × Academic Year × Batch → generates fees for the resulting student set. Adding a single Student field at parent would defeat the bulk-generation purpose. The child `Bulk Fee Generator Student` already links to Student per row. | ✅ Kept by design. UAT-1 marked Won't Fix with rationale. |
| 9 | Procurement | Procurement Invoice | Purchase Invoice |  | _added (ERPNext app)_ | ✅ |
| 10 | Procurement | Purchase Requisition | Purchase Order |  | _added (ERPNext app)_ | ✅ |
| 11 | Payments | Payment Entry | Payment Entry |  | _added (ERPNext app)_ | ✅ |
| 12 | Payments | Payment Request | Payment Request |  | _added (ERPNext app)_ | ✅ |
| 13 | Payments | Payment Order | Payment Order | FIXED | **UAT-1**: Student Link existed and was in_standard_filter, but had `in_list_view: 0` so the column didn't show. | ✅ `student` field now `in_list_view: 1`. |
| 14 | Payments | Razorpay Settings | Razorpay Settings |  |  |  |
| 15 | Payments | PayU Settings | PayU Settings |  |  |  |
| 16 | Banking | Bank Account | Bank Account |  | _added_ | ✅ |
| 17 | Banking | Bank Reconciliation Tool | Bank Reconciliation Tool |  | _added_ | ✅ |
| 18 | Banking | Bank Clearance | Bank Clearance |  | _added_ | ✅ |
| 19 | Banking | Bank Guarantee | Bank Guarantee |  | _added_ | ✅ |
| 20 | Banking | Bank Transaction | Bank Transaction |  |  |  |
| 21 | General Ledger | Account | Account |  | _added (ERPNext app)_ | ✅ |
| 22 | General Ledger | GL Entry | GL Entry |  | _added (ERPNext app)_ | ✅ |
| 23 | General Ledger | Journal Entry | Journal Entry |  | _added (ERPNext app)_ | ✅ |
| 24 | General Ledger | Cost Center | Cost Center |  | _added (ERPNext app)_ | ✅ |
| 25 | General Ledger | Fiscal Year | Fiscal Year |  | _added (ERPNext app)_ | ✅ |
| 26 | Settings | Accounts Settings | Accounts Settings |  |  | ✅ 🟠 **BUG-3 RESOLVED** — link now points to ERPNext's real `Accounts Settings`. The old prod link mislabeled `University Accounts Settings` as `Accounts Settings`. |
| 27 | Settings | University Accounts Settings | University Accounts Settings |  | _added separately, clearly labeled_ | ✅ |
| 28 | Settings | Finance Book | Finance Book |  | _added_ | ✅ |
| 29 | Settings | Tax Category | Tax Category |  | _added_ | ✅ |
| 30 | Settings | Budget | Budget |  | _added_ | ✅ |
| 31 | Scholarships | Scholarship Type | Scholarship Type |  |  |  |
| 32 | Scholarships | Student Scholarship | Student Scholarship | FIXED | **UAT-1**: Student Link existed; needs `in_standard_filter`. | ✅ `student` field now `in_standard_filter`. |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | General Ledger | Reports |  | _added (ERPNext)_ | ✅ |
| 2 | Trial Balance | Reports |  | _added (ERPNext)_ | ✅ |
| 3 | Balance Sheet | Reports |  | _added (ERPNext)_ | ✅ |
| 4 | Profit and Loss | Reports |  | _added (Profit and Loss Statement)_ | ✅ |
| 5 | Fee Receivable | Reports |  | _added (Accounts Receivable)_ | ✅ |
| 6 | Vendor Payable | Reports |  | _added (Accounts Payable)_ | ✅ |
| 7 | Student Ledger Summary | Reports |  | _added (Customer Ledger Summary)_ | ✅ |
| 8 | Vendor Ledger Summary | Reports |  | _added (Supplier Ledger Summary)_ | ✅ |
| 9 | Cash Flow | Reports |  | _added (ERPNext)_ | ✅ |
| 10 | Budget Variance Report | Reports |  | _added (ERPNext)_ | ✅ |
| 11 | Fee Collection Summary | Reports |  |  |  |
| 12 | Fee Defaulters | Reports |  |  |  |
| 13 | Daily Collection Report | Reports |  |  |  |
| 14 | Gateway Reconciliation Report | Reports |  |  |  |
| 15 | Refund Report | Reports |  |  |  |

### Workspace fix summary (2026-04-30)
- 🔴 **BUG-1 RESOLVED** — Removed broken `Fee Payment` shortcut + card link (DocType doesn't exist anywhere in the install). The 404 from `frappe.desk.reportview.get_count` that was breaking workspace render is gone.
- 🟠 **BUG-3 RESOLVED** — `Accounts Settings` label now points to ERPNext's actual `Accounts Settings`; `University Accounts Settings` is listed separately with clear label.
- ✅ Workspace now renders **8 cards × 32 DocTypes + 15 Reports** instead of 4 broken shortcuts. Pushed local rich workspace JSON to prod.
- 🟠 **BUG-2 NOT RESOLVED** — duplicate Fee Refund DocType (one in `university_finance`, one in `university_payments`) is still there. Will be tackled in Section: University Finance.

### Available DocTypes in `university_finance` module on prod (unchanged)
`bulk_fee_generator`, `bulk_fee_generator_student` (child), `fee_category`, `fee_refund`, `fee_refund_deduction` (child), `scholarship_type`, `student_scholarship`. **Total: 7 DocTypes (5 main + 2 child).** Workspace now references these PLUS ERPNext app DocTypes for full Finance UX.

---

## Workspace: University Hostel
**Module:** University Hostel

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Hostel Building | Master Data |  |  |
| 2 | Hostel Room | Master Data |  |  |
| 3 | Hostel Mess | Master Data |  |  |
| 4 | Hostel Allocation | Transactions |  |  |
| 5 | Hostel Attendance | Transactions |  |  |
| 6 | Hostel Bulk Attendance | Transactions |  |  |
| 7 | Hostel Visitor | Transactions |  |  |
| 8 | Hostel Maintenance Request | Transactions |  |  |
| 9 | Mess Menu | Transactions |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Hostel Occupancy | Reports |  |  |
| 2 | Room Availability | Reports |  |  |
| 3 | Hostel Attendance Report | Reports |  |  |
| 4 | Maintenance Summary | Reports |  |  |
| 5 | Visitor Log | Reports |  |  |

### Orphan child DocTypes
Hostel Attendance Record, Hostel Room Occupant, Mess Menu Item.

---

## Workspace: University Transport
**Module:** University Transport

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Transport Route | Master Data |  |  |
| 2 | Transport Vehicle | Master Data |  |  |
| 3 | Transport Allocation | Transactions |  |  |
| 4 | Transport Trip Log | Transactions |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Route Wise Students | Reports | FIXED | **UAT-7**: filters had no defaults; only 2 filters (route, academic_year). | ✅ Filters expanded to 4 (Academic Year w/ user-default, Route, Program, Vehicle). Python `get_data` accepts `program` and `vehicle` filters. Joins to `tabTransport Route` already in place. Chart (route counts) + summary cards (Total Students / Routes / Monthly Revenue) already present. |
| 2 | Vehicle Utilization | Reports | FIXED | **UAT-7**: had defaults on dates already, but missing route filter. | ✅ Filters expanded to 5 (From/To Date now `reqd: 1`, Vehicle Type, Status, Route). Python `get_data` accepts `route`. Existing chart (top 10 utilization %) + summary (Total / Active / Avg Utilization / Total Students) preserved. |
| 3 | Transport Fee Collection | Reports | FIXED | **UAT-7**: filters had no defaults; only 2 filters. | ✅ Filters expanded to 4 (Academic Year w/ user-default, Route, Program, "Outstanding Only" checkbox). Python `get_data` accepts `program`; "Outstanding Only" filters out fully-collected routes. Existing stacked bar chart (Collected vs Outstanding) + summary cards (Total Billed / Collected / Outstanding / Collection Rate) preserved. |

### Orphan child DocTypes
Transport Route Stop.

---

## Workspace: University Library
**Module:** University Library

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Library Category | Master Data |  |  |
| 2 | Library Subject | Master Data |  |  |
| 3 | Library Article | Master Data |  |  |
| 4 | Library Member | Master Data |  |  |
| 5 | Library Transaction | Transactions |  |  |
| 6 | Book Reservation | Transactions |  |  |
| 7 | Library Fine | Transactions |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Library Circulation | Reports | FIXED | **UAT-7**: only had From/To Date filters, no joins to filter by member type or category. | ✅ Filters expanded to 5 (From/To Date `reqd: 1`, Member Type, Article Category, Transaction Type). Python `get_data` now LEFT JOINs `tabLibrary Member` + `tabLibrary Article` to honor new filters. Existing line chart (Issues vs Returns last 30 days) + summary cards (Total Issues / Returns / Renewals) preserved. |
| 2 | Overdue Books | Reports | FIXED | **UAT-7**: ZERO filters configured. | ✅ Filters added: Member Type, Category, Min Overdue Days (default 1), Max Overdue Days. Python `get_data` honors all 4 plus uses `library_fine_per_day` from University Settings. Pie chart (1-7 / 8-14 / 15-30 / 30+ days buckets) + summary cards (Overdue / Total Fines / Max Overdue Days) preserved. |
| 3 | Library Collection | Reports | FIXED | **UAT-7**: only Category filter. | ✅ Filters expanded to 3 (Category, Subject, Article Status). Python `get_data` honors all 3. Existing pie chart (titles per category) + summary cards (Total Titles / Copies / Available / Value) preserved. |
| 4 | Member Borrowing History | Reports | FIXED | **UAT-7**: only Member filter (mandatory). | ✅ Filters expanded to 4 (Member `reqd: 1`, From/To Date, Transaction Type). Python `get_data` honors all 4 with parameterised conditions. Summary cards (Total Transactions / Currently Borrowed / Total Fines) preserved. |

---

## Workspace: University Placement
**Module:** University Placement

### DocTypes
| # | DocType | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Industry Type | Master Data |  |  |  |
| 2 | Placement Company | Master Data |  |  |  |
| 3 | Student Resume | Master Data |  | **UAT-1**: Student Link already in standard filter. |  |
| 4 | Placement Job Opening | Job Management |  |  |  |
| 5 | Placement Drive | Job Management |  |  |  |
| 6 | Placement Application | Job Management |  | **UAT-1**: Student Link already in standard filter. Has all needed fields (`student`, `company`, `offered_ctc`, `placement_date`, `joining_date`, `status='Placed'`) — acts as the de-facto Placement Outcome record. |  |
| ~~7~~ | ~~**(MISSING)** Placement Outcome~~ | ~~Job Management~~ | RESOLVED | **UAT-9**: claimed Placement Outcome DocType missing. **Investigation:** Placement Application already covers the needed schema (`student` + `company` + `offered_ctc` + `placement_date` + `joining_date`, with `status='Placed'` filtering). All 4 reports query `tabPlacement Application` with `status IN ('Placed','Selected')`. No new DocType needed. | ✅ UAT-9 resolved without creating a new DocType — Placement Application is the right model. Reports now correctly query it. |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Placement Statistics | Reports | FIXED | **UAT-7**: had hardcoded `default: "2025-2026"` for academic year. **Schema bug:** none in this report's SQL. | ✅ `default` for academic_year now reads `frappe.defaults.get_user_default("academic_year")` (dynamic). Added Program filter. Python `get_data` honors program via `Student.custom_program` join. Existing chart + summary cards preserved. |
| 2 | Company Wise Placement | Reports | FIXED | **UAT-7**: hardcoded date default; `placement_drive` field added by mistake. **Schema bug:** Python joined `pa.placement_drive` (column doesn't exist on `tabPlacement Application`) → returned empty data even when records existed. | ✅ Filters: dynamic Academic Year default, Industry Type (link to Industry Type), Placement Company. **Schema bug fixed:** changed `LEFT JOIN tabPlacement Application pa ON pa.placement_drive = pd.name` → `LEFT JOIN tabPlacement Application pa ON pa.company = pc.name` (Placement Application has `company` link directly). |
| 3 | Program Wise Placement | Reports | FIXED | **UAT-7**: hardcoded date default. **Schema bug:** same `pa.placement_drive` ghost join. | ✅ Filters: dynamic Academic Year default, Program. **Schema bug fixed:** join now `LEFT JOIN tabPlacement Drive pd ON pd.job_opening = pa.job_opening` (correct link via Job Opening). |
| 4 | Placement Trend | Reports | FIXED | **UAT-7**: hardcoded date default `"2026-03-01"`. **Schema bug:** same `pa.placement_drive` ghost join. | ✅ Filters: From/To Date `reqd: 1` with dynamic defaults (last 12 months), Academic Year, Group By (Month/Quarter/Year). **Schema bug fixed:** `LEFT JOIN tabPlacement Application pa ON pa.job_opening = pd.job_opening`. |

### Orphan child DocTypes
Job Eligible Program, Placement Round, Resume Education, Resume Project, Resume Skill.

---

## Workspace: University LMS
**Module:** University LMS

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | LMS Course | Course Management |  |  |
| 2 | LMS Content | Course Management |  |  |
| 3 | LMS Content Progress | Course Management | NEEDS-CHANGE | **UAT-1**: missing `Student` Link field. |
| 4 | LMS Assignment | Assessments |  |  |
| 5 | Assignment Submission | Assessments | NEEDS-CHANGE | **UAT-1**: missing `Student` Link field. |
| 6 | LMS Quiz | Assessments |  |  |
| 7 | Quiz Attempt | Assessments |  |  |
| 8 | LMS Discussion | Collaboration | FIXED | **UAT-1**: Student Link existed but conditional on `created_by_type='Student'`; lacked `in_standard_filter`. | ✅ Added `in_standard_filter: 1` to student field so users can filter discussions by student in the list view. |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Course Progress | Reports | FIXED | **UAT-7**: `lms_course` was `reqd: 1` so report blocked first load; needed Student filter + min progress. | ✅ Removed `reqd: 1` from `lms_course`. Added Student + Min Progress % filters. Python `get_data` honors student filter and `HAVING overall_progress >= min_progress`. Existing chart + summary preserved. |
| 2 | Assignment Submission Report | Reports | FIXED | **UAT-7**: no date defaults; no Student filter. | ✅ From/To Date now default to last 3 months / today. Added Student filter. Python honors all filters via parameterised conditions. |
| 3 | Quiz Analytics | Reports | FIXED | **UAT-7**: no date defaults; no Student / Passed-Only filters. | ✅ From/To Date default to last 3 months / today. Added Student Link filter and Passed-Only checkbox filter. Python honors all. |

### Orphan child DocTypes
Assignment Rubric Item, Discussion Reply, LMS Course Module, Quiz Answer, Quiz Question, Submission File, Submission Rubric Score.

---

## Workspace: University OBE
**Module:** University OBE

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Program Educational Objective | Outcome Definitions |  |  |
| 2 | Program Outcome | Outcome Definitions |  |  |
| 3 | Course Outcome | Outcome Definitions |  |  |
| 4 | CO PO Mapping | Outcome Mapping |  |  |
| 5 | CO Attainment | Attainment Calculation |  |  |
| 6 | PO Attainment | Attainment Calculation |  |  |
| 7 | OBE Survey | OBE Surveys |  |  |
| 8 | Survey Template | OBE Surveys |  |  |
| 9 | **Assessment Rubric** | _placed under Reports card_ |  | 🟡 **ISSUE-5**: misplaced |
| 10 | Accreditation Cycle | Accreditation |  |  |
| 11 | NAAC Metric | Accreditation |  |  |
| 12 | NIRF Data | Accreditation |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | CO-PO Mapping Matrix | Reports |  |  |
| 2 | CO Attainment Report | Reports |  |  |
| 3 | PO Attainment Report | Reports |  |  |
| 4 | Program Attainment Summary | Reports |  |  |
| 5 | Survey Analysis Report | Reports |  |  |
| 6 | NAAC Criterion Progress | Accreditation |  |  |
| 7 | NIRF Parameter Report | Accreditation |  |  |
| 8 | Program Outcome Attainment | Accreditation |  |  |

### Orphan DocTypes (in code, not on workspace)
Accreditation Criterion, plus child tables: Accreditation Department Link, Accreditation Program Link, Accreditation Team Member, Assessment CO Link, Assessment Criteria Item, Bloom Distribution Rule, CO Direct/Final/Indirect Attainment, CO PO Mapping Entry, Committee Category Link, Committee Member, PO Attainment Entry, PO Final/Indirect Entry, PO PEO Mapping, Survey PO Rating, Survey Question Item, Unit Distribution Rule.

> Also note the orphan report `co_po_attainment` exists in code but isn't linked anywhere in the workspace.

---

## Workspace: University Inventory
**Module:** University Inventory

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Inventory Item | Inventory |  |  |
| 2 | Inventory Item Group | Inventory |  |  |
| 3 | Warehouse | Inventory |  |  |
| 4 | Stock Entry | Inventory |  |  |
| 5 | Stock Ledger Entry | Inventory |  |  |
| 6 | Supplier | Purchasing |  |  |
| 7 | Material Request | Purchasing |  |  |
| 8 | Purchase Order | Purchasing |  |  |
| 9 | Asset | Assets |  |  |
| 10 | Asset Category | Assets |  |  |
| 11 | Asset Movement | Assets |  |  |
| 12 | Asset Maintenance | Assets |  |  |
| 13 | Lab Consumable Issue | Assets |  |  |
| 14 | Lab Equipment | Assets |  |  |
| 15 | Lab Equipment Booking | Assets |  |  |
| 16 | Maintenance Team | Assets |  |  |
| 17 | Purchase Receipt | Assets |  |  |
| 18 | Stock Reconciliation | Assets |  |  |
| 19 | Supplier Group | Assets |  |  |
| 20 | UOM | Assets |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Asset Register | Reports |  |  |
| 2 | Stock Balance | Reports |  |  |
| 3 | Stock Ledger | Reports |  |  |
| 4 | Low Stock Items | Reports |  |  |
| 5 | Purchase Order Status | Reports |  |  |
| 6 | Lab Equipment Utilization | Reports |  |  |

### Orphan child DocTypes
Asset Maintenance Part, Asset Movement Item, Depreciation Schedule, Item Specification, Lab Consumable Issue Item, Maintenance Team Member, Material Request Item, Purchase Order Item, Purchase Receipt Item, Purchase Taxes and Charges, Stock Entry Item, Stock Reconciliation Item.

---

## Workspace: University Research
**Module:** University Research

### DocTypes
| # | DocType | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Research Publication | Publications | FIXED | **UAT-10**: only linked to Faculty (`corresponding_author` was Employee-only). | ✅ Added `researcher_type` Select (Faculty/Student/Mixed) with default Faculty, in_list_view+filter+description. Added `corresponding_student` Link to Student. Both author fields use `depends_on` based on researcher_type. Child `Publication Author` updated to support `author_type` Faculty/Student/External with conditional `employee` or `student` field. |
| 2 | Research Project | Projects & Grants | FIXED | **UAT-10**: PI was Employee-only; no student-led project support. | ✅ Added `researcher_type` (Faculty/Student/Mixed). Added `principal_student_investigator` (Link Student) + `principal_student_name` (fetch from student.student_name). PI fields show conditionally based on researcher_type. Child `Research Team Member` reworked to allow Faculty OR Student member with `member_type` switch. |
| 3 | Research Grant | Projects & Grants | FIXED | **UAT-10**: no recipient field at all (only research_project link). | ✅ Added `recipient_type` (Faculty/Student) + `recipient_employee` + `recipient_student` (with auto-fetched names). Conditional on recipient_type. Useful for student travel grants, paper presentation grants, etc. |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Faculty Research Output | Reports |  | **UAT-10**: keep name (still tracks faculty); for student research output, use Research Project / Publication list views filtered by `researcher_type=Student`. | _Renaming/sibling not needed — list views with the new `researcher_type` filter cover student-research analytics._ |
| 2 | Publication Statistics | Reports |  | **UAT-10**: now supports filtering by `researcher_type` via standard filter on Research Publication (since the field has `in_standard_filter:1`). | _Existing report works with standard sidebar filter._ |
| 3 | Grant Utilization Report | Reports |  |  |  |

### Orphan child DocTypes
Grant Utilization, Project Publication Link, Publication Author, Research Team Member.

---

## Workspace: University Communication
**Module:** University Integrations &nbsp;•&nbsp; Path: `university_integrations/workspace/university_communication`

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Notice Board | Notifications |  |  |
| 2 | User Notification | Notifications |  |  |
| 3 | Emergency Alert | Notifications |  |  |
| 4 | Emergency Acknowledgment | Notifications |  |  |
| 5 | Push Notification Settings | Notifications |  |  |
| 6 | Push Notification Log | Notifications |  |  |
| 7 | User Device Token | Notifications |  |  |
| 8 | Notice View Log | Notifications |  |  |
| 9 | University SMS Settings | Messaging |  |  |
| 10 | SMS Log | Messaging |  |  |
| 11 | SMS Queue | Messaging |  |  |
| 12 | WhatsApp Settings | Messaging |  |  |
| 13 | WhatsApp Template | Messaging |  |  |
| 14 | WhatsApp Log | Messaging |  |  |
| 15 | Email Queue Extended | Messaging |  |  |
| 16 | Grievance | Grievance & Feedback |  |  |
| 17 | Grievance Type | Grievance & Feedback |  |  |
| 18 | Grievance Committee | Grievance & Feedback | FIXED | **UAT-6**: form looked incomplete; Committee Member's Member Name didn't auto-populate. | ✅ Added `chairperson_name` + `secretary_name` (fetch_from `user.full_name`) so the names show beside the user IDs. Committee Member child: `member_name` now `read_only` + `fetch_from: user.full_name` for clean auto-fill. Schema already had members table, categories, contact info, active flag — kept. |
| 19 | Feedback Form | Grievance & Feedback |  |  |
| 20 | Feedback Response | Grievance & Feedback |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues | Fixed |
|---|---|---|---|---|---|
| 1 | Grievance Summary | Reports |  | Already had date defaults + category + grievance_type + status filters. |  |
| 2 | SLA Compliance Report | Reports |  | Already had from/to dates `reqd: 1` with defaults + category filter. UAT-7 finding stale — was likely "no data" because of empty DB at UAT time. |  |
| 3 | Faculty Feedback Report | Reports | FIXED | **UAT-7**: had only 3 filters, no dates, SQL was f-string interpolated (injection risk). | ✅ Filters expanded to 6 (From/To Date with 3-month defaults, Term, Department, Faculty, Min Rating). Python `get_data` rewritten with parameterised SQL. Added `HAVING avg_score >= min_rating`. |
| 4 | Feedback Analysis | Reports |  | Already had Form, Form Type, Term, From/To Date filters with 3-month default + custom formatter for color coding. UAT-7 stale. |  |
| 5 | Communication Analytics | Reports | FIXED | **UAT-8**: 404 on open; report had `ref_doctype: ""`. | ✅ Set `ref_doctype: "Communication"` (Frappe core doctype, always present). Frappe's report router now resolves the report URL. Existing 4 report types (summary/daily/category/template_usage), filters, and chart preserved. |
| 6 | SMS Delivery Report | Reports |  | Already has from/to dates with defaults + status filter. UAT-7 stale. |  |

---

## Workspace: University Integrations
**Module:** University Integrations &nbsp;•&nbsp; Path: `university_integrations/workspace/university_integrations`

### DocTypes
| # | DocType | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Payment Gateway Settings | Payment Gateway |  |  |
| 2 | Payment Transaction | Payment Gateway |  |  |
| _empty_ | — | **SMS Gateway** |  | 🟡 **ISSUE-4**: empty card |
| 3 | Biometric Device | Biometric Integration |  |  |
| 4 | Biometric Attendance Log | Biometric Integration |  |  |
| 5 | DigiLocker Settings | DigiLocker |  |  |
| 6 | DigiLocker Issued Document | DigiLocker |  |  |
| 7 | Certificate Template | Certificate Generation |  |  |
| 8 | Certificate Request | Certificate Generation |  |  |

### Reports
| # | Report | Card | Status | Notes / Issues |
|---|---|---|---|---|
| 1 | Payment Transaction Report | Reports |  |  |
| 2 | Certificate Issuance Report | Reports |  |  |

### Orphan DocTypes
Certificate Field (child), DigiLocker Document Type (child), **SMS Template** (could fill empty SMS Gateway card), WhatsApp Template Button (child).

---

## Workspace: University Analytics
**Module:** University Analytics

### DocTypes
| # | DocType | Status | Notes / Issues |
|---|---|---|---|
| 1 | Custom Dashboard |  |  |
| 2 | KPI Definition |  |  |
| 3 | KPI Value |  |  |
| 4 | Scheduled Report |  |  |
| 5 | Custom Report Definition |  |  |

### Reports
| # | Report | Status | Notes / Issues | Fixed |
|---|---|---|---|---|
| 1 | Student Performance Analysis |  |  |  |
| 2 | Grievance Summary |  | _shared with Communication ws_ |  |
| 3 | Faculty Feedback Report | FIXED | **UAT-7** _(shared with Communication ws — fixed in Section 9)_ | ✅ See Communication ws row for full details. |
| 4 | Feedback Analysis |  | _shared with Communication ws — already had defaults_ |  |
| 5 | SLA Compliance Report |  | _shared with Communication ws — already had defaults_ |  |
| 6 | Communication Analytics | FIXED | **UAT-8** _(fixed in Section 9)_ | ✅ `ref_doctype` set to `Communication`. |

### Orphan child DocTypes
Dashboard Role, Dashboard User, Dashboard Widget, Report Access Role, Report Column Definition, Report Filter Definition, Report Join Definition, Scheduled Report Recipient.

---

## Modules WITHOUT a dedicated workspace

### university_admissions
DocTypes appear under **University Academics → Admissions** card. Items: Admission Cycle, Admission Cycle Program (child), Admission Criteria, Merit List, Merit List Applicant (child), Seat Matrix.

### university_student_info
DocTypes appear under **University Academics → Student Info** card. Items: Student Status Log, University Alumni, University Announcement.

### university_feedback
DocTypes appear under **University Communication → Grievance & Feedback** card. Items: Feedback Form, Feedback Form Section (child), Feedback Question, Feedback Response, Feedback Answer (child), Feedback Section Score (child), Feedback Course/Department/Program Filter (child).

### university_grievance
DocTypes appear under **University Communication → Grievance & Feedback** card. Items: Grievance, Grievance Type, Grievance Committee, Grievance Action (child), Grievance Attachment (child), Grievance Communication (child), Grievance Escalation Log (child), Grievance Escalation Rule.

### university_payments
DocTypes appear under **University Finance → Payments** card. Items: Bank Transaction, Fee Category Account (child), Fee Refund (collides with finance — see BUG-2), Payment Order, PayU Settings, Razorpay Settings, University Accounts Settings, Webhook Log.

### university_portals 🟡 ISSUE-6
**No workspace.** DocTypes are reachable only via direct URLs (`/app/alumni`, `/app/job-posting`, etc.). Items:
- **Alumni** — NEEDS-CHANGE: **UAT-1** missing `Student` Link field (alumni records should link back to the originating Student row).
- Alumni Donation, Alumni Event, Alumni Event Registration, Alumni News.
- Announcement, Job Posting.
- Placement Application (duplicate name with `university_placement` — see UAT-9 + BUG/duplicate flag), Placement Drive (duplicate name), Placement Profile.

### Top-level `university_erp/doctype/` (utilities)
On University Home: University Settings, University Department.
On Communication: Notice Board, Notice View Log, User Notification, Emergency Alert, Emergency Acknowledgment.
On OBE Accreditation: NAAC Metric, NIRF Data.

**Not on any workspace** (test via direct URL): University Laboratory, Batch, Notice Target Department (child), Notice Target Program (child), Notification Preference, Notification Template, Suggestion, Suggestion Attachment (child), NAAC Document Checklist Item (child), NAAC Metric Document (child), NAAC Metric Year Data (child), Payment Webhook Log, Proctoring Snapshot.

---

## Production summary
| Workspace | DocTypes (linked) | Reports (linked) |
|---|---:|---:|
| University Home | 9 | 0 |
| University Academics | 10 | 0 |
| Faculty Management | 7 | 4 |
| University Examinations | 14 | 3 |
| University Finance | 12 (incl. broken Fee Payment) | 5 |
| University Hostel | 9 | 5 |
| University Transport | 4 | 3 |
| University Library | 7 | 4 |
| University Placement | 6 | 4 |
| University LMS | 8 | 3 |
| University OBE | 12 | 8 |
| University Inventory | 20 | 6 |
| University Research | 3 | 3 |
| University Communication | 20 | 6 |
| University Integrations | 8 | 2 |
| University Analytics | 5 | 6 |
| **TOTAL (workspace-linked)** | **154** | **62** |

Total DocTypes in `university_erp` app on prod: **264** (across 21 modules — most are child tables).
Total reports: **70**.

---

## Testing legend
- **PASS** — opens, CRUD works, validations behave, listed in workspace correctly.
- **FAIL** — error on open / save / submit / list view / report run.
- **NEEDS-CHANGE** — opens but has missing fields, wrong labels, broken filters, layout issues, etc. Describe in the Notes column.

## Reporting an issue
For each FAIL/NEEDS-CHANGE, paste in the Notes column:
1. **What you did** (e.g., "Clicked New, filled name = 'Test', clicked Save")
2. **What happened** (error message, blank screen, wrong field shown)
3. **What you expected** (optional but helpful)
4. **Browser console error** if any (open DevTools → Console, copy red lines)

---

## Open UAT issues — fix-tracking summary
| ID | Severity | Title | Affects |
|---|---|---|---|
| UAT-1 | ✅ Resolved | Student Link existed on all flagged DocTypes; root cause was lack of `in_standard_filter` and/or `in_list_view`. Plus the upstream `student_query` whitelist bug (separately fixed). All 8+ DocTypes now have proper visibility flags. Bulk Fee Generator + Internal Assessment + Practical Examination kept Won't Fix (architecturally correct as 1-to-many). | Course Registration, Student Status Log, University Alumni, Hall Ticket, Student Transcript, Student Scholarship, Payment Order, LMS Discussion (all updated). Already-correct: Answer Sheet, Revaluation Request, Fee Refund, Student Resume, Placement Application, LMS Content Progress, Assignment Submission, Alumni (portals). |
| UAT-2 | ✅ Resolved | Fee Refund doesn't fetch original Fee — schema was already wired; added client-side Fee filter by Student | Fee Refund |
| UAT-3 | 🟠 | Naming series missing/wrong | Course Registration, Hall Ticket, Answer Sheet, Internal Assessment, Practical Examination, Student Transcript, Online Examination, Generated Question Paper, Exam Schedule, Revaluation Request |
| UAT-4 | 🟡 | Elective Course Group field clarity | Elective Course Group |
| UAT-5 | ✅ Won't Fix | ~~Merge Question Bank~~ — KEEP Question Bank as designed | Question Bank, Question Tag, Question Paper Template, Generated Question Paper, Online Examination, Question Bank Analysis report (all preserved) |
| UAT-6 | ✅ Resolved | Grievance Committee schema was already complete; UI looked incomplete because chairperson/secretary names didn't auto-populate. Added fetch_from for full_name. | Grievance Committee, Committee Member |
| UAT-7 | 🔴 | Reports lack filters/joins/data | SLA Compliance, Faculty Feedback Report, Feedback Analysis, SMS Delivery Report, all Transport reports (3), all Library reports (4), all Placement reports (4), all LMS reports (3) |
| UAT-8 | ✅ Resolved | `ref_doctype` was empty in JSON — set to `Communication` so Frappe routes the report URL | Communication Analytics |
| UAT-9 | ✅ Resolved | Placement Application IS the placement-outcome model. Reports had 3 bad SQL joins + hardcoded date defaults — all fixed. | Placement Statistics, Company Wise Placement, Program Wise Placement, Placement Trend |
| UAT-10 | ✅ Resolved | Research module now supports Faculty/Student/Mixed via `researcher_type` field on Project/Publication and `recipient_type` on Grant. Child tables updated. | Research Project, Research Publication, Research Grant, Research Team Member, Publication Author |

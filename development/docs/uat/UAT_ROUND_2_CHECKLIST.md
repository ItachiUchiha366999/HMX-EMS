# UAT Round 2 — Verification Checklist

**Site:** `https://ems.hanumatrix.com`
**Tester:** Ruchik
**Round 1 date:** 2026-04-29
**Round 2 date:** _____________________
**Login:** Administrator (System Manager — sees everything)

---

## Pre-flight (before clicking anything)

- [ ] **Hard refresh** every workspace tab: Ctrl + Shift + R (Cmd + Shift + R on Mac).
  Round 1 fixes touched workspace JSON, doctypes, reports, and a service worker. Stale cache will hide what's been fixed.
- [ ] **Open in fresh incognito window** if anything looks broken — eliminates SW + localStorage pollution.
- [ ] If you see "Search dropdown 404" or "Invalid Method" → that means cache is still stale. Clear site data in DevTools → Application → Storage → Clear site data.

## How to use this checklist
- Each row has a **Pass/Fail** column. Tick the box if it works as described, otherwise leave unchecked and add a note in **Issues**.
- The tests are designed for **empty data** — most expected outcomes say "list opens with 0 rows, no error."  Once you re-seed data, run a second pass to test the data-bearing flows.
- A row **Fails** if you see: 404, "Invalid Method", "Not permitted", JS console error breaking page, blank white screen, or wrong field/label.

---

## Section 1 — Login + session sanity (5 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 1.1 | Open `https://ems.hanumatrix.com/login` in incognito | Login page renders | ☐ |  |
| 1.2 | Log in as `Administrator` | Lands on `/app/home` (no white screen, no JS error in console) | ☐ |  |
| 1.3 | Open `/app/student` | Empty list, "No Student found" message, no error in console | ☐ |  |
| 1.4 | Click the **+ New** button on `/app/student/new` | Form loads with all fields, `student_email_id` field visible | ☐ |  |
| 1.5 | DevTools → Network tab → see `frappe.desk.search.search_link` returning **200** (not 404) when you click any Link field | Returns 200 with `{message: []}` | ☐ |  |
| 1.6 | Open `/app/role` | Lists at least 44 Roles including `University Faculty`, `University HOD`, `University Exam Cell`, `Customer`, `Supplier` | ☐ |  |
| 1.7 | Open `/app/user` | Lists ONLY `Administrator` and `Guest` (data wipe still in effect) | ☐ |  |

---

## Section 2 — Workspace sidebar render (5 min)

For each workspace, confirm the page **renders without console errors** and shows the cards listed.

| # | Workspace | Expected cards visible | Pass | Issues |
|---|---|---|---|---|
| 2.1 | University Home | Student Management, Academics, Examinations, Finance, Masters, Settings | ☐ |  |
| 2.2 | University Academics | Academics, Admissions, Student Info | ☐ |  |
| 2.3 | Faculty Management | HR Management, Performance & Feedback, Reports | ☐ |  |
| 2.4 | University Examinations | Exam Scheduling, Question Bank, Online Examinations, Internal Assessment, Results & Transcripts, Reports | ☐ |  |
| 2.5 | **University Finance** ⚠️ | Fee Management, Procurement, Payments, Banking, General Ledger, Settings, Reports, Scholarships (8 cards × 32 doctypes + 15 reports) | ☐ |  |
| 2.6 | University Hostel | Master Data, Transactions, Reports | ☐ |  |
| 2.7 | University Transport | Master Data, Transactions, Reports | ☐ |  |
| 2.8 | University Library | Master Data, Transactions, Reports | ☐ |  |
| 2.9 | University Placement | Master Data, Job Management, Reports | ☐ |  |
| 2.10 | University LMS | Course Management, Assessments, Collaboration, Reports | ☐ |  |
| 2.11 | University OBE | Outcome Definitions (incl. Assessment Rubric — moved here), Outcome Mapping, Attainment Calculation, OBE Surveys, Reports, Accreditation | ☐ |  |
| 2.12 | University Inventory | Inventory, Purchasing, Assets, Reports | ☐ |  |
| 2.13 | University Research | Publications, Projects & Grants, Reports | ☐ |  |
| 2.14 | University Communication | Notifications, Messaging, Grievance & Feedback, Reports | ☐ |  |
| 2.15 | **University Integrations** ⚠️ | Payment Gateway, **SMS Gateway** (now 4 links: SMS Settings, SMS Template, SMS Log, SMS Queue), Biometric Integration, DigiLocker, Certificate Generation, Reports | ☐ |  |
| 2.16 | University Analytics | Custom Dashboard, KPI Definition, KPI Value, Scheduled Report, Custom Report Definition + 6 reports | ☐ |  |

---

## Section 3 — Resolved bug verification (10 min)

These are the bugs that broke things in Round 1. Confirm each is gone.

### 🔴 BUG-1 — Fee Payment ghost shortcut

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 3.1 | Open `/app/university-finance` | No "Fee Payment" shortcut at the top | ☐ |  |
| 3.2 | Network tab: no `reportview.get_count?doctype=Fee Payment` 404 | No 404 on this DocType | ☐ |  |
| 3.3 | Console: no "Uncaught (in promise) und" error during workspace render | Clean console | ☐ |  |

### 🟠 BUG-2 — Two Fee Refund DocTypes

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 3.4 | Open `/app/fee-refund` | Single Fee Refund list (no module-collision) | ☐ |  |
| 3.5 | Open `/app/doctype/Fee Refund` and check Module field | Module = "University Payments" | ☐ |  |

### 🟠 BUG-3 — Accounts Settings label

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 3.6 | On Finance workspace → Settings card, see TWO clearly-labeled entries | "Accounts Settings" (ERPNext) AND "University Accounts Settings" (us) | ☐ |  |

### 🟡 ISSUE-4 — SMS Gateway empty card

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 3.7 | Integrations workspace → SMS Gateway card | 4 entries: SMS Settings, SMS Template, SMS Log, SMS Queue | ☐ |  |

### 🟡 ISSUE-5 — Assessment Rubric placement

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 3.8 | OBE workspace → Outcome Definitions card | Includes "Assessment Rubric" link (after Course Outcome) | ☐ |  |
| 3.9 | OBE workspace → Reports card | Does NOT contain "Assessment Rubric" any more | ☐ |  |

### 🔴 UAT-8 — Communication Analytics

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 3.10 | Click **Communication Analytics** report from Communication or Analytics workspace | Report page loads (no 404 / "Not Found") | ☐ |  |
| 3.11 | Filters visible: Report Type, From Date, To Date | All three present with defaults (Today-30 / Today) | ☐ |  |
| 3.12 | Click "Generate New Report" | Either shows empty result or "no data" — no exception | ☐ |  |

---

## Section 4 — UAT-1 (Student field visibility) verification (15 min)

For each form below, click **+ New**, click the **Student** field, and confirm it BOTH (a) opens a dropdown (even if empty), (b) appears in the list view's filter sidebar.

> Note: with empty DB the dropdown will show "Create new Student". That's correct — the test is that the dropdown OPENS without a 404, and that you can filter list views by Student.

| # | DocType | Form opens | Student dropdown opens | Student in standard filter (sidebar of list view) | Issues |
|---|---|---|---|---|---|
| 4.1 | Course Registration `/app/course-registration/new` | ☐ | ☐ | ☐ |  |
| 4.2 | Student Status Log | ☐ | ☐ | ☐ |  |
| 4.3 | University Alumni `/app/university-alumni/new` | ☐ | ☐ | ☐ |  |
| 4.4 | Hall Ticket | ☐ | ☐ | ☐ |  |
| 4.5 | Answer Sheet | ☐ | ☐ | ☐ |  |
| 4.6 | Student Transcript | ☐ | ☐ | ☐ |  |
| 4.7 | Revaluation Request | ☐ | ☐ | ☐ |  |
| 4.8 | Fee Refund | ☐ | ☐ | ☐ |  |
| 4.9 | Student Scholarship | ☐ | ☐ | ☐ |  |
| 4.10 | Payment Order | ☐ | ☐ | ☐ |  |
| 4.11 | Student Resume | ☐ | ☐ | ☐ |  |
| 4.12 | Placement Application | ☐ | ☐ | ☐ |  |
| 4.13 | LMS Content Progress | ☐ | ☐ | ☐ |  |
| 4.14 | Assignment Submission | ☐ | ☐ | ☐ |  |
| 4.15 | LMS Discussion | ☐ | ☐ | ☐ |  |
| 4.16 | Alumni (portals) `/app/alumni/new` | ☐ | ☐ | ☐ |  |

**Won't Fix (don't expect a parent.student field):** Bulk Fee Generator, Internal Assessment, Practical Examination — these are class/cohort docs by design.

---

## Section 5 — UAT-2 + UAT-3 (Fee Refund + Naming series) (5 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 5.1 | Open `/app/fee-refund/new` | Form opens with field labeled **Original Fee** (not just "fees") | ☐ |  |
| 5.2 | Pick a Student in the Student field, then click "Original Fee" | Dropdown shows ONLY that student's fees (filtered) | ☐ |  |
| 5.3 | Pick a Fee | `Original Fee Amount`, `Paid Amount`, `Program` auto-populate | ☐ |  |
| 5.4 | Type values into Refund Amount (1000) and Deduction Amount (100) | Net Refund = 900 auto-computed | ☐ |  |
| 5.5 | Save a Course Registration draft | Doc name format `CR-2026-#####` (not a hash) | ☐ |  |
| 5.6 | Save an Exam Schedule draft | Doc name format `ES-2026-#####` (not a hash) | ☐ |  |
| 5.7 | Save a Student Status Log draft | Doc name format `SSL-2026-#####` (not a hash) | ☐ |  |
| 5.8 | Hall Ticket draft | Format `HT-2026-#####` | ☐ |  |
| 5.9 | Answer Sheet draft | Format `AS-2026-#####` | ☐ |  |
| 5.10 | Student Transcript draft | Format `TR-2026-#####` | ☐ |  |
| 5.11 | Revaluation Request draft | Format `RR-2026-#####` | ☐ |  |

---

## Section 6 — UAT-4 (Elective Course Group clarity) (3 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 6.1 | Open `/app/elective-course-group/new` | Help-text appears under **Group Name** explaining naming convention | ☐ |  |
| 6.2 | Click **Elective Type** dropdown | Shows 7 options with full names: DSE - Discipline Specific Elective, GE - Generic Elective, SEC - Skill Enhancement Course, AEC - Ability Enhancement Course, VAC - Value Addition Course, OE - Open Elective, MOOC - Online Elective | ☐ |  |
| 6.3 | Help-text appears under Elective Type | UGC NEP 2020 description visible | ☐ |  |
| 6.4 | List view sidebar filter | Elective Type filter chip available | ☐ |  |

---

## Section 7 — UAT-5 (Question Bank kept by design) (3 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 7.1 | Open `/app/question-bank` | List view exists and renders empty | ☐ |  |
| 7.2 | Click **Question Bank** card on Examinations workspace | Still present (intentionally NOT removed — see UAT-5 Won't Fix decision) | ☐ |  |
| 7.3 | Open Generated Question Paper form | Has child table linking to Question Bank | ☐ |  |
| 7.4 | Question Bank Analysis report runs | Empty result, no error | ☐ |  |

> **Why kept:** Question Bank is a reusable pool driving Question Paper Template auto-pick by Bloom/CO/PO distribution and provides cross-paper analytics. Removing it would break the architecture. Change of mind? Re-open the discussion.

---

## Section 8 — UAT-6 (Grievance Committee form) (3 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 8.1 | Open `/app/grievance-committee/new` | Form has all fields: Committee Name, Type, Description, Active flag, Meeting Frequency, Members section, Categories, Contact | ☐ |  |
| 8.2 | Pick Chairperson user | **Chairperson Name** auto-populates with the user's full_name | ☐ |  |
| 8.3 | Pick Secretary user | **Secretary Name** auto-populates | ☐ |  |
| 8.4 | Add a row in the Members child table → pick User | Member Name auto-populates (read-only) | ☐ |  |
| 8.5 | Try to save | Saves successfully | ☐ |  |

---

## Section 9 — UAT-7 (Reports filters + data) (20 min)

For each report, click into it from its workspace and verify:
1. **Filter sidebar opens** with the listed filter chips.
2. **Default values are pre-filled** where noted.
3. Click **Generate New Report** — should return either data (post-seed) or empty result with no exception.

### Transport (3 reports)

| # | Report | Expected filters | Pass | Issues |
|---|---|---|---|---|
| 9.1 | Route Wise Students | Academic Year (default = your user default), Route, Program, Vehicle | ☐ |  |
| 9.2 | Vehicle Utilization | From Date (last month, reqd), To Date (today, reqd), Vehicle Type, Status, Route | ☐ |  |
| 9.3 | Transport Fee Collection | Academic Year (default), Route, Program, "Outstanding Only" checkbox | ☐ |  |

### Library (4 reports)

| # | Report | Expected filters | Pass | Issues |
|---|---|---|---|---|
| 9.4 | Library Circulation | From/To Date (last month/today, reqd), Member Type, Article Category, Transaction Type | ☐ |  |
| 9.5 | Overdue Books | Member Type, Category, Min Overdue Days (default 1), Max Overdue Days | ☐ |  |
| 9.6 | Library Collection | Category, Subject, Article Status | ☐ |  |
| 9.7 | Member Borrowing History | Member (reqd), From/To Date, Transaction Type | ☐ |  |

### Placement (4 reports)

| # | Report | Expected filters | Pass | Issues |
|---|---|---|---|---|
| 9.8 | Placement Statistics | Academic Year (dynamic default), Program | ☐ |  |
| 9.9 | Company Wise Placement | Academic Year (dynamic), Industry Type, Placement Company | ☐ |  |
| 9.10 | Program Wise Placement | Academic Year (dynamic), Program | ☐ |  |
| 9.11 | Placement Trend | From/To Date (last 12 months/today, reqd), Academic Year, Group By (Month/Quarter/Year) | ☐ |  |

### LMS (3 reports)

| # | Report | Expected filters | Pass | Issues |
|---|---|---|---|---|
| 9.12 | Course Progress | LMS Course (NOT required anymore), Academic Term, Student, Min Progress % | ☐ |  |
| 9.13 | Assignment Submission Report | From/To Date (last 3 months/today), LMS Course, Assignment, Student, Status | ☐ |  |
| 9.14 | Quiz Analytics | From/To Date (last 3 months/today), LMS Course, Quiz, Student, Passed-Only checkbox | ☐ |  |

### Communication (5 reports + 1 fixed)

| # | Report | Expected filters | Pass | Issues |
|---|---|---|---|---|
| 9.15 | Grievance Summary | From/To Date (last 3 months/today), Category, Grievance Type, Status | ☐ |  |
| 9.16 | SLA Compliance Report | From/To Date (last month/today, reqd), Category, etc. | ☐ |  |
| 9.17 | Faculty Feedback Report ⭐ | From/To Date (last 3 months/today), Term, Department, Faculty, Min Rating | ☐ |  |
| 9.18 | Feedback Analysis | Form, Form Type, Term, From/To Date (last 3 months/today) | ☐ |  |
| 9.19 | Communication Analytics ⭐ | Report Type (default summary), From/To Date (Today-30/Today) | ☐ |  |
| 9.20 | SMS Delivery Report | From/To Date, Status | ☐ |  |

⭐ = had real bugs in Round 1, fixed in Round 2.

---

## Section 10 — UAT-9 (Placement Outcome SQL fix) (5 min)

These reports had a SQL ghost-join bug (`pa.placement_drive` field that didn't exist) → silently returned 0 rows even when data existed.

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 10.1 | Run Company Wise Placement after re-seed | Returns rows (not empty) once seed has Placement Application records with company set | ☐ |  |
| 10.2 | Run Program Wise Placement after re-seed | Same — returns rows | ☐ |  |
| 10.3 | Run Placement Trend after re-seed | Same — returns rows grouped by month/quarter | ☐ |  |

> Without seeded data: all 3 will return empty. **Mark them PASS if they don't error**, then re-test after re-seed.

---

## Section 11 — UAT-10 (Research Faculty/Student/Mixed) (5 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 11.1 | Open `/app/research-project/new` | New field **Researcher Type** (Select: Faculty / Student / Mixed, default Faculty) | ☐ |  |
| 11.2 | With Researcher Type = Faculty | Only "Principal Investigator (Faculty)" Link to Employee shows | ☐ |  |
| 11.3 | Switch Researcher Type = Student | Form swaps to "Principal Investigator (Student)" Link to Student | ☐ |  |
| 11.4 | Switch Researcher Type = Mixed | Both faculty AND student PI fields appear | ☐ |  |
| 11.5 | Open `/app/research-publication/new` | Researcher Type select + conditional `corresponding_author` (Employee) / `corresponding_student` (Student) | ☐ |  |
| 11.6 | Open `/app/research-grant/new` | New **Recipient Type** select (Faculty / Student) with conditional recipient field | ☐ |  |
| 11.7 | Add a row in Research Project's Co-Investigators table | New Member Type select; Faculty option shows Employee Link, Student option shows Student Link | ☐ |  |
| 11.8 | Add a row in Research Publication's Authors table | New Type select (Faculty/Student/External); conditional Employee or Student field | ☐ |  |

---

## Section 12 — Permission model (3 min)

These tests confirm the new DocPerm-based pattern works (no hardcoded role allowlists).

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 12.1 | Logged in as Administrator → click Student dropdown on any form | Opens (no 404) | ☐ |  |
| 12.2 | Open `/api/method/frappe.desk.search.search_link` directly via DevTools Console:<br>`frappe.call({method: 'frappe.desk.search.search_link', args: {doctype: 'Student', txt: ''}})` | Returns `{message: []}` HTTP 200 | ☐ |  |
| 12.3 | DevTools Console: `frappe.user_roles` | Lists 39+ roles including System Manager + all university roles | ☐ |  |

---

## Section 13 — Post-seed only (run AFTER re-seed) ⏳

These tests assume Students, Fees, Faculty, etc. exist. Skip until after re-seed.

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 13.1 | Hall Ticket form → pick a Student | `student_name` and `enrollment_number` auto-populate | ☐ |  |
| 13.2 | Fee Refund form → pick Student → pick Fee | `original_amount`, `paid_amount`, `program` auto-populate | ☐ |  |
| 13.3 | Course Progress report with no filters | Returns rows for every student with progress records | ☐ |  |
| 13.4 | Quiz Analytics: filter by Passed Only=true | Only passed attempts shown | ☐ |  |
| 13.5 | Transport Fee Collection: "Outstanding Only" checked | Only routes with outstanding > 0 | ☐ |  |
| 13.6 | Library Circulation: filter by Member Type=Student | Only student transactions | ☐ |  |
| 13.7 | Placement reports run | Show actual placement counts/companies | ☐ |  |
| 13.8 | Faculty Feedback Report: Min Rating = 4.0 | Only faculty with avg ≥ 4 shown | ☐ |  |
| 13.9 | Bulk Fee Generator → fill Program + Academic Year + Fee Structure → click "Generate Fees" | Fees generated for matching students | ☐ |  |
| 13.10 | Sales Invoice (ERPNext) → linked to Student | Customer auto-derived from Student profile | ☐ |  |

---

## Section 14 — Cross-flow integration (run AFTER re-seed) ⏳

End-to-end flows that span multiple modules.

| # | Flow | Steps | Pass | Issues |
|---|---|---|---|---|
| 14.1 | Admission → Student → Course → Fees | Create Applicant → convert to Student → enroll in Program → fee auto-generated | ☐ |  |
| 14.2 | Hall Ticket → Online Examination → Answer Sheet → Result | Issue Hall Ticket → student attempts exam → answer sheet evaluated → result published | ☐ |  |
| 14.3 | Hostel Allocation → Mess Menu → Attendance | Allocate room → student appears in mess menu → daily attendance logs | ☐ |  |
| 14.4 | Library: Issue → Overdue → Fine → Pay | Issue book → simulate overdue → fine generated → settle via Fees | ☐ |  |
| 14.5 | Placement: Drive → Job Opening → Application → Outcome | Schedule drive → post opening → student applies → status = "Placed" → reports update | ☐ |  |
| 14.6 | Grievance: Submit → Committee assigns → SLA tracks → Resolve | Student raises grievance → routed to committee → action steps → closed within SLA | ☐ |  |
| 14.7 | Research: Faculty starts project → adds Student team member → publishes paper with Student first-author | Both Researcher Type = Mixed flows work | ☐ |  |

---

## Section 15 — Performance + UX sanity (5 min)

| # | Test | Expected | Pass | Issues |
|---|---|---|---|---|
| 15.1 | Time from clicking workspace to render | < 3 seconds on broadband | ☐ |  |
| 15.2 | Search a DocType in global search (Ctrl+G) → "Course Registration" | Result links to `/app/course-registration` | ☐ |  |
| 15.3 | DevTools Console: any red errors during normal navigation? | Zero errors | ☐ |  |
| 15.4 | Network tab: any 404s during workspace render? | Zero (the SW + asset 404s for missing CSS bundles are expected and harmless) | ☐ |  |
| 15.5 | Service Worker (DevTools → Application → Service Workers) | Registered, active, no errors | ☐ |  |

---

## Section 16 — Regression tests (run AFTER any new fix lands) ⏳

If we patch anything else after Round 2, re-run these as a smoke test.

| # | Test | Pass | Issues |
|---|---|---|---|
| 16.1 | Login still works | ☐ |  |
| 16.2 | Finance workspace renders 8 cards | ☐ |  |
| 16.3 | Student dropdown opens (search_link returns 200) | ☐ |  |
| 16.4 | All 16 workspaces render | ☐ |  |
| 16.5 | Communication Analytics report opens | ☐ |  |

---

## Reporting Issues Found in Round 2

For each FAIL row, paste in the Issues column:

```
What I clicked:
What I saw:
What I expected:
Console error (if any):
Network 4xx/5xx URL (if any):
```

If something was working in Round 1 but broken in Round 2 → **regression** — flag it 🔴 in the Issues column.

---

## Sign-off

- [ ] All sections 1-9 pass
- [ ] All UAT-resolved bugs (3.1-3.12) verified
- [ ] No regressions found
- [ ] Section 13-14 deferred to post-seed
- [ ] Ready for re-seed

**Signed by:** _______________ **Date:** _______________

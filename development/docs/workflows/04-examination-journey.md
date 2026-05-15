# Journey 04 — Examination

**End-to-end examination flow:** the registrar opens the demo student's record on the desk → clicks **Create → Issue Hall Ticket** → the system pulls all the student's enrolled courses for the current term and creates a Hall Ticket with one exam row per course → registrar walks the Hall Ticket workflow Draft → Eligibility Check → **Issued** → student sees + downloads the hall ticket PDF on the portal → student writes the exams → registrar opens the Hall Ticket form again, clicks **Create → Enter Results**, types marks for each course in a single dialog → the system creates Assessment Plan + Assessment Group + Assessment Result rows automatically → the student sees grades + CGPA on the portal Academics tab.

This journey **uses the demo student created in Journey 01** (`zopevedant1@gmail.com`) and assumes Journeys 02 / 03 have run so the student has 7 enrolled courses + paid fees.

**No custom portal page for the registrar.** Both Issue Hall Ticket and Enter Results run from the standard ERPNext desk via buttons added by the university app.

---

## Test site

| | |
|---|---|
| Registrar desk — Student record | https://ems.hanumatrix.com/app/student/EDU-STU-2026-01602 |
| Registrar desk — Hall Ticket form | https://ems.hanumatrix.com/app/hall-ticket/HT-XXXX-XXXXX |
| Student portal — Hall Ticket / Results | https://ems.hanumatrix.com/student_portal → **Academics** / **Hall Tickets** tabs |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Exam Cell` (or Registrar) | any user with the role (or Administrator for UAT) | 1 – 2, 5 – 6 |
| `University Student` | `zopevedant1@gmail.com` / `demo@1234` | 3 – 4, 7 |

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert stu, "Run Journey 01 first"

ce_count = frappe.db.count("Course Enrollment", {"student": stu})
assert ce_count > 0, "No Course Enrollments — run Journey 01/02 first"
print(f"Ready: student {stu} has {ce_count} enrolled courses")
```

---

## Step-by-step UAT script

### Step 1 — Registrar opens the student's desk record

**As:** any user with `University Exam Cell` / `University Registrar` role
**Where:** https://ems.hanumatrix.com/app/student → list view → click `EDU-STU-2026-01602`

**Expected:** standard Frappe Student form. Top-right shows **Create** dropdown including a new **Issue Hall Ticket** action (added by the university app's `student_exam_actions.js`).

### Step 2 — Issue Hall Ticket

Click **Create → Issue Hall Ticket**. A dialog opens, pre-filled with the student's most-recent academic term.

| Field | Value |
|---|---|
| Academic Term | `2026-2027 (Semester 2)` (auto-filled) |
| Exam Type | `Regular` (or `Mid-Term` / `Supplementary` / `Makeup`) |

Click **Create Hall Ticket**.

**Expected:**
- Toast: _"Hall Ticket HT-XXXX-XXXXX created with 7 exams. Opening it..."_
- The Hall Ticket form opens automatically
- **Exams** child table is pre-populated with one row per enrolled course (Computer Networks, DSA, DBMS, OS, Software Engineering, Environmental Engineering, Communication Systems)
- For each course: `exam_date` and `venue` are pulled from any matching `Exam Schedule` row, otherwise defaulted to `today + 14 days` and the first available Room
- Workflow indicator pill: **Draft**, docstatus = 0

### Step 3 — Walk the workflow

Stay on the Hall Ticket form.

1. In the workflow action dropdown click **Submit for Eligibility Check** → state becomes **Eligibility Check**
2. Verify `Is Eligible` checkbox is ticked (default: ✓). If withholding, untick it and click **Withhold** instead.
3. Click **Issue** → state becomes **Issued**, docstatus = **1 (Submitted)**

**Expected:** the form is now read-only except for the **Create** dropdown which now shows a new **Enter Results** action (only appears in Issued state).

### Step 4 — Student downloads the hall ticket from the portal

**As:** `zopevedant1@gmail.com` / `demo@1234`
**Where:** https://ems.hanumatrix.com/student_portal → click **Academics** tab in the sidebar

**Expected:**
- The Academics page shows your enrolled courses
- For any course with results published, a **Download Hall Ticket** button appears next to the result row
- Clicking it downloads `Hall_Ticket_HT-XXXX-XXXXX.pdf` (~24 KB) — verifies code at top, exam-by-exam table with date/time/venue

> **Don't see the download button yet?** That's expected before Step 5 — the Vue portal only enables it when there's at least one Assessment Result for the student (which happens in Step 6).

### Step 5 — Registrar enters marks (after the exams are over)

**As:** `University Exam Cell`
**Where:** open the Hall Ticket again — `/app/hall-ticket/HT-XXXX-XXXXX`

Click **Create → Enter Results**.

A wide dialog opens with one editable row per exam:

| Course | Marks | Max |
|---|---|---|
| Computer Networks | `88` | 100 |
| Data Structures and Algorithms | `81` | 100 |
| Database Management Systems | `73` | 100 |
| Operating Systems | `67` | 100 |
| Software Engineering | `92` | 100 |
| Environmental Engineering | `78` | 100 |
| Communication Systems | `85` | 100 |

Type marks for each course (any plausible numbers — the test above used the values shown). Click **Submit Results**.

**Expected:**
- Toast: _"7 Assessment Results created."_
- The Hall Ticket form reloads — under **View** dropdown a new **Assessment Results** link appears

**Behind the scenes** (idempotent — clicking Submit Results twice doesn't duplicate):
- One `Assessment Plan` per course is created + submitted
- One `Assessment Group` named **Examinations** is auto-created on first run (under a root **All Assessment Groups** node)
- One `Assessment Criteria` master per exam type is auto-created
- One `Student Group` per (course, term, program) is auto-created and the student added — required by Education app's validation
- One `Assessment Result` per course is created and submitted, with `grade` mapped via the site's Grading Scale (10-point — A+ / A / B+ / B / C / D / F)

### Step 6 — Student sees grades + CGPA on the portal

**As:** `zopevedant1@gmail.com`
**Where:** https://ems.hanumatrix.com/student_portal → **Academics** tab (refresh)

**Expected:**

| Section | Expected |
|---|---|
| **Current CGPA** | calculated from all submitted Assessment Results (e.g. ≈ 8.06 with the marks above) |
| **Semester Results** | grouped by `2026-2027 - 2026-2027 (Semester 2)`, listing all 7 courses with marks + grade |
| **Total Courses** | `7` |
| **Latest Results** | first 4 rows visible on the Academics summary card |

Click any result row → opens the **Download Hall Ticket** button (now active) → PDF downloads.

### Step 7 — (Optional) Walk a Revaluation Request

If the student disputes a grade:

1. **As Student:** open the result on the portal → click **Request Revaluation** (if the UI exposes it; otherwise the Registrar files it on the student's behalf at `/app/revaluation-request/new`)
2. **As Registrar:** approve the request → the linked Assessment Result is unlocked for re-marking → repeat Step 5 to overwrite the score
3. **As Student:** refresh Academics → updated grade visible

(Revaluation has its own workflow — left as a follow-up journey if needed.)

---

## What the system creates when the registrar clicks "Issue Hall Ticket" / "Enter Results"

| Step | Artefact | DocType | Created by |
|---|---|---|---|
| Issue HT | Hall Ticket draft (one row per enrolled course) | `Hall Ticket`, `Hall Ticket Exam` (child) | `issue_hall_ticket` API |
| Issue (workflow) | Hall Ticket submitted (docstatus=1) | — | Standard workflow engine |
| Enter Results | Assessment Plans (one per course) | `Assessment Plan`, `Assessment Plan Criteria` (child) | `enter_results` API → `_ensure_assessment_plan` |
| Enter Results | Assessment Groups (`All Assessment Groups`, `Examinations`) — first time only | `Assessment Group` (NestedSet) | `_ensure_assessment_plan` |
| Enter Results | Assessment Criteria masters (e.g. `Regular`, `Mid-Term`) — first time only | `Assessment Criteria` | `_ensure_assessment_plan` |
| Enter Results | Student Groups for new exam combinations | `Student Group`, `Student Group Student` (child) | `_ensure_exam_group` |
| Enter Results | One submitted Assessment Result per course | `Assessment Result`, `Assessment Result Detail` (child) | `enter_results` API |

All driven by [`university_examinations/doctype/hall_ticket/hall_ticket_actions.py`](../../frappe-bench/apps/university_erp/university_erp/university_examinations/doctype/hall_ticket/hall_ticket_actions.py).

---

## Public APIs

| Method | Purpose | Permission |
|---|---|---|
| `university_erp.university_examinations.doctype.hall_ticket.hall_ticket_actions.issue_hall_ticket` | Create a draft Hall Ticket pre-filled with the student's enrolled courses | `University Exam Cell` / `University Registrar` / `System Manager` / `Administrator` |
| `university_erp.university_examinations.doctype.hall_ticket.hall_ticket_actions.enter_results` | Bulk-create + submit Assessment Results from per-course marks | Same as above |
| `university_erp.university_portals.api.portal_api.download_hall_ticket` | Render Hall Ticket as PDF | The student themselves |
| `university_erp.university_portals.api.portal_api.get_student_results` | Return all results for the current student (with linked Hall Ticket) | The student themselves |

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Issue Hall Ticket button missing on Student form** | Caller doesn't have `University Exam Cell` / `University Registrar` / `System Manager` / `Administrator`; OR Student record is in Draft (rare) | Add the role; hard-refresh the form. |
| **`No active Program Enrollment`** when clicking Issue | Student admission journey didn't complete OR PE was cancelled | Check `/app/program-enrollment` — should have one for this student with `docstatus=1`. Re-run Journey 01 if missing. |
| **`Hall Ticket already exists for X in Y`** | Existing HT for same student/term/exam_type | Cancel + delete the existing HT first, or pick a different `Exam Type` (e.g. `Supplementary`). |
| **Hall Ticket workflow: `Illegal Document Status`** when clicking Issue | The Issued state must have `doc_status=1`, but the workflow definition has it as `0` | Check **Workflow → Hall Ticket Workflow → States → Issued** and set `doc_status=1`. |
| **`Could not find Row #N: Venue`** on Issue Hall Ticket | Default room `Exam Hall 1` doesn't exist as a Room master | Already handled — the helper falls back to `frappe.db.get_value("Room", {}, "name")`. If the site has zero Rooms, create one under `/app/room`. |
| **Enter Results: `Sum of Scores of Assessment Criteria needs to be 100`** | Assessment Plan was created with `maximum_assessment_score` ≠ child criteria sum | Already handled — `_ensure_assessment_plan` adds one criterion row equal to `max_score`. |
| **Enter Results: `Student does not belong to group`** | Student missing from the per-course Student Group | Already handled — `_ensure_exam_group` creates the group + adds the student on first call. |
| **CGPA shows 0 on portal even though grades are entered** | Grading Scale on the site doesn't include the grade letters used | Open `/app/grading-scale` → confirm the active scale has rows for `O`, `A+`, `A`, `B+`, `B`, `C`, `D`, `F` with their grade points. The portal calculates CGPA by averaging `total_score / max_score × 10`. |
| **Hall Ticket PDF download returns HTML** | Frappe < 14 doesn't accept `type: "pdf"` directly | Already handled — `download_hall_ticket` uses `frappe.utils.pdf.get_pdf` to render bytes; this site is on Frappe 15.103.0. |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")

# Cancel and delete Assessment Results
for ar in frappe.db.get_all("Assessment Result", filters={"student": stu}, fields=["name", "docstatus"]):
    if ar.docstatus == 1:
        try: frappe.get_doc("Assessment Result", ar.name).cancel()
        except Exception: pass
    frappe.delete_doc("Assessment Result", ar.name, force=True)

# Cancel and delete Hall Tickets for this student
for ht in frappe.db.get_all("Hall Ticket", filters={"student": stu}, fields=["name", "docstatus"]):
    if ht.docstatus == 1:
        try: frappe.get_doc("Hall Ticket", ht.name).cancel()
        except Exception: pass
    frappe.delete_doc("Hall Ticket", ht.name, force=True)

# (Assessment Plans, Assessment Groups, Student Groups created during Enter Results
#  are intentionally kept — they're shared masters, not per-student junk.)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: Issue Hall Ticket (Registrar) ===
  Created HT-2026-04937 with 7 exams (one per enrolled course)
  Initial state: Draft, docstatus=0

=== STEP 2-3: Workflow walk ===
  Submit for Eligibility Check  →  state=Eligibility Check
  Issue                          →  state=Issued, docstatus=1

=== STEP 4: Student downloads PDF ===
  type=pdf, filename=Hall_Ticket_HT-2026-04937.pdf, bytes=24,228

=== STEP 5: Registrar enters results (7 courses, 1 dialog) ===
  Created 7 Results, skipped 0
    - Communication Systems:           85/100 → A+
    - Environmental Engineering:       78/100 → A
    - Software Engineering:            92/100 → O
    - Operating Systems:               67/100 → B+
    - Database Management Systems:     73/100 → A
    - Data Structures and Algorithms:  81/100 → A+
    - Computer Networks:               88/100 → A+

=== STEP 6: Portal academics ===
  semester_results count: 1 (2026-2027 - Semester 2)
  current_cgpa:           8.06
  total_courses:          7
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1-2 — Issue Hall Ticket creates draft with all enrolled courses | PASS / FAIL |
| Step 3 — workflow walks Draft → Eligibility Check → Issued | PASS / FAIL |
| Step 4 — student downloads Hall Ticket PDF | PASS / FAIL |
| Step 5 — Enter Results creates Assessment Results for all courses | PASS / FAIL |
| Step 6 — portal shows grades + CGPA + per-course breakdown | PASS / FAIL |
| Notes / defects logged |  |

# Journey 01 — Admission

**End-to-end admission flow:** an applicant fills the application form → registrar reviews documents → applicant is shortlisted → registrar allots a seat → registrar clicks **Admit** → the system auto-creates the Student record, the portal User (with the right role), the Program Enrollment, the Student-Group memberships, and the first Fees record. The applicant can then log into the student portal and see their courses + outstanding fee.

This journey **creates the demo student** (`zopevedant1@gmail.com`) used by every subsequent journey.

---

## Test site

| | |
|---|---|
| URL | https://ems.hanumatrix.com |
| Backend host | `ems.hanumatrix.com` (Docker container `ems-backend`) |
| DB | MariaDB container `ems-mariadb` |
| Today's date as of writing | 2026-05-03 |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| Applicant (anonymous form filler) | — | 1 |
| `University Registrar` | `registrar@nit.edu` (or any user with this role) | 2 – 6 |
| `University Student` | `zopevedant1@gmail.com` (created in step 6) | 7 |

## Pre-requisites

Run the checks on the back-end console (`bench --site ems.hanumatrix.com console`):

```python
import frappe
assert frappe.db.exists("Admission Cycle", {"status": "Open"}), "No open Admission Cycle"
assert frappe.db.count("Program") > 0, "No Programs defined"
assert frappe.db.exists("Academic Year", {}), "No Academic Year"
assert frappe.db.exists("Role", "University Student"), "Role missing"
assert frappe.db.exists("Workflow", {"document_type": "Student Applicant", "is_active": 1}), "Workflow inactive"
```

If any assert fails, fix the missing data before starting.

---

## Step-by-step UAT script

### Step 1 — Applicant fills the public admission form

**As:** anonymous applicant (no login)
**Where:** open https://ems.hanumatrix.com/admission-apply in a private/incognito browser tab

This is a real public Web Form bound to the `Student Applicant` doctype — anyone on the internet can submit it without an account. Fill the fields:

| Field | Value |
|---|---|
| First Name | `Vedant` |
| Middle Name | `Ganesh` |
| Last Name | `Zope` |
| Email | `zopevedant1@gmail.com` |
| Mobile Number | `9604520045` |
| Date of Birth | `2004-11-05` |
| Gender | `Male` |
| Admission Cycle | `AY 2026-2027 UG Admissions` |
| Academic Year | `2026-2027` |
| Program (primary preference) | `B.Tech Computer Science and Engineering` |
| Program Preference 1 | same as Program |
| Category | `General` |
| 10th Standard % | `88` |
| 12th Standard % | `70` |
| Entrance Exam Score | `93` |
| Address Line 1 | `Godrej Hillside 1` |
| City | `Pune` |
| State | `Maharashtra` |
| Pincode | `411045` |
| Country | `India` |

Click **Submit Application**.

**Expected:**
- Success page: _"Application received ✓ Thank you. Your application has been submitted."_
- Back-end: a `Student Applicant` row exists with workflow state **Applied**, application number auto-generated (e.g. `UG-2026-00001`), merit score auto-calculated as `(88 × 0.2) + (70 × 0.3) + (93 × 0.5) = 85.1`

> **For testers without browser access** — to simulate the form POST from the back-end:
> ```python
> # bench --site ems.hanumatrix.com console
> import frappe
> frappe.set_user("Guest")
> app = frappe.get_doc({
>     "doctype": "Student Applicant",
>     "first_name": "Vedant", "middle_name": "Ganesh", "last_name": "Zope",
>     "student_email_id": "zopevedant1@gmail.com", "student_mobile_number": "9604520045",
>     "date_of_birth": "2004-11-05", "gender": "Male",
>     "custom_admission_cycle": "AY 2026-2027 UG Admissions",
>     "academic_year": "2026-2027",
>     "program": "B.Tech Computer Science and Engineering",
>     "custom_program_preference_1": "B.Tech Computer Science and Engineering",
>     "custom_category": "General",
>     "custom_percentage_10th": 88, "custom_percentage_12th": 70, "custom_entrance_exam_score": 93,
>     "address_line_1": "Godrej Hillside 1", "city": "Pune", "state": "Maharashtra",
>     "pincode": "411045", "country": "India",
> })
> app.flags.ignore_permissions = True
> app.insert(ignore_permissions=True)
> frappe.db.commit()
> ```

### Step 2 — Registrar verifies documents (on the desk)

**As:** any user with `University Registrar` role (or Administrator for UAT)
**Where:** standard ERPNext desk

1. Open https://ems.hanumatrix.com/app/student-applicant — list view of all applicants
2. Filter the list by **workflow_state = Applied** to see fresh submissions
3. Click the row for `Vedant Ganesh Zope` (newest at the top — application number `UG-2026-XXXXX`)
4. The Student Applicant form opens — review the fields the candidate filled
5. In the workflow action dropdown (top right), click **Verify Documents**

**Expected:** state = **Document Verification**.

### Step 3 — Registrar shortlists

**As:** `University Registrar`
**Where:** same doc

Click **Shortlist**.

**Expected:** state = **Shortlisted**.

### Step 4 — Allot seat

**As:** `University Registrar`
**Where:** same doc

When the applicant is in the **Shortlisted** state, the form shows an **Actions → Allot Seat** button (added by the university client script).

- Click **Actions → Allot Seat**
- A dialog opens listing the applicant's program preferences (1, 2, 3) — **pick one**
- Click **Allot Seat**

**Expected:**
- `Custom Seat Allotted`, `Program`, and `Custom Admission Status` ("Seat Allotted") fields are populated automatically
- Toast: _"Seat allotted: B.Tech Computer Science and Engineering. You can now click Admit."_
- State still = **Shortlisted** (workflow doesn't move yet — Admit is a separate step)

> **Don't see the Allot Seat button?** It only appears when:
> - State is **Shortlisted** (not Applied / Document Verification)
> - `Custom Seat Allotted` is empty (the button hides itself once a seat is allotted)
> - You have permission to edit the doc
>
> If still missing after a hard refresh, run `bench --site ems.hanumatrix.com clear-cache` and reload.

### Step 5 — Admit

**As:** `University Registrar`
**Where:** same doc

Click **Admit**.

**Expected:**
- State = **Admitted**, **docstatus = 1 (Submitted)**
- Toast: _"Student EDU-STU-XXXX-XXXXX created from applicant EDU-APP-XXXX-XXXXX. Portal login enabled."_

### Step 6 — Set the student's password

**As:** `Administrator`
**Where:** **bench --site ems.hanumatrix.com console** OR User form

```python
from frappe.utils.password import update_password
update_password("zopevedant1@gmail.com", "demo@1234")
```

(In production the Welcome Email handles this; for UAT we set it explicitly so the tester can log in immediately.)

### Step 7 — Verify on the student portal

**As:** `zopevedant1@gmail.com` / `demo@1234`
**Where:** https://ems.hanumatrix.com/login → after login should redirect to **/student_portal**

| Panel | Expected |
|---|---|
| Top bar | Greeting "Hi Vedant", profile dropdown shows `zopevedant1@gmail.com` |
| Dashboard → **Total Courses** | `7` (program courses + the 2 electives the student picked) |
| Dashboard → **Outstanding Fees** | `₹50,000` (default tuition fee since no Fee Structure exists for B.Tech CSE) |
| Academics → **Current Courses** | 7 course cards (from the program's Student Groups + electives picked in Journey 02) |
| Fees → **Pending** | One row, **EDU-FEE-XXXX-XXXXX**, ₹50,000, status `Upcoming` |
| Profile | Name `Vedant Ganesh Zope`, email `zopevedant1@gmail.com`, program `B.Tech Computer Science and Engineering` |

---

## What the system creates automatically when you click "Admit"

| Artefact | DocType | Auto-created by |
|---|---|---|
| Student record | `Student` | `UniversityApplicant.on_update` → `_create_student_from_applicant` |
| Portal User | `User` | `_create_student_from_applicant` (also adds **Student** + **University Student** roles) |
| Program Enrollment | `Program Enrollment` | `_ensure_program_enrollment` (also enrolls in courses pulled from existing Student Groups for the program) |
| Student Group memberships | `Student Group Student` (child) | `_ensure_student_group_membership` (so the portal academics page sees the courses) |
| Fees record | `Fees` | `_ensure_first_fees` (auto-submitted) |
| Sales Invoice | `Sales Invoice` | `_ensure_first_invoice` (parallel to Fees, for accounting) |

All hooks live in [`overrides/student_applicant.py`](../../frappe-bench/apps/university_erp/university_erp/overrides/student_applicant.py).

### Public admission form

The Step-1 page at `/admission-apply` is a Frappe **Web Form** named `apply-for-admission`, bound to `Student Applicant`, with `published=1`, `login_required=0`, `anonymous=1`. To recreate or edit it: **Awesome Bar → Web Form → Apply for Admission**, or rerun the bootstrap script (kept here as the source of truth):

```python
# bench --site ems.hanumatrix.com execute path/to/create_admission_webform.py
# (or paste into bench console)
```

The 21 form fields mirror the columns the Registrar later sees on the back-end Student Applicant doc, so nothing is lost in translation.

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Workflow action buttons missing** | User doesn't have `University Registrar` role | `bench --site ems.hanumatrix.com console`: `frappe.get_doc("User", "registrar@nit.edu").add_roles("University Registrar")` |
| **`Illegal Document Status for Document Verification`** when clicking Verify Documents | Workflow's `Admitted` state has wrong `doc_status` | Should be: Applied=0, Document Verification=0, Shortlisted=0, Admitted=1, Rejected=0, Withdrawn=2. Patched in `setup/create_workflows.py`. |
| **`Cannot create Student record — no program allotted`** toast on Admit | Step 4 was skipped — no `Custom Seat Allotted` value | Re-open the Applicant in **Edit** mode, set Custom Seat Allotted, Save, then click Admit again. |
| **Portal redirects student to /app instead of /student_portal** | User is missing `University Student` role | The auto-creation should have added it; if not: `User → Add Role → University Student` |
| **`Enrollment Date cannot be before the Start Date of the Academic Year`** in error log | Today's date < AY start date | Already handled — `_ensure_program_enrollment` picks the AY/term start date in that case. |
| **Fees panel still empty after Admit** | The `Fees` record was inserted but submit failed | Check error log; manually: `bench --site ems.hanumatrix.com console` → `f = frappe.get_doc("Fees", "EDU-FEE-XXXX-XXXXX"); f.submit(); frappe.db.commit()` |
| **`Invalid Enrollment None for student EDU-STU-XXXX`** during fees insert | Program Enrollment hadn't been created/submitted before fees insert | Already handled — `_ensure_first_fees` short-circuits if no submitted PE exists. |
| **Academics page shows 0 courses despite admission succeeding** | Program has no `courses` child rows AND there are no Student Groups for that program | Either add courses to the Program master, or create at least one `Student Group` per program/course combination. |
| **`/admission-apply` returns 404** | Web Form not published, or route changed | Check **Web Form → apply-for-admission**: `published=1`, `route=admission-apply`. Then `bench --site ems.hanumatrix.com clear-website-cache`. |
| **`/admission-apply` shows "Login required" page** | Web Form has `login_required=1` | Set the field on the Web Form to `0` and clear cache. |
| **Form submit returns "Permission denied"** | `Guest` role lacks Create permission on `Student Applicant` | The Web Form's `accept()` calls `insert(ignore_permissions=True)` so this should not happen — but if you see it, confirm the Web Form's `anonymous=1` flag is set. |

---

## Re-run the journey (cleanup)

To wipe the UAT student and re-run from scratch:

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"

s = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
if s:
    for ce in frappe.db.get_all("Course Enrollment", filters={"student": s}, fields=["name"]):
        frappe.delete_doc("Course Enrollment", ce.name, force=True)
    for f in frappe.db.get_all("Fees", filters={"student": s}, fields=["name", "docstatus"]):
        if f.docstatus == 1: frappe.get_doc("Fees", f.name).cancel()
        frappe.delete_doc("Fees", f.name, force=True)
    for pe in frappe.db.get_all("Program Enrollment", filters={"student": s}, fields=["name", "docstatus"]):
        if pe.docstatus == 1: frappe.get_doc("Program Enrollment", pe.name).cancel()
        frappe.delete_doc("Program Enrollment", pe.name, force=True)
    for si in frappe.db.get_all("Sales Invoice", filters={"remarks": ["like", f"%{s}%"]}, fields=["name", "docstatus"]):
        if si.docstatus == 1: frappe.get_doc("Sales Invoice", si.name).cancel()
        frappe.delete_doc("Sales Invoice", si.name, force=True)
    # Remove from any Student Groups
    for sgs in frappe.db.get_all("Student Group Student", filters={"student": s}, fields=["name", "parent"]):
        frappe.db.sql("DELETE FROM `tabStudent Group Student` WHERE name=%s", sgs.name)
    frappe.delete_doc("Student", s, force=True)

for a in frappe.db.get_all("Student Applicant", filters={"student_email_id": EMAIL}, fields=["name", "docstatus"]):
    if a.docstatus == 1:
        try: frappe.get_doc("Student Applicant", a.name).cancel()
        except Exception: pass
    frappe.delete_doc("Student Applicant", a.name, force=True)

if frappe.db.exists("User", EMAIL):
    frappe.db.sql("UPDATE `tabStudent` SET user=NULL WHERE user=%s", EMAIL)
    frappe.delete_doc("User", EMAIL, force=True)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: Create Student Applicant (state=Applied, draft) ===
  Created: EDU-APP-2026-00004
    App #: UG-2026-00001, merit: 85.1, state: Applied

=== STEP 2: Verify Documents ===  →  state=Document Verification
=== STEP 3: Shortlist ===          →  state=Shortlisted
=== STEP 4: Allot seat ===         →  custom_seat_allotted=B.Tech CSE
=== STEP 5: Admit ===              →  state=Admitted, docstatus=1

=== Verify auto-created artefacts ===
  Student:             EDU-STU-2026-01602
  User roles:          ['Student', 'University Student']
  Program Enrollment:  EDU-ENR-2026-02406 (B.Tech CSE, AY 2026-2027, Sem 2, docstatus=1)
  Enrolled courses:    5 (DSA, DBMS, OS, Software Engineering, Computer Networks)
  Fees:                EDU-FEE-2026-01404, ₹50,000, docstatus=1
  Sales Invoice:       ACC-SINV-2026-01402, ₹50,000 outstanding
  Portal redirect:     student_portal ✓
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1 — application form filled | PASS / FAIL |
| Step 2-3 — workflow transitions visible | PASS / FAIL |
| Step 4 — seat allotment saved | PASS / FAIL |
| Step 5 — Admit auto-creates artefacts | PASS / FAIL |
| Step 7 — portal shows courses + fees | PASS / FAIL |
| Notes / defects logged |  |

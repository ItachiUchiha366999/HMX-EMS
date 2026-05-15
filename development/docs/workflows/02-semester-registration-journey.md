# Journey 02 — Semester Registration

**End-to-end course registration flow:** the student logs into the portal → opens the **Register for Courses** page → ticks a few electives → submits → the registrar approves → the system auto-creates `Course Enrollment` rows so the new courses appear in the student's academics view.

This journey **uses the demo student created in Journey 01** (`zopevedant1@gmail.com` / `demo@1234`). If that student doesn't exist yet, run Journey 01 first.

---

## Test site

| | |
|---|---|
| Public registration page | https://ems.hanumatrix.com/register-courses (login required) |
| Back-end Course Registration list | https://ems.hanumatrix.com/app/course-registration |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Student` (Website User — no desk access) | `zopevedant1@gmail.com` | 1 – 3, 6 |
| `University Registrar` | any user with the role (or Administrator for UAT) | 4 – 5 |

> **Note on student perms.** A student is a Frappe **Website User**, not a System User, and only has the `Student` + `University Student` roles — no access to `/app/*` desk pages. The portal page at `/register-courses` and the three whitelisted API methods are all the student needs. They never have to open a desk form. When the student submits, the registration is auto-pushed to **Pending Faculty Approval** by the API (since the student can't click the workflow button themselves), and lands directly in the Registrar's queue for one-click approval.

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"

# 1. demo student exists (created in Journey 01)
assert frappe.db.exists("Student", {"student_email_id": EMAIL}), "Run Journey 01 first"

# 2. Student has an active Program Enrollment
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert frappe.db.exists("Program Enrollment", {"student": stu, "docstatus": 1}), "PE missing"

# 3. Course Registration Workflow active
wf = frappe.db.get_value("Workflow", {"document_type": "Course Registration"}, ["name", "is_active"], as_dict=True)
assert wf and wf.is_active, "Workflow inactive"

# 4. The /register-courses page is reachable (no SPA conflict)
print("All checks passed")
```

---

## Step-by-step UAT script

### Step 1 — Student opens the registration page

**As:** `zopevedant1@gmail.com` (logged in)
**Where:** open https://ems.hanumatrix.com/register-courses

**Expected:**
- Page title **"Register for Courses"**, greeting **"Hi Vedant Ganesh Zope — pick courses for 2026-2027 (Semester 2) (B.Tech CSE)"**
- "Available Courses" card lists ~10 courses the student isn't currently enrolled in (Core in orange, Elective in blue)
- "My Registrations" card is empty (no prior registrations)

> **If the page redirects to the Vue dashboard or shows a spinner forever:** the URL must be `/register-courses` (not `/student_portal/register_courses`). The Vue SPA grabs everything under `/student_portal/*`.

### Step 2 — Student picks courses

Tick the checkboxes next to **2–4 courses**. The footer counter updates: `"3 selected, 9 credits"`. The **Submit Registration** button enables.

### Step 3 — Submit

Click **Submit Registration**.

**Expected:**
- Green toast: _"Registration CR-XXXX-XXXXX submitted (3 courses, 9 credits). Pending Registrar approval."_
- Page reloads after 1.5 s
- "My Registrations" card now shows the new row, status pill **Pending** (orange) — the API auto-advanced the workflow from `Draft` to `Pending Faculty Approval` on the student's behalf
- The picked courses no longer appear in "Available Courses" (they're in your registration now)

### Step 4 — Registrar approves (on the desk)

**As:** any user with `University Registrar` role (or Administrator for UAT)
**Where:** open the standard ERPNext desk:

1. https://ems.hanumatrix.com/app/course-registration → list view shows all CRs
2. Filter the list by **workflow_state = Pending Faculty Approval** to see the queue
3. Click the row for the demo student (it'll be the most recent CR with `student = EDU-STU-2026-01602`)
4. The Course Registration form opens — you'll see the picked courses in the child table
5. Click **Approve** in the workflow action dropdown (top right)

**Expected:**
- State pill changes to **Approved**, docstatus = **1 (Submitted)**
- Green toast: _"N courses enrolled for Vedant Ganesh Zope."_
- A `Course Enrollment` row is auto-created for each course in the registration

### Step 5 — Verify Course Enrollments were created

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")
ce_count = frappe.db.count("Course Enrollment", {"student": stu})
print(f"Total Course Enrollments: {ce_count}")
# Should be 5 (admission baseline) + N (from this journey) = 5+N
```

### Step 6 — Student sees the updated portal

**As:** `zopevedant1@gmail.com`
**Where:** https://ems.hanumatrix.com/register-courses (refresh)

**Expected:**
- "My Registrations" row now shows status **Approved** (green pill)
- Available Courses list shrinks by N (the picked courses are now enrolled and so are excluded)

Then go to https://ems.hanumatrix.com/student_portal → **Academics** tab.

**Expected:** the new courses appear in the academics list (this requires the courses to have a Student Group for the program — see "Common breaks" below).

---

## What the system creates automatically when the Registrar clicks "Approve"

| Artefact | DocType | Auto-created by |
|---|---|---|
| One Course Enrollment per registered course | `Course Enrollment` | `CourseRegistration.on_update` (in [`course_registration.py`](../../frappe-bench/apps/university_erp/university_erp/university_academics/doctype/course_registration/course_registration.py)) |

Idempotent — if you click Approve twice (or re-approve an already-approved registration), no duplicate Course Enrollments are created.

---

## Public API used by the page

| Method | Purpose |
|---|---|
| `university_erp.university_academics.doctype.course_registration.course_registration.get_registrable_courses` | List of courses the current student can register for |
| `university_erp.university_academics.doctype.course_registration.course_registration.submit_registration` | Insert a Draft Course Registration with the picked courses |
| `university_erp.university_academics.doctype.course_registration.course_registration.get_my_registrations` | List of current student's existing Course Registrations |

All three are `@frappe.whitelist()` and run as the logged-in student — no permissions need to be granted to `University Student` to use them.

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| `/register-courses` shows spinner / Vue dashboard | URL is under `/student_portal/*`, intercepted by the Vue SPA | Use **`/register-courses`** (no `student_portal/` prefix). |
| **No courses available** message even though student isn't enrolled in everything | Program has no `courses` child rows AND no Student Groups exist for the program | Either add courses to the Program master, or create at least one Student Group per program. The API now also falls back to courses from *other* programs as elective options (capped at 10). |
| **Submit button stays disabled** after ticking | JS console error / network issue | Open DevTools → Network: confirm `submit_registration` POST returns 200. |
| **`Duplicate course in registration: X`** on submit | The student already has this course in another draft CR for the same term | Open the prior CR and remove the duplicate, or pick different courses. |
| **No Course Enrollments after Approve** | Student has no submitted Program Enrollment | Check error log: _"No Program Enrollment for X — cannot create Course Enrollments"_. Run Journey 01 to ensure PE exists. |
| **Course Enrollments created but Academics page still shows old list** | Portal Academics queries `Student Group Student`, not `Course Enrollment` | Add the student to the Student Groups for the new courses (or use the Vue portal's Academics tab which reads from a different source). |
| **`Enrollment Date cannot be before the Start Date of the Academic Term`** in error log | Academic Term starts in the future | Already handled — `on_update` uses `term_start_date` if today is before it. |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")

# Find the courses added by THIS journey (CR after the seed baseline)
for cr in frappe.db.get_all("Course Registration", filters={"student": stu}, fields=["name", "docstatus"]):
    courses = [r.course for r in frappe.get_all("Course Registration Item", filters={"parent": cr.name}, fields=["course"])]
    if cr.docstatus == 1:
        try: frappe.get_doc("Course Registration", cr.name).cancel()
        except Exception: pass
    frappe.delete_doc("Course Registration", cr.name, force=True)
    # Drop the Course Enrollments that this CR created
    for ce in frappe.db.get_all("Course Enrollment", filters={"student": stu, "course": ["in", courses]}, fields=["name"]):
        frappe.delete_doc("Course Enrollment", ce.name, force=True)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== Acting as zopevedant1@gmail.com ===
Roles: ['Student', 'University Student', 'All', 'Guest']
(Website User — no desk access)

=== STEP 1: Student fetches available courses ===
  10 courses available for Vedant Ganesh Zope in 2026-2027 (Semester 2)

=== STEP 2-3: Student picks + submits ===
  Picked: ['Environmental Engineering', 'Communication Systems']
  Submitted: CR-2026-04929
  workflow_state: Pending Faculty Approval     ← API auto-advanced from Draft

=== STEP 4: Registrar → Approve ===           →   state=Approved, docstatus=1

=== STEP 5: New Course Enrollments ===
  - EDU-CE-2026-04935: Environmental Engineering
  - EDU-CE-2026-04936: Communication Systems

=== STEP 6: Portal ===
  My Registrations row shows: Approved (green)
  Total Course Enrollments:   7  (5 baseline + 2 new)
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1 — page loads with available courses | PASS / FAIL |
| Step 2-3 — submit lands directly in Pending Faculty Approval | PASS / FAIL |
| Step 4 — Registrar approves and docstatus=1 | PASS / FAIL |
| Step 5 — Course Enrollments auto-created | PASS / FAIL |
| Step 6 — portal "My Registrations" shows Approved | PASS / FAIL |
| Notes / defects logged |  |

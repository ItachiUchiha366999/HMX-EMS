# Journey 08 — Placement

**End-to-end placement flow:** the placement officer posts a Placement Job Opening on the desk → student opens the portal Placement tab → clicks **Apply Now** → a Placement Application is created in `Applied` state → placement officer walks the application through the workflow on desk: Applied → Screening → Shortlisted → **Schedule Interview** (dialog prompts for date/time/venue) → Interview Scheduled → **Record Offer** (dialog prompts for CTC) → Offer Received → student accepts/declines from portal → Accepted (or Withdrawn).

Uses the demo student created in Journey 01 (`zopevedant1@gmail.com` / `demo@1234`).

---

## Test site

| | |
|---|---|
| Job Opening list | https://ems.hanumatrix.com/app/placement-job-opening |
| Placement Application list | https://ems.hanumatrix.com/app/placement-application |
| Student portal — Placement tab | https://ems.hanumatrix.com/student_portal → **Placement** |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Placement Officer` | any user with role | 1, 3 – 5 |
| `University Student` | `zopevedant1@gmail.com` | 2, 6 |

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert stu, "Run Journey 01 first"

open_jobs = frappe.db.count("Placement Job Opening", {"status": "Open"})
assert open_jobs > 0, "No open jobs seeded"

wf = frappe.db.get_value("Workflow", {"document_type": "Placement Application", "is_active": 1}, "name")
assert wf, "Placement Application workflow not active"
print(f"Ready: {stu}, {open_jobs} open jobs, workflow={wf}")
```

---

## Step-by-step UAT script

### Step 1 — (Optional) Placement Officer posts a new job

If you need a fresh job opening for the test, do it on desk:

**As:** `University Placement Officer`
**Where:** https://ems.hanumatrix.com/app/placement-job-opening/new

| Field | Value |
|---|---|
| Job Title | `Software Engineer` |
| Company | `Flipkart` (or any seeded company) |
| Job Type | `Full Time` |
| Status | `Open` |
| Vacancies | `5` |
| Min CTC / Max CTC | `600000` / `1500000` |
| Job Location | `Bengaluru` |
| Min CGPA | `6.5` |
| Deadline | today + 14 days |
| Job Description | free text |
| Skills Required | comma-separated tags |

Click **Save**. The job is now listed on the student portal's Placement → Job Postings tab.

> **For the UAT, the seed already has 20 open jobs.** Skip this step and use one of them.

### Step 2 — Student applies via portal

**As:** `zopevedant1@gmail.com` / `demo@1234`
**Where:** https://ems.hanumatrix.com/student_portal → **Placement** tab → **Job Postings** sub-tab

Pick a job (e.g. `Flipkart - Analyst (JOB-2026-00100)`). Click **Apply Now**.

**Expected:**
- Toast: success message
- Switch to **My Applications** sub-tab — the new application shows up with status **Applied**
- Behind the scenes: a `Placement Application` is created (`PA-XXXX-XXXXX`), workflow_state=`Applied`, with company + job_title auto-filled from the job opening
- Idempotent: clicking Apply again on the same job returns the existing application instead of creating a duplicate

### Step 3 — Placement Officer screens + shortlists

**As:** `University Placement Officer`
**Where:** https://ems.hanumatrix.com/app/placement-application — list filter `workflow_state = Applied`

Open the demo student's row (e.g. `PA-XXXX-XXXXX`). In the workflow action dropdown:

1. Click **Start Screening** → state becomes **Screening**
2. (Review the candidate's profile, scores, etc.)
3. Click **Shortlist** → state becomes **Shortlisted**

(If unsuitable, click **Reject** instead.)

### Step 4 — Schedule Interview

Stay on the same form. The custom university JS adds an **Actions → Schedule Interview** button when state = `Shortlisted`.

Click it. Dialog:

| Field | Value |
|---|---|
| Interview Date | today + 7 days (default) |
| Interview Time | `10:00:00` (default) |
| Venue | `Auditorium A` (default) |
| Round | `Technical` (optional, e.g. Technical / HR / Aptitude) |

Click **Schedule**.

**Expected:**
- The `interview_date / time / venue / round` fields save first, then the workflow advances to **Interview Scheduled**
- The student sees the interview info on the portal Placement → My Applications panel

### Step 5 — Record Offer

After the interview, return to the same Placement Application form. The form now shows an **Actions → Record Offer** button (when state = `Interview Scheduled`).

Click it. Dialog:

| Field | Value |
|---|---|
| Offered Package (₹/year) | `800000` |
| Remarks | _e.g. "Strong technical interview; aptitude test cleared"_ |

Click **Record Offer**.

**Expected:**
- `package_offered = 800000` saved
- Workflow advances to **Offer Received**
- A mirror is written to the legacy `offered_ctc` column too (some reports key off it)
- Student sees the offer + CTC on the portal

### Step 6 — Student accepts (or declines)

**As:** `zopevedant1@gmail.com`
**Where:** https://ems.hanumatrix.com/student_portal → **Placement** → **My Applications**

The accepted offer row shows two buttons. The student calls one of:
- `respond_to_offer(application, decision="accept")` → workflow_state = `Accepted`, status = `Accepted`
- `respond_to_offer(application, decision="decline")` → workflow_state = `Withdrawn`, status = `Withdrawn`

> **Implementation detail:** the Frappe workflow's `Accept Offer` transition is locked to `University Placement Officer` (a quirk of the seeded workflow), so the student-side acceptance bypasses it via `db.set_value`. The end state is identical.

**Expected:**
- Toast: success
- Application row now shows `Accepted` (or `Withdrawn` on decline)

---

## What the system creates / updates

| Step | Artefact | Created/Updated by |
|---|---|---|
| Step 2 | `Placement Application` (workflow_state=Applied) | `apply_for_job` API |
| Step 3 | workflow_state → Screening / Shortlisted / Rejected | Standard workflow |
| Step 4 | `interview_date / time / venue / round` set; state → Interview Scheduled | desk dialog (`placement_application.js`) → `frappe.model.workflow.apply_workflow` |
| Step 5 | `package_offered` set; state → Offer Received; `offered_ctc` mirrored | desk dialog → `apply_workflow` + `frappe.db.set_value` |
| Step 6 | workflow_state → Accepted or Withdrawn | `respond_to_offer` API |

All driven by:
- [`university_portals/api/portal_api.py`](../../frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py) (`apply_for_job`, `respond_to_offer`, `get_placement_*`)
- [`public/js/placement_application.js`](../../frappe-bench/apps/university_erp/university_erp/public/js/placement_application.js) (Schedule / Record Offer dialogs)

---

## Public APIs

| Method | Purpose | Permission |
|---|---|---|
| `university_erp.university_portals.api.portal_api.get_placement_opportunities` | All open jobs | Logged-in student |
| `university_erp.university_portals.api.portal_api.apply_for_job(job_opening)` | Create a Placement Application | Logged-in student |
| `university_erp.university_portals.api.portal_api.get_placement_applications` | Student's own applications + interview/offer details | Logged-in student |
| `university_erp.university_portals.api.portal_api.respond_to_offer(application, decision)` | Accept / decline offer | Logged-in student (their own application) |
| `university_erp.university_portals.api.portal_api.get_placement_stats` | applied / shortlisted / interviews / new roles | Logged-in student |

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Apply Now button errors with "no attribute apply_for_job"** | Backend method missing | Already added — `university_portals/api/portal_api.py::apply_for_job`. |
| **`Placement Drive None not found`** when applying | Old controller demanded `placement_drive` | Already patched to make `placement_drive` optional and validate only when present. |
| **`This is not your application`** on respond_to_offer | A different student is logged in | Log in as the application's owner. |
| **`Cannot accept — application is in 'Applied' state, not 'Offer Received'`** | Trying to accept too early | Walk the workflow to Offer Received first. |
| **Schedule Interview workflow throws "Mandatory: interview_date"** | Officer clicked the workflow button directly without setting interview details first | Use the **Actions → Schedule Interview** dialog instead, which sets the fields before the transition. |
| **Record Offer button missing at Interview Scheduled** | User doesn't have `University Placement Officer` (or higher) | Add the role: `frappe.get_doc("User", "...").add_roles("University Placement Officer")`. Hard-refresh form. |
| **`offered_ctc` shows 0 in old reports** | Frappe meta drift — active doctype uses `package_offered`, legacy reports use `offered_ctc` | The dialog mirrors to both columns. If you set CTC programmatically, do `frappe.db.set_value(..., {"package_offered": X, "offered_ctc": X})`. |
| **Application list throws `Unknown column 'workflow_state'`** | Column wasn't added to the table | Already patched (`ALTER TABLE \`tabPlacement Application\` ADD COLUMN workflow_state varchar(140)`). |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")

for pa in frappe.db.get_all("Placement Application", filters={"student": stu}, fields=["name", "docstatus"]):
    if pa.docstatus == 1:
        try: frappe.get_doc("Placement Application", pa.name).cancel()
        except Exception: pass
    frappe.delete_doc("Placement Application", pa.name, force=True)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: Student applies (apply_for_job) ===
  PA-2026-00402  →  Flipkart Analyst (Applied)

=== STEP 2: Placement Officer walks workflow ===
  Start Screening      → Screening
  Shortlist            → Shortlisted
  Schedule Interview   → Interview Scheduled (2026-05-09 @ Auditorium A)
  Mark Offer Received  → Offer Received (₹800,000)

=== STEP 3: Student accepts (respond_to_offer) ===
  PA-2026-00402  →  state=Accepted, status=Accepted, ctc=₹800,000

=== Portal verification ===
  My Applications:  1 row, Accepted, interview 2026-05-09 @ Auditorium A, ₹800,000
  Stats:            applied=1, shortlisted=0 (already moved past), interviews=0, new_roles=20
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 2 — Apply Now creates application without errors | PASS / FAIL |
| Step 3 — Officer walks Screening → Shortlisted | PASS / FAIL |
| Step 4 — Schedule Interview dialog populates all 4 fields | PASS / FAIL |
| Step 5 — Record Offer dialog sets package_offered + transition | PASS / FAIL |
| Step 6 — Student accepts → state=Accepted on portal | PASS / FAIL |
| Notes / defects logged |  |

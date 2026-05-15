# Journey 05 — Hostel

**End-to-end hostel flow:** the registrar/admin opens a Student record on the desk → clicks **Create → Allot Hostel Room** → picks a room with available beds → the system creates a `Hostel Allocation` in `Pending Warden Approval` → warden approves on the Hostel Allocation form → student sees their room (building, room number, bed, dates) on the portal Hostel tab → student raises a maintenance request from the portal → warden / hostel staff sees it on the desk and resolves it.

Uses the demo student created in Journey 01 (`zopevedant1@gmail.com` / `demo@1234`).

**No custom portal page for staff.** Allotment + approval + maintenance triage all happen on standard ERPNext desk forms, with two desk-side action buttons added by the university app.

---

## Test site

| | |
|---|---|
| Allot hostel (Student form) | https://ems.hanumatrix.com/app/student/EDU-STU-2026-01602 |
| Hostel Allocation list | https://ems.hanumatrix.com/app/hostel-allocation |
| Maintenance Request list | https://ems.hanumatrix.com/app/hostel-maintenance-request |
| Student portal — Hostel tab | https://ems.hanumatrix.com/student_portal → **Hostel** |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Admin` / `University Registrar` (allotment) | any user with role | 1 – 2 |
| `University Warden` (approval, maintenance triage) | any user with role | 3, 7 |
| `University Student` | `zopevedant1@gmail.com` | 4, 5, 6 |

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert stu, "Run Journey 01 first"

# Hostel masters
assert frappe.db.count("Hostel Building") > 0, "No Hostel Buildings seeded"
assert frappe.db.count("Hostel Room") > 0, "No Hostel Rooms seeded"

# Workflow
wf = frappe.db.get_value("Workflow", {"document_type": "Hostel Allocation", "is_active": 1}, "name")
assert wf, "Hostel Allocation workflow not active"
print(f"Ready: {stu}, workflow={wf}")
```

> The seed already created a `Hostel Allocation` for the demo student (`HA-2026-00878`, room `PGB-401`). To re-run the allotment journey from scratch, see the cleanup section at the bottom of this doc.

---

## Step-by-step UAT script

### Step 1 — Admin opens the Student record on desk

**As:** `University Admin` (or Administrator for UAT)
**Where:** https://ems.hanumatrix.com/app/student → list view → click `EDU-STU-2026-01602`

**Expected:** the Student form opens. Top-right **Create** dropdown now shows two custom actions:
- **Issue Hall Ticket** (added in Journey 04)
- **Allot Hostel Room** (added in this journey)

### Step 2 — Allot a room

Click **Create → Allot Hostel Room**. The dialog:

1. Loads via `list_available_rooms` — only shows rooms where `available_beds > 0`
2. Dropdown lists each room as: **`<room_name> | <building name> · floor X · <type> · beds avail/cap`**

Pick a room (e.g. `KCH-101 | Kalpana Chawla Hall · floor 1 · Double · beds 2/2`).
- **From Date**: defaults to today
- **To Date**: defaults to today + 12 months

Click **Allot Room**.

**Expected:**
- Toast: _"Allocation HA-XXXX-XXXXX created (room KCH-101). Awaiting warden approval."_
- Browser auto-navigates to the new `Hostel Allocation` form
- Workflow state pill: **Pending Warden Approval**, docstatus = 0

### Step 3 — Warden approves

**As:** `University Warden` (or Administrator for UAT)
**Where:** https://ems.hanumatrix.com/app/hostel-allocation — list view filtered by `workflow_state = Pending Warden Approval`

Open the new allocation, click **Approve** in the workflow action dropdown.

**Expected:**
- State pill becomes **Approved**, docstatus = **1 (Submitted)**
- The Hostel Room's `occupied_beds` increases by 1 (Frappe's controller does this); `status` flips to `Occupied` if fully booked.

### Step 4 — Student sees their hostel info on the portal

**As:** `zopevedant1@gmail.com` / `demo@1234`
**Where:** https://ems.hanumatrix.com/student_portal → **Hostel** tab

**Expected:**

| Card | Shows |
|---|---|
| Allocation | Building name, room number (`401`), bed `1`, from / to dates, status `Active` |
| Room | Type `Double`, floor, capacity, occupancy |
| Building | Building name (e.g. `PG Block`), warden, contact number (when populated) |
| Mess Menu | Next 7 days of menus (if seeded) |

### Step 5 — Student raises a maintenance request

**As:** `zopevedant1@gmail.com`
**Where:** Hostel tab → **Submit Maintenance Request** button

Fill the form:

| Field | Value |
|---|---|
| Subject | `Leaking tap in washroom` |
| Description | `The cold-water tap drips continuously. Needs replacement washer.` |
| Priority | `Medium` |
| Request Type | `Plumbing` (must be one of: Electrical / Plumbing / Furniture / Cleaning / AC / Internet / Other) |

Click **Submit**.

**Expected:**
- Toast: _"Maintenance request submitted successfully"_
- The form re-fetches and the maintenance requests panel now shows the new row (e.g. `MR-XXXX-XXXXX`, status `Open`, priority `Medium`).

### Step 6 — Student sees their request status

The Maintenance Requests panel on the same Hostel tab lists the entry with status pill `Open`. Once the warden updates it (Step 7), the panel refresh shows the new state.

### Step 7 — Warden triages the maintenance request

**As:** `University Warden` (or Administrator for UAT)
**Where:** https://ems.hanumatrix.com/app/hostel-maintenance-request — list view filtered by `status = Open`

Open the request:

1. Set **Assigned To** to a maintenance employee
2. Set **Expected Completion** date
3. Click **Save** — `status` automatically becomes `In Progress`
4. After the work is done, set **Status = Completed**, fill **Resolution Remarks**, **Cost Incurred**
5. Click **Save**

**Expected:** status flips to `Completed`. Refresh the student portal — the maintenance row now shows `Completed`.

---

## What the system creates / updates when the admin clicks "Allot Hostel Room"

| Step | Artefact | DocType | Created by |
|---|---|---|---|
| Allot Room | Draft Hostel Allocation pre-filled with student + room + dates | `Hostel Allocation` | `allot_room` API |
| Allot Room | Workflow state set directly to `Pending Warden Approval` | — | `db_set("workflow_state", ...)` |
| Warden Approve | docstatus becomes 1; allocation goes Active | — | Standard workflow engine |
| Warden Approve | `Hostel Room.occupied_beds += 1` and `available_beds -= 1` | `Hostel Room` | Hostel Allocation `on_submit` (existing controller) |
| Maintenance Submit | New `Hostel Maintenance Request` (status `Open`) | `Hostel Maintenance Request` | `submit_maintenance_request` API |

All driven by:
- [`university_hostel/doctype/hostel_allocation/hostel_allocation_actions.py`](../../frappe-bench/apps/university_erp/university_erp/university_hostel/doctype/hostel_allocation/hostel_allocation_actions.py) (allotment APIs)
- [`university_portals/api/portal_api.py`](../../frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py) (`get_student_hostel`, `submit_maintenance_request`)
- [`public/js/student_exam_actions.js`](../../frappe-bench/apps/university_erp/university_erp/public/js/student_exam_actions.js) (Allot Hostel Room button)

---

## Public APIs

| Method | Purpose | Permission |
|---|---|---|
| `university_erp.university_hostel.doctype.hostel_allocation.hostel_allocation_actions.list_available_rooms` | List rooms with `available_beds > 0` | `University Admin/Warden/Registrar/System Manager/Administrator` |
| `university_erp.university_hostel.doctype.hostel_allocation.hostel_allocation_actions.allot_room` | Create + push to Pending Warden Approval | Same |
| `university_erp.university_portals.api.portal_api.get_student_hostel` | Allocation + room + building + attendance + maintenance | Logged-in student |
| `university_erp.university_portals.api.portal_api.submit_maintenance_request` | File a maintenance request from the portal | Logged-in student |

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Allot Hostel Room button missing** | Caller doesn't have `University Admin/Warden/Registrar/System Manager/Administrator` | `bench --site ems.hanumatrix.com console`: `frappe.get_doc("User", "you@nit.edu").add_roles("University Admin")`. Hard-refresh form. |
| **No rooms with available beds** | All rooms are full or `available_beds` is stale | Run a script to recompute: `for r in frappe.db.get_all("Hostel Room"): doc = frappe.get_doc("Hostel Room", r.name); occupied = frappe.db.count("Hostel Allocation", {"room": r.name, "docstatus": 1, "status": "Active"}); doc.db_set("occupied_beds", occupied); doc.db_set("available_beds", (doc.capacity or 0) - occupied)`. |
| **`Student already has an active allocation`** | Student is already allotted | Cancel the existing allocation first (or use the cleanup script below). |
| **`Room X does not belong to building Y`** when student submits maintenance | The student's allocation has stale `hostel_building` (seed bug — value doesn't match the room's actual building) | Already patched — `submit_maintenance_request` derives `building` from the room itself. If you still see this, run `frappe.db.set_value("Hostel Allocation", "<HA name>", "hostel_building", frappe.db.get_value("Hostel Room", "<room>", "hostel_building"))`. |
| **`Request Type cannot be "X"`** on maintenance submit | The Vue form sent an invalid Select option | Allowed types: `Electrical`, `Plumbing`, `Furniture`, `Cleaning`, `AC`, `Internet`, `Other`. Default in API is `Other`. |
| **Approve workflow throws "Illegal Document Status"** | Approved state mapped to wrong doc_status | Should be: Draft=0, Pending Warden Approval=0, Approved=1, Rejected=0, Cancelled=2. Patched in `setup/create_workflows.py`. |
| **Allocation created but bed count not updated** | `Hostel Room.occupied_beds` controller hook didn't fire | Confirm allocation reached docstatus=1 (was actually approved, not just saved). The bed counter updates in `on_submit`. |
| **Portal Hostel tab shows "Loading hostel data..." forever** | API call failed silently — open browser DevTools → Network → look for 500 on `get_student_hostel` | Most often a missing field on `Hostel Building` (e.g. `warden`, `contact_number`). Check `frappe.log_error()`. |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")

# Cancel + delete allocations
for ha in frappe.db.get_all("Hostel Allocation", filters={"student": stu}, fields=["name", "docstatus", "room"]):
    if ha.docstatus == 1:
        try: frappe.get_doc("Hostel Allocation", ha.name).cancel()
        except Exception: pass
    frappe.delete_doc("Hostel Allocation", ha.name, force=True)
    # Recompute room occupancy
    if ha.room:
        rdoc = frappe.get_doc("Hostel Room", ha.room)
        occupied = frappe.db.count("Hostel Allocation", {"room": ha.room, "docstatus": 1, "status": "Active"})
        rdoc.db_set("occupied_beds", occupied)
        rdoc.db_set("available_beds", (rdoc.capacity or 0) - occupied)

# Cancel + delete maintenance requests
for mr in frappe.db.get_all("Hostel Maintenance Request", filters={"requested_by": stu}, fields=["name", "docstatus"]):
    if mr.docstatus == 1:
        try: frappe.get_doc("Hostel Maintenance Request", mr.name).cancel()
        except Exception: pass
    frappe.delete_doc("Hostel Maintenance Request", mr.name, force=True)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: Admin lists available rooms ===
  50 rooms with available beds (e.g. KCH-101 / Kalpana Chawla Hall / 2 of 2 beds free)

=== STEP 2: Allot KCH-101 to EDU-STU-2026-01402 ===
  Created HA-2026-00879
    student=EDU-STU-2026-01402, room=KCH-101, building=KCH
    from=2026-05-04, to=2027-05-04
    workflow_state=Pending Warden Approval

=== STEP 3: Warden Approves ===
  state=Approved, docstatus=1

=== STEP 5: Demo student raises a maintenance request ===
  Submitted MR-2026-04938: "UAT — leaking tap in washroom" (Open, Medium)

=== Portal verification (as zopevedant1@gmail.com) ===
  Hostel allocation: HA-2026-00878 — Room PGB-401 (PG Block), bed 1, Active 2026-05-03 → 2027-05-04
  Maintenance requests visible: 1 (MR-2026-04938)
  Mess menus visible: 2
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1-2 — Allot Room button creates draft allocation | PASS / FAIL |
| Step 3 — Warden Approve flips to Approved + bed count | PASS / FAIL |
| Step 4 — portal Hostel tab shows allocation + room + building | PASS / FAIL |
| Step 5-6 — student submits maintenance request, sees it on portal | PASS / FAIL |
| Step 7 — warden triages on desk, student sees status update | PASS / FAIL |
| Notes / defects logged |  |

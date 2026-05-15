# Journey 07 — Transport

**End-to-end transport flow:** the admin opens the Student record on the desk → clicks **Create → Allot Transport Route** → picks a route from the list of active routes → the system creates a draft `Transport Allocation` and pushes it to **Pending Approval** → the registrar approves → the student sees their assigned route, pickup/drop stops, vehicle, and full timetable on the portal Transport tab.

Uses the demo student created in Journey 01 (`zopevedant1@gmail.com` / `demo@1234`).

**No custom portal page for staff.** Allotment + approval all happen on the standard ERPNext desk via a button added by the university app.

---

## Test site

| | |
|---|---|
| Allot transport (Student form) | https://ems.hanumatrix.com/app/student/EDU-STU-2026-01602 |
| Transport Allocation list | https://ems.hanumatrix.com/app/transport-allocation |
| Transport Route list | https://ems.hanumatrix.com/app/transport-route |
| Student portal — Transport tab | https://ems.hanumatrix.com/student_portal → **Transport** |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Admin` / `University Transport` (allotment) | any user with role | 1 – 2 |
| `University Registrar` (approval) | any user with role | 3 |
| `University Student` | `zopevedant1@gmail.com` | 4 |

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert stu, "Run Journey 01 first"

# Transport masters
active_routes = frappe.db.count("Transport Route", {"is_active": 1})
assert active_routes > 0, "No active Transport Routes seeded"

# Workflow
wf = frappe.db.get_value("Workflow", {"document_type": "Transport Allocation", "is_active": 1}, "name")
assert wf, "Transport Allocation workflow not active"
print(f"Ready: {stu}, {active_routes} routes")
```

---

## Step-by-step UAT script

### Step 1 — Admin opens the Student record on desk

**As:** any user with `University Admin` / `University Transport` role
**Where:** https://ems.hanumatrix.com/app/student → list view → click `EDU-STU-2026-01602`

**Expected:** Student form with three custom actions in the **Create** dropdown:
- Issue Hall Ticket (Journey 04)
- Allot Hostel Room (Journey 05)
- **Allot Transport Route** (this journey)

### Step 2 — Allot a route

Click **Create → Allot Transport Route**. The dialog:

1. Loads via `list_active_routes` — shows all routes with `is_active=1`
2. Dropdown lists each route as: **`<route_name> | <start> → <end> · ₹<fare>/mo · vehicle <number>`**

Pick a route (e.g. `Route A - City Center | City Center → NIT Campus · ₹0/mo · vehicle TBD`).

| Field | Value |
|---|---|
| Pickup Stop | `Pune Main Bus Stop` (optional) |
| Drop Stop | `Campus Gate` (optional) |
| From Date | today (default) |
| To Date | today + 12 months (default) |

Click **Allot Route**.

**Expected:**
- Toast: _"Allocation TA-XXXX-XXXXX created (route Route A - City Center). Awaiting registrar approval."_
- Browser auto-navigates to the new `Transport Allocation` form
- Workflow state pill: **Pending Approval**, docstatus = 0
- Vehicle, monthly_fare, pickup_time, drop_time auto-filled from the route master

### Step 3 — Registrar approves

**As:** `University Registrar` (or Administrator for UAT)
**Where:** https://ems.hanumatrix.com/app/transport-allocation — list filtered by `workflow_state = Pending Approval`

Open the new allocation, click **Approve**.

**Expected:**
- State pill: **Active**, docstatus = **1 (Submitted)**
- The Transport Allocation is now visible to the student on the portal

### Step 4 — Student sees the allocation

**As:** `zopevedant1@gmail.com` / `demo@1234`
**Where:** https://ems.hanumatrix.com/student_portal → **Transport** tab

**Expected:**

| Section | Shows |
|---|---|
| Allocation | Route name, pickup stop, drop stop, from/to dates, monthly fare |
| Route Details | Start point, end point, total distance, departure/arrival times |
| Stops | Ordered list of all stops on the route with pickup + drop times |
| Vehicle | Vehicle number, type, capacity, driver name + contact (if route has `assigned_vehicle`) |

---

## What the system creates / updates

| Step | Artefact | DocType | Created by |
|---|---|---|---|
| Allot Route | Draft Transport Allocation pre-filled with student + route + auto-filled fare/vehicle/times | `Transport Allocation` | `allot_transport` API |
| Allot Route | Workflow state set directly to `Pending Approval` | — | `db_set` |
| Registrar Approve | docstatus → 1; allocation `Active` | — | Standard workflow engine |

All driven by [`university_transport/doctype/transport_allocation/transport_allocation_actions.py`](../../frappe-bench/apps/university_erp/university_erp/university_transport/doctype/transport_allocation/transport_allocation_actions.py).

---

## Public APIs

| Method | Purpose | Permission |
|---|---|---|
| `university_erp.university_transport.doctype.transport_allocation.transport_allocation_actions.list_active_routes` | All active Transport Routes with vehicle/fare/times | Logged-in staff |
| `university_erp.university_transport.doctype.transport_allocation.transport_allocation_actions.list_route_stops` | Ordered stops on a route | Logged-in staff |
| `university_erp.university_transport.doctype.transport_allocation.transport_allocation_actions.allot_transport` | Create allocation + push to Pending Approval | `University Admin/Registrar/Transport/SysMgr/Admin` |
| `university_erp.university_portals.api.portal_api.get_student_transport` | Student's allocation + route + stops + vehicle | Logged-in student |

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Allot Transport Route button missing** | Caller doesn't have the right role | Add `University Admin` (or `University Transport`) role: `frappe.get_doc("User", "you@nit.edu").add_roles("University Admin")`. Hard-refresh form. |
| **No active transport routes** | Routes seeded but `is_active=0` | Open `/app/transport-route`, set `is_active=1`. Or seed via `bench --site … execute …`. |
| **`Student already has an active transport allocation`** | One active allocation per student | Cancel the existing one first, or use the cleanup script below. |
| **Allocation created but vehicle is `null`** | The Transport Route has no `assigned_vehicle` | Open the route master and set `assigned_vehicle`. Or the registrar can set it directly on the allocation form before approving. |
| **`Route X is not active`** on allotment | `is_active=0` on the route | Reactivate the route first. |
| **Approve workflow throws "Illegal Document Status"** | Active state mapped to wrong doc_status | Should be: Draft=0, Pending Approval=0, Active=1, Rejected=0, Cancelled=2. Patched in `setup/create_workflows.py`. |
| **Portal Transport tab shows "Loading…" forever** | API errored — open DevTools → Network → look for 500 on `get_student_transport` | Check `frappe.log_error()`. Most often a missing field on Transport Vehicle (e.g. `driver_contact`). |
| **List Transport Allocation throws `Unknown column 'workflow_state'`** | Column wasn't added to the table | Already patched (`ALTER TABLE \`tabTransport Allocation\` ADD COLUMN workflow_state varchar(140)`). |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")

for ta in frappe.db.get_all("Transport Allocation", filters={"student": stu}, fields=["name", "docstatus"]):
    if ta.docstatus == 1:
        try: frappe.get_doc("Transport Allocation", ta.name).cancel()
        except Exception: pass
    frappe.delete_doc("Transport Allocation", ta.name, force=True)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: 5 active routes ===
  - Route A - City Center: City Center → NIT Campus (₹0/mo, 5 stops)
  - Route B - Railway Station: Railway Station → NIT Campus
  - Route C - Airport Road: Airport → NIT Campus
  - Route D - Old City: Old City → NIT Campus
  - Route E - Industrial Area: Industrial Area → NIT Campus

=== STEP 2: Stops on Route A ===
  06:30 City Center Bus Stand → 06:45 Railway Station → 07:00 Market Square →
  07:15 Hospital Road → 07:45 NIT Main Gate

=== STEP 3: Allot Route A to EDU-STU-2026-01602 ===
  Created TA-2026-00841 (Pending Approval)

=== STEP 4: Registrar Approves ===
  state=Active, docstatus=1

=== STEP 5: Portal verification ===
  allocation.route:        Route A - City Center
  allocation.from_date:    2026-05-04, to_date: 2027-05-04
  allocation.pickup_stop:  Pune Main Bus Stop
  allocation.drop_stop:    Campus Gate
  route.total_distance:    15.0 km
  stops:                   5 (with pickup + drop times)
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1-2 — Allot Route button creates draft allocation | PASS / FAIL |
| Step 3 — Registrar Approve flips to Active | PASS / FAIL |
| Step 4 — portal Transport tab shows route + stops + vehicle | PASS / FAIL |
| Notes / defects logged |  |

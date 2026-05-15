# Demo 10 — Inventory Module

Walkthrough of the **Inventory** module on `ems.hanumatrix.com`. Designed for a 15-minute live demo to a non-developer audience. Every record ID and row count below was audited live on prod (2026-05-04) — nothing in this doc is hypothetical.

**No application changes.** Everything documented here works against the existing wiring + seeded data. Where the system has a real-world gap (re-examination / backlog handling), it's called out explicitly under the "What the system does NOT handle today" section so the audience isn't misled.

---

## At a glance — what's wired on prod

| Doctype | Rows | Walkable? |
|---|---|---|
| `Inventory Item` | 450 | ✅ |
| `Inventory Item Group` | 5 | ✅ |
| `Asset` | 30 | ✅ |
| `Asset Category` | 6 | ✅ |
| `Asset Movement` | 15 | ✅ |
| `Asset Maintenance` | 8 | ✅ |
| `Maintenance Team` | 2 | ✅ |
| `Lab Equipment` | 20 | ✅ |
| `Lab Equipment Booking` | 105 (all Pending) | ✅ — workflow walk live |
| `Lab Consumable Issue` | 64 | ✅ |
| `Material Request` | 0 | ⚠️ create fresh during demo |
| `Purchase Order` | 0 | ⚠️ create fresh during demo |
| `Purchase Receipt` | 0 | ⚠️ optional during demo |
| `Stock Entry` | 0 | ⚠️ optional |
| `Stock Reconciliation` | 5 | ✅ |
| `Stock Ledger Entry` | 300 | ✅ — backs Stock Balance / Stock Ledger reports |
| `Supplier` | 8 | ✅ |
| `Supplier Group` | 3 | ✅ |
| `Warehouse` | 5 | ✅ |

**Active workflows:**
- **Material Request Approval** (`University Admin` → `University HOD`)
- **Purchase Order Approval** (`University Admin` → `University HOD` → `University Finance`)
- **Lab Equipment Booking** (`University Admin` / `University Registrar`)

---

## Test site & actors

| | |
|---|---|
| Site | https://ems.hanumatrix.com |
| Demo actors | `University Admin` (initiator) · `University HOD` (mid-approval) · `University Finance` (final approval) · `University Registrar` (lab bookings) |
| Pre-cooked records | `AST-2026-00510` (3D Printer CS Lab, ₹220,000) · `EQ-DSO-001` (Digital Storage Oscilloscope) · `SUP-2026-00008` (Reliance Books) |

---

## Pre-flight check (30 seconds)

```python
# bench --site ems.hanumatrix.com console
import frappe
print(frappe.db.count("Inventory Item"))               # → 450
print(frappe.db.count("Asset"))                        # →  30
print(frappe.db.count("Lab Equipment Booking"))        # → 105
print(frappe.db.count("Stock Ledger Entry"))           # → 300
print(frappe.db.count("Supplier"))                     # →   8
```

---

## Demo flow A — Walk a Lab Equipment Booking

**Why:** the simplest workflow in the module — one click per state, no upstream dependencies. Good warm-up for the audience.

1. **As `University Registrar`** (or Admin), open https://ems.hanumatrix.com/app/lab-equipment-booking
2. List shows **105 bookings**, all in **Pending** state. Pick any row tied to `EQ-DSO-001` or similar.
3. Workflow walk:
   - Pending → click **Approve** → state becomes **Approved**
   - Approved → click **Start Use** → state becomes **In Use**
   - In Use → click **Complete** → state becomes **Completed**
4. The Lab Equipment master's `current_status` and `last_used` fields update automatically.

**Side branch to mention:** any state can transition to **Cancelled** via the Cancel action.

> **Tip:** if the audience asks how a student requests a booking, point at the back-end Lab Equipment Booking form for now. Student-portal lab booking is a Phase-2 feature.

---

## Demo flow B — Browse the 30 Assets

**Why:** shows the system's grasp on capital expenditure — gross value, depreciation, location, maintenance.

1. Open https://ems.hanumatrix.com/app/asset → list of 30 assets.
2. Filter by `Asset Category` — there are 6 (Computers, Lab Equipment, Furniture, Vehicles, Buildings, Network Equipment).
3. Open `AST-2026-00510` "3D Printer CS Lab":
   - **Gross Purchase Amount**: ₹220,000
   - **Status**: In Use
   - **Asset Category**: Computers
   - **Cost Center**: linked to Finance
4. Show child tables:
   - **Asset Movements** — 15 rows site-wide; this asset's row shows where it was issued
   - **Maintenance Activities** — links to `Asset Maintenance` (8 rows site-wide, planned + completed)
5. Click into the linked **Asset Maintenance** doc to show planned-vs-actual maintenance dates and which `Maintenance Team` (one of 2 — Lab Maintenance / IT Support) is responsible.

---

## Demo flow C — Inventory Items + Stock Ledger

**Why:** shows live stock tracking + the audit trail needed for procurement reports.

1. Open https://ems.hanumatrix.com/app/inventory-item → 450 items across 5 groups (Lab Equipment, Office Stationery, IT Hardware, Furniture, Consumables).
2. Filter by `Inventory Item Group = Consumables` — show 10s of items like solder wire, lab gloves, printer toner.
3. Open the Stock Ledger report at https://ems.hanumatrix.com/app/query-report/Stock%20Ledger
   - Filter `Warehouse = Finished Goods` → see balance per item
   - Show how each ledger row points back to a `Stock Entry` / `Purchase Receipt` / `Stock Reconciliation`
4. Open https://ems.hanumatrix.com/app/query-report/Stock%20Balance → snapshot quantities per item per warehouse.

---

## Demo flow D — Live Material Request → Purchase Order chain

**Why:** demonstrates the **3-stage approval workflow** real procurement teams need (Admin raises → HOD approves → Finance approves). Since `Material Request` and `Purchase Order` are empty on prod, this is the part where the demo creates fresh records — a deliberate showcase.

### Step 1 — Admin raises a Material Request

**As `University Admin`**: https://ems.hanumatrix.com/app/material-request/new

| Field | Value |
|---|---|
| Material Request Type | `Purchase` |
| Required By | today + 14 days |
| **Items** child table | Add a row — Item: `INV-2026-01200` (Soldering Wire 500g, or any seeded item) — Qty: `5` |
| Warehouse | `Finished Goods` |

**Save** → state pill: **Draft**.

Click **Submit for HOD Approval** → state: **Pending HOD Approval**, docstatus = 0.

### Step 2 — HOD approves

**As `University HOD`**: open the same MR → workflow action **Approve** → state: **Approved**, docstatus = 1.

### Step 3 — Admin creates Purchase Order from the MR

Still on the Approved MR form, top-right **Create → Purchase Order**. ERPNext copies the items + qty automatically.

| Field | Value |
|---|---|
| Supplier | `SUP-2026-00008` (Reliance Books) — or any of the 8 seeded suppliers |
| Schedule Date | today + 7 days |

**Save** → workflow state: **Draft**.

Walk the workflow:
- **Submit for HOD Approval** → **Pending HOD Approval**
- (As HOD) **Approve** → **Pending Finance Approval**
- (As Finance) **Approve** → **Approved**, docstatus = 1

### Step 4 (optional) — receive the goods

From the Approved PO, top-right **Create → Purchase Receipt**. Submit it. This generates **Stock Ledger Entries** that update `Inventory Item.stock_qty` per warehouse.

> **Branch to mention:** PO has a **Send Back to HOD** transition from `Pending Finance Approval` for when Finance wants HOD to revisit the request before approving.

---

## Demo flow E — Reports tour (90 seconds)

| Report | What it shows | URL |
|---|---|---|
| **Asset Register** | All 30 assets with depreciated value | `/app/query-report/Asset Register` |
| **Lab Equipment Utilization** | Booking-hours per equipment per term | `/app/query-report/Lab Equipment Utilization` |
| **Stock Balance** | Per-item / per-warehouse on-hand | `/app/query-report/Stock Balance` |
| **Stock Ledger** | Every stock movement | `/app/query-report/Stock Ledger` |
| **Low Stock Items** | Items below reorder level | `/app/query-report/Low Stock Items` |
| **Purchase Order Status** | Pending / Approved / Closed POs | `/app/query-report/Purchase Order Status` |

---

## What the system does NOT handle today — re-examinations / backlogs

When a student fails a course (Assessment Result `grade = F`), there is no way today to re-take just that course. The current Hall Ticket flow (Journey 04) re-issues all 7 enrolled courses for whatever term the student is in.

**Concrete example:** Vedant is in Sem 2 with 7 courses. He fails 2 (Operating Systems, DBMS). Per a real university's policy he should sit a **Supplementary** exam for those 2 courses next semester while taking 5 fresh Sem-3 courses. Today's system would:
- Issue a Sem-3 Hall Ticket for 5 fresh courses ✓
- Have **no concept** of carrying forward the 2 backlogs
- Have **no separate fee** for the Supplementary attempt
- Have **no policy enforcement** (e.g. cap at 3 attempts; block promotion if backlogs > 4)

**What an exam-cell user must do manually today:**

1. Issue a regular Hall Ticket for Sem 3 as usual (Journey 04).
2. Issue a **second Hall Ticket** with **Exam Type = `Supplementary`** for the same student.
3. **Manually edit the Exams child table** to remove all courses except the failed ones — cross-reference the student's `Assessment Result` rows with `grade = F`.
4. Track attempts in the `Remarks` field of the Hall Ticket.
5. Bill the supplementary exam fee via a manual `Fees` doc tagged `Supplementary` — there's no auto-fee.

**Known enhancement (parked, NOT in this UAT):**

| Option | Effort | What it gives |
|---|---|---|
| **A** | ~30 min | When `exam_type = Supplementary`, the desk-side **Issue Hall Ticket** button (Journey 04) reads `Assessment Result` for the student and only adds courses where `grade = F` (or score < 40). Same Journey 04 flow otherwise. **Recommended for Phase 2.** |
| **B** | ~2-3 hours | New `Student Backlog` doctype — auto-creates a row when `Assessment Result.on_submit` posts a fail. Tracks attempt count, max-attempts policy, separate fee per re-exam. Workflow Pending → Registered → Cleared / Failed Again. Portal panel for the student. Hall Ticket pulls from the Backlog doctype. |
| **C** | ~1 hour | Use the existing `Practical Examination` doctype as a template — clone its workflow, add a `failed_courses` child table. Less polished than B, more polished than A. |

---

## Common breaks (already known + patched)

| Symptom | Status |
|---|---|
| `Unknown column 'workflow_state' in 'SELECT'` on Lab Equipment Booking / MR / PO list | ✅ Fixed — columns added in earlier session |
| Lab Equipment Booking workflow can't reach `In Use` | ✅ Wiring verified; states work top-down Pending → Approved → In Use → Completed |
| **`Sum of Scores of Assessment Criteria needs to be 100`** on Hall Ticket Enter Results | ✅ Fixed (Journey 04) — auto-creates Assessment Plan with matching criterion total |
| Hostel Maintenance Request "Building does not match Room" on save | ✅ Fixed — `building` is now derived from the room itself |

---

## Sign-off block

| Field | Value |
|---|---|
| Demo presenter |  |
| Demo date |  |
| Audience size |  |
| Flow A (Lab Equipment Booking workflow) | PASS / FAIL |
| Flow B (Asset browsing) | PASS / FAIL |
| Flow C (Inventory + Stock Ledger) | PASS / FAIL |
| Flow D (MR → PO live walk) | PASS / FAIL |
| Flow E (reports tour) | PASS / FAIL |
| Backlog/re-exam gap explained | YES / NO |
| Questions raised |  |
| Action items |  |

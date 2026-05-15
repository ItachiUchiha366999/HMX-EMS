# Demo 09 — Finance Module

Walkthrough of the **Finance** module on `ems.hanumatrix.com`. Designed for a 15-minute live demo to a non-developer audience. Every record ID and row count below was audited live on prod (2026-05-04) — nothing in this doc is hypothetical.

**No application changes.** Everything documented here works against the existing wiring + seeded data. Where the system has a real-world gap (govt-funded scholarship reversal), it's called out explicitly under the "What the system does NOT handle today" section so the audience isn't misled.

---

## At a glance — what's wired on prod

| Doctype | Rows | Walkable? |
|---|---|---|
| `Fees` | 203 | ✅ |
| `Sales Invoice` | 203 | ✅ |
| `Payment Entry` | 134 (already submitted from seed; workflow walk needs a fresh PE) | ✅ via fresh PE |
| `Fee Refund` | 3 (all Pending) | ✅ — workflow walk live |
| `Journal Entry` | 0 | ⚠️ create fresh during demo |
| `GL Entry` | 1,122 | ✅ — backs every report |
| `Account` | 96 | ✅ |
| `Cost Center` | 2 | ✅ |
| `Mode of Payment` | 5 (Cash / Bank Transfer / Cheque / UPI / Credit Card) | ✅ |
| `Fee Structure` / `Fee Category` | 5 / 5 | ✅ |

**Active workflows:**
- **Fee Refund Approval** (`University Finance`)
- **Payment Entry Approval** (`University Finance`)
- **Journal Entry Approval** (`University Finance`)

---

## Test site & actor

| | |
|---|---|
| Site | https://ems.hanumatrix.com |
| Demo actor | any user with **`University Finance`** role (or Administrator) |
| Pre-cooked records to anchor the walk | `EDU-FEE-2026-01404` (demo student's fee, ₹50,000) · `RFD-2026-00006` (Pending refund) · `ACC-PAY-2026-00825/26` (Approved PEs) |
| Demo student | `zopevedant1@gmail.com` / `demo@1234` (Vedant Ganesh Zope) — same student used in journeys 01-08 |

---

## Pre-flight check (30 seconds)

```python
# bench --site ems.hanumatrix.com console
import frappe
print(frappe.db.count("Fees"))                    # → 203
print(frappe.db.count("Payment Entry"))           # → 134
print(frappe.db.count("Fee Refund"))              # →   3
print(frappe.db.count("GL Entry"))                # → 1,122
```

If any number is materially below the above, the seed has drifted — re-run `bench execute university_erp.setup.seed_demo_v2.seed_all` first.

---

## Demo flow A — Record an offline fee payment

**Why:** the most common Finance interaction — student pays cash/UPI at the counter, cashier records it.

1. **As `University Finance`**, open https://ems.hanumatrix.com/app/fees
2. Filter the list by **Outstanding > 0** — picks any student with money owed (e.g. `EDU-FEE-2026-01404` for the demo student, ₹50,000 outstanding)
3. Open the row → on the form, top-right **Create → Record Offline Payment** (custom button shipped in Journey 03)
4. Dialog opens, pre-filled with the outstanding amount. Edit:
   - **Amount**: `20000` (partial)
   - **Mode of Payment**: `Cash`
   - **Reference #**: `DEMO-CASH-001`
5. Click **Record Payment**

**What just happened:**
- Toast: _"Payment ACC-PAY-XXXX-XXXXX recorded (₹20,000.00). Remaining: ₹30,000.00"_
- A **submitted Payment Entry** is created and linked to the Fees doc
- `Outstanding Amount` on the form drops to ₹30,000
- GL Entries are auto-generated (debit Cash, credit Receivable) — visible at `/app/gl-entry?voucher_no=ACC-PAY-XXXX-XXXXX`

Repeat with **Mode of Payment = UPI** and the remaining ₹30,000 to fully close the fee. The button hides itself once `outstanding_amount = 0`.

**Audience-visible side effect:** the student logs into the portal → Fees tab → sees both payments in Payment History with downloadable PDF receipts.

> _Detailed end-to-end walk:_ see [`03-fees-journey.md`](03-fees-journey.md).

---

## Demo flow B — Walk a Fee Refund through approval

**Why:** demonstrates the multi-stage approval workflow (every Finance team needs this).

> **Demo subject:** `RFD-2026-00007` — a refund for the demo student **Vedant Ganesh Zope** (`EDU-STU-2026-01602`). Story: he dropped one elective in week 3, the registrar issued a pro-rata refund of ₹8,500 with ₹1,500 admin deduction → net ₹7,000.
>
> The 3 originally-seeded Fee Refunds (`RFD-2026-00004/5/6`) carry a seed-data drift bug: their `docstatus=1` doesn't match `workflow_state=Pending`, so clicking **Submit for Approval** on them throws _"Illegal Document Status for Pending Approval"_. **Use `RFD-2026-00007` instead** — it's clean and walks the full path.

1. Open https://ems.hanumatrix.com/app/fee-refund/RFD-2026-00007
2. Confirm: workflow state pill **Pending**, docstatus = 0, refund_amount ₹8,500, net_refund ₹7,000
3. Click **Submit for Approval** in the workflow action dropdown → state becomes **Pending Approval**, email alert fires to all `University Finance` users
4. Click **Approve** → state becomes **Approved** (still docstatus=0 — money hasn't moved yet)
5. Confirm **Payment Mode = Bank Transfer** (already pre-filled). Optionally add a Reference Number.
6. Click **Process Refund** → state becomes **Processed**, docstatus = **1 (Submitted)**

**Branches to mention without walking** (so the audience knows they exist):
- **Reject** from Pending Approval → state **Rejected**
- **Return to Draft** → goes back to **Pending** for edits
- **Reconsider** from Rejected → re-opens it for a second look
- **Cancel** from Processed → state **Cancelled** (docstatus=2)

**To re-run the demo (fresh refund row):**

```python
# bench --site ems.hanumatrix.com console — re-creates RFD-2026-00007 in Pending state
import frappe
frappe.db.sql("DELETE FROM `tabFee Refund` WHERE student='EDU-STU-2026-01602'")
now, today = frappe.utils.now(), frappe.utils.nowdate()
frappe.db.sql("""
    INSERT INTO `tabFee Refund`
    (name, creation, modified, modified_by, owner, docstatus, idx,
     student, student_name, fees, fee, program,
     refund_date, refund_reason, reason_details,
     original_amount, paid_amount, refund_amount,
     deduction_amount, deduction_reason, net_refund,
     gross_refund_amount, total_deductions, net_refund_amount,
     payment_mode, status, workflow_state)
    VALUES
    ('RFD-2026-00007', %s, %s, 'Administrator', 'Administrator', 0, 1,
     'EDU-STU-2026-01602', 'Vedant Ganesh Zope',
     'EDU-FEE-2026-01404', 'EDU-FEE-2026-01404',
     'B.Tech Computer Science and Engineering',
     %s, 'Withdrew from one elective course mid-semester',
     'Student dropped Environmental Engineering elective in week 3.',
     50000, 50000, 8500, 1500, 'Administrative processing fee', 7000,
     8500, 1500, 7000, 'Bank Transfer', 'Pending', 'Pending')
""", (now, now, today))
frappe.db.commit()
```

---

## Demo flow C — Approve a Payment Entry (live, fresh PE)

**Why:** Payment Entries created via the cashier flow (Demo A) bypass the workflow because they're already submitted. Payments entered manually by Finance (e.g. supplier payouts, bulk bank settlements) walk the approval workflow.

> **Note about seed data:** the 132 Payment Entries with `workflow_state=Draft` were seeded as **already submitted** (`docstatus=1`) — that means their workflow can't be walked further without a fresh PE. Either skip this flow or create a new one live during the demo.

To demo the workflow live, create a fresh PE:

1. Open https://ems.hanumatrix.com/app/payment-entry/new
2. **Payment Type**: `Pay`
3. **Party Type**: `Supplier` → **Party**: `SUP-2026-00008` (Reliance Books)
4. **Paid Amount**: `5000`
5. **Mode of Payment**: `Bank Transfer`
6. Save → workflow state: **Draft**
7. **Submit for Approval** → **Pending Finance Approval**
8. **Approve** → **Approved**, docstatus = 1
9. Open `/app/gl-entry?voucher_no=...` to show the audit trail.

If you have time, demo the **Reject** branch on another fresh PE to show the negative path.

---

## Demo flow D — Reports tour (90 seconds)

Open each report from the **Awesome Bar** (Ctrl+G) and let the data speak. All numbers are real, backed by the 1,122 GL Entries.

| Report | What it shows | URL |
|---|---|---|
| **Profit and Loss Statement** | Income vs expenses for the fiscal year | `/app/query-report/Profit and Loss Statement` |
| **Trial Balance** | All accounts with debit/credit balances | `/app/query-report/Trial Balance` |
| **Accounts Receivable** | Outstanding fees by student | `/app/query-report/Accounts Receivable` |
| **Fee Collection Summary** | Daily/monthly fee collections | `/app/query-report/Fee Collection Summary` |
| **General Ledger** | Every transaction line | `/app/query-report/General Ledger` |

Each runs in <1 sec on prod and returns non-zero rows.

---

## What the system does NOT handle today — govt-funded scholarships

When a scholarship is funded by the government (Post-Matric SC/ST, NSP, state schemes), the actual approval comes from the funding body **months after** the college has provisionally given the discount. If the govt later rejects the application — typically at year-end — the college has a money problem.

**Current `Student Scholarship` workflow:**

| State | Meaning | docstatus |
|---|---|---|
| Draft | Application captured | 0 |
| Under Verification | College verifying eligibility | 0 |
| Approved | College has internally approved | 1 |
| Rejected | College has internally rejected | 0 |
| Disbursed | Money posted to student ledger | 1 |
| Cancelled | Scholarship voided | 2 |

**The gap:** there is no `Pending Govt Confirmation` state, no `Govt Rejected` state, no field for the govt sanction order number, and no automatic fee-reversal flow.

**What a registrar must do manually today:**

1. **At provisional approval** — record the govt application reference number in the `Remarks` field of `Student Scholarship`. Apply the discount via `Fee Refund` or by reducing the next Sales Invoice manually.
2. **At year-end if govt approves** — no further action; mark `Disbursed` once the money lands.
3. **At year-end if govt rejects** — manually create a fresh Sales Invoice on the student's account for the discount amount, marked `Reversal of provisionally approved scholarship`. Notify the student via the Communication doctype to settle within 30 days. If the student has graduated, escalate to recovery.
4. **At year-end if govt approves a smaller amount** (very common — they fund 60% of what was claimed) — create a delta Sales Invoice for the unfunded portion.

**Known enhancement (parked, NOT in this UAT):**

| Option | Effort | What it gives |
|---|---|---|
| **A** | ~1 hour | Add 6 Custom Fields (`external_body`, `govt_reference_no`, `govt_status`, `expected_confirmation_date`, `actual_confirmation_date`, `confirmed_amount`) + 2 new workflow states (`Pending Govt Confirmation`, `Govt Rejected`) + an aging report. **Manual reversal still required.** |
| **B** | ~3-4 hours | All of A + auto-creates the reversal Sales Invoice when the workflow hits `Govt Rejected` + handles partial confirmations via a delta invoice. |
| **C** | ~1-2 days | All of B + CSV export/import to reconcile against govt portal batch files (NSP works this way). |

For UAT we recommend documenting the manual workflow honestly and parking option A as a Phase-2 enhancement.

---

## Common breaks (already known + patched)

| Symptom | Status |
|---|---|
| `Unknown column 'workflow_state' in 'SELECT'` on Fee Refund / Payment Entry / Journal Entry list | ✅ Fixed — column added in earlier session |
| Demo student's allocation building mismatch (PGB-401 in building RH) | ✅ Fixed |
| **Record Offline Payment** button missing on Fees form | Caller doesn't have `University Finance` / `System Manager` / `Administrator` role. Add the role + hard-refresh. |
| `placement_drive` mandatory error on Placement Application save | ✅ Fixed (made optional) — unrelated but commonly hit during a finance + placement combined demo |

---

## Sign-off block

| Field | Value |
|---|---|
| Demo presenter |  |
| Demo date |  |
| Audience size |  |
| Flow A (record offline payment) | PASS / FAIL |
| Flow B (Fee Refund workflow) | PASS / FAIL |
| Flow C (Payment Entry approval) | PASS / FAIL |
| Flow D (reports tour) | PASS / FAIL |
| Govt-scholarship gap explained | YES / NO |
| Questions raised |  |
| Action items |  |

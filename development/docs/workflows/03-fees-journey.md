# Journey 03 — Fees Payment

**End-to-end fees flow:** the student logs into the portal and sees the outstanding fee created during admission → the cashier opens the **Fees** doc on the standard ERPNext desk → clicks **Create → Record Offline Payment** → fills amount + mode + reference → submits → the system creates a `Payment Entry` linked to the `Fees` doc, reduces outstanding, and the student immediately sees the payment in their portal Payment History plus a downloadable PDF receipt.

**No custom portal page for the cashier.** The action runs from the standard Frappe desk — same form an Accounts Manager would see in any ERPNext install — only the **Record Offline Payment** button is added on top.

This journey **uses the demo student created in Journey 01** (`zopevedant1@gmail.com` / `demo@1234`) and assumes the admission auto-created a Fees doc (`EDU-FEE-XXXX`) for ₹50,000.

---

## Test site

| | |
|---|---|
| Cashier desk (Fees list) | https://ems.hanumatrix.com/app/fees (login required, needs `University Finance` role) |
| Cashier desk (single Fees doc) | https://ems.hanumatrix.com/app/fees/EDU-FEE-XXXX-XXXXX |
| Student fees view | https://ems.hanumatrix.com/student_portal → **Fees** tab |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Student` (Website User — no desk access) | `zopevedant1@gmail.com` | 1, 5 |
| `University Finance` (cashier) | any user with the role (or Administrator for UAT) | 2 – 4 |

> **About online payment.** This journey covers offline / counter payments only. The Razorpay/PayU online flow at `/pay-fees?fees=XXX` exists in the codebase but needs gateway credentials configured under **Razorpay Settings** / **PayU Settings**. For UAT the cashier flow is sufficient and faster.

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert stu, "Run Journey 01 first"

fee = frappe.db.get_value("Fees", {"student": stu, "docstatus": 1}, ["name", "outstanding_amount"], as_dict=True)
assert fee, "No submitted Fees doc — Journey 01 should have created one"
print(f"Ready: {fee.name} owes ₹{fee.outstanding_amount}")

# Modes of payment
modes = frappe.db.get_all("Mode of Payment", fields=["name"])
print(f"Available modes: {[m.name for m in modes]}")
```

---

## Step-by-step UAT script

### Step 1 — Student sees the outstanding fee

**As:** `zopevedant1@gmail.com`
**Where:** https://ems.hanumatrix.com/student_portal → **Fees** tab

**Expected:**
- **Pending Fees** card shows one row: `EDU-FEE-XXXX-XXXXX`, ₹50,000, status **Upcoming**
- **Payment History** is empty
- **Fee Summary**: total ₹50,000 / paid ₹0 / pending ₹50,000

### Step 2 — Cashier opens the Fees list on desk

**As:** any user with `University Finance` role (or Administrator for UAT)
**Where:** https://ems.hanumatrix.com/app/fees

**Expected:**
- Standard ERPNext list view of all `Fees` rows
- In the filter bar add **Status = Unpaid** (or filter on **Outstanding Amount > 0**) to see only fees that owe money
- Locate `EDU-FEE-XXXX-XXXXX` for student `EDU-STU-2026-01602` (Vedant Ganesh Zope) — outstanding ₹50,000
- Click into the doc to open it

### Step 3 — Cashier records a partial payment from the Fees form

**Where:** the Fees form (e.g. `/app/fees/EDU-FEE-2026-01404`)

Click **Create → Record Offline Payment** (top right). The button is added by `university_erp` and only appears when the doc is submitted with outstanding > 0.

A dialog opens, pre-filled with the outstanding amount. Edit:

| Field | Value |
|---|---|
| Amount | `20000` (try a partial amount first) |
| Mode of Payment | `Cash` |
| Reference # | `VZ-CASH-001` |

Click **Record Payment**.

**Expected:**
- Green toast: _"Payment ACC-PAY-XXXX-XXXXX recorded (₹20,000.00). Remaining: ₹30,000.00"_
- The form reloads automatically — `Outstanding Amount` field now shows ₹30,000
- A new submitted Payment Entry exists at `/app/payment-entry/ACC-PAY-XXXX-XXXXX` with the Fees doc in its References table

### Step 4 — Cashier records the remainder

**Where:** still on the same Fees form (already reloaded)

Click **Create → Record Offline Payment** again. Fill:

| Field | Value |
|---|---|
| Amount | `30000` (defaults to the new outstanding) |
| Mode of Payment | `UPI` |
| Reference # | `VZ-UPI-002` |

Click **Record Payment**.

**Expected:**
- Green toast: _"Payment ACC-PAY-XXXX-XXXXX recorded (₹30,000.00). Fee fully paid ✓"_
- `Outstanding Amount` on the Fees form is now `₹0`
- The **Record Offline Payment** button no longer appears (the JS hides it once outstanding == 0)
- Status sidebar pill on the Fees doc switches to **Paid**

### Step 5 — Student sees updated portal

**As:** `zopevedant1@gmail.com`
**Where:** https://ems.hanumatrix.com/student_portal → **Fees** tab (refresh)

**Expected:**

| Section | Expected |
|---|---|
| Pending Fees | Empty |
| Payment History | Two rows: ₹20,000 Cash (VZ-CASH-001), ₹30,000 UPI (VZ-UPI-002), both today's date |
| Fee Summary | total ₹50,000 / paid ₹50,000 / pending ₹0 |

Click the download icon on either Payment History row → a **PDF receipt** named `Payment_Receipt_ACC-PAY-XXXX-XXXXX.pdf` downloads (~19 KB).

---

## What the system creates when the cashier clicks Record Offline Payment

| Artefact | DocType | Created by |
|---|---|---|
| One Payment Entry per click, submitted (docstatus=1) | `Payment Entry` | `record_offline_payment` API, called from the desk Fees form via [`public/js/fees.js`](../../frappe-bench/apps/university_erp/university_erp/public/js/fees.js) |
| Payment Entry Reference linking the PE to the Fees doc | `Payment Entry Reference` (child) | Auto, inside the PE |
| Reduced outstanding on the Fees doc | `Fees.outstanding_amount` | `db_set` after PE submit |
| GL Entries (debit cash/bank, credit receivable) | `GL Entry` | Auto-generated by Payment Entry submit |

The button is wired through `doctype_js` in `hooks.py` so it ships with the app and is visible to every Frappe desk user that has `University Finance` / `System Manager` / `Administrator`. Backend API in [`university_finance/payment_recorder.py`](../../frappe-bench/apps/university_erp/university_erp/university_finance/payment_recorder.py).

---

## Public API

| Method | Purpose | Permission |
|---|---|---|
| `university_erp.university_finance.payment_recorder.list_outstanding_fees` | List Fees rows with `outstanding > 0` | Any logged-in user |
| `university_erp.university_finance.payment_recorder.record_offline_payment` | Create + submit a Payment Entry against a Fees doc | `University Finance` / `System Manager` / `Administrator` |
| `university_erp.university_portals.api.portal_api.download_payment_receipt` | Render Payment Entry as PDF | Owner of the linked Fees, or finance staff |

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Record Offline Payment** button missing on Fees form | Caller doesn't have `University Finance` (or `System Manager` / `Administrator`) role, OR the doc is in Draft, OR outstanding == 0 | Add the role: `bench --site ems.hanumatrix.com console` → `frappe.get_doc("User", "you@nit.edu").add_roles("University Finance")`. Confirm doc is `docstatus=1` and `outstanding_amount > 0`. Hard-refresh the form. |
| **No outstanding fees right now** when the demo student does have one | The Fees doc is in Draft (`docstatus=0`) | Open Fees → click **Submit**. Or run Journey 01's Step 5 (Admit) again. |
| **`No Receivable account configured for company X`** | Company has no account marked as Receivable | Create one under Chart of Accounts, mark `account_type=Receivable`. |
| **`No active asset account configured for Cash`** | No Cash account in the company chart | Create one under Chart of Accounts, mark `account_type=Cash`. Or add a row to **Mode of Payment Account** for the company. |
| **Payment Entry submits but portal still shows ₹50,000 outstanding** | Frappe Education's Fees controller didn't recompute outstanding | Already handled — `record_offline_payment` does an explicit `db_set("outstanding_amount", ...)` after submit. |
| **Payment History row missing in portal** | The PE has `reference_doctype != 'Fees'` | Check **Payment Entry → References** child table. The portal's `get_payment_history` joins on `Payment Entry Reference.reference_doctype = 'Fees'`. |
| **Receipt PDF download returns HTML** | Frappe < 14 doesn't accept `type: "pdf"` directly | The portal API `download_payment_receipt` already uses `frappe.utils.pdf.get_pdf` to render bytes; this site is on Frappe 15.103.0 which supports it natively. |
| **Modal "Record Payment" button stays disabled / doesn't fire** | Asset bundle stale | Run `bench build --app university_erp` then hard-refresh (Ctrl+Shift+R). |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")

# Cancel and delete all Payment Entries for this student
for pe in frappe.db.get_all("Payment Entry", filters={"party": stu, "party_type": "Student"}, fields=["name", "docstatus"]):
    if pe.docstatus == 1:
        try: frappe.get_doc("Payment Entry", pe.name).cancel()
        except Exception: pass
    frappe.delete_doc("Payment Entry", pe.name, force=True)

# Reset outstanding on the Fees doc back to grand_total so the journey can re-run
fee_name = frappe.db.get_value("Fees", {"student": stu, "docstatus": 1}, "name")
if fee_name:
    f = frappe.get_doc("Fees", fee_name)
    f.db_set("outstanding_amount", f.grand_total, update_modified=False)

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: Cashier lists outstanding fees ===
  1 outstanding for EDU-STU-2026-01602
  - EDU-FEE-2026-01404: ₹50,000 due 2026-06-02

=== STEP 2: Record ₹20,000 by Cash ===
  Result: ACC-PAY-2026-00827, remaining ₹30,000

=== STEP 3: Record ₹30,000 by UPI ===
  Result: ACC-PAY-2026-00828, fully_paid=True

=== STEP 4: Student portal ===
  pending_fees:    []
  payment_history: [
    ACC-PAY-2026-00827 — ₹20,000 Cash, ref VZ-CASH-001
    ACC-PAY-2026-00828 — ₹30,000 UPI,  ref VZ-UPI-002
  ]
  fee_summary:     total ₹50,000 / paid ₹50,000 / pending ₹0

=== STEP 5: Receipt PDF download ===
  ACC-PAY-2026-00827 → Payment_Receipt_ACC-PAY-2026-00827.pdf (19,435 bytes)
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1 — student sees ₹50,000 outstanding | PASS / FAIL |
| Step 2 — cashier sees Outstanding Fees list | PASS / FAIL |
| Step 3 — partial payment reduces outstanding | PASS / FAIL |
| Step 4 — final payment marks fee fully paid | PASS / FAIL |
| Step 5 — portal shows both payments + receipts download | PASS / FAIL |
| Notes / defects logged |  |

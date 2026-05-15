# Journey 06 — Library

**End-to-end library flow:** the librarian opens a Library Article on the desk → clicks **Create → Issue Book** → picks a student → the system auto-creates a Library Member if missing, creates a submitted Library Transaction, and decrements `available_copies`. The student sees the issued book on the portal. When the book comes back, the librarian opens the transaction and clicks **Actions → Mark Returned** — if returned after the due date, a Library Fine row is auto-created and added to the member's outstanding fines.

Uses the demo student created in Journey 01 (`zopevedant1@gmail.com` / `demo@1234`).

**No custom portal page for staff.** Both Issue and Return run from standard ERPNext desk forms.

---

## Test site

| | |
|---|---|
| Library Article list | https://ems.hanumatrix.com/app/library-article |
| Library Transaction list | https://ems.hanumatrix.com/app/library-transaction |
| Library Fine list | https://ems.hanumatrix.com/app/library-fine |
| Student portal — Library tab | https://ems.hanumatrix.com/student_portal → **Library** |

## Actors

| Role | UAT username | Used in step |
|---|---|---|
| `University Librarian` (or Admin) | any user with role | 1 – 2, 5 – 6 |
| `University Student` | `zopevedant1@gmail.com` | 3 – 4, 7 |

## Pre-requisites

```python
# bench --site ems.hanumatrix.com console
import frappe
EMAIL = "zopevedant1@gmail.com"
stu = frappe.db.get_value("Student", {"student_email_id": EMAIL}, "name")
assert stu, "Run Journey 01 first"

# Library masters
borrowable = frappe.db.count("Library Article", {"status": "Available", "available_copies": [">", 0]})
assert borrowable > 0, "No borrowable Library Articles seeded"
print(f"Ready: {stu}, {borrowable} books available")
```

> Library Member is **auto-created** the first time a book is issued to a student — no separate enrollment step.

---

## Step-by-step UAT script

### Step 1 — Librarian opens a Library Article

**As:** any user with `University Librarian` / `University Admin` / Administrator role
**Where:** https://ems.hanumatrix.com/app/library-article — list view, filter by `Status = Available`

Click any row (e.g. `LIB-2026-00425 — Artificial Intelligence: A Modern Approach`).

**Expected:** Library Article form. Top-right **Create** dropdown shows a custom **Issue Book** action (only when `available_copies > 0`).

### Step 2 — Issue Book

Click **Create → Issue Book**. Dialog:

| Field | Value |
|---|---|
| Student | `EDU-STU-2026-01602` (or pick by name) |
| Loan period (days) | `14` (default) |

Click **Issue Book**.

**Expected:**
- Toast: _"Transaction LT-XXXX-XXXXX created. Due 2026-05-18. (Library Member auto-created)"_ — the suffix appears only on the first issue per student
- Form reloads → `available_copies` decrements by 1, `issued_copies` increments by 1
- Submitted Library Transaction at `/app/library-transaction/LT-XXXX-XXXXX` linked to the article and member

### Step 3 — Student sees the issue on the portal

**As:** `zopevedant1@gmail.com`
**Where:** https://ems.hanumatrix.com/student_portal → **Library** tab

**Expected:**

| Section | Shows |
|---|---|
| Currently Issued | 1 book — title, author, issue date, due date, days remaining |
| Library Stats | total_borrowed=1, currently_issued=1, max_allowed=5 |
| Overdue | empty (book is not yet overdue) |

### Step 4 — Student returns the book on time

(In a real test the student walks to the library and the librarian receives the book.)

### Step 5 — Librarian marks the book returned

**As:** `University Librarian`
**Where:** https://ems.hanumatrix.com/app/library-transaction/LT-XXXX-XXXXX

Click **Actions → Mark Returned**. Dialog:

| Field | Value |
|---|---|
| Return Date | today (default) |
| Fine per overdue day | `₹5` (default — only applied if return_date > due_date) |

Click **Confirm Return**.

**Expected (on-time return):**
- Toast: _"Returned on time ✓ No fine."_
- Transaction `status` flips to **Returned**, `return_date` set, `is_overdue=0`, `fine_amount=0`
- Article's `available_copies` increments by 1 (back to original)
- Library Member's `current_borrowed` decrements by 1

### Step 6 — Test the overdue path (issue another, return late)

Repeat Steps 1-2 with a different article. Then on the new transaction:

1. Click **Actions → Mark Returned**
2. Set **Return Date** to **at least 1 day after the due date** (e.g. due_date + 15 days)
3. Click **Confirm Return**

**Expected (late return):**
- Toast: _"Returned. 15 day(s) overdue — Library Fine LF-XXXX-XXXXX for ₹75 created."_
- Transaction has `is_overdue=1`, `overdue_days=15`, `fine_amount=75`, `fine_reference=LF-XXXX-XXXXX`
- A new submitted **Library Fine** doc exists at `/app/library-fine/LF-XXXX-XXXXX` with status `Unpaid`
- Library Member's `outstanding_fines` field += 75

### Step 7 — Student sees the fine on the portal

**As:** `zopevedant1@gmail.com`
**Where:** Library tab (refresh)

**Expected:**

| Section | Shows |
|---|---|
| Currently Issued | empty (both books returned) |
| Borrowing History | 2 entries (one on-time, one late with overdue badge) |
| Outstanding fines | ₹75 (the late return) |

> **Note:** the next book issue to this student will be **blocked** by the controller until the fine is settled (`outstanding_fines > 0` check in `issue_article`). Settle by paying via the Fees flow or marking the Fine `Paid` on the desk.

---

## What the system creates / updates when "Issue Book" is clicked

| Step | Artefact | DocType | Created by |
|---|---|---|---|
| Issue (first time per student) | Library Member with status `Active`, max_books=5, expiry=+1 year | `Library Member` | `ensure_member` helper inside `issue_article` |
| Issue | Submitted Library Transaction (type=Issue, status=Issued) | `Library Transaction` | `issue_article` API |
| Issue | `Library Article.available_copies` -1, `issued_copies` +1, status flips if last copy | — | `issue_article` API (db_set) |
| Issue | `Library Member.current_borrowed` +1, `available_quota` -1 | — | `issue_article` API (db_set) |
| Return (on-time) | Transaction status → Returned, return_date set | — | `return_article` API |
| Return (overdue) | Submitted Library Fine (status=Unpaid) | `Library Fine` | `return_article` API |
| Return | Article counters reverse, Member counters reverse | — | `return_article` API |

All driven by [`university_library/doctype/library_transaction/library_transaction_actions.py`](../../frappe-bench/apps/university_erp/university_erp/university_library/doctype/library_transaction/library_transaction_actions.py).

---

## Public APIs

| Method | Purpose | Permission |
|---|---|---|
| `university_erp.university_library.doctype.library_transaction.library_transaction_actions.list_borrowable_articles` | Library Articles with `available_copies > 0` (optional `query` filter) | Logged-in librarian/admin |
| `university_erp.university_library.doctype.library_transaction.library_transaction_actions.ensure_member` | Find or auto-create Library Member for a Student | Logged-in staff |
| `university_erp.university_library.doctype.library_transaction.library_transaction_actions.issue_article` | Issue a Library Article to a student | `University Librarian/Admin/SysMgr/Admin` |
| `university_erp.university_library.doctype.library_transaction.library_transaction_actions.return_article` | Mark transaction returned, auto-fine if overdue | Same |
| `university_erp.university_portals.api.portal_api.get_student_library` | Student's issued books, history, stats, overdue | Logged-in student |

---

## Common breaks and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| **Issue Book button missing on Library Article form** | Caller doesn't have the librarian role, or `available_copies = 0` | Add the role; check article's `available_copies` field. |
| **`Article X has no available copies`** on issue | All copies already out | Wait for a return or mark a return manually. |
| **`Member has reached the borrowing limit (5)`** | Student already has 5 books out | Return one of the existing books first. |
| **`Member has outstanding fines: ₹X`** | Settle the fine first | Mark the Library Fine `Paid` on `/app/library-fine`, then issue. |
| **`Mark Returned` button missing** | Transaction is in Draft (`docstatus != 1`) or already returned | Submit the transaction first; if already returned, the button hides itself. |
| **Fine row created but Member's `outstanding_fines` not updated** | `db_set` was called outside the API path | Re-run `return_article`; or recompute: `frappe.db.set_value("Library Member", "<LM>", "outstanding_fines", sum unpaid Library Fine for that member)`. |
| **Article counters drift over time** | Direct DB edits or seed inconsistencies | Recompute: for each article, `available_copies = total_copies - SUM(issued)`. |

---

## Re-run the journey (cleanup)

```python
# bench --site ems.hanumatrix.com console
import frappe
stu = frappe.db.get_value("Student", {"student_email_id": "zopevedant1@gmail.com"}, "name")
mem = frappe.db.get_value("Library Member", {"student": stu}, "name")

if mem:
    # Cancel + delete all transactions
    for txn in frappe.db.get_all("Library Transaction", filters={"member": mem}, fields=["name", "docstatus", "article"]):
        if txn.docstatus == 1:
            try: frappe.get_doc("Library Transaction", txn.name).cancel()
            except Exception: pass
        frappe.delete_doc("Library Transaction", txn.name, force=True)
    # Cancel + delete fines
    for fine in frappe.db.get_all("Library Fine", filters={"member": mem}, fields=["name", "docstatus"]):
        if fine.docstatus == 1:
            try: frappe.get_doc("Library Fine", fine.name).cancel()
            except Exception: pass
        frappe.delete_doc("Library Fine", fine.name, force=True)
    # Delete the member
    frappe.delete_doc("Library Member", mem, force=True)

# Recompute article counters (optional sanity)
for art in frappe.db.get_all("Library Article"):
    issued = frappe.db.count("Library Transaction", {"article": art.name, "status": "Issued", "docstatus": 1})
    total = frappe.db.get_value("Library Article", art.name, "total_copies") or 0
    frappe.db.set_value("Library Article", art.name, "available_copies", max(total - issued, 0))
    frappe.db.set_value("Library Article", art.name, "issued_copies", issued)
    frappe.db.set_value("Library Article", art.name, "status", "Available" if (total - issued) > 0 else "Issued")

frappe.db.commit()
```

---

## Live verification log (last successful run)

```
=== STEP 1: 40 borrowable articles listed ===
  e.g. LIB-2026-00425: "Artificial Intelligence: A Modern Approach" (9 copies)

=== STEP 2: Issue first article ===
  Transaction: LT-2026-00298
  Member auto-created: LM-2026-00562
  Issue date: 2026-05-04, Due date: 2026-05-18

=== STEP 3: Portal as student ===
  issued_books: 1
  library_stats: {total_borrowed:1, currently_issued:1, max_allowed:5}

=== STEP 4: Return on time ===
  overdue_days=0, fine_amount=0, no fine created

=== STEP 5: Issue + Return LATE (15 days overdue) ===
  Transaction: LT-2026-00299
  Late return → Fine LF-2026-00107 for ₹75
```

---

## Tester sign-off

| Field | Value |
|---|---|
| Tester name |  |
| Test date |  |
| Build / commit |  |
| Step 1-2 — Issue Book creates txn + auto-creates Library Member | PASS / FAIL |
| Step 3 — portal Library tab shows issued book | PASS / FAIL |
| Step 5 — on-time return clears the issue, no fine | PASS / FAIL |
| Step 6 — late return auto-creates Library Fine | PASS / FAIL |
| Step 7 — portal shows borrowing history + outstanding fine | PASS / FAIL |
| Notes / defects logged |  |

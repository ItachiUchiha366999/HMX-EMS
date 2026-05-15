"""Check Fees doctype and what the Fee Collection Summary needs."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Check if tabFees exists and has data
    try:
        fees_count = frappe.db.sql("SELECT COUNT(*) as cnt FROM `tabFees`", as_dict=True)
        print(f"tabFees rows: {fees_count[0].cnt}")

        fees_sample = frappe.db.sql(
            "SELECT name, student, program, grand_total, outstanding_amount, docstatus FROM `tabFees` LIMIT 3",
            as_dict=True
        )
        print(f"Sample: {fees_sample}")

        fees_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabFees`", as_dict=True)]
        prog_cols = [c for c in fees_cols if 'program' in c.lower() or 'student' in c.lower()]
        print(f"Fees program/student cols: {prog_cols}")
    except Exception as e:
        print(f"tabFees error: {e}")

    # Check if Sales Invoice has a program field
    si_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabSales Invoice`", as_dict=True)]
    prog_cols = [c for c in si_cols if 'program' in c.lower() or 'student' in c.lower() or 'academic' in c.lower()]
    print(f"\nSales Invoice program/student/academic cols: {prog_cols}")

    # Check what SI data looks like
    si_sample = frappe.db.sql(
        "SELECT name, customer, grand_total, outstanding_amount, docstatus FROM `tabSales Invoice` WHERE docstatus=1 LIMIT 3",
        as_dict=True
    )
    print(f"Sales Invoice sample: {si_sample}")

    # What does the report validator currently use for Fee Collection Summary?
    # It's been passing (8 rows) — so the report must actually work differently
    # Let's run it directly
    from frappe.desk.query_report import run as run_report
    try:
        res = run_report("Fee Collection Summary", filters={"academic_year": "2026-2027"}, ignore_prepared_report=True)
        print(f"\nFee Collection Summary rows: {len(res.get('result', []))}")
        print(f"Sample result: {res.get('result', [])[:2]}")
    except Exception as e:
        print(f"Fee Collection Summary ERR: {e}")

    # Try without academic_year filter
    try:
        res2 = run_report("Fee Collection Summary", filters={}, ignore_prepared_report=True)
        print(f"\nFee Collection Summary (no filter) rows: {len(res2.get('result', []))}")
    except Exception as e:
        print(f"No-filter ERR: {e}")

"""Probe Internal Assessment columns and Fee Collection Summary."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    print("=== Internal Assessment cols ===")
    cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabInternal Assessment`", as_dict=True)]
    print("cols:", cols)

    print("\n=== Internal Assessment sample ===")
    ia_sample = frappe.db.sql(
        "SELECT * FROM `tabInternal Assessment` WHERE docstatus=1 LIMIT 1", as_dict=True
    )
    if ia_sample:
        print({k: v for k, v in ia_sample[0].items() if k not in ('_user_tags', '_comments', '_assign', '_liked_by')})

    print("\n=== Fee Collection Summary script ===")
    import os
    fcs_paths = [
        "/home/frappe/frappe-bench/apps/university_erp/university_erp/university_finance/report/fee_collection_summary/fee_collection_summary.py",
    ]
    for p in fcs_paths:
        if os.path.exists(p):
            with open(p) as f:
                print(f.read()[:100])
            break

    print("\n=== Sales Invoice sample ===")
    si = frappe.db.sql("""
        SELECT name, customer, program_name, academic_year, outstanding_amount, status
        FROM `tabSales Invoice` WHERE docstatus=1 LIMIT 3
    """, as_dict=True)
    for r in si:
        print(f"  {r}")

    print("\n=== Sales Invoice cols (custom) ===")
    si_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabSales Invoice`", as_dict=True)]
    # Show only custom/relevant cols
    relevant = [c for c in si_cols if 'program' in c.lower() or 'academic' in c.lower() or 'fee' in c.lower() or 'student' in c.lower()]
    print("  relevant cols:", relevant)

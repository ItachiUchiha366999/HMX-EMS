"""Probe Fee Collection Summary query."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # What does tabFees have?
    fees = frappe.db.sql("""
        SELECT f.program, f.student, f.grand_total, f.outstanding_amount,
               f.docstatus, f.posting_date, f.fee_structure
        FROM `tabFees` f
        WHERE f.docstatus = 1
        LIMIT 5
    """, as_dict=True)
    print("Fees sample:", fees)

    # Count by program
    prog_dist = frappe.db.sql("""
        SELECT program, COUNT(*) as cnt, SUM(grand_total) as total
        FROM `tabFees` WHERE docstatus=1
        GROUP BY program
    """, as_dict=True)
    print("\nFees by program:", prog_dist)

    # Check the fee_structure field — does it link to Fee Structure?
    fs_sample = frappe.db.sql(
        "SELECT name, custom_academic_year FROM `tabFee Structure` LIMIT 5", as_dict=True
    )
    print("\nFee Structure sample:", fs_sample)

    # Check tabFee Structure columns for academic year field
    fs_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabFee Structure`", as_dict=True)]
    print("Fee Structure cols:", [c for c in fs_cols if 'year' in c.lower() or 'academic' in c.lower() or 'name' == c])

    # Now run the exact query from the script WITHOUT date filter
    data = frappe.db.sql("""
        SELECT
            f.program,
            COUNT(DISTINCT f.student) as total_students,
            SUM(f.grand_total) as fees_generated,
            SUM(f.grand_total - f.outstanding_amount) as fees_collected,
            SUM(f.outstanding_amount) as fees_outstanding,
            ROUND(SUM(f.grand_total - f.outstanding_amount) / NULLIF(SUM(f.grand_total), 0) * 100, 2) as collection_percentage
        FROM `tabFees` f
        LEFT JOIN `tabFee Structure` fs ON f.fee_structure = fs.name
        WHERE f.docstatus = 1
        GROUP BY f.program
        ORDER BY fees_generated DESC
    """, as_dict=True)
    print(f"\nFee Collection query result (no date filter): {len(data)} rows")
    for r in data:
        print(f"  {r}")

    # Now with the date filter the script uses
    data2 = frappe.db.sql("""
        SELECT f.program, COUNT(*) as cnt
        FROM `tabFees` f
        LEFT JOIN `tabFee Structure` fs ON f.fee_structure = fs.name
        WHERE f.docstatus = 1
          AND f.posting_date >= '2026-01-01'
          AND f.posting_date <= '2026-05-01'
        GROUP BY f.program
    """, as_dict=True)
    print(f"\nWith date filter (2026-01-01 to 2026-05-01): {len(data2)} rows")

    # What are the actual posting_date values?
    dates = frappe.db.sql(
        "SELECT MIN(posting_date) as min_d, MAX(posting_date) as max_d FROM `tabFees` WHERE docstatus=1",
        as_dict=True
    )
    print(f"\nFees posting_date range: {dates}")

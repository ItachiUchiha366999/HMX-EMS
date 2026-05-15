"""Final filter fixes — Fee Collection Summary should have no academic_year default."""
import frappe
import json


def run():
    frappe.flags.ignore_permissions = True

    # Fee Collection Summary: academic_year filter is broken (JOIN col doesn't exist)
    # Remove academic_year default; add from/to_date so it always shows data
    if frappe.db.exists("Report", "Fee Collection Summary"):
        doc = frappe.get_doc("Report", "Fee Collection Summary")
        doc.filters = json.dumps([
            {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
             "default": "Today - 365", "mandatory": 0},
            {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
             "default": "Today", "mandatory": 0},
            {"fieldname": "program", "fieldtype": "Link", "label": "Program",
             "options": "Program", "mandatory": 0},
        ])
        doc.db_update()
        print("OK: Fee Collection Summary (removed academic_year default)")

    frappe.db.commit()

    # Verify — run without academic_year
    from frappe.desk.query_report import run as run_report
    res = run_report("Fee Collection Summary", filters={}, ignore_prepared_report=True)
    print(f"Fee Collection Summary (no filter): {len(res.get('result', []))} rows")

    # Now also fix Internal Assessment Summary — deploy the fixed Python
    print("\nVerify Internal Assessment Summary with term filter...")
    res2 = run_report("Internal Assessment Summary",
                      filters={"academic_year": "2026-2027",
                               "academic_term": "2026-2027 (Semester 2)",
                               "course": "Operations Management"},
                      ignore_prepared_report=True)
    print(f"Internal Assessment Summary: {len(res2.get('result', []))} rows")

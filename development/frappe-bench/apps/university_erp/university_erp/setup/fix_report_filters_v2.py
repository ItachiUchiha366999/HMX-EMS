"""Fix report filters correctly using Frappe v15's tabReport Filter child table."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Check tabReport Filter structure
    rf_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabReport Filter`", as_dict=True)]
    print("tabReport Filter cols:", rf_cols)

    # Check existing filters for CO Attainment
    existing = frappe.db.sql(
        "SELECT * FROM `tabReport Filter` WHERE parent='CO Attainment Report'",
        as_dict=True
    )
    print(f"\nExisting CO Attainment filters: {existing}")

    # Check Report Filter Definition too
    rfd_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabReport Filter Definition`", as_dict=True)]
    print(f"\ntabReport Filter Definition cols: {rfd_cols}")

    existing2 = frappe.db.sql(
        "SELECT * FROM `tabReport Filter Definition` WHERE parent='CO Attainment Report'",
        as_dict=True
    )
    print(f"Existing CO Attainment Filter Definitions: {existing2}")

    # Check tabReport Column Definition
    rcd_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabReport Column Definition`", as_dict=True)]
    print(f"\ntabReport Column Definition cols: {rcd_cols}")

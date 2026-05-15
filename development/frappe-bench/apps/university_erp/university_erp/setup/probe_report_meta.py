"""Check actual Report doctype structure in Frappe v15."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Check tabReport columns
    report_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabReport`", as_dict=True)]
    print("tabReport cols:", report_cols)

    # Check child tables for Report
    report_tables = frappe.db.sql(
        "SHOW TABLES LIKE 'tabReport%'", as_dict=True
    )
    print("Report-related tables:", report_tables)

    # Check what the Report doc actually contains
    rpt = frappe.get_doc("Report", "CO Attainment Report")
    print(f"\nReport CO Attainment fields: {list(rpt.__dict__.keys())[:30]}")
    print(f"filters child: {getattr(rpt, 'filters', 'NO ATTR')}")
    print(f"json_fields: {rpt.get('json_fields') or 'none'}")

    # Check tabDefaultValue for report filters (Frappe stores user filter defaults here)
    dv = frappe.db.sql("""
        SELECT parent, defkey, defvalue
        FROM `tabDefaultValue`
        WHERE defkey LIKE '%_report_%' OR defkey LIKE '%report_filter%'
        LIMIT 10
    """, as_dict=True)
    print(f"\nDefaultValue report keys: {dv}")

    # How does Frappe v15 store report filters? Check the JSON field on Report
    rpt_raw = frappe.db.sql(
        "SELECT * FROM `tabReport` WHERE name='CO Attainment Report'",
        as_dict=True
    )
    if rpt_raw:
        r = rpt_raw[0]
        print(f"\nRaw Report row keys: {list(r.keys())}")
        # Show any JSON-like fields
        for k, v in r.items():
            if v and isinstance(v, str) and (v.startswith('[') or v.startswith('{')):
                print(f"  {k}: {v[:200]}")

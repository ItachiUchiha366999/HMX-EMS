"""Check where Frappe stores report filter defaults."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Check if there's a DefaultValue table storing old filters
    dv = frappe.db.sql("""
        SELECT parent, defkey, defvalue
        FROM `tabDefaultValue`
        WHERE defkey LIKE '%CO Attainment%'
           OR defkey LIKE '%co_attainment%'
           OR defkey LIKE '%Survey Analysis%'
           OR defkey LIKE '%Program Attainment%'
           OR defkey LIKE '%CO-PO%'
        LIMIT 20
    """, as_dict=True)
    print("DefaultValue rows for these reports:", dv)

    # Check Report document filters field format
    for rname in ["CO Attainment Report", "CO-PO Mapping Matrix",
                  "Program Attainment Summary", "Survey Analysis Report"]:
        if not frappe.db.exists("Report", rname):
            continue
        filters_raw = frappe.db.get_value("Report", rname, "filters")
        print(f"\n{rname} filters in DB: {filters_raw}")

    # Check if there's a tabUser Report Filters or similar
    tables = frappe.db.sql(
        "SHOW TABLES LIKE '%Report%Filter%'", as_dict=True
    )
    print("\nTables with 'Report' and 'Filter':", tables)

    tables2 = frappe.db.sql(
        "SHOW TABLES LIKE '%Default%'", as_dict=True
    )
    print("Tables with 'Default':", tables2)

    # Check the Report document's filters field type
    rpt = frappe.get_doc("Report", "CO Attainment Report")
    print(f"\nReport.filters type: {type(rpt.filters)}")
    print(f"Report.filters value: {rpt.filters}")

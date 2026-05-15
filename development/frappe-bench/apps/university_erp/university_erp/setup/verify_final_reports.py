"""Final verification: run each broken report with its new default filters."""
import frappe
from frappe.desk.query_report import run as run_report


def check(report_name, filters, expect_min=1):
    try:
        res = run_report(report_name, filters=filters, ignore_prepared_report=True)
        rows = len(res.get("result", []))
        has_chart = bool(res.get("chart"))
        status = "OK" if rows >= expect_min else "EMPTY"
        print(f"  {'✓' if status=='OK' else '✗'} {report_name}: {rows} rows, chart={'yes' if has_chart else 'no'}")
        return rows
    except Exception as e:
        print(f"  ✗ {report_name}: ERR — {e}")
        return 0


def run():
    frappe.flags.ignore_permissions = True

    print("=== OBE Reports ===")
    check("CO Attainment Report",
          {"academic_year": "2026-2027", "academic_term": "2026-2027 (Semester 2)"}, 5)
    check("CO-PO Mapping Matrix",
          {"program": "B.Tech Computer Science and Engineering", "course": "Operating Systems"}, 1)
    check("CO-PO Mapping Matrix", {}, 1)  # No filters — auto-fallback
    check("Program Attainment Summary", {"academic_year": "2026-2027"}, 5)
    check("Survey Analysis Report", {"academic_year": "2026-2027"}, 5)
    check("PO Attainment Report", {"academic_year": "2026-2027"}, 5)
    check("NAAC Criterion Progress", {}, 3)
    check("NIRF Parameter Report", {"ranking_year": "2026", "category": "Engineering"}, 1)

    print("\n=== Placement Reports ===")
    check("Placement Statistics", {"academic_year": "2026-2027"}, 1)
    check("Company Wise Placement", {"academic_year": "2026-2027"}, 3)
    check("Program Wise Placement", {"academic_year": "2026-2027"}, 3)
    check("Placement Trend", {}, 1)

    print("\n=== Examination Reports ===")
    check("Internal Assessment Summary",
          {"academic_year": "2026-2027", "academic_term": "2026-2027 (Semester 2)",
           "course": "Operations Management"}, 1)
    check("Examination Result Analysis",
          {"academic_term": "2026-2027 (Semester 2)"}, 1)

    print("\n=== Library / Hostel / Finance Reports ===")
    check("Library Circulation", {}, 1)
    check("Hostel Occupancy", {}, 1)
    check("Fee Collection Summary", {"academic_year": "2026-2027"}, 1)

    print("\n=== Faculty / Research Reports ===")
    check("Faculty Directory", {}, 1)
    check("Faculty Research Output", {"from_year": 2024, "to_year": 2026}, 1)

    print("\n=== Validator summary ===")
    from university_erp.setup.seed_validate import validate_all
    validate_all()

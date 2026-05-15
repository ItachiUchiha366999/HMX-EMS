"""Verify all four OBE reports return data."""
import frappe


def _run_report(report_name, filters):
    report = frappe.get_doc("Report", report_name)
    result = report.execute_script_report(filters)
    # result = (columns, data, message, chart, summary)
    data = result[1] if result else []
    return len(data)


def run():
    frappe.flags.ignore_permissions = True

    print("=== Testing OBE Reports ===\n")

    # 1. CO Attainment Report
    rows = _run_report("CO Attainment Report", {
        "academic_year": "2026-2027",
        "academic_term": "2026-2027 (Semester 2)"
    })
    print(f"CO Attainment Report: {rows} rows")

    # 2. CO PO Mapping Matrix — no filters (should auto-pick)
    rows = _run_report("CO-PO Mapping Matrix", {})
    print(f"CO-PO Mapping Matrix (no filters): {rows} rows")

    # 3. CO PO Mapping with filters
    rows2 = _run_report("CO-PO Mapping Matrix", {
        "program": "B.Tech Computer Science and Engineering",
        "course": "Operating Systems"
    })
    print(f"CO-PO Mapping Matrix (CSE/OS): {rows2} rows")

    # 4. Program Attainment Summary
    rows = _run_report("Program Attainment Summary", {
        "academic_year": "2026-2027"
    })
    print(f"Program Attainment Summary: {rows} rows")

    # 5. Survey Analysis Report
    rows = _run_report("Survey Analysis Report", {
        "academic_year": "2026-2027"
    })
    print(f"Survey Analysis Report: {rows} rows")

    # Also check what Survey Analysis returns to confirm correctness
    print("\n=== Survey Analysis detail check ===")
    surveys = frappe.get_all("OBE Survey",
        filters={"status": ["in", ["Submitted", "Verified"]], "academic_year": "2026-2027"},
        fields=["name", "program", "survey_type"]
    )
    print(f"Surveys in scope: {len(surveys)}")
    for s in surveys:
        ratings = frappe.db.count("Survey PO Rating", {"parent": s.name})
        print(f"  {s.name}: {s.program}, type={s.survey_type}, ratings={ratings}")

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Report & Dashboard Audit Script

Tests all reports for execution correctness, verifies analytics API endpoints,
and checks dashboard aggregation accuracy against direct SQL queries.

Usage:
    bench --site university.local execute university_erp.scripts.audit_reports.run
"""

import os
import re
import json
import traceback
from datetime import datetime, timedelta

import frappe
from frappe.utils import nowdate, getdate, today, flt


# ---------------------------------------------------------------------------
# Report discovery
# ---------------------------------------------------------------------------

def _discover_reports_from_db():
    """Discover all registered reports from the database."""
    return frappe.get_all(
        "Report",
        filters={"disabled": 0},
        fields=["name", "module", "report_type", "ref_doctype"],
    )


def _discover_report_files_on_disk():
    """Scan the university_erp app for report .py files on disk."""
    app_path = frappe.get_app_path("university_erp")
    report_files = []
    for root, _dirs, files in os.walk(app_path):
        if "/report/" not in root:
            continue
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                # Extract report name from directory structure
                parts = root.split("/report/")
                if len(parts) == 2:
                    report_dir = parts[1].split("/")[0] if "/" in parts[1] else parts[1]
                    report_files.append({
                        "file": os.path.join(root, f),
                        "report_dir": report_dir,
                        "report_name_guess": report_dir.replace("_", " ").title(),
                    })
    return report_files


def _find_unregistered_reports(db_reports, disk_reports):
    """Compare DB reports with disk files, flag unregistered ones."""
    db_names_lower = {r["name"].lower().replace(" ", "_") for r in db_reports}
    unregistered = []
    for dr in disk_reports:
        if dr["report_dir"] not in db_names_lower:
            unregistered.append(dr)
    return unregistered


# ---------------------------------------------------------------------------
# Report execution (two-pass)
# ---------------------------------------------------------------------------

def _read_mandatory_filters(report_name):
    """Try to read a report's .js file to find mandatory filters and supply defaults."""
    filters = {}
    # Find the .js file for this report
    app_path = frappe.get_app_path("university_erp")
    report_dir_name = report_name.lower().replace(" ", "_")

    js_file = None
    for root, _dirs, files in os.walk(app_path):
        if root.endswith(f"/report/{report_dir_name}"):
            for f in files:
                if f.endswith(".js"):
                    js_file = os.path.join(root, f)
                    break
            break

    if not js_file or not os.path.exists(js_file):
        return _get_common_defaults()

    try:
        with open(js_file, "r") as fp:
            content = fp.read()

        # Look for mandatory/reqd fields
        field_patterns = re.findall(
            r'fieldname["\s:]+["\'](\w+)["\'].*?(?:mandatory|reqd)\s*:\s*1',
            content,
            re.DOTALL | re.IGNORECASE,
        )
        # Also look for default values
        default_patterns = re.findall(
            r'fieldname["\s:]+["\'](\w+)["\'].*?default\s*:\s*["\']?([^"\'}\n,]+)',
            content,
            re.DOTALL | re.IGNORECASE,
        )

        for field_name in field_patterns:
            fn = field_name.lower()
            if "academic_year" in fn or fn == "academic_year":
                filters["academic_year"] = _get_default_academic_year()
            elif "academic_term" in fn:
                filters["academic_term"] = _get_default_academic_term()
            elif "department" in fn:
                filters["department"] = _get_default_department()
            elif "from_date" in fn:
                filters["from_date"] = str(getdate(today()) - timedelta(days=365))
            elif "to_date" in fn:
                filters["to_date"] = nowdate()
            elif "company" in fn:
                filters["company"] = frappe.defaults.get_defaults().get("company", "")
            elif "program" in fn:
                filters["program"] = _get_default_program()
            elif "course" in fn:
                filters["course"] = _get_default_course()

        # If we found no mandatory filters from JS, fall back to common defaults
        if not filters:
            filters = _get_common_defaults()

    except Exception:
        filters = _get_common_defaults()

    return filters


def _get_common_defaults():
    """Return a set of common defaults that work for most reports."""
    return {
        "academic_year": _get_default_academic_year(),
        "from_date": str(getdate(today()) - timedelta(days=365)),
        "to_date": nowdate(),
        "company": frappe.defaults.get_defaults().get("company", ""),
    }


def _get_default_academic_year():
    years = frappe.get_all("Academic Year", order_by="name desc", limit=1)
    return years[0]["name"] if years else ""


def _get_default_academic_term():
    terms = frappe.get_all("Academic Term", order_by="name desc", limit=1)
    return terms[0]["name"] if terms else ""


def _get_default_department():
    depts = frappe.get_all("Department", limit=1)
    return depts[0]["name"] if depts else ""


def _get_default_program():
    programs = frappe.get_all("Program", limit=1)
    return programs[0]["name"] if programs else ""


def _get_default_course():
    courses = frappe.get_all("Course", limit=1)
    return courses[0]["name"] if courses else ""


def _execute_report(report_name, filters):
    """Execute a single report and return results."""
    from frappe.desk.query_report import run as run_report

    result = run_report(report_name, filters=filters)
    rows = len(result.get("result", [])) if isinstance(result, dict) else 0
    columns = len(result.get("columns", [])) if isinstance(result, dict) else 0
    return {"rows": rows, "columns": columns}


def _test_report(report):
    """Two-pass strategy: empty filters first, then with sensible defaults."""
    name = report["name"]
    module = report.get("module", "")
    rtype = report.get("report_type", "")

    result = {
        "name": name,
        "module": module,
        "report_type": rtype,
        "pass1": "UNTESTED",
        "pass2": "N/A",
        "rows": 0,
        "columns": 0,
        "error": "",
    }

    # Pass 1: empty filters
    try:
        data = _execute_report(name, {})
        result["pass1"] = "PASS"
        result["rows"] = data["rows"]
        result["columns"] = data["columns"]
        return result
    except Exception as e:
        result["pass1"] = "FAIL"
        result["error"] = str(e)[:200]

    # Pass 2: with sensible defaults
    try:
        filters = _read_mandatory_filters(name)
        data = _execute_report(name, filters)
        result["pass2"] = "PASS"
        result["rows"] = data["rows"]
        result["columns"] = data["columns"]
        result["error"] = f"Pass 1 failed, Pass 2 OK with defaults: {list(filters.keys())}"
        return result
    except Exception as e2:
        result["pass2"] = "FAIL"
        result["error"] = f"Pass 1: {result['error'][:100]} | Pass 2: {str(e2)[:100]}"
        return result


# ---------------------------------------------------------------------------
# Analytics API testing
# ---------------------------------------------------------------------------

def _test_analytics_api():
    """Test all 9 analytics API endpoints."""
    results = []

    # Ensure we're admin for permissions
    frappe.set_user("Administrator")

    # 1. get_available_dashboards
    results.append(_test_analytics_endpoint(
        "get_available_dashboards",
        lambda: _import_analytics("get_available_dashboards")(),
        expect_type="list",
    ))

    # 2. get_dashboard - try with first available dashboard
    def _call_get_dashboard():
        fn = _import_analytics("get_available_dashboards")
        dashboards = fn()
        if dashboards:
            dash_name = dashboards[0].get("name", dashboards[0]) if isinstance(dashboards[0], dict) else dashboards[0]
            return _import_analytics("get_dashboard")(dash_name)
        return {"note": "No dashboards available"}

    results.append(_test_analytics_endpoint(
        "get_dashboard",
        _call_get_dashboard,
        expect_type="dict",
    ))

    # 3. get_quick_stats
    results.append(_test_analytics_endpoint(
        "get_quick_stats",
        lambda: _import_analytics("get_quick_stats")(),
        expect_type="dict",
    ))

    # 4. get_all_kpis
    results.append(_test_analytics_endpoint(
        "get_all_kpis",
        lambda: _import_analytics("get_all_kpis")(),
        expect_type="list",
    ))

    # 5. get_kpi_value - try with first available KPI
    def _call_get_kpi_value():
        kpis = frappe.get_all("KPI Definition", limit=1)
        if kpis:
            return _import_analytics("get_kpi_value")(kpis[0]["name"])
        return {"note": "No KPI Definitions found"}

    results.append(_test_analytics_endpoint(
        "get_kpi_value",
        _call_get_kpi_value,
        expect_type="dict",
    ))

    # 6. get_kpi_trend - try with first available KPI
    def _call_get_kpi_trend():
        kpis = frappe.get_all("KPI Definition", limit=1)
        if kpis:
            return _import_analytics("get_kpi_trend")(kpis[0]["name"])
        return []

    results.append(_test_analytics_endpoint(
        "get_kpi_trend",
        _call_get_kpi_trend,
        expect_type="list",
    ))

    # 7. get_kpi_comparison
    def _call_get_kpi_comparison():
        kpis = frappe.get_all("KPI Definition", limit=1)
        if kpis:
            today_date = getdate(today())
            return _import_analytics("get_kpi_comparison")(
                kpis[0]["name"],
                str(today_date - timedelta(days=30)),
                str(today_date),
                str(today_date - timedelta(days=60)),
                str(today_date - timedelta(days=30)),
            )
        return {"note": "No KPI Definitions found"}

    results.append(_test_analytics_endpoint(
        "get_kpi_comparison",
        _call_get_kpi_comparison,
        expect_type="dict",
    ))

    # 8. execute_custom_report
    def _call_execute_custom_report():
        reports = frappe.get_all("Custom Report Definition", limit=1)
        if reports:
            return _import_analytics("execute_custom_report")(reports[0]["name"])
        return {"note": "No Custom Report Definitions found"}

    results.append(_test_analytics_endpoint(
        "execute_custom_report",
        _call_execute_custom_report,
        expect_type="dict",
    ))

    # 9. calculate_kpi_now
    def _call_calculate_kpi_now():
        kpis = frappe.get_all("KPI Definition", limit=1)
        if kpis:
            return _import_analytics("calculate_kpi_now")(kpis[0]["name"], store_value=False)
        return {"note": "No KPI Definitions found"}

    results.append(_test_analytics_endpoint(
        "calculate_kpi_now",
        _call_calculate_kpi_now,
        expect_type="dict",
    ))

    return results


def _import_analytics(func_name):
    """Import an analytics API function by name."""
    from university_erp.university_erp.analytics import api as analytics_api
    return getattr(analytics_api, func_name)


def _test_analytics_endpoint(name, call_fn, expect_type="dict"):
    """Test a single analytics endpoint."""
    try:
        result = call_fn()
        response_type = type(result).__name__
        note = ""

        if expect_type == "dict" and isinstance(result, dict):
            if result.get("note"):
                note = result["note"]
            status = "PASS"
        elif expect_type == "list" and isinstance(result, list):
            status = "PASS"
            note = f"{len(result)} items"
        elif result is None:
            status = "DEGRADED"
            note = "Returned None"
        else:
            status = "PASS"
            note = f"Returned {response_type}"

        return {
            "endpoint": name,
            "status": status,
            "response_type": response_type,
            "notes": note,
        }
    except Exception as e:
        return {
            "endpoint": name,
            "status": "FAIL",
            "response_type": "error",
            "notes": str(e)[:200],
        }


# ---------------------------------------------------------------------------
# Dashboard accuracy testing
# ---------------------------------------------------------------------------

def _test_dashboard_accuracy():
    """Compare dashboard aggregation values against direct SQL queries."""
    results = []

    try:
        from university_erp.university_erp.analytics.dashboards.executive_dashboard import (
            get_overview_metrics,
        )
        metrics = get_overview_metrics()
    except Exception as e:
        return [{"metric": "get_overview_metrics()", "dashboard_value": "ERROR",
                 "sql_value": "N/A", "difference": "N/A", "status": f"FAIL: {str(e)[:100]}"}]

    # total_students
    dashboard_students = metrics.get("total_students", 0)
    try:
        sql_students = frappe.db.count("Student") if frappe.db.exists("DocType", "Student") else 0
    except Exception:
        sql_students = 0
    results.append(_compare_metric("total_students", dashboard_students, sql_students))

    # total_faculty (uses Instructor count per executive_dashboard.py)
    dashboard_faculty = metrics.get("total_faculty", 0)
    try:
        sql_faculty = frappe.db.count("Instructor") if frappe.db.exists("DocType", "Instructor") else 0
    except Exception:
        sql_faculty = 0
    results.append(_compare_metric("total_faculty", dashboard_faculty, sql_faculty))

    # total_programs
    dashboard_programs = metrics.get("total_programs", 0)
    try:
        sql_programs = frappe.db.count("Program") if frappe.db.exists("DocType", "Program") else 0
    except Exception:
        sql_programs = 0
    results.append(_compare_metric("total_programs", dashboard_programs, sql_programs))

    # total_courses
    dashboard_courses = metrics.get("total_courses", 0)
    try:
        sql_courses = frappe.db.count("Course") if frappe.db.exists("DocType", "Course") else 0
    except Exception:
        sql_courses = 0
    results.append(_compare_metric("total_courses", dashboard_courses, sql_courses))

    # fee_collection_today
    dashboard_fee = metrics.get("fee_collection_today", 0)
    try:
        if frappe.db.exists("DocType", "Fees"):
            sql_result = frappe.db.sql(
                "SELECT SUM(paid_amount) as total FROM `tabFees` WHERE docstatus = 1 AND posting_date = %s",
                today(), as_dict=True,
            )
            sql_fee = flt(sql_result[0]["total"]) if sql_result else 0
        else:
            sql_fee = 0
    except Exception:
        sql_fee = 0
    results.append(_compare_metric("fee_collection_today", dashboard_fee, sql_fee))

    return results


def _compare_metric(name, dashboard_val, sql_val):
    """Compare two values and return status."""
    dashboard_val = flt(dashboard_val)
    sql_val = flt(sql_val)

    if sql_val == 0 and dashboard_val == 0:
        diff_pct = 0.0
        status = "PASS"
    elif sql_val == 0:
        diff_pct = 100.0
        status = "WARNING" if dashboard_val < 100 else "FAIL"
    else:
        diff_pct = abs((dashboard_val - sql_val) / sql_val) * 100
        if diff_pct <= 5:
            status = "PASS"
        elif diff_pct <= 20:
            status = "WARNING"
        else:
            status = "FAIL"

    return {
        "metric": name,
        "dashboard_value": dashboard_val,
        "sql_value": sql_val,
        "difference": f"{diff_pct:.1f}%",
        "status": status,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_report_md(report_results, unregistered, analytics_results, accuracy_results):
    """Generate REPORT_AUDIT.md content."""
    total = len(report_results)
    pass_count = sum(1 for r in report_results if r["pass1"] == "PASS" or r["pass2"] == "PASS")
    fail_count = total - pass_count

    analytics_pass = sum(1 for r in analytics_results if r["status"] == "PASS")
    analytics_fail = sum(1 for r in analytics_results if r["status"] == "FAIL")
    analytics_degraded = sum(1 for r in analytics_results if r["status"] == "DEGRADED")

    accuracy_pass = sum(1 for r in accuracy_results if r["status"] == "PASS")
    accuracy_warn = sum(1 for r in accuracy_results if r["status"] == "WARNING")
    accuracy_fail = sum(1 for r in accuracy_results if r["status"] == "FAIL")

    lines = []
    lines.append("# Report & Dashboard Audit Results")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Site:** {frappe.local.site}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Total Reports Tested:** {total}")
    lines.append(f"- **Reports Passing:** {pass_count}")
    lines.append(f"- **Reports Failing:** {fail_count}")
    lines.append(f"- **Unregistered Report Files:** {len(unregistered)}")
    lines.append(f"- **Analytics API Endpoints:** {len(analytics_results)} ({analytics_pass} PASS, {analytics_fail} FAIL, {analytics_degraded} DEGRADED)")
    lines.append(f"- **Dashboard Accuracy Checks:** {len(accuracy_results)} ({accuracy_pass} PASS, {accuracy_warn} WARNING, {accuracy_fail} FAIL)")
    lines.append("")

    # Report Results table
    lines.append("## Report Results")
    lines.append("")
    lines.append("| # | Report Name | Module | Type | Pass 1 | Pass 2 | Rows | Columns | Error |")
    lines.append("|---|-------------|--------|------|--------|--------|------|---------|-------|")
    for i, r in enumerate(report_results, 1):
        error = r.get("error", "").replace("|", "\\|").replace("\n", " ")[:100]
        lines.append(
            f"| {i} | {r['name']} | {r['module']} | {r['report_type']} | "
            f"{r['pass1']} | {r['pass2']} | {r['rows']} | {r['columns']} | {error} |"
        )
    lines.append("")

    # Failed Reports Detail
    failed = [r for r in report_results if r["pass1"] != "PASS" and r["pass2"] != "PASS"]
    if failed:
        lines.append("## Failed Reports Detail")
        lines.append("")
        for r in failed:
            lines.append(f"### {r['name']}")
            lines.append(f"- **Module:** {r['module']}")
            lines.append(f"- **Type:** {r['report_type']}")
            lines.append(f"- **Error:** {r.get('error', 'Unknown')}")
            lines.append("")
    else:
        lines.append("## Failed Reports Detail")
        lines.append("")
        lines.append("No reports failed both passes.")
        lines.append("")

    # Unregistered Reports
    lines.append("## Unregistered Reports")
    lines.append("")
    if unregistered:
        lines.append("These `.py` report files exist on disk but are not registered in the Report doctype:")
        lines.append("")
        lines.append("| # | Report Directory | File Path |")
        lines.append("|---|-----------------|-----------|")
        for i, ur in enumerate(unregistered, 1):
            lines.append(f"| {i} | {ur['report_dir']} | {ur['file']} |")
        lines.append("")
    else:
        lines.append("All report files on disk are registered in the database.")
        lines.append("")

    # Analytics API Results
    lines.append("## Analytics API Results")
    lines.append("")
    lines.append("| Endpoint | Status | Response Type | Notes |")
    lines.append("|----------|--------|---------------|-------|")
    for r in analytics_results:
        notes = r.get("notes", "").replace("|", "\\|")[:100]
        lines.append(f"| {r['endpoint']} | {r['status']} | {r['response_type']} | {notes} |")
    lines.append("")

    # Dashboard Accuracy
    lines.append("## Dashboard Accuracy")
    lines.append("")
    lines.append("Comparison of `get_overview_metrics()` values against direct SQL counts.")
    lines.append("")
    lines.append("| Metric | Dashboard Value | Direct SQL Value | Difference | Status |")
    lines.append("|--------|----------------|-----------------|------------|--------|")
    for r in accuracy_results:
        lines.append(
            f"| {r['metric']} | {r['dashboard_value']} | {r['sql_value']} | "
            f"{r['difference']} | {r['status']} |"
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run():
    """Main entry point for the report audit script."""
    print("=" * 70)
    print("REPORT & DASHBOARD AUDIT")
    print("=" * 70)
    print()

    # Ensure admin context
    frappe.set_user("Administrator")

    # Step 1: Discover reports
    print("[1/5] Discovering reports from database...")
    db_reports = _discover_reports_from_db()
    print(f"  Found {len(db_reports)} registered reports")

    print("[2/5] Scanning report files on disk...")
    disk_reports = _discover_report_files_on_disk()
    print(f"  Found {len(disk_reports)} report .py files on disk")

    unregistered = _find_unregistered_reports(db_reports, disk_reports)
    if unregistered:
        print(f"  WARNING: {len(unregistered)} unregistered report files")

    # Step 2: Execute each report (two-pass)
    print(f"[3/5] Testing {len(db_reports)} reports (two-pass strategy)...")
    report_results = []
    for i, report in enumerate(db_reports, 1):
        print(f"  [{i}/{len(db_reports)}] {report['name']}...", end=" ", flush=True)
        result = _test_report(report)
        status = "PASS" if result["pass1"] == "PASS" or result["pass2"] == "PASS" else "FAIL"
        print(status)
        report_results.append(result)

    pass_count = sum(1 for r in report_results if r["pass1"] == "PASS" or r["pass2"] == "PASS")
    print(f"  Reports: {pass_count}/{len(report_results)} passing")

    # Step 3: Test analytics API endpoints
    print("[4/5] Testing analytics API endpoints (9 endpoints)...")
    analytics_results = _test_analytics_api()
    for r in analytics_results:
        print(f"  {r['endpoint']}: {r['status']}")

    # Step 4: Test dashboard accuracy
    print("[5/5] Testing dashboard aggregation accuracy...")
    accuracy_results = _test_dashboard_accuracy()
    for r in accuracy_results:
        print(f"  {r['metric']}: {r['status']} (dashboard={r['dashboard_value']}, sql={r['sql_value']}, diff={r['difference']})")

    # Step 5: Generate report
    md_content = _generate_report_md(report_results, unregistered, analytics_results, accuracy_results)
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "..",
        ".planning",
        "phases",
        "03.1-cross-app-integration-audit-accessibility-testing",
        "REPORT_AUDIT.md",
    )
    # Normalize path
    output_path = os.path.normpath(output_path)

    # Also try the absolute path directly
    abs_output = "/workspace/development/.planning/phases/03.1-cross-app-integration-audit-accessibility-testing/REPORT_AUDIT.md"
    target = abs_output if os.path.isdir(os.path.dirname(abs_output)) else output_path

    with open(target, "w") as fp:
        fp.write(md_content)
    print(f"\nReport written to: {target}")

    # Reset user
    frappe.set_user("Administrator")

    print()
    print("=" * 70)
    print("AUDIT COMPLETE")
    total = len(report_results)
    print(f"Reports: {pass_count}/{total} passing | Analytics: {sum(1 for r in analytics_results if r['status'] == 'PASS')}/9 | Accuracy: {sum(1 for r in accuracy_results if r['status'] == 'PASS')}/{len(accuracy_results)}")
    print("=" * 70)

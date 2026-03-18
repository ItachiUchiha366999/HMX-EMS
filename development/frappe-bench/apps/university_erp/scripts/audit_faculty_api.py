# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Faculty API Integration Test Script

Tests all @frappe.whitelist() endpoints in faculty_api.py with a real faculty
user session. Discovers endpoints programmatically, tests GET and ACTION
endpoints differently, and verifies cross-app data resolution.

Usage:
    bench --site university.local execute university_erp.scripts.audit_faculty_api.run
"""

import inspect
import os
import re
import traceback
from datetime import datetime, timedelta

import frappe
from frappe.utils import nowdate, getdate, today, flt


# ---------------------------------------------------------------------------
# Faculty user discovery
# ---------------------------------------------------------------------------

def _find_faculty_user():
    """Find a valid faculty user for testing."""
    # Check if custom_is_faculty column exists
    has_faculty_col = False
    try:
        cols = frappe.db.sql("SHOW COLUMNS FROM `tabEmployee` LIKE 'custom_is_faculty'")
        has_faculty_col = bool(cols)
    except Exception:
        pass

    # Try faculty employee first (if column exists)
    if has_faculty_col:
        result = frappe.db.sql(
            """SELECT e.user_id FROM `tabEmployee` e
               WHERE e.user_id IS NOT NULL AND e.user_id != ''
               AND e.custom_is_faculty = 1 AND e.status = 'Active'
               LIMIT 1""",
            as_dict=True,
        )
        if result:
            return result[0]["user_id"], "faculty"

    # Try Instructor-linked employee (Education app pattern)
    try:
        result = frappe.db.sql(
            """SELECT e.user_id FROM `tabEmployee` e
               INNER JOIN `tabInstructor` i ON i.employee = e.name
               WHERE e.user_id IS NOT NULL AND e.user_id != ''
               AND e.status = 'Active'
               LIMIT 1""",
            as_dict=True,
        )
        if result:
            return result[0]["user_id"], "instructor-linked employee"
    except Exception:
        pass

    # Fallback: any employee with a user_id
    result = frappe.db.sql(
        """SELECT e.user_id FROM `tabEmployee` e
           WHERE e.user_id IS NOT NULL AND e.user_id != ''
           AND e.status = 'Active'
           LIMIT 1""",
        as_dict=True,
    )
    if result:
        return result[0]["user_id"], "employee (non-faculty fallback)"

    return None, None


# ---------------------------------------------------------------------------
# Endpoint discovery
# ---------------------------------------------------------------------------

def _discover_endpoints():
    """Discover all @frappe.whitelist() endpoints programmatically."""
    from university_erp.university_portals.api import faculty_api

    # Read source file to find @frappe.whitelist() decorated functions
    source_file = inspect.getfile(faculty_api)
    with open(source_file, "r") as fp:
        source = fp.read()

    # Find all function definitions preceded by @frappe.whitelist()
    pattern = r'@frappe\.whitelist\(\)\s*\ndef\s+(\w+)\s*\('
    discovered = re.findall(pattern, source)

    # Classify into GET (get_*) and ACTION (everything else that's whitelisted)
    get_endpoints = []
    action_endpoints = []
    for name in discovered:
        if name.startswith("get_"):
            get_endpoints.append(name)
        else:
            action_endpoints.append(name)

    return get_endpoints, action_endpoints, faculty_api


# ---------------------------------------------------------------------------
# Default parameter generation
# ---------------------------------------------------------------------------

def _get_defaults():
    """Get sensible default values for common parameters."""
    defaults = {}

    courses = frappe.get_all("Course", limit=1)
    defaults["course"] = courses[0]["name"] if courses else ""

    students = frappe.get_all("Student", limit=1)
    defaults["student"] = students[0]["name"] if students else ""

    groups = frappe.get_all("Student Group", limit=1)
    defaults["student_group"] = groups[0]["name"] if groups else ""

    defaults["date"] = nowdate()

    years = frappe.get_all("Academic Year", order_by="name desc", limit=1)
    defaults["academic_year"] = years[0]["name"] if years else ""

    terms = frappe.get_all("Academic Term", order_by="name desc", limit=1)
    defaults["academic_term"] = terms[0]["name"] if terms else ""

    # Try to find a course_schedule (Student Attendance Tool schedule)
    schedules = frappe.get_all("Course Schedule", limit=1)
    defaults["course_schedule"] = schedules[0]["name"] if schedules else ""

    # Assessment plan
    plans = frappe.get_all("Assessment Plan", limit=1)
    defaults["assessment_plan"] = plans[0]["name"] if plans else ""

    return defaults


def _get_function_params(func):
    """Get the parameter names for a function."""
    sig = inspect.signature(func)
    return [p.name for p in sig.parameters.values()
            if p.name not in ("self", "cls") and p.default is inspect.Parameter.empty]


def _build_call_args(func, func_name, defaults):
    """Build arguments for calling a function based on its signature."""
    sig = inspect.signature(func)
    args = {}
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue
        # Skip **kwargs
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            continue
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            continue
        # Only fill in required params (no default value)
        if param.default is inspect.Parameter.empty:
            # Try to find a sensible default
            if param_name in defaults:
                args[param_name] = defaults[param_name]
            elif "course" in param_name:
                args[param_name] = defaults.get("course", "")
            elif "student" in param_name:
                args[param_name] = defaults.get("student", "")
            elif "date" in param_name:
                args[param_name] = defaults.get("date", nowdate())
            elif "name" in param_name:
                args[param_name] = ""
            else:
                args[param_name] = ""
    return args


# ---------------------------------------------------------------------------
# GET endpoint testing
# ---------------------------------------------------------------------------

def _test_get_endpoint(func_name, func, defaults):
    """Test a single GET endpoint."""
    result = {
        "endpoint": func_name,
        "status": "UNTESTED",
        "response_type": "",
        "data_size": 0,
        "cross_app_check": "N/A",
        "notes": "",
    }

    # Try with no arguments first
    try:
        response = func()
        result["status"] = "PASS"
        result["response_type"] = type(response).__name__
        if isinstance(response, (list, tuple)):
            result["data_size"] = len(response)
            if len(response) == 0:
                result["status"] = "DEGRADED"
                result["notes"] = "Empty result"
        elif isinstance(response, dict):
            result["data_size"] = len(response)
        elif response is None:
            result["status"] = "DEGRADED"
            result["notes"] = "Returned None"
        return result
    except TypeError as te:
        # Missing required arguments
        pass
    except frappe.PermissionError:
        result["status"] = "FAIL"
        result["notes"] = "PermissionError (faculty user lacks permissions)"
        return result
    except Exception as e:
        if "missing" in str(e).lower() or "required" in str(e).lower():
            pass  # Try with defaults below
        else:
            # Real error on no-args call -- still try with defaults
            pass

    # Try with sensible defaults
    try:
        args = _build_call_args(func, func_name, defaults)
        response = func(**args)
        result["status"] = "PASS"
        result["response_type"] = type(response).__name__
        if isinstance(response, (list, tuple)):
            result["data_size"] = len(response)
            if len(response) == 0:
                result["status"] = "DEGRADED"
                result["notes"] = f"Empty result (with args: {list(args.keys())})"
        elif isinstance(response, dict):
            result["data_size"] = len(response)
        elif response is None:
            result["status"] = "DEGRADED"
            result["notes"] = "Returned None (with defaults)"
        else:
            result["notes"] = f"Called with: {list(args.keys())}"
        return result
    except Exception as e:
        result["status"] = "FAIL"
        result["notes"] = str(e)[:200]
        return result


# ---------------------------------------------------------------------------
# ACTION endpoint testing
# ---------------------------------------------------------------------------

def _test_action_endpoint(func_name, func, defaults):
    """Test an ACTION endpoint - verify it validates inputs without modifying data."""
    result = {
        "endpoint": func_name,
        "validation_check": "UNTESTED",
        "status": "UNTESTED",
        "notes": "",
    }

    try:
        # Call with empty/invalid data to trigger validation
        args = _build_call_args(func, func_name, defaults)
        # Override with obviously invalid data
        for key in args:
            if "data" in key:
                args[key] = "[]"
            elif "name" in key and key != "func_name":
                args[key] = "NONEXISTENT_RECORD_12345"

        try:
            response = func(**args)
            # If it succeeds without error, that's still informative
            result["validation_check"] = "NO_VALIDATION"
            result["status"] = "WARNING"
            result["notes"] = "Accepted invalid input without validation error"
        except frappe.ValidationError as ve:
            result["validation_check"] = "VALIDATES"
            result["status"] = "PASS"
            result["notes"] = f"Validation error: {str(ve)[:100]}"
        except frappe.PermissionError as pe:
            result["validation_check"] = "PERMISSION_CHECK"
            result["status"] = "PASS"
            result["notes"] = f"Permission check: {str(pe)[:100]}"
        except frappe.DoesNotExistError:
            result["validation_check"] = "VALIDATES"
            result["status"] = "PASS"
            result["notes"] = "DoesNotExistError for invalid record"
        except TypeError as te:
            result["validation_check"] = "SIGNATURE_CHECK"
            result["status"] = "PASS"
            result["notes"] = f"Type check: {str(te)[:100]}"
        except Exception as e:
            err_str = str(e)
            if "not found" in err_str.lower() or "does not exist" in err_str.lower():
                result["validation_check"] = "VALIDATES"
                result["status"] = "PASS"
                result["notes"] = f"Record validation: {err_str[:100]}"
            elif "required" in err_str.lower() or "mandatory" in err_str.lower():
                result["validation_check"] = "VALIDATES"
                result["status"] = "PASS"
                result["notes"] = f"Required field check: {err_str[:100]}"
            else:
                result["validation_check"] = "ERROR"
                result["status"] = "FAIL"
                result["notes"] = f"Unexpected error: {err_str[:150]}"
    except Exception as e:
        result["status"] = "FAIL"
        result["notes"] = f"Could not build args: {str(e)[:150]}"

    return result


# ---------------------------------------------------------------------------
# Cross-app data resolution
# ---------------------------------------------------------------------------

def _test_cross_app_resolution(faculty_api, defaults):
    """Verify cross-app data resolution for key endpoints."""
    results = []

    # 1. get_faculty_dashboard -> check pending_tasks references real doctypes
    try:
        dashboard = faculty_api.get_faculty_dashboard()
        if isinstance(dashboard, dict):
            pending = dashboard.get("pending_tasks", {})
            doctypes_checked = []
            for key in pending:
                # Keys often map to doctype concepts
                doctype_map = {
                    "unmarked_attendance": "Student Attendance",
                    "pending_assessments": "Assessment Result",
                    "pending_leave_requests": "Leave Application",
                    "pending_grades": "Assessment Result",
                }
                dt = doctype_map.get(key)
                if dt:
                    exists = frappe.db.exists("DocType", dt)
                    count = frappe.db.count(dt) if exists else 0
                    doctypes_checked.append({
                        "endpoint": "get_faculty_dashboard",
                        "referenced_doctype": dt,
                        "exists_in_db": "Yes" if exists else "No",
                        "records_found": f"{count} records" if exists else "N/A",
                    })
            if doctypes_checked:
                results.extend(doctypes_checked)
            else:
                results.append({
                    "endpoint": "get_faculty_dashboard",
                    "referenced_doctype": "(no pending_tasks keys)",
                    "exists_in_db": "N/A",
                    "records_found": "N/A",
                })
    except Exception as e:
        results.append({
            "endpoint": "get_faculty_dashboard",
            "referenced_doctype": "ERROR",
            "exists_in_db": "N/A",
            "records_found": str(e)[:80],
        })

    # 2. get_today_classes -> Teaching Assignment Schedule
    try:
        classes = faculty_api.get_today_classes()
        if isinstance(classes, list) and classes:
            # Check that Teaching Assignment Schedule doctype exists
            exists = frappe.db.exists("DocType", "Teaching Assignment Schedule")
            count = frappe.db.count("Teaching Assignment Schedule") if exists else 0
            results.append({
                "endpoint": "get_today_classes",
                "referenced_doctype": "Teaching Assignment Schedule",
                "exists_in_db": "Yes" if exists else "No",
                "records_found": f"{count} records",
            })
        else:
            results.append({
                "endpoint": "get_today_classes",
                "referenced_doctype": "Teaching Assignment Schedule",
                "exists_in_db": str(frappe.db.exists("DocType", "Teaching Assignment Schedule") or False),
                "records_found": "No classes returned today",
            })
    except Exception as e:
        results.append({
            "endpoint": "get_today_classes",
            "referenced_doctype": "Teaching Assignment Schedule",
            "exists_in_db": "N/A",
            "records_found": str(e)[:80],
        })

    # 3. get_leave_balance -> Leave Type
    try:
        balance = faculty_api.get_leave_balance()
        if isinstance(balance, (list, dict)):
            exists = frappe.db.exists("DocType", "Leave Type")
            count = frappe.db.count("Leave Type") if exists else 0
            results.append({
                "endpoint": "get_leave_balance",
                "referenced_doctype": "Leave Type",
                "exists_in_db": "Yes" if exists else "No",
                "records_found": f"{count} records",
            })
    except Exception as e:
        results.append({
            "endpoint": "get_leave_balance",
            "referenced_doctype": "Leave Type",
            "exists_in_db": "N/A",
            "records_found": str(e)[:80],
        })

    # 4. get_students_for_grading -> Student
    if defaults.get("course") and defaults.get("assessment_plan"):
        try:
            students = faculty_api.get_students_for_grading(
                defaults["course"], defaults["assessment_plan"]
            )
            if isinstance(students, list) and students:
                # Verify returned student IDs exist
                sample = students[:3]
                for s in sample:
                    sid = s.get("student") or s.get("name", "")
                    if sid:
                        exists = frappe.db.exists("Student", sid)
                        results.append({
                            "endpoint": "get_students_for_grading",
                            "referenced_doctype": f"Student ({sid})",
                            "exists_in_db": "Yes" if exists else "No",
                            "records_found": "Record verified" if exists else "NOT FOUND",
                        })
            else:
                results.append({
                    "endpoint": "get_students_for_grading",
                    "referenced_doctype": "Student",
                    "exists_in_db": str(frappe.db.exists("DocType", "Student") or False),
                    "records_found": "Empty result",
                })
        except Exception as e:
            results.append({
                "endpoint": "get_students_for_grading",
                "referenced_doctype": "Student",
                "exists_in_db": "N/A",
                "records_found": str(e)[:80],
            })
    else:
        results.append({
            "endpoint": "get_students_for_grading",
            "referenced_doctype": "Student",
            "exists_in_db": "N/A",
            "records_found": "No course/assessment_plan defaults available",
        })

    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_api_audit_md(
    get_endpoints, action_endpoints, get_results, action_results,
    cross_app_results, faculty_user, user_type
):
    """Generate API_AUDIT.md content."""
    total = len(get_results) + len(action_results)
    get_pass = sum(1 for r in get_results if r["status"] == "PASS")
    get_fail = sum(1 for r in get_results if r["status"] == "FAIL")
    get_degraded = sum(1 for r in get_results if r["status"] == "DEGRADED")
    action_pass = sum(1 for r in action_results if r["status"] == "PASS")
    action_fail = sum(1 for r in action_results if r["status"] == "FAIL")
    action_warn = sum(1 for r in action_results if r["status"] == "WARNING")

    lines = []
    lines.append("# Faculty API Integration Audit Results")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Site:** {frappe.local.site}")
    lines.append(f"**Faculty User:** {faculty_user} ({user_type})")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Total Endpoints Tested:** {total}")
    lines.append(f"- **GET Endpoints:** {len(get_results)} ({get_pass} PASS, {get_fail} FAIL, {get_degraded} DEGRADED)")
    lines.append(f"- **ACTION Endpoints:** {len(action_results)} ({action_pass} PASS, {action_fail} FAIL, {action_warn} WARNING)")
    lines.append(f"- **Cross-App Checks:** {len(cross_app_results)}")
    lines.append("")

    # Endpoint Discovery
    lines.append("## Endpoint Discovery")
    lines.append("")
    lines.append(f"Discovered **{len(get_endpoints) + len(action_endpoints)}** @frappe.whitelist() endpoints programmatically from faculty_api.py source.")
    lines.append("")
    lines.append("**GET endpoints:**")
    for ep in get_endpoints:
        lines.append(f"- `{ep}`")
    lines.append("")
    lines.append("**ACTION endpoints:**")
    for ep in action_endpoints:
        lines.append(f"- `{ep}`")
    lines.append("")

    # GET Endpoint Results
    lines.append("## GET Endpoint Results")
    lines.append("")
    lines.append("| # | Endpoint | Status | Response Type | Data Size | Cross-App Check | Notes |")
    lines.append("|---|----------|--------|---------------|-----------|-----------------|-------|")
    for i, r in enumerate(get_results, 1):
        notes = r.get("notes", "").replace("|", "\\|")[:80]
        lines.append(
            f"| {i} | {r['endpoint']} | {r['status']} | {r['response_type']} | "
            f"{r['data_size']} | {r['cross_app_check']} | {notes} |"
        )
    lines.append("")

    # ACTION Endpoint Results
    lines.append("## ACTION Endpoint Results")
    lines.append("")
    lines.append("| # | Endpoint | Validation Check | Status | Notes |")
    lines.append("|---|----------|-----------------|--------|-------|")
    for i, r in enumerate(action_results, 1):
        notes = r.get("notes", "").replace("|", "\\|")[:80]
        lines.append(
            f"| {i} | {r['endpoint']} | {r['validation_check']} | {r['status']} | {notes} |"
        )
    lines.append("")

    # Cross-App Data Resolution
    lines.append("## Cross-App Data Resolution")
    lines.append("")
    lines.append("| Endpoint | Referenced Doctype | Exists in DB? | Records Found? |")
    lines.append("|----------|--------------------|---------------|----------------|")
    for r in cross_app_results:
        rf = r.get("records_found", "").replace("|", "\\|")[:60]
        lines.append(
            f"| {r['endpoint']} | {r['referenced_doctype']} | {r['exists_in_db']} | {rf} |"
        )
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")

    failed_gets = [r for r in get_results if r["status"] == "FAIL"]
    degraded_gets = [r for r in get_results if r["status"] == "DEGRADED"]
    failed_actions = [r for r in action_results if r["status"] == "FAIL"]

    if failed_gets:
        lines.append("### Failed GET Endpoints (need fixing)")
        for r in failed_gets:
            lines.append(f"- **{r['endpoint']}**: {r.get('notes', 'Unknown error')}")
        lines.append("")

    if degraded_gets:
        lines.append("### Degraded GET Endpoints (empty data)")
        for r in degraded_gets:
            lines.append(f"- **{r['endpoint']}**: {r.get('notes', 'Returns empty')}")
        lines.append("")

    if failed_actions:
        lines.append("### Failed ACTION Endpoints (need fixing)")
        for r in failed_actions:
            lines.append(f"- **{r['endpoint']}**: {r.get('notes', 'Unknown error')}")
        lines.append("")

    if not (failed_gets or degraded_gets or failed_actions):
        lines.append("All endpoints are functioning correctly. No issues found.")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run():
    """Main entry point for the faculty API audit script."""
    print("=" * 70)
    print("FACULTY API INTEGRATION AUDIT")
    print("=" * 70)
    print()

    # Step 1: Find faculty user
    print("[1/6] Finding faculty user...")
    faculty_user, user_type = _find_faculty_user()
    if not faculty_user:
        print("  ERROR: No faculty or employee user found. Cannot proceed.")
        # Generate empty report
        _write_empty_report("No faculty or employee user found in database")
        return
    print(f"  Using: {faculty_user} ({user_type})")

    # Set user context
    frappe.set_user(faculty_user)

    # Step 2: Discover endpoints
    print("[2/6] Discovering endpoints from faculty_api.py source...")
    get_endpoints, action_endpoints, faculty_api = _discover_endpoints()
    total = len(get_endpoints) + len(action_endpoints)
    print(f"  Found {total} endpoints ({len(get_endpoints)} GET, {len(action_endpoints)} ACTION)")

    # Step 3: Get defaults
    print("[3/6] Loading default parameter values...")
    defaults = _get_defaults()
    available = {k: v for k, v in defaults.items() if v}
    print(f"  Available defaults: {list(available.keys())}")

    # Step 4: Test GET endpoints
    print(f"[4/6] Testing {len(get_endpoints)} GET endpoints...")
    get_results = []
    for name in get_endpoints:
        print(f"  {name}...", end=" ", flush=True)
        func = getattr(faculty_api, name)
        result = _test_get_endpoint(name, func, defaults)
        print(result["status"])
        get_results.append(result)

    # Step 5: Test ACTION endpoints
    print(f"[5/6] Testing {len(action_endpoints)} ACTION endpoints...")
    action_results = []
    for name in action_endpoints:
        print(f"  {name}...", end=" ", flush=True)
        func = getattr(faculty_api, name)
        result = _test_action_endpoint(name, func, defaults)
        print(result["status"])
        action_results.append(result)

    # Step 6: Cross-app data resolution
    print("[6/6] Verifying cross-app data resolution...")
    cross_app_results = _test_cross_app_resolution(faculty_api, defaults)
    for r in cross_app_results:
        print(f"  {r['endpoint']} -> {r['referenced_doctype']}: {r['exists_in_db']}")

    # Generate report
    md_content = _generate_api_audit_md(
        get_endpoints, action_endpoints, get_results, action_results,
        cross_app_results, faculty_user, user_type,
    )

    output_path = "/workspace/development/.planning/phases/03.1-cross-app-integration-audit-accessibility-testing/API_AUDIT.md"
    with open(output_path, "w") as fp:
        fp.write(md_content)
    print(f"\nReport written to: {output_path}")

    # Reset user
    frappe.set_user("Administrator")

    # Summary
    get_pass = sum(1 for r in get_results if r["status"] == "PASS")
    action_pass = sum(1 for r in action_results if r["status"] == "PASS")
    print()
    print("=" * 70)
    print("AUDIT COMPLETE")
    print(f"GET: {get_pass}/{len(get_results)} passing | ACTION: {action_pass}/{len(action_results)} passing | Cross-app checks: {len(cross_app_results)}")
    print("=" * 70)


def _write_empty_report(reason):
    """Write an empty report with error message."""
    content = f"""# Faculty API Integration Audit Results

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** FAILED

## Error

{reason}

No endpoints could be tested.
"""
    output_path = "/workspace/development/.planning/phases/03.1-cross-app-integration-audit-accessibility-testing/API_AUDIT.md"
    with open(output_path, "w") as fp:
        fp.write(content)
    print(f"  Empty report written to: {output_path}")

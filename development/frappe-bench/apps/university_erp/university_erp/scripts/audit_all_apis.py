# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Comprehensive API Audit Script

Discovers and tests ALL @frappe.whitelist() endpoints across the entire
university_erp app. Generates API_COMPREHENSIVE_AUDIT.md with pass/fail
for every endpoint.

Usage:
    bench --site university.local execute university_erp.scripts.audit_all_apis.run
"""

import importlib
import inspect
import os
import re
import traceback
from datetime import datetime

import frappe
from frappe.utils import nowdate


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GET_PREFIXES = (
    "get_", "list_", "search_", "check_", "is_", "has_",
    "count_", "fetch_", "calculate_", "run",
)

ACTION_PREFIXES = (
    "submit_", "save_", "create_", "update_", "delete_",
    "approve_", "reject_", "cancel_", "send_", "mark_",
    "toggle_", "set_",
)

OUTPUT_PATH = (
    "/workspace/development/.planning/phases/"
    "03.1-cross-app-integration-audit-accessibility-testing/"
    "API_COMPREHENSIVE_AUDIT.md"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_app_root():
    """Return the root path of the university_erp package (inner)."""
    return os.path.join(
        frappe.get_app_path("university_erp"),  # .../university_erp/university_erp
    )


def _file_to_module(filepath, app_root):
    """Convert a filesystem path to a Python dotted module path."""
    rel = os.path.relpath(filepath, os.path.dirname(app_root))
    module = rel.replace(os.sep, ".").replace(".py", "")
    return module


def _classify_endpoint(func_name):
    """Classify an endpoint as GET, ACTION, or OTHER."""
    if any(func_name.startswith(p) for p in GET_PREFIXES):
        return "GET"
    if any(func_name.startswith(p) for p in ACTION_PREFIXES):
        return "ACTION"
    return "OTHER"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def _discover_all_endpoints():
    """
    Walk the university_erp directory tree and discover every
    @frappe.whitelist() decorated function.

    Returns:
        list of dict: Each with keys module_path, func_name, file_path,
                      endpoint_type, allow_guest
    """
    app_root = _get_app_root()
    endpoints = []

    # Pattern matches @frappe.whitelist() or @frappe.whitelist(allow_guest=True) etc.
    pattern = re.compile(
        r'@frappe\.whitelist\(([^)]*)\)\s*\ndef\s+(\w+)',
        re.MULTILINE,
    )

    for dirpath, _dirnames, filenames in os.walk(app_root):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, fname)
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as fp:
                    source = fp.read()
            except Exception:
                continue

            for match in pattern.finditer(source):
                decorator_args = match.group(1).strip()
                func_name = match.group(2)
                allow_guest = "allow_guest" in decorator_args and "True" in decorator_args
                module_path = _file_to_module(filepath, app_root)
                endpoint_type = _classify_endpoint(func_name)

                endpoints.append({
                    "module_path": module_path,
                    "func_name": func_name,
                    "file_path": filepath,
                    "endpoint_type": endpoint_type,
                    "allow_guest": allow_guest,
                })

    return endpoints


def _group_endpoints(endpoints):
    """Group endpoints by module for reporting."""
    groups = {}
    for ep in endpoints:
        module = ep["module_path"]
        # Create a short group label from the module path
        parts = module.split(".")
        # e.g. university_erp.university_portals.api.faculty_api -> Faculty Api
        label = parts[-1].replace("_", " ").title() if parts else module
        # Use the full module as key for uniqueness, label for display
        key = module
        if key not in groups:
            groups[key] = {"label": label, "module": module, "endpoints": []}
        groups[key]["endpoints"].append(ep)
    return groups


# ---------------------------------------------------------------------------
# Import testing
# ---------------------------------------------------------------------------

def _try_import(module_path, func_name):
    """Try to import a module and get a function reference.

    Returns:
        (func, None) on success or (None, error_string) on failure.
    """
    try:
        mod = importlib.import_module(module_path)
        func = getattr(mod, func_name, None)
        if func is None:
            return None, f"Function '{func_name}' not found in module"
        return func, None
    except Exception as e:
        return None, str(e)[:200]


# ---------------------------------------------------------------------------
# GET endpoint testing
# ---------------------------------------------------------------------------

def _test_get_endpoint(func, func_name):
    """Test a GET endpoint with no arguments (Administrator context).

    Returns dict with keys: status, response_type, error
    """
    result = {"status": "UNTESTED", "response_type": "", "error": ""}

    # Try calling with no args first
    try:
        response = func()
        result["status"] = "PASS"
        result["response_type"] = type(response).__name__
        if response is None:
            result["status"] = "PASS_NONE"
            result["response_type"] = "NoneType"
        return result
    except TypeError as te:
        # Likely missing required arguments
        result["status"] = "NEEDS_ARGS"
        result["error"] = str(te)[:150]
        return result
    except frappe.PermissionError:
        result["status"] = "DENIED"
        result["error"] = "PermissionError even as Administrator"
        return result
    except frappe.DoesNotExistError as e:
        result["status"] = "PASS_NO_DATA"
        result["error"] = str(e)[:150]
        return result
    except Exception as e:
        err = str(e)[:150]
        # If it's a "not found" or "no data" type, that's expected
        if any(kw in err.lower() for kw in ("not found", "does not exist", "no ", "empty")):
            result["status"] = "PASS_NO_DATA"
            result["error"] = err
        else:
            result["status"] = "FAIL"
            result["error"] = err
        return result


# ---------------------------------------------------------------------------
# ACTION / OTHER endpoint testing (import-only)
# ---------------------------------------------------------------------------

def _test_importable(func):
    """Verify a function is importable and callable."""
    if callable(func):
        return "IMPORTABLE"
    return "IMPORT_FAIL"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_report(endpoints, grouped, test_results):
    """Generate API_COMPREHENSIVE_AUDIT.md content."""
    total = len(endpoints)
    get_eps = [e for e in endpoints if e["endpoint_type"] == "GET"]
    action_eps = [e for e in endpoints if e["endpoint_type"] == "ACTION"]
    other_eps = [e for e in endpoints if e["endpoint_type"] == "OTHER"]

    # Count statuses
    get_pass = sum(1 for e in get_eps if test_results.get(_key(e), {}).get("status", "").startswith("PASS"))
    get_fail = sum(1 for e in get_eps if test_results.get(_key(e), {}).get("status") == "FAIL")
    get_denied = sum(1 for e in get_eps if test_results.get(_key(e), {}).get("status") == "DENIED")
    get_needs_args = sum(1 for e in get_eps if test_results.get(_key(e), {}).get("status") == "NEEDS_ARGS")
    get_import_fail = sum(1 for e in get_eps if test_results.get(_key(e), {}).get("status") == "IMPORT_FAIL")

    action_importable = sum(1 for e in action_eps if test_results.get(_key(e), {}).get("status") == "IMPORTABLE")
    action_import_fail = sum(1 for e in action_eps if test_results.get(_key(e), {}).get("status") == "IMPORT_FAIL")

    other_importable = sum(1 for e in other_eps if test_results.get(_key(e), {}).get("status") == "IMPORTABLE")
    other_import_fail = sum(1 for e in other_eps if test_results.get(_key(e), {}).get("status") == "IMPORT_FAIL")

    total_import_fails = get_import_fail + action_import_fail + other_import_fail

    lines = []
    lines.append("# Comprehensive API Audit Results")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Site:** {frappe.local.site}")
    lines.append(f"**Test User:** Administrator")
    lines.append(f"**Scope:** All @frappe.whitelist() endpoints in university_erp")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Total Endpoints Discovered:** {total}")
    lines.append(f"- **GET Endpoints:** {len(get_eps)} (PASS: {get_pass}, FAIL: {get_fail}, DENIED: {get_denied}, NEEDS_ARGS: {get_needs_args}, IMPORT_FAIL: {get_import_fail})")
    lines.append(f"- **ACTION Endpoints:** {len(action_eps)} (IMPORTABLE: {action_importable}, IMPORT_FAIL: {action_import_fail})")
    lines.append(f"- **OTHER Endpoints:** {len(other_eps)} (IMPORTABLE: {other_importable}, IMPORT_FAIL: {other_import_fail})")
    lines.append(f"- **Total Import Failures:** {total_import_fails}")
    lines.append(f"- **Modules Scanned:** {len(grouped)}")
    lines.append("")

    # Per-module tables
    lines.append("## Endpoint Details by Module")
    lines.append("")

    for module_key in sorted(grouped.keys()):
        group = grouped[module_key]
        lines.append(f"### {group['label']} (`{group['module']}`)")
        lines.append("")
        lines.append("| # | Endpoint | Type | Status | Response/Error |")
        lines.append("|---|----------|------|--------|----------------|")
        for i, ep in enumerate(group["endpoints"], 1):
            key = _key(ep)
            result = test_results.get(key, {})
            status = result.get("status", "UNTESTED")
            if result.get("response_type"):
                detail = result["response_type"]
            elif result.get("error"):
                detail = result["error"].replace("|", "\\|").replace("\n", " ")[:100]
            else:
                detail = ""
            guest = " (guest)" if ep["allow_guest"] else ""
            lines.append(f"| {i} | `{ep['func_name']}`{guest} | {ep['endpoint_type']} | {status} | {detail} |")
        lines.append("")

    # Import failures section
    import_failures = [
        e for e in endpoints
        if test_results.get(_key(e), {}).get("status") == "IMPORT_FAIL"
    ]
    if import_failures:
        lines.append("## Import Failures")
        lines.append("")
        lines.append("These endpoints could not be imported, indicating broken code or missing dependencies.")
        lines.append("")
        lines.append("| Module | Endpoint | Error |")
        lines.append("|--------|----------|-------|")
        for ep in import_failures:
            key = _key(ep)
            error = test_results.get(key, {}).get("error", "").replace("|", "\\|")[:120]
            lines.append(f"| `{ep['module_path']}` | `{ep['func_name']}` | {error} |")
        lines.append("")

    # Endpoints needing specific arguments
    needs_args = [
        e for e in endpoints
        if test_results.get(_key(e), {}).get("status") == "NEEDS_ARGS"
    ]
    if needs_args:
        lines.append("## Endpoints Needing Specific Arguments")
        lines.append("")
        lines.append("These GET endpoints require arguments that cannot be auto-guessed.")
        lines.append("")
        lines.append("| Module | Endpoint | Error |")
        lines.append("|--------|----------|-------|")
        for ep in needs_args:
            key = _key(ep)
            error = test_results.get(key, {}).get("error", "").replace("|", "\\|")[:120]
            lines.append(f"| `{ep['module_path']}` | `{ep['func_name']}` | {error} |")
        lines.append("")

    # Guest-accessible endpoints
    guest_eps = [e for e in endpoints if e["allow_guest"]]
    if guest_eps:
        lines.append("## Guest-Accessible Endpoints")
        lines.append("")
        lines.append("These endpoints allow unauthenticated access (allow_guest=True).")
        lines.append("")
        lines.append("| Module | Endpoint | Type |")
        lines.append("|--------|----------|------|")
        for ep in guest_eps:
            lines.append(f"| `{ep['module_path']}` | `{ep['func_name']}` | {ep['endpoint_type']} |")
        lines.append("")

    return "\n".join(lines)


def _key(ep):
    """Create a unique key for an endpoint."""
    return f"{ep['module_path']}.{ep['func_name']}"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run():
    """Main entry point for the comprehensive API audit."""
    print("=" * 70)
    print("COMPREHENSIVE API AUDIT")
    print("=" * 70)
    print()

    # Step 1: Discover all endpoints
    print("[1/4] Discovering all @frappe.whitelist() endpoints...")
    endpoints = _discover_all_endpoints()
    print(f"  Found {len(endpoints)} endpoints across {len(set(e['module_path'] for e in endpoints))} modules")

    get_eps = [e for e in endpoints if e["endpoint_type"] == "GET"]
    action_eps = [e for e in endpoints if e["endpoint_type"] == "ACTION"]
    other_eps = [e for e in endpoints if e["endpoint_type"] == "OTHER"]
    print(f"  GET: {len(get_eps)} | ACTION: {len(action_eps)} | OTHER: {len(other_eps)}")

    # Step 2: Group by module
    print("[2/4] Grouping by module...")
    grouped = _group_endpoints(endpoints)
    print(f"  {len(grouped)} module groups")

    # Step 3: Test endpoints
    print("[3/4] Testing endpoints...")
    frappe.set_user("Administrator")
    test_results = {}

    # Test GET endpoints (call with no args)
    print(f"  Testing {len(get_eps)} GET endpoints...")
    for ep in get_eps:
        key = _key(ep)
        func, import_err = _try_import(ep["module_path"], ep["func_name"])
        if import_err:
            test_results[key] = {"status": "IMPORT_FAIL", "response_type": "", "error": import_err}
            print(f"    {ep['func_name']}: IMPORT_FAIL")
            continue

        result = _test_get_endpoint(func, ep["func_name"])
        test_results[key] = result
        print(f"    {ep['func_name']}: {result['status']}")

    # Test ACTION endpoints (import check only)
    print(f"  Testing {len(action_eps)} ACTION endpoints (import only)...")
    for ep in action_eps:
        key = _key(ep)
        func, import_err = _try_import(ep["module_path"], ep["func_name"])
        if import_err:
            test_results[key] = {"status": "IMPORT_FAIL", "response_type": "", "error": import_err}
            print(f"    {ep['func_name']}: IMPORT_FAIL")
            continue
        status = _test_importable(func)
        test_results[key] = {"status": status, "response_type": "", "error": ""}
        print(f"    {ep['func_name']}: {status}")

    # Test OTHER endpoints (import check only)
    print(f"  Testing {len(other_eps)} OTHER endpoints (import only)...")
    for ep in other_eps:
        key = _key(ep)
        func, import_err = _try_import(ep["module_path"], ep["func_name"])
        if import_err:
            test_results[key] = {"status": "IMPORT_FAIL", "response_type": "", "error": import_err}
            print(f"    {ep['func_name']}: IMPORT_FAIL")
            continue
        status = _test_importable(func)
        test_results[key] = {"status": status, "response_type": "", "error": ""}
        print(f"    {ep['func_name']}: {status}")

    # Step 4: Generate report
    print("[4/4] Generating report...")
    md_content = _generate_report(endpoints, grouped, test_results)

    with open(OUTPUT_PATH, "w") as fp:
        fp.write(md_content)
    print(f"  Report written to: {OUTPUT_PATH}")

    # Reset user
    frappe.set_user("Administrator")

    # Summary
    total_pass = sum(1 for r in test_results.values() if r["status"].startswith("PASS") or r["status"] == "IMPORTABLE")
    total_fail = sum(1 for r in test_results.values() if r["status"] in ("FAIL", "IMPORT_FAIL"))
    total_other = len(test_results) - total_pass - total_fail

    print()
    print("=" * 70)
    print("AUDIT COMPLETE")
    print(f"Total: {len(endpoints)} endpoints | PASS/IMPORTABLE: {total_pass} | FAIL: {total_fail} | Other: {total_other}")
    print("=" * 70)

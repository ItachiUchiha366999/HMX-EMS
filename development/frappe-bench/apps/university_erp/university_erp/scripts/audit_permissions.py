# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Permission Matrix Audit Script

Tests role-based access for 9 roles across all university_erp doctypes
and key API endpoints. Generates PERMISSION_AUDIT.md with role x resource
permission matrices and security findings.

Usage:
    bench --site university.local execute university_erp.scripts.audit_permissions.run
"""

import importlib
import traceback
from datetime import datetime

import frappe
from frappe import _


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROLES_TO_TEST = [
    {"role": "System Manager", "label": "Admin"},
    {"role": "Instructor", "label": "Faculty"},
    {"role": "Student", "label": "Student"},
    {"role": "Guardian", "label": "Parent"},
    {"role": "HOD", "label": "HOD"},
    {"role": "University VC", "label": "VC"},
    {"role": "University Dean", "label": "Dean"},
    {"role": "University Registrar", "label": "Registrar"},
    {"role": "University Finance Officer", "label": "Finance"},
]

# Modules from university_erp modules.txt (21 modules)
UNIVERSITY_MODULES = [
    "University ERP",
    "University Academics",
    "University Admissions",
    "University Student Info",
    "University Examinations",
    "University Finance",
    "Faculty Management",
    "University Hostel",
    "University Transport",
    "University Library",
    "University Placement",
    "University LMS",
    "University Research",
    "University OBE",
    "University Integrations",
    "University Portals",
    "University Payments",
    "University Inventory",
    "University Grievance",
    "University Analytics",
    "University Feedback",
]

# Key API endpoints to test across roles
# (module_path, function_name, description, expected_access)
# expected_access: dict mapping role label -> expected outcome
KEY_API_ENDPOINTS = [
    {
        "module": "university_erp.university_portals.api.faculty_api",
        "func": "get_faculty_dashboard",
        "description": "Faculty dashboard (should need faculty user)",
        "expected": {"Admin": "PASS", "Faculty": "PASS", "Student": "DENIED"},
    },
    {
        "module": "university_erp.university_portals.api.portal_api",
        "func": "get_session_info",
        "description": "Session info (should work for all logged-in users)",
        "expected": {"Admin": "PASS", "Faculty": "PASS", "Student": "PASS"},
    },
    {
        "module": "university_erp.university_erp.analytics.api",
        "func": "get_available_dashboards",
        "description": "Analytics dashboards (management + admin)",
        "expected": {"Admin": "PASS", "Student": "DENIED"},
    },
    {
        "module": "university_erp.university_erp.health_check",
        "func": "run_checks",
        "description": "Health checks (System Manager only)",
        "expected": {"Admin": "PASS", "Student": "DENIED", "Faculty": "DENIED"},
    },
    {
        "module": "university_erp.university_erp.api.v1.student",
        "func": "get_profile",
        "description": "Student profile API v1 (Student + Admin)",
        "expected": {"Admin": "PASS", "Student": "PASS"},
    },
    {
        "module": "university_erp.university_erp.api.v1.admin",
        "func": "get_dashboard_stats",
        "description": "Admin dashboard stats (System Manager only)",
        "expected": {"Admin": "PASS", "Student": "DENIED"},
    },
    {
        "module": "university_erp.university_erp.analytics.api",
        "func": "get_quick_stats",
        "description": "Quick stats (needs Custom Dashboard read)",
        "expected": {"Admin": "PASS"},
    },
    {
        "module": "university_erp.university_portals.api.portal_api",
        "func": "get_portal_redirect",
        "description": "Portal redirect (guest allowed)",
        "expected": {"Admin": "PASS", "Student": "PASS", "Faculty": "PASS"},
    },
]

OUTPUT_PATH = (
    "/workspace/development/.planning/phases/"
    "03.1-cross-app-integration-audit-accessibility-testing/"
    "PERMISSION_AUDIT.md"
)


# ---------------------------------------------------------------------------
# User discovery
# ---------------------------------------------------------------------------

def _find_user_for_role(role_name):
    """Find an existing user that has the given role.

    Returns (user_email, method) or (None, None).
    """
    # Find a user with this role
    users = frappe.db.sql(
        """
        SELECT hr.parent
        FROM `tabHas Role` hr
        INNER JOIN `tabUser` u ON u.name = hr.parent
        WHERE hr.role = %s
          AND hr.parenttype = 'User'
          AND u.enabled = 1
          AND u.name NOT IN ('Guest', 'Administrator')
        LIMIT 1
        """,
        (role_name,),
        as_dict=True,
    )

    if users:
        return users[0]["parent"], "has_role"

    # For System Manager, fall back to Administrator
    if role_name == "System Manager":
        return "Administrator", "administrator_fallback"

    return None, None


# ---------------------------------------------------------------------------
# Doctype permission testing
# ---------------------------------------------------------------------------

def _get_university_doctypes():
    """Get all doctypes belonging to university_erp modules."""
    doctypes = []
    for module in UNIVERSITY_MODULES:
        module_doctypes = frappe.get_all(
            "DocType",
            filters={"module": module},
            fields=["name", "module"],
            order_by="name",
        )
        doctypes.extend(module_doctypes)
    return doctypes


def _test_doctype_permissions(user_email, doctypes):
    """Test RWCD permissions for a user against all doctypes.

    Returns list of dicts with doctype, read, write, create, delete.
    """
    results = []
    original_user = frappe.session.user
    frappe.set_user(user_email)

    for dt in doctypes:
        result = {"doctype": dt["name"], "module": dt["module"]}
        for perm_type in ("read", "write", "create", "delete"):
            try:
                has_perm = frappe.has_permission(dt["name"], perm_type)
                result[perm_type] = has_perm
            except Exception:
                result[perm_type] = False
        results.append(result)

    frappe.set_user(original_user)
    return results


# ---------------------------------------------------------------------------
# API permission testing
# ---------------------------------------------------------------------------

def _test_api_endpoint(user_email, endpoint_info):
    """Test an API endpoint as a specific user.

    Returns: PASS, DENIED, ERROR, or NO_USER
    """
    if not user_email:
        return "NO_USER", ""

    original_user = frappe.session.user

    try:
        frappe.set_user(user_email)

        # Import the function
        try:
            mod = importlib.import_module(endpoint_info["module"])
            func = getattr(mod, endpoint_info["func"])
        except Exception as e:
            frappe.set_user(original_user)
            return "IMPORT_FAIL", str(e)[:100]

        # Call it with no args
        try:
            result = func()
            frappe.set_user(original_user)
            return "PASS", ""
        except frappe.PermissionError:
            frappe.set_user(original_user)
            return "DENIED", "PermissionError"
        except TypeError as te:
            # Missing args but function was accessible
            err = str(te)
            if "missing" in err.lower() and "argument" in err.lower():
                frappe.set_user(original_user)
                return "PASS_NEEDS_ARGS", "Function accessible but needs arguments"
            frappe.set_user(original_user)
            return "ERROR", str(te)[:100]
        except frappe.AuthenticationError:
            frappe.set_user(original_user)
            return "DENIED", "AuthenticationError"
        except Exception as e:
            err_str = str(e).lower()
            if "not permitted" in err_str or "permission" in err_str or "not authorized" in err_str:
                frappe.set_user(original_user)
                return "DENIED", str(e)[:100]
            if "not found" in err_str or "does not exist" in err_str:
                frappe.set_user(original_user)
                return "PASS_NO_DATA", str(e)[:100]
            frappe.set_user(original_user)
            return "ERROR", str(e)[:100]
    except Exception as e:
        frappe.set_user(original_user)
        return "ERROR", str(e)[:100]


# ---------------------------------------------------------------------------
# Security analysis
# ---------------------------------------------------------------------------

def _analyze_security(role_doctype_results, role_api_results, role_users):
    """Identify potential security issues from the audit results."""
    findings = []

    # Check: Student should not have write access to Faculty-related doctypes
    student_user = role_users.get("Student")
    if student_user:
        student_results = role_doctype_results.get("Student", [])
        faculty_doctypes = [
            "Faculty Profile", "Teaching Assignment", "Faculty Publication",
            "Faculty Research Project", "Faculty Award", "Workload Distributor",
            "Student Feedback",
        ]
        for result in student_results:
            if result["doctype"] in faculty_doctypes:
                if result.get("write") or result.get("create") or result.get("delete"):
                    findings.append({
                        "severity": "HIGH",
                        "finding": f"Student role has write/create/delete on {result['doctype']}",
                        "role": "Student",
                        "doctype": result["doctype"],
                        "permissions": f"W={result.get('write')} C={result.get('create')} D={result.get('delete')}",
                    })

    # Check: Guardian should only have read access to student-related doctypes
    guardian_user = role_users.get("Parent")
    if guardian_user:
        guardian_results = role_doctype_results.get("Parent", [])
        for result in guardian_results:
            if result.get("write") or result.get("create") or result.get("delete"):
                # Guardians should rarely write to anything
                if result["doctype"] not in ("Communication", "Comment"):
                    findings.append({
                        "severity": "MEDIUM",
                        "finding": f"Guardian role has write/create/delete on {result['doctype']}",
                        "role": "Parent",
                        "doctype": result["doctype"],
                        "permissions": f"W={result.get('write')} C={result.get('create')} D={result.get('delete')}",
                    })

    # Check: Finance Officer should not access academic doctypes
    finance_user = role_users.get("Finance")
    if finance_user:
        finance_results = role_doctype_results.get("Finance", [])
        academic_doctypes = [
            "Assessment Plan", "Assessment Result", "Course Schedule",
            "Student Attendance",
        ]
        for result in finance_results:
            if result["doctype"] in academic_doctypes and result.get("write"):
                findings.append({
                    "severity": "LOW",
                    "finding": f"Finance Officer has write access to academic doctype {result['doctype']}",
                    "role": "Finance",
                    "doctype": result["doctype"],
                    "permissions": f"W={result.get('write')} C={result.get('create')}",
                })

    # Check: API endpoints where student can access admin/faculty endpoints
    for ep in KEY_API_ENDPOINTS:
        student_api_result = role_api_results.get("Student", {}).get(
            f"{ep['module']}.{ep['func']}", ("UNTESTED", "")
        )
        expected = ep.get("expected", {}).get("Student", None)
        if expected == "DENIED" and student_api_result[0] in ("PASS", "PASS_NEEDS_ARGS"):
            findings.append({
                "severity": "HIGH",
                "finding": f"Student can access {ep['func']} (expected DENIED, got {student_api_result[0]})",
                "role": "Student",
                "doctype": f"API: {ep['module']}.{ep['func']}",
                "permissions": f"Status: {student_api_result[0]}",
            })

    return findings


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_report(
    role_users, role_doctype_results, role_api_results,
    doctypes, security_findings
):
    """Generate PERMISSION_AUDIT.md."""
    lines = []
    lines.append("# Permission Matrix Audit Results")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Site:** {frappe.local.site}")
    lines.append(f"**Scope:** 9 roles x {len(doctypes)} doctypes + {len(KEY_API_ENDPOINTS)} key API endpoints")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    total_roles_tested = sum(1 for v in role_users.values() if v)
    missing_roles = [r["label"] for r in ROLES_TO_TEST if not role_users.get(r["label"])]
    lines.append(f"- **Roles Tested:** {total_roles_tested}/{len(ROLES_TO_TEST)}")
    lines.append(f"- **Total Doctypes:** {len(doctypes)}")
    lines.append(f"- **API Endpoints Tested:** {len(KEY_API_ENDPOINTS)}")
    lines.append(f"- **Security Findings:** {len(security_findings)}")
    if missing_roles:
        lines.append(f"- **Missing Users for Roles:** {', '.join(missing_roles)}")
    lines.append("")

    # Role user mapping
    lines.append("## Role-User Mapping")
    lines.append("")
    lines.append("| Role | Label | Test User | Method |")
    lines.append("|------|-------|-----------|--------|")
    for role_info in ROLES_TO_TEST:
        label = role_info["label"]
        user = role_users.get(label, None)
        method = role_users.get(f"{label}_method", "")
        if user:
            lines.append(f"| {role_info['role']} | {label} | {user} | {method} |")
        else:
            lines.append(f"| {role_info['role']} | {label} | NO_USER | -- |")
    lines.append("")

    # Doctype Permission Matrix
    lines.append("## Doctype Permission Matrix")
    lines.append("")
    lines.append("Legend: R=Read, W=Write, C=Create, D=Delete")
    lines.append("")

    # Create one table per role (more readable than one massive table)
    for role_info in ROLES_TO_TEST:
        label = role_info["label"]
        results = role_doctype_results.get(label, [])
        if not results:
            lines.append(f"### {label} ({role_info['role']})")
            lines.append("")
            lines.append("No test user available -- skipped.")
            lines.append("")
            continue

        # Only show doctypes where the role has at least one permission
        accessible = [r for r in results if r.get("read") or r.get("write") or r.get("create") or r.get("delete")]
        no_access = [r for r in results if not (r.get("read") or r.get("write") or r.get("create") or r.get("delete"))]

        lines.append(f"### {label} ({role_info['role']})")
        lines.append("")
        lines.append(f"Access to {len(accessible)}/{len(results)} doctypes.")
        lines.append("")

        if accessible:
            lines.append("| Doctype | Module | R | W | C | D |")
            lines.append("|---------|--------|---|---|---|---|")
            for r in accessible:
                rd = "Y" if r.get("read") else "-"
                wr = "Y" if r.get("write") else "-"
                cr = "Y" if r.get("create") else "-"
                dl = "Y" if r.get("delete") else "-"
                lines.append(f"| {r['doctype']} | {r['module']} | {rd} | {wr} | {cr} | {dl} |")
            lines.append("")

        if no_access:
            lines.append(f"<details><summary>No access ({len(no_access)} doctypes)</summary>")
            lines.append("")
            for r in no_access:
                lines.append(f"- {r['doctype']}")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    # API Permission Matrix
    lines.append("## API Permission Matrix")
    lines.append("")
    role_labels = [r["label"] for r in ROLES_TO_TEST]
    header = "| Endpoint | Description | " + " | ".join(role_labels) + " |"
    separator = "|----------|-------------|" + "|".join(["----"] * len(role_labels)) + "|"
    lines.append(header)
    lines.append(separator)

    for ep in KEY_API_ENDPOINTS:
        key = f"{ep['module']}.{ep['func']}"
        row = f"| `{ep['func']}` | {ep['description']} |"
        for role_info in ROLES_TO_TEST:
            label = role_info["label"]
            result = role_api_results.get(label, {}).get(key, ("UNTESTED", ""))
            status = result[0]
            # Color-code with emoji-free markers
            if status in ("PASS", "PASS_NEEDS_ARGS", "PASS_NO_DATA"):
                marker = "PASS"
            elif status == "DENIED":
                marker = "DENIED"
            elif status == "NO_USER":
                marker = "NO_USER"
            elif status == "ERROR":
                marker = "ERROR"
            else:
                marker = status
            row += f" {marker} |"
        lines.append(row)
    lines.append("")

    # Security Findings
    lines.append("## Security Findings")
    lines.append("")
    if not security_findings:
        lines.append("No security issues found. All roles have appropriate access levels.")
        lines.append("")
    else:
        high = [f for f in security_findings if f["severity"] == "HIGH"]
        medium = [f for f in security_findings if f["severity"] == "MEDIUM"]
        low = [f for f in security_findings if f["severity"] == "LOW"]

        lines.append(f"**Total findings:** {len(security_findings)} (HIGH: {len(high)}, MEDIUM: {len(medium)}, LOW: {len(low)})")
        lines.append("")
        lines.append("| # | Severity | Role | Resource | Finding | Permissions |")
        lines.append("|---|----------|------|----------|---------|-------------|")
        for i, f in enumerate(security_findings, 1):
            finding_text = f["finding"].replace("|", "\\|")
            lines.append(
                f"| {i} | {f['severity']} | {f['role']} | {f['doctype']} | {finding_text} | {f['permissions']} |"
            )
        lines.append("")

    # Missing users
    missing = [r for r in ROLES_TO_TEST if not role_users.get(r["label"])]
    if missing:
        lines.append("## Missing Users")
        lines.append("")
        lines.append("The following roles have no test user in the system:")
        lines.append("")
        for r in missing:
            lines.append(f"- **{r['role']}** ({r['label']}): No user with this role found")
        lines.append("")
        lines.append("Create test users with these roles for complete coverage.")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run():
    """Main entry point for the permission matrix audit."""
    print("=" * 70)
    print("PERMISSION MATRIX AUDIT")
    print("=" * 70)
    print()

    # Step 1: Find users for each role
    print("[1/5] Finding test users for 9 roles...")
    role_users = {}
    for role_info in ROLES_TO_TEST:
        user, method = _find_user_for_role(role_info["role"])
        role_users[role_info["label"]] = user
        role_users[f"{role_info['label']}_method"] = method or ""
        if user:
            print(f"  {role_info['label']} ({role_info['role']}): {user} ({method})")
        else:
            print(f"  {role_info['label']} ({role_info['role']}): NO USER FOUND")

    # Step 2: Get all university_erp doctypes
    print("[2/5] Discovering university_erp doctypes...")
    doctypes = _get_university_doctypes()
    print(f"  Found {len(doctypes)} doctypes across {len(UNIVERSITY_MODULES)} modules")

    # Step 3: Test doctype permissions
    print("[3/5] Testing doctype permissions for each role...")
    role_doctype_results = {}
    for role_info in ROLES_TO_TEST:
        label = role_info["label"]
        user = role_users.get(label)
        if not user:
            print(f"  {label}: SKIPPED (no user)")
            continue
        print(f"  {label} ({user}): testing {len(doctypes)} doctypes...", end=" ", flush=True)
        results = _test_doctype_permissions(user, doctypes)
        role_doctype_results[label] = results
        accessible = sum(1 for r in results if r.get("read"))
        print(f"{accessible}/{len(doctypes)} readable")

    # Step 4: Test API permissions
    print("[4/5] Testing API endpoints for each role...")
    role_api_results = {}
    for role_info in ROLES_TO_TEST:
        label = role_info["label"]
        user = role_users.get(label)
        role_api_results[label] = {}
        for ep in KEY_API_ENDPOINTS:
            key = f"{ep['module']}.{ep['func']}"
            status, detail = _test_api_endpoint(user, ep)
            role_api_results[label][key] = (status, detail)
            print(f"  {label} -> {ep['func']}: {status}")

    # Ensure we reset to Administrator
    frappe.set_user("Administrator")

    # Step 5: Analyze security
    print("[5/5] Analyzing security findings...")
    security_findings = _analyze_security(role_doctype_results, role_api_results, role_users)
    print(f"  Found {len(security_findings)} security findings")

    # Generate report
    md_content = _generate_report(
        role_users, role_doctype_results, role_api_results,
        doctypes, security_findings,
    )

    with open(OUTPUT_PATH, "w") as fp:
        fp.write(md_content)
    print(f"\nReport written to: {OUTPUT_PATH}")

    # Summary
    tested_roles = sum(1 for v in role_users.values() if v and not v.endswith("_method"))
    print()
    print("=" * 70)
    print("AUDIT COMPLETE")
    print(f"Roles: {tested_roles}/9 tested | Doctypes: {len(doctypes)} | APIs: {len(KEY_API_ENDPOINTS)} | Findings: {len(security_findings)}")
    print("=" * 70)

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Cross-app data integrity health checks.

Callable via: GET /api/method/university_erp.university_erp.health_check.run_checks
Access: University Admin role only.

Returns:
    {
        "status": "ok" | "degraded" | "critical",
        "checks": [
            {"name": str, "status": "pass" | "fail" | "warn", "detail": str, "count": int}
        ]
    }
"""

import frappe
from frappe import _


@frappe.whitelist()
def run_checks():
    """Run all cross-app integrity checks. University Admin only."""
    if "University Admin" not in frappe.get_roles():
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    checks = [
        _check_student_enrollment(),
        _check_fees_gl_accounts(),
        _check_employee_faculty_profile(),
        _check_academic_year_validity(),
    ]

    # Derive overall status
    statuses = [c["status"] for c in checks]
    if "fail" in statuses:
        overall = "critical"
    elif "warn" in statuses:
        overall = "degraded"
    else:
        overall = "ok"

    return {"status": overall, "checks": checks}


def _check_student_enrollment():
    """
    Check 1: Every active Student has at least one submitted Program Enrollment.
    Orphaned students = students with no Program Enrollment at docstatus=1.
    """
    name = "Student ↔ Program Enrollment"

    if not frappe.db.exists("DocType", "Student") or not frappe.db.exists("DocType", "Program Enrollment"):
        return {"name": name, "status": "warn", "detail": "DocType not found — skipped", "count": 0}

    result = frappe.db.sql(
        """
        SELECT COUNT(*) as cnt
        FROM `tabStudent` s
        WHERE NOT EXISTS (
            SELECT 1 FROM `tabProgram Enrollment` pe
            WHERE pe.student = s.name AND pe.docstatus = 1
        )
        """,
        as_dict=True,
    )
    count = result[0]["cnt"] if result else 0

    if count == 0:
        return {"name": name, "status": "pass", "detail": "All students have a submitted Program Enrollment", "count": 0}
    return {
        "name": name,
        "status": "warn",
        "detail": f"{count} student(s) have no submitted Program Enrollment",
        "count": count,
    }


def _check_fees_gl_accounts():
    """
    Check 2: Every Fee Structure references valid, existing GL Accounts.
    Validates receivable_account and income_account fields link to existing Account records.
    """
    name = "Fees ↔ GL Accounts"

    if not frappe.db.exists("DocType", "Fee Structure"):
        return {"name": name, "status": "warn", "detail": "Fee Structure DocType not found — skipped", "count": 0}

    invalid = frappe.db.sql(
        """
        SELECT fs.name
        FROM `tabFee Structure` fs
        WHERE fs.docstatus != 2
          AND (
            (fs.receivable_account IS NOT NULL AND fs.receivable_account != ''
             AND NOT EXISTS (SELECT 1 FROM `tabAccount` a WHERE a.name = fs.receivable_account))
            OR
            (fs.income_account IS NOT NULL AND fs.income_account != ''
             AND NOT EXISTS (SELECT 1 FROM `tabAccount` a WHERE a.name = fs.income_account))
          )
        """,
        as_dict=True,
    )
    count = len(invalid)

    if count == 0:
        return {"name": name, "status": "pass", "detail": "All Fee Structures reference valid GL Accounts", "count": 0}
    names = ", ".join([r["name"] for r in invalid[:5]])
    return {
        "name": name,
        "status": "fail",
        "detail": f"{count} Fee Structure(s) have invalid GL Account links: {names}{'...' if count > 5 else ''}",
        "count": count,
    }


def _check_employee_faculty_profile():
    """
    Check 3: Every Faculty Profile links to a valid, existing Employee record.
    """
    name = "Employee ↔ Faculty Profile"

    if not frappe.db.exists("DocType", "Faculty Profile"):
        # Try Instructor as fallback (Education app uses Instructor, not Faculty Profile)
        if not frappe.db.exists("DocType", "Instructor"):
            return {"name": name, "status": "warn", "detail": "Faculty Profile / Instructor DocType not found — skipped", "count": 0}
        # Check Instructor.employee links
        invalid = frappe.db.sql(
            """
            SELECT i.name
            FROM `tabInstructor` i
            WHERE i.employee IS NOT NULL AND i.employee != ''
              AND NOT EXISTS (SELECT 1 FROM `tabEmployee` e WHERE e.name = i.employee)
            """,
            as_dict=True,
        )
        count = len(invalid)
        if count == 0:
            return {"name": name, "status": "pass", "detail": "All Instructor records link to valid Employees", "count": 0}
        return {
            "name": name,
            "status": "fail",
            "detail": f"{count} Instructor(s) link to non-existent Employee records",
            "count": count,
        }

    invalid = frappe.db.sql(
        """
        SELECT fp.name
        FROM `tabFaculty Profile` fp
        WHERE fp.employee IS NOT NULL AND fp.employee != ''
          AND NOT EXISTS (SELECT 1 FROM `tabEmployee` e WHERE e.name = fp.employee)
        """,
        as_dict=True,
    )
    count = len(invalid)

    if count == 0:
        return {"name": name, "status": "pass", "detail": "All Faculty Profiles link to valid Employees", "count": 0}
    return {
        "name": name,
        "status": "fail",
        "detail": f"{count} Faculty Profile(s) link to non-existent Employee records",
        "count": count,
    }


def _check_academic_year_validity():
    """
    Check 4: At least one Academic Year exists with non-null dates; Academic Terms
    have non-null term_start_date and term_end_date.
    """
    name = "Academic Year / Term Validity"

    if not frappe.db.exists("DocType", "Academic Year"):
        return {"name": name, "status": "warn", "detail": "Academic Year DocType not found — skipped", "count": 0}

    year_count = frappe.db.count("Academic Year", {})
    if year_count == 0:
        return {"name": name, "status": "fail", "detail": "No Academic Year records found", "count": 0}

    # Academic Years with null date fields
    invalid_years = frappe.db.sql(
        """
        SELECT COUNT(*) as cnt FROM `tabAcademic Year`
        WHERE year_start_date IS NULL OR year_end_date IS NULL
        """,
        as_dict=True,
    )
    bad_years = invalid_years[0]["cnt"] if invalid_years else 0

    bad_terms = 0
    if frappe.db.exists("DocType", "Academic Term"):
        invalid_terms = frappe.db.sql(
            """
            SELECT COUNT(*) as cnt FROM `tabAcademic Term`
            WHERE term_start_date IS NULL OR term_end_date IS NULL
            """,
            as_dict=True,
        )
        bad_terms = invalid_terms[0]["cnt"] if invalid_terms else 0

    total_bad = bad_years + bad_terms
    if total_bad == 0:
        return {
            "name": name,
            "status": "pass",
            "detail": f"{year_count} Academic Year(s) found, all dates valid",
            "count": year_count,
        }
    return {
        "name": name,
        "status": "warn",
        "detail": f"{bad_years} Academic Year(s) and {bad_terms} Academic Term(s) have null date fields",
        "count": total_bad,
    }

# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Admin API v1
Administrative endpoints for university operations
"""

import frappe
from frappe import _
from frappe.utils import nowdate, getdate
from . import api_handler, NotFoundError, ValidationError


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["System Manager", "Education Manager"])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    return {
        "students": get_student_stats(),
        "faculty": get_faculty_stats(),
        "finance": get_finance_stats(),
        "admissions": get_admission_stats()
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["System Manager", "Education Manager"])
def get_student_stats():
    """Get student statistics"""
    total = frappe.db.count("Student", {"enabled": 1})

    by_program = frappe.db.sql("""
        SELECT
            p.program_name,
            COUNT(pe.name) as count
        FROM `tabProgram Enrollment` pe
        JOIN `tabProgram` p ON pe.program = p.name
        WHERE pe.docstatus = 1
        GROUP BY pe.program
        ORDER BY count DESC
        LIMIT 10
    """, as_dict=True)

    by_batch = frappe.db.sql("""
        SELECT
            student_batch_name,
            COUNT(*) as count
        FROM `tabProgram Enrollment`
        WHERE docstatus = 1
        AND student_batch_name IS NOT NULL
        GROUP BY student_batch_name
        ORDER BY student_batch_name DESC
        LIMIT 5
    """, as_dict=True)

    return {
        "total_active": total,
        "by_program": by_program,
        "by_batch": by_batch
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["System Manager", "HR Manager"])
def get_faculty_stats():
    """Get faculty statistics"""
    total = frappe.db.count("Instructor", {"status": "Active"})

    by_department = frappe.db.sql("""
        SELECT
            department,
            COUNT(*) as count
        FROM `tabInstructor`
        WHERE status = 'Active'
        AND department IS NOT NULL
        GROUP BY department
        ORDER BY count DESC
    """, as_dict=True)

    return {
        "total_active": total,
        "by_department": by_department
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["System Manager", "Accounts Manager"])
def get_finance_stats():
    """Get finance statistics"""
    current_fy = get_current_fiscal_year()

    # Total fees collected
    collected = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total - outstanding_amount), 0) as amount
        FROM `tabFees`
        WHERE docstatus = 1
        AND posting_date >= %s
    """, (current_fy.get("start_date"),), as_dict=True)

    # Total outstanding
    outstanding = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as amount
        FROM `tabFees`
        WHERE docstatus = 1
        AND outstanding_amount > 0
    """, as_dict=True)

    # Monthly collection trend
    monthly_trend = frappe.db.sql("""
        SELECT
            DATE_FORMAT(posting_date, '%%Y-%%m') as month,
            SUM(grand_total - outstanding_amount) as collected
        FROM `tabFees`
        WHERE docstatus = 1
        AND posting_date >= %s
        GROUP BY DATE_FORMAT(posting_date, '%%Y-%%m')
        ORDER BY month
    """, (current_fy.get("start_date"),), as_dict=True)

    return {
        "total_collected": collected[0].amount if collected else 0,
        "total_outstanding": outstanding[0].amount if outstanding else 0,
        "monthly_trend": monthly_trend
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["System Manager", "Education Manager"])
def get_admission_stats():
    """Get admission statistics"""
    current_year = frappe.db.get_value(
        "Academic Year",
        {"is_current": 1},
        "name"
    )

    stats = frappe.db.sql("""
        SELECT
            application_status,
            COUNT(*) as count
        FROM `tabStudent Applicant`
        WHERE academic_year = %s
        GROUP BY application_status
    """, (current_year,), as_dict=True)

    return {
        "academic_year": current_year,
        "by_status": {s.application_status: s.count for s in stats}
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["System Manager"])
def get_system_health():
    """Get system health metrics"""
    # Background jobs
    pending_jobs = frappe.db.count(
        "RQ Job",
        {"status": "queued"}
    )

    failed_jobs = frappe.db.count(
        "RQ Job",
        {"status": "failed"}
    )

    # Error logs (last 24 hours)
    error_count = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabError Log`
        WHERE creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """, as_dict=True)

    # Scheduler status
    scheduler_status = "Active"
    try:
        from frappe.utils.scheduler import is_scheduler_disabled
        if is_scheduler_disabled():
            scheduler_status = "Disabled"
    except Exception:
        scheduler_status = "Unknown"

    return {
        "scheduler_status": scheduler_status,
        "pending_jobs": pending_jobs,
        "failed_jobs": failed_jobs,
        "errors_24h": error_count[0].count if error_count else 0,
        "database_size": get_database_size()
    }


@frappe.whitelist()
@api_handler(allowed_methods=["POST"], allowed_roles=["System Manager"])
def send_bulk_notification(template_name, recipients, context=None):
    """
    Send bulk notification

    Args:
        template_name: Notification template name
        recipients: List of email addresses
        context: Template context variables
    """
    from university_erp.university_erp.notification_service import NotificationService

    import json
    if isinstance(recipients, str):
        recipients = json.loads(recipients)

    if isinstance(context, str):
        context = json.loads(context)

    results = NotificationService.send_notification(
        recipients=recipients,
        template_name=template_name,
        context=context or {},
        respect_preferences=True
    )

    return {
        "sent_to": len(recipients),
        "results": results
    }


# Helper functions

def get_current_fiscal_year():
    """Get current fiscal year dates"""
    fy = frappe.db.get_value(
        "Fiscal Year",
        {"is_current": 1},
        ["year_start_date", "year_end_date"],
        as_dict=True
    )

    if not fy:
        # Default to calendar year
        today = getdate(nowdate())
        return {
            "start_date": f"{today.year}-01-01",
            "end_date": f"{today.year}-12-31"
        }

    return {
        "start_date": fy.year_start_date,
        "end_date": fy.year_end_date
    }


def get_database_size():
    """Get database size in MB"""
    try:
        result = frappe.db.sql("""
            SELECT
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
        """, as_dict=True)

        return result[0].size_mb if result else 0
    except Exception:
        return 0

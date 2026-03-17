# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, add_months, getdate, flt


@frappe.whitelist()
def get_dashboard_data():
    """Get comprehensive university dashboard data"""
    data = {
        "students": get_student_stats(),
        "academics": get_academic_stats(),
        "finance": get_finance_stats(),
        "hr": get_hr_stats(),
        "admissions": get_admission_stats(),
        "placements": get_placement_stats(),
        "hostel": get_hostel_stats(),
        "library": get_library_stats()
    }

    return data


def get_student_stats():
    """Student-related statistics"""
    total = frappe.db.count("Student", {"enabled": 1})

    by_program = frappe.db.sql("""
        SELECT program, COUNT(*) as count
        FROM `tabStudent`
        WHERE enabled = 1 AND program IS NOT NULL
        GROUP BY program
        ORDER BY count DESC
        LIMIT 10
    """, as_dict=True)

    by_gender = frappe.db.sql("""
        SELECT gender, COUNT(*) as count
        FROM `tabStudent`
        WHERE enabled = 1 AND gender IS NOT NULL
        GROUP BY gender
    """, as_dict=True)

    # New enrollments this month
    new_this_month = frappe.db.count("Student", {
        "enabled": 1,
        "creation": [">=", add_months(nowdate(), -1)]
    })

    return {
        "total": total,
        "by_program": by_program,
        "by_gender": by_gender,
        "new_this_month": new_this_month
    }


def get_academic_stats():
    """Academic statistics"""
    # Get current academic term
    current_term = frappe.db.get_value(
        "Academic Term",
        {"term_start_date": ["<=", nowdate()], "term_end_date": [">=", nowdate()]},
        "name"
    )

    # Count active courses
    active_courses = frappe.db.count("Course", {"is_published": 1}) if frappe.db.has_column("Course", "is_published") else frappe.db.count("Course")

    # Count programs
    total_programs = frappe.db.count("Program")

    # Average attendance (last 30 days)
    avg_attendance = frappe.db.sql("""
        SELECT AVG(
            CASE WHEN status = 'Present' THEN 100 ELSE 0 END
        ) as avg
        FROM `tabStudent Attendance`
        WHERE date >= %s
    """, (add_months(nowdate(), -1),))[0][0] or 0

    # Teaching assignments count
    teaching_assignments = frappe.db.count("Teaching Assignment", {"docstatus": 1})

    return {
        "current_term": current_term,
        "active_courses": active_courses,
        "total_programs": total_programs,
        "avg_attendance": round(avg_attendance, 1),
        "teaching_assignments": teaching_assignments
    }


def get_finance_stats():
    """Financial statistics"""
    current_fy = get_current_fiscal_year()
    start_date = current_fy.get("start_date") if current_fy else add_months(nowdate(), -12)

    fee_stats = frappe.db.sql("""
        SELECT
            COALESCE(SUM(grand_total), 0) as total_generated,
            COALESCE(SUM(grand_total - outstanding_amount), 0) as total_collected,
            COALESCE(SUM(outstanding_amount), 0) as total_outstanding
        FROM `tabFees`
        WHERE docstatus = 1
        AND posting_date >= %s
    """, (start_date,), as_dict=True)[0]

    # Monthly collection trend
    monthly_collection = frappe.db.sql("""
        SELECT
            DATE_FORMAT(posting_date, '%%Y-%%m') as month,
            SUM(grand_total - outstanding_amount) as collected
        FROM `tabFees`
        WHERE docstatus = 1
        AND posting_date >= %s
        GROUP BY DATE_FORMAT(posting_date, '%%Y-%%m')
        ORDER BY month
        LIMIT 12
    """, (add_months(nowdate(), -12),), as_dict=True)

    collection_rate = 0
    if fee_stats.get("total_generated"):
        collection_rate = round(
            (fee_stats.get("total_collected") or 0) /
            fee_stats.get("total_generated") * 100, 1
        )

    return {
        "total_generated": flt(fee_stats.get("total_generated")),
        "total_collected": flt(fee_stats.get("total_collected")),
        "total_outstanding": flt(fee_stats.get("total_outstanding")),
        "collection_rate": collection_rate,
        "monthly_trend": monthly_collection
    }


def get_hr_stats():
    """HR statistics"""
    # Total employees
    total_employees = frappe.db.count("Employee", {"status": "Active"})

    # Faculty count
    faculty_count = frappe.db.count(
        "Employee",
        {"custom_employee_category": "Teaching", "status": "Active"}
    ) if frappe.db.has_column("Employee", "custom_employee_category") else 0

    # Staff count
    staff_count = total_employees - faculty_count

    # Faculty by department
    by_department = frappe.db.sql("""
        SELECT
            COALESCE(custom_academic_department, 'Unassigned') as department,
            COUNT(*) as count
        FROM `tabEmployee`
        WHERE status = 'Active'
        AND custom_employee_category = 'Teaching'
        GROUP BY custom_academic_department
        ORDER BY count DESC
        LIMIT 10
    """, as_dict=True) if frappe.db.has_column("Employee", "custom_academic_department") else []

    # Pending leave applications
    pending_leaves = frappe.db.count("Leave Application", {"status": "Open"})

    return {
        "total_employees": total_employees,
        "faculty_count": faculty_count,
        "staff_count": staff_count,
        "by_department": by_department,
        "pending_leaves": pending_leaves
    }


def get_admission_stats():
    """Admission statistics"""
    # Get current academic year
    current_ay = frappe.db.get_value(
        "Academic Year",
        {"year_start_date": ["<=", nowdate()], "year_end_date": [">=", nowdate()]},
        "name"
    )

    if not current_ay:
        return {
            "academic_year": None,
            "total_applications": 0,
            "approved": 0,
            "admitted": 0,
            "pending": 0,
            "rejected": 0
        }

    applications = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN application_status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN application_status = 'Admitted' THEN 1 ELSE 0 END) as admitted,
            SUM(CASE WHEN application_status IN ('Applied', 'Pending') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN application_status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM `tabStudent Applicant`
        WHERE academic_year = %s
    """, (current_ay,), as_dict=True)[0]

    return {
        "academic_year": current_ay,
        "total_applications": applications.get("total") or 0,
        "approved": applications.get("approved") or 0,
        "admitted": applications.get("admitted") or 0,
        "pending": applications.get("pending") or 0,
        "rejected": applications.get("rejected") or 0
    }


def get_placement_stats():
    """Placement statistics"""
    # Students placed
    placed = frappe.db.count(
        "Placement Application",
        {"status": "Offer Accepted", "docstatus": ["!=", 2]}
    )

    # Active companies
    companies = frappe.db.count("Placement Company")

    # Average package
    avg_package = frappe.db.sql("""
        SELECT AVG(pjo.package_offered) as avg
        FROM `tabPlacement Application` pa
        JOIN `tabPlacement Job Opening` pjo ON pa.job_opening = pjo.name
        WHERE pa.status = 'Offer Accepted'
    """)[0][0] or 0

    # Highest package
    highest_package = frappe.db.sql("""
        SELECT MAX(pjo.package_offered) as max
        FROM `tabPlacement Application` pa
        JOIN `tabPlacement Job Opening` pjo ON pa.job_opening = pjo.name
        WHERE pa.status = 'Offer Accepted'
    """)[0][0] or 0

    # Active job openings
    active_openings = frappe.db.count("Placement Job Opening", {"status": "Open"})

    return {
        "students_placed": placed,
        "active_companies": companies,
        "avg_package": round(avg_package, 2),
        "highest_package": round(highest_package, 2),
        "active_openings": active_openings
    }


def get_hostel_stats():
    """Hostel statistics"""
    # Total capacity
    total_capacity = frappe.db.sql("""
        SELECT COALESCE(SUM(capacity), 0) as total
        FROM `tabHostel Room`
    """)[0][0] or 0

    # Occupied beds
    occupied = frappe.db.sql("""
        SELECT COALESCE(SUM(occupied_beds), 0) as total
        FROM `tabHostel Room`
    """)[0][0] or 0

    # Occupancy rate
    occupancy_rate = round(occupied / total_capacity * 100, 1) if total_capacity else 0

    # Active allocations
    active_allocations = frappe.db.count("Hostel Allocation", {"status": "Active"})

    return {
        "total_capacity": total_capacity,
        "occupied": occupied,
        "available": total_capacity - occupied,
        "occupancy_rate": occupancy_rate,
        "active_allocations": active_allocations
    }


def get_library_stats():
    """Library statistics"""
    # Total articles
    total_articles = frappe.db.count("Library Article")

    # Available articles
    available = frappe.db.sql("""
        SELECT COALESCE(SUM(available_count), 0) as total
        FROM `tabLibrary Article`
    """)[0][0] or 0

    # Active members
    active_members = frappe.db.count("Library Member", {"status": "Active"})

    # Books issued (active transactions)
    books_issued = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabLibrary Transaction` lt
        WHERE lt.type = 'Issue'
        AND lt.docstatus = 1
        AND lt.name NOT IN (
            SELECT issue_reference FROM `tabLibrary Transaction`
            WHERE type = 'Return' AND docstatus = 1 AND issue_reference IS NOT NULL
        )
    """)[0][0] or 0

    # Overdue books
    overdue = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabLibrary Transaction` lt
        WHERE lt.type = 'Issue'
        AND lt.docstatus = 1
        AND lt.to_date < %s
        AND lt.name NOT IN (
            SELECT issue_reference FROM `tabLibrary Transaction`
            WHERE type = 'Return' AND docstatus = 1 AND issue_reference IS NOT NULL
        )
    """, (nowdate(),))[0][0] or 0

    return {
        "total_articles": total_articles,
        "available": available,
        "active_members": active_members,
        "books_issued": books_issued,
        "overdue_books": overdue
    }


def get_current_fiscal_year():
    """Get current fiscal year"""
    fy = frappe.db.get_value(
        "Fiscal Year",
        {"year_start_date": ["<=", nowdate()], "year_end_date": [">=", nowdate()]},
        ["year_start_date", "year_end_date"],
        as_dict=True
    )
    return fy or {"start_date": add_months(nowdate(), -12), "end_date": nowdate()}


@frappe.whitelist()
def get_quick_stats():
    """Get quick stats for dashboard header"""
    return {
        "students": frappe.db.count("Student", {"enabled": 1}),
        "faculty": frappe.db.count("Employee", {"status": "Active", "custom_employee_category": "Teaching"}) if frappe.db.has_column("Employee", "custom_employee_category") else 0,
        "courses": frappe.db.count("Course"),
        "programs": frappe.db.count("Program")
    }

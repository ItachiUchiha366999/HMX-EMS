# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, add_months, getdate, flt


@frappe.whitelist()
def get_role_dashboard_data():
    """Get dashboard data based on user role"""
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "Student" in roles:
        return get_student_dashboard(user)
    elif "Instructor" in roles:
        return get_faculty_dashboard(user)
    elif "Education Manager" in roles:
        return get_admin_dashboard()
    elif "HR Manager" in roles:
        return get_hr_dashboard()
    elif "Accounts Manager" in roles:
        return get_finance_dashboard()

    return get_default_dashboard()


def get_student_dashboard(user):
    """Student-specific dashboard"""
    student = frappe.db.get_value("Student", {"user": user}, "name")

    if not student:
        return {"type": "student", "error": "Student record not found"}

    student_doc = frappe.get_doc("Student", student)

    # Get current enrollments
    enrollments = frappe.get_all(
        "Course Enrollment",
        filters={"student": student},
        fields=["course", "enrollment_date"],
        limit=10
    )

    # Enrich with course names
    for e in enrollments:
        e["course_name"] = frappe.db.get_value("Course", e["course"], "course_name")

    # Get attendance (last 30 days)
    attendance = frappe.db.sql("""
        SELECT
            COALESCE(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END), 0) as present,
            COUNT(*) as total
        FROM `tabStudent Attendance`
        WHERE student = %s
        AND date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    """, (student,), as_dict=True)[0]

    attendance_rate = 0
    if attendance.get("total"):
        attendance_rate = round(attendance.get("present", 0) / attendance.get("total") * 100, 1)

    # Get pending fees
    pending_fees = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as total
        FROM `tabFees`
        WHERE student = %s AND docstatus = 1 AND outstanding_amount > 0
    """, (student,))[0][0] or 0

    # Get latest results
    latest_results = frappe.db.sql("""
        SELECT
            ar.course,
            c.course_name,
            ar.custom_grade as grade,
            ar.custom_grade_points as grade_points
        FROM `tabAssessment Result` ar
        JOIN `tabCourse` c ON ar.course = c.name
        WHERE ar.student = %s AND ar.docstatus = 1
        ORDER BY ar.creation DESC
        LIMIT 5
    """, (student,), as_dict=True)

    # Get library status
    books_borrowed = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabLibrary Transaction` lt
        WHERE lt.library_member IN (
            SELECT name FROM `tabLibrary Member` WHERE student = %s
        )
        AND lt.type = 'Issue'
        AND lt.docstatus = 1
        AND lt.name NOT IN (
            SELECT issue_reference FROM `tabLibrary Transaction`
            WHERE type = 'Return' AND docstatus = 1 AND issue_reference IS NOT NULL
        )
    """, (student,))[0][0] or 0

    # Get hostel allocation
    hostel_allocation = frappe.db.get_value(
        "Hostel Allocation",
        {"student": student, "status": "Active"},
        ["hostel_room", "hostel_building"],
        as_dict=True
    )

    # Get placement applications
    placement_applications = frappe.db.count(
        "Placement Application",
        {"student": student, "docstatus": ["!=", 2]}
    )

    return {
        "type": "student",
        "student_name": student_doc.student_name,
        "program": student_doc.program,
        "enrollments": enrollments,
        "attendance_rate": attendance_rate,
        "pending_fees": flt(pending_fees),
        "latest_results": latest_results,
        "books_borrowed": books_borrowed,
        "hostel_allocation": hostel_allocation,
        "placement_applications": placement_applications,
        "cgpa": student_doc.get("custom_cgpa") or student_doc.get("cgpa") or 0
    }


def get_faculty_dashboard(user):
    """Faculty-specific dashboard"""
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return {"type": "faculty", "error": "Employee record not found"}

    employee_doc = frappe.get_doc("Employee", employee)

    # Get assigned courses
    assignments = frappe.get_all(
        "Teaching Assignment",
        filters={"instructor": employee, "docstatus": 1},
        fields=["name", "course", "course_name", "weekly_hours", "academic_term"]
    )

    total_hours = sum(a.get("weekly_hours") or 0 for a in assignments)

    # Get today's schedule
    today_schedule = []
    day_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    today_day = day_map.get(getdate(nowdate()).weekday())

    for assignment in assignments:
        schedule = frappe.get_all(
            "Teaching Assignment Schedule",
            filters={"parent": assignment["name"], "day": today_day},
            fields=["start_time", "end_time"],
            order_by="start_time"
        )
        for s in schedule:
            s["course"] = assignment["course"]
            s["course_name"] = assignment["course_name"]
            today_schedule.append(s)

    today_schedule.sort(key=lambda x: x["start_time"])

    # Get pending leave applications
    pending_leaves = frappe.db.count(
        "Leave Application",
        {"employee": employee, "status": "Open"}
    )

    # Get leave balance
    leave_balance = frappe.db.sql("""
        SELECT leave_type, total_leaves_allocated, total_leaves_taken
        FROM `tabLeave Allocation`
        WHERE employee = %s
        AND from_date <= %s AND to_date >= %s
    """, (employee, nowdate(), nowdate()), as_dict=True)

    # Get student feedback summary
    feedback = frappe.db.sql("""
        SELECT AVG(sf.overall_rating) as avg_rating, COUNT(*) as count
        FROM `tabStudent Feedback` sf
        JOIN `tabTeaching Assignment` ta ON sf.teaching_assignment = ta.name
        WHERE ta.instructor = %s AND sf.docstatus = 1
    """, (employee,), as_dict=True)[0]

    return {
        "type": "faculty",
        "employee_name": employee_doc.employee_name,
        "department": employee_doc.department,
        "assignments": assignments,
        "total_hours": total_hours,
        "today_schedule": today_schedule,
        "pending_leaves": pending_leaves,
        "leave_balance": leave_balance,
        "avg_feedback": round(feedback.get("avg_rating") or 0, 1),
        "feedback_count": feedback.get("count") or 0
    }


def get_admin_dashboard():
    """Education admin dashboard"""
    return {
        "type": "admin",
        "total_students": frappe.db.count("Student", {"enabled": 1}),
        "total_programs": frappe.db.count("Program"),
        "total_courses": frappe.db.count("Course"),
        "pending_applications": frappe.db.count("Student Applicant", {"application_status": ["in", ["Applied", "Pending"]]}),
        "active_term": frappe.db.get_value(
            "Academic Term",
            {"term_start_date": ["<=", nowdate()], "term_end_date": [">=", nowdate()]},
            "name"
        ),
        "recent_enrollments": frappe.db.count("Student", {"creation": [">=", add_months(nowdate(), -1)]})
    }


def get_hr_dashboard():
    """HR dashboard"""
    return {
        "type": "hr",
        "total_employees": frappe.db.count("Employee", {"status": "Active"}),
        "pending_leaves": frappe.db.count("Leave Application", {"status": "Open"}),
        "open_positions": frappe.db.count("Job Opening", {"status": "Open"}),
        "recent_hires": frappe.db.count("Employee", {"date_of_joining": [">=", add_months(nowdate(), -1)]}),
        "attendance_today": frappe.db.count("Attendance", {"attendance_date": nowdate(), "status": "Present"})
    }


def get_finance_dashboard():
    """Finance dashboard"""
    fee_stats = frappe.db.sql("""
        SELECT
            COALESCE(SUM(grand_total), 0) as total_generated,
            COALESCE(SUM(grand_total - outstanding_amount), 0) as total_collected,
            COALESCE(SUM(outstanding_amount), 0) as total_outstanding
        FROM `tabFees`
        WHERE docstatus = 1
        AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    """, as_dict=True)[0]

    return {
        "type": "finance",
        "total_generated": flt(fee_stats.get("total_generated")),
        "total_collected": flt(fee_stats.get("total_collected")),
        "total_outstanding": flt(fee_stats.get("total_outstanding")),
        "collection_rate": round(
            (fee_stats.get("total_collected") or 0) / (fee_stats.get("total_generated") or 1) * 100, 1
        ),
        "pending_payments": frappe.db.count("Fees", {"docstatus": 1, "outstanding_amount": [">", 0]}),
        "refund_requests": frappe.db.count("Fee Refund", {"docstatus": 0})
    }


def get_default_dashboard():
    """Default dashboard for other users"""
    return {
        "type": "default",
        "welcome_message": _("Welcome to University ERP"),
        "quick_links": [
            {"label": _("Students"), "link": "/app/student"},
            {"label": _("Courses"), "link": "/app/course"},
            {"label": _("Programs"), "link": "/app/program"}
        ]
    }

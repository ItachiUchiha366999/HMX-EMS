# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Student API v1
Endpoints for student-related data
"""

import frappe
from frappe import _
from frappe.utils import nowdate, getdate
from . import api_handler, NotFoundError, ValidationError


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager", "Education Manager"])
def get_profile(student_id=None):
    """
    Get student profile

    Args:
        student_id: Student ID (optional, defaults to current user's student)
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student profile not found")

    student = frappe.get_doc("Student", student_id)

    return {
        "student_id": student.name,
        "student_name": student.student_name,
        "first_name": student.first_name,
        "middle_name": student.middle_name,
        "last_name": student.last_name,
        "email": student.student_email_id,
        "mobile": student.student_mobile_number,
        "date_of_birth": student.date_of_birth,
        "gender": student.gender,
        "blood_group": student.blood_group,
        "nationality": student.nationality,
        "image": student.image,
        "joining_date": student.joining_date,
        "student_category": student.student_category,
        "enabled": student.enabled
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager", "Education Manager"])
def get_enrollments(student_id=None, academic_year=None, include_completed=False):
    """
    Get student enrollments

    Args:
        student_id: Student ID
        academic_year: Filter by academic year
        include_completed: Include completed enrollments
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    filters = {"student": student_id}

    if academic_year:
        filters["academic_year"] = academic_year

    enrollments = frappe.get_all(
        "Program Enrollment",
        filters=filters,
        fields=[
            "name", "program", "academic_year", "academic_term",
            "enrollment_date", "student_category", "student_batch_name"
        ]
    )

    result = []
    for enrollment in enrollments:
        program = frappe.db.get_value(
            "Program",
            enrollment.program,
            ["program_name", "department"],
            as_dict=True
        )

        result.append({
            "enrollment_id": enrollment.name,
            "program": enrollment.program,
            "program_name": program.program_name if program else None,
            "department": program.department if program else None,
            "academic_year": enrollment.academic_year,
            "academic_term": enrollment.academic_term,
            "enrollment_date": enrollment.enrollment_date,
            "batch": enrollment.student_batch_name
        })

    return result


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager", "Education Manager"])
def get_attendance(student_id=None, course=None, from_date=None, to_date=None):
    """
    Get student attendance

    Args:
        student_id: Student ID
        course: Filter by course
        from_date: Start date
        to_date: End date
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    filters = {"student": student_id}

    if course:
        filters["course"] = course

    if from_date:
        filters["date"] = [">=", getdate(from_date)]

    if to_date:
        if "date" in filters:
            filters["date"] = ["between", [getdate(from_date), getdate(to_date)]]
        else:
            filters["date"] = ["<=", getdate(to_date)]

    attendance = frappe.get_all(
        "Student Attendance",
        filters=filters,
        fields=["name", "course", "date", "status", "student_group"],
        order_by="date desc"
    )

    # Calculate summary
    total = len(attendance)
    present = sum(1 for a in attendance if a.status == "Present")
    absent = sum(1 for a in attendance if a.status == "Absent")
    percentage = round((present / total) * 100, 2) if total > 0 else 0

    return {
        "records": attendance,
        "summary": {
            "total_classes": total,
            "present": present,
            "absent": absent,
            "percentage": percentage
        }
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager", "Accounts User"])
def get_fees(student_id=None, status=None, academic_year=None):
    """
    Get student fees

    Args:
        student_id: Student ID
        status: Filter by status (Unpaid, Partially Paid, Paid)
        academic_year: Filter by academic year
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    filters = {"student": student_id, "docstatus": 1}

    if academic_year:
        filters["academic_year"] = academic_year

    fees = frappe.get_all(
        "Fees",
        filters=filters,
        fields=[
            "name", "posting_date", "due_date", "program",
            "grand_total", "outstanding_amount", "academic_year"
        ],
        order_by="posting_date desc"
    )

    result = []
    for fee in fees:
        # Determine status
        if fee.outstanding_amount == 0:
            fee_status = "Paid"
        elif fee.outstanding_amount < fee.grand_total:
            fee_status = "Partially Paid"
        else:
            fee_status = "Unpaid"

        if status and fee_status != status:
            continue

        result.append({
            "fee_id": fee.name,
            "posting_date": fee.posting_date,
            "due_date": fee.due_date,
            "program": fee.program,
            "total_amount": fee.grand_total,
            "outstanding_amount": fee.outstanding_amount,
            "paid_amount": fee.grand_total - fee.outstanding_amount,
            "status": fee_status,
            "academic_year": fee.academic_year
        })

    # Calculate totals
    total_fees = sum(f["total_amount"] for f in result)
    total_paid = sum(f["paid_amount"] for f in result)
    total_outstanding = sum(f["outstanding_amount"] for f in result)

    return {
        "fees": result,
        "summary": {
            "total_fees": total_fees,
            "total_paid": total_paid,
            "total_outstanding": total_outstanding
        }
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager", "Education Manager"])
def get_results(student_id=None, academic_year=None, academic_term=None):
    """
    Get student assessment results

    Args:
        student_id: Student ID
        academic_year: Filter by academic year
        academic_term: Filter by academic term
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    filters = {"student": student_id, "docstatus": 1}

    if academic_year:
        filters["academic_year"] = academic_year

    if academic_term:
        filters["academic_term"] = academic_term

    results = frappe.get_all(
        "Assessment Result",
        filters=filters,
        fields=[
            "name", "course", "assessment_plan", "academic_year",
            "academic_term", "total_score", "maximum_score",
            "grade", "grade_points"
        ],
        order_by="creation desc"
    )

    # Enrich with course details
    for result in results:
        course = frappe.db.get_value(
            "Course",
            result.course,
            ["course_name", "credit_hours"],
            as_dict=True
        )
        if course:
            result["course_name"] = course.course_name
            result["credit_hours"] = course.credit_hours

        result["percentage"] = round(
            (result.total_score / result.maximum_score) * 100, 2
        ) if result.maximum_score else 0

    # Calculate CGPA
    total_credits = sum(r.get("credit_hours", 0) or 0 for r in results if r.get("grade_points"))
    total_points = sum(
        (r.get("credit_hours", 0) or 0) * (r.get("grade_points", 0) or 0)
        for r in results if r.get("grade_points")
    )
    cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0

    return {
        "results": results,
        "summary": {
            "total_courses": len(results),
            "total_credits": total_credits,
            "cgpa": cgpa
        }
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager", "Education Manager"])
def get_timetable(student_id=None, date=None):
    """
    Get student timetable

    Args:
        student_id: Student ID
        date: Specific date (defaults to today)
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    if not date:
        date = nowdate()

    # Get current enrollment
    enrollment = frappe.db.get_value(
        "Program Enrollment",
        {"student": student_id},
        ["student_group", "program"],
        as_dict=True,
        order_by="creation desc"
    )

    if not enrollment or not enrollment.student_group:
        return {"schedule": [], "message": "No active enrollment found"}

    # Get schedule for the student group
    schedule = frappe.get_all(
        "Course Schedule",
        filters={
            "student_group": enrollment.student_group,
            "schedule_date": date
        },
        fields=[
            "name", "course", "instructor", "room",
            "from_time", "to_time", "schedule_date"
        ],
        order_by="from_time"
    )

    # Enrich with course and instructor names
    for entry in schedule:
        entry["course_name"] = frappe.db.get_value("Course", entry.course, "course_name")
        entry["instructor_name"] = frappe.db.get_value("Instructor", entry.instructor, "instructor_name")
        entry["room_name"] = frappe.db.get_value("Room", entry.room, "room_name") if entry.room else None

    return {"schedule": schedule, "date": date}


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager"])
def get_library_status(student_id=None):
    """
    Get student library status

    Args:
        student_id: Student ID
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    # Get library member
    member = frappe.db.get_value(
        "Library Member",
        {"student": student_id},
        ["name", "membership_expiry_date", "max_books_allowed"],
        as_dict=True
    )

    if not member:
        return {"has_membership": False, "message": "No library membership found"}

    # Get issued books
    issued_books = frappe.db.sql("""
        SELECT
            lt.name,
            la.title,
            la.author,
            lt.from_date as issue_date,
            lt.to_date as due_date,
            CASE
                WHEN lt.to_date < CURDATE() THEN 'Overdue'
                ELSE 'Active'
            END as status
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Article` la ON lt.article = la.name
        WHERE lt.library_member = %s
        AND lt.type = 'Issue'
        AND lt.docstatus = 1
        AND lt.name NOT IN (
            SELECT issue_reference FROM `tabLibrary Transaction`
            WHERE type = 'Return' AND docstatus = 1 AND issue_reference IS NOT NULL
        )
    """, (member.name,), as_dict=True)

    # Get pending fines
    pending_fines = frappe.db.sql("""
        SELECT SUM(fine_amount) as total
        FROM `tabLibrary Fine`
        WHERE library_member = %s
        AND status = 'Pending'
    """, (member.name,), as_dict=True)

    return {
        "has_membership": True,
        "member_id": member.name,
        "expiry_date": member.membership_expiry_date,
        "max_books": member.max_books_allowed,
        "books_issued": len(issued_books),
        "issued_books": issued_books,
        "pending_fines": pending_fines[0].total if pending_fines and pending_fines[0].total else 0
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Student", "System Manager"])
def get_hostel_details(student_id=None):
    """
    Get student hostel details

    Args:
        student_id: Student ID
    """
    if not student_id:
        student_id = get_current_student()

    if not student_id:
        raise NotFoundError("Student not found")

    # Get current allocation
    allocation = frappe.db.sql("""
        SELECT
            ha.name,
            ha.hostel_building,
            ha.hostel_room,
            ha.from_date,
            ha.to_date,
            hb.building_name,
            hr.room_number,
            hr.room_type,
            hr.floor
        FROM `tabHostel Allocation` ha
        JOIN `tabHostel Building` hb ON ha.hostel_building = hb.name
        JOIN `tabHostel Room` hr ON ha.hostel_room = hr.name
        WHERE ha.student = %s
        AND ha.docstatus = 1
        AND (ha.to_date IS NULL OR ha.to_date >= CURDATE())
        ORDER BY ha.from_date DESC
        LIMIT 1
    """, (student_id,), as_dict=True)

    if not allocation:
        return {"has_allocation": False, "message": "No hostel allocation found"}

    return {
        "has_allocation": True,
        "allocation_id": allocation[0].name,
        "building": allocation[0].building_name,
        "room_number": allocation[0].room_number,
        "room_type": allocation[0].room_type,
        "floor": allocation[0].floor,
        "from_date": allocation[0].from_date,
        "to_date": allocation[0].to_date
    }


# Helper functions

def get_current_student():
    """Get student ID for current user"""
    user = frappe.session.user

    student = frappe.db.get_value(
        "Student",
        {"user": user, "enabled": 1},
        "name"
    )

    if not student:
        student = frappe.db.get_value(
            "Student",
            {"student_email_id": user, "enabled": 1},
            "name"
        )

    return student

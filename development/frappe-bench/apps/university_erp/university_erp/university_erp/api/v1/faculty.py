# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Faculty API v1
Endpoints for faculty-related data
"""

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, add_days
from . import api_handler, NotFoundError, ValidationError


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Instructor", "System Manager", "Education Manager"])
def get_profile(instructor_id=None):
    """
    Get faculty profile

    Args:
        instructor_id: Instructor ID (optional, defaults to current user's instructor)
    """
    if not instructor_id:
        instructor_id = get_current_instructor()

    if not instructor_id:
        raise NotFoundError("Faculty profile not found")

    instructor = frappe.get_doc("Instructor", instructor_id)

    # Get employee details if linked
    employee_details = {}
    if instructor.employee:
        employee = frappe.db.get_value(
            "Employee",
            instructor.employee,
            ["employee_name", "department", "designation", "date_of_joining"],
            as_dict=True
        )
        if employee:
            employee_details = {
                "employee_id": instructor.employee,
                "employee_name": employee.employee_name,
                "department": employee.department,
                "designation": employee.designation,
                "date_of_joining": employee.date_of_joining
            }

    return {
        "instructor_id": instructor.name,
        "instructor_name": instructor.instructor_name,
        "department": instructor.department,
        "gender": instructor.gender,
        "image": instructor.image,
        "status": instructor.status,
        **employee_details
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Instructor", "System Manager", "Education Manager"])
def get_teaching_schedule(instructor_id=None, date=None, week=False):
    """
    Get faculty teaching schedule

    Args:
        instructor_id: Instructor ID
        date: Specific date (defaults to today)
        week: If True, return schedule for entire week
    """
    if not instructor_id:
        instructor_id = get_current_instructor()

    if not instructor_id:
        raise NotFoundError("Instructor not found")

    if not date:
        date = nowdate()

    date = getdate(date)

    if week:
        # Get Monday of the week
        start_date = date - frappe.utils.datetime.timedelta(days=date.weekday())
        end_date = start_date + frappe.utils.datetime.timedelta(days=6)
        date_filter = ["between", [start_date, end_date]]
    else:
        date_filter = date

    schedule = frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor_id,
            "schedule_date": date_filter
        },
        fields=[
            "name", "course", "student_group", "room",
            "from_time", "to_time", "schedule_date"
        ],
        order_by="schedule_date, from_time"
    )

    # Enrich with details
    for entry in schedule:
        entry["course_name"] = frappe.db.get_value("Course", entry.course, "course_name")
        entry["room_name"] = frappe.db.get_value("Room", entry.room, "room_name") if entry.room else None

        # Get student count
        student_count = frappe.db.count(
            "Student Group Student",
            {"parent": entry.student_group}
        )
        entry["student_count"] = student_count

    return {"schedule": schedule}


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Instructor", "System Manager", "Education Manager"])
def get_assigned_courses(instructor_id=None, academic_year=None):
    """
    Get courses assigned to faculty

    Args:
        instructor_id: Instructor ID
        academic_year: Filter by academic year
    """
    if not instructor_id:
        instructor_id = get_current_instructor()

    if not instructor_id:
        raise NotFoundError("Instructor not found")

    filters = {"instructor": instructor_id}

    if academic_year:
        filters["academic_year"] = academic_year

    assignments = frappe.get_all(
        "Instructor Log",
        filters=filters,
        fields=["course", "academic_year", "academic_term", "student_group"]
    )

    # Get unique courses
    courses = {}
    for assignment in assignments:
        if assignment.course not in courses:
            course_data = frappe.db.get_value(
                "Course",
                assignment.course,
                ["course_name", "course_code", "credit_hours"],
                as_dict=True
            )

            if course_data:
                courses[assignment.course] = {
                    "course_id": assignment.course,
                    "course_name": course_data.course_name,
                    "course_code": course_data.course_code,
                    "credit_hours": course_data.credit_hours,
                    "student_groups": []
                }

        if assignment.course in courses:
            courses[assignment.course]["student_groups"].append({
                "student_group": assignment.student_group,
                "academic_year": assignment.academic_year,
                "academic_term": assignment.academic_term
            })

    return {"courses": list(courses.values())}


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Instructor", "System Manager", "HR Manager"])
def get_leave_balance(instructor_id=None):
    """
    Get faculty leave balance

    Args:
        instructor_id: Instructor ID
    """
    if not instructor_id:
        instructor_id = get_current_instructor()

    if not instructor_id:
        raise NotFoundError("Instructor not found")

    # Get employee ID
    employee = frappe.db.get_value("Instructor", instructor_id, "employee")

    if not employee:
        return {"message": "No employee linked to instructor", "balances": []}

    # Get leave balances
    balances = frappe.get_all(
        "Leave Allocation",
        filters={
            "employee": employee,
            "docstatus": 1,
            "from_date": ["<=", nowdate()],
            "to_date": [">=", nowdate()]
        },
        fields=["leave_type", "total_leaves_allocated", "new_leaves_allocated"]
    )

    # Calculate used leaves
    for balance in balances:
        used = frappe.db.sql("""
            SELECT COALESCE(SUM(total_leave_days), 0) as used
            FROM `tabLeave Application`
            WHERE employee = %s
            AND leave_type = %s
            AND docstatus = 1
            AND status = 'Approved'
            AND from_date >= (
                SELECT from_date FROM `tabLeave Allocation`
                WHERE employee = %s AND leave_type = %s AND docstatus = 1
                ORDER BY from_date DESC LIMIT 1
            )
        """, (employee, balance.leave_type, employee, balance.leave_type), as_dict=True)

        balance["used_leaves"] = used[0].used if used else 0
        balance["remaining_leaves"] = balance.total_leaves_allocated - balance["used_leaves"]

    return {"employee": employee, "balances": balances}


@frappe.whitelist()
@api_handler(allowed_methods=["POST"], allowed_roles=["Instructor", "System Manager", "Education Manager"])
def mark_attendance(student_group, course, date, attendance_data):
    """
    Mark student attendance

    Args:
        student_group: Student Group name
        course: Course name
        date: Attendance date
        attendance_data: List of {student: student_id, status: Present/Absent}
    """
    instructor_id = get_current_instructor()

    if not instructor_id:
        raise NotFoundError("Instructor not found")

    # Validate instructor is assigned to this course
    assignment = frappe.db.exists(
        "Instructor Log",
        {"instructor": instructor_id, "course": course, "student_group": student_group}
    )

    if not assignment and not frappe.has_permission("Student Attendance", "write"):
        raise ValidationError("You are not authorized to mark attendance for this course")

    import json
    if isinstance(attendance_data, str):
        attendance_data = json.loads(attendance_data)

    results = []
    for record in attendance_data:
        try:
            # Check if attendance already exists
            existing = frappe.db.exists(
                "Student Attendance",
                {
                    "student": record["student"],
                    "course": course,
                    "date": date
                }
            )

            if existing:
                # Update existing
                frappe.db.set_value(
                    "Student Attendance",
                    existing,
                    "status",
                    record["status"]
                )
                results.append({
                    "student": record["student"],
                    "action": "updated",
                    "status": record["status"]
                })
            else:
                # Create new
                doc = frappe.get_doc({
                    "doctype": "Student Attendance",
                    "student": record["student"],
                    "course": course,
                    "student_group": student_group,
                    "date": date,
                    "status": record["status"]
                })
                doc.insert()
                results.append({
                    "student": record["student"],
                    "action": "created",
                    "status": record["status"]
                })

        except Exception as e:
            results.append({
                "student": record.get("student"),
                "action": "error",
                "error": str(e)
            })

    frappe.db.commit()

    return {
        "date": date,
        "course": course,
        "student_group": student_group,
        "results": results,
        "total_marked": len([r for r in results if r["action"] != "error"])
    }


@frappe.whitelist()
@api_handler(allowed_methods=["GET"], allowed_roles=["Instructor", "System Manager", "Education Manager"])
def get_student_list(student_group=None, course=None):
    """
    Get list of students

    Args:
        student_group: Student Group name
        course: Course name (to get enrolled students)
    """
    instructor_id = get_current_instructor()

    if not instructor_id and not frappe.has_permission("Student", "read"):
        raise ValidationError("You are not authorized to view student list")

    if student_group:
        # Get students from student group
        students = frappe.db.sql("""
            SELECT
                sgs.student,
                s.student_name,
                s.student_email_id as email,
                s.image
            FROM `tabStudent Group Student` sgs
            JOIN `tabStudent` s ON sgs.student = s.name
            WHERE sgs.parent = %s
            AND s.enabled = 1
            ORDER BY s.student_name
        """, (student_group,), as_dict=True)

    elif course:
        # Get students enrolled in course
        students = frappe.db.sql("""
            SELECT DISTINCT
                ce.student,
                s.student_name,
                s.student_email_id as email,
                s.image
            FROM `tabCourse Enrollment` ce
            JOIN `tabStudent` s ON ce.student = s.name
            WHERE ce.course = %s
            AND ce.docstatus = 1
            AND s.enabled = 1
            ORDER BY s.student_name
        """, (course,), as_dict=True)

    else:
        # Get all assigned students
        students = frappe.db.sql("""
            SELECT DISTINCT
                sgs.student,
                s.student_name,
                s.student_email_id as email,
                s.image
            FROM `tabInstructor Log` il
            JOIN `tabStudent Group Student` sgs ON il.student_group = sgs.parent
            JOIN `tabStudent` s ON sgs.student = s.name
            WHERE il.instructor = %s
            AND s.enabled = 1
            ORDER BY s.student_name
        """, (instructor_id,), as_dict=True)

    return {"students": students, "count": len(students)}


# Helper functions

def get_current_instructor():
    """Get instructor ID for current user"""
    user = frappe.session.user

    # Try to get instructor from user
    instructor = frappe.db.get_value(
        "Instructor",
        {"user_id": user},
        "name"
    )

    if not instructor:
        # Try via employee
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee:
            instructor = frappe.db.get_value(
                "Instructor",
                {"employee": employee},
                "name"
            )

    return instructor

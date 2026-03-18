# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, flt, today


def get_current_faculty():
    """Get current logged-in faculty's employee record.

    Maps session user -> Employee with custom_is_faculty=1.
    Returns dict with name, employee_name, department, designation, user_id.
    """
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)

    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user, "custom_is_faculty": 1, "status": "Active"},
        ["name", "employee_name", "department", "designation", "user_id"],
        as_dict=True,
    )

    if not employee:
        frappe.throw(
            _("No active faculty profile found for this user"),
            frappe.PermissionError,
        )

    return employee


def _get_faculty_teaching_assignments(employee_name, academic_term=None):
    """Get all active teaching assignments for a faculty member."""
    filters = {
        "instructor": employee_name,
        "docstatus": 1,
    }
    if academic_term:
        filters["academic_term"] = academic_term

    return frappe.get_all(
        "Teaching Assignment",
        filters=filters,
        fields=[
            "name",
            "course",
            "course_name",
            "student_group",
            "academic_term",
            "total_weekly_hours",
        ],
    )


def _get_current_academic_term():
    """Get the current active academic term."""
    today_date = nowdate()
    term = frappe.db.get_value(
        "Academic Term",
        {
            "term_start_date": ["<=", today_date],
            "term_end_date": [">=", today_date],
        },
        ["name", "term_start_date", "term_end_date"],
        as_dict=True,
    )
    return term


# ==================== Plan 01 Active Endpoints ====================


@frappe.whitelist()
def get_faculty_dashboard():
    """Get faculty dashboard data: today's classes, pending tasks, announcements."""
    employee = get_current_faculty()

    today_classes = _get_today_classes_internal(employee)
    pending_tasks = _get_pending_tasks_internal(employee, today_classes)
    announcements = _get_recent_announcements(limit=3)

    return {
        "today_classes": today_classes,
        "pending_tasks": pending_tasks,
        "announcements": announcements,
    }


@frappe.whitelist()
def get_today_classes():
    """Get today's classes for the current faculty.

    Returns list of classes with is_marked status and student_count.
    """
    employee = get_current_faculty()
    return _get_today_classes_internal(employee)


def _get_today_classes_internal(employee):
    """Internal: Get today's classes from Teaching Assignment Schedule."""
    today_date = nowdate()
    today_day = getdate(today_date).strftime("%A")

    # Get teaching assignments for this faculty
    assignments = _get_faculty_teaching_assignments(employee.name)
    if not assignments:
        return []

    classes = []
    for assignment in assignments:
        # Get schedule entries for today's day of week
        schedules = frappe.get_all(
            "Teaching Assignment Schedule",
            filters={"parent": assignment.name, "day": today_day},
            fields=["name", "day", "start_time", "end_time", "room"],
        )

        for schedule in schedules:
            # Check if attendance is already marked via Course Schedule
            course_schedule = frappe.db.get_value(
                "Course Schedule",
                {
                    "course": assignment.course,
                    "instructor": employee.name,
                    "schedule_date": today_date,
                    "from_time": schedule.start_time,
                },
                "name",
            )

            is_marked = False
            if course_schedule:
                existing_attendance = frappe.db.count(
                    "Student Attendance",
                    {"course_schedule": course_schedule, "date": today_date},
                )
                is_marked = existing_attendance > 0

            # Get student count from student group enrollment
            student_count = 0
            if assignment.student_group:
                student_count = frappe.db.count(
                    "Student Group Student",
                    {"parent": assignment.student_group},
                )

            classes.append(
                {
                    "name": course_schedule or schedule.name,
                    "course": assignment.course,
                    "course_name": assignment.course_name,
                    "room": schedule.room or "",
                    "start_time": str(schedule.start_time),
                    "end_time": str(schedule.end_time),
                    "section": assignment.student_group or "",
                    "schedule_date": today_date,
                    "is_marked": is_marked,
                    "student_count": student_count,
                }
            )

    # Sort by start_time
    classes.sort(key=lambda c: c["start_time"])
    return classes


def _get_pending_tasks_internal(employee, today_classes=None):
    """Internal: Get pending task counts for dashboard KPIs."""
    if today_classes is None:
        today_classes = _get_today_classes_internal(employee)

    classes_today = len(today_classes)
    unmarked_attendance = sum(1 for c in today_classes if not c["is_marked"])

    # Count pending grades: Assessment Plans for current term where results < enrollments
    pending_grades = 0
    term = _get_current_academic_term()
    if term:
        assignments = _get_faculty_teaching_assignments(
            employee.name, term.name
        )
        for assignment in assignments:
            plans = frappe.get_all(
                "Assessment Plan",
                filters={
                    "course": assignment.course,
                    "academic_term": term.name,
                    "docstatus": 1,
                },
                fields=["name"],
            )
            for plan in plans:
                result_count = frappe.db.count(
                    "Assessment Result",
                    {"assessment_plan": plan.name, "docstatus": 1},
                )
                # If no results at all, count as pending
                if result_count == 0:
                    pending_grades += 1

    # Count pending student leave requests
    pending_leave_requests = 0
    if frappe.db.exists("DocType", "Student Leave Application"):
        assignments = _get_faculty_teaching_assignments(employee.name)
        courses = [a.course for a in assignments]
        if courses:
            pending_leave_requests = frappe.db.count(
                "Student Leave Application",
                {"status": "Open"},
            )

    return {
        "classes_today": classes_today,
        "unmarked_attendance": unmarked_attendance,
        "pending_grades": pending_grades,
        "pending_leave_requests": pending_leave_requests,
    }


@frappe.whitelist()
def get_weekly_timetable(week_start=None):
    """Get weekly timetable based on Teaching Assignment Schedule.

    Returns: {week_start, days, slots}
    """
    employee = get_current_faculty()

    if week_start:
        week_start = getdate(week_start)
    else:
        # Get Monday of current week
        today_obj = getdate(nowdate())
        week_start = today_obj - __import__("datetime").timedelta(
            days=today_obj.weekday()
        )

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    assignments = _get_faculty_teaching_assignments(employee.name)

    slots = []
    for assignment in assignments:
        schedules = frappe.get_all(
            "Teaching Assignment Schedule",
            filters={
                "parent": assignment.name,
                "day": ["in", days],
            },
            fields=["day", "start_time", "end_time", "room"],
        )

        for schedule in schedules:
            slots.append(
                {
                    "day": schedule.day[:3],  # Mon, Tue, etc.
                    "start_time": str(schedule.start_time),
                    "end_time": str(schedule.end_time),
                    "course": assignment.course,
                    "course_name": assignment.course_name,
                    "room": schedule.room or "",
                    "section": assignment.student_group or "",
                }
            )

    # Sort by day order then start_time
    day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}
    slots.sort(key=lambda s: (day_order.get(s["day"], 9), s["start_time"]))

    return {
        "week_start": str(week_start),
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "slots": slots,
    }


@frappe.whitelist()
def get_students_for_attendance(course_schedule):
    """Get student list for attendance marking.

    Verifies the faculty teaches this course before returning students.
    Returns list of {student, student_name, roll_no, enrollment_no, image}.
    """
    employee = get_current_faculty()

    # Get course info from course schedule
    schedule = frappe.db.get_value(
        "Course Schedule",
        course_schedule,
        ["course", "student_group", "instructor"],
        as_dict=True,
    )

    if not schedule:
        # May be a Teaching Assignment Schedule name, resolve course
        tas = frappe.db.get_value(
            "Teaching Assignment Schedule",
            course_schedule,
            ["parent"],
            as_dict=True,
        )
        if tas:
            assignment = frappe.db.get_value(
                "Teaching Assignment",
                tas.parent,
                ["course", "student_group", "instructor"],
                as_dict=True,
            )
            if assignment:
                schedule = assignment

    if not schedule:
        frappe.throw(_("Class schedule not found"))

    # Get students from student group
    students = []
    if schedule.get("student_group"):
        students = frappe.db.sql(
            """
            SELECT
                sgs.student,
                sgs.student_name,
                s.custom_roll_number as roll_no,
                s.name as enrollment_no,
                s.image
            FROM `tabStudent Group Student` sgs
            LEFT JOIN `tabStudent` s ON s.name = sgs.student
            WHERE sgs.parent = %s
            ORDER BY s.custom_roll_number, sgs.student_name
        """,
            schedule.student_group,
            as_dict=True,
        )
    else:
        # Fallback: get from Course Enrollment
        students = frappe.db.sql(
            """
            SELECT
                ce.student,
                ce.student_name,
                s.custom_roll_number as roll_no,
                s.name as enrollment_no,
                s.image
            FROM `tabCourse Enrollment` ce
            LEFT JOIN `tabStudent` s ON s.name = ce.student
            WHERE ce.course = %s
            ORDER BY s.custom_roll_number, ce.student_name
        """,
            schedule.course,
            as_dict=True,
        )

    return students


@frappe.whitelist()
def submit_attendance(course_schedule, attendance_data):
    """Submit attendance for a class with idempotency check.

    Args:
        course_schedule: Course Schedule name
        attendance_data: JSON string of [{student, status}]

    Returns: {present, absent, percentage, total}
    """
    if isinstance(attendance_data, str):
        attendance_data = json.loads(attendance_data)

    employee = get_current_faculty()

    # Get schedule info
    schedule = frappe.db.get_value(
        "Course Schedule",
        course_schedule,
        ["course", "schedule_date", "instructor", "student_group"],
        as_dict=True,
    )

    if not schedule:
        frappe.throw(_("Course Schedule not found"))

    # Idempotency: check for existing attendance records
    existing = frappe.db.count(
        "Student Attendance",
        {"course_schedule": course_schedule, "date": schedule.schedule_date},
    )
    if existing > 0:
        frappe.throw(
            _("Attendance has already been submitted for this class")
        )

    # Create Student Attendance records
    created = 0
    for entry in attendance_data:
        try:
            attendance = frappe.new_doc("Student Attendance")
            attendance.student = entry.get("student")
            attendance.course_schedule = course_schedule
            attendance.status = entry.get("status", "Present")
            attendance.date = schedule.schedule_date
            attendance.course = schedule.course
            attendance.student_group = schedule.student_group
            attendance.insert(ignore_permissions=True)
            created += 1
        except Exception:
            frappe.log_error(
                f"Attendance creation failed for {entry.get('student')}"
            )

    frappe.db.commit()

    present = sum(
        1 for s in attendance_data if s.get("status") == "Present"
    )
    absent = len(attendance_data) - present
    total = len(attendance_data)

    return {
        "present": present,
        "absent": absent,
        "percentage": round((present / total) * 100, 1) if total > 0 else 0,
        "total": total,
    }


@frappe.whitelist()
def get_announcements(category=None, search=None, start=0, page_length=20):
    """Get paginated announcements from Notice Board.

    Args:
        category: Filter by category (Academic, Administrative, Emergency)
        search: Search by title
        start: Pagination offset
        page_length: Items per page

    Returns: {data: [...], total_count}
    """
    get_current_faculty()  # Auth check

    filters = {}
    if category:
        filters["category"] = category

    or_filters = {}
    if search:
        or_filters["title"] = ["like", f"%{search}%"]

    notices = frappe.get_all(
        "Notice Board",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=[
            "name",
            "title",
            "category",
            "posting_date",
            "content",
        ],
        order_by="posting_date desc",
        start=int(start),
        page_length=int(page_length),
    )

    # Truncate content for list view
    for notice in notices:
        if notice.get("content") and len(notice["content"]) > 200:
            notice["content"] = notice["content"][:200] + "..."

    total_count = frappe.db.count("Notice Board", filters=filters)

    return {"data": notices, "total_count": total_count}


def _get_recent_announcements(limit=3):
    """Get recent announcements for dashboard."""
    notices = frappe.get_all(
        "Notice Board",
        fields=["name", "title", "category", "posting_date", "content"],
        order_by="posting_date desc",
        limit=limit,
    )

    for notice in notices:
        if notice.get("content") and len(notice["content"]) > 200:
            notice["content"] = notice["content"][:200] + "..."

    return notices


# ==================== Plan 02 Stub Endpoints (Grades, Students) ====================


@frappe.whitelist()
def get_students_for_grading(course, assessment_plan):
    """Get students for grade entry. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(_("Grade entry not yet implemented"), frappe.ValidationError)


@frappe.whitelist()
def save_draft_grade(**kwargs):
    """Save draft grade for a student. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(_("Grade save not yet implemented"), frappe.ValidationError)


@frappe.whitelist()
def submit_grades(course, assessment_plan):
    """Submit final grades. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(
        _("Grade submission not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_grade_analytics(course, assessment_plan):
    """Get grade analytics for side panel. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(
        _("Grade analytics not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_student_list(**kwargs):
    """Get student list with attendance and grades. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(
        _("Student list not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_student_detail(student, course):
    """Get student detail with history. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(
        _("Student detail not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_performance_analytics(course):
    """Get course performance analytics. Stub -- implemented in Plan 02."""
    get_current_faculty()
    frappe.throw(
        _("Performance analytics not yet implemented"), frappe.ValidationError
    )


# ==================== Plan 03 Stub Endpoints (Leave, LMS, Research, OBE, Workload) ====================


@frappe.whitelist()
def get_leave_balance():
    """Get faculty leave balance. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Leave balance not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def apply_leave(**kwargs):
    """Apply for leave. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Leave application not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_leave_history(**kwargs):
    """Get leave application history. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Leave history not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_student_leave_requests(**kwargs):
    """Get student leave requests for approval. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Student leave requests not yet implemented"),
        frappe.ValidationError,
    )


@frappe.whitelist()
def approve_student_leave(name):
    """Approve student leave. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Student leave approval not yet implemented"),
        frappe.ValidationError,
    )


@frappe.whitelist()
def reject_student_leave(name, reason=None):
    """Reject student leave. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Student leave rejection not yet implemented"),
        frappe.ValidationError,
    )


@frappe.whitelist()
def get_lms_courses():
    """Get LMS courses for faculty. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("LMS courses not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_lms_course_content(course):
    """Get LMS course content. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("LMS content not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def save_lms_content(**kwargs):
    """Save LMS content. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("LMS content save not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def delete_lms_content(doctype, name):
    """Delete LMS content. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("LMS content delete not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_publications():
    """Get faculty publications. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Publications not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_copo_matrix(course):
    """Get CO-PO attainment matrix. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("CO-PO matrix not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_copo_student_detail(course, co):
    """Get student-level CO attainment. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("CO-PO student detail not yet implemented"), frappe.ValidationError
    )


@frappe.whitelist()
def get_workload_summary():
    """Get workload summary. Stub -- implemented in Plan 03."""
    get_current_faculty()
    frappe.throw(
        _("Workload summary not yet implemented"), frappe.ValidationError
    )

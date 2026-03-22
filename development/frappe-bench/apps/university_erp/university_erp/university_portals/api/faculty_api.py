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
        # For System Manager / Administrator, try to find ANY active faculty
        # to allow admin testing of faculty portal features
        if "System Manager" in frappe.get_roles(user):
            employee = frappe.db.get_value(
                "Employee",
                {"custom_is_faculty": 1, "status": "Active"},
                ["name", "employee_name", "department", "designation", "user_id"],
                as_dict=True,
            )
        if not employee:
            return None

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


@frappe.whitelist(methods=["GET"])
def get_faculty_dashboard():
    """Get faculty dashboard data: today's classes, pending tasks, announcements."""
    employee = get_current_faculty()
    if not employee:
        return {"today_classes": [], "pending_tasks": [], "announcements": [], "no_faculty_profile": True}

    today_classes = _get_today_classes_internal(employee)
    pending_tasks = _get_pending_tasks_internal(employee, today_classes)
    announcements = _get_recent_announcements(limit=3)

    return {
        "today_classes": today_classes,
        "pending_tasks": pending_tasks,
        "announcements": announcements,
    }


@frappe.whitelist(methods=["GET"])
def get_today_classes():
    """Get today's classes for the current faculty.

    Returns list of classes with is_marked status and student_count.
    """
    employee = get_current_faculty()
    if not employee:
        return {}

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


@frappe.whitelist(methods=["GET"])
def get_weekly_timetable(week_start=None):
    """Get weekly timetable based on Teaching Assignment Schedule.

    Returns: {week_start, days, slots}
    """
    employee = get_current_faculty()
    if not employee:
        return {}


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


@frappe.whitelist(methods=["GET"])
def get_students_for_attendance(course_schedule):
    """Get student list for attendance marking.

    Verifies the faculty teaches this course before returning students.
    Returns list of {student, student_name, roll_no, enrollment_no, image}.
    """
    employee = get_current_faculty()
    if not employee:
        return {}


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
    if not employee:
        return {}


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


@frappe.whitelist(methods=["GET"])
def get_announcements(category=None, search=None, start=0, page_length=20):
    """Get paginated announcements from Notice Board.

    Args:
        category: Filter by category (Academic, Administrative, Emergency)
        search: Search by title
        start: Pagination offset
        page_length: Items per page

    Returns: {data: [...], total_count}
    """
    # Announcements are readable by any authenticated user
    if not frappe.session.user or frappe.session.user == "Guest":
        return {"data": [], "total_count": 0}

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


# ==================== Plan 02 Active Endpoints (Grades, Students) ====================


def _verify_faculty_teaches_course(employee_name, course):
    """Verify that the faculty member teaches the given course."""
    exists = frappe.db.exists(
        "Teaching Assignment",
        {"instructor": employee_name, "course": course, "docstatus": 1},
    )
    if not exists:
        frappe.throw(
            _("You are not authorized to access this course"),
            frappe.PermissionError,
        )


@frappe.whitelist(methods=["GET"])
def get_students_for_grading(course, assessment_plan):
    """Get students for grade entry with existing grades.

    Returns:
        {students: [{student, student_name, roll_no, grades: [{assessment_name, marks, grade, docstatus}]}],
         assessments: [{name, assessment_type, max_marks}]}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    _verify_faculty_teaches_course(employee.name, course)

    # Get assessment criteria from Assessment Plan
    plan = frappe.get_doc("Assessment Plan", assessment_plan)
    assessments = []
    for criteria in plan.get("assessment_criteria", []):
        assessments.append(
            {
                "name": criteria.assessment_criteria,
                "assessment_type": plan.assessment_type or "",
                "max_marks": flt(criteria.maximum_score),
            }
        )

    # Get enrolled students
    assignment = frappe.db.get_value(
        "Teaching Assignment",
        {"instructor": employee.name, "course": course, "docstatus": 1},
        "student_group",
    )

    students_raw = []
    if assignment:
        students_raw = frappe.db.sql(
            """
            SELECT
                sgs.student,
                sgs.student_name,
                s.custom_roll_number as roll_no
            FROM `tabStudent Group Student` sgs
            LEFT JOIN `tabStudent` s ON s.name = sgs.student
            WHERE sgs.parent = %(student_group)s
            ORDER BY s.custom_roll_number, sgs.student_name
            """,
            {"student_group": assignment},
            as_dict=True,
        )
    else:
        students_raw = frappe.db.sql(
            """
            SELECT
                ce.student,
                ce.student_name,
                s.custom_roll_number as roll_no
            FROM `tabCourse Enrollment` ce
            LEFT JOIN `tabStudent` s ON s.name = ce.student
            WHERE ce.course = %(course)s
            ORDER BY s.custom_roll_number, ce.student_name
            """,
            {"course": course},
            as_dict=True,
        )

    # Get existing Assessment Results
    students = []
    for stu in students_raw:
        grades = []
        for assess in assessments:
            result = frappe.db.sql(
                """
                SELECT ar.docstatus, ard.grade, ard.score as marks
                FROM `tabAssessment Result` ar
                INNER JOIN `tabAssessment Result Detail` ard ON ard.parent = ar.name
                WHERE ar.student = %(student)s
                  AND ar.assessment_plan = %(assessment_plan)s
                  AND ard.assessment_criteria = %(criteria)s
                LIMIT 1
                """,
                {
                    "student": stu.student,
                    "assessment_plan": assessment_plan,
                    "criteria": assess["name"],
                },
                as_dict=True,
            )
            if result:
                grades.append(
                    {
                        "assessment_name": assess["name"],
                        "marks": flt(result[0].marks),
                        "grade": result[0].grade or None,
                        "docstatus": result[0].docstatus,
                    }
                )
            else:
                grades.append(
                    {
                        "assessment_name": assess["name"],
                        "marks": None,
                        "grade": None,
                        "docstatus": 0,
                    }
                )

        students.append(
            {
                "student": stu.student,
                "student_name": stu.student_name,
                "roll_no": stu.roll_no or "",
                "grades": grades,
            }
        )

    return {"students": students, "assessments": assessments}


@frappe.whitelist()
def save_draft_grade(**kwargs):
    """Save draft grade for a student.

    Args:
        student, course, assessment_plan, assessment_name, marks

    Returns:
        {grade: computed_grade, marks: entered_marks, status: "saved"}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    student = kwargs.get("student")
    course = kwargs.get("course")
    assessment_plan = kwargs.get("assessment_plan")
    assessment_name = kwargs.get("assessment_name")
    marks = kwargs.get("marks")

    _verify_faculty_teaches_course(employee.name, course)

    # Find or create Assessment Result (draft)
    existing = frappe.db.get_value(
        "Assessment Result",
        {
            "student": student,
            "assessment_plan": assessment_plan,
            "docstatus": 0,
        },
        "name",
    )

    if existing:
        doc = frappe.get_doc("Assessment Result", existing)
    else:
        doc = frappe.new_doc("Assessment Result")
        doc.student = student
        doc.assessment_plan = assessment_plan
        doc.course = course
        plan = frappe.get_doc("Assessment Plan", assessment_plan)
        doc.academic_year = plan.academic_year if plan.get("academic_year") else ""
        doc.academic_term = plan.academic_term if plan.get("academic_term") else ""
        doc.student_group = plan.student_group if plan.get("student_group") else ""
        doc.grading_scale = plan.grading_scale if plan.get("grading_scale") else ""

    # Update the specific criteria row
    found = False
    for row in doc.get("details", []):
        if row.assessment_criteria == assessment_name:
            row.score = flt(marks) if marks else 0
            found = True
            break

    if not found:
        doc.append(
            "details",
            {
                "assessment_criteria": assessment_name,
                "score": flt(marks) if marks else 0,
            },
        )

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    computed_grade = None
    for row in doc.get("details", []):
        if row.assessment_criteria == assessment_name:
            computed_grade = row.grade
            break

    return {
        "grade": computed_grade,
        "marks": flt(marks),
        "status": "saved",
    }


@frappe.whitelist()
def submit_grades(course, assessment_plan):
    """Submit/finalize all draft grades for a course + assessment plan.

    Returns:
        {submitted_count, message}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    _verify_faculty_teaches_course(employee.name, course)

    drafts = frappe.get_all(
        "Assessment Result",
        filters={
            "assessment_plan": assessment_plan,
            "docstatus": 0,
        },
        fields=["name"],
    )

    submitted_count = 0
    for draft in drafts:
        try:
            doc = frappe.get_doc("Assessment Result", draft.name)
            doc.submit()
            submitted_count += 1
        except Exception:
            frappe.log_error(
                f"Grade submission failed for {draft.name}"
            )

    frappe.db.commit()

    return {
        "submitted_count": submitted_count,
        "message": _("{0} grade(s) submitted successfully").format(
            submitted_count
        ),
    }


@frappe.whitelist(methods=["GET"])
def get_grade_analytics(course, assessment_plan):
    """Get grade analytics for the side panel.

    Returns:
        {distribution: {grade: count}, average, pass_count, fail_count,
         at_risk_count, at_risk_threshold}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    _verify_faculty_teaches_course(employee.name, course)

    at_risk_threshold = 40

    results = frappe.db.sql(
        """
        SELECT ar.student, ar.total_score, ar.grade
        FROM `tabAssessment Result` ar
        WHERE ar.assessment_plan = %(assessment_plan)s
        """,
        {"assessment_plan": assessment_plan},
        as_dict=True,
    )

    if not results:
        return {
            "distribution": {},
            "average": 0,
            "pass_count": 0,
            "fail_count": 0,
            "at_risk_count": 0,
            "at_risk_threshold": at_risk_threshold,
        }

    distribution = {}
    total_score = 0
    pass_count = 0
    fail_count = 0
    at_risk_count = 0

    for r in results:
        grade = r.grade or "Ungraded"
        distribution[grade] = distribution.get(grade, 0) + 1
        score = flt(r.total_score)
        total_score += score

        if grade.upper() in ("F", "FAIL"):
            fail_count += 1
        else:
            pass_count += 1

        if score < at_risk_threshold:
            at_risk_count += 1

    average = round(total_score / len(results), 1) if results else 0

    return {
        "distribution": distribution,
        "average": average,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "at_risk_count": at_risk_count,
        "at_risk_threshold": at_risk_threshold,
    }


@frappe.whitelist(methods=["GET"])
def get_student_list(**kwargs):
    """Get paginated student list with attendance and grades.

    Args:
        course, section, search, start, page_length, order_by

    Returns:
        {data: [{student, student_name, roll_no, enrollment_no, image,
                 attendance_percentage, current_grade}], total_count}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    course = kwargs.get("course")
    section = kwargs.get("section")
    search = kwargs.get("search")
    start = int(kwargs.get("start", 0))
    page_length = int(kwargs.get("page_length", 20))
    order_by = kwargs.get("order_by", "student_name")

    _verify_faculty_teaches_course(employee.name, course)

    conditions = "WHERE ce.course = %(course)s"
    params = {"course": course, "start": start, "page_length": page_length}

    if search:
        conditions += " AND (ce.student_name LIKE %(search)s OR s.custom_roll_number LIKE %(search)s)"
        params["search"] = f"%{search}%"

    count_sql = """
        SELECT COUNT(*) as cnt
        FROM `tabCourse Enrollment` ce
        LEFT JOIN `tabStudent` s ON s.name = ce.student
        {conditions}
    """.format(conditions=conditions)
    total_count = frappe.db.sql(count_sql, params, as_dict=True)[0].cnt

    allowed_order = {
        "student_name": "ce.student_name",
        "roll_no": "s.custom_roll_number",
    }
    order_clause = allowed_order.get(order_by, "ce.student_name")

    sql = """
        SELECT
            ce.student,
            ce.student_name,
            s.custom_roll_number as roll_no,
            s.name as enrollment_no,
            s.image
        FROM `tabCourse Enrollment` ce
        LEFT JOIN `tabStudent` s ON s.name = ce.student
        {conditions}
        ORDER BY {order_clause}
        LIMIT %(start)s, %(page_length)s
    """.format(conditions=conditions, order_clause=order_clause)
    students = frappe.db.sql(sql, params, as_dict=True)

    for stu in students:
        total_att = frappe.db.count(
            "Student Attendance",
            {"student": stu.student, "course": course},
        )
        present_att = frappe.db.count(
            "Student Attendance",
            {
                "student": stu.student,
                "course": course,
                "status": "Present",
            },
        )
        stu["attendance_percentage"] = (
            round((present_att / total_att) * 100, 1)
            if total_att > 0
            else 0
        )

        latest_grade = frappe.db.get_value(
            "Assessment Result",
            {
                "student": stu.student,
                "course": course,
                "docstatus": ["in", [0, 1]],
            },
            "grade",
            order_by="creation desc",
        )
        stu["current_grade"] = latest_grade or "-"

    return {"data": students, "total_count": total_count}


@frappe.whitelist(methods=["GET"])
def get_student_detail(student, course):
    """Get student detail with attendance history, assessment marks, grade trend.

    Returns:
        {attendance_history, assessment_marks, grade_trend}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    _verify_faculty_teaches_course(employee.name, course)

    attendance_history = frappe.db.sql(
        """
        SELECT date, status
        FROM `tabStudent Attendance`
        WHERE student = %(student)s AND course = %(course)s
        ORDER BY date DESC
        LIMIT 30
        """,
        {"student": student, "course": course},
        as_dict=True,
    )

    assessment_marks = frappe.db.sql(
        """
        SELECT
            ard.assessment_criteria as assessment_name,
            ard.score as marks,
            ard.maximum_score as max_marks,
            ard.grade
        FROM `tabAssessment Result` ar
        INNER JOIN `tabAssessment Result Detail` ard ON ard.parent = ar.name
        WHERE ar.student = %(student)s AND ar.course = %(course)s
        ORDER BY ar.creation
        """,
        {"student": student, "course": course},
        as_dict=True,
    )

    grade_trend = []
    for mark in assessment_marks:
        max_marks = flt(mark.max_marks) or 100
        grade_trend.append(
            {
                "assessment_name": mark.assessment_name,
                "marks_percentage": round(
                    (flt(mark.marks) / max_marks) * 100, 1
                ),
            }
        )

    return {
        "attendance_history": attendance_history,
        "assessment_marks": assessment_marks,
        "grade_trend": grade_trend,
    }


@frappe.whitelist(methods=["GET"])
def get_performance_analytics(course):
    """Get course performance analytics with charts data.

    Returns:
        {grade_distribution, attendance_correlation, assessment_trend, batch_comparison}
    """
    employee = get_current_faculty()
    if not employee:
        return {}

    _verify_faculty_teaches_course(employee.name, course)

    # Grade distribution
    grade_dist = frappe.db.sql(
        """
        SELECT grade, COUNT(*) as cnt
        FROM `tabAssessment Result`
        WHERE course = %(course)s AND docstatus IN (0, 1)
        GROUP BY grade
        ORDER BY grade
        """,
        {"course": course},
        as_dict=True,
    )
    grade_labels = [r.grade or "Ungraded" for r in grade_dist]
    grade_data = [r.cnt for r in grade_dist]

    # Attendance correlation
    attendance_buckets = ["0-50%", "50-60%", "60-75%", "75-90%", "90-100%"]
    att_corr_data = []
    bucket_ranges = [(0, 50), (50, 60), (60, 75), (75, 90), (90, 100)]

    for low, high in bucket_ranges:
        avg = frappe.db.sql(
            """
            SELECT AVG(ar.total_score) as avg_score
            FROM `tabAssessment Result` ar
            WHERE ar.course = %(course)s
              AND ar.student IN (
                SELECT sa.student
                FROM `tabStudent Attendance` sa
                WHERE sa.course = %(course)s
                GROUP BY sa.student
                HAVING (SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100
                  BETWEEN %(low)s AND %(high)s
              )
            """,
            {"course": course, "low": low, "high": high},
            as_dict=True,
        )
        att_corr_data.append(round(flt(avg[0].avg_score if avg else 0), 1))

    # Assessment trend
    trend = frappe.db.sql(
        """
        SELECT ard.assessment_criteria, AVG(ard.score) as avg_score
        FROM `tabAssessment Result` ar
        INNER JOIN `tabAssessment Result Detail` ard ON ard.parent = ar.name
        WHERE ar.course = %(course)s
        GROUP BY ard.assessment_criteria
        ORDER BY ard.assessment_criteria
        """,
        {"course": course},
        as_dict=True,
    )
    trend_labels = [r.assessment_criteria for r in trend]
    trend_data = [round(flt(r.avg_score), 1) for r in trend]

    # Batch comparison
    current_term = _get_current_academic_term()
    current_avg = 0
    current_pass = 0
    previous_avg = 0
    previous_pass = 0

    if current_term:
        current_stats = frappe.db.sql(
            """
            SELECT AVG(total_score) as avg_score,
                   SUM(CASE WHEN grade NOT IN ('F', 'Fail') THEN 1 ELSE 0 END) as pass_count,
                   COUNT(*) as total
            FROM `tabAssessment Result`
            WHERE course = %(course)s AND academic_term = %(term)s
            """,
            {"course": course, "term": current_term.name},
            as_dict=True,
        )
        if current_stats and current_stats[0].total:
            current_avg = round(flt(current_stats[0].avg_score), 1)
            current_pass = round(
                (flt(current_stats[0].pass_count) / flt(current_stats[0].total)) * 100, 1
            )

        prev_term = frappe.db.get_value(
            "Academic Term",
            {"term_end_date": ["<", current_term.term_start_date]},
            "name",
            order_by="term_end_date desc",
        )
        if prev_term:
            prev_stats = frappe.db.sql(
                """
                SELECT AVG(total_score) as avg_score,
                       SUM(CASE WHEN grade NOT IN ('F', 'Fail') THEN 1 ELSE 0 END) as pass_count,
                       COUNT(*) as total
                FROM `tabAssessment Result`
                WHERE course = %(course)s AND academic_term = %(term)s
                """,
                {"course": course, "term": prev_term},
                as_dict=True,
            )
            if prev_stats and prev_stats[0].total:
                previous_avg = round(flt(prev_stats[0].avg_score), 1)
                previous_pass = round(
                    (flt(prev_stats[0].pass_count) / flt(prev_stats[0].total)) * 100, 1
                )

    return {
        "grade_distribution": {"labels": grade_labels, "data": grade_data},
        "attendance_correlation": {
            "labels": attendance_buckets,
            "data": att_corr_data,
        },
        "assessment_trend": {
            "labels": trend_labels,
            "series": [{"name": "Class Average", "data": trend_data}],
        },
        "batch_comparison": {
            "current": {"average": current_avg, "pass_rate": current_pass},
            "previous": {
                "average": previous_avg,
                "pass_rate": previous_pass,
            },
        },
    }


# ==================== Plan 03 Active Endpoints (Leave, LMS, Research, OBE, Workload) ====================


@frappe.whitelist(methods=["GET"])
def get_leave_balance():
    """Get faculty leave balance with used/total per leave type."""
    employee = get_current_faculty()
    if not employee:
        return {}


    # Get leave allocations for this employee in the current leave period
    allocations = frappe.db.sql(
        """
        SELECT
            la.leave_type,
            la.total_leaves_allocated as total,
            la.total_leaves_allocated - la.total_leaves_encashed
                - la.unused_leaves as used
        FROM `tabLeave Allocation` la
        WHERE la.employee = %(employee)s
            AND la.docstatus = 1
            AND la.from_date <= %(today)s
            AND la.to_date >= %(today)s
        ORDER BY la.leave_type
        """,
        values={"employee": employee.name, "today": nowdate()},
        as_dict=True,
    )

    if not allocations:
        # Fallback: build from Leave Type list with zero balances
        leave_types = frappe.get_all(
            "Leave Type",
            filters={"is_lwp": 0},
            fields=["name as leave_type"],
            limit=5,
        )
        return [
            {"leave_type": lt.leave_type, "total": 0, "used": 0, "balance": 0}
            for lt in leave_types
        ]

    result = []
    for alloc in allocations:
        # Count approved leaves for this period
        used = frappe.db.sql(
            """
            SELECT IFNULL(SUM(total_leave_days), 0) as used
            FROM `tabLeave Application`
            WHERE employee = %(employee)s
                AND leave_type = %(leave_type)s
                AND status = 'Approved'
                AND docstatus = 1
                AND from_date >= (
                    SELECT from_date FROM `tabLeave Allocation`
                    WHERE employee = %(employee)s
                        AND leave_type = %(leave_type)s
                        AND docstatus = 1
                        AND from_date <= %(today)s
                        AND to_date >= %(today)s
                    LIMIT 1
                )
            """,
            values={
                "employee": employee.name,
                "leave_type": alloc.leave_type,
                "today": nowdate(),
            },
            as_dict=True,
        )[0].used or 0

        total = flt(alloc.total)
        result.append(
            {
                "leave_type": alloc.leave_type,
                "total": total,
                "used": flt(used),
                "balance": total - flt(used),
            }
        )

    return result


@frappe.whitelist()
def apply_leave(leave_type, from_date, to_date, reason=None):
    """Submit a leave request for the current faculty."""
    employee = get_current_faculty()
    if not employee:
        return {}


    doc = frappe.new_doc("Leave Application")
    doc.employee = employee.name
    doc.leave_type = leave_type
    doc.from_date = from_date
    doc.to_date = to_date
    doc.description = reason or ""
    doc.status = "Open"
    doc.insert()

    return {
        "name": doc.name,
        "status": doc.status,
        "message": _("Leave request submitted"),
    }


@frappe.whitelist(methods=["GET"])
def get_leave_history(start=0, page_length=10):
    """Get leave application history for current faculty."""
    employee = get_current_faculty()
    if not employee:
        return {}


    applications = frappe.get_all(
        "Leave Application",
        filters={"employee": employee.name},
        fields=[
            "name",
            "leave_type",
            "from_date",
            "to_date",
            "description",
            "status",
            "posting_date",
        ],
        order_by="posting_date desc",
        start=int(start),
        page_length=int(page_length),
    )

    total_count = frappe.db.count(
        "Leave Application", {"employee": employee.name}
    )

    return {"data": applications, "total_count": total_count}


@frappe.whitelist(methods=["GET"])
def get_student_leave_requests(start=0, page_length=20):
    """Get student leave requests for courses taught by current faculty."""
    employee = get_current_faculty()
    if not employee:
        return {}

    assignments = _get_faculty_teaching_assignments(employee.name)
    courses = [a.course for a in assignments]

    if not courses:
        return {"data": [], "total_count": 0}

    # Check for Student Leave Application doctype
    if frappe.db.exists("DocType", "Student Leave Application"):
        applications = frappe.db.sql(
            """
            SELECT
                sla.name,
                sla.student_name,
                sla.student as roll_no,
                sla.from_date,
                sla.to_date,
                sla.reason,
                sla.status
            FROM `tabStudent Leave Application` sla
            WHERE sla.status = 'Open'
            ORDER BY sla.creation DESC
            LIMIT %(page_length)s OFFSET %(start)s
            """,
            values={
                "start": int(start),
                "page_length": int(page_length),
            },
            as_dict=True,
        )
        total_count = frappe.db.count(
            "Student Leave Application", {"status": "Open"}
        )
        return {"data": applications, "total_count": total_count}

    # Fallback: no student leave doctype
    return {"data": [], "total_count": 0}


@frappe.whitelist()
def approve_student_leave(name):
    """Approve a student leave request."""
    if not get_current_faculty():

        frappe.throw(_("Faculty access required"), frappe.PermissionError)


    if frappe.db.exists("DocType", "Student Leave Application"):
        doc = frappe.get_doc("Student Leave Application", name)
        doc.status = "Approved"
        doc.save()
    else:
        frappe.throw(_("Student Leave Application doctype not found"))

    return {"status": "Approved", "message": _("Leave request approved")}


@frappe.whitelist()
def reject_student_leave(name, reason=None):
    """Reject a student leave request with reason."""
    if not get_current_faculty():

        frappe.throw(_("Faculty access required"), frappe.PermissionError)


    if frappe.db.exists("DocType", "Student Leave Application"):
        doc = frappe.get_doc("Student Leave Application", name)
        doc.status = "Rejected"
        if reason and hasattr(doc, "rejection_reason"):
            doc.rejection_reason = reason
        doc.add_comment("Comment", reason or "Rejected by faculty")
        doc.save()
    else:
        frappe.throw(_("Student Leave Application doctype not found"))

    return {"status": "Rejected", "message": _("Leave request rejected")}


@frappe.whitelist(methods=["GET"])
def get_lms_courses():
    """Get LMS courses for faculty. Gracefully degrades if LMS not installed."""
    employee = get_current_faculty()
    if not employee:
        return {}


    if not frappe.db.exists("DocType", "LMS Course"):
        return {"available": False, "courses": []}

    courses = frappe.get_all(
        "LMS Course",
        filters={"instructor": employee.name},
        fields=["name", "title"],
    )

    result = []
    for course in courses:
        lesson_count = frappe.db.count(
            "LMS Lesson", {"course": course.name}
        ) if frappe.db.exists("DocType", "LMS Lesson") else 0

        assignment_count = frappe.db.count(
            "LMS Assignment", {"course": course.name}
        ) if frappe.db.exists("DocType", "LMS Assignment") else 0

        quiz_count = frappe.db.count(
            "LMS Quiz", {"course": course.name}
        ) if frappe.db.exists("DocType", "LMS Quiz") else 0

        result.append(
            {
                "name": course.name,
                "title": course.title,
                "lesson_count": lesson_count,
                "assignment_count": assignment_count,
                "quiz_count": quiz_count,
            }
        )

    return {"available": True, "courses": result}


@frappe.whitelist(methods=["GET"])
def get_lms_course_content(course):
    """Get LMS course content (lessons, assignments, quizzes)."""
    if not get_current_faculty():

        return {}


    lessons = []
    if frappe.db.exists("DocType", "LMS Lesson"):
        lessons = frappe.get_all(
            "LMS Lesson",
            filters={"course": course},
            fields=["name", "title", "content", "idx"],
            order_by="idx",
        )

    assignments = []
    if frappe.db.exists("DocType", "LMS Assignment"):
        assignments = frappe.get_all(
            "LMS Assignment",
            filters={"course": course},
            fields=["name", "title", "due_date", "status"],
            order_by="due_date",
        )

    quizzes = []
    if frappe.db.exists("DocType", "LMS Quiz"):
        quizzes = frappe.get_all(
            "LMS Quiz",
            filters={"course": course},
            fields=["name", "title", "question_count", "status"],
        )

    return {"lessons": lessons, "assignments": assignments, "quizzes": quizzes}


@frappe.whitelist()
def save_lms_content(doctype, name=None, **data):
    """Create or update LMS content (lesson, assignment, quiz)."""
    if not get_current_faculty():

        frappe.throw(_("Faculty access required"), frappe.PermissionError)


    if name:
        doc = frappe.get_doc(doctype, name)
        doc.update(data)
        doc.save()
    else:
        doc = frappe.new_doc(doctype)
        doc.update(data)
        doc.insert()

    return {"name": doc.name, "message": _("Content saved")}


@frappe.whitelist()
def delete_lms_content(doctype, name):
    """Delete an LMS content item."""
    if not get_current_faculty():

        frappe.throw(_("Faculty access required"), frappe.PermissionError)


    frappe.delete_doc(doctype, name)
    return {"message": _("Content deleted")}


@frappe.whitelist(methods=["GET"])
def get_publications():
    """Get faculty publications grouped by type from Faculty Profile."""
    employee = get_current_faculty()
    if not employee:
        return {}


    # Faculty Publication is a child table on Faculty Profile
    profile = frappe.db.get_value(
        "Faculty Profile", {"employee": employee.name}, "name"
    )

    if not profile:
        return {"total": 0, "by_type": {}, "publications": []}

    publications = frappe.get_all(
        "Faculty Publication",
        filters={"parent": profile, "parenttype": "Faculty Profile"},
        fields=[
            "name",
            "title",
            "type",
            "journal_conference",
            "publication_date",
            "doi_isbn",
            "impact_factor",
            "scopus_indexed",
        ],
        order_by="publication_date desc",
    )

    # Group by type
    by_type = {}
    for pub in publications:
        pub_type = pub.type or "Other"
        by_type[pub_type] = by_type.get(pub_type, 0) + 1

    return {
        "total": len(publications),
        "by_type": by_type,
        "publications": publications,
    }


@frappe.whitelist(methods=["GET"])
def get_copo_matrix(course):
    """Get CO-PO attainment matrix using accreditation calculator."""
    if not get_current_faculty():

        return {}


    try:
        from university_erp.university_erp.accreditation.attainment_calculator import (
            COPOAttainmentCalculator,
        )

        calculator = COPOAttainmentCalculator(course)
        direct = calculator.calculate_direct_attainment()

        # Build matrix format
        cos = sorted(direct.keys()) if direct else []

        # Get PO list from CO-PO mapping
        pos = []
        if frappe.db.exists("DocType", "CO PO Mapping"):
            po_records = frappe.get_all(
                "Program Outcome",
                filters={"status": "Active"},
                fields=["po_code"],
                order_by="po_number",
            )
            pos = [po.po_code for po in po_records]

        if not pos:
            pos = [f"PO{i}" for i in range(1, 13)]

        # Build the matrix
        matrix = []
        for co in cos:
            row = []
            for po in pos:
                # Get mapping value if exists
                mapping_val = 0
                if frappe.db.exists("DocType", "CO PO Mapping"):
                    val = frappe.db.get_value(
                        "CO PO Mapping",
                        {"co_code": co, "po_code": po, "course": course},
                        "correlation_level",
                    )
                    if val:
                        attainment = direct.get(co, {}).get("attainment", 0)
                        mapping_val = round(flt(val) * attainment / 100, 1)
                row.append(mapping_val)
            matrix.append(row)

        return {"course": course, "cos": cos, "pos": pos, "matrix": matrix}

    except (ImportError, Exception):
        # Graceful degradation
        return {"course": course, "cos": [], "pos": [], "matrix": []}


@frappe.whitelist(methods=["GET"])
def get_copo_student_detail(course, co):
    """Get student-level attainment for a specific CO."""
    if not get_current_faculty():

        return {}


    try:
        from university_erp.university_erp.accreditation.attainment_calculator import (
            COPOAttainmentCalculator,
        )

        calculator = COPOAttainmentCalculator(course)
        # Get student-level data for the CO
        student_data = calculator._get_co_assessment_data_by_student(co)
        return {"co": co, "students": student_data}

    except (ImportError, AttributeError, Exception):
        # Graceful degradation
        return {"co": co, "students": []}


@frappe.whitelist(methods=["GET"])
def get_workload_summary():
    """Get workload summary with personal KPIs, department averages, and weekly heatmap."""
    employee = get_current_faculty()
    if not employee:
        return {}


    # Get personal workload from teaching assignments
    assignments = _get_faculty_teaching_assignments(employee.name)

    personal_hours = sum(flt(a.total_weekly_hours) for a in assignments)
    personal_courses = len(assignments)
    personal_credits = 0
    personal_students = 0

    for assignment in assignments:
        # Get course credits
        credits = frappe.db.get_value("Course", assignment.course, "total_credits") or 0
        personal_credits += flt(credits)

        # Get student count
        if assignment.student_group:
            count = frappe.db.count(
                "Student Group Student", {"parent": assignment.student_group}
            )
            personal_students += count

    # Department averages using faculty_workload_summary report
    dept_hours = personal_hours
    dept_courses = personal_courses
    dept_credits = personal_credits
    dept_students = personal_students

    if employee.department:
        try:
            from university_erp.faculty_management.report.faculty_workload_summary.faculty_workload_summary import (
                get_data,
            )
            dept_data = get_data({"department": employee.department})
            if dept_data:
                total_faculty = len(dept_data)
                if total_faculty > 0:
                    dept_hours = round(
                        sum(flt(d.get("total_hours", 0)) for d in dept_data)
                        / total_faculty,
                        1,
                    )
                    dept_courses = round(
                        sum(flt(d.get("total_assignments", 0)) for d in dept_data)
                        / total_faculty,
                        1,
                    )
        except (ImportError, Exception):
            pass

    # Build weekly heatmap from teaching schedules
    heatmap = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_abbrev = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu", "Friday": "Fri"}

    for assignment in assignments:
        schedules = frappe.get_all(
            "Teaching Assignment Schedule",
            filters={"parent": assignment.name, "day": ["in", days]},
            fields=["day", "start_time", "end_time", "room"],
        )
        for schedule in schedules:
            heatmap.append(
                {
                    "day": day_abbrev.get(schedule.day, schedule.day[:3]),
                    "timeslot": str(schedule.start_time)[:5],
                    "occupied": True,
                    "course_name": assignment.course_name,
                }
            )

    return {
        "personal": {
            "hours_per_week": round(personal_hours, 1),
            "total_courses": personal_courses,
            "total_credits": round(personal_credits, 1),
            "total_students": personal_students,
        },
        "department_avg": {
            "hours_per_week": round(dept_hours, 1),
            "total_courses": round(dept_courses, 1),
            "total_credits": round(dept_credits, 1),
            "total_students": round(dept_students, 1),
        },
        "heatmap": heatmap,
    }

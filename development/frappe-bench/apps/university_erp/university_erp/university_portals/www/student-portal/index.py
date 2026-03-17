# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt, cint, get_datetime


def get_context(context):
    """Main context function for Student Portal"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.dashboard = get_dashboard_data(student.name)
    context.today_classes = get_today_classes(student.name)
    context.announcements = get_announcements()
    context.quick_links = get_quick_links()

    return context


def get_current_student():
    """Get current logged in student"""
    user = frappe.session.user
    student = frappe.db.get_value("Student", {"user": user}, ["name", "student_name", "program", "student_batch_name", "image"], as_dict=1)
    return student


def get_dashboard_data(student):
    """Get student dashboard summary data"""
    return {
        "attendance_percentage": get_attendance_percentage(student),
        "current_cgpa": get_current_cgpa(student),
        "pending_fees": get_pending_fees(student),
        "upcoming_exams": get_upcoming_exams(student),
        "issued_books": get_issued_books_count(student),
        "pending_assignments": get_pending_assignments(student),
        "student_groups": get_student_groups(student)
    }


def get_attendance_percentage(student):
    """Calculate overall attendance percentage"""
    total_present = frappe.db.count("Student Attendance", {
        "student": student,
        "status": "Present"
    })
    total_classes = frappe.db.count("Student Attendance", {
        "student": student
    })

    if total_classes > 0:
        return round((total_present / total_classes) * 100, 1)
    return 0


def get_current_cgpa(student):
    """Get current CGPA from latest assessment"""
    cgpa = frappe.db.get_value(
        "Student Result",
        {"student": student, "docstatus": 1},
        "cgpa",
        order_by="academic_year desc, academic_term desc"
    )
    return flt(cgpa, 2) if cgpa else 0.0


def get_pending_fees(student):
    """Get total pending fees amount"""
    pending = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as pending
        FROM `tabFee Schedule`
        WHERE student = %s AND outstanding_amount > 0 AND docstatus = 1
    """, student, as_dict=1)

    return pending[0].pending if pending else 0


def get_upcoming_exams(student):
    """Get count of upcoming exams"""
    today = nowdate()

    # Get student's program
    program = frappe.db.get_value("Student", student, "program")
    if not program:
        return 0

    count = frappe.db.sql("""
        SELECT COUNT(DISTINCT es.name) as count
        FROM `tabExam Schedule` es
        JOIN `tabExam Schedule Course` esc ON esc.parent = es.name
        WHERE es.exam_date >= %s
        AND es.docstatus = 1
        AND esc.program = %s
    """, (today, program), as_dict=1)

    return count[0].count if count else 0


def get_issued_books_count(student):
    """Get count of currently issued library books"""
    count = frappe.db.count("Library Transaction", {
        "library_member": student,
        "type": "Issue",
        "docstatus": 1
    })

    returned = frappe.db.count("Library Transaction", {
        "library_member": student,
        "type": "Return",
        "docstatus": 1
    })

    return max(0, count - returned)


def get_pending_assignments(student):
    """Get count of pending assignments"""
    today = nowdate()

    # Get student groups for the student
    student_groups = frappe.db.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        pluck="parent"
    )

    if not student_groups:
        return 0

    count = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabLMS Assignment` a
        WHERE a.student_group IN %s
        AND a.due_date >= %s
        AND a.docstatus = 1
        AND NOT EXISTS (
            SELECT 1 FROM `tabLMS Assignment Submission` s
            WHERE s.assignment = a.name AND s.student = %s
        )
    """, (tuple(student_groups), today, student), as_dict=1)

    return count[0].count if count else 0


def get_student_groups(student):
    """Get student's enrolled groups/courses"""
    groups = frappe.db.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        fields=["parent as student_group"]
    )

    for group in groups:
        group_doc = frappe.db.get_value(
            "Student Group",
            group.student_group,
            ["group_based_on", "course", "program", "batch"],
            as_dict=1
        )
        group.update(group_doc or {})

    return groups


def get_today_classes(student):
    """Get today's class schedule"""
    today = getdate(nowdate())
    day_name = today.strftime("%A")

    # Get student groups
    student_groups = frappe.db.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        pluck="parent"
    )

    if not student_groups:
        return []

    classes = frappe.db.sql("""
        SELECT
            cs.course,
            cs.instructor,
            cs.instructor_name,
            cs.room,
            cs.from_time,
            cs.to_time,
            sg.name as student_group
        FROM `tabCourse Schedule` cs
        JOIN `tabStudent Group` sg ON sg.name = cs.student_group
        WHERE cs.student_group IN %s
        AND cs.schedule_date = %s
        ORDER BY cs.from_time
    """, (tuple(student_groups), today), as_dict=1)

    return classes


def get_announcements():
    """Get recent announcements for students"""
    announcements = frappe.db.get_all(
        "Announcement",
        filters={
            "for_students": 1,
            "publish_date": ["<=", nowdate()],
            "expiry_date": [">=", nowdate()]
        },
        fields=["title", "description", "publish_date", "priority"],
        order_by="priority desc, publish_date desc",
        limit=5
    )

    return announcements


def get_quick_links():
    """Get quick links for student portal"""
    return [
        {"label": _("View Timetable"), "url": "/student-portal/timetable", "icon": "calendar"},
        {"label": _("Check Results"), "url": "/student-portal/results", "icon": "file-text"},
        {"label": _("Pay Fees"), "url": "/student-portal/fees", "icon": "credit-card"},
        {"label": _("Attendance"), "url": "/student-portal/attendance", "icon": "check-circle"},
        {"label": _("Library"), "url": "/student-portal/library", "icon": "book"},
        {"label": _("Certificates"), "url": "/student-portal/certificates", "icon": "award"},
        {"label": _("Grievances"), "url": "/student-portal/grievances", "icon": "message-circle"},
        {"label": _("Profile"), "url": "/student-portal/profile", "icon": "user"}
    ]

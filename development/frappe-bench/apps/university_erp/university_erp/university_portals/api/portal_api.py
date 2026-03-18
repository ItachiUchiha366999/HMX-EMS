# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, flt


# ==================== Student Portal APIs ====================

@frappe.whitelist()
def get_student_dashboard():
    """Get student dashboard data"""
    from university_erp.www.student_portal.index import (
        get_current_student,
        get_dashboard_data,
        get_today_classes,
        get_announcements
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "student": student,
        "dashboard": get_dashboard_data(student.name),
        "today_classes": get_today_classes(student.name),
        "announcements": get_announcements()
    }


@frappe.whitelist()
def get_student_timetable(week_start=None):
    """Get student weekly timetable"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.timetable import get_weekly_timetable, get_week_days

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    if week_start:
        week_start = getdate(week_start)
    else:
        week_start = getdate(nowdate())

    return {
        "week_start": week_start,
        "days": get_week_days(week_start),
        "timetable": get_weekly_timetable(student.name, week_start)
    }


@frappe.whitelist()
def get_student_results():
    """Get student results"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.results import (
        get_student_results as get_results,
        get_semester_wise_results,
        get_cgpa_trend
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "results": get_results(student.name),
        "semester_results": get_semester_wise_results(student.name),
        "cgpa_trend": get_cgpa_trend(student.name)
    }


@frappe.whitelist()
def get_student_attendance_details(month=None):
    """Get student attendance details"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.attendance import (
        get_attendance_summary,
        get_monthly_attendance,
        get_course_wise_attendance
    )
    from frappe.utils import get_first_day

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    if month:
        selected_month = getdate(month + "-01")
    else:
        selected_month = get_first_day(nowdate())

    return {
        "summary": get_attendance_summary(student.name),
        "monthly": get_monthly_attendance(student.name, selected_month),
        "course_wise": get_course_wise_attendance(student.name)
    }


@frappe.whitelist()
def request_certificate(certificate_template, purpose, copies=1):
    """Request a certificate"""
    from university_erp.www.student_portal.certificates import request_certificate as req_cert
    return req_cert(certificate_template, purpose, copies)


@frappe.whitelist()
def submit_grievance(category, subject, description, priority="Medium"):
    """Submit a grievance"""
    from university_erp.www.student_portal.grievances import submit_grievance as submit_grv
    return submit_grv(category, subject, description, priority)


@frappe.whitelist()
def update_student_profile(**kwargs):
    """Update student profile"""
    from university_erp.www.student_portal.profile import update_student_profile as update_profile
    return update_profile(**kwargs)


@frappe.whitelist()
def create_payment_request(fee_schedule):
    """Create payment request for fee schedule"""
    frappe.has_permission("Fee Schedule", "read", throw=True)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    fee = frappe.get_doc("Fee Schedule", fee_schedule)
    if fee.student != student.name:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    if fee.outstanding_amount <= 0:
        frappe.throw(_("No outstanding amount"))

    # Create payment request
    payment_request = frappe.get_doc({
        "doctype": "Payment Request",
        "payment_request_type": "Inward",
        "party_type": "Student",
        "party": student.name,
        "grand_total": fee.outstanding_amount,
        "email_to": frappe.session.user,
        "subject": _("Fee Payment for {0}").format(fee.fee_structure),
        "message": _("Payment request for fee schedule {0}").format(fee_schedule),
        "reference_doctype": "Fee Schedule",
        "reference_name": fee_schedule
    })
    payment_request.insert(ignore_permissions=True)
    payment_request.submit()

    return {
        "success": True,
        "payment_request": payment_request.name,
        "payment_url": payment_request.get_payment_url()
    }


@frappe.whitelist()
def get_logged_student():
    """Get lightweight student info for the SPA layout"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "name": student.name,
        "student_name": student.student_name,
        "image": student.get("image"),
        "program": student.get("program"),
        "cgpa": student.get("custom_cgpa"),
    }


@frappe.whitelist()
def get_student_academics():
    """Get academics data: courses, credits, CGPA, semester results"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.academics import (
        get_current_courses,
        get_total_courses,
        get_total_credits,
        get_current_cgpa,
        get_semester_wise_results,
        get_cgpa_trend,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "current_courses": get_current_courses(student.name),
        "total_courses": get_total_courses(student.name),
        "total_credits": get_total_credits(student.name),
        "current_cgpa": get_current_cgpa(student.name),
        "semester_results": get_semester_wise_results(student.name),
        "cgpa_trend": get_cgpa_trend(student.name),
    }


@frappe.whitelist()
def get_student_fees():
    """Get fees data: pending fees, payment history, summary"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.fees import (
        get_pending_fees,
        get_payment_history,
        get_fee_summary,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "pending_fees": get_pending_fees(student.name),
        "payment_history": get_payment_history(student.name),
        "fee_summary": get_fee_summary(student.name),
    }


@frappe.whitelist()
def get_student_library():
    """Get library data: issued books, history, stats, overdue"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.library import (
        get_issued_books,
        get_borrowing_history,
        get_library_stats,
        get_overdue_books,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "issued_books": get_issued_books(student.name),
        "borrowing_history": get_borrowing_history(student.name),
        "library_stats": get_library_stats(student.name),
        "overdue_books": get_overdue_books(student.name),
    }


@frappe.whitelist()
def get_student_notifications():
    """Get notifications and announcements"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.notifications import (
        get_notifications,
        get_announcements,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    notifications = get_notifications(student.name)

    return {
        "notifications": notifications,
        "announcements": get_announcements(),
        "unread_count": len([n for n in notifications if not n.get("read")]),
    }


@frappe.whitelist()
def get_student_profile():
    """Get full profile data with guardians and academic info"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.profile import (
        get_guardians,
        get_academic_info,
        get_editable_fields,
    )

    student_link = get_current_student()
    if not student_link:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    student_doc = frappe.get_doc("Student", student_link.name)

    return {
        "student": student_doc.as_dict(),
        "guardians": get_guardians(student_link.name),
        "academic_info": get_academic_info(student_link.name),
        "editable_fields": get_editable_fields(),
    }


@frappe.whitelist()
def get_student_grievances():
    """Get grievances, categories, and stats"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.grievances import (
        get_student_grievances as get_grievances,
        get_grievance_categories,
        get_grievance_stats,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "grievances": get_grievances(student.name),
        "categories": get_grievance_categories(),
        "stats": get_grievance_stats(student.name),
    }


@frappe.whitelist()
def get_student_certificates():
    """Get certificate requests, available types, and issued certificates"""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.certificates import (
        get_certificate_requests,
        get_available_certificate_types,
        get_issued_certificates,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    return {
        "requests": get_certificate_requests(student.name),
        "available_types": get_available_certificate_types(),
        "issued": get_issued_certificates(student.name),
    }


@frappe.whitelist()
def get_student_hostel():
    """Get hostel allocation, room, building, attendance, and maintenance data"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    # Get active hostel allocation
    allocation = None
    room_info = None
    building_info = None
    if frappe.db.exists("DocType", "Hostel Allocation"):
        allocation = frappe.db.get_value(
            "Hostel Allocation",
            {"student": student.name, "docstatus": 1},
            ["name", "hostel_building", "hostel_room", "from_date", "to_date", "bed_number"],
            as_dict=1,
            order_by="from_date desc",
        )

    if allocation:
        if frappe.db.exists("DocType", "Hostel Room") and allocation.get("hostel_room"):
            room_info = frappe.db.get_value(
                "Hostel Room",
                allocation.hostel_room,
                ["name", "room_number", "room_type", "floor", "capacity"],
                as_dict=1,
            )

        if frappe.db.exists("DocType", "Hostel Building") and allocation.get("hostel_building"):
            building_info = frappe.db.get_value(
                "Hostel Building",
                allocation.hostel_building,
                ["name", "building_name", "warden", "warden_name", "contact_number"],
                as_dict=1,
            )

    # Get recent hostel attendance
    attendance = []
    if frappe.db.exists("DocType", "Hostel Attendance"):
        attendance = frappe.db.get_all(
            "Hostel Attendance",
            filters={"student": student.name},
            fields=["date", "status", "check_in_time", "check_out_time"],
            order_by="date desc",
            limit=30,
        )

    # Get maintenance requests
    maintenance_requests = []
    if frappe.db.exists("DocType", "Hostel Maintenance Request"):
        maintenance_requests = frappe.db.get_all(
            "Hostel Maintenance Request",
            filters={"student": student.name},
            fields=["name", "subject", "description", "status", "priority", "creation", "resolution_date"],
            order_by="creation desc",
            limit=20,
        )

    # Get mess menu if available
    mess_menu = []
    if frappe.db.exists("DocType", "Mess Menu"):
        today = nowdate()
        mess_menu = frappe.db.get_all(
            "Mess Menu",
            filters={"date": [">=", today]},
            fields=["name", "date", "meal_type", "menu_items"],
            order_by="date asc, meal_type asc",
            limit=21,
        )

    return {
        "allocation": allocation,
        "room": room_info,
        "building": building_info,
        "attendance": attendance,
        "maintenance_requests": maintenance_requests,
        "mess_menu": mess_menu,
    }


@frappe.whitelist()
def submit_maintenance_request(subject, description, priority="Medium"):
    """Submit a hostel maintenance request"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    if not frappe.db.exists("DocType", "Hostel Maintenance Request"):
        frappe.throw(_("Maintenance request system not configured"))

    # Get student's active allocation for the room
    allocation = frappe.db.get_value(
        "Hostel Allocation",
        {"student": student.name, "docstatus": 1},
        ["hostel_building", "hostel_room"],
        as_dict=1,
        order_by="from_date desc",
    )

    if not allocation:
        frappe.throw(_("No active hostel allocation found"))

    request = frappe.get_doc({
        "doctype": "Hostel Maintenance Request",
        "student": student.name,
        "hostel_building": allocation.hostel_building,
        "hostel_room": allocation.hostel_room,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "Open",
    })
    request.insert()

    return {
        "success": True,
        "request_id": request.name,
        "message": _("Maintenance request submitted successfully"),
    }


@frappe.whitelist()
def get_student_transport():
    """Get transport allocation, route, and schedule data"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    # Get active transport allocation
    allocation = None
    route_info = None
    vehicle_info = None
    stops = []

    if frappe.db.exists("DocType", "Transport Allocation"):
        allocation = frappe.db.get_value(
            "Transport Allocation",
            {"student": student.name, "docstatus": 1},
            ["name", "transport_route", "transport_vehicle", "from_date", "to_date", "pickup_stop", "drop_stop", "fare_amount"],
            as_dict=1,
            order_by="from_date desc",
        )

    if allocation:
        if frappe.db.exists("DocType", "Transport Route") and allocation.get("transport_route"):
            route_info = frappe.db.get_value(
                "Transport Route",
                allocation.transport_route,
                ["name", "route_name", "start_location", "end_location", "distance", "estimated_time"],
                as_dict=1,
            )

            # Get route stops
            if frappe.db.exists("DocType", "Transport Route Stop"):
                stops = frappe.db.get_all(
                    "Transport Route Stop",
                    filters={"parent": allocation.transport_route},
                    fields=["stop_name", "arrival_time", "departure_time", "idx"],
                    order_by="idx asc",
                )

        if frappe.db.exists("DocType", "Transport Vehicle") and allocation.get("transport_vehicle"):
            vehicle_info = frappe.db.get_value(
                "Transport Vehicle",
                allocation.transport_vehicle,
                ["name", "vehicle_name", "vehicle_number", "vehicle_type", "capacity", "driver_name", "driver_contact"],
                as_dict=1,
            )

    return {
        "allocation": allocation,
        "route": route_info,
        "stops": stops,
        "vehicle": vehicle_info,
    }


# ==================== Faculty Portal APIs ====================

@frappe.whitelist()
def get_faculty_dashboard():
    """Get faculty dashboard data"""
    from university_erp.university_portals.www.faculty_portal.index import (
        get_current_instructor,
        get_faculty_dashboard as get_dashboard,
        get_today_classes,
        get_pending_tasks,
        get_faculty_announcements
    )

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("Faculty not found"), frappe.PermissionError)

    return {
        "instructor": instructor,
        "dashboard": get_dashboard(instructor.name),
        "today_classes": get_today_classes(instructor.name),
        "pending_tasks": get_pending_tasks(instructor.name),
        "announcements": get_faculty_announcements()
    }


@frappe.whitelist()
def mark_attendance(class_schedule, attendance_data):
    """Mark attendance for a class"""
    from university_erp.university_portals.www.faculty_portal.attendance import mark_attendance as mark_att
    return mark_att(class_schedule, attendance_data)


@frappe.whitelist()
def submit_assessment_results(assessment_plan, results_data):
    """Submit assessment results"""
    from university_erp.university_portals.www.faculty_portal.grades import submit_assessment_results as submit_results
    return submit_results(assessment_plan, results_data)


@frappe.whitelist()
def approve_leave_request(leave_application, status, remarks=None):
    """Approve or reject a student leave request"""
    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    leave = frappe.get_doc("Student Leave Application", leave_application)
    leave.status = status
    if remarks:
        leave.remarks = remarks
    leave.save(ignore_permissions=True)

    return {
        "success": True,
        "message": _("Leave request {0}").format(status.lower())
    }


# ==================== Parent Portal APIs ====================

@frappe.whitelist()
def get_parent_dashboard():
    """Get parent dashboard data"""
    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("Guardian not found"), frappe.PermissionError)

    children = get_linked_children(guardian.name)

    return {
        "guardian": guardian,
        "children": children
    }


def get_current_guardian():
    """Get current logged in guardian"""
    user = frappe.session.user
    guardian = frappe.db.get_value(
        "Guardian",
        {"user": user},
        ["name", "guardian_name", "email_address", "mobile_number", "image"],
        as_dict=1
    )
    return guardian


def get_linked_children(guardian):
    """Get children linked to guardian"""
    children = frappe.db.sql("""
        SELECT
            sg.student,
            s.student_name,
            s.program,
            s.student_batch_name,
            s.image,
            sg.relation
        FROM `tabStudent Guardian` sg
        JOIN `tabStudent` s ON s.name = sg.guardian
        WHERE sg.guardian = %s
    """, guardian, as_dict=1)

    # Add summary data for each child
    for child in children:
        child["attendance"] = get_child_attendance_summary(child.student)
        child["fees"] = get_child_fee_summary(child.student)

    return children


def get_child_attendance_summary(student):
    """Get attendance summary for a child"""
    from university_erp.www.student_portal.attendance import get_attendance_summary
    return get_attendance_summary(student)


def get_child_fee_summary(student):
    """Get fee summary for a child"""
    from university_erp.www.student_portal.fees import get_fee_summary
    return get_fee_summary(student)


@frappe.whitelist()
def get_child_details(student):
    """Get detailed information about a child"""
    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    # Verify parent-child relationship
    is_linked = frappe.db.exists("Student Guardian", {
        "parent": student,
        "guardian": guardian.name
    })

    if not is_linked:
        frappe.throw(_("You are not authorized to view this student's information"), frappe.PermissionError)

    student_doc = frappe.get_doc("Student", student)

    return {
        "student": student_doc.as_dict(),
        "attendance": get_child_attendance_summary(student),
        "fees": get_child_fee_summary(student)
    }


@frappe.whitelist()
def send_message_to_faculty(instructor, subject, message):
    """Send a message to faculty"""
    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    # Create communication
    comm = frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "sender": frappe.session.user,
        "recipients": frappe.db.get_value("Instructor", instructor, "user"),
        "subject": subject,
        "content": message,
        "reference_doctype": "Instructor",
        "reference_name": instructor
    })
    comm.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": _("Message sent successfully")
    }


# ==================== Utility Functions ====================

def get_user_portal_type():
    """Determine which portal type the current user has access to"""
    user = frappe.session.user

    # Check if student
    if frappe.db.exists("Student", {"user": user}):
        return "student"

    # Check if instructor/faculty
    if frappe.db.exists("Instructor", {"user": user}):
        return "faculty"

    # Check if guardian/parent
    if frappe.db.exists("Guardian", {"user": user}):
        return "parent"

    # Check if alumni
    if frappe.db.exists("Alumni", {"user": user}):
        return "alumni"

    return None


@frappe.whitelist(allow_guest=True)
def get_portal_redirect():
    """Get the appropriate portal URL for the current user"""
    if frappe.session.user == "Guest":
        return {"url": "/login"}

    portal_type = get_user_portal_type()

    portal_urls = {
        "student": "/student-portal",
        "faculty": "/faculty-portal",
        "parent": "/parent-portal",
        "alumni": "/alumni-portal"
    }

    if portal_type:
        return {"url": portal_urls.get(portal_type, "/me")}

    return {"url": "/me"}


# ==================== Unified Portal APIs ====================

@frappe.whitelist()
def get_session_info():
    """
    Get current session info for the unified portal app shell.

    Called once at boot by the Pinia session store (portal-vue/src/stores/session.js).
    Returns user identity, roles, and allowed modules in a single response.

    Returns:
        dict: {logged_user, full_name, user_image, roles[], allowed_modules[]}
    """
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(frappe._("Not logged in"), frappe.AuthenticationError)

    user_doc = frappe.db.get_value(
        "User",
        user,
        ["full_name", "user_image"],
        as_dict=True,
    ) or {}

    roles = frappe.get_roles(user)

    # Determine allowed portal modules based on roles held
    # This list grows as Phase 3-6 add new portal modules
    module_role_map = {
        "management": ["University Admin", "University VC", "University Dean", "University Registrar"],
        "faculty": ["University Faculty", "University HOD"],
        "hod": ["University HOD"],
        "student": ["University Student"],
        "finance": ["University Finance", "University Admin"],
    }
    allowed_modules = [
        module for module, required_roles in module_role_map.items()
        if any(r in roles for r in required_roles)
    ]

    return {
        "logged_user": user,
        "full_name": user_doc.get("full_name", ""),
        "user_image": user_doc.get("user_image", ""),
        "roles": roles,
        "allowed_modules": allowed_modules,
    }

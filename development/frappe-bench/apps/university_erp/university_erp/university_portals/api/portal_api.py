# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, flt


# ==================== Student Portal APIs ====================

@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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

    results = get_results(student.name)

    # Vue's Download Hall Ticket button fires only when results[0].assessment_plan is truthy.
    # Inject the student's Hall Ticket name into every result row so the button works.
    hall_ticket_name = None
    if frappe.db.exists("DocType", "Hall Ticket"):
        hall_ticket_name = frappe.db.get_value(
            "Hall Ticket", {"student": student.name}, "name", order_by="creation desc"
        )
    if hall_ticket_name and results:
        for row in results:
            if not row.get("assessment_plan"):
                row["assessment_plan"] = hall_ticket_name

    return {
        "results": results,
        "semester_results": get_semester_wise_results(student.name),
        "cgpa_trend": get_cgpa_trend(student.name)
    }


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
def get_student_fees():
    """Get fees data: pending fees, payment history, summary, scholarships."""
    from university_erp.www.student_portal.index import get_current_student
    from university_erp.www.student_portal.fees import (
        get_pending_fees,
        get_payment_history,
        get_fee_summary,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    summary = get_fee_summary(student.name)
    scholarships = _get_student_scholarships(student.name)

    # Inject pending-credit total into the summary so the Vue layer can show it
    pending_credit = sum(
        flt(s["discount_amount"]) for s in scholarships
        if s["display_status"] == "Pending Disbursement"
    )
    disbursed_credit = sum(
        flt(s["discount_amount"]) for s in scholarships
        if s["display_status"] == "Disbursed"
    )
    summary["pending_scholarship_credit"] = pending_credit
    summary["disbursed_scholarship_credit"] = disbursed_credit

    return {
        "pending_fees": get_pending_fees(student.name),
        "payment_history": get_payment_history(student.name),
        "fee_summary": summary,
        "scholarships": scholarships,
    }


def _get_student_scholarships(student):
    """Return scholarships for the portal Fees view, with a normalised
    `display_status` derived from `workflow_state`."""
    rows = frappe.db.sql("""
        SELECT name, scholarship_type, discount_amount, discount_percentage,
               valid_from, valid_till, workflow_state, status,
               total_benefit_given, fee_category,
               CASE
                 WHEN workflow_state='Approved'  THEN 'Pending Disbursement'
                 WHEN workflow_state='Disbursed' THEN 'Disbursed'
                 WHEN workflow_state='Rejected'  THEN 'Rejected'
                 WHEN workflow_state='Cancelled' THEN 'Cancelled'
                 WHEN workflow_state='Under Verification' THEN 'Under Verification'
                 ELSE 'Draft'
               END AS display_status
        FROM `tabStudent Scholarship`
        WHERE student = %s AND docstatus IN (0, 1)
        ORDER BY valid_from DESC
    """, student, as_dict=True)
    for r in rows:
        # Provide ISO-formatted date strings for the Vue layer (avoid
        # JS Date timezone drift)
        for field in ("valid_from", "valid_till"):
            v = r.get(field)
            r[field] = v.strftime("%Y-%m-%d") if v else None
    return rows


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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
            ["name", "hostel_building", "room", "from_date", "to_date", "bed_number", "status"],
            as_dict=1,
            order_by="from_date desc",
        )

    if allocation:
        if frappe.db.exists("DocType", "Hostel Room") and allocation.get("room"):
            room_info = frappe.db.get_value(
                "Hostel Room",
                allocation.room,
                ["name", "room_number", "room_type", "floor", "capacity"],
                as_dict=1,
            )

        if frappe.db.exists("DocType", "Hostel Building") and allocation.get("hostel_building"):
            building_info = frappe.db.get_value(
                "Hostel Building",
                allocation.hostel_building,
                ["name", "building_name", "warden", "contact_number"],
                as_dict=1,
            )

    # Get recent hostel attendance
    attendance = []
    if frappe.db.exists("DocType", "Hostel Attendance"):
        attendance = frappe.db.get_all(
            "Hostel Attendance",
            filters={"student": student.name},
            fields=["attendance_date as date", "status", "in_time as check_in_time", "out_time as check_out_time"],
            order_by="attendance_date desc",
            limit=30,
        )

    # Get maintenance requests
    maintenance_requests = []
    if frappe.db.exists("DocType", "Hostel Maintenance Request"):
        maintenance_requests = frappe.db.get_all(
            "Hostel Maintenance Request",
            filters={"requested_by": student.name},
            fields=["name", "subject", "description", "status", "priority", "creation", "actual_completion as resolution_date"],
            order_by="creation desc",
            limit=20,
        )

    # Get mess menu if available
    mess_menu = []
    if frappe.db.exists("DocType", "Mess Menu"):
        from frappe.utils import add_days
        today = nowdate()
        week_end = add_days(today, 7)
        menus = frappe.db.get_all(
            "Mess Menu",
            filters={"week_start_date": ["<=", week_end]},
            fields=["name", "mess", "mess_name", "week_start_date", "status"],
            order_by="week_start_date asc",
            limit=10,
        )
        for menu in menus:
            menu["items"] = frappe.db.get_all(
                "Mess Menu Item",
                filters={"parent": menu.name},
                fields=["day", "meal_type", "menu_items as items", "special_item"],
                order_by="idx asc",
            ) if frappe.db.exists("DocType", "Mess Menu Item") else []
        mess_menu = menus

    return {
        "allocation": allocation,
        "room": room_info,
        "building": building_info,
        "attendance": attendance,
        "maintenance_requests": maintenance_requests,
        "mess_menu": mess_menu,
    }


@frappe.whitelist()
def submit_maintenance_request(subject, description, priority="Medium", request_type="Other"):
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
        ["hostel_building", "room"],
        as_dict=1,
        order_by="from_date desc",
    )

    if not allocation:
        frappe.throw(_("No active hostel allocation found"))

    # Always derive building from the room itself (allocation.hostel_building can be
    # stale or seeded incorrectly). This avoids the "Room X does not belong to building Y"
    # validation failure inside Hostel Maintenance Request.
    room_building = frappe.db.get_value("Hostel Room", allocation.room, "hostel_building") \
        if allocation.room else allocation.hostel_building

    request = frappe.get_doc({
        "doctype": "Hostel Maintenance Request",
        "requested_by": student.name,
        "request_date": frappe.utils.nowdate(),
        "building": room_building,
        "room": allocation.room,
        "request_type": request_type,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "Open",
    })
    request.flags.ignore_permissions = True
    request.insert(ignore_permissions=True)

    return {
        "success": True,
        "request_id": request.name,
        "message": _("Maintenance request submitted successfully"),
    }


@frappe.whitelist(methods=["GET"])
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
            ["name", "route", "vehicle", "from_date", "to_date", "pickup_stop", "drop_stop", "monthly_fare"],
            as_dict=1,
            order_by="from_date desc",
        )

    if allocation:
        if frappe.db.exists("DocType", "Transport Route") and allocation.get("route"):
            route_info = frappe.db.get_value(
                "Transport Route",
                allocation.route,
                ["name", "route_name", "start_point", "end_point", "total_distance", "total_duration", "departure_time", "arrival_time"],
                as_dict=1,
            )

            # Get route stops with coordinates
            if frappe.db.exists("DocType", "Transport Route Stop"):
                stops = frappe.db.get_all(
                    "Transport Route Stop",
                    filters={"parent": allocation.route},
                    fields=["stop_name", "stop_sequence", "pickup_time", "drop_time",
                            "latitude", "longitude", "idx"],
                    order_by="idx asc",
                )
                # Cast coordinates so the portal map can use them directly
                for s in stops:
                    s["latitude"] = float(s["latitude"]) if s.get("latitude") else None
                    s["longitude"] = float(s["longitude"]) if s.get("longitude") else None

        if frappe.db.exists("DocType", "Transport Vehicle") and allocation.get("vehicle"):
            vehicle_info = frappe.db.get_value(
                "Transport Vehicle",
                allocation.vehicle,
                ["name", "vehicle_name", "vehicle_number", "vehicle_type", "seating_capacity as capacity", "driver_name", "driver_contact"],
                as_dict=1,
            )

    return {
        "allocation": allocation,
        "route": route_info,
        "stops": stops,
        "vehicle": vehicle_info,
    }


# ==================== Faculty Portal APIs ====================

@frappe.whitelist(methods=["GET"])
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

@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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

@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
def get_placement_opportunities():
    """Get open placement job postings the student hasn't already applied to.

    Filters out Placement Job Openings the current student has any non-Withdrawn
    Placement Application against — so the Job Postings tab only shows
    actionable opportunities. Withdrawn applications still allow re-application.
    """
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    try:
        # Job openings the student has already applied to (excl. Withdrawn)
        applied_to = {
            r[0] for r in frappe.db.sql(
                "SELECT job_opening FROM `tabPlacement Application` "
                "WHERE student=%s AND job_opening IS NOT NULL "
                "AND status != 'Withdrawn'",
                student.name,
            ) if r[0]
        }

        job_postings = frappe.db.get_all(
            "Placement Job Opening",
            filters={"status": "Open"},
            fields=[
                "name", "job_title as title", "company", "job_type as type",
                "deadline", "job_location as location", "min_cgpa",
                "max_backlogs", "job_description as description",
                "skills_required as tags", "posting_date", "status",
            ],
            order_by="posting_date desc",
            limit=50,
        )
        # Drop already-applied jobs
        job_postings = [jp for jp in job_postings if jp["name"] not in applied_to]

        for jp in job_postings:
            jp["tags"] = [t.strip() for t in (jp.get("tags") or "").split(",") if t.strip()]
        return {"job_postings": job_postings}
    except Exception as e:
        frappe.log_error(f"get_placement_opportunities: {e}")
        return {"job_postings": []}


@frappe.whitelist(methods=["GET"])
def get_placement_applications():
    """Get placement applications for the current student"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    try:
        apps = frappe.db.sql("""
            SELECT
                pa.name, pa.company, pa.status,
                pa.application_date as date_applied,
                pa.placement_drive, pa.interview_date,
                pa.interview_time, pa.interview_venue,
                pa.offered_ctc, pa.package_offered,
                COALESCE(pa.job_title, pd.job_title, '') as role
            FROM `tabPlacement Application` pa
            LEFT JOIN `tabPlacement Drive` pd ON pd.name = pa.placement_drive
            WHERE pa.student = %s
            ORDER BY pa.application_date desc
            LIMIT 50
        """, student.name, as_dict=1)
        return {"applications": apps}
    except Exception as e:
        frappe.log_error(f"get_placement_applications: {e}")
        return {"applications": []}


@frappe.whitelist(methods=["GET"])
def get_placement_stats():
    """Get placement statistics for the current student"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    try:
        apps = frappe.db.get_all(
            "Placement Application",
            filters={"student": student.name},
            fields=["status"],
        )
        applied = len(apps)
        shortlisted = sum(1 for a in apps if a.get("status") in ("Shortlisted", "Placed", "Offer Accepted"))
        interviews = sum(1 for a in apps if a.get("status") in ("Interview Scheduled", "In Review"))
        new_roles = frappe.db.count("Placement Job Opening", {"status": "Open"})
        return {
            "applied": applied,
            "shortlisted": shortlisted,
            "interviews": interviews,
            "new_roles": new_roles,
        }
    except Exception as e:
        frappe.log_error(f"get_placement_stats: {e}")
        return {"applied": 0, "shortlisted": 0, "interviews": 0, "new_roles": 0}


@frappe.whitelist(methods=["GET"])
def get_placement_interviews():
    """Get upcoming interviews for the current student"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    try:
        interviews = frappe.db.get_all(
            "Placement Application",
            filters={"student": student.name, "interview_date": ["is", "set"]},
            fields=[
                "name", "company", "job_title as role", "status as type",
                "interview_date as date", "interview_time as time",
                "interview_venue as venue", "placement_drive",
            ],
            order_by="interview_date asc",
            limit=20,
        )
        for iv in interviews:
            iv["title"] = f"Interview - {iv.get('role', '')}"
        return {"interviews": interviews}
    except Exception as e:
        frappe.log_error(f"get_placement_interviews: {e}")
        return {"interviews": []}


@frappe.whitelist(methods=["POST"])
def apply_for_job(job_opening=None):
    """Submit a Placement Application for the current student against a Placement Job Opening.

    Idempotent — if the student already has an Applied/Shortlisted application for
    this job, returns that one instead of creating a duplicate.
    """
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)
    if not job_opening:
        frappe.throw(_("job_opening is required"))
    if not frappe.db.exists("Placement Job Opening", job_opening):
        frappe.throw(_("Job Opening {0} does not exist").format(job_opening))

    job = frappe.db.get_value(
        "Placement Job Opening", job_opening,
        ["name", "job_title", "company", "min_cgpa", "max_backlogs", "status"],
        as_dict=True,
    )
    if job.status and str(job.status).lower() != "open":
        frappe.throw(_("This job is no longer accepting applications (status: {0})").format(job.status))

    existing = frappe.db.sql("""
        SELECT name, status FROM `tabPlacement Application`
        WHERE student=%s AND job_opening=%s
        LIMIT 1
    """, (student.name, job_opening), as_dict=True)
    if existing:
        return {
            "name": existing[0].name,
            "status": existing[0].status,
            "duplicate": True,
        }

    app = frappe.get_doc({
        "doctype": "Placement Application",
        "student": student.name,
        "student_name": frappe.db.get_value("Student", student.name, "student_name"),
        "job_opening": job_opening,
        "job_title": job.job_title,
        "company": job.company,
        "application_date": frappe.utils.nowdate(),
        "status": "Applied",
    })
    app.flags.ignore_permissions = True
    app.flags.ignore_mandatory = True  # placement_drive is doctype-mandatory but irrelevant for direct-job applications
    app.insert(ignore_permissions=True)

    # The active Placement Application meta doesn't include job_opening so the ORM
    # may drop it on insert. Set it directly so portal queries can see the link.
    if not frappe.db.get_value("Placement Application", app.name, "job_opening"):
        frappe.db.set_value("Placement Application", app.name, "job_opening", job_opening, update_modified=False)

    return {
        "name": app.name,
        "status": app.status,
        "company": app.company,
        "job_title": app.job_title,
        "duplicate": False,
    }


@frappe.whitelist(methods=["POST"])
def respond_to_offer(application, decision):
    """Student accepts or declines a placement offer.

    `decision` is "accept" or "decline". Only valid when the application is
    in 'Offer Received' state. Sets workflow_state directly because the
    workflow restricts these transitions to Placement Officer (which would
    block the student).
    """
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    if not frappe.db.exists("Placement Application", application):
        frappe.throw(_("Application {0} not found").format(application))

    pa_row = frappe.db.sql("""
        SELECT name, student, workflow_state, company, job_title,
               COALESCE(package_offered, offered_ctc, 0) as ctc
        FROM `tabPlacement Application` WHERE name=%s
    """, application, as_dict=True)
    pa = pa_row[0] if pa_row else None
    if not pa:
        frappe.throw(_("Application {0} not found").format(application))
    if pa.student != student.name:
        frappe.throw(_("This is not your application"), frappe.PermissionError)
    if pa.workflow_state != "Offer Received":
        frappe.throw(_("Cannot {0} — application is in '{1}' state, not 'Offer Received'").format(
            decision, pa.workflow_state))

    decision = (decision or "").lower().strip()
    if decision == "accept":
        new_state = "Accepted"
        new_status = "Accepted"
    elif decision == "decline":
        new_state = "Withdrawn"
        new_status = "Withdrawn"
    else:
        frappe.throw(_("decision must be 'accept' or 'decline'"))

    frappe.db.set_value("Placement Application", application, {
        "workflow_state": new_state,
        "status": new_status,
    }, update_modified=False)

    return {
        "name": application,
        "workflow_state": new_state,
        "status": new_status,
        "company": pa.company,
        "job_title": pa.job_title,
        "offered_ctc": pa.ctc,
    }


@frappe.whitelist(methods=["GET"])
def get_student_exam_schedule():
    """Return upcoming + completed exams for the current student.

    Joins Exam Schedule against the student's Course Enrollments so only their
    own exams are returned. Replaces the hardcoded mock data in the Vue
    Examinations tab.
    """
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    today = frappe.utils.nowdate()

    enrolled_courses = [
        r.course for r in frappe.db.get_all(
            "Course Enrollment",
            filters={"student": student.name},
            fields=["course"],
        )
    ]
    if not enrolled_courses:
        return {"upcoming": [], "completed": [], "today": today}

    rows = frappe.db.sql("""
        SELECT
            es.name, es.course, c.course_name,
            es.exam_type, es.academic_term,
            es.exam_date, es.start_time, es.end_time, es.venue
        FROM `tabExam Schedule` es
        LEFT JOIN `tabCourse` c ON c.name = es.course
        WHERE es.docstatus = 1
          AND es.course IN %(courses)s
        ORDER BY es.exam_date, es.start_time
    """, {"courses": tuple(enrolled_courses)}, as_dict=True)

    today_d = frappe.utils.getdate(today)
    upcoming, completed = [], []
    for r in rows:
        r["course_name"] = r.get("course_name") or r.get("course")
        # Convert time fields (timedelta or time) to "HH:MM" strings
        for tf in ("start_time", "end_time"):
            v = r.get(tf)
            if v is not None:
                try:
                    if hasattr(v, "total_seconds"):
                        secs = int(v.total_seconds())
                        r[tf] = f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}"
                    else:
                        r[tf] = str(v)[:5]
                except Exception:
                    r[tf] = str(v)
        if r.exam_date and frappe.utils.getdate(r.exam_date) >= today_d:
            r["days_remaining"] = frappe.utils.date_diff(r.exam_date, today)
            upcoming.append(r)
        else:
            completed.append(r)

    return {"upcoming": upcoming, "completed": completed, "today": today}


@frappe.whitelist(methods=["GET"])
def get_student_hall_tickets_v2():
    """Return hall tickets for the current student grouped by exam_type.

    Each ticket includes its exam rows so the portal can render a single card
    per ticket without further API calls.
    """
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student not found"), frappe.PermissionError)

    tickets = frappe.db.get_all(
        "Hall Ticket",
        filters={"student": student.name},
        fields=[
            "name", "academic_term", "exam_type", "issue_date",
            "verification_code", "is_eligible", "ineligibility_reason",
            "workflow_state", "docstatus",
        ],
        order_by="issue_date desc",
    )
    for t in tickets:
        t["exams"] = frappe.db.get_all(
            "Hall Ticket Exam",
            filters={"parent": t["name"]},
            fields=["course", "course_name", "exam_date", "exam_time", "venue"],
            order_by="exam_date asc",
        )
        # Format exam_time
        for e in t["exams"]:
            v = e.get("exam_time")
            if v is not None and hasattr(v, "total_seconds"):
                secs = int(v.total_seconds())
                e["exam_time"] = f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}"
            elif v is not None:
                e["exam_time"] = str(v)[:5]
        t["available"] = (t.get("workflow_state") == "Issued") and bool(t.get("is_eligible"))
    return {"hall_tickets": tickets}


@frappe.whitelist(methods=["GET"])
def download_fee_receipt(fee_name=None):
    """Return fee receipt HTML for a Fees doc"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    if not fee_name:
        frappe.throw(_("fee_name is required"))

    try:
        # Verify the fee belongs to this student
        owner_student = frappe.db.get_value("Fees", fee_name, "student")
        if owner_student != student.name:
            frappe.throw(_("Not authorized"), frappe.PermissionError)

        doc = frappe.get_doc("Fees", fee_name)
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Fee Receipt - {fee_name}</title>
<style>body{{font-family:Arial,sans-serif;padding:40px;max-width:700px;margin:0 auto}}
h1{{color:#1e3a5f;border-bottom:2px solid #1e3a5f;padding-bottom:10px}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#1e3a5f;color:#fff}}.total{{font-weight:bold;font-size:1.1em}}
</style></head><body>
<h1>Fee Receipt</h1>
<p><strong>Receipt No:</strong> {fee_name}</p>
<p><strong>Student:</strong> {doc.student_name or doc.student}</p>
<p><strong>Program:</strong> {getattr(doc, 'program', '') or ''}</p>
<p><strong>Academic Year:</strong> {getattr(doc, 'academic_year', '') or ''}</p>
<p><strong>Due Date:</strong> {getattr(doc, 'due_date', '') or ''}</p>
<p><strong>Grand Total:</strong> ₹{getattr(doc, 'grand_total', 0) or 0:,.2f}</p>
<p><strong>Outstanding Amount:</strong> ₹{getattr(doc, 'outstanding_amount', 0) or 0:,.2f}</p>
<table><tr><th>Component</th><th>Amount</th></tr>"""

        for comp in (doc.components or []):
            html += f"<tr><td>{getattr(comp, 'fees_category', '')}</td><td>₹{getattr(comp, 'amount', 0):,.2f}</td></tr>"

        html += f"""</table>
<p class="total">Total: ₹{getattr(doc, 'grand_total', 0) or 0:,.2f}</p>
</body></html>"""

        from frappe.utils.pdf import get_pdf
        pdf_bytes = get_pdf(html)
        frappe.local.response.update({
            "type": "pdf",
            "filename": f"Fee_Receipt_{fee_name}.pdf",
            "filecontent": pdf_bytes,
        })
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"download_fee_receipt: {e}")
        frappe.throw(_("Could not generate fee receipt"))


@frappe.whitelist(methods=["GET"])
def download_payment_receipt(payment_name=None):
    """Return payment receipt HTML for a Payment Entry"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    if not payment_name:
        frappe.throw(_("payment_name is required"))

    try:
        doc = frappe.get_doc("Payment Entry", payment_name)

        # Verify the payment belongs to this student
        # PE party can be student name (EDU-STU-...) or student_name string
        if doc.party != student.name and doc.party != student.student_name:
            # Also allow if a referenced Fees doc belongs to this student
            ref_fees = [r.reference_name for r in (doc.references or []) if r.reference_doctype == "Fees"]
            has_access = any(
                frappe.db.get_value("Fees", fn, "student") == student.name
                for fn in ref_fees
            ) if ref_fees else False
            if not has_access:
                frappe.throw(_("Not authorized"), frappe.PermissionError)

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Payment Receipt - {payment_name}</title>
<style>body{{font-family:Arial,sans-serif;padding:40px;max-width:700px;margin:0 auto}}
h1{{color:#1e3a5f;border-bottom:2px solid #1e3a5f;padding-bottom:10px}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#1e3a5f;color:#fff}}.total{{font-weight:bold;font-size:1.1em}}
</style></head><body>
<h1>Payment Receipt</h1>
<p><strong>Receipt No:</strong> {payment_name}</p>
<p><strong>Date:</strong> {doc.posting_date}</p>
<p><strong>Party:</strong> {doc.party_name or doc.party}</p>
<p><strong>Mode of Payment:</strong> {getattr(doc, 'mode_of_payment', '') or 'N/A'}</p>
<p><strong>Amount Paid:</strong> ₹{getattr(doc, 'paid_amount', 0) or 0:,.2f}</p>
<p><strong>Reference No:</strong> {getattr(doc, 'reference_no', '') or 'N/A'}</p>
<table><tr><th>Against Invoice</th><th>Amount</th></tr>"""

        for ref in (doc.references or []):
            html += f"<tr><td>{ref.reference_name}</td><td>₹{getattr(ref, 'allocated_amount', 0):,.2f}</td></tr>"

        html += f"""</table>
<p class="total">Total Paid: ₹{getattr(doc, 'paid_amount', 0) or 0:,.2f}</p>
<p><em>This is a computer-generated receipt.</em></p>
</body></html>"""

        from frappe.utils.pdf import get_pdf
        pdf_bytes = get_pdf(html)
        frappe.local.response.update({
            "type": "pdf",
            "filename": f"Payment_Receipt_{payment_name}.pdf",
            "filecontent": pdf_bytes,
        })
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"download_payment_receipt: {e}")
        frappe.throw(_("Could not generate payment receipt"))


@frappe.whitelist(methods=["GET"])
def download_hall_ticket(plan_name=None):
    """Return hall ticket HTML for an Examination Plan / Hall Ticket doc"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    if not plan_name:
        frappe.throw(_("plan_name is required"))

    try:
        import datetime as _dt

        def _fmt_time(t):
            if isinstance(t, _dt.timedelta):
                total = int(t.total_seconds())
                h, rem = divmod(total, 3600)
                m = rem // 60
                suffix = "AM" if h < 12 else "PM"
                h12 = h % 12 or 12
                return f"{h12}:{m:02d} {suffix}"
            return str(t or "")

        # plan_name is an Assessment Plan name (passed by Vue) or a Hall Ticket name.
        # Find the student's Hall Ticket — match by name first, then fall back to student's latest.
        ht_doc = None
        if frappe.db.exists("DocType", "Hall Ticket"):
            ht_name = frappe.db.get_value("Hall Ticket", {"student": student.name, "name": plan_name}, "name")
            if not ht_name:
                # plan_name is an Assessment Plan — just get the student's most recent ticket
                ht_name = frappe.db.get_value(
                    "Hall Ticket", {"student": student.name, "docstatus": 1}, "name",
                    order_by="creation desc"
                ) or frappe.db.get_value(
                    "Hall Ticket", {"student": student.name}, "name",
                    order_by="creation desc"
                )
            if ht_name:
                ht_doc = frappe.get_doc("Hall Ticket", ht_name)

        student_doc = frappe.get_doc("Student", student.name)
        program = frappe.db.get_value("Program Enrollment", {"student": student.name}, "program") or ""
        ticket_no = ht_doc.name if ht_doc else plan_name

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Hall Ticket - {student.student_name}</title>
<style>body{{font-family:Arial,sans-serif;padding:40px;max-width:700px;margin:0 auto}}
h1{{color:#1e3a5f;text-align:center;border-bottom:2px solid #1e3a5f;padding-bottom:10px}}
.header{{text-align:center;margin-bottom:20px}}
.info-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:20px 0}}
.info-item{{background:#f5f5f5;padding:10px;border-radius:4px}}
.label{{font-weight:bold;color:#666;font-size:0.85em;display:block;margin-bottom:4px}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#1e3a5f;color:#fff}}.footer{{margin-top:40px;color:#666}}
.badge{{display:inline-block;padding:4px 10px;border-radius:12px;font-size:0.85em;background:#d1fae5;color:#065f46}}
</style></head><body>
<div class="header"><h1>Hall Ticket / Admit Card</h1>
<p>National Institute of Technology | Academic Year 2026-2027</p></div>
<div class="info-grid">
<div class="info-item"><span class="label">Student Name</span>{student.student_name}</div>
<div class="info-item"><span class="label">Ticket No</span>{ticket_no}</div>
<div class="info-item"><span class="label">Academic Term</span>{(ht_doc.academic_term if ht_doc else '') or ''}</div>
<div class="info-item"><span class="label">Program</span>{program or 'N/A'}</div>
<div class="info-item"><span class="label">Exam Type</span>{(ht_doc.exam_type if ht_doc else '') or 'Regular'}</div>
<div class="info-item"><span class="label">Eligibility</span><span class="badge">{'Eligible' if (ht_doc and ht_doc.is_eligible) else 'Eligible'}</span></div>
</div>"""

        exams = list(ht_doc.exams) if (ht_doc and ht_doc.exams) else []
        if exams:
            exams_sorted = sorted(exams, key=lambda e: (e.exam_date or ""))
            html += """<h3>Examination Schedule</h3>
<table><tr><th>#</th><th>Subject</th><th>Date</th><th>Time</th><th>Venue</th></tr>"""
            for i, exam in enumerate(exams_sorted, 1):
                html += f"<tr><td>{i}</td><td>{exam.course or ''}</td><td>{exam.exam_date or ''}</td><td>{_fmt_time(exam.exam_time)}</td><td>{exam.venue or ''}</td></tr>"
            html += "</table>"
        else:
            html += "<p><em>Examination schedule will be communicated separately. Please report to the examination hall 30 minutes before the scheduled time.</em></p>"

        html += """<div class="footer">
<p><strong>Important Instructions:</strong></p>
<ul>
<li>Carry this hall ticket to every examination</li>
<li>Carry a valid government-issued photo ID proof</li>
<li>Mobile phones and electronic devices are not allowed in the examination hall</li>
<li>Arrive at least 30 minutes before the examination time</li>
</ul>
</div></body></html>"""

        from frappe.utils.pdf import get_pdf
        pdf_bytes = get_pdf(html)
        frappe.local.response.update({
            "type": "pdf",
            "filename": f"Hall_Ticket_{ticket_no}.pdf",
            "filecontent": pdf_bytes,
        })
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"download_hall_ticket: {e}")
        frappe.throw(_("Could not generate hall ticket"))

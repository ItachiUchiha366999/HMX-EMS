"""Server-side helpers for Hostel Allocation desk-side actions.

`allot_room(student, room, from_date, ...)` creates a Hostel Allocation in
draft state and pushes it to "Pending Warden Approval" so the warden's
approval queue picks it up. Available rooms are determined by occupancy
vs capacity.
"""

import frappe
from frappe import _


@frappe.whitelist(methods=["GET"])
def list_available_rooms(building=None, gender=None):
    """List rooms with available beds. Optional filters by building/gender."""
    cond = ["hr.docstatus = 0", "hr.status = 'Available'"]
    args = []
    if building:
        cond.append("hr.hostel_building = %s")
        args.append(building)

    rows = frappe.db.sql(f"""
        SELECT hr.name, hr.room_number, hr.hostel_building, hr.floor, hr.room_type,
               hr.capacity, hr.occupied_beds, hr.available_beds,
               hr.rent_per_month, hb.building_name
        FROM `tabHostel Room` hr
        LEFT JOIN `tabHostel Building` hb ON hb.name = hr.hostel_building
        WHERE {' AND '.join(cond)} AND hr.available_beds > 0
        ORDER BY hr.hostel_building, hr.room_number
        LIMIT 50
    """, args, as_dict=True)
    return rows


@frappe.whitelist(methods=["POST"])
def allot_room(student, room, from_date=None, to_date=None, bed_number=None):
    """Create a Hostel Allocation in 'Pending Warden Approval' state.

    Caller needs `University Admin` (or higher). The warden then approves
    via the standard workflow on the Hostel Allocation form.
    """
    roles = set(frappe.get_roles(frappe.session.user))
    if not (roles & {"University Admin", "University Warden", "University Registrar",
                     "System Manager", "Administrator"}):
        frappe.throw(_("You don't have permission to allot hostel rooms"), frappe.PermissionError)

    if not frappe.db.exists("Student", student):
        frappe.throw(_("Student {0} not found").format(student))
    if not frappe.db.exists("Hostel Room", room):
        frappe.throw(_("Hostel Room {0} not found").format(room))

    # Reject if student already has an active allocation
    existing = frappe.db.get_value(
        "Hostel Allocation",
        {"student": student, "docstatus": 1, "status": "Active"},
        "name",
    )
    if existing:
        frappe.throw(_("Student already has an active allocation: {0}").format(existing))

    room_doc = frappe.db.get_value(
        "Hostel Room", room,
        ["name", "hostel_building", "room_type", "floor", "rent_per_month",
         "capacity", "occupied_beds", "available_beds"],
        as_dict=True,
    )
    if (room_doc.available_beds or 0) <= 0:
        frappe.throw(_("Room {0} has no available beds").format(room))

    student_doc = frappe.db.get_value(
        "Student", student,
        ["name", "student_name", "gender", "custom_program"],
        as_dict=True,
    )

    today = frappe.utils.nowdate()
    from_date = from_date or today
    to_date = to_date or frappe.utils.add_years(from_date, 1)

    ha = frappe.get_doc({
        "doctype": "Hostel Allocation",
        "student": student,
        "student_name": student_doc.student_name,
        "gender": student_doc.gender,
        "program": student_doc.custom_program,
        "academic_year": frappe.db.get_value("Academic Year", {}, "name"),
        "from_date": from_date,
        "to_date": to_date,
        "duration_months": 12,
        "status": "Active",
        "hostel_building": room_doc.hostel_building,
        "room": room,
        "room_type": room_doc.room_type,
        "bed_number": bed_number or ((room_doc.occupied_beds or 0) + 1),
        "floor": room_doc.floor,
        "rent_per_month": room_doc.rent_per_month or 0,
        "generate_fee": 0,
        "total_rent": 0,
        "security_deposit": 0,
        "mess_charges": 0,
        "total_amount": 0,
    })
    ha.flags.ignore_permissions = True
    ha.flags.ignore_mandatory = True
    ha.insert(ignore_permissions=True)

    # Push the workflow to Pending Warden Approval (admin's transition)
    ha.db_set("workflow_state", "Pending Warden Approval", update_modified=False)

    return {
        "name": ha.name,
        "student": student,
        "room": room,
        "building": room_doc.hostel_building,
        "from_date": from_date,
        "to_date": to_date,
        "workflow_state": "Pending Warden Approval",
    }

"""Server-side helpers for Transport Allocation desk-side actions.

`allot_transport(student, route, ...)` creates a draft Transport Allocation
and pushes it to "Pending Approval" so the registrar's approval queue picks
it up. Vehicle is taken from `Transport Route.assigned_vehicle`.
"""

import frappe
from frappe import _


@frappe.whitelist(methods=["GET"])
def list_active_routes():
    """Return all active Transport Routes with vehicle + driver + monthly_fare."""
    rows = frappe.db.sql("""
        SELECT name, route_name, route_code, route_type, start_point, end_point,
               total_distance, total_duration, total_stops, monthly_fare,
               departure_time, arrival_time,
               assigned_vehicle, driver, driver_contact
        FROM `tabTransport Route`
        WHERE is_active = 1
        ORDER BY route_name
        LIMIT 50
    """, as_dict=True)
    return rows


@frappe.whitelist(methods=["GET"])
def list_route_stops(route):
    """Return the stops on a route (in order)."""
    if not frappe.db.exists("DocType", "Transport Route Stop"):
        return []
    return frappe.db.get_all(
        "Transport Route Stop",
        filters={"parent": route},
        fields=["stop_name", "stop_sequence", "pickup_time", "drop_time", "idx"],
        order_by="idx asc",
    )


@frappe.whitelist(methods=["POST"])
def allot_transport(student, route, pickup_stop=None, drop_stop=None,
                    from_date=None, to_date=None):
    """Create a Transport Allocation in 'Pending Approval' state.

    Caller needs `University Admin` (or higher). The registrar then approves
    via the standard workflow on the Transport Allocation form.
    """
    roles = set(frappe.get_roles(frappe.session.user))
    if not (roles & {"University Admin", "University Registrar", "University Transport",
                     "System Manager", "Administrator"}):
        frappe.throw(_("You don't have permission to allot transport"), frappe.PermissionError)

    if not frappe.db.exists("Student", student):
        frappe.throw(_("Student {0} not found").format(student))
    if not frappe.db.exists("Transport Route", route):
        frappe.throw(_("Transport Route {0} not found").format(route))

    # Reject if student already has an active allocation
    existing = frappe.db.get_value(
        "Transport Allocation",
        {"student": student, "docstatus": 1, "status": "Active"},
        "name",
    )
    if existing:
        frappe.throw(_("Student already has an active transport allocation: {0}").format(existing))

    route_doc = frappe.db.get_value(
        "Transport Route", route,
        ["name", "route_name", "monthly_fare", "departure_time", "arrival_time",
         "assigned_vehicle", "is_active"],
        as_dict=True,
    )
    if not route_doc.is_active:
        frappe.throw(_("Route {0} is not active").format(route))

    student_doc = frappe.db.get_value(
        "Student", student,
        ["name", "student_name", "custom_program"],
        as_dict=True,
    )

    today = frappe.utils.nowdate()
    from_date = from_date or today
    to_date = to_date or frappe.utils.add_years(from_date, 1)
    months = max(int((frappe.utils.date_diff(to_date, from_date) or 0) / 30), 1)

    fare = float(route_doc.monthly_fare or 0)

    ta = frappe.get_doc({
        "doctype": "Transport Allocation",
        "student": student,
        "student_name": student_doc.student_name,
        "program": student_doc.custom_program,
        "academic_year": frappe.db.get_value("Academic Year", {}, "name"),
        "from_date": from_date,
        "to_date": to_date,
        "status": "Active",
        "route": route,
        "pickup_stop": pickup_stop,
        "drop_stop": drop_stop,
        "vehicle": route_doc.assigned_vehicle,
        "pickup_time": route_doc.departure_time,
        "drop_time": route_doc.arrival_time,
        "monthly_fare": fare,
        "total_months": months,
        "total_fare": fare * months,
        "generate_fee": 0,
    })
    ta.flags.ignore_permissions = True
    ta.flags.ignore_mandatory = True
    ta.insert(ignore_permissions=True)

    # Push the workflow to Pending Approval (admin's transition)
    ta.db_set("workflow_state", "Pending Approval", update_modified=False)

    return {
        "name": ta.name,
        "student": student,
        "route": route,
        "route_name": route_doc.route_name,
        "vehicle": route_doc.assigned_vehicle,
        "monthly_fare": fare,
        "from_date": from_date,
        "to_date": to_date,
        "workflow_state": "Pending Approval",
    }

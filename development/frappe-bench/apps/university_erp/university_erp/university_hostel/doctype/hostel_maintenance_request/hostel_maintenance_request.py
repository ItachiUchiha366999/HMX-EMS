# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate


class HostelMaintenanceRequest(Document):
    """Hostel Maintenance Request for tracking room/building maintenance issues"""

    def validate(self):
        self.validate_room_belongs_to_building()
        self.set_assigned_date()

    def validate_room_belongs_to_building(self):
        """Validate that the room belongs to the selected building"""
        if self.room and self.building:
            room_building = frappe.db.get_value("Hostel Room", self.room, "hostel_building")
            if room_building != self.building:
                frappe.throw(
                    _("Room {0} does not belong to building {1}").format(
                        self.room_number or self.room,
                        self.building_name or self.building
                    )
                )

    def set_assigned_date(self):
        """Set assigned date when assigned_to is set"""
        if self.assigned_to and not self.assigned_on:
            self.assigned_on = today()

    def on_submit(self):
        """Actions on submit"""
        self.notify_staff()

    def notify_staff(self):
        """Notify relevant staff about the maintenance request"""
        if self.priority == "Urgent":
            frappe.msgprint(
                _("Urgent maintenance request submitted. Staff will be notified."),
                indicator="red"
            )

    def before_update_after_submit(self):
        """Allow status updates after submit"""
        pass

    def on_cancel(self):
        """Actions on cancel"""
        self.status = "Cancelled"


@frappe.whitelist()
def get_open_requests(building=None, priority=None, request_type=None):
    """Get all open maintenance requests"""
    filters = {"status": ["in", ["Open", "In Progress"]], "docstatus": 1}

    if building:
        filters["building"] = building
    if priority:
        filters["priority"] = priority
    if request_type:
        filters["request_type"] = request_type

    return frappe.get_all(
        "Hostel Maintenance Request",
        filters=filters,
        fields=[
            "name",
            "request_date",
            "building",
            "building_name",
            "room",
            "room_number",
            "requested_by",
            "student_name",
            "request_type",
            "priority",
            "subject",
            "description",
            "assigned_to",
            "expected_completion",
            "status"
        ],
        order_by="priority desc, request_date asc"
    )


@frappe.whitelist()
def assign_request(request_name, employee, expected_completion=None):
    """Assign a maintenance request to an employee"""
    request = frappe.get_doc("Hostel Maintenance Request", request_name)

    if request.docstatus != 1:
        frappe.throw(_("Request must be submitted before assignment"))

    request.assigned_to = employee
    request.assigned_on = today()
    request.expected_completion = expected_completion
    request.status = "In Progress"
    request.db_update()
    request.notify_update()

    return {
        "name": request.name,
        "assigned_to": request.assigned_to,
        "status": request.status
    }


@frappe.whitelist()
def complete_request(request_name, resolution_remarks=None, cost_incurred=None):
    """Mark a maintenance request as completed"""
    request = frappe.get_doc("Hostel Maintenance Request", request_name)

    if request.docstatus != 1:
        frappe.throw(_("Request must be submitted before completion"))

    if request.status == "Completed":
        frappe.throw(_("Request is already completed"))

    request.status = "Completed"
    request.actual_completion = today()
    request.resolution_remarks = resolution_remarks
    if cost_incurred:
        request.cost_incurred = cost_incurred
    request.db_update()
    request.notify_update()

    return {
        "name": request.name,
        "status": request.status,
        "actual_completion": request.actual_completion
    }


@frappe.whitelist()
def get_request_summary(building=None, from_date=None, to_date=None):
    """Get summary of maintenance requests"""
    conditions = ["docstatus = 1"]
    values = []

    if building:
        conditions.append("building = %s")
        values.append(building)
    if from_date:
        conditions.append("request_date >= %s")
        values.append(from_date)
    if to_date:
        conditions.append("request_date <= %s")
        values.append(to_date)

    where_clause = " AND ".join(conditions)

    # By type
    by_type = frappe.db.sql(f"""
        SELECT
            request_type,
            COUNT(*) as count,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(COALESCE(cost_incurred, 0)) as total_cost
        FROM `tabHostel Maintenance Request`
        WHERE {where_clause}
        GROUP BY request_type
        ORDER BY count DESC
    """, values, as_dict=True)

    # By priority
    by_priority = frappe.db.sql(f"""
        SELECT
            priority,
            COUNT(*) as count,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
        FROM `tabHostel Maintenance Request`
        WHERE {where_clause}
        GROUP BY priority
    """, values, as_dict=True)

    # By status
    by_status = frappe.db.sql(f"""
        SELECT
            status,
            COUNT(*) as count
        FROM `tabHostel Maintenance Request`
        WHERE {where_clause}
        GROUP BY status
    """, values, as_dict=True)

    # Overall stats
    overall = frappe.db.sql(f"""
        SELECT
            COUNT(*) as total_requests,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_requests,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(COALESCE(cost_incurred, 0)) as total_cost,
            AVG(CASE WHEN actual_completion IS NOT NULL AND request_date IS NOT NULL
                THEN DATEDIFF(actual_completion, request_date) END) as avg_resolution_days
        FROM `tabHostel Maintenance Request`
        WHERE {where_clause}
    """, values, as_dict=True)[0]

    return {
        "overall": overall,
        "by_type": by_type,
        "by_priority": by_priority,
        "by_status": by_status
    }


@frappe.whitelist()
def get_pending_requests_for_room(room):
    """Get pending maintenance requests for a specific room"""
    return frappe.get_all(
        "Hostel Maintenance Request",
        filters={
            "room": room,
            "status": ["in", ["Open", "In Progress"]],
            "docstatus": 1
        },
        fields=[
            "name",
            "request_date",
            "request_type",
            "priority",
            "subject",
            "status",
            "assigned_to",
            "expected_completion"
        ],
        order_by="priority desc, request_date asc"
    )

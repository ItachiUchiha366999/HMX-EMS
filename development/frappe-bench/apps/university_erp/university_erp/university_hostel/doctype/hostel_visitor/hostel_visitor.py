# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowtime, getdate, today, time_diff_in_hours, get_time


class HostelVisitor(Document):
    """Hostel Visitor management for tracking visitors"""

    def validate(self):
        self.validate_student_in_building()
        self.set_student_room()
        self.calculate_duration()

    def validate_student_in_building(self):
        """Validate student is currently residing in the specified building"""
        if not self.student or not self.building:
            return

        # Check for active allocation in this building
        allocation = frappe.db.sql("""
            SELECT ha.room, hr.room_number
            FROM `tabHostel Allocation` ha
            JOIN `tabHostel Room` hr ON ha.room = hr.name
            WHERE ha.student = %s
            AND hr.hostel_building = %s
            AND ha.status = 'Active'
            AND ha.docstatus = 1
            AND ha.from_date <= %s
            AND (ha.to_date IS NULL OR ha.to_date >= %s)
        """, (self.student, self.building, self.visit_date or today(), self.visit_date or today()), as_dict=True)

        if not allocation:
            frappe.throw(
                _("Student {0} does not have an active allocation in {1}").format(
                    self.student_name or self.student,
                    self.building_name or self.building
                )
            )

    def set_student_room(self):
        """Set student's room from allocation"""
        if not self.student or not self.building:
            return

        room_data = frappe.db.sql("""
            SELECT ha.room
            FROM `tabHostel Allocation` ha
            JOIN `tabHostel Room` hr ON ha.room = hr.name
            WHERE ha.student = %s
            AND hr.hostel_building = %s
            AND ha.status = 'Active'
            AND ha.docstatus = 1
            LIMIT 1
        """, (self.student, self.building), as_dict=True)

        if room_data:
            self.room = room_data[0].room

    def calculate_duration(self):
        """Calculate visit duration if checked out"""
        if self.check_in_time and self.check_out_time:
            hours = time_diff_in_hours(self.check_out_time, self.check_in_time)
            if hours < 1:
                minutes = int(hours * 60)
                self.duration = f"{minutes} minutes"
            else:
                self.duration = f"{hours:.1f} hours"
        else:
            self.duration = None

    def on_update(self):
        """Actions on update"""
        if self.status == "Checked Out" and not self.check_out_time:
            self.check_out_time = nowtime()
            self.db_update()


@frappe.whitelist()
def check_in_visitor(visitor_name, visitor_mobile, student, building, relationship,
                     purpose=None, visitor_id_type=None, visitor_id_number=None):
    """Create a new visitor check-in record"""
    visitor = frappe.get_doc({
        "doctype": "Hostel Visitor",
        "visitor_name": visitor_name,
        "visitor_mobile": visitor_mobile,
        "student": student,
        "building": building,
        "relationship": relationship,
        "purpose": purpose,
        "visitor_id_type": visitor_id_type,
        "visitor_id_number": visitor_id_number,
        "visit_date": today(),
        "check_in_time": nowtime(),
        "status": "Checked In"
    })
    visitor.insert()
    return {
        "name": visitor.name,
        "visitor_name": visitor.visitor_name,
        "student_name": visitor.student_name,
        "check_in_time": visitor.check_in_time
    }


@frappe.whitelist()
def check_out_visitor(visitor_id):
    """Check out a visitor"""
    visitor = frappe.get_doc("Hostel Visitor", visitor_id)
    if visitor.status != "Checked In":
        frappe.throw(_("Visitor is not currently checked in"))

    visitor.check_out_time = nowtime()
    visitor.status = "Checked Out"
    visitor.save()

    return {
        "name": visitor.name,
        "visitor_name": visitor.visitor_name,
        "check_out_time": visitor.check_out_time,
        "duration": visitor.duration
    }


@frappe.whitelist()
def deny_visitor(visitor_id, remarks=None):
    """Deny a visitor entry"""
    visitor = frappe.get_doc("Hostel Visitor", visitor_id)
    visitor.status = "Denied"
    visitor.approval_remarks = remarks
    visitor.save()
    return visitor.status


@frappe.whitelist()
def get_active_visitors(building=None):
    """Get all currently checked-in visitors"""
    filters = {"status": "Checked In"}
    if building:
        filters["building"] = building

    return frappe.get_all(
        "Hostel Visitor",
        filters=filters,
        fields=[
            "name",
            "visitor_name",
            "visitor_mobile",
            "relationship",
            "student",
            "student_name",
            "building",
            "building_name",
            "room",
            "visit_date",
            "check_in_time",
            "expected_checkout_time",
            "purpose"
        ],
        order_by="check_in_time desc"
    )


@frappe.whitelist()
def get_visitor_log(building=None, from_date=None, to_date=None):
    """Get visitor log for a building"""
    conditions = []
    values = []

    if building:
        conditions.append("building = %s")
        values.append(building)

    if from_date:
        conditions.append("visit_date >= %s")
        values.append(from_date)

    if to_date:
        conditions.append("visit_date <= %s")
        values.append(to_date)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    return frappe.db.sql("""
        SELECT
            name,
            visitor_name,
            visitor_mobile,
            relationship,
            visitor_id_type,
            visitor_id_number,
            student,
            student_name,
            building,
            building_name,
            room,
            visit_date,
            check_in_time,
            check_out_time,
            duration,
            purpose,
            status
        FROM `tabHostel Visitor`
        WHERE {where_clause}
        ORDER BY visit_date DESC, check_in_time DESC
    """.format(where_clause=where_clause), values, as_dict=True)


@frappe.whitelist()
def auto_checkout_visitors():
    """Scheduled job to auto-checkout visitors at end of day"""
    # Get all checked-in visitors from previous days
    visitors = frappe.get_all(
        "Hostel Visitor",
        filters={
            "status": "Checked In",
            "visit_date": ["<", today()]
        },
        pluck="name"
    )

    for visitor_id in visitors:
        visitor = frappe.get_doc("Hostel Visitor", visitor_id)
        visitor.check_out_time = "23:59:00"
        visitor.status = "Checked Out"
        visitor.approval_remarks = "Auto-checkout at end of day"
        visitor.save(ignore_permissions=True)

    if visitors:
        frappe.db.commit()

    return len(visitors)

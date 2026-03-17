# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, get_datetime, now_datetime, time_diff_in_hours, nowdate


class LabEquipmentBooking(Document):
    """Lab Equipment Booking - Equipment booking management"""

    def validate(self):
        """Validate booking"""
        self.validate_times()
        self.check_conflicts()
        self.validate_equipment_status()

    def validate_times(self):
        """Validate time fields"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                frappe.throw(_("End Time must be after Start Time"))

        if self.booking_date:
            if getdate(self.booking_date) < getdate(nowdate()) and self.docstatus == 0:
                frappe.throw(_("Booking Date cannot be in the past"))

    def check_conflicts(self):
        """Check for conflicting bookings"""
        equipment = frappe.get_doc("Lab Equipment", self.equipment)
        is_available, message = equipment.check_availability(
            self.booking_date,
            self.start_time,
            self.end_time,
            exclude_booking=self.name if not self.is_new() else None
        )

        if not is_available:
            frappe.throw(message)

    def validate_equipment_status(self):
        """Validate equipment is available"""
        equipment = frappe.get_doc("Lab Equipment", self.equipment)

        if equipment.status not in ["Available", "In Use"]:
            frappe.throw(_("Equipment {0} is {1} and cannot be booked").format(
                self.equipment, equipment.status
            ))

    def on_submit(self):
        """On submit - approve booking"""
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = nowdate()
        self.db_update()

    def on_cancel(self):
        """On cancel"""
        self.status = "Cancelled"

        # If equipment was in use, set it back to available
        if self.actual_start_time and not self.actual_end_time:
            equipment = frappe.get_doc("Lab Equipment", self.equipment)
            equipment.db_set("status", "Available")

    def calculate_duration(self):
        """Calculate duration in hours"""
        if self.actual_start_time and self.actual_end_time:
            start = get_datetime(self.actual_start_time)
            end = get_datetime(self.actual_end_time)
            self.duration_hours = time_diff_in_hours(end, start)
        return self.duration_hours


@frappe.whitelist()
def start_usage(name):
    """Start using the equipment"""
    doc = frappe.get_doc("Lab Equipment Booking", name)

    if doc.docstatus != 1:
        frappe.throw(_("Booking must be submitted before starting usage"))

    if doc.status != "Approved":
        frappe.throw(_("Only approved bookings can be started"))

    doc.status = "In Use"
    doc.actual_start_time = now_datetime()
    doc.db_update()

    # Update equipment status
    equipment = frappe.get_doc("Lab Equipment", doc.equipment)
    equipment.db_set("status", "In Use")

    frappe.msgprint(_("Equipment usage started"))
    return doc


@frappe.whitelist()
def end_usage(name):
    """End equipment usage"""
    doc = frappe.get_doc("Lab Equipment Booking", name)

    if doc.status != "In Use":
        frappe.throw(_("Can only end usage for bookings that are In Use"))

    doc.status = "Completed"
    doc.actual_end_time = now_datetime()
    doc.calculate_duration()
    doc.db_update()

    # Update equipment status and usage hours
    equipment = frappe.get_doc("Lab Equipment", doc.equipment)
    equipment.db_set("status", "Available")
    equipment.update_usage_hours(doc.duration_hours)

    frappe.msgprint(_("Equipment usage ended. Duration: {0} hours").format(
        round(doc.duration_hours, 2)
    ))
    return doc


@frappe.whitelist()
def get_equipment_bookings(equipment, from_date, to_date):
    """Get bookings for equipment in date range"""
    return frappe.get_all(
        "Lab Equipment Booking",
        filters={
            "equipment": equipment,
            "booking_date": ["between", [from_date, to_date]],
            "status": ["in", ["Pending", "Approved", "In Use", "Completed"]],
            "docstatus": ["<", 2]
        },
        fields=["name", "booked_by", "booking_date", "start_time", "end_time", "purpose", "status"],
        order_by="booking_date, start_time"
    )

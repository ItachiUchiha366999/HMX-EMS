# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_months, nowdate, flt


class LabEquipment(Document):
    """Lab Equipment - Equipment in university laboratories"""

    def validate(self):
        """Validate lab equipment"""
        self.validate_dates()
        self.calculate_next_calibration()
        self.check_usage_limits()

    def validate_dates(self):
        """Validate date fields"""
        if self.purchase_date and self.warranty_end:
            if getdate(self.warranty_end) < getdate(self.purchase_date):
                frappe.throw(_("Warranty End Date cannot be before Purchase Date"))

    def calculate_next_calibration(self):
        """Calculate next calibration date based on frequency"""
        if self.requires_calibration and self.last_calibration_date and self.calibration_frequency:
            months_map = {
                "Monthly": 1,
                "Quarterly": 3,
                "Half-yearly": 6,
                "Yearly": 12
            }
            months = months_map.get(self.calibration_frequency, 12)
            self.next_calibration_date = add_months(self.last_calibration_date, months)

    def check_usage_limits(self):
        """Check if equipment has exceeded usage limits"""
        if self.max_usage_hours and self.max_usage_hours > 0:
            if flt(self.total_usage_hours) >= flt(self.max_usage_hours):
                frappe.msgprint(
                    _("Equipment {0} has reached maximum usage hours. Maintenance may be required.").format(
                        self.equipment_name
                    ),
                    alert=True
                )

    def update_usage_hours(self, hours):
        """Update total usage hours"""
        self.total_usage_hours = flt(self.total_usage_hours) + flt(hours)
        self.db_set("total_usage_hours", self.total_usage_hours)

        # Check if maintenance is needed
        self.check_usage_limits()

    def check_availability(self, booking_date, start_time, end_time, exclude_booking=None):
        """Check if equipment is available for booking"""
        if self.status != "Available":
            return False, _("Equipment is {0}").format(self.status)

        # Check for conflicting bookings
        filters = {
            "equipment": self.name,
            "booking_date": booking_date,
            "status": ["in", ["Pending", "Approved", "In Use"]],
            "docstatus": ["<", 2]
        }

        if exclude_booking:
            filters["name"] = ["!=", exclude_booking]

        conflicting = frappe.db.sql("""
            SELECT name, start_time, end_time
            FROM `tabLab Equipment Booking`
            WHERE equipment = %(equipment)s
            AND booking_date = %(date)s
            AND status IN ('Pending', 'Approved', 'In Use')
            AND docstatus < 2
            AND (
                (start_time <= %(start)s AND end_time > %(start)s)
                OR (start_time < %(end)s AND end_time >= %(end)s)
                OR (start_time >= %(start)s AND end_time <= %(end)s)
            )
            {exclude}
        """.format(exclude="AND name != %(exclude)s" if exclude_booking else ""),
        {
            "equipment": self.name,
            "date": booking_date,
            "start": start_time,
            "end": end_time,
            "exclude": exclude_booking
        }, as_dict=True)

        if conflicting:
            return False, _("Equipment is already booked from {0} to {1}").format(
                conflicting[0].start_time, conflicting[0].end_time
            )

        return True, None


@frappe.whitelist()
def check_equipment_availability(equipment, booking_date, start_time, end_time, exclude_booking=None):
    """API to check equipment availability"""
    doc = frappe.get_doc("Lab Equipment", equipment)
    is_available, message = doc.check_availability(booking_date, start_time, end_time, exclude_booking)
    return {"available": is_available, "message": message}


@frappe.whitelist()
def get_equipment_due_for_calibration():
    """Get equipment due for calibration"""
    today = nowdate()

    return frappe.db.sql("""
        SELECT name, equipment_name, equipment_code, lab,
               next_calibration_date, calibration_frequency
        FROM `tabLab Equipment`
        WHERE requires_calibration = 1
        AND next_calibration_date <= %s
        AND status NOT IN ('Decommissioned', 'Out of Order')
        ORDER BY next_calibration_date
    """, today, as_dict=True)

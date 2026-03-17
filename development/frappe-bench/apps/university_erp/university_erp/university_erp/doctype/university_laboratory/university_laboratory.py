# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class UniversityLaboratory(Document):
    """University Laboratory - Lab/Workshop facilities"""

    def validate(self):
        """Validate laboratory"""
        self.validate_in_charge()

    def validate_in_charge(self):
        """Validate lab in-charge is an active employee"""
        if self.in_charge:
            employee = frappe.get_doc("Employee", self.in_charge)
            if employee.status != "Active":
                frappe.throw(_("Lab In-Charge {0} is not an active employee").format(
                    self.in_charge
                ))

    def get_equipment_count(self):
        """Get count of equipment in this lab"""
        return frappe.db.count("Lab Equipment", {"lab": self.name})

    def get_available_equipment(self):
        """Get list of available equipment in this lab"""
        return frappe.get_all(
            "Lab Equipment",
            filters={"lab": self.name, "status": "Available"},
            fields=["name", "equipment_name", "equipment_type"]
        )


@frappe.whitelist()
def get_lab_equipment(lab):
    """Get all equipment in a lab"""
    return frappe.get_all(
        "Lab Equipment",
        filters={"lab": lab},
        fields=["name", "equipment_name", "equipment_code", "equipment_type", "status"]
    )


@frappe.whitelist()
def get_lab_schedule(lab, date):
    """Get lab equipment booking schedule for a date"""
    return frappe.get_all(
        "Lab Equipment Booking",
        filters={
            "equipment": ["in", frappe.get_all("Lab Equipment", {"lab": lab}, pluck="name")],
            "booking_date": date,
            "status": ["in", ["Approved", "In Use"]]
        },
        fields=["equipment", "booked_by", "start_time", "end_time", "purpose", "status"]
    )

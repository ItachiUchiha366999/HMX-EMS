# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff


class TransportVehicle(Document):
    """Transport Vehicle master with maintenance tracking"""

    def validate(self):
        self.validate_capacity()
        self.check_document_expiry()

    def validate_capacity(self):
        """Validate seating capacity based on vehicle type"""
        type_capacity = {
            "Bus": (30, 60),
            "Mini Bus": (15, 30),
            "Van": (8, 15),
            "Car": (4, 8)
        }

        if self.vehicle_type in type_capacity:
            min_cap, max_cap = type_capacity[self.vehicle_type]
            if self.seating_capacity < min_cap or self.seating_capacity > max_cap:
                frappe.msgprint(
                    _("Seating capacity for {0} is typically between {1} and {2}").format(
                        self.vehicle_type, min_cap, max_cap
                    ),
                    alert=True
                )

    def check_document_expiry(self):
        """Check for document expiry warnings"""
        today = getdate(nowdate())
        warning_days = 30

        documents = [
            ("Insurance", self.insurance_expiry),
            ("Fitness Certificate", self.fitness_expiry),
            ("Permit", self.permit_expiry),
            ("Registration", self.registration_expiry)
        ]

        for doc_name, expiry_date in documents:
            if expiry_date:
                days_left = date_diff(expiry_date, today)
                if days_left < 0:
                    frappe.msgprint(
                        _("{0} has expired on {1}").format(doc_name, expiry_date),
                        indicator="red",
                        alert=True
                    )
                elif days_left <= warning_days:
                    frappe.msgprint(
                        _("{0} will expire in {1} days").format(doc_name, days_left),
                        indicator="orange",
                        alert=True
                    )


@frappe.whitelist()
def get_available_vehicles(vehicle_type=None, date=None):
    """Get available vehicles for assignment"""
    conditions = ["is_active = 1", "status = 'Available'"]
    values = []

    if vehicle_type:
        conditions.append("vehicle_type = %s")
        values.append(vehicle_type)

    where_clause = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            name,
            vehicle_number,
            vehicle_name,
            vehicle_type,
            seating_capacity,
            driver_name,
            driver_contact
        FROM `tabTransport Vehicle`
        WHERE {where_clause}
        ORDER BY seating_capacity DESC
    """.format(where_clause=where_clause), values, as_dict=True)


@frappe.whitelist()
def get_vehicles_needing_attention():
    """Get vehicles with expiring documents or pending maintenance"""
    today = nowdate()
    warning_date = frappe.utils.add_days(today, 30)

    return frappe.db.sql("""
        SELECT
            name,
            vehicle_number,
            vehicle_type,
            CASE
                WHEN insurance_expiry <= %s THEN 'Insurance'
                WHEN fitness_expiry <= %s THEN 'Fitness Certificate'
                WHEN permit_expiry <= %s THEN 'Permit'
                WHEN next_service_due <= %s THEN 'Service Due'
            END as attention_needed,
            LEAST(
                COALESCE(insurance_expiry, '9999-12-31'),
                COALESCE(fitness_expiry, '9999-12-31'),
                COALESCE(permit_expiry, '9999-12-31'),
                COALESCE(next_service_due, '9999-12-31')
            ) as due_date
        FROM `tabTransport Vehicle`
        WHERE is_active = 1
        AND (
            insurance_expiry <= %s
            OR fitness_expiry <= %s
            OR permit_expiry <= %s
            OR next_service_due <= %s
        )
        ORDER BY due_date
    """, (warning_date, warning_date, warning_date, warning_date,
          warning_date, warning_date, warning_date, warning_date), as_dict=True)

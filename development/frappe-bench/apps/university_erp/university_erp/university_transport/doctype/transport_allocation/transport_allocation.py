# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff, add_months


class TransportAllocation(Document):
    """Student transport route allocation with fee generation"""

    def validate(self):
        self.set_student_details()
        self.validate_dates()
        self.validate_route_capacity()
        self.validate_duplicate_allocation()
        self.calculate_fare()

    def set_student_details(self):
        """Set student details from linked student"""
        if self.student:
            student = frappe.get_doc("Student", self.student)
            self.student_name = student.student_name

            # Get active program enrollment
            enrollment = frappe.db.get_value(
                "Program Enrollment",
                {"student": self.student, "docstatus": 1},
                "program"
            )
            if enrollment:
                self.program = enrollment

    def validate_dates(self):
        """Validate allocation dates"""
        if self.to_date and getdate(self.from_date) > getdate(self.to_date):
            frappe.throw(_("From Date cannot be after To Date"))

        # Calculate total months if to_date is set
        if self.to_date:
            days = date_diff(self.to_date, self.from_date)
            self.total_months = max(1, round(days / 30))
        elif self.total_months:
            self.to_date = add_months(self.from_date, self.total_months)

    def validate_route_capacity(self):
        """Check if route has available capacity"""
        if not self.route:
            return

        route = frappe.get_doc("Transport Route", self.route)
        if not route.assigned_vehicle:
            frappe.msgprint(
                _("Route {0} does not have an assigned vehicle").format(self.route),
                alert=True
            )
            return

        vehicle = frappe.get_doc("Transport Vehicle", route.assigned_vehicle)

        # Count current allocations for this route
        current_allocations = frappe.db.count(
            "Transport Allocation",
            {
                "route": self.route,
                "status": "Active",
                "docstatus": 1,
                "name": ["!=", self.name or ""]
            }
        )

        if current_allocations >= vehicle.seating_capacity:
            frappe.throw(
                _("Route {0} has reached maximum capacity ({1} students)").format(
                    self.route, vehicle.seating_capacity
                )
            )

    def validate_duplicate_allocation(self):
        """Check for existing active allocation for the student"""
        existing = frappe.db.exists(
            "Transport Allocation",
            {
                "student": self.student,
                "status": "Active",
                "docstatus": 1,
                "name": ["!=", self.name or ""]
            }
        )
        if existing:
            frappe.throw(
                _("Student {0} already has an active transport allocation: {1}").format(
                    self.student_name, existing
                )
            )

    def calculate_fare(self):
        """Calculate total fare"""
        if self.monthly_fare and self.total_months:
            self.total_fare = self.monthly_fare * self.total_months
        else:
            self.total_fare = self.monthly_fare or 0

    def on_submit(self):
        """Create transport fee on submit"""
        if self.generate_fee and self.total_fare > 0:
            self.create_transport_fee()

    def on_cancel(self):
        """Update status on cancel"""
        self.db_set("status", "Cancelled")

    def create_transport_fee(self):
        """Create transport fee for student"""
        try:
            fee = frappe.get_doc({
                "doctype": "Fees",
                "student": self.student,
                "posting_date": nowdate(),
                "due_date": self.from_date,
                "custom_fee_type": "Transport Fee",
                "components": [{
                    "fees_category": "Transport Fee",
                    "description": f"Transport for {self.route} ({self.total_months or 1} month(s))",
                    "amount": self.total_fare
                }]
            })
            fee.insert(ignore_permissions=True)

            self.db_set("fee_reference", fee.name)
            frappe.msgprint(
                _("Transport Fee {0} created for amount {1}").format(
                    fee.name, self.total_fare
                ),
                alert=True
            )
        except Exception as e:
            frappe.log_error(f"Error creating transport fee: {str(e)}")
            frappe.msgprint(
                _("Could not create transport fee automatically. Please create manually."),
                alert=True
            )


@frappe.whitelist()
def get_route_students(route):
    """Get all students allocated to a route"""
    return frappe.db.sql("""
        SELECT
            ta.name as allocation,
            ta.student,
            s.student_name,
            ta.pickup_stop,
            ta.drop_stop,
            ta.pickup_time,
            pe.program
        FROM `tabTransport Allocation` ta
        JOIN `tabStudent` s ON ta.student = s.name
        LEFT JOIN `tabProgram Enrollment` pe ON ta.student = pe.student AND pe.docstatus = 1
        WHERE ta.route = %s
        AND ta.status = 'Active'
        AND ta.docstatus = 1
        ORDER BY ta.pickup_time
    """, (route,), as_dict=True)


@frappe.whitelist()
def get_route_capacity(route):
    """Get current capacity utilization of a route"""
    route_doc = frappe.get_doc("Transport Route", route)

    current_allocations = frappe.db.count(
        "Transport Allocation",
        {
            "route": route,
            "status": "Active",
            "docstatus": 1
        }
    )

    capacity = 0
    if route_doc.assigned_vehicle:
        capacity = frappe.db.get_value(
            "Transport Vehicle", route_doc.assigned_vehicle, "seating_capacity"
        ) or 0

    return {
        "route": route,
        "route_name": route_doc.route_name,
        "vehicle": route_doc.assigned_vehicle,
        "capacity": capacity,
        "allocated": current_allocations,
        "available": max(0, capacity - current_allocations),
        "utilization": round(current_allocations / capacity * 100, 2) if capacity else 0
    }

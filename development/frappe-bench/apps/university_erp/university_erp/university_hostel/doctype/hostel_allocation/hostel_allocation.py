# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, date_diff, add_months


class HostelAllocation(Document):
    """Student hostel room allocation with fee generation"""

    def validate(self):
        self.set_student_details()
        self.validate_availability()
        self.validate_gender()
        self.validate_dates()
        self.validate_duplicate_allocation()
        self.calculate_amounts()

    def set_student_details(self):
        """Set student details from linked student"""
        if self.student:
            student = frappe.get_doc("Student", self.student)
            self.student_name = student.student_name
            self.gender = student.gender

            # Get active program enrollment
            enrollment = frappe.db.get_value(
                "Program Enrollment",
                {"student": self.student, "docstatus": 1},
                "program"
            )
            if enrollment:
                self.program = enrollment

    def validate_availability(self):
        """Check room availability"""
        room = frappe.get_doc("Hostel Room", self.room)

        # For new allocations or status change to Active
        if self.is_new() or (self.status == "Active" and self.get_doc_before_save() and
                              self.get_doc_before_save().status != "Active"):
            if room.available_beds <= 0:
                frappe.throw(
                    _("Room {0} has no available beds").format(self.room)
                )

    def validate_gender(self):
        """Ensure student gender matches hostel type"""
        if not self.gender:
            return

        hostel_type = frappe.db.get_value(
            "Hostel Building", self.hostel_building, "hostel_type"
        )

        gender_map = {"Boys": "Male", "Girls": "Female"}

        if hostel_type in gender_map:
            if self.gender != gender_map[hostel_type]:
                frappe.throw(
                    _("Student gender ({0}) does not match hostel type ({1})").format(
                        self.gender, hostel_type
                    )
                )

    def validate_dates(self):
        """Validate allocation dates"""
        if self.to_date and getdate(self.from_date) > getdate(self.to_date):
            frappe.throw(_("From Date cannot be after To Date"))

        # Calculate duration if to_date is set
        if self.to_date:
            days = date_diff(self.to_date, self.from_date)
            self.duration_months = max(1, round(days / 30))
        elif self.duration_months:
            self.to_date = add_months(self.from_date, self.duration_months)

    def validate_duplicate_allocation(self):
        """Check for existing active allocation for the student"""
        existing = frappe.db.exists(
            "Hostel Allocation",
            {
                "student": self.student,
                "status": "Active",
                "docstatus": 1,
                "name": ["!=", self.name or ""]
            }
        )
        if existing:
            frappe.throw(
                _("Student {0} already has an active hostel allocation: {1}").format(
                    self.student_name, existing
                )
            )

    def calculate_amounts(self):
        """Calculate total rent and amounts"""
        if self.rent_per_month and self.duration_months:
            self.total_rent = self.rent_per_month * self.duration_months
        else:
            self.total_rent = self.rent_per_month or 0

        self.total_amount = (
            (self.total_rent or 0) +
            (self.security_deposit or 0) +
            (self.mess_charges or 0)
        )

    def on_submit(self):
        """Update room availability and create fee on submit"""
        self.add_to_room_occupants()
        self.update_room_status()
        self.update_building_stats()
        if self.generate_fee:
            self.create_hostel_fee()

    def on_cancel(self):
        """Update room availability on cancel"""
        self.remove_from_room_occupants()
        self.db_set("status", "Cancelled")
        self.update_room_status()
        self.update_building_stats()

    def add_to_room_occupants(self):
        """Add student to room occupants table"""
        room = frappe.get_doc("Hostel Room", self.room)
        room.add_occupant(
            student=self.student,
            allocation=self.name,
            from_date=self.from_date,
            to_date=self.to_date
        )

    def remove_from_room_occupants(self):
        """Remove student from room occupants table"""
        room = frappe.get_doc("Hostel Room", self.room)
        room.remove_occupant(allocation=self.name)

    def update_building_stats(self):
        """Update hostel building statistics"""
        if self.hostel_building:
            building = frappe.get_doc("Hostel Building", self.hostel_building)
            building.update_stats()
            building.db_update()

    def update_room_status(self):
        """Update room occupancy"""
        room = frappe.get_doc("Hostel Room", self.room)
        room.update_availability_from_occupants()
        room.set_status()
        room.save(ignore_permissions=True)

    def create_hostel_fee(self):
        """Create hostel fee for student"""
        if self.total_amount <= 0:
            return

        components = []

        if self.total_rent:
            components.append({
                "fees_category": "Hostel Fee",
                "description": f"Hostel rent for {self.duration_months or 1} month(s)",
                "amount": self.total_rent
            })

        if self.security_deposit:
            components.append({
                "fees_category": "Security Deposit",
                "description": "Hostel security deposit (refundable)",
                "amount": self.security_deposit
            })

        if self.mess_charges:
            components.append({
                "fees_category": "Mess Fee",
                "description": "Mess charges",
                "amount": self.mess_charges
            })

        if not components:
            return

        try:
            fee = frappe.get_doc({
                "doctype": "Fees",
                "student": self.student,
                "posting_date": nowdate(),
                "due_date": self.from_date,
                "custom_fee_type": "Hostel Fee",
                "components": components
            })
            fee.insert(ignore_permissions=True)

            self.db_set("fee_reference", fee.name)
            frappe.msgprint(
                _("Hostel Fee {0} created for amount {1}").format(
                    fee.name, self.total_amount
                ),
                alert=True
            )
        except Exception as e:
            frappe.log_error(f"Error creating hostel fee: {str(e)}")
            frappe.msgprint(
                _("Could not create hostel fee automatically. Please create manually."),
                alert=True
            )


@frappe.whitelist()
def get_available_rooms(hostel_type=None, room_type=None):
    """Get available rooms with filters"""
    conditions = ["hr.available_beds > 0", "hr.status != 'Under Maintenance'"]
    values = []

    if hostel_type:
        conditions.append("hb.hostel_type = %s")
        values.append(hostel_type)

    if room_type:
        conditions.append("hr.room_type = %s")
        values.append(room_type)

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(f"""
        SELECT
            hr.name,
            hr.room_number,
            hr.room_type,
            hr.capacity,
            hr.available_beds,
            hr.rent_per_month,
            hb.name as building,
            hb.building_name,
            hb.hostel_type
        FROM `tabHostel Room` hr
        JOIN `tabHostel Building` hb ON hr.hostel_building = hb.name
        WHERE {where_clause}
        ORDER BY hb.building_name, hr.room_number
    """, values, as_dict=True)


@frappe.whitelist()
def vacate_room(allocation_name, vacate_date=None, remarks=None):
    """Vacate a hostel room"""
    allocation = frappe.get_doc("Hostel Allocation", allocation_name)

    if allocation.docstatus != 1:
        frappe.throw(_("Only submitted allocations can be vacated"))

    if allocation.status != "Active":
        frappe.throw(_("Allocation is not active"))

    allocation.db_set("status", "Vacated")
    allocation.db_set("to_date", vacate_date or nowdate())
    if remarks:
        allocation.db_set("remarks", remarks)

    # Remove from room occupants
    room = frappe.get_doc("Hostel Room", allocation.room)
    room.remove_occupant(allocation=allocation_name)

    # Update room status
    room.update_availability_from_occupants()
    room.set_status()
    room.save(ignore_permissions=True)

    # Update building stats
    if allocation.hostel_building:
        building = frappe.get_doc("Hostel Building", allocation.hostel_building)
        building.update_stats()
        building.db_update()

    return {"message": _("Room vacated successfully")}


@frappe.whitelist()
def transfer_room(allocation_name, new_room, transfer_date=None, remarks=None):
    """Transfer student to a different room"""
    old_allocation = frappe.get_doc("Hostel Allocation", allocation_name)

    if old_allocation.docstatus != 1:
        frappe.throw(_("Only submitted allocations can be transferred"))

    if old_allocation.status != "Active":
        frappe.throw(_("Allocation is not active"))

    # Check new room availability
    new_room_doc = frappe.get_doc("Hostel Room", new_room)
    if new_room_doc.available_beds <= 0:
        frappe.throw(_("New room {0} has no available beds").format(new_room))

    # Remove from old room occupants
    old_room = frappe.get_doc("Hostel Room", old_allocation.room)
    old_room.remove_occupant(allocation=allocation_name)

    # Mark old allocation as transferred
    old_allocation.db_set("status", "Transferred")
    old_allocation.db_set("to_date", transfer_date or nowdate())
    old_allocation.db_set("remarks", f"Transferred to {new_room}. {remarks or ''}")

    # Create new allocation
    new_allocation = frappe.get_doc({
        "doctype": "Hostel Allocation",
        "student": old_allocation.student,
        "academic_year": old_allocation.academic_year,
        "hostel_building": new_room_doc.hostel_building,
        "room": new_room,
        "from_date": transfer_date or nowdate(),
        "to_date": old_allocation.to_date,
        "generate_fee": 0,  # Don't generate fee for transfer
        "remarks": f"Transferred from {old_allocation.room}"
    })
    new_allocation.insert()
    new_allocation.submit()

    # Update old room status
    old_room.update_availability_from_occupants()
    old_room.set_status()
    old_room.save(ignore_permissions=True)

    # Update building stats for both buildings
    if old_allocation.hostel_building:
        old_building = frappe.get_doc("Hostel Building", old_allocation.hostel_building)
        old_building.update_stats()
        old_building.db_update()

    if new_room_doc.hostel_building and new_room_doc.hostel_building != old_allocation.hostel_building:
        new_building = frappe.get_doc("Hostel Building", new_room_doc.hostel_building)
        new_building.update_stats()
        new_building.db_update()

    return {
        "message": _("Transfer successful"),
        "new_allocation": new_allocation.name
    }

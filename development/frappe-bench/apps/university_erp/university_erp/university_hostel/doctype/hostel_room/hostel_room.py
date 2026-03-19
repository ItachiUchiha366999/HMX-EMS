# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class HostelRoom(Document):
    """Hostel Room master with availability tracking"""

    def validate(self):
        self.validate_capacity()
        self.update_availability_from_occupants()
        self.set_status()

    def validate_capacity(self):
        """Validate capacity based on room type"""
        if self.room_type == "Single" and self.capacity != 1:
            frappe.throw(_("Single room capacity must be 1"))
        elif self.room_type == "Double" and self.capacity not in [1, 2]:
            frappe.throw(_("Double room capacity must be 1 or 2"))
        elif self.room_type == "Triple" and self.capacity not in [1, 2, 3]:
            frappe.throw(_("Triple room capacity must be between 1 and 3"))

    def update_availability_from_occupants(self):
        """Update available beds based on occupants table"""
        # Count from occupants table if it exists
        if hasattr(self, 'occupants') and self.occupants:
            self.occupied_beds = len(self.occupants)
        else:
            # Fallback to counting from allocations
            if self.name:
                allocated = frappe.db.count(
                    "Hostel Allocation",
                    {
                        "room": self.name,
                        "status": "Active",
                        "docstatus": 1
                    }
                )
                self.occupied_beds = allocated
            else:
                self.occupied_beds = 0

        self.available_beds = (self.capacity or 0) - (self.occupied_beds or 0)

    def set_status(self):
        """Set room status based on occupancy"""
        if self.status == "Under Maintenance":
            return  # Don't change if under maintenance

        if self.available_beds <= 0:
            self.status = "Fully Occupied"
        elif self.occupied_beds > 0:
            self.status = "Partially Occupied"
        else:
            self.status = "Available"

    def on_update(self):
        """Update building statistics"""
        self.update_building_stats()

    def update_building_stats(self):
        """Update hostel building statistics"""
        if self.hostel_building:
            building = frappe.get_doc("Hostel Building", self.hostel_building)
            building.update_stats()
            building.db_update()

    def add_occupant(self, student, allocation, bed_number=None, from_date=None, to_date=None):
        """Add an occupant to this room"""
        # Check if student already in room
        for occupant in self.occupants or []:
            if occupant.student == student:
                frappe.throw(_("Student {0} is already in this room").format(student))

        # Check capacity
        if len(self.occupants or []) >= self.capacity:
            frappe.throw(_("Room is at full capacity"))

        self.append("occupants", {
            "student": student,
            "allocation": allocation,
            "bed_number": bed_number or str(len(self.occupants or []) + 1),
            "from_date": from_date,
            "to_date": to_date
        })
        self.save(ignore_permissions=True)

    def remove_occupant(self, student=None, allocation=None):
        """Remove an occupant from this room"""
        if not self.occupants:
            return

        self.occupants = [
            o for o in self.occupants
            if not ((student and o.student == student) or (allocation and o.allocation == allocation))
        ]
        self.save(ignore_permissions=True)


@frappe.whitelist()
def get_available_rooms(hostel_building=None, hostel_type=None, room_type=None, gender=None):
    """Get available rooms with filters including gender-based filtering"""
    conditions = ["hr.available_beds > 0", "hr.status != 'Under Maintenance'", "hb.status = 'Active'"]
    values = []

    if hostel_building:
        conditions.append("hr.hostel_building = %s")
        values.append(hostel_building)

    if hostel_type:
        conditions.append("hb.hostel_type = %s")
        values.append(hostel_type)

    if room_type:
        conditions.append("hr.room_type = %s")
        values.append(room_type)

    # Gender-based filtering
    if gender:
        if gender == "Male":
            conditions.append("hb.hostel_type IN ('Boys', 'Co-Ed')")
        elif gender == "Female":
            conditions.append("hb.hostel_type IN ('Girls', 'Co-Ed')")

    where_clause = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            hr.name,
            hr.room_number,
            hr.room_type,
            hr.capacity,
            hr.available_beds,
            hr.rent_per_month,
            hr.rent_per_semester,
            hr.floor,
            hr.has_ac,
            hr.has_attached_bathroom,
            hr.furniture_condition,
            hb.name as building,
            hb.building_name,
            hb.hostel_type,
            hb.annual_fee,
            hb.security_deposit
        FROM `tabHostel Room` hr
        JOIN `tabHostel Building` hb ON hr.hostel_building = hb.name
        WHERE {where_clause}
        ORDER BY hb.building_name, hr.floor, hr.room_number
    """.format(where_clause=where_clause), values, as_dict=True)


@frappe.whitelist()
def get_room_occupants(room):
    """Get current occupants of a room"""
    return frappe.db.sql("""
        SELECT
            ha.name as allocation,
            ha.student,
            s.student_name,
            s.gender,
            ha.from_date,
            ha.to_date,
            pe.program
        FROM `tabHostel Allocation` ha
        JOIN `tabStudent` s ON ha.student = s.name
        LEFT JOIN `tabProgram Enrollment` pe ON ha.student = pe.student AND pe.docstatus = 1
        WHERE ha.room = %s
        AND ha.status = 'Active'
        AND ha.docstatus = 1
        ORDER BY ha.from_date
    """, (room,), as_dict=True)


@frappe.whitelist()
def set_maintenance_status(room, status, remarks=None):
    """Set room maintenance status"""
    room_doc = frappe.get_doc("Hostel Room", room)

    if status == "start":
        if room_doc.occupied_beds > 0:
            frappe.throw("Cannot put room under maintenance while occupied")
        room_doc.status = "Under Maintenance"
        room_doc.maintenance_remarks = remarks
    else:
        room_doc.status = "Available"
        room_doc.last_maintenance_date = frappe.utils.today()

    room_doc.save()
    return room_doc.status

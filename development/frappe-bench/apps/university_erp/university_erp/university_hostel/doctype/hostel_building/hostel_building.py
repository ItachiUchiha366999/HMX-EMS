# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class HostelBuilding(Document):
    """Hostel Building master with capacity tracking"""

    def validate(self):
        self.validate_warden()
        self.validate_warden_gender()
        self.update_stats()

    def validate_warden(self):
        """Validate warden is an active employee"""
        if self.warden:
            status = frappe.db.get_value("Employee", self.warden, "status")
            if status != "Active":
                frappe.throw(_("Warden {0} is not an active employee").format(self.warden))

        if self.assistant_warden:
            status = frappe.db.get_value("Employee", self.assistant_warden, "status")
            if status != "Active":
                frappe.throw(_("Assistant Warden {0} is not an active employee").format(self.assistant_warden))

    def validate_warden_gender(self):
        """Validate warden gender matches hostel type"""
        if self.warden and self.hostel_type in ["Boys", "Girls"]:
            warden_gender = frappe.db.get_value("Employee", self.warden, "gender")
            expected_gender = "Male" if self.hostel_type == "Boys" else "Female"
            if warden_gender and warden_gender != expected_gender:
                frappe.msgprint(
                    _("Warning: Warden gender ({0}) doesn't match hostel type ({1})").format(
                        warden_gender, self.hostel_type
                    ),
                    indicator="orange"
                )

    def update_stats(self):
        """Update building statistics from rooms"""
        if not self.name:
            return

        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_rooms,
                COALESCE(SUM(capacity), 0) as total_capacity,
                COALESCE(SUM(occupied_beds), 0) as occupied
            FROM `tabHostel Room`
            WHERE hostel_building = %s
            AND status != 'Under Maintenance'
        """, (self.name,), as_dict=True)[0]

        self.total_rooms = stats.total_rooms or 0
        self.total_capacity = stats.total_capacity or 0
        self.occupied = stats.occupied or 0
        self.available = self.total_capacity - self.occupied

        if self.total_capacity > 0:
            self.occupancy_rate = (self.occupied / self.total_capacity) * 100
        else:
            self.occupancy_rate = 0

    def update_capacity_stats(self):
        """Public method to update and save capacity stats"""
        self.update_stats()
        self.db_update()


@frappe.whitelist()
def recalculate_all_building_stats():
    """Recalculate and persist occupancy stats for all buildings and rooms.
    Call this after bulk imports or data restores to fix stale cached fields."""
    # Recalculate room occupied_beds from live Hostel Allocation records
    frappe.db.sql("""
        UPDATE `tabHostel Room` hr
        SET hr.occupied_beds = (
            SELECT COUNT(*)
            FROM `tabHostel Allocation` ha
            WHERE ha.room = hr.name
            AND ha.status = 'Active'
            AND ha.docstatus = 1
        ),
        hr.available_beds = hr.capacity - (
            SELECT COUNT(*)
            FROM `tabHostel Allocation` ha
            WHERE ha.room = hr.name
            AND ha.status = 'Active'
            AND ha.docstatus = 1
        )
    """)

    # Recalculate building occupied/available/occupancy_rate from room stats
    frappe.db.sql("""
        UPDATE `tabHostel Building` hb
        JOIN (
            SELECT
                hostel_building,
                COUNT(*) as total_rooms,
                COALESCE(SUM(capacity), 0) as total_capacity,
                COALESCE(SUM(occupied_beds), 0) as occupied
            FROM `tabHostel Room`
            WHERE status != 'Under Maintenance'
            GROUP BY hostel_building
        ) stats ON stats.hostel_building = hb.name
        SET
            hb.total_rooms = stats.total_rooms,
            hb.total_capacity = stats.total_capacity,
            hb.occupied = stats.occupied,
            hb.available = stats.total_capacity - stats.occupied,
            hb.occupancy_rate = CASE WHEN stats.total_capacity > 0
                THEN ROUND(stats.occupied / stats.total_capacity * 100, 2)
                ELSE 0 END
    """)

    frappe.db.commit()
    return {"message": "Occupancy stats recalculated for all buildings"}


@frappe.whitelist()
def get_building_stats(building):
    """Get detailed building statistics"""
    doc = frappe.get_doc("Hostel Building", building)
    doc.update_capacity_stats()

    # Get room type distribution
    room_distribution = frappe.db.sql("""
        SELECT
            room_type,
            COUNT(*) as count,
            SUM(capacity) as total_beds,
            SUM(occupied_beds) as occupied
        FROM `tabHostel Room`
        WHERE hostel_building = %s
        GROUP BY room_type
    """, building, as_dict=True)

    return {
        "building": doc.name,
        "building_name": doc.building_name,
        "hostel_type": doc.hostel_type,
        "status": doc.status,
        "total_rooms": doc.total_rooms,
        "total_capacity": doc.total_capacity,
        "occupied": doc.occupied,
        "available": doc.available,
        "occupancy_rate": doc.occupancy_rate,
        "annual_fee": doc.annual_fee,
        "security_deposit": doc.security_deposit,
        "mess_fee_monthly": doc.mess_fee_monthly,
        "room_distribution": room_distribution,
        "warden": doc.warden,
        "contact_number": doc.contact_number
    }


@frappe.whitelist()
def get_building_occupancy(building=None):
    """Get occupancy statistics for a building or all buildings"""
    filters = {"status": "Active"}
    if building:
        filters["name"] = building

    return frappe.get_all(
        "Hostel Building",
        filters=filters,
        fields=[
            "name as building",
            "building_name",
            "hostel_type",
            "total_rooms",
            "total_capacity",
            "occupied",
            "available",
            "occupancy_rate",
            "annual_fee",
            "status"
        ],
        order_by="building_name"
    )


@frappe.whitelist()
def get_buildings_by_type(hostel_type):
    """Get buildings filtered by hostel type"""
    return frappe.get_all(
        "Hostel Building",
        filters={"hostel_type": hostel_type, "status": "Active"},
        fields=["name", "building_name", "total_capacity", "available", "annual_fee"]
    )


@frappe.whitelist()
def get_buildings_for_gender(gender):
    """Get buildings available for a specific gender"""
    if gender == "Male":
        hostel_types = ["Boys", "Co-Ed"]
    elif gender == "Female":
        hostel_types = ["Girls", "Co-Ed"]
    else:
        hostel_types = ["Co-Ed"]

    return frappe.get_all(
        "Hostel Building",
        filters={"hostel_type": ["in", hostel_types], "status": "Active"},
        fields=["name", "building_name", "hostel_type", "available", "annual_fee"]
    )

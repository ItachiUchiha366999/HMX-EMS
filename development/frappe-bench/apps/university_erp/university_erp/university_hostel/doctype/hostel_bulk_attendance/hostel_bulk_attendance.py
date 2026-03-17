# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowtime, getdate, today


class HostelBulkAttendance(Document):
    """Hostel Bulk Attendance for marking attendance of all residents in a building"""

    def validate(self):
        self.validate_duplicate()
        self.set_marking_time()
        self.update_summary()

    def validate_duplicate(self):
        """Check for duplicate attendance entry"""
        if self.is_new():
            existing = frappe.db.exists(
                "Hostel Bulk Attendance",
                {
                    "building": self.building,
                    "attendance_date": self.attendance_date,
                    "attendance_type": self.attendance_type,
                    "docstatus": ["!=", 2]
                }
            )
            if existing:
                frappe.throw(
                    _("Attendance for {0} on {1} ({2}) already exists: {3}").format(
                        self.building_name or self.building,
                        self.attendance_date,
                        self.attendance_type,
                        existing
                    )
                )

    def set_marking_time(self):
        """Set the marking time if not already set"""
        if not self.marking_time:
            self.marking_time = nowtime()

    def update_summary(self):
        """Update attendance summary counts"""
        self.total_residents = len(self.attendance_records) if self.attendance_records else 0
        self.present_count = 0
        self.absent_count = 0
        self.late_count = 0
        self.on_leave_count = 0
        self.out_pass_count = 0

        for record in self.attendance_records or []:
            if record.status == "Present":
                self.present_count += 1
            elif record.status == "Absent":
                self.absent_count += 1
            elif record.status == "Late":
                self.late_count += 1
            elif record.status == "On Leave":
                self.on_leave_count += 1
            elif record.status == "Out Pass":
                self.out_pass_count += 1

    def on_submit(self):
        """Actions on submit"""
        self.create_individual_attendance_records()
        if self.absent_count > 0:
            self.notify_absent_students()

    def create_individual_attendance_records(self):
        """Create individual Hostel Attendance records for each student"""
        for record in self.attendance_records:
            # Check if individual record exists
            existing = frappe.db.exists(
                "Hostel Attendance",
                {
                    "student": record.student,
                    "attendance_date": self.attendance_date,
                    "attendance_type": self.attendance_type
                }
            )
            if not existing:
                attendance = frappe.get_doc({
                    "doctype": "Hostel Attendance",
                    "student": record.student,
                    "attendance_date": self.attendance_date,
                    "attendance_type": self.attendance_type,
                    "status": record.status,
                    "room": record.room,
                    "in_time": record.in_time,
                    "out_time": record.out_time,
                    "remarks": record.remarks or f"Marked via bulk attendance {self.name}"
                })
                attendance.insert(ignore_permissions=True)

    def notify_absent_students(self):
        """Send notification for absent students"""
        absent_students = [
            r.student_name for r in self.attendance_records
            if r.status == "Absent"
        ]
        if absent_students:
            frappe.msgprint(
                _("{0} students marked absent. Consider sending notifications.").format(
                    len(absent_students)
                ),
                indicator="orange"
            )

    def on_cancel(self):
        """Actions on cancel"""
        # Optionally delete individual attendance records
        frappe.db.delete(
            "Hostel Attendance",
            {
                "remarks": ["like", f"%{self.name}%"],
                "docstatus": 0
            }
        )


@frappe.whitelist()
def get_residents_for_attendance(building, attendance_date=None):
    """Get all current residents of a building for attendance marking"""
    if not attendance_date:
        attendance_date = today()

    # Get all active allocations for the building
    residents = frappe.db.sql("""
        SELECT
            ha.student,
            s.student_name,
            ha.room,
            hr.room_number,
            hr.floor
        FROM `tabHostel Allocation` ha
        JOIN `tabStudent` s ON ha.student = s.name
        JOIN `tabHostel Room` hr ON ha.room = hr.name
        WHERE hr.hostel_building = %s
        AND ha.status = 'Active'
        AND ha.docstatus = 1
        AND ha.from_date <= %s
        AND (ha.to_date IS NULL OR ha.to_date >= %s)
        ORDER BY hr.floor, hr.room_number, s.student_name
    """, (building, attendance_date, attendance_date), as_dict=True)

    return residents


@frappe.whitelist()
def mark_bulk_attendance(building, attendance_date, attendance_type, records, remarks=None):
    """Create bulk attendance record"""
    import json
    if isinstance(records, str):
        records = json.loads(records)

    # Create bulk attendance document
    bulk_attendance = frappe.get_doc({
        "doctype": "Hostel Bulk Attendance",
        "building": building,
        "attendance_date": attendance_date,
        "attendance_type": attendance_type,
        "remarks": remarks,
        "attendance_records": records
    })

    bulk_attendance.insert()
    bulk_attendance.submit()

    return {
        "name": bulk_attendance.name,
        "total": bulk_attendance.total_residents,
        "present": bulk_attendance.present_count,
        "absent": bulk_attendance.absent_count
    }


@frappe.whitelist()
def get_attendance_status(building, attendance_date, attendance_type):
    """Check if attendance has been marked for a building"""
    existing = frappe.db.get_value(
        "Hostel Bulk Attendance",
        {
            "building": building,
            "attendance_date": attendance_date,
            "attendance_type": attendance_type,
            "docstatus": 1
        },
        ["name", "total_residents", "present_count", "absent_count", "marked_by", "marking_time"],
        as_dict=True
    )
    return existing


@frappe.whitelist()
def get_building_attendance_summary(building, from_date, to_date):
    """Get attendance summary for a building over a date range"""
    return frappe.db.sql("""
        SELECT
            attendance_date,
            attendance_type,
            total_residents,
            present_count,
            absent_count,
            late_count,
            on_leave_count,
            out_pass_count,
            ROUND((present_count + late_count) * 100.0 / NULLIF(total_residents, 0), 2) as attendance_percentage
        FROM `tabHostel Bulk Attendance`
        WHERE building = %s
        AND attendance_date BETWEEN %s AND %s
        AND docstatus = 1
        ORDER BY attendance_date DESC, attendance_type
    """, (building, from_date, to_date), as_dict=True)

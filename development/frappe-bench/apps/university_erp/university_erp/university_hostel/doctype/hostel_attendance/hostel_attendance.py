# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_time, time_diff_in_hours
import json


class HostelAttendance(Document):
    """Daily hostel attendance tracking"""

    def validate(self):
        self.validate_duplicate()
        self.set_room_details()
        self.check_late_entry()

    def validate_duplicate(self):
        """Prevent duplicate attendance"""
        existing = frappe.db.exists(
            "Hostel Attendance",
            {
                "student": self.student,
                "attendance_date": self.attendance_date,
                "name": ["!=", self.name or ""]
            }
        )
        if existing:
            frappe.throw(
                _("Attendance already marked for student {0} on {1}").format(
                    self.student_name, self.attendance_date
                )
            )

    def set_room_details(self):
        """Set room details from active allocation"""
        if not self.room:
            allocation = frappe.db.get_value(
                "Hostel Allocation",
                {
                    "student": self.student,
                    "hostel_building": self.hostel_building,
                    "status": "Active",
                    "docstatus": 1
                },
                "room"
            )
            if allocation:
                self.room = allocation

    def check_late_entry(self):
        """Check if entry time is late (after 10 PM)"""
        if self.in_time:
            in_time = get_time(self.in_time)
            curfew_time = get_time("22:00:00")  # 10 PM curfew
            if in_time > curfew_time:
                self.late_entry = 1
                if self.status == "Present":
                    self.status = "Late"


@frappe.whitelist()
def mark_bulk_attendance(hostel_building, attendance_date, students):
    """Mark attendance for multiple students"""
    if isinstance(students, str):
        students = json.loads(students)

    success_count = 0
    error_count = 0
    errors = []

    for student_data in students:
        try:
            # Check for existing attendance
            if frappe.db.exists("Hostel Attendance", {
                "student": student_data["student"],
                "attendance_date": attendance_date
            }):
                continue

            attendance = frappe.get_doc({
                "doctype": "Hostel Attendance",
                "student": student_data["student"],
                "hostel_building": hostel_building,
                "attendance_date": attendance_date,
                "status": student_data.get("status", "Present"),
                "in_time": student_data.get("in_time"),
                "out_time": student_data.get("out_time"),
                "remarks": student_data.get("remarks")
            })
            attendance.insert(ignore_permissions=True)
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append(f"{student_data.get('student')}: {str(e)}")

    frappe.db.commit()

    return {
        "message": _("Attendance marked for {0} students. {1} errors.").format(
            success_count, error_count
        ),
        "success": success_count,
        "errors": errors
    }


@frappe.whitelist()
def get_hostel_residents(hostel_building, attendance_date=None):
    """Get all active residents of a hostel building for attendance"""
    attendance_date = attendance_date or nowdate()

    residents = frappe.db.sql("""
        SELECT
            ha.student,
            s.student_name,
            ha.room,
            hr.room_number,
            (SELECT status FROM `tabHostel Attendance` hatt
             WHERE hatt.student = ha.student
             AND hatt.attendance_date = %s) as attendance_status
        FROM `tabHostel Allocation` ha
        JOIN `tabStudent` s ON ha.student = s.name
        JOIN `tabHostel Room` hr ON ha.room = hr.name
        WHERE ha.hostel_building = %s
        AND ha.status = 'Active'
        AND ha.docstatus = 1
        ORDER BY hr.room_number, s.student_name
    """, (attendance_date, hostel_building), as_dict=True)

    return residents


@frappe.whitelist()
def get_attendance_summary(hostel_building, from_date, to_date):
    """Get attendance summary for a hostel building"""
    return frappe.db.sql("""
        SELECT
            attendance_date,
            COUNT(CASE WHEN status = 'Present' THEN 1 END) as present,
            COUNT(CASE WHEN status = 'Absent' THEN 1 END) as absent,
            COUNT(CASE WHEN status = 'Late' THEN 1 END) as late,
            COUNT(CASE WHEN status = 'On Leave' THEN 1 END) as on_leave,
            COUNT(*) as total
        FROM `tabHostel Attendance`
        WHERE hostel_building = %s
        AND attendance_date BETWEEN %s AND %s
        GROUP BY attendance_date
        ORDER BY attendance_date DESC
    """, (hostel_building, from_date, to_date), as_dict=True)


@frappe.whitelist()
def get_student_attendance_history(student, from_date=None, to_date=None):
    """Get attendance history for a student"""
    conditions = ["student = %s"]
    values = [student]

    if from_date:
        conditions.append("attendance_date >= %s")
        values.append(from_date)

    if to_date:
        conditions.append("attendance_date <= %s")
        values.append(to_date)

    where_clause = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            attendance_date,
            status,
            in_time,
            out_time,
            late_entry,
            remarks
        FROM `tabHostel Attendance`
        WHERE {where_clause}
        ORDER BY attendance_date DESC
    """.format(where_clause=where_clause), values, as_dict=True)

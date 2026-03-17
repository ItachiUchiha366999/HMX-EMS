# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns(filters):
    columns = [
        {
            "fieldname": "student",
            "label": _("Student"),
            "fieldtype": "Link",
            "options": "Student",
            "width": 120
        },
        {
            "fieldname": "student_name",
            "label": _("Student Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "room",
            "label": _("Room"),
            "fieldtype": "Link",
            "options": "Hostel Room",
            "width": 100
        }
    ]

    # Add date columns if date range is provided
    if filters.get("from_date") and filters.get("to_date"):
        from_date = getdate(filters.get("from_date"))
        to_date = getdate(filters.get("to_date"))

        current_date = from_date
        while current_date <= to_date:
            columns.append({
                "fieldname": current_date.strftime("%Y-%m-%d"),
                "label": current_date.strftime("%d/%m"),
                "fieldtype": "Data",
                "width": 60
            })
            current_date = add_days(current_date, 1)

    columns.extend([
        {
            "fieldname": "present_days",
            "label": _("Present"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "absent_days",
            "label": _("Absent"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "late_days",
            "label": _("Late"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "attendance_percentage",
            "label": _("Attendance %"),
            "fieldtype": "Percent",
            "width": 100
        }
    ])

    return columns


def get_data(filters):
    conditions = []
    values = []

    if filters.get("hostel_building"):
        conditions.append("ha.hostel_building = %s")
        values.append(filters.get("hostel_building"))

    if filters.get("from_date"):
        conditions.append("hatt.attendance_date >= %s")
        values.append(filters.get("from_date"))

    if filters.get("to_date"):
        conditions.append("hatt.attendance_date <= %s")
        values.append(filters.get("to_date"))

    if filters.get("student"):
        conditions.append("ha.student = %s")
        values.append(filters.get("student"))

    where_clause = "WHERE ha.status = 'Active' AND ha.docstatus = 1"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    # Get all students with active allocations
    students = frappe.db.sql(f"""
        SELECT DISTINCT
            ha.student,
            s.student_name,
            ha.room,
            ha.hostel_building
        FROM `tabHostel Allocation` ha
        JOIN `tabStudent` s ON ha.student = s.name
        LEFT JOIN `tabHostel Attendance` hatt ON ha.student = hatt.student
        {where_clause}
        ORDER BY ha.room, s.student_name
    """, values, as_dict=True)

    # Get attendance data for each student
    from_date = getdate(filters.get("from_date")) if filters.get("from_date") else None
    to_date = getdate(filters.get("to_date")) if filters.get("to_date") else None

    data = []
    for student in students:
        row = {
            "student": student.student,
            "student_name": student.student_name,
            "room": student.room
        }

        # Get attendance records
        attendance_records = frappe.db.sql("""
            SELECT attendance_date, status
            FROM `tabHostel Attendance`
            WHERE student = %s
            AND attendance_date BETWEEN %s AND %s
        """, (student.student, from_date, to_date), as_dict=True)

        attendance_map = {str(a.attendance_date): a.status for a in attendance_records}

        present = 0
        absent = 0
        late = 0
        total_days = 0

        if from_date and to_date:
            current_date = from_date
            while current_date <= to_date:
                date_str = current_date.strftime("%Y-%m-%d")
                status = attendance_map.get(date_str, "")

                if status == "Present":
                    row[date_str] = "P"
                    present += 1
                elif status == "Absent":
                    row[date_str] = "A"
                    absent += 1
                elif status == "Late":
                    row[date_str] = "L"
                    late += 1
                elif status == "On Leave":
                    row[date_str] = "OL"
                else:
                    row[date_str] = "-"

                total_days += 1
                current_date = add_days(current_date, 1)

        row["present_days"] = present
        row["absent_days"] = absent
        row["late_days"] = late
        row["attendance_percentage"] = round(
            (present + late) / total_days * 100, 2
        ) if total_days else 0

        data.append(row)

    return data


def get_chart(data, filters):
    if not data:
        return None

    # Aggregate by date
    if filters.get("from_date") and filters.get("to_date"):
        from_date = getdate(filters.get("from_date"))
        to_date = getdate(filters.get("to_date"))

        dates = []
        present_counts = []
        absent_counts = []

        current_date = from_date
        while current_date <= to_date:
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(current_date.strftime("%d/%m"))

            present = sum(1 for d in data if d.get(date_str) in ["P", "L"])
            absent = sum(1 for d in data if d.get(date_str) == "A")

            present_counts.append(present)
            absent_counts.append(absent)
            current_date = add_days(current_date, 1)

        return {
            "data": {
                "labels": dates,
                "datasets": [
                    {"name": _("Present"), "values": present_counts},
                    {"name": _("Absent"), "values": absent_counts}
                ]
            },
            "type": "line",
            "colors": ["#98d85b", "#fc4f51"]
        }

    return None


def get_summary(data):
    if not data:
        return []

    total_students = len(data)
    avg_attendance = sum(d.get("attendance_percentage", 0) for d in data) / total_students if total_students else 0
    low_attendance = sum(1 for d in data if d.get("attendance_percentage", 0) < 75)

    return [
        {
            "value": total_students,
            "label": _("Total Students"),
            "datatype": "Int"
        },
        {
            "value": round(avg_attendance, 2),
            "label": _("Avg Attendance %"),
            "datatype": "Percent"
        },
        {
            "value": low_attendance,
            "label": _("Low Attendance (<75%)"),
            "datatype": "Int",
            "indicator": "red" if low_attendance > 0 else "green"
        }
    ]

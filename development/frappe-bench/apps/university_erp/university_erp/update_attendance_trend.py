#!/usr/bin/env python3
"""Update attendance records to create a realistic trend for dashboard"""

import frappe
from frappe.utils import add_months, nowdate, getdate, add_days
import random


def run():
    frappe.set_user("Administrator")

    print("=" * 70)
    print("UPDATING ATTENDANCE TREND FOR DASHBOARD")
    print("=" * 70)

    student_name = "EDU-STU-2026-00002"

    # Get student
    student = frappe.get_doc("Student", student_name)
    print(f"\nStudent: {student.student_name} ({student.name})")

    # Delete existing attendance records
    print("\nDeleting existing attendance records...")
    frappe.db.sql("""
        DELETE FROM `tabStudent Attendance`
        WHERE student = %s
    """, student_name)
    frappe.db.commit()
    print("✅ Cleared old attendance records")

    # Get student's course schedules
    student_groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student_name, "active": 1},
        pluck="parent"
    )

    schedules = []
    for sg_name in student_groups:
        sg_schedules = frappe.get_all(
            "Course Schedule",
            filters={"student_group": sg_name},
            fields=["name", "course", "schedule_date"],
            order_by="schedule_date desc",
            limit=200
        )
        schedules.extend(sg_schedules)

    print(f"\nFound {len(schedules)} course schedules")

    # Create attendance records with a trend
    # Recent months: 90% attendance
    # 2 months ago: 88% attendance
    # 3 months ago: 85% attendance
    # 4 months ago: 87% attendance
    # 5 months ago: 82% attendance

    today = getdate(nowdate())

    attendance_patterns = {
        0: 0.92,   # Current month - 92%
        -1: 0.90,  # Last month - 90%
        -2: 0.88,  # 2 months ago - 88%
        -3: 0.85,  # 3 months ago - 85%
        -4: 0.87,  # 4 months ago - 87%
        -5: 0.82,  # 5 months ago - 82%
    }

    created_count = 0
    status_summary = {"Present": 0, "Absent": 0}

    for schedule in schedules:
        if not schedule.schedule_date:
            continue

        schedule_date = getdate(schedule.schedule_date)

        # Calculate months difference
        months_diff = (today.year - schedule_date.year) * 12 + (today.month - schedule_date.month)

        # Skip if older than 5 months
        if months_diff > 5:
            continue

        # Get attendance probability for this month
        attendance_rate = attendance_patterns.get(-months_diff, 0.85)

        # Determine status based on probability
        status = "Present" if random.random() < attendance_rate else "Absent"

        try:
            # Check if attendance already exists
            existing = frappe.db.exists("Student Attendance", {
                "student": student_name,
                "course_schedule": schedule.name
            })

            if not existing:
                attendance = frappe.get_doc({
                    "doctype": "Student Attendance",
                    "student": student_name,
                    "course_schedule": schedule.name,
                    "course": schedule.course,
                    "date": schedule.schedule_date,
                    "status": status
                })
                attendance.insert(ignore_permissions=True)
                attendance.submit()
                created_count += 1
                status_summary[status] += 1

        except Exception as e:
            print(f"  ⚠️  Error creating attendance for {schedule.schedule_date}: {str(e)}")
            continue

    frappe.db.commit()

    # Calculate overall percentage
    total = status_summary["Present"] + status_summary["Absent"]
    percentage = (status_summary["Present"] / total * 100) if total > 0 else 0

    print(f"\n✅ Created {created_count} attendance records")
    print(f"\n📊 Attendance Summary:")
    print(f"   Present: {status_summary['Present']}")
    print(f"   Absent: {status_summary['Absent']}")
    print(f"   Total: {total}")
    print(f"   Percentage: {percentage:.1f}%")

    # Show monthly breakdown
    print(f"\n📅 Monthly Breakdown:")

    for months_back in range(6):
        target_date = add_months(today, -months_back)

        monthly_records = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
            FROM `tabStudent Attendance`
            WHERE student = %s
            AND MONTH(date) = %s
            AND YEAR(date) = %s
        """, (student_name, target_date.month, target_date.year), as_dict=1)

        if monthly_records and monthly_records[0].total > 0:
            rec = monthly_records[0]
            month_pct = (rec.present / rec.total * 100) if rec.total > 0 else 0
            month_name = target_date.strftime("%B %Y")
            print(f"   {month_name}: {month_pct:.1f}% ({rec.present}/{rec.total})")

    print("\n" + "=" * 70)
    print("✅ ATTENDANCE TREND UPDATED SUCCESSFULLY!")
    print("=" * 70)

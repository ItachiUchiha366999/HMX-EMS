#!/usr/bin/env python3
"""
Create 120 days of Student Attendance records for trend chart
"""

import frappe
from frappe.utils import getdate, add_days, nowdate
from datetime import datetime, timedelta

def create_attendance_records():
    """Create attendance records for last 120 days"""

    frappe.init(site="university.local")
    frappe.connect()
    frappe.set_user("Administrator")

    print("=" * 70)
    print("CREATING FULL ATTENDANCE HISTORY")
    print("=" * 70)

    student_name = "EDU-STU-2026-00002"
    today = getdate(nowdate())

    # Get student group
    student_groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student_name, "active": 1},
        fields=["parent"]
    )

    if not student_groups:
        print("❌ No student groups found!")
        return

    student_group = student_groups[0].parent
    print(f"\n✓ Using Student Group: {student_group}")

    # Create attendance for last 120 days (4 months)
    start_date = add_days(today, -120)
    print(f"\n📅 Creating attendance from {start_date} to {today}...")

    total_created = 0
    present_count = 0
    absent_count = 0

    # Create daily attendance for 120 days
    for day_offset in range(120):
        date = add_days(start_date, day_offset)

        # Skip weekends (Saturday=5, Sunday=6)
        weekday = date.weekday()
        if weekday >= 5:
            continue

        # 90% attendance: absent on every 10th record
        status = "Absent" if day_offset % 10 == 9 else "Present"

        try:
            att = frappe.get_doc({
                "doctype": "Student Attendance",
                "student": student_name,
                "student_group": student_group,
                "date": date,
                "status": status
            })
            att.insert(ignore_permissions=True)
            total_created += 1

            if status == "Present":
                present_count += 1
            else:
                absent_count += 1

            # Print progress every 20 records
            if total_created % 20 == 0:
                print(f"  Created {total_created} records...")

        except Exception as e:
            error_msg = str(e)
            if "duplicate" not in error_msg.lower():
                print(f"  ⚠️ Error on {date}: {error_msg[:60]}")

    frappe.db.commit()

    # Final statistics
    percentage = round((present_count / total_created) * 100, 1) if total_created > 0 else 0

    print("\n" + "=" * 70)
    print("ATTENDANCE CREATION COMPLETE")
    print("=" * 70)
    print(f"  ✅ Total Records: {total_created}")
    print(f"  ✅ Present: {present_count}")
    print(f"  ✅ Absent: {absent_count}")
    print(f"  ✅ Attendance %: {percentage}%")
    print(f"  ✅ Date Range: {start_date} to {today}")


if __name__ == "__main__":
    create_attendance_records()

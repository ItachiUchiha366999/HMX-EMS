#!/usr/bin/env python3
"""Test student portal dashboard context"""

import frappe


def run():
    frappe.set_user("student@test.edu")

    print("=" * 70)
    print("TESTING DASHBOARD CONTEXT")
    print("=" * 70)

    from university_erp.www.student_portal.index import get_context

    ctx = frappe._dict()
    get_context(ctx)

    print(f"\nStudent: {ctx.student.student_name}")
    print(f"Program: {ctx.student.get('program', 'Not set')}")
    print(f"CGPA: {ctx.student.get('custom_cgpa', 'Not set')}")

    print(f"\n📊 Dashboard Data:")
    if ctx.get('dashboard'):
        print(f"  Attendance: {ctx.dashboard.get('attendance_percentage', 0)}%")
        print(f"  CGPA: {ctx.dashboard.get('current_cgpa', 0)}")
        print(f"  Pending Assignments: {ctx.dashboard.get('pending_assignments', 0)}")
        print(f"  Upcoming Exams: {ctx.dashboard.get('upcoming_exams', 0)}")
        print(f"  Issued Books: {ctx.dashboard.get('issued_books', 0)}")
        print(f"  Pending Fees: Rs. {ctx.dashboard.get('pending_fees', 0)}")
    else:
        print("  No dashboard data")

    print(f"\n📅 Today's Classes: {len(ctx.get('today_classes', []))}")
    for cls in ctx.get('today_classes', [])[:3]:
        print(f"  - {cls.get('course_name', 'Unknown Course')}")
        print(f"    Time: {cls.get('from_time')} - {cls.get('to_time')}")
        print(f"    Room: {cls.get('room', 'TBA')}")

    print(f"\n📈 Attendance Trend: {len(ctx.get('attendance_trend', []))} months")
    for month_data in ctx.get('attendance_trend', []):
        print(f"  {month_data.get('month')}: {month_data.get('percentage')}% ({month_data.get('present')}/{month_data.get('total')})")

    print("\n" + "=" * 70)

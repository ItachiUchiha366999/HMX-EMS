#!/usr/bin/env python3
"""Test portal pages loading"""

import frappe


def run():
    frappe.set_user("student@test.edu")

    print("=" * 70)
    print("TESTING PORTAL PAGES")
    print("=" * 70)

    # Test 1: Dashboard
    print("\n[1/6] Testing Dashboard...")
    try:
        from university_erp.www.student_portal.index import get_context
        ctx = frappe._dict()
        get_context(ctx)
        print(f"  ✅ Dashboard loaded")
        print(f"      Student: {ctx.get('student', {}).get('first_name', 'N/A')}")
        print(f"      Stats: {ctx.get('stats', {})}")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:100]}")

    # Test 2: Academics
    print("\n[2/6] Testing Academics...")
    try:
        from university_erp.www.student_portal.academics import get_context
        ctx = frappe._dict()
        get_context(ctx)
        print(f"  ✅ Academics loaded")
        print(f"      Enrollments: {len(ctx.get('enrollments', []))}")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:100]}")

    # Test 3: Attendance
    print("\n[3/6] Testing Attendance...")
    try:
        from university_erp.www.student_portal.attendance import get_context
        ctx = frappe._dict()
        get_context(ctx)
        print(f"  ✅ Attendance loaded")
        print(f"      Chart data: {len(ctx.get('chart_data', {}).get('datasets', [{}])[0].get('values', []))} points")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:100]}")

    # Test 4: Timetable
    print("\n[4/6] Testing Timetable...")
    try:
        from university_erp.www.student_portal.timetable import get_context
        ctx = frappe._dict()
        get_context(ctx)
        print(f"  ✅ Timetable loaded")
        print(f"      Days with classes: {len(ctx.get('timetable', {}))}")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:100]}")

    # Test 5: Assignments
    print("\n[5/6] Testing Assignments...")
    try:
        from university_erp.www.student_portal.assignments import get_context
        ctx = frappe._dict()
        get_context(ctx)
        print(f"  ✅ Assignments loaded")
        print(f"      Assignments: {len(ctx.get('assignments', []))}")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:100]}")

    # Test 6: Examinations
    print("\n[6/6] Testing Examinations...")
    try:
        from university_erp.www.student_portal.exams import get_context
        ctx = frappe._dict()
        get_context(ctx)
        print(f"  ✅ Examinations loaded")
        print(f"      Exams: {len(ctx.get('exams', []))}")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:100]}")

    # Check timetable data
    print("\n" + "=" * 70)
    print("TIMETABLE DETAILS")
    print("=" * 70)
    try:
        from frappe.utils import getdate, nowdate
        from university_erp.www.student_portal.timetable import get_weekly_timetable, get_week_days

        student = frappe.db.get_value("Student", {"user": "student@test.edu"}, "name")
        week_start = getdate(nowdate())

        timetable = get_weekly_timetable(student, week_start)
        days = get_week_days(week_start)

        print(f"\nWeek starting: {week_start}")
        print(f"Days: {len(days)}")
        print(f"Days with classes: {list(timetable.keys())}")

        for day_name, classes in timetable.items():
            print(f"\n{day_name}: {len(classes)} classes")
            for cls in classes[:2]:
                print(f"  - {cls.get('course', 'N/A')} at {cls.get('from_time', 'N/A')}")

    except Exception as e:
        print(f"⚠️  Error: {str(e)[:150]}")

    print("\n" + "=" * 70)
    print("✅ PORTAL PAGES TEST COMPLETE")
    print("=" * 70)

#!/usr/bin/env python3
"""Test exams page context"""

import frappe


def run():
    frappe.set_user("student@test.edu")

    print("=" * 70)
    print("TESTING EXAMS PAGE CONTEXT")
    print("=" * 70)

    from university_erp.www.student_portal.exams import get_context

    ctx = frappe._dict()
    get_context(ctx)

    print(f"\nStudent: {ctx.student.student_name}")
    print(f"Active page: {ctx.active_page}")

    print(f"\nStats:")
    print(f"  Upcoming: {ctx.stats['upcoming']}")
    print(f"  Completed: {ctx.stats['completed']}")
    print(f"  Total: {ctx.stats['total']}")

    print(f"\nUpcoming exams: {len(ctx.upcoming_exams)}")
    for exam in ctx.upcoming_exams[:5]:
        print(f"  - {exam.course_name}: {exam.schedule_date} at {exam.from_time}")
        print(f"    Type: {exam.exam_type}")
        print(f"    Room: {exam.room}")
        print(f"    Countdown: {exam.countdown_text}")

    print(f"\nCompleted exams: {len(ctx.completed_exams)}")

    print("\n" + "=" * 70)

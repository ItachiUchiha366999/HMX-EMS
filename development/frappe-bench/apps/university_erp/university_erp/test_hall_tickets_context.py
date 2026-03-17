#!/usr/bin/env python3
"""Test hall tickets in exams page context"""

import frappe


def run():
    frappe.set_user("student@test.edu")

    print("=" * 70)
    print("TESTING HALL TICKETS IN EXAMS PAGE")
    print("=" * 70)

    from university_erp.www.student_portal.exams import get_context

    ctx = frappe._dict()
    get_context(ctx)

    print(f"\nStudent: {ctx.student.student_name}")
    print(f"Active page: {ctx.active_page}")

    print(f"\nStats:")
    print(f"  Upcoming exams: {ctx.stats['upcoming']}")
    print(f"  Completed exams: {ctx.stats['completed']}")
    print(f"  Hall tickets: {ctx.stats.get('hall_tickets', 0)}")
    print(f"  Total exams: {ctx.stats['total']}")

    print(f"\nHall Tickets: {len(ctx.hall_tickets)}")
    for ticket in ctx.hall_tickets:
        print(f"\n  Ticket: {ticket.name}")
        print(f"  Student: {ticket.student_name}")
        print(f"  Enrollment: {ticket.enrollment_number}")
        print(f"  Term: {ticket.term_name}")
        print(f"  Exam Type: {ticket.exam_type}")
        print(f"  Issue Date: {ticket.issue_date}")
        print(f"  Verification: {ticket.verification_code}")
        print(f"  Eligible: {'Yes' if ticket.is_eligible else 'No'}")
        if ticket.ineligibility_reason:
            print(f"  Reason: {ticket.ineligibility_reason}")

        print(f"\n  Exams in ticket: {len(ticket.exams)}")
        for exam in ticket.exams:
            print(f"    - {exam.course_name}")
            print(f"      Date: {exam.exam_date}")
            print(f"      Time: {exam.exam_time}")
            print(f"      Venue: {exam.venue}")

    print("\n" + "=" * 70)

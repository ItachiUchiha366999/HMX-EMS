#!/usr/bin/env python3
"""Test hall ticket download functionality"""

import frappe


def run():
    frappe.set_user("student@test.edu")

    print("=" * 70)
    print("TESTING HALL TICKET DOWNLOAD")
    print("=" * 70)

    # Get student
    student = frappe.db.get_value("Student", {"user": "student@test.edu"}, "name")
    print(f"\nStudent: {student}")

    # Get hall ticket
    hall_ticket = frappe.db.get_value(
        "Hall Ticket",
        {"student": student, "docstatus": 1},
        "name"
    )

    if not hall_ticket:
        print("❌ No hall ticket found!")
        return

    print(f"Hall Ticket: {hall_ticket}")

    # Try to get the document
    try:
        ticket_doc = frappe.get_doc("Hall Ticket", hall_ticket)
        print(f"\n✅ Hall Ticket document loaded")
        print(f"   Student: {ticket_doc.student_name}")
        print(f"   Eligible: {ticket_doc.is_eligible}")
        print(f"   Exams: {len(ticket_doc.exams)}")
    except Exception as e:
        print(f"❌ Error loading hall ticket: {str(e)}")
        return

    # Test download function
    print("\nTesting download function...")
    try:
        from university_erp.www.student_portal.exams import download_hall_ticket

        # This should work or give us a specific error
        frappe.local.response = frappe._dict()
        download_hall_ticket(hall_ticket)

        print(f"✅ Download function executed")
        print(f"   Response type: {frappe.local.response.get('type')}")
        print(f"   Filename: {frappe.local.response.get('filename')}")

        if frappe.local.response.get('filecontent'):
            print(f"   PDF size: {len(frappe.local.response.get('filecontent'))} bytes")

    except Exception as e:
        print(f"❌ Error in download function: {str(e)}")
        import traceback
        traceback.print_exc()

    print("=" * 70)

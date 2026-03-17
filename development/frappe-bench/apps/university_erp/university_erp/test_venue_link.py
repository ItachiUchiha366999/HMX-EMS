#!/usr/bin/env python3
"""Test if Venue can be accessed"""

import frappe


def run():
    frappe.set_user("Administrator")

    print("=" * 70)
    print("TESTING VENUE ACCESS")
    print("=" * 70)

    # Check if Venue DocType exists
    venue_doctype_exists = frappe.db.exists("DocType", "Venue")
    print(f"\nVenue DocType exists: {venue_doctype_exists}")

    # Check if we can get the venue
    try:
        venue = frappe.get_doc("Venue", "Exam Hall 1")
        print(f"✅ Got venue: {venue.name}")
        print(f"   Venue Name: {venue.venue_name}")
        print(f"   Room: {venue.room}")
    except Exception as e:
        print(f"⚠️  Cannot get venue: {str(e)}")

    # Check if the Venue DocType is properly set up
    try:
        meta = frappe.get_meta("Venue")
        print(f"\n✅ Venue meta loaded")
        print(f"   Is custom: {meta.custom}")
        print(f"   Module: {meta.module}")
        print(f"   Fields: {[f.fieldname for f in meta.fields]}")
    except Exception as e:
        print(f"\n⚠️  Cannot get meta: {str(e)}")

    # Try to validate Venue as a link
    try:
        from frappe.model.document import Document
        test_doc = frappe._dict({
            "doctype": "Exam Schedule",
            "venue": "Exam Hall 1"
        })

        # Check if the venue exists in database
        venue_check = frappe.db.exists("Venue", "Exam Hall 1")
        print(f"\n✅ Venue exists in DB: {venue_check}")

        # Get the actual record
        venue_record = frappe.db.get_value("Venue", "Exam Hall 1", ["name", "venue_name"], as_dict=True)
        print(f"   Record: {venue_record}")

    except Exception as e:
        print(f"\n⚠️  Link validation issue: {str(e)}")

    print("\n" + "=" * 70)

#!/usr/bin/env python3
"""Update test student's CGPA"""

import frappe


def run():
    frappe.set_user("Administrator")

    print("=" * 70)
    print("UPDATING STUDENT CGPA")
    print("=" * 70)

    # Get test student
    student_name = "EDU-STU-2026-00002"

    student = frappe.get_doc("Student", student_name)
    print(f"\nStudent: {student.student_name} ({student.name})")
    print(f"Current CGPA: {student.get('custom_cgpa') or 'Not set'}")

    # Update CGPA
    new_cgpa = 8.75

    # Check if custom_cgpa field exists
    meta = frappe.get_meta("Student")
    has_cgpa_field = any(f.fieldname == "custom_cgpa" for f in meta.fields)

    if has_cgpa_field:
        student.custom_cgpa = new_cgpa
        student.save(ignore_permissions=True)
        frappe.db.commit()

        print(f"✅ Updated CGPA to: {new_cgpa}")
    else:
        # Field doesn't exist, add it via custom field
        print("\n⚠️  custom_cgpa field not found, creating it...")

        if not frappe.db.exists("Custom Field", {"dt": "Student", "fieldname": "custom_cgpa"}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Student",
                "fieldname": "custom_cgpa",
                "label": "CGPA",
                "fieldtype": "Float",
                "insert_after": "student_name",
                "precision": "2",
                "description": "Cumulative Grade Point Average"
            })
            custom_field.insert(ignore_permissions=True)
            print("✅ Created custom_cgpa field")

        # Now update the value
        frappe.db.set_value("Student", student_name, "custom_cgpa", new_cgpa)
        frappe.db.commit()
        print(f"✅ Updated CGPA to: {new_cgpa}")

    # Verify
    updated_cgpa = frappe.db.get_value("Student", student_name, "custom_cgpa")
    print(f"\n✅ Verified CGPA: {updated_cgpa}")

    print("=" * 70)

#!/usr/bin/env python3
"""Add Student role permission to Hall Ticket DocType"""

import frappe


def run():
    frappe.set_user("Administrator")

    print("=" * 70)
    print("ADDING STUDENT PERMISSION TO HALL TICKET")
    print("=" * 70)

    # Check existing permissions
    existing_perms = frappe.db.sql("""
        SELECT role, `read`, `print`, `email`
        FROM `tabCustom DocPerm`
        WHERE parent = 'Hall Ticket'
        AND role = 'Student'
    """, as_dict=1)

    if existing_perms:
        print("\n✓ Student permission already exists:")
        for perm in existing_perms:
            print(f"  Role: {perm.role}")
            print(f"  Read: {perm.read}")
            print(f"  Print: {perm['print']}")
            print(f"  Email: {perm.email}")
    else:
        print("\nAdding Student role permission...")

        # Create Custom DocPerm for Student role
        perm = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": "Hall Ticket",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": "Student",
            "read": 1,
            "print": 1,
            "email": 1,
            "export": 1,
            "permlevel": 0,
            "if_owner": 1  # Only allow students to access their own hall tickets
        })

        try:
            perm.insert(ignore_permissions=True)
            frappe.db.commit()
            print("✅ Student permission added successfully")
        except Exception as e:
            print(f"❌ Error adding permission: {str(e)}")
            import traceback
            traceback.print_exc()

    # Clear permission cache
    frappe.clear_cache(doctype="Hall Ticket")

    print("\n" + "=" * 70)
    print("CURRENT HALL TICKET PERMISSIONS")
    print("=" * 70)

    # Show all permissions
    all_perms = frappe.db.sql("""
        SELECT role, `read`, `write`, `create`, `delete`, `print`, `email`, `if_owner`
        FROM `tabCustom DocPerm`
        WHERE parent = 'Hall Ticket'
        ORDER BY role
    """, as_dict=1)

    if not all_perms:
        # Check DocType permissions (non-custom)
        all_perms = frappe.db.sql("""
            SELECT role, `read`, `write`, `create`, `delete`, `print`, `email`, `if_owner`
            FROM `tabDocPerm`
            WHERE parent = 'Hall Ticket'
            ORDER BY role
        """, as_dict=1)
        print("\n(Showing DocType permissions - no custom permissions)")

    for perm in all_perms:
        print(f"\nRole: {perm.role}")
        print(f"  Read: {perm.read}, Print: {perm['print']}, Email: {perm.email}")
        if perm.if_owner:
            print(f"  If Owner: {perm.if_owner}")

    print("=" * 70)

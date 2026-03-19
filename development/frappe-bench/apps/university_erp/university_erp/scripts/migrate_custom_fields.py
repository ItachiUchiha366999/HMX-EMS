# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Custom Field Migration Script

Reads custom field fixture JSON files and creates/updates Custom Field records
in the database. This ensures that all custom fields defined in fixtures are
registered in the DB so that the corresponding columns exist on their parent
doctypes after `bench migrate`.

Usage:
    bench --site university.local execute university_erp.scripts.migrate_custom_fields.run
"""

import json
import os

import frappe


# Properties to copy from fixture JSON into Custom Field documents
FIELD_PROPERTIES = [
    "dt",
    "fieldname",
    "fieldtype",
    "label",
    "options",
    "insert_after",
    "default",
    "read_only",
    "precision",
    "depends_on",
]


def run():
    """Entry point for bench execute."""
    fixtures_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "faculty_management",
        "fixtures",
    )
    fixtures_dir = os.path.normpath(fixtures_dir)

    employee_count = _migrate_fixture(
        os.path.join(fixtures_dir, "employee_custom_fields.json")
    )
    leave_count = _migrate_fixture(
        os.path.join(fixtures_dir, "leave_application_custom_fields.json")
    )

    frappe.db.commit()
    print(
        f"Migrated {employee_count} Employee custom fields, "
        f"{leave_count} Leave Application custom fields"
    )


def _migrate_fixture(filepath):
    """Load a fixture JSON and create/update Custom Field records.

    Args:
        filepath: Absolute path to the fixture JSON file.

    Returns:
        int: Number of fields processed.
    """
    if not os.path.exists(filepath):
        print(f"WARNING: Fixture file not found: {filepath}")
        return 0

    with open(filepath, "r") as f:
        fields = json.load(f)

    count = 0
    for field_def in fields:
        name = field_def.get("name")
        if not name:
            continue

        if frappe.db.exists("Custom Field", name):
            # Update existing
            cf = frappe.get_doc("Custom Field", name)
            for prop in FIELD_PROPERTIES:
                if prop in field_def:
                    cf.set(prop, field_def[prop])
            cf.flags.ignore_permissions = True
            cf.save()
        else:
            # Create new
            cf = frappe.new_doc("Custom Field")
            cf.name = name
            for prop in FIELD_PROPERTIES:
                if prop in field_def:
                    cf.set(prop, field_def[prop])
            cf.flags.ignore_permissions = True
            cf.insert()

        count += 1

    return count

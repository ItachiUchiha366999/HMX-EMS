#!/usr/bin/env python3
"""Test if frappe has built-in format_time"""

import frappe


def run():
    frappe.set_user("Administrator")

    print("=" * 70)
    print("TESTING FRAPPE FORMAT_TIME")
    print("=" * 70)

    # Check if frappe.utils has format_time
    try:
        from frappe.utils import format_time
        print("\n✅ frappe.utils.format_time exists")

        # Test it
        test_time = "14:30:00"
        result = format_time(test_time)
        print(f"   format_time('{test_time}') = '{result}'")

        # Test with format string
        try:
            result_formatted = format_time(test_time, "h:mm a")
            print(f"   format_time('{test_time}', 'h:mm a') = '{result_formatted}'")
        except Exception as e:
            print(f"   ⚠️  With format string: {str(e)}")

    except ImportError:
        print("\n⚠️  frappe.utils.format_time does not exist")

    # Check frappe module
    print("\n" + "=" * 70)
    print("FRAPPE MODULE ATTRIBUTES")
    print("=" * 70)

    if hasattr(frappe, 'format_time'):
        print("✅ frappe.format_time exists")
    else:
        print("⚠️  frappe.format_time does NOT exist")

    if hasattr(frappe.utils, 'format_time'):
        print("✅ frappe.utils.format_time exists")
    else:
        print("⚠️  frappe.utils.format_time does NOT exist")

    print("=" * 70)

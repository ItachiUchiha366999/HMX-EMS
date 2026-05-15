"""Check Course Outcome status for Operating Systems."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Check COs for Operating Systems
    cos = frappe.db.sql(
        "SELECT name, co_code, status FROM `tabCourse Outcome` WHERE course='Operating Systems'",
        as_dict=True
    )
    print(f"COs for Operating Systems ({len(cos)} total):")
    for co in cos:
        print(f"  {co['name']}: code={co['co_code']}, status={co['status']}")

    # Check all COs - status distribution
    status_dist = frappe.db.sql(
        "SELECT status, COUNT(*) as cnt FROM `tabCourse Outcome` GROUP BY status",
        as_dict=True
    )
    print(f"\nAll CO status distribution: {status_dist}")

    # Check Program Outcome status
    po_status = frappe.db.sql(
        "SELECT status, COUNT(*) as cnt FROM `tabProgram Outcome` GROUP BY status",
        as_dict=True
    )
    print(f"PO status distribution: {po_status}")

    # CO PO Mapping Entry sample
    entries = frappe.db.sql(
        "SELECT course_outcome, program_outcome, correlation_level "
        "FROM `tabCO PO Mapping Entry` "
        "WHERE parent='Operating Systems-2026-2027 (Semester 2)-COPOMAP' LIMIT 6",
        as_dict=True
    )
    print(f"\nCO PO Mapping Entries sample: {entries}")

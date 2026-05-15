"""Verify placement data after fixes."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Placement Drive status
    drives = frappe.db.sql(
        "SELECT name, company, job_opening, academic_year, docstatus FROM `tabPlacement Drive` LIMIT 5",
        as_dict=True
    )
    print("Placement Drives:", drives)

    # Placement Application status
    apps = frappe.db.sql(
        "SELECT status, company, job_opening, offered_ctc, placement_drive FROM `tabPlacement Application` LIMIT 5",
        as_dict=True
    )
    print("Placement Apps sample:", apps)

    # Status distribution
    status_dist = frappe.db.sql(
        "SELECT status, COUNT(*) as cnt FROM `tabPlacement Application` GROUP BY status",
        as_dict=True
    )
    print("App status distribution:", status_dist)

    # Company distribution
    company_dist = frappe.db.sql(
        "SELECT company, COUNT(*) as cnt FROM `tabPlacement Application` WHERE company IS NOT NULL GROUP BY company ORDER BY cnt DESC LIMIT 5",
        as_dict=True
    )
    print("Company distribution:", company_dist)

    # Student.custom_program check
    prog_sample = frappe.db.sql(
        "SELECT custom_program, COUNT(*) as cnt FROM `tabStudent` WHERE custom_program IS NOT NULL GROUP BY custom_program LIMIT 5",
        as_dict=True
    )
    print("Student custom_program distribution:", prog_sample)

    # Placed students count
    placed = frappe.db.count("Placement Application", {"status": "Placed"})
    print(f"Total Placed applications: {placed}")

    # NAAC Metric check
    naac = frappe.db.sql(
        "SELECT COUNT(*) as cnt FROM `tabNAAC Metric`",
        as_dict=True
    )
    print("NAAC Metrics:", naac[0].cnt if naac else 0)

    # NIRF Data check
    nirf = frappe.db.sql(
        "SELECT COUNT(*) as cnt FROM `tabNIRF Data`",
        as_dict=True
    )
    print("NIRF Data rows:", nirf[0].cnt if nirf else 0)

    # Internal Assessment check
    ia = frappe.db.sql(
        "SELECT COUNT(*) as total, SUM(docstatus=1) as submitted, SUM(academic_term IS NOT NULL) as has_term "
        "FROM `tabInternal Assessment`",
        as_dict=True
    )
    print("Internal Assessment:", ia[0] if ia else {})

    # Internal Assessment Score check
    ias = frappe.db.sql(
        "SELECT COUNT(*) as cnt FROM `tabInternal Assessment Score`",
        as_dict=True
    )
    print("Internal Assessment Score rows:", ias[0].cnt if ias else 0)

    # CO PO Mapping check
    co_po = frappe.db.sql(
        "SELECT COUNT(*) as total, SUM(docstatus=1) as submitted FROM `tabCO PO Mapping`",
        as_dict=True
    )
    print("CO PO Mapping:", co_po[0] if co_po else {})

    # CO PO Mapping Entry check
    co_po_entry = frappe.db.sql(
        "SELECT COUNT(*) as cnt FROM `tabCO PO Mapping Entry`",
        as_dict=True
    )
    print("CO PO Mapping Entry rows:", co_po_entry[0].cnt if co_po_entry else 0)

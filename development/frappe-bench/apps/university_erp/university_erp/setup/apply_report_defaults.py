"""
Apply correct default filter values to all university_erp reports.
Run this on prod after deploying the updated JSON files.
Updates the Report doctype in DB to match the JSON filter definitions.
"""
import frappe
import json


def update_report_filters(report_name, filters_json):
    """Update a Report's filters in the DB."""
    if not frappe.db.exists("Report", report_name):
        print(f"  SKIP (not found): {report_name}")
        return False
    doc = frappe.get_doc("Report", report_name)
    doc.filters = json.dumps(filters_json)
    doc.db_update()
    print(f"  OK: {report_name} ({len(filters_json)} filters)")
    return True


def run():
    frappe.flags.ignore_permissions = True

    updates = 0

    # === OBE Reports ===
    updates += update_report_filters("CO Attainment Report", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "academic_term", "fieldtype": "Link", "label": "Academic Term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)", "mandatory": 0},
        {"fieldname": "course", "fieldtype": "Link", "label": "Course",
         "options": "Course", "mandatory": 0},
    ])

    updates += update_report_filters("CO-PO Mapping Matrix", [
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "default": "B.Tech Computer Science and Engineering", "mandatory": 0},
        {"fieldname": "course", "fieldtype": "Link", "label": "Course",
         "options": "Course", "default": "Operating Systems", "mandatory": 0},
        {"fieldname": "academic_term", "fieldtype": "Link", "label": "Academic Term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)", "mandatory": 0},
    ])

    updates += update_report_filters("Program Attainment Summary", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "mandatory": 0},
        {"fieldname": "department", "fieldtype": "Data", "label": "Department", "mandatory": 0},
    ])

    updates += update_report_filters("Survey Analysis Report", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "mandatory": 0},
        {"fieldname": "survey_type", "fieldtype": "Select", "label": "Survey Type",
         "options": "\nCourse End Survey\nProgram Exit Survey\nEmployer Survey\nAlumni Survey",
         "mandatory": 0},
    ])

    updates += update_report_filters("PO Attainment Report", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "mandatory": 0},
    ])

    updates += update_report_filters("NAAC Criterion Progress", [
        {"fieldname": "accreditation_cycle", "fieldtype": "Link", "label": "Accreditation Cycle",
         "options": "Accreditation Cycle", "mandatory": 0},
    ])

    updates += update_report_filters("NIRF Parameter Report", [
        {"fieldname": "ranking_year", "fieldtype": "Select", "label": "Ranking Year",
         "options": "\n2023\n2024\n2025\n2026", "default": "2026", "mandatory": 0},
        {"fieldname": "category", "fieldtype": "Select", "label": "Category",
         "options": "\nEngineering\nManagement", "default": "Engineering", "mandatory": 0},
    ])

    # === Examination Reports ===
    updates += update_report_filters("Internal Assessment Summary", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "academic_term", "fieldtype": "Link", "label": "Academic Term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)", "mandatory": 0},
        {"fieldname": "course", "fieldtype": "Link", "label": "Course",
         "options": "Course", "default": "Operations Management", "mandatory": 0},
    ])

    updates += update_report_filters("Examination Result Analysis", [
        {"fieldname": "academic_term", "fieldtype": "Link", "label": "Academic Term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)", "mandatory": 0},
        {"fieldname": "exam_type", "fieldtype": "Select", "label": "Exam Type",
         "options": "\nMid-Term\nEnd-Term\nPractical\nQuiz",
         "default": "Mid-Term", "mandatory": 0},
    ])

    # === Placement Reports ===
    updates += update_report_filters("Placement Statistics", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "mandatory": 0},
    ])

    updates += update_report_filters("Company Wise Placement", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "mandatory": 0},
    ])

    updates += update_report_filters("Program Wise Placement", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
    ])

    updates += update_report_filters("Placement Trend", [
        {"fieldname": "from_year", "fieldtype": "Link", "label": "From Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
    ])

    # === Library Reports ===
    updates += update_report_filters("Library Circulation", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
        {"fieldname": "transaction_type", "fieldtype": "Select", "label": "Transaction Type",
         "options": "\nIssue\nReturn\nRenew", "mandatory": 0},
    ])

    updates += update_report_filters("Library Collection", [
        {"fieldname": "category", "fieldtype": "Data", "label": "Category", "mandatory": 0},
    ])

    updates += update_report_filters("Overdue Books", [
        {"fieldname": "as_on_date", "fieldtype": "Date", "label": "As On Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Member Borrowing History", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    # === Hostel Reports ===
    updates += update_report_filters("Hostel Occupancy", [
        {"fieldname": "hostel_type", "fieldtype": "Select", "label": "Hostel Type",
         "options": "\nBoys\nGirls\nMixed", "mandatory": 0},
    ])

    updates += update_report_filters("Hostel Attendance Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 30", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Visitor Log", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 30", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Maintenance Summary", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Room Availability", [
        {"fieldname": "hostel_type", "fieldtype": "Select", "label": "Hostel Type",
         "options": "\nBoys\nGirls\nMixed", "mandatory": 0},
    ])

    # === Faculty Reports ===
    updates += update_report_filters("Faculty Directory", [
        {"fieldname": "department", "fieldtype": "Link", "label": "Department",
         "options": "Department", "mandatory": 0},
        {"fieldname": "designation", "fieldtype": "Link", "label": "Designation",
         "options": "Designation", "mandatory": 0},
    ])

    updates += update_report_filters("Faculty Workload Summary", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "academic_term", "fieldtype": "Link", "label": "Academic Term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)", "mandatory": 0},
    ])

    updates += update_report_filters("Department HR Summary", [
        {"fieldname": "department", "fieldtype": "Link", "label": "Department",
         "options": "Department", "mandatory": 0},
    ])

    updates += update_report_filters("Leave Utilization Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 365", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    # === Research Reports ===
    updates += update_report_filters("Faculty Research Output", [
        {"fieldname": "from_year", "fieldtype": "Int", "label": "From Year",
         "default": "2024", "mandatory": 0},
        {"fieldname": "to_year", "fieldtype": "Int", "label": "To Year",
         "default": "2026", "mandatory": 0},
        {"fieldname": "department", "fieldtype": "Link", "label": "Department",
         "options": "Department", "mandatory": 0},
    ])

    updates += update_report_filters("Publication Statistics", [
        {"fieldname": "year", "fieldtype": "Int", "label": "Year",
         "default": "2026", "mandatory": 0},
    ])

    updates += update_report_filters("Grant Utilization Report", [
        {"fieldname": "status", "fieldtype": "Select", "label": "Status",
         "options": "\nApproved\nCompleted\nRejected", "mandatory": 0},
    ])

    # === Finance Reports ===
    updates += update_report_filters("Fee Collection Summary", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
        {"fieldname": "program", "fieldtype": "Link", "label": "Program",
         "options": "Program", "mandatory": 0},
    ])

    updates += update_report_filters("Fee Defaulters", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
    ])

    updates += update_report_filters("Program-wise Fee Report", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
    ])

    updates += update_report_filters("Daily Collection Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 30", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    # === Communication / Integration Reports ===
    updates += update_report_filters("SMS Delivery Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 30", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status",
         "options": "\nSent\nFailed\nPending", "mandatory": 0},
    ])

    updates += update_report_filters("Payment Transaction Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 30", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Certificate Issuance Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    # === Inventory Reports ===
    updates += update_report_filters("Purchase Order Status", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Asset Register", [
        {"fieldname": "status", "fieldtype": "Select", "label": "Status",
         "options": "\nIn Location\nScrapped\nSold", "default": "In Location", "mandatory": 0},
    ])

    updates += update_report_filters("Lab Equipment Utilization", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    # === LMS Reports ===
    updates += update_report_filters("Course Progress", [
        {"fieldname": "course", "fieldtype": "Link", "label": "Course",
         "options": "LMS Course", "mandatory": 0},
    ])

    updates += update_report_filters("Quiz Analytics", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Assignment Submission Report", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    # === Transport Reports ===
    updates += update_report_filters("Route Wise Students", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
    ])

    updates += update_report_filters("Vehicle Utilization", [
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date",
         "default": "Today - 90", "mandatory": 0},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date",
         "default": "Today", "mandatory": 0},
    ])

    updates += update_report_filters("Transport Fee Collection", [
        {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year",
         "options": "Academic Year", "default": "2026-2027", "mandatory": 0},
    ])

    frappe.db.commit()
    print(f"\nTotal reports updated: {updates}")

"""
Fix report filters using Frappe v15's tabReport Filter child table.
Inserts filter rows with correct defaults so reports open with data.
"""
import frappe
import uuid


def set_report_filters(report_name, filters):
    """Replace all tabReport Filter rows for a report."""
    if not frappe.db.exists("Report", report_name):
        print(f"  SKIP (not found): {report_name}")
        return 0

    # Delete existing filter rows
    frappe.db.sql(
        "DELETE FROM `tabReport Filter` WHERE parent=%s",
        report_name
    )

    # Insert new filter rows
    for idx, f in enumerate(filters, 1):
        row_name = uuid.uuid4().hex[:10]
        frappe.db.sql("""
            INSERT INTO `tabReport Filter`
            (name, creation, modified, modified_by, owner, docstatus, idx,
             label, fieldtype, fieldname, mandatory, options, `default`,
             parent, parentfield, parenttype)
            VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator', 0, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, 'filters', 'Report')
        """, (
            row_name, idx,
            f.get('label', ''), f.get('fieldtype', 'Data'), f.get('fieldname', ''),
            1 if f.get('mandatory') else 0,
            f.get('options', ''),
            f.get('default', ''),
            report_name
        ))

    print(f"  OK: {report_name} ({len(filters)} filters)")
    return len(filters)


def run():
    frappe.flags.ignore_permissions = True
    total = 0

    # === OBE Reports ===
    total += set_report_filters("CO Attainment Report", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Academic Term", "fieldtype": "Link", "fieldname": "academic_term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)"},
        {"label": "Course", "fieldtype": "Link", "fieldname": "course",
         "options": "Course", "default": ""},
    ])

    total += set_report_filters("CO-PO Mapping Matrix", [
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": "B.Tech Computer Science and Engineering"},
        {"label": "Course", "fieldtype": "Link", "fieldname": "course",
         "options": "Course", "default": "Operating Systems"},
        {"label": "Academic Term", "fieldtype": "Link", "fieldname": "academic_term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)"},
    ])

    total += set_report_filters("Program Attainment Summary", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": ""},
        {"label": "Department", "fieldtype": "Data", "fieldname": "department", "default": ""},
    ])

    total += set_report_filters("Survey Analysis Report", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": ""},
        {"label": "Survey Type", "fieldtype": "Select", "fieldname": "survey_type",
         "options": "\nCourse End Survey\nProgram Exit Survey\nEmployer Survey\nAlumni Survey",
         "default": ""},
    ])

    total += set_report_filters("PO Attainment Report", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": ""},
    ])

    total += set_report_filters("NAAC Criterion Progress", [
        {"label": "Accreditation Cycle", "fieldtype": "Link", "fieldname": "accreditation_cycle",
         "options": "Accreditation Cycle", "default": ""},
    ])

    total += set_report_filters("NIRF Parameter Report", [
        {"label": "Ranking Year", "fieldtype": "Select", "fieldname": "ranking_year",
         "options": "\n2023\n2024\n2025\n2026", "default": "2026"},
        {"label": "Category", "fieldtype": "Select", "fieldname": "category",
         "options": "\nEngineering\nManagement", "default": "Engineering"},
    ])

    # === Examination Reports ===
    total += set_report_filters("Internal Assessment Summary", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Academic Term", "fieldtype": "Link", "fieldname": "academic_term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)"},
        {"label": "Course", "fieldtype": "Link", "fieldname": "course",
         "options": "Course", "default": "Operations Management"},
    ])

    total += set_report_filters("Examination Result Analysis", [
        {"label": "Academic Term", "fieldtype": "Link", "fieldname": "academic_term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)"},
        {"label": "Exam Type", "fieldtype": "Select", "fieldname": "exam_type",
         "options": "\nMid-Term\nEnd-Term\nPractical\nQuiz", "default": "Mid-Term"},
    ])

    # === Placement Reports ===
    total += set_report_filters("Placement Statistics", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": ""},
    ])

    total += set_report_filters("Company Wise Placement", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": ""},
    ])

    total += set_report_filters("Program Wise Placement", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
    ])

    total += set_report_filters("Placement Trend", [
        {"label": "From Year", "fieldtype": "Link", "fieldname": "from_year",
         "options": "Academic Year", "default": "2026-2027"},
    ])

    # === Library Reports ===
    total += set_report_filters("Library Circulation", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-02-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
        {"label": "Transaction Type", "fieldtype": "Select", "fieldname": "transaction_type",
         "options": "\nIssue\nReturn\nRenew", "default": ""},
    ])

    total += set_report_filters("Overdue Books", [
        {"label": "As On Date", "fieldtype": "Date", "fieldname": "as_on_date",
         "default": "2026-05-01"},
    ])

    total += set_report_filters("Member Borrowing History", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-02-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    # === Hostel Reports ===
    total += set_report_filters("Hostel Attendance Report", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-04-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    total += set_report_filters("Visitor Log", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-04-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    total += set_report_filters("Maintenance Summary", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-02-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    # === Faculty Reports ===
    total += set_report_filters("Faculty Workload Summary", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
        {"label": "Academic Term", "fieldtype": "Link", "fieldname": "academic_term",
         "options": "Academic Term", "default": "2026-2027 (Semester 2)"},
    ])

    total += set_report_filters("Leave Utilization Report", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-01-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    # === Research Reports ===
    total += set_report_filters("Faculty Research Output", [
        {"label": "From Year", "fieldtype": "Int", "fieldname": "from_year", "default": "2024"},
        {"label": "To Year", "fieldtype": "Int", "fieldname": "to_year", "default": "2026"},
        {"label": "Department", "fieldtype": "Link", "fieldname": "department",
         "options": "Department", "default": ""},
    ])

    total += set_report_filters("Publication Statistics", [
        {"label": "Year", "fieldtype": "Int", "fieldname": "year", "default": "2026"},
    ])

    # === Finance Reports ===
    total += set_report_filters("Fee Collection Summary", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-01-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
        {"label": "Program", "fieldtype": "Link", "fieldname": "program",
         "options": "Program", "default": ""},
    ])

    total += set_report_filters("Fee Defaulters", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
    ])

    total += set_report_filters("Daily Collection Report", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-04-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    # === Communication / Integration ===
    total += set_report_filters("SMS Delivery Report", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-04-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
        {"label": "Status", "fieldtype": "Select", "fieldname": "status",
         "options": "\nSent\nFailed\nPending", "default": ""},
    ])

    total += set_report_filters("Payment Transaction Report", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-04-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    # === Inventory ===
    total += set_report_filters("Purchase Order Status", [
        {"label": "From Date", "fieldtype": "Date", "fieldname": "from_date",
         "default": "2026-01-01"},
        {"label": "To Date", "fieldtype": "Date", "fieldname": "to_date",
         "default": "2026-05-01"},
    ])

    total += set_report_filters("Asset Register", [
        {"label": "Status", "fieldtype": "Select", "fieldname": "status",
         "options": "\nIn Location\nScrapped\nSold", "default": "In Location"},
    ])

    # === Transport ===
    total += set_report_filters("Route Wise Students", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
    ])

    total += set_report_filters("Transport Fee Collection", [
        {"label": "Academic Year", "fieldtype": "Link", "fieldname": "academic_year",
         "options": "Academic Year", "default": "2026-2027"},
    ])

    frappe.db.commit()
    print(f"\nTotal filter rows inserted: {total}")

    # Verify
    check = frappe.db.sql("""
        SELECT parent, COUNT(*) as cnt, GROUP_CONCAT(CONCAT(fieldname,'=',IFNULL(`default`,'')) ORDER BY idx SEPARATOR ', ') as defaults
        FROM `tabReport Filter`
        WHERE parent IN ('CO Attainment Report','CO-PO Mapping Matrix','Program Attainment Summary',
                         'Survey Analysis Report','Internal Assessment Summary','PO Attainment Report')
        GROUP BY parent
    """, as_dict=True)
    print("\nVerification:")
    for r in check:
        print(f"  {r['parent']}: {r['cnt']} filters — {r['defaults']}")

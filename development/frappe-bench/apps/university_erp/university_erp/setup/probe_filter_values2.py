"""Probe remaining filter values."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    print("=== Hostel Building cols ===")
    cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabHostel Building`", as_dict=True)]
    print("  cols:", cols)

    print("\n=== Hostel Buildings ===")
    hb = frappe.db.sql("SELECT name FROM `tabHostel Building` LIMIT 5", as_dict=True)
    print("  buildings:", [r['name'] for r in hb])

    print("\n=== Hostel Allocations ===")
    ha = frappe.db.sql(
        "SELECT ha.hostel_building, COUNT(*) as cnt FROM `tabHostel Allocation` ha WHERE ha.docstatus=1 GROUP BY ha.hostel_building ORDER BY cnt DESC LIMIT 3",
        as_dict=True
    )
    print("  allocations:", ha)

    print("\n=== Exam Schedule ===")
    es = frappe.db.sql("""
        SELECT es.name, es.exam_name, es.academic_year, es.academic_term,
               COUNT(sea.name) as attempts
        FROM `tabExam Schedule` es
        LEFT JOIN `tabStudent Exam Attempt` sea ON sea.exam_schedule = es.name
        WHERE es.docstatus = 1
        GROUP BY es.name ORDER BY attempts DESC LIMIT 3
    """, as_dict=True)
    for r in es:
        print(f"  exam={r['name']!r}, name={r['exam_name']!r}, ay={r['academic_year']!r}, term={r['academic_term']!r}, attempts={r['attempts']}")

    print("\n=== Library Transaction dates ===")
    lt = frappe.db.sql("""
        SELECT transaction_type, COUNT(*) as cnt,
               MIN(transaction_date) as min_d, MAX(transaction_date) as max_d
        FROM `tabLibrary Transaction` GROUP BY transaction_type
    """, as_dict=True)
    for r in lt:
        print(f"  type={r['transaction_type']!r}, cnt={r['cnt']}, min={r['min_d']}, max={r['max_d']}")

    print("\n=== Placement Drive fields ===")
    pd_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabPlacement Drive`", as_dict=True)]
    print("  cols:", pd_cols)

    print("\n=== Placement Stats Report ref_doctype ===")
    rep = frappe.db.get_value("Report", "Placement Statistics", ["ref_doctype", "report_type"], as_dict=True)
    print("  ref:", rep)

    print("\n=== CO Attainment Report filter logic ===")
    # What does the CO Attainment script filter on?
    # It filters `attainment_filters` = {docstatus:1, course, academic_term, academic_year}
    # So academic_year='2026-2027' + academic_term='2026-2027 (Semester 2)' should work
    test = frappe.get_all("CO Attainment",
        filters={"docstatus": 1, "academic_year": "2026-2027"},
        fields=["name", "course", "academic_term"]
    )
    print(f"  CO Attainment with ay=2026-2027: {len(test)} rows")
    for r in test[:3]:
        print(f"    {r['name']}: course={r['course']!r}, term={r['academic_term']!r}")

    print("\n=== PO Attainment Report JSON check ===")
    rep2 = frappe.db.sql(
        "SELECT name FROM `tabReport` WHERE name LIKE '%PO Attainment%'",
        as_dict=True
    )
    print("  reports:", [r['name'] for r in rep2])

    print("\n=== Course Progress report ref ===")
    cp = frappe.db.get_value("Report", "Course Progress", ["ref_doctype", "report_type"], as_dict=True)
    print("  ref:", cp)

    print("\n=== LMS Course Enrollment ===")
    lms = frappe.db.sql(
        "SELECT COUNT(*) as cnt FROM `tabLMS Enrollment`", as_dict=True
    )
    print("  LMS Enrollments:", lms[0].cnt if lms else 0)

    print("\n=== Feedback Form / Response ===")
    ff = frappe.db.sql("SELECT name FROM `tabFeedback Form` LIMIT 3", as_dict=True)
    print("  Feedback Forms:", [r['name'] for r in ff])

    print("\n=== Faculty Feedback Report ref ===")
    ffr = frappe.db.get_value("Report", "Faculty Feedback Report", ["ref_doctype", "report_type"], as_dict=True)
    print("  ref:", ffr)

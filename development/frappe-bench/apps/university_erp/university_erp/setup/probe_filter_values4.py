"""Probe report script filter logic by reading the Python files."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    reports = ["Placement Statistics", "Course Progress", "Faculty Feedback Report",
               "Hostel Occupancy", "Library Circulation", "Examination Result Analysis",
               "CO-PO Mapping Matrix", "PO Attainment Report", "CO Attainment Report",
               "Program Attainment Summary", "Survey Analysis Report",
               "Internal Assessment Summary", "Communication Analytics",
               "Faculty Research Output", "Faculty Directory", "SMS Delivery Report"]

    for rname in reports:
        r = frappe.db.get_value("Report", rname, ["ref_doctype", "report_type", "module"], as_dict=True)
        print(f"  {rname!r}: ref={r.get('ref_doctype') if r else None}, module={r.get('module') if r else None}")

    print("\n=== Student Exam Attempt links ===")
    sea = frappe.db.sql(
        "SELECT online_examination, COUNT(*) as cnt FROM `tabStudent Exam Attempt` GROUP BY online_examination ORDER BY cnt DESC LIMIT 3",
        as_dict=True
    )
    print("  by exam:", sea)

    print("\n=== Online Examination sample ===")
    oe = frappe.db.sql(
        "SELECT name, exam_name, academic_term, course FROM `tabOnline Examination` WHERE docstatus=1 LIMIT 3",
        as_dict=True
    )
    for r in oe:
        print(f"  {r['name']}: exam={r['exam_name']!r}, term={r['academic_term']!r}, course={r['course']!r}")

    print("\n=== Exam Schedule filter check ===")
    # Examination Result Analysis uses exam_schedule not exam_name
    es_attempt = frappe.db.sql(
        "SELECT exam_schedule, COUNT(*) as cnt FROM `tabStudent Exam Attempt` WHERE exam_schedule IS NOT NULL GROUP BY exam_schedule LIMIT 3",
        as_dict=True
    )
    print("  attempts by exam_schedule:", es_attempt)

    # Check Examination Result Analysis script ref
    era_path = "/home/frappe/frappe-bench/apps/university_erp/university_erp/university_examinations/report/examination_result_analysis/examination_result_analysis.py"
    print("\n=== Examination Result Analysis script (first 60 lines) ===")
    import os
    if os.path.exists(era_path):
        with open(era_path) as f:
            lines = f.readlines()[:60]
        print("".join(lines))

    print("\n=== Hostel Occupancy script ===")
    ho_path = "/home/frappe/frappe-bench/apps/university_erp/university_erp/university_hostel/report/hostel_occupancy/hostel_occupancy.py"
    if os.path.exists(ho_path):
        with open(ho_path) as f:
            lines = f.readlines()[:60]
        print("".join(lines))

    print("\n=== Library Circulation script ===")
    lc_path = "/home/frappe/frappe-bench/apps/university_erp/university_erp/university_library/report/library_circulation/library_circulation.py"
    if os.path.exists(lc_path):
        with open(lc_path) as f:
            lines = f.readlines()[:60]
        print("".join(lines))

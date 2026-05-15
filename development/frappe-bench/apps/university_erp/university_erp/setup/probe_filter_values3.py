"""Probe remaining filter values — no JOIN on unknown cols."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    print("=== Exam Schedule cols ===")
    cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabExam Schedule`", as_dict=True)]
    print("  cols:", cols[:20])

    print("\n=== Exam Schedule sample ===")
    es = frappe.db.sql("SELECT * FROM `tabExam Schedule` WHERE docstatus=1 LIMIT 3", as_dict=True)
    for r in es:
        print("  ", {k: v for k, v in r.items() if k not in ('creation', 'modified', 'modified_by', 'owner', '_user_tags', '_comments', '_assign', '_liked_by')})

    print("\n=== Student Exam Attempt cols ===")
    sea_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabStudent Exam Attempt`", as_dict=True)]
    print("  cols:", sea_cols)

    print("\n=== Library Transaction cols ===")
    lt_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabLibrary Transaction`", as_dict=True)]
    print("  cols:", lt_cols)

    print("\n=== Library Transaction sample ===")
    lt = frappe.db.sql("SELECT * FROM `tabLibrary Transaction` LIMIT 3", as_dict=True)
    for r in lt:
        print("  ", {k: v for k, v in r.items() if k not in ('creation', 'modified', 'modified_by', 'owner', '_user_tags', '_comments', '_assign', '_liked_by')})

    print("\n=== LMS Enrollment cols ===")
    lms_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabLMS Enrollment`", as_dict=True)]
    print("  cols:", lms_cols)

    print("\n=== LMS Course sample ===")
    lms = frappe.db.sql("SELECT name FROM `tabLMS Course` LIMIT 5", as_dict=True)
    print("  courses:", [r['name'] for r in lms])

    print("\n=== Report refs ===")
    reports = ["Placement Statistics", "Course Progress", "Faculty Feedback Report",
               "Hostel Occupancy", "Library Circulation", "Examination Result Analysis",
               "CO-PO Mapping Matrix", "PO Attainment Report"]
    for rname in reports:
        r = frappe.db.get_value("Report", rname, ["ref_doctype", "report_type"], as_dict=True)
        print(f"  {rname!r}: ref={r}")

    print("\n=== Feedback Response for Faculty Feedback filter ===")
    ff = frappe.db.sql(
        "SELECT instructor, COUNT(*) as cnt FROM `tabFeedback Response` GROUP BY instructor ORDER BY cnt DESC LIMIT 5",
        as_dict=True
    )
    print("  Instructors:", ff)

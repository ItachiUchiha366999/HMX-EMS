"""
Post-run validation for the comprehensive seed.

Three checks:
  A. Row-count probe — actual vs target per doctype
  B. Cross-link integrity — orphan FK detection
  C. Smoke tests — exercise key reports + student portal API

Usage:
    bench --site ems.hanumatrix.com execute university_erp.setup.seed_validate.validate_all
"""

import frappe
import json
import traceback


# Target row counts (lean 200-student volume)
TARGETS = {
    # People
    "Student": 200,
    "Employee": 50,
    "Instructor": 50,
    "Guardian": 50,
    "User": 17,  # Admin + Guest + 5 students + 2 faculty + 1 hod + 1 parent + 8 mgmt
    # Education foundation
    "Program": 8,
    "Course": 30,
    "Topic": 45,
    "Room": 12,
    "Academic Year": 2,
    "Academic Term": 4,
    "Fee Structure": 5,
    "Grading Scale": 1,
    "Student Group": 10,
    "Program Enrollment": 200,
    "Course Enrollment": 500,
    # Finance
    "Sales Invoice": 100,
    "Payment Entry": 50,
    "Account": 80,
    "Cost Center": 2,
    "GL Entry": 200,
    "Communication": 25,
    # HR
    "Attendance": 200,
    "Job Opening": 2,
    "Job Applicant": 3,
    # Hostel
    "Hostel Building": 4,
    "Hostel Room": 50,
    "Hostel Allocation": 30,
    # Library
    "Library Article": 30,
    "Library Member": 20,
    "Library Transaction": 10,
    # Transport
    "Transport Vehicle": 4,
    "Transport Route": 4,
    "Transport Allocation": 20,
    # Placement
    "Placement Company": 10,
    "Placement Job Opening": 5,
    "Placement Application": 10,
    # LMS
    "LMS Course": 10,
    "LMS Content": 20,
    # Examinations
    "Exam Schedule": 5,
    "Hall Ticket": 50,
    "Question Bank": 5,
    # OBE
    "Program Educational Objective": 8,
    "Program Outcome": 24,
    "Course Outcome": 30,
    # Communication / Notifications
    "Grievance": 5,
    "Notice Board": 3,
    "User Notification": 10,
    # Research
    "Research Project": 5,
    "Research Publication": 5,
    # === Layer 11a — Inventory & Assets ===
    "Supplier Group": 3,
    "Supplier": 8,
    "Inventory Item Group": 5,
    "Inventory Item": 50,
    "Asset Category": 6,
    "Asset": 25,
    "Asset Movement": 10,
    "Asset Maintenance": 5,
    "Maintenance Team": 2,
    "Lab Equipment": 15,
    "Lab Equipment Booking": 10,
    "Lab Consumable Issue": 5,
    "Stock Reconciliation": 4,
    # === Layer 11b — Admissions ===
    "Admission Cycle": 2,
    "Admission Criteria": 6,
    "Seat Matrix": 6,
    "Merit List": 4,
    # === Layer 11c — Examinations deep ===
    "External Examiner": 5,
    "Question Paper Template": 6,
    "Practical Examination": 6,
    "Internal Assessment": 15,
    "Answer Sheet": 50,
    "Revaluation Request": 3,
    "Student Transcript": 30,
    "Notification Template": 6,
    "Certificate Template": 4,
    "Certificate Request": 15,
    # === Layer 11d — OBE / Accreditation ===
    "Accreditation Cycle": 1,
    "Assessment Rubric": 5,
    "Survey Template": 2,
    "OBE Survey": 4,
    "PO Attainment": 5,
    "NAAC Metric": 20,
    "NIRF Data": 6,
    # === Layer 11e — Integrations ===
    "Biometric Device": 2,
    "Biometric Attendance Log": 80,
    "WhatsApp Template": 4,
    "SMS Log": 80,
    "SMS Queue": 4,
    "WhatsApp Log": 40,
    "Push Notification Log": 20,
    "User Device Token": 10,
    "Payment Transaction": 40,
    "Payment Order": 4,
    "Webhook Log": 15,
    # === Layer 11f — Portal richness ===
    "Student Status Log": 8,
    "Student Resume": 5,
    "Placement Profile": 25,
    "Course Registration": 5,
    "Hostel Attendance": 100,
    "Hostel Visitor": 8,
    "Hostel Maintenance Request": 5,
    "Library Fine": 4,
    "Book Reservation": 4,
    "Transport Trip Log": 40,
    "Student Scholarship": 5,
    "Assessment Result": 15,
    "Notification Preference": 5,
    "Course Schedule": 20,
    "Announcement": 4,
    "Student Attendance": 300,
    # === Layer 11g — Alumni / Workload ===
    "Alumni": 20,
    "University Alumni": 20,
    "Alumni Event": 4,
    "Alumni Event Registration": 60,
    "Workload Distributor": 6,
    "Teaching Assignment": 20,
    "Timetable Slot": 8,
    "Elective Course Group": 4,
    "Grievance Committee": 4,
    "Job Posting": 10,
    # === Layer 11h — Analytics / LMS deeper ===
    "KPI Definition": 8,
    "KPI Value": 20,
    "Custom Dashboard": 4,
    "Scheduled Report": 3,
    "LMS Assignment": 10,
    "LMS Quiz": 6,
    "LMS Discussion": 12,
    "Quiz Attempt": 5,
    "Assignment Submission": 5,
    "Discussion Reply": 5,
    # === Layer 11i — Remaining ===
    "Custom Report Definition": 4,
    "DigiLocker Issued Document": 5,
    "Email Queue Extended": 10,
    "Emergency Acknowledgment": 2,
    "Fee Category": 5,
    "Fee Refund": 3,
    "Hostel Bulk Attendance": 2,
    "Mess Menu": 2,
    "Notice View Log": 5,
    "Payment Webhook Log": 5,
    "Research Grant": 3,
    "Student Feedback": 10,
    "Temporary Teaching Assignment": 3,
    "University Announcement": 4,
    "Bulk Fee Generator": 2,
}


# Cross-link integrity checks: (parent_dt, parent_field, target_dt)
# Verifies that every value in `parent_dt.parent_field` exists in `tabtarget_dt`
LINK_CHECKS = [
    ("Hall Ticket", "student", "Student"),
    ("Course Registration", "student", "Student"),
    ("Student Status Log", "student", "Student"),
    ("University Alumni", "student", "Student"),
    ("Student Scholarship", "student", "Student"),
    ("Library Member", "student", "Student"),  # only when member_type=Student
    ("Hostel Allocation", "student", "Student"),
    ("Program Enrollment", "student", "Student"),
    ("Program Enrollment", "program", "Program"),
    ("Course Enrollment", "student", "Student"),
    ("Course Enrollment", "course", "Course"),
    ("Sales Invoice", "customer", "Customer"),
    ("Payment Entry", "company", "Company"),
    ("Faculty Profile", "employee", "Employee"),
    ("Instructor", None, None),  # No required Link, skip
]


# Reports to smoke-test (run as Administrator, expect non-empty result)
REPORTS_TO_SMOKE_TEST = [
    # Finance
    "Profit and Loss Statement",
    "General Ledger",
    "Trial Balance",
    "Accounts Receivable",
    # Education
    "Fee Collection Summary",
    "Course Progress",
    # Examinations
    "Examination Result Analysis",
    "CO Attainment Report",
    # Hostel / Library / Transport / Placement
    "Hostel Occupancy",
    "Library Circulation",
    "Placement Statistics",
    # HR / Communication / Faculty
    "Faculty Feedback Report",
    "Communication Analytics",
    # Examinations / OBE (Layer 11c/11d)
    "Internal Assessment Summary",
    "PO Attainment Report",
    "Program Attainment Summary",
    "Survey Analysis Report",
    # Integration / Communication (Layer 11e)
    "SMS Delivery Report",
    # Portal / Alumni (Layer 11f/11g)
    "Faculty Directory",
    # Research
    "Faculty Research Output",
]


def _check_row_counts():
    print("\n=== A. Row-count probe ===")
    results = []
    for dt, target in TARGETS.items():
        if not frappe.db.exists("DocType", dt):
            results.append({"dt": dt, "target": target, "actual": "-", "status": "SKIP-NODOCTYPE"})
            continue
        try:
            actual = frappe.db.count(dt)
        except Exception as e:
            results.append({"dt": dt, "target": target, "actual": "?", "status": f"ERR: {str(e)[:60]}"})
            continue
        if actual >= target:
            status = "OK"
        elif actual >= target * 0.5:
            status = "LOW"
        else:
            status = "MISS"
        results.append({"dt": dt, "target": target, "actual": actual, "status": status})

    # Print table
    print(f"  {'DocType':<35} {'Target':>8} {'Actual':>8}  Status")
    print(f"  {'-' * 35} {'-' * 8} {'-' * 8}  ------")
    for r in results:
        actual_str = str(r["actual"])
        target_str = str(r["target"])
        marker = {"OK": "✓", "LOW": "⚠", "MISS": "✗", "SKIP-NODOCTYPE": "-"}.get(r["status"], "?")
        print(f"  {r['dt']:<35} {target_str:>8} {actual_str:>8}  {marker} {r['status']}")

    miss_count = sum(1 for r in results if r["status"] == "MISS")
    low_count = sum(1 for r in results if r["status"] == "LOW")
    print(f"\n  Summary: {len(results) - miss_count - low_count} OK, {low_count} LOW, {miss_count} MISS")
    return results


def _check_cross_links():
    print("\n=== B. Cross-link integrity ===")
    results = []
    for parent_dt, field, target_dt in LINK_CHECKS:
        if field is None:
            continue
        if not frappe.db.exists("DocType", parent_dt):
            continue
        if not frappe.db.exists("DocType", target_dt):
            continue
        try:
            sql = f"""
                SELECT COUNT(*) FROM `tab{parent_dt}` p
                WHERE IFNULL(p.`{field}`, '') != ''
                  AND p.`{field}` NOT IN (SELECT name FROM `tab{target_dt}`)
            """
            orphans = frappe.db.sql(sql)[0][0]
            results.append({
                "rel": f"{parent_dt}.{field} → {target_dt}",
                "orphans": orphans,
                "status": "OK" if orphans == 0 else "ORPHAN",
            })
        except Exception as e:
            results.append({
                "rel": f"{parent_dt}.{field} → {target_dt}",
                "orphans": "?",
                "status": f"ERR: {str(e)[:60]}",
            })

    print(f"  {'Relation':<55} {'Orphans':>8}  Status")
    print(f"  {'-' * 55} {'-' * 8}  ------")
    for r in results:
        marker = "✓" if r["status"] == "OK" else "✗"
        print(f"  {r['rel']:<55} {str(r['orphans']):>8}  {marker} {r['status']}")
    orphan_count = sum(1 for r in results if r["status"] == "ORPHAN")
    print(f"\n  Summary: {orphan_count} relations with orphans")
    return results


def _smoke_test_reports():
    print("\n=== C. Smoke-test reports ===")
    results = []
    for report_name in REPORTS_TO_SMOKE_TEST:
        if not frappe.db.exists("Report", report_name):
            results.append({"report": report_name, "status": "MISSING"})
            continue
        try:
            from frappe.desk.query_report import run as run_report
            # Pick filters — most reports we've seen need date range
            filters = {}
            company = frappe.db.get_value("Company", {}, "name") or "NIT"
            fiscal_year = frappe.db.get_value(
                "Fiscal Year", {"year_start_date": ["<=", frappe.utils.nowdate()],
                                "year_end_date": [">=", frappe.utils.nowdate()]},
                "name",
            ) or frappe.db.get_value("Fiscal Year", {}, "name")
            ref_dt = frappe.db.get_value("Report", report_name, "ref_doctype")
            if ref_dt and ref_dt in ("Sales Invoice", "Payment Entry", "GL Entry", "Account"):
                filters = {
                    "company": company,
                    "from_date": frappe.utils.add_months(frappe.utils.nowdate(), -12),
                    "to_date": frappe.utils.nowdate(),
                    "fiscal_year": fiscal_year,
                    "periodicity": "Yearly",
                }
            # Reports that always need company + fiscal_year + dates regardless of ref
            if report_name in ("Profit and Loss Statement", "Trial Balance",
                               "Balance Sheet", "Cash Flow"):
                filters = {
                    "company": company,
                    "from_date": frappe.utils.add_months(frappe.utils.nowdate(), -12),
                    "to_date": frappe.utils.nowdate(),
                    "fiscal_year": fiscal_year,
                    "periodicity": "Yearly",
                    "filter_based_on": "Date Range",
                    "period_start_date": frappe.utils.add_months(frappe.utils.nowdate(), -12),
                    "period_end_date": frappe.utils.nowdate(),
                }
            # Reports that need specific mandatory filters
            if report_name == "Internal Assessment Summary":
                # Requires course + academic_year; pick first IA's course
                ia = frappe.db.sql(
                    "SELECT course, academic_year FROM `tabInternal Assessment` WHERE docstatus=1 LIMIT 1",
                    as_dict=True
                )
                if ia:
                    filters = {"course": ia[0].course, "academic_year": ia[0].academic_year}
            if report_name in ("Program Attainment Summary", "Survey Analysis Report"):
                filters = {"academic_year": "2026-2027"}
            if report_name == "CO-PO Mapping Matrix":
                first = frappe.db.sql(
                    "SELECT course, program FROM `tabCO PO Mapping` WHERE docstatus=1 LIMIT 1",
                    as_dict=True
                )
                if first:
                    filters = {"course": first[0].course, "program": first[0].program}
            res = run_report(report_name, filters=filters, ignore_prepared_report=True)
            row_count = len(res.get("result", []))
            results.append({
                "report": report_name,
                "rows": row_count,
                "status": "OK" if row_count > 0 else "EMPTY",
            })
        except Exception as e:
            results.append({
                "report": report_name,
                "rows": "?",
                "status": f"ERR: {str(e)[:60]}",
            })

    print(f"  {'Report':<40} {'Rows':>6}  Status")
    print(f"  {'-' * 40} {'-' * 6}  ------")
    for r in results:
        marker = "✓" if r["status"] == "OK" else ("⚠" if r["status"] == "EMPTY" else "✗")
        print(f"  {r['report']:<40} {str(r.get('rows', '-')): >6}  {marker} {r['status']}")
    ok_count = sum(1 for r in results if r["status"] == "OK")
    print(f"\n  Summary: {ok_count}/{len(results)} reports return non-zero data")
    return results


def _smoke_test_student_portal():
    print("\n=== D. Student portal smoke test ===")
    test_email = "student1@nit.edu"
    if not frappe.db.exists("User", test_email):
        print(f"  ✗ User {test_email} not seeded — portal redirect cannot be tested")
        return {"status": "USER-MISSING"}

    # Roles
    roles = frappe.get_roles(test_email)
    has_student = "Student" in roles
    has_uni_student = "University Student" in roles
    has_sysmgr = "System Manager" in roles
    has_admin = "Administrator" in roles

    # Student record link
    student = frappe.db.get_value("Student", {"user": test_email}, "name")

    # Redirect logic test
    try:
        from university_erp.utils import get_website_user_home_page
        redirect = get_website_user_home_page(test_email)
    except Exception as e:
        redirect = f"ERR: {str(e)[:60]}"

    print(f"  User {test_email}:")
    print(f"    Has Student role:           {'✓' if has_student else '✗'}")
    print(f"    Has University Student role: {'✓' if has_uni_student else '✗'}")
    print(f"    NOT System Manager:         {'✓' if not has_sysmgr else '✗'}")
    print(f"    NOT Administrator:          {'✓' if not has_admin else '✗'}")
    print(f"    Linked Student record:      {'✓' if student else '✗'}  ({student})")
    print(f"    get_website_user_home_page: {redirect}")
    print(f"    (expected: 'student_portal')")

    return {
        "user": test_email,
        "has_student_role": has_student,
        "has_university_student_role": has_uni_student,
        "no_system_manager": not has_sysmgr,
        "no_administrator": not has_admin,
        "linked_student": student,
        "redirect": redirect,
        "status": "OK" if (has_student and has_uni_student and not has_sysmgr and student and redirect == "student_portal") else "FAIL",
    }


def validate_all():
    print("=" * 60)
    print("POST-SEED VALIDATION")
    print("=" * 60)

    rc = _check_row_counts()
    xl = _check_cross_links()
    rep = _smoke_test_reports()
    portal = _smoke_test_student_portal()

    summary = {
        "row_counts": rc,
        "cross_links": xl,
        "reports": rep,
        "portal": portal,
    }

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

    # High-level pass/fail
    miss_dt = sum(1 for r in rc if r["status"] == "MISS")
    orphan_rels = sum(1 for r in xl if r["status"] == "ORPHAN")
    failed_reports = sum(1 for r in rep if r["status"] not in ("OK", "EMPTY"))
    portal_ok = portal.get("status") == "OK"

    print(f"  Doctypes missing target by >50%: {miss_dt}")
    print(f"  Cross-link orphan relations: {orphan_rels}")
    print(f"  Reports erroring (not just empty): {failed_reports}")
    print(f"  Student portal redirect: {'✓ OK' if portal_ok else '✗ FAIL'}")

    overall_pass = (miss_dt == 0 and orphan_rels == 0 and failed_reports == 0 and portal_ok)
    print(f"\n  OVERALL: {'✓ PASS' if overall_pass else '✗ NEEDS ATTENTION'}")

    return summary

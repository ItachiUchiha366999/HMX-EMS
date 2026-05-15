"""
Pre-flight schema validation for the comprehensive seed.

Goal: catch schema/data issues BEFORE the seed touches data, so we don't
half-fill the system. Returns a JSON report with blockers + warnings.

Usage:
    bench --site ems.hanumatrix.com execute university_erp.setup.seed_preflight.run

Returns dict:
    {
        "checks_passed": int,
        "checks_failed": int,
        "blockers": [str, ...],     # If non-empty, seed must NOT run.
        "warnings": [str, ...],     # Seed can proceed but log these.
    }
"""

import frappe
import json


# DocTypes the seed writes to (across all 4 apps + university_erp).
# Sourced from the doctype inventory in the plan file.
TARGET_DOCTYPES = [
    # Frappe core
    "User", "Has Role", "Communication", "Notification Settings",
    # ERPNext
    "Company", "Customer", "Customer Group", "Territory", "Item", "Item Group",
    "Brand", "Supplier", "Supplier Group", "Mode of Payment", "Bank", "Bank Account",
    "Account", "Cost Center", "Fiscal Year", "Sales Invoice", "Sales Invoice Item",
    "Payment Entry", "Payment Entry Reference", "Payment Schedule", "Journal Entry",
    "Journal Entry Account", "Purchase Invoice", "Purchase Invoice Item",
    "Stock Entry", "Stock Entry Item", "Asset", "Asset Category", "Asset Movement",
    "Warehouse", "UOM", "Designation", "Department",
    # HRMS
    "Employee", "Employee Grade", "Employment Type", "Branch", "Holiday List",
    "Leave Type", "Leave Allocation", "Leave Application", "Salary Component",
    "Salary Structure", "Salary Structure Assignment", "Salary Slip",
    "Attendance", "Job Opening", "Job Applicant",
    # Education
    "Academic Year", "Academic Term", "Program", "Course", "Topic", "Room",
    "Instructor", "Student", "Student Applicant", "Student Group",
    "Student Group Student", "Student Group Instructor", "Program Enrollment",
    "Course Enrollment", "Course Schedule", "Student Attendance",
    "Grading Scale", "Assessment Group", "Assessment Criteria",
    "Assessment Plan", "Assessment Result", "Fee Category", "Fee Structure",
    "Fee Component", "Fee Schedule", "Fees", "Guardian", "Student Category",
    "Student Batch Name",
    # university_erp - faculty_management
    "Faculty Profile", "Teaching Assignment", "Teaching Assignment Schedule",
    "Workload Distributor", "Student Feedback", "Faculty Award",
    "Faculty Publication", "Faculty Research Project", "Employee Qualification",
    # university_erp - university_academics
    "Course Registration", "Course Registration Item",
    "Elective Course Group", "Elective Course Group Item", "Timetable Slot",
    # university_erp - university_admissions
    "Admission Cycle", "Admission Cycle Program", "Admission Criteria",
    "Seat Matrix", "Merit List", "Merit List Applicant",
    # university_erp - core
    "University Settings", "University Department", "University Laboratory",
    "Notice Board", "Notice Target Department", "Notice Target Program",
    "User Notification", "Emergency Alert", "Suggestion", "Notification Template",
    # university_erp - examinations
    "Question Bank", "Question Tag", "Question Tag Link",
    "Question Paper Template", "Question Paper Section",
    "Generated Question Paper", "Question Paper Question Item",
    "Exam Schedule", "Exam Invigilator", "External Examiner",
    "Internal Assessment", "Internal Assessment Score",
    "Practical Examination", "Practical Exam Student Score",
    "Online Examination", "Online Exam Student", "Student Exam Attempt",
    "Hall Ticket", "Hall Ticket Exam", "Answer Sheet", "Answer Sheet Score",
    "Student Transcript", "Transcript Semester Result", "Revaluation Request",
    # university_erp - finance & payments
    "Bulk Fee Generator", "Bulk Fee Generator Student", "Fee Refund",
    "Fee Refund Deduction", "Scholarship Type", "Student Scholarship",
    "University Accounts Settings", "Fee Category Account",
    "Payment Order", "Bank Transaction", "Webhook Log",
    "Razorpay Settings", "PayU Settings",
    # university_erp - hostel
    "Hostel Building", "Hostel Room", "Hostel Room Occupant",
    "Hostel Mess", "Mess Menu", "Mess Menu Item",
    "Hostel Allocation", "Hostel Attendance", "Hostel Attendance Record",
    "Hostel Bulk Attendance", "Hostel Visitor", "Hostel Maintenance Request",
    # university_erp - library
    "Library Subject", "Library Category", "Library Article",
    "Library Member", "Library Transaction", "Library Fine", "Book Reservation",
    # university_erp - transport
    "Transport Vehicle", "Transport Route", "Transport Route Stop",
    "Transport Allocation", "Transport Trip Log",
    # university_erp - lms
    "LMS Course", "LMS Course Module", "LMS Content", "LMS Content Progress",
    "LMS Assignment", "Assignment Rubric Item", "Assignment Submission",
    "Submission File", "Submission Rubric Score",
    "LMS Quiz", "Quiz Question", "Quiz Attempt", "Quiz Answer",
    "LMS Discussion", "Discussion Reply",
    # university_erp - placement
    "Industry Type", "Placement Company", "Placement Job Opening",
    "Job Eligible Program", "Placement Drive", "Placement Round",
    "Placement Application", "Student Resume",
    "Resume Education", "Resume Skill", "Resume Project",
    # university_erp - research
    "Research Project", "Research Team Member", "Research Publication",
    "Publication Author", "Project Publication Link",
    "Research Grant", "Grant Utilization",
    # university_erp - obe
    "Program Educational Objective", "Program Outcome", "Course Outcome",
    "CO PO Mapping", "CO PO Mapping Entry", "CO Attainment",
    "CO Direct Attainment", "CO Indirect Attainment", "CO Final Attainment",
    "PO Attainment", "PO Attainment Entry", "PO Indirect Entry",
    "PO Final Entry", "PO PEO Mapping",
    "Assessment Rubric", "Assessment Criteria Item", "Assessment CO Link",
    "Bloom Distribution Rule", "Unit Distribution Rule",
    "OBE Survey", "Survey Question Item", "Survey Template", "Survey PO Rating",
    "Accreditation Cycle", "Accreditation Criterion",
    "Accreditation Department Link", "Accreditation Program Link",
    "Accreditation Team Member",
    "NAAC Metric", "NAAC Metric Year Data", "NAAC Metric Document",
    "NAAC Document Checklist Item", "NIRF Data",
    "Committee Member", "Committee Category Link",
    # university_erp - integrations
    "Biometric Device", "Biometric Attendance Log",
    "Certificate Template", "Certificate Field", "Certificate Request",
    "DigiLocker Settings", "DigiLocker Document Type", "DigiLocker Issued Document",
    "SMS Template", "SMS Log", "SMS Queue", "University SMS Settings",
    "WhatsApp Template", "WhatsApp Log", "WhatsApp Settings",
    "Push Notification Settings", "Push Notification Log", "User Device Token",
    "Email Queue Extended", "Payment Gateway Settings", "Payment Transaction",
    # university_erp - inventory
    "Inventory Item", "Inventory Item Group", "Item Specification",
    "Stock Reconciliation", "Stock Reconciliation Item",
    "Material Request", "Material Request Item",
    "Purchase Order", "Purchase Order Item", "Purchase Receipt", "Purchase Receipt Item",
    "Lab Equipment", "Lab Equipment Booking",
    "Lab Consumable Issue", "Lab Consumable Issue Item",
    "Maintenance Team", "Maintenance Team Member",
    "Asset Maintenance", "Asset Maintenance Part", "Depreciation Schedule",
    # university_erp - communication & feedback
    "Grievance Type", "Grievance Committee", "Grievance",
    "Grievance Action", "Grievance Communication", "Grievance Attachment",
    "Grievance Escalation Log", "Grievance Escalation Rule",
    "Feedback Form", "Feedback Form Section", "Feedback Question",
    "Feedback Course Filter", "Feedback Department Filter", "Feedback Program Filter",
    "Feedback Response", "Feedback Answer", "Feedback Section Score",
    # university_erp - portals
    "Alumni", "Alumni Event", "Alumni Event Registration",
    "Announcement", "Job Posting", "Placement Profile",
    # university_erp - student_info
    "Student Status Log", "University Alumni", "University Announcement",
]

# Custom Fields the seeder reads or writes.
TARGET_CUSTOM_FIELDS = [
    ("Student", "custom_program"),
    ("Student", "custom_enrollment_number"),
    ("Student", "custom_cgpa"),
    ("Student", "custom_category"),
    ("Student", "custom_aadhaar_number"),
    ("Student", "custom_biometric_id"),
    ("Student", "custom_digilocker_id"),
    ("Student", "custom_category_certificate"),
    ("Student", "custom_student_status"),
]

# Single doctypes the seeder configures.
TARGET_SINGLES = [
    "University Settings", "University Accounts Settings",
    "Razorpay Settings", "PayU Settings",
    "WhatsApp Settings", "DigiLocker Settings",
    "Push Notification Settings", "University SMS Settings",
    "Education Settings", "Accounts Settings",
    "System Settings", "Global Defaults",
    "Stock Settings", "Domain Settings",
    "Payment Gateway Settings",
]

# Required reference data that must be present before any seed phase runs.
REQUIRED_REFERENCE_DATA = [
    ("DocType", "Country"),  # at least one Country
    ("DocType", "Currency"),  # at least one Currency
    ("DocType", "Gender"),    # at least Male, Female
    ("DocType", "UOM"),       # at least Nos
    ("Company", None),        # at least one Company
    ("Fiscal Year", None),    # at least one FY (current)
    ("Cost Center", None),    # at least one Cost Center
    ("Warehouse", None),      # at least one Warehouse
]


def _check_doctype_exists(report):
    """Check 3: every doctype referenced exists."""
    missing = []
    for dt in TARGET_DOCTYPES:
        if not frappe.db.exists("DocType", dt):
            missing.append(dt)
    if missing:
        report["blockers"].append(
            f"Missing DocTypes ({len(missing)}): {', '.join(missing[:10])}"
            + (f" ... +{len(missing)-10} more" if len(missing) > 10 else "")
        )
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_required_fields(report):
    """Check 1: required fields are sane on each target doctype."""
    issues = []
    for dt in TARGET_DOCTYPES:
        if not frappe.db.exists("DocType", dt):
            continue
        try:
            meta = frappe.get_meta(dt)
        except Exception as e:
            issues.append(f"{dt}: cannot load meta ({str(e)[:80]})")
            continue
        for f in meta.fields:
            if f.fieldtype == "Link" and f.reqd and not f.options:
                issues.append(f"{dt}.{f.fieldname}: required Link with no options")
    if issues:
        report["warnings"].extend(issues[:30])
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_custom_fields(report):
    """Check 5: required Custom Fields exist."""
    missing = []
    for dt, fieldname in TARGET_CUSTOM_FIELDS:
        if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
            missing.append(f"{dt}.{fieldname}")
    if missing:
        report["blockers"].append(
            f"Missing Custom Fields: {', '.join(missing)}"
        )
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_singles(report):
    """Check 6: target Single doctypes are actually singles."""
    issues = []
    for dt in TARGET_SINGLES:
        if not frappe.db.exists("DocType", dt):
            issues.append(f"{dt}: doctype missing")
            continue
        meta = frappe.get_meta(dt)
        if not meta.issingle:
            issues.append(f"{dt}: expected Single, got non-Single")
    if issues:
        report["warnings"].extend(issues)
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_reference_data(report):
    """Check 2: required reference data present."""
    missing = []
    if frappe.db.count("Country") == 0:
        missing.append("Country")
    if frappe.db.count("Currency") == 0:
        missing.append("Currency")
    if frappe.db.count("Gender") < 2:
        missing.append("Gender (need Male+Female)")
    if frappe.db.count("UOM") == 0:
        missing.append("UOM")
    if frappe.db.count("Company") == 0:
        missing.append("Company")
    if frappe.db.count("Fiscal Year") == 0:
        missing.append("Fiscal Year")
    if frappe.db.count("Cost Center") == 0:
        missing.append("Cost Center")
    if frappe.db.count("Warehouse") == 0:
        missing.append("Warehouse")
    if missing:
        report["blockers"].append(f"Missing reference data: {', '.join(missing)}")
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_admin_permissions(report):
    """Check 4: Administrator can read/write/create on every target doctype."""
    issues = []
    user = "Administrator"
    for dt in TARGET_DOCTYPES:
        if not frappe.db.exists("DocType", dt):
            continue
        try:
            meta = frappe.get_meta(dt)
        except Exception:
            continue
        # Admin should always have create on non-virtual doctypes
        if not meta.issingle and not meta.istable:
            try:
                if not frappe.has_permission(dt, "create", user=user):
                    issues.append(f"{dt}: Administrator cannot create")
            except Exception as e:
                issues.append(f"{dt}: permission check failed ({str(e)[:60]})")
    if issues:
        report["warnings"].extend(issues[:20])
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_series_counters(report):
    """Check 7: tabSeries counters - warn if any will skew numbering."""
    rows = frappe.db.sql(
        "SELECT name, current FROM tabSeries WHERE current > 0",
        as_dict=True,
    )
    if rows:
        report["warnings"].append(
            f"tabSeries has {len(rows)} non-zero counters (e.g. {rows[0]['name']}={rows[0]['current']}). "
            f"Will continue numbering from there instead of starting at 1."
        )
        # Not a failure - just a warning
    report["checks_passed"] += 1


def _check_app_installed(report):
    """Bonus check: required apps installed."""
    installed = frappe.get_installed_apps()
    required = ["frappe", "erpnext", "hrms", "education", "university_erp"]
    missing = [a for a in required if a not in installed]
    if missing:
        report["blockers"].append(f"Required apps missing: {', '.join(missing)}")
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_student_user_link(report):
    """Bonus check: Student doctype has 'user' Link field (needed for portal redirect)."""
    if not frappe.db.exists("DocType", "Student"):
        report["blockers"].append("Student doctype missing")
        report["checks_failed"] += 1
        return
    meta = frappe.get_meta("Student")
    user_field = next((f for f in meta.fields if f.fieldname == "user"), None)
    if not user_field:
        report["blockers"].append("Student.user field missing - portal redirect won't work")
        report["checks_failed"] += 1
    elif user_field.options != "User":
        report["blockers"].append(f"Student.user expected Link to User, got {user_field.options}")
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_required_roles(report):
    """Bonus check: roles needed for the demo users exist."""
    required_roles = [
        "Student", "University Student",                       # student portal redirect
        "University Faculty", "Instructor", "Academics User",  # faculty
        "University HOD", "University Registrar",
        "University Finance", "University HR Admin",
        "University Exam Cell", "University Librarian",
        "University Warden", "University Placement Officer",
        "University Admin", "Guardian",
        "System Manager",                                      # admin escalation
    ]
    missing = [r for r in required_roles if not frappe.db.exists("Role", r)]
    if missing:
        report["blockers"].append(f"Required roles missing: {', '.join(missing)}")
        report["checks_failed"] += 1
    else:
        report["checks_passed"] += 1


def _check_student_permission_override(report):
    """Bonus check: Student permission override loads (Round-2 fix)."""
    try:
        from university_erp.overrides.student import (
            get_permission_query_conditions,
            has_permission,
            student_query,
            STUDENT_SELF_ROLES,
        )
        # Sanity-check: passing Administrator returns no restriction
        cond = get_permission_query_conditions("Administrator")
        if cond not in ("", None):
            report["warnings"].append(
                f"Student.get_permission_query_conditions('Administrator') = {cond!r}, "
                "expected empty"
            )
        report["checks_passed"] += 1
    except Exception as e:
        report["blockers"].append(
            f"Cannot import student.py override (Round-2 fix): {str(e)[:120]}"
        )
        report["checks_failed"] += 1


def run():
    """Main entry — run all pre-flight checks."""
    report = {
        "checks_passed": 0,
        "checks_failed": 0,
        "blockers": [],
        "warnings": [],
    }

    print("=" * 60)
    print("PRE-FLIGHT SCHEMA VALIDATION")
    print("=" * 60)

    _check_app_installed(report)
    _check_doctype_exists(report)
    _check_required_fields(report)
    _check_custom_fields(report)
    _check_singles(report)
    _check_reference_data(report)
    _check_admin_permissions(report)
    _check_series_counters(report)
    _check_student_user_link(report)
    _check_required_roles(report)
    _check_student_permission_override(report)

    print(f"\n  Checks passed: {report['checks_passed']}")
    print(f"  Checks failed: {report['checks_failed']}")

    if report["blockers"]:
        print(f"\n  🔴 BLOCKERS ({len(report['blockers'])}):")
        for b in report["blockers"]:
            print(f"    - {b}")

    if report["warnings"]:
        print(f"\n  🟡 Warnings ({len(report['warnings'])}):")
        for w in report["warnings"][:30]:
            print(f"    - {w}")
        if len(report["warnings"]) > 30:
            print(f"    ... +{len(report['warnings']) - 30} more")

    print("\n" + "=" * 60)
    if report["blockers"]:
        print("PRE-FLIGHT FAILED — DO NOT RUN seed_all() YET")
    else:
        print("PRE-FLIGHT PASSED — safe to run seed_all()")
    print("=" * 60)

    print("\nJSON report:")
    print(json.dumps(report, indent=2))

    return report

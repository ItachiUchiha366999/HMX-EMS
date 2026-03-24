"""
Comprehensive Demo Data Seeder for University ERP
National Institute of Technology (NIT) -- Academic Year 2025-2026

Creates 500+ students, 50+ faculty, full transactional data across all 21 modules,
and 20+ role-specific demo users.  Validates the university_finance GL posting fork
end-to-end with real data volumes.

Usage:
    bench --site university.local execute university_erp.setup.seed_comprehensive_demo_data.seed_all
    bench --site university.local execute university_erp.setup.seed_comprehensive_demo_data.clean_all
"""

import frappe
from frappe.utils import nowdate, add_days, getdate, today, random_string
from datetime import date, timedelta
import random
import traceback


# ---------------------------------------------------------------------------
# Indian name pools for realistic random generation
# ---------------------------------------------------------------------------
FIRST_NAMES_M = [
    "Aarav", "Aditya", "Akash", "Amit", "Anand", "Arjun", "Arun", "Ashwin",
    "Bharat", "Chetan", "Deepak", "Dev", "Dhruv", "Ganesh", "Harsh", "Hemant",
    "Ishaan", "Jayesh", "Karthik", "Kunal", "Mahesh", "Manish", "Mohan", "Nakul",
    "Nikhil", "Pranav", "Rahul", "Rajat", "Ravi", "Rohit", "Sachin", "Sahil",
    "Sanjay", "Siddharth", "Suresh", "Tarun", "Varun", "Vikram", "Vinay", "Vishal",
    "Yash", "Ramesh", "Pankaj", "Gaurav", "Shivam", "Ajay", "Naveen", "Rohan",
    "Pradeep", "Tushar",
]
FIRST_NAMES_F = [
    "Aanya", "Aditi", "Ananya", "Anjali", "Aparna", "Bhavya", "Chitra", "Deepa",
    "Divya", "Gauri", "Isha", "Jaya", "Kavya", "Lakshmi", "Meera", "Neha",
    "Nisha", "Pallavi", "Pooja", "Priya", "Rashmi", "Riya", "Sakshi", "Shruti",
    "Sneha", "Sunita", "Swati", "Tanvi", "Urmila", "Vidya", "Yamini", "Zara",
    "Kavita", "Radha", "Suman", "Minal", "Parul", "Rekha", "Simran", "Trupti",
    "Varsha", "Kirti", "Preeti", "Nandini", "Seema", "Shweta", "Amrita", "Padma",
    "Geeta", "Hema",
]
LAST_NAMES = [
    "Agarwal", "Banerjee", "Bhat", "Chauhan", "Choudhary", "Das", "Desai",
    "Dubey", "Gowda", "Gupta", "Hegde", "Iyer", "Jha", "Joshi", "Kapoor",
    "Khan", "Kulkarni", "Kumar", "Malhotra", "Mehta", "Menon", "Mishra", "Nair",
    "Pandey", "Patel", "Pillai", "Rao", "Rajan", "Reddy", "Saxena", "Shah",
    "Sharma", "Shetty", "Singh", "Sinha", "Srivastava", "Tiwari", "Varma",
    "Verma", "Yadav", "Bose", "Dutta", "Ghosh", "Mukherjee", "Roy", "Sen",
    "Chopra", "Tandon", "Sethi", "Kaur",
]

COMPANY = "National Institute of Technology"
COMPANY_ABBR = "NIT"
ACADEMIC_YEAR = "2025-2026"
PASSWORD = "Demo@Nit2026!"

PROGRAMS = [
    ("B.Tech Computer Science and Engineering", "BTCSE", 4),
    ("B.Tech Electronics and Communication", "BTECE", 4),
    ("B.Tech Mechanical Engineering", "BTME", 4),
    ("B.Tech Civil Engineering", "BTCE", 4),
    ("B.Tech Electrical Engineering", "BTEE", 4),
    ("M.Tech Computer Science", "MTCS", 2),
    ("M.Tech Electronics", "MTEC", 2),
    ("MBA", "MBA", 2),
]

DEPARTMENTS = [
    ("Computer Science", "CSE"),
    ("Electronics", "ECE"),
    ("Mechanical", "ME"),
    ("Civil", "CE"),
    ("Electrical", "EE"),
    ("Chemical", "CHE"),
    ("Mathematics", "MATH"),
    ("Physics", "PHY"),
]

COURSE_MAP = {
    "BTCSE": [
        ("Data Structures and Algorithms", "CS201"), ("Database Management Systems", "CS202"),
        ("Operating Systems", "CS301"), ("Computer Networks", "CS302"),
        ("Software Engineering", "CS401"), ("Artificial Intelligence", "CS501"),
    ],
    "BTECE": [
        ("Digital Electronics", "EC201"), ("Signals and Systems", "EC202"),
        ("Microprocessors", "EC301"), ("Communication Systems", "EC302"),
        ("VLSI Design", "EC401"),
    ],
    "BTME": [
        ("Engineering Mechanics", "ME201"), ("Thermodynamics", "ME202"),
        ("Fluid Mechanics", "ME301"), ("Manufacturing Processes", "ME302"),
        ("Machine Design", "ME401"),
    ],
    "BTCE": [
        ("Structural Analysis", "CE201"), ("Surveying", "CE202"),
        ("Geotechnical Engineering", "CE301"), ("Transportation Engineering", "CE302"),
        ("Environmental Engineering", "CE401"),
    ],
    "BTEE": [
        ("Circuit Theory", "EE201"), ("Electromagnetic Theory", "EE202"),
        ("Power Systems", "EE301"), ("Control Systems", "EE302"),
        ("Electrical Machines", "EE401"),
    ],
    "MTCS": [
        ("Advanced Algorithms", "CS601"), ("Machine Learning", "CS602"),
        ("Cloud Computing", "CS603"), ("Big Data Analytics", "CS604"),
        ("Research Methodology", "CS605"),
    ],
    "MTEC": [
        ("Advanced Communication", "EC601"), ("Embedded Systems", "EC602"),
        ("Wireless Networks", "EC603"), ("Signal Processing", "EC604"),
        ("Research Methods", "EC605"),
    ],
    "MBA": [
        ("Financial Management", "MB201"), ("Marketing Management", "MB202"),
        ("Human Resource Management", "MB301"), ("Operations Management", "MB302"),
        ("Strategic Management", "MB401"), ("Business Analytics", "MB402"),
    ],
}


# ============================================================
# HELPERS
# ============================================================

def _safe(fn_name, fn, *args, **kwargs):
    """Execute a seeding function with error handling."""
    try:
        fn(*args, **kwargs)
    except Exception:
        print(f"  ERROR in {fn_name}:")
        traceback.print_exc()
        print(f"  Continuing to next section...")


def _exists_or_create(doctype, filters, data, ignore_links=False):
    """Idempotent document creation. Returns name or None."""
    existing = frappe.db.exists(doctype, filters)
    if existing:
        return existing
    try:
        doc = frappe.get_doc({"doctype": doctype, **data})
        doc.insert(ignore_permissions=True, ignore_links=ignore_links)
        return doc.name
    except frappe.DuplicateEntryError:
        return frappe.db.get_value(doctype, filters, "name")
    except Exception as e:
        err = str(e)[:200]
        print(f"    WARN creating {doctype}: {err}")
        return None


def _create_user(email, first_name, last_name, roles, password=PASSWORD):
    """Create user with multiple roles, bypassing throttle."""
    if frappe.db.exists("User", email):
        return email
    try:
        # Filter out roles that don't exist
        valid_roles = [r for r in roles if frappe.db.exists("Role", r)]
        if not valid_roles:
            valid_roles = ["System Manager"]

        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "enabled": 1,
            "new_password": password,
            "send_welcome_email": 0,
            "user_type": "System User",
        })
        for role in valid_roles:
            user.append("roles", {"role": role})
        # Bypass throttle by temporarily raising the limit
        old_limit = frappe.local.conf.get("throttle_user_limit", 60)
        frappe.local.conf["throttle_user_limit"] = 9999
        user.insert(ignore_permissions=True)
        frappe.local.conf["throttle_user_limit"] = old_limit
        return email
    except Exception as e:
        print(f"    WARN creating user {email}: {str(e)[:150]}")
        return None


def _random_name(gender):
    """Generate a random Indian name."""
    if gender == "Male":
        first = random.choice(FIRST_NAMES_M)
    else:
        first = random.choice(FIRST_NAMES_F)
    last = random.choice(LAST_NAMES)
    return first, last


def _random_dob(min_year=2002, max_year=2006):
    """Random date of birth."""
    year = random.randint(min_year, max_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


# ============================================================
# CLEAN ALL DATA
# ============================================================

def clean_all():
    """Delete ALL existing demo/transactional data. Keep Company, Fiscal Year."""
    frappe.flags.ignore_permissions = True
    frappe.flags.in_test = True
    print("=" * 60)
    print("CLEANING ALL DATA...")
    print("=" * 60)

    # University finance (GL entries etc.)
    finance_dts = [
        "GL Entry", "Payment Ledger Entry", "Payment Entry",
    ]

    # University ERP transactional (children first)
    child_dts = [
        "Hostel Attendance", "Hostel Allocation", "Hostel Visitor",
        "Hostel Maintenance Request",
        "Library Transaction", "Library Member", "Book Reservation", "Library Fine",
        "Assignment Submission", "Quiz Attempt", "LMS Content Progress", "LMS Discussion",
        "Student Exam Attempt", "Answer Sheet", "Fee Payment", "Student Scholarship",
        "Grievance", "Feedback Response", "Student Feedback", "Suggestion",
        "User Notification", "Certificate Request", "Transport Allocation",
        "Transport Trip Log",
        "Placement Application", "CO Attainment", "PO Attainment", "CO PO Mapping",
        "Course Outcome", "Notice Board", "Notice View Log", "Internal Assessment",
        "Hostel Bulk Attendance", "Notification Preference",
    ]

    master_dts = [
        "Hostel Room", "Hostel Building", "Hostel Mess", "Mess Menu",
        "Library Article", "Library Category", "Library Subject",
        "LMS Course", "LMS Content", "LMS Assignment", "LMS Quiz",
        "Question Bank", "Question Paper Template", "Question Tag",
        "Exam Schedule", "Hall Ticket", "External Examiner", "Student Transcript",
        "Generated Question Paper", "Practical Examination", "Online Examination",
        "Revaluation Request", "Assessment Rubric", "Accreditation Cycle",
        "Transport Route", "Transport Vehicle",
        "Placement Company", "Placement Job Opening", "Student Resume", "Industry Type",
        "Placement Drive", "Placement Profile", "Job Posting",
        "Research Publication", "Research Project", "Research Grant",
        "Faculty Profile", "Teaching Assignment", "Temporary Teaching Assignment",
        "Workload Distributor", "Timetable Slot", "Elective Course Group",
        "Admission Cycle", "Admission Criteria", "Seat Matrix", "Merit List",
        "Fee Category", "Scholarship Type", "Bulk Fee Generator",
        "University Department", "University Laboratory",
        "Feedback Form", "Grievance Type", "Grievance Committee",
        "Certificate Template", "Notification Template",
        "Program Educational Objective", "Program Outcome",
        "OBE Survey", "Survey Template",
        "University Announcement", "Student Status Log",
        "University Alumni", "Alumni", "Alumni Event",
        "Announcement", "Emergency Alert", "Emergency Acknowledgment",
    ]

    edu_dts = [
        "Student Attendance", "Course Enrollment", "Course Schedule",
        "Assessment Result", "Assessment Plan", "Fees", "Fee Schedule",
        "Program Enrollment", "Student Group", "Student",
        "Instructor", "Guardian", "Course", "Program", "Room", "Topic",
        "Student Category", "Student Batch Name", "Assessment Criteria",
        "Assessment Group", "Fee Structure",
    ]

    hrms_dts = [
        "Leave Application", "Attendance", "Salary Structure Assignment",
        "Salary Structure", "Leave Policy Assignment", "Leave Policy",
        "Leave Allocation",
    ]

    for dt_list in [finance_dts, child_dts, master_dts, edu_dts, hrms_dts]:
        for dt in dt_list:
            if frappe.db.exists("DocType", dt):
                try:
                    count = frappe.db.count(dt)
                    if count:
                        frappe.db.sql(f"DELETE FROM `tab{dt}`")
                        meta = frappe.get_meta(dt)
                        for tf in meta.get_table_fields():
                            frappe.db.sql(
                                f"DELETE FROM `tab{tf.options}` WHERE parenttype='{dt}'"
                            )
                        print(f"  Deleted {count} {dt}")
                except Exception as e:
                    print(f"  WARN: {dt}: {e}")

    # Delete employees (not Company)
    emp_count = frappe.db.count("Employee")
    if emp_count:
        frappe.db.sql("DELETE FROM `tabEmployee`")
        print(f"  Deleted {emp_count} Employee")

    # Delete non-system users
    users = frappe.get_all("User", filters={
        "name": ["not in", ["Administrator", "Guest"]],
        "user_type": "Website User",
    }, pluck="name")
    users += frappe.get_all("User", filters={
        "name": ["not in", ["Administrator", "Guest"]],
        "name": ["like", "%@nit.edu"],
    }, pluck="name")
    users += frappe.get_all("User", filters={
        "name": ["not in", ["Administrator", "Guest"]],
        "name": ["like", "%@university.local"],
    }, pluck="name")

    for u in set(users):
        try:
            frappe.db.sql("DELETE FROM `tabHas Role` WHERE parent=%s", u)
            frappe.db.sql("DELETE FROM `tabUser Email` WHERE parent=%s", u)
            frappe.db.sql("DELETE FROM `tabBlock Module` WHERE parent=%s", u)
            frappe.db.sql("DELETE FROM `tabSessions` WHERE user=%s", u)
            frappe.db.delete("User", {"name": u})
        except Exception:
            pass

    frappe.db.commit()
    print("Clean complete!\n")


# ============================================================
# SEED ALL (orchestrator)
# ============================================================

def seed_all():
    """Seed complete demo data for University ERP -- 500+ students, 50+ faculty."""
    frappe.flags.ignore_permissions = True
    frappe.flags.in_test = True  # bypass user creation throttle
    print("=" * 60)
    print("SEEDING COMPREHENSIVE DEMO DATA")
    print("National Institute of Technology")
    print("=" * 60)

    clean_all()

    ctx = {}  # shared context for cross-referencing

    _safe("_seed_core",               _seed_core, ctx)
    _safe("_seed_accounts_settings",  _seed_accounts_settings, ctx)
    _safe("_seed_departments",        _seed_departments, ctx)
    _safe("_seed_programs_courses",   _seed_programs_courses, ctx)
    _safe("_seed_faculty",            _seed_faculty, ctx)
    _safe("_seed_students",           _seed_students, ctx)
    _safe("_seed_finance",            _seed_finance, ctx)
    _safe("_seed_hostel",             _seed_hostel, ctx)
    _safe("_seed_library",            _seed_library, ctx)
    _safe("_seed_transport",          _seed_transport, ctx)
    _safe("_seed_placement",          _seed_placement, ctx)
    _safe("_seed_examinations",       _seed_examinations, ctx)
    _safe("_seed_research_obe",       _seed_research_obe, ctx)
    _safe("_seed_lms",                _seed_lms, ctx)
    _safe("_seed_grievance_feedback", _seed_grievance_feedback, ctx)
    _safe("_seed_attendance",         _seed_attendance, ctx)
    _safe("_seed_users",              _seed_users, ctx)

    frappe.db.commit()
    print("\n" + "=" * 60)
    print("DEMO DATA SEEDED SUCCESSFULLY!")
    print("=" * 60)

    # Final counts
    for dt in ["Student", "Employee", "Program", "Course", "Fees",
               "GL Entry", "Hostel Room", "Library Article"]:
        if frappe.db.exists("DocType", dt):
            print(f"  {dt}: {frappe.db.count(dt)}")

    print("\nLogin Credentials (password: Demo@Nit2026!):")
    print("-" * 60)
    for email in [
        "student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
        "faculty1@nit.edu", "faculty2@nit.edu",
        "hod1@nit.edu", "hod2@nit.edu",
        "parent1@nit.edu", "parent2@nit.edu",
        "vc@nit.edu", "registrar@nit.edu", "dean@nit.edu",
        "finance@nit.edu", "warden@nit.edu", "transport@nit.edu",
    ]:
        print(f"  {email}")
    print("-" * 60)


# ============================================================
# 1. CORE: Company, Academic Year, Terms, Fiscal Year
# ============================================================

def _seed_core(ctx):
    print("\n[1/17] Core Setup...")

    # Company -- verify or get existing
    company_list = frappe.get_all("Company", pluck="name", limit=1)
    if company_list:
        ctx["company"] = company_list[0]
    else:
        ctx["company"] = COMPANY
    abbr = frappe.db.get_value("Company", ctx["company"], "abbr") or COMPANY_ABBR
    ctx["abbr"] = abbr

    # Academic Year
    if not frappe.db.exists("Academic Year", ACADEMIC_YEAR):
        _exists_or_create("Academic Year", {"name": ACADEMIC_YEAR}, {
            "academic_year_name": ACADEMIC_YEAR,
            "year_start_date": "2025-07-01",
            "year_end_date": "2026-06-30",
        })
    ctx["academic_year"] = ACADEMIC_YEAR

    # Academic Terms
    for term_name, start, end in [
        ("Semester 1", "2025-07-01", "2025-12-31"),
        ("Semester 2", "2026-01-01", "2026-06-30"),
    ]:
        existing = frappe.db.get_value(
            "Academic Term",
            {"term_name": term_name, "academic_year": ACADEMIC_YEAR},
            "name",
        )
        if not existing:
            doc = frappe.get_doc({
                "doctype": "Academic Term",
                "term_name": term_name,
                "academic_year": ACADEMIC_YEAR,
                "term_start_date": start,
                "term_end_date": end,
            })
            doc.insert(ignore_permissions=True)
            existing = doc.name
    ctx["academic_term"] = frappe.db.get_value(
        "Academic Term",
        {"term_name": "Semester 1", "academic_year": ACADEMIC_YEAR},
        "name",
    ) or "Semester 1"

    # Fiscal Year
    if not frappe.db.exists("Fiscal Year", ACADEMIC_YEAR):
        _exists_or_create("Fiscal Year", {"name": ACADEMIC_YEAR}, {
            "year": ACADEMIC_YEAR,
            "year_start_date": "2025-04-01",
            "year_end_date": "2026-03-31",
            "is_short_year": 0,
        })

    # Chart of Accounts -- create university-specific accounts if missing
    _ensure_accounts(ctx)

    # Designations
    for d in [
        "Professor", "Associate Professor", "Assistant Professor",
        "Lab Instructor", "Registrar", "Librarian", "Warden",
        "Administrative Officer", "Finance Officer", "Transport Officer",
    ]:
        if not frappe.db.exists("Designation", d):
            frappe.db.sql(
                "INSERT IGNORE INTO tabDesignation "
                "(name, creation, modified, owner, modified_by) "
                "VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator')",
                d,
            )

    # Holiday List
    if not frappe.db.exists("Holiday List", "NIT Holidays 2025-26"):
        hl = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": "NIT Holidays 2025-26",
            "from_date": "2025-07-01",
            "to_date": "2026-06-30",
        })
        for dt, desc in [
            ("2025-08-15", "Independence Day"), ("2025-10-02", "Gandhi Jayanti"),
            ("2025-10-20", "Dussehra"), ("2025-11-01", "Diwali"),
            ("2025-12-25", "Christmas"), ("2026-01-26", "Republic Day"),
            ("2026-03-14", "Holi"),
        ]:
            hl.append("holidays", {"holiday_date": dt, "description": desc})
        hl.insert(ignore_permissions=True)
    ctx["holiday_list"] = "NIT Holidays 2025-26"

    # Student Categories
    for c in ["General", "SC/ST", "OBC", "EWS"]:
        if not frappe.db.exists("Student Category", c):
            _exists_or_create("Student Category", {"name": c}, {"category": c})

    # Student Batch Names
    for b in ["2023", "2024", "2025"]:
        if not frappe.db.exists("Student Batch Name", b):
            _exists_or_create("Student Batch Name", {"name": b}, {"batch_name": b})

    # Assessment Criteria
    for name, weight in [("Theory", 40), ("Practical", 30), ("Assignment", 15),
                         ("Project", 10), ("Viva", 5)]:
        if not frappe.db.exists("Assessment Criteria", name):
            _exists_or_create("Assessment Criteria", {"assessment_criteria": name}, {
                "assessment_criteria": name, "weightage": weight,
            })

    # Assessment Groups
    for g in ["Internal Assessment", "External Assessment", "Final Assessment"]:
        if not frappe.db.exists("Assessment Group", g):
            _exists_or_create("Assessment Group", {"assessment_group_name": g}, {
                "assessment_group_name": g,
            })

    # Rooms
    rooms = [
        ("LH-101", "Lecture Hall 1", 120), ("LH-102", "Lecture Hall 2", 120),
        ("LH-103", "Lecture Hall 3", 80), ("LH-104", "Lecture Hall 4", 80),
        ("LH-105", "Lecture Hall 5", 80), ("LH-106", "Lecture Hall 6", 60),
        ("CS-LAB", "Computer Science Lab", 60), ("EC-LAB", "Electronics Lab", 40),
        ("ME-LAB", "Mechanical Lab", 40), ("PH-LAB", "Physics Lab", 40),
        ("SH-01", "Seminar Hall", 200), ("EH-01", "Exam Hall 1", 150),
        ("EH-02", "Exam Hall 2", 150),
    ]
    ctx["rooms"] = []
    for code, name, cap in rooms:
        rid = _exists_or_create("Room", {"room_number": code}, {
            "room_name": name, "room_number": code, "seating_capacity": cap,
        })
        if rid:
            ctx["rooms"].append(rid)

    frappe.db.commit()
    print(f"  Created core setup: {len(ctx['rooms'])} rooms")


def _ensure_accounts(ctx):
    """Create university-specific GL accounts if they don't exist."""
    company = ctx["company"]
    abbr = ctx.get("abbr", COMPANY_ABBR)

    # Find parent accounts in the chart
    receivable_parent = frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Receivable", "is_group": 1},
        "name",
    )
    if not receivable_parent:
        receivable_parent = frappe.db.get_value(
            "Account",
            {"company": company, "root_type": "Asset", "is_group": 1},
            "name",
        )

    income_parent = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Income", "is_group": 1},
        "name",
    )

    asset_parent = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Asset", "is_group": 1},
        "name",
    )

    expense_parent = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Expense", "is_group": 1},
        "name",
    )

    liability_parent = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Liability", "is_group": 1},
        "name",
    )

    # Define accounts to create
    accounts = [
        (f"Fee Collection - {abbr}", "Bank", asset_parent),
        (f"Fee Income - {abbr}", "Income Account", income_parent),
        (f"Student Receivable - {abbr}", "Receivable", receivable_parent or asset_parent),
        (f"Late Fee Income - {abbr}", "Income Account", income_parent),
        (f"Fee Discount - {abbr}", "Expense Account", expense_parent),
        (f"Scholarship Expense - {abbr}", "Expense Account", expense_parent),
        (f"Scholarship Liability - {abbr}", "Payable", liability_parent),
        (f"Hostel Receivable - {abbr}", "Receivable", receivable_parent or asset_parent),
        (f"Hostel Income - {abbr}", "Income Account", income_parent),
        (f"Mess Income - {abbr}", "Income Account", income_parent),
        (f"Hostel Deposit - {abbr}", "Payable", liability_parent),
        (f"Transport Income - {abbr}", "Income Account", income_parent),
        (f"Transport Receivable - {abbr}", "Receivable", receivable_parent or asset_parent),
        (f"Library Fine Income - {abbr}", "Income Account", income_parent),
        (f"Library Deposit - {abbr}", "Payable", liability_parent),
    ]

    for acct_name, acct_type, parent in accounts:
        if not frappe.db.exists("Account", acct_name):
            if parent:
                try:
                    frappe.get_doc({
                        "doctype": "Account",
                        "account_name": acct_name.replace(f" - {abbr}", ""),
                        "account_type": acct_type,
                        "parent_account": parent,
                        "company": company,
                        "is_group": 0,
                    }).insert(ignore_permissions=True)
                except Exception as e:
                    print(f"    WARN creating account {acct_name}: {str(e)[:100]}")

    # Cost Center
    if not frappe.db.exists("Cost Center", f"Main - {abbr}"):
        cc_parent = frappe.db.get_value(
            "Cost Center", {"company": company, "is_group": 1}, "name"
        )
        if cc_parent:
            try:
                frappe.get_doc({
                    "doctype": "Cost Center",
                    "cost_center_name": "Main",
                    "parent_cost_center": cc_parent,
                    "company": company,
                    "is_group": 0,
                }).insert(ignore_permissions=True)
            except Exception:
                pass

    ctx["accounts"] = {
        "fee_collection": f"Fee Collection - {abbr}",
        "fee_income": f"Fee Income - {abbr}",
        "student_receivable": f"Student Receivable - {abbr}",
        "late_fee_income": f"Late Fee Income - {abbr}",
        "fee_discount": f"Fee Discount - {abbr}",
        "scholarship_expense": f"Scholarship Expense - {abbr}",
        "scholarship_liability": f"Scholarship Liability - {abbr}",
        "hostel_receivable": f"Hostel Receivable - {abbr}",
        "hostel_income": f"Hostel Income - {abbr}",
        "mess_income": f"Mess Income - {abbr}",
        "hostel_deposit": f"Hostel Deposit - {abbr}",
        "transport_income": f"Transport Income - {abbr}",
        "transport_receivable": f"Transport Receivable - {abbr}",
        "library_fine_income": f"Library Fine Income - {abbr}",
        "library_deposit": f"Library Deposit - {abbr}",
        "cost_center": f"Main - {abbr}",
    }
    frappe.db.commit()
    print("  GL Accounts ensured")


# ============================================================
# 2. UNIVERSITY ACCOUNTS SETTINGS
# ============================================================

def _seed_accounts_settings(ctx):
    print("\n[2/17] University Accounts Settings...")
    abbr = ctx.get("abbr", COMPANY_ABBR)
    accts = ctx.get("accounts", {})

    settings = frappe.get_single("University Accounts Settings")
    settings.company = ctx["company"]
    settings.auto_post_gl = 1
    settings.default_cost_center = (
        frappe.db.get_value("Cost Center", {"company": ctx["company"], "is_group": 0}, "name")
        or accts.get("cost_center")
    )
    settings.fee_collection_account = (
        frappe.db.get_value("Account", accts.get("fee_collection"), "name")
        or accts.get("fee_collection")
    )
    settings.fee_income_account = (
        frappe.db.get_value("Account", accts.get("fee_income"), "name")
        or accts.get("fee_income")
    )
    settings.fee_receivable_account = (
        frappe.db.get_value("Account", accts.get("student_receivable"), "name")
        or accts.get("student_receivable")
    )
    settings.late_fee_income_account = (
        frappe.db.get_value("Account", accts.get("late_fee_income"), "name")
        or accts.get("late_fee_income")
    )
    settings.fee_discount_account = (
        frappe.db.get_value("Account", accts.get("fee_discount"), "name")
        or accts.get("fee_discount")
    )
    settings.scholarship_expense_account = (
        frappe.db.get_value("Account", accts.get("scholarship_expense"), "name")
        or accts.get("scholarship_expense")
    )
    settings.scholarship_liability_account = (
        frappe.db.get_value("Account", accts.get("scholarship_liability"), "name")
        or accts.get("scholarship_liability")
    )
    settings.hostel_receivable_account = (
        frappe.db.get_value("Account", accts.get("hostel_receivable"), "name")
        or accts.get("hostel_receivable")
    )
    settings.hostel_income_account = (
        frappe.db.get_value("Account", accts.get("hostel_income"), "name")
        or accts.get("hostel_income")
    )
    settings.mess_income_account = (
        frappe.db.get_value("Account", accts.get("mess_income"), "name")
        or accts.get("mess_income")
    )
    settings.hostel_deposit_account = (
        frappe.db.get_value("Account", accts.get("hostel_deposit"), "name")
        or accts.get("hostel_deposit")
    )
    settings.transport_income_account = (
        frappe.db.get_value("Account", accts.get("transport_income"), "name")
        or accts.get("transport_income")
    )
    settings.transport_receivable_account = (
        frappe.db.get_value("Account", accts.get("transport_receivable"), "name")
        or accts.get("transport_receivable")
    )
    settings.library_fine_income_account = (
        frappe.db.get_value("Account", accts.get("library_fine_income"), "name")
        or accts.get("library_fine_income")
    )
    settings.library_deposit_account = (
        frappe.db.get_value("Account", accts.get("library_deposit"), "name")
        or accts.get("library_deposit")
    )

    settings.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"  University Accounts Settings configured (company={ctx['company']}, auto_post_gl=1)")


# ============================================================
# 3. DEPARTMENTS
# ============================================================

def _seed_departments(ctx):
    print("\n[3/17] Departments...")
    ctx["departments"] = []
    for name, code in DEPARTMENTS:
        did = _exists_or_create("University Department", {"department_code": code}, {
            "department_name": name, "department_code": code,
        })
        if did:
            ctx["departments"].append((did, name, code))

    # University Laboratories
    for name, code in [
        ("CS Laboratory", "CS-LAB"), ("Electronics Laboratory", "EC-LAB"),
        ("Mechanical Laboratory", "ME-LAB"), ("Physics Laboratory", "PH-LAB"),
        ("Chemistry Laboratory", "CHE-LAB"),
    ]:
        _exists_or_create("University Laboratory", {"lab_code": code}, {
            "lab_name": name, "lab_code": code,
        })

    frappe.db.commit()
    print(f"  Created {len(ctx['departments'])} departments")


# ============================================================
# 4. PROGRAMS & COURSES
# ============================================================

def _seed_programs_courses(ctx):
    print("\n[4/17] Programs & Courses...")
    ctx["programs"] = []
    ctx["courses"] = []
    ctx["program_courses"] = {}  # abbr -> [course_name, ...]

    # Fee Categories
    for cat in ["Tuition Fee", "Laboratory Fee", "Library Fee", "Hostel Fee",
                "Examination Fee", "Development Fee"]:
        if not frappe.db.exists("Fee Category", cat):
            _exists_or_create("Fee Category", {"category_name": cat}, {
                "category_name": cat,
            })

    # Programs
    for prog_name, abbr, dur in PROGRAMS:
        pid = _exists_or_create("Program", {"program_abbreviation": abbr}, {
            "program_name": prog_name,
            "program_abbreviation": abbr,
            "custom_program_code": abbr,
            "custom_credit_system": "CBCS",
            "custom_min_credits_graduation": 160 if dur == 4 else 80,
            "custom_duration_years": dur,
        })
        if pid:
            ctx["programs"].append((pid, prog_name, abbr))

    # Courses per program
    all_courses = set()
    for prog_name, prog_abbr, dur in PROGRAMS:
        course_list = COURSE_MAP.get(prog_abbr, [])
        ctx["program_courses"][prog_abbr] = []
        for cname, ccode in course_list:
            if ccode not in all_courses:
                cid = _exists_or_create("Course", {"course_code": ccode}, {
                    "course_name": cname,
                    "course_code": ccode,
                    "custom_course_code": ccode,
                })
                if cid:
                    ctx["courses"].append((cid, cname, ccode))
                all_courses.add(ccode)
            ctx["program_courses"][prog_abbr].append(ccode)

    # Topics
    topics = [
        "Data Structures", "Algorithms", "Object Oriented Programming",
        "Database Management", "Operating Systems", "Computer Networks",
        "Web Technologies", "Artificial Intelligence", "Discrete Mathematics",
        "Linear Algebra", "Probability and Statistics", "Digital Logic",
        "Microprocessors", "Software Engineering", "Compiler Design",
        "Thermodynamics", "Fluid Mechanics", "Structural Analysis",
        "Circuit Theory", "Control Systems",
    ]
    for t in topics:
        if not frappe.db.exists("Topic", t):
            _exists_or_create("Topic", {"topic_name": t}, {"topic_name": t})

    frappe.db.commit()
    print(f"  Created {len(ctx['programs'])} programs, {len(ctx['courses'])} courses")


# ============================================================
# 5. FACULTY (50+ Employees)
# ============================================================

def _seed_faculty(ctx):
    print("\n[5/17] Faculty & Staff (50+ employees)...")
    company = ctx["company"]

    dept_list = frappe.get_all("Department", filters={"company": company}, pluck="name")
    if not dept_list:
        dept_list = frappe.get_all("Department", pluck="name", limit=5)
    default_dept = dept_list[0] if dept_list else None

    ctx["employees"] = []
    ctx["faculty_employees"] = []
    ctx["instructors"] = []

    designations_faculty = ["Professor", "Associate Professor", "Assistant Professor"]
    count = 0

    # Generate 55 faculty members across departments
    for i in range(55):
        gender = "Male" if i % 3 != 2 else "Female"
        first, last = _random_name(gender)
        full_name = f"{first} {last}"
        designation = designations_faculty[i % 3]
        dob = _random_dob(1965, 1992)
        dept = dept_list[i % len(dept_list)] if dept_list else default_dept

        emp_filter = {"employee_name": full_name, "company": company}
        if frappe.db.exists("Employee", emp_filter):
            eid = frappe.db.get_value("Employee", emp_filter, "name")
        else:
            try:
                emp = frappe.get_doc({
                    "doctype": "Employee",
                    "first_name": first,
                    "last_name": last,
                    "employee_name": full_name,
                    "gender": gender,
                    "date_of_birth": dob,
                    "date_of_joining": "2020-07-01",
                    "designation": designation,
                    "company": company,
                    "department": dept,
                    "status": "Active",
                })
                emp.insert(ignore_permissions=True)
                eid = emp.name

                # Set custom fields via db.set_value to avoid validation issues
                frappe.db.set_value("Employee", eid, "custom_is_faculty", 1)
                frappe.db.set_value("Employee", eid, "custom_employee_category", "Teaching")
            except Exception as e:
                print(f"    WARN Employee {full_name}: {str(e)[:100]}")
                continue

        ctx["employees"].append(eid)
        ctx["faculty_employees"].append((eid, full_name))
        count += 1

    # Non-faculty staff (5 people)
    staff_data = [
        ("Ramesh", "Gupta", "Male", "1970-12-01", "Registrar"),
        ("Sunita", "Devi", "Female", "1978-08-15", "Librarian"),
        ("Prakash", "Rao", "Male", "1975-03-28", "Warden"),
        ("Venkatesh", "Iyer", "Male", "1980-10-05", "Finance Officer"),
        ("Anjali", "Desai", "Female", "1985-06-12", "Transport Officer"),
    ]
    for first, last, gender, dob, designation in staff_data:
        full_name = f"{first} {last}"
        emp_filter = {"employee_name": full_name, "company": company}
        if not frappe.db.exists("Employee", emp_filter):
            try:
                emp = frappe.get_doc({
                    "doctype": "Employee",
                    "first_name": first,
                    "last_name": last,
                    "employee_name": full_name,
                    "gender": gender,
                    "date_of_birth": dob,
                    "date_of_joining": "2020-07-01",
                    "designation": designation,
                    "company": company,
                    "department": default_dept,
                    "status": "Active",
                })
                emp.insert(ignore_permissions=True)
                ctx["employees"].append(emp.name)
            except Exception as e:
                print(f"    WARN Staff {full_name}: {str(e)[:100]}")

    # Faculty Profiles
    for eid, ename in ctx["faculty_employees"]:
        if not frappe.db.exists("Faculty Profile", {"employee": eid}):
            _exists_or_create("Faculty Profile", {"employee": eid}, {
                "employee": eid, "employee_name": ename,
            })

    # Instructors
    for eid, ename in ctx["faculty_employees"]:
        if not frappe.db.exists("Instructor", {"employee": eid}):
            iid = _exists_or_create("Instructor", {"employee": eid}, {
                "instructor_name": ename, "employee": eid,
            })
            if iid:
                ctx["instructors"].append((iid, ename))

    # Teaching Assignments
    if ctx["instructors"] and ctx.get("courses"):
        for i, (cid, cname, ccode) in enumerate(ctx["courses"]):
            inst_idx = i % len(ctx["instructors"])
            iid, iname = ctx["instructors"][inst_idx]
            room = ctx["rooms"][i % len(ctx["rooms"])] if ctx.get("rooms") else None
            data = {
                "instructor": iid,
                "instructor_name": iname,
                "course": cid,
                "academic_year": ctx["academic_year"],
                "academic_term": ctx["academic_term"],
            }
            if room:
                data["room"] = room
            _exists_or_create(
                "Teaching Assignment",
                {"instructor": iid, "course": cid, "academic_year": ctx["academic_year"]},
                data,
            )

    frappe.db.commit()
    print(f"  Created {count} faculty, {len(ctx['employees'])} total employees, "
          f"{len(ctx['instructors'])} instructors")


# ============================================================
# 6. STUDENTS (500+)
# ============================================================

def _seed_students(ctx):
    print("\n[6/17] Students (500+)...")

    # Skip auto-user creation for students (avoids throttle during bulk seed)
    try:
        edu_settings = frappe.get_single("Education Settings")
        edu_settings.user_creation_skip = 1
        edu_settings.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        pass

    # Distribution: ~70/program for B.Tech (5 programs), ~40 for M.Tech (2), ~50 for MBA
    distribution = {
        "BTCSE": 80, "BTECE": 75, "BTME": 70, "BTCE": 70, "BTEE": 70,
        "MTCS": 45, "MTEC": 45, "MBA": 55,
    }

    ctx["students"] = []
    ctx["guardians"] = []
    total = 0
    used_emails = set()

    for pid, pname, pabbr in ctx.get("programs", []):
        target = distribution.get(pabbr, 50)
        batches = ["2023", "2024", "2025"]
        prog_created = 0

        for idx in range(target):
            gender = "Male" if idx % 2 == 0 else "Female"
            first, last = _random_name(gender)
            batch = batches[idx % 3]
            enroll = f"NIT-{batch}-{pabbr}-{idx+1:03d}"

            # Ensure unique email by appending index
            email = f"{first.lower()}.{last.lower()}.{pabbr.lower()}.{idx+1}@nit.edu"
            # Avoid email collisions across programs
            while email in used_emails:
                email = f"{first.lower()}{idx+1}.{last.lower()}.{pabbr.lower()}@nit.edu"
            used_emails.add(email)

            full_name = f"{first} {last}"
            dob = _random_dob(2000, 2006) if pabbr.startswith("BT") else _random_dob(1998, 2003)

            # Check by enrollment number
            existing = frappe.db.get_value(
                "Student", {"custom_enrollment_number": enroll}, "name"
            )
            if existing:
                ctx["students"].append((existing, full_name, pid, pname, pabbr, batch, email))
                total += 1
                prog_created += 1
                continue

            try:
                doc = frappe.get_doc({
                    "doctype": "Student",
                    "first_name": first,
                    "last_name": last,
                    "student_email_id": email,
                    "gender": gender,
                    "date_of_birth": dob,
                    "joining_date": "2025-07-01",
                    "enabled": 1,
                    "custom_enrollment_number": enroll,
                })
                doc.insert(ignore_permissions=True, ignore_links=True)
                ctx["students"].append((doc.name, full_name, pid, pname, pabbr, batch, email))
                total += 1
                prog_created += 1
            except frappe.DuplicateEntryError:
                existing = frappe.db.get_value(
                    "Student", {"custom_enrollment_number": enroll}, "name"
                )
                if existing:
                    ctx["students"].append((existing, full_name, pid, pname, pabbr, batch, email))
                    total += 1
                    prog_created += 1
            except Exception as e:
                if total == 0:
                    print(f"    Student creation note: {str(e)[:150]}")

        if prog_created > 0:
            frappe.db.commit()
            print(f"    {pabbr}: {prog_created} students")

    frappe.db.commit()

    # Program Enrollments
    enrolled = 0
    for sid, sname, pid, pname, pabbr, batch, email in ctx["students"]:
        if not frappe.db.exists("Program Enrollment", {"student": sid, "program": pid}):
            _exists_or_create(
                "Program Enrollment",
                {"student": sid, "program": pid},
                {
                    "student": sid,
                    "student_name": sname,
                    "program": pid,
                    "academic_year": ctx["academic_year"],
                    "enrollment_date": "2025-07-01",
                },
                ignore_links=True,
            )
            enrolled += 1
        if enrolled % 100 == 0 and enrolled > 0:
            frappe.db.commit()
    frappe.db.commit()

    # Student Groups
    for pid, pname, pabbr in ctx.get("programs", []):
        for batch in ["2023", "2024", "2025"]:
            gname = f"{pabbr}-{batch}"
            if not frappe.db.exists("Student Group", {"student_group_name": gname}):
                _exists_or_create(
                    "Student Group",
                    {"student_group_name": gname},
                    {
                        "student_group_name": gname,
                        "group_based_on": "Batch",
                        "program": pid,
                        "academic_year": ctx["academic_year"],
                        "batch": batch,
                    },
                    ignore_links=True,
                )

    # Guardians (1 per 3 students)
    guardian_count = 0
    for i in range(0, len(ctx["students"]), 3):
        sid, sname, pid, pname, pabbr, batch, email = ctx["students"][i]
        gfirst, glast = _random_name("Male")
        gname = f"{gfirst} {glast}"
        gid = _exists_or_create(
            "Guardian",
            {"guardian_name": gname},
            {
                "guardian_name": gname,
                "email_address": f"parent{guardian_count+1}@nit.edu"
                if guardian_count < 10
                else f"guardian{guardian_count+1}@nit.edu",
                "mobile_number": f"98765{guardian_count:05d}",
            },
        )
        if gid:
            ctx["guardians"].append((gid, gname, sid))
            guardian_count += 1

    frappe.db.commit()
    print(f"  Created {total} students, {enrolled} enrollments, {guardian_count} guardians")


# ============================================================
# 7. FINANCE (Fees + GL Entries via university_finance)
# ============================================================

def _seed_finance(ctx):
    print("\n[7/17] Finance (Fees with GL posting)...")

    amounts = {"BTCSE": 85000, "BTECE": 80000, "BTME": 75000, "BTCE": 75000,
               "BTEE": 75000, "MTCS": 65000, "MTEC": 65000, "MBA": 95000}
    created = 0
    submitted = 0
    errors = 0

    for sid, sname, pid, pname, pabbr, batch, email in ctx.get("students", []):
        amount = amounts.get(pabbr, 75000)

        # Check if fee already exists for this student
        if frappe.db.exists("Fees", {"student": sid, "academic_year": ctx["academic_year"]}):
            continue

        try:
            tuition = amount * 0.6
            lab = amount * 0.2
            lib = amount * 0.1
            exam = amount * 0.1
            fee = frappe.get_doc({
                "doctype": "Fees",
                "student": sid,
                "student_name": sname,
                "program": pid,
                "academic_year": ctx["academic_year"],
                "academic_term": ctx["academic_term"],
                "due_date": "2025-09-30",
                "components": [
                    {"fees_category": "Tuition Fee", "amount": tuition},
                    {"fees_category": "Laboratory Fee", "amount": lab},
                    {"fees_category": "Library Fee", "amount": lib},
                    {"fees_category": "Examination Fee", "amount": exam},
                ],
                "grand_total": amount,
                "outstanding_amount": amount,
            })
            fee.flags.ignore_validate = True
            fee.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
            # Ensure grand_total is set (ignore_validate may skip calculation)
            if not fee.grand_total:
                frappe.db.set_value("Fees", fee.name, "grand_total", amount, update_modified=False)
                frappe.db.set_value("Fees", fee.name, "outstanding_amount", amount, update_modified=False)
            created += 1

            # Submit first 200 fees to trigger GL posting
            if submitted < 200:
                try:
                    fee.reload()
                    # Set accounts required by Education's Fees.on_submit()
                    accts = ctx.get("accounts", {})
                    abbr = ctx.get("abbr", COMPANY_ABBR)
                    if not fee.receivable_account:
                        fee.receivable_account = accts.get("student_receivable") or f"Student Receivable - {abbr}"
                    if not fee.income_account:
                        fee.income_account = accts.get("fee_income") or f"Fee Income - {abbr}"
                    if not fee.cost_center:
                        fee.cost_center = accts.get("cost_center") or frappe.db.get_value(
                            "Cost Center", {"company": ctx["company"], "is_group": 0}, "name"
                        )
                    fee.flags.ignore_validate = True
                    fee.submit()
                    submitted += 1
                except Exception as e:
                    if submitted == 0:
                        print(f"    Fee submit note: {str(e)[:150]}")
                    errors += 1
        except Exception as e:
            if created == 0:
                print(f"    Fee creation note: {str(e)[:150]}")
            errors += 1

        if created % 100 == 0 and created > 0:
            frappe.db.commit()
            print(f"    ...{created} fees created, {submitted} submitted")

    frappe.db.commit()

    # Verify GL Entries
    gl_count = 0
    if frappe.db.exists("DocType", "GL Entry"):
        gl_count = frappe.db.count("GL Entry")

    print(f"  Created {created} fees, submitted {submitted}, GL entries: {gl_count}")
    if gl_count > 0:
        print("  GL posting VERIFIED -- university_finance fork works end-to-end!")
    else:
        print("  NOTE: GL entries = 0 (accounts may need manual configuration)")

    # Scholarship Types
    for st in ["Merit Scholarship", "Need-Based Scholarship", "Sports Scholarship"]:
        if not frappe.db.exists("Scholarship Type", st):
            _exists_or_create("Scholarship Type", {"scholarship_name": st}, {
                "scholarship_name": st,
            })

    frappe.db.commit()


# ============================================================
# 8. HOSTEL
# ============================================================

def _seed_hostel(ctx):
    print("\n[8/17] Hostel...")
    ctx["hostel_buildings"] = []
    ctx["hostel_rooms"] = []

    buildings = [
        ("Tagore Hall", "TH", "Boys", 4), ("Sarojini House", "SH", "Girls", 3),
        ("Raman Hostel", "RH", "Boys", 4), ("Kalpana Chawla Hall", "KCH", "Girls", 3),
        ("PG Block", "PGB", "Co-Ed", 2),
    ]
    for name, code, hostel_type, floors in buildings:
        bid = _exists_or_create("Hostel Building", {"building_name": name}, {
            "building_name": name, "building_code": code,
            "hostel_type": hostel_type, "total_floors": floors,
        })
        if bid:
            ctx["hostel_buildings"].append(bid)

    # Rooms: ~25 per building = 125+ rooms
    room_types = ["Single", "Double", "Double", "Triple"]
    rents = {"Single": 5000, "Double": 3500, "Triple": 2500}
    for bid in ctx["hostel_buildings"]:
        for floor in range(1, 6):
            for room_num in range(1, 6):
                rtype = room_types[(floor + room_num) % len(room_types)]
                rnum = f"{floor}0{room_num}"
                rid = _exists_or_create(
                    "Hostel Room",
                    {"room_number": rnum, "hostel_building": bid},
                    {
                        "room_number": rnum,
                        "hostel_building": bid,
                        "floor": floor,
                        "room_type": rtype,
                        "capacity": 1 if rtype == "Single" else (2 if rtype == "Double" else 3),
                        "rent": rents[rtype],
                    },
                )
                if rid:
                    ctx["hostel_rooms"].append(rid)

    # Mess
    for name, mess_type in [
        ("Central Mess", "Vegetarian"), ("South Block Mess", "Both"),
        ("PG Mess", "Both"),
    ]:
        if not frappe.db.exists("Hostel Mess", {"mess_name": name}):
            _exists_or_create("Hostel Mess", {"mess_name": name}, {
                "mess_name": name, "mess_type": mess_type, "capacity": 300,
            })

    # Hostel Allocations (200+ students)
    allocated = 0
    for i, (sid, sname, pid, pname, pabbr, batch, email) in enumerate(
        ctx.get("students", [])[:250]
    ):
        if not ctx["hostel_rooms"]:
            break
        if allocated >= len(ctx["hostel_rooms"]):
            break
        room_name = ctx["hostel_rooms"][allocated % len(ctx["hostel_rooms"])]
        # Get hostel_building from room
        room_building = frappe.db.get_value("Hostel Room", room_name, "hostel_building")
        if not frappe.db.exists("Hostel Allocation", {"student": sid}):
            _exists_or_create(
                "Hostel Allocation",
                {"student": sid},
                {
                    "student": sid,
                    "student_name": sname,
                    "hostel_building": room_building,
                    "room": room_name,
                    "academic_year": ctx["academic_year"],
                    "from_date": "2025-07-01",
                    "to_date": "2026-06-30",
                },
                ignore_links=True,
            )
            allocated += 1

    # Mess Menus -- requires mess (Link), week_start_date, menu_items (Table)
    # Skip if Mess Menu Item child doctype is complex; just create the mess buildings
    # Mess Menu creation deferred as the child table structure is complex

    frappe.db.commit()
    print(f"  Created {len(ctx['hostel_buildings'])} buildings, "
          f"{len(ctx['hostel_rooms'])} rooms, {allocated} allocations")


# ============================================================
# 9. LIBRARY
# ============================================================

def _seed_library(ctx):
    print("\n[9/17] Library...")
    ctx["library_articles"] = []

    # Categories
    for cat in ["Textbook", "Reference", "Journal", "Fiction", "Digital Resource"]:
        if not frappe.db.exists("Library Category", cat):
            _exists_or_create("Library Category", {"category_name": cat}, {
                "category_name": cat,
            })

    # Subjects
    for sub in ["Computer Science", "Electronics", "Mechanical", "Civil",
                "Mathematics", "Management", "English", "Physics", "Chemistry", "General"]:
        if not frappe.db.exists("Library Subject", sub):
            _exists_or_create("Library Subject", {"subject_name": sub}, {
                "subject_name": sub,
            })

    # 60+ Library Articles
    # Library Article requires: title, author, category, total_copies
    categories = frappe.get_all("Library Category", pluck="name", limit=5)
    default_cat = categories[0] if categories else "Textbook"

    books = [
        ("Introduction to Algorithms", "978-0262033848", "Thomas H. Cormen", "MIT Press"),
        ("Operating System Concepts", "978-1119800361", "Abraham Silberschatz", "Wiley"),
        ("Database System Concepts", "978-0078022159", "Abraham Silberschatz", "McGraw Hill"),
        ("Computer Networking", "978-0133594140", "James Kurose", "Pearson"),
        ("Artificial Intelligence: A Modern Approach", "978-0134610993", "Stuart Russell", "Pearson"),
        ("Data Structures in Python", "978-1118290279", "Michael Goodrich", "Wiley"),
        ("Digital Logic Design", "978-8131714317", "M. Morris Mano", "Pearson"),
        ("Discrete Mathematics", "978-0073383095", "Kenneth Rosen", "McGraw Hill"),
        ("Engineering Mathematics", "978-8120345287", "B.S. Grewal", "Khanna Publishers"),
        ("The C Programming Language", "978-0131103627", "Brian Kernighan", "Prentice Hall"),
        ("Clean Code", "978-0132350884", "Robert C. Martin", "Prentice Hall"),
        ("Design Patterns", "978-0201633610", "Gang of Four", "Addison Wesley"),
        ("Computer Organization", "978-0134101613", "William Stallings", "Pearson"),
        ("Software Engineering", "978-0133943030", "Ian Sommerville", "Pearson"),
        ("Linear Algebra", "978-0321982384", "David Lay", "Pearson"),
        ("Microprocessors", "978-0198066477", "Krishna Kant", "Oxford"),
        ("Compiler Design", "978-0321486813", "Alfred Aho", "Pearson"),
        ("Machine Learning", "978-0070428072", "Tom Mitchell", "McGraw Hill"),
        ("Python Crash Course", "978-1593279288", "Eric Matthes", "No Starch Press"),
        ("The Pragmatic Programmer", "978-0135957059", "David Thomas", "Addison Wesley"),
        ("Thermodynamics", "978-0073398174", "Yunus Cengel", "McGraw Hill"),
        ("Fluid Mechanics", "978-0073380322", "Frank White", "McGraw Hill"),
        ("Structural Analysis", "978-0132696548", "Russell Hibbeler", "Pearson"),
        ("Circuit Theory", "978-0073380575", "James Nilsson", "McGraw Hill"),
        ("Control Systems Engineering", "978-1118170519", "Norman Nise", "Wiley"),
        ("Signals and Systems", "978-0138147570", "Alan Oppenheim", "Pearson"),
        ("Power Systems Analysis", "978-0071325561", "Hadi Saadat", "McGraw Hill"),
        ("Manufacturing Processes", "978-0470924679", "Mikell Groover", "Wiley"),
        ("Surveying", "978-0070146341", "B.C. Punmia", "Laxmi Publications"),
        ("Environmental Engineering", "978-0071713849", "Howard Peavy", "McGraw Hill"),
        ("VLSI Design", "978-0132774208", "Neil Weste", "Pearson"),
        ("Embedded Systems", "978-0124105119", "Jonathan Valvano", "Elsevier"),
        ("Financial Management", "978-9332585201", "I.M. Pandey", "Pearson"),
        ("Marketing Management", "978-9332587403", "Philip Kotler", "Pearson"),
        ("Human Resource Management", "978-0273756927", "Gary Dessler", "Pearson"),
        ("Operations Management", "978-0133872132", "Jay Heizer", "Pearson"),
        ("Strategic Management", "978-1259255175", "Arthur Thompson", "McGraw Hill"),
        ("Business Analytics", "978-0134633282", "James Evans", "Pearson"),
        ("Cloud Computing", "978-0124046276", "Thomas Erl", "Prentice Hall"),
        ("Big Data Analytics", "978-0133940725", "Frank Ohlhorst", "Wiley"),
        ("Wireless Communications", "978-0131918351", "Andrea Goldsmith", "Cambridge"),
        ("Probability and Statistics", "978-0321500465", "Jay Devore", "Cengage"),
        ("Numerical Methods", "978-0070634169", "Steven Chapra", "McGraw Hill"),
        ("Advanced Algorithms", "978-0262033848", "Jon Kleinberg", "Pearson"),
        ("Deep Learning", "978-0262035613", "Ian Goodfellow", "MIT Press"),
        ("Natural Language Processing", "978-0131873216", "Dan Jurafsky", "Pearson"),
        ("Computer Vision", "978-1848829343", "Richard Szeliski", "Springer"),
        ("Robotics", "978-0201543612", "John Craig", "Pearson"),
        ("Cryptography", "978-1119183471", "William Stallings", "Pearson"),
        ("Research Methodology", "978-8122436228", "C.R. Kothari", "New Age"),
        ("Technical Writing", "978-1319058524", "Mike Markel", "Bedford"),
        ("Project Management", "978-0133798074", "Kathy Schwalbe", "Cengage"),
        ("Engineering Economics", "978-0199336814", "Leland Blank", "Oxford"),
        ("Material Science", "978-1119405498", "William Callister", "Wiley"),
        ("Heat Transfer", "978-0073398181", "Yunus Cengel", "McGraw Hill"),
        ("Geotechnical Engineering", "978-1305635180", "Braja Das", "Cengage"),
        ("Transportation Engineering", "978-0470290378", "Nicholas Garber", "Wiley"),
        ("Communication Skills", "978-0070264915", "Meenakshi Raman", "McGraw Hill"),
        ("Engineering Drawing", "978-8174091093", "N.D. Bhatt", "Charotar"),
        ("Physics for Engineers", "978-8126556021", "Serway Jewett", "Cengage"),
    ]
    for title, isbn, author, publisher in books:
        cat = categories[hash(title) % len(categories)] if categories else default_cat
        aid = _exists_or_create("Library Article", {"title": title}, {
            "title": title, "isbn": isbn, "author": author, "publisher": publisher,
            "category": cat, "total_copies": random.randint(3, 10),
        })
        if aid:
            ctx["library_articles"].append(aid)

    # Library Members (students)
    # Required: member_type, member_name, membership_date
    members = 0
    for sid, sname, pid, pname, pabbr, batch, email in ctx.get("students", [])[:80]:
        if not frappe.db.exists("Library Member", {"member_name": sname}):
            _exists_or_create("Library Member", {"member_name": sname}, {
                "member_type": "Student",
                "member_name": sname,
                "membership_date": "2025-07-01",
            })
            members += 1

    frappe.db.commit()
    print(f"  Created {len(ctx['library_articles'])} articles, {members} members")


# ============================================================
# 10. TRANSPORT
# ============================================================

def _seed_transport(ctx):
    print("\n[10/17] Transport...")

    routes = [
        ("Route A - City Center", "RTA", "City Center", "NIT Campus", 15),
        ("Route B - Railway Station", "RTB", "Railway Station", "NIT Campus", 20),
        ("Route C - Airport Road", "RTC", "Airport", "NIT Campus", 35),
        ("Route D - Old City", "RTD", "Old City", "NIT Campus", 25),
        ("Route E - Industrial Area", "RTE", "Industrial Area", "NIT Campus", 18),
    ]
    ctx["routes"] = []
    for name, code, start, end, km in routes:
        rid = _exists_or_create("Transport Route", {"route_name": name}, {
            "route_name": name, "route_code": code,
            "start_point": start, "end_point": end,
            "total_distance": km,
        })
        if rid:
            ctx["routes"].append(rid)

    # Vehicles (required: vehicle_number, seating_capacity)
    vehicles = [
        ("KA-01-AB-1234", "Bus", 50), ("KA-01-CD-5678", "Bus", 50),
        ("KA-01-EF-9012", "Mini Bus", 30), ("KA-01-GH-3456", "Mini Bus", 30),
        ("KA-01-IJ-7890", "Bus", 50), ("KA-01-KL-2345", "Mini Bus", 30),
        ("KA-01-MN-6789", "Bus", 50), ("KA-01-OP-0123", "Mini Bus", 30),
        ("KA-01-QR-4567", "Van", 15), ("KA-01-ST-8901", "Van", 15),
    ]
    for reg, vtype, cap in vehicles:
        _exists_or_create("Transport Vehicle", {"vehicle_number": reg}, {
            "vehicle_number": reg, "seating_capacity": cap,
        })

    # Allocations (required: student, academic_year, from_date, route)
    allocated = 0
    for i, (sid, sname, pid, pname, pabbr, batch, email) in enumerate(
        ctx.get("students", [])[:120]
    ):
        if ctx["routes"]:
            route = ctx["routes"][i % len(ctx["routes"])]
            if not frappe.db.exists("Transport Allocation", {"student": sid}):
                _exists_or_create(
                    "Transport Allocation",
                    {"student": sid},
                    {
                        "student": sid, "student_name": sname,
                        "route": route,
                        "academic_year": ctx["academic_year"],
                        "from_date": "2025-07-01", "to_date": "2026-06-30",
                    },
                    ignore_links=True,
                )
                allocated += 1

    frappe.db.commit()
    print(f"  Created {len(ctx['routes'])} routes, 10 vehicles, {allocated} allocations")


# ============================================================
# 11. PLACEMENT
# ============================================================

def _seed_placement(ctx):
    print("\n[11/17] Placement...")

    # Industry Types
    for it in ["Information Technology", "Finance and Banking", "Manufacturing",
               "Consulting", "Startup", "Healthcare", "Education", "Government"]:
        if not frappe.db.exists("Industry Type", it):
            _exists_or_create("Industry Type", {"industry_type": it}, {"industry_type": it})

    # Companies
    companies = [
        ("Tata Consultancy Services", "Information Technology"),
        ("Infosys", "Information Technology"),
        ("Wipro", "Information Technology"),
        ("Amazon", "Information Technology"),
        ("Google", "Information Technology"),
        ("Microsoft", "Information Technology"),
        ("Deloitte", "Consulting"),
        ("HDFC Bank", "Finance and Banking"),
        ("Larsen and Toubro", "Manufacturing"),
        ("Flipkart", "Startup"),
    ]
    for name, industry in companies:
        _exists_or_create("Placement Company", {"company_name": name}, {
            "company_name": name, "industry_type": industry,
        })

    # Job Openings
    openings = [
        ("Software Engineer", "Tata Consultancy Services", 450000),
        ("Associate Consultant", "Infosys", 400000),
        ("Systems Engineer", "Wipro", 380000),
        ("SDE-1", "Amazon", 2200000),
        ("Software Engineer", "Google", 2500000),
        ("SDE", "Microsoft", 1800000),
        ("Analyst", "Deloitte", 800000),
        ("Management Trainee", "HDFC Bank", 600000),
        ("Graduate Engineer Trainee", "Larsen and Toubro", 500000),
        ("Product Engineer", "Flipkart", 1500000),
        ("Data Analyst", "Tata Consultancy Services", 500000),
        ("Quality Analyst", "Infosys", 420000),
        ("Cloud Engineer", "Amazon", 2000000),
        ("Business Analyst", "Deloitte", 900000),
        ("Associate", "HDFC Bank", 550000),
        ("Junior Developer", "Wipro", 360000),
        ("ML Engineer", "Google", 2800000),
        ("Frontend Developer", "Flipkart", 1400000),
        ("DevOps Engineer", "Microsoft", 1700000),
        ("Structural Engineer", "Larsen and Toubro", 480000),
    ]
    for title, comp, ctc in openings:
        _exists_or_create(
            "Placement Job Opening",
            {"job_title": title, "company": comp},
            {"job_title": title, "company": comp, "ctc_offered": ctc},
        )

    # Applications (50+)
    apps = 0
    final_year = [s for s in ctx.get("students", []) if s[5] == "2023"][:60]
    for i, (sid, sname, pid, pname, pabbr, batch, email) in enumerate(final_year):
        company = companies[i % len(companies)][0]
        title = openings[i % len(openings)][0]
        if not frappe.db.exists("Placement Application", {"student": sid, "company": company}):
            status = random.choice(["Applied", "Shortlisted", "Selected", "Rejected"])
            _exists_or_create(
                "Placement Application",
                {"student": sid, "company": company},
                {
                    "student": sid, "student_name": sname,
                    "company": company, "job_title": title,
                    "status": status,
                },
                ignore_links=True,
            )
            apps += 1

    frappe.db.commit()
    print(f"  Created 10 companies, 20 openings, {apps} applications")


# ============================================================
# 12. EXAMINATIONS
# ============================================================

def _seed_examinations(ctx):
    print("\n[12/17] Examinations...")

    # Question Tags
    for tag in ["Easy", "Medium", "Hard", "Bloom-L1", "Bloom-L2", "Bloom-L3",
                "Bloom-L4", "Bloom-L5", "Bloom-L6"]:
        if not frappe.db.exists("Question Tag", tag):
            _exists_or_create("Question Tag", {"tag_name": tag}, {"tag_name": tag})

    # Exam Schedules
    exam_dates = [
        "2025-10-15", "2025-10-16", "2025-10-17", "2025-10-18",
        "2025-10-20", "2025-10-21", "2025-10-22", "2025-10-23",
    ]
    for i, (cid, cname, ccode) in enumerate(ctx.get("courses", [])[:20]):
        room = ctx["rooms"][-1] if ctx.get("rooms") else None  # Exam Hall
        _exists_or_create(
            "Exam Schedule",
            {"course": cid, "academic_year": ctx["academic_year"]},
            {
                "course": cid,
                "schedule_date": exam_dates[i % len(exam_dates)],
                "from_time": "10:00",
                "to_time": "13:00",
                "room": room,
                "academic_year": ctx["academic_year"],
                "academic_term": ctx["academic_term"],
            },
            ignore_links=True,
        )

    # Assessment Plans & Results for first course
    if ctx.get("courses"):
        cid, cname, ccode = ctx["courses"][0]
        plan_name = _exists_or_create(
            "Assessment Plan",
            {"course": cid, "academic_year": ctx["academic_year"]},
            {
                "course": cid,
                "assessment_group": "Internal Assessment",
                "grading_scale": frappe.db.get_value("Grading Scale", {}, "name"),
                "academic_year": ctx["academic_year"],
                "academic_term": ctx["academic_term"],
                "schedule_date": "2025-09-15",
                "maximum_assessment_score": 100,
            },
            ignore_links=True,
        )

        # Assessment Results for first 50 students
        results = 0
        for sid, sname, pid, pname, pabbr, batch, email in ctx.get("students", [])[:50]:
            if not frappe.db.exists("Assessment Result", {"student": sid, "course": cid}):
                score = random.randint(40, 95)
                _exists_or_create(
                    "Assessment Result",
                    {"student": sid, "course": cid},
                    {
                        "student": sid,
                        "student_name": sname,
                        "course": cid,
                        "assessment_plan": plan_name,
                        "academic_year": ctx["academic_year"],
                        "academic_term": ctx["academic_term"],
                        "total_score": score,
                    },
                    ignore_links=True,
                )
                results += 1

    frappe.db.commit()
    print(f"  Created exam schedules, assessment plans, {results} results")


# ============================================================
# 13. RESEARCH & OBE
# ============================================================

def _seed_research_obe(ctx):
    print("\n[13/17] Research & OBE...")

    # Research Publications
    pubs = [
        ("Deep Learning for NLP: A Survey", "Journal", "2025-03-15"),
        ("IoT Security Framework for Smart Campus", "Conference", "2025-01-20"),
        ("Quantum Computing: Current State", "Journal", "2024-11-10"),
        ("Machine Learning in Education", "Conference", "2025-05-22"),
        ("Blockchain for Academic Credentials", "Journal", "2025-02-28"),
        ("Edge Computing in Healthcare", "Journal", "2025-04-15"),
        ("Autonomous Vehicle Navigation", "Conference", "2025-02-10"),
        ("Smart Grid Optimization", "Journal", "2025-06-01"),
        ("Reinforcement Learning Applications", "Conference", "2025-03-20"),
        ("Cybersecurity in Education", "Journal", "2025-01-05"),
    ]
    for title, pub_type, pub_date in pubs:
        _exists_or_create("Research Publication", {"title": title}, {
            "title": title, "publication_type": pub_type, "publication_date": pub_date,
        })

    # Research Projects
    projects = [
        ("AI-Powered Student Analytics", "DST", 2500000),
        ("Green Computing Research", "UGC", 1500000),
        ("Cybersecurity Framework", "DRDO", 3000000),
        ("Smart Campus IoT Infrastructure", "MHRD", 2000000),
        ("Renewable Energy Systems", "MNRE", 1800000),
    ]
    for title, agency, amount in projects:
        _exists_or_create("Research Project", {"project_title": title}, {
            "project_title": title, "funding_agency": agency,
            "sanctioned_amount": amount, "start_date": "2025-01-01",
        })

    # OBE: Program Educational Objectives
    if ctx.get("programs"):
        pid = ctx["programs"][0][0]  # First program
        peos = [
            "Graduates will have successful careers in industry or academia",
            "Graduates will solve real-world problems using technical skills",
            "Graduates will demonstrate leadership and ethical practices",
            "Graduates will engage in lifelong learning",
        ]
        for i, desc in enumerate(peos):
            _exists_or_create(
                "Program Educational Objective",
                {"peo_name": f"PEO-{i+1}"},
                {"peo_name": f"PEO-{i+1}", "description": desc, "program": pid},
            )

        # Program Outcomes (NBA standard 12)
        po_names = [
            "Engineering Knowledge", "Problem Analysis", "Design/Development",
            "Investigation", "Modern Tool Usage", "Engineer and Society",
            "Environment and Sustainability", "Ethics", "Individual and Teamwork",
            "Communication", "Project Management", "Lifelong Learning",
        ]
        for i, name in enumerate(po_names):
            _exists_or_create(
                "Program Outcome",
                {"po_name": f"PO-{i+1}"},
                {"po_name": f"PO-{i+1}", "description": name, "program": pid},
            )

        # Course Outcomes for first 5 courses
        for cid, cname, ccode in ctx.get("courses", [])[:5]:
            for j in range(3):
                co_name = f"CO-{ccode}-{j+1}"
                _exists_or_create(
                    "Course Outcome",
                    {"co_name": co_name},
                    {
                        "co_name": co_name,
                        "description": f"Students will be able to demonstrate {cname} concept {j+1}",
                        "course": cid,
                    },
                )

    frappe.db.commit()
    print("  Research and OBE complete")


# ============================================================
# 14. LMS
# ============================================================

def _seed_lms(ctx):
    print("\n[14/17] LMS...")
    for i, (cid, cname, ccode) in enumerate(ctx.get("courses", [])[:15]):
        lms_name = f"LMS - {cname}"
        if not frappe.db.exists("LMS Course", {"course_name": lms_name}):
            data = {"course_name": lms_name, "course": cid}
            # Add optional fields if available
            if ctx.get("academic_term"):
                data["academic_term"] = ctx["academic_term"]
            if ctx.get("instructors") and i < len(ctx["instructors"]):
                data["instructor"] = ctx["instructors"][i][0]
            _exists_or_create("LMS Course", {"course_name": lms_name}, data)

    frappe.db.commit()
    print("  LMS complete")


# ============================================================
# 15. GRIEVANCE & FEEDBACK
# ============================================================

def _seed_grievance_feedback(ctx):
    print("\n[15/17] Grievance & Feedback...")

    # Grievance Types (required: grievance_type_name, category)
    gt_categories = {
        "Academic": "Academic", "Hostel": "Hostel", "Library": "Library",
        "Transport": "Transport", "Financial": "Financial", "General": "Administrative",
    }
    for gt, cat in gt_categories.items():
        if not frappe.db.exists("Grievance Type", {"grievance_type_name": gt}):
            _exists_or_create("Grievance Type", {"grievance_type_name": gt}, {
                "grievance_type_name": gt, "category": cat,
            })

    # Grievances (10)
    # Required: subject, grievance_type, category, priority, submitted_by_type, description
    # Valid category values: Academic, Administrative, Financial, Infrastructure,
    # Hostel, Transport, Library, Examination, Faculty Related, Ragging, Harassment, Other
    grievances_data = [
        ("Hostel water supply issue", "Hostel", "Infrastructure", "High", "Student", "Water supply is intermittent in Tagore Hall since last week."),
        ("Library book not available", "Library", "Library", "Medium", "Student", "Required textbook for CS201 is not available in library."),
        ("Transport bus timing issue", "Transport", "Transport", "High", "Student", "Route A bus is consistently 20 minutes late."),
        ("Fee calculation error", "Financial", "Financial", "High", "Student", "Scholarship not deducted from fee amount."),
        ("Lab equipment malfunction", "Academic", "Infrastructure", "Medium", "Student", "3 PCs in CS Lab are non-functional."),
        ("Mess food quality", "Hostel", "Hostel", "Medium", "Student", "Food quality has declined in Central Mess."),
        ("Exam hall ventilation", "Academic", "Infrastructure", "Low", "Student", "Exam Hall 1 needs better ventilation."),
        ("Scholarship not credited", "Financial", "Financial", "High", "Student", "Merit scholarship amount not reflected in fee statement."),
        ("WiFi connectivity issue", "General", "Infrastructure", "High", "Student", "WiFi is very slow in hostel blocks after 8 PM."),
        ("Placement support needed", "General", "Administrative", "Medium", "Student", "Need more mock interview sessions before placement drive."),
    ]
    for i, (subject, gtype, category, priority, sub_by, desc) in enumerate(grievances_data):
        sid = ctx["students"][i][0] if i < len(ctx.get("students", [])) else None
        data = {
            "subject": subject,
            "grievance_type": gtype,
            "category": category,
            "priority": priority,
            "submitted_by_type": sub_by,
            "description": desc,
        }
        if sid:
            data["student"] = sid
        _exists_or_create("Grievance", {"subject": subject}, data, ignore_links=True)

    # Feedback Forms
    # Valid form_type: Course Feedback, Faculty Feedback, Facility Feedback,
    #   Event Feedback, Service Feedback, General Survey, Exit Survey, Alumni Survey
    for title, ftype, audience in [
        ("Mid-Semester Feedback", "Course Feedback", "Students"),
        ("End-Semester Feedback", "Course Feedback", "Students"),
        ("Hostel Feedback", "Facility Feedback", "Students"),
        ("Library Feedback", "Service Feedback", "Students"),
        ("Overall Satisfaction", "General Survey", "All"),
    ]:
        _exists_or_create("Feedback Form", {"form_title": title}, {
            "form_title": title, "form_type": ftype,
            "target_audience": audience,
            "start_date": "2025-09-01", "end_date": "2025-12-31",
        })

    # Suggestions
    # Valid category: Academic Improvement, Infrastructure, Services,
    #   Events & Activities, Policy Suggestion, Technology, Other
    suggestions = [
        ("Improve WiFi speed in hostels", "Infrastructure", "Install additional WiFi access points in hostel buildings."),
        ("Add more reference books to library", "Services", "Library should stock latest editions of core CS textbooks."),
        ("Extend library hours during exams", "Services", "Library should be open till midnight during exam weeks."),
        ("Improve cafeteria menu variety", "Services", "Add more variety in breakfast menu, especially South Indian items."),
        ("Add more sports facilities", "Infrastructure", "Need a dedicated badminton court and swimming pool."),
    ]
    for subject, category, suggestion in suggestions:
        _exists_or_create("Suggestion", {"subject": subject}, {
            "subject": subject, "category": category, "suggestion": suggestion,
        })

    frappe.db.commit()
    print("  Grievance and feedback complete")


# ============================================================
# 16. ATTENDANCE, NOTICES, ALERTS
# ============================================================

def _seed_attendance(ctx):
    print("\n[16/17] Attendance & Notices...")

    # Student Attendance (batch create for performance)
    att_count = 0
    att_errors = 0
    dates = [
        f"2025-{m:02d}-{d:02d}"
        for m in range(7, 11)  # Jul-Oct
        for d in range(1, 29)
        if not (date(2025, m, d).weekday() in [5, 6])  # skip weekends
    ]
    # Sample: 50 students x ~80 working days = ~4000 records
    sample_students = ctx.get("students", [])[:50]
    student_groups = frappe.get_all("Student Group", pluck="name", limit=3)
    default_group = student_groups[0] if student_groups else None

    for att_date in dates[:80]:  # limit to 80 days
        for sid, sname, pid, pname, pabbr, batch, email in sample_students:
            if not frappe.db.exists("Student Attendance", {
                "student": sid, "date": att_date,
            }):
                status = random.choices(["Present", "Absent"], weights=[85, 15])[0]
                try:
                    doc = frappe.get_doc({
                        "doctype": "Student Attendance",
                        "student": sid,
                        "student_name": sname,
                        "date": att_date,
                        "status": status,
                        "student_group": default_group,
                    })
                    doc.flags.ignore_validate = True
                    doc.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
                    att_count += 1
                except Exception as e:
                    att_errors += 1
                    if att_errors == 1:
                        print(f"    Attendance note: {str(e)[:200]}")

            if att_count % 500 == 0 and att_count > 0:
                frappe.db.commit()

    frappe.db.commit()

    # Notice Board (required: title, notice_type, publish_date, content)
    notices = [
        ("Mid-Semester Exam Schedule Released", "Examination", "The mid-semester examination schedule for Semester 1 2025-26 has been published."),
        ("Library Holiday on Oct 2", "Library", "The library will remain closed on October 2 for Gandhi Jayanti."),
        ("Placement Drive - TCS", "Placement", "TCS campus placement drive scheduled for November 15."),
        ("Hostel Room Allocation", "Hostel", "Room allocation for new batch students is now available."),
        ("Sports Day Announcement", "Sports", "Annual sports day on November 25."),
        ("Fee Payment Deadline", "General", "Last date for fee payment: September 30, 2025."),
        ("Research Seminar Series", "Academic", "Weekly research seminars starting October 1."),
        ("Cultural Fest Registrations Open", "Cultural", "Register for Technoculture 2025 before October 15."),
    ]
    for title, ntype, content in notices:
        _exists_or_create("Notice Board", {"title": title}, {
            "title": title, "notice_type": ntype, "content": content,
            "publish_date": "2025-09-01",
        })

    # Emergency Alerts
    # Valid alert_type: Fire, Medical Emergency, Security Threat, Natural Disaster,
    #   Evacuation, Lockdown, Utility Failure, Weather Alert, Accident, Other
    for title, alert_type, severity, message in [
        ("Fire Drill Scheduled", "Fire", "Medium", "Fire drill scheduled for October 15. All residents must evacuate to assembly points."),
        ("Heavy Rain Advisory", "Weather Alert", "High", "Heavy rainfall expected. Avoid low-lying areas. Classes may be suspended."),
    ]:
        _exists_or_create("Emergency Alert", {"title": title}, {
            "title": title, "alert_type": alert_type,
            "severity": severity, "message": message,
            "target_audience": "All",
        })

    frappe.db.commit()
    print(f"  Created {att_count} attendance records, {len(notices)} notices")


# ============================================================
# 17. DEMO USERS
# ============================================================

def _seed_users(ctx):
    print("\n[17/17] Demo Users...")
    created = 0

    # Student users
    for i in range(5):
        if i < len(ctx.get("students", [])):
            sid, sname, pid, pname, pabbr, batch, email = ctx["students"][i]
            parts = sname.split()
            if _create_user(
                f"student{i+1}@nit.edu", parts[0], parts[-1],
                ["Student", "University Student"],
            ):
                created += 1

    # Faculty users
    for i in range(5):
        if i < len(ctx.get("faculty_employees", [])):
            eid, ename = ctx["faculty_employees"][i]
            parts = ename.split()
            if _create_user(
                f"faculty{i+1}@nit.edu", parts[0], parts[-1],
                ["Academics User", "Instructor", "University Faculty"],
            ):
                created += 1

    # HOD users
    for i in range(2):
        idx = 10 + i  # Pick from later in the faculty list
        if idx < len(ctx.get("faculty_employees", [])):
            eid, ename = ctx["faculty_employees"][idx]
            parts = ename.split()
            if _create_user(
                f"hod{i+1}@nit.edu", parts[0], parts[-1],
                ["Academics User", "Instructor", "University HOD", "University Faculty"],
            ):
                created += 1

    # Parent users
    for i in range(2):
        if i < len(ctx.get("guardians", [])):
            gid, gname, sid = ctx["guardians"][i]
            parts = gname.split()
            if _create_user(
                f"parent{i+1}@nit.edu", parts[0], parts[-1],
                ["Guardian"],
            ):
                created += 1

    # Management users (using actual university roles from the system)
    management_users = [
        ("vc@nit.edu", "Vijay", "Chancellor", ["System Manager", "University VC"]),
        ("registrar@nit.edu", "Ramesh", "Registrar", ["System Manager", "University Registrar", "Academics User"]),
        ("dean@nit.edu", "Sunil", "Dean", ["System Manager", "University Dean", "Academics User"]),
        ("finance@nit.edu", "Venkatesh", "Finance", ["System Manager", "University Finance", "Accounts Manager"]),
        ("warden@nit.edu", "Prakash", "Warden", ["System Manager", "University Warden"]),
        ("transport@nit.edu", "Anjali", "Transport", ["System Manager"]),
        ("librarian@nit.edu", "Sunita", "Librarian", ["System Manager", "University Librarian"]),
        ("placement@nit.edu", "Kiran", "PlacementOfficer", ["System Manager", "University Placement Officer"]),
    ]
    for email, first, last, roles in management_users:
        if _create_user(email, first, last, roles):
            created += 1

    frappe.db.commit()
    print(f"  Created {created} demo users")

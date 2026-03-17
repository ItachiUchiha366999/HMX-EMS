"""
Seed Demo Data for University ERP
National Institute of Technology (NIT) — Academic Year 2025-26

Usage:
    bench --site university.local execute university_erp.setup.seed_demo_data.seed_all
    bench --site university.local execute university_erp.setup.seed_demo_data.clean_all
"""

import frappe
from frappe.utils import nowdate, add_days, getdate, random_string
from datetime import date, timedelta
import random


# ============================================================
# CLEAN ALL DATA
# ============================================================

def clean_all():
    """Delete ALL existing demo/transactional data. Keep Company, Fiscal Year, Grading Scale."""
    frappe.flags.ignore_permissions = True
    print("Cleaning all data...")

    # University ERP transactional (children first)
    child_dts = [
        "Hostel Attendance", "Hostel Allocation", "Hostel Visitor", "Hostel Maintenance Request",
        "Library Transaction", "Library Member", "Book Reservation", "Library Fine",
        "Assignment Submission", "Quiz Attempt", "LMS Content Progress", "LMS Discussion",
        "Student Exam Attempt", "Answer Sheet", "Fee Payment", "Student Scholarship",
        "Grievance", "Feedback Response", "Student Feedback", "Suggestion",
        "User Notification", "Certificate Request", "Transport Allocation", "Transport Trip Log",
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
        "Student Category", "Student Batch Name", "Assessment Criteria", "Assessment Group",
        "Fee Structure",
    ]

    hrms_dts = ["Leave Application", "Attendance", "Salary Structure Assignment",
                "Salary Structure", "Leave Policy Assignment", "Leave Policy", "Leave Allocation"]

    for dt_list in [child_dts, master_dts, edu_dts, hrms_dts]:
        for dt in dt_list:
            if frappe.db.exists("DocType", dt):
                try:
                    count = frappe.db.count(dt)
                    if count:
                        frappe.db.sql(f"DELETE FROM `tab{dt}`")
                        # Also delete child tables
                        meta = frappe.get_meta(dt)
                        for tf in meta.get_table_fields():
                            frappe.db.sql(f"DELETE FROM `tab{tf.options}` WHERE parenttype='{dt}'")
                        print(f"  Deleted {count} {dt}")
                except Exception as e:
                    print(f"  WARN: {dt}: {e}")

    # Delete employees (but not Company)
    emp_count = frappe.db.count("Employee")
    if emp_count:
        frappe.db.sql("DELETE FROM `tabEmployee`")
        print(f"  Deleted {emp_count} Employee")

    # Delete non-system users
    users = frappe.get_all("User", filters={
        "name": ["not in", ["Administrator", "Guest"]],
        "user_type": "Website User"
    }, pluck="name")
    users += frappe.get_all("User", filters={
        "name": ["not in", ["Administrator", "Guest"]],
        "name": ["like", "%@nit.edu"]
    }, pluck="name")
    users += frappe.get_all("User", filters={
        "name": ["not in", ["Administrator", "Guest"]],
        "name": ["like", "%@university.local"]
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
# HELPER
# ============================================================

def _create(doctype, data, ignore_links=False):
    """Create a document if it doesn't exist."""
    # Check by name or unique key
    name = data.get("name")
    if name and frappe.db.exists(doctype, name):
        return name

    try:
        doc = frappe.get_doc({"doctype": doctype, **data})
        doc.insert(ignore_permissions=True, ignore_links=ignore_links, ignore_mandatory=False)
        return doc.name
    except frappe.DuplicateEntryError:
        return data.get("name") or frappe.db.get_value(doctype, data, "name")
    except Exception as e:
        err = str(e)[:150]
        print(f"  WARN creating {doctype}: {err}")
        return None


def _create_user(email, first_name, last_name, role, password="Demo@Nit2026!"):
    """Create user with role."""
    if frappe.db.exists("User", email):
        return email
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "enabled": 1,
        "new_password": password,
        "send_welcome_email": 0,
    })
    user.append("roles", {"role": role})
    user.insert(ignore_permissions=True)
    return email


# ============================================================
# SEED ALL
# ============================================================

def seed_all():
    """Seed complete demo data for University ERP."""
    frappe.flags.ignore_permissions = True

    print("=" * 60)
    print("SEEDING DEMO DATA — National Institute of Technology")
    print("=" * 60)

    clean_all()

    ctx = {}  # Shared context for cross-referencing

    _phase1_core_setup(ctx)
    _phase2_education_masters(ctx)
    _phase3_hrms(ctx)
    _phase4_students(ctx)
    _phase5_university_core(ctx)
    _phase6_academics(ctx)
    _phase7_examinations(ctx)
    _phase8_finance(ctx)
    _phase9_faculty(ctx)
    _phase10_hostel(ctx)
    _phase11_library(ctx)
    _phase12_lms(ctx)
    _phase13_placement(ctx)
    _phase14_research(ctx)
    _phase15_obe(ctx)
    _phase16_transport(ctx)
    _phase17_users(ctx)
    _phase18_student_portal_data(ctx)
    _phase19_transactional(ctx)

    print("\n" + "=" * 60)
    print("DEMO DATA SEEDED SUCCESSFULLY!")
    print("=" * 60)
    print("\nLogin Credentials:")
    print("-" * 60)
    print(f"{'Role':<25} {'Email':<30} {'Password'}")
    print("-" * 60)
    print(f"{'Admin':<25} {'admin@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Registrar':<25} {'registrar@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Finance':<25} {'finance@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Exam Cell':<25} {'examcell@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Faculty (HOD)':<25} {'hod.cse@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Faculty':<25} {'faculty1@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Student':<25} {'student1@nit.edu':<30} Student@Nit2026!")
    print(f"{'Student':<25} {'student2@nit.edu':<30} Student@Nit2026!")
    print(f"{'Librarian':<25} {'librarian@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Warden':<25} {'warden@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Placement':<25} {'placement@nit.edu':<30} Admin@Nit2026!")
    print(f"{'Parent':<25} {'parent1@nit.edu':<30} Admin@Nit2026!")
    print("-" * 60)


# ============================================================
# PHASES
# ============================================================

def _phase1_core_setup(ctx):
    print("\n[Phase 1] Core Setup...")

    # Company - update existing
    company = frappe.get_all("Company", pluck="name", limit=1)
    if company:
        ctx["company"] = company[0]
    else:
        ctx["company"] = "National Institute of Technology"

    # Academic Year
    if not frappe.db.exists("Academic Year", "2025-26"):
        _create("Academic Year", {
            "academic_year_name": "2025-26",
            "year_start_date": "2025-07-01",
            "year_end_date": "2026-06-30"
        })
    ctx["academic_year"] = "2025-26"

    # Academic Term
    at_name = frappe.db.get_value("Academic Term", {"term_name": "Odd Semester", "academic_year": "2025-26"})
    if not at_name:
        at = frappe.get_doc({
            "doctype": "Academic Term",
            "term_name": "Odd Semester",
            "academic_year": "2025-26",
            "term_start_date": "2025-07-01",
            "term_end_date": "2025-12-31"
        })
        at.insert(ignore_permissions=True)
        at_name = at.name
    ctx["academic_term"] = at_name or "Odd Semester 2025"

    # Designations
    for d in ["Professor", "Associate Professor", "Assistant Professor", "Lab Instructor",
              "Registrar", "Librarian", "Warden", "Administrative Officer"]:
        if not frappe.db.exists("Designation", d):
            frappe.db.sql("INSERT IGNORE INTO tabDesignation (name, creation, modified, owner, modified_by) VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator')", d)
    frappe.db.commit()
    print("    Designations created")

    # Holiday List
    if not frappe.db.exists("Holiday List", "NIT Holidays 2025-26"):
        hl = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": "NIT Holidays 2025-26",
            "from_date": "2025-07-01",
            "to_date": "2026-06-30",
        })
        holidays = [
            ("2025-08-15", "Independence Day"), ("2025-10-02", "Gandhi Jayanti"),
            ("2025-10-20", "Dussehra"), ("2025-11-01", "Diwali"),
            ("2025-11-05", "Diwali Holiday"), ("2025-12-25", "Christmas"),
            ("2026-01-26", "Republic Day"), ("2026-03-14", "Holi"),
        ]
        for dt, desc in holidays:
            hl.append("holidays", {"holiday_date": dt, "description": desc})
        hl.insert(ignore_permissions=True)
    ctx["holiday_list"] = "NIT Holidays 2025-26"

    frappe.db.commit()
    print("  Core setup complete")


def _phase2_education_masters(ctx):
    print("\n[Phase 2] Education Masters...")

    # Rooms
    rooms = [
        ("LH-101", "Lecture Hall 1", 120), ("LH-102", "Lecture Hall 2", 120),
        ("LH-103", "Lecture Hall 3", 80), ("LH-104", "Lecture Hall 4", 80),
        ("CS-LAB", "Computer Science Lab", 60), ("EC-LAB", "Electronics Lab", 40),
        ("PH-LAB", "Physics Lab", 40), ("SH-01", "Seminar Hall", 200),
        ("EH-01", "Exam Hall 1", 150), ("EH-02", "Exam Hall 2", 150),
    ]
    ctx["rooms"] = []
    for code, name, cap in rooms:
        rid = _create("Room", {"room_name": name, "room_number": code, "seating_capacity": cap})
        if rid:
            ctx["rooms"].append(rid)

    # Student Categories
    for c in ["General", "SC/ST", "OBC"]:
        _create("Student Category", {"category": c})

    # Student Batch Names
    for b in ["2023", "2024", "2025"]:
        if not frappe.db.exists("Student Batch Name", b):
            _create("Student Batch Name", {"batch_name": b})

    # Assessment Criteria
    for name, weight in [("Theory", 40), ("Practical", 30), ("Assignment", 15),
                         ("Project", 10), ("Viva", 5)]:
        _create("Assessment Criteria", {"assessment_criteria": name, "weightage": weight})

    # Assessment Groups
    for g in ["Internal Assessment", "External Assessment", "Final Assessment"]:
        _create("Assessment Group", {"assessment_group_name": g})

    # Topics
    topics = ["Data Structures", "Algorithms", "Object Oriented Programming",
              "Database Management", "Operating Systems", "Computer Networks",
              "Web Technologies", "Artificial Intelligence", "Discrete Mathematics",
              "Linear Algebra", "Probability & Statistics", "Digital Logic",
              "Microprocessors", "Software Engineering", "Compiler Design"]
    for t in topics:
        _create("Topic", {"topic_name": t})

    # Programs
    programs = [
        ("B.Tech Computer Science", "BTCS", 4), ("B.Tech Electronics", "BTEC", 4),
        ("M.Tech Computer Science", "MTCS", 2), ("MBA", "MBA", 2),
    ]
    ctx["programs"] = []
    for name, abbr, dur in programs:
        pid = _create("Program", {
            "program_name": name, "program_abbreviation": abbr,
            "custom_program_code": abbr,
            "custom_credit_system": "CBCS",
            "custom_min_credits_graduation": 160 if dur == 4 else 80,
            "custom_duration_years": dur,
        })
        if pid:
            ctx["programs"].append(pid)

    # Courses
    courses_data = [
        ("Data Structures", "CS201"), ("Database Systems", "CS301"),
        ("Operating Systems", "CS302"), ("Computer Networks", "CS401"),
        ("Web Technologies", "CS402"), ("Artificial Intelligence", "CS501"),
        ("Digital Electronics", "EC201"), ("Microprocessors", "EC301"),
        ("Engineering Mathematics", "MA201"), ("Communication Skills", "HS101"),
        ("Environmental Science", "ES101"), ("Software Engineering", "CS601"),
    ]
    ctx["courses"] = []
    for name, code in courses_data:
        cid = _create("Course", {
            "course_name": name, "course_code": code,
            "custom_course_code": code,
        })
        if cid:
            ctx["courses"].append(cid)

    frappe.db.commit()
    print(f"  Created {len(ctx['rooms'])} rooms, {len(ctx['programs'])} programs, {len(ctx['courses'])} courses")


def _phase3_hrms(ctx):
    print("\n[Phase 3] HRMS (Employees)...")

    dept = frappe.get_all("Department", filters={"company": ctx["company"]}, pluck="name", limit=1)
    if not dept:
        # Try without company filter
        dept = frappe.get_all("Department", pluck="name", limit=1)
    dept_name = dept[0] if dept else None

    employees_data = [
        ("Rajesh", "Kumar", "Male", "1975-05-15", "Professor", True),
        ("Priya", "Singh", "Female", "1982-03-20", "Associate Professor", True),
        ("Amit", "Sharma", "Male", "1985-08-10", "Assistant Professor", True),
        ("Deepa", "Nair", "Female", "1980-11-25", "Associate Professor", True),
        ("Vikram", "Patel", "Male", "1973-02-14", "Professor", True),
        ("Meera", "Iyer", "Female", "1988-06-30", "Assistant Professor", True),
        ("Suresh", "Reddy", "Male", "1979-09-05", "Associate Professor", True),
        ("Kavita", "Joshi", "Female", "1986-04-18", "Assistant Professor", True),
        ("Anand", "Verma", "Male", "1977-07-22", "Professor", True),
        ("Lakshmi", "Menon", "Female", "1990-01-10", "Assistant Professor", True),
        ("Ramesh", "Gupta", "Male", "1970-12-01", "Registrar", False),
        ("Sunita", "Devi", "Female", "1978-08-15", "Librarian", False),
        ("Prakash", "Rao", "Male", "1975-03-28", "Warden", False),
        ("Venkatesh", "Iyer", "Male", "1980-10-05", "Administrative Officer", False),
        ("Anjali", "Desai", "Female", "1985-06-12", "Administrative Officer", False),
    ]

    ctx["employees"] = []
    ctx["faculty_employees"] = []
    for first, last, gender, dob, designation, is_faculty in employees_data:
        eid = _create("Employee", {
            "first_name": first,
            "last_name": last,
            "employee_name": f"{first} {last}",
            "gender": gender,
            "date_of_birth": dob,
            "date_of_joining": "2020-07-01",
            "designation": designation,
            "company": ctx["company"],
            "department": dept_name,
            "status": "Active",
        })
        if eid:
            ctx["employees"].append(eid)
            if is_faculty:
                ctx["faculty_employees"].append((eid, f"{first} {last}"))

    frappe.db.commit()
    print(f"  Created {len(ctx['employees'])} employees ({len(ctx['faculty_employees'])} faculty)")


def _phase4_students(ctx):
    print("\n[Phase 4] Students & Enrollments...")

    # Students data: (first, last, gender, dob, program_idx, batch, enrollment_num)
    students_data = [
        # B.Tech CSE (20 students)
        ("Arjun", "Mehta", "Male", "2004-03-15", 0, "2023", "NIT-2023-001"),
        ("Sneha", "Reddy", "Female", "2004-07-22", 0, "2023", "NIT-2023-002"),
        ("Rahul", "Sharma", "Male", "2004-01-10", 0, "2023", "NIT-2023-003"),
        ("Ananya", "Gupta", "Female", "2005-05-18", 0, "2024", "NIT-2024-001"),
        ("Vikash", "Kumar", "Male", "2003-11-30", 0, "2023", "NIT-2023-004"),
        ("Pooja", "Verma", "Female", "2004-09-05", 0, "2023", "NIT-2023-005"),
        ("Rohit", "Patel", "Male", "2005-02-14", 0, "2024", "NIT-2024-002"),
        ("Divya", "Nair", "Female", "2005-08-20", 0, "2024", "NIT-2024-003"),
        ("Aditya", "Joshi", "Male", "2004-04-25", 0, "2023", "NIT-2023-006"),
        ("Kavya", "Iyer", "Female", "2005-06-11", 0, "2024", "NIT-2024-004"),
        ("Siddharth", "Rao", "Male", "2006-01-08", 0, "2025", "NIT-2025-001"),
        ("Priyanka", "Das", "Female", "2006-03-22", 0, "2025", "NIT-2025-002"),
        ("Nikhil", "Saxena", "Male", "2003-12-15", 0, "2023", "NIT-2023-007"),
        ("Shruti", "Mishra", "Female", "2004-10-03", 0, "2023", "NIT-2023-008"),
        ("Karan", "Singh", "Male", "2005-07-19", 0, "2024", "NIT-2024-005"),
        ("Neha", "Agarwal", "Female", "2005-11-28", 0, "2024", "NIT-2024-006"),
        ("Manish", "Tiwari", "Male", "2006-02-10", 0, "2025", "NIT-2025-003"),
        ("Riya", "Kapoor", "Female", "2006-05-30", 0, "2025", "NIT-2025-004"),
        ("Akash", "Dubey", "Male", "2004-08-14", 0, "2023", "NIT-2023-009"),
        ("Meghna", "Pillai", "Female", "2003-10-20", 0, "2023", "NIT-2023-010"),
        # B.Tech ECE (5)
        ("Suraj", "Bhat", "Male", "2005-04-12", 1, "2024", "NIT-2024-007"),
        ("Pallavi", "Hegde", "Female", "2005-09-01", 1, "2024", "NIT-2024-008"),
        ("Harish", "Gowda", "Male", "2006-01-25", 1, "2025", "NIT-2025-005"),
        ("Swati", "Kulkarni", "Female", "2005-12-08", 1, "2024", "NIT-2024-009"),
        ("Naveen", "Shetty", "Male", "2006-06-15", 1, "2025", "NIT-2025-006"),
        # M.Tech CSE (3)
        ("Deepak", "Chauhan", "Male", "2001-03-18", 2, "2025", "NIT-2025-007"),
        ("Aparna", "Rajan", "Female", "2001-07-22", 2, "2025", "NIT-2025-008"),
        ("Manoj", "Pandey", "Male", "2000-11-05", 2, "2025", "NIT-2025-009"),
        # MBA (2)
        ("Sanjay", "Malhotra", "Male", "2002-02-28", 3, "2025", "NIT-2025-010"),
        ("Nisha", "Choudhary", "Female", "2002-08-10", 3, "2025", "NIT-2025-011"),
    ]

    ctx["students"] = []
    ctx["key_students"] = []  # First 5 with portal access

    for i, (first, last, gender, dob, prog_idx, batch, enroll) in enumerate(students_data):
        email = f"{first.lower()}.{last.lower()}@nit.edu"
        sid = _create("Student", {
            "first_name": first,
            "last_name": last,
            "student_email_id": email,
            "gender": gender,
            "date_of_birth": dob,
            "joining_date": "2025-07-01",
            "enabled": 1,
            "custom_enrollment_number": enroll,
        })
        if sid:
            ctx["students"].append((sid, f"{first} {last}", prog_idx, batch, email))
            if i < 5:
                ctx["key_students"].append((sid, f"{first} {last}", prog_idx, email))

    # Instructors
    ctx["instructors"] = []
    for emp_id, emp_name in ctx.get("faculty_employees", []):
        iid = _create("Instructor", {
            "instructor_name": emp_name,
            "employee": emp_id,
        })
        if iid:
            ctx["instructors"].append((iid, emp_name))

    # Student Groups
    groups = [
        ("CSE-2023-A", "B.Tech Computer Science", "2023"),
        ("CSE-2024-A", "B.Tech Computer Science", "2024"),
        ("CSE-2025-A", "B.Tech Computer Science", "2025"),
        ("ECE-2024-A", "B.Tech Electronics", "2024"),
        ("MTech-2025", "M.Tech Computer Science", "2025"),
        ("MBA-2025", "MBA", "2025"),
    ]
    for gname, prog, batch in groups:
        _create("Student Group", {
            "student_group_name": gname,
            "group_based_on": "Batch",
            "program": prog,
            "academic_year": ctx["academic_year"],
            "batch": batch,
        })

    # Program Enrollments
    for sid, sname, prog_idx, batch, email in ctx["students"]:
        if prog_idx < len(ctx.get("programs", [])):
            _create("Program Enrollment", {
                "student": sid,
                "student_name": sname,
                "program": ctx["programs"][prog_idx],
                "academic_year": ctx["academic_year"],
                "enrollment_date": "2025-07-01",
            })

    # Guardians for first 5 students
    ctx["guardians"] = []
    guardian_data = [
        ("Rajendra", "Mehta", "9876543210", "Father"),
        ("Lakshmi", "Reddy", "9876543211", "Mother"),
        ("Sunil", "Sharma", "9876543212", "Father"),
        ("Anita", "Gupta", "9876543213", "Mother"),
        ("Mohan", "Kumar", "9876543214", "Father"),
    ]
    for i, (first, last, phone, relation) in enumerate(guardian_data):
        gid = _create("Guardian", {
            "guardian_name": f"{first} {last}",
            "email_address": f"parent{i+1}@nit.edu",
            "mobile_number": phone,
        })
        if gid:
            ctx["guardians"].append(gid)

    frappe.db.commit()
    print(f"  Created {len(ctx['students'])} students, {len(ctx['instructors'])} instructors")


def _phase5_university_core(ctx):
    print("\n[Phase 5] University Core...")

    # University Departments
    for name, code in [("Computer Science", "CSE"), ("Electronics", "ECE"),
                       ("Mathematics", "MATH"), ("Management", "MGMT"), ("General", "GEN")]:
        _create("University Department", {
            "department_name": name,
            "department_code": code,
        })

    # University Laboratories
    for name, code in [("CS Laboratory", "CS-LAB"), ("Electronics Laboratory", "EC-LAB"),
                       ("Physics Laboratory", "PH-LAB")]:
        _create("University Laboratory", {
            "lab_name": name,
            "lab_code": code,
        })

    frappe.db.commit()
    print("  University core complete")


def _phase6_academics(ctx):
    print("\n[Phase 6] Academics & Admissions...")

    # Admission Cycle
    _create("Admission Cycle", {
        "cycle_name": "Admissions 2025-26",
        "academic_year": ctx["academic_year"],
        "start_date": "2025-04-01",
        "end_date": "2025-07-31",
    })

    frappe.db.commit()
    print("  Academics complete")


def _phase7_examinations(ctx):
    print("\n[Phase 7] Examinations...")

    # Question Tags
    for tag in ["Easy", "Medium", "Hard", "Bloom-L1", "Bloom-L2", "Bloom-L3", "Bloom-L4", "Bloom-L5"]:
        _create("Question Tag", {"tag_name": tag})

    # Exam Schedule for 6 courses
    exam_dates = ["2025-10-15", "2025-10-16", "2025-10-17", "2025-10-18", "2025-10-20", "2025-10-21"]
    for i, course in enumerate(ctx.get("courses", [])[:6]):
        room = ctx["rooms"][8] if len(ctx["rooms"]) > 8 else ctx["rooms"][0]  # Exam Hall 1
        _create("Exam Schedule", {
            "course": course,
            "schedule_date": exam_dates[i] if i < len(exam_dates) else "2025-10-22",
            "from_time": "10:00",
            "to_time": "13:00",
            "room": room,
            "academic_year": ctx["academic_year"],
            "academic_term": ctx["academic_term"],
        })

    frappe.db.commit()
    print("  Examinations complete")


def _phase8_finance(ctx):
    print("\n[Phase 8] Finance...")

    # Fee Categories
    for cat in ["Tuition Fee", "Laboratory Fee", "Library Fee", "Hostel Fee", "Examination Fee"]:
        _create("Fee Category", {"category_name": cat})

    # Scholarship Types
    for st in ["Merit Scholarship", "Need-Based Scholarship", "Sports Scholarship"]:
        _create("Scholarship Type", {"scholarship_name": st})

    # Create Fees for each student
    amounts = {0: 75000, 1: 70000, 2: 60000, 3: 80000}  # Per program
    for sid, sname, prog_idx, batch, email in ctx.get("students", []):
        amount = amounts.get(prog_idx, 75000)
        if prog_idx < len(ctx.get("programs", [])):
            try:
                fee = frappe.get_doc({
                    "doctype": "Fees",
                    "student": sid,
                    "student_name": sname,
                    "program": ctx["programs"][prog_idx],
                    "academic_year": ctx["academic_year"],
                    "academic_term": ctx["academic_term"],
                    "due_date": "2025-09-30",
                    "components": [
                        {"fees_category": "Tuition Fee - NIT" if frappe.db.exists("Fee Component", "Tuition Fee - NIT") else "Tuition Fee", "amount": amount * 0.6},
                        {"fees_category": "Laboratory Fee - NIT" if frappe.db.exists("Fee Component", "Laboratory Fee - NIT") else "Laboratory Fee", "amount": amount * 0.2},
                    ],
                    "grand_total": amount,
                })
                fee.flags.ignore_validate = True
                fee.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
            except Exception as e:
                pass  # Fee structure may differ

    # Scholarships for top 5
    for i, (sid, sname, prog_idx, email) in enumerate(ctx.get("key_students", [])[:3]):
        _create("Student Scholarship", {
            "student": sid,
            "student_name": sname,
            "scholarship_name": "Merit Scholarship",
            "amount": 10000,
            "academic_year": ctx["academic_year"],
        })

    frappe.db.commit()
    print("  Finance complete")


def _phase9_faculty(ctx):
    print("\n[Phase 9] Faculty Management...")

    # Faculty Profiles
    for emp_id, emp_name in ctx.get("faculty_employees", []):
        _create("Faculty Profile", {
            "employee": emp_id,
            "employee_name": emp_name,
        })

    # Teaching Assignments
    if ctx.get("instructors") and ctx.get("courses"):
        for i, course in enumerate(ctx["courses"][:6]):
            inst_idx = i % len(ctx["instructors"])
            inst_id, inst_name = ctx["instructors"][inst_idx]
            room = ctx["rooms"][i % 4] if ctx.get("rooms") else None
            data = {
                "instructor": inst_id,
                "instructor_name": inst_name,
                "course": course,
                "academic_year": ctx["academic_year"],
                "academic_term": ctx["academic_term"],
            }
            if room:
                data["room"] = room
            _create("Teaching Assignment", data)

    frappe.db.commit()
    print("  Faculty management complete")


def _phase10_hostel(ctx):
    print("\n[Phase 10] Hostel...")

    # Buildings
    buildings = [
        ("Tagore Hall", "Boys", 4), ("Sarojini House", "Girls", 3), ("PG Block", "Co-Ed", 2),
    ]
    ctx["hostel_buildings"] = []
    for name, hostel_type, floors in buildings:
        bid = _create("Hostel Building", {
            "building_name": name,
            "hostel_type": hostel_type,
            "total_floors": floors,
        })
        if bid:
            ctx["hostel_buildings"].append(bid)

    # Rooms (10 per building)
    ctx["hostel_rooms"] = []
    room_types = ["Single", "Double", "Double", "Triple"]
    rents = {"Single": 5000, "Double": 3500, "Triple": 2500}
    for bid in ctx["hostel_buildings"]:
        for floor in range(1, 4):
            for room_num in range(1, 5):
                rtype = room_types[(floor + room_num) % len(room_types)]
                rid = _create("Hostel Room", {
                    "room_number": f"{floor}0{room_num}",
                    "hostel_building": bid,
                    "floor": floor,
                    "room_type": rtype,
                    "capacity": 1 if rtype == "Single" else (2 if rtype == "Double" else 3),
                    "rent": rents[rtype],
                })
                if rid:
                    ctx["hostel_rooms"].append(rid)

    # Mess
    for name, mess_type in [("Central Mess", "Vegetarian"), ("PG Mess", "Both")]:
        _create("Hostel Mess", {"mess_name": name, "mess_type": mess_type, "capacity": 300})

    # Hostel Allocations for first 15 students
    for i, (sid, sname, prog_idx, batch, email) in enumerate(ctx.get("students", [])[:15]):
        if i < len(ctx["hostel_rooms"]):
            _create("Hostel Allocation", {
                "student": sid,
                "student_name": sname,
                "hostel_room": ctx["hostel_rooms"][i],
                "from_date": "2025-07-01",
                "to_date": "2026-06-30",
            })

    frappe.db.commit()
    print(f"  Created {len(ctx['hostel_buildings'])} buildings, {len(ctx['hostel_rooms'])} rooms")


def _phase11_library(ctx):
    print("\n[Phase 11] Library...")

    # Categories
    for cat in ["Textbook", "Reference", "Journal", "Fiction", "Digital Resource"]:
        _create("Library Category", {"category_name": cat})

    # Subjects
    for sub in ["Computer Science", "Electronics", "Mathematics", "Management", "English", "General"]:
        _create("Library Subject", {"subject_name": sub})

    # Library Articles (real books)
    books = [
        ("Introduction to Algorithms", "978-0262033848", "Thomas H. Cormen", "MIT Press"),
        ("Operating System Concepts", "978-1119800361", "Abraham Silberschatz", "Wiley"),
        ("Database System Concepts", "978-0078022159", "Abraham Silberschatz", "McGraw Hill"),
        ("Computer Networking: A Top-Down Approach", "978-0133594140", "James Kurose", "Pearson"),
        ("Artificial Intelligence: A Modern Approach", "978-0134610993", "Stuart Russell", "Pearson"),
        ("Data Structures and Algorithms in Python", "978-1118290279", "Michael Goodrich", "Wiley"),
        ("Digital Logic and Computer Design", "978-8131714317", "M. Morris Mano", "Pearson"),
        ("Discrete Mathematics and Its Applications", "978-0073383095", "Kenneth Rosen", "McGraw Hill"),
        ("Engineering Mathematics", "978-8120345287", "B.S. Grewal", "Khanna Publishers"),
        ("The C Programming Language", "978-0131103627", "Brian Kernighan", "Prentice Hall"),
        ("Clean Code", "978-0132350884", "Robert C. Martin", "Prentice Hall"),
        ("Design Patterns", "978-0201633610", "Gang of Four", "Addison Wesley"),
        ("Computer Organization and Architecture", "978-0134101613", "William Stallings", "Pearson"),
        ("Software Engineering", "978-0133943030", "Ian Sommerville", "Pearson"),
        ("Linear Algebra and Its Applications", "978-0321982384", "David Lay", "Pearson"),
        ("Microprocessors and Microcontrollers", "978-0198066477", "Krishna Kant", "Oxford"),
        ("Compiler Design", "978-0321486813", "Alfred Aho", "Pearson"),
        ("Machine Learning", "978-0070428072", "Tom Mitchell", "McGraw Hill"),
        ("Python Crash Course", "978-1593279288", "Eric Matthes", "No Starch Press"),
        ("The Pragmatic Programmer", "978-0135957059", "David Thomas", "Addison Wesley"),
    ]
    ctx["library_articles"] = []
    for title, isbn, author, publisher in books:
        aid = _create("Library Article", {
            "article_name": title,
            "isbn": isbn,
            "author": author,
            "publisher": publisher,
        })
        if aid:
            ctx["library_articles"].append(aid)

    # Library Members (10 students + faculty)
    for sid, sname, prog_idx, batch, email in ctx.get("students", [])[:8]:
        _create("Library Member", {
            "library_member_name": sname,
            "student": sid,
        })

    frappe.db.commit()
    print(f"  Created {len(ctx['library_articles'])} library articles")


def _phase12_lms(ctx):
    print("\n[Phase 12] LMS...")

    for course in ctx.get("courses", [])[:6]:
        _create("LMS Course", {
            "course_name": f"LMS - {course}",
            "course": course,
        })

    frappe.db.commit()
    print("  LMS complete")


def _phase13_placement(ctx):
    print("\n[Phase 13] Placement...")

    # Industry Types
    for it in ["Information Technology", "Finance & Banking", "Manufacturing",
               "Consulting", "Startup"]:
        _create("Industry Type", {"industry_type": it})

    # Companies
    companies = [
        ("Tata Consultancy Services", "Information Technology"),
        ("Infosys", "Information Technology"),
        ("Wipro", "Information Technology"),
        ("Amazon", "Information Technology"),
        ("Google", "Information Technology"),
    ]
    for name, industry in companies:
        _create("Placement Company", {"company_name": name, "industry_type": industry})

    frappe.db.commit()
    print("  Placement complete")


def _phase14_research(ctx):
    print("\n[Phase 14] Research...")

    pubs = [
        ("Deep Learning for NLP: A Survey", "Journal", "2025-03-15"),
        ("IoT Security Framework for Smart Campus", "Conference", "2025-01-20"),
        ("Quantum Computing: Current State", "Journal", "2024-11-10"),
        ("Machine Learning in Education", "Conference", "2025-05-22"),
        ("Blockchain for Academic Credentials", "Journal", "2025-02-28"),
    ]
    for title, pub_type, pub_date in pubs:
        _create("Research Publication", {
            "title": title,
            "publication_type": pub_type,
            "publication_date": pub_date,
        })

    for title, agency, amount in [
        ("AI-Powered Student Analytics", "DST", 2500000),
        ("Green Computing Research", "UGC", 1500000),
        ("Cybersecurity Framework", "DRDO", 3000000),
    ]:
        _create("Research Project", {
            "project_title": title,
            "funding_agency": agency,
            "sanctioned_amount": amount,
            "start_date": "2025-01-01",
        })

    frappe.db.commit()
    print("  Research complete")


def _phase15_obe(ctx):
    print("\n[Phase 15] OBE...")

    # PEOs
    peos = [
        "Graduates will have successful careers in industry or academia",
        "Graduates will solve real-world problems using technical skills",
        "Graduates will demonstrate leadership and ethical practices",
        "Graduates will engage in lifelong learning and professional development",
    ]
    for i, desc in enumerate(peos):
        _create("Program Educational Objective", {
            "peo_name": f"PEO-{i+1}",
            "description": desc,
            "program": ctx["programs"][0] if ctx.get("programs") else None,
        })

    # Program Outcomes (NBA standard 12)
    po_names = [
        "Engineering Knowledge", "Problem Analysis", "Design/Development",
        "Investigation", "Modern Tool Usage", "Engineer and Society",
        "Environment and Sustainability", "Ethics", "Individual and Teamwork",
        "Communication", "Project Management", "Lifelong Learning",
    ]
    for i, name in enumerate(po_names):
        _create("Program Outcome", {
            "po_name": f"PO-{i+1}",
            "description": name,
            "program": ctx["programs"][0] if ctx.get("programs") else None,
        })

    frappe.db.commit()
    print("  OBE complete")


def _phase16_transport(ctx):
    print("\n[Phase 16] Transport...")

    routes = [("Route A - City Center", "A"), ("Route B - Railway Station", "B"),
              ("Route C - Airport Road", "C")]
    ctx["transport_routes"] = []
    for name, code in routes:
        rid = _create("Transport Route", {"route_name": name, "route_code": code})
        if rid:
            ctx["transport_routes"].append(rid)

    for name, num, cap in [("Bus NIT-01", "NIT-01", 50), ("Bus NIT-02", "NIT-02", 50),
                           ("Bus NIT-03", "NIT-03", 40)]:
        _create("Transport Vehicle", {"vehicle_name": name, "vehicle_number": num, "seating_capacity": cap})

    # Allocate students to routes
    for i, (sid, sname, prog_idx, batch, email) in enumerate(ctx.get("students", [])[:10]):
        if ctx["transport_routes"]:
            _create("Transport Allocation", {
                "student": sid,
                "student_name": sname,
                "transport_route": ctx["transport_routes"][i % len(ctx["transport_routes"])],
            })

    frappe.db.commit()
    print("  Transport complete")


def _phase17_users(ctx):
    print("\n[Phase 17] Demo Users (RBAC)...")

    # Staff users
    staff_users = [
        ("admin@nit.edu", "University", "Admin", "University Admin"),
        ("registrar@nit.edu", "NIT", "Registrar", "University Registrar"),
        ("finance@nit.edu", "NIT", "Finance", "University Finance"),
        ("hr@nit.edu", "NIT", "HR", "University HR Admin"),
        ("examcell@nit.edu", "NIT", "Exam Cell", "University Exam Cell"),
        ("librarian@nit.edu", "NIT", "Librarian", "University Librarian"),
        ("warden@nit.edu", "NIT", "Warden", "University Warden"),
        ("placement@nit.edu", "NIT", "Placement", "University Placement Officer"),
    ]
    for email, first, last, role in staff_users:
        _create_user(email, first, last, role, "Admin@Nit2026!")

    # HOD user linked to employee
    _create_user("hod.cse@nit.edu", "Dr. Rajesh", "Kumar", "University HOD", "Admin@Nit2026!")
    if ctx.get("faculty_employees"):
        frappe.db.set_value("Employee", ctx["faculty_employees"][0][0], "user_id", "hod.cse@nit.edu")

    # Faculty users
    faculty_emails = ["faculty1@nit.edu", "faculty2@nit.edu"]
    for i, email in enumerate(faculty_emails):
        if i + 1 < len(ctx.get("faculty_employees", [])):
            emp_id, emp_name = ctx["faculty_employees"][i + 1]
            parts = emp_name.split()
            _create_user(email, parts[0], parts[-1], "University Faculty", "Admin@Nit2026!")
            frappe.db.set_value("Employee", emp_id, "user_id", email)

    # Student users
    student_emails = [
        ("student1@nit.edu", 0), ("student2@nit.edu", 1),
        ("student3@nit.edu", 2), ("student4@nit.edu", 3), ("student5@nit.edu", 4),
    ]
    for email, idx in student_emails:
        if idx < len(ctx.get("key_students", [])):
            sid, sname, prog_idx, orig_email = ctx["key_students"][idx]
            parts = sname.split()
            _create_user(email, parts[0], parts[-1], "University Student", "Student@Nit2026!")
            frappe.db.set_value("Student", sid, "user", email)

    # Parent user
    _create_user("parent1@nit.edu", "Rajendra", "Mehta", "Guardian", "Admin@Nit2026!")
    if ctx.get("guardians"):
        frappe.db.set_value("Guardian", ctx["guardians"][0], "user", "parent1@nit.edu")

    frappe.db.commit()
    print("  Created 14+ demo users")


def _phase18_student_portal_data(ctx):
    print("\n[Phase 18] Student Portal Data...")

    # Course Schedules for key students
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    times = [("09:00", "10:00"), ("10:00", "11:00"), ("11:30", "12:30"), ("14:00", "15:00")]

    for course_idx, course in enumerate(ctx.get("courses", [])[:5]):
        for day_idx, day in enumerate(days):
            if (course_idx + day_idx) % 3 == 0:  # Not every course every day
                slot_idx = (course_idx + day_idx) % len(times)
                start, end = times[slot_idx]
                inst = ctx["instructors"][course_idx % len(ctx["instructors"])] if ctx.get("instructors") else None
                room = ctx["rooms"][course_idx % 4] if ctx.get("rooms") else None
                try:
                    _create("Course Schedule", {
                        "course": course,
                        "instructor": inst[0] if inst else None,
                        "room": room,
                        "schedule_date": None,
                        "from_time": start,
                        "to_time": end,
                    })
                except:
                    pass

    # Student Attendance (20 days × 5 courses for key students)
    base_date = date(2025, 8, 1)
    for sid, sname, prog_idx, email in ctx.get("key_students", []):
        for day_offset in range(20):
            d = base_date + timedelta(days=day_offset)
            if d.weekday() >= 5:  # Skip weekends
                continue
            for course in ctx.get("courses", [])[:5]:
                status = "Present" if random.random() < 0.85 else "Absent"
                try:
                    frappe.get_doc({
                        "doctype": "Student Attendance",
                        "student": sid,
                        "student_name": sname,
                        "course_schedule": None,
                        "date": str(d),
                        "status": status,
                    }).insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
                except:
                    pass

    # Grievances for key students
    grievance_data = [
        ("WiFi connectivity issues in hostel", "Infrastructure", "Resolved"),
        ("Lab equipment not working", "Academic", "Open"),
    ]
    for sid, sname, prog_idx, email in ctx.get("key_students", [])[:2]:
        for subject, category, status in grievance_data:
            _create("Grievance", {
                "subject": subject,
                "raised_by": sid,
                "status": status,
            })

    # Notifications
    notifications = [
        "Fee payment reminder: ₹25,000 due by Sept 30",
        "Mid-semester exams start Oct 15",
        "Library book 'Operating Systems' due for return",
        "Hostel maintenance: WiFi issue resolved",
        "New announcement: Sports Day on Nov 15",
    ]
    for sid, sname, prog_idx, email in ctx.get("key_students", []):
        for msg in notifications:
            _create("User Notification", {
                "subject": msg,
                "for_user": email if frappe.db.exists("User", email) else None,
            })

    # Certificate Requests
    for sid, sname, prog_idx, email in ctx.get("key_students", [])[:2]:
        for cert_type, status in [("Bonafide Certificate", "Approved"), ("Transfer Certificate", "Pending")]:
            _create("Certificate Request", {
                "student": sid,
                "student_name": sname,
                "certificate_type": cert_type,
                "status": status,
            })

    frappe.db.commit()
    print("  Student portal data complete")


def _phase19_transactional(ctx):
    print("\n[Phase 19] Transactional Data...")

    # Notice Board
    notices = [
        ("Mid-Semester Examination Schedule", "Mid-semester exams for Odd Semester 2025 will be held from Oct 15-22."),
        ("Library Extended Hours", "Library will remain open till 10 PM during exam period."),
        ("Sports Day Announcement", "Annual Sports Day will be held on November 15, 2025."),
        ("Placement Drive - TCS", "TCS campus recruitment drive on December 1, 2025."),
        ("Holiday Notice - Diwali", "University will remain closed from Nov 1-5 for Diwali holidays."),
    ]
    for title, content in notices:
        _create("Notice Board", {"title": title, "content": content})

    # Grievance Types
    for gt in ["Academic", "Hostel", "Infrastructure", "Faculty", "Administrative"]:
        _create("Grievance Type", {"grievance_type": gt})

    # Grievance Committee
    _create("Grievance Committee", {"committee_name": "Student Grievance Committee"})
    _create("Grievance Committee", {"committee_name": "Anti-Ragging Committee"})

    # Feedback Forms
    _create("Feedback Form", {"title": "Course Feedback Form", "form_type": "Course"})
    _create("Feedback Form", {"title": "Faculty Feedback Form", "form_type": "Faculty"})

    # University Announcements
    for title in ["Welcome to Odd Semester 2025", "Mid-Semester Exam Dates Announced",
                  "Annual Cultural Festival - Techfest 2025"]:
        _create("University Announcement", {"title": title, "announcement_date": nowdate()})

    # Certificate Templates
    for name in ["Bonafide Certificate", "Transfer Certificate", "Character Certificate"]:
        _create("Certificate Template", {"template_name": name})

    # Hostel Visitors
    for i in range(5):
        sid_data = ctx["students"][i] if i < len(ctx.get("students", [])) else None
        if sid_data:
            _create("Hostel Visitor", {
                "visitor_name": f"Visitor {i+1}",
                "student": sid_data[0],
                "student_name": sid_data[1],
                "purpose": "Parent Visit",
                "visit_date": str(date(2025, 9, 15 + i)),
            })

    # Student Feedback (faculty ratings)
    for sid, sname, prog_idx, email in ctx.get("key_students", [])[:3]:
        for inst_id, inst_name in ctx.get("instructors", [])[:3]:
            _create("Student Feedback", {
                "student": sid,
                "student_name": sname,
                "instructor": inst_id,
                "instructor_name": inst_name,
                "academic_year": ctx["academic_year"],
                "academic_term": ctx["academic_term"],
                "overall_rating": random.choice([3, 4, 5]),
            })

    # Suggestions
    suggestions = [
        "Please add more power outlets in the library",
        "Can we have a coffee machine in the CS department?",
        "Request for extended lab hours on weekends",
    ]
    for i, text in enumerate(suggestions):
        sid_data = ctx["students"][i] if i < len(ctx.get("students", [])) else None
        if sid_data:
            _create("Suggestion", {"subject": text})

    frappe.db.commit()
    print("  Transactional data complete")

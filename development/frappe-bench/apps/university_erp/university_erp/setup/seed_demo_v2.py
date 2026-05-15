"""
Comprehensive Demo Data Seeder v2 — `ems.hanumatrix.com`
National Institute of Technology — Academic Year 2026-2027

Reuses helpers + most phases from `seed_comprehensive_demo_data.py` (v1) but:
  - scaled to 200 students (not 510)
  - uses `demo@1234` password
  - dynamic dates centered on today (not hardcoded 2025)
  - adds inline error recovery (RECOVERY_MAP + MANDATORY_DEFAULTS + _safe_with_recovery)
  - adds missing phases: Admissions, full Examinations chain, Inventory,
    Integrations, Notifications, Cross-app report data (Purchase Invoice,
    Salary Slip, HR Attendance, Leave Application, Job Opening, Communication).
  - wires student auto-redirect (Student.user link, role assignment)

Usage:
    bench --site ems.hanumatrix.com execute university_erp.setup.seed_demo_v2.seed_all
    bench --site ems.hanumatrix.com execute university_erp.setup.seed_demo_v2.clean_all
"""

import frappe
import random
import traceback
from frappe.utils import nowdate, add_days, add_months, getdate, today, get_first_day, get_last_day
from datetime import date, timedelta

from university_erp.setup.seed_comprehensive_demo_data import (
    # Reused helpers
    _safe as _safe_v1,
    _exists_or_create,
    _random_name,
    _random_dob,
    # Reused name pools
    FIRST_NAMES_M, FIRST_NAMES_F, LAST_NAMES,
    COMPANY, COMPANY_ABBR,
    PROGRAMS, DEPARTMENTS, COURSE_MAP,
    # Reused phase functions (we override _seed_students + _seed_users for v2)
    _ensure_accounts,
    _seed_core,
    _seed_accounts_settings,
    _seed_departments,
    _seed_programs_courses,
    _seed_faculty,
    _seed_finance,
    _seed_hostel,
    _seed_library,
    _seed_transport,
    _seed_placement,
    _seed_research_obe,
    _seed_lms,
    _seed_grievance_feedback,
    _seed_attendance,
    clean_all as clean_all_v1,
)


# === v2 constants ===========================================================

ACADEMIC_YEAR = "2026-2027"
ACADEMIC_YEAR_PREV = "2025-2026"
PASSWORD = "demo@1234"

# 200 students total, distributed by program
STUDENT_DISTRIBUTION = {
    "BTCSE": 30,
    "BTECE": 28,
    "BTME": 25,
    "BTCE": 25,
    "BTEE": 25,
    "MTCS": 20,
    "MTEC": 20,
    "MBA": 27,
}


# === Inline error recovery ==================================================

# Patterns we recognize + how to fix them mid-run.
RECOVERY_MAP = {
    "Could not find Currency": lambda: _ensure_currency("INR"),
    "Could not find Mode of Payment": lambda: _ensure_mode_of_payment(),
    "Could not find Customer Group": lambda: _ensure_customer_group(),
    "Could not find Territory": lambda: _ensure_territory(),
    "Could not find Holiday List": lambda: _ensure_holiday_list(),
}

# Default values to inject when MandatoryError fires
MANDATORY_DEFAULTS = {
    "posting_date": lambda: nowdate(),
    "due_date": lambda: add_days(nowdate(), 30),
    "transaction_date": lambda: nowdate(),
    "schedule_date": lambda: nowdate(),
    "from_time": "10:00:00",
    "to_time": "11:00:00",
    "currency": "INR",
}


def _ensure_currency(code="INR"):
    if not frappe.db.exists("Currency", code):
        frappe.get_doc({
            "doctype": "Currency",
            "currency_name": code,
            "enabled": 1,
        }).insert(ignore_permissions=True)


def _ensure_mode_of_payment():
    for m in ["Cash", "Bank Transfer", "Cheque", "UPI", "Credit Card"]:
        if not frappe.db.exists("Mode of Payment", m):
            try:
                frappe.get_doc({
                    "doctype": "Mode of Payment",
                    "mode_of_payment": m,
                    "enabled": 1,
                }).insert(ignore_permissions=True)
            except Exception:
                pass


def _ensure_customer_group():
    for g in ["All Customer Groups", "Students"]:
        if not frappe.db.exists("Customer Group", g):
            try:
                frappe.get_doc({
                    "doctype": "Customer Group",
                    "customer_group_name": g,
                    "is_group": 1 if g == "All Customer Groups" else 0,
                }).insert(ignore_permissions=True)
            except Exception:
                pass


def _ensure_territory():
    for t in ["All Territories", "India"]:
        if not frappe.db.exists("Territory", t):
            try:
                frappe.get_doc({
                    "doctype": "Territory",
                    "territory_name": t,
                    "is_group": 1 if t == "All Territories" else 0,
                }).insert(ignore_permissions=True)
            except Exception:
                pass


def _ensure_holiday_list():
    name = "NIT Holidays 2026-27"
    if not frappe.db.exists("Holiday List", name):
        hl = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": name,
            "from_date": "2026-04-01",
            "to_date": "2027-03-31",
        })
        for dt, desc in [
            ("2026-08-15", "Independence Day"),
            ("2026-10-02", "Gandhi Jayanti"),
            ("2026-11-01", "Diwali"),
            ("2026-12-25", "Christmas"),
            ("2027-01-26", "Republic Day"),
            ("2027-03-14", "Holi"),
        ]:
            hl.append("holidays", {"holiday_date": dt, "description": desc})
        try:
            hl.insert(ignore_permissions=True)
        except Exception:
            pass


def _safe_with_recovery(fn_name, fn, *args, max_retries=3, **kwargs):
    """Per-record wrapper with inline error recovery.
    Returns (success, result_or_error_str).
    """
    last_err = None
    for attempt in range(max_retries):
        try:
            result = fn(*args, **kwargs)
            return True, result
        except frappe.LinkValidationError as e:
            last_err = str(e)
            recovered = False
            for pat, fix in RECOVERY_MAP.items():
                if pat in last_err:
                    try:
                        fix()
                        frappe.db.commit()
                        recovered = True
                        break
                    except Exception:
                        pass
            if not recovered:
                # Unknown link — give up on this record
                return False, last_err
        except frappe.MandatoryError as e:
            last_err = str(e)
            # Check if any of our defaults match
            recovered = False
            for field, value_fn in MANDATORY_DEFAULTS.items():
                if field in last_err:
                    # Inject default into the doc-being-created
                    if args and hasattr(args[0], "set"):
                        v = value_fn() if callable(value_fn) else value_fn
                        args[0].set(field, v)
                        recovered = True
                        break
            if not recovered:
                return False, last_err
        except frappe.DuplicateEntryError:
            # idempotent retry — fetch existing
            return True, "duplicate_skipped"
        except AttributeError as e:
            if "lft" in str(e) or "rgt" in str(e):
                # NestedSet bug — pre-set lft/rgt
                if args and hasattr(args[0], "set"):
                    args[0].set("lft", 0)
                    args[0].set("rgt", 0)
                else:
                    return False, str(e)
            else:
                return False, str(e)
        except Exception as e:
            last_err = str(e)
            if "Table" in last_err and "doesn't exist" in last_err:
                # Run migrate to materialize the table
                try:
                    import subprocess
                    subprocess.run(
                        ["bench", "--site", frappe.local.site, "migrate"],
                        capture_output=True, check=False, timeout=120,
                    )
                except Exception:
                    pass
            else:
                return False, last_err
    return False, last_err


# === Override: _seed_core_v2 (force AY = 2026-2027) =========================

def _seed_core_v2(ctx):
    """Override v1 _seed_core: AY=2026-2027 instead of 2025-2026."""
    print("\n[1/20] Core Setup (v2)...")

    company_list = frappe.get_all("Company", pluck="name", limit=1)
    if company_list:
        ctx["company"] = company_list[0]
    else:
        ctx["company"] = COMPANY
    abbr = frappe.db.get_value("Company", ctx["company"], "abbr") or COMPANY_ABBR
    ctx["abbr"] = abbr

    # Both Academic Years
    for ay, start, end in [
        (ACADEMIC_YEAR_PREV, "2025-07-01", "2026-06-30"),
        (ACADEMIC_YEAR, "2026-07-01", "2027-06-30"),
    ]:
        if not frappe.db.exists("Academic Year", ay):
            _exists_or_create("Academic Year", {"name": ay}, {
                "academic_year_name": ay,
                "year_start_date": start,
                "year_end_date": end,
            })
    ctx["academic_year"] = ACADEMIC_YEAR

    # Academic Terms — both years × 2 terms each
    for ay, term_name, start, end in [
        (ACADEMIC_YEAR_PREV, "Semester 1", "2025-07-01", "2025-12-31"),
        (ACADEMIC_YEAR_PREV, "Semester 2", "2026-01-01", "2026-06-30"),
        (ACADEMIC_YEAR, "Semester 1", "2026-07-01", "2026-12-31"),
        (ACADEMIC_YEAR, "Semester 2", "2027-01-01", "2027-06-30"),
    ]:
        existing = frappe.db.get_value(
            "Academic Term",
            {"term_name": term_name, "academic_year": ay},
            "name",
        )
        if not existing:
            try:
                frappe.get_doc({
                    "doctype": "Academic Term",
                    "term_name": term_name,
                    "academic_year": ay,
                    "term_start_date": start,
                    "term_end_date": end,
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  WARN: Academic Term {ay}/{term_name}: {str(e)[:100]}")

    # Current term: Sem 2 of 2026-2027 (because we are in Apr 2026, but we want
    # data to look forward — students ARE in current academic period)
    ctx["academic_term"] = frappe.db.get_value(
        "Academic Term",
        {"term_name": "Semester 2", "academic_year": ACADEMIC_YEAR},
        "name",
    ) or "Semester 2"

    # Fiscal Years: previous + current
    for fy, start, end in [
        ("2025-2026", "2025-04-01", "2026-03-31"),
        (ACADEMIC_YEAR, "2026-04-01", "2027-03-31"),
    ]:
        if not frappe.db.exists("Fiscal Year", fy):
            _exists_or_create("Fiscal Year", {"name": fy}, {
                "year": fy,
                "year_start_date": start,
                "year_end_date": end,
                "is_short_year": 0,
            })

    # Link FY to Company (avoid the FiscalYearError we hit during wipe)
    try:
        fy_doc = frappe.get_doc("Fiscal Year", ACADEMIC_YEAR)
        existing_companies = [c.company for c in fy_doc.companies]
        if ctx["company"] not in existing_companies:
            fy_doc.append("companies", {"company": ctx["company"]})
            fy_doc.flags.ignore_permissions = True
            fy_doc.flags.ignore_mandatory = True
            fy_doc.save()
    except Exception as e:
        print(f"  WARN: FY company link: {str(e)[:100]}")

    # University-specific accounts
    _ensure_accounts(ctx)

    # Designations
    for d in [
        "Professor", "Associate Professor", "Assistant Professor",
        "Lab Instructor", "Registrar", "Librarian", "Warden",
        "Administrative Officer", "Finance Officer", "Transport Officer",
        "HOD", "Dean",
    ]:
        if not frappe.db.exists("Designation", d):
            try:
                frappe.db.sql(
                    "INSERT IGNORE INTO tabDesignation "
                    "(name, creation, modified, owner, modified_by) "
                    "VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator')",
                    d,
                )
            except Exception:
                pass

    # Holiday List for current AY
    _ensure_holiday_list()
    ctx["holiday_list"] = "NIT Holidays 2026-27"

    # Mode of Payment
    _ensure_mode_of_payment()

    # Customer Group + Territory + Default Customer
    _ensure_customer_group()
    _ensure_territory()
    if not frappe.db.exists("Customer", "Student Customer"):
        try:
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Student Customer",
                "customer_group": "Students",
                "territory": "India",
                "customer_type": "Individual",
            }).insert(ignore_permissions=True)
        except Exception as e:
            print(f"  WARN: default Customer: {str(e)[:100]}")
    ctx["default_customer"] = "Student Customer"

    # Student Categories
    for c in ["General", "SC/ST", "OBC", "EWS"]:
        if not frappe.db.exists("Student Category", c):
            _exists_or_create("Student Category", {"name": c}, {"category": c})

    # Student Batch Names
    for b in ["2024", "2025", "2026"]:
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

    # Grading Scale
    if not frappe.db.exists("Grading Scale", "10-point CGPA"):
        try:
            gs = frappe.get_doc({
                "doctype": "Grading Scale",
                "grading_scale_name": "10-point CGPA",
                "intervals": [
                    {"grade_code": "A+", "threshold": 90.0, "grade_description": "Outstanding"},
                    {"grade_code": "A", "threshold": 80.0, "grade_description": "Excellent"},
                    {"grade_code": "B+", "threshold": 70.0, "grade_description": "Very Good"},
                    {"grade_code": "B", "threshold": 60.0, "grade_description": "Good"},
                    {"grade_code": "C", "threshold": 50.0, "grade_description": "Average"},
                    {"grade_code": "D", "threshold": 40.0, "grade_description": "Pass"},
                    {"grade_code": "F", "threshold": 0.0, "grade_description": "Fail"},
                ],
            })
            gs.insert(ignore_permissions=True)
        except Exception as e:
            print(f"  WARN: Grading Scale: {str(e)[:100]}")

    # Rooms
    rooms = [
        ("LH-101", "Lecture Hall 1", 120), ("LH-102", "Lecture Hall 2", 120),
        ("LH-103", "Lecture Hall 3", 80), ("LH-104", "Lecture Hall 4", 80),
        ("LH-105", "Lecture Hall 5", 80), ("LH-106", "Lecture Hall 6", 60),
        ("CS-LAB", "Computer Science Lab", 60), ("EC-LAB", "Electronics Lab", 40),
        ("ME-LAB", "Mechanical Lab", 40), ("PH-LAB", "Physics Lab", 40),
        ("SH-01", "Seminar Hall", 200),
        ("EH-01", "Exam Hall 1", 150), ("EH-02", "Exam Hall 2", 150),
    ]
    ctx["rooms"] = []
    for code, name, cap in rooms:
        rid = _exists_or_create("Room", {"room_number": code}, {
            "room_name": name, "room_number": code, "seating_capacity": cap,
        })
        if rid:
            ctx["rooms"].append(rid)

    frappe.db.commit()
    print(f"  Core: AY={ACADEMIC_YEAR}, Term={ctx['academic_term']}, {len(ctx['rooms'])} rooms")


# === Override: _seed_students_v2 (200 students, attached User for first 5) ==

def _seed_students_v2(ctx):
    print("\n[6/20] Students (200) + first 5 with portal User...")

    # Skip auto-user creation during bulk insert
    try:
        edu_settings = frappe.get_single("Education Settings")
        edu_settings.user_creation_skip = 1
        edu_settings.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        pass

    ctx["students"] = []
    ctx["guardians"] = []
    total = 0
    used_emails = set()

    for pid, pname, pabbr in ctx.get("programs", []):
        target = STUDENT_DISTRIBUTION.get(pabbr, 25)
        batches = ["2024", "2025", "2026"]
        prog_created = 0

        for idx in range(target):
            gender = "Male" if idx % 2 == 0 else "Female"
            first, last = _random_name(gender)
            batch = batches[idx % 3]
            enroll = f"NIT-{batch}-{pabbr}-{idx+1:03d}"

            email = f"{first.lower()}.{last.lower()}.{pabbr.lower()}.{idx+1}@nit.edu"
            while email in used_emails:
                email = f"{first.lower()}{idx+1}.{last.lower()}.{pabbr.lower()}@nit.edu"
            used_emails.add(email)

            full_name = f"{first} {last}"
            dob = _random_dob(2000, 2006) if pabbr.startswith("BT") else _random_dob(1998, 2003)

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
                    "joining_date": "2026-07-01",
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

    # Program Enrollments + Course Enrollments + Student Groups
    enrolled = 0
    for sid, sname, pid, pname, pabbr, batch, email in ctx["students"]:
        if not frappe.db.exists("Program Enrollment", {"student": sid, "program": pid}):
            try:
                pe = frappe.get_doc({
                    "doctype": "Program Enrollment",
                    "student": sid,
                    "student_name": sname,
                    "program": pid,
                    "academic_year": ACADEMIC_YEAR,
                    "academic_term": ctx["academic_term"],
                    "enrollment_date": nowdate(),
                    "student_batch_name": batch,
                })
                pe.insert(ignore_permissions=True, ignore_links=True)
                pe.submit()
                enrolled += 1
            except Exception:
                pass
    frappe.db.commit()
    print(f"  Program enrollments: {enrolled}")

    # Set Student.user for first 5 students (link demo portal users)
    # Will be created in _seed_users_v2; here we just earmark
    ctx["portal_students"] = ctx["students"][:5]

    # Guardians
    guardian_count = 0
    for i in range(0, min(len(ctx["students"]), 70 * 3), 3):
        sid, sname, pid, pname, pabbr, batch, email = ctx["students"][i]
        gname = f"Mr. {sname.split()[-1]}"  # parent shares last name
        try:
            g = frappe.get_doc({
                "doctype": "Guardian",
                "guardian_name": gname,
                "email_address": f"parent.{sname.split()[0].lower()}@nit.edu",
                "mobile_number": f"9{random.randint(100000000, 999999999)}",
            })
            g.insert(ignore_permissions=True, ignore_links=True)
            ctx["guardians"].append((g.name, gname, sid))
            guardian_count += 1
        except Exception:
            pass
    frappe.db.commit()
    print(f"  Guardians: {guardian_count}")

    print(f"  TOTAL: {total} students, {enrolled} program enrollments, {guardian_count} guardians")


# === Override: _seed_users_v2 (proper portal redirect setup) ================

def _seed_users_v2(ctx):
    """Create demo users with correct roles for student portal redirect."""
    print("\n[19/20] Demo Users (with portal redirect roles)...")
    created = 0

    # 5 student users — Student + University Student roles ONLY (no System Manager)
    for i in range(5):
        if i >= len(ctx.get("portal_students", [])):
            break
        sid, sname, pid, pname, pabbr, batch, email = ctx["portal_students"][i]
        parts = sname.split()
        portal_email = f"student{i+1}@nit.edu"

        if not frappe.db.exists("User", portal_email):
            try:
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": portal_email,
                    "first_name": parts[0],
                    "last_name": parts[-1] if len(parts) > 1 else "",
                    "enabled": 1,
                    "new_password": PASSWORD,
                    "send_welcome_email": 0,
                    "user_type": "Website User",
                })
                # Critical: ONLY Student + University Student
                # NO System Manager (would override the redirect)
                # NO Administrator
                for role in ["Student", "University Student"]:
                    if frappe.db.exists("Role", role):
                        user.append("roles", {"role": role})

                # Bypass throttle
                old = frappe.local.conf.get("throttle_user_limit", 60)
                frappe.local.conf["throttle_user_limit"] = 9999
                user.flags.ignore_permissions = True
                user.flags.no_welcome_mail = True
                user.flags.ignore_password_policy = True
                user.insert(ignore_permissions=True)
                frappe.local.conf["throttle_user_limit"] = old
                created += 1
            except Exception as e:
                print(f"  WARN student user {portal_email}: {str(e)[:120]}")

        # Link Student.user → portal_email (CRITICAL for get_current_student)
        try:
            frappe.db.set_value("Student", sid, "user", portal_email)
            frappe.db.set_value("Student", sid, "student_email_id", portal_email)
        except Exception as e:
            print(f"  WARN linking Student.user for {sid}: {str(e)[:120]}")
    frappe.db.commit()

    # Faculty users — Faculty roles, no System Manager
    for i in range(2):
        if i >= len(ctx.get("faculty_employees", [])):
            break
        eid, ename = ctx["faculty_employees"][i]
        parts = ename.split()
        femail = f"faculty{i+1}@nit.edu"
        if not frappe.db.exists("User", femail):
            try:
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": femail,
                    "first_name": parts[0],
                    "last_name": parts[-1] if len(parts) > 1 else "",
                    "enabled": 1,
                    "new_password": PASSWORD,
                    "send_welcome_email": 0,
                    "user_type": "System User",
                })
                for role in ["Academics User", "Instructor", "University Faculty"]:
                    if frappe.db.exists("Role", role):
                        user.append("roles", {"role": role})
                user.flags.ignore_permissions = True
                user.flags.no_welcome_mail = True
                user.flags.ignore_password_policy = True
                user.insert(ignore_permissions=True)
                created += 1
            except Exception as e:
                print(f"  WARN faculty user {femail}: {str(e)[:120]}")

    # 1 HOD
    if len(ctx.get("faculty_employees", [])) > 5:
        eid, ename = ctx["faculty_employees"][5]
        parts = ename.split()
        if not frappe.db.exists("User", "hod.cse@nit.edu"):
            try:
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": "hod.cse@nit.edu",
                    "first_name": parts[0],
                    "last_name": parts[-1] if len(parts) > 1 else "",
                    "enabled": 1,
                    "new_password": PASSWORD,
                    "send_welcome_email": 0,
                    "user_type": "System User",
                })
                for role in ["Academics User", "Instructor", "University HOD", "University Faculty"]:
                    if frappe.db.exists("Role", role):
                        user.append("roles", {"role": role})
                user.flags.ignore_permissions = True
                user.flags.no_welcome_mail = True
                user.flags.ignore_password_policy = True
                user.insert(ignore_permissions=True)
                created += 1
            except Exception:
                pass

    # 1 Parent (Guardian)
    if ctx.get("guardians"):
        gid, gname, sid = ctx["guardians"][0]
        parts = gname.replace("Mr. ", "").split()
        if not frappe.db.exists("User", "parent1@nit.edu"):
            try:
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": "parent1@nit.edu",
                    "first_name": parts[0] if parts else "Parent",
                    "last_name": parts[-1] if len(parts) > 1 else "",
                    "enabled": 1,
                    "new_password": PASSWORD,
                    "send_welcome_email": 0,
                    "user_type": "System User",
                })
                if frappe.db.exists("Role", "Guardian"):
                    user.append("roles", {"role": "Guardian"})
                user.flags.ignore_permissions = True
                user.flags.no_welcome_mail = True
                user.flags.ignore_password_policy = True
                user.insert(ignore_permissions=True)
                created += 1
            except Exception:
                pass

    # Management users — university roles ONLY (no System Manager)
    # Each is constrained to their own area; sidebar will filter accordingly.
    management_users = [
        ("admin@nit.edu", "Admin", "User", ["University Admin"]),
        ("registrar@nit.edu", "NIT", "Registrar", ["University Registrar", "Academics User"]),
        ("finance@nit.edu", "NIT", "Finance", ["University Finance", "Accounts Manager"]),
        ("hr@nit.edu", "NIT", "HR", ["University HR Admin", "HR Manager"]),
        ("examcell@nit.edu", "NIT", "ExamCell", ["University Exam Cell"]),
        ("librarian@nit.edu", "NIT", "Librarian", ["University Librarian"]),
        ("warden@nit.edu", "NIT", "Warden", ["University Warden"]),
        ("placement@nit.edu", "NIT", "PlacementOfficer", ["University Placement Officer"]),
    ]
    for email, first, last, roles in management_users:
        if not frappe.db.exists("User", email):
            try:
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "enabled": 1,
                    "new_password": PASSWORD,
                    "send_welcome_email": 0,
                    "user_type": "System User",
                })
                for role in roles:
                    if frappe.db.exists("Role", role):
                        user.append("roles", {"role": role})
                user.flags.ignore_permissions = True
                user.flags.no_welcome_mail = True
                user.flags.ignore_password_policy = True
                user.insert(ignore_permissions=True)
                created += 1
            except Exception as e:
                print(f"  WARN management user {email}: {str(e)[:120]}")

    frappe.db.commit()
    print(f"  Created {created} demo users (password: {PASSWORD})")


# === New phase: cross-app report seed data ==================================

def _seed_cross_app_reports(ctx):
    """Seed minimal data for ERPNext / HRMS / Education reports."""
    print("\n[20/20] Cross-app report data...")
    company = ctx.get("company", COMPANY)

    # === HR Attendance for first 30 employees, last 22 working days ===
    att_count = 0
    if ctx.get("faculty_employees"):
        for eid, ename in ctx["faculty_employees"][:30]:
            for d_offset in range(22):
                att_date = add_days(nowdate(), -d_offset - 1)
                if not frappe.db.exists("Attendance", {"employee": eid, "attendance_date": att_date}):
                    try:
                        a = frappe.get_doc({
                            "doctype": "Attendance",
                            "employee": eid,
                            "attendance_date": att_date,
                            "status": "Present" if d_offset % 6 != 0 else "On Leave",
                            "company": company,
                        })
                        a.insert(ignore_permissions=True)
                        a.submit()
                        att_count += 1
                    except Exception:
                        pass
    frappe.db.commit()
    print(f"  HR Attendance: {att_count}")

    # === HR Leave Applications (5 demo) ===
    leave_count = 0
    if ctx.get("faculty_employees"):
        for eid, ename in ctx["faculty_employees"][:5]:
            try:
                la = frappe.get_doc({
                    "doctype": "Leave Application",
                    "employee": eid,
                    "leave_type": "Casual Leave" if frappe.db.exists("Leave Type", "Casual Leave") else None,
                    "from_date": add_days(nowdate(), 7),
                    "to_date": add_days(nowdate(), 9),
                    "company": company,
                    "status": "Open",
                })
                la.insert(ignore_permissions=True)
                leave_count += 1
            except Exception:
                pass
    frappe.db.commit()
    print(f"  Leave Applications: {leave_count}")

    # === HR Job Opening + Job Applicant ===
    job_count = 0
    desig = frappe.db.get_value("Designation", {"name": "Assistant Professor"}, "name") or \
            frappe.db.get_value("Designation", {}, "name")
    for title, dept_name in [
        ("Assistant Professor - CSE", "Computer Science"),
        ("Lab Assistant - ECE", "Electronics"),
        ("Junior Engineer - ME", "Mechanical"),
    ]:
        if not frappe.db.exists("Job Opening", {"job_title": title}):
            try:
                jo = frappe.get_doc({
                    "doctype": "Job Opening",
                    "job_title": title,
                    "status": "Open",
                    "company": company,
                    "designation": desig,
                    "publish": 0,
                })
                jo.flags.ignore_permissions = True
                jo.flags.ignore_mandatory = True
                jo.insert(ignore_permissions=True)
                job_count += 1
            except Exception as e:
                if job_count == 0:
                    print(f"  Job Opening note: {str(e)[:120]}")
    frappe.db.commit()
    applicant_count = 0
    job_openings = frappe.get_all("Job Opening", limit=3, pluck="name")
    if job_openings:
        for i in range(5):
            try:
                ja = frappe.get_doc({
                    "doctype": "Job Applicant",
                    "applicant_name": f"Applicant {i+1}",
                    "email_id": f"applicant{i+1}@example.com",
                    "job_title": job_openings[i % len(job_openings)],
                    "status": "Open",
                })
                ja.insert(ignore_permissions=True)
                applicant_count += 1
            except Exception:
                pass
    frappe.db.commit()
    print(f"  Job Opening: {job_count}, Job Applicant: {applicant_count}")

    # === Communication (Frappe core) — 30 demo email logs ===
    comm_count = 0
    for i in range(30):
        try:
            c = frappe.get_doc({
                "doctype": "Communication",
                "communication_type": "Communication",
                "subject": f"Demo communication {i+1}",
                "content": f"<p>Demo email content {i+1}</p>",
                "sender": "noreply@nit.edu",
                "recipients": f"student{(i % 5) + 1}@nit.edu",
                "communication_medium": "Email",
                "sent_or_received": "Sent",
                "delivery_status": "Sent",
                "communication_date": add_days(nowdate(), -i),
            })
            c.insert(ignore_permissions=True)
            comm_count += 1
        except Exception:
            pass
    frappe.db.commit()
    print(f"  Communication: {comm_count}")

    # === Sales Invoice = Tuition fees per student (200 invoices) ===
    si_count = 0
    paid_count = 0
    income_account = frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Income Account", "is_group": 0},
        "name",
    ) or frappe.db.get_value("Account", {"company": company, "root_type": "Income", "is_group": 0}, "name")
    debtors_account = frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Receivable", "is_group": 0},
        "name",
    )

    # Customer's `name` is auto-generated (CUST-2026-...). Look it up by customer_name.
    student_customer = frappe.db.get_value(
        "Customer", {"customer_name": "Student Customer"}, "name"
    )
    if not student_customer:
        # Create on-demand with all required fields populated
        try:
            cg = "Students" if frappe.db.exists("Customer Group", "Students") else "All Customer Groups"
            tg = "India" if frappe.db.exists("Territory", "India") else "All Territories"
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Student Customer",
                "customer_group": cg,
                "territory": tg,
                "customer_type": "Individual",
            })
            doc.insert(ignore_permissions=True)
            student_customer = doc.name
            print(f"  Created Student Customer: {student_customer}")
        except Exception as e:
            print(f"  ERR creating Student Customer: {str(e)[:120]}")
            student_customer = None

    if income_account and debtors_account and student_customer and ctx.get("students"):
        for sid, sname, pid, pname, pabbr, batch, email in ctx["students"][:200]:
            try:
                si = frappe.get_doc({
                    "doctype": "Sales Invoice",
                    "customer": student_customer,
                    "company": company,
                    "posting_date": add_days(nowdate(), -random.randint(1, 60)),
                    "due_date": add_days(nowdate(), random.randint(1, 30)),
                    "debit_to": debtors_account,
                    "currency": "INR",
                    "items": [{
                        "item_name": f"Tuition Fee - {pabbr}",
                        "description": f"Tuition for {sname} ({sid})",
                        "qty": 1,
                        "rate": 50000 if pabbr.startswith("BT") else 75000,
                        "income_account": income_account,
                    }],
                })
                si.flags.ignore_permissions = True
                si.flags.ignore_mandatory = True
                si.insert(ignore_permissions=True)
                si.submit()
                si_count += 1

                # ~70% paid
                if random.random() < 0.7:
                    cash_acct = frappe.db.get_value(
                        "Account",
                        {"company": company, "account_type": "Cash", "is_group": 0},
                        "name",
                    ) or frappe.db.get_value(
                        "Account",
                        {"company": company, "account_type": "Bank", "is_group": 0},
                        "name",
                    )
                    if cash_acct:
                        try:
                            pe = frappe.get_doc({
                                "doctype": "Payment Entry",
                                "payment_type": "Receive",
                                "company": company,
                                "posting_date": si.posting_date,
                                "party_type": "Customer",
                                "party": student_customer,
                                "paid_from": debtors_account,
                                "paid_to": cash_acct,
                                "paid_amount": si.grand_total,
                                "received_amount": si.grand_total,
                                "source_exchange_rate": 1,
                                "target_exchange_rate": 1,
                                "references": [{
                                    "reference_doctype": "Sales Invoice",
                                    "reference_name": si.name,
                                    "total_amount": si.grand_total,
                                    "outstanding_amount": si.grand_total,
                                    "allocated_amount": si.grand_total,
                                }],
                            })
                            pe.flags.ignore_permissions = True
                            pe.flags.ignore_mandatory = True
                            pe.insert(ignore_permissions=True)
                            pe.submit()
                            paid_count += 1
                        except Exception:
                            pass
            except Exception as e:
                if si_count == 0:
                    print(f"  Sales Invoice creation note: {str(e)[:200]}")
    frappe.db.commit()
    print(f"  Sales Invoice: {si_count} (Paid via Payment Entry: {paid_count})")

    print(f"  Cross-app data complete.")


# === clean_all wrapper ======================================================

def clean_all():
    """Delegate to v1 clean_all + extra cleanup for v2-only doctypes."""
    clean_all_v1()
    # v2 extras — financials & HR transactions v1 didn't cover + all Layer 11a–11h
    extra_dts = [
        # Finance transactions
        "Communication", "Job Opening", "Job Applicant",
        "Sales Invoice", "Sales Invoice Item", "Sales Taxes and Charges",
        "Purchase Invoice", "Purchase Invoice Item",
        "Salary Slip", "Salary Detail",
        # Layer 11a — Inventory (child-first)
        "Stock Ledger Entry", "Stock Entry Detail", "Stock Entry",
        "Stock Reconciliation Item", "Stock Reconciliation",
        "Purchase Receipt Item", "Purchase Receipt",
        "Purchase Order Item", "Purchase Order",
        "Material Request Item", "Material Request",
        "Lab Consumable Issue", "Lab Equipment Booking", "Lab Equipment",
        "Asset Maintenance Log", "Asset Maintenance Task", "Asset Maintenance",
        "Asset Movement Item", "Asset Movement",
        "Asset", "Batch",
        "Item", "Supplier",
        # Layer 11b — Admissions
        "Merit List Applicant", "Merit List",
        "Seat Matrix", "Admission Criteria", "Admission Cycle",
        # Layer 11c — Examinations deep
        "Certificate Request", "Certificate Template",
        "Notification Template",
        "Student Transcript Result", "Student Transcript",
        "Revaluation Request", "Answer Sheet",
        "Internal Assessment", "Practical Examination",
        "Question Paper Template Section", "Question Paper Template",
        "External Examiner",
        # Layer 11d — OBE / Accreditation
        "NIRF Data", "NAAC Metric",
        "PO Attainment Entry", "PO Attainment",
        "OBE Survey", "Survey Template Question", "Survey Template",
        "Assessment Rubric", "Accreditation Cycle",
        # Layer 11e — Integrations
        "Bank Transaction", "Webhook Log", "Payment Order",
        "Payment Transaction", "User Device Token",
        "Push Notification Log", "WhatsApp Log",
        "SMS Queue", "SMS Log", "WhatsApp Template",
        "Biometric Attendance Log", "Biometric Device",
        # Layer 11f — Portal richness
        "Student Attendance",
        "Announcement",
        "Course Schedule",
        "Notification Preference",
        "Assessment Result", "Student Result",
        "Student Scholarship",
        "Transport Trip Log",
        "Library Fine", "Book Reservation",
        "Library Transaction",
        "Hostel Maintenance Request", "Hostel Visitor", "Hostel Attendance",
        "Course Registration Course", "Course Registration",
        "Placement Profile", "Student Resume",
        "Student Status Log",
        # Layer 11g — Alumni / Workload
        "Job Posting Program", "Job Posting",
        "Grievance Committee Member", "Grievance Committee",
        "Elective Course Group Course", "Elective Course Group",
        "Timetable Slot", "Teaching Assignment",
        "Workload Distributor",
        "Alumni Event Registration", "Alumni Event",
        "University Alumni", "Alumni",
        # Layer 11h — Analytics / LMS deeper
        "Discussion Reply", "Assignment Submission",
        "Quiz Attempt",
        "LMS Discussion", "LMS Quiz Question", "LMS Quiz",
        "LMS Assignment",
        "Scheduled Report", "KPI Value", "KPI Definition",
        "Custom Dashboard",
        # Layer 11i — Remaining
        "Bulk Fee Generator",
        "University Announcement",
        "Temporary Teaching Assignment",
        "Student Feedback",
        "Research Grant",
        "Payment Webhook Log",
        "Notice View Log",
        "Mess Menu Item", "Mess Menu",
        "Hostel Bulk Attendance Record", "Hostel Bulk Attendance",
        "Fee Refund",
        "Fee Category",
        "Emergency Acknowledgment",
        "Email Queue Extended",
        "DigiLocker Issued Document",
        "Custom Report Column", "Custom Report Definition",
    ]
    for dt in extra_dts:
        if frappe.db.exists("DocType", dt):
            try:
                count = frappe.db.count(dt)
                if count:
                    frappe.db.sql(f"DELETE FROM `tab{dt}`")
                    # cascade child tables
                    try:
                        meta = frappe.get_meta(dt)
                        for tf in meta.get_table_fields():
                            frappe.db.sql(
                                f"DELETE FROM `tab{tf.options}` WHERE parenttype='{dt}'"
                            )
                    except Exception:
                        pass
                    print(f"  Deleted {count} {dt}")
            except Exception:
                pass
    frappe.db.commit()


# === seed_all orchestrator (v2) =============================================

def _disable_education_user_creation():
    """HARD-disable Education's auto-user-creation via direct SQL on tabSingles.
    This survives clean_all and any subsequent .save() calls in the same run.
    """
    frappe.db.sql(
        "UPDATE tabSingles SET value=%s "
        "WHERE doctype=%s AND field=%s",
        ("1", "Education Settings", "user_creation_skip"),
    )
    # If row doesn't exist yet, insert it
    exists = frappe.db.sql(
        "SELECT 1 FROM tabSingles WHERE doctype=%s AND field=%s",
        ("Education Settings", "user_creation_skip"),
    )
    if not exists:
        frappe.db.sql(
            "INSERT INTO tabSingles (doctype, field, value) VALUES (%s, %s, %s)",
            ("Education Settings", "user_creation_skip", "1"),
        )
    frappe.db.commit()
    frappe.clear_document_cache("Education Settings", "Education Settings")


def _disable_user_throttle():
    """Disable per-day user creation throttle for the seed run."""
    # Throttle uses tabSingles 'System Settings' key 'maximum_users_per_hour' or
    # tabUser count check. Easiest: temporarily monkey-patch throttle function.
    import frappe.core.doctype.user.user as user_mod
    user_mod.throttle_user_creation = lambda *args, **kwargs: None


def _ensure_employee_custom_fields():
    """Make sure custom fields the v1 seeder writes to exist.
    If missing, create them so the seed doesn't fail on `Unknown column`.
    """
    needed = [
        ("Employee", "custom_employee_category", "Select", "Teaching\nNon-Teaching\nAdministrative"),
        ("Employee", "custom_is_faculty", "Check", None),
    ]
    for dt, fieldname, fieldtype, options in needed:
        if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
            try:
                cf = frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": dt,
                    "fieldname": fieldname,
                    "label": fieldname.replace("custom_", "").replace("_", " ").title(),
                    "fieldtype": fieldtype,
                    "options": options,
                    "insert_after": "designation",
                })
                cf.insert(ignore_permissions=True)
                print(f"    Added Custom Field: {dt}.{fieldname}")
            except Exception as e:
                print(f"    WARN Custom Field {dt}.{fieldname}: {str(e)[:80]}")
    frappe.db.commit()


def seed_all():
    """Seed comprehensive demo data — v2.

    Order:
    [1]  Core Setup (v2 — AY=2026-2027)
    [2]  Accounts Settings
    [3]  Departments
    [4]  Programs + Courses
    [5]  Faculty (Employees + Instructors + Faculty Profiles)
    [6]  Students (v2 — 200 students + portal_students earmarked)
    [7]  Finance (Sales Invoice / Payment Entry / Fees / Bulk Fee Generator)
    [8]  Hostel
    [9]  Library
    [10] Transport
    [11] Placement
    [12] Examinations (v1 — partial, will extend later)
    [13] Research & OBE
    [14] LMS
    [15] Grievance & Feedback
    [16] Attendance + Notices
    [17] Demo Users (v2 — proper portal redirect)
    [18] Cross-app report data (Sales Invoice for tuition, Communication, HR Attendance/Leave/Job)
    """
    frappe.flags.ignore_permissions = True
    frappe.flags.in_test = True
    frappe.flags.in_install = True
    frappe.local.flags.mute_emails = True
    frappe.local.flags.no_welcome_mail = True
    frappe.set_user("Administrator")

    print("=" * 60)
    print("SEEDING DEMO DATA (v2)")
    print(f"  Site: {frappe.local.site}")
    print(f"  Academic Year: {ACADEMIC_YEAR}")
    print(f"  Total Students: {sum(STUDENT_DISTRIBUTION.values())}")
    print(f"  Password: {PASSWORD}")
    print("=" * 60)

    clean_all()

    # CRITICAL: Disable Education auto-user-creation + user throttle BEFORE
    # any Student insert. Education's Student.validate_user() will try to
    # create a User row per Student otherwise, hitting the per-hour throttle.
    _disable_education_user_creation()
    _disable_user_throttle()
    _ensure_employee_custom_fields()
    print("\n  ✓ Education auto-user-creation disabled (via tabSingles)")
    print("  ✓ User throttle bypassed (monkey-patched)")
    print("  ✓ Employee Custom Fields ensured\n")

    ctx = {}

    # Layer 1-4: foundation
    _safe_v1("_seed_core_v2", _seed_core_v2, ctx)
    _safe_v1("_seed_accounts_settings", _seed_accounts_settings, ctx)
    _safe_v1("_seed_departments", _seed_departments, ctx)
    _safe_v1("_seed_programs_courses", _seed_programs_courses, ctx)

    # Layer 5: people
    _safe_v1("_seed_faculty", _seed_faculty, ctx)
    _safe_v1("_seed_students_v2", _seed_students_v2, ctx)
    _safe_v1("_seed_enrollments_v2", _seed_enrollments_v2, ctx)

    # Layer 7-11: domain
    _safe_v1("_seed_finance", _seed_finance, ctx)
    _safe_v1("_seed_hostel", _seed_hostel, ctx)
    _safe_v1("_seed_library", _seed_library, ctx)
    _safe_v1("_seed_library_transactions_v2", _seed_library_transactions_v2, ctx)
    _safe_v1("_seed_transport", _seed_transport, ctx)
    _safe_v1("_seed_placement_v2", _seed_placement_v2, ctx)
    _safe_v1("_seed_examinations", _safe_phase_v1_examinations, ctx)
    _safe_v1("_seed_hall_tickets_v2", _seed_hall_tickets_v2, ctx)
    _safe_v1("_seed_research_obe", _seed_research_obe, ctx)
    _safe_v1("_seed_obe_v2", _seed_obe_v2, ctx)
    _safe_v1("_seed_lms", _seed_lms, ctx)
    _safe_v1("_seed_grievance_feedback", _seed_grievance_feedback, ctx)
    _safe_v1("_seed_attendance", _seed_attendance, ctx)

    # Layer 13: users with portal redirect — must run BEFORE notifications
    _safe_v1("_seed_users_v2", _seed_users_v2, ctx)

    _safe_v1("_seed_user_notifications_v2", _seed_user_notifications_v2, ctx)

    # Top-up missing doctypes (Topic, Fee Structure, LMS Content, etc.)
    _safe_v1("_seed_topups_v2", _seed_topups_v2, ctx)

    # Layer 8/cross-app: more reports data + Sales Invoice for finance reports
    _safe_v1("_seed_cross_app_reports", _seed_cross_app_reports, ctx)

    # Layer 11a–11i: coverage extension (all 148 doctypes, all reports, portal richness)
    _safe_v1("_seed_inventory_v2", _seed_inventory_v2, ctx)
    _safe_v1("_seed_admissions_v2", _seed_admissions_v2, ctx)
    _safe_v1("_seed_examinations_deep_v2", _seed_examinations_deep_v2, ctx)
    _safe_v1("_seed_obe_accreditation_v2", _seed_obe_accreditation_v2, ctx)
    _safe_v1("_seed_integrations_v2", _seed_integrations_v2, ctx)
    _safe_v1("_seed_portal_richness_v2", _seed_portal_richness_v2, ctx)
    _safe_v1("_seed_alumni_portals_v2", _seed_alumni_portals_v2, ctx)
    _safe_v1("_seed_analytics_v2", _seed_analytics_v2, ctx)
    _safe_v1("_seed_remaining_v2", _seed_remaining_v2, ctx)

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("SEED COMPLETE")
    print("=" * 60)

    # Final counts
    for dt in [
        "Student", "Employee", "Program", "Course", "Fees",
        "Sales Invoice", "Payment Entry", "GL Entry",
        "Hostel Allocation", "Library Article", "Library Transaction",
        "Transport Allocation", "Placement Application",
        "User", "Has Role",
    ]:
        if frappe.db.exists("DocType", dt):
            try:
                print(f"  {dt}: {frappe.db.count(dt)}")
            except Exception:
                pass

    print("\nDemo Login Credentials (password: " + PASSWORD + "):")
    print("-" * 60)
    for email in [
        "student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
        "faculty1@nit.edu", "faculty2@nit.edu",
        "hod.cse@nit.edu", "parent1@nit.edu",
        "admin@nit.edu", "registrar@nit.edu", "finance@nit.edu",
        "hr@nit.edu", "examcell@nit.edu",
        "librarian@nit.edu", "warden@nit.edu", "placement@nit.edu",
    ]:
        print(f"  {email}")
    print("-" * 60)


def _safe_phase_v1_examinations(ctx):
    """Wrapper to call v1 _seed_examinations with our import already done."""
    from university_erp.setup.seed_comprehensive_demo_data import _seed_examinations
    _seed_examinations(ctx)


# === Additional v2 phases to fill gaps =====================================

def _seed_enrollments_v2(ctx):
    """Create Program Enrollment + Course Enrollment + Student Group + members.
    These were not produced by v1 phases for v2's 200 students.
    """
    print("\n[6b/20] Enrollments + Student Groups...")
    if not ctx.get("students") or not ctx.get("courses"):
        print("  no students/courses — skip")
        return

    # Group courses by program (use COURSE_MAP)
    pe_count = 0
    ce_count = 0
    sg_count = 0
    sgs_count = 0

    # Pick courses per program from COURSE_MAP
    courses_by_program = {}
    for cid, cname, ccode in ctx["courses"]:
        for pabbr, course_list in COURSE_MAP.items():
            for course_name, code in course_list:
                if course_name == cname:
                    courses_by_program.setdefault(pabbr, []).append((cid, cname))
                    break

    # Create student groups: 1 per (Program, Course, current term)
    student_groups = {}  # (pabbr, cid) -> sg_name
    for pid, pname, pabbr in ctx.get("programs", []):
        for cid, cname in courses_by_program.get(pabbr, [])[:5]:  # first 5 courses per program
            sg_name = f"{pabbr}-{cid[:30]}-{ctx['academic_term'][:15]}"[:140]
            if not frappe.db.exists("Student Group", sg_name):
                try:
                    sg = frappe.get_doc({
                        "doctype": "Student Group",
                        "student_group_name": sg_name,
                        "academic_year": ctx["academic_year"],
                        "academic_term": ctx["academic_term"],
                        "group_based_on": "Course",
                        "course": cid,
                        "program": pid,
                        "max_strength": 100,
                    })
                    sg.insert(ignore_permissions=True, ignore_links=True)
                    student_groups[(pabbr, cid)] = sg.name
                    sg_count += 1
                except Exception as e:
                    if sg_count == 0:
                        print(f"  WARN Student Group {sg_name}: {str(e)[:120]}")

    frappe.db.commit()

    # Per-student: Program Enrollment + Course Enrollment + Student Group Student
    # Enrollment date must be >= max(academic_year.year_start_date, academic_term.term_start_date).
    ay_start = frappe.db.get_value(
        "Academic Year", ctx["academic_year"], "year_start_date"
    )
    term_start = frappe.db.get_value(
        "Academic Term", ctx["academic_term"], "term_start_date"
    )
    if term_start and ay_start:
        enroll_date = str(max(getdate(ay_start), getdate(term_start)))
    elif term_start:
        enroll_date = str(term_start)
    elif ay_start:
        enroll_date = str(ay_start)
    else:
        enroll_date = "2026-07-01"

    for sid, sname, pid, pname, pabbr, batch, email in ctx["students"]:
        # Program Enrollment
        pe = frappe.db.get_value("Program Enrollment", {"student": sid, "program": pid}, "name")
        if not pe:
            try:
                doc = frappe.get_doc({
                    "doctype": "Program Enrollment",
                    "student": sid,
                    "student_name": sname,
                    "program": pid,
                    "academic_year": ctx["academic_year"],
                    "academic_term": ctx["academic_term"],
                    "enrollment_date": enroll_date,
                    "student_batch_name": batch,
                })
                doc.flags.ignore_permissions = True
                doc.flags.ignore_links = True
                doc.flags.ignore_mandatory = True
                doc.insert(ignore_permissions=True, ignore_links=True)
                try:
                    doc.submit()
                except Exception:
                    pass
                pe = doc.name
                pe_count += 1
            except Exception:
                continue

        # Course Enrollments + Student Group memberships
        for (gp_pabbr, cid), sg_name in student_groups.items():
            if gp_pabbr != pabbr:
                continue
            # Course Enrollment
            if not frappe.db.exists("Course Enrollment", {"student": sid, "course": cid}):
                try:
                    ce = frappe.get_doc({
                        "doctype": "Course Enrollment",
                        "student": sid,
                        "course": cid,
                        "program_enrollment": pe,
                        "enrollment_date": enroll_date,
                        "academic_year": ctx["academic_year"],
                        "academic_term": ctx["academic_term"],
                    })
                    ce.flags.ignore_permissions = True
                    ce.flags.ignore_links = True
                    ce.flags.ignore_mandatory = True
                    ce.insert(ignore_permissions=True, ignore_links=True)
                    ce_count += 1
                except Exception:
                    pass
            # Student Group Student
            try:
                sg_doc = frappe.get_doc("Student Group", sg_name)
                # Skip if already a member
                if not any(s.student == sid for s in sg_doc.students):
                    sg_doc.append("students", {
                        "student": sid,
                        "student_name": sname,
                        "active": 1,
                    })
                    sg_doc.flags.ignore_permissions = True
                    sg_doc.flags.ignore_mandatory = True
                    sg_doc.save(ignore_permissions=True)
                    sgs_count += 1
            except Exception:
                pass

    frappe.db.commit()
    print(f"  {pe_count} program enrollments, {ce_count} course enrollments, {sg_count} student groups, {sgs_count} memberships")


def _seed_obe_v2(ctx):
    """Seed PEO/PO/CO + CO-PO Mapping with all required fields."""
    print("\n[14b/20] OBE — PEOs + POs + COs + CO-PO Mapping...")
    if not ctx.get("programs") or not ctx.get("courses"):
        return

    peo_count = po_count = co_count = mapping_count = 0

    # PEO + PO per program (NBA standard 12 POs)
    peo_statements = [
        "Apply technical knowledge to solve real-world problems",
        "Engage in lifelong learning and professional development",
        "Demonstrate ethical and social responsibility",
        "Lead and collaborate effectively in diverse teams",
    ]
    po_data = [
        ("PO1", "Engineering Knowledge", "Apply knowledge of mathematics, science, and engineering"),
        ("PO2", "Problem Analysis", "Identify, formulate, and analyze complex engineering problems"),
        ("PO3", "Design/Development", "Design solutions for complex engineering problems"),
        ("PO4", "Investigation", "Use research-based knowledge and methods"),
        ("PO5", "Modern Tools", "Apply techniques, resources, and modern engineering tools"),
        ("PO6", "Engineer & Society", "Apply contextual knowledge to assess societal issues"),
        ("PO7", "Environment", "Understand environmental and sustainability impact"),
        ("PO8", "Ethics", "Apply ethical principles and professional ethics"),
        ("PO9", "Individual & Team Work", "Function effectively as an individual and team member"),
        ("PO10", "Communication", "Communicate effectively with engineering community"),
        ("PO11", "Project Management", "Apply engineering management principles"),
        ("PO12", "Life-long Learning", "Engage in independent and life-long learning"),
    ]

    for pid, pname, pabbr in ctx["programs"]:
        # PEOs
        for i, stmt in enumerate(peo_statements):
            if not frappe.db.exists("Program Educational Objective", {"program": pid, "peo_number": i + 1}):
                try:
                    frappe.get_doc({
                        "doctype": "Program Educational Objective",
                        "program": pid,
                        "peo_number": i + 1,
                        "peo_statement": stmt,
                    }).insert(ignore_permissions=True, ignore_links=True)
                    peo_count += 1
                except Exception:
                    pass

        # POs — po_code is globally unique, so prefix with program abbreviation
        for code, title, stmt in po_data:
            unique_code = f"{pabbr}-{code}"
            if not frappe.db.exists("Program Outcome", {"po_code": unique_code}):
                try:
                    frappe.get_doc({
                        "doctype": "Program Outcome",
                        "program": pid,
                        "po_code": unique_code,
                        "po_number": int(code[2:]),
                        "po_title": title,
                        "po_statement": stmt,
                    }).insert(ignore_permissions=True, ignore_links=True)
                    po_count += 1
                except Exception:
                    pass

    frappe.db.commit()

    # COs per course (3 per course)
    co_statements = [
        ("Understand fundamentals", "Understand"),
        ("Apply techniques to problems", "Apply"),
        ("Analyze and design solutions", "Analyze"),
    ]
    for cid, cname, ccode in ctx["courses"][:30]:
        for i, (stmt, bloom) in enumerate(co_statements):
            if not frappe.db.exists("Course Outcome", {"course": cid, "co_number": i + 1}):
                try:
                    frappe.get_doc({
                        "doctype": "Course Outcome",
                        "course": cid,
                        "co_number": i + 1,
                        "co_statement": f"Students will be able to {stmt} in {cname}",
                        "bloom_level": bloom,
                    }).insert(ignore_permissions=True, ignore_links=True)
                    co_count += 1
                except Exception:
                    pass

    frappe.db.commit()

    # CO PO Mapping (one per course, current term)
    for cid, cname, ccode in ctx["courses"][:30]:
        # Find program for this course
        prog = None
        for pabbr, course_list in COURSE_MAP.items():
            for course_name, code in course_list:
                if course_name == cname:
                    prog = next((p[0] for p in ctx["programs"] if p[2] == pabbr), None)
                    break
        if not prog:
            continue
        if not frappe.db.exists("CO PO Mapping", {"course": cid, "academic_term": ctx["academic_term"]}):
            try:
                copo = frappe.get_doc({
                    "doctype": "CO PO Mapping",
                    "course": cid,
                    "program": prog,
                    "academic_term": ctx["academic_term"],
                })
                # Get COs and POs for this course/program
                cos = frappe.get_all(
                    "Course Outcome", filters={"course": cid}, pluck="name", limit=3
                )
                pos = frappe.get_all(
                    "Program Outcome", filters={"program": prog}, pluck="name", limit=12
                )
                for co in cos:
                    for po in pos[:4]:  # only first 4 POs per CO for variety
                        copo.append("mapping_table", {
                            "course_outcome": co,
                            "program_outcome": po,
                            "correlation_level": random.choice(["1 - Low", "2 - Medium", "3 - High"]),
                        })
                copo.flags.ignore_permissions = True
                copo.flags.ignore_links = True
                copo.flags.ignore_mandatory = True
                copo.insert(ignore_permissions=True, ignore_links=True)
                mapping_count += 1
            except Exception as e:
                if mapping_count == 0:
                    print(f"  CO PO Mapping note: {str(e)[:120]}")

    frappe.db.commit()
    print(f"  {peo_count} PEOs, {po_count} POs, {co_count} COs, {mapping_count} CO-PO mappings")


def _seed_library_transactions_v2(ctx):
    """Library Transactions for the existing Library Members + Articles."""
    print("\n[10b/20] Library Transactions...")
    members = frappe.get_all("Library Member", limit=30, fields=["name", "member_name", "student"])
    articles = frappe.get_all("Library Article", limit=50, fields=["name", "title"])
    if not members or not articles:
        print(f"  members={len(members)}, articles={len(articles)} - skip")
        return

    tx_count = 0
    fine_count = 0
    for i in range(min(50, len(members) * 2)):
        m = members[i % len(members)]
        a = articles[i % len(articles)]
        issue_date = add_days(nowdate(), -random.randint(1, 60))
        due_date = add_days(issue_date, 14)
        is_returned = random.random() < 0.6
        return_date = add_days(due_date, random.randint(-3, 10)) if is_returned else None
        try:
            tx = frappe.get_doc({
                "doctype": "Library Transaction",
                "transaction_type": "Issue" if not is_returned else "Return",
                "article": a.name,
                "member": m.name,
                "transaction_date": issue_date,
                "issue_date": issue_date,
                "due_date": due_date,
                "return_date": return_date,
                "status": "Returned" if is_returned else "Active",
            })
            tx.flags.ignore_permissions = True
            tx.flags.ignore_links = True
            tx.flags.ignore_mandatory = True
            tx.insert(ignore_permissions=True, ignore_links=True)
            tx_count += 1
            # Fine for late returns
            if is_returned and return_date and getdate(return_date) > getdate(due_date):
                try:
                    days_late = (getdate(return_date) - getdate(due_date)).days
                    fine = frappe.get_doc({
                        "doctype": "Library Fine",
                        "member": m.name,
                        "transaction": tx.name,
                        "article": a.name,
                        "fine_date": return_date,
                        "fine_amount": days_late * 5,
                        "status": "Unpaid",
                        "reason": f"{days_late} days late return",
                    })
                    fine.insert(ignore_permissions=True, ignore_links=True)
                    fine_count += 1
                except Exception:
                    pass
        except Exception as e:
            if tx_count == 0:
                print(f"  Library Tx note: {str(e)[:120]}")
    frappe.db.commit()
    print(f"  {tx_count} library transactions, {fine_count} fines")


def _seed_placement_v2(ctx):
    """Placement Companies, Job Openings, Drives, Applications."""
    print("\n[11b/20] Placement (v2)...")

    # Industry Type — uses field `industry_name` not `industry_type`
    industries = ["Information Technology", "Banking", "Manufacturing", "Consulting", "Retail", "Healthcare", "Energy", "Education"]
    for ind in industries:
        if not frappe.db.exists("Industry Type", ind):
            try:
                frappe.get_doc({
                    "doctype": "Industry Type",
                    "industry_name": ind,  # CORRECT FIELD NAME
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  WARN Industry Type {ind}: {str(e)[:80]}")

    frappe.db.commit()

    # Placement Companies
    companies_data = [
        ("Tata Consultancy Services", "Information Technology", 600000),
        ("Infosys", "Information Technology", 650000),
        ("Wipro", "Information Technology", 600000),
        ("Amazon", "Information Technology", 1500000),
        ("Google", "Information Technology", 2500000),
        ("Microsoft", "Information Technology", 2200000),
        ("Deloitte", "Consulting", 950000),
        ("HDFC Bank", "Banking", 700000),
        ("Larsen and Toubro", "Manufacturing", 850000),
        ("Flipkart", "Information Technology", 1300000),
    ]
    pc_count = 0
    for name, industry, ctc in companies_data:
        if not frappe.db.exists("Placement Company", name):
            try:
                frappe.get_doc({
                    "doctype": "Placement Company",
                    "company_name": name,
                    "industry_type": industry,
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "India",
                    "average_ctc": ctc,
                    "company_type": "Product" if industry == "Information Technology" else "Service",
                }).insert(ignore_permissions=True, ignore_links=True)
                pc_count += 1
            except Exception as e:
                if pc_count == 0:
                    print(f"  WARN Placement Company: {str(e)[:120]}")
    frappe.db.commit()

    # Placement Job Openings
    pjo_count = 0
    for name, industry, ctc in companies_data:
        if not frappe.db.exists("Placement Company", name):
            continue
        for role in ["Software Engineer", "Analyst"]:
            if not frappe.db.exists("Placement Job Opening", {"company": name, "job_title": role}):
                try:
                    frappe.get_doc({
                        "doctype": "Placement Job Opening",
                        "company": name,
                        "job_title": role,
                        "job_type": "Full Time",
                        "posting_date": add_days(nowdate(), -random.randint(10, 60)),
                        "deadline": add_days(nowdate(), random.randint(5, 30)),
                        "status": "Open",
                        "vacancies": random.randint(2, 10),
                        "min_ctc": int(ctc * 0.7),
                        "max_ctc": ctc,
                        "job_location": "Bangalore",
                        "min_cgpa": 6.5,
                        "batch_year": "2026",
                    }).insert(ignore_permissions=True, ignore_links=True)
                    pjo_count += 1
                except Exception:
                    pass
    frappe.db.commit()

    # Placement Drives + Applications
    drives = frappe.get_all("Placement Job Opening", limit=10, fields=["name", "company", "job_title"])
    pd_count = 0
    pa_count = 0
    placed_count = 0
    if drives and ctx.get("students"):
        for d in drives:
            try:
                # Future drive_date so last_date_to_apply >= today and Open status
                # passes is_application_open() during application insert.
                drive_offset = random.randint(20, 60)
                last_apply_offset = random.randint(7, 19)  # before drive_date, after today
                drive = frappe.get_doc({
                    "doctype": "Placement Drive",
                    "company": d["company"],
                    "job_opening": d["name"],
                    "job_title": d["job_title"],
                    "drive_date": add_days(nowdate(), drive_offset),
                    "drive_end_date": add_days(nowdate(), drive_offset + 1),
                    "last_date_to_apply": add_days(nowdate(), last_apply_offset),
                    "academic_year": ctx["academic_year"],
                    "venue": "Auditorium",
                    "status": "Open",
                })
                drive.flags.ignore_permissions = True
                drive.flags.ignore_links = True
                drive.flags.ignore_mandatory = True
                drive.insert(ignore_permissions=True, ignore_links=True)
                pd_count += 1
            except Exception as e:
                if pd_count == 0:
                    print(f"  Placement Drive note: {str(e)[:200]}")
                continue

        # Applications: ~8 per drive, with mix of statuses
        # NOTE: Live Placement Application is the university_portals one — uses
        # `placement_drive` Link (not job_opening) and `student` only.
        all_drives = frappe.get_all(
            "Placement Drive", limit=20,
            fields=["name", "company", "job_opening"],
        )
        for drv in all_drives:
            for sid, sname, pid, pname, pabbr, batch, email in ctx["students"][:8]:
                if not frappe.db.exists(
                    "Placement Application",
                    {"student": sid, "placement_drive": drv.name},
                ):
                    status = random.choice(["Applied", "Shortlisted", "Selected", "Placed", "Rejected"])
                    try:
                        pa = frappe.get_doc({
                            "doctype": "Placement Application",
                            "student": sid,
                            "student_name": sname,
                            "placement_drive": drv.name,
                        })
                        pa.flags.ignore_permissions = True
                        pa.flags.ignore_links = True
                        pa.insert(ignore_permissions=True, ignore_links=True)
                        # Set status post-insert to bypass eligibility re-validation
                        frappe.db.set_value("Placement Application", pa.name, "status", status, update_modified=False)
                        pa_count += 1
                        if status == "Placed":
                            placed_count += 1
                    except Exception as e:
                        if pa_count == 0:
                            print(f"  Placement App note: {str(e)[:140]}")
        # Now mark drives Completed for realism (post-application)
        for drv in all_drives:
            frappe.db.set_value("Placement Drive", drv.name, "status", "Completed", update_modified=False)
    frappe.db.commit()
    print(f"  {pc_count} companies, {pjo_count} openings, {pd_count} drives, {pa_count} applications ({placed_count} placed)")


def _seed_hall_tickets_v2(ctx):
    """Hall Ticket per student."""
    print("\n[12b/20] Hall Tickets...")
    if not ctx.get("students"):
        return

    ht_count = 0
    for sid, sname, pid, pname, pabbr, batch, email in ctx["students"][:100]:
        if frappe.db.exists("Hall Ticket", {"student": sid, "academic_term": ctx["academic_term"]}):
            continue
        try:
            ht = frappe.get_doc({
                "doctype": "Hall Ticket",
                "student": sid,
                "student_name": sname,
                "academic_term": ctx["academic_term"],
                "academic_year": ctx["academic_year"],
                "exam_type": "Regular",
                "issue_date": nowdate(),
            })
            # Add 4-5 exams
            courses_for_program = []
            for pabbr_cm, course_list in COURSE_MAP.items():
                if pabbr_cm == pabbr:
                    for course_name, code in course_list:
                        course_id = frappe.db.get_value("Course", {"course_name": course_name}, "name")
                        if course_id:
                            courses_for_program.append(course_id)
            for cid in courses_for_program[:5]:
                ht.append("exams", {
                    "course": cid,
                    "exam_date": add_days(nowdate(), random.randint(7, 28)),
                    "from_time": "10:00:00",
                    "to_time": "13:00:00",
                    "venue": "Exam Hall 1",
                })
            ht.flags.ignore_permissions = True
            ht.flags.ignore_links = True
            ht.flags.ignore_mandatory = True
            ht.insert(ignore_permissions=True, ignore_links=True)
            ht_count += 1
        except Exception as e:
            if ht_count == 0:
                print(f"  Hall Ticket note: {str(e)[:140]}")
    frappe.db.commit()
    print(f"  {ht_count} hall tickets")


def _seed_user_notifications_v2(ctx):
    """User Notifications for demo users."""
    print("\n[16b/20] User Notifications...")
    n_count = 0
    demo_users = [
        "student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
        "faculty1@nit.edu", "hod.cse@nit.edu",
    ]
    titles = [
        ("Hall Ticket Issued", "Your hall ticket for End Semester is now available.", "info"),
        ("Fee Reminder", "Your tuition fee is due within 7 days.", "warning"),
        ("Result Published", "Your Sem-1 results are now available on the portal.", "success"),
        ("Class Schedule Updated", "Your class schedule for next week has been updated.", "announcement"),
        ("Library Book Due", "Library book due in 3 days. Please return on time.", "warning"),
    ]
    for u in demo_users:
        if not frappe.db.exists("User", u):
            continue
        for t, m, ntype in titles:
            try:
                frappe.get_doc({
                    "doctype": "User Notification",
                    "user": u,
                    "title": t,
                    "message": m,
                    "notification_type": ntype,
                    "category": "Academic",
                    "priority": "Normal",
                    "read": 0,
                }).insert(ignore_permissions=True, ignore_links=True)
                n_count += 1
            except Exception as e:
                if n_count == 0:
                    print(f"  User Notification note: {str(e)[:120]}")
    frappe.db.commit()
    print(f"  {n_count} user notifications")


def _seed_topups_v2(ctx):
    """Top-up missing doctypes: Topic, Fee Structure, LMS Content, Exam Schedule,
    Question Bank, Research Project/Publication."""
    print("\n[17b/20] Top-up missing doctypes...")

    # --- Topic ---
    topics_extra = [
        "Recursion", "Dynamic Programming", "Graph Theory", "Sorting Algorithms",
        "Searching Algorithms", "Linked Lists", "Trees", "Hash Tables",
        "Networks Layer", "Transport Layer", "TCP/IP", "Routing Protocols",
        "SQL Joins", "Normalization", "Indexing", "Transactions",
        "Process Scheduling", "Memory Management", "File Systems", "Concurrency",
        "OOP Concepts", "Design Patterns", "UML Diagrams", "Software Testing",
        "Linear Algebra", "Calculus", "Probability", "Statistics",
        "Digital Logic", "Microprocessors", "Embedded Systems", "VLSI Design",
    ]
    t_count = 0
    for t in topics_extra:
        if not frappe.db.exists("Topic", t):
            try:
                frappe.get_doc({"doctype": "Topic", "topic_name": t}).insert(
                    ignore_permissions=True, ignore_links=True
                )
                t_count += 1
            except Exception:
                pass

    # --- Fee Structure ---
    fs_count = 0
    if ctx.get("programs") and ctx.get("academic_year"):
        # Find a Receivable account for this Company
        company = frappe.db.get_value("Company", {}, "name")
        rec_acct = frappe.db.get_value(
            "Account",
            {"company": company, "account_type": "Receivable", "is_group": 0},
            "name",
        )
        for pid, pname, pabbr in ctx["programs"][:5]:
            fs_name = f"{pabbr}-{ctx['academic_year']}"
            if frappe.db.exists("Fee Structure", {"program": pid, "academic_year": ctx["academic_year"]}):
                continue
            try:
                fs = frappe.get_doc({
                    "doctype": "Fee Structure",
                    "program": pid,
                    "academic_year": ctx["academic_year"],
                    "receivable_account": rec_acct,
                    "components": [
                        {"fees_category": "Tuition Fee", "amount": 50000},
                        {"fees_category": "Library Fee", "amount": 5000},
                        {"fees_category": "Lab Fee", "amount": 8000},
                    ],
                })
                fs.flags.ignore_mandatory = True
                fs.insert(ignore_permissions=True, ignore_links=True)
                fs_count += 1
            except Exception as e:
                if fs_count == 0:
                    print(f"  Fee Structure note: {str(e)[:140]}")

    # --- LMS Content (use Text type with required text_content) ---
    lc_count = 0
    lms_courses = frappe.get_all("LMS Course", pluck="name", limit=10)
    for lmsc in lms_courses[:8]:
        for i in range(3):
            try:
                frappe.get_doc({
                    "doctype": "LMS Content",
                    "title": f"{lmsc} - Lesson {i+1}",
                    "lms_course": lmsc,
                    "content_type": "Text",
                    "text_content": f"<p>Auto-generated lesson content for {lmsc}, lesson {i+1}.</p>",
                    "description": f"Auto-generated content for {lmsc}",
                }).insert(ignore_permissions=True, ignore_links=True)
                lc_count += 1
            except Exception as e:
                if lc_count == 0:
                    print(f"  LMS Content note: {str(e)[:140]}")

    # --- Exam Schedule ---
    es_count = 0
    if ctx.get("courses") and ctx.get("academic_term"):
        rooms = frappe.get_all("Room", pluck="name", limit=5)
        room_default = rooms[0] if rooms else None
        from frappe.utils import add_days, nowdate
        for i, (cid, cname, ccode) in enumerate(ctx["courses"][:8]):
            try:
                frappe.get_doc({
                    "doctype": "Exam Schedule",
                    "course": cid,
                    "academic_term": ctx["academic_term"],
                    "exam_type": "Mid-Term",
                    "exam_date": add_days(nowdate(), 14 + i),
                    "start_time": "09:00:00",
                    "end_time": "12:00:00",
                    "venue": room_default,
                }).insert(ignore_permissions=True, ignore_links=True)
                es_count += 1
            except Exception as e:
                if es_count == 0:
                    print(f"  Exam Schedule note: {str(e)[:140]}")

    # --- Question Bank ---
    qb_count = 0
    if ctx.get("courses"):
        bloom_levels = ["Remember (L1)", "Understand (L2)", "Apply (L3)", "Analyze (L4)"]
        difficulties = ["Easy", "Medium", "Hard"]
        # Pre-pick an Instructor so set_created_by skips the broken Instructor.user lookup
        first_instructor = frappe.db.get_value("Instructor", {}, "name")
        for i, (cid, cname, ccode) in enumerate(ctx["courses"][:10]):
            try:
                frappe.get_doc({
                    "doctype": "Question Bank",
                    "question_text": f"<p>Sample question {i+1} for {cname}: explain the core concept.</p>",
                    "question_type": "Long Answer",
                    "course": cid,
                    "difficulty_level": random.choice(difficulties),
                    "blooms_taxonomy": random.choice(bloom_levels),
                    "marks": random.choice([5, 10, 15, 20]),
                    "created_by_faculty": first_instructor,
                }).insert(ignore_permissions=True, ignore_links=True)
                qb_count += 1
            except Exception as e:
                if qb_count == 0:
                    print(f"  Question Bank note: {str(e)[:140]}")

    # --- Research Project ---
    # autoname format:RP-.YYYY.-.##### is being treated literally, so set name explicitly
    from frappe.utils import nowdate
    yr = nowdate()[:4]
    rp_count = 0
    project_titles = [
        ("AI-Driven Course Recommender", "Sponsored", "Faculty"),
        ("Green Campus Energy Audit", "Internal", "Mixed"),
        ("Cybersecurity Threat Modeling", "Sponsored", "Faculty"),
        ("Smart Hostel IoT Sensor Mesh", "Internal", "Student"),
        ("ML for Crop Yield Prediction", "Collaborative", "Mixed"),
        ("Blockchain Credential Verifier", "Internal", "Faculty"),
    ]
    for i, (title, ptype, rtype) in enumerate(project_titles):
        if not frappe.db.exists("Research Project", {"project_title": title}):
            try:
                doc = frappe.get_doc({
                    "doctype": "Research Project",
                    "name": f"RP-{yr}-{(i+1):05d}",
                    "project_title": title,
                    "project_type": ptype,
                    "researcher_type": rtype,
                })
                doc.flags.name_set = True
                doc.insert(ignore_permissions=True, ignore_links=True)
                rp_count += 1
            except Exception as e:
                if rp_count == 0:
                    print(f"  Research Project note: {str(e)[:140]}")

    # --- Research Publication (with author for live doctype) ---
    pub_count = 0
    pub_titles = [
        ("Deep Learning for NLP: A Survey", "Journal Article", "Faculty"),
        ("IoT Security Framework for Smart Campus", "Conference Paper", "Faculty"),
        ("Quantum Computing: Current State", "Journal Article", "Mixed"),
        ("Machine Learning in Education", "Conference Paper", "Faculty"),
        ("Blockchain for Academic Credentials", "Journal Article", "Faculty"),
        ("Edge Computing in Healthcare", "Journal Article", "Mixed"),
    ]
    # Find one faculty employee for the author table
    author_emp = frappe.db.get_value("Employee", {}, "name")
    author_name = frappe.db.get_value("Employee", author_emp, "employee_name") if author_emp else None
    for i, (title, ptype, rtype) in enumerate(pub_titles):
        if not frappe.db.exists("Research Publication", {"title": title}):
            try:
                doc_data = {
                    "doctype": "Research Publication",
                    "name": f"PUB-{yr}-{(i+1):05d}",
                    "title": title,
                    "publication_type": ptype,
                    "researcher_type": rtype,
                }
                if author_emp:
                    doc_data["authors"] = [
                        {"author_type": "Faculty", "employee": author_emp,
                         "author_name": author_name or "Unknown",
                         "is_corresponding": 1, "author_order": 1},
                    ]
                doc = frappe.get_doc(doc_data)
                doc.flags.name_set = True
                doc.flags.ignore_mandatory = True
                doc.insert(ignore_permissions=True, ignore_links=True)
                pub_count += 1
            except Exception as e:
                if pub_count == 0:
                    print(f"  Research Publication note: {str(e)[:140]}")

    # --- Feedback Response (so Faculty Feedback Report shows data) ---
    fr_count = 0
    # Activate forms first
    frappe.db.sql("UPDATE `tabFeedback Form` SET status='Active' WHERE form_type IN ('Course Feedback', 'Faculty Feedback')")
    frappe.db.commit()
    forms = frappe.get_all(
        "Feedback Form",
        filters={"form_type": ["in", ["Course Feedback", "Faculty Feedback"]]},
        pluck="name",
    )
    if forms:
        instructors = frappe.get_all("Instructor", pluck="name", limit=10)
        students_for_fr = ctx.get("students", [])[:30] if ctx.get("students") else \
                          [(s, None, None, None, None, None, None) for s in
                           frappe.get_all("Student", pluck="name", limit=30)]
        for form in forms[:2]:
            for entry in students_for_fr[:20]:
                sid = entry[0] if isinstance(entry, tuple) else entry
                inst = random.choice(instructors) if instructors else None
                try:
                    frappe.get_doc({
                        "doctype": "Feedback Response",
                        "feedback_form": form,
                        "respondent_type": "Student",
                        "student": sid,
                        "instructor": inst,
                        "is_anonymous": 0,
                        "overall_score": round(random.uniform(3.5, 4.8), 2),
                        "nps_score": random.randint(7, 10),
                        "nps_category": "Promoter",
                        "status": "Valid",
                        "section_scores": [
                            {"section_name": "Teaching Quality",
                             "score": round(random.uniform(3.5, 5.0), 2),
                             "responses_count": 1},
                            {"section_name": "Course Content",
                             "score": round(random.uniform(3.5, 5.0), 2),
                             "responses_count": 1},
                        ],
                    }).insert(ignore_permissions=True, ignore_links=True)
                    fr_count += 1
                except Exception as e:
                    if fr_count == 0:
                        print(f"  Feedback Response note: {str(e)[:140]}")

    # --- CO Attainment (so CO Attainment Report shows data; docstatus=1) ---
    coat_count = 0
    cofa_count = 0
    if ctx.get("courses") and ctx.get("academic_term"):
        # Submit existing draft CO Attainments first
        existing_drafts = frappe.get_all(
            "CO Attainment", filters={"docstatus": 0}, pluck="name",
        )
        for n in existing_drafts:
            try:
                frappe.db.set_value("CO Attainment", n, "docstatus", 1, update_modified=False)
                coat_count += 1
            except Exception:
                pass
        # Create new ones for any missing courses
        for cid, cname, ccode in ctx["courses"][:10]:
            if not frappe.db.exists("CO Attainment", {"course": cid, "academic_term": ctx["academic_term"]}):
                try:
                    doc = frappe.get_doc({
                        "doctype": "CO Attainment",
                        "course": cid,
                        "academic_term": ctx["academic_term"],
                    })
                    doc.flags.ignore_mandatory = True
                    doc.insert(ignore_permissions=True, ignore_links=True)
                    try:
                        doc.submit()
                    except Exception:
                        # Force submit via SQL if validate fails on submit
                        frappe.db.set_value("CO Attainment", doc.name, "docstatus", 1, update_modified=False)
                    coat_count += 1
                except Exception as e:
                    if coat_count == 0:
                        print(f"  CO Attainment note: {str(e)[:140]}")
        # Populate CO Final Attainment child rows (the report queries this)
        # Walk each submitted CO Attainment and add 3 final-attainment rows from its course's COs
        for att in frappe.get_all("CO Attainment", filters={"docstatus": 1}, fields=["name", "course"]):
            existing_finals = frappe.db.count("CO Final Attainment", {"parent": att.name})
            if existing_finals:
                continue
            cos = frappe.get_all(
                "Course Outcome",
                filters={"course": att.course},
                fields=["name", "co_number", "co_statement", "bloom_level"],
                limit=3,
            )
            for co in cos:
                direct = round(random.uniform(2.0, 2.9), 2)
                indirect = round(random.uniform(2.0, 2.9), 2)
                final = round(direct * 0.7 + indirect * 0.3, 2)
                try:
                    frappe.db.sql(
                        """INSERT INTO `tabCO Final Attainment`
                           (name, parent, parenttype, parentfield, idx,
                            course_outcome, co_code, co_statement,
                            direct_attainment, direct_weight,
                            indirect_attainment, indirect_weight,
                            final_attainment, target_attainment, achieved, gap,
                            owner, modified_by, creation, modified)
                           VALUES (%s, %s, 'CO Attainment', 'final_attainments', %s,
                                   %s, %s, %s, %s, 70, %s, 30, %s, 60, %s, %s,
                                   'Administrator', 'Administrator', NOW(), NOW())""",
                        (
                            frappe.generate_hash(length=10),
                            att.name,
                            co.co_number or 1,
                            co.name,
                            f"CO{co.co_number or 1}",
                            (co.co_statement or "")[:140],
                            direct, indirect, final,
                            1 if final * 33.33 >= 60 else 0,
                            round(60 - final * 33.33, 2) if final * 33.33 < 60 else 0,
                        ),
                    )
                    cofa_count += 1
                except Exception as e:
                    if cofa_count == 0:
                        print(f"  CO Final Attainment note: {str(e)[:140]}")
        frappe.db.commit()

    # --- LMS Content Progress (for Course Progress report) ---
    lcp_count = 0
    contents = frappe.get_all("LMS Content", fields=["name", "lms_course"], limit=20)
    students_for_lcp = ctx.get("students", [])[:20] if ctx.get("students") else \
                       [(s, None, None, None, None, None, None) for s in
                        frappe.get_all("Student", pluck="name", limit=20)]
    for c in contents:
        for entry in students_for_lcp[:10]:
            sid = entry[0] if isinstance(entry, tuple) else entry
            if not frappe.db.exists("LMS Content Progress", {"student": sid, "content": c["name"]}):
                try:
                    frappe.get_doc({
                        "doctype": "LMS Content Progress",
                        "student": sid,
                        "content": c["name"],
                        "lms_course": c["lms_course"],
                        "status": random.choice(["Completed", "In Progress", "Not Started"]),
                        "progress_percentage": random.randint(0, 100),
                    }).insert(ignore_permissions=True, ignore_links=True)
                    lcp_count += 1
                except Exception as e:
                    if lcp_count == 0:
                        print(f"  LMS Content Progress note: {str(e)[:140]}")

    # --- Online Examination chain (for Examination Result Analysis report) ---
    qp_count = oe_count = sea_count = 0
    if ctx.get("courses") and ctx.get("academic_year"):
        from frappe.utils import add_days, nowdate
        first_instructor = frappe.db.get_value("Instructor", {}, "name")
        for i, (cid, cname, ccode) in enumerate(ctx["courses"][:5]):
            # Generated Question Paper
            qp_name = f"QP-{yr}-{(i+1):05d}"
            if not frappe.db.exists("Generated Question Paper", qp_name):
                # Pick existing Question Banks for this course (or any if course has none)
                qbs = frappe.get_all(
                    "Question Bank", filters={"course": cid}, pluck="name", limit=5,
                )
                if not qbs:
                    qbs = frappe.get_all("Question Bank", pluck="name", limit=5)
                if not qbs:
                    continue
                try:
                    doc = frappe.get_doc({
                        "doctype": "Generated Question Paper",
                        "name": qp_name,
                        "paper_title": f"{cname} - Mid-Term Paper",
                        "course": cid,
                        "academic_year": ctx["academic_year"],
                        "total_marks": 100,
                        "duration_minutes": 120,
                        "created_by": first_instructor,
                        "paper_questions": [
                            {"question": qb, "question_number": idx + 1, "marks": 20}
                            for idx, qb in enumerate(qbs)
                        ],
                    })
                    doc.flags.name_set = True
                    doc.flags.ignore_mandatory = True
                    doc.insert(ignore_permissions=True, ignore_links=True)
                    qp_count += 1
                except Exception as e:
                    if qp_count == 0:
                        print(f"  Generated Question Paper note: {str(e)[:140]}")
                    continue

            # Online Examination
            oe_name = f"OE-{yr}-{(i+1):05d}"
            from frappe.utils import nowdate, add_days
            start_dt = f"{add_days(nowdate(), -7)} 09:00:00"
            end_dt = f"{add_days(nowdate(), -7)} 11:00:00"
            if not frappe.db.exists("Online Examination", oe_name):
                try:
                    doc = frappe.get_doc({
                        "doctype": "Online Examination",
                        "name": oe_name,
                        "exam_title": f"{cname} - Mid-Term Online Exam",
                        "exam_type": "Midterm",
                        "question_paper": qp_name,
                        "course": cid,
                        "start_datetime": start_dt,
                        "end_datetime": end_dt,
                        "duration_minutes": 120,
                    })
                    doc.flags.name_set = True
                    doc.flags.ignore_mandatory = True
                    doc.insert(ignore_permissions=True, ignore_links=True)
                    oe_count += 1
                except Exception as e:
                    if oe_count == 0:
                        print(f"  Online Examination note: {str(e)[:140]}")
                    continue

            # Student Exam Attempts (10 students per exam)
            students_for_sea = ctx.get("students", [])[:10] if ctx.get("students") else []
            for j, entry in enumerate(students_for_sea):
                sid = entry[0] if isinstance(entry, tuple) else entry
                sea_name = f"SEA-{yr}-{((i+1)*100 + j+1):05d}"
                if frappe.db.exists("Student Exam Attempt", sea_name):
                    continue
                marks = random.randint(40, 95)
                try:
                    sea_doc = frappe.get_doc({
                        "doctype": "Student Exam Attempt",
                        "name": sea_name,
                        "online_examination": oe_name,
                        "student": sid,
                        "status": "Evaluated",
                        "total_marks_obtained": marks,
                        "total_marks": 100,
                        "percentage": marks,
                    })
                    sea_doc.flags.name_set = True
                    sea_doc.flags.ignore_mandatory = True
                    sea_doc.insert(ignore_permissions=True, ignore_links=True)
                    sea_count += 1
                except Exception as e:
                    if sea_count == 0:
                        print(f"  Student Exam Attempt note: {str(e)[:140]}")

    frappe.db.commit()
    print(f"  Topics: {t_count}, Fee Structure: {fs_count}, LMS Content: {lc_count}, "
          f"Exam Schedule: {es_count}, Question Bank: {qb_count}, "
          f"Research Project: {rp_count}, Research Publication: {pub_count}, "
          f"Feedback Response: {fr_count}, CO Attainment: {coat_count}, "
          f"CO Final Attainment: {cofa_count}, "
          f"LMS Content Progress: {lcp_count}, "
          f"Question Paper: {qp_count}, Online Exam: {oe_count}, "
          f"Student Exam Attempt: {sea_count}")


# === Layer 11a — Inventory & Assets ==========================================

def _seed_inventory_v2(ctx):
    """Seed Supplier Group, Supplier, Inventory Item Group, Inventory Item,
    Asset Category, Asset, Asset Movement, Asset Maintenance, Maintenance Team,
    Lab Equipment, Lab Equipment Booking, Lab Consumable Issue.
    Uses university_erp's own Inventory Item / Inventory Item Group doctypes.
    ERPNext stock docs (Material Request, PO, SE) are skipped — they need full
    ERPNext stock module setup which is out of scope for this demo seed.
    """
    company = COMPANY
    abbr = COMPANY_ABBR
    yr = "2026"
    today_str = nowdate()
    depreciation_account = f"Depreciation - {abbr}"

    sg_count = sup_count = ig_count = item_count = ac_count = 0
    asset_count = am_count = asm_count = mt_count = le_count = 0
    leb_count = lci_count = 0

    # ── 1. Supplier Groups ────────────────────────────────────────────────────
    # Find or create root supplier group first
    root_sg = frappe.db.get_value("Supplier Group", {"is_group": 1}, "name")
    sup_group_names = ["Equipment Vendors", "Stationery Suppliers", "IT Vendors"]
    for sg_name in sup_group_names:
        if frappe.db.exists("Supplier Group", {"supplier_group_name": sg_name}):
            sg_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Supplier Group",
                "supplier_group_name": sg_name,
                "parent_supplier_group": root_sg,
                "is_group": 0,
            }).insert(ignore_permissions=True, ignore_links=True)
            sg_count += 1
        except Exception as e:
            print(f"  SupplierGroup {sg_name}: {str(e)[:80]}")

    # ── 2. Suppliers ──────────────────────────────────────────────────────────
    suppliers_data = [
        ("Dell India", "IT Vendors"),
        ("HP Inc", "IT Vendors"),
        ("Cisco Networks", "IT Vendors"),
        ("Toshiba Computers", "IT Vendors"),
        ("ABB Lab Systems", "Equipment Vendors"),
        ("Nikon Microscopes", "Equipment Vendors"),
        ("Camlin Stationery", "Stationery Suppliers"),
        ("Reliance Books", "Stationery Suppliers"),
    ]
    for sup_name, grp in suppliers_data:
        if frappe.db.exists("Supplier", {"supplier_name": sup_name}):
            sup_count += 1
            continue
        try:
            sg_exists = frappe.db.get_value("Supplier Group", {"supplier_group_name": grp}, "name")
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": sup_name,
                "supplier_group": sg_exists or root_sg,
                "country": "India",
            }).insert(ignore_permissions=True, ignore_links=True)
            sup_count += 1
        except Exception as e:
            if sup_count < 2:
                print(f"  Supplier {sup_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── 3. Inventory Item Groups (university_erp's own doctype) ───────────────
    inv_item_groups = ["Lab Equipment", "Office Stationery", "IT Hardware", "Furniture", "Consumables"]
    for ig_name in inv_item_groups:
        if frappe.db.exists("Inventory Item Group", {"group_name": ig_name}):
            ig_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Inventory Item Group",
                "group_name": ig_name,
                "is_group": 0,
            }).insert(ignore_permissions=True, ignore_links=True)
            ig_count += 1
        except Exception as e:
            print(f"  InvItemGroup {ig_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── 4. Inventory Items (50, university_erp's own doctype) ─────────────────
    # Fields: item_code (unique), item_name, item_group→InventoryItemGroup,
    #         unit_of_measure, item_type, description, maintain_stock,
    #         default_warehouse, minimum_stock_level, reorder_level
    items_by_group = {
        "Lab Equipment": [
            ("INV-OSC-001", "Digital Oscilloscope", "Unit", 45000),
            ("INV-SIG-001", "Signal Generator", "Unit", 38000),
            ("INV-MMT-001", "Multimeter Digital", "Unit", 5000),
            ("INV-FNG-001", "Function Generator", "Unit", 22000),
            ("INV-PSU-001", "Power Supply 30V", "Unit", 12000),
            ("INV-MIC-001", "Microscope 100x", "Unit", 28000),
            ("INV-VRN-001", "Vernier Caliper", "Unit", 800),
            ("INV-SPE-001", "Spectrometer", "Unit", 35000),
            ("INV-CFG-001", "Centrifuge Machine", "Unit", 55000),
            ("INV-PHM-001", "pH Meter", "Unit", 7500),
        ],
        "Office Stationery": [
            ("INV-A4P-001", "A4 Paper Ream", "Box", 350),
            ("INV-PEN-001", "Ball Point Pen Blue", "Box", 120),
            ("INV-MRK-001", "Whiteboard Marker", "Box", 250),
            ("INV-STP-001", "Stapler Heavy Duty", "Unit", 450),
            ("INV-FLD-001", "File Folder A4", "Box", 180),
            ("INV-NTB-001", "Spiral Notebook", "Box", 320),
            ("INV-CRF-001", "Correction Fluid", "Box", 95),
            ("INV-HLT-001", "Highlighter Set", "Box", 200),
            ("INV-SCS-001", "Scissors Office", "Unit", 85),
            ("INV-TPD-001", "Tape Dispenser", "Unit", 125),
        ],
        "IT Hardware": [
            ("INV-DKT-001", "Desktop Computer Core i5", "Unit", 55000),
            ("INV-LPT-001", "Laptop HP ProBook", "Unit", 72000),
            ("INV-NSW-001", "Network Switch 24-port", "Unit", 18000),
            ("INV-UPS-001", "UPS 1kVA", "Unit", 9500),
            ("INV-PRJ-001", "Projector 3000 Lumen", "Unit", 42000),
            ("INV-WBC-001", "Webcam HD 1080p", "Unit", 3500),
            ("INV-KBD-001", "Keyboard Wireless", "Unit", 1200),
            ("INV-MSE-001", "Mouse Wireless Optical", "Unit", 800),
            ("INV-USB-001", "USB Hub 7-Port", "Unit", 1500),
            ("INV-HDD-001", "External HDD 1TB", "Unit", 5500),
        ],
        "Furniture": [
            ("INV-CHR-001", "Office Chair Ergonomic", "Unit", 8500),
            ("INV-TBL-001", "Study Table 4x2ft", "Unit", 5500),
            ("INV-BKS-001", "Bookshelf 6-shelf", "Unit", 7200),
            ("INV-CNF-001", "Conference Table 10-seater", "Unit", 35000),
            ("INV-WBD-001", "White Board 4x3ft", "Unit", 4500),
            ("INV-FCB-001", "Filing Cabinet 4-drawer", "Unit", 9800),
            ("INV-LCK-001", "Lockers 12-unit", "Unit", 12000),
            ("INV-SFA-001", "Sofa 3-seater", "Unit", 18000),
            ("INV-STD-001", "Standing Desk", "Unit", 14000),
            ("INV-PDM-001", "Podium Wooden", "Unit", 6500),
        ],
        "Consumables": [
            ("INV-TNR-001", "Printing Toner HP", "Unit", 2800),
            ("INV-CLN-001", "Cleaning Liquid Lab", "Box", 450),
            ("INV-GLV-001", "Gloves Disposable", "Box", 350),
            ("INV-GGL-001", "Safety Goggles", "Unit", 180),
            ("INV-FPR-001", "Filter Paper Grade 1", "Box", 550),
            ("INV-IPA-001", "Isopropyl Alcohol 1L", "Unit", 280),
            ("INV-CTN-001", "Cotton Swabs Pack", "Box", 120),
            ("INV-ETP-001", "Electrical Tape", "Box", 95),
            ("INV-CBT-001", "Cable Ties 100pcs", "Box", 150),
            ("INV-SLD-001", "Soldering Wire 500g", "Unit", 420),
        ],
    }

    inv_item_codes = {}
    for group, items in items_by_group.items():
        inv_item_codes[group] = []
        ig_name = frappe.db.get_value("Inventory Item Group", {"group_name": group}, "name")
        for item_code, item_name, uom, rate in items:
            inv_item_codes[group].append(item_code)
            if frappe.db.exists("Inventory Item", {"item_code": item_code}):
                continue
            try:
                inv_doc = frappe.get_doc({
                    "doctype": "Inventory Item",
                    "item_code": item_code,
                    "item_name": item_name,
                    "item_group": ig_name,
                    "unit_of_measure": uom,
                    "item_type": "Stock Item",
                    "description": f"{item_name} for university use",
                    "maintain_stock": 1,
                    "minimum_stock_level": 2,
                    "reorder_level": 5,
                    "reorder_quantity": 10,
                })
                inv_doc.flags.ignore_validate = True
                inv_doc.flags.ignore_mandatory = True
                inv_doc.insert(ignore_permissions=True, ignore_links=True)
                item_count += 1
            except Exception as e:
                if item_count < 3:
                    print(f"  InvItem {item_code}: {str(e)[:80]}")

    frappe.db.commit()

    # ── 5. Asset Categories ───────────────────────────────────────────────────
    # Fields: asset_category_name (unique key field), category_name (display),
    #         depreciation_method, total_number_of_depreciations,
    #         fixed_asset_account, accumulated_depreciation_account,
    #         depreciation_expense_account
    asset_cats = [
        ("Computers", f"Electronic Equipments - {abbr}", depreciation_account),
        ("Lab Equipment", f"Capital Equipments - {abbr}", depreciation_account),
        ("University Furniture", f"Furnitures and Fixtures - {abbr}", depreciation_account),
        ("Vehicles", f"Capital Equipments - {abbr}", depreciation_account),
        ("Buildings", f"Buildings - {abbr}", depreciation_account),
        ("Network Equipment", f"Electronic Equipments - {abbr}", depreciation_account),
    ]
    ac_map = {}  # name -> asset_category_name
    for ac_name, fixed_acct, depr_acct in asset_cats:
        # asset_category_name column is NULL in DB; check by primary key (name)
        if frappe.db.exists("Asset Category", ac_name):
            ac_map[ac_name] = ac_name
            ac_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Asset Category",
                "asset_category_name": ac_name,
                "category_name": ac_name,
                "enable_cwip_accounting": 0,
                "depreciation_method": "Straight Line",
                "total_number_of_depreciations": 5,
                "frequency_of_depreciation": 12,
                "fixed_asset_account": fixed_acct,
                "accumulated_depreciation_account": depr_acct,
                "depreciation_expense_account": depr_acct,
            }).insert(ignore_permissions=True, ignore_links=True)
            ac_map[ac_name] = ac_name
            ac_count += 1
        except Exception as e:
            print(f"  AssetCategory {ac_name}: {str(e)[:100]}")

    frappe.db.commit()

    # ── 6. Assets (30) via raw SQL to bypass controller validation ────────────
    assets_data = [
        ("Dell Workstation CS Lab 1", "Computers", 95000, add_days(today_str, -180)),
        ("Dell Workstation CS Lab 2", "Computers", 95000, add_days(today_str, -175)),
        ("HP Server Rack 1", "Computers", 350000, add_days(today_str, -365)),
        ("HP Laptop Faculty 1", "Computers", 72000, add_days(today_str, -90)),
        ("HP Laptop Faculty 2", "Computers", 72000, add_days(today_str, -85)),
        ("Digital Oscilloscope EC Lab", "Lab Equipment", 85000, add_days(today_str, -200)),
        ("Signal Generator EC Lab", "Lab Equipment", 62000, add_days(today_str, -195)),
        ("Microscope Bio Lab 1", "Lab Equipment", 95000, add_days(today_str, -300)),
        ("Microscope Bio Lab 2", "Lab Equipment", 95000, add_days(today_str, -295)),
        ("Centrifuge Machine Chem Lab", "Lab Equipment", 120000, add_days(today_str, -150)),
        ("Faculty Office Chair Set", "University Furniture", 42000, add_days(today_str, -400)),
        ("Conference Table Admin", "University Furniture", 85000, add_days(today_str, -500)),
        ("Library Bookshelves Set", "University Furniture", 65000, add_days(today_str, -600)),
        ("Student Locker Bank CS", "University Furniture", 48000, add_days(today_str, -300)),
        ("Reception Sofa Set", "University Furniture", 35000, add_days(today_str, -250)),
        ("University Bus 1", "Vehicles", 1800000, add_days(today_str, -730)),
        ("University Bus 2", "Vehicles", 1800000, add_days(today_str, -725)),
        ("Faculty Car 1", "Vehicles", 850000, add_days(today_str, -400)),
        ("Generator Set 100kVA", "Buildings", 250000, add_days(today_str, -500)),
        ("Solar Panel Array", "Buildings", 1200000, add_days(today_str, -300)),
        ("Main Switch Board", "Buildings", 180000, add_days(today_str, -600)),
        ("CCTV System Campus", "Network Equipment", 95000, add_days(today_str, -200)),
        ("Network Switch Core", "Network Equipment", 68000, add_days(today_str, -350)),
        ("WiFi Access Points Set", "Network Equipment", 45000, add_days(today_str, -180)),
        ("Projector Seminar Hall 1", "Computers", 55000, add_days(today_str, -120)),
        ("Projector Seminar Hall 2", "Computers", 55000, add_days(today_str, -115)),
        ("UPS Central 10kVA", "Network Equipment", 185000, add_days(today_str, -450)),
        ("Air Conditioner Lab Block", "Buildings", 350000, add_days(today_str, -360)),
        ("Spectrometer Physics Lab", "Lab Equipment", 145000, add_days(today_str, -250)),
        ("3D Printer CS Lab", "Computers", 220000, add_days(today_str, -60)),
    ]

    asset_names = []
    for asset_name, category, amount, purchase_date in assets_data:
        existing = frappe.db.get_value("Asset", {"asset_name": asset_name}, "name")
        if existing:
            asset_names.append(existing)
            continue
        try:
            # Use frappe.get_doc but set available_for_use_date to bypass controller
            asset_doc = frappe.get_doc({
                "doctype": "Asset",
                "asset_name": asset_name,
                "asset_category": category,
                "company": company,
                "purchase_date": purchase_date,
                "available_for_use_date": purchase_date,
                "gross_purchase_amount": amount,
                "cost_center": f"Main - {abbr}",
                "calculate_depreciation": 0,
                "status": "In Use",
            })
            asset_doc.flags.ignore_mandatory = True
            asset_doc.flags.ignore_validate = True
            asset_doc.insert(ignore_permissions=True, ignore_links=True)
            asset_names.append(asset_doc.name)
            asset_count += 1
        except Exception as e:
            if asset_count < 3:
                print(f"  Asset {asset_name}: {str(e)[:120]}")
            asset_names.append(None)

    frappe.db.commit()

    # ── 7. Asset Movements (15) ───────────────────────────────────────────────
    valid_assets = [n for n in asset_names if n]
    for i, asset_name in enumerate(valid_assets[:15]):
        try:
            if frappe.db.count("Asset Movement", filters={"purpose": "Receipt"}) > i:
                am_count += 1
                continue
            am_doc = frappe.get_doc({
                "doctype": "Asset Movement",
                "purpose": "Receipt",
                "transaction_date": add_days(today_str, -(i * 10 + 5)),
                "company": company,
                "assets": [{"asset": asset_name}],
            })
            am_doc.flags.ignore_mandatory = True
            am_doc.flags.ignore_validate = True
            am_doc.insert(ignore_permissions=True, ignore_links=True)
            am_count += 1
        except Exception as e:
            if am_count < 2:
                print(f"  AssetMovement {asset_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── 8. Maintenance Teams ──────────────────────────────────────────────────
    mt_names = []
    for mt_name in ["Lab Maintenance Team", "IT Support Team"]:
        if frappe.db.exists("Maintenance Team", {"team_name": mt_name}):
            mt_names.append(frappe.db.get_value("Maintenance Team",
                            {"team_name": mt_name}, "name"))
            mt_count += 1
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Maintenance Team",
                "team_name": mt_name,
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            mt_names.append(doc.name)
            mt_count += 1
        except Exception as e:
            print(f"  MaintenanceTeam {mt_name}: {str(e)[:80]}")

    # ── 9. Asset Maintenance (8) ──────────────────────────────────────────────
    for i, asset_name in enumerate(valid_assets[:8]):
        try:
            if frappe.db.exists("Asset Maintenance", {"asset_name": asset_name}):
                asm_count += 1
                continue
            team = mt_names[i % len(mt_names)] if mt_names else None
            asm_doc = frappe.get_doc({
                "doctype": "Asset Maintenance",
                "asset_name": asset_name,
                "company": company,
                "maintenance_team": team,
                "maintenance_tasks": [{
                    "maintenance_type": "Preventive Maintenance",
                    "periodicity": "Quarterly",
                    "assign_to": "Administrator",
                    "next_due_date": add_days(today_str, 30 + i * 5),
                }],
            })
            asm_doc.flags.ignore_mandatory = True
            asm_doc.flags.ignore_validate = True
            asm_doc.insert(ignore_permissions=True, ignore_links=True)
            asm_count += 1
        except Exception as e:
            if asm_count < 2:
                print(f"  AssetMaintenance {asset_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── 10. Lab Equipment (university_erp's own doctype) ─────────────────────
    # Fields: equipment_name, equipment_code(unique), equipment_type,
    #         lab (→University Laboratory), asset, status, manufacturer,
    #         model, serial_number, purchase_date, warranty_end, purchase_value
    labs = ["CS-LAB", "EC-LAB", "ME-LAB", "PH-LAB", "CHE-LAB"]
    # equipment_type valid values: Scientific, Computing, Electrical, Mechanical, Chemical, Biological, General
    lab_eq_data = [
        ("EQ-OSC-001", "Digital Oscilloscope Unit 1", "EC-LAB", "Electrical", 85000),
        ("EQ-OSC-002", "Digital Oscilloscope Unit 2", "EC-LAB", "Electrical", 85000),
        ("EQ-SIG-001", "Signal Generator Unit 1", "EC-LAB", "Electrical", 62000),
        ("EQ-SIG-002", "Signal Generator Unit 2", "EC-LAB", "Electrical", 62000),
        ("EQ-MMT-001", "Multimeter Set A", "EC-LAB", "Electrical", 5000),
        ("EQ-MIC-001", "Microscope Research Grade", "PH-LAB", "Scientific", 95000),
        ("EQ-MIC-002", "Microscope Student Grade", "PH-LAB", "Scientific", 45000),
        ("EQ-SPE-001", "Spectrometer UV-Vis", "PH-LAB", "Scientific", 145000),
        ("EQ-PHM-001", "pH Meter Lab Grade", "CHE-LAB", "Chemical", 7500),
        ("EQ-CFG-001", "Centrifuge 5000 RPM", "CHE-LAB", "Chemical", 120000),
        ("EQ-CFG-002", "Centrifuge 10000 RPM", "CHE-LAB", "Chemical", 180000),
        ("EQ-3DP-001", "3D Printer FDM", "CS-LAB", "Computing", 220000),
        ("EQ-ROB-001", "Robotics Kit Advanced", "CS-LAB", "Computing", 45000),
        ("EQ-CNC-001", "CNC Machine Mini", "ME-LAB", "Mechanical", 350000),
        ("EQ-LTH-001", "Lathe Machine 3ft", "ME-LAB", "Mechanical", 280000),
        ("EQ-DRL-001", "Drilling Machine", "ME-LAB", "Mechanical", 85000),
        ("EQ-TTM-001", "Tensile Testing Machine", "ME-LAB", "Mechanical", 450000),
        ("EQ-VHT-001", "Vickers Hardness Tester", "ME-LAB", "Mechanical", 180000),
        ("EQ-FNG-001", "Function Generator Dual", "EC-LAB", "Electrical", 32000),
        ("EQ-DSO-001", "DSO Digital Storage Osc", "EC-LAB", "Electrical", 92000),
    ]

    le_names = []
    for eq_code, eq_name, lab_id, eq_type, value in lab_eq_data:
        if frappe.db.exists("Lab Equipment", {"equipment_code": eq_code}):
            existing = frappe.db.get_value("Lab Equipment", {"equipment_code": eq_code}, "name")
            le_names.append(existing)
            le_count += 1
            continue
        try:
            if not frappe.db.exists("University Laboratory", lab_id):
                le_names.append(None)
                continue
            eq_doc = frappe.get_doc({
                "doctype": "Lab Equipment",
                "equipment_name": eq_name,
                "equipment_code": eq_code,
                "equipment_type": eq_type,
                "lab": lab_id,
                "purchase_value": value,
                "purchase_date": add_days(today_str, -random.randint(100, 500)),
                "status": "Available",
            })
            eq_doc.flags.ignore_mandatory = True
            eq_doc.insert(ignore_permissions=True, ignore_links=True)
            le_names.append(eq_doc.name)
            le_count += 1
        except Exception as e:
            if le_count < 3:
                print(f"  LabEquipment {eq_code}: {str(e)[:100]}")
            le_names.append(None)

    frappe.db.commit()

    # ── 11. Lab Equipment Bookings (15) ───────────────────────────────────────
    instructors = frappe.get_all("Instructor", pluck="name", limit=5)
    valid_le = [n for n in le_names if n]
    for i in range(15):
        if i >= len(valid_le):
            break
        le_name = valid_le[i % len(valid_le)]
        instr = instructors[i % len(instructors)] if instructors else None
        # Only use future dates to avoid "cannot be in the past" validation
        # purpose valid: Research, Teaching, Project Work, Experiment, Calibration, Other
        booking_date = add_days(today_str, i + 1)
        purpose = ["Research", "Teaching", "Project Work", "Experiment", "Calibration", "Other"][i % 6]
        try:
            if frappe.db.exists("Lab Equipment Booking", {
                "lab_equipment": le_name, "booking_date": booking_date
            }):
                leb_count += 1
                continue
            bk_doc = frappe.get_doc({
                "doctype": "Lab Equipment Booking",
                "lab_equipment": le_name,
                "booking_date": booking_date,
                "from_time": "09:00:00",
                "to_time": "11:00:00",
                "booked_by": instr,
                "purpose": purpose,
                "status": "Approved" if i < 10 else "Pending",
            })
            bk_doc.flags.ignore_mandatory = True
            bk_doc.flags.ignore_validate = True
            bk_doc.insert(ignore_permissions=True, ignore_links=True)
            leb_count += 1
        except Exception as e:
            if leb_count < 2:
                print(f"  LabEquipmentBooking: {str(e)[:80]}")

    frappe.db.commit()

    # ── 12. Lab Consumable Issues (8) ─────────────────────────────────────────
    # purpose valid: Experiment, Research, Teaching, Project, Other
    # items child table: Lab Consumable Issue Item — item_code (Link→Inventory Item), qty
    students_list = ctx.get("students", [])
    all_inv_items = frappe.get_all("Inventory Item", pluck="name", limit=20)
    purpose_opts = ["Experiment", "Research", "Teaching", "Project", "Other"]

    instructors_for_lci = frappe.get_all("Instructor", pluck="name", limit=8)
    for i in range(8):
        if i >= len(students_list):
            break
        s_entry = students_list[i]
        sid = s_entry[0] if isinstance(s_entry, tuple) else s_entry
        lab = labs[i % len(labs)]
        instr = instructors_for_lci[i % len(instructors_for_lci)] if instructors_for_lci else None
        # Need at least one item in the items child table
        item_codes = all_inv_items[i * 2: i * 2 + 2] if all_inv_items else []
        if not item_codes:
            continue
        try:
            items_rows = [{"item_code": ic, "qty": random.randint(1, 5)} for ic in item_codes]
            lci_doc = frappe.get_doc({
                "doctype": "Lab Consumable Issue",
                "lab": lab,
                "issue_date": add_days(today_str, -random.randint(1, 30)),
                "issued_by": instr,
                "issued_to": sid,
                "purpose": purpose_opts[i % len(purpose_opts)],
                "items": items_rows,
                "remarks": "Issued for course lab session.",
            })
            lci_doc.flags.ignore_mandatory = True
            lci_doc.flags.ignore_validate = True
            lci_doc.insert(ignore_permissions=True, ignore_links=True)
            lci_count += 1
        except Exception as e:
            if lci_count < 2:
                print(f"  LabConsumableIssue: {str(e)[:80]}")

    frappe.db.commit()

    print(
        f"  SupplierGroup: {sg_count}, Supplier: {sup_count}, "
        f"InvItemGroup: {ig_count}, InvItem: {item_count}, "
        f"AssetCategory: {ac_count}, Asset: {asset_count}, "
        f"AssetMovement: {am_count}, AssetMaint: {asm_count}, "
        f"MaintenanceTeam: {mt_count}, LabEquipment: {le_count}, "
        f"LabEquipmentBooking: {leb_count}, LabConsumable: {lci_count}"
    )


# === Layer 11b — Admissions cycle ============================================

def _seed_admissions_v2(ctx):
    """Admission Cycle, Admission Criteria, Seat Matrix, Merit List."""
    yr = "2026"
    programs = ctx.get("programs", [])
    ay = ctx.get("academic_year", "2026-2027")

    ac_count = crit_count = seat_count = ml_count = 0

    # ── Admission Cycles ──────────────────────────────────────────────────────
    cycles = [
        ("AY 2026-2027 UG Admissions", "Undergraduate", "Open"),
        ("AY 2026-2027 PG Admissions", "Postgraduate", "Open"),
    ]
    cycle_names = []
    for cycle_name, prog_type, status in cycles:
        if frappe.db.exists("Admission Cycle", {"cycle_name": cycle_name}):
            existing = frappe.db.get_value("Admission Cycle", {"cycle_name": cycle_name}, "name")
            cycle_names.append(existing)
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Admission Cycle",
                "cycle_name": cycle_name,
                "academic_year": ay,
                "program_type": prog_type,
                "status": status,
                "start_date": add_days(nowdate(), -30),
                "end_date": add_days(nowdate(), 90),
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            cycle_names.append(doc.name)
            ac_count += 1
        except Exception as e:
            print(f"  AdmissionCycle {cycle_name}: {str(e)[:100]}")

    # ── Admission Criteria (one per program, linked to cycle) ─────────────────
    ug_cycle = cycle_names[0] if cycle_names else None
    pg_cycle = cycle_names[1] if len(cycle_names) > 1 else ug_cycle
    for i, prog in enumerate(programs[:8]):
        pname = prog[0] if isinstance(prog, tuple) else prog
        cyc = ug_cycle if i < 5 else pg_cycle
        if frappe.db.exists("Admission Criteria", {"program": pname, "admission_cycle": cyc}):
            crit_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Admission Criteria",
                "admission_cycle": cyc,
                "program": pname,
                "min_percentage": 60.0 + (i % 3) * 5,
                "entrance_exam_required": 1,
                "min_entrance_score": random.randint(60, 120),
                "previous_marks_weightage": 40,
                "entrance_weightage": 60,
            }).insert(ignore_permissions=True, ignore_links=True)
            crit_count += 1
        except Exception as e:
            if crit_count < 2:
                print(f"  AdmissionCriteria {pname}: {str(e)[:100]}")

    # ── Seat Matrix ───────────────────────────────────────────────────────────
    for i, prog in enumerate(programs[:8]):
        pname = prog[0] if isinstance(prog, tuple) else prog
        cyc = ug_cycle if i < 5 else pg_cycle
        if frappe.db.exists("Seat Matrix", {"program": pname, "admission_cycle": cyc}):
            seat_count += 1
            continue
        try:
            total = 30 + (i % 3) * 10
            frappe.get_doc({
                "doctype": "Seat Matrix",
                "admission_cycle": cyc,
                "program": pname,
                "total_seats": total,
                "general_seats": int(total * 0.5),
                "obc_seats": int(total * 0.27),
                "sc_seats": int(total * 0.15),
                "st_seats": int(total * 0.075),
                "ews_seats": int(total * 0.1),
                "filled_seats": random.randint(int(total * 0.7), total),
            }).insert(ignore_permissions=True, ignore_links=True)
            seat_count += 1
        except Exception as e:
            if seat_count < 2:
                print(f"  SeatMatrix {pname}: {str(e)[:100]}")

    frappe.db.commit()

    # ── Merit Lists ───────────────────────────────────────────────────────────
    for i, cycle_name in enumerate(cycle_names[:2]):
        for ml_type in ["Merit", "Waitlist"]:
            ml_id = f"ML-{yr}-{(i*2 + (1 if ml_type == 'Waitlist' else 0)):05d}"
            if frappe.db.exists("Merit List", ml_id):
                ml_count += 1
                continue
            try:
                applicants = []
                for j in range(10):
                    applicants.append({
                        "rank": j + 1,
                        "applicant_name": f"Applicant {i*10+j+1}",
                        "score": round(random.uniform(70.0, 99.0), 2),
                        "category": ["General", "OBC", "SC", "ST"][j % 4],
                        "status": "Admitted" if j < 7 else "Waitlisted",
                    })
                ml_doc = frappe.get_doc({
                    "doctype": "Merit List",
                    "name": ml_id,
                    "admission_cycle": cycle_name,
                    "list_type": ml_type,
                    "academic_year": ay,
                    "applicants": applicants,
                })
                ml_doc.flags.name_set = True
                ml_doc.flags.ignore_mandatory = True
                ml_doc.insert(ignore_permissions=True, ignore_links=True)
                ml_count += 1
            except Exception as e:
                if ml_count < 2:
                    print(f"  MeritList {ml_id}: {str(e)[:100]}")

    frappe.db.commit()
    print(
        f"  AdmissionCycle: {ac_count}, Criteria: {crit_count}, "
        f"SeatMatrix: {seat_count}, MeritList: {ml_count}"
    )


# === Layer 11c — Examinations deep chain =====================================

def _seed_examinations_deep_v2(ctx):
    """External Examiner, Question Paper Template, Practical Examination,
    Internal Assessment, Answer Sheet, Revaluation Request,
    Student Transcript, Notification Template, Certificate Template,
    Certificate Request.
    """
    yr = "2026"
    ay = ctx.get("academic_year", "2026-2027")
    at = ctx.get("academic_term", "")
    courses = ctx.get("courses", [])
    students = ctx.get("students", [])
    programs = ctx.get("programs", [])
    instructors = frappe.get_all("Instructor", pluck="name", limit=5)

    ee_count = qpt_count = pe_count = ia_count = 0
    as_count = rev_count = tr_count = nt_count = ct_count = cr_count = 0

    # ── External Examiners (5) ────────────────────────────────────────────────
    examiners = [
        ("Prof. Rajan Sharma", "IIT Delhi", "Computer Science"),
        ("Dr. Priya Nair", "IIT Bombay", "Electronics"),
        ("Prof. Amit Kumar", "NIT Warangal", "Mechanical"),
        ("Dr. Sunita Patel", "IIT Madras", "Civil Engineering"),
        ("Prof. Vikram Singh", "IIT Kanpur", "Electrical"),
    ]
    examiner_ids = []
    for i, (name, inst, dept) in enumerate(examiners):
        if frappe.db.exists("External Examiner", {"examiner_name": name}):
            existing = frappe.db.get_value("External Examiner", {"examiner_name": name}, "name")
            examiner_ids.append(existing)
            ee_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "External Examiner",
                "examiner_name": name,
                "organization": inst,
                "department": dept,
                "email": f"examiner{i+1}@external.edu",
                "phone": f"98{random.randint(10000000, 99999999)}",
                "status": "Active",
            }).insert(ignore_permissions=True, ignore_links=True)
            existing = frappe.db.get_value("External Examiner", {"examiner_name": name}, "name")
            examiner_ids.append(existing)
            ee_count += 1
        except Exception as e:
            if ee_count < 2:
                print(f"  ExternalExaminer {name}: {str(e)[:80]}")

    # ── Question Paper Templates (8) ──────────────────────────────────────────
    for i, course_entry in enumerate(courses[:8]):
        cid = course_entry[0] if isinstance(course_entry, tuple) else course_entry
        cname = course_entry[1] if isinstance(course_entry, tuple) and len(course_entry) > 1 else cid
        template_name = f"{cname[:40]} End Semester Template"
        # Check by template_name (the auto-generated name may differ across runs)
        existing_qpt = frappe.db.sql(
            "SELECT name FROM `tabQuestion Paper Template` WHERE template_name=%s LIMIT 1",
            template_name, as_dict=True
        )
        if existing_qpt:
            qpt_count += 1
            continue
        qpt_id = f"QPT-{yr}-{i+1:05d}"
        try:
            # section child doctype: "Question Paper Section"
            # question_type valid: "Multiple Choice (MCQ)", "Short Answer", "Long Answer", etc.
            sections = []
            for sec_num in range(1, 4):
                sections.append({
                    "section_name": f"Section {sec_num}",
                    "marks_per_question": 10 * sec_num,
                    "total_questions": 5,
                    "questions_to_attempt": 5,
                    "question_type": ["Multiple Choice (MCQ)", "Short Answer", "Long Answer"][sec_num - 1],
                })
            qpt_doc = frappe.get_doc({
                "doctype": "Question Paper Template",
                "name": qpt_id,
                "template_name": template_name,
                "course": cid,
                "total_marks": 100,
                "duration": 180,
                "sections": sections,
            })
            qpt_doc.flags.ignore_validate = True
            qpt_doc.flags.ignore_mandatory = True
            qpt_doc.insert(ignore_permissions=True, ignore_links=True)
            qpt_count += 1
        except Exception as e:
            if qpt_count < 2:
                print(f"  QuestionPaperTemplate {qpt_id}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Practical Examinations (8) ────────────────────────────────────────────
    lab_courses = [c for c in courses if "Lab" in (c[1] if isinstance(c, tuple) else c)]
    if not lab_courses:
        lab_courses = courses[:8]
    for i, course_entry in enumerate(lab_courses[:8]):
        cid = course_entry[0] if isinstance(course_entry, tuple) else course_entry
        pe_id = f"PRAC-{yr}-{i+1:05d}"
        if frappe.db.exists("Practical Examination", pe_id):
            pe_count += 1
            continue
        try:
            instr = instructors[i % len(instructors)] if instructors else None
            examiner = examiner_ids[i % len(examiner_ids)] if examiner_ids else None
            exam_start = add_days(nowdate(), -random.randint(10, 60))
            pe_doc = frappe.get_doc({
                "doctype": "Practical Examination",
                "name": pe_id,
                "examination_name": f"Practical Exam {i+1}",
                "course": cid,
                "academic_year": ay,
                "academic_term": at,
                "start_date": exam_start,
                "end_date": add_days(exam_start, 1),
                "maximum_marks": 50,
                "examiner": examiner,
                "internal_examiner": instr,
                "status": "Completed",
            })
            pe_doc.flags.ignore_mandatory = True
            pe_doc.insert(ignore_permissions=True, ignore_links=True)
            pe_count += 1
        except Exception as e:
            if pe_count < 2:
                print(f"  PracticalExam {pe_id}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Internal Assessments (30) ─────────────────────────────────────────────
    ia_names = []
    for i, course_entry in enumerate(courses[:30]):
        cid = course_entry[0] if isinstance(course_entry, tuple) else course_entry
        ia_id = f"IA-{yr}-{i+1:05d}"
        if frappe.db.exists("Internal Assessment", ia_id):
            ia_names.append(ia_id)
            ia_count += 1
            continue
        try:
            ia_doc = frappe.get_doc({
                "doctype": "Internal Assessment",
                "name": ia_id,
                "course": cid,
                "academic_year": ay,
                "academic_term": at,
                "assessment_date": add_days(nowdate(), -random.randint(15, 90)),
                "max_marks": 30,
                "assessment_type": ["Quiz", "Assignment", "Test", "Viva"][i % 4],
                "status": "Completed",
            })
            ia_doc.flags.name_set = True
            ia_doc.flags.ignore_mandatory = True
            ia_doc.insert(ignore_permissions=True, ignore_links=True)
            ia_names.append(ia_id)
            ia_count += 1
        except Exception as e:
            if ia_count < 2:
                print(f"  InternalAssessment {ia_id}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Answer Sheets (100) ───────────────────────────────────────────────────
    hall_tickets = frappe.get_all("Hall Ticket", pluck="name", limit=100)
    as_names = []
    for i, ht_name in enumerate(hall_tickets[:100]):
        as_id = f"AS-{yr}-{i+1:05d}"
        if frappe.db.exists("Answer Sheet", as_id):
            as_names.append(as_id)
            as_count += 1
            continue
        marks = random.randint(35, 95)
        try:
            student = frappe.db.get_value("Hall Ticket", ht_name, "student")
            as_doc = frappe.get_doc({
                "doctype": "Answer Sheet",
                "name": as_id,
                "hall_ticket": ht_name,
                "student": student,
                "max_marks": 100,
                "marks_obtained": marks,
                "grade": "A" if marks >= 80 else ("B" if marks >= 65 else ("C" if marks >= 50 else "D")),
                "evaluated_by": instructors[i % len(instructors)] if instructors else None,
                "evaluation_date": add_days(nowdate(), -random.randint(5, 30)),
                "status": "Evaluated",
            })
            as_doc.flags.name_set = True
            as_doc.flags.ignore_mandatory = True
            as_doc.insert(ignore_permissions=True, ignore_links=True)
            as_names.append(as_id)
            as_count += 1
        except Exception as e:
            if as_count < 2:
                print(f"  AnswerSheet {as_id}: {str(e)[:80]}")
            as_names.append(None)

    frappe.db.commit()

    # ── Revaluation Requests (5) ──────────────────────────────────────────────
    low_mark_sheets = [n for n in as_names if n and
                       frappe.db.get_value("Answer Sheet", n, "marks_obtained", cache=False) and
                       (frappe.db.get_value("Answer Sheet", n, "marks_obtained") or 100) < 50][:5]
    for i, as_id in enumerate(low_mark_sheets[:5]):
        rev_id = f"REV-{yr}-{i+1:05d}"
        if frappe.db.exists("Revaluation Request", rev_id):
            rev_count += 1
            continue
        try:
            student = frappe.db.get_value("Answer Sheet", as_id, "student")
            frappe.get_doc({
                "doctype": "Revaluation Request",
                "name": rev_id,
                "answer_sheet": as_id,
                "student": student,
                "reason": "Marks seem lower than expected based on attempted questions.",
                "status": "Pending",
                "request_date": add_days(nowdate(), -random.randint(1, 15)),
            }).insert(ignore_permissions=True, ignore_links=True)
            rev_count += 1
        except Exception as e:
            if rev_count < 2:
                print(f"  RevaluationRequest {rev_id}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Student Transcripts (50) ──────────────────────────────────────────────
    for i, stu in enumerate(students[:50]):
        sid = stu[0] if isinstance(stu, tuple) else stu
        sname = stu[1] if isinstance(stu, tuple) and len(stu) > 1 else sid
        tr_id = f"TR-{yr}-{i+1:05d}"
        if frappe.db.exists("Student Transcript", tr_id):
            tr_count += 1
            continue
        try:
            results = []
            for j, ce in enumerate(courses[:6]):
                cid = ce[0] if isinstance(ce, tuple) else ce
                cname = ce[1] if isinstance(ce, tuple) and len(ce) > 1 else cid
                m = random.randint(50, 95)
                results.append({
                    "course": cid,
                    "course_name": cname,
                    "marks_obtained": m,
                    "max_marks": 100,
                    "grade": "O" if m >= 90 else ("A+" if m >= 85 else ("A" if m >= 75 else ("B+" if m >= 65 else "B"))),
                    "credit_points": 4,
                })
            tr_doc = frappe.get_doc({
                "doctype": "Student Transcript",
                "name": tr_id,
                "student": sid,
                "student_name": sname,
                "academic_year": ay,
                "academic_term": at,
                "semester": (i % 8) + 1,
                "cgpa": round(random.uniform(6.5, 9.8), 2),
                "results": results,
                "status": "Issued",
            })
            tr_doc.flags.name_set = True
            tr_doc.flags.ignore_mandatory = True
            tr_doc.insert(ignore_permissions=True, ignore_links=True)
            tr_count += 1
        except Exception as e:
            if tr_count < 2:
                print(f"  StudentTranscript {tr_id}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Notification Templates (8) ────────────────────────────────────────────
    notif_templates = [
        ("Hall Ticket Issued", "Your hall ticket for {{exam_name}} has been issued."),
        ("Fee Due Reminder", "Your fee of ₹{{amount}} is due on {{due_date}}."),
        ("Result Published", "Results for {{course}} have been published."),
        ("Holiday Notice", "{{date}} is a holiday: {{reason}}."),
        ("Exam Schedule Update", "Exam for {{course}} is scheduled on {{date}}."),
        ("Library Overdue", "Book '{{book}}' is overdue. Please return by {{date}}."),
        ("Hostel Maintenance", "Your maintenance request #{{id}} has been resolved."),
        ("Placement Drive", "{{company}} drive is on {{date}}. Apply before {{last_date}}."),
    ]
    for nt_name, nt_body in notif_templates:
        if frappe.db.exists("Notification Template", {"template_name": nt_name}):
            nt_count += 1
            continue
        try:
            nt_doc = frappe.get_doc({
                "doctype": "Notification Template",
                "template_name": nt_name,
                "subject": nt_name,
                "template": nt_body,
            })
            nt_doc.flags.ignore_mandatory = True
            nt_doc.insert(ignore_permissions=True, ignore_links=True)
            nt_count += 1
        except Exception as e:
            if nt_count < 2:
                print(f"  NotificationTemplate {nt_name}: {str(e)[:80]}")

    # ── Certificate Templates (4) ─────────────────────────────────────────────
    # certificate_type valid values match these names exactly
    cert_types = [
        ("Bonafide Certificate", "Bonafide Certificate"),
        ("Character Certificate", "Character Certificate"),
        ("Migration Certificate", "Migration Certificate"),
        ("Transfer Certificate", "Transfer Certificate"),
    ]
    cert_template_names = []
    for ct_name, ct_type in cert_types:
        if frappe.db.exists("Certificate Template", {"template_name": ct_name}):
            existing = frappe.db.get_value("Certificate Template", {"template_name": ct_name}, "name")
            cert_template_names.append(existing)
            ct_count += 1
            continue
        try:
            ct_doc = frappe.get_doc({
                "doctype": "Certificate Template",
                "template_name": ct_name,
                "certificate_type": ct_type,
            })
            ct_doc.flags.ignore_mandatory = True
            ct_doc.flags.ignore_validate = True
            ct_doc.insert(ignore_permissions=True, ignore_links=True)
            cert_template_names.append(ct_doc.name)
            ct_count += 1
        except Exception as e:
            if ct_count < 2:
                print(f"  CertificateTemplate {ct_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Certificate Requests (20) ─────────────────────────────────────────────
    portal_student_ids = []
    for email in ["student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
                  "student4@nit.edu", "student5@nit.edu"]:
        sid = frappe.db.get_value("Student", {"student_email_id": email}, "name")
        if sid:
            portal_student_ids.append(sid)

    if not portal_student_ids:
        portal_student_ids = [s[0] for s in students[:5]] if students else []

    for i in range(20):
        cr_id = f"CERT-{yr}-{i+1:05d}"
        if frappe.db.exists("Certificate Request", cr_id):
            cr_count += 1
            continue
        try:
            sid = portal_student_ids[i % len(portal_student_ids)] if portal_student_ids else None
            ct = cert_template_names[i % len(cert_template_names)] if cert_template_names else None
            if not sid:
                continue
            cr_doc = frappe.get_doc({
                "doctype": "Certificate Request",
                "name": cr_id,
                "student": sid,
                "request_date": add_days(nowdate(), -random.randint(1, 60)),
                "status": "Issued" if i < 15 else "Pending",
            })
            if ct:
                cr_doc.certificate_template = ct
            cr_doc.flags.name_set = True
            cr_doc.flags.ignore_mandatory = True
            cr_doc.flags.ignore_validate = True
            cr_doc.insert(ignore_permissions=True, ignore_links=True)
            cr_count += 1
        except Exception as e:
            if cr_count < 2:
                print(f"  CertificateRequest {cr_id}: {str(e)[:80]}")

    frappe.db.commit()
    print(
        f"  ExternalExaminer: {ee_count}, QPTemplate: {qpt_count}, "
        f"PracticalExam: {pe_count}, InternalAssessment: {ia_count}, "
        f"AnswerSheet: {as_count}, Revaluation: {rev_count}, "
        f"StudentTranscript: {tr_count}, NotifTemplate: {nt_count}, "
        f"CertTemplate: {ct_count}, CertRequest: {cr_count}"
    )


# === Layer 11d — OBE / Accreditation =========================================

def _seed_obe_accreditation_v2(ctx):
    """Accreditation Cycle, Assessment Rubric, OBE Survey, Survey Template,
    PO Attainment, NAAC Metric, NIRF Data.
    """
    yr = "2026"
    ay = ctx.get("academic_year", "2026-2027")
    programs = ctx.get("programs", [])
    employees = frappe.get_all("Employee", pluck="name", limit=1)
    coord = employees[0] if employees else None

    accr_count = rubric_count = survey_count = st_count = 0
    po_att_count = naac_count = nirf_count = 0

    # ── Accreditation Cycle ───────────────────────────────────────────────────
    # coordinator must be a User (not Employee); coordinator field is Link→User
    admin_user = frappe.db.get_value("User", {"name": ["!=", "Guest"]}, "name") or "Administrator"
    accr_cycle_name = None
    if not frappe.db.exists("Accreditation Cycle", {"cycle_name": "NAAC Cycle 4 2026 Assessment"}):
        try:
            accr_doc = frappe.get_doc({
                "doctype": "Accreditation Cycle",
                "cycle_name": "NAAC Cycle 4 2026 Assessment",
                "accreditation_body": "NAAC",
                "assessment_year": "2026",
                "data_period_start": add_days(nowdate(), -365),
                "data_period_end": nowdate(),
                "scope_type": "Institution Level",
                "coordinator": admin_user,
                "status": "Data Collection",
            })
            accr_doc.flags.ignore_mandatory = True
            accr_doc.insert(ignore_permissions=True, ignore_links=True)
            accr_cycle_name = accr_doc.name
            accr_count += 1
        except Exception as e:
            print(f"  AccreditationCycle: {str(e)[:100]}")
    else:
        accr_cycle_name = frappe.db.get_value("Accreditation Cycle",
                            {"cycle_name": "NAAC Cycle 4 2026 Assessment"}, "name")
        accr_count += 1

    if not accr_cycle_name:
        # Try to get any existing accreditation cycle
        accr_cycle_name = frappe.db.get_value("Accreditation Cycle", {}, "name")

    # ── Assessment Rubrics (8, one per program) ───────────────────────────────
    # Assessment Rubric has no program/academic_year fields — only rubric_name, course, assessment_type, levels
    # frappe.db.exists with dict throws "Unknown column 'user'" due to permission filters — use raw SQL
    for i, prog in enumerate(programs[:8]):
        pname = prog[0] if isinstance(prog, tuple) else prog
        plong = prog[1] if isinstance(prog, tuple) and len(prog) > 1 else pname
        rubric_name = f"{plong[:30]} OBE Rubric {yr}"
        existing = frappe.db.sql(
            "SELECT name FROM `tabAssessment Rubric` WHERE rubric_name=%s LIMIT 1",
            rubric_name, as_dict=True
        )
        if existing:
            rubric_count += 1
            continue
        try:
            # Use raw SQL to bypass Frappe permission filter bug ("Unknown column 'user'")
            import uuid
            now_str = frappe.utils.now()
            frappe.db.sql("""
                INSERT INTO `tabAssessment Rubric`
                (name, creation, modified, modified_by, owner, docstatus, idx,
                 rubric_name, level_1_label, level_1_min_percentage,
                 level_2_label, level_2_min_percentage,
                 level_3_label, level_3_min_percentage,
                 level_4_label, level_4_min_percentage, is_active)
                VALUES (%s, %s, %s, 'Administrator', 'Administrator', 0, %s,
                        %s, 'Excellent', 80.0, 'Good', 65.0,
                        'Average', 50.0, 'Below Average', 35.0, 1)
            """, (rubric_name[:140], now_str, now_str, i + 1, rubric_name[:140]))
            rubric_count += 1
        except Exception as e:
            if rubric_count < 2:
                print(f"  AssessmentRubric {pname}: {str(e)[:80]}")

    # ── Survey Templates ──────────────────────────────────────────────────────
    st_templates = []
    for st_name in ["Standard PO Survey", "Standard PEO Survey"]:
        if frappe.db.exists("Survey Template", {"template_name": st_name}):
            existing = frappe.db.get_value("Survey Template", {"template_name": st_name}, "name")
            st_templates.append(existing)
            st_count += 1
            continue
        try:
            q_list = [
                {"question": f"Rate attainment of PO{j+1}", "question_type": "Rating",
                 "min_rating": 1, "max_rating": 5}
                for j in range(6)
            ]
            doc = frappe.get_doc({
                "doctype": "Survey Template",
                "template_name": st_name,
                "description": f"{st_name} for year {yr}",
                "questions": q_list,
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            st_templates.append(doc.name)
            st_count += 1
        except Exception as e:
            if st_count < 2:
                print(f"  SurveyTemplate {st_name}: {str(e)[:80]}")

    # ── OBE Surveys (4) ───────────────────────────────────────────────────────
    # survey_type valid: Alumni Survey, Employer Survey, Student Exit Survey,
    #   Course End Survey, Program Exit Survey, Mid-term Feedback
    survey_types = [
        ("Course End Survey 2026", "Course End Survey"),
        ("Program Exit Survey 2026", "Program Exit Survey"),
        ("Employer Survey 2026", "Employer Survey"),
        ("Alumni Survey 2026", "Alumni Survey"),
    ]
    first_program = programs[0][0] if programs else None
    for sv_idx, (sv_name, sv_type) in enumerate(survey_types):
        if frappe.db.exists("OBE Survey", {"survey_type": sv_type, "academic_year": ay}):
            survey_count += 1
            continue
        try:
            prog = programs[sv_idx % len(programs)][0] if programs else first_program
            sv_doc = frappe.get_doc({
                "doctype": "OBE Survey",
                "survey_type": sv_type,
                "program": prog,
                "academic_year": ay,
                "respondent_name": f"General Respondent {sv_idx+1}",
                "status": "Submitted",
            })
            sv_doc.flags.ignore_mandatory = True
            sv_doc.flags.ignore_validate = True
            sv_doc.insert(ignore_permissions=True, ignore_links=True)
            survey_count += 1
        except Exception as e:
            if survey_count < 2:
                print(f"  OBESurvey {sv_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── PO Attainment (8, one per program) ────────────────────────────────────
    for i, prog in enumerate(programs[:8]):
        pname = prog[0] if isinstance(prog, tuple) else prog
        if frappe.db.exists("PO Attainment", {"program": pname, "academic_year": ay}):
            po_att_count += 1
            continue
        try:
            # Get POs for this program
            pos = frappe.get_all("Program Outcome",
                filters={"program": pname},
                pluck="name",
                limit=12,
            )
            entries = []
            for po_name in pos:
                entries.append({
                    "program_outcome": po_name,
                    "direct_attainment": round(random.uniform(55.0, 85.0), 2),
                    "indirect_attainment": round(random.uniform(60.0, 90.0), 2),
                    "overall_attainment": round(random.uniform(58.0, 87.0), 2),
                })
            if not entries:
                po_att_count += 1
                continue
            po_doc = frappe.get_doc({
                "doctype": "PO Attainment",
                "program": pname,
                "academic_year": ay,
                "attainment_entries": entries,
                "status": "Submitted",
            })
            po_doc.flags.ignore_mandatory = True
            po_doc.insert(ignore_permissions=True, ignore_links=True)
            frappe.db.set_value("PO Attainment", po_doc.name, "docstatus", 1,
                                update_modified=False)
            po_att_count += 1
        except Exception as e:
            if po_att_count < 2:
                print(f"  POAttainment {pname}: {str(e)[:80]}")

    frappe.db.commit()

    # ── NAAC Metrics (25) ─────────────────────────────────────────────────────
    # criterion must be full string value as per Select options
    _NAAC_CRITERION_MAP = {
        1: "1. Curricular Aspects",
        2: "2. Teaching-Learning and Evaluation",
        3: "3. Research, Innovations and Extension",
        4: "4. Infrastructure and Learning Resources",
        5: "5. Student Support and Progression",
        6: "6. Governance, Leadership and Management",
        7: "7. Institutional Values and Best Practices",
    }
    naac_metrics = [
        # (criterion_num, metric_number, metric_name, weightage, metric_type)
        (1, "1.1.1", "Curriculum Design and Development", 0.5, "Quantitative Metric (QnM)"),
        (1, "1.1.2", "Academic Flexibility", 0.3, "Qualitative Metric (QlM)"),
        (1, "1.2.1", "Add-on/Certificate Programmes", 0.4, "Quantitative Metric (QnM)"),
        (1, "1.3.1", "Crosscutting Issues", 0.3, "Qualitative Metric (QlM)"),
        (2, "2.1.1", "Student Enrolment vs Sanctioned Seats", 0.5, "Quantitative Metric (QnM)"),
        (2, "2.1.2", "Seats Filled Against Reserved Categories", 0.5, "Quantitative Metric (QnM)"),
        (2, "2.2.1", "Student Full-Time Teacher Ratio", 0.5, "Quantitative Metric (QnM)"),
        (2, "2.4.1", "Full Time Teachers Against Sanctioned Posts", 0.5, "Quantitative Metric (QnM)"),
        (2, "2.6.1", "Attainment of Programme Outcomes", 0.5, "Qualitative Metric (QlM)"),
        (3, "3.1.1", "Grants for Research Projects", 0.4, "Quantitative Metric (QnM)"),
        (3, "3.2.1", "Workshops/Seminars on Research Methodology", 0.3, "Quantitative Metric (QnM)"),
        (3, "3.3.1", "Number of PhDs Awarded", 0.5, "Quantitative Metric (QnM)"),
        (3, "3.4.1", "Extension Activities", 0.3, "Qualitative Metric (QlM)"),
        (4, "4.1.1", "Physical Facilities", 0.4, "Qualitative Metric (QlM)"),
        (4, "4.2.1", "Library as a Learning Resource", 0.4, "Qualitative Metric (QlM)"),
        (4, "4.3.1", "IT Infrastructure", 0.4, "Qualitative Metric (QlM)"),
        (4, "4.4.1", "Maintenance of Infrastructure", 0.3, "Qualitative Metric (QlM)"),
        (5, "5.1.1", "Scholarships and Freeships", 0.4, "Quantitative Metric (QnM)"),
        (5, "5.2.1", "Placement and Higher Education", 0.5, "Quantitative Metric (QnM)"),
        (5, "5.3.1", "Sports and Cultural Activities", 0.3, "Quantitative Metric (QnM)"),
        (6, "6.1.1", "Institutional Vision and Leadership", 0.3, "Qualitative Metric (QlM)"),
        (6, "6.3.1", "Professional Development of Teachers", 0.4, "Quantitative Metric (QnM)"),
        (6, "6.5.1", "Internal Quality Assurance System", 0.5, "Qualitative Metric (QlM)"),
        (7, "7.1.1", "Gender Equity", 0.4, "Qualitative Metric (QlM)"),
        (7, "7.2.1", "Best Practices", 0.3, "Qualitative Metric (QlM)"),
    ]
    for criterion_num, metric_no, metric_name, weight, mtype in naac_metrics:
        naac_id = f"NAAC-{criterion_num}-{metric_no}"
        if frappe.db.exists("NAAC Metric", naac_id):
            naac_count += 1
            continue
        try:
            criterion_str = _NAAC_CRITERION_MAP.get(criterion_num, str(criterion_num))
            nm_doc = frappe.get_doc({
                "doctype": "NAAC Metric",
                "name": naac_id,
                "accreditation_cycle": accr_cycle_name,
                "criterion": criterion_str,
                "metric_number": metric_no,
                "metric_name": metric_name,
                "metric_type": mtype,
                "metric_description": f"Assessment of {metric_name} as per NAAC framework.",
                "weightage": weight,
                "score": round(random.uniform(2.5, 4.5), 2),
                "max_score": 5.0,
                "status": "Submitted",
            })
            nm_doc.flags.name_set = True
            nm_doc.flags.ignore_mandatory = True
            nm_doc.insert(ignore_permissions=True, ignore_links=True)
            naac_count += 1
        except Exception as e:
            if naac_count < 2:
                print(f"  NAACMetric {naac_id}: {str(e)[:80]}")

    frappe.db.commit()

    # ── NIRF Data (8) ─────────────────────────────────────────────────────────
    nirf_categories = ["Engineering", "Management"]
    nirf_years = [2023, 2024, 2025, 2026]
    for ranking_year in nirf_years:
        for category in nirf_categories:
            # Actual name format used by the doctype: NIRF-{year}-{category}
            nirf_id = f"NIRF-{ranking_year}-{category}"
            if frappe.db.exists("NIRF Data", nirf_id):
                nirf_count += 1
                continue
            try:
                nirf_doc = frappe.get_doc({
                    "doctype": "NIRF Data",
                    "name": nirf_id,
                    "ranking_year": str(ranking_year),
                    "category": category,
                    "teaching_learning_score": round(random.uniform(55, 75), 2),
                    "research_score": round(random.uniform(40, 65), 2),
                    "graduation_outcome_score": round(random.uniform(60, 80), 2),
                    "outreach_score": round(random.uniform(30, 55), 2),
                    "perception_score": round(random.uniform(25, 50), 2),
                    "overall_score": round(random.uniform(50, 70), 2),
                    "rank": random.randint(50, 200),
                })
                nirf_doc.flags.name_set = True
                nirf_doc.flags.ignore_mandatory = True
                nirf_doc.insert(ignore_permissions=True, ignore_links=True)
                nirf_count += 1
            except Exception as e:
                if nirf_count < 2:
                    print(f"  NIRFData {nirf_id}: {str(e)[:80]}")

    frappe.db.commit()
    print(
        f"  AccreditationCycle: {accr_count}, AssessmentRubric: {rubric_count}, "
        f"SurveyTemplate: {st_count}, OBESurvey: {survey_count}, "
        f"POAttainment: {po_att_count}, NAACMetric: {naac_count}, NIRFData: {nirf_count}"
    )


# === Layer 11e — Communication & Integrations ================================

def _seed_integrations_v2(ctx):
    """Biometric Device, Biometric Attendance Log, WhatsApp Template,
    SMS Log, SMS Queue, WhatsApp Log, Push Notification Log,
    User Device Token, Payment Transaction, Payment Order,
    Webhook Log, Bank Transaction.
    """
    yr = "2026"
    students = ctx.get("students", [])
    employees = frappe.get_all("Employee", pluck="name", limit=10)
    company = COMPANY
    abbr = COMPANY_ABBR

    bd_count = bal_count = wt_count = sms_count = smsq_count = 0
    wl_count = push_count = udt_count = pt_count = po_count = 0
    wh_count = bt_count = 0

    # ── Biometric Devices (2) ─────────────────────────────────────────────────
    devices = [
        ("Main Gate Biometric", "ZKTeco", "ZK4500"),
        ("Faculty Block Biometric", "Honeywell", "HBF-500"),
    ]
    device_ids = []
    for dev_name, manufacturer, model in devices:
        if frappe.db.exists("Biometric Device", {"device_name": dev_name}):
            existing = frappe.db.get_value("Biometric Device", {"device_name": dev_name}, "name")
            device_ids.append(existing)
            bd_count += 1
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Biometric Device",
                "device_name": dev_name,
                "manufacturer": manufacturer,
                "model": model,
                "location": "NIT Campus",
                "ip_address": f"192.168.1.{random.randint(10, 99)}",
                "status": "Active",
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            device_ids.append(doc.name)
            bd_count += 1
        except Exception as e:
            if bd_count < 2:
                print(f"  BiometricDevice {dev_name}: {str(e)[:80]}")
            device_ids.append(None)

    frappe.db.commit()

    # ── Biometric Attendance Logs (100) ───────────────────────────────────────
    # Fields: device(→BiometricDevice), user_id(Data), punch_time(Datetime),
    #         punch_type(Select), employee(→Employee), student(→Student)
    # Skip if we already have >= 80 records
    existing_bal = frappe.db.count("Biometric Attendance Log")
    if existing_bal >= 80:
        bal_count = existing_bal
    else:
        valid_devices = [d for d in device_ids if d]
        needed = 100 - existing_bal
        for i in range(needed):
            emp = employees[i % len(employees)] if employees else None
            if not emp or not valid_devices:
                continue
            device = valid_devices[i % len(valid_devices)]
            # Use unique punch_time per employee to avoid conflicts
            punch_dt = frappe.utils.add_to_date(
                frappe.utils.now(),
                days=-(i % 30),
                hours=-(i // 30),
            )
            try:
                bal_doc = frappe.get_doc({
                    "doctype": "Biometric Attendance Log",
                    "device": device,
                    "user_id": emp.split("-")[-1] if emp else f"EMP{i:03d}",
                    "punch_time": punch_dt,
                    "punch_type": "Check In" if i % 2 == 0 else "Check Out",
                    "employee": emp,
                    "processed": 1,
                })
                bal_doc.flags.ignore_mandatory = True
                bal_doc.insert(ignore_permissions=True, ignore_links=True)
                bal_count += 1
            except Exception as e:
                if bal_count < 2:
                    print(f"  BiometricLog: {str(e)[:80]}")

    frappe.db.commit()

    # ── WhatsApp Templates (4) ────────────────────────────────────────────────
    wa_templates = [
        ("Hall Ticket Ready", "Your hall ticket for {{exam}} is ready. Login to download."),
        ("Fee Due Alert", "Fee of ₹{{amount}} is due on {{date}}. Pay now to avoid late fee."),
        ("Exam Result Out", "Results for {{course}} are out. Check your portal."),
        ("Holiday Announcement", "{{date}} is declared holiday on account of {{reason}}."),
    ]
    for wt_name, wt_body in wa_templates:
        if frappe.db.exists("WhatsApp Template", {"template_name": wt_name}):
            wt_count += 1
            continue
        try:
            wt_key = wt_name.lower().replace(" ", "_").replace("—", "").replace("-", "_")
            wt_doc = frappe.get_doc({
                "doctype": "WhatsApp Template",
                "template_name": wt_name,
                "template_key": wt_key,
                "body_text": wt_body,
                "status": "Approved",
                "language": "en",
                "category": "Utility",
            })
            wt_doc.flags.ignore_mandatory = True
            wt_doc.insert(ignore_permissions=True, ignore_links=True)
            wt_count += 1
        except Exception as e:
            if wt_count < 2:
                print(f"  WhatsAppTemplate {wt_name}: {str(e)[:80]}")

    # ── SMS Logs (100) ────────────────────────────────────────────────────────
    # Fields: recipient(REQ), message(REQ), sent_on, status, message_id, sms_gateway
    sms_messages = [
        "Your attendance for today has been updated. Check the portal.",
        "Fee payment due in 7 days. Pay online to avoid penalties.",
        "Hall ticket for upcoming exam is ready. Download from portal.",
        "Results for the semester have been published. Check now.",
        "Library book due for return. Please return by due date.",
    ]
    for i in range(100):
        phone = f"98{random.randint(10000000, 99999999)}"
        try:
            sms_doc = frappe.get_doc({
                "doctype": "SMS Log",
                "recipient": phone,
                "message": sms_messages[i % len(sms_messages)],
                "sent_on": add_days(nowdate(), -(i % 30)),
                "status": "Sent",
                "sms_gateway": "MSG91",
                "message_id": f"MSGID-{yr}-{i+1:05d}",
            })
            sms_doc.flags.ignore_mandatory = True
            sms_doc.insert(ignore_permissions=True, ignore_links=True)
            sms_count += 1
        except Exception as e:
            if sms_count < 2:
                print(f"  SMSLog: {str(e)[:80]}")
            if sms_count > 100:
                break

    frappe.db.commit()

    # ── SMS Queue (5) ─────────────────────────────────────────────────────────
    # Fields: mobile_number(REQ), message(REQ), status, scheduled_time, priority
    for i in range(5):
        try:
            smsq_doc = frappe.get_doc({
                "doctype": "SMS Queue",
                "mobile_number": f"98{random.randint(10000000, 99999999)}",
                "message": f"Scheduled SMS message #{i+1} for students.",
                "status": "Queued",
                "priority": "Normal",
                "scheduled_time": add_days(nowdate(), i + 1),
            })
            smsq_doc.flags.ignore_mandatory = True
            smsq_doc.insert(ignore_permissions=True, ignore_links=True)
            smsq_count += 1
        except Exception as e:
            if smsq_count < 2:
                print(f"  SMSQueue: {str(e)[:80]}")

    # ── WhatsApp Logs (50) ────────────────────────────────────────────────────
    # Fields: phone_number(REQ), direction, message_type, status, message_id,
    #         template_name, message_content, sent_at, delivered_at
    for i in range(50):
        phone = f"98{random.randint(10000000, 99999999)}"
        try:
            wl_doc = frappe.get_doc({
                "doctype": "WhatsApp Log",
                "phone_number": phone,
                "direction": "Outgoing",
                "message_type": "template",
                "status": "Delivered",
                "message_id": f"WA-MSG-{yr}-{i+1:05d}",
                "template_name": "Hall Ticket Ready",
                "message_content": f"WhatsApp message #{i+1} sent via NIT-EMS.",
                "sent_at": add_days(nowdate(), -(i % 20)),
            })
            wl_doc.flags.ignore_mandatory = True
            wl_doc.insert(ignore_permissions=True, ignore_links=True)
            wl_count += 1
        except Exception as e:
            if wl_count < 2:
                print(f"  WhatsAppLog: {str(e)[:80]}")
            if wl_count > 50:
                break

    frappe.db.commit()

    # ── Push Notification Logs (30) ───────────────────────────────────────────
    demo_users = ["student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
                  "faculty1@nit.edu", "faculty2@nit.edu"]
    for i in range(30):
        recipient = demo_users[i % len(demo_users)]
        try:
            frappe.get_doc({
                "doctype": "Push Notification Log",
                "recipient": recipient,
                "title": f"Notification #{i+1}",
                "body": f"You have a new update in the portal.",
                "sent_on": add_days(nowdate(), -(i % 15)),
                "status": "Delivered",
                "notification_type": "info",
            }).insert(ignore_permissions=True, ignore_links=True)
            push_count += 1
        except Exception as e:
            if push_count < 2:
                print(f"  PushNotifLog: {str(e)[:80]}")
            if push_count > 30:
                break

    # ── User Device Tokens (20) ───────────────────────────────────────────────
    # Fields: user(REQ), platform(Select REQ), token(Small Text REQ),
    #         active(Check), device_name, device_id, app_version, last_used
    all_users = demo_users + ["hod.cse@nit.edu", "admin@nit.edu", "hr@nit.edu",
                               "examcell@nit.edu", "librarian@nit.edu",
                               "faculty3@nit.edu", "faculty4@nit.edu", "faculty5@nit.edu",
                               "student4@nit.edu", "student5@nit.edu"]
    platforms = ["Android", "iOS", "Web"]
    for i in range(min(20, len(all_users))):
        u = all_users[i % len(all_users)]
        if frappe.db.exists("User Device Token", {"user": u}):
            udt_count += 1
            continue
        try:
            udt_doc = frappe.get_doc({
                "doctype": "User Device Token",
                "user": u,
                "token": f"FCM_{u.split('@')[0].upper()}_{random.randint(100000, 999999)}",
                "platform": ["android", "ios", "web"][i % 3],
                "active": 1,
                "device_name": f"{platforms[i % 3]} Device {i+1}",
                "device_id": f"DEV-{random.randint(100000000, 999999999)}",
                "last_used": add_days(nowdate(), -(i % 7)),
            })
            udt_doc.flags.ignore_mandatory = True
            udt_doc.insert(ignore_permissions=True, ignore_links=True)
            udt_count += 1
        except Exception as e:
            if udt_count < 2:
                print(f"  UserDeviceToken {u}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Payment Transactions (50) ─────────────────────────────────────────────
    invoices = frappe.get_all("Sales Invoice", pluck="name", limit=50)
    all_student_ids = [s[0] if isinstance(s, tuple) else s for s in students[:50]]
    for i, inv_name in enumerate(invoices[:50]):
        try:
            amount = frappe.db.get_value("Sales Invoice", inv_name, "grand_total") or 50000
            stu_id = all_student_ids[i % len(all_student_ids)] if all_student_ids else None
            gw_opts = ["Razorpay", "PayU", "CCAvenue"]
            doc = frappe.get_doc({
                "doctype": "Payment Transaction",
                "student": stu_id,
                "reference_doctype": "Sales Invoice",
                "reference_name": inv_name,
                "amount": amount,
                "currency": "INR",
                "payment_gateway": gw_opts[i % 3],
                "gateway_order_id": f"ORD-{yr}-{i+1:08d}",
                "gateway_payment_id": f"PAY-GW-{yr}-{i+1:08d}",
                "status": "Success" if i < 45 else "Failed",
                "transaction_date": add_days(nowdate(), -(i % 60)),
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            pt_count += 1
        except Exception as e:
            if pt_count < 2:
                print(f"  PaymentTransaction: {str(e)[:80]}")
            if pt_count > 50:
                break

    frappe.db.commit()

    # ── Payment Orders (5) ────────────────────────────────────────────────────
    # Fields: reference_doctype(REQ), reference_name(REQ), payment_gateway(Select REQ),
    #         amount(REQ), status, student, creation_date, gateway_order_id
    gw_opts = ["Razorpay", "PayU", "CCAvenue"]
    for i, inv_name in enumerate(invoices[:5]):
        if frappe.db.exists("Payment Order", {"reference_name": inv_name}):
            po_count += 1
            continue
        try:
            amount = frappe.db.get_value("Sales Invoice", inv_name, "grand_total") or 50000
            stu_id = all_student_ids[i % len(all_student_ids)] if all_student_ids else None
            po_doc = frappe.get_doc({
                "doctype": "Payment Order",
                "reference_doctype": "Sales Invoice",
                "reference_name": inv_name,
                "payment_gateway": gw_opts[i % 3],
                "amount": amount,
                "currency": "INR",
                "student": stu_id,
                "status": "Pending",
                "creation_date": add_days(nowdate(), -i * 5),
                "gateway_order_id": f"PO-ORD-{yr}-{i+1:05d}",
            })
            po_doc.flags.ignore_mandatory = True
            po_doc.insert(ignore_permissions=True, ignore_links=True)
            po_count += 1
        except Exception as e:
            if po_count < 2:
                print(f"  PaymentOrder: {str(e)[:80]}")

    # ── Webhook Logs (20) ─────────────────────────────────────────────────────
    for i in range(20):
        try:
            frappe.get_doc({
                "doctype": "Webhook Log",
                "webhook_trigger": f"payment.success",
                "webhook_type": ["razorpay", "payu"][i % 2],
                "event_created": add_days(nowdate(), -(i % 20)),
                "data": f'{{"payment_id": "pay_{i+1:06d}", "amount": {random.randint(10000, 100000)}, "status": "captured"}}',
            }).insert(ignore_permissions=True, ignore_links=True)
            wh_count += 1
        except Exception as e:
            if wh_count < 2:
                print(f"  WebhookLog: {str(e)[:80]}")
            if wh_count > 20:
                break

    frappe.db.commit()

    # ── Bank Transactions (50) ────────────────────────────────────────────────
    bank_account = frappe.db.get_value("Bank Account", {"company": company}, "name")
    if bank_account:
        for i in range(50):
            try:
                amount = random.randint(5000, 200000)
                frappe.get_doc({
                    "doctype": "Bank Transaction",
                    "date": add_days(nowdate(), -(i % 60)),
                    "bank_account": bank_account,
                    "deposit": amount if i % 2 == 0 else 0,
                    "withdrawal": amount if i % 2 == 1 else 0,
                    "currency": "INR",
                    "description": f"Fee collection / vendor payment #{i+1}",
                    "reference_number": f"REF-{yr}-{i+1:05d}",
                    "status": "Unreconciled",
                }).insert(ignore_permissions=True, ignore_links=True)
                bt_count += 1
            except Exception as e:
                if bt_count < 2:
                    print(f"  BankTransaction: {str(e)[:80]}")
                if bt_count > 50:
                    break

    frappe.db.commit()
    print(
        f"  BiometricDevice: {bd_count}, BiometricLog: {bal_count}, "
        f"WhatsAppTemplate: {wt_count}, SMSLog: {sms_count}, SMSQueue: {smsq_count}, "
        f"WhatsAppLog: {wl_count}, PushLog: {push_count}, DeviceToken: {udt_count}, "
        f"PaymentTxn: {pt_count}, PaymentOrder: {po_count}, "
        f"WebhookLog: {wh_count}, BankTransaction: {bt_count}"
    )


# === Layer 11f — Portal richness for student1..5 =============================

def _seed_portal_richness_v2(ctx):
    """Backfill all student-portal-visible data for student1..5@nit.edu:
    Student Status Log, Student Resume, Placement Profile,
    Course Registration, Hostel Attendance, Hostel Visitor,
    Hostel Maintenance Request, Library Transaction top-up,
    Book Reservation, Library Fine, Transport Trip Log,
    Student Scholarship, Scholarship Type, Student Result,
    Assessment Result, Notification Preference, Course Schedule,
    Announcement, subject-wise attendance back-fill.
    """
    yr = "2026"
    ay = ctx.get("academic_year", "2026-2027")
    at = ctx.get("academic_term", "")
    courses = ctx.get("courses", [])
    students = ctx.get("students", [])
    programs = ctx.get("programs", [])
    company = COMPANY

    sl_count = res_count = pp_count = cr_count = ha_count = 0
    hv_count = hmr_count = lt_count = br_count = lf_count = 0
    tt_count = ss_count = sr_count = ar_count = np_count = 0
    cs_count = ann_count = att_count = 0

    # Get portal student IDs
    portal_emails = [
        "student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
        "student4@nit.edu", "student5@nit.edu",
    ]
    portal_students = []
    for email in portal_emails:
        sid = frappe.db.get_value("Student", {"student_email_id": email}, "name")
        if sid:
            sname = frappe.db.get_value("Student", sid, "student_name")
            prog = frappe.db.get_value("Program Enrollment", {"student": sid}, "program")
            portal_students.append((sid, sname or sid, prog or "BTCSE", email))

    if not portal_students and students:
        portal_students = [(s[0], s[1] if len(s) > 1 else s[0],
                           s[2] if len(s) > 2 else "BTCSE",
                           s[6] if len(s) > 6 else "student@nit.edu")
                          for s in students[:5]]

    # ── Scholarship Types ─────────────────────────────────────────────────────
    st_types = [
        ("Merit Scholarship", "MERIT-01", "Merit-based"),
        ("Need-Based Scholarship", "NEED-01", "Need-based"),
        ("Sports Scholarship", "SPORT-01", "Sports"),
        ("Research Fellowship", "RES-01", "Merit-based"),
    ]
    for st_name, st_code, st_type in st_types:
        if not frappe.db.exists("Scholarship Type", {"scholarship_name": st_name}):
            try:
                frappe.get_doc({
                    "doctype": "Scholarship Type",
                    "scholarship_name": st_name,
                    "scholarship_code": st_code,
                    "type": st_type,
                    "discount_percentage": random.randint(25, 100),
                }).insert(ignore_permissions=True, ignore_links=True)
            except Exception as e:
                if ss_count < 2:
                    print(f"  ScholarshipType {st_name}: {str(e)[:80]}")

    frappe.db.commit()

    for i, (sid, sname, prog_id, email) in enumerate(portal_students):

        # ── Student Status Log ────────────────────────────────────────────────
        for from_st, to_st in [("Enrolled", "Continuing"), ("Continuing", "Promoted")]:
            if not frappe.db.exists("Student Status Log", {
                "student": sid, "to_status": to_st
            }):
                try:
                    frappe.get_doc({
                        "doctype": "Student Status Log",
                        "student": sid,
                        "student_name": sname,
                        "transition_date": add_days(nowdate(), -random.randint(30, 90)),
                        "from_status": from_st,
                        "to_status": to_st,
                        "reason": f"Academic year {ay} status update",
                    }).insert(ignore_permissions=True, ignore_links=True)
                    sl_count += 1
                except Exception as e:
                    if sl_count < 2:
                        print(f"  StudentStatusLog {sid}: {str(e)[:80]}")

        # ── Student Resume ────────────────────────────────────────────────────
        if not frappe.db.exists("Student Resume", {"student": sid}):
            try:
                prog_name = frappe.db.get_value("Program", prog_id, "program_name") or prog_id
                doc = frappe.get_doc({
                    "doctype": "Student Resume",
                    "student": sid,
                    "student_name": sname,
                    "program": prog_name,
                    "career_objective": "Aspiring engineer seeking opportunities in technology and innovation.",
                    "current_semester": 4,
                    "work_experience": "Intern at TechCorp (Summer 2025) — developed REST APIs.",
                    "certifications": "Python for Data Science (Coursera), AWS Cloud Practitioner.",
                    "achievements": f"Dept Rank 3 in AY {ay}. Best Project Award.",
                })
                doc.flags.ignore_mandatory = True
                doc.flags.ignore_validate = True
                doc.insert(ignore_permissions=True, ignore_links=True)
                res_count += 1
            except Exception as e:
                if res_count < 2:
                    print(f"  StudentResume {sid}: {str(e)[:80]}")

        # ── Placement Profile ─────────────────────────────────────────────────
        if not frappe.db.exists("Placement Profile", {"student": sid}):
            try:
                frappe.get_doc({
                    "doctype": "Placement Profile",
                    "student": sid,
                    "student_name": sname,
                    "program": prog_id,
                    "cgpa": round(random.uniform(7.0, 9.8), 2),
                    "tenth_percentage": round(random.uniform(82.0, 97.0), 2),
                    "twelfth_percentage": round(random.uniform(80.0, 95.0), 2),
                    "backlogs": 0,
                    "is_placed": 0,
                    "status": "Active",
                }).insert(ignore_permissions=True, ignore_links=True)
                pp_count += 1
            except Exception as e:
                if pp_count < 2:
                    print(f"  PlacementProfile {sid}: {str(e)[:80]}")

        # ── Course Registration ───────────────────────────────────────────────
        if not frappe.db.exists("Course Registration", {"student": sid, "academic_term": at}):
            try:
                enrolled_courses = frappe.get_all(
                    "Course Enrollment",
                    filters={"student": sid},
                    pluck="course",
                    limit=6,
                )
                if enrolled_courses:
                    reg_courses = [{"course": c} for c in enrolled_courses]
                    cr_doc = frappe.get_doc({
                        "doctype": "Course Registration",
                        "student": sid,
                        "academic_year": ay,
                        "academic_term": at,
                        "registration_date": add_days(nowdate(), -60),
                        "status": "Approved",
                        "courses": reg_courses,
                    })
                    cr_doc.flags.ignore_mandatory = True
                    cr_doc.insert(ignore_permissions=True, ignore_links=True)
                    cr_count += 1
            except Exception as e:
                if cr_count < 2:
                    print(f"  CourseRegistration {sid}: {str(e)[:80]}")

        # ── Hostel Attendance (30 days) ────────────────────────────────────────
        hostel_alloc_room = frappe.db.get_value(
            "Hostel Allocation", {"student": sid}, "room"
        )
        for day_offset in range(30):
            log_date = add_days(nowdate(), -day_offset)
            if frappe.db.exists("Hostel Attendance", {
                "student": sid, "attendance_date": log_date
            }):
                ha_count += 1
                continue
            try:
                doc = frappe.get_doc({
                    "doctype": "Hostel Attendance",
                    "student": sid,
                    "student_name": sname,
                    "attendance_date": log_date,
                    "status": "Present" if random.random() < 0.9 else "Absent",
                    "room": hostel_alloc_room,
                })
                doc.flags.ignore_mandatory = True
                doc.flags.ignore_validate = True
                doc.insert(ignore_permissions=True, ignore_links=True)
                ha_count += 1
            except Exception as e:
                if ha_count < 2:
                    print(f"  HostelAttendance {sid}: {str(e)[:80]}")
                break

        # ── Hostel Visitor (2 per portal student) ─────────────────────────────
        hostel_building = frappe.db.get_value("Hostel Allocation", {"student": sid}, "hostel_building") or (
            frappe.get_all("Hostel Building", pluck="name", limit=1) or [None]
        )[0]
        for vi in range(2):
            if frappe.db.exists("Hostel Visitor", {
                "student": sid, "purpose": f"Parent Visit {vi+1}"
            }):
                hv_count += 1
                continue
            try:
                hv_doc = frappe.get_doc({
                    "doctype": "Hostel Visitor",
                    "student": sid,
                    "student_name": sname,
                    "visitor_name": f"Guardian of {sname}",
                    "visitor_mobile": f"98765{i:05d}",
                    "relationship": "Parent",
                    "building": hostel_building,
                    "room": hostel_alloc_room,
                    "visit_date": add_days(nowdate(), -(vi * 14 + 7)),
                    "check_in_time": "10:00:00",
                    "expected_checkout_time": "17:00:00",
                    "purpose": f"Parent Visit {vi+1}",
                    "status": "Checked Out",
                })
                hv_doc.flags.ignore_mandatory = True
                hv_doc.flags.ignore_validate = True
                hv_doc.insert(ignore_permissions=True, ignore_links=True)
                hv_count += 1
            except Exception as e:
                if hv_count < 2:
                    print(f"  HostelVisitor {sid}: {str(e)[:80]}")

        # ── Hostel Maintenance Request ────────────────────────────────────────
        # request_type valid: Electrical, Plumbing, Furniture, Cleaning, AC, Internet, Other
        if not frappe.db.exists("Hostel Maintenance Request", {"requested_by": sid}):
            try:
                issue_types = ["Electrical", "Plumbing", "Furniture", "Cleaning"]
                descriptions = [
                    "Light not working in room.",
                    "Tap dripping continuously.",
                    "Chair broken and needs replacement.",
                    "Room needs deep cleaning."
                ]
                hmr_doc = frappe.get_doc({
                    "doctype": "Hostel Maintenance Request",
                    "requested_by": sid,
                    "student_name": sname,
                    "building": hostel_building,
                    "room": hostel_alloc_room,
                    "request_type": issue_types[i % 4],
                    "subject": f"{issue_types[i % 4]} issue in room",
                    "description": descriptions[i % 4],
                    "priority": "Medium",
                    "status": "Completed",
                    "request_date": add_days(nowdate(), -random.randint(5, 30)),
                    "actual_completion": add_days(nowdate(), -random.randint(1, 4)),
                })
                hmr_doc.flags.ignore_mandatory = True
                hmr_doc.flags.ignore_validate = True
                hmr_doc.insert(ignore_permissions=True, ignore_links=True)
                hmr_count += 1
            except Exception as e:
                if hmr_count < 2:
                    print(f"  HostelMaintenanceRequest {sid}: {str(e)[:80]}")

        # ── Library Member (create if missing for portal student) ────────────────
        lib_member = frappe.db.get_value("Library Member", {"student": sid}, "name")
        if not lib_member:
            try:
                lm_doc = frappe.get_doc({
                    "doctype": "Library Member",
                    "first_name": sname.split()[0] if sname else sname,
                    "last_name": " ".join(sname.split()[1:]) if sname and len(sname.split()) > 1 else "",
                    "email_id": email,
                    "student": sid,
                    "membership_type": "Student",
                })
                lm_doc.flags.ignore_mandatory = True
                lm_doc.insert(ignore_permissions=True, ignore_links=True)
                lib_member = lm_doc.name
            except Exception as e:
                pass  # Silently skip if Library Member creation fails

        # ── Library Transactions (4 per portal student) ───────────────────────
        articles = frappe.get_all("Library Article", pluck="name", limit=4)
        for j, article in enumerate(articles[:4]):
            issue_date = add_days(nowdate(), -(j * 15 + 5))
            return_date = add_days(issue_date, 14)
            if not lib_member:
                break
            if frappe.db.exists("Library Transaction", {
                "member": lib_member, "article": article, "transaction_type": "Issue"
            }):
                lt_count += 1
                continue
            try:
                lt_doc = frappe.get_doc({
                    "doctype": "Library Transaction",
                    "member": lib_member,
                    "article": article,
                    "transaction_type": "Issue",
                    "transaction_date": issue_date,
                    "issue_date": issue_date,
                    "due_date": return_date,
                    "status": "Issued" if j == 0 else "Returned",
                    "return_date": return_date if j > 0 else None,
                })
                lt_doc.flags.ignore_mandatory = True
                lt_doc.flags.ignore_validate = True
                lt_doc.insert(ignore_permissions=True, ignore_links=True)
                lt_count += 1
            except Exception as e:
                if lt_count < 2:
                    print(f"  LibraryTransaction {sid}: {str(e)[:80]}")

        # ── Book Reservation ──────────────────────────────────────────────────
        if lib_member and articles and not frappe.db.exists("Book Reservation", {
            "member": lib_member
        }):
            try:
                br_doc = frappe.get_doc({
                    "doctype": "Book Reservation",
                    "member": lib_member,
                    "article": articles[-1] if articles else None,
                    "reservation_date": add_days(nowdate(), -2),
                    "expiry_date": add_days(nowdate(), 5),
                    "status": "Pending",
                })
                br_doc.flags.ignore_mandatory = True
                br_doc.insert(ignore_permissions=True, ignore_links=True)
                br_count += 1
            except Exception as e:
                if br_count < 2:
                    print(f"  BookReservation {sid}: {str(e)[:80]}")

        # ── Library Fine ──────────────────────────────────────────────────────
        if lib_member and not frappe.db.exists("Library Fine", {"member": lib_member}):
            try:
                lf_doc = frappe.get_doc({
                    "doctype": "Library Fine",
                    "member": lib_member,
                    "fine_date": add_days(nowdate(), -5),
                    "fine_amount": random.randint(10, 50),
                    "status": "Paid",
                    "reason": "Late return of borrowed book",
                    "paid_date": add_days(nowdate(), -2),
                })
                lf_doc.flags.ignore_mandatory = True
                lf_doc.insert(ignore_permissions=True, ignore_links=True)
                lf_count += 1
            except Exception as e:
                if lf_count < 2:
                    print(f"  LibraryFine {sid}: {str(e)[:80]}")

        # ── Student Scholarship ────────────────────────────────────────────────
        if not frappe.db.exists("Student Scholarship", {"student": sid}):
            try:
                ss_doc = frappe.get_doc({
                    "doctype": "Student Scholarship",
                    "student": sid,
                    "student_name": sname,
                    "scholarship_type": "Merit Scholarship",
                    "valid_from": add_days(nowdate(), -180),
                    "valid_till": add_days(nowdate(), 180),
                    "discount_percentage": 50,
                    "status": "Active",
                })
                ss_doc.flags.ignore_mandatory = True
                ss_doc.insert(ignore_permissions=True, ignore_links=True)
                ss_count += 1
            except Exception as e:
                if ss_count < 2:
                    print(f"  StudentScholarship {sid}: {str(e)[:80]}")

        # ── Assessment Results ────────────────────────────────────────────────
        enrolled_courses = frappe.get_all(
            "Course Enrollment", filters={"student": sid}, pluck="course", limit=4
        )
        any_assessment_plan = frappe.db.get_value("Assessment Plan", {}, "name")
        for j, cid in enumerate(enrolled_courses[:4]):
            if frappe.db.exists("Assessment Result", {"student": sid, "course": cid}):
                ar_count += 1
                sr_count += 1
                continue
            try:
                m = random.uniform(65.0, 95.0)
                ar_doc = frappe.get_doc({
                    "doctype": "Assessment Result",
                    "assessment_plan": any_assessment_plan,
                    "student": sid,
                    "student_name": sname,
                    "course": cid,
                    "academic_year": ay,
                    "academic_term": at,
                    "total_score": round(m, 2),
                    "maximum_score": 100,
                    "grade": "O" if m >= 90 else ("A+" if m >= 85 else ("A" if m >= 75 else "B+")),
                    "custom_percentage": round(m, 2),
                })
                ar_doc.flags.ignore_mandatory = True
                ar_doc.flags.ignore_validate = True
                ar_doc.insert(ignore_permissions=True, ignore_links=True)
                ar_count += 1
                sr_count += 1
            except Exception as e:
                if ar_count < 2:
                    print(f"  AssessmentResult {sid}: {str(e)[:80]}")

        # ── Notification Preference ────────────────────────────────────────────
        # user field is Link→User; email is the User name (frappe uses email as user name)
        if frappe.db.exists("User", email) and not frappe.db.exists("Notification Preference", {"user": email}):
            try:
                frappe.get_doc({
                    "doctype": "Notification Preference",
                    "user": email,
                    "enabled": 1,
                    "email_enabled": 1,
                    "sms_enabled": 1,
                    "push_enabled": 1,
                    "whatsapp_enabled": 0,
                    "in_app_enabled": 1,
                }).insert(ignore_permissions=True, ignore_links=True)
                np_count += 1
            except Exception as e:
                if np_count < 2:
                    print(f"  NotificationPreference {email}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Transport Trip Logs (50) ──────────────────────────────────────────────
    routes = frappe.get_all("Transport Route", pluck="name", limit=4)
    vehicles = frappe.get_all("Transport Vehicle", pluck="name", limit=4)
    for i in range(50):
        log_date = add_days(nowdate(), -(i % 25))
        direction = "Morning" if i % 2 == 0 else "Evening"
        try:
            if frappe.db.exists("Transport Trip Log", {
                "trip_date": log_date, "direction": direction
            }):
                tt_count += 1
                continue
            route = routes[i % len(routes)] if routes else None
            vehicle = vehicles[i % len(vehicles)] if vehicles else None
            frappe.get_doc({
                "doctype": "Transport Trip Log",
                "trip_date": log_date,
                "direction": direction,
                "route": route,
                "vehicle": vehicle,
                "departure_time": "08:00:00" if direction == "Morning" else "17:00:00",
                "arrival_time": "09:00:00" if direction == "Morning" else "18:00:00",
                "passenger_count": random.randint(20, 45),
                "status": "Completed",
            }).insert(ignore_permissions=True, ignore_links=True)
            tt_count += 1
        except Exception as e:
            if tt_count < 2:
                print(f"  TransportTripLog: {str(e)[:80]}")
            if tt_count > 50:
                break

    frappe.db.commit()

    # ── Course Schedules (today + 4 days for portal students) ────────────────
    instr_list = frappe.get_all("Instructor", pluck="name", limit=5)
    rooms_list = frappe.get_all("Room", pluck="name", limit=5)
    for ps_idx, (sid, sname, prog_id, email) in enumerate(portal_students):
        enrolled_courses = frappe.get_all(
            "Course Enrollment", filters={"student": sid}, pluck="course", limit=5
        )
        sg = frappe.db.get_value("Student Group", {"program": prog_id}, "name") or (
            student_groups[ps_idx % len(student_groups)] if student_groups else None
        )
        for day_offset in range(5):
            sched_date = add_days(nowdate(), day_offset)
            for c_idx, cid in enumerate(enrolled_courses[:5]):
                if frappe.db.exists("Course Schedule", {
                    "course": cid, "schedule_date": sched_date,
                    "student_group": sg
                }):
                    cs_count += 1
                    continue
                try:
                    instr = instr_list[c_idx % len(instr_list)] if instr_list else None
                    room = rooms_list[c_idx % len(rooms_list)] if rooms_list else None
                    from_h = 8 + c_idx
                    to_h = from_h + 1
                    cs_doc = frappe.get_doc({
                        "doctype": "Course Schedule",
                        "course": cid,
                        "student_group": sg,
                        "instructor": instr,
                        "room": room,
                        "schedule_date": sched_date,
                        "from_time": f"{from_h:02d}:00:00",
                        "to_time": f"{to_h:02d}:00:00",
                        "academic_year": ay,
                        "academic_term": at,
                    })
                    cs_doc.flags.ignore_mandatory = True
                    cs_doc.flags.ignore_validate = True
                    cs_doc.insert(ignore_permissions=True, ignore_links=True)
                    cs_count += 1
                except Exception as e:
                    if cs_count < 2:
                        print(f"  CourseSchedule {cid}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Announcements (4) ─────────────────────────────────────────────────────
    ann_list = [
        ("Examination Committee Notice", "End-semester examinations start from next week. All students must carry their hall tickets."),
        ("Library Extended Hours", "Library will remain open till 10 PM during examination period."),
        ("Placement Drive — TCS", "TCS placement drive on 15th May. Register on the placement portal before 10th May."),
        ("Holiday Notice — Eid", "The institute will remain closed on account of Eid Al-Fitr."),
    ]
    for ann_title, ann_body in ann_list:
        if frappe.db.exists("Announcement", {"title": ann_title}):
            ann_count += 1
            continue
        try:
            ann_doc = frappe.get_doc({
                "doctype": "Announcement",
                "title": ann_title,
                "description": ann_body,
                "publish_date": add_days(nowdate(), -2),
                "expiry_date": add_days(nowdate(), 30),
                "for_students": 1,
                "for_faculty": 1,
            })
            ann_doc.flags.ignore_mandatory = True
            ann_doc.insert(ignore_permissions=True, ignore_links=True)
            ann_count += 1
        except Exception as e:
            if ann_count < 2:
                print(f"  Announcement {ann_title}: {str(e)[:80]}")

    # ── Subject-wise Attendance back-fill (30 days × 5 courses × 5 students) ─
    student_groups = frappe.get_all(
        "Student Group", pluck="name", limit=10
    )
    for ps_idx, (sid, sname, prog_id, email) in enumerate(portal_students):
        enrolled_courses = frappe.get_all(
            "Course Enrollment", filters={"student": sid}, pluck="course", limit=5
        )
        sg = student_groups[ps_idx % len(student_groups)] if student_groups else None
        for cid in enrolled_courses[:5]:
            for day_offset in range(30):
                att_date = add_days(nowdate(), -(day_offset + 1))
                if frappe.db.exists("Student Attendance", {
                    "student": sid, "date": att_date, "course": cid
                }):
                    att_count += 1
                    continue
                try:
                    sa_doc = frappe.get_doc({
                        "doctype": "Student Attendance",
                        "student": sid,
                        "date": att_date,
                        "student_group": sg,
                        "course": cid,
                        "status": "Present" if random.random() < 0.88 else "Absent",
                    })
                    sa_doc.flags.ignore_mandatory = True
                    sa_doc.flags.ignore_validate = True
                    sa_doc.insert(ignore_permissions=True, ignore_links=True)
                    att_count += 1
                except Exception as e:
                    if att_count < 2:
                        print(f"  StudentAttendance {sid}: {str(e)[:80]}")
                    break

    frappe.db.commit()
    print(
        f"  StudentStatusLog: {sl_count}, StudentResume: {res_count}, "
        f"PlacementProfile: {pp_count}, CourseRegistration: {cr_count}, "
        f"HostelAttendance: {ha_count}, HostelVisitor: {hv_count}, "
        f"HostelMaintReq: {hmr_count}, LibraryTxn: {lt_count}, "
        f"BookReservation: {br_count}, LibFine: {lf_count}, "
        f"TransportTripLog: {tt_count}, StudentScholarship: {ss_count}, "
        f"StudentResult: {sr_count}, AssessmentResult: {ar_count}, "
        f"NotifPref: {np_count}, CourseSchedule: {cs_count}, "
        f"Announcement: {ann_count}, StudentAttendance(portal): {att_count}"
    )


# === Layer 11g — Alumni / Workload / Teaching Assignment =====================

def _seed_alumni_portals_v2(ctx):
    """Alumni, University Alumni, Alumni Event, Alumni Event Registration,
    Workload Distributor, Teaching Assignment, Timetable Slot,
    Elective Course Group, Grievance Committee, Job Posting.
    """
    yr = "2026"
    ay = ctx.get("academic_year", "2026-2027")
    at = ctx.get("academic_term", "")
    students = ctx.get("students", [])
    programs = ctx.get("programs", [])
    courses = ctx.get("courses", [])
    company = COMPANY

    alum_count = ua_count = ae_count = aer_count = 0
    wd_count = ta_count = ts_count = ecg_count = gc_count = jp_count = 0

    # ── Alumni (30) ───────────────────────────────────────────────────────────
    # Fields: student, student_name, user, email, batch, program(→Program),
    #         graduation_year, degree, department, current_company, designation,
    #         industry, city, country, linkedin_profile, github_profile
    alumni_ids = []
    companies = ["TCS", "Infosys", "Wipro", "HCL Technologies",
                 "Tech Mahindra", "Cognizant", "L&T Technology",
                 "Samsung India", "Intel India", "Qualcomm India"]
    designations = ["Software Engineer", "Senior Engineer", "Data Scientist",
                    "Product Manager", "Research Analyst", "Systems Engineer"]
    for i, stu in enumerate(students[:30]):
        sid = stu[0] if isinstance(stu, tuple) else stu
        sname = stu[1] if isinstance(stu, tuple) and len(stu) > 1 else sid
        prog = stu[2] if isinstance(stu, tuple) and len(stu) > 2 else None
        if frappe.db.exists("Alumni", {"student": sid}):
            existing = frappe.db.get_value("Alumni", {"student": sid}, "name")
            alumni_ids.append(existing)
            alum_count += 1
            continue
        try:
            alum_doc = frappe.get_doc({
                "doctype": "Alumni",
                "student": sid,
                "student_name": sname,
                "program": prog,
                "graduation_year": str(random.randint(2020, 2025)),
                "current_company": companies[i % len(companies)],
                "designation": designations[i % len(designations)],
                "industry": "Information Technology",
                "linkedin_profile": f"https://linkedin.com/in/{sname.lower().replace(' ', '-')}",
                "email": f"alumni{i+1}@example.com",
                "city": "Bengaluru",
                "country": "India",
            })
            alum_doc.flags.ignore_mandatory = True
            alum_doc.insert(ignore_permissions=True, ignore_links=True)
            alumni_ids.append(alum_doc.name)
            alum_count += 1
        except Exception as e:
            if alum_count < 2:
                print(f"  Alumni {sid}: {str(e)[:80]}")
            alumni_ids.append(None)

    # ── University Alumni (30) ────────────────────────────────────────────────
    # Fields: student, student_name, email, program(→Program), graduation_year,
    #         current_employer, designation, industry, location,
    #         willing_to_mentor, available_for_placement, linkedin_profile
    for i, stu in enumerate(students[:30]):
        sid = stu[0] if isinstance(stu, tuple) else stu
        sname = stu[1] if isinstance(stu, tuple) and len(stu) > 1 else sid
        prog = stu[2] if isinstance(stu, tuple) and len(stu) > 2 else None
        email_addr = stu[6] if isinstance(stu, tuple) and len(stu) > 6 else f"alumni{i+1}@nit.edu"
        if frappe.db.exists("University Alumni", {"student": sid}):
            ua_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "University Alumni",
                "student": sid,
                "student_name": sname,
                "email": email_addr,
                "program": prog,
                "graduation_year": str(random.randint(2020, 2025)),
                "current_employer": companies[i % len(companies)],
                "designation": designations[i % len(designations)],
                "industry": "Information Technology",
                "location": "Bengaluru, India",
                "willing_to_mentor": 1,
                "available_for_placement": 0,
            }).insert(ignore_permissions=True, ignore_links=True)
            ua_count += 1
        except Exception as e:
            if ua_count < 2:
                print(f"  UniversityAlumni {sid}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Alumni Events (4) ─────────────────────────────────────────────────────
    events_data = [
        ("Annual Alumni Reunion 2026", add_days(nowdate(), 45), "Main Auditorium"),
        ("Tech Talk — Industry Trends", add_days(nowdate(), 20), "Seminar Hall A"),
        ("Career Workshop 2026", add_days(nowdate(), 30), "Conference Room"),
        ("Cultural Night 2026", add_days(nowdate(), 60), "Open Air Theatre"),
    ]
    event_names = []
    for ev_title, ev_date, ev_venue in events_data:
        if frappe.db.exists("Alumni Event", {"event_title": ev_title}):
            existing = frappe.db.get_value("Alumni Event", {"event_title": ev_title}, "name")
            event_names.append(existing)
            ae_count += 1
            continue
        try:
            ev_doc = frappe.get_doc({
                "doctype": "Alumni Event",
                "event_title": ev_title,
                "event_date": ev_date,
                "venue": ev_venue,
                "status": "Open",
                "description": f"{ev_title} — Join fellow alumni for networking and fun.",
            })
            ev_doc.flags.ignore_mandatory = True
            ev_doc.insert(ignore_permissions=True, ignore_links=True)
            event_names.append(ev_doc.name)
            ae_count += 1
        except Exception as e:
            if ae_count < 2:
                print(f"  AlumniEvent {ev_title}: {str(e)[:80]}")
            event_names.append(None)

    # ── Alumni Event Registrations (80 = 20 per event) ────────────────────────
    valid_alumni = [a for a in alumni_ids if a]
    for ev_name in event_names[:4]:
        if not ev_name:
            continue
        for j in range(20):
            alum = valid_alumni[j % len(valid_alumni)] if valid_alumni else None
            if not alum:
                continue
            if frappe.db.exists("Alumni Event Registration", {
                "event": ev_name, "alumni": alum
            }):
                aer_count += 1
                continue
            try:
                frappe.get_doc({
                    "doctype": "Alumni Event Registration",
                    "event": ev_name,
                    "alumni": alum,
                    "registration_date": add_days(nowdate(), -random.randint(1, 10)),
                    "status": "Confirmed",
                }).insert(ignore_permissions=True, ignore_links=True)
                aer_count += 1
            except Exception as e:
                if aer_count < 2:
                    print(f"  AlumniEventRegistration: {str(e)[:80]}")

    frappe.db.commit()

    # ── Timetable Slots (8) ───────────────────────────────────────────────────
    slot_data = [
        ("09:00-10:00", "09:00:00", "10:00:00"),
        ("10:00-11:00", "10:00:00", "11:00:00"),
        ("11:00-12:00", "11:00:00", "12:00:00"),
        ("12:00-13:00", "12:00:00", "13:00:00"),
        ("14:00-15:00", "14:00:00", "15:00:00"),
        ("15:00-16:00", "15:00:00", "16:00:00"),
        ("16:00-17:00", "16:00:00", "17:00:00"),
        ("17:00-18:00", "17:00:00", "18:00:00"),
    ]
    for slot_name, from_t, to_t in slot_data:
        if frappe.db.exists("Timetable Slot", {"slot_name": slot_name}):
            ts_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Timetable Slot",
                "slot_name": slot_name,
                "from_time": from_t,
                "to_time": to_t,
                "is_active": 1,
            }).insert(ignore_permissions=True, ignore_links=True)
            ts_count += 1
        except Exception as e:
            if ts_count < 2:
                print(f"  TimetableSlot {slot_name}: {str(e)[:80]}")

    # ── Workload Distributors (8, one per program) ────────────────────────────
    instructors = frappe.get_all("Instructor", pluck="name", limit=8)
    for i, prog in enumerate(programs[:8]):
        pname = prog[0] if isinstance(prog, tuple) else prog
        if frappe.db.exists("Workload Distributor", {"program": pname, "academic_year": ay}):
            wd_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Workload Distributor",
                "program": pname,
                "academic_year": ay,
                "academic_term": at,
                "total_credit_hours": random.randint(20, 30),
                "status": "Approved",
            }).insert(ignore_permissions=True, ignore_links=True)
            wd_count += 1
        except Exception as e:
            if wd_count < 2:
                print(f"  WorkloadDistributor {pname}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Teaching Assignments (30) ─────────────────────────────────────────────
    # Fields: instructor(→Employee), course, academic_term, teaching_type,
    #         weekly_hours, is_active, academic_year, assignment_status,
    #         lecture_hours, tutorial_hours
    ta_instructors = frappe.get_all("Employee", pluck="name", limit=10)
    all_prog_names = [p[0] if isinstance(p, tuple) else p for p in programs]

    for i, course_entry in enumerate(courses[:30]):
        cid = course_entry[0] if isinstance(course_entry, tuple) else course_entry
        instr = ta_instructors[i % len(ta_instructors)] if ta_instructors else None
        prog_for_ta = all_prog_names[i % len(all_prog_names)] if all_prog_names else None
        if frappe.db.exists("Teaching Assignment", {
            "course": cid, "academic_year": ay, "academic_term": at
        }):
            ta_count += 1
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Teaching Assignment",
                "instructor": instr,
                "course": cid,
                "program": prog_for_ta,
                "academic_year": ay,
                "academic_term": at,
                "lecture_hours": random.randint(2, 4),
                "tutorial_hours": 1,
                "practical_hours": 0,
                "assignment_status": "Approved",
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            ta_count += 1
        except Exception as e:
            if ta_count < 2:
                print(f"  TeachingAssignment {cid}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Elective Course Groups (4) ────────────────────────────────────────────
    elective_groups = [
        ("CSE Open Electives", "BTCSE"),
        ("ECE Elective Group A", "BTECE"),
        ("Management Electives MBA", "MBA"),
        ("ME Advanced Electives", "BTME"),
    ]
    for eg_name, prog_abbr in elective_groups:
        if frappe.db.exists("Elective Course Group", {"group_name": eg_name}):
            ecg_count += 1
            continue
        try:
            prog = frappe.db.get_value("Program", {"program_abbreviation": prog_abbr}, "name")
            group_courses = [
                {"course": c[0] if isinstance(c, tuple) else c}
                for c in courses[ecg_count*4: ecg_count*4+4]
                if frappe.db.exists("Course", c[0] if isinstance(c, tuple) else c)
            ]
            doc = frappe.get_doc({
                "doctype": "Elective Course Group",
                "group_name": eg_name,
                "program": prog,
                "academic_year": ay,
                "academic_term": at,
                "courses": group_courses,
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            ecg_count += 1
        except Exception as e:
            if ecg_count < 2:
                print(f"  ElectiveCourseGroup {eg_name}: {str(e)[:80]}")

    # ── Grievance Committees (4) ──────────────────────────────────────────────
    # Fields: committee_name, committee_type, description, is_active,
    #         meeting_frequency, chairperson, secretary, email, phone
    gc_types = [
        ("Academic", "General Grievance"),
        ("Hostel", "Anti-Ragging"),
        ("Library", "General Grievance"),
        ("Examination", "Academic Appeals"),
    ]
    ta_instructors_gc = frappe.get_all("Employee", pluck="name", limit=5)
    for gc_cat, gc_type in gc_types:
        committee_name = f"{gc_cat} Grievance Committee"
        if frappe.db.exists("Grievance Committee", {"committee_name": committee_name}):
            gc_count += 1
            continue
        try:
            chair = ta_instructors_gc[0] if ta_instructors_gc else None
            secretary = ta_instructors_gc[1] if len(ta_instructors_gc) > 1 else None
            frappe.get_doc({
                "doctype": "Grievance Committee",
                "committee_name": committee_name,
                "committee_type": gc_type,
                "chairperson": chair,
                "secretary": secretary,
                "is_active": 1,
                "meeting_frequency": "Monthly",
                "email": f"grievance.{gc_cat.lower()}@nit.edu",
            }).insert(ignore_permissions=True, ignore_links=True)
            gc_count += 1
        except Exception as e:
            if gc_count < 2:
                print(f"  GrievanceCommittee {gc_cat}: {str(e)[:80]}")

    # ── Job Postings (12) ─────────────────────────────────────────────────────
    jp_companies = [
        "TCS", "Infosys", "Wipro", "HCL Technologies",
        "Tech Mahindra", "Cognizant", "Google India", "Microsoft India",
        "Amazon India", "Flipkart", "Zomato", "ISRO",
    ]
    for i, jp_comp in enumerate(jp_companies[:12]):
        jp_name = f"JP-{yr}-{i+1:05d}"
        if frappe.db.exists("Job Posting", jp_name):
            jp_count += 1
            continue
        try:
            target_progs = [p[0] for p in programs[:4]] if programs else []
            frappe.get_doc({
                "doctype": "Job Posting",
                "name": jp_name,
                "company": jp_comp,
                "job_title": random.choice([
                    "Software Engineer", "Data Engineer", "ML Engineer",
                    "Systems Engineer", "DevOps Engineer", "Product Manager"
                ]),
                "description": f"{jp_comp} is hiring for {yr} batch. Package: ₹{random.randint(8, 25)} LPA.",
                "last_date": add_days(nowdate(), random.randint(10, 60)),
                "posted_on": add_days(nowdate(), -random.randint(1, 10)),
                "status": "Open",
                "programs": [{"program": p} for p in target_progs],
            }).insert(ignore_permissions=True, ignore_links=True)
            jp_count += 1
        except Exception as e:
            if jp_count < 2:
                print(f"  JobPosting {jp_name}: {str(e)[:80]}")

    frappe.db.commit()
    print(
        f"  Alumni: {alum_count}, UniversityAlumni: {ua_count}, "
        f"AlumniEvent: {ae_count}, AlumniEventReg: {aer_count}, "
        f"WorkloadDistrib: {wd_count}, TeachingAssignment: {ta_count}, "
        f"TimetableSlot: {ts_count}, ElectiveCourseGroup: {ecg_count}, "
        f"GrievanceCommittee: {gc_count}, JobPosting: {jp_count}"
    )


# === Layer 11h — Analytics / KPI / LMS deeper ================================

def _seed_analytics_v2(ctx):
    """Custom Dashboard, KPI Definition, KPI Value, Scheduled Report,
    LMS Assignment, LMS Quiz, LMS Discussion, Quiz Attempt,
    Assignment Submission, Discussion Reply, Placement Profile (bulk).
    """
    yr = "2026"
    ay = ctx.get("academic_year", "2026-2027")
    at = ctx.get("academic_term", "")
    students = ctx.get("students", [])
    courses = ctx.get("courses", [])

    cd_count = kd_count = kv_count = sched_count = 0
    la_count = lq_count = ld_count = qa_count = asub_count = dr_count = pp_count = 0

    # ── KPI Definitions (8) ───────────────────────────────────────────────────
    # Fields: kpi_name, kpi_code(unique), category, description, unit,
    #         tracking_frequency, is_active, target_value, higher_is_better
    kpi_list = [
        ("AVG-ATT", "Average Attendance", "Academic", "%", 80),
        ("PASS-PCT", "Pass Percentage", "Academic", "%", 75),
        ("PLACE-PCT", "Placement Percentage", "Placement", "%", 70),
        ("LIB-UTIL", "Library Utilization", "Student Services", "books/student", 4),
        ("FEE-COLL", "Fee Collection Rate", "Financial", "%", 95),
        ("HST-OCC", "Hostel Occupancy Rate", "Infrastructure", "%", 85),
        ("RES-PUB", "Research Publications", "Research", "count", 10),
        ("LMS-COMP", "Course Completion Rate", "Academic", "%", 65),
    ]
    kpi_names = []
    for kpi_code, kpi_name, kpi_cat, unit, target_val in kpi_list:
        # Check by name first (may exist from a prior run with different kpi_code)
        existing_name = frappe.db.get_value("KPI Definition", {"kpi_name": kpi_name}, "name")
        if existing_name:
            # Update category if it was empty
            if not frappe.db.get_value("KPI Definition", existing_name, "category"):
                frappe.db.set_value("KPI Definition", existing_name, "category", kpi_cat)
            kpi_names.append(existing_name)
            kd_count += 1
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "KPI Definition",
                "kpi_name": kpi_name,
                "kpi_code": kpi_code,
                "category": kpi_cat,
                "unit": unit,
                "description": f"{kpi_name} tracking KPI",
                "tracking_frequency": "Monthly",
                "is_active": 1,
                "target_value": target_val,
                "higher_is_better": 1,
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True, ignore_links=True)
            kpi_names.append(doc.name)
            kd_count += 1
        except Exception as e:
            if kd_count < 2:
                print(f"  KPIDefinition {kpi_name}: {str(e)[:80]}")
            kpi_names.append(None)

    # ── KPI Values (24 = 3 months × 8 KPIs) ──────────────────────────────────
    # Fields: kpi(→KPI Definition), period_type, period_start, period_end,
    #         value, target, variance, status, academic_year, calculated_on
    for month_offset in range(3):
        period_start = add_days(nowdate(), -(month_offset * 30 + 29))
        period_end = add_days(nowdate(), -(month_offset * 30))
        for kpi_ref in kpi_names:
            if not kpi_ref:
                continue
            if frappe.db.exists("KPI Value", {
                "kpi": kpi_ref, "period_start": period_start
            }):
                kv_count += 1
                continue
            try:
                val = round(random.uniform(65.0, 95.0), 2)
                tgt = frappe.db.get_value("KPI Definition", kpi_ref, "target_value") or 75
                frappe.get_doc({
                    "doctype": "KPI Value",
                    "kpi": kpi_ref,
                    "period_type": "Monthly",
                    "period_start": period_start,
                    "period_end": period_end,
                    "value": val,
                    "target": tgt,
                    "variance": round(val - tgt, 2),
                    "status": "On Track" if val >= tgt else "Below Target",
                    "academic_year": ay,
                    "calculated_on": nowdate(),
                }).insert(ignore_permissions=True, ignore_links=True)
                kv_count += 1
            except Exception as e:
                if kv_count < 2:
                    print(f"  KPIValue {kpi_ref}: {str(e)[:80]}")

    # ── Custom Dashboards (4) ─────────────────────────────────────────────────
    # Fields: dashboard_name, dashboard_type, description, is_public, is_active
    dashboards = [
        ("Faculty Workload Dashboard", "Faculty"),
        ("Hostel Occupancy Dashboard", "Student"),
        ("Fee Collection Dashboard", "Financial"),
        ("Placement Pipeline Dashboard", "Executive"),
    ]
    for db_name, db_type in dashboards:
        if frappe.db.exists("Custom Dashboard", {"dashboard_name": db_name}):
            cd_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Custom Dashboard",
                "dashboard_name": db_name,
                "dashboard_type": db_type,
                "is_public": 1,
                "is_active": 1,
                "description": f"{db_name} for admin users.",
            }).insert(ignore_permissions=True, ignore_links=True)
            cd_count += 1
        except Exception as e:
            if cd_count < 2:
                print(f"  CustomDashboard {db_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Scheduled Reports (4) ─────────────────────────────────────────────────
    # Fields: report_name, report, description, is_enabled, output_format,
    #         frequency, day_of_week, day_of_month, time_of_day, delivery_method
    scheduled_reports = [
        ("Daily Fee Collection", "Fee Collection Summary", "Daily", None, None),
        ("Weekly Placement Update", "Placement Statistics", "Weekly", "Monday", None),
        ("Monthly Attendance Report", "Student Attendance", "Monthly", None, 1),
        ("Monthly Library Report", "Library Circulation", "Monthly", None, 5),
    ]
    for sr_name, report_name, freq, dow, dom in scheduled_reports:
        if frappe.db.exists("Scheduled Report", {"report_name": sr_name}):
            sched_count += 1
            continue
        try:
            report_ref = frappe.db.get_value("Report", report_name, "name")
            doc_data = {
                "doctype": "Scheduled Report",
                "report_name": sr_name,
                "report": report_ref,
                "frequency": freq,
                "is_enabled": 1,
                "output_format": "PDF",
                "delivery_method": "File Storage",
                "time_of_day": "08:00:00",
            }
            if dow:
                doc_data["day_of_week"] = dow
            if dom:
                doc_data["day_of_month"] = dom
            frappe.get_doc(doc_data).insert(ignore_permissions=True, ignore_links=True)
            sched_count += 1
        except Exception as e:
            if sched_count < 2:
                print(f"  ScheduledReport {sr_name}: {str(e)[:80]}")

    # ── LMS Assignments (12) ──────────────────────────────────────────────────
    lms_courses = frappe.get_all("LMS Course", pluck="name", limit=10)
    la_names = []
    for i, lc in enumerate(lms_courses):
        for j in range(1, 3):
            if i * 2 + j > 12:
                break
            la_name = f"LA-{yr}-{i*2+j:05d}"
            if frappe.db.exists("LMS Assignment", la_name):
                la_names.append(la_name)
                la_count += 1
                continue
            try:
                now_dt = now_datetime() if hasattr(frappe.utils, "now_datetime") else frappe.utils.now()
                due_dt = frappe.utils.add_days(frappe.utils.now(), random.randint(7, 30))
                la_doc = frappe.get_doc({
                    "doctype": "LMS Assignment",
                    "name": la_name,
                    "lms_course": lc,
                    "title": f"Assignment {j} for {lc}",
                    "instructions": f"Complete the exercises as described in Chapter {j}.",
                    "available_from": frappe.utils.now(),
                    "due_date": due_dt,
                    "max_marks": 20,
                })
                la_doc.flags.name_set = True
                la_doc.flags.ignore_mandatory = True
                la_doc.flags.ignore_validate = True
                la_doc.insert(ignore_permissions=True, ignore_links=True)
                la_names.append(la_name)
                la_count += 1
            except Exception as e:
                if la_count < 2:
                    print(f"  LMSAssignment {la_name}: {str(e)[:80]}")
                la_names.append(None)

    # ── LMS Quizzes (8) ───────────────────────────────────────────────────────
    # Fields: title, lms_course, module, quiz_type, total_marks, passing_marks,
    #         time_limit_minutes, max_attempts, shuffle_questions
    lq_names = []
    for i, lc in enumerate(lms_courses[:8]):
        lq_name = f"LQ-{yr}-{i+1:05d}"
        if frappe.db.exists("LMS Quiz", lq_name):
            lq_names.append(lq_name)
            lq_count += 1
            continue
        try:
            lq_doc = frappe.get_doc({
                "doctype": "LMS Quiz",
                "name": lq_name,
                "title": f"Quiz {i+1} — Module Assessment",
                "lms_course": lc,
                "quiz_type": "Graded",
                "total_marks": 20,
                "passing_marks": 12,
                "time_limit_minutes": 30,
                "max_attempts": 3,
                "shuffle_questions": 1,
                "show_correct_answers": 1,
                "show_score_immediately": 1,
            })
            lq_doc.flags.name_set = True
            lq_doc.flags.ignore_mandatory = True
            lq_doc.flags.ignore_validate = True
            lq_doc.insert(ignore_permissions=True, ignore_links=True)
            lq_names.append(lq_name)
            lq_count += 1
        except Exception as e:
            if lq_count < 2:
                print(f"  LMSQuiz {lq_name}: {str(e)[:80]}")
            lq_names.append(None)

    # ── LMS Discussions (16) ─────────────────────────────────────────────────
    # Fields: lms_course, title, created_by_type, student, instructor,
    #         is_pinned, is_locked, content, reply_count, view_count
    ld_names = []
    for i, lc in enumerate(lms_courses[:8]):
        for j in range(2):
            ld_name = f"LD-{yr}-{i*2+j+1:05d}"
            if frappe.db.exists("LMS Discussion", ld_name):
                ld_names.append(ld_name)
                ld_count += 1
                continue
            try:
                ld_doc = frappe.get_doc({
                    "doctype": "LMS Discussion",
                    "name": ld_name,
                    "lms_course": lc,
                    "title": f"{'Concepts' if j == 0 else 'Questions'} — Module {i+1}",
                    "created_by_type": "Instructor",
                    "content": f"Discussion thread for {'concept clarity' if j == 0 else 'student queries'} on module {i+1}.",
                    "is_pinned": 1 if j == 0 else 0,
                    "is_locked": 0,
                    "reply_count": 0,
                    "view_count": random.randint(5, 30),
                })
                ld_doc.flags.name_set = True
                ld_doc.flags.ignore_mandatory = True
                ld_doc.flags.ignore_validate = True
                ld_doc.insert(ignore_permissions=True, ignore_links=True)
                ld_names.append(ld_name)
                ld_count += 1
            except Exception as e:
                if ld_count < 2:
                    print(f"  LMSDiscussion {ld_name}: {str(e)[:80]}")
                ld_names.append(None)

    frappe.db.commit()

    # ── Quiz Attempts (8, portal students) ────────────────────────────────────
    portal_emails = [f"student{k}@nit.edu" for k in range(1, 6)]
    portal_sids = [
        frappe.db.get_value("Student", {"student_email_id": e}, "name")
        for e in portal_emails
    ]
    portal_sids = [s for s in portal_sids if s]

    valid_lq = [n for n in lq_names if n]
    for i in range(8):
        if i >= len(valid_lq) or i >= len(portal_sids):
            break
        sid = portal_sids[i % len(portal_sids)]
        lq = valid_lq[i % len(valid_lq)]
        if frappe.db.exists("Quiz Attempt", {"student": sid, "quiz": lq}):
            qa_count += 1
            continue
        try:
            marks = round(random.uniform(12, 20), 1)
            frappe.get_doc({
                "doctype": "Quiz Attempt",
                "student": sid,
                "quiz": lq,
                "attempt_number": 1,
                "start_time": add_days(nowdate(), -random.randint(1, 15)),
                "end_time": add_days(nowdate(), -random.randint(1, 15)),
                "status": "Graded",
                "total_questions": 20,
                "attempted": 20,
                "correct": int(marks),
                "marks_obtained": marks,
                "total_marks": 20,
                "percentage": round(marks / 20 * 100, 1),
                "passed": 1 if marks >= 12 else 0,
            }).insert(ignore_permissions=True, ignore_links=True)
            qa_count += 1
        except Exception as e:
            if qa_count < 2:
                print(f"  QuizAttempt: {str(e)[:80]}")

    # ── Assignment Submissions (6, portal students) ───────────────────────────
    valid_la = [n for n in la_names if n]
    for i in range(6):
        if i >= len(valid_la) or i >= len(portal_sids):
            break
        sid = portal_sids[i % len(portal_sids)]
        la = valid_la[i % len(valid_la)]
        if frappe.db.exists("Assignment Submission", {"student": sid, "assignment": la}):
            asub_count += 1
            continue
        try:
            marks = random.randint(14, 20)
            asub_doc = frappe.get_doc({
                "doctype": "Assignment Submission",
                "student": sid,
                "assignment": la,
                "submission_date": add_days(nowdate(), -random.randint(1, 10)),
                "marks_obtained": marks,
                "final_marks": marks,
                "status": "Graded",
                "submission_text": "Completed assignment as per instructions.",
            })
            asub_doc.flags.ignore_mandatory = True
            asub_doc.flags.ignore_validate = True
            asub_doc.insert(ignore_permissions=True, ignore_links=True)
            asub_count += 1
        except Exception as e:
            if asub_count < 2:
                print(f"  AssignmentSubmission: {str(e)[:80]}")

    # ── Discussion Replies (6, portal students) ───────────────────────────────
    valid_ld = [n for n in ld_names if n]
    for i in range(6):
        if i >= len(valid_ld) or i >= len(portal_sids):
            break
        sid = portal_sids[i % len(portal_sids)]
        ld = valid_ld[i % len(valid_ld)]
        try:
            frappe.get_doc({
                "doctype": "Discussion Reply",
                "discussion": ld,
                "student": sid,
                "reply_by_type": "Student",
                "reply_content": f"Great point! I think the concept relates to what we studied in Chapter {i+1}.",
                "reply_date": add_days(nowdate(), -random.randint(1, 10)),
                "upvotes": random.randint(0, 5),
            }).insert(ignore_permissions=True, ignore_links=True)
            dr_count += 1
        except Exception as e:
            if dr_count < 2:
                print(f"  DiscussionReply: {str(e)[:80]}")

    frappe.db.commit()

    # ── Placement Profiles (bulk, first 50 students) ──────────────────────────
    for i, stu in enumerate(students[:50]):
        sid = stu[0] if isinstance(stu, tuple) else stu
        sname = stu[1] if isinstance(stu, tuple) and len(stu) > 1 else sid
        prog_id = stu[2] if isinstance(stu, tuple) and len(stu) > 2 else "BTCSE"
        if frappe.db.exists("Placement Profile", {"student": sid}):
            pp_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Placement Profile",
                "student": sid,
                "student_name": sname,
                "program": prog_id,
                "cgpa": round(random.uniform(6.5, 9.5), 2),
                "tenth_percentage": round(random.uniform(75.0, 97.0), 2),
                "twelfth_percentage": round(random.uniform(72.0, 95.0), 2),
                "backlogs": random.choice([0, 0, 0, 1]),
                "is_placed": random.choice([0, 0, 1]),
                "status": "Active",
            }).insert(ignore_permissions=True, ignore_links=True)
            pp_count += 1
        except Exception as e:
            if pp_count < 2:
                print(f"  PlacementProfile bulk {sid}: {str(e)[:80]}")

    frappe.db.commit()
    print(
        f"  KPIDef: {kd_count}, KPIValue: {kv_count}, CustomDashboard: {cd_count}, "
        f"ScheduledReport: {sched_count}, LMSAssignment: {la_count}, "
        f"LMSQuiz: {lq_count}, LMSDiscussion: {ld_count}, "
        f"QuizAttempt: {qa_count}, AssignmentSub: {asub_count}, "
        f"DiscussionReply: {dr_count}, PlacementProfile(bulk): {pp_count}"
    )


# === Layer 11i — Remaining empty doctypes ====================================

def _seed_remaining_v2(ctx):
    """Seed remaining empty doctypes:
    Custom Report Definition, DigiLocker Issued Document, Email Queue Extended,
    Emergency Acknowledgment, Fee Category, Fee Refund, Hostel Bulk Attendance,
    Mess Menu, Notice View Log, Payment Webhook Log, Research Grant,
    Student Feedback, Temporary Teaching Assignment, University Announcement.
    """
    yr = "2026"
    ay = ctx.get("academic_year", "2026-2027")
    at = ctx.get("academic_term", "")
    students = ctx.get("students", [])
    courses = ctx.get("courses", [])
    programs = ctx.get("programs", [])

    crd_count = dgl_count = eqe_count = ea_count = fc_count = fr_count = 0
    hba_count = mm_count = nvl_count = pwh_count = rg_count = sf_count = 0
    tta_count = ua_count = 0

    # ── Custom Report Definitions (4) ─────────────────────────────────────────
    # columns child table (Report Column Definition) is required
    crd_defs = [
        ("Faculty Workload Report", "Tabular", "Teaching Assignment"),
        ("Hostel Occupancy Summary", "Tabular", "Hostel Allocation"),
        ("Fee Collection Analysis", "Tabular", "Student"),
        ("Placement Pipeline View", "Tabular", "Placement Application"),
    ]
    for title, rtype, pdoc in crd_defs:
        if frappe.db.exists("Custom Report Definition", {"report_title": title}):
            crd_count += 1
            continue
        try:
            crd_doc = frappe.get_doc({
                "doctype": "Custom Report Definition",
                "report_title": title,
                "report_type": rtype,
                "primary_doctype": pdoc,
                "description": f"Custom report for {title}",
                "columns": [
                    {"field_name": "name", "label": "Name", "fieldtype": "Data", "width": 150},
                ],
            })
            crd_doc.flags.ignore_mandatory = True
            crd_doc.flags.ignore_validate = True
            crd_doc.insert(ignore_permissions=True, ignore_links=True)
            crd_count += 1
        except Exception as e:
            if crd_count < 2:
                print(f"  CustomReportDef {title}: {str(e)[:80]}")

    # ── DigiLocker Issued Documents (5) ───────────────────────────────────────
    cert_requests = frappe.get_all("Certificate Request",
        filters={"status": "Issued"}, fields=["name", "student"], limit=5)
    for i, cr in enumerate(cert_requests[:5]):
        if frappe.db.exists("DigiLocker Issued Document", {"student": cr.student}):
            dgl_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "DigiLocker Issued Document",
                "student": cr.student,
                "document_type": ["Bonafide Certificate", "Transcript", "Degree Certificate",
                                  "Migration Certificate", "Character Certificate"][i % 5],
                "issued_date": frappe.utils.add_days(frappe.utils.nowdate(), -random.randint(1, 30)),
                "status": "Issued",
            }).insert(ignore_permissions=True, ignore_links=True)
            dgl_count += 1
        except Exception as e:
            if dgl_count < 2:
                print(f"  DigiLockerDoc: {str(e)[:80]}")

    frappe.db.commit()

    # ── Email Queue Extended (10) ─────────────────────────────────────────────
    portal_emails = ["student1@nit.edu", "student2@nit.edu", "student3@nit.edu",
                     "student4@nit.edu", "student5@nit.edu"]
    subjects = [
        "Hall Ticket Ready for Download",
        "Fee Payment Reminder",
        "Exam Results Published",
        "Library Book Due Date",
        "Placement Drive Announcement",
        "Holiday Notice",
        "Internal Assessment Marks",
        "Hostel Maintenance Update",
        "Scholarship Disbursement",
        "Course Registration Reminder",
    ]
    for i in range(10):
        try:
            frappe.get_doc({
                "doctype": "Email Queue Extended",
                "recipient": portal_emails[i % len(portal_emails)],
                "subject": subjects[i % len(subjects)],
                "message": f"Dear Student,\n\n{subjects[i % len(subjects)]}.\n\nRegards,\nNIT Administration",
                "status": "Sent" if i < 7 else "Pending",
                "sent_at": frappe.utils.add_days(frappe.utils.nowdate(), -random.randint(0, 30)) if i < 7 else None,
            }).insert(ignore_permissions=True, ignore_links=True)
            eqe_count += 1
        except Exception as e:
            if eqe_count < 2:
                print(f"  EmailQueueExtended: {str(e)[:80]}")
            if eqe_count > 10:
                break

    # ── Emergency Acknowledgments ─────────────────────────────────────────────
    alerts = frappe.get_all("Emergency Alert", pluck="name", limit=3)
    portal_users = [frappe.db.get_value("User", {"email": e}, "name") for e in portal_emails]
    portal_users = [u for u in portal_users if u]
    # status valid: Safe, Need Help, Evacuated, Sheltering, Not Present
    for i, alert in enumerate(alerts[:3]):
        user = portal_users[i % len(portal_users)] if portal_users else "Administrator"
        if frappe.db.exists("Emergency Acknowledgment", {"emergency_alert": alert, "user": user}):
            ea_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Emergency Acknowledgment",
                "emergency_alert": alert,
                "user": user,
                "acknowledged_at": frappe.utils.now(),
                "status": "Safe",
            }).insert(ignore_permissions=True, ignore_links=True)
            ea_count += 1
        except Exception as e:
            if ea_count < 2:
                print(f"  EmergencyAcknowledgment: {str(e)[:80]}")

    frappe.db.commit()

    # ── Fee Categories (5) ────────────────────────────────────────────────────
    fee_cats = [
        ("Tuition Fee", "TF-001", "Tuition"),
        ("Examination Fee", "EF-001", "Examination"),
        ("Hostel Fee", "HF-001", "Hostel"),
        ("Library Fee", "LF-001", "Library"),
        ("Transport Fee", "TRF-001", "Transport"),
    ]
    for cat_name, cat_code, fee_type in fee_cats:
        if frappe.db.exists("Fee Category", {"category_name": cat_name}):
            fc_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Fee Category",
                "category_name": cat_name,
                "category_code": cat_code,
                "fee_type": fee_type,
                "description": f"{cat_name} collected annually",
            }).insert(ignore_permissions=True, ignore_links=True)
            fc_count += 1
        except Exception as e:
            if fc_count < 2:
                print(f"  FeeCategory {cat_name}: {str(e)[:80]}")

    # ── Fee Refunds (3) ───────────────────────────────────────────────────────
    # fees is Link→Fees; use ignore_validate to bypass controller
    fees_docs = frappe.get_all("Fees", pluck="name", limit=3)
    for i, fees_name in enumerate(fees_docs[:3]):
        student = frappe.db.get_value("Fees", fees_name, "student")
        if not student:
            continue
        if frappe.db.exists("Fee Refund", {"fees": fees_name}):
            fr_count += 1
            continue
        try:
            fr_doc = frappe.get_doc({
                "doctype": "Fee Refund",
                "student": student,
                "fees": fees_name,
                "refund_date": frappe.utils.add_days(frappe.utils.nowdate(), -random.randint(5, 60)),
                "refund_reason": ["Excess Payment", "Scholarship Adjustment", "Medical Reason"][i % 3],
                "refund_amount": random.randint(5000, 25000),
                "payment_mode": ["Bank Transfer", "Online Refund", "UPI"][i % 3],
                "status": "Processed",
            })
            fr_doc.flags.ignore_mandatory = True
            fr_doc.flags.ignore_validate = True
            fr_doc.insert(ignore_permissions=True, ignore_links=True)
            fr_count += 1
        except Exception as e:
            if fr_count < 2:
                print(f"  FeeRefund: {str(e)[:80]}")

    frappe.db.commit()

    # ── Hostel Bulk Attendance (3) ─────────────────────────────────────────────
    buildings = frappe.get_all("Hostel Building", pluck="name", limit=2)
    for i, building in enumerate(buildings[:3]):
        att_date = frappe.utils.add_days(frappe.utils.nowdate(), -(i * 3 + 1))
        if frappe.db.exists("Hostel Bulk Attendance", {"attendance_date": att_date, "building": building}):
            hba_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Hostel Bulk Attendance",
                "attendance_date": att_date,
                "building": building,
                "attendance_type": ["Morning", "Evening", "Night"][i % 3],
                "attendance_records": [{"student": s[0] if isinstance(s, tuple) else s,
                                        "status": "Present"} for s in students[:5]],
            }).insert(ignore_permissions=True, ignore_links=True)
            hba_count += 1
        except Exception as e:
            if hba_count < 2:
                print(f"  HostelBulkAttendance: {str(e)[:80]}")

    # ── Mess Menus (2) ────────────────────────────────────────────────────────
    messes = frappe.get_all("Hostel Mess", pluck="name", limit=2)
    meal_types = ["Breakfast", "Lunch", "Dinner"]
    items_pool = [
        "Idli Sambar", "Dosa Chutney", "Paratha Curd", "Rice Dal",
        "Rajma Rice", "Chole Bhature", "Khichdi", "Biryani"
    ]
    for i, mess_name in enumerate(messes[:2]):
        # week_start_date must be a Monday; find the most recent Monday
        import datetime as _dt
        today_date = frappe.utils.getdate(frappe.utils.nowdate())
        days_since_monday = today_date.weekday()  # 0=Monday
        week_start = frappe.utils.add_days(
            frappe.utils.nowdate(), -days_since_monday - (i * 7)
        )
        if frappe.db.exists("Mess Menu", {"mess": mess_name, "week_start_date": week_start}):
            mm_count += 1
            continue
        try:
            # menu_items child has: day (Select reqd), meal_type (Select reqd), menu_items (Small Text reqd)
            meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks"]
            days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            menu_rows = []
            for j in range(7):
                for mt in ["Breakfast", "Lunch", "Dinner"]:
                    menu_rows.append({
                        "day": days_list[j],
                        "meal_type": mt,
                        "menu_items": items_pool[(i * 21 + j * 3 + meal_types.index(mt)) % len(items_pool)],
                    })
            mm_doc = frappe.get_doc({
                "doctype": "Mess Menu",
                "mess": mess_name,
                "week_start_date": week_start,
                "menu_items": menu_rows,
            })
            mm_doc.flags.ignore_mandatory = True
            mm_doc.flags.ignore_validate = True
            mm_doc.insert(ignore_permissions=True, ignore_links=True)
            mm_count += 1
        except Exception as e:
            if mm_count < 2:
                print(f"  MessMenu {mess_name}: {str(e)[:80]}")

    frappe.db.commit()

    # ── Notice View Logs ──────────────────────────────────────────────────────
    notices = frappe.get_all("Notice Board", pluck="name", limit=5)
    for i, notice in enumerate(notices[:5]):
        user = portal_users[i % len(portal_users)] if portal_users else "Administrator"
        if frappe.db.exists("Notice View Log", {"notice": notice, "user": user}):
            nvl_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Notice View Log",
                "notice": notice,
                "user": user,
                "viewed_at": frappe.utils.now(),
            }).insert(ignore_permissions=True, ignore_links=True)
            nvl_count += 1
        except Exception as e:
            if nvl_count < 2:
                print(f"  NoticeViewLog: {str(e)[:80]}")

    # ── Payment Webhook Logs (5) ──────────────────────────────────────────────
    gateways = ["Razorpay", "PayU", "Paytm"]
    for i in range(5):
        try:
            frappe.get_doc({
                "doctype": "Payment Webhook Log",
                "gateway": gateways[i % len(gateways)],
                "received_at": frappe.utils.now(),
                "payload": '{"event": "payment.captured", "amount": 50000}',
                "status": "Processed" if i < 4 else "Failed",
            }).insert(ignore_permissions=True, ignore_links=True)
            pwh_count += 1
        except Exception as e:
            if pwh_count < 2:
                print(f"  PaymentWebhookLog: {str(e)[:80]}")
            if pwh_count > 5:
                break

    frappe.db.commit()

    # ── Research Grants (4) ───────────────────────────────────────────────────
    # autoname=format:GRT-.YYYY.-.##### fails to generate unique names via ORM;
    # use raw SQL with explicit names instead.
    rg_grants = [
        ("GRT-2026-00001", f"Research Grant {yr} Project 1", f"DST / SERB {yr}", "Approved"),
        ("GRT-2026-00002", f"Research Grant {yr} Project 2", f"UGC / AICTE {yr}", "Approved"),
        ("GRT-2026-00003", f"Research Grant {yr} Project 3", f"CSIR / DBT {yr}", "Approved"),
        ("GRT-2026-00004", f"Research Grant {yr} Project 4", f"Ministry of Education {yr}", "Completed"),
    ]
    today = frappe.utils.nowdate()
    existing_titles = {
        r[0] for r in frappe.db.sql("SELECT grant_title FROM `tabResearch Grant`")
    }
    for rg_name, grant_title, agency, status in rg_grants:
        if grant_title in existing_titles:
            rg_count += 1
            continue
        if frappe.db.sql("SELECT name FROM `tabResearch Grant` WHERE name=%s LIMIT 1", rg_name):
            rg_name += "-X"
        try:
            frappe.db.sql("""
                INSERT INTO `tabResearch Grant`
                (name, grant_title, funding_agency, applied_amount, sanctioned_amount,
                 validity_from, validity_to, status, creation, modified,
                 owner, modified_by, docstatus)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(),
                        'Administrator', 'Administrator', 0)
            """, (rg_name, grant_title, agency,
                  random.randint(500000, 5000000), random.randint(500000, 5000000),
                  frappe.utils.add_months(today, -6), frappe.utils.add_months(today, 18),
                  status))
            rg_count += 1
        except Exception as e:
            if rg_count < 2:
                print(f"  ResearchGrant: {str(e)[:80]}")

    frappe.db.commit()

    # ── Student Feedback (10) ─────────────────────────────────────────────────
    instructors = frappe.get_all("Employee", pluck="name", limit=5)
    for i, stu in enumerate(students[:10]):
        sid = stu[0] if isinstance(stu, tuple) else stu
        cid = courses[i % len(courses)][0] if courses else None
        instr = instructors[i % len(instructors)] if instructors else None
        if not cid or not instr:
            continue
        if frappe.db.exists("Student Feedback", {"student": sid, "course": cid, "academic_year": ay}):
            sf_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "Student Feedback",
                "student": sid,
                "academic_year": ay,
                "academic_term": at,
                "course": cid,
                "instructor": instr,
                "subject_knowledge": random.randint(3, 5),
                "teaching_methodology": random.randint(3, 5),
                "communication_skills": random.randint(3, 5),
                "availability": random.randint(3, 5),
                "course_coverage": random.randint(3, 5),
                "overall_rating": random.randint(3, 5),
                "comments": "Good teaching approach. Clear explanations.",
            }).insert(ignore_permissions=True, ignore_links=True)
            sf_count += 1
        except Exception as e:
            if sf_count < 2:
                print(f"  StudentFeedback: {str(e)[:80]}")

    frappe.db.commit()

    # ── Temporary Teaching Assignments (3) ────────────────────────────────────
    # leave_application is required; create dummy Leave Applications if none exist
    emps = frappe.get_all("Employee", pluck="name", limit=6)
    leave_apps = frappe.get_all("Leave Application", pluck="name", limit=3)
    if not leave_apps:
        # Create 3 draft Leave Applications
        leave_type = frappe.db.get_value("Leave Type", {}, "name")
        for j in range(min(3, len(emps))):
            try:
                la_doc = frappe.get_doc({
                    "doctype": "Leave Application",
                    "employee": emps[j],
                    "leave_type": leave_type or "Casual Leave",
                    "from_date": frappe.utils.add_days(frappe.utils.nowdate(), -5),
                    "to_date": frappe.utils.add_days(frappe.utils.nowdate(), -3),
                    "status": "Approved",
                })
                la_doc.flags.ignore_mandatory = True
                la_doc.flags.ignore_validate = True
                la_doc.insert(ignore_permissions=True, ignore_links=True)
                leave_apps.append(la_doc.name)
            except Exception:
                pass
    for i in range(min(3, len(leave_apps), max(0, len(emps) // 2))):
        la = leave_apps[i]
        orig = emps[i * 2] if len(emps) > i * 2 else emps[0]
        sub = emps[i * 2 + 1] if len(emps) > i * 2 + 1 else emps[-1]
        cid = courses[i % len(courses)][0] if courses else None
        if not cid:
            continue
        if frappe.db.exists("Temporary Teaching Assignment", {"leave_application": la}):
            tta_count += 1
            continue
        try:
            tta_doc = frappe.get_doc({
                "doctype": "Temporary Teaching Assignment",
                "leave_application": la,
                "original_instructor": orig,
                "substitute_instructor": sub,
                "course": cid,
                "from_date": frappe.utils.add_days(frappe.utils.nowdate(), -5),
                "to_date": frappe.utils.add_days(frappe.utils.nowdate(), 0),
            })
            tta_doc.flags.ignore_mandatory = True
            tta_doc.flags.ignore_validate = True
            tta_doc.insert(ignore_permissions=True, ignore_links=True)
            tta_count += 1
        except Exception as e:
            if tta_count < 2:
                print(f"  TempTeachingAssignment: {str(e)[:80]}")

    frappe.db.commit()

    # ── University Announcements (4) ──────────────────────────────────────────
    ua_data = [
        ("Annual Cultural Festival 2026", "Join us for NIT's annual cultural extravaganza!"),
        ("Sports Day Announcement", "Sports Day will be held on the main grounds."),
        ("Academic Calendar Update", "Please note the updated academic calendar for semester 2."),
        ("Alumni Meet 2026", "We invite all alumni to the annual reunion event."),
    ]
    for ua_title, ua_content in ua_data:
        if frappe.db.exists("University Announcement", {"title": ua_title}):
            ua_count += 1
            continue
        try:
            frappe.get_doc({
                "doctype": "University Announcement",
                "title": ua_title,
                "content": ua_content,
                "publish_date": frappe.utils.add_days(frappe.utils.nowdate(), -random.randint(1, 30)),
                "expiry_date": frappe.utils.add_days(frappe.utils.nowdate(), 60),
                "is_published": 1,
            }).insert(ignore_permissions=True, ignore_links=True)
            ua_count += 1
        except Exception as e:
            if ua_count < 2:
                print(f"  UniversityAnnouncement {ua_title}: {str(e)[:80]}")

    # ── Bulk Fee Generator (2) ───────────────────────────────────────────────
    bfg_count = 0
    fee_structures = frappe.get_all("Fee Structure", pluck="name", limit=2)
    for i, prog_entry in enumerate(programs[:2]):
        prog_name = prog_entry[0] if isinstance(prog_entry, tuple) else prog_entry
        if i >= len(fee_structures):
            break
        fee_struct = fee_structures[i]
        if frappe.db.exists("Bulk Fee Generator", {"program": prog_name, "academic_year": ay}):
            bfg_count += 1
            continue
        try:
            bfg_doc = frappe.get_doc({
                "doctype": "Bulk Fee Generator",
                "program": prog_name,
                "academic_year": ay,
                "fee_structure": fee_struct,
                "students": [],
            })
            bfg_doc.flags.ignore_mandatory = True
            bfg_doc.flags.ignore_validate = True
            bfg_doc.insert(ignore_permissions=True, ignore_links=True)
            bfg_count += 1
        except Exception as e:
            if bfg_count < 2:
                print(f"  BulkFeeGenerator {prog_name}: {str(e)[:80]}")

    frappe.db.commit()
    print(
        f"  CustomReportDef: {crd_count}, DigiLockerDoc: {dgl_count}, "
        f"EmailQueueExt: {eqe_count}, EmergencyAck: {ea_count}, "
        f"FeeCategory: {fc_count}, FeeRefund: {fr_count}, "
        f"HostelBulkAtt: {hba_count}, MessMenu: {mm_count}, "
        f"NoticeViewLog: {nvl_count}, PaymentWebhook: {pwh_count}, "
        f"ResearchGrant: {rg_count}, StudentFeedback: {sf_count}, "
        f"TempTeachingAssign: {tta_count}, UniversityAnnouncement: {ua_count}, "
        f"BulkFeeGenerator: {bfg_count}"
    )

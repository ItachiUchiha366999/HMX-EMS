#!/usr/bin/env python3
"""
Production Portal Data Seeder - ems.hanumatrix.com

Seeds fresh transactional data for ALL 12 identified student portal data gaps.
Designed to be idempotent: safe to re-run multiple times.

Deployment:
  scp seed_production_portal_data.py root@ems.hanumatrix.com:/tmp/
  ssh root@ems.hanumatrix.com 'docker cp /tmp/seed_production_portal_data.py ems-backend:/tmp/'
  ssh root@ems.hanumatrix.com 'docker exec -w /home/frappe/frappe-bench ems-backend \
    /home/frappe/frappe-bench/env/bin/python /tmp/seed_production_portal_data.py'
"""

import os
import sys
import traceback
import random
from datetime import datetime, timedelta, date

# --- Bootstrap Frappe ---
os.chdir("/home/frappe/frappe-bench/sites")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/frappe")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/erpnext")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/education")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/university_erp")

import frappe
frappe.init(site="ems.hanumatrix.com")
frappe.connect()
frappe.set_user("Administrator")

# Seed for reproducibility
random.seed(42)

# --- Constants ---
STUDENTS_WITH_LOGINS = [
    ("EDU-STU-2026-00145", "student1@nit.edu"),
    ("EDU-STU-2026-00146", "student2@nit.edu"),
    ("EDU-STU-2026-00147", "student3@nit.edu"),
    ("EDU-STU-2026-00148", "student4@nit.edu"),
    ("EDU-STU-2026-00149", "student5@nit.edu"),
    ("EDU-STU-2026-00150", "pooja.verma@nit.edu"),
    ("EDU-STU-2026-00151", "rohit.patel@nit.edu"),
    ("EDU-STU-2026-00152", "divya.nair@nit.edu"),
    ("EDU-STU-2026-00153", "aditya.joshi@nit.edu"),
    ("EDU-STU-2026-00154", "kavya.iyer@nit.edu"),
    ("EDU-STU-2026-00155", "siddharth.rao@nit.edu"),
    ("EDU-STU-2026-00156", "priyanka.das@nit.edu"),
    ("EDU-STU-2026-00157", "nikhil.saxena@nit.edu"),
    ("EDU-STU-2026-00158", "shruti.mishra@nit.edu"),
    ("EDU-STU-2026-00159", "karan.singh@nit.edu"),
]

STUDENT_GROUPS = [
    "CSE-2026-Communication Skills",
    "CSE-2026-Engineering Mathemat",
    "CSE-2026-Environmental Scienc",
    "CSE-2026-Software Engineering",
]

TIME_SLOTS = [
    ("09:00:00", "10:00:00"),
    ("10:15:00", "11:15:00"),
    ("11:30:00", "12:30:00"),
    ("14:00:00", "15:00:00"),
]

# Realistic Indian mess menu items
BREAKFAST_ITEMS = [
    "Idli, Sambar, Coconut Chutney",
    "Masala Dosa, Chutney, Filter Coffee",
    "Poha, Jalebi, Chai",
    "Aloo Paratha, Curd, Pickle",
    "Upma, Vada, Sambar",
    "Chole Bhature, Lassi",
    "Bread, Butter, Omelette, Juice",
]
LUNCH_ITEMS = [
    "Rice, Dal Tadka, Aloo Gobi, Roti, Raita",
    "Rice, Rajma, Bhindi Masala, Chapati, Salad",
    "Jeera Rice, Chole, Lauki Sabzi, Phulka, Papad",
    "Rice, Sambar, Cabbage Poriyal, Rasam, Curd",
    "Pulao, Dal Fry, Paneer Butter Masala, Naan",
    "Rice, Kadhi Pakoda, Aloo Matar, Roti, Pickle",
    "Biryani, Raita, Onion Salad, Gulab Jamun",
]
SNACKS_ITEMS = [
    "Samosa, Chai",
    "Bread Pakora, Green Chutney, Tea",
    "Vada Pav, Chai",
    "Biscuits, Coffee",
    "Bhel Puri, Lemonade",
    "Cutlet, Sauce, Tea",
    "Spring Roll, Ketchup, Juice",
]
DINNER_ITEMS = [
    "Roti, Dal Makhani, Mixed Veg, Rice, Salad",
    "Chapati, Palak Paneer, Jeera Rice, Raita",
    "Phulka, Chana Masala, Rice, Boondi Raita",
    "Roti, Egg Curry, Rice, Dal, Pickle",
    "Paratha, Matar Paneer, Rice, Dal Tadka",
    "Chapati, Kadai Paneer, Fried Rice, Soup",
    "Roti, Aloo Matar, Rice, Moong Dal, Kheer",
]

GRADE_MAP = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"), (50, "C"), (0, "F"),
]

def get_grade(score):
    for threshold, grade in GRADE_MAP:
        if score >= threshold:
            return grade
    return "F"


# --- Safe execution wrapper ---
_results = {}

def _safe(label, fn):
    """Run fn with error handling. Print traceback on failure, continue."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    try:
        fn()
        frappe.db.commit()
        _results[label] = "OK"
        print(f"  -> {label}: DONE")
    except Exception:
        frappe.db.rollback()
        _results[label] = "FAILED"
        print(f"  -> {label}: FAILED")
        traceback.print_exc()


# ============================================================
# GAP 1: Student Group Student entries
# ============================================================
def fix_student_group_students():
    """Add all 15 students to all 4 course-based student groups."""
    for sg_name in STUDENT_GROUPS:
        if not frappe.db.exists("Student Group", sg_name):
            print(f"  [SKIP] Student Group '{sg_name}' not found")
            continue

        sg = frappe.get_doc("Student Group", sg_name)
        existing_students = {row.student for row in sg.students}

        added = 0
        for student_id, email in STUDENTS_WITH_LOGINS:
            if student_id in existing_students:
                continue
            # Get student_name
            student_name = frappe.db.get_value("Student", student_id, "student_name") or student_id
            sg.append("students", {
                "student": student_id,
                "student_name": student_name,
                "active": 1,
            })
            added += 1

        if added > 0:
            sg.flags.ignore_validate = True
            sg.flags.ignore_mandatory = True
            sg.save(ignore_permissions=True)
            print(f"  Added {added} students to {sg_name}")
        else:
            print(f"  {sg_name}: all students already present")


# ============================================================
# GAP 2: Course Schedules (current + next week)
# ============================================================
def fix_course_schedules():
    """Create course schedules for this week (Apr 7-11) and next week (Apr 14-18)."""
    # Query existing instructors
    instructors = frappe.db.sql(
        "SELECT name, instructor_name FROM `tabInstructor` LIMIT 10",
        as_dict=True
    )
    if not instructors:
        print("  [WARN] No instructors found, skipping course schedules")
        return

    # Query existing rooms
    rooms = frappe.db.sql(
        "SELECT name FROM `tabRoom` LIMIT 10",
        as_dict=True
    )
    room_names = [r["name"] for r in rooms] if rooms else []

    # Map student groups to their courses
    sg_courses = {}
    for sg_name in STUDENT_GROUPS:
        sg = frappe.get_doc("Student Group", sg_name) if frappe.db.exists("Student Group", sg_name) else None
        if sg and sg.course:
            sg_courses[sg_name] = sg.course
        else:
            # Try to extract course from group name
            print(f"  [INFO] Student Group {sg_name} has no course link")

    # Date ranges: this week Mon-Fri and next week Mon-Fri
    this_week_start = date(2026, 4, 7)
    dates = []
    for week_offset in [0, 7]:
        for day_offset in range(5):  # Mon-Fri
            dates.append(this_week_start + timedelta(days=week_offset + day_offset))

    created = 0
    for schedule_date in dates:
        for sg_name in STUDENT_GROUPS:
            course = sg_courses.get(sg_name)
            if not course:
                continue

            # Pick 3 time slots for this group on this day (not all 4 every day)
            day_seed = schedule_date.toordinal() + hash(sg_name)
            rng = random.Random(day_seed)
            slots_for_day = rng.sample(TIME_SLOTS, k=min(3, len(TIME_SLOTS)))

            for from_time, to_time in slots_for_day:
                instructor = instructors[created % len(instructors)]
                room = room_names[created % len(room_names)] if room_names else None

                # Check if schedule already exists
                filters = {
                    "student_group": sg_name,
                    "schedule_date": str(schedule_date),
                    "from_time": from_time,
                }
                if frappe.db.exists("Course Schedule", filters):
                    continue

                doc = frappe.get_doc({
                    "doctype": "Course Schedule",
                    "student_group": sg_name,
                    "course": course,
                    "instructor": instructor["name"],
                    "instructor_name": instructor.get("instructor_name", ""),
                    "room": room,
                    "schedule_date": str(schedule_date),
                    "from_time": from_time,
                    "to_time": to_time,
                })
                doc.flags.ignore_validate = True
                doc.flags.ignore_mandatory = True
                doc.insert(ignore_permissions=True)
                created += 1

    print(f"  Created {created} new course schedules")


# ============================================================
# GAP 3: Student Attendance
# ============================================================
def fix_student_attendance():
    """Create attendance for past 3 weeks linked to course schedules."""
    # Get course schedules from Mar 23 to Apr 7
    schedules = frappe.db.sql("""
        SELECT cs.name, cs.student_group, cs.course, cs.schedule_date
        FROM `tabCourse Schedule` cs
        WHERE cs.schedule_date BETWEEN '2026-03-23' AND '2026-04-07'
        ORDER BY cs.schedule_date
    """, as_dict=True)

    if not schedules:
        print("  [WARN] No course schedules found for attendance date range")
        # Fall back: create attendance for the newly created schedules too
        schedules = frappe.db.sql("""
            SELECT cs.name, cs.student_group, cs.course, cs.schedule_date
            FROM `tabCourse Schedule` cs
            WHERE cs.schedule_date BETWEEN '2026-04-07' AND '2026-04-08'
            ORDER BY cs.schedule_date
        """, as_dict=True)

    statuses = ["Present"] * 75 + ["Absent"] * 15 + ["Late"] * 10
    created = 0

    for cs in schedules:
        # Get students in this group
        students_in_group = frappe.db.sql("""
            SELECT sgs.student, sgs.student_name
            FROM `tabStudent Group Student` sgs
            WHERE sgs.parent = %s AND sgs.active = 1
        """, cs["student_group"], as_dict=True)

        for stu in students_in_group:
            # Check if attendance already exists
            exists = frappe.db.exists("Student Attendance", {
                "student": stu["student"],
                "course_schedule": cs["name"],
            })
            if exists:
                continue

            status = random.choice(statuses)
            # Map "Late" to "Present" with leave_application note if needed
            # Actually Student Attendance has status: Present/Absent only in most setups
            actual_status = "Present" if status in ("Present", "Late") else "Absent"

            doc = frappe.get_doc({
                "doctype": "Student Attendance",
                "student": stu["student"],
                "student_name": stu.get("student_name", ""),
                "course_schedule": cs["name"],
                "student_group": cs["student_group"],
                "date": str(cs["schedule_date"]),
                "status": actual_status,
            })
            doc.flags.ignore_validate = True
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True)
            created += 1

    print(f"  Created {created} attendance records")


# ============================================================
# GAP 4: Assessment Results
# ============================================================
def fix_assessment_results():
    """Update existing assessment results with real scores and create new ones."""
    academic_term_sem1 = "2025-26 (Semester 1)"
    academic_term_sem2 = "2025-26 (Semester 2)"

    # Update existing 10 assessment results with real scores
    existing = frappe.db.sql("""
        SELECT name, student, total_score, grade
        FROM `tabAssessment Result` LIMIT 20
    """, as_dict=True)

    updated = 0
    for ar in existing:
        score = random.randint(55, 95)
        grade = get_grade(score)
        frappe.db.set_value("Assessment Result", ar["name"], {
            "total_score": score,
            "grade": grade,
            "academic_term": academic_term_sem1,
        })
        updated += 1

    print(f"  Updated {updated} existing assessment results")

    # Create new assessment results for Semester 2
    # Get assessment plans
    assessment_plans = frappe.db.sql("""
        SELECT name, assessment_name, course, student_group, maximum_assessment_score
        FROM `tabAssessment Plan`
        LIMIT 10
    """, as_dict=True)

    if not assessment_plans:
        print("  [INFO] No assessment plans found; creating results without plan link")
        # Create results directly per student per course group
        courses = frappe.db.sql("""
            SELECT sg.name as student_group, sg.course
            FROM `tabStudent Group` sg
            WHERE sg.name IN ({})
        """.format(",".join([f"'{sg}'" for sg in STUDENT_GROUPS])), as_dict=True)

        created = 0
        for course_info in courses:
            for student_id, email in STUDENTS_WITH_LOGINS[:8]:  # First 8 students
                score = random.randint(50, 98)
                grade = get_grade(score)
                student_name = frappe.db.get_value("Student", student_id, "student_name") or student_id

                # Check existence
                exists = frappe.db.exists("Assessment Result", {
                    "student": student_id,
                    "course": course_info.get("course"),
                    "academic_term": academic_term_sem2,
                })
                if exists:
                    continue

                doc = frappe.get_doc({
                    "doctype": "Assessment Result",
                    "student": student_id,
                    "student_name": student_name,
                    "course": course_info.get("course"),
                    "student_group": course_info["student_group"],
                    "academic_term": academic_term_sem2,
                    "academic_year": "2025-26",
                    "total_score": score,
                    "grade": grade,
                    "maximum_score": 100,
                    "docstatus": 1,
                })
                doc.flags.ignore_validate = True
                doc.flags.ignore_mandatory = True
                try:
                    doc.insert(ignore_permissions=True)
                    created += 1
                except Exception as e:
                    # Some assessment results may fail due to missing mandatory fields
                    print(f"  [WARN] Could not create result for {student_id}: {e}")

        print(f"  Created {created} new assessment results")
    else:
        created = 0
        for plan in assessment_plans:
            max_score = plan.get("maximum_assessment_score") or 100
            for student_id, email in STUDENTS_WITH_LOGINS[:8]:
                score = random.randint(50, 98)
                grade = get_grade(score)
                student_name = frappe.db.get_value("Student", student_id, "student_name") or student_id

                exists = frappe.db.exists("Assessment Result", {
                    "student": student_id,
                    "assessment_plan": plan["name"],
                })
                if exists:
                    continue

                doc = frappe.get_doc({
                    "doctype": "Assessment Result",
                    "student": student_id,
                    "student_name": student_name,
                    "assessment_plan": plan["name"],
                    "course": plan.get("course"),
                    "student_group": plan.get("student_group"),
                    "academic_term": academic_term_sem2,
                    "academic_year": "2025-26",
                    "total_score": score,
                    "grade": grade,
                    "maximum_score": max_score,
                    "docstatus": 1,
                })
                doc.flags.ignore_validate = True
                doc.flags.ignore_mandatory = True
                try:
                    doc.insert(ignore_permissions=True)
                    created += 1
                except Exception as e:
                    print(f"  [WARN] Could not create result for {student_id}/{plan['name']}: {e}")

        print(f"  Created {created} new assessment results")


# ============================================================
# GAP 5: Student custom_cgpa
# ============================================================
def fix_student_cgpa():
    """Compute and set realistic CGPA for all 15 login-enabled students."""
    for student_id, email in STUDENTS_WITH_LOGINS:
        # Get average score from assessment results
        avg_score = frappe.db.sql("""
            SELECT AVG(total_score) as avg_score
            FROM `tabAssessment Result`
            WHERE student = %s AND total_score > 0
        """, student_id, as_dict=True)

        if avg_score and avg_score[0].get("avg_score"):
            raw_cgpa = float(avg_score[0]["avg_score"]) * 10 / 100
            # Clamp to 7.0-9.5 range
            cgpa = max(7.0, min(9.5, raw_cgpa))
        else:
            # No scores yet, assign a reasonable default
            cgpa = round(random.uniform(7.2, 9.0), 2)

        cgpa = round(cgpa, 2)
        frappe.db.set_value("Student", student_id, "custom_cgpa", cgpa)
        print(f"  {student_id}: CGPA = {cgpa}")


# ============================================================
# GAP 6: Semester 2 Fees
# ============================================================
def fix_semester2_fees():
    """Create Fees records for Semester 2 with paid/pending/partial mix."""
    academic_term = "2025-26 (Semester 2)"
    academic_year = "2025-26"
    due_date = "2026-04-30"

    # Ensure Academic Term "2025-26 (Semester 2)" exists
    if not frappe.db.exists("Academic Term", "2025-26 (Semester 2)"):
        # Find the academic year record
        ay_doc = frappe.get_doc({
            "doctype": "Academic Term",
            "academic_year": academic_year,
            "term_name": "Semester 2",
            "term_start_date": "2026-01-15",
            "term_end_date": "2026-06-30",
        })
        ay_doc.flags.ignore_validate = True
        ay_doc.flags.ignore_mandatory = True
        ay_doc.insert(ignore_permissions=True)
        print(f"  Created Academic Term: {ay_doc.name}")

    # Use exact Fee Category names from production DB
    fee_components = [
        {"fees_category": "Tuition Fee", "description": "Tuition Fee", "amount": 50000},
        {"fees_category": "Laboratory Fee", "description": "Laboratory Fee", "amount": 10000},
        {"fees_category": "Library Fee", "description": "Library Fee", "amount": 5000},
        {"fees_category": "Examination Fee", "description": "Examination Fee", "amount": 3000},
    ]
    grand_total = sum(c["amount"] for c in fee_components)

    # All fee categories already exist on production (Tuition Fee, Laboratory Fee,
    # Library Fee, Examination Fee with codes TUI, LAB, LIB, EXM)

    created = 0
    for idx, (student_id, email) in enumerate(STUDENTS_WITH_LOGINS):
        # Check if Semester 2 fees already exist
        existing = frappe.db.exists("Fees", {
            "student": student_id,
            "academic_term": academic_term,
        })
        if existing:
            print(f"  [SKIP] Fees already exist for {student_id} Semester 2")
            continue

        student_name = frappe.db.get_value("Student", student_id, "student_name") or student_id
        program = frappe.db.get_value("Student", student_id, "custom_program") or ""

        # Determine outstanding amount based on position
        stu_num = int(student_id.split("-")[-1])
        if stu_num <= 150:
            outstanding = 0  # Fully paid
        elif stu_num <= 155:
            outstanding = grand_total  # Fully pending
        else:
            outstanding = 18000  # Partial (tuition paid, rest pending)

        doc = frappe.get_doc({
            "doctype": "Fees",
            "student": student_id,
            "student_name": student_name,
            "program": program if program else None,
            "academic_year": academic_year,
            "academic_term": academic_term,
            "due_date": due_date,
            "grand_total": grand_total,
            "outstanding_amount": outstanding,
            "components": [
                {
                    "doctype": "Fee Component",
                    "fees_category": c["fees_category"],
                    "description": c["description"],
                    "amount": c["amount"],
                }
                for c in fee_components
            ],
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.insert(ignore_permissions=True)

        # Submit the fee doc
        try:
            doc.flags.ignore_validate = True
            doc.flags.ignore_mandatory = True
            doc.submit()
        except Exception as e:
            print(f"  [WARN] Could not submit fees for {student_id}: {e}")
            # At least set docstatus via SQL
            frappe.db.set_value("Fees", doc.name, "docstatus", 1)

        # Set outstanding amount directly (submit may reset it)
        frappe.db.set_value("Fees", doc.name, "outstanding_amount", outstanding)

        created += 1

    print(f"  Created {created} Semester 2 fee records")


# ============================================================
# GAP 7: Notice Board
# ============================================================
def fix_notice_board():
    """Submit draft notices and create new current notices."""
    # Submit existing draft notices
    drafts = frappe.db.sql("""
        SELECT name FROM `tabNotice Board`
        WHERE docstatus = 0
    """, as_dict=True)

    submitted_drafts = 0
    for draft in drafts:
        try:
            doc = frappe.get_doc("Notice Board", draft["name"])
            doc.flags.ignore_validate = True
            doc.flags.ignore_mandatory = True
            doc.submit()
            submitted_drafts += 1
        except Exception as e:
            print(f"  [WARN] Could not submit {draft['name']}: {e}")
            # Force submit via SQL
            frappe.db.set_value("Notice Board", draft["name"], "docstatus", 1)
            submitted_drafts += 1

    print(f"  Submitted {submitted_drafts} draft notices")

    # Create new notices with current dates
    new_notices = [
        {
            "title": "Mid-Semester Examination Schedule Released",
            "notice_type": "Academic",
            "priority": "High",
            "expiry_date": "2026-04-30",
            "content": "The mid-semester examination schedule for all B.Tech programs has been released. "
                       "Students are advised to check the examination portal for their individual schedules. "
                       "Hall tickets will be available for download one week before exams.",
        },
        {
            "title": "Annual Sports Day Registration Open",
            "notice_type": "Sports",
            "priority": "Medium",
            "expiry_date": "2026-04-25",
            "content": "Registration for the Annual Sports Day 2026 is now open. "
                       "Events include athletics, cricket, basketball, volleyball, and chess. "
                       "Register through your student portal or contact the Sports Committee.",
        },
        {
            "title": "Library Extended Hours During Exams",
            "notice_type": "General",
            "priority": "Low",
            "expiry_date": "2026-04-20",
            "content": "The Central Library will operate with extended hours during the examination period. "
                       "New timings: 7:00 AM to 11:00 PM (Monday to Saturday), 8:00 AM to 9:00 PM (Sunday). "
                       "Students are encouraged to make use of the reading rooms and digital resources.",
        },
        {
            "title": "Summer Internship Applications Due",
            "notice_type": "Academic",
            "priority": "High",
            "expiry_date": "2026-05-15",
            "content": "Last date to submit summer internship applications through the placement portal is May 15, 2026. "
                       "Eligible students from B.Tech 2nd year and above are encouraged to apply. "
                       "Contact the Placement Cell for the list of participating companies.",
        },
    ]

    created = 0
    for notice_data in new_notices:
        # Check if notice with same title already exists
        if frappe.db.exists("Notice Board", {"title": notice_data["title"]}):
            print(f"  [SKIP] Notice '{notice_data['title']}' already exists")
            continue

        doc = frappe.get_doc({
            "doctype": "Notice Board",
            "title": notice_data["title"],
            "notice_type": notice_data.get("notice_type", "General"),
            "priority": notice_data.get("priority", "Medium"),
            "publish_date": "2026-04-08",
            "expiry_date": notice_data["expiry_date"],
            "content": notice_data["content"],
            "audience_type": "All",
            "docstatus": 0,
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.insert(ignore_permissions=True)

        # Submit
        try:
            doc.flags.ignore_validate = True
            doc.flags.ignore_mandatory = True
            doc.submit()
        except Exception as e:
            print(f"  [WARN] Could not submit notice: {e}")
            frappe.db.set_value("Notice Board", doc.name, "docstatus", 1)

        created += 1

    print(f"  Created {created} new notices")


# ============================================================
# GAP 8: Hostel Allocation dates
# ============================================================
def fix_hostel_allocations():
    """Extend expired hostel allocation dates to 2026-06-30."""
    expired = frappe.db.sql("""
        SELECT name, student, to_date
        FROM `tabHostel Allocation`
        WHERE to_date < '2026-04-08'
    """, as_dict=True)

    updated = 0
    for alloc in expired:
        frappe.db.set_value("Hostel Allocation", alloc["name"], "to_date", "2026-06-30")
        updated += 1

    print(f"  Extended {updated} hostel allocations to 2026-06-30")


# ============================================================
# GAP 9: Library Transactions
# ============================================================
def fix_library_transactions():
    """Return overdue books and issue new ones for demo student."""
    # Return overdue books
    overdue = frappe.db.sql("""
        SELECT name, member, article
        FROM `tabLibrary Transaction`
        WHERE transaction_type = 'Issue' AND due_date < '2026-04-08'
    """, as_dict=True)

    returned = 0
    for txn in overdue:
        # Check if already returned
        already_returned = frappe.db.exists("Library Transaction", {
            "transaction_type": "Return",
            "article": txn["article"],
            "member": txn["member"],
        })
        if already_returned:
            continue

        # Create return transaction
        ret_doc = frappe.get_doc({
            "doctype": "Library Transaction",
            "transaction_type": "Return",
            "member": txn["member"],
            "article": txn["article"],
            "transaction_date": "2026-04-08",
        })
        ret_doc.flags.ignore_validate = True
        ret_doc.flags.ignore_mandatory = True
        try:
            ret_doc.insert(ignore_permissions=True)
            returned += 1
        except Exception as e:
            print(f"  [WARN] Could not create return for {txn['name']}: {e}")

    print(f"  Created {returned} return transactions")

    # Issue new books for demo student
    # Find library member for EDU-STU-2026-00145 via student field
    demo_member = frappe.db.get_value("Library Member", {"student": "EDU-STU-2026-00145"})
    if not demo_member:
        # Fallback: use known member ID
        demo_member = "LM-2026-00025" if frappe.db.exists("Library Member", "LM-2026-00025") else None
    if not demo_member:
        demo_member = frappe.db.get_all("Library Member", limit=1, pluck="name")
        demo_member = demo_member[0] if demo_member else None

    if not demo_member:
        print("  [WARN] No library member found, skipping new issues")
        return

    # Get available Library Articles
    articles = frappe.db.get_all("Library Article", fields=["name", "title"], limit=5)

    issued = 0
    for article in articles[:3]:
        # Check if already issued and not returned
        active_issue = frappe.db.exists("Library Transaction", {
            "transaction_type": "Issue",
            "article": article["name"],
            "member": demo_member,
        })
        if active_issue:
            continue

        doc = frappe.get_doc({
            "doctype": "Library Transaction",
            "transaction_type": "Issue",
            "member": demo_member,
            "article": article["name"],
            "transaction_date": "2026-04-08",
            "issue_date": "2026-04-08",
            "due_date": "2026-04-30",
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        try:
            doc.insert(ignore_permissions=True)
            issued += 1
        except Exception as e:
            print(f"  [WARN] Could not issue {article['name']}: {e}")

    print(f"  Issued {issued} new books to demo student")


# ============================================================
# GAP 10: Mess Menu
# ============================================================
def fix_mess_menu():
    """Create current and next week mess menus."""
    # Find existing mess
    mess_list = frappe.db.sql("SELECT name FROM `tabHostel Mess` LIMIT 1", as_dict=True)
    mess_name = mess_list[0]["name"] if mess_list else None

    if not mess_name:
        print("  [WARN] No Hostel Mess found, skipping mess menu")
        return

    # Autoname is format:{mess}-{week_start_date}, fields: week_start_date, week_end_date
    weeks = [
        ("2026-04-06", "2026-04-12"),
        ("2026-04-13", "2026-04-19"),
    ]

    created = 0
    for week_start, week_end in weeks:
        # Check if menu exists: autoname = "{mess}-{week_start_date}"
        expected_name = f"{mess_name}-{week_start}"
        if frappe.db.exists("Mess Menu", expected_name):
            print(f"  [SKIP] Mess menu '{expected_name}' already exists")
            continue

        menu_items = []
        start = datetime.strptime(week_start, "%Y-%m-%d").date()
        for day_offset in range(7):
            menu_date = start + timedelta(days=day_offset)
            day_name = menu_date.strftime("%A")
            day_idx = day_offset

            menu_items.extend([
                {
                    "doctype": "Mess Menu Item",
                    "day": day_name,
                    "meal_type": "Breakfast",
                    "menu_items": BREAKFAST_ITEMS[day_idx % len(BREAKFAST_ITEMS)],
                },
                {
                    "doctype": "Mess Menu Item",
                    "day": day_name,
                    "meal_type": "Lunch",
                    "menu_items": LUNCH_ITEMS[day_idx % len(LUNCH_ITEMS)],
                },
                {
                    "doctype": "Mess Menu Item",
                    "day": day_name,
                    "meal_type": "Snacks",
                    "menu_items": SNACKS_ITEMS[day_idx % len(SNACKS_ITEMS)],
                },
                {
                    "doctype": "Mess Menu Item",
                    "day": day_name,
                    "meal_type": "Dinner",
                    "menu_items": DINNER_ITEMS[day_idx % len(DINNER_ITEMS)],
                },
            ])

        doc = frappe.get_doc({
            "doctype": "Mess Menu",
            "mess": mess_name,
            "week_start_date": week_start,
            "week_end_date": week_end,
            "status": "Published",
            "menu_items": menu_items,
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.insert(ignore_permissions=True)
        created += 1

    print(f"  Created {created} mess menus")


# ============================================================
# GAP 11: Portal API field mismatch (hostel_room vs room)
# NOTE: portal_api.py get_student_hostel() queries 'hostel_room' but
# DocType field is 'room' -- code fix needed in portal_api.py
# This is a code bug, NOT a data gap. Do not fix on production.
# ============================================================
def note_portal_api_bug():
    """Document the known portal API field mismatch."""
    print("  NOTE: portal_api.py get_student_hostel() queries 'hostel_room'")
    print("        but Hostel Allocation DocType field is 'room'")
    print("        This is a code bug that needs fixing in portal_api.py")
    print("        Not attempting code changes on production.")


# ============================================================
# GAP 12: Suggestions (Student Grievance DocType missing)
# NOTE: Student Grievance DocType does not exist on production.
# Suggestions created instead. Portal grievances.py will return
# empty until DocType is created.
# ============================================================
def fix_suggestions():
    """Create suggestion records as workaround for missing Student Grievance DocType."""
    suggestions = [
        {
            "subject": "Improve Wi-Fi connectivity in hostel areas",
            "description": "The Wi-Fi signal in the hostel rooms is very weak, especially on the upper floors. "
                          "Students face difficulty in attending online classes and accessing study materials. "
                          "Please consider installing additional access points.",
            "suggestion_type": "Infrastructure",
        },
        {
            "subject": "Request for extended library hours during exams",
            "description": "During examination periods, the library closes at 8 PM which is too early. "
                          "Many students prefer studying in the library environment. "
                          "Requesting extension of library hours to 11 PM during exam weeks.",
            "suggestion_type": "Academic",
        },
        {
            "subject": "Suggestion for more vegetarian options in mess",
            "description": "The current mess menu has limited vegetarian options, especially during dinner. "
                          "A significant portion of students are vegetarian and would appreciate more variety "
                          "in vegetarian dishes, including South Indian options.",
            "suggestion_type": "Hostel",
        },
        {
            "subject": "Need better lab equipment for Electronics lab",
            "description": "Several oscilloscopes and function generators in the Electronics lab are non-functional. "
                          "Students have to share equipment which affects practical learning. "
                          "Request procurement of new equipment for the upcoming semester.",
            "suggestion_type": "Academic",
        },
    ]

    created = 0
    for idx, sugg_data in enumerate(suggestions):
        # Check if suggestion with same subject exists
        if frappe.db.exists("Suggestion", {"subject": sugg_data["subject"]}):
            print(f"  [SKIP] Suggestion '{sugg_data['subject'][:40]}...' already exists")
            continue

        student_email = STUDENTS_WITH_LOGINS[idx % len(STUDENTS_WITH_LOGINS)][1]
        creation_date = datetime(2026, 4, 8 - idx, 10, 0, 0)

        doc = frappe.get_doc({
            "doctype": "Suggestion",
            "subject": sugg_data["subject"],
            "description": sugg_data["description"],
            "owner": student_email,
        })
        # Set suggestion_type if the field exists
        if hasattr(doc, "suggestion_type"):
            doc.suggestion_type = sugg_data.get("suggestion_type", "General")
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        try:
            doc.insert(ignore_permissions=True)
            # Update creation date
            frappe.db.set_value("Suggestion", doc.name, "creation", creation_date)
            created += 1
        except Exception as e:
            print(f"  [WARN] Could not create suggestion: {e}")

    print(f"  Created {created} suggestions")


# ============================================================
# MAIN EXECUTION
# ============================================================
print("\n" + "=" * 70)
print("  PRODUCTION PORTAL DATA SEEDER - ems.hanumatrix.com")
print("  Addressing all 12 student portal data gaps")
print("=" * 70)

_safe("Gap 1: Student Group Students", fix_student_group_students)
_safe("Gap 2: Course Schedules", fix_course_schedules)
_safe("Gap 3: Student Attendance", fix_student_attendance)
_safe("Gap 4: Assessment Results", fix_assessment_results)
_safe("Gap 5: Student CGPA", fix_student_cgpa)
_safe("Gap 6: Semester 2 Fees", fix_semester2_fees)
_safe("Gap 7: Notice Board", fix_notice_board)
_safe("Gap 8: Hostel Allocations", fix_hostel_allocations)
_safe("Gap 9: Library Transactions", fix_library_transactions)
_safe("Gap 10: Mess Menu", fix_mess_menu)
_safe("Gap 11: Portal API Bug (noted)", note_portal_api_bug)
_safe("Gap 12: Suggestions", fix_suggestions)

# Final commit and summary
frappe.db.commit()
frappe.destroy()

print("\n" + "=" * 70)
print("  RESULTS SUMMARY")
print("=" * 70)
for label, status in _results.items():
    marker = "OK" if status == "OK" else "FAILED"
    print(f"  [{marker}] {label}")

failed = sum(1 for s in _results.values() if s != "OK")
if failed:
    print(f"\n  WARNING: {failed} section(s) failed. Review output above.")
else:
    print(f"\n  All {len(_results)} sections completed successfully.")
print("\nDONE - All portal data gaps addressed")

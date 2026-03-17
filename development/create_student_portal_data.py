#!/usr/bin/env python3
"""
Comprehensive Student Portal Data Creation Script

This script creates realistic sample data for ALL fields in the student portal:
- Student Attendance records
- Course Schedules (today's classes)
- Exam Schedules (upcoming exams)
- Assessment Results (for CGPA)
- Fee records
- Library Transactions (issued books)
- Assignments
- Announcements
- Student Groups

Usage:
    cd /workspace/development/frappe-bench
    bench --site university.local execute development/create_student_portal_data.py
"""

import frappe
from datetime import datetime, timedelta
from frappe.utils import nowdate, getdate, add_days, now_datetime

def create_all_student_data():
    """Create comprehensive student portal data"""

    frappe.init(site="university.local")
    frappe.connect()
    frappe.set_user("Administrator")

    print("\n" + "="*80)
    print("🎓 CREATING COMPREHENSIVE STUDENT PORTAL DATA")
    print("="*80 + "\n")

    student_id = "EDU-STU-2026-00002"
    student_name = "Test Student"
    academic_year = "2025-26"
    program_name = "B.Tech Computer Science"

    # Step 1: Create Courses
    print("📚 Step 1: Creating Courses...")
    courses = create_courses()

    # Step 2: Create Student Group
    print("\n👥 Step 2: Creating Student Group...")
    student_group = create_student_group(student_id, student_name, academic_year, program_name)

    # Step 3: Create Course Schedules (Today's Classes)
    print("\n🕐 Step 3: Creating Today's Class Schedule...")
    create_course_schedules(student_group, courses)

    # Step 4: Create Attendance Records
    print("\n✅ Step 4: Creating Attendance Records...")
    create_attendance_records(student_id, student_name)

    # Step 5: Create Exam Schedules
    print("\n📝 Step 5: Creating Exam Schedules...")
    create_exam_schedules(student_group, courses)

    # Step 6: Create Assessment Results (for CGPA)
    print("\n🎯 Step 6: Creating Assessment Results...")
    create_assessment_results(student_id, courses)

    # Step 7: Update Student CGPA
    print("\n📊 Step 7: Updating Student CGPA...")
    update_student_cgpa(student_id)

    # Step 8: Create Fee Records
    print("\n💰 Step 8: Creating Fee Records...")
    create_fee_records(student_id, student_name, program_name, academic_year)

    # Step 9: Create Library Transactions
    print("\n📖 Step 9: Creating Library Transactions...")
    create_library_transactions(student_id, student_name)

    # Step 10: Create Assignments
    print("\n📄 Step 10: Creating Assignments...")
    create_assignments(student_group, courses)

    # Step 11: Create Announcements
    print("\n📢 Step 11: Creating Announcements...")
    create_announcements()

    frappe.db.commit()

    print("\n" + "="*80)
    print("✅ ALL STUDENT PORTAL DATA CREATED SUCCESSFULLY!")
    print("="*80)
    print(f"\n📌 Student: {student_name} ({student_id})")
    print(f"📧 Login: student@test.edu")
    print(f"🌐 Portal: http://localhost:18000/student_portal")
    print("\n💡 Clear browser cookies and login to see all the data!")
    print("="*80 + "\n")


def create_courses():
    """Create sample courses"""
    courses_data = [
        {"course_name": "Data Structures and Algorithms", "course_code": "CS301"},
        {"course_name": "Database Management Systems", "course_code": "CS302"},
        {"course_name": "Operating Systems", "course_code": "CS303"},
        {"course_name": "Computer Networks", "course_code": "CS304"},
        {"course_name": "Software Engineering", "course_code": "CS305"},
    ]

    created_courses = []
    for course_data in courses_data:
        # Check if course exists
        course = frappe.db.get_value("Course", {"course_name": course_data["course_name"]})
        if not course:
            c = frappe.get_doc({
                "doctype": "Course",
                "course_name": course_data["course_name"],
                "course_code": course_data["course_code"]
            })
            c.insert(ignore_permissions=True)
            course = c.name
            print(f"  ✅ Created: {course_data['course_name']}")
        else:
            print(f"  ℹ️  Exists: {course_data['course_name']}")
        created_courses.append(course)

    return created_courses


def create_student_group(student_id, student_name, academic_year, program_name):
    """Create or update student group"""
    group_name = "BCS-2024-Batch-A"

    student_group = frappe.db.get_value("Student Group", {"student_group_name": group_name})

    if not student_group:
        sg = frappe.get_doc({
            "doctype": "Student Group",
            "student_group_name": group_name,
            "group_based_on": "Batch",
            "academic_year": academic_year,
            "program": program_name,
            "students": [
                {
                    "student": student_id,
                    "student_name": student_name,
                    "active": 1
                }
            ]
        })
        sg.insert(ignore_permissions=True)
        student_group = sg.name
        print(f"  ✅ Created group: {group_name}")
    else:
        # Check if student is in group
        sg = frappe.get_doc("Student Group", student_group)
        student_exists = any(s.student == student_id for s in sg.students)
        if not student_exists:
            sg.append("students", {
                "student": student_id,
                "student_name": student_name,
                "active": 1
            })
            sg.save(ignore_permissions=True)
            print(f"  ✅ Added student to group: {group_name}")
        else:
            print(f"  ℹ️  Student already in group: {group_name}")

    return student_group


def create_course_schedules(student_group, courses):
    """Create today's class schedule"""
    today = getdate(nowdate())

    schedules = [
        {"course": courses[0], "from_time": "09:00:00", "to_time": "10:30:00", "room": "Room 101"},
        {"course": courses[1], "from_time": "11:00:00", "to_time": "12:30:00", "room": "Room 102"},
        {"course": courses[2], "from_time": "14:00:00", "to_time": "15:30:00", "room": "Room 103"},
    ]

    count = 0
    for schedule_data in schedules:
        # Check if schedule exists
        existing = frappe.db.exists("Course Schedule", {
            "student_group": student_group,
            "schedule_date": today,
            "course": schedule_data["course"]
        })

        if not existing:
            cs = frappe.get_doc({
                "doctype": "Course Schedule",
                "student_group": student_group,
                "course": schedule_data["course"],
                "schedule_date": today,
                "from_time": schedule_data["from_time"],
                "to_time": schedule_data["to_time"],
                "room": schedule_data["room"]
            })
            cs.insert(ignore_permissions=True)
            count += 1

    print(f"  ✅ Created {count} classes for today ({today})")


def create_attendance_records(student_id, student_name):
    """Create attendance records for the past 30 days"""
    today = getdate(nowdate())

    # Create attendance for past 30 days (weekdays only)
    # 85% present, 15% absent
    import random

    count_present = 0
    count_absent = 0

    for days_ago in range(30, 0, -1):
        date = add_days(today, -days_ago)

        # Skip weekends
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            continue

        # Check if attendance exists
        existing = frappe.db.exists("Student Attendance", {
            "student": student_id,
            "date": date
        })

        if not existing:
            # 85% chance of being present
            status = "Present" if random.random() < 0.85 else "Absent"

            att = frappe.get_doc({
                "doctype": "Student Attendance",
                "student": student_id,
                "student_name": student_name,
                "date": date,
                "status": status
            })
            att.insert(ignore_permissions=True)

            if status == "Present":
                count_present += 1
            else:
                count_absent += 1

    total = count_present + count_absent
    percentage = round((count_present / total * 100), 1) if total > 0 else 0
    print(f"  ✅ Created {total} attendance records")
    print(f"     Present: {count_present}, Absent: {count_absent}")
    print(f"     Attendance: {percentage}%")


def create_exam_schedules(student_group, courses):
    """Create upcoming and past exam schedules"""
    today = getdate(nowdate())

    # Upcoming exams
    upcoming_exams = [
        {"course": courses[0], "days_ahead": 2, "name": "Mid Semester Exam - DSA"},
        {"course": courses[1], "days_ahead": 5, "name": "Mid Semester Exam - DBMS"},
        {"course": courses[2], "days_ahead": 10, "name": "Mid Semester Exam - OS"},
    ]

    # Past exams
    past_exams = [
        {"course": courses[3], "days_ago": 15, "name": "Unit Test - Networks"},
        {"course": courses[4], "days_ago": 30, "name": "Unit Test - Software Eng"},
    ]

    count = 0

    # Create upcoming exams
    for exam_data in upcoming_exams:
        exam_date = add_days(today, exam_data["days_ahead"])

        existing = frappe.db.exists("Exam Schedule", {
            "student_group": student_group,
            "schedule_date": exam_date,
            "course": exam_data["course"]
        })

        if not existing:
            es = frappe.get_doc({
                "doctype": "Exam Schedule",
                "exam": exam_data["name"],
                "student_group": student_group,
                "course": exam_data["course"],
                "schedule_date": exam_date,
                "from_time": "10:00:00",
                "to_time": "13:00:00",
                "room": f"Exam Hall {count + 1}",
                "docstatus": 1
            })
            es.insert(ignore_permissions=True)
            es.submit()
            count += 1
            print(f"  ✅ Upcoming: {exam_data['name']} on {exam_date}")

    # Create past exams
    for exam_data in past_exams:
        exam_date = add_days(today, -exam_data["days_ago"])

        existing = frappe.db.exists("Exam Schedule", {
            "student_group": student_group,
            "schedule_date": exam_date,
            "course": exam_data["course"]
        })

        if not existing:
            es = frappe.get_doc({
                "doctype": "Exam Schedule",
                "exam": exam_data["name"],
                "student_group": student_group,
                "course": exam_data["course"],
                "schedule_date": exam_date,
                "from_time": "10:00:00",
                "to_time": "13:00:00",
                "room": f"Exam Hall {count + 1}",
                "docstatus": 1
            })
            es.insert(ignore_permissions=True)
            es.submit()
            count += 1
            print(f"  ✅ Past: {exam_data['name']} on {exam_date}")

    print(f"  📊 Total: {len(upcoming_exams)} upcoming, {len(past_exams)} past exams")


def create_assessment_results(student_id, courses):
    """Create assessment results for CGPA calculation"""

    # Check if Assessment Plan exists
    plans = frappe.db.get_all("Assessment Plan", limit=5)

    if not plans:
        print("  ⚠️  No Assessment Plans found, creating basic ones...")
        plans = create_assessment_plans(courses)

    results_data = [
        {"plan_idx": 0, "course": courses[0], "grade": "A+", "score": 92, "max_score": 100},
        {"plan_idx": 1, "course": courses[1], "grade": "A", "score": 88, "max_score": 100},
        {"plan_idx": 2, "course": courses[2], "grade": "B+", "score": 81, "max_score": 100},
        {"plan_idx": 0, "course": courses[3], "grade": "A+", "score": 95, "max_score": 100},
        {"plan_idx": 1, "course": courses[4], "grade": "A", "score": 86, "max_score": 100},
    ]

    count = 0
    for result_data in results_data:
        if result_data["plan_idx"] < len(plans):
            plan = plans[result_data["plan_idx"]].name if hasattr(plans[result_data["plan_idx"]], 'name') else plans[result_data["plan_idx"]]

            existing = frappe.db.exists("Assessment Result", {
                "student": student_id,
                "assessment_plan": plan,
                "course": result_data["course"]
            })

            if not existing:
                ar = frappe.get_doc({
                    "doctype": "Assessment Result",
                    "student": student_id,
                    "assessment_plan": plan,
                    "course": result_data["course"],
                    "grade": result_data["grade"],
                    "total_score": result_data["score"],
                    "maximum_score": result_data["max_score"],
                    "docstatus": 1
                })
                ar.insert(ignore_permissions=True)
                ar.submit()
                count += 1
                print(f"  ✅ Created result: {result_data['course'][:30]}... - Grade: {result_data['grade']}")

    print(f"  📊 Total: {count} assessment results created")


def create_assessment_plans(courses):
    """Create basic assessment plans"""
    plans = []
    plan_types = ["Mid Semester", "End Semester"]

    for plan_type in plan_types:
        for course in courses[:2]:  # Create for first 2 courses only
            ap = frappe.get_doc({
                "doctype": "Assessment Plan",
                "assessment_name": f"{plan_type} - {course[:20]}",
                "course": course,
                "assessment_criteria": [
                    {"assessment_criteria": "Written Exam", "maximum_score": 100}
                ]
            })
            ap.insert(ignore_permissions=True)
            plans.append(ap.name)

    return plans


def update_student_cgpa(student_id):
    """Update student's CGPA field"""
    # Calculate CGPA: A+ = 9.0, A = 8.5, B+ = 8.0
    cgpa = 8.64  # Average of above grades

    frappe.db.set_value("Student", student_id, "custom_cgpa", cgpa)
    print(f"  ✅ Updated CGPA: {cgpa}")


def create_fee_records(student_id, student_name, program_name, academic_year):
    """Create fee records (both paid and pending)"""

    # Semester 1 - Paid
    fee1 = frappe.db.exists("Fees", {
        "student": student_id,
        "academic_year": academic_year,
        "fee_structure": ["like", "%Semester 1%"]
    })

    if not fee1:
        f1 = frappe.get_doc({
            "doctype": "Fees",
            "student": student_id,
            "student_name": student_name,
            "program": program_name,
            "academic_year": academic_year,
            "due_date": add_days(nowdate(), -60),
            "grand_total": 50000,
            "outstanding_amount": 0,  # Fully paid
            "docstatus": 1
        })
        f1.insert(ignore_permissions=True)
        f1.submit()
        print(f"  ✅ Created Semester 1 fee: ₹50,000 (Paid)")

    # Semester 2 - Partially paid
    fee2 = frappe.db.exists("Fees", {
        "student": student_id,
        "academic_year": academic_year,
        "outstanding_amount": [">", 0]
    })

    if not fee2:
        f2 = frappe.get_doc({
            "doctype": "Fees",
            "student": student_id,
            "student_name": student_name,
            "program": program_name,
            "academic_year": academic_year,
            "due_date": add_days(nowdate(), 15),  # Due in 15 days
            "grand_total": 50000,
            "outstanding_amount": 15000,  # ₹15,000 pending
            "docstatus": 1
        })
        f2.insert(ignore_permissions=True)
        f2.submit()
        print(f"  ✅ Created Semester 2 fee: ₹50,000 (₹15,000 pending)")


def create_library_transactions(student_id, student_name):
    """Create library book issue transactions"""

    # Create Library Member if not exists
    member = frappe.db.get_value("Library Member", {
        "library_member_type": "Student",
        "library_member_name": student_id
    })

    if not member:
        lm = frappe.get_doc({
            "doctype": "Library Member",
            "library_member_type": "Student",
            "library_member_name": student_id,
            "first_name": student_name
        })
        lm.insert(ignore_permissions=True)
        member = lm.name
        print(f"  ✅ Created Library Member: {member}")

    # Create some library items (books)
    books = create_library_items()

    # Issue 3 books
    issued_count = 0
    for i, book in enumerate(books[:3]):
        existing = frappe.db.exists("Library Transaction", {
            "library_member": member,
            "item": book,
            "type": "Issue"
        })

        if not existing:
            lt = frappe.get_doc({
                "doctype": "Library Transaction",
                "library_member": member,
                "item": book,
                "type": "Issue",
                "date": add_days(nowdate(), -(10 - i*3)),  # Issued at different dates
                "docstatus": 1
            })
            lt.insert(ignore_permissions=True)
            lt.submit()
            issued_count += 1

    print(f"  ✅ Issued {issued_count} books to student")


def create_library_items():
    """Create sample library book items"""
    books_data = [
        "Introduction to Algorithms",
        "Database System Concepts",
        "Operating System Concepts",
        "Computer Networks",
        "Software Engineering",
    ]

    created_books = []
    for book_name in books_data:
        item = frappe.db.get_value("Item", {"item_name": book_name})
        if not item:
            # Create item
            it = frappe.get_doc({
                "doctype": "Item",
                "item_code": book_name.replace(" ", "-").lower(),
                "item_name": book_name,
                "item_group": "Library Books",
                "is_stock_item": 1
            })
            it.insert(ignore_permissions=True)
            item = it.name

        created_books.append(item)

    return created_books


def create_assignments(student_group, courses):
    """Create assignments (both pending and completed)"""
    today = getdate(nowdate())

    assignments_data = [
        {"course": courses[0], "title": "Data Structures Assignment 1", "days_ahead": 7},
        {"course": courses[1], "title": "DBMS Project", "days_ahead": 14},
        {"course": courses[2], "title": "OS Lab Assignment", "days_ahead": 5},
    ]

    count = 0
    for assign_data in assignments_data:
        due_date = add_days(today, assign_data["days_ahead"])

        existing = frappe.db.exists("LMS Assignment", {
            "student_group": student_group,
            "title": assign_data["title"]
        })

        if not existing:
            la = frappe.get_doc({
                "doctype": "LMS Assignment",
                "title": assign_data["title"],
                "student_group": student_group,
                "course": assign_data["course"],
                "due_date": due_date,
                "max_score": 100,
                "docstatus": 1
            })
            la.insert(ignore_permissions=True)
            la.submit()
            count += 1
            print(f"  ✅ Created: {assign_data['title']} (Due: {due_date})")

    print(f"  📊 Total: {count} assignments created")


def create_announcements():
    """Create sample announcements"""
    today = getdate(nowdate())

    announcements_data = [
        {
            "title": "Mid Semester Examination Schedule Released",
            "description": "The mid-semester examination schedule has been published. Please check your exam timetable.",
            "priority": "High"
        },
        {
            "title": "Library Timing Change",
            "description": "The library will remain open until 10 PM during examination week.",
            "priority": "Medium"
        },
        {
            "title": "Guest Lecture on AI/ML",
            "description": "A guest lecture on Artificial Intelligence and Machine Learning will be conducted on Friday at 3 PM.",
            "priority": "Medium"
        },
    ]

    count = 0
    for ann_data in announcements_data:
        existing = frappe.db.exists("Announcement", {"title": ann_data["title"]})

        if not existing:
            ann = frappe.get_doc({
                "doctype": "Announcement",
                "title": ann_data["title"],
                "description": ann_data["description"],
                "publish_date": today,
                "expiry_date": add_days(today, 15),
                "for_students": 1
            })

            # Add priority if field exists
            if hasattr(ann, 'priority'):
                ann.priority = ann_data["priority"]

            ann.insert(ignore_permissions=True)
            count += 1
            print(f"  ✅ Created: {ann_data['title']}")

    print(f"  📊 Total: {count} announcements created")


if __name__ == "__main__":
    create_all_student_data()

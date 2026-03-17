#!/usr/bin/env python3
"""
Complete Student Portal Data Population Script
Creates all necessary data for demonstrating the student portal functionality
"""

import frappe
from datetime import datetime, timedelta
from frappe.utils import nowdate, getdate, add_days, add_months, get_first_day, get_last_day

def create_complete_portal_data():
    """Create all data needed for student portal demonstration"""

    frappe.init(site="university.local")
    frappe.connect()
    frappe.set_user("Administrator")

    print("=" * 70)
    print("CREATING COMPLETE STUDENT PORTAL DATA")
    print("=" * 70)

    student_name = "EDU-STU-2026-00002"
    student_email = "student@test.edu"

    # Step 1: Create Courses
    print("\n[1/10] Creating Courses...")
    courses = create_courses()

    # Step 2: Create Student Groups
    print("\n[2/10] Creating Student Groups...")
    student_groups = create_student_groups(student_name, courses)

    # Step 3: Create Course Schedules (Today's Classes)
    print("\n[3/10] Creating Today's Class Schedule...")
    create_course_schedules(student_groups)

    # Step 4: Create Student Attendance Records (for chart)
    print("\n[4/10] Creating Attendance Records (5 months history)...")
    create_attendance_records(student_name)

    # Step 5: Create Exam Schedules
    print("\n[5/10] Creating Exam Schedules...")
    create_exam_schedules(student_groups)

    # Step 6: Create Assessment Results
    print("\n[6/10] Creating Assessment Results...")
    create_assessment_results(student_name, courses)

    # Step 7: Create Fee Records
    print("\n[7/10] Creating Fee Records...")
    create_fee_records(student_name)

    # Step 8: Create LMS Assignments
    print("\n[8/10] Creating Assignments...")
    create_assignments(student_groups)

    # Step 9: Create Library Records
    print("\n[9/10] Creating Library Records...")
    create_library_records(student_name)

    # Step 10: Create Announcements
    print("\n[10/10] Creating Announcements...")
    create_announcements()

    frappe.db.commit()

    print("\n" + "=" * 70)
    print("✅ DATA CREATION COMPLETE!")
    print("=" * 70)
    print_summary(student_name)


def create_courses():
    """Create sample courses"""
    course_data = [
        {"code": "CS101", "name": "Data Structures and Algorithms", "credits": 4},
        {"code": "CS102", "name": "Database Management Systems", "credits": 4},
        {"code": "CS103", "name": "Operating Systems", "credits": 4},
        {"code": "CS104", "name": "Computer Networks", "credits": 3},
        {"code": "CS105", "name": "Software Engineering", "credits": 3},
    ]

    courses = []
    for data in course_data:
        course_name = data["name"]

        if frappe.db.exists("Course", course_name):
            print(f"  ✓ Course exists: {course_name}")
            courses.append(course_name)
            continue

        try:
            course = frappe.get_doc({
                "doctype": "Course",
                "course_name": data["name"],
                "course_code": data["code"]
            })
            course.insert(ignore_permissions=True)
            courses.append(course.name)
            print(f"  ✅ Created: {course.name}")
        except Exception as e:
            print(f"  ❌ Error creating {data['name']}: {str(e)}")

    return courses


def create_student_groups(student_name, courses):
    """Create student groups and add student to them"""
    program = "B.Tech Computer Science"
    academic_year = "2025-26"

    groups = []

    for idx, course in enumerate(courses[:4]):  # First 4 courses
        group_name = f"BCS-2026-Sem1-{course[:15]}"

        if frappe.db.exists("Student Group", group_name):
            print(f"  ✓ Group exists: {group_name}")
            groups.append(group_name)
            continue

        try:
            sg = frappe.get_doc({
                "doctype": "Student Group",
                "student_group_name": group_name,
                "group_based_on": "Course",
                "program": program,
                "course": course,
                "academic_year": academic_year,
                "students": [
                    {
                        "student": student_name,
                        "student_name": "Test Student",
                        "active": 1
                    }
                ]
            })
            sg.insert(ignore_permissions=True)
            groups.append(sg.name)
            print(f"  ✅ Created: {sg.name}")
        except Exception as e:
            print(f"  ❌ Error creating group for {course}: {str(e)}")

    return groups


def create_course_schedules(student_groups):
    """Create today's class schedules"""
    today = getdate(nowdate())

    schedules = [
        {"time": "09:00:00", "end": "10:30:00", "room": "Room 101"},
        {"time": "11:00:00", "end": "12:30:00", "room": "Room 102"},
        {"time": "14:00:00", "end": "15:30:00", "room": "Lab 1"},
        {"time": "16:00:00", "end": "17:00:00", "room": "Room 103"}
    ]

    for idx, sg in enumerate(student_groups[:4]):
        schedule_data = schedules[idx]

        try:
            cs = frappe.get_doc({
                "doctype": "Course Schedule",
                "student_group": sg,
                "schedule_date": today,
                "from_time": schedule_data["time"],
                "to_time": schedule_data["end"],
                "room": schedule_data["room"]
            })
            cs.insert(ignore_permissions=True)
            print(f"  ✅ Created schedule for {sg} at {schedule_data['time']}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")


def create_attendance_records(student_name):
    """Create 5 months of attendance data for the chart"""
    today = getdate(nowdate())

    # Generate attendance for last 5 months
    attendance_by_month = {
        0: {"present": 18, "absent": 2},  # Current month
        1: {"present": 22, "absent": 1},  # Last month
        2: {"present": 19, "absent": 3},  # 2 months ago
        3: {"present": 21, "absent": 2},  # 3 months ago
        4: {"present": 20, "absent": 2},  # 4 months ago
    }

    total_created = 0

    for months_ago, data in attendance_by_month.items():
        target_date = add_months(today, -months_ago)
        first_day = get_first_day(target_date)
        last_day = get_last_day(target_date)

        # Create present records
        for i in range(data["present"]):
            date = add_days(first_day, i)
            if date > last_day or date > today:
                continue

            try:
                att = frappe.get_doc({
                    "doctype": "Student Attendance",
                    "student": student_name,
                    "date": date,
                    "status": "Present"
                })
                att.insert(ignore_permissions=True)
                total_created += 1
            except Exception:
                pass  # Duplicate dates, ignore

        # Create absent records
        for i in range(data["absent"]):
            date = add_days(first_day, data["present"] + i)
            if date > last_day or date > today:
                continue

            try:
                att = frappe.get_doc({
                    "doctype": "Student Attendance",
                    "student": student_name,
                    "date": date,
                    "status": "Absent"
                })
                att.insert(ignore_permissions=True)
                total_created += 1
            except Exception:
                pass

    print(f"  ✅ Created {total_created} attendance records")


def create_exam_schedules(student_groups):
    """Create upcoming exam schedules"""
    today = getdate(nowdate())

    # Create exams for different dates
    exam_dates = [
        {"days": 3, "time": "10:00:00", "room": "Exam Hall 1"},
        {"days": 7, "time": "14:00:00", "room": "Exam Hall 2"},
        {"days": 10, "time": "10:00:00", "room": "Exam Hall 1"},
    ]

    # First ensure we have an Exam master
    exam_name = "Mid Semester Examination"
    if not frappe.db.exists("Exam", exam_name):
        try:
            exam = frappe.get_doc({
                "doctype": "Exam",
                "exam_name": exam_name,
                "exam_type": "Mid Semester"
            })
            exam.insert(ignore_permissions=True)
            print(f"  ✅ Created Exam: {exam_name}")
        except Exception as e:
            print(f"  ⚠️  Could not create Exam: {str(e)}")
            return

    # Create exam schedules
    for idx, sg in enumerate(student_groups[:3]):
        exam_data = exam_dates[idx]
        exam_date = add_days(today, exam_data["days"])

        try:
            es = frappe.get_doc({
                "doctype": "Exam Schedule",
                "exam": exam_name,
                "student_group": sg,
                "schedule_date": exam_date,
                "from_time": exam_data["time"],
                "to_time": add_time(exam_data["time"], hours=3),
                "room": exam_data["room"]
            })
            es.insert(ignore_permissions=True)
            es.submit()
            print(f"  ✅ Created exam schedule for {sg} on {exam_date}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")


def create_assessment_results(student_name, courses):
    """Create assessment results for CGPA calculation"""
    grades = [
        {"grade": "A", "score": 85, "max": 100},
        {"grade": "A-", "score": 82, "max": 100},
        {"grade": "B+", "score": 78, "max": 100},
        {"grade": "A", "score": 88, "max": 100},
    ]

    for idx, course in enumerate(courses[:4]):
        grade_data = grades[idx]

        try:
            ar = frappe.get_doc({
                "doctype": "Assessment Result",
                "student": student_name,
                "course": course,
                "total_score": grade_data["score"],
                "maximum_score": grade_data["max"],
                "grade": grade_data["grade"]
            })
            ar.insert(ignore_permissions=True)
            ar.submit()
            print(f"  ✅ Created result for {course}: {grade_data['grade']}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")


def create_fee_records(student_name):
    """Create fee records with pending amount"""
    today = getdate(nowdate())

    try:
        fee = frappe.get_doc({
            "doctype": "Fees",
            "student": student_name,
            "student_name": "Test Student",
            "program": "B.Tech Computer Science",
            "academic_year": "2025-26",
            "due_date": add_days(today, 15),
            "grand_total": 50000,
            "outstanding_amount": 15000
        })
        fee.insert(ignore_permissions=True)
        fee.submit()
        print(f"  ✅ Created fee record: ₹15,000 pending")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)}")


def create_assignments(student_groups):
    """Create LMS assignments"""
    today = getdate(nowdate())

    assignments = [
        {"title": "Data Structures Assignment 1", "days": 5, "marks": 100},
        {"title": "DBMS Lab Assignment", "days": 8, "marks": 50},
        {"title": "OS Theory Assignment", "days": 12, "marks": 100},
    ]

    for idx, sg in enumerate(student_groups[:3]):
        assign_data = assignments[idx]

        try:
            assignment = frappe.get_doc({
                "doctype": "LMS Assignment",
                "title": assign_data["title"],
                "student_group": sg,
                "due_date": add_days(today, assign_data["days"]),
                "max_score": assign_data["marks"]
            })
            assignment.insert(ignore_permissions=True)
            assignment.submit()
            print(f"  ✅ Created: {assign_data['title']}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")


def create_library_records(student_name):
    """Create library member and issue books"""

    # Create library member
    member_name = f"{student_name}-LIB"
    if not frappe.db.exists("Library Member", member_name):
        try:
            member = frappe.get_doc({
                "doctype": "Library Member",
                "library_member_type": "Student",
                "library_member_name": student_name,
                "first_name": "Test",
                "last_name": "Student"
            })
            member.insert(ignore_permissions=True)
            print(f"  ✅ Created Library Member")
        except Exception as e:
            print(f"  ⚠️  Error creating member: {str(e)}")
            return
    else:
        print(f"  ✓ Library Member exists")

    # Note: Creating Library Transactions requires Item doctype setup
    # which is complex. Skipping for now.
    print(f"  ⚠️  Library transactions skipped (requires Item setup)")


def create_announcements():
    """Create student announcements"""
    today = getdate(nowdate())

    announcements = [
        {
            "title": "Mid Semester Examination Schedule Released",
            "desc": "The mid-semester examination schedule has been published. Please check the Examinations page.",
            "days": 0
        },
        {
            "title": "Library Timings Extended",
            "desc": "Library will remain open till 10 PM during examination period.",
            "days": -1
        },
        {
            "title": "Assignment Submission Reminder",
            "desc": "All pending assignments must be submitted before the exam week.",
            "days": -2
        }
    ]

    for ann_data in announcements:
        try:
            ann = frappe.get_doc({
                "doctype": "Announcement",
                "title": ann_data["title"],
                "description": ann_data["desc"],
                "publish_date": add_days(today, ann_data["days"]),
                "expiry_date": add_days(today, 15)
            })
            ann.insert(ignore_permissions=True)
            print(f"  ✅ Created: {ann_data['title']}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")


def add_time(time_str, hours=0):
    """Add hours to a time string"""
    from datetime import datetime, timedelta
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    new_time = time_obj + timedelta(hours=hours)
    return new_time.strftime("%H:%M:%S")


def print_summary(student_name):
    """Print summary of created data"""

    # Count records
    attendance_count = frappe.db.count("Student Attendance", {"student": student_name})
    groups_count = frappe.db.count("Student Group Student", {"student": student_name, "active": 1})
    exams_count = frappe.db.count("Exam Schedule", {"docstatus": 1})
    fees_count = frappe.db.count("Fees", {"student": student_name})
    assignments_count = frappe.db.count("LMS Assignment", {"docstatus": 1})
    results_count = frappe.db.count("Assessment Result", {"student": student_name, "docstatus": 1})

    # Calculate attendance percentage
    if attendance_count > 0:
        present = frappe.db.count("Student Attendance", {"student": student_name, "status": "Present"})
        att_percentage = round((present / attendance_count) * 100, 1)
    else:
        att_percentage = 0

    print(f"\nStudent: {student_name}")
    print(f"  📚 Enrolled Courses: {groups_count}")
    print(f"  ✅ Attendance Records: {attendance_count} ({att_percentage}% present)")
    print(f"  📝 Exam Schedules: {exams_count}")
    print(f"  💰 Fee Records: {fees_count}")
    print(f"  📄 Assignments: {assignments_count}")
    print(f"  🎓 Assessment Results: {results_count}")

    print(f"\n🌐 Access the portal:")
    print(f"   URL: http://localhost:18000/student_portal")
    print(f"   Login: student@test.edu")

    print(f"\n✨ All pages should now display data:")
    print(f"   ✅ Dashboard - Stats, charts, today's classes")
    print(f"   ✅ Examinations - Upcoming exams")
    print(f"   ✅ Attendance - 5-month trend chart")
    print(f"   ✅ Academics - Assessment results")
    print(f"   ✅ Fees - Pending ₹15,000")
    print(f"   ✅ Assignments - {assignments_count} pending")


if __name__ == "__main__":
    create_complete_portal_data()

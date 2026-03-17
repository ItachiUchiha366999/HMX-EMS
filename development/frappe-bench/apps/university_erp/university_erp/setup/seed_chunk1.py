"""
Seed Chunk 1: Phases 2-10
- Phase 2 gaps: Assessment Group, Fee Structure, Assessment Criteria (1 missing)
- Phase 3 gaps: Leave Policy, Salary Structure, Employee Group, Salary Component (1 missing)
- Phase 4 gaps: Course Enrollment
- Phase 6: Timetable Slot, Elective Course Group, Admission Cycle, Admission Criteria, Seat Matrix
- Phase 7: Question Bank, Exam Schedule, Hall Ticket, Internal Assessment, Question Paper Template, External Examiner
- Phase 8 gaps: Fee Category, Scholarship Type, Fee Payment, Student Scholarship
- Phase 9: Faculty Profile, Teaching Assignment, Student Feedback, Workload Distributor
- Phase 10: Hostel Building, Hostel Room, Mess Menu, Hostel Allocation, Hostel Attendance, Hostel Maintenance Request
"""
import frappe
import random
from datetime import date, timedelta, datetime

def run():
    frappe.flags.ignore_permissions = True
    frappe.flags.mute_emails = True

    # ============================================================
    # REFERENCE DATA
    # ============================================================
    COMPANY = "Hanumatrix"
    ACADEMIC_YEAR = "2025-26"
    ACADEMIC_TERM = "2025-26 (Semester 1)"
    GRADING_SCALE = "University 10-Point Scale"

    programs = {p.name: p for p in frappe.get_all("Program", fields=["name", "program_name"])}
    courses = {c.name: c for c in frappe.get_all("Course", fields=["name", "course_name"])}
    students = frappe.get_all("Student", fields=["name", "student_name", "student_email_id"], order_by="name")
    employees = frappe.get_all("Employee", fields=["name", "employee_name", "designation", "department"], order_by="name")
    instructors = frappe.get_all("Instructor", fields=["name", "instructor_name", "employee"], order_by="name")
    enrollments = frappe.get_all("Program Enrollment", fields=["name", "student", "program"], order_by="name")
    student_groups = frappe.get_all("Student Group", fields=["name", "program", "batch"], order_by="name")
    rooms = [r.name for r in frappe.get_all("Room", order_by="name")]
    fees_list = frappe.get_all("Fees", fields=["name", "student", "program", "grand_total"], order_by="name")

    # Map students to their enrollment
    student_enrollment = {e.student: e for e in enrollments}
    # Map students to their fees
    student_fees = {f.student: f for f in fees_list}

    # Course-Program mapping (CSE courses for B.Tech CS, ECE for B.Tech Electronics, etc.)
    cse_courses = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks",
                   "Web Technologies", "Artificial Intelligence", "Software Engineering"]
    ece_courses = ["Digital Electronics", "Microprocessors"]
    common_courses = ["Engineering Mathematics", "Communication Skills", "Environmental Science"]

    # Faculty employees (first 10 are faculty)
    faculty_employees = employees[:10]

    # Course to instructor mapping
    course_instructor = {}
    for i, course_name in enumerate(list(courses.keys())[:10]):
        if i < len(instructors):
            course_instructor[course_name] = instructors[i]

    print("=== Reference data loaded ===")

    # ============================================================
    # PHASE 2 GAPS
    # ============================================================
    print("\n--- Phase 2: Assessment Group, Fee Structure ---")

    # Assessment Group (tree doctype)
    if frappe.db.count("Assessment Group") == 0:
        # Root node
        root = frappe.get_doc({"doctype": "Assessment Group", "assessment_group_name": "All Assessment Groups", "is_group": 1})
        root.flags.ignore_mandatory = True
        root.insert(ignore_if_duplicate=True)

        for name in ["Internal Assessment", "External Assessment", "Final Assessment"]:
            doc = frappe.get_doc({
                "doctype": "Assessment Group",
                "assessment_group_name": name,
                "parent_assessment_group": "All Assessment Groups",
                "is_group": 0
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_if_duplicate=True)
        print("  Created 4 Assessment Groups")

    # Missing Assessment Criteria
    if frappe.db.count("Assessment Criteria") < 6:
        for ac in ["Attendance"]:
            if not frappe.db.exists("Assessment Criteria", ac):
                frappe.get_doc({"doctype": "Assessment Criteria", "assessment_criteria": ac}).insert()
        print("  Created missing Assessment Criteria")

    # Fee Structure (4 - one per program)
    if frappe.db.count("Fee Structure") == 0:
        fee_configs = [
            ("B.Tech Computer Science", [("Tuition Fee", 50000), ("Lab Fee", 10000), ("Library Fee", 5000), ("Hostel Fee", 10000)]),
            ("B.Tech Electronics", [("Tuition Fee", 45000), ("Lab Fee", 10000), ("Library Fee", 5000), ("Hostel Fee", 10000)]),
            ("M.Tech Computer Science", [("Tuition Fee", 40000), ("Lab Fee", 10000), ("Library Fee", 5000), ("Hostel Fee", 5000)]),
            ("MBA", [("Tuition Fee", 60000), ("Lab Fee", 5000), ("Library Fee", 5000), ("Hostel Fee", 10000)]),
        ]
        for prog, components in fee_configs:
            if prog in programs:
                doc = frappe.get_doc({
                    "doctype": "Fee Structure",
                    "program": prog,
                    "academic_year": ACADEMIC_YEAR,
                    "receivable_account": "Debtors - HMX",
                    "income_account": "Sales - HMX",
                    "cost_center": "Main - HMX",
                    "company": COMPANY,
                    "components": [{"fees_category": comp[0], "amount": comp[1]} for comp in components]
                })
                try:
                    doc.insert(ignore_if_duplicate=True)
                except Exception as e:
                    print(f"  Fee Structure {prog}: {e}")
        print("  Created 4 Fee Structures")

    # ============================================================
    # PHASE 3 GAPS
    # ============================================================
    print("\n--- Phase 3: Leave Policy, Salary Structure, Employee Group ---")

    # Employee Group
    if frappe.db.count("Employee Group") == 0:
        for name in ["Teaching Staff", "Non-Teaching Staff", "Administrative Staff"]:
            frappe.get_doc({"doctype": "Employee Group", "employee_group_name": name}).insert(ignore_if_duplicate=True)
        print("  Created 3 Employee Groups")

    # Missing Salary Component
    existing_sc = [s.name for s in frappe.get_all("Salary Component")]
    for sc in ["Dearness Allowance", "Transport Allowance"]:
        if sc not in existing_sc:
            frappe.get_doc({"doctype": "Salary Component", "salary_component": sc, "type": "Earning"}).insert(ignore_if_duplicate=True)
    print("  Ensured 8+ Salary Components")

    # Leave Policy
    if frappe.db.count("Leave Policy") == 0:
        for title, details in [
            ("Faculty Leave Policy", [("Casual Leave", 12), ("Privilege Leave", 15), ("Sick Leave", 10)]),
            ("Non-Teaching Leave Policy", [("Casual Leave", 10), ("Privilege Leave", 12), ("Sick Leave", 8)]),
        ]:
            frappe.get_doc({
                "doctype": "Leave Policy",
                "title": title,
                "leave_policy_details": [{"leave_type": lt, "annual_allocation": alloc} for lt, alloc in details]
            }).insert(ignore_if_duplicate=True)
        print("  Created 2 Leave Policies")

    # Salary Structure
    if frappe.db.count("Salary Structure") == 0:
        for ss_name, is_active in [("Faculty Salary Structure", "Yes"), ("Admin Salary Structure", "Yes")]:
            frappe.get_doc({
                "doctype": "Salary Structure",
                "name": ss_name,
                "__newname": ss_name,
                "company": COMPANY,
                "is_active": is_active,
                "payroll_frequency": "Monthly",
                "currency": "INR",
                "earnings": [
                    {"salary_component": "Basic", "formula": "base * 0.5", "amount_based_on_formula": 1},
                    {"salary_component": "House Rent Allowance", "formula": "base * 0.2", "amount_based_on_formula": 1},
                ],
                "deductions": [
                    {"salary_component": "Provident Fund", "formula": "base * 0.12", "amount_based_on_formula": 1},
                ]
            }).insert(ignore_if_duplicate=True)
        print("  Created 2 Salary Structures")

    frappe.db.commit()

    # ============================================================
    # PHASE 4 GAP: Course Enrollment
    # ============================================================
    print("\n--- Phase 4: Course Enrollment ---")

    if frappe.db.count("Course Enrollment") == 0:
        # Assign courses based on program
        program_courses = {
            "B.Tech Computer Science": ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Engineering Mathematics"],
            "B.Tech Electronics": ["Digital Electronics", "Microprocessors", "Engineering Mathematics"],
            "M.Tech Computer Science": ["Artificial Intelligence", "Web Technologies", "Software Engineering"],
            "MBA": ["Communication Skills", "Environmental Science"],
        }
        count = 0
        for enr in enrollments:
            course_list = program_courses.get(enr.program, [])
            for course_name in course_list[:3]:  # Max 3 courses per student
                if course_name in courses:
                    try:
                        frappe.get_doc({
                            "doctype": "Course Enrollment",
                            "program_enrollment": enr.name,
                            "course": course_name,
                            "student": enr.student,
                            "enrollment_date": "2025-07-15",
                        }).insert(ignore_if_duplicate=True)
                        count += 1
                    except Exception:
                        pass
        frappe.db.commit()
        print(f"  Created {count} Course Enrollments")

    # ============================================================
    # PHASE 6: Academics & Admissions
    # ============================================================
    print("\n--- Phase 6: Timetable, Admissions ---")

    # Timetable Slots
    if frappe.db.count("Timetable Slot") == 0:
        slots = [
            ("Period 1", "09:00:00", "09:50:00", "Lecture"),
            ("Period 2", "10:00:00", "10:50:00", "Lecture"),
            ("Period 3", "11:00:00", "11:50:00", "Lecture"),
            ("Period 4", "12:00:00", "12:50:00", "Lecture"),
            ("Lunch", "13:00:00", "14:00:00", "Break"),
            ("Period 5", "14:00:00", "14:50:00", "Tutorial"),
            ("Period 6", "15:00:00", "15:50:00", "Practical"),
            ("Period 7", "16:00:00", "16:50:00", "Practical"),
        ]
        for day in ["Monday", "Tuesday", "Wednesday"]:
            for slot_name, start, end, stype in slots:
                if stype != "Break":
                    frappe.get_doc({
                        "doctype": "Timetable Slot",
                        "slot_name": f"{day} {slot_name}",
                        "day": day,
                        "start_time": start,
                        "end_time": end,
                        "slot_type": stype,
                    }).insert(ignore_if_duplicate=True)
        print("  Created 21 Timetable Slots")

    # Elective Course Group
    if frappe.db.count("Elective Course Group") == 0:
        for gname, prog, sem, etype in [
            ("Open Elective Group 1", "B.Tech Computer Science", 5, "GE"),
            ("Department Elective Group 1", "B.Tech Computer Science", 5, "DSE"),
        ]:
            frappe.get_doc({
                "doctype": "Elective Course Group",
                "group_name": gname,
                "program": prog,
                "semester": sem,
                "elective_type": etype,
                "courses": [
                    {"course": "Web Technologies"},
                    {"course": "Artificial Intelligence"},
                ]
            }).insert(ignore_if_duplicate=True)
        print("  Created 2 Elective Course Groups")

    # Admission Cycle
    if frappe.db.count("Admission Cycle") == 0:
        ac = frappe.get_doc({
            "doctype": "Admission Cycle",
            "cycle_name": "Admission 2025-26",
            "cycle_code": "ADM-2025",
            "academic_year": ACADEMIC_YEAR,
            "status": "Completed",
            "application_start_date": "2025-04-01",
            "application_deadline": "2025-06-30",
        })
        ac.insert(ignore_if_duplicate=True)
        print("  Created 1 Admission Cycle")

        # Admission Criteria
        for prog, cat in [
            ("B.Tech Computer Science", "General"),
            ("B.Tech Electronics", "General"),
            ("M.Tech Computer Science", "General"),
        ]:
            frappe.get_doc({
                "doctype": "Admission Criteria",
                "admission_cycle": ac.name,
                "program": prog,
                "category": cat,
                "min_percentage": 60,
            }).insert(ignore_if_duplicate=True)
        print("  Created 3 Admission Criteria")

        # Seat Matrix
        for prog, seats in [
            ("B.Tech Computer Science", 60),
            ("B.Tech Electronics", 30),
            ("M.Tech Computer Science", 20),
            ("MBA", 30),
        ]:
            frappe.get_doc({
                "doctype": "Seat Matrix",
                "admission_cycle": ac.name,
                "program": prog,
                "total_seats": seats,
            }).insert(ignore_if_duplicate=True)
        print("  Created 4 Seat Matrices")

    frappe.db.commit()

    # ============================================================
    # PHASE 7: Examinations
    # ============================================================
    print("\n--- Phase 7: Examinations ---")

    # Question Bank (30 questions)
    if frappe.db.count("Question Bank") == 0:
        q_courses = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Artificial Intelligence", "Digital Electronics"]
        q_types = ["MCQ", "Short Answer", "Long Answer", "True/False", "Numerical"]
        difficulties = ["Easy", "Medium", "Hard"]
        blooms = ["L1 - Remember", "L2 - Understand", "L3 - Apply", "L4 - Analyze", "L5 - Evaluate"]
        count = 0
        for course in q_courses:
            if course not in courses:
                continue
            for i in range(5):
                qt = q_types[i % len(q_types)]
                doc_data = {
                    "doctype": "Question Bank",
                    "question_text": f"<p>Sample question {i+1} for {course}: Explain the concept of {'arrays' if i==0 else 'linked lists' if i==1 else 'trees' if i==2 else 'graphs' if i==3 else 'hashing'}.</p>",
                    "question_type": qt,
                    "course": course,
                    "difficulty_level": difficulties[i % 3],
                    "blooms_taxonomy": blooms[i % 5],
                    "marks": [2, 5, 10, 1, 5][i % 5],
                }
                if qt == "MCQ":
                    doc_data["options"] = [
                        {"option_text": "Option A", "is_correct": 1},
                        {"option_text": "Option B", "is_correct": 0},
                        {"option_text": "Option C", "is_correct": 0},
                        {"option_text": "Option D", "is_correct": 0},
                    ]
                try:
                    frappe.get_doc(doc_data).insert(ignore_if_duplicate=True)
                    count += 1
                except Exception as e:
                    print(f"  QB error: {e}")
        print(f"  Created {count} Question Bank entries")

    # Exam Schedule (6)
    exam_schedules = []
    if frappe.db.count("Exam Schedule") == 0:
        exam_courses = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Artificial Intelligence", "Digital Electronics"]
        base_date = date(2025, 10, 15)
        for i, course in enumerate(exam_courses):
            if course not in courses:
                continue
            d = base_date + timedelta(days=i * 2)
            doc = frappe.get_doc({
                "doctype": "Exam Schedule",
                "course": course,
                "academic_term": ACADEMIC_TERM,
                "exam_type": "Mid-Term",
                "exam_date": str(d),
                "start_time": "10:00:00",
                "end_time": "13:00:00",
                "venue": rooms[i % len(rooms)],
                "total_marks": 50,
            })
            try:
                doc.insert(ignore_if_duplicate=True)
                exam_schedules.append(doc)
            except Exception as e:
                print(f"  Exam Schedule error: {e}")
        print(f"  Created {len(exam_schedules)} Exam Schedules")

    # Hall Ticket (for first 30 students)
    if frappe.db.count("Hall Ticket") == 0:
        count = 0
        for student in students[:30]:
            try:
                frappe.get_doc({
                    "doctype": "Hall Ticket",
                    "student": student.name,
                    "academic_term": ACADEMIC_TERM,
                }).insert(ignore_if_duplicate=True)
                count += 1
            except Exception as e:
                if "Duplicate" not in str(e):
                    print(f"  Hall Ticket error for {student.name}: {e}")
        print(f"  Created {count} Hall Tickets")

    # Internal Assessment (12)
    if frappe.db.count("Internal Assessment") == 0:
        ia_courses = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Artificial Intelligence", "Digital Electronics"]
        count = 0
        for course in ia_courses:
            if course not in courses:
                continue
            for ia_num in [1, 2]:
                d = date(2025, 8, 15) if ia_num == 1 else date(2025, 9, 20)
                try:
                    frappe.get_doc({
                        "doctype": "Internal Assessment",
                        "assessment_name": f"IA-{ia_num} {course}",
                        "assessment_type": "Written Test",
                        "academic_year": ACADEMIC_YEAR,
                        "academic_term": ACADEMIC_TERM,
                        "course": course,
                        "assessment_date": str(d),
                        "maximum_marks": 25,
                    }).insert(ignore_if_duplicate=True)
                    count += 1
                except Exception as e:
                    print(f"  IA error: {e}")
        print(f"  Created {count} Internal Assessments")

    # Question Paper Template (3)
    if frappe.db.count("Question Paper Template") == 0:
        for tname, etype, marks, dur in [
            ("Mid-Semester Template", "Mid-Term", 50, 120),
            ("End-Semester Template", "End-Term", 100, 180),
            ("Practical Exam Template", "Practical", 50, 120),
        ]:
            try:
                frappe.get_doc({
                    "doctype": "Question Paper Template",
                    "template_name": tname,
                    "course": "Data Structures",
                    "exam_type": etype,
                    "total_marks": marks,
                    "duration_minutes": dur,
                    "sections": [{
                        "section_name": "Section A",
                        "section_marks": marks,
                        "num_questions": 5,
                        "question_type": "Short Answer",
                    }]
                }).insert(ignore_if_duplicate=True)
            except Exception as e:
                print(f"  QPT error: {e}")
        print("  Created 3 Question Paper Templates")

    # External Examiner (3)
    if frappe.db.count("External Examiner") == 0:
        for name, org, email in [
            ("Dr. Suresh Babu", "IIT Delhi", "suresh.babu@iitd.ac.in"),
            ("Dr. Meena Kumari", "NIT Warangal", "meena.k@nitw.ac.in"),
            ("Dr. Arvind Patel", "BITS Pilani", "arvind.p@bits-pilani.ac.in"),
        ]:
            frappe.get_doc({
                "doctype": "External Examiner",
                "examiner_name": name,
                "organization": org,
                "email": email,
                "status": "Active",
            }).insert(ignore_if_duplicate=True)
        print("  Created 3 External Examiners")

    frappe.db.commit()

    # ============================================================
    # PHASE 8 GAPS: Finance
    # ============================================================
    print("\n--- Phase 8: Fee Category, Scholarship, Payments ---")

    # Fee Category
    if frappe.db.count("Fee Category") == 0:
        for cat, code, ftype in [
            ("Tuition Fee", "TF", "Tuition"),
            ("Examination Fee", "EF", "Examination"),
            ("Hostel Fee", "HF", "Hostel"),
            ("Library Fee", "LF", "Library"),
            ("Laboratory Fee", "LAB", "Laboratory"),
        ]:
            frappe.get_doc({
                "doctype": "Fee Category",
                "category_name": cat,
                "category_code": code,
                "fee_type": ftype,
            }).insert(ignore_if_duplicate=True)
        print("  Created 5 Fee Categories")

    # Scholarship Type
    if frappe.db.count("Scholarship Type") == 0:
        for sname, scode, stype in [
            ("Merit Scholarship", "MERIT", "Merit-based"),
            ("Need-based Scholarship", "NEED", "Need-based"),
            ("Sports Scholarship", "SPORTS", "Sports"),
        ]:
            frappe.get_doc({
                "doctype": "Scholarship Type",
                "scholarship_name": sname,
                "scholarship_code": scode,
                "type": stype,
            }).insert(ignore_if_duplicate=True)
        print("  Created 3 Scholarship Types")

    # Fee Payment (20)
    if frappe.db.count("Fee Payment") == 0:
        modes = ["Cash", "Wire Transfer", "Credit Card", "Cheque"]
        count = 0
        for fee in fees_list[:20]:
            try:
                frappe.get_doc({
                    "doctype": "Fee Payment",
                    "fee": fee.name,
                    "student": fee.student,
                    "amount": fee.grand_total * 0.7,  # 70% paid
                    "payment_date": "2025-08-01",
                    "payment_mode": modes[count % len(modes)],
                }).insert(ignore_if_duplicate=True)
                count += 1
            except Exception as e:
                print(f"  Fee Payment error: {e}")
        print(f"  Created {count} Fee Payments")

    # Student Scholarship (5)
    if frappe.db.count("Student Scholarship") == 0:
        scholarship_types = frappe.get_all("Scholarship Type", limit=3)
        if scholarship_types:
            for i in range(5):
                try:
                    frappe.get_doc({
                        "doctype": "Student Scholarship",
                        "student": students[i].name,
                        "scholarship_type": scholarship_types[i % len(scholarship_types)].name,
                        "valid_from": "2025-07-01",
                        "valid_till": "2026-06-30",
                        "scholarship_amount": [10000, 15000, 20000, 10000, 12000][i],
                    }).insert(ignore_if_duplicate=True)
                except Exception as e:
                    print(f"  Scholarship error: {e}")
            print("  Created 5 Student Scholarships")

    frappe.db.commit()

    # ============================================================
    # PHASE 9: Faculty Management
    # ============================================================
    print("\n--- Phase 9: Faculty ---")

    # Faculty Profile (10)
    if frappe.db.count("Faculty Profile") == 0:
        for emp in faculty_employees:
            try:
                frappe.get_doc({
                    "doctype": "Faculty Profile",
                    "employee": emp.name,
                    "department": emp.department,
                    "designation": emp.designation,
                }).insert(ignore_if_duplicate=True)
            except Exception as e:
                print(f"  Faculty Profile error: {e}")
        print("  Created 10 Faculty Profiles")

    # Teaching Assignment (12)
    if frappe.db.count("Teaching Assignment") == 0:
        ta_data = [
            ("Data Structures", "B.Tech Computer Science", 0),
            ("Database Systems", "B.Tech Computer Science", 1),
            ("Operating Systems", "B.Tech Computer Science", 2),
            ("Computer Networks", "B.Tech Computer Science", 3),
            ("Web Technologies", "B.Tech Computer Science", 4),
            ("Artificial Intelligence", "B.Tech Computer Science", 5),
            ("Software Engineering", "B.Tech Computer Science", 6),
            ("Engineering Mathematics", "B.Tech Computer Science", 7),
            ("Digital Electronics", "B.Tech Electronics", 8),
            ("Microprocessors", "B.Tech Electronics", 9),
            ("Communication Skills", "MBA", 0),
            ("Environmental Science", "B.Tech Computer Science", 1),
        ]
        count = 0
        for course, prog, instr_idx in ta_data:
            if course not in courses or instr_idx >= len(instructors):
                continue
            try:
                frappe.get_doc({
                    "doctype": "Teaching Assignment",
                    "academic_year": ACADEMIC_YEAR,
                    "academic_term": ACADEMIC_TERM,
                    "course": course,
                    "program": prog,
                    "instructor": instructors[instr_idx].employee,
                    "room": rooms[count % len(rooms)],
                }).insert(ignore_if_duplicate=True)
                count += 1
            except Exception as e:
                print(f"  TA error: {e}")
        print(f"  Created {count} Teaching Assignments")

    # Student Feedback (10)
    if frappe.db.count("Student Feedback") == 0:
        fb_courses = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Artificial Intelligence"]
        count = 0
        for i, course in enumerate(fb_courses):
            if course not in courses:
                continue
            instr_idx = i % len(instructors)
            for j in range(2):  # 2 students per course
                student = students[j + i * 2]
                try:
                    frappe.get_doc({
                        "doctype": "Student Feedback",
                        "student": student.name,
                        "academic_year": ACADEMIC_YEAR,
                        "academic_term": ACADEMIC_TERM,
                        "course": course,
                        "instructor": instructors[instr_idx].employee,
                        "subject_knowledge": random.randint(3, 5),
                        "teaching_methodology": random.randint(3, 5),
                        "communication_skills": random.randint(3, 5),
                        "availability": random.randint(3, 5),
                        "course_coverage": random.randint(3, 5),
                        "overall_rating": random.randint(3, 5),
                    }).insert(ignore_if_duplicate=True)
                    count += 1
                except Exception as e:
                    print(f"  Feedback error: {e}")
        print(f"  Created {count} Student Feedbacks")

    # Workload Distributor (1)
    if frappe.db.count("Workload Distributor") == 0:
        try:
            frappe.get_doc({
                "doctype": "Workload Distributor",
                "academic_year": ACADEMIC_YEAR,
                "academic_term": ACADEMIC_TERM,
                "department": "Computer Science",
            }).insert(ignore_if_duplicate=True)
            print("  Created 1 Workload Distributor")
        except Exception as e:
            print(f"  WD error: {e}")

    frappe.db.commit()

    # ============================================================
    # PHASE 10: Hostel
    # ============================================================
    print("\n--- Phase 10: Hostel ---")

    # Hostel Building (3)
    hostel_buildings = []
    if frappe.db.count("Hostel Building") == 0:
        for bname, bcode, btype in [
            ("Boys Hostel", "BH", "Boys"),
            ("Girls Hostel", "GH", "Girls"),
            ("PG Hostel", "PGH", "Co-Ed"),
        ]:
            doc = frappe.get_doc({
                "doctype": "Hostel Building",
                "building_name": bname,
                "building_code": bcode,
                "hostel_type": btype,
                "total_rooms": 10,
                "mess": "Central Mess" if bcode != "PGH" else "PG Mess",
            })
            doc.insert(ignore_if_duplicate=True)
            hostel_buildings.append(doc.name)
        print("  Created 3 Hostel Buildings")
    else:
        hostel_buildings = [b.name for b in frappe.get_all("Hostel Building", order_by="name")]

    # Hostel Room (30 - 10 per building)
    hostel_rooms = []
    if frappe.db.count("Hostel Room") == 0:
        room_types = ["Single", "Double", "Triple"]
        for bldg in hostel_buildings:
            for rnum in range(1, 11):
                rtype = room_types[rnum % 3]
                cap = {"Single": 1, "Double": 2, "Triple": 3}[rtype]
                doc = frappe.get_doc({
                    "doctype": "Hostel Room",
                    "hostel_building": bldg,
                    "room_number": f"{rnum:03d}",
                    "room_type": rtype,
                    "capacity": cap,
                    "status": "Available",
                })
                doc.insert(ignore_if_duplicate=True)
                hostel_rooms.append(doc.name)
        print(f"  Created {len(hostel_rooms)} Hostel Rooms")
    else:
        hostel_rooms = [r.name for r in frappe.get_all("Hostel Room", order_by="name")]

    # Mess Menu (2)
    if frappe.db.count("Mess Menu") == 0:
        for mess_name in ["Central Mess", "PG Mess"]:
            try:
                frappe.get_doc({
                    "doctype": "Mess Menu",
                    "mess": mess_name,
                    "week_start_date": "2025-10-06",
                    "menu_items": [
                        {"day": "Monday", "meal_type": "Breakfast", "items": "Idli, Sambar, Coffee"},
                        {"day": "Monday", "meal_type": "Lunch", "items": "Rice, Dal, Sabzi, Roti, Curd"},
                        {"day": "Monday", "meal_type": "Dinner", "items": "Chapati, Paneer, Rice, Dal"},
                        {"day": "Tuesday", "meal_type": "Breakfast", "items": "Dosa, Chutney, Coffee"},
                        {"day": "Tuesday", "meal_type": "Lunch", "items": "Rice, Rajma, Salad, Roti"},
                        {"day": "Tuesday", "meal_type": "Dinner", "items": "Pulao, Raita, Dal Fry"},
                        {"day": "Wednesday", "meal_type": "Breakfast", "items": "Poha, Tea, Banana"},
                    ]
                }).insert(ignore_if_duplicate=True)
            except Exception as e:
                print(f"  Mess Menu error: {e}")
        print("  Created 2 Mess Menus")

    frappe.db.commit()

    # Hostel Allocation (15)
    if frappe.db.count("Hostel Allocation") == 0:
        count = 0
        for i in range(15):
            student = students[i]
            bldg = hostel_buildings[0] if i < 10 else hostel_buildings[2]  # Boys or PG
            room = hostel_rooms[i % len(hostel_rooms)]
            try:
                frappe.get_doc({
                    "doctype": "Hostel Allocation",
                    "naming_series": "HA-.YYYY.-",
                    "student": student.name,
                    "academic_year": ACADEMIC_YEAR,
                    "from_date": "2025-07-15",
                    "to_date": "2026-06-30",
                    "hostel_building": bldg,
                    "room": room,
                }).insert(ignore_if_duplicate=True)
                count += 1
            except Exception as e:
                print(f"  Hostel Allocation error: {e}")
        frappe.db.commit()
        print(f"  Created {count} Hostel Allocations")

    # Hostel Attendance (30 - 2 days for 15 students)
    if frappe.db.count("Hostel Attendance") == 0:
        count = 0
        statuses = ["Present", "Present", "Present", "Present", "Absent"]  # 80% present
        for d_offset in range(2):
            att_date = date(2025, 10, 6) + timedelta(days=d_offset)
            for i in range(15):
                student = students[i]
                bldg = hostel_buildings[0] if i < 10 else hostel_buildings[2]
                try:
                    frappe.get_doc({
                        "doctype": "Hostel Attendance",
                        "student": student.name,
                        "hostel_building": bldg,
                        "attendance_date": str(att_date),
                        "status": statuses[(i + d_offset) % len(statuses)],
                    }).insert(ignore_if_duplicate=True)
                    count += 1
                except Exception as e:
                    print(f"  Hostel Att error: {e}")
        frappe.db.commit()
        print(f"  Created {count} Hostel Attendance records")

    # Hostel Maintenance Request (2)
    if frappe.db.count("Hostel Maintenance Request") == 0:
        for subj, rtype, status, desc in [
            ("WiFi not working", "Electrical", "Resolved", "WiFi router in Room 003 is not working since yesterday"),
            ("Water leakage", "Plumbing", "Open", "Water leaking from bathroom tap in Room 005"),
        ]:
            try:
                frappe.get_doc({
                    "doctype": "Hostel Maintenance Request",
                    "request_date": "2025-10-05",
                    "building": hostel_buildings[0],
                    "request_type": rtype,
                    "subject": subj,
                    "description": desc,
                    "status": status,
                    "priority": "Medium",
                    "requested_by": students[0].name,
                }).insert(ignore_if_duplicate=True)
            except Exception as e:
                print(f"  Maint Req error: {e}")
        print("  Created 2 Hostel Maintenance Requests")

    frappe.db.commit()
    print("\n=== CHUNK 1 COMPLETE ===")


if __name__ == "__main__":
    run()

"""
Comprehensive Demo Data Seeding Script
Seeds all missing doctypes across university_erp modules with realistic data.
Idempotent: each section checks existing count before inserting.
"""
import frappe
import random
from datetime import date, timedelta

frappe.init(site='university.local', sites_path='/workspace/development/frappe-bench/sites')
frappe.connect()
frappe.set_user('Administrator')


def ins(doctype, fields, submittable=False):
    doc = frappe.new_doc(doctype)
    for k, v in fields.items():
        setattr(doc, k, v)
    doc.flags.ignore_validate = True
    doc.flags.ignore_links = True
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    if submittable:
        frappe.db.set_value(doctype, doc.name, 'docstatus', 1)
        frappe.db.commit()
    return doc.name


def log(msg):
    print(f"  >> {msg}")


# ─── REFERENCE DATA ─────────────────────────────────────────────────────────────
students = frappe.db.sql("SELECT name, student_name FROM `tabStudent` ORDER BY name", as_dict=True)
student_ids = [s.name for s in students]
student_names = {s.name: s.student_name for s in students}

programs = ['B.Tech Computer Science', 'B.Tech Electronics', 'M.Tech Computer Science', 'MBA']
courses_list = ['Data Structures', 'Database Systems', 'Operating Systems', 'Computer Networks',
                'Web Technologies', 'Artificial Intelligence', 'Digital Electronics',
                'Microprocessors', 'Engineering Mathematics', 'Communication Skills',
                'Software Engineering', 'Environmental Science']

employees = frappe.db.sql("SELECT name, employee_name FROM `tabEmployee` ORDER BY name LIMIT 10", as_dict=True)
emp_ids = [e.name for e in employees]

pe_data = frappe.db.sql(
    "SELECT name, student, program, academic_year, academic_term FROM `tabProgram Enrollment` ORDER BY name",
    as_dict=True
)
pe_by_student = {p.student: p for p in pe_data}

fees_data = frappe.db.sql(
    "SELECT name, student, program, grand_total, receivable_account, income_account, company, cost_center FROM `tabFees`",
    as_dict=True
)

discs = frappe.db.sql("SELECT name, student, title FROM `tabLMS Discussion`", as_dict=True)

academic_year = '2025-26'
academic_term = '2025-26 (Semester 1)'
company = 'Hanumatrix'
receivable_account = 'Debtors - HMX'
income_account = 'Sales - HMX'
main_cost_center = 'Main - HMX'

# ─── 1. PROGRAM COURSES (fix CO PO Mapping Matrix filter) ───────────────────────
print("\n=== 1. Program Courses ===")
pc_count = frappe.db.sql("SELECT COUNT(*) as c FROM `tabProgram Course`", as_dict=True)[0].c
if pc_count == 0:
    program_course_map = {
        'B.Tech Computer Science': ['Data Structures', 'Database Systems', 'Operating Systems',
                                     'Computer Networks', 'Web Technologies', 'Artificial Intelligence',
                                     'Software Engineering', 'Engineering Mathematics'],
        'B.Tech Electronics': ['Digital Electronics', 'Microprocessors', 'Engineering Mathematics',
                                'Communication Skills', 'Environmental Science'],
        'M.Tech Computer Science': ['Artificial Intelligence', 'Database Systems', 'Computer Networks',
                                     'Software Engineering'],
        'MBA': ['Communication Skills', 'Environmental Science'],
    }
    prog_code = {'B.Tech Computer Science': 'BCS', 'B.Tech Electronics': 'BEC',
                 'M.Tech Computer Science': 'MCS', 'MBA': 'MBA'}
    for prog, prog_courses in program_course_map.items():
        pc = prog_code.get(prog, prog[:3].upper())
        for idx, course in enumerate(prog_courses, 1):
            frappe.db.sql(
                """INSERT INTO `tabProgram Course` (name, creation, modified, modified_by, owner,
                   docstatus, idx, course, parent, parentfield, parenttype)
                   VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator',
                   0, %s, %s, %s, 'courses', 'Program')""",
                (f"PC-{pc}-{idx:02d}", idx, course, prog)
            )
    frappe.db.commit()
    log(f"Created Program Course rows")
else:
    log(f"Already exists: {pc_count} rows — skipping")


# ─── 2. COST CENTERS ────────────────────────────────────────────────────────────
print("\n=== 2. Cost Centers ===")
existing_cc = frappe.db.sql("SELECT COUNT(*) as c FROM `tabCost Center`", as_dict=True)[0].c
if existing_cc <= 2:
    depts = [
        ('CS Department - HMX', 'CS Department', main_cost_center),
        ('ECE Department - HMX', 'ECE Department', main_cost_center),
        ('MBA Department - HMX', 'MBA Department', main_cost_center),
    ]
    for cc_name, cc_label, parent_cc in depts:
        existing = frappe.db.exists('Cost Center', cc_name)
        if not existing:
            doc = frappe.new_doc('Cost Center')
            doc.cost_center_name = cc_label
            doc.parent_cost_center = parent_cc
            doc.company = company
            doc.is_group = 0
            doc.flags.ignore_validate = True
            doc.flags.ignore_links = True
            doc.flags.ignore_mandatory = True
            doc.flags.ignore_permissions = True
            doc.insert(ignore_permissions=True)
            log(f"Created Cost Center: {doc.name}")
    frappe.db.commit()
else:
    log(f"Already {existing_cc} cost centers — skipping")


# ─── 3. FEE SCHEDULE ────────────────────────────────────────────────────────────
print("\n=== 3. Fee Schedule ===")
if frappe.db.count('Fee Schedule') == 0:
    for fs_name, prog in [('EDU-FST-2026-00001', 'B.Tech Computer Science'),
                          ('EDU-FST-2026-00002', 'B.Tech Electronics')]:
        n = ins('Fee Schedule', {
            'fee_structure': fs_name,
            'posting_date': '2025-07-01',
            'due_date': '2025-07-31',
            'program': prog,
            'academic_year': academic_year,
            'academic_term': academic_term,
            'company': company,
            'receivable_account': receivable_account,
            'income_account': income_account,
            'cost_center': main_cost_center,
            'currency': 'INR',
        })
        log(f"Created Fee Schedule: {n}")
else:
    log(f"Already {frappe.db.count('Fee Schedule')} fee schedules — skipping")


# ─── 4. SUBMIT FEES (needed before Payment Entry) ───────────────────────────────
print("\n=== 4. Submit Fees ===")
unsubmitted_fees = frappe.db.sql(
    "SELECT name FROM `tabFees` WHERE docstatus=0 LIMIT 15", as_dict=True
)
submitted_count = 0
for f in unsubmitted_fees:
    frappe.db.set_value('Fees', f.name, 'docstatus', 1)
    submitted_count += 1
if submitted_count:
    frappe.db.commit()
    log(f"Submitted {submitted_count} Fees records")
else:
    log("All Fees already submitted")

# Refresh fees data
fees_data = frappe.db.sql(
    "SELECT name, student, program, grand_total, receivable_account, income_account, company FROM `tabFees` WHERE docstatus=1 LIMIT 15",
    as_dict=True
)


# ─── 5. PAYMENT ENTRY ────────────────────────────────────────────────────────────
print("\n=== 5. Payment Entry ===")
if frappe.db.count('Payment Entry') == 0:
    modes = ['Cash', 'Bank Transfer', 'Cheque', 'Online']
    for i, fee in enumerate(fees_data[:10]):
        paid_amount = fee.grand_total * 0.5 if i % 3 == 0 else fee.grand_total
        n = ins('Payment Entry', {
            'payment_type': 'Receive',
            'posting_date': '2025-08-01',
            'company': company,
            'mode_of_payment': modes[i % len(modes)],
            'party_type': 'Student',
            'party': fee.student,
            'party_name': student_names.get(fee.student, fee.student),
            'paid_from': receivable_account,
            'paid_from_account_type': 'Receivable',
            'paid_from_account_currency': 'INR',
            'paid_to': 'Cash - HMX',
            'paid_to_account_type': 'Cash',
            'paid_to_account_currency': 'INR',
            'paid_amount': paid_amount,
            'received_amount': paid_amount,
            'source_exchange_rate': 1,
            'target_exchange_rate': 1,
            'base_paid_amount': paid_amount,
            'base_received_amount': paid_amount,
            'reference_no': f'REF-2025-{i+1:04d}',
            'reference_date': '2025-08-01',
            'remarks': f'Fee payment for {fee.program}',
        }, submittable=True)
        log(f"Created Payment Entry: {n} for {fee.student} amount={paid_amount}")
else:
    log(f"Already {frappe.db.count('Payment Entry')} payment entries — skipping")


# ─── 6. JOURNAL ENTRY ────────────────────────────────────────────────────────────
print("\n=== 6. Journal Entry ===")
if frappe.db.count('Journal Entry') == 0:
    for title, debit_acct, credit_acct, amount, narration in [
        ('Miscellaneous Income', 'Cash - HMX', 'Service - HMX', 5000.0, 'Misc income from printing/scanning'),
        ('Lab Consumables Expense', 'Indirect Income - HMX', 'Cash - HMX', 12000.0, 'Lab consumables purchase'),
    ]:
        doc = frappe.new_doc('Journal Entry')
        doc.title = title
        doc.posting_date = '2025-09-01'
        doc.company = company
        doc.voucher_type = 'Journal Entry'
        doc.user_remark = narration
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_permissions = True
        doc.append('accounts', {
            'account': debit_acct,
            'debit_in_account_currency': amount,
            'credit_in_account_currency': 0,
            'cost_center': main_cost_center,
        })
        doc.append('accounts', {
            'account': credit_acct,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': amount,
            'cost_center': main_cost_center,
        })
        doc.insert(ignore_permissions=True)
        log(f"Created Journal Entry: {doc.name}")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Journal Entry')} journal entries — skipping")


# ─── 7. STUDENT APPLICANT ────────────────────────────────────────────────────────
print("\n=== 7. Student Applicant ===")
if frappe.db.count('Student Applicant') == 0:
    applicant_names = [
        ('Arun', 'Kumar', 'B.Tech Computer Science', 'arun.kumar@example.com', 'General', 85.5, 92.0, 78.5),
        ('Preethi', 'Nair', 'B.Tech Computer Science', 'preethi.nair@example.com', 'OBC', 88.0, 90.5, 82.0),
        ('Vinod', 'Sharma', 'B.Tech Electronics', 'vinod.sharma@example.com', 'General', 75.0, 80.0, 70.0),
        ('Suma', 'Bhat', 'B.Tech Electronics', 'suma.bhat@example.com', 'SC', 70.5, 75.0, 68.0),
        ('Kiran', 'Reddy', 'M.Tech Computer Science', 'kiran.reddy@example.com', 'General', 78.0, 82.0, 88.5),
        ('Lakshmi', 'Patel', 'M.Tech Computer Science', 'lakshmi.patel@example.com', 'OBC', 80.5, 85.0, 85.0),
        ('Rahul', 'Jain', 'MBA', 'rahul.jain@example.com', 'General', 72.0, 78.0, 92.0),
        ('Divya', 'Menon', 'MBA', 'divya.menon@example.com', 'General', 76.0, 80.0, 88.0),
        ('Suresh', 'Yadav', 'B.Tech Computer Science', 'suresh.yadav@example.com', 'ST', 65.0, 70.0, 62.0),
        ('Meera', 'Pillai', 'B.Tech Electronics', 'meera.pillai@example.com', 'General', 82.0, 86.0, 74.0),
    ]
    sa_names = []
    for first, last, prog, email, cat, p10, p12, score in applicant_names:
        n = ins('Student Applicant', {
            'first_name': first,
            'last_name': last,
            'program': prog,
            'student_email_id': email,
            'academic_year': academic_year,
            'application_status': 'Applied',
            'application_date': '2025-03-01',
            'gender': 'Male' if first in ['Arun', 'Vinod', 'Kiran', 'Rahul', 'Suresh'] else 'Female',
            'nationality': 'Indian',
            'custom_category': cat,
            'custom_percentage_10th': p10,
            'custom_percentage_12th': p12,
            'custom_entrance_exam_score': score,
            'custom_merit_score': (p12 * 0.4 + score * 0.6),
            'custom_document_verification_status': 'Verified',
        })
        sa_names.append((n, first + ' ' + last, prog, cat, p12 * 0.4 + score * 0.6))
        log(f"Created Student Applicant: {n} - {first} {last}")
else:
    log(f"Already {frappe.db.count('Student Applicant')} applicants — skipping")
    sa_names = [(r.name, r.title, r.program, r.student_category or 'General', 0)
                for r in frappe.db.get_all('Student Applicant',
                                           fields=['name', 'title', 'program', 'student_category'], limit=10)]


# ─── 8. MERIT LIST ────────────────────────────────────────────────────────────────
print("\n=== 8. Merit List ===")
if frappe.db.count('Merit List') == 0 and sa_names:
    doc = frappe.new_doc('Merit List')
    doc.admission_cycle = 'Admission 2025-26'
    doc.program = 'B.Tech Computer Science'
    doc.category = 'General'
    doc.list_number = 1
    doc.generation_date = '2025-04-15'
    doc.valid_till = '2025-05-15'
    doc.status = 'Published'
    doc.flags.ignore_validate = True
    doc.flags.ignore_links = True
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    btcs_applicants = [(n, name, cat, score) for n, name, prog, cat, score in sa_names
                       if prog == 'B.Tech Computer Science']
    btcs_applicants.sort(key=lambda x: x[3], reverse=True)
    for rank, (sa_name, sa_full_name, cat, score) in enumerate(btcs_applicants, 1):
        doc.append('applicants', {
            'applicant': sa_name,
            'applicant_name': sa_full_name,
            'merit_rank': rank,
            'merit_score': round(score, 2),
            'category': cat,
            'seat_allotted': 1 if rank <= 3 else 0,
        })
    doc.insert(ignore_permissions=True)
    log(f"Created Merit List: {doc.name} with {len(doc.applicants)} applicants")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Merit List')} merit lists — skipping")


# ─── 9. COURSE REGISTRATION ────────────────────────────────────────────────────
print("\n=== 9. Course Registration ===")
if frappe.db.count('Course Registration') == 0:
    btcs_courses = ['Data Structures', 'Database Systems', 'Operating Systems',
                    'Computer Networks', 'Engineering Mathematics']
    btcs_students = [s for s in student_ids if pe_by_student.get(s, {}).get('program') == 'B.Tech Computer Science'][:10]
    for stu in btcs_students[:10]:
        doc = frappe.new_doc('Course Registration')
        doc.student = stu
        doc.student_name = student_names.get(stu, stu)
        doc.program = 'B.Tech Computer Science'
        doc.academic_term = academic_term
        doc.registration_date = '2025-07-15'
        doc.total_credits = 20
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_permissions = True
        for i, course in enumerate(btcs_courses, 1):
            doc.append('courses', {
                'course': course,
                'course_name': course,
                'credits': 4,
                'course_type': 'Theory',
                'is_elective': 0,
            })
        doc.insert(ignore_permissions=True)
        log(f"Created Course Registration: {doc.name} for {stu}")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Course Registration')} course registrations — skipping")


# ─── 10. COURSE PREREQUISITE ───────────────────────────────────────────────────
print("\n=== 10. Course Prerequisite ===")
if frappe.db.count('Course Prerequisite') == 0:
    prereq_map = [
        ('Data Structures', 'Engineering Mathematics'),
        ('Database Systems', 'Data Structures'),
        ('Operating Systems', 'Computer Networks'),
        ('Artificial Intelligence', 'Data Structures'),
        ('Software Engineering', 'Database Systems'),
    ]
    for course, prereq in prereq_map:
        try:
            course_doc = frappe.get_doc('Course', course)
            existing = frappe.db.sql(
                "SELECT name FROM `tabCourse Prerequisite` WHERE parent=%s AND prerequisite_course=%s",
                (course, prereq)
            )
            if not existing:
                frappe.db.sql(
                    """INSERT INTO `tabCourse Prerequisite`
                       (name, creation, modified, modified_by, owner, docstatus, idx,
                        prerequisite_course, prerequisite_course_name, is_mandatory,
                        parent, parentfield, parenttype)
                       VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator',
                       0, 1, %s, %s, 1, %s, 'prerequisites', 'Course')""",
                    (f"CP-{course[:3].upper()}-{prereq[:3].upper()}", prereq, prereq, course)
                )
                log(f"Created Course Prerequisite: {course} requires {prereq}")
        except Exception as e:
            log(f"Skip Course Prerequisite {course}->{prereq}: {e}")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Course Prerequisite')} prerequisites — skipping")


# ─── 11. FACULTY RESEARCH PROJECT ─────────────────────────────────────────────
print("\n=== 11. Faculty Research Project ===")
if frappe.db.count('Faculty Research Project') == 0:
    projects = [
        ('Machine Learning for Student Performance Prediction', 'DST', 'Principal Investigator', 1500000, '2024-01-01', '2026-12-31', 'Ongoing'),
        ('IoT-based Smart Campus Monitoring', 'AICTE', 'Principal Investigator', 800000, '2024-04-01', '2026-03-31', 'Ongoing'),
        ('Blockchain for Academic Records', 'NIT Internal', 'Principal Investigator', 500000, '2023-07-01', '2025-06-30', 'Completed'),
        ('Natural Language Processing for Multilingual Education', 'UGC', 'Co-Investigator', 1200000, '2024-01-01', '2027-12-31', 'Ongoing'),
        ('Cloud Computing for Rural Education Access', 'MEITY', 'Principal Investigator', 2000000, '2025-01-01', '2027-12-31', 'Ongoing'),
    ]
    # Faculty Research Project is a child table under Faculty Profile
    fp_docs = frappe.db.sql("SELECT name, employee FROM `tabFaculty Profile` LIMIT 5", as_dict=True)
    for i, (fp, (title, agency, role, amount, sd, ed, status)) in enumerate(zip(fp_docs, projects)):
        frappe.db.sql(
            """INSERT INTO `tabFaculty Research Project`
               (name, creation, modified, modified_by, owner, docstatus, idx,
                project_title, funding_agency, role, amount, start_date, end_date, status,
                parent, parentfield, parenttype)
               VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator',
               0, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'research_projects', 'Faculty Profile')""",
            (f"FRP-{i+1:03d}", i+1, title, agency, role, amount, sd, ed, status, fp.name)
        )
        log(f"Created Faculty Research Project: {title[:40]}... for {fp.name}")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Faculty Research Project')} research projects — skipping")


# ─── 12. FACULTY AWARD ────────────────────────────────────────────────────────
print("\n=== 12. Faculty Award ===")
if frappe.db.count('Faculty Award') == 0:
    awards = [
        ('Best Teacher Award', 'NIT Academic Council', '2024-03-15', 'Awarded for excellence in teaching'),
        ('Research Excellence Award', 'DST India', '2024-11-20', 'Best research contribution in CS'),
        ('Young Scientist Award', 'Indian Science Congress', '2023-01-10', 'Awarded to young scientists under 35'),
        ('Best Paper Award', 'IEEE International Conference', '2024-07-05', 'Best paper in AI track'),
        ('Outstanding Faculty Award', 'Alumni Association', '2025-02-01', 'Voted by graduating batch'),
    ]
    fp_docs = frappe.db.sql("SELECT name FROM `tabFaculty Profile` LIMIT 5", as_dict=True)
    for i, (fp, (award, body, dt, desc)) in enumerate(zip(fp_docs, awards)):
        frappe.db.sql(
            """INSERT INTO `tabFaculty Award`
               (name, creation, modified, modified_by, owner, docstatus, idx,
                award_name, awarding_body, award_date, description,
                parent, parentfield, parenttype)
               VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator',
               0, %s, %s, %s, %s, %s, %s, 'awards', 'Faculty Profile')""",
            (f"FA-{i+1:03d}", i+1, award, body, dt, desc, fp.name)
        )
        log(f"Created Faculty Award: {award} for {fp.name}")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Faculty Award')} awards — skipping")


# ─── 13. EMPLOYEE QUALIFICATION ───────────────────────────────────────────────
print("\n=== 13. Employee Qualification ===")
if frappe.db.count('Employee Qualification') == 0:
    qualifications = [
        ('Ph.D', 'Computer Science', 'IIT Delhi', 2018, 8.5, 'PHD001'),
        ('M.Tech', 'Software Engineering', 'NIT Trichy', 2014, 8.9, 'MTH001'),
        ('B.Tech', 'Computer Science', 'BITS Pilani', 2012, 9.1, 'BTH001'),
        ('Ph.D', 'Electronics', 'IIT Bombay', 2016, 8.2, 'PHD002'),
        ('M.Tech', 'VLSI Design', 'IIT Madras', 2013, 8.7, 'MTH002'),
        ('Ph.D', 'AI & Machine Learning', 'IISc Bangalore', 2019, 9.0, 'PHD003'),
        ('M.E', 'Communication Engineering', 'Anna University', 2015, 8.3, 'ME001'),
        ('Ph.D', 'Mathematics', 'IIT Kharagpur', 2017, 8.6, 'PHD004'),
        ('MBA', 'Finance & Operations', 'IIM Ahmedabad', 2014, 3.8, 'MBA001'),
        ('Ph.D', 'Management Science', 'IIM Calcutta', 2020, 9.2, 'PHD005'),
    ]
    fp_docs = frappe.db.sql("SELECT name FROM `tabFaculty Profile` LIMIT 10", as_dict=True)
    for i, (fp, (qual, spec, inst, yr, pct, cert)) in enumerate(zip(fp_docs, qualifications)):
        frappe.db.sql(
            """INSERT INTO `tabEmployee Qualification`
               (name, creation, modified, modified_by, owner, docstatus, idx,
                qualification, specialization, institution, year_of_passing, percentage, certificate_number,
                parent, parentfield, parenttype)
               VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator',
               0, %s, %s, %s, %s, %s, %s, %s, %s, 'qualifications', 'Faculty Profile')""",
            (f"EQ-{i+1:03d}", i+1, qual, spec, inst, yr, pct, cert, fp.name)
        )
        log(f"Created Employee Qualification: {qual} for {fp.name}")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Employee Qualification')} qualifications — skipping")


# ─── 14. TEMPORARY TEACHING ASSIGNMENT ────────────────────────────────────────
print("\n=== 14. Temporary Teaching Assignment ===")
if frappe.db.count('Temporary Teaching Assignment') == 0:
    tta_data = [
        (emp_ids[0], emp_ids[1], emp_ids[1].replace('HR-EMP-', ''),
         'Data Structures', 'B.Tech Computer Science', '2025-10-01', '2025-10-07', 3, 'Faculty on medical leave'),
        (emp_ids[2], emp_ids[3], emp_ids[3].replace('HR-EMP-', ''),
         'Database Systems', 'B.Tech Computer Science', '2025-11-10', '2025-11-14', 2, 'Faculty at conference'),
        (emp_ids[4], emp_ids[5], emp_ids[5].replace('HR-EMP-', ''),
         'Computer Networks', 'B.Tech Computer Science', '2025-12-01', '2025-12-05', 4, 'Faculty on leave'),
    ]
    for orig, sub, sub_name, course, prog, fd, td, cls, remarks in tta_data:
        n = ins('Temporary Teaching Assignment', {
            'original_instructor': orig,
            'substitute_instructor': sub,
            'substitute_name': sub_name,
            'course': course,
            'course_name': course,
            'program': prog,
            'from_date': fd,
            'to_date': td,
            'classes_covered': cls,
            'remarks': remarks,
        })
        log(f"Created Temporary Teaching Assignment: {n}")
else:
    log(f"Already {frappe.db.count('Temporary Teaching Assignment')} TTAs — skipping")


# ─── 15. DISCUSSION REPLY ─────────────────────────────────────────────────────
print("\n=== 15. Discussion Reply ===")
if frappe.db.count('Discussion Reply') == 0 and discs:
    replies = [
        "Have you checked the lecture slides from Week 3? The concept is explained well there.",
        "I had the same doubt — the key point is that time complexity for this case is O(n log n).",
        "Please refer to the textbook Chapter 5, section 5.3 for detailed explanation.",
        "Great question! The difference lies in the normalization — please check the ER diagram.",
        "This was covered in last Tuesday's lab session. The answer is in the lab manual page 42.",
        "The professor mentioned this in office hours — the solution uses dynamic programming.",
    ]
    reply_idx = 0
    for disc in discs:
        for j in range(2):
            n = ins('Discussion Reply', {
                'topic': disc.name,
                'reply_by_type': 'Student' if j == 0 else 'Student',
                'student': student_ids[(reply_idx + j) % len(student_ids)],
                'reply_date': '2025-09-15',
                'reply_content': replies[reply_idx % len(replies)],
                'is_answer': 1 if j == 1 else 0,
                'upvotes': j * 3 + 1,
            })
            log(f"Created Discussion Reply: {n} for {disc.name}")
            reply_idx += 1
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Discussion Reply')} replies — skipping")


# ─── 16. EMERGENCY ALERT ─────────────────────────────────────────────────────
print("\n=== 16. Emergency Alert ===")
if frappe.db.count('Emergency Alert') == 0:
    alerts = [
        ('Fire Drill', 'Fire', 'Low', 'Resolved', 'Scheduled Fire Drill - Block A',
         'Evacuate Block A via emergency exits. Assemble at Ground Zero.',
         'Remain calm, use staircases only.', 'All', '2025-09-01 10:00:00', '2025-09-01 11:00:00'),
        ('Severe Weather Warning', 'Natural Disaster', 'High', 'Active',
         'Cyclone Warning: Stay Indoors',
         'Severe cyclone expected in 6 hours. All outdoor activities cancelled.',
         'Stay indoors, do not use electrical appliances.', 'All', '2025-10-15 14:00:00', '2025-10-16 06:00:00'),
    ]
    for alert_type, typ, sev, status, title, msg, instr, audience, bc_time, exp_at in alerts:
        n = ins('Emergency Alert', {
            'alert_type': typ,
            'severity': sev,
            'status': status,
            'initiated_by': 'Administrator',
            'title': title,
            'message': msg,
            'instructions': instr,
            'send_email': 1,
            'target_audience': audience,
            'broadcast_time': bc_time,
            'expires_at': exp_at,
            'require_acknowledgment': 1,
            'total_recipients': 30,
            'acknowledgments_received': 10,
        })
        log(f"Created Emergency Alert: {n}")
else:
    log(f"Already {frappe.db.count('Emergency Alert')} alerts — skipping")


# ─── 17. NOTIFICATION PREFERENCE ─────────────────────────────────────────────
print("\n=== 17. Notification Preference ===")
if frappe.db.count('Notification Preference') == 0:
    student_users = frappe.db.sql(
        """SELECT u.name FROM `tabUser` u
           JOIN `tabHas Role` hr ON hr.parent=u.name
           WHERE hr.role='University Student' LIMIT 5""",
        as_dict=True
    )
    for u in student_users:
        n = ins('Notification Preference', {
            'user': u.name,
            'enabled': 1,
            'email_enabled': 1,
            'sms_enabled': 1,
            'push_enabled': 1,
            'in_app_enabled': 1,
            'fee_notifications': 1,
            'academic_notifications': 1,
            'library_notifications': 1,
            'placement_notifications': 1,
            'quiet_hours_enabled': 1,
            'quiet_start_time': '22:00:00',
            'quiet_end_time': '07:00:00',
            'email_digest': 1,
            'digest_frequency': 'Daily',
        })
        log(f"Created Notification Preference: {n} for {u.name}")
else:
    log(f"Already {frappe.db.count('Notification Preference')} prefs — skipping")


# ─── 18. KPI DEFINITION ──────────────────────────────────────────────────────
print("\n=== 18. KPI Definition ===")
if frappe.db.count('KPI Definition') == 0:
    kpis = [
        ('Student Enrollment Rate', 'ENR-001', 'Academic', 'Percentage of admitted students who enrolled',
         'Percentage', 'Monthly', 'Formula', None, '(enrolled / admitted) * 100',
         90.0, 75.0, 95.0, 1, 60.0, 75.0, 90.0),
        ('Fee Collection Rate', 'FIN-001', 'Financial', 'Percentage of fees collected vs billed',
         'Percentage', 'Monthly', 'Formula', None, '(collected / billed) * 100',
         95.0, 80.0, 98.0, 1, 70.0, 85.0, 95.0),
        ('Average Attendance Rate', 'ATT-001', 'Academic', 'Average student attendance percentage',
         'Percentage', 'Weekly', 'Formula', None, 'AVG(attendance_pct)',
         85.0, 70.0, 90.0, 1, 65.0, 75.0, 85.0),
        ('Placement Rate', 'PLC-001', 'Placement', 'Percentage of eligible students placed',
         'Percentage', 'Yearly', 'Formula', None, '(placed / eligible) * 100',
         80.0, 65.0, 90.0, 1, 55.0, 70.0, 85.0),
        ('Faculty Research Output', 'RES-001', 'Research', 'Number of publications per year per faculty',
         'Count', 'Yearly', 'SQL Query',
         'SELECT COUNT(*) FROM `tabFaculty Research Project` WHERE status="Ongoing"',
         None, 2.0, 1.0, 4.0, 1, 1.0, 2.0, 3.0),
    ]
    for kpi_name, code, cat, desc, unit, freq, method, sql, formula, target, min_val, stretch, higher, red, yellow, green in kpis:
        n = ins('KPI Definition', {
            'kpi_name': kpi_name,
            'kpi_code': code,
            'category': cat,
            'description': desc,
            'unit': unit,
            'tracking_frequency': freq,
            'is_active': 1,
            'show_on_executive_dashboard': 1,
            'calculation_method': method,
            'sql_query': sql or '',
            'formula': formula or '',
            'target_value': target,
            'minimum_acceptable': min_val,
            'stretch_target': stretch,
            'higher_is_better': higher,
            'red_threshold': red,
            'yellow_threshold': yellow,
            'green_threshold': green,
            'responsible_role': 'University Admin',
        })
        log(f"Created KPI Definition: {n} - {kpi_name}")
else:
    log(f"Already {frappe.db.count('KPI Definition')} KPIs — skipping")


# ─── 19. CUSTOM DASHBOARD ─────────────────────────────────────────────────────
print("\n=== 19. Custom Dashboard ===")
if frappe.db.count('Custom Dashboard') == 0:
    doc = frappe.new_doc('Custom Dashboard')
    doc.dashboard_name = 'Executive Overview'
    doc.dashboard_type = 'Executive'
    doc.description = 'High-level KPIs for university administration'
    doc.is_public = 1
    doc.is_active = 1
    doc.owner_role = 'University Admin'
    doc.refresh_interval = '5 minutes'
    doc.layout_type = 'Grid'
    doc.columns = 3
    doc.enable_date_filter = 1
    doc.default_date_range = 'This Month'
    doc.enable_department_filter = 1
    doc.enable_program_filter = 1
    doc.flags.ignore_validate = True
    doc.flags.ignore_links = True
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    widgets = [
        ('Enrollment Rate', 'Number Card', 'Query', None, 'Bar', '#3498db', 'users', 1, 1, 1, 2),
        ('Fee Collection', 'Progress Card', 'Query', None, 'Donut', '#2ecc71', 'currency', 1, 2, 1, 2),
        ('Attendance Overview', 'Chart', 'Report', None, 'Bar', '#e74c3c', 'calendar', 2, 1, 2, 3),
    ]
    for wt, wtype, ds, report, chart, color, icon, row, col, w, h in widgets:
        doc.append('widgets', {
            'widget_title': wt,
            'widget_type': wtype,
            'data_source': ds,
            'report_name': report or '',
            'chart_type': chart,
            'color': color,
            'icon': icon,
            'position_row': row,
            'position_col': col,
            'width': w,
            'height': h,
        })
    doc.insert(ignore_permissions=True)
    log(f"Created Custom Dashboard: {doc.name} with {len(doc.widgets)} widgets")
    frappe.db.commit()
else:
    log(f"Already {frappe.db.count('Custom Dashboard')} dashboards — skipping")


# ─── 20. SCHEDULED REPORT ─────────────────────────────────────────────────────
print("\n=== 20. Scheduled Report ===")
if frappe.db.count('Scheduled Report') == 0:
    reports = [
        ('Weekly Attendance Summary', 'Student Monthly Attendance Sheet', 'Weekly attendance report for HoDs',
         'Weekly', 'Monday', None, '08:00:00', 'PDF'),
        ('Monthly Fee Collection Report', 'Student Fee Collection Report', 'Monthly fee collection status',
         'Monthly', None, 1, '09:00:00', 'Excel'),
    ]
    for rpt_name, report, desc, freq, dow, dom, tod, fmt in reports:
        n = ins('Scheduled Report', {
            'report_name': rpt_name,
            'report': report,
            'description': desc,
            'is_enabled': 1,
            'output_format': fmt,
            'include_charts': 1,
            'frequency': freq,
            'day_of_week': dow or '',
            'day_of_month': dom or 0,
            'time_of_day': tod,
            'timezone': 'Asia/Kolkata',
            'delivery_method': 'Email',
        })
        log(f"Created Scheduled Report: {n}")
else:
    log(f"Already {frappe.db.count('Scheduled Report')} scheduled reports — skipping")


# ─── FINAL COUNTS ─────────────────────────────────────────────────────────────
print("\n=== FINAL COUNTS ===")
check_doctypes = [
    'Program Enrollment', 'Student Applicant', 'Merit List', 'Merit List Applicant',
    'Fee Schedule', 'Payment Entry', 'Journal Entry',
    'Course Registration', 'Course Prerequisite',
    'Faculty Research Project', 'Faculty Award', 'Employee Qualification',
    'Temporary Teaching Assignment', 'Discussion Reply',
    'Emergency Alert', 'Notification Preference',
    'KPI Definition', 'Custom Dashboard', 'Dashboard Widget', 'Scheduled Report',
]
for dt in check_doctypes:
    try:
        cnt = frappe.db.count(dt)
        print(f"  {dt}: {cnt}")
    except Exception as e:
        print(f"  {dt}: ERROR - {e}")

print("\nProgram Courses:", frappe.db.sql("SELECT COUNT(*) as c FROM `tabProgram Course`", as_dict=True)[0].c)
print("Cost Centers:", frappe.db.count('Cost Center'))
print("GL Entry:", frappe.db.count('GL Entry'))
print("\nDone!")

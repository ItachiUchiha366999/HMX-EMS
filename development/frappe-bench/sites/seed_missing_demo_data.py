"""
Seed missing demo data for university.local — fully schema-verified version.
Inserts: Library Fine, Attendance (HRMS), Workload Distributor, Feedback Form/Response,
Placement Drive/Application, Transport Trip Log, Hostel Visitor, Suggestion,
LMS Content Progress, Assignment Submission, Quiz Attempt, Student Transcript,
Book Reservation, User Notification
"""
import frappe
from datetime import date, timedelta
import random

frappe.init(site='university.local', sites_path='/workspace/development/frappe-bench/sites')
frappe.connect()
frappe.set_user('Administrator')
random.seed(42)
TODAY = date.today()

def ins(doctype, fields, submittable=False):
    """Insert a doc, bypassing all validation. Returns doc.name."""
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

counts = {}

# Master data references
students = [
    'EDU-STU-2026-00149','EDU-STU-2026-00148','EDU-STU-2026-00147',
    'EDU-STU-2026-00146','EDU-STU-2026-00145',
]
members  = ['LM-2026-00030','LM-2026-00029','LM-2026-00028','LM-2026-00027','LM-2026-00026']
articles = ['LIB-2026-00114','LIB-2026-00112','LIB-2026-00110','LIB-2026-00109','LIB-2026-00108']
employees = [f'HR-EMP-{i:05d}' for i in [11,10,9,23,22,21,20,19,18,17,16,15,14,13,12]]

# ── 1. Library Fine (3) ───────────────────────────────────────────────────────
# naming_series: LF-.YYYY.-
# reqd: naming_series, member, fine_date, fine_amount
# status options: Unpaid | Paid | Waived
for i, (amt, status) in enumerate([(50,'Unpaid'),(100,'Unpaid'),(75,'Paid')]):
    ins('Library Fine', {
        'naming_series': 'LF-.YYYY.-',
        'member': members[i], 'member_name': 'Library Member',
        'article': articles[i], 'fine_date': TODAY,
        'fine_amount': amt, 'status': status, 'reason': 'Late Return',
    })
frappe.db.commit()
counts['Library Fine'] = frappe.db.count('Library Fine')
print(f"Library Fine: {counts['Library Fine']}")

# ── 2. Attendance HRMS (15) ───────────────────────────────────────────────────
# naming_series: HR-ATT-.YYYY.-
# status options: Present | Absent | On Leave | Half Day | Work From Home
att_statuses = ['Present','Present','Present','Absent','Present','Present','Half Day',
                'Present','Present','Present','Present','Absent','Present','Present','Present']
for i, emp in enumerate(employees):
    name = ins('Attendance', {
        'naming_series': 'HR-ATT-.YYYY.-',
        'employee': emp, 'attendance_date': TODAY - timedelta(days=1),
        'status': att_statuses[i], 'company': 'Hanumatrix',
    }, submittable=True)
frappe.db.commit()
counts['Attendance'] = frappe.db.count('Attendance')
print(f"Attendance: {counts['Attendance']}")

# ── 3. Workload Distributor (1) ───────────────────────────────────────────────
# autoname: format:{name} — frappe generates a name from academic_year+term
ins('Workload Distributor', {
    'academic_year': '2025-26', 'academic_term': '2025-26 (Odd Semester)',
})
frappe.db.commit()
counts['Workload Distributor'] = frappe.db.count('Workload Distributor')
print(f"Workload Distributor: {counts['Workload Distributor']}")

# ── 4. Feedback Form (2) ──────────────────────────────────────────────────────
# form_type options: Course Feedback | Faculty Feedback | ...
# target_audience options: Students | Faculty | Parents | Alumni | Staff | All
# status options: Draft | Scheduled | Active | Paused | Closed | Archived
ff_names = []
for title, ftype in [('Course Feedback Form','Course Feedback'),('Faculty Feedback Form','Faculty Feedback')]:
    name = ins('Feedback Form', {
        'naming_series': 'FF-.YYYY.-.#####',
        'form_title': title, 'form_type': ftype,
        'target_audience': 'Students',
        'start_date': TODAY - timedelta(days=7),
        'end_date': TODAY + timedelta(days=7),
        'status': 'Active',
    })
    ff_names.append(name)
    # Add question via direct SQL
    try:
        frappe.db.sql("""INSERT INTO `tabFeedback Question`
            (name, parent, parenttype, parentfield, idx, question_text, question_type, is_required)
            VALUES (%s, %s, 'Feedback Form', 'questions', 1, 'Rate the overall quality', 'Rating', 1)""",
            (frappe.generate_hash(length=10), name))
        frappe.db.commit()
    except Exception as e:
        print(f'  FF question: {e}')
frappe.db.commit()
counts['Feedback Form'] = frappe.db.count('Feedback Form')
print(f"Feedback Form: {counts['Feedback Form']}, names={ff_names}")

# ── 5. Feedback Response (10) ─────────────────────────────────────────────────
# respondent_type options: Student | Faculty | Parent | Alumni | Staff | Anonymous
# status options: In Progress | Submitted | Valid | Invalid
q_ids = []
for ff in ff_names:
    row = frappe.db.sql("SELECT name FROM `tabFeedback Question` WHERE parent=%s LIMIT 1", ff, as_list=True)
    q_ids.append(row[0][0] if row else None)

for i in range(10):
    name = ins('Feedback Response', {
        'naming_series': 'FR-.YYYY.-.#####',
        'feedback_form': ff_names[i % 2],
        'respondent_type': 'Student',
        'student': students[i % 5],
        'status': 'Submitted',
    })
    qid = q_ids[i % 2]
    if qid:
        try:
            frappe.db.sql("""INSERT INTO `tabFeedback Answer`
                (name, parent, parenttype, parentfield, idx, question_id, answer_value)
                VALUES (%s, %s, 'Feedback Response', 'answers', 1, %s, '4')""",
                (frappe.generate_hash(length=10), name, qid))
        except Exception as e:
            print(f'  FR answer: {e}')
frappe.db.commit()
counts['Feedback Response'] = frappe.db.count('Feedback Response')
print(f"Feedback Response: {counts['Feedback Response']}")

# ── 6. Placement Drive (2) ────────────────────────────────────────────────────
# naming_series: PD-.YYYY.-
# status options: Draft | Open | Closed | Completed
pd_names = []
for company, job_title in [('Google','Software Engineer'),('Amazon','Data Analyst')]:
    name = ins('Placement Drive', {
        'naming_series': 'PD-.YYYY.-',
        'company': company, 'job_title': job_title,
        'drive_date': TODAY + timedelta(days=30),
        'last_date_to_apply': TODAY + timedelta(days=14),
        'status': 'Open',
    })
    pd_names.append(name)
    try:
        frappe.db.sql("""INSERT INTO `tabPlacement Round`
            (name, parent, parenttype, parentfield, idx, round_number, round_name)
            VALUES (%s, %s, 'Placement Drive', 'rounds', 1, 1, 'Technical Test')""",
            (frappe.generate_hash(length=10), name))
        frappe.db.commit()
    except Exception as e:
        print(f'  PD round: {e}')
frappe.db.commit()
counts['Placement Drive'] = frappe.db.count('Placement Drive')
print(f"Placement Drive: {counts['Placement Drive']}, names={pd_names}")

# ── 7. Placement Application (8) ──────────────────────────────────────────────
# status options: Applied | Shortlisted | Interview Scheduled | Selected | Rejected | Withdrawn
app_students = (students * 2)[:8]
for i in range(8):
    ins('Placement Application', {
        'naming_series': 'PA-.YYYY.-',
        'student': app_students[i],
        'placement_drive': pd_names[i % 2],
        'status': ['Applied','Shortlisted','Selected','Applied','Shortlisted','Applied','Selected','Applied'][i],
    })
frappe.db.commit()
counts['Placement Application'] = frappe.db.count('Placement Application')
print(f"Placement Application: {counts['Placement Application']}")

# ── 8. Transport Trip Log (10) ────────────────────────────────────────────────
# naming_series: TL-.YYYY.-
# trip_type options: Morning | Evening | Special
# status options: Scheduled | In Progress | Completed | Cancelled
routes   = ['Route A','Route B','Route C']
vehicles = ['NIT-01','NIT-02','NIT-03']
for i in range(10):
    name = ins('Transport Trip Log', {
        'naming_series': 'TL-.YYYY.-',
        'trip_date': TODAY - timedelta(days=i % 5 + 1),
        'trip_type': ['Morning','Evening'][i % 2],
        'route': routes[i % 3], 'vehicle': vehicles[i % 3],
        'status': 'Completed',
    }, submittable=True)
frappe.db.commit()
counts['Transport Trip Log'] = frappe.db.count('Transport Trip Log')
print(f"Transport Trip Log: {counts['Transport Trip Log']}")

# ── 9. Hostel Visitor (5) ─────────────────────────────────────────────────────
# relationship options: Parent | Guardian | Sibling | Relative | Friend | Other
# status options: Checked In | Checked Out | Denied
visitor_data = [
    ('Ravi Kumar','9876543210','Parent','BH-01'),
    ('Priya Sharma','9876543211','Sibling','GH-01'),
    ('Suresh Patel','9876543212','Guardian','PGH-01'),
    ('Meena Verma','9876543213','Parent','BH-01'),
    ('Ajay Singh','9876543214','Sibling','GH-01'),
]
for i, (vname, vmobile, rel, bldg) in enumerate(visitor_data):
    ins('Hostel Visitor', {
        'visitor_name': vname, 'visitor_mobile': vmobile,
        'relationship': rel, 'student': students[i],
        'building': bldg, 'visit_date': TODAY,
        'check_in_time': '10:00:00', 'status': 'Checked In',
    })
frappe.db.commit()
counts['Hostel Visitor'] = frappe.db.count('Hostel Visitor')
print(f"Hostel Visitor: {counts['Hostel Visitor']}")

# ── 10. Suggestion (5) ───────────────────────────────────────────────────────
# naming_series: SUG-.YYYY.-.#####
# category options: Academic Improvement | Infrastructure | Services | Events & Activities | Policy Suggestion | Technology | Other
# status options: New | Under Review | Approved | ...
sug_data = [
    ('Improve WiFi Coverage','Infrastructure'),
    ('Better Canteen Food','Services'),
    ('More Study Rooms','Infrastructure'),
    ('Sports Equipment Upgrade','Events & Activities'),
    ('Lab Upgrade Request','Academic Improvement'),
]
for subject, category in sug_data:
    ins('Suggestion', {
        'naming_series': 'SUG-.YYYY.-.#####',
        'subject': subject, 'category': category,
        'suggestion': 'Please look into this matter and take necessary action.',
        'status': 'New',
    })
frappe.db.commit()
counts['Suggestion'] = frappe.db.count('Suggestion')
print(f"Suggestion: {counts['Suggestion']}")

# ── 11. LMS Content Progress (30) ────────────────────────────────────────────
# autoname: format:{student}-{content}
# status options: Not Started | In Progress | Completed
# columns: student, content, status, progress_percent, time_spent_minutes
contents    = ['LC-.2026.-.00273','LC-.2026.-.00274','LC-.2026.-.00275',
               'LC-.2026.-.00276','LC-.2026.-.00277','LC-.2026.-.00278']
lcp_status  = ['Completed','Completed','In Progress','Completed','In Progress','Completed']
for stu in students:
    for ci, content in enumerate(contents):
        ins('LMS Content Progress', {
            'student': stu, 'content': content,
            'status': lcp_status[ci],
            'progress_percent': 100 if lcp_status[ci] == 'Completed' else 60,
        })
frappe.db.commit()
counts['LMS Content Progress'] = frappe.db.count('LMS Content Progress')
print(f"LMS Content Progress: {counts['LMS Content Progress']}")

# ── 12. Assignment Submission (20) ────────────────────────────────────────────
# autoname: format:SUB-.{YYYY}.-.{#####}
# status options: Submitted | Under Review | Graded | Resubmission Required
# columns: assignment, student, status, marks_obtained, submission_date
assignments = ['ASN-.2026.-.00290','ASN-.2026.-.00289','ASN-.2026.-.00288','ASN-.2026.-.00287']
for stu in students:
    for asgn in assignments:
        ins('Assignment Submission', {
            'assignment': asgn, 'student': stu,
            'status': 'Graded', 'marks_obtained': random.randint(15, 24),
        })
frappe.db.commit()
counts['Assignment Submission'] = frappe.db.count('Assignment Submission')
print(f"Assignment Submission: {counts['Assignment Submission']}")

# ── 13. Quiz Attempt (15) ─────────────────────────────────────────────────────
# autoname: format:QA-.{YYYY}.-.{#####}
# status options: In Progress | Submitted | Auto Submitted | Graded
# columns: quiz, student, status, marks_obtained, total_marks, percentage, passed
quizzes     = ['QZ-.2026.-.00293','QZ-.2026.-.00292','QZ-.2026.-.00291']
marks_list  = [16, 14, 18, 12, 16]   # out of 20
for si, stu in enumerate(students):
    for quiz in quizzes:
        ins('Quiz Attempt', {
            'quiz': quiz, 'student': stu,
            'marks_obtained': marks_list[si],
            'total_marks': 20,
            'percentage': marks_list[si] * 5,   # out of 100
            'passed': 1,
            'status': 'Graded',
        })
frappe.db.commit()
counts['Quiz Attempt'] = frappe.db.count('Quiz Attempt')
print(f"Quiz Attempt: {counts['Quiz Attempt']}")

# ── 14. Student Transcript (5) ───────────────────────────────────────────────
# autoname: format:TR-{YYYY}-{#####}
# transcript_type options: Provisional | Final | Duplicate
for stu in students:
    name = ins('Student Transcript', {
        'student': stu, 'transcript_type': 'Provisional',
    }, submittable=True)
frappe.db.commit()
counts['Student Transcript'] = frappe.db.count('Student Transcript')
print(f"Student Transcript: {counts['Student Transcript']}")

# ── 15. Book Reservation (3) ─────────────────────────────────────────────────
# naming_series: BR-.YYYY.-
# status options: Pending | Available | Fulfilled | Cancelled | Expired
for i in range(3):
    ins('Book Reservation', {
        'naming_series': 'BR-.YYYY.-',
        'article': articles[i], 'member': members[i],
        'reservation_date': TODAY, 'status': 'Pending',
    })
frappe.db.commit()
counts['Book Reservation'] = frappe.db.count('Book Reservation')
print(f"Book Reservation: {counts['Book Reservation']}")

# ── 16. User Notification (10) ───────────────────────────────────────────────
# autoname: UN-.#####
# notification_type options: info | success | warning | error | announcement
# category options: General | Academic | Fee | Examination | Library | Hostel | Placement | Emergency
# priority options: Low | Normal | High | Urgent
# field is 'read' (not 'is_read')
user_emails  = ['aditya.joshi@nit.edu','akash.dubey@nit.edu','ananya.gupta@nit.edu',
                'aparna.rajan@nit.edu','arjun.mehta@nit.edu']
notif_data = [
    ('Fee Reminder',        'Fee',         'warning',     'High'),
    ('Exam Schedule',       'Examination', 'info',        'High'),
    ('Attendance Update',   'Academic',    'info',        'Normal'),
    ('Library Book Due',    'Library',     'warning',     'Normal'),
    ('Assignment Due',      'Academic',    'announcement','Normal'),
]
for i in range(10):
    t, cat, ntype, priority = notif_data[i % 5]
    ins('User Notification', {
        'user': user_emails[i % 5],
        'title': t, 'message': f'Reminder: {t}',
        'notification_type': ntype,
        'category': cat, 'priority': priority,
        'read': 0,
    })
frappe.db.commit()
counts['User Notification'] = frappe.db.count('User Notification')
print(f"User Notification: {counts['User Notification']}")

# ── Final Summary ─────────────────────────────────────────────────────────────
expected = {
    'Library Fine': 3, 'Attendance': 15, 'Workload Distributor': 1,
    'Feedback Form': 2, 'Feedback Response': 10, 'Placement Drive': 2,
    'Placement Application': 8, 'Transport Trip Log': 10, 'Hostel Visitor': 5,
    'Suggestion': 5, 'LMS Content Progress': 30, 'Assignment Submission': 20,
    'Quiz Attempt': 15, 'Student Transcript': 5, 'Book Reservation': 3,
    'User Notification': 10,
}
print('\n=== FINAL SEED RESULTS ===')
all_ok = True
for dt, exp in expected.items():
    actual = counts.get(dt, 0)
    ok = actual >= exp
    if not ok:
        all_ok = False
    print(f"{'OK  ' if ok else 'FAIL'} {dt}: {actual} (need {exp})")
print('\nAll OK!' if all_ok else '\nSome items FAILED — check errors above')

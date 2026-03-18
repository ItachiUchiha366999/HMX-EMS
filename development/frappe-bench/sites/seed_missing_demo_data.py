"""
Seed missing demo data for university.local
Inserts: Library Fine, Attendance, Workload Distributor, Feedback Form/Response,
Placement Drive/Application, Transport Trip Log, Hostel Visitor, Suggestion,
LMS Content Progress, Assignment Submission, Quiz Attempt, Student Transcript,
Book Reservation, User Notification
"""
import frappe
from datetime import date, timedelta

frappe.init(site='university.local', sites_path='/workspace/development/frappe-bench/sites')
frappe.connect()

TODAY = date.today()
YYYY = TODAY.strftime('%Y')
NOW = frappe.utils.now()


def sql_insert(doctype, fields):
    """Direct SQL insert to bypass autoname for format-type doctypes."""
    tab = 'tab' + doctype
    fields.setdefault('docstatus', 0)
    fields.setdefault('owner', 'Administrator')
    fields.setdefault('creation', NOW)
    fields.setdefault('modified', NOW)
    fields.setdefault('modified_by', 'Administrator')
    cols = ', '.join(f'`{k}`' for k in fields)
    vals = ', '.join(['%s'] * len(fields))
    frappe.db.sql(f'INSERT INTO `{tab}` ({cols}) VALUES ({vals})', list(fields.values()))


counts = {}

# ---------------------------------------------------------------------------
# 1. Library Fine (3 records) — naming_series, set name manually
# ---------------------------------------------------------------------------
members = ['LM-2026-00030', 'LM-2026-00029', 'LM-2026-00028']
articles = ['LIB-2026-00114', 'LIB-2026-00112', 'LIB-2026-00110']
fine_amounts = [50, 100, 75]

for i, (member, article, amount) in enumerate(zip(members, articles, fine_amounts), 1):
    name = f'LF-{YYYY}-{i:05d}'
    if not frappe.db.exists('Library Fine', name):
        doc = frappe.new_doc('Library Fine')
        doc.name = name
        doc.naming_series = 'LF-.YYYY.-'
        doc.member = member
        doc.member_name = 'Library Member'
        doc.article = article
        doc.fine_date = TODAY
        doc.fine_amount = amount
        doc.status = 'Unpaid'
        doc.reason = 'Late Return'
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        # Fix name if autoname overrode it
        if doc.name != name:
            frappe.db.sql(f"UPDATE `tabLibrary Fine` SET name=%s WHERE name=%s", (name, doc.name))

frappe.db.commit()
counts['Library Fine'] = frappe.db.count('Library Fine')
print(f"Library Fine: {counts['Library Fine']}")

# ---------------------------------------------------------------------------
# 2. Attendance (15 records) — naming_series, submittable
# ---------------------------------------------------------------------------
employees = [
    'HR-EMP-00009', 'HR-EMP-00010', 'HR-EMP-00011', 'HR-EMP-00012', 'HR-EMP-00013',
    'HR-EMP-00014', 'HR-EMP-00015', 'HR-EMP-00016', 'HR-EMP-00017', 'HR-EMP-00018',
    'HR-EMP-00019', 'HR-EMP-00020', 'HR-EMP-00021', 'HR-EMP-00022', 'HR-EMP-00023',
]
statuses = ['Present', 'Present', 'Absent', 'Present', 'Present']

for i, emp in enumerate(employees[:15], 1):
    name = f'HR-ATT-{YYYY}-{i:05d}'
    if not frappe.db.exists('Attendance', name):
        att_date = TODAY - timedelta(days=i - 1)
        doc = frappe.new_doc('Attendance')
        doc.name = name
        doc.naming_series = 'HR-ATT-.YYYY.-'
        doc.employee = emp
        doc.status = statuses[(i - 1) % len(statuses)]
        doc.attendance_date = att_date
        doc.company = 'Hanumatrix'
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != name:
            frappe.db.sql(f"UPDATE `tabAttendance` SET name=%s WHERE name=%s", (name, doc.name))
        frappe.db.set_value('Attendance', name, 'docstatus', 1)

frappe.db.commit()
counts['Attendance'] = frappe.db.count('Attendance')
print(f"Attendance: {counts['Attendance']}")

# ---------------------------------------------------------------------------
# 3. Workload Distributor (1 record) — format:{name}, use direct SQL
# ---------------------------------------------------------------------------
wd_name = 'WLDIST-2025-26-ODD'
if not frappe.db.exists('Workload Distributor', wd_name):
    sql_insert('Workload Distributor', {
        'name': wd_name,
        'academic_year': '2025-26',
        'academic_term': '2025-26 (Odd Semester)',
    })

frappe.db.commit()
counts['Workload Distributor'] = frappe.db.count('Workload Distributor')
print(f"Workload Distributor: {counts['Workload Distributor']}")

# ---------------------------------------------------------------------------
# 4. Feedback Form (2 records) — naming_series, set name manually
# ---------------------------------------------------------------------------
ff_names = [f'FF-{YYYY}-00001', f'FF-{YYYY}-00002']
ff_titles = ['Course Feedback Form', 'Faculty Feedback Form']
ff_types = ['Course Feedback', 'Faculty Feedback']
start_dt = str(TODAY - timedelta(days=7)) + ' 00:00:00'
end_dt = str(TODAY + timedelta(days=7)) + ' 23:59:59'

for i, (ff_name, title, ftype) in enumerate(zip(ff_names, ff_titles, ff_types)):
    if not frappe.db.exists('Feedback Form', ff_name):
        doc = frappe.new_doc('Feedback Form')
        doc.name = ff_name
        doc.naming_series = 'FF-.YYYY.-'
        doc.form_title = title
        doc.form_type = ftype
        doc.target_audience = 'Students'
        doc.start_date = start_dt
        doc.end_date = end_dt
        doc.status = 'Active'
        doc.append('questions', {
            'question_text': 'Rate the overall quality',
            'question_type': 'Rating (1-5)',
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != ff_name:
            frappe.db.sql(f"UPDATE `tabFeedback Form` SET name=%s WHERE name=%s", (ff_name, doc.name))
            frappe.db.sql(f"UPDATE `tabFeedback Question` SET parent=%s WHERE parent=%s", (ff_name, doc.name))

frappe.db.commit()
counts['Feedback Form'] = frappe.db.count('Feedback Form')
print(f"Feedback Form: {counts['Feedback Form']}")

# ---------------------------------------------------------------------------
# 5. Feedback Response (10 records) — naming_series, set name manually
# ---------------------------------------------------------------------------
for i in range(1, 11):
    fr_name = f'FR-{YYYY}-{i:05d}'
    if not frappe.db.exists('Feedback Response', fr_name):
        ff_form = ff_names[(i - 1) % 2]
        questions = frappe.db.sql(
            "SELECT name FROM `tabFeedback Question` WHERE parent=%s LIMIT 1",
            ff_form, as_dict=True
        )
        question_id = questions[0].name if questions else 'Q1'

        doc = frappe.new_doc('Feedback Response')
        doc.name = fr_name
        doc.naming_series = 'FR-.YYYY.-'
        doc.feedback_form = ff_form
        doc.respondent_type = 'Student'
        doc.append('answers', {
            'question_id': question_id,
            'answer_value': '4',
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != fr_name:
            frappe.db.sql(f"UPDATE `tabFeedback Response` SET name=%s WHERE name=%s", (fr_name, doc.name))
            frappe.db.sql(f"UPDATE `tabFeedback Answer` SET parent=%s WHERE parent=%s", (fr_name, doc.name))

frappe.db.commit()
counts['Feedback Response'] = frappe.db.count('Feedback Response')
print(f"Feedback Response: {counts['Feedback Response']}")

# ---------------------------------------------------------------------------
# 6. Placement Drive (2 records) — naming_series
# ---------------------------------------------------------------------------
pd_data = [
    (f'PD-{YYYY}-00001', 'Google', 'Software Engineer'),
    (f'PD-{YYYY}-00002', 'Amazon', 'Data Analyst'),
]
drive_date = TODAY + timedelta(days=30)
last_apply = TODAY + timedelta(days=14)

created_drives = []
for pd_name, company, job_title in pd_data:
    if not frappe.db.exists('Placement Drive', pd_name):
        doc = frappe.new_doc('Placement Drive')
        doc.name = pd_name
        doc.naming_series = 'PD-.YYYY.-'
        doc.company = company
        doc.job_title = job_title
        doc.drive_date = drive_date
        doc.last_date_to_apply = last_apply
        doc.status = 'Open'
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != pd_name:
            frappe.db.sql(f"UPDATE `tabPlacement Drive` SET name=%s WHERE name=%s", (pd_name, doc.name))
    created_drives.append(pd_name)

frappe.db.commit()
counts['Placement Drive'] = frappe.db.count('Placement Drive')
print(f"Placement Drive: {counts['Placement Drive']}")

# ---------------------------------------------------------------------------
# 7. Placement Application (8 records) — naming_series
# ---------------------------------------------------------------------------
pa_students = [
    'EDU-STU-2026-00174', 'EDU-STU-2026-00173', 'EDU-STU-2026-00172',
    'EDU-STU-2026-00171', 'EDU-STU-2026-00170', 'EDU-STU-2026-00174',
    'EDU-STU-2026-00173', 'EDU-STU-2026-00172',
]
drives_cycle = [created_drives[0]] * 4 + [created_drives[1]] * 4

for i in range(1, 9):
    pa_name = f'PA-{YYYY}-{i:05d}'
    if not frappe.db.exists('Placement Application', pa_name):
        doc = frappe.new_doc('Placement Application')
        doc.name = pa_name
        doc.naming_series = 'PA-.YYYY.-'
        doc.student = pa_students[i - 1]
        doc.placement_drive = drives_cycle[i - 1]
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != pa_name:
            frappe.db.sql(f"UPDATE `tabPlacement Application` SET name=%s WHERE name=%s", (pa_name, doc.name))

frappe.db.commit()
counts['Placement Application'] = frappe.db.count('Placement Application')
print(f"Placement Application: {counts['Placement Application']}")

# ---------------------------------------------------------------------------
# 8. Transport Trip Log (10 records) — naming_series, submittable
# ---------------------------------------------------------------------------
trip_types = ['Morning', 'Evening']
routes = ['Route A', 'Route B', 'Route C']
vehicles = ['NIT-01', 'NIT-02', 'NIT-03']

for i in range(1, 11):
    ttl_name = f'TTL-{YYYY}-{i:05d}'
    if not frappe.db.exists('Transport Trip Log', ttl_name):
        trip_date = TODAY - timedelta(days=i - 1)
        doc = frappe.new_doc('Transport Trip Log')
        doc.name = ttl_name
        doc.naming_series = 'TL-.YYYY.-'
        doc.trip_date = trip_date
        doc.trip_type = trip_types[(i - 1) % 2]
        doc.route = routes[(i - 1) % 3]
        doc.vehicle = vehicles[(i - 1) % 3]
        doc.status = 'Completed'
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != ttl_name:
            frappe.db.sql(f"UPDATE `tabTransport Trip Log` SET name=%s WHERE name=%s", (ttl_name, doc.name))
        frappe.db.set_value('Transport Trip Log', ttl_name, 'docstatus', 1)

frappe.db.commit()
counts['Transport Trip Log'] = frappe.db.count('Transport Trip Log')
print(f"Transport Trip Log: {counts['Transport Trip Log']}")

# ---------------------------------------------------------------------------
# 9. Hostel Visitor (5 records) — format:VIS-{YYYY}-{#####}, use direct SQL
# ---------------------------------------------------------------------------
visitor_data = [
    ('Ravi Kumar', '9876543210', 'Parent'),
    ('Priya Sharma', '9876543211', 'Sibling'),
    ('Suresh Patel', '9876543212', 'Guardian'),
    ('Meena Verma', '9876543213', 'Parent'),
    ('Ajay Singh', '9876543214', 'Relative'),
]
buildings = ['BH-01', 'GH-01', 'PGH-01']
vis_students = [
    'EDU-STU-2026-00174', 'EDU-STU-2026-00173', 'EDU-STU-2026-00172',
    'EDU-STU-2026-00171', 'EDU-STU-2026-00170',
]

for i, (vname, vmobile, rel) in enumerate(visitor_data, 1):
    hv_name = f'VIS-{YYYY}-{i:05d}'
    if not frappe.db.exists('Hostel Visitor', hv_name):
        sql_insert('Hostel Visitor', {
            'name': hv_name,
            'visitor_name': vname,
            'visitor_mobile': vmobile,
            'relationship': rel,
            'student': vis_students[i - 1],
            'building': buildings[(i - 1) % 3],
            'visit_date': str(TODAY),
            'check_in_time': '10:00:00',
        })

frappe.db.commit()
counts['Hostel Visitor'] = frappe.db.count('Hostel Visitor')
print(f"Hostel Visitor: {counts['Hostel Visitor']}")

# ---------------------------------------------------------------------------
# 10. Suggestion (5 records) — naming_series
# ---------------------------------------------------------------------------
sug_data = [
    ('Improve WiFi Coverage', 'Infrastructure', 'Please extend WiFi coverage to all hostel rooms and outdoor areas.'),
    ('Better Canteen Food', 'Services', 'Please look into this matter and take necessary action.'),
    ('More Study Rooms', 'Infrastructure', 'Please look into this matter and take necessary action.'),
    ('Sports Equipment', 'Services', 'Please provide updated sports equipment for the gymnasium.'),
    ('Lab Upgrades', 'Academic Improvement', 'Please look into this matter and take necessary action.'),
]

for i, (subject, category, suggestion) in enumerate(sug_data, 1):
    sug_name = f'SUG-{YYYY}-{i:05d}'
    if not frappe.db.exists('Suggestion', sug_name):
        doc = frappe.new_doc('Suggestion')
        doc.name = sug_name
        doc.naming_series = 'SUG-.YYYY.-'
        doc.subject = subject
        doc.category = category
        doc.suggestion = suggestion
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != sug_name:
            frappe.db.sql(f"UPDATE `tabSuggestion` SET name=%s WHERE name=%s", (sug_name, doc.name))

frappe.db.commit()
counts['Suggestion'] = frappe.db.count('Suggestion')
print(f"Suggestion: {counts['Suggestion']}")

# ---------------------------------------------------------------------------
# 11. LMS Content Progress (30 records) — format:{student}-{content}, use direct SQL
# ---------------------------------------------------------------------------
lms_students = [
    'EDU-STU-2026-00174', 'EDU-STU-2026-00173', 'EDU-STU-2026-00172',
    'EDU-STU-2026-00171', 'EDU-STU-2026-00170',
]
lms_contents = [
    'LC-.2026.-.00273', 'LC-.2026.-.00274', 'LC-.2026.-.00275',
    'LC-.2026.-.00276', 'LC-.2026.-.00277', 'LC-.2026.-.00278',
]
lms_statuses = ['Completed', 'In Progress']
lms_percentages = [100, 60]

for student in lms_students:
    for j, content in enumerate(lms_contents):
        cp_name = f'{student}-{content}'
        if not frappe.db.exists('LMS Content Progress', cp_name):
            status_idx = j % 2
            sql_insert('LMS Content Progress', {
                'name': cp_name,
                'student': student,
                'content': content,
                'status': lms_statuses[status_idx],
                'progress_percent': lms_percentages[status_idx],
            })

frappe.db.commit()
counts['LMS Content Progress'] = frappe.db.count('LMS Content Progress')
print(f"LMS Content Progress: {counts['LMS Content Progress']}")

# ---------------------------------------------------------------------------
# 12. Assignment Submission (20 records) — format:SUB-.{YYYY}.-.{#####}, use direct SQL
# ---------------------------------------------------------------------------
lms_assignments = [
    'ASN-.2026.-.00290', 'ASN-.2026.-.00289', 'ASN-.2026.-.00288', 'ASN-.2026.-.00287',
]
sub_date = str(TODAY - timedelta(days=2))

seq = 1
for student in lms_students:
    for assignment in lms_assignments:
        sub_name = f'SUB-{YYYY}-{seq:05d}'
        if not frappe.db.exists('Assignment Submission', sub_name):
            sql_insert('Assignment Submission', {
                'name': sub_name,
                'assignment': assignment,
                'student': student,
                'status': 'Submitted',
                'submission_date': sub_date,
            })
        seq += 1

frappe.db.commit()
counts['Assignment Submission'] = frappe.db.count('Assignment Submission')
print(f"Assignment Submission: {counts['Assignment Submission']}")

# ---------------------------------------------------------------------------
# 13. Quiz Attempt (15 records) — format:QA-.{YYYY}.-.{#####}, use direct SQL
# ---------------------------------------------------------------------------
lms_quizzes = ['QZ-.2026.-.00293', 'QZ-.2026.-.00292', 'QZ-.2026.-.00291']
scores_cycle = [8, 7, 9, 6, 8]

seq = 1
for student in lms_students:
    for k, quiz in enumerate(lms_quizzes):
        qa_name = f'QA-{YYYY}-{seq:05d}'
        if not frappe.db.exists('Quiz Attempt', qa_name):
            sql_insert('Quiz Attempt', {
                'name': qa_name,
                'quiz': quiz,
                'student': student,
                'marks_obtained': scores_cycle[(seq - 1) % len(scores_cycle)],
                'status': 'Graded',
            })
        seq += 1

frappe.db.commit()
counts['Quiz Attempt'] = frappe.db.count('Quiz Attempt')
print(f"Quiz Attempt: {counts['Quiz Attempt']}")

# ---------------------------------------------------------------------------
# 14. Student Transcript (5 records) — format:TR-{YYYY}-{#####}, use direct SQL
# ---------------------------------------------------------------------------
transcript_students = [
    'EDU-STU-2026-00174', 'EDU-STU-2026-00173', 'EDU-STU-2026-00172',
    'EDU-STU-2026-00171', 'EDU-STU-2026-00170',
]

for i, student in enumerate(transcript_students, 1):
    tr_name = f'TR-{YYYY}-{i:05d}'
    if not frappe.db.exists('Student Transcript', tr_name):
        sql_insert('Student Transcript', {
            'name': tr_name,
            'student': student,
            'transcript_type': 'Provisional',
        })

frappe.db.commit()
counts['Student Transcript'] = frappe.db.count('Student Transcript')
print(f"Student Transcript: {counts['Student Transcript']}")

# ---------------------------------------------------------------------------
# 15. Book Reservation (3 records) — naming_series
# ---------------------------------------------------------------------------
br_articles = ['LIB-2026-00114', 'LIB-2026-00112', 'LIB-2026-00110']
br_members = ['LM-2026-00030', 'LM-2026-00029', 'LM-2026-00028']

for i, (article, member) in enumerate(zip(br_articles, br_members), 1):
    br_name = f'BR-{YYYY}-{i:05d}'
    if not frappe.db.exists('Book Reservation', br_name):
        doc = frappe.new_doc('Book Reservation')
        doc.name = br_name
        doc.naming_series = 'BR-.YYYY.-'
        doc.article = article
        doc.member = member
        doc.reservation_date = TODAY
        doc.status = 'Pending'
        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_autoname = True
        doc.insert(ignore_permissions=True)
        if doc.name != br_name:
            frappe.db.sql(f"UPDATE `tabBook Reservation` SET name=%s WHERE name=%s", (br_name, doc.name))

frappe.db.commit()
counts['Book Reservation'] = frappe.db.count('Book Reservation')
print(f"Book Reservation: {counts['Book Reservation']}")

# ---------------------------------------------------------------------------
# 16. User Notification (10 records) — UN-.#####, use direct SQL
# ---------------------------------------------------------------------------
notif_users = [
    'aditya.joshi@nit.edu', 'akash.dubey@nit.edu', 'ananya.gupta@nit.edu',
    'aparna.rajan@nit.edu', 'arjun.mehta@nit.edu',
]
notif_titles = [
    'Fee Reminder', 'Exam Schedule Released', 'Attendance Update',
    'Library Due', 'Assignment Due',
]

for i in range(1, 11):
    un_name = f'UN-{i:05d}'
    if not frappe.db.exists('User Notification', un_name):
        sql_insert('User Notification', {
            'name': un_name,
            'user': notif_users[(i - 1) % len(notif_users)],
            'title': notif_titles[(i - 1) % len(notif_titles)],
            'read': 0,
        })

frappe.db.commit()
counts['User Notification'] = frappe.db.count('User Notification')
print(f"User Notification: {counts['User Notification']}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== SEED SUMMARY ===")
targets = {
    'Library Fine': 3, 'Attendance': 15, 'Workload Distributor': 1,
    'Feedback Form': 2, 'Feedback Response': 10, 'Placement Drive': 2,
    'Placement Application': 8, 'Transport Trip Log': 10, 'Hostel Visitor': 5,
    'Suggestion': 5, 'LMS Content Progress': 30, 'Assignment Submission': 20,
    'Quiz Attempt': 15, 'Student Transcript': 5, 'Book Reservation': 3,
    'User Notification': 10,
}
all_ok = True
for dt, target in targets.items():
    count = frappe.db.count(dt)
    status = 'OK' if count >= target else 'FAIL'
    if status == 'FAIL':
        all_ok = False
    print(f"  {status} {dt}: {count} (need {target})")

print(f"\n{'ALL OK' if all_ok else 'SOME FAILED'}")
print("Done.")

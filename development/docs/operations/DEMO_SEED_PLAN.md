# Reusable Demo Data Seed Plan — University ERP

## Purpose

This plan is designed to be **shared with Claude each time** you need to seed fresh demo data for a live demo. It handles:
1. **Deleting** all old transactional/live data (keeping master data intact)
2. **Seeding** fresh, date-relative transactional data that looks "live" at demo time

**File location**: Save this to `/workspace/development/docs/DEMO_SEED_PLAN.md`

## How to Use

Tell Claude:
> "Follow the plan at `/workspace/development/docs/DEMO_SEED_PLAN.md` to seed fresh demo data for today's demo."

Claude will:
1. Delete all transactional data (Step 1)
2. Seed fresh data with dates relative to today (Step 2)
3. Verify counts (Step 3)

---

## Step 0: Environment Setup

```python
import os; os.chdir('/workspace/development/frappe-bench')
import frappe
frappe.init(site='university.local', sites_path='sites')
frappe.connect()
frappe.set_user('Administrator')
from datetime import date, timedelta, datetime
import random
random.seed(42)
TODAY = date.today()
```

All dates below use `TODAY`, `TODAY - timedelta(days=N)`, etc. so data always looks fresh.

---

## Step 1: Delete Old Transactional Data

Delete in this exact order (children before parents, submittable cancelled first). **DO NOT delete master data.**

### What to DELETE (transactional — changes every demo):

```python
# Order matters: children/submittable first
TRANSACTIONAL_DOCTYPES = [
    # LMS engagement
    'LMS Content Progress', 'Assignment Submission', 'Quiz Attempt',
    # Feedback
    'Feedback Response', 'Feedback Form',
    # Placement activity
    'Placement Application', 'Placement Drive',
    # OBE calculations
    'CO Attainment',
    # Student portal live data
    'Student Attendance', 'Assessment Result', 'Assessment Plan',
    'Course Schedule', 'University Announcement',
    'Grievance', 'Certificate Request',
    'User Notification', 'Student Transcript', 'Book Reservation',
    # Hostel live data
    'Hostel Attendance', 'Hostel Maintenance Request', 'Hostel Visitor',
    'Mess Menu',
    # Library live data
    'Library Transaction', 'Library Fine',
    # Transport live data
    'Transport Trip Log',
    # HR live data
    'Attendance',  # HRMS
    'Leave Application',
    # Faculty live data
    'Student Feedback', 'Teaching Assignment', 'Workload Distributor',
    # Finance live data
    'Fee Payment', 'Student Scholarship',
    # Exam live data
    'Internal Assessment', 'Hall Ticket', 'Exam Schedule',
    # Misc
    'Suggestion', 'Notice Board', 'Notification Template',
]
```

**Delete logic** for each doctype:
```python
for dt in TRANSACTIONAL_DOCTYPES:
    try:
        meta = frappe.get_meta(dt)
        if meta.is_submittable:
            # Cancel submitted docs first
            for d in frappe.get_all(dt, filters={'docstatus': 1}):
                frappe.db.set_value(dt, d.name, 'docstatus', 2)
            frappe.db.commit()
        # Delete all
        frappe.db.sql(f'DELETE FROM `tab{dt}`')
        # Delete child tables
        for f in meta.fields:
            if f.fieldtype == 'Table':
                frappe.db.sql(f'DELETE FROM `tab{f.options}` WHERE parenttype=%s', dt)
        frappe.db.commit()
    except Exception as e:
        print(f'Skip {dt}: {e}')
```

### What to KEEP (master data — never delete):

```
Company, Fiscal Year, Academic Year, Academic Term, Cost Center, Mode of Payment,
Designation, Holiday List, Employee Group, Grading Scale,
Room, Student Category, Student Batch Name, Assessment Criteria, Assessment Group,
Topic, Program, Course, Fee Structure, Fee Category,
Employee, Leave Type, Leave Policy, Salary Component, Salary Structure,
Guardian, Student, Instructor, Student Group, Program Enrollment, Course Enrollment,
University Department, University Laboratory,
Timetable Slot, Elective Course Group, Admission Cycle, Admission Criteria, Seat Matrix,
Question Tag, Question Bank, Question Paper Template, External Examiner,
Fees (keep — these are semester fees, not payments),
Scholarship Type,
Faculty Profile,
Hostel Building, Hostel Room, Hostel Mess,
Library Category, Library Subject, Library Article, Library Member,
LMS Course, LMS Content, LMS Assignment, LMS Quiz, LMS Discussion,
Industry Type, Placement Company, Placement Job Opening, Student Resume,
Research Publication, Research Project, Research Grant,
Program Educational Objective, Program Outcome, Course Outcome,
CO PO Mapping, Assessment Rubric,
Transport Route, Transport Vehicle, Transport Allocation,
Certificate Template, Grievance Type,
User
```

---

## Step 2: Seed Fresh Data

**Important**: Always query existing master data by name before linking. Never hardcode IDs — use `frappe.get_all()`.

### 2.1 Course Schedule (20 records)

Weekly timetable for current week. Links: Student Group → Instructor → Course → Room.

```
Fields: student_group [REQD], instructor [REQD], course [REQD], room [REQD],
        schedule_date, from_time [REQD], to_time [REQD]
Use: flags.ignore_validate = True (avoids room overlap check)
```

**Data**: Mon-Fri of current week, 4 classes/day for CSE-2025-A, plus ECE/MTech/MBA slots.
Each slot uses a DIFFERENT room to avoid overlap. Use `rooms[i % len(rooms)]`.

### 2.2 University Announcement (5 records)

```
Fields: title [REQD], content (Text Editor) [REQD], publish_date [REQD],
        priority (Select: High/Medium/Low), target_audience (Select: All/Students/Faculty)
```

**Data**:
- "Mid-Semester Examination Schedule" (TODAY - 5 days, High)
- "Library Extended Hours During Exams" (TODAY - 3 days, Medium)
- "Annual Sports Day Registration" (TODAY - 7 days, Medium)
- "Hostel Room Inspection Notice" (TODAY - 1 day, Low)
- "Placement Drive: Amazon on Campus" (TODAY, High)

### 2.3 Student Attendance (100 records)

```
Fields: student [REQD], date [REQD], status (Select: Present/Absent) [REQD]
Submittable — insert then set docstatus=1 via DB
Use: flags.ignore_validate = True
```

**Data**: First 5 CSE students × 3 courses × ~7 working days (TODAY-10 to TODAY-2).
85% Present, 15% Absent (use `random.choices`).

### 2.4 Assessment Plan (10 records)

```
Fields: student_group [REQD], assessment_group [REQD], grading_scale [REQD],
        course [REQD], schedule_date [REQD], from_time [REQD], to_time [REQD],
        maximum_assessment_score [REQD],
        assessment_criteria (Table→Assessment Plan Criteria): assessment_criteria [REQD], maximum_score [REQD]
Submittable — insert then set docstatus=1 via DB
Use: flags.ignore_validate = True
```

**Data**: 2 per course (IA1 past, IA2 upcoming) for 5 courses. Scores: 50 max (2 criteria × 25 each).

### 2.5 Assessment Result (10 records)

```
Fields: assessment_plan (Link→Assessment Plan) [REQD], student [REQD],
        details (Table→Assessment Result Detail): assessment_criteria [REQD], score [REQD]
Submittable — insert then set docstatus=1 via DB
Use: flags.ignore_validate = True
```

**Data**: Link to the Assessment Plans from 2.4. Scores: random 15-23 per criteria.

### 2.6 Exam Schedule (6 records)

```
Fields: course [REQD], academic_term [REQD], exam_type (Select: Mid-Term/End-Term) [REQD],
        exam_date [REQD], start_time [REQD], end_time [REQD], venue (Link→Room) [REQD],
        invigilators (Table→Exam Invigilator): instructor [REQD], role
```

**Data**: 6 courses, mid-term exams scheduled TODAY+5 to TODAY+10.

### 2.7 Hall Ticket (30 records)

```
Fields: student [REQD], academic_term [REQD], exam_type (Select: Regular),
        exams (Table→Hall Ticket Exam): course [REQD], exam_date, exam_time, venue
Submittable. Use: flags.ignore_validate = True (bypasses attendance check)
Insert then set docstatus=1 via DB.
```

**Data**: One per student, linked to exam schedules from 2.6.

### 2.8 Internal Assessment (12 records)

```
Fields: assessment_name [REQD], assessment_type (Select: Class Test/Assignment) [REQD],
        academic_year [REQD], academic_term [REQD], course [REQD],
        assessment_date [REQD], maximum_marks [REQD],
        scores (Table→Internal Assessment Score): student [REQD], total_marks, percentage
Submittable. Use: flags.ignore_validate = True + flags.ignore_links = True
Insert then set docstatus=1 via DB.
```

**Data**: 2 per course (6 courses). IA1: TODAY-20, IA2: TODAY-5. Marks: random 12-24 out of 25.

### 2.9 Fee Payment (20 records)

```
Fields: fee (Link→Fees) [REQD], student [REQD], amount [REQD],
        payment_date [REQD], payment_mode (Select: Cash/Bank Transfer/Online Payment/DD) [REQD]
Submittable. Use: flags.ignore_validate = True. Insert then set docstatus=1 via DB.
```

**Data**: First 20 students. Amount: 50000-75000. Dates: TODAY-30 to TODAY-10.

### 2.10 Student Scholarship (5 records)

```
Fields: student [REQD], scholarship_type [REQD], status (Select: Active),
        valid_from [REQD], valid_till [REQD], discount_amount
Submittable. Insert then set docstatus=1 via DB.
```

**Data**: 3 Merit + 1 Need-based + 1 Sports for top 5 students.

### 2.11 Teaching Assignment (12 records)

```
Fields: academic_year [REQD], academic_term [REQD], course [REQD], program [REQD],
        instructor (Link→Employee) [REQD], lecture_hours, tutorial_hours, total_weekly_hours,
        schedule (Table→Teaching Assignment Schedule): day [REQD], start_time [REQD], end_time [REQD], room, type
Submittable. Use: flags.ignore_validate = True. Insert then set docstatus=1 via DB.
```

**Data**: 12 course-instructor mappings (see course_instructor_map in reference data below).

### 2.12 Student Feedback (10 records)

```
Fields: student [REQD], academic_year [REQD], academic_term [REQD],
        course [REQD], instructor (Link→Employee) [REQD],
        subject_knowledge (Rating) [REQD], teaching_methodology (Rating) [REQD],
        communication_skills (Rating) [REQD], availability (Rating) [REQD],
        course_coverage (Rating) [REQD], overall_rating (Rating) [REQD]
Submittable. Use: flags.ignore_validate = True. Insert then set docstatus=1 via DB.
```

**Data**: Ratings 3.5-5.0. Mix of students and courses.

### 2.13 Hostel Attendance (30 records)

```
Fields: student [REQD], hostel_building [REQD], room, attendance_date [REQD],
        status (Select: Present/Absent/On Leave/Late), in_time
```

**Data**: 15 students × 2 days (TODAY-1, TODAY-2). 80% Present, 10% Late, 10% Absent.

### 2.14 Hostel Maintenance Request (2 records)

```
Fields: request_date [REQD], building [REQD], room, requested_by (Link→Student),
        request_type (Select: Electrical/Plumbing/Internet/...) [REQD],
        priority (Select) , subject [REQD], description [REQD], status (Select)
Submittable. Use: flags.ignore_validate = True.
```

**Data**: 1 Resolved (WiFi, TODAY-5) + 1 Open (Plumbing, TODAY-1).

### 2.15 Mess Menu (2 records)

```
Fields: mess [REQD], week_start_date [REQD], status,
        menu_items (Table→Mess Menu Item): day [REQD], meal_type [REQD], menu_items [REQD]
```

**Data**: Current week menu for Central Mess + PG Mess. Full 7-day × 4-meal menu.

### 2.16 Library Transaction (8 records)

```
Fields: naming_series [REQD], transaction_type (Select: Issue/Return) [REQD],
        article [REQD], member [REQD], transaction_date [REQD],
        issue_date, due_date, return_date, status (Select: Active/Returned)
```

**Data**: 4 active issues + 4 returned. Dates: last 2 weeks.

### 2.17 Library Fine (3 records)

```
Fields: naming_series [REQD], member [REQD], fine_date [REQD], fine_amount [REQD],
        status (Select: Unpaid/Paid/Waived), article, reason
```

**Data**: ₹50 Paid, ₹100 Unpaid, ₹25 Waived. Overdue book returns.

### 2.18 Grievance (2 records)

```
Fields: naming_series [REQD], subject [REQD], grievance_type [REQD],
        category (Select) [REQD], priority (Select) [REQD],
        submitted_by_type (Select) [REQD], student (Link→Student),
        description [REQD], status (Select: Submitted/Resolved/...)
Use: flags.ignore_validate = True (needs student field for Student type).
```

**Data**: 1 Resolved + 1 Submitted.

### 2.19 Certificate Request (2 records)

```
Fields: naming_series [REQD], student [REQD], certificate_template [REQD], request_date [REQD]
Submittable. Use: flags.ignore_validate = True.
```

**Data**: 1 Approved (Bonafide) + 1 Pending (Transfer).

### 2.20 Leave Application (5 records)

```
Fields: naming_series [REQD], employee [REQD], leave_type [REQD],
        company [REQD], from_date [REQD], to_date [REQD], status
Submittable. Use: flags.ignore_validate = True. Submit approved ones via DB.
```

**Data**: 3 Approved + 2 Open. Faculty employees. Dates: next 1-2 weeks.

### 2.21 Notice Board (5 records)

```
Check schema before inserting: frappe.get_meta('Notice Board') for exact field names.
```

### 2.22 Notification Template (5 records)

```
Fields: template_name [REQD], subject [REQD], category (Select), enabled, template [REQD]
autoname = field:template_name — use unique names
```

### 2.23 Attendance — HRMS (15 records)

```
Fields: naming_series [REQD], employee [REQD], attendance_date [REQD],
        status (Select: Present/Absent/Half Day) [REQD], company [REQD]
Submittable. Use: flags.ignore_validate = True. Insert then set docstatus=1 via DB.
```

**Data**: All 15 employees for TODAY-1. 13 Present, 1 Half Day, 1 Absent.

### 2.24 Workload Distributor (1 record)

```
Fields: academic_year [REQD], academic_term [REQD]
```

### 2.25 Feedback Form (2 records)

```
Fields: naming_series [REQD], form_title [REQD], form_type (Select) [REQD],
        target_audience (Select) [REQD], start_date (Datetime) [REQD], end_date (Datetime) [REQD],
        questions (Table→Feedback Question): question_text [REQD], question_type [REQD], is_required
        status (Select: Active)
```

### 2.26 Feedback Response (10 records)

```
Fields: naming_series [REQD], feedback_form [REQD], respondent_type (Select) [REQD],
        student, answers (Table→Feedback Answer): question_id [REQD], answer_value
        status: Submitted
```

### 2.27 Placement Drive (2 records)

```
Fields: company [REQD], drive_date [REQD], academic_year [REQD],
        status, rounds (Table→Placement Round): round_number [REQD], round_name [REQD]
autoname: PD-.YYYY.-.##### — FIX FIRST if broken (replace .YYYY. with .{YYYY}. and .##### with .{#####})
```

### 2.28 Placement Application (8 records)

```
Fields: naming_series [REQD], student [REQD], job_opening [REQD],
        application_date [REQD], status (Select: Applied/Shortlisted/Selected/Placed/Rejected)
```

### 2.29 CO Attainment (6 records)

```
Fields: course [REQD], academic_term [REQD],
        direct_attainment_table (Table→CO Direct Attainment):
          course_outcome [REQD], assessment_type [REQD], max_marks [REQD],
          target_percent [REQD], total_students [REQD], students_above_target [REQD]
Submittable. Use: flags.ignore_validate = True. Insert then set docstatus=1 via DB.
```

**Data**: 2 per course (DS, DBMS, OS). Link to Course Outcomes.

### 2.30 Transport Trip Log (10 records)

```
Fields: naming_series [REQD], trip_date [REQD], trip_type (Select: Morning/Evening) [REQD],
        route [REQD], vehicle [REQD], status (Select: Completed)
```

**Data**: 3 routes × 2 types × ~2 days. TODAY-1, TODAY-2.

### 2.31 Hostel Visitor (5 records)

```
Fields: visitor_name [REQD], visitor_mobile [REQD], relationship (Select) [REQD],
        student [REQD], building [REQD], visit_date [REQD], check_in_time [REQD],
        status (Select: Checked In/Checked Out)
autoname: format:VIS-{YYYY}-{#####}
```

### 2.32 Suggestion (5 records)

```
Fields: naming_series [REQD], subject [REQD], category (Select) [REQD],
        suggestion (Text Editor) [REQD], status (Select)
```

### 2.33 LMS Content Progress (30 records)

```
Fields: student [REQD], content [REQD], status (Select), progress_percent, time_spent_minutes
autoname: format:{student}-{content}
```

**Data**: 5 students × 6 LMS Contents. 60% Completed, 30% In Progress, 10% Not Started.

### 2.34 Assignment Submission (20 records)

```
Fields: assignment [REQD], student [REQD], status (Select: Graded), marks_obtained
autoname: format:SUB-.{YYYY}.-.{#####}
```

**Data**: 5 students × 4 assignments. Marks: 15-24 out of 25.

### 2.35 Quiz Attempt (15 records)

```
Fields: quiz [REQD], student [REQD], status (Select: Graded),
        marks_obtained, total_marks, percentage, passed,
        answers (Table→Quiz Answer): question_idx [REQD], student_answer, is_correct, marks_obtained
autoname: format:QA-.{YYYY}.-.{#####}
```

**Data**: 5 students × 3 quizzes. Scores: 12-19 out of 20.

### 2.36 Student Transcript (5 records)

```
Fields: student [REQD], transcript_type (Select: Provisional) [REQD],
        semester_results (Table→Transcript Semester Result): semester, credits_earned, sgpa, cgpa
Submittable. Insert then set docstatus=1 via DB.
autoname: format:TR-{YYYY}-{#####}
```

### 2.37 Book Reservation (3 records)

```
Fields: naming_series [REQD], article [REQD], member [REQD], reservation_date [REQD],
        status (Select: Pending/Available/Fulfilled)
```

### 2.38 User Notification (10 records)

```
Fields: user [REQD], title [REQD], message, notification_type (Select),
        category (Select), priority (Select), read (Check)
autoname: UN-.#####
```

**Data**: 2 per student user (student1-student5@nit.edu): fee reminder + exam alert.

---

## Step 3: Verify

Run count check for all transactional doctypes:
```python
expected = {
    'Course Schedule': 20, 'University Announcement': 5, 'Student Attendance': 100,
    'Assessment Plan': 10, 'Assessment Result': 10, 'Exam Schedule': 6,
    'Hall Ticket': 30, 'Internal Assessment': 12, 'Fee Payment': 20,
    'Student Scholarship': 5, 'Teaching Assignment': 12, 'Student Feedback': 10,
    'Hostel Attendance': 30, 'Hostel Maintenance Request': 2, 'Mess Menu': 2,
    'Library Transaction': 8, 'Library Fine': 3, 'Grievance': 2,
    'Certificate Request': 2, 'Leave Application': 5, 'Notice Board': 5,
    'Notification Template': 5, 'Attendance': 15, 'Workload Distributor': 1,
    'Feedback Form': 2, 'Feedback Response': 10,
    'Placement Drive': 2, 'Placement Application': 8,
    'CO Attainment': 6, 'Transport Trip Log': 10, 'Hostel Visitor': 5,
    'Suggestion': 5, 'LMS Content Progress': 30, 'Assignment Submission': 20,
    'Quiz Attempt': 15, 'Student Transcript': 5, 'Book Reservation': 3,
    'User Notification': 10,
}
```

---

## Reference Data (Master — Do Not Delete)

```
Students (first 5 — key demo students):
  Query: frappe.get_all('Student', fields=['name','student_name','user'], order_by='name', limit=5)
  These are B.Tech CSE students enrolled in: Operating Systems, Database Systems, Data Structures

All Students: 30 total (20 CSE, 5 ECE, 3 M.Tech, 2 MBA)
  Query: frappe.get_all('Student', fields=['name','student_name'], order_by='name')

Faculty Employees (10):
  Query: frappe.get_all('Employee', filters={'designation':['in',['Professor','Associate Professor','Assistant Professor']]}, fields=['name','employee_name'], order_by='name')

All Employees (15):
  Query: frappe.get_all('Employee', fields=['name','employee_name'], order_by='name')

Course-Instructor Mapping (12):
  ('Data Structures','B.Tech Computer Science', <emp_00009>),
  ('Database Systems','B.Tech Computer Science', <emp_00010>),
  ('Operating Systems','B.Tech Computer Science', <emp_00011>),
  ('Computer Networks','B.Tech Computer Science', <emp_00012>),
  ('Software Engineering','M.Tech Computer Science', <emp_00013>),
  ('Web Technologies','M.Tech Computer Science', <emp_00014>),
  ('Artificial Intelligence','M.Tech Computer Science', <emp_00015>),
  ('Digital Electronics','B.Tech Electronics', <emp_00016>),
  ('Microprocessors','B.Tech Electronics', <emp_00017>),
  ('Engineering Mathematics','B.Tech Electronics', <emp_00018>),
  ('Communication Skills','MBA', <emp_00009>),
  ('Environmental Science','MBA', <emp_00010>),

Company: Hanumatrix
Academic Year: 2025-26
Academic Term: 2025-26 (Odd Semester)
Grading Scale: (query first available)
Hostel Buildings: BH-01 (Boys), GH-01 (Girls), PGH-01 (PG)
Hostel Rooms: 30 (query frappe.get_all('Hostel Room'))
Hostel Mess: Central Mess, PG Mess
Transport Routes: 3 (query frappe.get_all('Transport Route'))
Transport Vehicles: 3 (query frappe.get_all('Transport Vehicle'))
Placement Companies: TCS, Infosys, Wipro, Amazon, Google
Job Openings: 5 (query frappe.get_all('Placement Job Opening'))
Library Members: 10 (query frappe.get_all('Library Member'))
Library Articles: 20 (query frappe.get_all('Library Article'))
LMS Courses: 6 (query frappe.get_all('LMS Course'))
LMS Content: 12 (query frappe.get_all('LMS Content'))
LMS Assignments: 6 (query frappe.get_all('LMS Assignment'))
LMS Quizzes: 3 (query frappe.get_all('LMS Quiz'))
Course Outcomes: 15 (query frappe.get_all('Course Outcome'))
Certificate Templates: 3 (query frappe.get_all('Certificate Template'))
Grievance Types: 5 (query frappe.get_all('Grievance Type'))
Scholarship Types: 3 (Merit, Need-Based, Sports)
Assessment Criteria: 6 (query frappe.get_all('Assessment Criteria'))
Student Groups: CSE-2025-A, CSE-2024-A, ECE-2024-A, MTech-2025, MBA-2025, CSE-2023-A
Rooms: 10 (query frappe.get_all('Room'))
Fees: 30 (one per student, query frappe.get_all('Fees'))
```

## Known Schema Gotchas

1. **Broken autonames**: Some doctypes have `.YYYY.` and `.#####` instead of `{YYYY}` and `{#####}` in `format:` autonames. Fix via: `frappe.db.sql('UPDATE tabDocType SET autoname=REPLACE(REPLACE(autoname, ".YYYY.", ".{YYYY}."), ".#####", ".{#####}") WHERE autoname LIKE "format:%" AND autoname LIKE "%.YYYY.%"')`
2. **Broken select options**: Some Select fields have literal `\n` instead of newlines. Already fixed (754 fields), but if new ones appear: `frappe.db.sql('UPDATE tabDocField SET options=REPLACE(options, "\\\\n", "\n") WHERE fieldtype="Select" AND options LIKE "%\\\\\\\\n%"')`
3. **Submittable docs**: Never use `.submit()` — on_submit hooks often hit missing custom fields. Instead: insert with `flags.ignore_validate=True`, then `frappe.db.set_value(dt, name, 'docstatus', 1)`
4. **Hall Ticket validate**: Imports from `university_erp.academics.attendance` which doesn't exist. Always use `flags.ignore_validate=True`
5. **Teaching Assignment on_submit**: Tries to update `custom_current_workload` on Employee (missing column). Submit via DB.
6. **Course Outcome validate**: Reads `course_code` from Course (missing column). Use `flags.ignore_validate=True`
7. **Assessment Rubric validate**: Queries `user` on Instructor (missing column). Use `flags.ignore_validate=True`
8. **Grievance validate**: Requires `student` field when `submitted_by_type='Student'`. Use `flags.ignore_validate=True`
9. **LMS Content validate**: Document type requires file attachment. Use `content_type='Text'` or `flags.ignore_validate=True`
10. **Research Publication validate**: Requires at least one author in `authors` child table

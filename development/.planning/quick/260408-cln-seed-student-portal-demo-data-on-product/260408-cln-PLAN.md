---
phase: quick
plan: 260408-cln
type: execute
wave: 1
depends_on: []
files_modified:
  - seed_production_portal_data.py
autonomous: true
requirements: []

must_haves:
  truths:
    - "Student portal timetable shows classes for current and next week"
    - "Student portal attendance section shows recent attendance data"
    - "Student portal shows assessment results with real scores and grades"
    - "Student portal shows Semester 2 fees with some pending"
    - "Notice board shows current, non-expired notices"
    - "Hostel allocation is active for current semester"
    - "Library shows currently-issued books with future due dates"
    - "Mess menu shows current week meals"
    - "All 15 login-enabled students appear in course student groups"
    - "Student CGPA values are realistic (7.0-9.5 range)"
  artifacts:
    - path: "seed_production_portal_data.py"
      provides: "Idempotent production data seeder for all 12 portal data gaps"
  key_links:
    - from: "Course Schedule records"
      to: "Student Attendance records"
      via: "course_schedule link field"
    - from: "Student Group Student entries"
      to: "Course Schedule query"
      via: "student_group filter in timetable view"
---

<objective>
Create and deploy a single idempotent Python script to seed fresh transactional data on production (ems.hanumatrix.com) for all 12 identified student portal data gaps. The script fixes stale/missing data so the student portal demo showcases a fully working system with current-week timetables, recent attendance, real grades, active hostel allocations, fresh library transactions, current notices, and Semester 2 fees.

Purpose: Enable a convincing demo of the student portal at ems.hanumatrix.com with realistic, current data across all portal sections.
Output: One deployed-and-executed script that resolves all 12 data gaps.
</objective>

<execution_context>
@/workspace/development/.claude/get-shit-done/workflows/execute-plan.md
@/workspace/development/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md

Production environment:
- SSH: root@ems.hanumatrix.com
- Container: ems-backend
- Python: /home/frappe/frappe-bench/env/bin/python
- Site: ems.hanumatrix.com
- Scripts must os.chdir("/home/frappe/frappe-bench/sites") before frappe.init()

Deployment pattern:
```bash
scp script.py root@ems.hanumatrix.com:/tmp/script.py
ssh root@ems.hanumatrix.com 'docker cp /tmp/script.py ems-backend:/tmp/script.py'
ssh root@ems.hanumatrix.com 'docker exec -w /home/frappe/frappe-bench ems-backend /home/frappe/frappe-bench/env/bin/python /tmp/script.py'
```

Established seed pattern from seed_comprehensive_demo_data.py:
- Idempotent: frappe.db.exists() check before every insert
- _safe() wrapper with traceback for each section
- frappe.db.commit() after each section
- frappe.set_user("Administrator") for all operations
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write production portal data seeder script</name>
  <files>seed_production_portal_data.py</files>
  <action>
Create a self-contained Python script `seed_production_portal_data.py` at the project root that addresses ALL 12 data gaps. The script must:

**Bootstrap pattern (top of script):**
```python
import os, sys
os.chdir("/home/frappe/frappe-bench/sites")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/frappe")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/erpnext")
sys.path.insert(0, "/home/frappe/frappe-bench/apps/university_erp")
import frappe
frappe.init(site="ems.hanumatrix.com")
frappe.connect()
frappe.set_user("Administrator")
```

**Gap 1 - Student Group Student entries:**
- Query all 15 students with user accounts (student1@nit.edu through student15@nit.edu)
- Query all course-based student groups (names containing "CSE-2026-" pattern for B.Tech CS students)
- For each student, for each relevant course-based group, insert Student Group Student if not exists
- Match students to groups by their program: B.Tech CS students go in CSE course groups, B.Tech Elec in ECE groups, etc.
- Use frappe.get_doc("Student Group", name).append("students", {...}).save() pattern

**Gap 2 - Course Schedules (current + next week):**
- Create course schedules for 2026-04-07 to 2026-04-11 (this week) and 2026-04-14 to 2026-04-18 (next week)
- Use existing student groups, courses, instructors, and rooms from DB
- Schedule 3-4 classes per day per student group with realistic times: 9:00-10:00, 10:15-11:15, 11:30-12:30, 14:00-15:00
- Check frappe.db.exists("Course Schedule", filters) before creating each
- Set instructor and instructor_name from existing instructor records

**Gap 3 - Student Attendance:**
- Create attendance for the past 3 weeks (2026-03-23 to 2026-04-07) linked to the new course schedules
- For each course schedule, create Student Attendance for all students in that student group
- Mix of statuses: ~75% Present, ~15% Absent, ~10% Late (use random weights)
- Link via course_schedule field to the corresponding Course Schedule record

**Gap 4 - Assessment Results:**
- Update existing 10 assessment results: set total_score to random 55-95 (out of 100 max), compute grade from score (A+/A/B+/B/C/F), set academic_term to "2025-26 (Semester 1)"
- Create 2-3 new assessment results per student for current semester courses
- Grades: >=90 A+, >=80 A, >=70 B+, >=60 B, >=50 C, <50 F

**Gap 5 - Student custom_cgpa:**
- For each of the 15 login-enabled students, compute average of their assessment scores
- Map to CGPA scale: score_avg * 10 / 100, then clamp to 7.0-9.5 range
- Update via frappe.db.set_value("Student", student_id, "custom_cgpa", cgpa_value)

**Gap 6 - Semester 2 Fees:**
- For students 145-159, create Fees record for academic_term "2025-26 (Semester 2)"
- Use Fee Component child table with: Tuition Fee (50000), Lab Fee (10000), Library Fee (5000), Exam Fee (3000) = grand_total 68000
- Set due_date to 2026-04-30
- For students 145-150: set outstanding_amount to 0 (fully paid)
- For students 151-155: set outstanding_amount to 68000 (fully pending)
- For students 156-159: set outstanding_amount to 18000 (partial - only tuition component paid)
- Submit each Fees doc (doc.submit()) so they show properly in portal

**Gap 7 - Notice Board:**
- Submit the 5 draft notices NB-00026 through NB-00030 (set docstatus=1 via frappe.db.set_value then frappe.get_doc and run doc.submit())
- Actually, use amend_and_submit pattern: load doc, check docstatus, if 0 then doc.submit()
- Create 4 new notices with current dates:
  1. "Mid-Semester Examination Schedule Released" (priority High, expiry 2026-04-30)
  2. "Annual Sports Day Registration Open" (priority Medium, expiry 2026-04-25)
  3. "Library Extended Hours During Exams" (priority Low, expiry 2026-04-20)
  4. "Summer Internship Applications Due" (priority High, expiry 2026-05-15)
- Set publish_date=today, audience_type="All", notice_type="Academic"/"Event"/"General"
- Submit each new notice (docstatus=1)

**Gap 8 - Hostel Allocation dates:**
- Find existing hostel allocations where to_date < "2026-04-08"
- Update to_date to "2026-06-30" via frappe.db.set_value
- If no allocations exist for a student, skip (don't create new ones, the data exists but dates are stale)

**Gap 9 - Library Transactions:**
- Find existing Library Transactions with type "Issue" and status "Active" where due_date has passed
- For each overdue: create a Return transaction (type="Return", return_date=today, status="Returned") and update the original Issue status to "Returned"
- Create 2-3 new Issue transactions for the primary demo student (EDU-STU-2026-00145 / LM-2026-00025):
  - Use existing Library Articles from DB
  - Set issue_date=today, due_date=2026-04-30, status="Active"

**Gap 10 - Mess Menu:**
- Create Mess Menu for current week (2026-04-06 to 2026-04-12) and next week (2026-04-13 to 2026-04-19)
- Use existing mess (query from Mess table) or the first hostel building name
- For each day, create Mess Menu Item entries: Breakfast (7:00-9:00), Lunch (12:00-14:00), Snacks (16:00-17:00), Dinner (19:00-21:00)
- Use realistic Indian mess menu items (idli/dosa for breakfast, rice/dal/curry for lunch, samosa/tea for snacks, roti/sabzi for dinner)
- Set status="Active"

**Gap 11 - Portal API field mismatch (hostel_room vs room):**
- This is noted as a code bug. Do NOT attempt to fix code on production.
- Add a comment in the script noting this is a known issue: `# NOTE: portal_api.py get_student_hostel() queries 'hostel_room' but DocType field is 'room' -- code fix needed`

**Gap 12 - Student Grievance DocType missing:**
- Do NOT create DocType remotely.
- Create 3-4 Suggestion records instead (the existing DocType on production):
  - "Improve Wi-Fi connectivity in hostel areas"
  - "Request for extended library hours during exams"
  - "Suggestion for more vegetarian options in mess"
  - "Need better lab equipment for Electronics lab"
- Set owner to student1@nit.edu, creation date to recent dates
- Add comment: `# NOTE: Student Grievance DocType does not exist on production. Suggestions created instead. Portal grievances.py will return empty until DocType is created.`

**Error handling:** Wrap each gap-fix in a _safe(label, fn) helper that catches exceptions, prints traceback, and continues to next section. Always frappe.db.commit() after each successful section.

**Script termination:**
```python
frappe.db.commit()
frappe.destroy()
print("DONE - All portal data gaps addressed")
```
  </action>
  <verify>
    <automated>python3 -c "import ast; ast.parse(open('seed_production_portal_data.py').read()); print('Syntax OK')"</automated>
  </verify>
  <done>Script exists at project root, passes Python syntax check, contains all 12 gap fixes with idempotent checks and error handling</done>
</task>

<task type="auto">
  <name>Task 2: Deploy and execute script on production</name>
  <files>seed_production_portal_data.py</files>
  <action>
Deploy the script to production and execute it using the established pattern:

```bash
# Step 1: Copy script to production host
scp /workspace/development/seed_production_portal_data.py root@ems.hanumatrix.com:/tmp/seed_production_portal_data.py

# Step 2: Copy into Docker container
ssh root@ems.hanumatrix.com 'docker cp /tmp/seed_production_portal_data.py ems-backend:/tmp/seed_production_portal_data.py'

# Step 3: Execute inside container
ssh root@ems.hanumatrix.com 'docker exec -w /home/frappe/frappe-bench ems-backend /home/frappe/frappe-bench/env/bin/python /tmp/seed_production_portal_data.py'
```

**If the script fails on any section:**
1. Read the error output carefully
2. Fix the specific failing function in the local script
3. Re-deploy and re-execute (the script is idempotent so already-completed sections will skip)
4. Repeat until all 12 sections pass

**After successful execution, verify key data exists by running spot checks:**
```bash
ssh root@ems.hanumatrix.com 'docker exec ems-backend /home/frappe/frappe-bench/env/bin/python -c "
import os; os.chdir(\"/home/frappe/frappe-bench/sites\")
import frappe; frappe.init(site=\"ems.hanumatrix.com\"); frappe.connect()
# Check course schedules this week
cs = frappe.db.count(\"Course Schedule\", {\"schedule_date\": [\"between\", [\"2026-04-07\", \"2026-04-11\"]]})
print(f\"Course Schedules this week: {cs}\")
# Check recent attendance
att = frappe.db.count(\"Student Attendance\", {\"date\": [\">=\", \"2026-03-23\"]})
print(f\"Recent attendance records: {att}\")
# Check student group student count
sgs = frappe.db.count(\"Student Group Student\")
print(f\"Student Group Student entries: {sgs}\")
# Check CGPA values
cgpa = frappe.db.sql(\"SELECT name, custom_cgpa FROM tabStudent WHERE custom_cgpa > 0 LIMIT 5\")
print(f\"Students with CGPA: {cgpa}\")
# Check Semester 2 fees
fees = frappe.db.count(\"Fees\", {\"academic_term\": \"2025-26 (Semester 2)\"})
print(f\"Semester 2 fees: {fees}\")
# Check active notices
notices = frappe.db.count(\"Notice Board\", {\"docstatus\": 1, \"expiry_date\": [\">=\", \"2026-04-08\"]})
print(f\"Active notices: {notices}\")
frappe.destroy()
"'
```

Expected outputs: Course Schedules this week > 15, Recent attendance > 50, Student Group Student entries > 30, Students with CGPA showing values 7.0-9.5, Semester 2 fees = 15, Active notices >= 5.
  </action>
  <verify>
    <automated>ssh root@ems.hanumatrix.com 'docker exec ems-backend /home/frappe/frappe-bench/env/bin/python -c "import os; os.chdir(\"/home/frappe/frappe-bench/sites\"); import frappe; frappe.init(site=\"ems.hanumatrix.com\"); frappe.connect(); cs=frappe.db.count(\"Course Schedule\",{\"schedule_date\":[\"between\",[\"2026-04-07\",\"2026-04-11\"]]}); att=frappe.db.count(\"Student Attendance\",{\"date\":[\">>=\",\"2026-03-23\"]}); print(f\"Schedules={cs} Attendance={att}\"); assert cs > 10, f\"Too few schedules: {cs}\"; assert att > 30, f\"Too few attendance: {att}\"; print(\"VERIFY OK\"); frappe.destroy()"'</automated>
  </verify>
  <done>Script executed successfully on production. Course schedules exist for current week. Recent attendance records created. All 15 students in course groups. CGPA values set. Semester 2 fees created. Notices active. Hostel dates extended. Library transactions current. Mess menu current.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Seeded all 12 data gaps on production student portal. The student portal at ems.hanumatrix.com should now show complete, current data across all sections.</what-built>
  <how-to-verify>
    1. Visit https://ems.hanumatrix.com and login as student1@nit.edu
    2. Check Timetable section -- should show classes for this week (Apr 7-11)
    3. Check Attendance section -- should show recent attendance with Present/Absent/Late mix
    4. Check Examinations/Results -- should show grades (A+, A, B+, etc.) with real scores
    5. Check Finance/Fees -- should show Semester 2 fees (some paid, some pending)
    6. Check Notices -- should show current, non-expired notices
    7. Check Hostel -- should show active allocation through June 2026
    8. Check Library -- should show currently issued books with future due dates
    9. Check overall CGPA display -- should show a value in 7.0-9.5 range
  </how-to-verify>
  <resume-signal>Type "approved" if portal looks good, or describe any sections that still show stale/empty data</resume-signal>
</task>

</tasks>

<verification>
All 12 data gaps addressed:
1. Student Group Students: 15 students distributed across course groups
2. Course Schedules: Current + next week schedules created
3. Student Attendance: 3 weeks of recent attendance with realistic mix
4. Assessment Results: Real scores and grades, academic_term set
5. Student CGPA: Realistic values in 7.0-9.5 range
6. Semester 2 Fees: 15 records with paid/pending/partial mix
7. Notice Board: Draft notices submitted + 4 new current notices
8. Hostel Allocations: Extended to 2026-06-30
9. Library Transactions: Overdue returned, new books issued
10. Mess Menu: Current and next week menus
11. Portal API bug: Noted (code fix separate)
12. Grievances: Suggestion records created as workaround
</verification>

<success_criteria>
- Script runs to completion on production without fatal errors
- Student portal at ems.hanumatrix.com shows current data in all sections when logged in as student1@nit.edu
- Spot-check queries confirm: >15 course schedules this week, >50 recent attendance records, 15 semester 2 fee records, >=5 active notices, CGPA values > 0
</success_criteria>

<output>
After completion, create `.planning/quick/260408-cln-seed-student-portal-demo-data-on-product/260408-cln-SUMMARY.md`
</output>

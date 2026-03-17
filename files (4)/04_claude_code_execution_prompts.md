# University ERP - Claude Code Execution Prompts

## Document Overview

| Item | Details |
|------|---------|
| **Document Version** | 1.0 |
| **Last Updated** | December 2025 |
| **Purpose** | Sequential execution prompts for Claude Code to implement University EMS |
| **Prerequisites** | All previous documents (01, 02, 03) reviewed |

---

## Execution Sequence Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXECUTION SEQUENCE (15 PHASES)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE A: Environment Setup (Prompts 1-3)                                  │
│  └── Docker, DevContainer, Base ERPNext Installation                        │
│                                                                             │
│  PHASE B: App Foundation (Prompts 4-6)                                      │
│  └── Create university_ems app, structure, hooks, install script           │
│                                                                             │
│  PHASE C: Core Module Development (Prompts 7-11)                           │
│  └── Hostel, Transport, Library, Examination, Placement modules            │
│                                                                             │
│  PHASE D: Quality Modules (Prompts 12-14)                                  │
│  └── NAAC, OBE, CBCS, Research modules                                     │
│                                                                             │
│  PHASE E: Supporting Modules (Prompts 15-16)                               │
│  └── Alumni, Grievance, Sports & Cultural modules                          │
│                                                                             │
│  PHASE F: Integration & Portal (Prompts 17-19)                             │
│  └── Student/Faculty portals, API layer, dashboards                        │
│                                                                             │
│  PHASE G: Testing & Deployment (Prompts 20-21)                             │
│  └── Testing suite, deployment configuration                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE A: Environment Setup

### Prompt 1: Docker Environment Setup

```
You are setting up a Frappe/ERPNext development environment for a University ERP system.

TASK: Create the complete Docker development environment.

Create the following files in ~/university-erp/:

1. docker-compose.yml with:
   - MariaDB 10.6 service with health checks
   - Redis cache, queue, and socketio services
   - Frappe/ERPNext backend service
   - Worker services (short, long, scheduler)
   - Nginx proxy service
   - Proper networking and volume configuration

2. Dockerfile.frappe with:
   - Python 3.11 base
   - All system dependencies
   - Node.js 18.x
   - Frappe bench installation
   - ERPNext v15, Education module, HRMS module

3. config/mariadb.cnf with:
   - UTF8MB4 character set
   - Optimized InnoDB settings
   - Connection pool settings

4. .env file with:
   - Database credentials
   - Redis configuration
   - Site configuration

After creating files, provide commands to:
- Build containers
- Start the environment
- Verify all services are running
- Access the application

Reference the detailed configuration from Document 01 for exact settings.
```

### Prompt 2: DevContainer Setup

```
You are configuring VS Code DevContainer for University ERP development.

TASK: Create the DevContainer configuration files.

Create in ~/university-erp/.devcontainer/:

1. devcontainer.json with:
   - Docker compose file references
   - VS Code settings for Python/JavaScript development
   - Required VS Code extensions
   - Port forwarding configuration
   - Post-create and post-start commands
   - Volume mounts for custom apps

2. docker-compose.devcontainer.yml with:
   - Development-specific overrides
   - Volume persistence for env and node_modules
   - Sleep infinity command for container persistence

3. post-create.sh script that:
   - Waits for database connection
   - Configures bench with Docker services
   - Creates new site if not exists
   - Installs ERPNext, Education, HRMS apps
   - Enables developer mode
   - Builds assets

4. post-start.sh script that:
   - Sets current site
   - Checks for pending migrations
   - Displays available commands

Make all scripts executable and test the DevContainer setup.
```

### Prompt 3: ERPNext Base Configuration

```
You are configuring the base ERPNext installation for university use.

TASK: Configure ERPNext modules and create initial master data.

Execute these steps inside the Frappe container:

1. Company Setup:
   - Create company with university details
   - Configure fiscal year aligned with academic year
   - Setup cost centers for departments

2. Education Module Configuration:
   - Create Academic Year master (2024-25, 2025-26)
   - Create Academic Terms (Odd Semester, Even Semester)
   - Create Student Categories (Regular, Lateral Entry)
   - Configure basic fee categories

3. HR Module Configuration:
   - Create Department structure
   - Create Designation hierarchy for faculty
   - Setup basic leave types
   - Configure attendance settings

4. User Roles Creation:
   - Create custom roles: Hostel Warden, Librarian, Examination Controller, etc.
   - Set up basic permissions

5. Accounting Setup:
   - Configure chart of accounts for educational institution
   - Setup fee income accounts
   - Configure tax templates (GST)

Provide the Python/bench commands to execute each step.
Output a verification checklist after completion.
```

---

## PHASE B: App Foundation

### Prompt 4: Create University EMS App

```
You are creating the University EMS custom Frappe app.

TASK: Create and structure the university_ems Frappe app.

1. Create the app:
   ```
   bench new-app university_ems
   ```
   App details:
   - Title: University ERP Management System
   - Publisher: University ERP Team
   - License: MIT

2. Create the directory structure with all modules:
   - university_ems/ (core)
   - hostel_management/
   - transport_management/
   - library_management/
   - advanced_examination/
   - training_placement/
   - accreditation/
   - obe_system/
   - cbcs_system/
   - research_management/
   - alumni_management/
   - grievance_management/
   - sports_cultural/
   - cafeteria_management/

   Each module should have:
   - __init__.py
   - doctype/ folder
   - report/ folder (where applicable)

3. Create modules.txt listing all modules

4. Create public/ folder structure:
   - css/university_ems.css
   - js/university_ems.js
   - images/

5. Create templates/ and www/ folders for portals

6. Create api/ folder for REST endpoints

Output the complete directory tree after creation.
```

### Prompt 5: Configure Hooks and Integration

```
You are configuring the hooks.py for University EMS app.

TASK: Create comprehensive hooks.py with all integrations.

Create university_ems/hooks.py with:

1. App metadata:
   - app_name, app_title, app_publisher, etc.
   - required_apps: frappe, erpnext, education, hrms

2. Asset includes:
   - CSS and JS files

3. Role-based home pages:
   - Student → student-portal
   - Guardian → parent-portal
   - Instructor → faculty-portal
   - Alumni → alumni-portal

4. Fixtures configuration for:
   - Custom Fields
   - Property Setters
   - Print Formats
   - Workspaces
   - Dashboards

5. Document Events:
   - Student after_insert, on_update
   - Program Enrollment on_submit
   - Fee Schedule on_submit

6. Scheduler Events:
   - Daily: library reminders, attendance reports
   - Weekly: quality metrics update
   - Monthly: placement statistics
   - Cron jobs for specific times

7. Jinja methods

8. Permission hooks:
   - permission_query_conditions
   - has_permission

9. DocType JS customizations:
   - doctype_js for Student, Program Enrollment, etc.

10. Override doctype class for Student

Ensure all referenced functions have placeholder implementations.
```

### Prompt 6: Custom Fields and Install Script

```
You are creating custom fields for ERPNext integration.

TASK: Create custom fields and installation script.

1. Create custom_fields/ folder with:

   a. student_custom_fields.py:
      - University Information section
      - Admission Number, PRN Number, ABC ID
      - Category (SC/ST/OBC/General/EWS)
      - Physically Challenged, Blood Group
      - Hostel section (hostel_required, current_hostel, hostel_room)
      - Transport section (transport_required, route, pickup_stop)
      - Library section (library_card_number, library_member)
      - Scholarship section
      - Parent extended information

   b. course_custom_fields.py:
      - OBE section with course_outcomes table
      - Credit Information section
      - Course type, credit hours, lecture/tutorial/practical hours
      - Internal/External marks split
      - Prerequisites table

   c. employee_custom_fields.py:
      - Faculty Information section
      - Faculty ID, designation category, specialization
      - PhD guide status and capacity
      - Research section (areas, Google Scholar, ORCID, publications, patents)
      - Workload section

2. Create install.py with:
   - after_install() function that:
     - Calls create_all_custom_fields()
     - Calls setup_roles()
     - Calls setup_workspaces()
     - Calls setup_default_settings()
     - Calls setup_print_formats()

   - setup_roles() creating all custom roles:
     - Hostel Warden
     - Transport Manager
     - Librarian
     - Examination Controller
     - Placement Officer
     - IQAC Coordinator
     - Research Coordinator
     - Alumni Coordinator
     - Department Head
     - Dean

3. Create uninstall.py with cleanup functions

4. Install the app on site:
   ```
   bench --site university.localhost install-app university_ems
   ```

Verify custom fields appear in respective DocTypes.
```

---

## PHASE C: Core Module Development

### Prompt 7: Hostel Management Module

```
You are developing the Hostel Management module.

TASK: Create complete Hostel Management module with all DocTypes.

Create the following DocTypes in hostel_management/doctype/:

1. Hostel:
   - Fields: hostel_name, hostel_code, gender, warden, total_rooms, total_capacity
   - Child tables: amenities
   - Status tracking

2. Hostel Room:
   - Fields: hostel, room_number, floor, room_type, capacity, rent_per_month
   - Auto-calculate available beds
   - Link to Asset module

3. Hostel Room Allocation:
   - Fields: student, hostel, room, bed_number, academic_year, from_date, to_date
   - Workflow: Draft → Submitted → Active → Vacated
   - Validation: Check room availability before allocation

4. Hostel Fee Structure:
   - Fields: academic_year, hostel, room_type, monthly_rent, security_deposit, mess_charges
   - Auto-calculate total annual fee

5. Mess Menu:
   - Fields: hostel, day_of_week, meal_type, menu_items

6. Hostel Visitor:
   - Fields: student, visitor_name, relationship, in_time, out_time, approved_by

7. Hostel Maintenance Request:
   - Fields: hostel, room, issue_type, priority, assigned_to, status
   - Workflow for resolution tracking

8. Hostel Attendance:
   - Fields: hostel, date, students (child table)
   - Child table: student, room, status

For each DocType:
- Create the JSON definition
- Create Python controller with validations
- Create JavaScript form customizations
- Set up permissions

After creating DocTypes:
- Run bench migrate
- Test each DocType creation/validation
- Create sample data
```

### Prompt 8: Transport Management Module

```
You are developing the Transport Management module.

TASK: Create complete Transport Management module with all DocTypes.

Create the following DocTypes in transport_management/doctype/:

1. Transport Route:
   - Fields: route_name, route_code, start_point, end_point, total_distance
   - Child table: stops (Route Stop)
   - Fee calculation

2. Vehicle:
   - Fields: registration_number, vehicle_type, seating_capacity
   - Document validity tracking (insurance, fitness, permit)
   - GPS device ID for tracking
   - Link to Asset module

3. Vehicle Stop:
   - Fields: stop_name, stop_code, latitude, longitude, landmark
   - For Google Maps integration

4. Route Stop (Child Table):
   - Fields: stop, sequence, morning_arrival_time, evening_arrival_time, distance

5. Driver:
   - Fields: driver_name, employee link, license details, contact info
   - License validity tracking
   - Blood group for emergency

6. Student Route Assignment:
   - Fields: student, route, pickup_stop, drop_stop, fee_type
   - Academic year tracking
   - Fee calculation (one-way/two-way)

7. Transport Fee Structure:
   - Fields: academic_year, route, stop, one_way_fee, two_way_fee
   - Distance-based pricing

8. Vehicle Maintenance Log:
   - Fields: vehicle, maintenance_type, date, cost, next_maintenance_due
   - Vendor tracking
   - Odometer reading

9. Vehicle Trip Log:
   - Fields: vehicle, route, driver, date, start_time, end_time
   - Fuel consumption tracking
   - Student count

For each DocType:
- Create complete JSON definitions with all fields
- Create Python controllers with validations
- Create form JavaScript
- Set up permissions for Transport Manager role

Create reports:
- Route-wise Student List
- Vehicle Utilization Report
- Fuel Consumption Report
```

### Prompt 9: Library Management Module

```
You are developing the Library Management module.

TASK: Create complete Library Management module with all DocTypes.

Create the following DocTypes in library_management/doctype/:

1. Library Settings (Single DocType):
   - max_books_per_student, max_books_per_faculty
   - default_issue_days, fine_per_day
   - Allow renewal, max renewals
   - Library timings

2. Library Book:
   - Fields: title, isbn, authors, publisher, publication_year
   - Category, subject, language
   - Total copies, available copies (auto-calculated)
   - Location (rack/shelf), call number
   - Child table: Library Book Copy

3. Library Book Copy:
   - Fields: book, copy_number, barcode, accession_number
   - Condition, acquisition details
   - Current status, current holder

4. Library Category:
   - Hierarchical category structure
   - Parent category support

5. Library Subject:
   - DDC number support
   - Subject code

6. Library Member:
   - Fields: member_type, student/employee link
   - Library card number (auto-generated)
   - Membership validity
   - Books issued count, fine due

7. Library Transaction:
   - Fields: type (Issue/Return/Renew/Lost), member, book_copy
   - Issue date, due date, return date
   - Overdue days calculation
   - Fine amount calculation
   - Workflow: Issue → Active → Returned

8. Library Fine:
   - Fields: member, transaction, fine_type, amount
   - Payment tracking
   - Integration with Accounting

9. Library Reservation:
   - Fields: member, book, reserved_on, valid_till
   - Notification on availability

10. Library Card:
    - Fields: member, card_number, barcode
    - Print format for card generation

11. E-Resource:
    - Fields: title, resource_type, url, access_type
    - Subscription management

Create comprehensive Python controllers for:
- Book issue validation (check limits, fines)
- Fine calculation on return
- Overdue notifications
- Auto-membership on student enrollment

Create reports:
- Books Issued Report
- Overdue Books Report
- Fine Collection Report
- Most Borrowed Books
- Library Usage Statistics

Create Library Dashboard with charts.
```

### Prompt 10: Advanced Examination Module

```
You are developing the Advanced Examination module.

TASK: Create complete Advanced Examination module with all DocTypes.

Create the following DocTypes in advanced_examination/doctype/:

1. Exam Center:
   - Fields: center_name, center_code, center_type (Internal/External)
   - Contact details
   - Child table: Exam Room (room_name, capacity)

2. Examination Schedule:
   - Fields: examination, academic_year, academic_term, exam_type
   - Child table: Exam Schedule Item (course, program, date, time, center, max_marks)
   - Status: Draft → Published → Completed

3. Seating Arrangement:
   - Fields: examination, exam_date, exam_center, room
   - Arrangement type (Random/Roll Number/Subject Wise)
   - Child table: student, seat_number, row, column, course
   - Auto-generation algorithm

4. Hall Ticket:
   - Fields: student, examination, hall_ticket_number (auto)
   - Program, academic_year, exam_center
   - Child table: subjects with date, time, room, seat
   - Photo attachment
   - Print format for hall ticket

5. Invigilator Schedule:
   - Fields: examination, exam_date, session, exam_center, room
   - Chief invigilator, additional invigilators
   - Status tracking

6. External Examiner:
   - Fields: examiner_name, designation, institution, specialization
   - Contact details
   - Bank details for remuneration
   - Status tracking

7. Paper Evaluation Assignment:
   - Fields: examination, course, examiner_type, examiner
   - Papers assigned/evaluated count
   - Remuneration calculation
   - Status tracking

8. Revaluation Request:
   - Fields: student, examination, course, original_marks
   - Reason, fee payment tracking
   - Evaluator assignment
   - Revalued marks, result
   - Workflow: Applied → Under Review → Evaluated → Completed

9. Unfair Means Case (UFM):
   - Fields: student, examination, course, incident_type
   - Description, evidence
   - Committee members
   - Hearing date, student statement
   - Committee decision, punishment
   - Status: Reported → Investigation → Hearing → Decision → Closed

10. Grace Marks:
    - Fields: student, examination, course
    - Original, grace, final marks
    - Reason, approval

11. Answer Booklet:
    - Fields: booklet_number, examination, course
    - Student (hidden for anonymous evaluation)
    - Pages used, additional sheets
    - Evaluator, marks, evaluation date

Create Python controllers for:
- Seating arrangement auto-generation
- Hall ticket number generation
- Fine calculation for UFM
- Grace marks application rules

Create reports:
- Examination Schedule Report
- Result Analysis Report
- Pass Percentage by Subject
- UFM Cases Summary
- Grace Marks Report

Create print formats:
- Hall Ticket
- Seating Chart
- Invigilator Duty Slip
```

### Prompt 11: Training & Placement Module

```
You are developing the Training & Placement module.

TASK: Create complete Training & Placement module with all DocTypes.

Create the following DocTypes in training_placement/doctype/:

1. Company Master:
   - Fields: company_name, company_code, industry, company_type
   - Website, headquarters, about_company, logo
   - HR contact details
   - Hiring history (child table)
   - Status (Active/Blacklisted/Inactive)

2. Skill:
   - Fields: skill_name, skill_category, description
   - Categories: Technical/Soft Skill/Domain/Tool

3. Job Opening:
   - Fields: company, job_title, job_type, job_description
   - Skills required (multi-select)
   - Eligibility criteria:
     - min_cgpa, allowed_backlogs
     - eligible_programs, eligible_branches
     - batch_year
   - Package details: ctc_min, ctc_max, location, bond_period
   - Application deadline, max_applications
   - Applications received (auto-count)
   - Status: Open/Closed/On Hold/Cancelled

4. Placement Drive:
   - Fields: drive_name, company, drive_type
   - Job openings (multi-select)
   - Drive date, venue, coordinator
   - Process rounds (child table)
   - Registered/shortlisted/selected counts
   - Status: Scheduled → In Progress → Completed

5. Drive Round (Child Table):
   - round_name, round_type (PPT/Aptitude/GD/Technical/HR)
   - sequence, date, time, venue, duration
   - Instructions

6. Student Application:
   - Fields: student, job_opening, applied_on
   - Resume, cover_letter
   - Current round
   - Round results (child table)
   - Status: Applied → Shortlisted → In Process → Selected/Rejected

7. Application Round Result (Child Table):
   - round, date, result (Pass/Fail/Pending)
   - score, remarks, evaluated_by

8. Interview Schedule:
   - Fields: placement_drive, student, round
   - Interview date, time, venue
   - Interviewer name
   - Status, result, feedback

9. Placement Offer:
   - Fields: student, company, job_opening, placement_drive
   - Designation, department, job_location
   - CTC offered, joining date
   - Offer letter attachment
   - Offer date, acceptance deadline
   - Status: Offered → Accepted/Rejected/Expired

10. Student Skill:
    - Fields: student, skill, proficiency_level
    - Certification details

11. Pre-Placement Training:
    - Fields: training_name, training_type, trainer
    - Dates, duration, venue
    - Registered students
    - Attendance tracking
    - Status

12. Internship:
    - Fields: student, company, internship_type, role
    - Dates, stipend, location
    - Supervisor details
    - Project title and description
    - Certificate, evaluation
    - PPO offered flag

Create Python controllers for:
- Eligibility checking based on CGPA, backlogs, program
- Application status updates
- Placement statistics calculation

Create Student Portal features:
- View eligible job openings
- Apply for jobs with resume upload
- Track application status
- View interview schedules
- Accept/reject offers

Create reports:
- Placement Statistics Dashboard
- Company-wise Placement Report
- Department-wise Placement Report
- Package Analysis Report
- Unplaced Students Report
```

---

## PHASE D: Quality Modules

### Prompt 12: NAAC Accreditation Module

```
You are developing the NAAC/NBA Accreditation module.

TASK: Create complete Accreditation module with all DocTypes.

Create the following DocTypes in accreditation/doctype/:

1. NAAC Criteria:
   - Fields: criteria_number (1-7), criteria_name
   - Key indicators (child table)
   - Weightage, description

2. NAAC Key Indicator (Child Table):
   - indicator_number, indicator_name
   - metric_type (QnM/QlM)
   - data_source, weightage

3. Quality Metric:
   - Fields: metric_name, criteria, key_indicator
   - Academic year
   - Metric value, unit, target value
   - Achievement percentage (calculated)
   - Supporting documents (child table)
   - Status: Draft → Submitted → Verified → Approved

4. Best Practice:
   - Fields: title, objectives, context
   - Practice description (rich text)
   - Evidence of success
   - Problems encountered, resources required
   - Attachments
   - Status: Draft/Published

5. IQAC Meeting:
   - Fields: meeting_number, meeting_date, venue
   - Chairperson
   - Members present (child table)
   - Agenda items (child table)
   - Minutes (rich text)
   - Action items (child table)
   - Next meeting date
   - Status: Scheduled/Completed/Postponed

6. SSR Data (Self Study Report):
   - Fields: criteria, key_indicator, data_template
   - Academic year
   - Data entries (child table)
   - Verified by, verification date
   - Status: Draft → Submitted → Verified → Approved

7. Accreditation Document:
   - Fields: document_name, document_type
   - Criteria, key_indicator, academic_year
   - File attachment
   - Validity dates
   - Status: Active/Expired/Archived

8. Academic Audit:
   - Fields: audit_type (Internal/External/IQAC)
   - Academic year, department
   - Audit date
   - Auditors (child table)
   - Findings (child table)
   - Compliance score
   - Report attachment
   - Status: Scheduled → In Progress → Completed

9. Stakeholder Feedback:
   - Fields: feedback_type (Student/Alumni/Employer/Parent/Faculty)
   - Academic year, respondent
   - Feedback date
   - Questions (child table)
   - Overall rating
   - Suggestions, action taken

Create auto-population functions:
- Pull student strength from Student master
- Pull faculty data from Employee
- Pull placement data from Placement module
- Pull research data from Research module
- Pull exam results from Examination module

Create reports:
- NAAC Criteria-wise Summary
- Quality Metrics Trend
- Feedback Analysis Report
- IQAC Action Items Status
- DVV Ready Report

Create NAAC Compliance Dashboard.
```

### Prompt 13: OBE System Module

```
You are developing the Outcome-Based Education (OBE) module.

TASK: Create complete OBE System module with all DocTypes.

Create the following DocTypes in obe_system/doctype/:

1. Course Outcome:
   - Fields: course, co_number (CO1, CO2, etc.)
   - Outcome statement (text)
   - Bloom's taxonomy level (Remember/Understand/Apply/Analyze/Evaluate/Create)
   - Keywords
   - Assessment methods (multi-select)

2. Program Outcome:
   - Fields: program, po_number (PO1, PO2, etc.)
   - Outcome statement
   - Outcome type (PO/PSO)
   - Graduate attribute mapping

3. CO-PO Mapping:
   - Fields: course, academic_year
   - Mapping matrix (child table)
   - Justification
   - Approved by
   - Status: Draft/Approved

4. CO PO Mapping Entry (Child Table):
   - course_outcome, program_outcome
   - correlation_level (1-Low/2-Medium/3-High/-)

5. Assessment Method:
   - Fields: method_name, method_type (Direct/Indirect)
   - Description

6. CO Attainment:
   - Fields: course, academic_year, academic_term, student_group
   - CO attainments (child table)
   - Overall attainment (calculated)
   - Target attainment
   - Gap analysis, action plan

7. CO Attainment Detail (Child Table):
   - course_outcome
   - Target percentage
   - Students attempted, students attained
   - Attainment percentage (calculated)
   - Attainment level (1/2/3)

8. PO Attainment:
   - Fields: program, batch, academic_year
   - PO attainments (child table)
   - Calculation method (Direct/Indirect/Combined)
   - Status: Draft/Calculated/Approved

9. OBE Settings (Single DocType):
   - Attainment level thresholds (Level 1: 40%, Level 2: 60%, Level 3: 80%)
   - Direct assessment weightage (default 80%)
   - Indirect assessment weightage (default 20%)
   - Target attainment level (default 2)

Create Python controllers for:
- CO-PO correlation matrix generation
- Attainment calculation from assessment results
- Gap analysis generation
- Action plan suggestions

Create reports:
- CO-PO Mapping Matrix
- Course-wise CO Attainment
- Program-wise PO Attainment
- Batch-wise Attainment Trend
- Gap Analysis Report
- Continuous Improvement Report
```

### Prompt 14: CBCS and Research Modules

```
You are developing the CBCS System and Research Management modules.

TASK 1: Create CBCS System module.

Create the following DocTypes in cbcs_system/doctype/:

1. Credit Structure:
   - Fields: program, academic_year
   - Total credits required
   - Core credits, elective credits, open elective credits
   - Project credits, internship credits
   - Semester-wise credits (child table)

2. Elective Choice:
   - Fields: student, academic_term
   - Elective type (Program Elective/Open Elective)
   - Elective group
   - Selected course, alternate course
   - Status: Selected → Confirmed → Waitlisted → Allocated

3. Credit Transfer:
   - Fields: student, source_institution
   - Source course, source credits
   - Target course, target credits
   - Grade obtained, equivalent grade
   - Transfer date, approved by
   - Status: Applied → Under Review → Approved/Rejected

4. CGPA Calculation:
   - Fields: student, academic_term
   - Courses (child table)
   - SGPA, CGPA (calculated)
   - Total credits earned, credits this semester

5. CGPA Course Entry (Child Table):
   - course, credits, grade, grade_points
   - credit_points (calculated)

---

TASK 2: Create Research Management module.

Create the following DocTypes in research_management/doctype/:

1. Research Project:
   - Fields: project_title, project_type (Sponsored/Consultancy/Internal/Collaborative)
   - Principal investigator, co-investigators
   - Funding agency, sanctioned amount
   - Start date, end date, duration
   - Research area, abstract
   - Deliverables (child table)
   - Expenditure (child table)
   - Progress reports (child table)
   - Status: Applied → Sanctioned → Ongoing → Completed

2. Publication:
   - Fields: title, publication_type (Journal/Conference/Book Chapter/Book/Patent)
   - Authors (child table with sequence)
   - Journal/conference name, publisher
   - Volume, issue, pages, publication date
   - DOI, ISSN/ISBN
   - Indexing (SCI/SCOPUS/Web of Science/UGC Care)
   - Impact factor, citations
   - Abstract, full text attachment

3. Patent:
   - Fields: patent_title, patent_type (Product/Process/Design)
   - Inventors (child table)
   - Application number, application date
   - Patent number, grant date
   - Patent office (Indian/US/European/PCT)
   - Abstract, claims
   - Status: Filed → Published → Granted → Abandoned/Expired

4. Research Guide:
   - Fields: faculty (Employee link)
   - Recognition university, date, number
   - Specialization areas
   - Max scholars allowed
   - Current scholars (calculated), completed scholars
   - Status: Active/Inactive

5. PhD Scholar:
   - Fields: scholar_name, enrollment_number, student link
   - Guide, co-guide
   - Research topic, research area
   - Key dates: enrollment, coursework, comprehensive exam
   - Synopsis submission, thesis submission, viva, degree award
   - Publications (multi-select)
   - Status: Registered → Coursework → Research → Synopsis → Thesis → Awarded/Dropped

Create reports for both modules:
- Credit Summary Report
- Elective Allocation Report
- Research Project Summary
- Publication Statistics
- Faculty Research Profile
- PhD Progress Report
```

---

## PHASE E: Supporting Modules

### Prompt 15: Alumni Management Module

```
You are developing the Alumni Management module.

TASK: Create complete Alumni Management module with all DocTypes.

Create the following DocTypes in alumni_management/doctype/:

1. Alumni:
   - Fields: student (link), alumni_id (auto)
   - Full name, email, phone
   - Graduation year, program, department
   - Current employer, designation, industry, location
   - LinkedIn URL
   - Career history (child table)
   - Achievements (child table)
   - Willing to mentor flag
   - Membership type (Regular/Premium/Lifetime)
   - Membership validity
   - Photo
   - Status: Active/Inactive

2. Career Entry (Child Table):
   - Company, designation, from_date, to_date
   - Location, description

3. Achievement (Child Table):
   - Title, year, description

4. Alumni Event:
   - Fields: event_name, event_type (Reunion/Seminar/Workshop/Networking)
   - Event date, time, venue
   - Description (rich text)
   - Registration deadline, max participants
   - Registration fee
   - Organizers
   - Registrations (child table)
   - Status: Planning → Open → Closed → Completed

5. Event Registration (Child Table):
   - Alumni, registration_date
   - Payment status
   - Attendance marked

6. Alumni Donation:
   - Fields: alumni, donation_type
   - Amount, donation_date
   - Payment mode, transaction_id
   - Purpose
   - Receipt number
   - Tax exemption certificate
   - Status: Pledged → Received → Acknowledged

7. Alumni Chapter:
   - Fields: chapter_name, location
   - Chapter head (Alumni link)
   - Committee members (child table)
   - Establishment date
   - Member count (calculated)
   - Activities (child table)
   - Status: Active/Inactive

Create Python functions for:
- Auto-create Alumni from graduated Student
- Alumni search/directory
- Event notification
- Donation receipt generation

Create Alumni Portal features:
- Update profile
- View and register for events
- Make donations
- Search alumni directory
- Job posting for fellow alumni

Create reports:
- Alumni by Batch Report
- Alumni by Location Report
- Donation Summary Report
- Event Participation Report
```

### Prompt 16: Grievance and Sports Modules

```
You are developing the Grievance Management and Sports & Cultural modules.

TASK 1: Create Grievance Management module.

Create the following DocTypes in grievance_management/doctype/:

1. Grievance Category:
   - Fields: category_name, parent_category
   - Description
   - Default assignee
   - SLA days

2. Grievance:
   - Fields: grievance_id (auto)
   - Complainant type (Student/Faculty/Staff/Parent)
   - Complainant (Dynamic Link)
   - Anonymous flag
   - Category, subject, description
   - Attachments (child table)
   - Priority (Low/Medium/High/Critical)
   - Assigned to, escalated to
   - Resolution, resolution date
   - Satisfaction rating (1-5)
   - Feedback
   - Status: Open → Assigned → In Progress → Resolved → Closed

   Create workflow with:
   - Auto-assignment based on category
   - SLA tracking
   - Auto-escalation on SLA breach
   - Email notifications

3. Grievance Resolution:
   - Fields: grievance, action_taken
   - Resolution datetime, resolved by
   - Attachments

Create reports:
- Grievance Summary Report
- Category-wise Analysis
- SLA Compliance Report
- Resolution Time Analysis

---

TASK 2: Create Sports & Cultural module.

Create the following DocTypes in sports_cultural/doctype/:

1. Sport:
   - Fields: sport_name, sport_type (Indoor/Outdoor/Water)
   - Team size, description

2. Sports Event:
   - Fields: event_name, sport
   - Event type (Intra/Inter-college/University/State/National)
   - Event level (Individual/Team)
   - Start date, end date, venue, organizer
   - Registration deadline
   - Eligibility criteria
   - Participants (child table)
   - Results (child table)
   - Status: Upcoming/Ongoing/Completed

3. Cultural Event:
   - Fields: event_name, event_type (Music/Dance/Drama/Art/Literary/Quiz/Debate)
   - Event category (Solo/Group/Team)
   - Event date, venue, organizer
   - Participants (child table)
   - Judges (child table)
   - Results (child table)

4. Event Participant (Child Table):
   - Student, registration_date
   - Team name (if team event)
   - Status: Registered/Confirmed/Participated/Withdrawn

5. Event Result (Child Table):
   - Position (1st/2nd/3rd/Participant)
   - Student/Team
   - Score/marks
   - Certificate generated flag

6. Facility:
   - Fields: facility_name, facility_type (Ground/Hall/Room/Court)
   - Location, capacity
   - Available timings
   - Booking required flag
   - Charges

7. Facility Booking:
   - Fields: facility, requested_by
   - Booking date, start_time, end_time
   - Purpose, expected participants
   - Approved by
   - Status: Requested → Approved → Rejected → Completed

Create reports:
- Event Calendar
- Student Participation Report
- Facility Utilization Report
- Achievement Summary
```

---

## PHASE F: Integration & Portal

### Prompt 17: Student Portal Development

```
You are developing the Student Portal web interface.

TASK: Create comprehensive Student Portal.

1. Create www/student_portal/ with pages:

   a. Dashboard (index.html):
      - Welcome message with student name and photo
      - Quick stats: Attendance %, CGPA, Books issued, Fees due
      - Upcoming events calendar
      - Recent notifications
      - Quick links to all sections

   b. Academic (academic.html):
      - Current enrollment details
      - Semester-wise courses
      - Timetable view
      - Attendance summary
      - Exam schedule
      - Results/grades

   c. Fee (fee.html):
      - Fee summary (paid/pending)
      - Payment history
      - Online payment integration
      - Download receipts
      - Hostel/Transport fee details

   d. Library (library.html):
      - Library card details
      - Currently issued books
      - Issue/return history
      - Fine details
      - Book search (OPAC)
      - Reserve book

   e. Hostel (hostel.html):
      - Room allocation details
      - Mess menu
      - Maintenance request form
      - Visitor log
      - Hostel attendance

   f. Transport (transport.html):
      - Route details
      - Bus timings
      - Pickup stop information
      - Transport fee details

   g. Placement (placement.html):
      - Eligible job openings
      - Apply for jobs
      - Application status
      - Interview schedules
      - Placement offers
      - Resume upload/update

   h. Profile (profile.html):
      - Personal information
      - Contact details update
      - Password change
      - Document downloads (ID card, bonafide)

2. Create portal controller:
   student_portal.py with API endpoints for all data

3. Create CSS styling:
   - Responsive design
   - University branding
   - Mobile-friendly

4. Create JavaScript:
   - Dynamic data loading
   - Form validations
   - AJAX calls

5. Set up permissions:
   - Student role access only
   - Data visibility based on logged-in student
```

### Prompt 18: Faculty and Parent Portals

```
You are developing Faculty and Parent Portal interfaces.

TASK 1: Create Faculty Portal.

Create www/faculty_portal/ with pages:

1. Dashboard:
   - Welcome message, photo
   - Today's classes
   - Pending tasks (attendance, marks entry)
   - Research summary
   - Notifications

2. Academic:
   - Assigned courses
   - Student lists
   - Timetable
   - Attendance entry
   - Marks/grades entry

3. Students:
   - Class-wise student list
   - Student profiles
   - Performance tracking
   - Attendance defaulters

4. Examination:
   - Invigilation duties
   - Paper evaluation assignments
   - Result entry
   - Revaluation requests

5. Research:
   - Research projects
   - Publications
   - PhD scholars
   - Grants/funding

6. Leave:
   - Apply leave
   - Leave balance
   - Leave history

7. Profile:
   - Personal information
   - Qualifications
   - Publications list
   - Update research profile

---

TASK 2: Create Parent Portal.

Create www/parent_portal/ with pages:

1. Dashboard:
   - Ward's summary
   - Attendance overview
   - Recent grades
   - Fee status
   - Notifications

2. Academic:
   - Course details
   - Timetable
   - Attendance report
   - Exam schedule
   - Results/grades

3. Fee:
   - Fee summary
   - Payment history
   - Make payment
   - Download receipts

4. Communication:
   - Messages from teachers
   - Announcements
   - Contact faculty/admin

5. Reports:
   - Progress report
   - Attendance certificate
   - Fee receipts

Create proper authentication for each portal with role-based access.
```

### Prompt 19: API Layer and Dashboards

```
You are developing the API layer and analytics dashboards.

TASK 1: Create comprehensive API endpoints.

Create university_ems/api/ with:

1. student_api.py:
   - get_student_complete_profile(student_id)
   - get_student_attendance_summary(student_id, from_date, to_date)
   - get_student_fee_summary(student_id)
   - get_student_library_status(student_id)
   - get_student_placement_status(student_id)
   - bulk_allocate_hostel(students, hostel, academic_year)
   - bulk_assign_transport(students, route)

2. hostel_api.py:
   - get_hostel_occupancy(hostel)
   - get_available_rooms(hostel, gender)
   - allocate_room(student, hostel, room)
   - vacate_room(allocation)
   - get_mess_menu(hostel)

3. library_api.py:
   - search_books(query, filters)
   - issue_book(member, book_copy)
   - return_book(transaction)
   - renew_book(transaction)
   - get_member_transactions(member)
   - calculate_fine(transaction)

4. placement_api.py:
   - get_eligible_openings(student)
   - apply_for_job(student, job_opening)
   - get_application_status(application)
   - get_placement_statistics(academic_year)

5. examination_api.py:
   - generate_hall_tickets(examination, students)
   - generate_seating_arrangement(examination, center, room)
   - enter_marks(examination, course, marks_list)
   - calculate_results(examination)

---

TASK 2: Create Analytics Dashboards.

Create dashboards with charts for:

1. Academic Dashboard:
   - Student enrollment trends
   - Department-wise distribution
   - Pass percentage trends
   - Attendance analytics

2. Financial Dashboard:
   - Fee collection summary
   - Outstanding fees
   - Revenue by fee type
   - Month-wise collection

3. Placement Dashboard:
   - Placement percentage
   - Company-wise offers
   - Package distribution
   - Year-on-year comparison

4. Library Dashboard:
   - Books circulation
   - Category-wise usage
   - Overdue trends
   - Fine collection

5. Research Dashboard:
   - Publications by year
   - Funding received
   - PhD students progress
   - Patent status

Create Number Cards for key metrics on each dashboard.
```

---

## PHASE G: Testing & Deployment

### Prompt 20: Testing Suite

```
You are creating the testing suite for University EMS.

TASK: Create comprehensive test cases.

1. Create tests/ folder structure:
   tests/
   ├── test_hostel.py
   ├── test_transport.py
   ├── test_library.py
   ├── test_examination.py
   ├── test_placement.py
   ├── test_accreditation.py
   ├── test_obe.py
   ├── test_api.py
   └── test_integration.py

2. For each module, create tests for:

   a. DocType validation tests:
      - Required field validation
      - Unique constraint validation
      - Data type validation
      - Link validation

   b. Business logic tests:
      - Hostel: Room allocation, capacity check
      - Library: Issue limits, fine calculation
      - Examination: Seating generation, hall ticket
      - Placement: Eligibility checking

   c. Workflow tests:
      - State transitions
      - Permission checks
      - Trigger execution

3. Create API tests:
   - Authentication tests
   - Endpoint response tests
   - Error handling tests

4. Create integration tests:
   - Student enrollment → Library membership → Hostel allocation
   - Fee schedule → Payment → Receipt
   - Exam → Result → Transcript

5. Create test data fixtures:
   - Sample students
   - Sample courses
   - Sample faculty
   - Sample hostel/library data

6. Create test runner script:
   ```bash
   bench --site university.localhost run-tests --app university_ems
   ```

7. Generate test coverage report
```

### Prompt 21: Deployment Configuration

```
You are creating deployment configuration for production.

TASK: Create production deployment setup.

1. Create production docker-compose.prod.yml:
   - Production-optimized configurations
   - SSL/TLS with Let's Encrypt
   - Production Nginx configuration
   - Resource limits
   - Log rotation
   - Health checks

2. Create Nginx production configuration:
   - SSL termination
   - Proxy settings
   - Static file caching
   - Gzip compression
   - Rate limiting
   - Security headers

3. Create backup scripts:
   - Database backup (daily)
   - Files backup (weekly)
   - Backup rotation (keep 30 days)
   - Off-site backup sync
   - Restore procedure documentation

4. Create monitoring setup:
   - Application health endpoint
   - Database monitoring
   - Redis monitoring
   - Disk space alerts
   - Error log monitoring

5. Create CI/CD pipeline (.github/workflows/):
   - Code linting
   - Run tests
   - Build Docker images
   - Deploy to staging
   - Deploy to production

6. Create environment-specific configurations:
   - Development (.env.development)
   - Staging (.env.staging)
   - Production (.env.production)

7. Create documentation:
   - Deployment guide
   - Rollback procedure
   - Scaling guide
   - Troubleshooting guide

8. Create security checklist:
   - Firewall rules
   - SSL certificate renewal
   - Security updates
   - Access audit
   - Password policies
```

---

## Master Execution Prompt

Use this comprehensive prompt to start the entire implementation:

```
I am implementing a comprehensive University ERP system using Frappe/ERPNext framework.

PROJECT CONTEXT:
- Building a custom app called "university_ems" on top of ERPNext v15
- Need to integrate with existing ERPNext modules: Education, HRMS, Accounting, Assets
- Custom modules needed: Hostel, Transport, Library, Advanced Examination, Training & Placement, NAAC Accreditation, OBE, CBCS, Research, Alumni, Grievance, Sports & Cultural

CURRENT PHASE: [Specify current phase - e.g., "Phase A: Environment Setup"]

DOCUMENTS AVAILABLE:
1. Document 01: Frappe Docker & DevContainer Setup Guide
2. Document 02: App Architecture & Module Integration Guide  
3. Document 03: Module-wise Implementation Checklist
4. Document 04: Claude Code Execution Prompts (this document)

Please help me with [SPECIFIC TASK FROM THE RELEVANT PROMPT ABOVE].

Requirements:
1. Follow Frappe framework best practices
2. Create production-quality code with proper validations
3. Include comprehensive error handling
4. Add appropriate permissions
5. Create reusable components
6. Document all functions

Start with [SPECIFIC STARTING POINT] and provide complete implementation.
```

---

## Quick Reference: Execution Order

| Step | Prompt # | Description | Duration |
|------|----------|-------------|----------|
| 1 | Prompt 1 | Docker Environment Setup | 2-3 hours |
| 2 | Prompt 2 | DevContainer Setup | 1-2 hours |
| 3 | Prompt 3 | ERPNext Base Configuration | 3-4 hours |
| 4 | Prompt 4 | Create University EMS App | 2-3 hours |
| 5 | Prompt 5 | Configure Hooks | 2-3 hours |
| 6 | Prompt 6 | Custom Fields & Install | 3-4 hours |
| 7 | Prompt 7 | Hostel Management | 2-3 days |
| 8 | Prompt 8 | Transport Management | 2-3 days |
| 9 | Prompt 9 | Library Management | 3-4 days |
| 10 | Prompt 10 | Advanced Examination | 3-4 days |
| 11 | Prompt 11 | Training & Placement | 3-4 days |
| 12 | Prompt 12 | NAAC Accreditation | 3-4 days |
| 13 | Prompt 13 | OBE System | 2-3 days |
| 14 | Prompt 14 | CBCS & Research | 3-4 days |
| 15 | Prompt 15 | Alumni Management | 2-3 days |
| 16 | Prompt 16 | Grievance & Sports | 2-3 days |
| 17 | Prompt 17 | Student Portal | 3-4 days |
| 18 | Prompt 18 | Faculty & Parent Portals | 3-4 days |
| 19 | Prompt 19 | API & Dashboards | 2-3 days |
| 20 | Prompt 20 | Testing Suite | 3-4 days |
| 21 | Prompt 21 | Deployment Configuration | 2-3 days |

**Total Estimated Development Time: 10-12 weeks**

---

**Document End**

# University ERP - System Overview

## Architecture Overview

The University ERP is built on a **hybrid architecture** that leverages multiple Frappe apps working together to provide comprehensive university management functionality.

```
+------------------------------------------------------------------+
|                    UNIVERSITY ERP APPLICATION                     |
|      (17 Custom Modules, 155 DocTypes, Custom Extensions)        |
+------------------------------------------------------------------+
           |                    |                    |
           v                    v                    v
+------------------+  +------------------+  +------------------+
|    EDUCATION     |  |      HRMS        |  |     ERPNEXT      |
|   (73 DocTypes)  |  |  (150 DocTypes)  |  |  (550+ DocTypes) |
|                  |  |                  |  |                  |
| - Student        |  | - Employee       |  | - Accounts       |
| - Program        |  | - Payroll        |  | - GL Engine      |
| - Course         |  | - Leave          |  | - Workflow       |
| - Fees           |  | - Attendance     |  | - Reports        |
+------------------+  +------------------+  +------------------+
           |                    |                    |
           +--------------------+--------------------+
                               |
                               v
+------------------------------------------------------------------+
|                      FRAPPE FRAMEWORK                             |
|        (Core DocTypes, Permissions, UI, API, Workflow)           |
+------------------------------------------------------------------+
```

## Installed Apps

| App | Version | Purpose | DocTypes |
|-----|---------|---------|----------|
| **Frappe** | v15+ | Core framework | ~100 |
| **ERPNext** | v15+ | Business modules (Accounts, hidden modules) | 550+ |
| **HRMS** | v15+ | HR & Payroll management | 150 |
| **Education** | v15+ | Academic management foundation | 73 |
| **University ERP** | v0.0.1 | Custom university modules | 155 |

## Module Structure

The University ERP app contains **17 modules** with **155 custom DocTypes**:

```
university_erp/
+-- Academics              (8 DocTypes)   - Course registration, timetable, CBCS
+-- Admissions             (6 DocTypes)   - Admission cycles, merit lists, seats
+-- Student Info           (3 DocTypes)   - Status logs, alumni, announcements
+-- Examinations           (6 DocTypes)   - Hall tickets, transcripts, schedules
+-- University Finance     (8 DocTypes)   - Fee management, scholarships
+-- University HR          (14 DocTypes)  - Faculty profiles, workload, feedback
+-- University Hostel      (14 DocTypes)  - Buildings, rooms, mess, attendance
+-- University Transport   (5 DocTypes)   - Routes, vehicles, allocations
+-- University Library     (7 DocTypes)   - Books, members, transactions
+-- University Placement   (11 DocTypes)  - Companies, drives, applications
+-- University LMS         (15 DocTypes)  - Courses, content, quizzes
+-- University Research    (7 DocTypes)   - Publications, projects, grants
+-- University OBE         (18 DocTypes)  - Outcomes, attainments, surveys
+-- University Integrations(13 DocTypes)  - Biometric, SMS, DigiLocker
+-- University Portals     (8 DocTypes)   - Alumni, announcements, jobs
+-- University Payments    (8 DocTypes)   - Payment gateways, GL integration
+-- University ERP (Core)  (6 DocTypes)   - Settings, notifications
```

## App Dependencies & Override Architecture

### Required Apps
```python
required_apps = ["frappe", "erpnext", "hrms", "education"]
```

### DocType Override Classes
The University ERP extends Education app DocTypes with custom logic:

```python
override_doctype_class = {
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Assessment Result": "university_erp.overrides.assessment_result.UniversityAssessmentResult",
    "Fees": "university_erp.overrides.fees.UniversityFees",
    "Student Applicant": "university_erp.overrides.student_applicant.UniversityApplicant",
}
```

### Blocked ERPNext Modules
These business modules are hidden from the UI (not relevant to universities):
- Manufacturing, Stock, Selling, Buying, CRM, Projects, Assets, Quality, Support

## System Integration Diagram

```
                           +-------------------------+
                           |     STUDENT PORTAL      |
                           |   (Web/Mobile/PWA)      |
                           +-------------------------+
                                      |
                                      v
+------------------------------------------------------------------+
|                        UNIVERSITY ERP                             |
+------------------------------------------------------------------+
|                                                                   |
|  +----------+  +-----------+  +------------+  +-----------+      |
|  |ACADEMICS |  | ADMISSIONS|  |EXAMINATIONS|  | FINANCE   |      |
|  +----------+  +-----------+  +------------+  +-----------+      |
|       |              |              |               |             |
|       v              v              v               v             |
|  +------------------+     +-------------------+                   |
|  |    EDUCATION     |     |      ERPNEXT     |                   |
|  |   - Student      |     |   - GL Entries   |                   |
|  |   - Program      |     |   - Accounts     |                   |
|  |   - Course       |     |   - Workflows    |                   |
|  |   - Fees         |     +-------------------+                   |
|  +------------------+              |                              |
|                                    v                              |
|  +----------+  +-----------+  +------------+  +-----------+      |
|  |   HR     |  |  HOSTEL   |  |  LIBRARY   |  | PLACEMENT |      |
|  +----------+  +-----------+  +------------+  +-----------+      |
|       |                                                          |
|       v                                                          |
|  +------------------+                                            |
|  |      HRMS        |                                            |
|  |   - Employee     |                                            |
|  |   - Payroll      |                                            |
|  |   - Leave        |                                            |
|  +------------------+                                            |
|                                                                   |
+------------------------------------------------------------------+
                                      |
                                      v
+------------------------------------------------------------------+
|                     EXTERNAL INTEGRATIONS                         |
+------------------------------------------------------------------+
|  +----------+  +-----------+  +------------+  +-----------+      |
|  | RAZORPAY |  |   PAYU    |  | DIGILOCKER |  | BIOMETRIC |      |
|  +----------+  +-----------+  +------------+  +-----------+      |
|  +----------+  +-----------+                                     |
|  |   SMS    |  |  EMAIL    |                                     |
|  +----------+  +-----------+                                     |
+------------------------------------------------------------------+
```

## Data Flow Architecture

### Student Lifecycle Flow
```
+---------------+     +---------------+     +---------------+
|   ADMISSION   | --> |   ACADEMICS   | --> | EXAMINATIONS  |
| - Application |     | - Enrollment  |     | - Hall Ticket |
| - Merit List  |     | - Course Reg  |     | - Results     |
| - Seat Matrix |     | - Attendance  |     | - Transcript  |
+---------------+     +---------------+     +---------------+
       |                     |                      |
       v                     v                      v
+---------------+     +---------------+     +---------------+
|    STUDENT    | --> |    FINANCE    | --> |   ALUMNI      |
| - Record      |     | - Fees        |     | - Profile     |
| - Status      |     | - Scholarships|     | - Events      |
+---------------+     +---------------+     +---------------+
```

### Financial Integration Flow
```
+---------------+     +---------------+     +---------------+
|     FEES      | --> |   PAYMENT     | --> |   ERPNEXT     |
| (Education)   |     |   GATEWAY     |     |   ACCOUNTS    |
|               |     | - Razorpay    |     | - GL Entries  |
|               |     | - PayU        |     | - Journal     |
+---------------+     +---------------+     +---------------+
```

### HR Integration Flow
```
+---------------+     +---------------+     +---------------+
|   FACULTY     | --> |   EMPLOYEE    | --> |    PAYROLL    |
|   PROFILE     |     |   (HRMS)      |     |    (HRMS)     |
| (Univ. ERP)   |     |               |     |               |
+---------------+     +---------------+     +---------------+
       |
       v
+---------------+     +---------------+
|   TEACHING    | --> |   WORKLOAD    |
|  ASSIGNMENT   |     |  CALCULATION  |
+---------------+     +---------------+
```

## Module Interconnections

### Central Entity: Student

```
                              +----------------+
                              |    STUDENT     |
                              | (Education App)|
                              +----------------+
                                     |
        +----------------------------+----------------------------+
        |              |             |             |              |
        v              v             v             v              v
+------------+  +-----------+  +-----------+  +-----------+  +-----------+
| COURSE     |  | HOSTEL    |  | LIBRARY   |  | FEES      |  | PLACEMENT |
| REGISTR.   |  | ALLOC.    |  | MEMBER    |  | & SCHOL.  |  | APPLIC.   |
+------------+  +-----------+  +-----------+  +-----------+  +-----------+
        |              |             |             |              |
        v              v             v             v              v
+------------+  +-----------+  +-----------+  +-----------+  +-----------+
| HALL       |  | HOSTEL    |  | LIBRARY   |  | PAYMENT   |  | JOB       |
| TICKET     |  | ATTEND.   |  | TRANS.    |  | RECORD    |  | OFFERS    |
+------------+  +-----------+  +-----------+  +-----------+  +-----------+
        |
        v
+------------+
| TRANSCRIPT |
+------------+
```

### Module Cross-References

| Module | Links To | Purpose |
|--------|----------|---------|
| Academics | Education (Student, Course, Program) | Course registration, timetable |
| Admissions | Education (Student Applicant) | Application to enrollment |
| Examinations | Education (Assessment Result) | Grade processing |
| Finance | ERPNext (Accounts, GL) | Financial posting |
| HR | HRMS (Employee, Payroll) | Faculty management |
| LMS | Academics (Course) | Online learning |
| OBE | Academics (Course) | Outcome mapping |
| Placement | Student | Career services |

## Document Events & Hooks

### Doc Events Configured
```python
doc_events = {
    "Student": {
        "validate": "university_erp.overrides.student.validate_student",
        "on_update": "university_erp.overrides.student.on_student_update",
    },
    "Fees": {
        "on_submit": [
            "university_erp.integrations.gl_integration.create_fee_gl_entry",
            "university_erp.university_payments.gl_posting.on_fees_submit",
        ],
        "on_cancel": "university_erp.university_payments.gl_posting.on_fees_cancel",
    },
    "Leave Application": {
        "on_submit": "university_erp.university_hr.leave_events.on_submit",
        "on_cancel": "university_erp.university_hr.leave_events.on_cancel",
    },
    "Employee": {
        "on_update": "university_erp.university_hr.employee_events.on_update",
    },
    "Department": {
        "on_update": "university_erp.university_hr.department_events.on_update",
    },
}
```

### Scheduled Tasks
```python
scheduler_events = {
    "daily": [
        "send_fee_reminders",
        "send_overdue_notices",
        "send_library_overdue_notices",
        "expire_library_reservations",
        "update_student_cgpa",
        "check_attendance_thresholds",
    ],
    "weekly": [
        "send_attendance_warnings",
        "send_placement_updates",
        "cleanup_old_notifications",
    ],
    "monthly": [
        "generate_monthly_reports",
        "update_placement_statistics",
    ],
}
```

## Portal Architecture

### Website Routes
```python
website_route_rules = [
    {"from_route": "/student-portal/<path:app_path>", "to_route": "student-portal"},
    {"from_route": "/faculty-portal/<path:app_path>", "to_route": "faculty-portal"},
    {"from_route": "/student-feedback/<path:app_path>", "to_route": "student-feedback"},
    {"from_route": "/library/<path:app_path>", "to_route": "library"},
    {"from_route": "/placement/<path:app_path>", "to_route": "placement"},
]
```

### Role-Based Access
| Role | Primary Access |
|------|---------------|
| University Admin | All modules |
| University Registrar | Admissions, Student Records |
| University Finance | Fees, Scholarships, Reports |
| University HR Admin | Faculty, Staff, Payroll |
| University HOD | Department resources |
| University Exam Cell | Examinations, Results |
| University Faculty | Own classes, Attendance, Grades |
| University Student | Portal access only |

## Statistics Summary

| Metric | Count |
|--------|-------|
| Total Apps | 5 |
| University ERP Modules | 17 |
| University ERP DocTypes | 155 |
| Education DocTypes | 73 |
| HRMS DocTypes | 150 |
| ERPNext DocTypes | 550+ |
| DocType Overrides | 6 |
| Scheduled Tasks | 11 |
| Portal Routes | 5 |
| Payment Gateways | 2 |

## Quick Links to Module Documentation

1. [Academics Module](01_ACADEMICS.md)
2. [Admissions Module](02_ADMISSIONS.md)
3. [Student Info Module](03_STUDENT_INFO.md)
4. [Examinations Module](04_EXAMINATIONS.md)
5. [University Finance Module](05_UNIVERSITY_FINANCE.md)
6. [University HR Module](06_UNIVERSITY_HR.md)
7. [University Hostel Module](07_UNIVERSITY_HOSTEL.md)
8. [University Transport Module](08_UNIVERSITY_TRANSPORT.md)
9. [University Library Module](09_UNIVERSITY_LIBRARY.md)
10. [University Placement Module](10_UNIVERSITY_PLACEMENT.md)
11. [University LMS Module](11_UNIVERSITY_LMS.md)
12. [University Research Module](12_UNIVERSITY_RESEARCH.md)
13. [University OBE Module](13_UNIVERSITY_OBE.md)
14. [University Integrations Module](14_UNIVERSITY_INTEGRATIONS.md)
15. [University Portals Module](15_UNIVERSITY_PORTALS.md)
16. [University Payments Module](16_UNIVERSITY_PAYMENTS.md)
17. [University ERP Core Module](17_UNIVERSITY_ERP_CORE.md)

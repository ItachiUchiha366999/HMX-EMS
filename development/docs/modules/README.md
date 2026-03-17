# University ERP - Module Documentation

## Quick Navigation

This directory contains comprehensive documentation for all 17 modules implemented in the University ERP system.

## System Architecture

```
+------------------------------------------------------------------+
|                         UNIVERSITY ERP                            |
|                    (17 Modules, 155 DocTypes)                     |
+------------------------------------------------------------------+
|                              |                                    |
|   +-------------------------+-------------------------+           |
|   |                         |                         |           |
|   v                         v                         v           |
| +--------+            +----------+              +---------+       |
| |EDUCATION|           |   HRMS   |              | ERPNEXT |       |
| | (Base)  |           | (HR/Pay) |              |(Accounts)|      |
| +--------+            +----------+              +---------+       |
|   |                         |                         |           |
|   +-------------------------+-------------------------+           |
|                              |                                    |
|                              v                                    |
|                    +------------------+                           |
|                    | FRAPPE FRAMEWORK |                           |
|                    +------------------+                           |
+------------------------------------------------------------------+
```

## Module Index

### Core Academic Modules

| # | Module | DocTypes | Description | Documentation |
|---|--------|----------|-------------|---------------|
| 0 | **System Overview** | - | Architecture, dependencies, integration | [00_SYSTEM_OVERVIEW.md](00_SYSTEM_OVERVIEW.md) |
| 1 | **Academics** | 8 | Course registration, timetable, CBCS | [01_ACADEMICS.md](01_ACADEMICS.md) |
| 2 | **Admissions** | 6 | Admission cycles, merit lists, seats | [02_ADMISSIONS.md](02_ADMISSIONS.md) |
| 3 | **Student Info** | 3 | Status tracking, alumni, announcements | [03_STUDENT_INFO.md](03_STUDENT_INFO.md) |
| 4 | **Examinations** | 6 | Hall tickets, transcripts, schedules | [04_EXAMINATIONS.md](04_EXAMINATIONS.md) |

### Finance & Administration

| # | Module | DocTypes | Description | Documentation |
|---|--------|----------|-------------|---------------|
| 5 | **University Finance** | 8 | Fee management, scholarships, refunds | [05_UNIVERSITY_FINANCE.md](05_UNIVERSITY_FINANCE.md) |
| 6 | **University HR** | 14 | Faculty profiles, workload, appraisal | [06_UNIVERSITY_HR.md](06_UNIVERSITY_HR.md) |

### Campus Services

| # | Module | DocTypes | Description | Documentation |
|---|--------|----------|-------------|---------------|
| 7 | **University Hostel** | 14 | Buildings, rooms, mess, attendance | [07_UNIVERSITY_HOSTEL.md](07_UNIVERSITY_HOSTEL.md) |
| 8 | **University Transport** | 5 | Routes, vehicles, allocations | [08_UNIVERSITY_TRANSPORT.md](08_UNIVERSITY_TRANSPORT.md) |
| 9 | **University Library** | 7 | Books, members, transactions, fines | [09_UNIVERSITY_LIBRARY.md](09_UNIVERSITY_LIBRARY.md) |

### Career & Development

| # | Module | DocTypes | Description | Documentation |
|---|--------|----------|-------------|---------------|
| 10 | **University Placement** | 11 | Companies, drives, applications | [10_UNIVERSITY_PLACEMENT.md](10_UNIVERSITY_PLACEMENT.md) |
| 11 | **University LMS** | 15 | Online courses, quizzes, assignments | [11_UNIVERSITY_LMS.md](11_UNIVERSITY_LMS.md) |
| 12 | **University Research** | 7 | Publications, projects, grants | [12_UNIVERSITY_RESEARCH.md](12_UNIVERSITY_RESEARCH.md) |

### Quality & Accreditation

| # | Module | DocTypes | Description | Documentation |
|---|--------|----------|-------------|---------------|
| 13 | **University OBE** | 18 | Outcomes, attainments, surveys | [13_UNIVERSITY_OBE.md](13_UNIVERSITY_OBE.md) |

### Technical Infrastructure

| # | Module | DocTypes | Description | Documentation |
|---|--------|----------|-------------|---------------|
| 14 | **University Integrations** | 13 | Payment gateways, SMS, DigiLocker | [14_UNIVERSITY_INTEGRATIONS.md](14_UNIVERSITY_INTEGRATIONS.md) |
| 15 | **University Portals** | 8 | Student/Alumni portals, announcements | [15_UNIVERSITY_PORTALS.md](15_UNIVERSITY_PORTALS.md) |
| 16 | **University Payments** | 8 | GL posting, Razorpay, PayU | [16_UNIVERSITY_PAYMENTS.md](16_UNIVERSITY_PAYMENTS.md) |

## Module Relationships Diagram

```
                            +------------------+
                            |    ADMISSIONS    |
                            +------------------+
                                    |
                                    v
+-------------+            +------------------+            +-------------+
|   FINANCE   |<-----------|     STUDENT      |----------->|   HOSTEL    |
|  (Fees)     |            |  (Central Hub)   |            |             |
+-------------+            +------------------+            +-------------+
      |                            |                              |
      v                            v                              v
+-------------+            +------------------+            +-------------+
|  PAYMENTS   |            |    ACADEMICS     |            |  TRANSPORT  |
| (Razorpay)  |            | (Registration)   |            |             |
+-------------+            +------------------+            +-------------+
                                   |
                  +----------------+----------------+
                  |                |                |
                  v                v                v
          +-------------+  +-------------+  +-------------+
          |    EXAMS    |  |     LMS     |  |     OBE     |
          |(Hall Ticket)|  | (E-Learning)|  |(Outcomes)   |
          +-------------+  +-------------+  +-------------+
                                   |
                                   v
                          +------------------+
                          |    PLACEMENT     |
                          +------------------+
                                   |
                                   v
                          +------------------+
                          |     ALUMNI       |
                          |   (Portals)      |
                          +------------------+
```

## App Dependencies

```
university_erp
    |
    +-- education (Student, Course, Fees, Assessment)
    |       |
    |       +-- erpnext (Accounts, GL Engine)
    |
    +-- hrms (Employee, Payroll, Leave)
    |       |
    |       +-- erpnext
    |
    +-- frappe (Framework, Core DocTypes)
```

## DocType Override Classes

| Education DocType | Override Class |
|-------------------|----------------|
| Student | `university_erp.overrides.student.UniversityStudent` |
| Program | `university_erp.overrides.program.UniversityProgram` |
| Course | `university_erp.overrides.course.UniversityCourse` |
| Assessment Result | `university_erp.overrides.assessment_result.UniversityAssessmentResult` |
| Fees | `university_erp.overrides.fees.UniversityFees` |
| Student Applicant | `university_erp.overrides.student_applicant.UniversityApplicant` |

## Total Statistics

| Metric | Count |
|--------|-------|
| University ERP Modules | 17 |
| University ERP DocTypes | 155 |
| Education App DocTypes | 73 |
| HRMS DocTypes | 150 |
| ERPNext DocTypes Used | ~50 (Accounts subset) |
| DocType Overrides | 6 |
| Doc Event Hooks | 8 |
| Scheduled Tasks | 11 |
| Portal Routes | 5 |
| Payment Gateways | 2 |

## Cross-Module Integration Points

### Data Flow Summary

| From Module | To Module | Data Flow |
|-------------|-----------|-----------|
| Admissions | Student Info | Approved applicant → Student |
| Academics | Examinations | Course registration → Hall ticket |
| Examinations | Student Info | Results → Transcript → Alumni |
| Finance | Payments | Fees → Payment order → GL entry |
| HR | HRMS | Faculty profile → Employee → Payroll |
| LMS | OBE | Quiz/Assignment scores → CO attainment |
| Placement | Portals | Drives → Portal applications |
| Integrations | Finance | Payment webhooks → Fee updates |

### Scheduled Tasks

```python
scheduler_events = {
    "daily": [
        "send_fee_reminders",
        "send_library_overdue_notices",
        "update_student_cgpa",
    ],
    "weekly": [
        "send_attendance_warnings",
        "send_placement_updates",
    ],
    "monthly": [
        "generate_monthly_reports",
        "update_placement_statistics",
    ],
}
```

## Getting Started

1. **New to the system?** Start with [00_SYSTEM_OVERVIEW.md](00_SYSTEM_OVERVIEW.md)
2. **Understanding data flow?** Follow the Student entity through modules
3. **Adding a feature?** Find the relevant module documentation
4. **Integration questions?** Check the Integration Points section in each module

## Related Documentation

- [Architecture Overview](../01_architecture_overview.md)
- [Module Mapping](../03_module_mapping.md)
- [Education Deep Dive](../04_education_deep_dive.md)
- [HRMS Deep Dive](../05_hrms_deep_dive.md)
- [Security & Permissions](../06_security_permissions.md)
- [Implementation Phases](../phases/README.md)

---

**Last Updated**: January 2026
**Total Documentation Files**: 18
**Architecture**: Hybrid (Frappe Education + ERPNext + HRMS + Custom)

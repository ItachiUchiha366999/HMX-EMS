# University ERP - Module Mapping (Hybrid Approach)

## Overview

This document maps University ERP functional modules to:
1. **Frappe Education DocTypes** (reused with custom fields)
2. **Custom DocTypes** (built new in `university_erp`)
3. **ERPNext Backend Engines** (used silently)

---

## Module Mapping Summary

| University Module | Frappe Education (Reuse) | Custom DocTypes (Build) | ERPNext Engine |
|-------------------|--------------------------|-------------------------|----------------|
| **Academics** | Program, Course, Student Group | Credit Structure, Elective Group | - |
| **Admissions** | Student Applicant | Merit List, Seat Matrix, Admission Cycle | - |
| **Student Info (SIS)** | Student, Guardian | - (use custom fields) | - |
| **Attendance** | Student Attendance | Biometric Log | - |
| **Examinations** | Assessment Plan, Assessment Result | Hall Ticket, Seating, Transcript | - |
| **Fees & Finance** | Fees, Fee Schedule, Fee Category | Scholarship, Fee Waiver | Accounts (GL) |
| **HR & Payroll** | - | University Faculty, Teaching Assignment | HRMS (Employee, Payroll) |
| **Hostel** | - | Hostel Building, Room, Allocation | - |
| **Transport** | - | Route, Vehicle, Student Transport | - |
| **Library** | Article, Library Member | - (extend if needed) | - |
| **LMS** | LMS Module (if available) | Course Content, Quiz, Submission | - |
| **Placement** | - | Company, Job Posting, Application | - |
| **Research** | - | Publication, Project, Grant | - |
| **OBE/Accreditation** | - | CO, PO, CO-PO Mapping | - |
| **Alumni** | - | Alumni, Event, Donation | - |

---

## 1. Academics Module

### Frappe Education DocTypes (Reuse)

| DocType | Purpose | Custom Fields Added |
|---------|---------|---------------------|
| **Program** | Degree programs (B.Tech, MBA) | CBCS enabled, total credits, degree type, duration, max intake, grading scale |
| **Course** | Course catalog | Credits, L-T-P-S hours, course type, course outcomes |
| **Student Group** | Class sections | No major changes |
| **Academic Year** | Academic year master | No changes |
| **Academic Term** | Semester/term | No changes |
| **Instructor** | Maps to faculty | Link to University Faculty |

### Custom DocTypes (Build New)

```
cbcs/doctype/
├── credit_structure/          # Define credit rules per program
├── elective_group/            # Group elective courses
├── course_registration/       # Student course selection
└── course_prerequisite/       # Prerequisite mapping
```

#### Credit Structure DocType
```json
{
    "doctype": "DocType",
    "name": "Credit Structure",
    "module": "University ERP",
    "fields": [
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "semester", "fieldtype": "Link", "options": "Academic Term"},
        {"fieldname": "min_credits", "fieldtype": "Int", "label": "Minimum Credits"},
        {"fieldname": "max_credits", "fieldtype": "Int", "label": "Maximum Credits"},
        {"fieldname": "core_credits", "fieldtype": "Int", "label": "Core Course Credits"},
        {"fieldname": "elective_credits", "fieldtype": "Int", "label": "Elective Credits"},
        {"fieldname": "open_elective_credits", "fieldtype": "Int", "label": "Open Elective Credits"}
    ]
}
```

#### Elective Group DocType
```json
{
    "doctype": "DocType",
    "name": "Elective Group",
    "module": "University ERP",
    "fields": [
        {"fieldname": "group_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program"},
        {"fieldname": "semester", "fieldtype": "Link", "options": "Academic Term"},
        {"fieldname": "elective_type", "fieldtype": "Select", "options": "DSE\nGE\nSEC\nVAC"},
        {"fieldname": "min_courses_to_select", "fieldtype": "Int", "default": 1},
        {"fieldname": "max_courses_to_select", "fieldtype": "Int", "default": 1},
        {"fieldname": "courses", "fieldtype": "Table", "options": "Elective Course Item"}
    ]
}
```

---

## 2. Admissions Module

### Frappe Education DocTypes (Reuse)

| DocType | Purpose | Custom Fields Added |
|---------|---------|---------------------|
| **Student Applicant** | Application form | Category, entrance score, merit rank, admission cycle |
| **Program** | For program selection | Already extended |

### Custom DocTypes (Build New)

```
admissions/doctype/
├── admission_cycle/           # Admission cycle/year
├── seat_matrix/               # Category-wise seats
├── merit_list/                # Generated merit lists
├── counseling_schedule/       # Counseling slots
└── admission_offer/           # Offer letters
```

#### Admission Cycle DocType
```json
{
    "doctype": "DocType",
    "name": "Admission Cycle",
    "module": "University ERP",
    "fields": [
        {"fieldname": "cycle_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year"},
        {"fieldname": "start_date", "fieldtype": "Date"},
        {"fieldname": "end_date", "fieldtype": "Date"},
        {"fieldname": "application_start_date", "fieldtype": "Date"},
        {"fieldname": "application_end_date", "fieldtype": "Date"},
        {"fieldname": "programs", "fieldtype": "Table", "options": "Admission Cycle Program"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nOpen\nClosed"}
    ]
}
```

#### Merit List DocType
```json
{
    "doctype": "DocType",
    "name": "Merit List",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "admission_cycle", "fieldtype": "Link", "options": "Admission Cycle", "reqd": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "category", "fieldtype": "Select", "options": "General\nOBC\nSC\nST\nEWS"},
        {"fieldname": "list_number", "fieldtype": "Int", "label": "List Number (1st, 2nd, etc.)"},
        {"fieldname": "generated_date", "fieldtype": "Date"},
        {"fieldname": "applicants", "fieldtype": "Table", "options": "Merit List Applicant"}
    ]
}
```

### Student Applicant Custom Fields
```json
[
    {
        "dt": "Student Applicant",
        "fieldname": "admission_cycle",
        "fieldtype": "Link",
        "options": "Admission Cycle",
        "insert_after": "program"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "category",
        "fieldtype": "Select",
        "options": "General\nOBC\nSC\nST\nEWS",
        "insert_after": "admission_cycle"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "entrance_exam",
        "fieldtype": "Data",
        "label": "Entrance Exam",
        "insert_after": "category"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "entrance_score",
        "fieldtype": "Float",
        "insert_after": "entrance_exam"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "entrance_rank",
        "fieldtype": "Int",
        "insert_after": "entrance_score"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "merit_rank",
        "fieldtype": "Int",
        "read_only": 1,
        "insert_after": "entrance_rank"
    }
]
```

---

## 3. Student Information System (SIS)

### Frappe Education DocTypes (Reuse)

| DocType | Purpose | Custom Fields Added |
|---------|---------|---------------------|
| **Student** | Core student record | Enrollment number, roll number, category, CGPA, credits earned, biometric ID |
| **Guardian** | Parent/guardian info | No major changes |
| **Student Log** | Activity log | No changes |
| **Program Enrollment** | Program registration | No changes |
| **Course Enrollment** | Course registration | No changes |

### Student Lifecycle (Using Education + Extensions)

```python
# university_erp/overrides/student_applicant.py

def on_update_after_submit(doc, method):
    """Convert approved applicant to student"""
    if doc.application_status == "Approved":
        create_student_from_applicant(doc)

def create_student_from_applicant(applicant):
    """Create Student record from approved applicant"""
    from education.education.doctype.student_applicant.student_applicant import (
        make_student
    )

    # Use Education module's built-in conversion
    student = make_student(applicant.name)

    # Add university-specific fields
    student.enrollment_number = generate_enrollment_number(applicant)
    student.category = applicant.category
    student.save()

    # Create program enrollment
    create_program_enrollment(student, applicant.program)

    return student
```

---

## 4. Examinations Module

### Frappe Education DocTypes (Reuse)

| DocType | Purpose | Custom Fields Added |
|---------|---------|---------------------|
| **Assessment Plan** | Exam planning | Exam type, venue, invigilator |
| **Assessment Result** | Results storage | Grade, grade points, credit points, result status |
| **Assessment Criteria** | Marking scheme | No changes |
| **Grading Scale** | Grade definitions | Already exists in Education |

### Custom DocTypes (Build New)

```
examinations/doctype/
├── university_examination/    # Master exam record
├── hall_ticket/               # Admit cards
├── seating_arrangement/       # Room-wise seating
├── grade_card/                # Semester grade card
├── student_transcript/        # Complete transcript
└── exam_schedule/             # Exam timetable
```

#### University Examination DocType
```json
{
    "doctype": "DocType",
    "name": "University Examination",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "examination_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "exam_type", "fieldtype": "Select", "options": "Internal\nMid Semester\nEnd Semester\nSupplementary"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year"},
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term"},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program"},
        {"fieldname": "start_date", "fieldtype": "Date"},
        {"fieldname": "end_date", "fieldtype": "Date"},
        {"fieldname": "result_entry_deadline", "fieldtype": "Date"},
        {"fieldname": "courses", "fieldtype": "Table", "options": "Examination Course"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Scheduled\nOngoing\nCompleted\nResults Declared"}
    ]
}
```

#### Hall Ticket DocType
```json
{
    "doctype": "DocType",
    "name": "Hall Ticket",
    "module": "University ERP",
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1},
        {"fieldname": "examination", "fieldtype": "Link", "options": "University Examination", "reqd": 1},
        {"fieldname": "hall_ticket_number", "fieldtype": "Data", "unique": 1},
        {"fieldname": "eligible_courses", "fieldtype": "Table", "options": "Hall Ticket Course"},
        {"fieldname": "photo", "fieldtype": "Attach Image"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nIssued\nRevoked"}
    ],
    "autoname": "naming_series:HT-.YYYY.-"
}
```

#### Student Transcript DocType
```json
{
    "doctype": "DocType",
    "name": "Student Transcript",
    "module": "University ERP",
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1},
        {"fieldname": "transcript_number", "fieldtype": "Data", "unique": 1},
        {"fieldname": "generated_date", "fieldtype": "Date"},
        {"fieldname": "cgpa", "fieldtype": "Float"},
        {"fieldname": "total_credits", "fieldtype": "Int"},
        {"fieldname": "degree_class", "fieldtype": "Data"},
        {"fieldname": "semester_results", "fieldtype": "Table", "options": "Transcript Semester"},
        {"fieldname": "digilocker_uri", "fieldtype": "Data", "read_only": 1}
    ]
}
```

### Assessment Result Extensions
```python
# university_erp/overrides/assessment_result.py

from education.education.doctype.assessment_result.assessment_result import AssessmentResult

class UniversityAssessmentResult(AssessmentResult):
    """Extended with university grading"""

    def validate(self):
        super().validate()
        self.calculate_university_grade()

    def calculate_university_grade(self):
        """Calculate grade, grade points, credit points"""
        if not self.total_score:
            return

        grading_scale = self.get_grading_scale()
        percentage = (self.total_score / (self.maximum_score or 100)) * 100

        # Find grade from scale
        scale = frappe.get_doc("Grading Scale", grading_scale)
        for interval in scale.intervals:
            if interval.threshold <= percentage:
                self.grade = interval.grade
                self.grade_points = interval.grade_point
                break

        # Credit points = grade points × credits
        credits = frappe.db.get_value("Course", self.course, "credits") or 0
        self.credit_points = (self.grade_points or 0) * credits

        # Set result status
        pass_grade_point = frappe.db.get_value("Grading Scale", grading_scale, "minimum_pass_grade_point") or 4
        self.result_status = "Pass" if (self.grade_points or 0) >= pass_grade_point else "Fail"
```

---

## 5. Fees & Finance Module

### Frappe Education DocTypes (Reuse)

| DocType | Purpose | Custom Fields Added |
|---------|---------|---------------------|
| **Fees** | Fee invoice | GL accounts, payment gateway fields |
| **Fee Schedule** | Fee planning | No changes |
| **Fee Category** | Fee types | No changes |
| **Fee Structure** | Fee templates | No changes |

### Custom DocTypes (Build New)

```
fees/doctype/
├── scholarship/               # Scholarship master
├── scholarship_application/   # Student applications
├── fee_concession/            # Concession types
├── fee_waiver/                # Approved waivers
└── refund_request/            # Fee refunds
```

#### Scholarship DocType
```json
{
    "doctype": "DocType",
    "name": "Scholarship",
    "module": "University ERP",
    "fields": [
        {"fieldname": "scholarship_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "scholarship_type", "fieldtype": "Select", "options": "Merit Based\nNeed Based\nGovernment\nPrivate"},
        {"fieldname": "amount", "fieldtype": "Currency"},
        {"fieldname": "percentage", "fieldtype": "Percent"},
        {"fieldname": "eligibility_criteria", "fieldtype": "Text Editor"},
        {"fieldname": "applicable_programs", "fieldtype": "Table", "options": "Scholarship Program"},
        {"fieldname": "valid_from", "fieldtype": "Date"},
        {"fieldname": "valid_to", "fieldtype": "Date"},
        {"fieldname": "max_recipients", "fieldtype": "Int"}
    ]
}
```

### ERPNext Backend: Accounts Engine
```python
# university_erp/overrides/fees.py

def create_gl_entries(doc, method):
    """Create GL entries using ERPNext Accounts (hidden)"""
    from erpnext.accounts.general_ledger import make_gl_entries

    settings = frappe.get_single("University Settings")

    gl_entries = [
        # Debit: Receivable
        {
            "account": settings.student_receivable_account,
            "party_type": "Customer",
            "party": get_or_create_student_customer(doc.student),
            "debit": doc.grand_total,
            "voucher_type": "Fees",
            "voucher_no": doc.name,
            "company": settings.company,
            "posting_date": doc.posting_date,
        },
        # Credit: Income
        {
            "account": settings.fee_income_account,
            "credit": doc.grand_total,
            "voucher_type": "Fees",
            "voucher_no": doc.name,
            "company": settings.company,
            "posting_date": doc.posting_date,
            "cost_center": settings.default_cost_center,
        }
    ]

    make_gl_entries(gl_entries)
```

---

## 6. University HR Module

### Frappe Education DocTypes (Limited Use)

| DocType | Purpose | Notes |
|---------|---------|-------|
| **Instructor** | Basic instructor | Link to University Faculty |

### Custom DocTypes (Build New - Primary)

```
university_hr/doctype/
├── university_faculty/        # Faculty master (links to Employee)
├── university_staff/          # Non-teaching staff
├── teaching_assignment/       # Course-faculty mapping
├── faculty_workload/          # Workload tracking
├── faculty_appraisal/         # Performance appraisal
├── faculty_publication/       # Research publications
└── administrative_duty/       # HOD, Dean assignments
```

#### University Faculty DocType
```json
{
    "doctype": "DocType",
    "name": "University Faculty",
    "module": "University ERP",
    "fields": [
        {"fieldname": "faculty_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "employee_id", "fieldtype": "Data", "unique": 1},
        {"fieldname": "employee", "fieldtype": "Link", "options": "Employee", "hidden": 1},
        {"fieldname": "department", "fieldtype": "Link", "options": "Department", "reqd": 1},
        {"fieldname": "designation", "fieldtype": "Select", "options": "Professor\nAssociate Professor\nAssistant Professor\nLecturer"},
        {"fieldname": "employee_type", "fieldtype": "Select", "options": "Permanent\nContract\nVisiting"},
        {"fieldname": "date_of_joining", "fieldtype": "Date"},
        {"fieldname": "qualifications", "fieldtype": "Table", "options": "Faculty Qualification"},
        {"fieldname": "specialization", "fieldtype": "Small Text"},
        {"fieldname": "max_weekly_hours", "fieldtype": "Int", "default": 16},
        {"fieldname": "current_workload", "fieldtype": "Float", "read_only": 1},
        {"fieldname": "email", "fieldtype": "Data", "options": "Email"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nOn Leave\nResigned\nRetired"}
    ]
}
```

#### Teaching Assignment DocType
```json
{
    "doctype": "DocType",
    "name": "Teaching Assignment",
    "module": "University ERP",
    "fields": [
        {"fieldname": "faculty", "fieldtype": "Link", "options": "University Faculty", "reqd": 1},
        {"fieldname": "course", "fieldtype": "Link", "options": "Course", "reqd": 1},
        {"fieldname": "student_group", "fieldtype": "Link", "options": "Student Group"},
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year"},
        {"fieldname": "assignment_type", "fieldtype": "Select", "options": "Lecture\nTutorial\nPractical\nProject Guide"},
        {"fieldname": "weekly_hours", "fieldtype": "Float"},
        {"fieldname": "schedule", "fieldtype": "Table", "options": "Class Schedule Entry"}
    ]
}
```

### ERPNext Backend: HRMS Engine
```python
# university_erp/university_hr/events.py

def create_employee(doc, method):
    """Create ERPNext Employee when Faculty is created"""
    if doc.employee:
        return

    employee = frappe.new_doc("Employee")
    employee.employee_name = doc.faculty_name
    employee.date_of_joining = doc.date_of_joining
    employee.designation = doc.designation
    employee.department = doc.department
    employee.company = frappe.get_single("University Settings").company
    employee.employment_type = doc.employee_type
    employee.status = "Active"
    # Custom link back
    employee.university_faculty = doc.name
    employee.flags.ignore_permissions = True
    employee.insert()

    doc.employee = employee.name
    doc.db_update()

def sync_employee(doc, method):
    """Sync Faculty changes to Employee"""
    if not doc.employee:
        return

    frappe.db.set_value("Employee", doc.employee, {
        "employee_name": doc.faculty_name,
        "designation": doc.designation,
        "status": "Active" if doc.status == "Active" else "Left"
    })
```

---

## 7-12. Other Modules (Summary)

### 7. Hostel Module (All Custom)
| DocType | Purpose |
|---------|---------|
| Hostel Building | Building master |
| Hostel Room | Room inventory |
| Room Allocation | Student assignment |
| Hostel Fee | Linked to Fees |
| Hostel Attendance | Daily check-in |

### 8. Transport Module (All Custom)
| DocType | Purpose |
|---------|---------|
| Transport Route | Route master |
| Transport Vehicle | Vehicle inventory |
| Student Transport | Student-route mapping |
| Transport Fee | Linked to Fees |

### 9. Library Module (Use Education's)
Frappe Education has basic library support:
- Article
- Library Member
- Library Transaction

Extend if needed for:
- E-resources
- RFID integration
- Advanced reservations

### 10. LMS Module
If using Frappe LMS app:
- Reuse Course, Lesson, Quiz DocTypes
- Add custom assignments and grading

If building custom:
```
lms/doctype/
├── lms_course/
├── course_content/
├── lms_quiz/
├── quiz_attempt/
├── lms_assignment/
└── assignment_submission/
```

### 11. Placement Module (All Custom)
```
placement/doctype/
├── placement_company/
├── job_posting/
├── placement_application/
├── interview_schedule/
├── placement_offer/
└── placement_statistics/
```

### 12. OBE/Accreditation Module (All Custom)
```
obe/doctype/
├── course_outcome/
├── program_outcome/
├── program_educational_objective/
├── co_po_mapping/
├── obe_assessment/
└── attainment_report/
```

---

## Integration Points Summary

| University Module | Education DocType | Custom Extension | ERPNext Engine |
|-------------------|-------------------|------------------|----------------|
| Student Records | Student | Custom fields + Override class | - |
| Academics | Program, Course | Custom fields + CBCS DocTypes | - |
| Admissions | Student Applicant | Merit List, Seat Matrix | - |
| Attendance | Student Attendance | Biometric integration | - |
| Exams | Assessment Plan/Result | Hall Ticket, Transcript | - |
| Fees | Fees, Fee Schedule | Scholarship, Waiver | Accounts (GL) |
| HR | (Instructor) | University Faculty | HRMS (Employee, Payroll) |
| Library | Article, Library Member | Minor extensions | - |

---

## Next Document

Continue to [04_education_deep_dive.md](04_education_deep_dive.md) for detailed implementation of Education module extensions.

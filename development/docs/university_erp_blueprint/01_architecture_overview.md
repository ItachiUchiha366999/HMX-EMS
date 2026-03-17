# University ERP - Hybrid Architecture Blueprint

## Overview

This document outlines how to build a **University ERP** using a **hybrid approach**:
- **Frappe Education** as the foundation for core academic DocTypes
- **Custom `university_erp` app** for university-specific extensions and UI
- **ERPNext/HRMS** as hidden backend engines for finance and HR

This approach significantly reduces development time while achieving a dedicated university product experience.

---

## Hybrid Architecture Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    university_erp                           │
│         (Custom extensions, UI overrides, new modules)      │
│  • OBE/Accreditation  • Research  • Placement  • Advanced   │
│  • CBCS Extensions    • Portals   • Analytics    Fees       │
├─────────────────────────────────────────────────────────────┤
│                   Frappe Education                          │
│              (Base academic DocTypes)                       │
│  • Student  • Program  • Course  • Student Group            │
│  • Assessment  • Fees (basic)  • Attendance                 │
├─────────────────────────────────────────────────────────────┤
│                  ERPNext + HRMS                             │
│              (Hidden backend engines)                       │
│  • Accounts (GL, Payments)  • HR (Employee, Payroll, Leave) │
├─────────────────────────────────────────────────────────────┤
│                      Frappe                                 │
│              (Core framework)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## What We Reuse vs Build

### From Frappe Education (Reuse & Extend)

| DocType | Usage | Extension Needed |
|---------|-------|------------------|
| Student | Core student record | Add university-specific fields |
| Program | Degree programs | Add CBCS, duration, intake |
| Course | Course catalog | Add L-T-P-S credits, OBE fields |
| Student Group | Class sections | Minor extensions |
| Student Attendance | Attendance tracking | Biometric integration |
| Assessment Plan | Exam planning | Extend for university exams |
| Assessment Result | Results storage | Add grading scale, CGPA |
| Fees | Basic fee structure | Extend significantly |
| Fee Schedule | Fee planning | Extend for installments |
| Student Applicant | Admissions | Extend for merit lists |

### Custom DocTypes (Build New)

| Module | New DocTypes |
|--------|--------------|
| **CBCS System** | Credit Structure, Elective Group, CO-PO Mapping |
| **Advanced Exams** | Examination, Hall Ticket, Seating Arrangement, Transcript |
| **Research** | Faculty Publication, Research Project, Research Grant |
| **Placement** | Placement Company, Job Posting, Placement Application |
| **Accreditation** | Course Outcome, Program Outcome, OBE Assessment |
| **Advanced HR** | University Faculty, Teaching Assignment, Faculty Workload |
| **Hostel** | Hostel Building, Room, Room Allocation |
| **Transport** | Route, Vehicle, Student Transport |
| **Library** | (Can use Education's or extend) |

---

## App Structure

```
university_erp/
├── university_erp/
│   ├── __init__.py
│   ├── hooks.py                    # Critical: app configuration
│   ├── patches/                    # Data migrations
│   │
│   ├── overrides/                  # Extend Education DocTypes
│   │   ├── student.py              # Extend Student
│   │   ├── program.py              # Extend Program
│   │   ├── course.py               # Extend Course
│   │   ├── assessment_result.py    # Extend Assessment Result
│   │   └── fees.py                 # Extend Fees
│   │
│   ├── custom_fields/              # Custom fields on Education DocTypes
│   │   └── education_custom_fields.json
│   │
│   ├── cbcs/                       # CBCS Credit System (NEW)
│   │   ├── doctype/
│   │   │   ├── credit_structure/
│   │   │   ├── elective_group/
│   │   │   └── course_registration/
│   │   └── cbcs_manager.py
│   │
│   ├── examinations/               # Advanced Exam System (NEW)
│   │   ├── doctype/
│   │   │   ├── university_examination/
│   │   │   ├── hall_ticket/
│   │   │   ├── seating_arrangement/
│   │   │   ├── grade_card/
│   │   │   └── student_transcript/
│   │   └── result_processing.py
│   │
│   ├── obe/                        # OBE & Accreditation (NEW)
│   │   ├── doctype/
│   │   │   ├── course_outcome/
│   │   │   ├── program_outcome/
│   │   │   ├── co_po_mapping/
│   │   │   └── obe_assessment/
│   │   └── attainment_calculator.py
│   │
│   ├── university_hr/              # Faculty Management (NEW)
│   │   ├── doctype/
│   │   │   ├── university_faculty/
│   │   │   ├── teaching_assignment/
│   │   │   ├── faculty_workload/
│   │   │   └── faculty_appraisal/
│   │   └── workload_engine.py
│   │
│   ├── research/                   # Research Module (NEW)
│   │   ├── doctype/
│   │   │   ├── faculty_publication/
│   │   │   ├── research_project/
│   │   │   └── research_grant/
│   │   └── research_metrics.py
│   │
│   ├── placement/                  # Placement Module (NEW)
│   │   ├── doctype/
│   │   │   ├── placement_company/
│   │   │   ├── job_posting/
│   │   │   └── placement_application/
│   │   └── placement_statistics.py
│   │
│   ├── hostel/                     # Hostel Management (NEW)
│   ├── transport/                  # Transport Management (NEW)
│   │
│   ├── workspace/                  # Custom Workspaces
│   │   ├── university_home/
│   │   ├── academics/
│   │   ├── examinations/
│   │   └── ...
│   │
│   ├── www/                        # Portal Pages
│   │   ├── student-portal/
│   │   └── faculty-portal/
│   │
│   └── public/
│       ├── css/university_theme.css
│       └── js/university_erp.bundle.js
│
├── setup.py
├── requirements.txt
└── MANIFEST.in
```

---

## hooks.py - Hybrid Configuration

```python
app_name = "university_erp"
app_title = "University ERP"
app_publisher = "Your Organization"
app_description = "Comprehensive University Management System"
app_version = "1.0.0"
app_color = "#1a365d"

# ============================================================
# CRITICAL: App Dependencies
# ============================================================

# Frappe Education is required
required_apps = ["education"]

# ============================================================
# Extend Education DocTypes
# ============================================================

# Override DocType classes to add custom logic
override_doctype_class = {
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Assessment Result": "university_erp.overrides.assessment_result.UniversityAssessmentResult",
    "Fees": "university_erp.overrides.fees.UniversityFees",
    "Student Applicant": "university_erp.overrides.student_applicant.UniversityApplicant",
}

# ============================================================
# Hide ERPNext Core Modules (Keep Education visible but themed)
# ============================================================

block_modules = [
    "Manufacturing",
    "Stock",
    "Selling",
    "Buying",
    "CRM",
    "Projects",
    "Quality Management",
    "Assets",
    "Support",
    "Website",
    "E Commerce",
]

# ============================================================
# Custom Fields on Education DocTypes
# ============================================================

# Loaded from fixtures
fixtures = [
    # Custom fields on Education DocTypes
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "University ERP"]]
    },
    # Property setters for UI changes
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "University ERP"]]
    },
    # Custom workspaces
    {
        "dt": "Workspace",
        "filters": [["module", "=", "University ERP"]]
    },
    # University-specific roles
    {
        "dt": "Role",
        "filters": [["name", "like", "University%"]]
    },
    # Workflows
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", [
            "Student Applicant", "Student", "Fees", "Assessment Result"
        ]]]
    },
    # Print Formats
    {
        "dt": "Print Format",
        "filters": [["module", "=", "University ERP"]]
    },
]

# ============================================================
# App Includes
# ============================================================

app_include_css = [
    "/assets/university_erp/css/university_theme.css"
]

app_include_js = [
    "/assets/university_erp/js/university_erp.bundle.js"
]

# ============================================================
# Document Events - Extend Education Behavior
# ============================================================

doc_events = {
    # Extend Student behavior
    "Student": {
        "after_insert": "university_erp.overrides.student.after_insert",
        "on_update": "university_erp.overrides.student.on_update",
        "validate": "university_erp.overrides.student.validate",
    },
    # Extend Assessment Result for CGPA calculation
    "Assessment Result": {
        "on_submit": "university_erp.overrides.assessment_result.calculate_cgpa",
        "validate": "university_erp.overrides.assessment_result.validate_grading",
    },
    # Extend Fees for GL integration
    "Fees": {
        "on_submit": "university_erp.overrides.fees.create_gl_entries",
        "on_cancel": "university_erp.overrides.fees.reverse_gl_entries",
    },
    # Extend Student Applicant for admission workflow
    "Student Applicant": {
        "on_update": "university_erp.overrides.student_applicant.update_merit_list",
    },
    # Link Faculty to Employee
    "University Faculty": {
        "after_insert": "university_erp.university_hr.events.create_employee",
        "on_update": "university_erp.university_hr.events.sync_employee",
    },
}

# ============================================================
# Scheduler
# ============================================================

scheduler_events = {
    "daily": [
        "university_erp.tasks.daily.mark_absent_students",
        "university_erp.tasks.daily.send_fee_reminders",
    ],
    "weekly": [
        "university_erp.tasks.weekly.generate_attendance_reports",
    ],
    "monthly": [
        "university_erp.tasks.monthly.generate_defaulter_list",
    ],
}

# ============================================================
# Jinja
# ============================================================

jinja = {
    "methods": [
        "university_erp.utils.jinja_methods"
    ]
}

# ============================================================
# Installation
# ============================================================

after_install = "university_erp.setup.install.after_install"
after_migrate = "university_erp.setup.install.after_migrate"

# ============================================================
# Boot Session
# ============================================================

boot_session = "university_erp.startup.boot.boot_session"

# ============================================================
# Portal
# ============================================================

portal_menu_items = [
    {"title": "My Dashboard", "route": "/student-portal", "role": "Student"},
    {"title": "My Courses", "route": "/student-portal/courses", "role": "Student"},
    {"title": "My Results", "route": "/student-portal/results", "role": "Student"},
]

# ============================================================
# Global Search - Include Education DocTypes
# ============================================================

global_search_doctypes = {
    "Default": [
        {"doctype": "Student", "index": 0},
        {"doctype": "University Faculty", "index": 1},
        {"doctype": "Course", "index": 2},
        {"doctype": "Program", "index": 3},
        {"doctype": "Fees", "index": 4},
        {"doctype": "Student Applicant", "index": 5},
    ]
}
```

---

## Custom Fields on Education DocTypes

### Student Custom Fields
```json
[
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "university_section",
        "fieldtype": "Section Break",
        "label": "University Details",
        "insert_after": "student_email_id"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "enrollment_number",
        "fieldtype": "Data",
        "label": "Enrollment Number",
        "unique": 1,
        "insert_after": "university_section"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "roll_number",
        "fieldtype": "Data",
        "label": "Roll Number",
        "insert_after": "enrollment_number"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "current_semester",
        "fieldtype": "Link",
        "options": "Academic Term",
        "label": "Current Semester",
        "insert_after": "roll_number"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "category",
        "fieldtype": "Select",
        "options": "General\nOBC\nSC\nST\nEWS",
        "label": "Category",
        "insert_after": "current_semester"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "cgpa",
        "fieldtype": "Float",
        "label": "CGPA",
        "read_only": 1,
        "insert_after": "category"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "total_credits_earned",
        "fieldtype": "Int",
        "label": "Total Credits Earned",
        "read_only": 1,
        "insert_after": "cgpa"
    },
    {
        "doctype": "Custom Field",
        "dt": "Student",
        "module": "University ERP",
        "fieldname": "biometric_id",
        "fieldtype": "Data",
        "label": "Biometric ID",
        "insert_after": "total_credits_earned"
    }
]
```

### Program Custom Fields
```json
[
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "cbcs_section",
        "fieldtype": "Section Break",
        "label": "CBCS Configuration",
        "insert_after": "program_abbreviation"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "is_cbcs_enabled",
        "fieldtype": "Check",
        "label": "CBCS Enabled",
        "insert_after": "cbcs_section"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "total_credits",
        "fieldtype": "Int",
        "label": "Total Credits Required",
        "insert_after": "is_cbcs_enabled"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "min_credits_graduation",
        "fieldtype": "Int",
        "label": "Minimum Credits for Graduation",
        "insert_after": "total_credits"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "degree_type",
        "fieldtype": "Select",
        "options": "Certificate\nDiploma\nUG\nPG\nIntegrated\nPhD",
        "label": "Degree Type",
        "insert_after": "min_credits_graduation"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "duration_years",
        "fieldtype": "Float",
        "label": "Duration (Years)",
        "insert_after": "degree_type"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "max_intake",
        "fieldtype": "Int",
        "label": "Maximum Intake",
        "insert_after": "duration_years"
    },
    {
        "doctype": "Custom Field",
        "dt": "Program",
        "module": "University ERP",
        "fieldname": "grading_scale",
        "fieldtype": "Link",
        "options": "Grading Scale",
        "label": "Grading Scale",
        "insert_after": "max_intake"
    }
]
```

### Course Custom Fields
```json
[
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "credit_section",
        "fieldtype": "Section Break",
        "label": "Credit Structure (L-T-P-S)",
        "insert_after": "course_abbreviation"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "credits",
        "fieldtype": "Int",
        "label": "Credits",
        "insert_after": "credit_section"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "lecture_hours",
        "fieldtype": "Int",
        "label": "L (Lecture Hours/Week)",
        "insert_after": "credits"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "tutorial_hours",
        "fieldtype": "Int",
        "label": "T (Tutorial Hours/Week)",
        "insert_after": "lecture_hours"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "practical_hours",
        "fieldtype": "Int",
        "label": "P (Practical Hours/Week)",
        "insert_after": "tutorial_hours"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "self_study_hours",
        "fieldtype": "Int",
        "label": "S (Self Study Hours/Week)",
        "insert_after": "practical_hours"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "course_type",
        "fieldtype": "Select",
        "options": "Core\nDSE\nGE\nSEC\nAEC\nVAC\nProject\nInternship",
        "label": "Course Type",
        "insert_after": "self_study_hours"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "obe_section",
        "fieldtype": "Section Break",
        "label": "Outcome Based Education",
        "insert_after": "course_type"
    },
    {
        "doctype": "Custom Field",
        "dt": "Course",
        "module": "University ERP",
        "fieldname": "course_outcomes",
        "fieldtype": "Table",
        "options": "Course Outcome Item",
        "label": "Course Outcomes (COs)",
        "insert_after": "obe_section"
    }
]
```

### Assessment Result Custom Fields
```json
[
    {
        "doctype": "Custom Field",
        "dt": "Assessment Result",
        "module": "University ERP",
        "fieldname": "grading_section",
        "fieldtype": "Section Break",
        "label": "University Grading",
        "insert_after": "total_score"
    },
    {
        "doctype": "Custom Field",
        "dt": "Assessment Result",
        "module": "University ERP",
        "fieldname": "grade",
        "fieldtype": "Data",
        "label": "Grade",
        "read_only": 1,
        "insert_after": "grading_section"
    },
    {
        "doctype": "Custom Field",
        "dt": "Assessment Result",
        "module": "University ERP",
        "fieldname": "grade_points",
        "fieldtype": "Float",
        "label": "Grade Points",
        "read_only": 1,
        "insert_after": "grade"
    },
    {
        "doctype": "Custom Field",
        "dt": "Assessment Result",
        "module": "University ERP",
        "fieldname": "credit_points",
        "fieldtype": "Float",
        "label": "Credit Points",
        "read_only": 1,
        "insert_after": "grade_points"
    },
    {
        "doctype": "Custom Field",
        "dt": "Assessment Result",
        "module": "University ERP",
        "fieldname": "result_status",
        "fieldtype": "Select",
        "options": "Pass\nFail\nAbsent\nWithheld",
        "label": "Result Status",
        "insert_after": "credit_points"
    }
]
```

---

## DocType Override Classes

### Extending Student
```python
# university_erp/overrides/student.py

import frappe
from education.education.doctype.student.student import Student

class UniversityStudent(Student):
    """Extended Student class with university-specific logic"""

    def validate(self):
        super().validate()
        self.validate_enrollment_number()
        self.validate_category_documents()

    def validate_enrollment_number(self):
        """Auto-generate enrollment number if not set"""
        if not self.enrollment_number:
            self.enrollment_number = self.generate_enrollment_number()

    def generate_enrollment_number(self):
        """Generate unique enrollment number"""
        year = frappe.utils.nowdate()[:4]
        program_code = frappe.db.get_value("Program", self.program, "program_abbreviation") or "GEN"

        # Get next sequence
        last = frappe.db.sql("""
            SELECT MAX(CAST(SUBSTRING(enrollment_number, -4) AS UNSIGNED))
            FROM `tabStudent`
            WHERE enrollment_number LIKE %s
        """, (f"{year}{program_code}%",))

        next_num = (last[0][0] or 0) + 1
        return f"{year}{program_code}{next_num:04d}"

    def validate_category_documents(self):
        """Validate category certificate is uploaded for reserved categories"""
        if self.category in ["SC", "ST", "OBC", "EWS"]:
            if not self.has_category_certificate():
                frappe.msgprint(
                    f"Category certificate recommended for {self.category} category",
                    indicator="orange"
                )

    def has_category_certificate(self):
        """Check if category certificate is attached"""
        attachments = frappe.get_all(
            "File",
            filters={"attached_to_doctype": "Student", "attached_to_name": self.name}
        )
        return len(attachments) > 0

    def calculate_cgpa(self):
        """Calculate CGPA from all assessment results"""
        results = frappe.get_all(
            "Assessment Result",
            filters={"student": self.name, "docstatus": 1},
            fields=["credit_points", "course"]
        )

        if not results:
            return 0

        total_credit_points = 0
        total_credits = 0

        for r in results:
            credits = frappe.db.get_value("Course", r.course, "credits") or 0
            total_credit_points += r.credit_points or 0
            total_credits += credits

        return round(total_credit_points / total_credits, 2) if total_credits else 0


# Event hooks
def after_insert(doc, method):
    """Actions after student creation"""
    # Create user account
    if doc.student_email_id and not doc.user:
        create_student_user(doc)

def on_update(doc, method):
    """Actions on student update"""
    # Sync user if email changed
    pass

def validate(doc, method):
    """Additional validations"""
    pass

def create_student_user(doc):
    """Create portal user for student"""
    if frappe.db.exists("User", doc.student_email_id):
        doc.user = doc.student_email_id
        return

    user = frappe.new_doc("User")
    user.email = doc.student_email_id
    user.first_name = doc.first_name
    user.last_name = doc.last_name
    user.user_type = "Website User"
    user.send_welcome_email = 1
    user.add_roles("Student")
    user.flags.ignore_permissions = True
    user.insert()

    doc.user = user.name
```

### Extending Assessment Result
```python
# university_erp/overrides/assessment_result.py

import frappe
from education.education.doctype.assessment_result.assessment_result import AssessmentResult

class UniversityAssessmentResult(AssessmentResult):
    """Extended Assessment Result with university grading"""

    def validate(self):
        super().validate()
        self.calculate_grade()

    def calculate_grade(self):
        """Calculate grade from grading scale"""
        if not self.total_score:
            return

        # Get grading scale from program or use default
        grading_scale = self.get_grading_scale()

        if not grading_scale:
            return

        # Calculate percentage
        max_score = self.maximum_score or 100
        percentage = (self.total_score / max_score) * 100

        # Find grade
        scale = frappe.get_doc("Grading Scale", grading_scale)
        for interval in scale.intervals:
            if interval.threshold <= percentage:
                self.grade = interval.grade
                self.grade_points = interval.grade_point
                break

        # Calculate credit points
        credits = frappe.db.get_value("Course", self.course, "credits") or 0
        self.credit_points = (self.grade_points or 0) * credits

    def get_grading_scale(self):
        """Get applicable grading scale"""
        # Try to get from program
        if self.program:
            scale = frappe.db.get_value("Program", self.program, "grading_scale")
            if scale:
                return scale

        # Fall back to default
        return frappe.db.get_single_value("Education Settings", "default_grading_scale")


def calculate_cgpa(doc, method):
    """Recalculate student CGPA after result submission"""
    student = frappe.get_doc("Student", doc.student)
    cgpa = student.calculate_cgpa()

    frappe.db.set_value("Student", doc.student, {
        "cgpa": cgpa,
        "total_credits_earned": calculate_total_credits(doc.student)
    })

def calculate_total_credits(student):
    """Calculate total credits earned"""
    results = frappe.get_all(
        "Assessment Result",
        filters={"student": student, "docstatus": 1, "result_status": "Pass"},
        fields=["course"]
    )

    total = 0
    for r in results:
        credits = frappe.db.get_value("Course", r.course, "credits") or 0
        total += credits

    return total

def validate_grading(doc, method):
    """Validate grading rules"""
    # Ensure course has credits defined
    credits = frappe.db.get_value("Course", doc.course, "credits")
    if not credits:
        frappe.throw(f"Credits not defined for course {doc.course}")
```

### Extending Fees
```python
# university_erp/overrides/fees.py

import frappe
from education.education.doctype.fees.fees import Fees

class UniversityFees(Fees):
    """Extended Fees with ERPNext Accounts integration"""

    def validate(self):
        super().validate()
        self.set_accounts()

    def set_accounts(self):
        """Set GL accounts from University Settings"""
        settings = frappe.get_single("University Settings")
        self.receivable_account = settings.student_receivable_account
        self.income_account = settings.fee_income_account
        self.company = settings.company


def create_gl_entries(doc, method):
    """Create GL entries on fee submission"""
    if not doc.grand_total:
        return

    from erpnext.accounts.general_ledger import make_gl_entries

    settings = frappe.get_single("University Settings")

    gl_entries = []

    # Debit: Student Receivable
    gl_entries.append({
        "account": settings.student_receivable_account,
        "party_type": "Customer",
        "party": get_student_customer(doc.student),
        "debit": doc.grand_total,
        "debit_in_account_currency": doc.grand_total,
        "against": settings.fee_income_account,
        "voucher_type": "Fees",
        "voucher_no": doc.name,
        "company": settings.company,
        "posting_date": doc.posting_date,
    })

    # Credit: Fee Income
    gl_entries.append({
        "account": settings.fee_income_account,
        "credit": doc.grand_total,
        "credit_in_account_currency": doc.grand_total,
        "against": get_student_customer(doc.student),
        "voucher_type": "Fees",
        "voucher_no": doc.name,
        "company": settings.company,
        "posting_date": doc.posting_date,
        "cost_center": settings.default_cost_center,
    })

    make_gl_entries(gl_entries)

def reverse_gl_entries(doc, method):
    """Reverse GL entries on cancellation"""
    from erpnext.accounts.general_ledger import make_reverse_gl_entries
    make_reverse_gl_entries(voucher_type="Fees", voucher_no=doc.name)

def get_student_customer(student):
    """Get or create Customer for student"""
    customer = frappe.db.get_value("Customer", {"student": student})

    if customer:
        return customer

    # Create customer
    student_doc = frappe.get_doc("Student", student)

    customer_doc = frappe.new_doc("Customer")
    customer_doc.customer_name = student_doc.student_name
    customer_doc.customer_type = "Individual"
    customer_doc.customer_group = "Student"
    customer_doc.student = student
    customer_doc.flags.ignore_permissions = True
    customer_doc.insert()

    return customer_doc.name
```

---

## Installation Script

```python
# university_erp/setup/install.py

import frappe

def after_install():
    """Post-installation setup"""
    create_custom_fields()
    hide_erpnext_workspaces()
    setup_university_roles()
    setup_default_grading_scale()
    create_university_workspaces()
    print("University ERP installed successfully!")

def after_migrate():
    """Post-migration setup"""
    create_custom_fields()
    sync_workspaces()

def create_custom_fields():
    """Create custom fields on Education DocTypes"""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    custom_fields = get_all_custom_fields()
    create_custom_fields(custom_fields)

def get_all_custom_fields():
    """Return all custom field definitions"""
    return {
        "Student": [
            # ... student fields from JSON above
        ],
        "Program": [
            # ... program fields
        ],
        "Course": [
            # ... course fields
        ],
        "Assessment Result": [
            # ... assessment fields
        ],
    }

def hide_erpnext_workspaces():
    """Hide ERPNext default workspaces"""
    workspaces_to_hide = [
        "Manufacturing", "Stock", "Selling", "Buying",
        "CRM", "Projects", "Assets", "Support",
        "Quality", "Website", "Settings"
    ]

    for ws in workspaces_to_hide:
        if frappe.db.exists("Workspace", ws):
            frappe.db.set_value("Workspace", ws, {
                "public": 0
            })

    frappe.db.commit()

def setup_university_roles():
    """Create university-specific roles"""
    roles = [
        "University Admin",
        "University Registrar",
        "University Finance",
        "University HR Admin",
        "University HOD",
        "University Exam Cell",
        "University Faculty",
        "University Librarian",
        "University Warden",
        "University Placement Officer",
    ]

    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1 if role_name != "Student" else 0
            }).insert(ignore_permissions=True)

def setup_default_grading_scale():
    """Create default 10-point grading scale"""
    if frappe.db.exists("Grading Scale", "10-Point CBCS"):
        return

    scale = frappe.new_doc("Grading Scale")
    scale.grading_scale_name = "10-Point CBCS"
    scale.description = "Standard CBCS 10-point grading scale"

    intervals = [
        {"grade": "O", "threshold": 90, "grade_point": 10, "description": "Outstanding"},
        {"grade": "A+", "threshold": 80, "grade_point": 9, "description": "Excellent"},
        {"grade": "A", "threshold": 70, "grade_point": 8, "description": "Very Good"},
        {"grade": "B+", "threshold": 60, "grade_point": 7, "description": "Good"},
        {"grade": "B", "threshold": 55, "grade_point": 6, "description": "Above Average"},
        {"grade": "C", "threshold": 50, "grade_point": 5, "description": "Average"},
        {"grade": "P", "threshold": 40, "grade_point": 4, "description": "Pass"},
        {"grade": "F", "threshold": 0, "grade_point": 0, "description": "Fail"},
    ]

    for interval in intervals:
        scale.append("intervals", interval)

    scale.insert(ignore_permissions=True)
```

---

## Benefits of Hybrid Approach

| Aspect | Pure Custom | Hybrid Approach |
|--------|-------------|-----------------|
| **Development Time** | 18 months | 10-12 months |
| **Base DocTypes** | Build from scratch | Reuse 15+ DocTypes |
| **Maintenance** | Full responsibility | Shared with Education community |
| **Upgrades** | Custom patches | Education upgrades + custom patches |
| **Community** | None | Education module community |
| **Risk** | Higher | Lower |

---

## Next Document

Continue to [02_ui_workspace_strategy.md](02_ui_workspace_strategy.md) for workspace configuration that presents Education DocTypes with university branding.

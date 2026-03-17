# University ERP - App Interconnections Guide

## Overview

The University ERP system is built on a **hybrid architecture** using 5 interconnected Frappe apps. This document provides a comprehensive explanation of how these apps communicate, share data, and extend each other's functionality.

---

## App Stack Hierarchy

```
+==================================================================+
||                                                                 ||
||                      UNIVERSITY ERP APP                         ||
||                    (Custom University Logic)                    ||
||                                                                 ||
||   - 17 Modules                                                  ||
||   - 155 Custom DocTypes                                         ||
||   - 6 Override Classes                                          ||
||   - Doc Event Hooks                                             ||
||   - Scheduled Tasks                                             ||
||                                                                 ||
+==================================================================+
         |                    |                    |
         | extends            | extends            | extends
         v                    v                    v
+------------------+  +------------------+  +------------------+
|                  |  |                  |  |                  |
|    EDUCATION     |  |      HRMS        |  |     ERPNEXT      |
|      APP         |  |       APP        |  |       APP        |
|                  |  |                  |  |                  |
| - Student        |  | - Employee       |  | - Accounts       |
| - Program        |  | - Payroll        |  | - Company        |
| - Course         |  | - Leave          |  | - GL Engine      |
| - Fees           |  | - Attendance     |  | - Workflow       |
| - Assessment     |  | - Appraisal      |  |                  |
|                  |  |                  |  |                  |
+------------------+  +------------------+  +------------------+
         |                    |                    |
         |                    |                    |
         +--------------------+--------------------+
                              |
                              | all depend on
                              v
+==================================================================+
||                                                                 ||
||                     FRAPPE FRAMEWORK                            ||
||                    (Core Foundation)                            ||
||                                                                 ||
||   - DocType Engine        - Permission System                   ||
||   - Database Abstraction  - Workflow Engine                     ||
||   - REST API              - Report Builder                      ||
||   - Web Framework         - Scheduler                           ||
||   - User Management       - Email/Notification                  ||
||                                                                 ||
+==================================================================+
```

---

## App Dependencies Configuration

### Required Apps Declaration (hooks.py)

```python
# university_erp/hooks.py

app_name = "university_erp"
app_title = "University ERP"

# This declares the app dependency chain
required_apps = ["frappe", "erpnext", "hrms", "education"]
```

### Installation Order

Apps must be installed in this specific order due to dependencies:

```
1. frappe      (Framework - always first)
      ↓
2. erpnext     (Depends on frappe)
      ↓
3. hrms        (Depends on erpnext)
      ↓
4. education   (Depends on erpnext)
      ↓
5. university_erp (Depends on all above)
```

### apps.txt (Site Configuration)

```
frappe
erpnext
hrms
education
university_erp
```

---

## Interconnection Mechanisms

### 1. DocType Override Classes

The primary way University ERP extends Education app functionality:

```
+------------------------------------------------------------------+
|                    DOCTYPE OVERRIDE MECHANISM                     |
+------------------------------------------------------------------+
|                                                                   |
|   EDUCATION APP                    UNIVERSITY ERP                 |
|   (Original)                       (Override)                     |
|                                                                   |
|   +------------------+            +------------------------+      |
|   | class Student:   |            | class UniversityStudent|      |
|   |   def validate() |  ------→   |   (Student):           |      |
|   |   def on_submit()|            |                        |      |
|   +------------------+            |   def validate(self):  |      |
|                                   |     super().validate() |      |
|                                   |     # Custom logic     |      |
|                                   +------------------------+      |
|                                                                   |
+------------------------------------------------------------------+
```

**Configuration in hooks.py:**

```python
override_doctype_class = {
    # Education DocType → University ERP Override Class
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Assessment Result": "university_erp.overrides.assessment_result.UniversityAssessmentResult",
    "Fees": "university_erp.overrides.fees.UniversityFees",
    "Student Applicant": "university_erp.overrides.student_applicant.UniversityApplicant",
}
```

**Example Override Implementation:**

```python
# university_erp/overrides/student.py

from education.education.doctype.student.student import Student

class UniversityStudent(Student):
    """
    Extends Education's Student with university-specific logic.
    All Education Student functionality is preserved.
    """

    def validate(self):
        # Call parent validation first
        super().validate()

        # Add university-specific validation
        self.validate_enrollment_number()
        self.validate_program_eligibility()

    def on_update(self):
        super().on_update()

        # University-specific actions
        self.update_hostel_allocation()
        self.sync_library_membership()

    def validate_enrollment_number(self):
        """Custom: Generate enrollment number if not set"""
        if not self.custom_enrollment_number:
            self.custom_enrollment_number = self.generate_enrollment_number()

    def generate_enrollment_number(self):
        """Custom: University-specific enrollment format"""
        year = frappe.utils.nowdate()[:4]
        program_code = frappe.db.get_value("Program", self.custom_program, "program_code")
        sequence = get_next_sequence(program_code, year)
        return f"{year}{program_code}{sequence:04d}"
```

---

### 2. Doc Events (Hooks)

Allows University ERP to react to events on any DocType:

```
+------------------------------------------------------------------+
|                      DOC EVENT HOOKS                              |
+------------------------------------------------------------------+
|                                                                   |
|   When Education "Fees" is submitted:                             |
|                                                                   |
|   +------------------+                                            |
|   |   Fees DocType   |                                            |
|   |   (Education)    |                                            |
|   +------------------+                                            |
|           |                                                       |
|           | on_submit event                                       |
|           v                                                       |
|   +------------------+     +------------------+                   |
|   | University ERP   |     | University ERP   |                   |
|   | GL Integration   |     | Payment Module   |                   |
|   +------------------+     +------------------+                   |
|           |                        |                              |
|           v                        v                              |
|   +------------------+     +------------------+                   |
|   | ERPNext Accounts |     | Payment Gateway  |                   |
|   | (GL Entry)       |     | (Notifications)  |                   |
|   +------------------+     +------------------+                   |
|                                                                   |
+------------------------------------------------------------------+
```

**Configuration in hooks.py:**

```python
doc_events = {
    # Education DocType events
    "Student": {
        "validate": "university_erp.overrides.student.validate_student",
        "on_update": "university_erp.overrides.student.on_student_update",
    },

    # Fees integration with ERPNext Accounts
    "Fees": {
        "on_submit": [
            "university_erp.integrations.gl_integration.create_fee_gl_entry",
            "university_erp.university_payments.gl_posting.on_fees_submit",
        ],
        "on_cancel": "university_erp.university_payments.gl_posting.on_fees_cancel",
    },

    # HRMS integration
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

---

### 3. Custom Fields Extension

Adding university-specific fields to Education/HRMS DocTypes:

```
+------------------------------------------------------------------+
|                    CUSTOM FIELDS MECHANISM                        |
+------------------------------------------------------------------+
|                                                                   |
|   STUDENT (Education App)                                         |
|   +----------------------------------------------------------+   |
|   | Original Fields:                                          |   |
|   | - first_name                                              |   |
|   | - last_name                                               |   |
|   | - student_email                                           |   |
|   | - date_of_birth                                           |   |
|   +----------------------------------------------------------+   |
|   | Custom Fields (Added by University ERP):                  |   |
|   | - custom_enrollment_number                                |   |
|   | - custom_program (Link to Program)                        |   |
|   | - custom_category (SC/ST/OBC/General)                     |   |
|   | - custom_cgpa                                             |   |
|   | - custom_biometric_id                                     |   |
|   | - custom_hostel_allocation                                |   |
|   +----------------------------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

**Custom Fields JSON (fixtures):**

```python
# Exported via: bench export-fixtures
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "University ERP"]]},
]
```

**Example Custom Field Definition:**

```json
{
    "dt": "Student",
    "fieldname": "custom_enrollment_number",
    "fieldtype": "Data",
    "label": "Enrollment Number",
    "unique": 1,
    "in_list_view": 1,
    "insert_after": "student_name",
    "module": "University ERP"
}
```

---

### 4. Link Field References

DocTypes reference each other via Link fields:

```
+------------------------------------------------------------------+
|                    LINK FIELD CONNECTIONS                         |
+------------------------------------------------------------------+
|                                                                   |
|   UNIVERSITY ERP                      EDUCATION APP               |
|                                                                   |
|   +----------------------+            +------------------+        |
|   | Course Registration  |            |     Student      |        |
|   +----------------------+            +------------------+        |
|   | student ----------------Link----> | name (primary)   |        |
|   | academic_term ----------Link----> +------------------+        |
|   | program ----------------Link----> |                           |
|   +----------------------+            | Academic Term    |        |
|                                       +------------------+        |
|   +----------------------+            |                           |
|   | Teaching Assignment  |            |     Program      |        |
|   +----------------------+            +------------------+        |
|   | instructor -------------Link----> |                           |
|   | course -----------------Link----> |    Instructor    |        |
|   | student_group ----------Link----> +------------------+        |
|   +----------------------+            |                           |
|                                       |     Course       |        |
|   +----------------------+            +------------------+        |
|   | Hall Ticket          |            |                           |
|   +----------------------+            |   Student Group  |        |
|   | student ----------------Link----> +------------------+        |
|   | courses (child table with         |                           |
|   |   course links) -------Link----> |                           |
|   +----------------------+                                        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Detailed App-to-App Connections

### University ERP ↔ Education App

```
+------------------------------------------------------------------+
|              UNIVERSITY ERP ↔ EDUCATION CONNECTION                |
+------------------------------------------------------------------+
|                                                                   |
|  EDUCATION APP DOCTYPES USED:        UNIVERSITY ERP USAGE:        |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |     Student      | <------------> | Course Registration    |   |
|  |                  |                | Hall Ticket            |   |
|  |                  |                | Hostel Allocation      |   |
|  |                  |                | Library Member         |   |
|  |                  |                | Placement Application  |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |     Program      | <------------> | Admission Cycle        |   |
|  |                  |                | Seat Matrix            |   |
|  |                  |                | Merit List             |   |
|  |                  |                | Course Outcome (OBE)   |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |     Course       | <------------> | Course Registration    |   |
|  |                  |                | Teaching Assignment    |   |
|  |                  |                | LMS Course             |   |
|  |                  |                | Course Outcome         |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |      Fees        | <------------> | Scholarship            |   |
|  |                  |      GL        | Fee Payment            |   |
|  |                  | <---Posting--> | Payment Order          |   |
|  |                  |                | Bulk Fee Generator     |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |Assessment Result | <------------> | CO Attainment (OBE)    |   |
|  |                  |     Grading    | Student Transcript     |   |
|  |                  |                | CGPA Calculation       |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |Student Applicant | <------------> | Admission Cycle        |   |
|  |                  |     Convert    | Merit List             |   |
|  |                  | <---to Student | Seat Allocation        |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |   Instructor     | <------------> | Teaching Assignment    |   |
|  |                  |                | Exam Invigilator       |   |
|  |                  |                | (Links to Faculty)     |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |  Student Group   | <------------> | Teaching Assignment    |   |
|  |                  |                | Student Attendance     |   |
|  |                  |                | (Section management)   |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |  Academic Term   | <------------> | Course Registration    |   |
|  |                  |                | Teaching Assignment    |   |
|  |                  |                | Exam Schedule          |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |  Academic Year   | <------------> | Admission Cycle        |   |
|  |                  |                | Hostel Allocation      |   |
|  |                  |                | Transport Allocation   |   |
|  +------------------+                +------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

### University ERP ↔ HRMS App

```
+------------------------------------------------------------------+
|                UNIVERSITY ERP ↔ HRMS CONNECTION                   |
+------------------------------------------------------------------+
|                                                                   |
|  HRMS APP DOCTYPES:                  UNIVERSITY ERP USAGE:        |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |    Employee      | <------------> | Faculty Profile        |   |
|  |                  |     Sync       | (Auto-creates Employee)|   |
|  |                  | <------------> | Workload Calculation   |   |
|  |                  |                | Biometric Attendance   |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |Leave Application | <------------> | Leave Affected Course  |   |
|  |                  |     Hook       | Temporary Teaching     |   |
|  |                  | <---Events---> | Assignment             |   |
|  |                  |                | (Substitute faculty)   |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |   Attendance     | <------------> | Faculty Attendance     |   |
|  |                  |                | Biometric Sync         |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  | Salary Structure | <------------> | UGC Pay Scale          |   |
|  |                  |                | Faculty designation    |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |   Department     | <------------> | University Department  |   |
|  |                  |     Sync       | Faculty Profile        |   |
|  |                  | <---Events---> | Teaching Assignment    |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |    Appraisal     | <------------> | Faculty Performance    |   |
|  |                  |                | Evaluation             |   |
|  |                  |                | Student Feedback       |   |
|  +------------------+                +------------------------+   |
|                                                                   |
+------------------------------------------------------------------+

FACULTY PROFILE ↔ EMPLOYEE SYNC MECHANISM:

+-------------------+                    +-------------------+
|  Faculty Profile  |                    |     Employee      |
|  (University ERP) |                    |      (HRMS)       |
+-------------------+                    +-------------------+
| faculty_name      | ---------------→   | employee_name     |
| department        | ---------------→   | department        |
| designation       | ---------------→   | designation       |
| date_of_joining   | ---------------→   | date_of_joining   |
| status            | ---------------→   | status            |
| employee (link)   | ←--------------- | name (auto-linked)|
+-------------------+                    +-------------------+

Code Implementation:
```python
# On Faculty Profile creation
def on_insert(self):
    if not self.employee:
        employee = frappe.new_doc("Employee")
        employee.employee_name = self.faculty_name
        employee.department = self.department
        employee.designation = self.designation
        employee.company = get_university_company()
        employee.insert()
        self.employee = employee.name
```

---

### University ERP ↔ ERPNext App

```
+------------------------------------------------------------------+
|               UNIVERSITY ERP ↔ ERPNEXT CONNECTION                 |
+------------------------------------------------------------------+
|                                                                   |
|  ERPNEXT MODULES USED:               UNIVERSITY ERP USAGE:        |
|                                                                   |
|  ACCOUNTS MODULE                                                  |
|  +------------------+                +------------------------+   |
|  |    Company       | <------------> | University Settings    |   |
|  |                  |                | (Default company)      |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |    Account       | <------------> | Fee Category Account   |   |
|  |                  |                | University Accounts    |   |
|  |                  |                | Settings               |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |  Journal Entry   | <------------> | Fee GL Posting         |   |
|  |                  |     Auto       | Payment GL Entry       |   |
|  |                  | <--Created-->  | Refund Reversal        |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |    GL Entry      | <------------> | Fee submission creates |   |
|  |                  |                | GL entries via hook    |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |   Cost Center    | <------------> | Department-wise        |   |
|  |                  |                | accounting             |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  +------------------+                +------------------------+   |
|  |    Customer      | <------------> | Student as Customer    |   |
|  |                  |                | (for receivables)      |   |
|  +------------------+                +------------------------+   |
|                                                                   |
|  BLOCKED MODULES (Hidden from UI):                                |
|  +----------------------------------------------------------+   |
|  | Manufacturing | Stock | Selling | Buying | CRM           |   |
|  | Projects | Assets | Quality | Support                    |   |
|  +----------------------------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+

GL POSTING FLOW:

  Fee Submission                    ERPNext Accounts
  +-------------+                   +------------------+
  |   Fees      |                   |                  |
  |  (Submit)   |                   |                  |
  +-------------+                   |                  |
        |                           |                  |
        | on_submit hook            |                  |
        v                           |                  |
  +-------------+                   |                  |
  | University  |   make_gl_entries |  +------------+ |
  | ERP Hook    | ---------------→  |  | GL Entry   | |
  +-------------+                   |  +------------+ |
        |                           |  | Dr: AR     | |
        |                           |  | Cr: Income | |
        |                           |  +------------+ |
        |                           |                  |
        |                           +------------------+
```

---

## Data Flow Between Apps

### Student Lifecycle Flow

```
+------------------------------------------------------------------+
|                   STUDENT LIFECYCLE DATA FLOW                     |
+------------------------------------------------------------------+

1. ADMISSION PHASE
   +------------------+          +------------------+
   | Student Applicant|   --->   |     Student      |
   | (Education App)  |  convert | (Education App)  |
   +------------------+          +------------------+
           ↑                              |
           |                              |
   +------------------+                   |
   | Merit List       |                   |
   | (University ERP) |                   |
   +------------------+                   |
                                          |
2. ACADEMIC PHASE                         |
                                          v
   +------------------+          +------------------+
   | Course Reg.      |  <----   | Student (with    |
   | (University ERP) |          | custom fields)   |
   +------------------+          +------------------+
           |                              |
           v                              v
   +------------------+          +------------------+
   | Assessment Result|          | Student Group    |
   | (Education App)  |          | (Education App)  |
   +------------------+          +------------------+
           |
           v
3. EXAMINATION PHASE
   +------------------+          +------------------+
   | Hall Ticket      |  <----   | Course Reg.      |
   | (University ERP) |          | (eligibility)    |
   +------------------+          +------------------+
           |
           v
   +------------------+          +------------------+
   | Transcript       |  <----   | Assessment Result|
   | (University ERP) |          | (grades)         |
   +------------------+          +------------------+

4. GRADUATION PHASE
   +------------------+          +------------------+
   | University Alumni|  <----   |     Student      |
   | (University ERP) |  convert | (status=Graduated|
   +------------------+          +------------------+
```

### Fee Payment Flow

```
+------------------------------------------------------------------+
|                     FEE PAYMENT DATA FLOW                         |
+------------------------------------------------------------------+

+------------------+     +------------------+     +------------------+
|   Fee Schedule   |     |      Fees        |     |  Payment Order   |
| (Education App)  | --> | (Education App)  | --> | (University ERP) |
+------------------+     +------------------+     +------------------+
                                  |                       |
                                  |                       |
                    +-------------+                       |
                    |                                     |
                    v                                     v
           +------------------+                 +------------------+
           | University ERP   |                 | Payment Gateway  |
           | Fee Override     |                 | (Razorpay/PayU)  |
           | (on_submit hook) |                 +------------------+
           +------------------+                          |
                    |                                    |
                    v                                    v
           +------------------+                 +------------------+
           | ERPNext          |                 | Webhook Response |
           | make_gl_entries()|                 | (Success/Fail)   |
           +------------------+                 +------------------+
                    |                                    |
                    v                                    |
           +------------------+                          |
           |    GL Entry      |                          |
           | Dr: Receivable   | <------------------------+
           | Cr: Income       |     Update on payment
           +------------------+

GL Entry Details:
+------------------+------------------+------------------+
|     Account      |      Debit       |     Credit       |
+------------------+------------------+------------------+
| Student          | Fee Amount       |                  |
| Receivable       | (Rs. 50,000)     |                  |
+------------------+------------------+------------------+
| Fee Income       |                  | Fee Amount       |
| Account          |                  | (Rs. 50,000)     |
+------------------+------------------+------------------+

On Payment:
+------------------+------------------+------------------+
|     Account      |      Debit       |     Credit       |
+------------------+------------------+------------------+
| Bank Account     | Payment Amount   |                  |
|                  | (Rs. 50,000)     |                  |
+------------------+------------------+------------------+
| Student          |                  | Payment Amount   |
| Receivable       |                  | (Rs. 50,000)     |
+------------------+------------------+------------------+
```

### Faculty-Employee Sync Flow

```
+------------------------------------------------------------------+
|                   FACULTY-EMPLOYEE SYNC FLOW                      |
+------------------------------------------------------------------+

CREATE FLOW:
+------------------+          +------------------+
| Faculty Profile  |   Auto   |    Employee      |
| (Create)         | -------> |    (Created)     |
+------------------+          +------------------+
| faculty_name     |    →     | employee_name    |
| department       |    →     | department       |
| designation      |    →     | designation      |
| date_of_joining  |    →     | date_of_joining  |
+------------------+          +------------------+
        |                             |
        | employee = emp.name         |
        +-----------------------------+

UPDATE FLOW:
+------------------+          +------------------+
| Faculty Profile  |   Sync   |    Employee      |
| (Update)         | -------> |    (Updated)     |
+------------------+          +------------------+

LEAVE APPLICATION FLOW:
+------------------+          +------------------+
|    Employee      |          | Leave Application|
|                  | <------- |    (HRMS)        |
+------------------+          +------------------+
        |                             |
        | faculty lookup              | on_submit hook
        v                             v
+------------------+          +------------------+
| Faculty Profile  |          | Leave Affected   |
|                  |          | Course           |
+------------------+          | (University ERP) |
        |                     +------------------+
        |                             |
        v                             v
+------------------+          +------------------+
| Teaching         |          | Temporary        |
| Assignments      | -------> | Teaching         |
| (Get affected)   |          | Assignment       |
+------------------+          +------------------+
```

---

## API Integration Points

### Cross-App API Calls

```python
# ============================================================
# UNIVERSITY ERP CALLING EDUCATION APP
# ============================================================

# Get student data
from education.education.doctype.student.student import Student
student = frappe.get_doc("Student", student_id)

# Use Education's built-in method
from education.education.doctype.student_applicant.student_applicant import make_student
new_student = make_student(applicant_name)

# Get program courses
from education.education.doctype.program.program import get_program_courses
courses = get_program_courses(program_name)


# ============================================================
# UNIVERSITY ERP CALLING HRMS APP
# ============================================================

# Get employee
from hrms.hr.doctype.employee.employee import Employee
employee = frappe.get_doc("Employee", employee_id)

# Create leave application
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
leave = frappe.new_doc("Leave Application")

# Get salary structure
from hrms.payroll.doctype.salary_structure.salary_structure import SalaryStructure
structure = frappe.get_doc("Salary Structure", structure_name)


# ============================================================
# UNIVERSITY ERP CALLING ERPNEXT APP
# ============================================================

# Create GL entries
from erpnext.accounts.general_ledger import make_gl_entries
make_gl_entries(gl_entry_list)

# Reverse GL entries
from erpnext.accounts.general_ledger import make_reverse_gl_entries
make_reverse_gl_entries(voucher_type="Fees", voucher_no=doc.name)

# Get fiscal year
from erpnext.accounts.utils import get_fiscal_year
fiscal_year = get_fiscal_year(date)

# Get account balance
from erpnext.accounts.utils import get_balance_on
balance = get_balance_on(account, date)
```

---

## Configuration Requirements

### University Accounts Settings

```python
# Required ERPNext setup for GL integration

University Accounts Settings:
+---------------------------+--------------------------------+
| Field                     | Value/Link                     |
+---------------------------+--------------------------------+
| company                   | → ERPNext Company              |
| student_receivable_account| → ERPNext Account (Receivable) |
| default_income_account    | → ERPNext Account (Income)     |
| bank_account              | → ERPNext Account (Bank)       |
| default_cost_center       | → ERPNext Cost Center          |
+---------------------------+--------------------------------+
```

### Fee Category Account Mapping

```python
# Map each fee type to specific GL accounts

Fee Category Account:
+------------------+----------------------+----------------------+
| Fee Category     | Income Account       | Cost Center          |
+------------------+----------------------+----------------------+
| Tuition Fee      | Fee Income - Tuition | Department CC        |
| Hostel Fee       | Fee Income - Hostel  | Hostel CC            |
| Transport Fee    | Fee Income - Transport| Transport CC        |
| Library Fee      | Fee Income - Library | Library CC           |
| Examination Fee  | Fee Income - Exam    | Exam Cell CC         |
+------------------+----------------------+----------------------+
```

---

## Blocked Modules Configuration

```python
# hooks.py - Hide irrelevant ERPNext modules

block_modules = [
    "Manufacturing",    # Not needed for university
    "Stock",           # No inventory management
    "Selling",         # No sales
    "Buying",          # Simplified procurement
    "CRM",             # No CRM needed
    "Projects",        # Use custom research module
    "Assets",          # Simplified asset tracking
    "Quality",         # Not applicable
    "Support",         # Use custom grievance module
]
```

---

## Summary: Integration Mechanisms

| Mechanism | Purpose | Apps Involved |
|-----------|---------|---------------|
| **Override Classes** | Extend DocType behavior | Education → University ERP |
| **Doc Events** | React to document lifecycle | All apps → University ERP |
| **Custom Fields** | Add fields to existing DocTypes | University ERP → All apps |
| **Link Fields** | Reference across apps | All apps bidirectional |
| **API Calls** | Direct function invocation | University ERP → All apps |
| **GL Integration** | Financial posting | University ERP → ERPNext |
| **Employee Sync** | HR data synchronization | University ERP ↔ HRMS |
| **Webhooks** | External service callbacks | External → University ERP |

---

## Troubleshooting Common Issues

### 1. Override Not Working
```python
# Ensure correct class path in hooks.py
# Clear cache after changes
bench --site [site] clear-cache
bench --site [site] migrate
```

### 2. GL Entry Errors
```python
# Verify account setup
# Check cost center exists
# Ensure company is set
frappe.get_single("University Accounts Settings")
```

### 3. Custom Field Not Appearing
```python
# Rebuild fixtures
bench --site [site] migrate
bench --site [site] clear-cache
```

### 4. Doc Event Not Triggering
```python
# Check hooks.py syntax
# Verify function path exists
# Check for errors in function
```

---

## See Also

- [System Overview](00_SYSTEM_OVERVIEW.md)
- [Architecture Overview](../01_architecture_overview.md)
- [Module Mapping](../03_module_mapping.md)
- [Education Deep Dive](../04_education_deep_dive.md)
- [HRMS Deep Dive](../05_hrms_deep_dive.md)

# University ERP - HRMS Deep Dive (Faculty-Centric)

## Overview

This document details the faculty-centric HRMS implementation that uses ERPNext HRMS as a hidden backend engine while presenting a university-specific HR experience.

---

## Faculty vs Staff Modeling

### Employee Categories
```
University Employees
├── Teaching Staff (Faculty)
│   ├── Professor
│   ├── Associate Professor
│   ├── Assistant Professor
│   ├── Lecturer
│   ├── Visiting Faculty
│   └── Guest Lecturer
│
└── Non-Teaching Staff
    ├── Administrative Staff
    │   ├── Registrar
    │   ├── Administrative Officer
    │   ├── Office Assistant
    │   └── Data Entry Operator
    ├── Technical Staff
    │   ├── Lab Technician
    │   ├── IT Support
    │   └── Workshop Instructor
    ├── Library Staff
    │   ├── Librarian
    │   └── Library Assistant
    └── Support Staff
        ├── Security
        ├── Housekeeping
        └── Maintenance
```

### DocType: University Faculty
```json
{
    "doctype": "DocType",
    "name": "University Faculty",
    "module": "University ERP",
    "fields": [
        {"fieldname": "basic_info", "fieldtype": "Section Break", "label": "Basic Information"},
        {"fieldname": "faculty_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "employee_id", "fieldtype": "Data", "unique": 1},
        {"fieldname": "employee", "fieldtype": "Link", "options": "Employee", "hidden": 1},
        {"fieldname": "user", "fieldtype": "Link", "options": "User"},
        {"fieldname": "gender", "fieldtype": "Select", "options": "Male\nFemale\nOther"},
        {"fieldname": "date_of_birth", "fieldtype": "Date"},
        {"fieldname": "image", "fieldtype": "Attach Image"},

        {"fieldname": "employment_details", "fieldtype": "Section Break"},
        {"fieldname": "department", "fieldtype": "Link", "options": "University Department", "reqd": 1},
        {"fieldname": "designation", "fieldtype": "Select",
         "options": "Professor\nAssociate Professor\nAssistant Professor\nLecturer\nVisiting Faculty\nGuest Lecturer"},
        {"fieldname": "employee_type", "fieldtype": "Select",
         "options": "Permanent\nContract\nVisiting\nAdhoc\nDeputation"},
        {"fieldname": "date_of_joining", "fieldtype": "Date"},
        {"fieldname": "probation_end_date", "fieldtype": "Date"},
        {"fieldname": "confirmation_date", "fieldtype": "Date"},
        {"fieldname": "retirement_date", "fieldtype": "Date", "read_only": 1},
        {"fieldname": "status", "fieldtype": "Select",
         "options": "Active\nOn Leave\nSabbatical\nDeputed\nResigned\nRetired\nTerminated"},

        {"fieldname": "qualifications", "fieldtype": "Section Break"},
        {"fieldname": "highest_qualification", "fieldtype": "Select",
         "options": "PhD\nM.Phil\nPostgraduate\nGraduate"},
        {"fieldname": "specialization", "fieldtype": "Data"},
        {"fieldname": "research_areas", "fieldtype": "Small Text"},
        {"fieldname": "qualification_details", "fieldtype": "Table", "options": "Faculty Qualification"},

        {"fieldname": "experience", "fieldtype": "Section Break"},
        {"fieldname": "total_experience_years", "fieldtype": "Float"},
        {"fieldname": "teaching_experience_years", "fieldtype": "Float"},
        {"fieldname": "industry_experience_years", "fieldtype": "Float"},
        {"fieldname": "experience_history", "fieldtype": "Table", "options": "Faculty Experience"},

        {"fieldname": "workload", "fieldtype": "Section Break"},
        {"fieldname": "max_weekly_hours", "fieldtype": "Int", "default": 16},
        {"fieldname": "current_workload", "fieldtype": "Float", "read_only": 1},
        {"fieldname": "workload_status", "fieldtype": "Select",
         "options": "Under-loaded\nOptimal\nOver-loaded", "read_only": 1},

        {"fieldname": "research_metrics", "fieldtype": "Section Break"},
        {"fieldname": "h_index", "fieldtype": "Int"},
        {"fieldname": "total_publications", "fieldtype": "Int", "read_only": 1},
        {"fieldname": "total_citations", "fieldtype": "Int", "read_only": 1},
        {"fieldname": "funded_projects", "fieldtype": "Int", "read_only": 1},

        {"fieldname": "contact", "fieldtype": "Section Break"},
        {"fieldname": "email", "fieldtype": "Data", "options": "Email"},
        {"fieldname": "personal_email", "fieldtype": "Data", "options": "Email"},
        {"fieldname": "mobile", "fieldtype": "Data", "options": "Phone"},
        {"fieldname": "office_phone", "fieldtype": "Data"},
        {"fieldname": "office_location", "fieldtype": "Data"},

        {"fieldname": "bank_details", "fieldtype": "Section Break"},
        {"fieldname": "bank_name", "fieldtype": "Data"},
        {"fieldname": "bank_account_no", "fieldtype": "Data"},
        {"fieldname": "ifsc_code", "fieldtype": "Data"},
        {"fieldname": "pan", "fieldtype": "Data"}
    ],
    "autoname": "naming_series:FAC-.YYYY.-"
}
```

### DocType: University Staff
```json
{
    "doctype": "DocType",
    "name": "University Staff",
    "module": "University ERP",
    "fields": [
        {"fieldname": "staff_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "employee_id", "fieldtype": "Data", "unique": 1},
        {"fieldname": "employee", "fieldtype": "Link", "options": "Employee", "hidden": 1},
        {"fieldname": "department", "fieldtype": "Link", "options": "University Department"},
        {"fieldname": "staff_category", "fieldtype": "Select",
         "options": "Administrative\nTechnical\nLibrary\nSupport"},
        {"fieldname": "designation", "fieldtype": "Data"},
        {"fieldname": "employee_type", "fieldtype": "Select",
         "options": "Permanent\nContract\nTemporary\nOutsourced"},
        {"fieldname": "date_of_joining", "fieldtype": "Date"},
        {"fieldname": "status", "fieldtype": "Select",
         "options": "Active\nOn Leave\nResigned\nRetired\nTerminated"},
        {"fieldname": "email", "fieldtype": "Data", "options": "Email"},
        {"fieldname": "mobile", "fieldtype": "Data", "options": "Phone"},
        {"fieldname": "qualifications", "fieldtype": "Table", "options": "Staff Qualification"}
    ],
    "autoname": "naming_series:STF-.YYYY.-"
}
```

---

## Teaching Workload as First-Class Data

### Workload Components
```python
# university_erp/university_hr/workload_components.py

WORKLOAD_COMPONENTS = {
    "teaching": {
        "lecture": {"multiplier": 1.0, "unit": "hour"},
        "tutorial": {"multiplier": 0.5, "unit": "hour"},
        "practical": {"multiplier": 0.75, "unit": "hour"},
    },
    "non_teaching": {
        "exam_duty": {"multiplier": 0.5, "unit": "session"},
        "paper_setting": {"multiplier": 2.0, "unit": "paper"},
        "paper_evaluation": {"multiplier": 0.1, "unit": "paper"},
        "project_guidance": {"multiplier": 1.0, "unit": "student"},
        "phd_supervision": {"multiplier": 2.0, "unit": "student"},
        "administrative": {"multiplier": 1.0, "unit": "hour"},
    }
}

DESIGNATION_LIMITS = {
    "Professor": {
        "min_teaching": 8, "max_teaching": 12,
        "phd_students_max": 8, "pg_projects_max": 6
    },
    "Associate Professor": {
        "min_teaching": 10, "max_teaching": 14,
        "phd_students_max": 6, "pg_projects_max": 8
    },
    "Assistant Professor": {
        "min_teaching": 12, "max_teaching": 16,
        "phd_students_max": 4, "pg_projects_max": 10
    },
    "Lecturer": {
        "min_teaching": 14, "max_teaching": 18,
        "phd_students_max": 0, "pg_projects_max": 4
    },
}
```

### Workload Calculation Engine
```python
# university_erp/university_hr/workload_engine.py

import frappe
from frappe.utils import flt

class WorkloadEngine:
    """Calculate and validate faculty workload"""

    def __init__(self, faculty, semester=None):
        self.faculty = frappe.get_doc("University Faculty", faculty)
        self.semester = semester or self.get_current_semester()

    def calculate_total_workload(self):
        """Calculate total workload from all sources"""
        teaching = self.get_teaching_workload()
        guidance = self.get_guidance_workload()
        administrative = self.get_administrative_workload()

        total = teaching["total"] + guidance["total"] + administrative["total"]

        return {
            "teaching": teaching,
            "guidance": guidance,
            "administrative": administrative,
            "total_hours": total,
            "max_allowed": self.faculty.max_weekly_hours,
            "status": self.get_status(total)
        }

    def get_teaching_workload(self):
        """Get teaching workload from assignments"""
        assignments = frappe.get_all(
            "Teaching Assignment",
            filters={"faculty": self.faculty.name, "academic_semester": self.semester},
            fields=["course", "weekly_hours", "assignment_type"]
        )

        breakdown = {}
        total = 0

        for a in assignments:
            multiplier = WORKLOAD_COMPONENTS["teaching"].get(
                a.assignment_type.lower(), {"multiplier": 1.0}
            )["multiplier"]

            effective_hours = a.weekly_hours * multiplier
            breakdown[a.course] = {
                "type": a.assignment_type,
                "scheduled_hours": a.weekly_hours,
                "effective_hours": effective_hours
            }
            total += effective_hours

        return {"breakdown": breakdown, "total": total}

    def get_guidance_workload(self):
        """Get project/thesis guidance workload"""
        phd_students = frappe.db.count(
            "Research Scholar",
            {"supervisor": self.faculty.name, "status": "Active"}
        )

        pg_projects = frappe.db.count(
            "Project Guidance",
            {"guide": self.faculty.name, "academic_semester": self.semester}
        )

        return {
            "phd_students": phd_students,
            "pg_projects": pg_projects,
            "total": (phd_students * 2) + (pg_projects * 1)  # Hours per week equivalent
        }

    def get_administrative_workload(self):
        """Get administrative duties workload"""
        duties = frappe.get_all(
            "Administrative Duty",
            filters={"faculty": self.faculty.name, "status": "Active"},
            fields=["duty_type", "hours_per_week"]
        )

        total = sum(d.hours_per_week for d in duties)

        return {"duties": duties, "total": total}

    def get_status(self, total_hours):
        """Determine workload status"""
        limits = DESIGNATION_LIMITS.get(self.faculty.designation, {})
        min_hours = limits.get("min_teaching", 12)
        max_hours = limits.get("max_teaching", 16)

        if total_hours < min_hours:
            return "Under-loaded"
        elif total_hours > max_hours:
            return "Over-loaded"
        return "Optimal"

    def validate_new_assignment(self, course, hours, assignment_type):
        """Validate if new assignment can be added"""
        current = self.calculate_total_workload()
        new_total = current["total_hours"] + hours

        limits = DESIGNATION_LIMITS.get(self.faculty.designation, {})
        max_hours = limits.get("max_teaching", 16)

        if new_total > max_hours:
            return {
                "valid": False,
                "message": f"Assignment would exceed max workload ({max_hours} hrs). Current: {current['total_hours']:.1f} hrs"
            }

        return {"valid": True}
```

### Workload Report
```python
# university_erp/university_hr/report/faculty_workload_report.py

import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "faculty", "label": "Faculty", "fieldtype": "Link", "options": "University Faculty", "width": 200},
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 120},
        {"fieldname": "teaching_hours", "label": "Teaching Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "guidance_hours", "label": "Guidance Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "admin_hours", "label": "Admin Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "total_hours", "label": "Total Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "max_hours", "label": "Max Allowed", "fieldtype": "Float", "width": 100},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
    ]

    data = []
    faculty_list = frappe.get_all(
        "University Faculty",
        filters={"status": "Active"},
        fields=["name", "faculty_name", "department", "designation", "max_weekly_hours"]
    )

    for faculty in faculty_list:
        engine = WorkloadEngine(faculty.name, filters.get("semester"))
        workload = engine.calculate_total_workload()

        data.append({
            "faculty": faculty.name,
            "department": faculty.department,
            "designation": faculty.designation,
            "teaching_hours": workload["teaching"]["total"],
            "guidance_hours": workload["guidance"]["total"],
            "admin_hours": workload["administrative"]["total"],
            "total_hours": workload["total_hours"],
            "max_hours": faculty.max_weekly_hours,
            "status": workload["status"]
        })

    return columns, data
```

---

## Payroll Integration with ERPNext HRMS

### Salary Structure Setup
```python
# university_erp/university_hr/salary_setup.py

import frappe

def setup_university_salary_components():
    """Setup university-specific salary components"""

    components = [
        # Earnings
        {"name": "Basic Salary", "type": "Earning", "is_tax_applicable": 1},
        {"name": "Dearness Allowance", "type": "Earning", "depends_on_payment_days": 1},
        {"name": "House Rent Allowance", "type": "Earning", "is_tax_applicable": 1},
        {"name": "Academic Allowance", "type": "Earning", "description": "For PhD holders"},
        {"name": "Research Incentive", "type": "Earning", "is_flexible_benefit": 1},
        {"name": "Administrative Allowance", "type": "Earning", "description": "For HOD/Dean"},
        {"name": "Exam Duty Allowance", "type": "Earning", "is_flexible_benefit": 1},
        {"name": "Paper Evaluation Allowance", "type": "Earning"},
        {"name": "Medical Allowance", "type": "Earning"},
        {"name": "Conveyance Allowance", "type": "Earning"},

        # Deductions
        {"name": "Provident Fund", "type": "Deduction", "is_tax_applicable": 0},
        {"name": "Professional Tax", "type": "Deduction"},
        {"name": "Income Tax", "type": "Deduction"},
        {"name": "NPS Contribution", "type": "Deduction", "description": "National Pension Scheme"},
        {"name": "LIC Deduction", "type": "Deduction"},
        {"name": "Loan Recovery", "type": "Deduction"},
    ]

    for comp in components:
        if not frappe.db.exists("Salary Component", comp["name"]):
            doc = frappe.new_doc("Salary Component")
            doc.salary_component = comp["name"]
            doc.salary_component_abbr = comp["name"][:4].upper()
            doc.type = comp["type"]
            doc.is_tax_applicable = comp.get("is_tax_applicable", 0)
            doc.depends_on_payment_days = comp.get("depends_on_payment_days", 0)
            doc.description = comp.get("description", "")
            doc.insert()

def create_salary_structure(designation, components):
    """Create salary structure for designation"""
    structure_name = f"University - {designation}"

    if frappe.db.exists("Salary Structure", structure_name):
        return

    ss = frappe.new_doc("Salary Structure")
    ss.name = structure_name
    ss.docstatus = 1
    ss.is_active = "Yes"
    ss.company = frappe.get_single("University Settings").company
    ss.payroll_frequency = "Monthly"

    for comp in components:
        if comp["type"] == "Earning":
            ss.append("earnings", {
                "salary_component": comp["component"],
                "amount_based_on_formula": 1 if comp.get("formula") else 0,
                "formula": comp.get("formula", ""),
                "amount": comp.get("amount", 0)
            })
        else:
            ss.append("deductions", {
                "salary_component": comp["component"],
                "amount_based_on_formula": 1 if comp.get("formula") else 0,
                "formula": comp.get("formula", ""),
                "amount": comp.get("amount", 0)
            })

    ss.insert()
    return ss.name
```

### University Payroll Entry
```python
# university_erp/university_hr/university_payroll.py

import frappe
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry

class UniversityPayrollEntry:
    """University-specific payroll processing wrapper"""

    def __init__(self, posting_date, department=None):
        self.posting_date = posting_date
        self.department = department
        self.company = frappe.get_single("University Settings").company

    def get_eligible_employees(self):
        """Get eligible employees (faculty + staff)"""
        filters = {"status": "Active"}
        if self.department:
            filters["department"] = self.department

        # Get faculty employees
        faculty_list = frappe.get_all(
            "University Faculty",
            filters=filters,
            fields=["employee", "faculty_name", "designation"]
        )

        # Get staff employees
        staff_list = frappe.get_all(
            "University Staff",
            filters={"status": "Active"},
            fields=["employee", "staff_name", "designation"]
        )

        employees = []
        for f in faculty_list:
            if f.employee:
                employees.append({
                    "employee": f.employee,
                    "name": f.faculty_name,
                    "type": "Faculty"
                })

        for s in staff_list:
            if s.employee:
                employees.append({
                    "employee": s.employee,
                    "name": s.staff_name,
                    "type": "Staff"
                })

        return employees

    def process_payroll(self):
        """Process payroll using HRMS engine"""
        employees = self.get_eligible_employees()

        if not employees:
            frappe.throw("No eligible employees found for payroll")

        # Create HRMS Payroll Entry (hidden from UI)
        payroll_entry = frappe.new_doc("Payroll Entry")
        payroll_entry.company = self.company
        payroll_entry.posting_date = self.posting_date
        payroll_entry.payroll_frequency = "Monthly"

        for emp in employees:
            payroll_entry.append("employees", {"employee": emp["employee"]})

        payroll_entry.flags.ignore_permissions = True
        payroll_entry.insert()

        # Create salary slips
        payroll_entry.create_salary_slips()

        # Create University Payroll Entry for tracking
        uni_payroll = frappe.new_doc("University Payroll Entry")
        uni_payroll.posting_date = self.posting_date
        uni_payroll.department = self.department
        uni_payroll.payroll_entry = payroll_entry.name
        uni_payroll.total_employees = len(employees)
        uni_payroll.status = "Draft"
        uni_payroll.insert()

        return uni_payroll.name

    def submit_payroll(self, university_payroll_entry):
        """Submit salary slips"""
        doc = frappe.get_doc("University Payroll Entry", university_payroll_entry)
        payroll_entry = frappe.get_doc("Payroll Entry", doc.payroll_entry)

        payroll_entry.submit_salary_slips()
        doc.status = "Submitted"
        doc.save()

    def create_payment_entry(self, university_payroll_entry):
        """Create bank payment entry"""
        doc = frappe.get_doc("University Payroll Entry", university_payroll_entry)
        payroll_entry = frappe.get_doc("Payroll Entry", doc.payroll_entry)

        payroll_entry.make_payment_entry()
        doc.status = "Paid"
        doc.save()
```

### Leave Management
```python
# university_erp/university_hr/leave.py

import frappe

LEAVE_TYPES = {
    "faculty": [
        {"name": "Casual Leave", "max_days": 12, "is_carry_forward": 0},
        {"name": "Earned Leave", "max_days": 30, "is_carry_forward": 1, "max_carry_forward": 300},
        {"name": "Medical Leave", "max_days": 20, "is_carry_forward": 0},
        {"name": "Maternity Leave", "max_days": 180, "is_carry_forward": 0, "applicable_for": "Female"},
        {"name": "Paternity Leave", "max_days": 15, "is_carry_forward": 0, "applicable_for": "Male"},
        {"name": "Study Leave", "max_days": 730, "is_carry_forward": 0, "description": "For PhD/higher studies"},
        {"name": "Sabbatical Leave", "max_days": 365, "is_carry_forward": 0, "description": "After 6 years service"},
        {"name": "Duty Leave", "max_days": 30, "is_carry_forward": 0, "description": "For conferences/workshops"},
        {"name": "Extraordinary Leave", "max_days": 365, "is_carry_forward": 0, "is_lwp": 1},
    ],
    "staff": [
        {"name": "Casual Leave", "max_days": 12, "is_carry_forward": 0},
        {"name": "Earned Leave", "max_days": 30, "is_carry_forward": 1},
        {"name": "Medical Leave", "max_days": 20, "is_carry_forward": 0},
        {"name": "Maternity Leave", "max_days": 180, "is_carry_forward": 0, "applicable_for": "Female"},
        {"name": "Paternity Leave", "max_days": 15, "is_carry_forward": 0, "applicable_for": "Male"},
    ]
}

class UniversityLeaveApplication:
    """University leave application wrapper"""

    def __init__(self, employee_type, employee_id):
        self.employee_type = employee_type
        self.employee_id = employee_id

        if employee_type == "Faculty":
            self.employee = frappe.db.get_value("University Faculty", employee_id, "employee")
        else:
            self.employee = frappe.db.get_value("University Staff", employee_id, "employee")

    def apply_leave(self, leave_type, from_date, to_date, reason):
        """Create leave application using HRMS"""
        leave_app = frappe.new_doc("Leave Application")
        leave_app.employee = self.employee
        leave_app.leave_type = leave_type
        leave_app.from_date = from_date
        leave_app.to_date = to_date
        leave_app.description = reason
        leave_app.status = "Open"
        leave_app.flags.ignore_permissions = True
        leave_app.insert()

        # Create university leave record for tracking
        uni_leave = frappe.new_doc("University Leave Application")
        uni_leave.employee_type = self.employee_type
        uni_leave.employee_id = self.employee_id
        uni_leave.leave_application = leave_app.name
        uni_leave.leave_type = leave_type
        uni_leave.from_date = from_date
        uni_leave.to_date = to_date
        uni_leave.status = "Pending"
        uni_leave.insert()

        return uni_leave.name

    def get_leave_balance(self, leave_type):
        """Get leave balance from HRMS"""
        from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on

        return get_leave_balance_on(
            self.employee,
            leave_type,
            frappe.utils.today()
        )
```

---

## Faculty Appraisal System

### Appraisal Components
```python
# university_erp/university_hr/appraisal.py

APPRAISAL_CRITERIA = {
    "teaching": {
        "weight": 40,
        "components": [
            {"name": "Student Feedback Score", "max_score": 100, "weight": 40},
            {"name": "Course Completion", "max_score": 100, "weight": 20},
            {"name": "Teaching Innovation", "max_score": 100, "weight": 20},
            {"name": "Curriculum Development", "max_score": 100, "weight": 20},
        ]
    },
    "research": {
        "weight": 30,
        "components": [
            {"name": "Journal Publications", "max_score": 100, "weight": 40},
            {"name": "Conference Papers", "max_score": 100, "weight": 20},
            {"name": "Funded Projects", "max_score": 100, "weight": 25},
            {"name": "Patents/Books", "max_score": 100, "weight": 15},
        ]
    },
    "academic_contribution": {
        "weight": 20,
        "components": [
            {"name": "PhD/PG Guidance", "max_score": 100, "weight": 40},
            {"name": "Committee Participation", "max_score": 100, "weight": 30},
            {"name": "Industry Collaboration", "max_score": 100, "weight": 30},
        ]
    },
    "administrative": {
        "weight": 10,
        "components": [
            {"name": "Administrative Duties", "max_score": 100, "weight": 50},
            {"name": "Event Organization", "max_score": 100, "weight": 30},
            {"name": "Student Mentoring", "max_score": 100, "weight": 20},
        ]
    }
}
```

### Faculty Appraisal DocType
```json
{
    "doctype": "DocType",
    "name": "Faculty Appraisal",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "faculty", "fieldtype": "Link", "options": "University Faculty", "reqd": 1},
        {"fieldname": "appraisal_period", "fieldtype": "Link", "options": "Appraisal Period"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year"},
        {"fieldname": "department", "fieldtype": "Link", "options": "University Department"},
        {"fieldname": "reviewer", "fieldtype": "Link", "options": "University Faculty", "label": "Reviewed By"},

        {"fieldname": "teaching_section", "fieldtype": "Section Break", "label": "Teaching (40%)"},
        {"fieldname": "teaching_scores", "fieldtype": "Table", "options": "Appraisal Score"},
        {"fieldname": "teaching_score", "fieldtype": "Float", "read_only": 1},

        {"fieldname": "research_section", "fieldtype": "Section Break", "label": "Research (30%)"},
        {"fieldname": "research_scores", "fieldtype": "Table", "options": "Appraisal Score"},
        {"fieldname": "research_score", "fieldtype": "Float", "read_only": 1},

        {"fieldname": "academic_section", "fieldtype": "Section Break", "label": "Academic Contribution (20%)"},
        {"fieldname": "academic_scores", "fieldtype": "Table", "options": "Appraisal Score"},
        {"fieldname": "academic_score", "fieldtype": "Float", "read_only": 1},

        {"fieldname": "admin_section", "fieldtype": "Section Break", "label": "Administrative (10%)"},
        {"fieldname": "admin_scores", "fieldtype": "Table", "options": "Appraisal Score"},
        {"fieldname": "admin_score", "fieldtype": "Float", "read_only": 1},

        {"fieldname": "summary_section", "fieldtype": "Section Break"},
        {"fieldname": "total_score", "fieldtype": "Float", "read_only": 1},
        {"fieldname": "grade", "fieldtype": "Select", "options": "Outstanding\nExcellent\nGood\nSatisfactory\nNeeds Improvement", "read_only": 1},
        {"fieldname": "recommendations", "fieldtype": "Text"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nPending Review\nReviewed\nApproved"}
    ]
}
```

### Publications Management
```json
{
    "doctype": "DocType",
    "name": "Faculty Publication",
    "fields": [
        {"fieldname": "faculty", "fieldtype": "Link", "options": "University Faculty", "reqd": 1},
        {"fieldname": "title", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "publication_type", "fieldtype": "Select",
         "options": "Journal Article\nConference Paper\nBook\nBook Chapter\nPatent\nTechnical Report"},
        {"fieldname": "authors", "fieldtype": "Small Text"},
        {"fieldname": "journal_name", "fieldtype": "Data"},
        {"fieldname": "publisher", "fieldtype": "Data"},
        {"fieldname": "publication_date", "fieldtype": "Date"},
        {"fieldname": "volume", "fieldtype": "Data"},
        {"fieldname": "issue", "fieldtype": "Data"},
        {"fieldname": "pages", "fieldtype": "Data"},
        {"fieldname": "doi", "fieldtype": "Data"},
        {"fieldname": "issn_isbn", "fieldtype": "Data"},
        {"fieldname": "indexing", "fieldtype": "Select",
         "options": "SCI\nSCIE\nScopus\nWeb of Science\nUGC Listed\nOther"},
        {"fieldname": "impact_factor", "fieldtype": "Float"},
        {"fieldname": "citations", "fieldtype": "Int"},
        {"fieldname": "abstract", "fieldtype": "Text"},
        {"fieldname": "document", "fieldtype": "Attach"}
    ]
}
```

---

## University-Specific HR Workspace

### HR Workspace Configuration
```json
{
    "doctype": "Workspace",
    "name": "University HR",
    "module": "University ERP",
    "label": "Human Resources",
    "icon": "users",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University HR Admin"}
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Faculty Management"
        },
        {"type": "Link", "label": "Faculty", "link_to": "University Faculty", "link_type": "DocType"},
        {"type": "Link", "label": "Staff", "link_to": "University Staff", "link_type": "DocType"},
        {"type": "Link", "label": "Department", "link_to": "University Department", "link_type": "DocType"},

        {
            "type": "Card Break",
            "label": "Workload & Assignments"
        },
        {"type": "Link", "label": "Teaching Assignment", "link_to": "Teaching Assignment", "link_type": "DocType"},
        {"type": "Link", "label": "Administrative Duty", "link_to": "Administrative Duty", "link_type": "DocType"},
        {"type": "Link", "label": "Workload Report", "link_to": "Faculty Workload Report", "link_type": "Report"},

        {
            "type": "Card Break",
            "label": "Leave & Attendance"
        },
        {"type": "Link", "label": "Leave Application", "link_to": "University Leave Application", "link_type": "DocType"},
        {"type": "Link", "label": "Attendance", "link_to": "Faculty Attendance", "link_type": "DocType"},
        {"type": "Link", "label": "Leave Balance Report", "link_to": "Leave Balance Report", "link_type": "Report"},

        {
            "type": "Card Break",
            "label": "Payroll"
        },
        {"type": "Link", "label": "Process Payroll", "link_to": "University Payroll Entry", "link_type": "DocType"},
        {"type": "Link", "label": "Salary Structure", "link_to": "University Salary Structure", "link_type": "DocType"},
        {"type": "Link", "label": "Payroll Report", "link_to": "Payroll Summary Report", "link_type": "Report"},

        {
            "type": "Card Break",
            "label": "Performance & Research"
        },
        {"type": "Link", "label": "Faculty Appraisal", "link_to": "Faculty Appraisal", "link_type": "DocType"},
        {"type": "Link", "label": "Publications", "link_to": "Faculty Publication", "link_type": "DocType"},
        {"type": "Link", "label": "Research Projects", "link_to": "Research Project", "link_type": "DocType"}
    ]
}
```

---

## Next Document

Continue to [06_security_permissions.md](06_security_permissions.md) for the security model and permission configuration.

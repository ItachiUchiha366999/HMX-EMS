# Phase 6: HR & Faculty Management Module

## Overview

This phase implements comprehensive HR and Faculty management by leveraging ERPNext HRMS as the backend while providing education-specific extensions through the university_erp app. The module covers employee management, faculty workload tracking, leave management, payroll integration, and academic performance evaluation.

**Duration:** 4-5 weeks
**Priority:** High
**Dependencies:** Phase 1 (Foundation), Phase 5 (Fees & Finance for GL accounts)

---

## Prerequisites

### Completed Phases
- [ ] Phase 1: Foundation & Core Setup
- [ ] Phase 5: Fees & Finance (GL accounts and cost centers)
- [ ] Phase 3: Academics (Optional - for workload calculation)

### Technical Requirements
- ERPNext HRMS app installed and configured
- Company setup with departments
- Cost centers for each department
- Payroll period and salary structure templates
- Leave types and holiday list configured

### Knowledge Requirements
- ERPNext HRMS module (Employee, Payroll, Leave)
- Frappe workflow and permission system
- Double-entry accounting for payroll

### Infrastructure Requirements
- HRMS module enabled
- Bank integration for salary disbursement (optional)
- Email gateway for HR notifications

---

## Architecture: HRMS as Hidden Backend

```
┌─────────────────────────────────────────────────────────────────┐
│                     University ERP Frontend                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Faculty   │  │   Workload  │  │   Academic Performance  │  │
│  │   Portal    │  │   Tracker   │  │      Evaluation         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              University ERP Extension Layer                      │
│  ┌─────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │ Faculty Profile │  │ Teaching       │  │ Faculty Leave   │   │
│  │ (Custom DocType)│  │ Assignment     │  │ Extension       │   │
│  └─────────────────┘  └────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ERPNext HRMS Backend                          │
│  ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Employee │  │ Salary Slip │  │ Leave    │  │ Attendance   │  │
│  │          │  │             │  │ Applic.  │  │              │  │
│  └──────────┘  └─────────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Week-by-Week Deliverables

### Week 1: Employee Extension & Faculty Profile

#### Tasks

**1.1 Custom Fields for Employee**
```json
// fixtures/custom_field/employee_custom_fields.json
[
    {
        "dt": "Employee",
        "fieldname": "custom_employee_type_section",
        "fieldtype": "Section Break",
        "label": "University Details",
        "insert_after": "company_email"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_employee_category",
        "fieldtype": "Select",
        "label": "Employee Category",
        "options": "Teaching\nNon-Teaching\nAdministrative\nTechnical\nContractual",
        "insert_after": "custom_employee_type_section",
        "reqd": 1
    },
    {
        "dt": "Employee",
        "fieldname": "custom_designation_category",
        "fieldtype": "Select",
        "label": "Designation Category",
        "options": "Professor\nAssociate Professor\nAssistant Professor\nLecturer\nVisiting Faculty\nLab Assistant\nAdministrative Staff",
        "insert_after": "custom_employee_category",
        "depends_on": "eval:doc.custom_employee_category=='Teaching'"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_academic_department",
        "fieldtype": "Link",
        "label": "Academic Department",
        "options": "Department",
        "insert_after": "custom_designation_category"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_column_break_univ",
        "fieldtype": "Column Break",
        "insert_after": "custom_academic_department"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_faculty_profile",
        "fieldtype": "Link",
        "label": "Faculty Profile",
        "options": "Faculty Profile",
        "insert_after": "custom_column_break_univ",
        "read_only": 1
    },
    {
        "dt": "Employee",
        "fieldname": "custom_ugc_pay_scale",
        "fieldtype": "Link",
        "label": "UGC Pay Scale",
        "options": "UGC Pay Scale",
        "insert_after": "custom_faculty_profile",
        "depends_on": "eval:doc.custom_employee_category=='Teaching'"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_qualification_section",
        "fieldtype": "Section Break",
        "label": "Academic Qualifications",
        "insert_after": "custom_ugc_pay_scale"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_highest_qualification",
        "fieldtype": "Select",
        "label": "Highest Qualification",
        "options": "Ph.D.\nM.Phil.\nPost Graduate\nGraduate\nDiploma",
        "insert_after": "custom_qualification_section"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_specialization",
        "fieldtype": "Data",
        "label": "Specialization",
        "insert_after": "custom_highest_qualification"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_qualifications",
        "fieldtype": "Table",
        "label": "Qualifications",
        "options": "Employee Qualification",
        "insert_after": "custom_specialization"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_experience_section",
        "fieldtype": "Section Break",
        "label": "Teaching Experience",
        "insert_after": "custom_qualifications"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_total_experience_years",
        "fieldtype": "Float",
        "label": "Total Experience (Years)",
        "insert_after": "custom_experience_section"
    },
    {
        "dt": "Employee",
        "fieldname": "custom_teaching_experience_years",
        "fieldtype": "Float",
        "label": "Teaching Experience (Years)",
        "insert_after": "custom_total_experience_years"
    }
]
```

**1.2 Faculty Profile DocType**
```python
# university_erp/university_erp/doctype/faculty_profile/faculty_profile.py
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FacultyProfile(Document):
    """Faculty Profile with academic details and metrics"""

    def validate(self):
        self.validate_employee()
        self.calculate_metrics()

    def validate_employee(self):
        """Ensure linked employee is teaching staff"""
        if self.employee:
            emp_category = frappe.db.get_value(
                "Employee", self.employee, "custom_employee_category"
            )
            if emp_category != "Teaching":
                frappe.throw("Faculty Profile can only be created for Teaching employees")

    def calculate_metrics(self):
        """Calculate faculty metrics"""
        if not self.employee:
            return

        # Calculate publication count
        self.total_publications = len(self.publications) if self.publications else 0

        # Calculate H-Index (simplified)
        if self.publications:
            citations = sorted([p.citations or 0 for p in self.publications], reverse=True)
            h_index = 0
            for i, c in enumerate(citations):
                if c >= i + 1:
                    h_index = i + 1
                else:
                    break
            self.h_index = h_index

        # Calculate current workload
        self.calculate_current_workload()

    def calculate_current_workload(self):
        """Calculate current semester workload"""
        from frappe.utils import nowdate

        current_term = frappe.db.get_value(
            "Academic Term",
            {"term_start_date": ["<=", nowdate()], "term_end_date": [">=", nowdate()]},
            "name"
        )

        if not current_term:
            return

        assignments = frappe.get_all(
            "Teaching Assignment",
            filters={
                "instructor": self.employee,
                "academic_term": current_term,
                "docstatus": 1
            },
            fields=["weekly_hours", "course"]
        )

        total_hours = sum(a["weekly_hours"] or 0 for a in assignments)
        self.current_weekly_hours = total_hours
        self.assigned_courses = len(assignments)

    def on_update(self):
        """Update employee link"""
        if self.employee:
            frappe.db.set_value(
                "Employee", self.employee, "custom_faculty_profile", self.name
            )

    @frappe.whitelist()
    def get_teaching_history(self):
        """Get teaching history for faculty"""
        return frappe.get_all(
            "Teaching Assignment",
            filters={"instructor": self.employee},
            fields=["course", "course_name", "academic_term", "academic_year", "weekly_hours"],
            order_by="academic_year desc, academic_term desc"
        )

    @frappe.whitelist()
    def get_student_feedback_summary(self):
        """Get student feedback summary"""
        return frappe.db.sql("""
            SELECT
                ta.course,
                ta.academic_term,
                AVG(sf.overall_rating) as avg_rating,
                COUNT(sf.name) as feedback_count
            FROM `tabStudent Feedback` sf
            JOIN `tabTeaching Assignment` ta ON sf.teaching_assignment = ta.name
            WHERE ta.instructor = %s
            GROUP BY ta.course, ta.academic_term
            ORDER BY ta.academic_term DESC
        """, (self.employee,), as_dict=True)
```

```json
// Faculty Profile DocType Definition
{
    "doctype": "DocType",
    "name": "Faculty Profile",
    "module": "University ERP",
    "fields": [
        {
            "fieldname": "employee",
            "fieldtype": "Link",
            "label": "Employee",
            "options": "Employee",
            "reqd": 1,
            "unique": 1
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": "Employee Name",
            "fetch_from": "employee.employee_name",
            "read_only": 1
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": "Department",
            "options": "Department",
            "fetch_from": "employee.custom_academic_department"
        },
        {
            "fieldname": "designation",
            "fieldtype": "Data",
            "label": "Designation",
            "fetch_from": "employee.designation",
            "read_only": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "email",
            "fieldtype": "Data",
            "label": "Email",
            "fetch_from": "employee.company_email",
            "read_only": 1
        },
        {
            "fieldname": "contact_number",
            "fieldtype": "Data",
            "label": "Contact Number",
            "fetch_from": "employee.cell_number"
        },
        {
            "fieldname": "profile_image",
            "fieldtype": "Attach Image",
            "label": "Profile Image"
        },
        {
            "fieldname": "workload_section",
            "fieldtype": "Section Break",
            "label": "Current Workload"
        },
        {
            "fieldname": "current_weekly_hours",
            "fieldtype": "Float",
            "label": "Current Weekly Hours",
            "read_only": 1
        },
        {
            "fieldname": "assigned_courses",
            "fieldtype": "Int",
            "label": "Assigned Courses",
            "read_only": 1
        },
        {
            "fieldname": "max_weekly_hours",
            "fieldtype": "Float",
            "label": "Max Weekly Hours",
            "default": 16
        },
        {
            "fieldname": "research_section",
            "fieldtype": "Section Break",
            "label": "Research & Publications"
        },
        {
            "fieldname": "research_interests",
            "fieldtype": "Small Text",
            "label": "Research Interests"
        },
        {
            "fieldname": "total_publications",
            "fieldtype": "Int",
            "label": "Total Publications",
            "read_only": 1
        },
        {
            "fieldname": "h_index",
            "fieldtype": "Int",
            "label": "H-Index",
            "read_only": 1
        },
        {
            "fieldname": "publications",
            "fieldtype": "Table",
            "label": "Publications",
            "options": "Faculty Publication"
        },
        {
            "fieldname": "projects_section",
            "fieldtype": "Section Break",
            "label": "Research Projects"
        },
        {
            "fieldname": "projects",
            "fieldtype": "Table",
            "label": "Research Projects",
            "options": "Faculty Research Project"
        },
        {
            "fieldname": "awards_section",
            "fieldtype": "Section Break",
            "label": "Awards & Recognitions"
        },
        {
            "fieldname": "awards",
            "fieldtype": "Table",
            "label": "Awards",
            "options": "Faculty Award"
        }
    ],
    "permissions": [
        {"role": "HR Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1},
        {"role": "Instructor", "read": 1, "write": 1, "if_owner": 1}
    ]
}
```

**1.3 UGC Pay Scale Master**
```python
# university_erp/university_erp/doctype/ugc_pay_scale/ugc_pay_scale.py
import frappe
from frappe.model.document import Document

class UGCPayScale(Document):
    """UGC Pay Scale as per 7th Pay Commission"""

    def validate(self):
        self.calculate_gross()

    def calculate_gross(self):
        """Calculate gross salary"""
        self.gross_salary = (
            self.basic_pay +
            (self.basic_pay * self.da_percentage / 100) +
            (self.basic_pay * self.hra_percentage / 100) +
            self.other_allowances
        )
```

```json
// UGC Pay Scale DocType Definition
{
    "doctype": "DocType",
    "name": "UGC Pay Scale",
    "module": "University ERP",
    "fields": [
        {
            "fieldname": "pay_level",
            "fieldtype": "Select",
            "label": "Pay Level",
            "options": "Level 10\nLevel 11\nLevel 12\nLevel 13\nLevel 13A\nLevel 14\nLevel 15\nLevel 16",
            "reqd": 1
        },
        {
            "fieldname": "designation_category",
            "fieldtype": "Select",
            "label": "Designation Category",
            "options": "Assistant Professor\nAssociate Professor\nProfessor\nProfessor (HAG)",
            "reqd": 1
        },
        {
            "fieldname": "entry_pay",
            "fieldtype": "Currency",
            "label": "Entry Pay",
            "reqd": 1
        },
        {
            "fieldname": "basic_pay",
            "fieldtype": "Currency",
            "label": "Basic Pay",
            "reqd": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "da_percentage",
            "fieldtype": "Percent",
            "label": "DA %",
            "default": 46
        },
        {
            "fieldname": "hra_percentage",
            "fieldtype": "Percent",
            "label": "HRA %",
            "default": 24
        },
        {
            "fieldname": "other_allowances",
            "fieldtype": "Currency",
            "label": "Other Allowances"
        },
        {
            "fieldname": "gross_salary",
            "fieldtype": "Currency",
            "label": "Gross Salary",
            "read_only": 1
        },
        {
            "fieldname": "academic_grade_pay",
            "fieldtype": "Currency",
            "label": "Academic Grade Pay (Pre-7th CPC)"
        }
    ]
}
```

#### Output
- Employee custom fields for university context
- Faculty Profile DocType with research metrics
- UGC Pay Scale master
- Child tables for qualifications, publications, projects

---

### Week 2: Teaching Assignment & Workload Management

#### Tasks

**2.1 Teaching Assignment DocType**
```python
# university_erp/university_erp/doctype/teaching_assignment/teaching_assignment.py
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TeachingAssignment(Document):
    """Teaching Assignment linking faculty to courses"""

    def validate(self):
        self.validate_instructor()
        self.calculate_weekly_hours()
        self.check_workload_limit()
        self.check_conflicts()

    def validate_instructor(self):
        """Ensure instructor is teaching staff"""
        emp_category = frappe.db.get_value(
            "Employee", self.instructor, "custom_employee_category"
        )
        if emp_category != "Teaching":
            frappe.throw("Instructor must be a Teaching employee")

    def calculate_weekly_hours(self):
        """Calculate weekly hours from L-T-P"""
        if self.course:
            course = frappe.get_doc("Course", self.course)
            # L + T + P hours per week
            self.weekly_hours = flt(course.custom_lecture_hours or 0) + \
                               flt(course.custom_tutorial_hours or 0) + \
                               flt(course.custom_practical_hours or 0)

    def check_workload_limit(self):
        """Check if instructor is within workload limits"""
        faculty_profile = frappe.db.get_value(
            "Employee", self.instructor, "custom_faculty_profile"
        )

        if not faculty_profile:
            return

        max_hours = frappe.db.get_value(
            "Faculty Profile", faculty_profile, "max_weekly_hours"
        ) or 16

        # Get current assigned hours for same term
        current_hours = frappe.db.sql("""
            SELECT SUM(weekly_hours)
            FROM `tabTeaching Assignment`
            WHERE instructor = %s
            AND academic_term = %s
            AND docstatus = 1
            AND name != %s
        """, (self.instructor, self.academic_term, self.name or ""))[0][0] or 0

        total_hours = flt(current_hours) + flt(self.weekly_hours)

        if total_hours > max_hours:
            frappe.msgprint(
                f"Warning: Total workload ({total_hours} hrs) exceeds maximum ({max_hours} hrs)",
                indicator="orange"
            )

    def check_conflicts(self):
        """Check for schedule conflicts"""
        if not self.schedule:
            return

        for slot in self.schedule:
            conflicts = frappe.db.sql("""
                SELECT ta.name, ta.course, tas.day, tas.start_time, tas.end_time
                FROM `tabTeaching Assignment` ta
                JOIN `tabTeaching Assignment Schedule` tas ON tas.parent = ta.name
                WHERE ta.instructor = %s
                AND ta.academic_term = %s
                AND ta.docstatus = 1
                AND ta.name != %s
                AND tas.day = %s
                AND (
                    (tas.start_time <= %s AND tas.end_time > %s)
                    OR (tas.start_time < %s AND tas.end_time >= %s)
                    OR (tas.start_time >= %s AND tas.end_time <= %s)
                )
            """, (
                self.instructor, self.academic_term, self.name or "",
                slot.day, slot.start_time, slot.start_time,
                slot.end_time, slot.end_time,
                slot.start_time, slot.end_time
            ), as_dict=True)

            if conflicts:
                conflict = conflicts[0]
                frappe.throw(
                    f"Schedule conflict: {conflict.day} {slot.start_time}-{slot.end_time} "
                    f"conflicts with {conflict.course}"
                )

    def on_submit(self):
        """Update faculty workload on submit"""
        self.update_faculty_workload()

    def on_cancel(self):
        """Update faculty workload on cancel"""
        self.update_faculty_workload()

    def update_faculty_workload(self):
        """Recalculate faculty workload"""
        faculty_profile = frappe.db.get_value(
            "Employee", self.instructor, "custom_faculty_profile"
        )

        if faculty_profile:
            doc = frappe.get_doc("Faculty Profile", faculty_profile)
            doc.calculate_current_workload()
            doc.save()
```

```json
// Teaching Assignment DocType Definition
{
    "doctype": "DocType",
    "name": "Teaching Assignment",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "instructor",
            "fieldtype": "Link",
            "label": "Instructor",
            "options": "Employee",
            "reqd": 1
        },
        {
            "fieldname": "instructor_name",
            "fieldtype": "Data",
            "label": "Instructor Name",
            "fetch_from": "instructor.employee_name",
            "read_only": 1
        },
        {
            "fieldname": "course",
            "fieldtype": "Link",
            "label": "Course",
            "options": "Course",
            "reqd": 1
        },
        {
            "fieldname": "course_name",
            "fieldtype": "Data",
            "label": "Course Name",
            "fetch_from": "course.course_name",
            "read_only": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "academic_year",
            "fieldtype": "Link",
            "label": "Academic Year",
            "options": "Academic Year",
            "reqd": 1
        },
        {
            "fieldname": "academic_term",
            "fieldtype": "Link",
            "label": "Academic Term",
            "options": "Academic Term",
            "reqd": 1
        },
        {
            "fieldname": "program",
            "fieldtype": "Link",
            "label": "Program",
            "options": "Program"
        },
        {
            "fieldname": "student_group",
            "fieldtype": "Link",
            "label": "Student Group",
            "options": "Student Group"
        },
        {
            "fieldname": "workload_section",
            "fieldtype": "Section Break",
            "label": "Workload"
        },
        {
            "fieldname": "weekly_hours",
            "fieldtype": "Float",
            "label": "Weekly Hours",
            "read_only": 1
        },
        {
            "fieldname": "assignment_type",
            "fieldtype": "Select",
            "label": "Assignment Type",
            "options": "Primary\nCo-Instructor\nTutorial\nLab Assistant",
            "default": "Primary"
        },
        {
            "fieldname": "schedule_section",
            "fieldtype": "Section Break",
            "label": "Schedule"
        },
        {
            "fieldname": "schedule",
            "fieldtype": "Table",
            "label": "Weekly Schedule",
            "options": "Teaching Assignment Schedule"
        },
        {
            "fieldname": "room",
            "fieldtype": "Link",
            "label": "Default Room",
            "options": "Room"
        }
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
        {"role": "Instructor", "read": 1, "if_owner": 1}
    ]
}
```

**2.2 Workload Summary Report**
```python
# university_erp/university_erp/report/faculty_workload_summary/faculty_workload_summary.py
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"fieldname": "instructor", "label": "Instructor", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"fieldname": "instructor_name", "label": "Name", "fieldtype": "Data", "width": 180},
        {"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 150},
        {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
        {"fieldname": "courses_assigned", "label": "Courses", "fieldtype": "Int", "width": 80},
        {"fieldname": "weekly_hours", "label": "Weekly Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "max_hours", "label": "Max Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "utilization", "label": "Utilization %", "fieldtype": "Percent", "width": 100},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):
    conditions = "ta.docstatus = 1"

    if filters.get("academic_term"):
        conditions += f" AND ta.academic_term = '{filters.get('academic_term')}'"

    if filters.get("department"):
        conditions += f" AND e.custom_academic_department = '{filters.get('department')}'"

    data = frappe.db.sql(f"""
        SELECT
            e.name as instructor,
            e.employee_name as instructor_name,
            e.custom_academic_department as department,
            e.designation,
            COUNT(DISTINCT ta.course) as courses_assigned,
            SUM(ta.weekly_hours) as weekly_hours,
            COALESCE(fp.max_weekly_hours, 16) as max_hours
        FROM `tabEmployee` e
        LEFT JOIN `tabTeaching Assignment` ta ON ta.instructor = e.name AND {conditions}
        LEFT JOIN `tabFaculty Profile` fp ON fp.employee = e.name
        WHERE e.custom_employee_category = 'Teaching'
        AND e.status = 'Active'
        GROUP BY e.name
        ORDER BY weekly_hours DESC
    """, as_dict=True)

    for row in data:
        row["weekly_hours"] = row["weekly_hours"] or 0
        row["utilization"] = (row["weekly_hours"] / row["max_hours"] * 100) if row["max_hours"] else 0

        if row["utilization"] < 50:
            row["status"] = "Underutilized"
        elif row["utilization"] > 100:
            row["status"] = "Overloaded"
        else:
            row["status"] = "Optimal"

    return data

def get_chart(data):
    return {
        "data": {
            "labels": [d["instructor_name"][:20] for d in data[:15]],
            "datasets": [
                {"name": "Weekly Hours", "values": [d["weekly_hours"] for d in data[:15]]},
                {"name": "Max Hours", "values": [d["max_hours"] for d in data[:15]]}
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#e2e2e2"]
    }
```

**2.3 Workload Distribution Tool**
```python
# university_erp/university_erp/doctype/workload_distributor/workload_distributor.py
import frappe
from frappe.model.document import Document

class WorkloadDistributor(Document):
    """Tool for distributing workload across faculty"""

    @frappe.whitelist()
    def get_unassigned_courses(self):
        """Get courses without teaching assignments"""
        courses = frappe.db.sql("""
            SELECT
                c.name,
                c.course_name,
                c.custom_lecture_hours,
                c.custom_tutorial_hours,
                c.custom_practical_hours,
                c.department
            FROM `tabCourse` c
            WHERE c.name NOT IN (
                SELECT DISTINCT course
                FROM `tabTeaching Assignment`
                WHERE academic_term = %s
                AND docstatus = 1
            )
            AND c.custom_is_active = 1
        """, (self.academic_term,), as_dict=True)

        return courses

    @frappe.whitelist()
    def get_available_faculty(self, department=None):
        """Get faculty with available capacity"""
        conditions = "e.custom_employee_category = 'Teaching' AND e.status = 'Active'"

        if department:
            conditions += f" AND e.custom_academic_department = '{department}'"

        faculty = frappe.db.sql(f"""
            SELECT
                e.name as employee,
                e.employee_name,
                e.designation,
                e.custom_academic_department as department,
                COALESCE(fp.max_weekly_hours, 16) as max_hours,
                COALESCE(SUM(ta.weekly_hours), 0) as assigned_hours
            FROM `tabEmployee` e
            LEFT JOIN `tabFaculty Profile` fp ON fp.employee = e.name
            LEFT JOIN `tabTeaching Assignment` ta ON ta.instructor = e.name
                AND ta.academic_term = %s AND ta.docstatus = 1
            WHERE {conditions}
            GROUP BY e.name
            HAVING max_hours - assigned_hours > 0
            ORDER BY (max_hours - assigned_hours) DESC
        """, (self.academic_term,), as_dict=True)

        for f in faculty:
            f["available_hours"] = f["max_hours"] - f["assigned_hours"]

        return faculty

    @frappe.whitelist()
    def auto_distribute(self):
        """Automatically distribute courses to faculty"""
        unassigned = self.get_unassigned_courses()
        results = {"assigned": [], "unassigned": []}

        for course in unassigned:
            course_hours = (
                (course.custom_lecture_hours or 0) +
                (course.custom_tutorial_hours or 0) +
                (course.custom_practical_hours or 0)
            )

            # Find suitable faculty
            faculty = self.get_available_faculty(course.department)

            assigned = False
            for f in faculty:
                if f["available_hours"] >= course_hours:
                    # Create teaching assignment
                    ta = frappe.get_doc({
                        "doctype": "Teaching Assignment",
                        "instructor": f["employee"],
                        "course": course.name,
                        "academic_year": self.academic_year,
                        "academic_term": self.academic_term
                    })
                    ta.insert()

                    if self.auto_submit:
                        ta.submit()

                    results["assigned"].append({
                        "course": course.name,
                        "instructor": f["employee_name"]
                    })
                    assigned = True
                    break

            if not assigned:
                results["unassigned"].append(course.name)

        return results
```

#### Output
- Teaching Assignment DocType with conflict detection
- Workload Summary Report
- Workload Distributor Tool
- Child table for weekly schedule

---

### Week 3: Leave Management & Attendance

#### Tasks

**3.1 Academic Leave Type**
```python
# Custom leave types for academic staff
ACADEMIC_LEAVE_TYPES = [
    {
        "leave_type_name": "Casual Leave",
        "max_leaves_allowed": 8,
        "applicable_after": 0,
        "is_carry_forward": 0
    },
    {
        "leave_type_name": "Earned Leave",
        "max_leaves_allowed": 30,
        "applicable_after": 365,
        "is_carry_forward": 1,
        "max_carry_forward_leaves": 300
    },
    {
        "leave_type_name": "Medical Leave",
        "max_leaves_allowed": 20,
        "applicable_after": 0,
        "is_carry_forward": 1
    },
    {
        "leave_type_name": "Study Leave",
        "max_leaves_allowed": 730,  # 2 years
        "applicable_after": 1825,  # 5 years service
        "is_carry_forward": 0,
        "is_without_pay": 1
    },
    {
        "leave_type_name": "Sabbatical Leave",
        "max_leaves_allowed": 365,
        "applicable_after": 2555,  # 7 years service
        "is_carry_forward": 0
    },
    {
        "leave_type_name": "Maternity Leave",
        "max_leaves_allowed": 180,
        "applicable_after": 0,
        "is_carry_forward": 0
    },
    {
        "leave_type_name": "Conference/Seminar Leave",
        "max_leaves_allowed": 15,
        "applicable_after": 0,
        "is_carry_forward": 0
    },
    {
        "leave_type_name": "Examination Duty Leave",
        "max_leaves_allowed": 0,  # As required
        "applicable_after": 0,
        "is_carry_forward": 0
    }
]
```

**3.2 Custom Fields for Leave Application**
```json
// fixtures/custom_field/leave_application_custom_fields.json
[
    {
        "dt": "Leave Application",
        "fieldname": "custom_academic_section",
        "fieldtype": "Section Break",
        "label": "Academic Impact",
        "insert_after": "follow_via_email"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_classes_affected",
        "fieldtype": "Int",
        "label": "Classes Affected",
        "insert_after": "custom_academic_section",
        "read_only": 1
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_alternative_arrangement",
        "fieldtype": "Select",
        "label": "Alternative Arrangement",
        "options": "\nSubstitute Faculty\nClass Rescheduled\nOnline Session\nSelf-Study",
        "insert_after": "custom_classes_affected"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_substitute_faculty",
        "fieldtype": "Link",
        "label": "Substitute Faculty",
        "options": "Employee",
        "insert_after": "custom_alternative_arrangement",
        "depends_on": "eval:doc.custom_alternative_arrangement=='Substitute Faculty'"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_column_break_academic",
        "fieldtype": "Column Break",
        "insert_after": "custom_substitute_faculty"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_affected_courses",
        "fieldtype": "Table",
        "label": "Affected Courses",
        "options": "Leave Affected Course",
        "insert_after": "custom_column_break_academic",
        "read_only": 1
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_purpose_section",
        "fieldtype": "Section Break",
        "label": "Leave Purpose",
        "insert_after": "custom_affected_courses",
        "depends_on": "eval:['Study Leave', 'Conference/Seminar Leave', 'Sabbatical Leave'].includes(doc.leave_type)"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_conference_name",
        "fieldtype": "Data",
        "label": "Conference/Event Name",
        "insert_after": "custom_purpose_section"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_venue",
        "fieldtype": "Data",
        "label": "Venue",
        "insert_after": "custom_conference_name"
    },
    {
        "dt": "Leave Application",
        "fieldname": "custom_paper_title",
        "fieldtype": "Data",
        "label": "Paper Title (if presenting)",
        "insert_after": "custom_venue"
    }
]
```

**3.3 Leave Application Extension**
```python
# university_erp/overrides/leave_application.py
import frappe
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from frappe.utils import getdate, add_days

class UniversityLeaveApplication(LeaveApplication):
    """Extended Leave Application with academic impact tracking"""

    def validate(self):
        super().validate()
        if self.is_teaching_staff():
            self.calculate_academic_impact()

    def is_teaching_staff(self):
        """Check if employee is teaching staff"""
        return frappe.db.get_value(
            "Employee", self.employee, "custom_employee_category"
        ) == "Teaching"

    def calculate_academic_impact(self):
        """Calculate classes affected during leave period"""
        from frappe.utils import nowdate

        # Get current term
        current_term = frappe.db.get_value(
            "Academic Term",
            {"term_start_date": ["<=", self.from_date], "term_end_date": [">=", self.to_date]},
            "name"
        )

        if not current_term:
            return

        # Get teaching assignments
        assignments = frappe.get_all(
            "Teaching Assignment",
            filters={
                "instructor": self.employee,
                "academic_term": current_term,
                "docstatus": 1
            },
            fields=["name", "course", "course_name"]
        )

        if not assignments:
            return

        # Clear existing affected courses
        self.custom_affected_courses = []

        total_classes = 0
        leave_dates = self.get_leave_dates()

        for assignment in assignments:
            # Get schedule
            schedule = frappe.get_all(
                "Teaching Assignment Schedule",
                filters={"parent": assignment.name},
                fields=["day", "start_time", "end_time"]
            )

            classes_affected = 0
            for date in leave_dates:
                day_name = getdate(date).strftime("%A")
                for slot in schedule:
                    if slot.day == day_name:
                        classes_affected += 1

            if classes_affected > 0:
                self.append("custom_affected_courses", {
                    "course": assignment.course,
                    "course_name": assignment.course_name,
                    "classes_affected": classes_affected
                })
                total_classes += classes_affected

        self.custom_classes_affected = total_classes

    def get_leave_dates(self):
        """Get list of dates in leave period"""
        dates = []
        current = getdate(self.from_date)
        end = getdate(self.to_date)

        while current <= end:
            dates.append(current)
            current = add_days(current, 1)

        return dates

    def on_submit(self):
        super().on_submit()
        if self.is_teaching_staff() and self.custom_substitute_faculty:
            self.create_substitute_assignments()

    def create_substitute_assignments(self):
        """Create temporary assignments for substitute faculty"""
        for affected in self.custom_affected_courses:
            # Get original assignment
            original = frappe.get_all(
                "Teaching Assignment",
                filters={
                    "instructor": self.employee,
                    "course": affected.course,
                    "docstatus": 1
                },
                limit=1
            )

            if not original:
                continue

            original_doc = frappe.get_doc("Teaching Assignment", original[0].name)

            # Create temporary assignment
            temp_assignment = frappe.get_doc({
                "doctype": "Temporary Teaching Assignment",
                "original_assignment": original_doc.name,
                "original_instructor": self.employee,
                "substitute_instructor": self.custom_substitute_faculty,
                "course": affected.course,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "leave_application": self.name
            })
            temp_assignment.insert()
```

**3.4 Faculty Attendance Tracking**
```python
# university_erp/university_erp/doctype/faculty_attendance/faculty_attendance.py
import frappe
from frappe.model.document import Document

class FacultyAttendance(Document):
    """Track faculty attendance for scheduled classes"""

    def validate(self):
        self.validate_duplicate()
        self.validate_schedule()

    def validate_duplicate(self):
        """Check for duplicate attendance"""
        existing = frappe.db.exists(
            "Faculty Attendance",
            {
                "employee": self.employee,
                "attendance_date": self.attendance_date,
                "teaching_assignment": self.teaching_assignment,
                "schedule_slot": self.schedule_slot,
                "name": ["!=", self.name]
            }
        )

        if existing:
            frappe.throw("Attendance already marked for this schedule slot")

    def validate_schedule(self):
        """Validate attendance is for correct day"""
        day_name = frappe.utils.getdate(self.attendance_date).strftime("%A")

        if self.schedule_slot:
            slot_day = frappe.db.get_value(
                "Teaching Assignment Schedule",
                self.schedule_slot,
                "day"
            )
            if slot_day != day_name:
                frappe.throw(f"Schedule slot is for {slot_day}, not {day_name}")


@frappe.whitelist()
def get_daily_schedule(employee, date):
    """Get faculty schedule for a specific date"""
    from frappe.utils import getdate, nowdate

    if not date:
        date = nowdate()

    day_name = getdate(date).strftime("%A")

    # Get current term
    current_term = frappe.db.get_value(
        "Academic Term",
        {"term_start_date": ["<=", date], "term_end_date": [">=", date]},
        "name"
    )

    if not current_term:
        return []

    schedule = frappe.db.sql("""
        SELECT
            ta.name as teaching_assignment,
            ta.course,
            ta.course_name,
            tas.name as schedule_slot,
            tas.day,
            tas.start_time,
            tas.end_time,
            ta.room,
            ta.student_group,
            fa.status as attendance_status
        FROM `tabTeaching Assignment` ta
        JOIN `tabTeaching Assignment Schedule` tas ON tas.parent = ta.name
        LEFT JOIN `tabFaculty Attendance` fa ON fa.teaching_assignment = ta.name
            AND fa.schedule_slot = tas.name
            AND fa.attendance_date = %s
        WHERE ta.instructor = %s
        AND ta.academic_term = %s
        AND ta.docstatus = 1
        AND tas.day = %s
        ORDER BY tas.start_time
    """, (date, employee, current_term, day_name), as_dict=True)

    return schedule
```

#### Output
- Academic leave types configuration
- Leave Application extensions with impact tracking
- Temporary Teaching Assignment DocType
- Faculty Attendance tracking

---

### Week 4: Payroll Integration & Performance

#### Tasks

**4.1 Salary Structure for Faculty**
```python
# university_erp/setup/setup_payroll.py
import frappe

def create_faculty_salary_components():
    """Create salary components for faculty payroll"""

    earnings = [
        {"salary_component": "Basic Salary", "type": "Earning", "depends_on_payment_days": 1},
        {"salary_component": "Dearness Allowance", "type": "Earning", "depends_on_payment_days": 1},
        {"salary_component": "House Rent Allowance", "type": "Earning", "depends_on_payment_days": 1},
        {"salary_component": "Transport Allowance", "type": "Earning", "depends_on_payment_days": 1},
        {"salary_component": "Academic Allowance", "type": "Earning", "depends_on_payment_days": 0},
        {"salary_component": "Research Allowance", "type": "Earning", "depends_on_payment_days": 0},
        {"salary_component": "Special Pay", "type": "Earning", "depends_on_payment_days": 0}
    ]

    deductions = [
        {"salary_component": "Provident Fund", "type": "Deduction"},
        {"salary_component": "Professional Tax", "type": "Deduction"},
        {"salary_component": "Income Tax", "type": "Deduction"},
        {"salary_component": "NPS Contribution", "type": "Deduction"},
        {"salary_component": "Group Insurance", "type": "Deduction"},
        {"salary_component": "Loan Recovery", "type": "Deduction"}
    ]

    for component in earnings + deductions:
        if not frappe.db.exists("Salary Component", component["salary_component"]):
            doc = frappe.get_doc({
                "doctype": "Salary Component",
                **component
            })
            doc.insert()


def create_faculty_salary_structure():
    """Create salary structure template for faculty"""

    if frappe.db.exists("Salary Structure", "Faculty - UGC Scale"):
        return

    structure = frappe.get_doc({
        "doctype": "Salary Structure",
        "name": "Faculty - UGC Scale",
        "company": frappe.defaults.get_defaults().get("company"),
        "is_active": "Yes",
        "payroll_frequency": "Monthly",
        "earnings": [
            {
                "salary_component": "Basic Salary",
                "formula": "base",
                "amount_based_on_formula": 1
            },
            {
                "salary_component": "Dearness Allowance",
                "formula": "base * 0.46",
                "amount_based_on_formula": 1
            },
            {
                "salary_component": "House Rent Allowance",
                "formula": "base * 0.24",
                "amount_based_on_formula": 1
            },
            {
                "salary_component": "Transport Allowance",
                "formula": "3600",
                "amount_based_on_formula": 1
            },
            {
                "salary_component": "Academic Allowance",
                "formula": "custom_academic_allowance",
                "amount_based_on_formula": 1
            }
        ],
        "deductions": [
            {
                "salary_component": "Provident Fund",
                "formula": "base * 0.12",
                "amount_based_on_formula": 1
            },
            {
                "salary_component": "Professional Tax",
                "formula": "200",
                "amount_based_on_formula": 1
            },
            {
                "salary_component": "NPS Contribution",
                "formula": "base * 0.10",
                "amount_based_on_formula": 1
            }
        ]
    })
    structure.insert()
```

**4.2 Academic Performance Evaluation**
```python
# university_erp/university_erp/doctype/faculty_performance_evaluation/faculty_performance_evaluation.py
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FacultyPerformanceEvaluation(Document):
    """Annual Performance Evaluation for Faculty"""

    def validate(self):
        self.calculate_scores()
        self.determine_grade()

    def calculate_scores(self):
        """Calculate scores for each category"""
        # Teaching Score (40%)
        self.teaching_score = self.calculate_teaching_score()

        # Research Score (30%)
        self.research_score = self.calculate_research_score()

        # Administration Score (15%)
        self.administration_score = flt(self.admin_responsibilities_score or 0)

        # Student Feedback Score (15%)
        self.feedback_score = self.calculate_feedback_score()

        # Total Score
        self.total_score = (
            (self.teaching_score * 0.40) +
            (self.research_score * 0.30) +
            (self.administration_score * 0.15) +
            (self.feedback_score * 0.15)
        )

    def calculate_teaching_score(self):
        """Calculate teaching performance score"""
        score = 0

        # Workload completion
        if self.classes_scheduled and self.classes_conducted:
            completion_rate = self.classes_conducted / self.classes_scheduled * 100
            score += min(completion_rate, 100) * 0.4

        # Syllabus coverage
        if self.syllabus_coverage:
            score += self.syllabus_coverage * 0.3

        # Course material preparation
        if self.course_material_score:
            score += self.course_material_score * 0.3

        return flt(score, 2)

    def calculate_research_score(self):
        """Calculate research performance score"""
        score = 0

        # Publications
        if self.publications_count:
            score += min(self.publications_count * 10, 40)

        # Research projects
        if self.projects_count:
            score += min(self.projects_count * 15, 30)

        # PhD guidance
        if self.phd_scholars_guided:
            score += min(self.phd_scholars_guided * 10, 20)

        # Patents/Books
        if self.patents_filed:
            score += self.patents_filed * 5

        return min(flt(score, 2), 100)

    def calculate_feedback_score(self):
        """Calculate student feedback score"""
        feedback = frappe.db.sql("""
            SELECT AVG(sf.overall_rating) as avg_rating
            FROM `tabStudent Feedback` sf
            JOIN `tabTeaching Assignment` ta ON sf.teaching_assignment = ta.name
            WHERE ta.instructor = %s
            AND ta.academic_year = %s
        """, (self.employee, self.academic_year), as_dict=True)

        if feedback and feedback[0].avg_rating:
            # Convert 5-point scale to 100
            return flt(feedback[0].avg_rating * 20, 2)
        return 0

    def determine_grade(self):
        """Determine performance grade"""
        if self.total_score >= 90:
            self.grade = "Outstanding"
        elif self.total_score >= 80:
            self.grade = "Very Good"
        elif self.total_score >= 70:
            self.grade = "Good"
        elif self.total_score >= 60:
            self.grade = "Satisfactory"
        elif self.total_score >= 50:
            self.grade = "Average"
        else:
            self.grade = "Below Average"

    @frappe.whitelist()
    def auto_fill_data(self):
        """Auto-fill data from system records"""
        # Get teaching data
        teaching_data = frappe.db.sql("""
            SELECT
                COUNT(DISTINCT ta.course) as courses_taught,
                SUM(ta.weekly_hours) as total_hours
            FROM `tabTeaching Assignment` ta
            WHERE ta.instructor = %s
            AND ta.academic_year = %s
            AND ta.docstatus = 1
        """, (self.employee, self.academic_year), as_dict=True)

        if teaching_data:
            self.courses_taught = teaching_data[0].courses_taught or 0
            self.weekly_hours = teaching_data[0].total_hours or 0

        # Get attendance data
        attendance_data = frappe.db.sql("""
            SELECT
                COUNT(CASE WHEN status = 'Present' THEN 1 END) as conducted,
                COUNT(*) as scheduled
            FROM `tabFaculty Attendance`
            WHERE employee = %s
            AND YEAR(attendance_date) = SUBSTRING(%s, 1, 4)
        """, (self.employee, self.academic_year), as_dict=True)

        if attendance_data:
            self.classes_conducted = attendance_data[0].conducted or 0
            self.classes_scheduled = attendance_data[0].scheduled or 0

        # Get publication data
        faculty_profile = frappe.db.get_value(
            "Employee", self.employee, "custom_faculty_profile"
        )

        if faculty_profile:
            publications = frappe.db.count(
                "Faculty Publication",
                {"parent": faculty_profile, "year": self.academic_year[:4]}
            )
            self.publications_count = publications

        return True
```

```json
// Faculty Performance Evaluation DocType Definition
{
    "doctype": "DocType",
    "name": "Faculty Performance Evaluation",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "employee",
            "fieldtype": "Link",
            "label": "Employee",
            "options": "Employee",
            "reqd": 1
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": "Employee Name",
            "fetch_from": "employee.employee_name",
            "read_only": 1
        },
        {
            "fieldname": "academic_year",
            "fieldtype": "Link",
            "label": "Academic Year",
            "options": "Academic Year",
            "reqd": 1
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": "Department",
            "options": "Department",
            "fetch_from": "employee.custom_academic_department"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "evaluation_date",
            "fieldtype": "Date",
            "label": "Evaluation Date",
            "default": "Today"
        },
        {
            "fieldname": "evaluator",
            "fieldtype": "Link",
            "label": "Evaluated By",
            "options": "Employee"
        },
        {
            "fieldname": "teaching_section",
            "fieldtype": "Section Break",
            "label": "Teaching Performance (40%)"
        },
        {
            "fieldname": "courses_taught",
            "fieldtype": "Int",
            "label": "Courses Taught"
        },
        {
            "fieldname": "weekly_hours",
            "fieldtype": "Float",
            "label": "Weekly Hours"
        },
        {
            "fieldname": "classes_scheduled",
            "fieldtype": "Int",
            "label": "Classes Scheduled"
        },
        {
            "fieldname": "classes_conducted",
            "fieldtype": "Int",
            "label": "Classes Conducted"
        },
        {
            "fieldname": "column_break_teaching",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "syllabus_coverage",
            "fieldtype": "Percent",
            "label": "Syllabus Coverage %"
        },
        {
            "fieldname": "course_material_score",
            "fieldtype": "Float",
            "label": "Course Material Score (0-100)"
        },
        {
            "fieldname": "teaching_score",
            "fieldtype": "Float",
            "label": "Teaching Score",
            "read_only": 1
        },
        {
            "fieldname": "research_section",
            "fieldtype": "Section Break",
            "label": "Research Performance (30%)"
        },
        {
            "fieldname": "publications_count",
            "fieldtype": "Int",
            "label": "Publications"
        },
        {
            "fieldname": "projects_count",
            "fieldtype": "Int",
            "label": "Research Projects"
        },
        {
            "fieldname": "phd_scholars_guided",
            "fieldtype": "Int",
            "label": "PhD Scholars Guided"
        },
        {
            "fieldname": "patents_filed",
            "fieldtype": "Int",
            "label": "Patents Filed"
        },
        {
            "fieldname": "column_break_research",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "research_score",
            "fieldtype": "Float",
            "label": "Research Score",
            "read_only": 1
        },
        {
            "fieldname": "admin_section",
            "fieldtype": "Section Break",
            "label": "Administration (15%)"
        },
        {
            "fieldname": "admin_responsibilities",
            "fieldtype": "Small Text",
            "label": "Administrative Responsibilities"
        },
        {
            "fieldname": "admin_responsibilities_score",
            "fieldtype": "Float",
            "label": "Admin Score (0-100)"
        },
        {
            "fieldname": "administration_score",
            "fieldtype": "Float",
            "label": "Administration Score",
            "read_only": 1
        },
        {
            "fieldname": "feedback_section",
            "fieldtype": "Section Break",
            "label": "Student Feedback (15%)"
        },
        {
            "fieldname": "feedback_score",
            "fieldtype": "Float",
            "label": "Feedback Score",
            "read_only": 1
        },
        {
            "fieldname": "result_section",
            "fieldtype": "Section Break",
            "label": "Final Result"
        },
        {
            "fieldname": "total_score",
            "fieldtype": "Float",
            "label": "Total Score",
            "read_only": 1
        },
        {
            "fieldname": "grade",
            "fieldtype": "Select",
            "label": "Grade",
            "options": "Outstanding\nVery Good\nGood\nSatisfactory\nAverage\nBelow Average",
            "read_only": 1
        },
        {
            "fieldname": "remarks",
            "fieldtype": "Text",
            "label": "Remarks"
        }
    ],
    "permissions": [
        {"role": "HR Manager", "read": 1, "write": 1, "create": 1, "submit": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1}
    ]
}
```

**4.3 Student Feedback Collection**
```python
# university_erp/university_erp/doctype/student_feedback/student_feedback.py
import frappe
from frappe.model.document import Document

class StudentFeedback(Document):
    """Student feedback for faculty evaluation"""

    def validate(self):
        self.validate_duplicate()
        self.calculate_overall_rating()

    def validate_duplicate(self):
        """Prevent duplicate feedback"""
        existing = frappe.db.exists(
            "Student Feedback",
            {
                "student": self.student,
                "teaching_assignment": self.teaching_assignment,
                "name": ["!=", self.name]
            }
        )

        if existing:
            frappe.throw("Feedback already submitted for this course")

    def calculate_overall_rating(self):
        """Calculate overall rating from individual parameters"""
        ratings = [
            self.knowledge_rating or 0,
            self.communication_rating or 0,
            self.availability_rating or 0,
            self.course_material_rating or 0,
            self.fairness_rating or 0
        ]

        self.overall_rating = sum(ratings) / len([r for r in ratings if r > 0]) if any(ratings) else 0


@frappe.whitelist()
def get_pending_feedback(student):
    """Get courses pending feedback from student"""
    from frappe.utils import nowdate

    # Get current term
    current_term = frappe.db.get_value(
        "Academic Term",
        {"term_start_date": ["<=", nowdate()], "term_end_date": [">=", nowdate()]},
        "name"
    )

    if not current_term:
        return []

    # Get enrolled courses
    enrollments = frappe.get_all(
        "Course Enrollment",
        filters={
            "student": student,
            "academic_term": current_term
        },
        pluck="course"
    )

    if not enrollments:
        return []

    # Get teaching assignments for these courses
    assignments = frappe.db.sql("""
        SELECT
            ta.name,
            ta.course,
            ta.course_name,
            ta.instructor,
            e.employee_name as instructor_name
        FROM `tabTeaching Assignment` ta
        JOIN `tabEmployee` e ON ta.instructor = e.name
        WHERE ta.course IN %s
        AND ta.academic_term = %s
        AND ta.docstatus = 1
        AND ta.name NOT IN (
            SELECT teaching_assignment
            FROM `tabStudent Feedback`
            WHERE student = %s
        )
    """, (enrollments, current_term, student), as_dict=True)

    return assignments
```

#### Output
- Salary components and structure for faculty
- Faculty Performance Evaluation with auto-calculation
- Student Feedback collection system
- Integration with HRMS payroll

---

### Week 5: Reports & Faculty Portal

#### Tasks

**5.1 Faculty Directory Report**
```python
# university_erp/university_erp/report/faculty_directory/faculty_directory.py
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "employee_name", "label": "Name", "fieldtype": "Data", "width": 180},
        {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
        {"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 150},
        {"fieldname": "qualification", "label": "Qualification", "fieldtype": "Data", "width": 120},
        {"fieldname": "specialization", "label": "Specialization", "fieldtype": "Data", "width": 180},
        {"fieldname": "email", "label": "Email", "fieldtype": "Data", "width": 200},
        {"fieldname": "contact", "label": "Contact", "fieldtype": "Data", "width": 120},
        {"fieldname": "experience", "label": "Experience (Yrs)", "fieldtype": "Float", "width": 100}
    ]

def get_data(filters):
    conditions = "e.custom_employee_category = 'Teaching' AND e.status = 'Active'"

    if filters.get("department"):
        conditions += f" AND e.custom_academic_department = '{filters.get('department')}'"

    if filters.get("designation"):
        conditions += f" AND e.custom_designation_category = '{filters.get('designation')}'"

    data = frappe.db.sql(f"""
        SELECT
            e.employee_name,
            e.designation,
            e.custom_academic_department as department,
            e.custom_highest_qualification as qualification,
            e.custom_specialization as specialization,
            e.company_email as email,
            e.cell_number as contact,
            e.custom_teaching_experience_years as experience
        FROM `tabEmployee` e
        WHERE {conditions}
        ORDER BY e.custom_academic_department, e.designation
    """, as_dict=True)

    return data
```

**5.2 Department HR Summary**
```python
# university_erp/university_erp/report/department_hr_summary/department_hr_summary.py
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 200},
        {"fieldname": "total_faculty", "label": "Total Faculty", "fieldtype": "Int", "width": 100},
        {"fieldname": "professors", "label": "Professors", "fieldtype": "Int", "width": 100},
        {"fieldname": "associate_professors", "label": "Assoc. Prof", "fieldtype": "Int", "width": 100},
        {"fieldname": "assistant_professors", "label": "Asst. Prof", "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_experience", "label": "Avg Exp (Yrs)", "fieldtype": "Float", "width": 100},
        {"fieldname": "phd_count", "label": "PhD Holders", "fieldtype": "Int", "width": 100},
        {"fieldname": "sanctioned_strength", "label": "Sanctioned", "fieldtype": "Int", "width": 100},
        {"fieldname": "vacancy", "label": "Vacancy", "fieldtype": "Int", "width": 80}
    ]

def get_data(filters):
    data = frappe.db.sql("""
        SELECT
            e.custom_academic_department as department,
            COUNT(*) as total_faculty,
            SUM(CASE WHEN e.custom_designation_category = 'Professor' THEN 1 ELSE 0 END) as professors,
            SUM(CASE WHEN e.custom_designation_category = 'Associate Professor' THEN 1 ELSE 0 END) as associate_professors,
            SUM(CASE WHEN e.custom_designation_category = 'Assistant Professor' THEN 1 ELSE 0 END) as assistant_professors,
            AVG(e.custom_teaching_experience_years) as avg_experience,
            SUM(CASE WHEN e.custom_highest_qualification = 'Ph.D.' THEN 1 ELSE 0 END) as phd_count
        FROM `tabEmployee` e
        WHERE e.custom_employee_category = 'Teaching'
        AND e.status = 'Active'
        GROUP BY e.custom_academic_department
        ORDER BY total_faculty DESC
    """, as_dict=True)

    # Add sanctioned strength (from department master)
    for row in data:
        sanctioned = frappe.db.get_value(
            "Department",
            row.department,
            "custom_sanctioned_faculty_strength"
        ) or 0
        row["sanctioned_strength"] = sanctioned
        row["vacancy"] = max(0, sanctioned - row["total_faculty"])

    return data

def get_chart(data):
    return {
        "data": {
            "labels": [d["department"] for d in data],
            "datasets": [
                {"name": "Current", "values": [d["total_faculty"] for d in data]},
                {"name": "Sanctioned", "values": [d["sanctioned_strength"] for d in data]}
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#e2e2e2"]
    }
```

**5.3 Faculty Portal Page**
```python
# university_erp/www/faculty/index.py
import frappe

def get_context(context):
    """Faculty portal context"""
    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Please login to access Faculty Portal")

    # Get employee from user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        frappe.throw("No employee record found for this user")

    # Verify teaching staff
    emp_category = frappe.db.get_value("Employee", employee, "custom_employee_category")
    if emp_category != "Teaching":
        frappe.throw("Faculty Portal is only for teaching staff")

    context.employee = frappe.get_doc("Employee", employee)

    # Get faculty profile
    faculty_profile = context.employee.custom_faculty_profile
    if faculty_profile:
        context.faculty_profile = frappe.get_doc("Faculty Profile", faculty_profile)

    # Get current schedule
    from university_erp.university_erp.doctype.faculty_attendance.faculty_attendance import get_daily_schedule
    context.today_schedule = get_daily_schedule(employee, frappe.utils.nowdate())

    # Get leave balance
    context.leave_balance = get_leave_balance(employee)

    # Get recent feedback
    context.recent_feedback = get_recent_feedback(employee)

    context.no_cache = 1


def get_leave_balance(employee):
    """Get leave balance summary"""
    return frappe.db.sql("""
        SELECT
            la.leave_type,
            lt.max_leaves_allowed,
            SUM(CASE WHEN la.status = 'Approved' THEN la.total_leave_days ELSE 0 END) as used,
            lt.max_leaves_allowed - SUM(CASE WHEN la.status = 'Approved' THEN la.total_leave_days ELSE 0 END) as balance
        FROM `tabLeave Type` lt
        LEFT JOIN `tabLeave Application` la ON la.leave_type = lt.name
            AND la.employee = %s
            AND YEAR(la.from_date) = YEAR(CURDATE())
        GROUP BY lt.name
    """, (employee,), as_dict=True)


def get_recent_feedback(employee):
    """Get recent student feedback"""
    return frappe.db.sql("""
        SELECT
            sf.course,
            sf.overall_rating,
            sf.creation
        FROM `tabStudent Feedback` sf
        JOIN `tabTeaching Assignment` ta ON sf.teaching_assignment = ta.name
        WHERE ta.instructor = %s
        ORDER BY sf.creation DESC
        LIMIT 5
    """, (employee,), as_dict=True)
```

```html
<!-- university_erp/www/faculty/index.html -->
{% extends "templates/web.html" %}

{% block page_content %}
<div class="faculty-portal">
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body text-center">
                    {% if faculty_profile and faculty_profile.profile_image %}
                    <img src="{{ faculty_profile.profile_image }}" class="rounded-circle mb-3" width="120">
                    {% endif %}
                    <h4>{{ employee.employee_name }}</h4>
                    <p class="text-muted">{{ employee.designation }}</p>
                    <p>{{ employee.custom_academic_department }}</p>
                </div>
            </div>

            <div class="card mt-3">
                <div class="card-header">Leave Balance</div>
                <div class="card-body">
                    <table class="table table-sm">
                        {% for leave in leave_balance %}
                        <tr>
                            <td>{{ leave.leave_type }}</td>
                            <td class="text-end">{{ leave.balance or 0 }} / {{ leave.max_leaves_allowed }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    <a href="/app/leave-application/new" class="btn btn-primary btn-sm">Apply Leave</a>
                </div>
            </div>
        </div>

        <div class="col-md-8">
            <div class="card">
                <div class="card-header">Today's Schedule</div>
                <div class="card-body">
                    {% if today_schedule %}
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Course</th>
                                <th>Room</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for slot in today_schedule %}
                            <tr>
                                <td>{{ slot.start_time }} - {{ slot.end_time }}</td>
                                <td>{{ slot.course_name }}</td>
                                <td>{{ slot.room or '-' }}</td>
                                <td>
                                    {% if slot.attendance_status %}
                                    <span class="badge bg-success">{{ slot.attendance_status }}</span>
                                    {% else %}
                                    <span class="badge bg-warning">Pending</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p class="text-muted">No classes scheduled for today</p>
                    {% endif %}
                </div>
            </div>

            {% if faculty_profile %}
            <div class="card mt-3">
                <div class="card-header">Workload Summary</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4 text-center">
                            <h3>{{ faculty_profile.current_weekly_hours or 0 }}</h3>
                            <p class="text-muted">Weekly Hours</p>
                        </div>
                        <div class="col-md-4 text-center">
                            <h3>{{ faculty_profile.assigned_courses or 0 }}</h3>
                            <p class="text-muted">Courses</p>
                        </div>
                        <div class="col-md-4 text-center">
                            <h3>{{ faculty_profile.total_publications or 0 }}</h3>
                            <p class="text-muted">Publications</p>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}

            <div class="card mt-3">
                <div class="card-header">Recent Feedback</div>
                <div class="card-body">
                    {% if recent_feedback %}
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Course</th>
                                <th>Rating</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for fb in recent_feedback %}
                            <tr>
                                <td>{{ fb.course }}</td>
                                <td>{{ fb.overall_rating }}/5</td>
                                <td>{{ frappe.format_date(fb.creation) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p class="text-muted">No recent feedback</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### Output
- Faculty Directory Report
- Department HR Summary Report
- Faculty Portal with dashboard
- Self-service features for faculty

---

## Output Checklist

### DocTypes Created
- [ ] Faculty Profile
- [ ] UGC Pay Scale
- [ ] Teaching Assignment
- [ ] Teaching Assignment Schedule (child table)
- [ ] Temporary Teaching Assignment
- [ ] Faculty Attendance
- [ ] Faculty Performance Evaluation
- [ ] Student Feedback
- [ ] Faculty Publication (child table)
- [ ] Faculty Research Project (child table)
- [ ] Faculty Award (child table)
- [ ] Employee Qualification (child table)
- [ ] Leave Affected Course (child table)

### Custom Fields Installed
- [ ] Employee custom fields (category, qualifications, experience)
- [ ] Leave Application custom fields (academic impact)
- [ ] Department custom fields (sanctioned strength)

### HRMS Integration
- [ ] Salary components created
- [ ] Faculty salary structure configured
- [ ] Leave types for academic staff
- [ ] Payroll integration tested

### Reports Developed
- [ ] Faculty Workload Summary
- [ ] Faculty Directory
- [ ] Department HR Summary
- [ ] Performance Evaluation Report
- [ ] Leave Utilization Report

### Portal Pages
- [ ] Faculty Portal (/faculty)
- [ ] Teaching Schedule View
- [ ] Leave Application Portal
- [ ] Student Feedback Portal

### Workflows Configured
- [ ] Leave Application Workflow (with HoD approval)
- [ ] Performance Evaluation Workflow
- [ ] Teaching Assignment Approval

### Security & Permissions
- [ ] Faculty can view own profile and schedule
- [ ] HoD can view department faculty
- [ ] HR Manager full access
- [ ] Student can submit feedback only for enrolled courses

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| HRMS module conflicts | High | Careful custom field placement, override testing |
| Payroll calculation errors | High | Thorough testing with sample data |
| Leave calendar conflicts | Medium | Automatic conflict detection |
| Performance evaluation bias | Medium | Multi-level review process |
| Data privacy concerns | High | Role-based access, audit trails |

---

## Dependencies for Next Phase

Phase 7 (Extended Modules) will require:
- Employee records for hostel warden assignment
- Faculty profiles for library services
- Department structure for placement coordination

---

## Sign-off Criteria

### Functional Acceptance
- [ ] Faculty profiles capture all required academic data
- [ ] Workload tracking accurately reflects assignments
- [ ] Leave management considers academic calendar
- [ ] Performance evaluation auto-calculates scores
- [ ] Student feedback collected and aggregated
- [ ] Payroll generates correct salary slips

### Technical Acceptance
- [ ] HRMS integration stable with no conflicts
- [ ] Performance optimized for large faculty counts
- [ ] Portal loads within 3 seconds
- [ ] All reports generate correctly

### Documentation
- [ ] Faculty onboarding guide
- [ ] Workload management procedures
- [ ] Performance evaluation guidelines
- [ ] HR operations manual

---

## Estimated Timeline

| Week | Focus Area | Key Deliverables |
|------|-----------|------------------|
| 1 | Employee Extension & Faculty Profile | Custom fields, Faculty Profile, UGC Pay Scale |
| 2 | Teaching Assignment & Workload | Teaching Assignment, Workload Reports |
| 3 | Leave Management | Leave extensions, Attendance tracking |
| 4 | Payroll & Performance | Salary structure, Performance Evaluation |
| 5 | Reports & Portal | Faculty Portal, Reports |

**Total Duration: 4-5 weeks**

---

## Implementation Summary

### Completed: 2026-01-01

**Phase 6 Implementation Status: ⚠️ CORE COMPLETE (56% - Core DocTypes Done, 25 Tasks Deferred)**

#### DocTypes Created (14 total):

**Child Tables (6):**
1. **Employee Qualification** - Stores employee education qualifications
2. **Faculty Publication** - Research publications with Scopus indexing tracking
3. **Faculty Research Project** - Funded research projects with PI/Co-PI roles
4. **Faculty Award** - Academic awards and recognition
5. **Teaching Assignment Schedule** - Weekly schedule for teaching assignments
6. **Leave Affected Course** - Courses impacted by faculty leave

**Main DocTypes (8):**
1. **UGC Pay Scale** - 7th Pay Commission pay scales with gross salary calculation
2. **Faculty Profile** - Comprehensive faculty data with research metrics and workload tracking
3. **Teaching Assignment** - Course assignments with conflict detection (instructor and room)
4. **Workload Distributor** - Workload analysis and distribution recommendations
5. **Temporary Teaching Assignment** - Substitute teaching during faculty leave
6. **Faculty Attendance** - Daily attendance with scheduled classes tracking
7. **Faculty Performance Evaluation** - Annual evaluation with auto-scoring (Teaching 40%, Research 35%, Service 25%)
8. **Student Feedback** - Course-specific student feedback with multi-dimensional ratings

#### Custom Fields Created (25 total):

**Employee Custom Fields (15 fields):**
- `custom_is_faculty`: Check if employee is teaching staff
- `custom_faculty_profile`: Link to Faculty Profile
- `custom_employee_category`: Teaching/Non-Teaching/Administrative/Contract/Visiting
- `custom_ugc_pay_scale`: Link to UGC Pay Scale
- `custom_faculty_type`: Permanent/Temporary/Adhoc/Guest
- `custom_current_workload`: Weekly teaching hours (auto-calculated)
- `custom_qualifications`: Table of qualifications
- `custom_highest_qualification`: Highest education degree
- `custom_specialization`: Area of specialization
- `custom_total_experience`: Total work experience in years
- `custom_teaching_experience`: Teaching experience in years
- Plus 4 more section breaks and column breaks

**Leave Application Custom Fields (10 fields):**
- `custom_affects_teaching`: Check if leave affects teaching
- `custom_total_classes_affected`: Number of classes affected (auto-calculated)
- `custom_substitute_arranged`: Check if substitute faculty arranged
- `custom_hod_notified`: HoD notification status
- `custom_affected_courses`: Table of affected courses with substitutes
- `custom_temporary_assignment`: Link to Temporary Teaching Assignment
- Plus 4 section breaks and column breaks

#### Key Features Implemented:

**Teaching Assignment:**
- ✅ Instructor validation (must be teaching staff)
- ✅ Weekly hours calculation (Lecture + Tutorial + Practical)
- ✅ Schedule conflict detection for instructors (prevents double-booking)
- ✅ Room conflict detection (prevents room double-booking)
- ✅ Auto-update faculty workload on submit/cancel
- ✅ Instructor and room availability APIs

**Faculty Profile:**
- ✅ Employee link with teaching staff validation
- ✅ Publication count tracking (total and Scopus)
- ✅ Research metrics (H-Index, citations)
- ✅ Current workload calculation
- ✅ Teaching history tracking
- ✅ Auto-update Employee record with profile link

**Faculty Performance Evaluation:**
- ✅ Teaching score (40%): Completion rate + Student feedback + Teaching rating
- ✅ Research score (35%): Publications (15) + Scopus (10) + Projects (5) + Patents (3) + PhD guidance (2)
- ✅ Service score (25%): Committees (10) + Mentoring (8) + Outreach (7)
- ✅ Auto-grade determination (Outstanding to Needs Improvement)
- ✅ Metrics fetch from Faculty Profile and Student Feedback

**Student Feedback:**
- ✅ 6-dimensional rating system (Subject Knowledge, Teaching Methodology, Communication, Availability, Course Coverage, Overall)
- ✅ Anonymous submission support
- ✅ Rating validation (1-5 scale)
- ✅ Pending feedback API for students
- ✅ Feedback summary API for instructors

**UGC Pay Scale:**
- ✅ 7th Pay Commission levels (10-16)
- ✅ Basic Pay + AGP (Academic Grade Pay)
- ✅ DA % and HRA % configuration
- ✅ Transport Allowance
- ✅ Auto-calculation of gross monthly salary

**Workload Management:**
- ✅ Workload analysis by academic term, department, program
- ✅ Unassigned course detection
- ✅ Overloaded faculty identification (>18 hrs/week)
- ✅ Underutilized faculty identification (<12 hrs/week)
- ✅ HTML recommendations generation
- ✅ Available faculty list API

**Faculty Attendance:**
- ✅ Daily attendance tracking
- ✅ Scheduled classes count (auto-calculated from teaching assignments)
- ✅ Classes conducted tracking
- ✅ Check-in/Check-out time recording
- ✅ Daily schedule API by employee and date

#### API Endpoints Created:

**Teaching Assignment APIs:**
- `get_instructor_schedule(instructor, academic_term, day)` - Get instructor's teaching schedule
- `check_instructor_availability(instructor, academic_term, day, start_time, end_time)` - Check time slot availability
- `check_room_availability(room, academic_term, day, start_time, end_time)` - Check room booking conflicts

**Faculty Profile APIs:**
- `get_faculty_metrics(faculty_profile)` - Get comprehensive metrics (publications, projects, awards, teaching assignments)
- `get_faculty_list(department, designation)` - Get faculty list with basic information

**Student Feedback APIs:**
- `get_pending_feedback(student, academic_term)` - Get courses needing feedback
- `get_feedback_summary(instructor, academic_year)` - Get aggregated feedback for instructor

**Workload Distributor APIs:**
- `get_available_faculty(academic_term, department)` - Get faculty available for assignment

**Faculty Attendance APIs:**
- `get_daily_schedule(employee, date)` - Get teaching schedule for a specific day

#### Files Location:

**DocType Files:**
```
university_erp/university_hr/doctype/
├── ugc_pay_scale/
│   ├── ugc_pay_scale.json
│   ├── ugc_pay_scale.py
│   └── ugc_pay_scale.js
├── faculty_profile/
│   ├── faculty_profile.json
│   ├── faculty_profile.py
│   └── faculty_profile.js
├── teaching_assignment/
│   ├── teaching_assignment.json
│   ├── teaching_assignment.py (with conflict detection)
│   └── teaching_assignment.js
├── workload_distributor/
│   ├── workload_distributor.json
│   ├── workload_distributor.py (with analysis logic)
│   └── workload_distributor.js
├── faculty_performance_evaluation/
│   ├── faculty_performance_evaluation.json
│   ├── faculty_performance_evaluation.py (with auto-scoring)
│   └── faculty_performance_evaluation.js
├── student_feedback/
│   ├── student_feedback.json
│   ├── student_feedback.py (with validation and APIs)
│   └── student_feedback.js
└── [8 more DocTypes...]
```

**Custom Fields:**
```
university_erp/university_hr/fixtures/
├── employee_custom_fields.json (15 fields)
└── leave_application_custom_fields.json (10 fields)
```

#### Migration Results:
- ✅ All 14 DocTypes synced successfully
- ✅ All 6 child table Python controllers created
- ✅ All 8 main DocType Python controllers with business logic
- ✅ All 25 custom fields ready for installation
- ✅ No migration errors

#### Testing Status:
- ✅ All DocTypes verified in database
- ✅ Teaching Assignment conflict detection logic implemented
- ✅ Faculty Profile publication counting implemented
- ✅ Performance Evaluation scoring logic implemented
- ✅ Student Feedback validation implemented
- ✅ UGC Pay Scale gross salary calculation implemented
- ✅ Workload Distributor analysis logic implemented
- ✅ Faculty Attendance schedule tracking implemented

#### Previously Deferred Items - NOW COMPLETED ✅ (All 25 tasks - 100%)

**Completion Date:** January 1, 2026
**Status:** All deferred items have been successfully implemented and migrated

**Reports (5 tasks - ALL COMPLETED):**
- ✅ Faculty Workload Summary Report - Comprehensive workload analysis with utilization status
- ✅ Faculty Directory Report - Searchable faculty directory with qualification filters
- ✅ Department HR Summary Report - Department-wise HR statistics with strength tracking
- ✅ Performance Evaluation Report - Performance trends and category-wise analysis
- ✅ Leave Utilization Report - Leave usage patterns with academic impact tracking

**Workspace & UI (1 task - COMPLETED):**
- ✅ University HR Workspace - Centralized HR workspace with 12 shortcuts and organized sections

**Event Handlers (5 tasks - ALL COMPLETED):**
- ✅ Leave Application events (leave_events.py) - Academic impact calculation and HOD notifications
- ✅ Employee events (employee_events.py) - Auto-create faculty profile when employee marked as faculty
- ✅ Department events (department_events.py) - Auto-calculate strength and vacancies
- ✅ Leave Type fixtures - 12 academic leave types (CL, EL, ML, Maternity, Paternity, Sabbatical, Study, Conference, Research, Duty, Compensatory, LWP)
- ✅ Salary Component fixtures - 21 salary components (10 earnings, 11 deductions)

**Payroll Integration (3 tasks - ALL COMPLETED):**
- ✅ Salary Components fixture - Comprehensive earnings (Basic, DA, HRA, TA, AGP, Special, Medical, Leave Encashment, Performance, Research) and Deductions (PT, PF, ESI, TDS, LIC, Loan, Advance, Fine, LWP, Others, Income Tax)
- ✅ Faculty Salary Structure setup script (setup_payroll.py) - Auto-create and update salary structures from UGC Pay Scale
- ✅ UGC Pay Scale to Salary Structure mapping - Full integration with increment processing

**Leave Management Extensions (3 tasks - ALL COMPLETED):**
- ✅ Leave events handler file (leave_events.py) - Complete leave impact tracking with class counting
- ✅ Leave impact tracking logic - Auto-calculate classes affected by leave with course-wise breakdown
- ✅ Academic Leave Types fixture - 12 leave types with carry-forward and continuous-days rules

**Department Extensions (1 task - COMPLETED):**
- ✅ Department custom fields - Sanctioned teaching/non-teaching strength, current strength (auto-calculated), vacancy tracking (auto-calculated)

**Portal Pages (4 tasks - ALL COMPLETED):**
- ✅ Faculty Portal page (/faculty-portal) - Complete dashboard with teaching assignments, leave balance, performance metrics
- ✅ Faculty Portal template (index.html) - Interactive dashboard with quick stats, workload display, feedback summary
- ✅ Student Feedback Portal page (/student-feedback) - Full interface for feedback submission with duplicate prevention
- ✅ Student Feedback Portal template - Tabbed interface (Pending, All Courses, Submitted) with modal form

**Workflows (3 tasks - ALL COMPLETED):**
- ✅ Leave Application Workflow - Complete workflow: Draft → Pending HOD Approval → Pending HR Approval → Approved/Rejected (with send-back options)
- ✅ Performance Evaluation Workflow - Full workflow: Draft → Self Assessment → HOD Review → HR Review → Completed/Cancelled
- ✅ Teaching Assignment Approval Workflow - Complete workflow: Draft → Faculty Acceptance → HOD Approval → Registrar Approval → Approved/Rejected

**Additional Implementations:**
- ✅ All fixtures registered in hooks.py
- ✅ All event handlers registered in doc_events
- ✅ Portal routes configured in website_route_rules
- ✅ Website permissions configured for Faculty Profile and Student Feedback
- ✅ Database migration completed successfully
- ✅ Payroll integration scripts with 5 functions (create structure, assign, increment, bulk processing, sync)

**Files Created:** 40+ files including 15 report files (5 reports × 3 files), 2 portal pages (4 files), 3 event handlers, 3 fixtures, 3 workflows, 1 payroll script

**Impact:** All deferred items are now complete. The system now has:
- Full reporting and analytics capabilities
- Automated workflows for leave, performance, and teaching assignments
- Self-service portals for faculty and students
- Complete payroll integration with UGC Pay Scale
- Automated event handling for profiles, leave impact, and department metrics
- Real-time strength and vacancy tracking

**Documentation:** Detailed completion summary available in `/workspace/development/frappe-bench/apps/university_erp/PHASE6_COMPLETION_SUMMARY.md`

---

## Next Phase: Phase 7 - Extended Modules

After completing Phase 6 core DocTypes, proceed with:
- Hostel Management
- Library Management  
- Transport Management
- Placement & Career Services

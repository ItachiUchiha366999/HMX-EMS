# University ERP - Education Module Deep Dive

## Hybrid Approach: Extending Frappe Education

This document covers how the University ERP extends Frappe Education DocTypes for student lifecycle, academic structure, examination system, and portal implementations.

---

## Architecture: Education Extension Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                 University ERP Extensions                    │
│  Override Classes + Custom Fields + doc_events hooks        │
├─────────────────────────────────────────────────────────────┤
│                   Frappe Education                           │
│  Student, Program, Course, Fees, Assessment Plan/Result     │
└─────────────────────────────────────────────────────────────┘
```

### Key Extension Points
1. **Override Classes**: Extend Education DocType behavior via `override_doctype_class`
2. **Custom Fields**: Add university-specific fields via fixtures
3. **doc_events**: Hook into lifecycle events (validate, on_submit, etc.)
4. **Custom DocTypes**: Build only what Education doesn't provide

---

## Student Lifecycle

### Using Frappe Education's Student DocType

The Education module provides the base `Student` DocType. We extend it with:

```python
# university_erp/overrides/student.py

from education.education.doctype.student.student import Student
import frappe

class UniversityStudent(Student):
    """Extended Student with university-specific features"""

    # Lifecycle states (custom field: custom_student_status)
    STUDENT_STATES = {
        "Applicant": ["Admitted", "Rejected", "Withdrawn"],
        "Admitted": ["Enrolled", "Withdrawn"],
        "Enrolled": ["Active"],
        "Active": ["Suspended", "Dropped", "Graduated", "Transfer Out"],
        "Suspended": ["Active", "Dropped"],
        "Graduated": ["Alumni"],
        "Alumni": [],
        "Dropped": [],
        "Rejected": [],
        "Withdrawn": [],
        "Transfer Out": [],
    }

    def validate(self):
        super().validate()
        self.validate_enrollment_number()
        self.validate_category_documents()

    def validate_enrollment_number(self):
        """Ensure unique enrollment number format"""
        if self.custom_enrollment_number:
            # Format: YEAR/DEPT/NUMBER e.g., 2024/CSE/001
            pattern = r'^\d{4}/[A-Z]{2,4}/\d{3,4}$'
            import re
            if not re.match(pattern, self.custom_enrollment_number):
                frappe.throw("Enrollment number must be in format: YEAR/DEPT/NUMBER")

    def validate_category_documents(self):
        """Validate required documents for reserved categories"""
        if self.custom_category in ["SC", "ST", "OBC", "EWS"]:
            if not self.custom_category_certificate:
                frappe.throw(f"Category certificate required for {self.custom_category}")

    def transition_status(self, new_status):
        """Transition student to new status with validation"""
        current = self.custom_student_status or "Applicant"

        if new_status not in self.STUDENT_STATES.get(current, []):
            frappe.throw(f"Cannot transition from {current} to {new_status}")

        # State-specific actions
        if new_status == "Enrolled":
            self.create_program_enrollment()
        elif new_status == "Graduated":
            self.generate_final_transcript()
            self.convert_to_alumni()
        elif new_status == "Suspended":
            self.suspend_enrollments()

        self.custom_student_status = new_status
        self.save()

    def create_program_enrollment(self):
        """Create Program Enrollment when student is enrolled"""
        if not frappe.db.exists("Program Enrollment", {"student": self.name, "docstatus": 1}):
            enrollment = frappe.new_doc("Program Enrollment")
            enrollment.student = self.name
            enrollment.program = self.custom_program
            enrollment.enrollment_date = frappe.utils.today()
            enrollment.insert()
            enrollment.submit()

    def generate_final_transcript(self):
        """Generate official transcript on graduation"""
        from university_erp.examinations.transcript import TranscriptGenerator
        generator = TranscriptGenerator(self.name)
        generator.generate_transcript()

    def convert_to_alumni(self):
        """Create alumni record from student"""
        alumni = frappe.new_doc("University Alumni")
        alumni.student = self.name
        alumni.student_name = self.student_name
        alumni.email = self.student_email_id
        alumni.graduation_year = frappe.utils.now_datetime().year
        alumni.program = self.custom_program
        alumni.insert()
```

### Custom Fields on Student (Fixture)
```json
[
    {
        "dt": "Student",
        "fieldname": "custom_enrollment_number",
        "fieldtype": "Data",
        "label": "Enrollment Number",
        "unique": 1,
        "insert_after": "student_name"
    },
    {
        "dt": "Student",
        "fieldname": "custom_student_status",
        "fieldtype": "Select",
        "label": "Student Status",
        "options": "Applicant\nAdmitted\nEnrolled\nActive\nSuspended\nGraduated\nAlumni\nDropped\nWithdrawn\nTransfer Out",
        "default": "Applicant",
        "insert_after": "enabled"
    },
    {
        "dt": "Student",
        "fieldname": "custom_category",
        "fieldtype": "Select",
        "label": "Category",
        "options": "General\nOBC\nSC\nST\nEWS\nPWD",
        "insert_after": "gender"
    },
    {
        "dt": "Student",
        "fieldname": "custom_category_certificate",
        "fieldtype": "Attach",
        "label": "Category Certificate",
        "depends_on": "eval:doc.custom_category && doc.custom_category !== 'General'",
        "insert_after": "custom_category"
    },
    {
        "dt": "Student",
        "fieldname": "custom_program",
        "fieldtype": "Link",
        "label": "Program",
        "options": "Program",
        "insert_after": "custom_enrollment_number"
    },
    {
        "dt": "Student",
        "fieldname": "custom_cgpa",
        "fieldtype": "Float",
        "label": "CGPA",
        "precision": 2,
        "read_only": 1,
        "insert_after": "custom_student_status"
    },
    {
        "dt": "Student",
        "fieldname": "custom_total_credits_earned",
        "fieldtype": "Int",
        "label": "Total Credits Earned",
        "read_only": 1,
        "insert_after": "custom_cgpa"
    }
]
```

### Lifecycle State Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Applicant  │───▶│  Admitted   │───▶│  Enrolled   │───▶│   Active    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                   ┌────────────────────────────────────────────┘
                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Active    │───▶│  Graduated  │───▶│   Alumni    │
│   Student   │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ├──── Suspended ────▶ Reinstated/Dropped
       ├──── Dropped (Terminal)
       └──── Transfer Out (Terminal)
```

---

## Academic Structure

### Extending Frappe Education's Program DocType

```python
# university_erp/overrides/program.py

from education.education.doctype.program.program import Program
import frappe

class UniversityProgram(Program):
    """Extended Program with CBCS and university features"""

    def validate(self):
        super().validate()
        self.validate_credit_structure()
        self.calculate_total_credits()

    def validate_credit_structure(self):
        """Validate CBCS credit requirements"""
        if self.custom_credit_system == "CBCS":
            if not self.custom_min_credits_graduation:
                frappe.throw("Minimum credits for graduation required for CBCS programs")

    def calculate_total_credits(self):
        """Calculate total program credits from courses"""
        total = 0
        for course in self.courses:
            credits = frappe.db.get_value("Course", course.course, "custom_credits")
            total += credits or 0
        self.custom_total_credits = total

    def get_semester_courses(self, semester_number):
        """Get courses for a specific semester"""
        return [c for c in self.courses if c.custom_semester_number == semester_number]

    def get_elective_groups(self, semester_number):
        """Get elective groups for semester"""
        return frappe.get_all(
            "Elective Course Group",
            filters={
                "program": self.name,
                "custom_semester_number": semester_number
            },
            fields=["name", "group_name", "min_courses", "max_courses"]
        )
```

### Custom Fields on Program (Fixture)
```json
[
    {
        "dt": "Program",
        "fieldname": "custom_program_code",
        "fieldtype": "Data",
        "label": "Program Code",
        "unique": 1,
        "insert_after": "program_name"
    },
    {
        "dt": "Program",
        "fieldname": "custom_degree_type",
        "fieldtype": "Select",
        "label": "Degree Type",
        "options": "Certificate\nDiploma\nUG\nPG\nIntegrated\nPhD",
        "insert_after": "custom_program_code"
    },
    {
        "dt": "Program",
        "fieldname": "custom_credit_system",
        "fieldtype": "Select",
        "label": "Credit System",
        "options": "CBCS\nTraditional\nGrade Points",
        "default": "CBCS",
        "insert_after": "custom_degree_type"
    },
    {
        "dt": "Program",
        "fieldname": "custom_duration_years",
        "fieldtype": "Float",
        "label": "Duration (Years)",
        "insert_after": "custom_credit_system"
    },
    {
        "dt": "Program",
        "fieldname": "custom_total_semesters",
        "fieldtype": "Int",
        "label": "Total Semesters",
        "insert_after": "custom_duration_years"
    },
    {
        "dt": "Program",
        "fieldname": "custom_total_credits",
        "fieldtype": "Int",
        "label": "Total Credits",
        "read_only": 1,
        "insert_after": "custom_total_semesters"
    },
    {
        "dt": "Program",
        "fieldname": "custom_min_credits_graduation",
        "fieldtype": "Int",
        "label": "Min Credits for Graduation",
        "insert_after": "custom_total_credits"
    },
    {
        "dt": "Program",
        "fieldname": "custom_regulation_year",
        "fieldtype": "Int",
        "label": "Regulation Year",
        "description": "Curriculum version year (e.g., 2023)",
        "insert_after": "custom_min_credits_graduation"
    },
    {
        "dt": "Program",
        "fieldname": "custom_max_intake",
        "fieldtype": "Int",
        "label": "Maximum Intake",
        "insert_after": "custom_regulation_year"
    }
]
```

### Academic Hierarchy
```
University
└── Campus (Multi-campus support)
    └── Department (Frappe Education DocType)
        └── Program (Extended with custom fields)
            └── Course (Extended with L-T-P-S credits)
                └── Student Group (Used as-is for sections)
```

---

## Extending Course for CBCS

### Course Override Class
```python
# university_erp/overrides/course.py

from education.education.doctype.course.course import Course
import frappe

class UniversityCourse(Course):
    """Extended Course with CBCS credit structure"""

    def validate(self):
        super().validate()
        self.calculate_credits()
        self.validate_assessment_weightage()

    def calculate_credits(self):
        """Calculate credits from L-T-P-S structure"""
        # Standard formula: L + T/2 + P/2 (or as per university policy)
        L = self.custom_lecture_hours or 0
        T = self.custom_tutorial_hours or 0
        P = self.custom_practical_hours or 0

        # Credits = L + T + P/2 (common formula)
        self.custom_credits = L + T + (P / 2)

    def validate_assessment_weightage(self):
        """Ensure assessment weightages sum to 100"""
        internal = self.custom_internal_weightage or 0
        external = self.custom_external_weightage or 0
        practical = self.custom_practical_weightage or 0

        total = internal + external + practical
        if total != 100:
            frappe.throw(f"Assessment weightages must sum to 100 (current: {total})")

    def get_course_outcomes(self):
        """Get Course Outcomes for OBE"""
        return frappe.get_all(
            "Course Outcome",
            filters={"parent": self.name},
            fields=["outcome_code", "outcome_description", "bloom_level"]
        )
```

### Custom Fields on Course (Fixture)
```json
[
    {
        "dt": "Course",
        "fieldname": "custom_course_code",
        "fieldtype": "Data",
        "label": "Course Code",
        "unique": 1,
        "insert_after": "course_name"
    },
    {
        "dt": "Course",
        "fieldname": "custom_course_type",
        "fieldtype": "Select",
        "label": "Course Type (CBCS)",
        "options": "Core\nDSE\nGE\nSEC\nAEC\nVAC\nProject\nInternship",
        "insert_after": "custom_course_code"
    },
    {
        "dt": "Course",
        "fieldname": "custom_credit_section",
        "fieldtype": "Section Break",
        "label": "Credit Structure (L-T-P-S)",
        "insert_after": "custom_course_type"
    },
    {
        "dt": "Course",
        "fieldname": "custom_lecture_hours",
        "fieldtype": "Int",
        "label": "L (Lecture Hours/Week)",
        "insert_after": "custom_credit_section"
    },
    {
        "dt": "Course",
        "fieldname": "custom_tutorial_hours",
        "fieldtype": "Int",
        "label": "T (Tutorial Hours/Week)",
        "insert_after": "custom_lecture_hours"
    },
    {
        "dt": "Course",
        "fieldname": "custom_practical_hours",
        "fieldtype": "Int",
        "label": "P (Practical Hours/Week)",
        "insert_after": "custom_tutorial_hours"
    },
    {
        "dt": "Course",
        "fieldname": "custom_self_study_hours",
        "fieldtype": "Int",
        "label": "S (Self Study Hours/Week)",
        "insert_after": "custom_practical_hours"
    },
    {
        "dt": "Course",
        "fieldname": "custom_credits",
        "fieldtype": "Float",
        "label": "Total Credits",
        "read_only": 1,
        "insert_after": "custom_self_study_hours"
    },
    {
        "dt": "Course",
        "fieldname": "custom_assessment_section",
        "fieldtype": "Section Break",
        "label": "Assessment Weightage",
        "insert_after": "custom_credits"
    },
    {
        "dt": "Course",
        "fieldname": "custom_internal_weightage",
        "fieldtype": "Percent",
        "label": "Internal Assessment (%)",
        "default": 30,
        "insert_after": "custom_assessment_section"
    },
    {
        "dt": "Course",
        "fieldname": "custom_external_weightage",
        "fieldtype": "Percent",
        "label": "External/End Sem (%)",
        "default": 70,
        "insert_after": "custom_internal_weightage"
    },
    {
        "dt": "Course",
        "fieldname": "custom_practical_weightage",
        "fieldtype": "Percent",
        "label": "Practical Assessment (%)",
        "insert_after": "custom_external_weightage"
    },
    {
        "dt": "Course",
        "fieldname": "custom_min_attendance",
        "fieldtype": "Percent",
        "label": "Minimum Attendance Required",
        "default": 75,
        "insert_after": "custom_practical_weightage"
    }
]
```

---

## CBCS (Choice Based Credit System) Implementation

### CBCS Manager (Custom Module)
```python
# university_erp/academics/cbcs.py

import frappe

class CBCSManager:
    """Manage Choice Based Credit System"""

    COURSE_TYPES = {
        "Core": {"min_credits": None, "max_credits": None},
        "DSE": {"min_credits": 4, "max_credits": 24},   # Discipline Specific Elective
        "GE": {"min_credits": 4, "max_credits": 12},    # Generic Elective
        "SEC": {"min_credits": 2, "max_credits": 8},    # Skill Enhancement
        "AEC": {"min_credits": 2, "max_credits": 4},    # Ability Enhancement
        "VAC": {"min_credits": 2, "max_credits": 4},    # Value Added Course
    }

    def validate_course_selection(self, student, semester, selected_courses):
        """Validate student course selection against CBCS rules"""
        # Get student's program from Education's Student DocType
        program_name = frappe.db.get_value("Student", student, "custom_program")
        program = frappe.get_doc("Program", program_name)

        errors = []
        credits_by_type = {}

        for course_name in selected_courses:
            course = frappe.get_doc("Course", course_name)

            # Check prerequisites
            if not self.check_prerequisites(student, course):
                errors.append(f"Prerequisites not met for {course.course_name}")

            # Track credits by type
            course_type = course.custom_course_type or "Core"
            credits_by_type.setdefault(course_type, 0)
            credits_by_type[course_type] += course.custom_credits or 0

        # Validate credit limits per type
        for course_type, credits in credits_by_type.items():
            limits = self.COURSE_TYPES.get(course_type, {})
            if limits.get("max_credits") and credits > limits["max_credits"]:
                errors.append(f"Exceeded max credits ({limits['max_credits']}) for {course_type}")

        return errors

    def check_prerequisites(self, student, course):
        """Check if student has completed prerequisites"""
        # Education module stores prerequisites in Course Topics child table
        # We check Assessment Results for passed courses
        prerequisites = frappe.get_all(
            "Course Prerequisite",
            filters={"parent": course.name},
            fields=["prerequisite_course"]
        )

        for prereq in prerequisites:
            # Check Education's Assessment Result for passed grade
            result = frappe.db.exists(
                "Assessment Result",
                {
                    "student": student,
                    "course": prereq.prerequisite_course,
                    "docstatus": 1,
                    "custom_result_status": "Pass"
                }
            )
            if not result:
                return False

        return True

    def calculate_semester_credits(self, student, academic_term):
        """Calculate total credits for a semester"""
        # Use Education's Course Enrollment
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"student": student, "academic_term": academic_term},
            fields=["course"]
        )

        total_credits = 0
        for enrollment in enrollments:
            credits = frappe.db.get_value("Course", enrollment.course, "custom_credits")
            total_credits += credits or 0

        return total_credits

    def get_elective_options(self, program, semester, course_type):
        """Get available elective courses for selection"""
        return frappe.get_all(
            "Course",
            filters={
                "custom_course_type": course_type,
                "department": frappe.db.get_value("Program", program, "department")
            },
            fields=["name", "course_name", "custom_credits", "custom_course_code"]
        )
```

### Elective Course Group (Custom DocType)
```json
{
    "doctype": "DocType",
    "name": "Elective Course Group",
    "module": "University ERP",
    "fields": [
        {"fieldname": "group_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "custom_semester_number", "fieldtype": "Int", "label": "Semester"},
        {"fieldname": "elective_type", "fieldtype": "Select",
         "options": "DSE\nGE\nSEC\nAEC\nVAC"},
        {"fieldname": "min_courses", "fieldtype": "Int", "label": "Min Courses to Select"},
        {"fieldname": "max_courses", "fieldtype": "Int", "label": "Max Courses to Select"},
        {"fieldname": "min_credits", "fieldtype": "Int"},
        {"fieldname": "courses", "fieldtype": "Table", "options": "Elective Course Group Item"}
    ]
}
```

---

## Examination System

### Extending Assessment Result

The Education module provides `Assessment Plan` and `Assessment Result`. We extend them for university-grade exams.

```python
# university_erp/overrides/assessment_result.py

from education.education.doctype.assessment_result.assessment_result import AssessmentResult
import frappe
from frappe.utils import flt

class UniversityAssessmentResult(AssessmentResult):
    """Extended Assessment Result for university grading"""

    def validate(self):
        super().validate()
        self.calculate_grade()
        self.calculate_credit_points()

    def calculate_grade(self):
        """Calculate grade from total score using 10-point scale"""
        if not self.total_score or not self.maximum_score:
            return

        percentage = (flt(self.total_score) / flt(self.maximum_score)) * 100
        grade_info = self.get_grade_from_scale(percentage)

        self.custom_percentage = percentage
        self.custom_grade = grade_info.get("grade", "F")
        self.custom_grade_points = grade_info.get("grade_points", 0)
        self.custom_result_status = "Pass" if self.custom_grade_points >= 4 else "Fail"

    def get_grade_from_scale(self, percentage):
        """Get grade from 10-point CBCS scale"""
        scale = [
            {"min": 90, "max": 100, "grade": "O", "grade_points": 10},
            {"min": 80, "max": 89.99, "grade": "A+", "grade_points": 9},
            {"min": 70, "max": 79.99, "grade": "A", "grade_points": 8},
            {"min": 60, "max": 69.99, "grade": "B+", "grade_points": 7},
            {"min": 55, "max": 59.99, "grade": "B", "grade_points": 6},
            {"min": 50, "max": 54.99, "grade": "C", "grade_points": 5},
            {"min": 40, "max": 49.99, "grade": "P", "grade_points": 4},
            {"min": 0, "max": 39.99, "grade": "F", "grade_points": 0},
        ]

        for interval in scale:
            if interval["min"] <= percentage <= interval["max"]:
                return {"grade": interval["grade"], "grade_points": interval["grade_points"]}

        return {"grade": "F", "grade_points": 0}

    def calculate_credit_points(self):
        """Calculate credit points (grade_points * credits)"""
        credits = frappe.db.get_value("Course", self.course, "custom_credits") or 0
        self.custom_credits = credits
        self.custom_credit_points = self.custom_grade_points * credits

    def on_submit(self):
        super().on_submit()
        self.update_student_cgpa()

    def update_student_cgpa(self):
        """Update student's CGPA after result submission"""
        student = self.student
        results = frappe.get_all(
            "Assessment Result",
            filters={
                "student": student,
                "docstatus": 1,
                "custom_result_status": "Pass"
            },
            fields=["custom_credit_points", "custom_credits"]
        )

        if not results:
            return

        total_credit_points = sum(r.custom_credit_points or 0 for r in results)
        total_credits = sum(r.custom_credits or 0 for r in results)

        cgpa = round(total_credit_points / total_credits, 2) if total_credits else 0

        frappe.db.set_value("Student", student, {
            "custom_cgpa": cgpa,
            "custom_total_credits_earned": total_credits
        })
```

### Custom Fields on Assessment Result (Fixture)
```json
[
    {
        "dt": "Assessment Result",
        "fieldname": "custom_result_section",
        "fieldtype": "Section Break",
        "label": "University Grade",
        "insert_after": "total_score"
    },
    {
        "dt": "Assessment Result",
        "fieldname": "custom_percentage",
        "fieldtype": "Float",
        "label": "Percentage",
        "precision": 2,
        "read_only": 1,
        "insert_after": "custom_result_section"
    },
    {
        "dt": "Assessment Result",
        "fieldname": "custom_grade",
        "fieldtype": "Data",
        "label": "Grade",
        "read_only": 1,
        "insert_after": "custom_percentage"
    },
    {
        "dt": "Assessment Result",
        "fieldname": "custom_grade_points",
        "fieldtype": "Float",
        "label": "Grade Points",
        "precision": 1,
        "read_only": 1,
        "insert_after": "custom_grade"
    },
    {
        "dt": "Assessment Result",
        "fieldname": "custom_credits",
        "fieldtype": "Float",
        "label": "Course Credits",
        "read_only": 1,
        "insert_after": "custom_grade_points"
    },
    {
        "dt": "Assessment Result",
        "fieldname": "custom_credit_points",
        "fieldtype": "Float",
        "label": "Credit Points",
        "description": "Grade Points x Credits",
        "read_only": 1,
        "insert_after": "custom_credits"
    },
    {
        "dt": "Assessment Result",
        "fieldname": "custom_result_status",
        "fieldtype": "Select",
        "label": "Result Status",
        "options": "Pass\nFail\nAbsent\nWithheld",
        "read_only": 1,
        "insert_after": "custom_credit_points"
    }
]
```

### Grading Scale (10-Point CBCS)

| Grade | Percentage Range | Grade Points | Description |
|-------|------------------|--------------|-------------|
| O | 90-100 | 10 | Outstanding |
| A+ | 80-89.99 | 9 | Excellent |
| A | 70-79.99 | 8 | Very Good |
| B+ | 60-69.99 | 7 | Good |
| B | 55-59.99 | 6 | Above Average |
| C | 50-54.99 | 5 | Average |
| P | 40-49.99 | 4 | Pass |
| F | Below 40 | 0 | Fail |

---

## Custom DocTypes (Not in Education)

### Hall Ticket
```json
{
    "doctype": "DocType",
    "name": "Hall Ticket",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1},
        {"fieldname": "student_name", "fieldtype": "Data", "fetch_from": "student.student_name", "read_only": 1},
        {"fieldname": "custom_enrollment_number", "fieldtype": "Data", "fetch_from": "student.custom_enrollment_number"},
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "reqd": 1},
        {"fieldname": "exam_type", "fieldtype": "Select", "options": "Mid Semester\nEnd Semester\nSupplementary"},
        {"fieldname": "issue_date", "fieldtype": "Date"},
        {"fieldname": "photo", "fieldtype": "Attach Image"},
        {"fieldname": "eligible_exams", "fieldtype": "Table", "options": "Hall Ticket Exam"},
        {"fieldname": "attendance_eligible", "fieldtype": "Check", "label": "Attendance Criteria Met"},
        {"fieldname": "fees_paid", "fieldtype": "Check", "label": "Exam Fees Paid"}
    ]
}
```

### Student Transcript (Custom DocType)
```json
{
    "doctype": "DocType",
    "name": "Student Transcript",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1},
        {"fieldname": "student_name", "fieldtype": "Data", "fetch_from": "student.student_name"},
        {"fieldname": "custom_enrollment_number", "fieldtype": "Data", "fetch_from": "student.custom_enrollment_number"},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program"},
        {"fieldname": "generated_date", "fieldtype": "Date"},
        {"fieldname": "cgpa", "fieldtype": "Float", "precision": 2},
        {"fieldname": "total_credits", "fieldtype": "Int"},
        {"fieldname": "degree_class", "fieldtype": "Data"},
        {"fieldname": "transcript_data", "fieldtype": "JSON", "hidden": 1},
        {"fieldname": "semester_results", "fieldtype": "Table", "options": "Transcript Semester Result"}
    ]
}
```

### Transcript Generator
```python
# university_erp/examinations/transcript.py

import frappe
from frappe.utils.pdf import get_pdf

class TranscriptGenerator:
    """Generate student transcripts using Education data"""

    def __init__(self, student):
        self.student = frappe.get_doc("Student", student)
        self.results = self.get_all_results()

    def get_all_results(self):
        """Get all assessment results for student"""
        return frappe.get_all(
            "Assessment Result",
            filters={"student": self.student.name, "docstatus": 1},
            fields=[
                "course", "academic_term", "total_score", "maximum_score",
                "custom_grade", "custom_grade_points", "custom_credits",
                "custom_credit_points", "custom_result_status"
            ],
            order_by="academic_term asc, course asc"
        )

    def generate_transcript(self):
        """Generate official transcript document"""
        transcript_data = {
            "student": self.student.as_dict(),
            "semesters": self.organize_by_semester(),
            "cgpa": self.student.custom_cgpa,
            "total_credits": self.student.custom_total_credits_earned,
            "degree_class": self.determine_degree_class(),
        }

        # Create transcript document
        transcript = frappe.new_doc("Student Transcript")
        transcript.student = self.student.name
        transcript.program = self.student.custom_program
        transcript.generated_date = frappe.utils.today()
        transcript.cgpa = transcript_data["cgpa"]
        transcript.total_credits = transcript_data["total_credits"]
        transcript.degree_class = transcript_data["degree_class"]
        transcript.transcript_data = frappe.as_json(transcript_data)
        transcript.insert()

        return transcript.name

    def organize_by_semester(self):
        """Organize results by academic term"""
        semesters = {}

        for result in self.results:
            term = result.academic_term
            if term not in semesters:
                semesters[term] = {
                    "courses": [],
                    "sgpa": 0,
                    "total_credits": 0
                }
            semesters[term]["courses"].append(result)

        # Calculate SGPA for each semester
        for term, data in semesters.items():
            passed = [c for c in data["courses"] if c.custom_result_status == "Pass"]
            total_cp = sum(c.custom_credit_points or 0 for c in passed)
            total_cr = sum(c.custom_credits or 0 for c in passed)
            data["sgpa"] = round(total_cp / total_cr, 2) if total_cr else 0
            data["total_credits"] = total_cr

        return semesters

    def determine_degree_class(self):
        """Determine degree classification"""
        cgpa = self.student.custom_cgpa or 0

        if cgpa >= 9.0:
            return "First Class with Distinction"
        elif cgpa >= 7.5:
            return "First Class"
        elif cgpa >= 6.0:
            return "Second Class"
        elif cgpa >= 4.0:
            return "Pass"
        else:
            return "Incomplete"

    def get_pdf(self):
        """Generate PDF transcript"""
        html = frappe.render_template(
            "university_erp/templates/transcript.html",
            {"data": self.generate_transcript()}
        )
        return get_pdf(html)
```

---

## Attendance Management

### Using Student Attendance (Education DocType)

The Education module provides `Student Attendance`. We extend its usage:

```python
# university_erp/academics/attendance.py

import frappe
from frappe.utils import getdate

class AttendanceManager:
    """Manage student attendance using Education's Student Attendance"""

    def mark_attendance(self, course, date, student_group, attendance_list):
        """Mark attendance for a class"""
        for entry in attendance_list:
            # Check if already marked
            existing = frappe.db.exists("Student Attendance", {
                "student": entry.get("student"),
                "course_schedule": course,
                "date": date
            })

            if existing:
                frappe.db.set_value("Student Attendance", existing, "status", entry.get("status"))
            else:
                att = frappe.new_doc("Student Attendance")
                att.student = entry.get("student")
                att.student_group = student_group
                att.course_schedule = course
                att.date = date
                att.status = entry.get("status", "Present")
                att.insert()

    def get_attendance_percentage(self, student, course, academic_term=None):
        """Calculate attendance percentage"""
        filters = {"student": student}

        # Get course schedule for this course
        schedules = frappe.get_all(
            "Course Schedule",
            filters={"course": course},
            pluck="name"
        )

        if not schedules:
            return 0

        filters["course_schedule"] = ["in", schedules]

        if academic_term:
            # Filter by date range of academic term
            term = frappe.get_doc("Academic Term", academic_term)
            filters["date"] = ["between", [term.term_start_date, term.term_end_date]]

        total = frappe.db.count("Student Attendance", filters)
        present = frappe.db.count("Student Attendance", {
            **filters,
            "status": ["in", ["Present", "Late"]]
        })

        return round((present / total * 100), 2) if total else 0

    def check_exam_eligibility(self, student, course):
        """Check if student is eligible for exam based on attendance"""
        min_required = frappe.db.get_value("Course", course, "custom_min_attendance") or 75
        actual = self.get_attendance_percentage(student, course)

        return {
            "eligible": actual >= min_required,
            "required": min_required,
            "actual": actual,
            "shortage": max(0, min_required - actual)
        }

    def get_shortage_students(self, course, academic_term):
        """Get students with attendance below threshold"""
        # Get all students enrolled in course
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"course": course, "academic_term": academic_term},
            pluck="student"
        )

        shortage_students = []
        for student in enrollments:
            eligibility = self.check_exam_eligibility(student, course)
            if not eligibility["eligible"]:
                student_name = frappe.db.get_value("Student", student, "student_name")
                shortage_students.append({
                    "student": student,
                    "student_name": student_name,
                    "attendance": eligibility["actual"],
                    "shortage": eligibility["shortage"]
                })

        return shortage_students
```

---

## Student Portal

### Portal Controller (Using Education Data)
```python
# university_erp/www/student_portal/index.py

import frappe

def get_context(context):
    """Student portal dashboard context"""
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access the portal", frappe.AuthenticationError)

    student = get_student_for_user(frappe.session.user)
    if not student:
        frappe.throw("No student record found for this user")

    student_doc = frappe.get_doc("Student", student)

    context.student = student_doc
    context.current_term = get_current_academic_term()
    context.enrolled_courses = get_enrolled_courses(student)
    context.attendance_summary = get_attendance_summary(student)
    context.fee_status = get_fee_status(student)
    context.recent_results = get_recent_results(student)
    context.announcements = get_announcements(student_doc.custom_program)

def get_student_for_user(user):
    """Get student linked to user"""
    return frappe.db.get_value("Student", {"user": user})

def get_current_academic_term():
    """Get current academic term"""
    return frappe.db.get_value(
        "Academic Term",
        {"term_start_date": ["<=", frappe.utils.today()],
         "term_end_date": [">=", frappe.utils.today()]},
        "name"
    )

def get_enrolled_courses(student):
    """Get currently enrolled courses"""
    current_term = get_current_academic_term()
    return frappe.get_all(
        "Course Enrollment",
        filters={"student": student, "academic_term": current_term},
        fields=["course", "course_name"]
    )

def get_attendance_summary(student):
    """Get attendance summary for current term"""
    from university_erp.academics.attendance import AttendanceManager
    manager = AttendanceManager()

    courses = get_enrolled_courses(student)
    summary = []

    for course in courses:
        percentage = manager.get_attendance_percentage(student, course.course)
        summary.append({
            "course": course.course_name,
            "percentage": percentage,
            "status": "Good" if percentage >= 75 else "Low"
        })

    return summary

def get_fee_status(student):
    """Get fee payment status using Education's Fees"""
    pending_fees = frappe.get_all(
        "Fees",
        filters={"student": student, "outstanding_amount": [">", 0]},
        fields=["name", "fee_structure", "grand_total", "outstanding_amount", "due_date"]
    )
    return pending_fees

def get_recent_results(student):
    """Get recent assessment results"""
    return frappe.get_all(
        "Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=["course", "custom_grade", "custom_grade_points", "custom_credits", "custom_result_status"],
        order_by="creation desc",
        limit=10
    )

def get_announcements(program):
    """Get announcements for program"""
    return frappe.get_all(
        "University Announcement",
        filters={
            "publish_date": ["<=", frappe.utils.today()],
            "program": ["in", [program, None]]  # Program-specific or general
        },
        fields=["title", "content", "publish_date"],
        order_by="publish_date desc",
        limit=5
    )
```

---

## Faculty Portal

### Faculty Dashboard
```python
# university_erp/www/faculty_portal/index.py

import frappe

def get_context(context):
    """Faculty portal dashboard context"""
    # Get faculty from Employee linked to user
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user})
    if not employee:
        frappe.throw("No faculty record found")

    # Get Instructor record linked to Employee
    instructor = frappe.db.get_value("Instructor", {"employee": employee})

    context.instructor = frappe.get_doc("Instructor", instructor) if instructor else None
    context.employee = frappe.get_doc("Employee", employee)
    context.teaching_assignments = get_teaching_assignments(instructor)
    context.today_schedule = get_today_schedule(instructor)
    context.pending_attendance = get_pending_attendance_marking(instructor)
    context.pending_assessments = get_pending_assessments(instructor)

def get_teaching_assignments(instructor):
    """Get current teaching assignments"""
    current_term = frappe.db.get_value(
        "Academic Term",
        {"term_start_date": ["<=", frappe.utils.today()],
         "term_end_date": [">=", frappe.utils.today()]}
    )

    # Get from Instructor Log or Course Schedule
    return frappe.get_all(
        "Course Schedule",
        filters={"instructor": instructor, "schedule_date": [">=", frappe.utils.today()]},
        fields=["course", "student_group", "schedule_date", "from_time", "to_time", "room"],
        order_by="schedule_date asc",
        limit=20
    )

def get_today_schedule(instructor):
    """Get today's class schedule"""
    return frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor,
            "schedule_date": frappe.utils.today()
        },
        fields=["course", "student_group", "from_time", "to_time", "room"],
        order_by="from_time asc"
    )

def get_pending_attendance_marking(instructor):
    """Get classes where attendance not yet marked"""
    schedules = frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor,
            "schedule_date": ["<", frappe.utils.today()]
        },
        fields=["name", "course", "student_group", "schedule_date"]
    )

    pending = []
    for schedule in schedules:
        # Check if attendance exists for this schedule
        has_attendance = frappe.db.exists("Student Attendance", {
            "course_schedule": schedule.name
        })
        if not has_attendance:
            pending.append(schedule)

    return pending[:10]  # Limit to recent 10

def get_pending_assessments(instructor):
    """Get assessments pending grade entry"""
    return frappe.get_all(
        "Assessment Plan",
        filters={
            "supervisor": instructor,
            "docstatus": 1,
            "custom_grading_status": ["!=", "Completed"]
        },
        fields=["name", "assessment_name", "course", "schedule_date"],
        limit=10
    )
```

---

## Summary: Education Module Reuse

| Component | Frappe Education | Custom Extension |
|-----------|------------------|------------------|
| Student | Base DocType | Override class + custom fields |
| Program | Base DocType | Override class + CBCS fields |
| Course | Base DocType | Override class + L-T-P-S credits |
| Student Group | Used as-is | - |
| Course Schedule | Used as-is | - |
| Student Attendance | Used as-is | Helper functions |
| Assessment Plan | Used as-is | Custom fields |
| Assessment Result | Base DocType | Override class + grading |
| Fees | Base DocType | GL integration |
| Hall Ticket | - | Custom DocType |
| Transcript | - | Custom DocType |

---

## Next Document

Continue to [05_hrms_deep_dive.md](05_hrms_deep_dive.md) for faculty-centric HRMS implementation details.

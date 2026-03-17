# Phase 2: Admissions & Student Information System

## Overview

**Duration:** 4-6 weeks
**Priority:** High - Core student management
**Module Focus:** Student Applicant extensions, Admission workflow, Student lifecycle, Student Portal
**Status:** ✅ **COMPLETED** (2025-12-31)

This phase implements the complete admission workflow and student information system by extending Frappe Education's Student Applicant and Student DocTypes.

---

## Prerequisites

### From Phase 1
- [x] `university_erp` app installed and working
- [x] Override classes for Student and Student Applicant configured
- [x] Custom fields on Student DocType deployed
- [x] University roles created (especially University Registrar)
- [x] University Department DocType working
- [x] University Settings populated

### Technical Requirements
- [x] Education module's Student Applicant DocType accessible
- [x] Education module's Student DocType accessible
- [x] Program DocType with custom fields
- [x] Email server configured for notifications

### Data Requirements
- [x] List of programs for admission
- [x] Seat matrix (intake per program/category)
- [x] Admission criteria (eligibility rules)
- [x] Fee structure for admission fees

---

## Deliverables

### Week 1-2: Student Applicant Extensions

#### 1.1 Override Student Applicant Class

**File:** `university_erp/overrides/student_applicant.py`
```python
from education.education.doctype.student_applicant.student_applicant import StudentApplicant
import frappe
from frappe.utils import flt

class UniversityApplicant(StudentApplicant):
    """Extended Student Applicant for university admissions"""

    def validate(self):
        super().validate()
        self.validate_eligibility()
        self.calculate_merit_score()

    def validate_eligibility(self):
        """Check if applicant meets program eligibility criteria"""
        if not self.program:
            return

        criteria = frappe.db.get_value(
            "Admission Criteria",
            {"program": self.program, "admission_cycle": self.custom_admission_cycle},
            ["min_percentage", "required_subjects"],
            as_dict=True
        )

        if not criteria:
            return

        if criteria.min_percentage and self.custom_previous_percentage:
            if flt(self.custom_previous_percentage) < flt(criteria.min_percentage):
                frappe.throw(
                    f"Minimum percentage required for {self.program} is {criteria.min_percentage}%. "
                    f"Your percentage: {self.custom_previous_percentage}%"
                )

    def calculate_merit_score(self):
        """Calculate merit score based on admission criteria"""
        if not self.custom_previous_percentage:
            return

        base_score = flt(self.custom_previous_percentage)

        # Add weightage for entrance exam
        if self.custom_entrance_score:
            entrance_weightage = frappe.db.get_single_value(
                "University Settings", "entrance_exam_weightage"
            ) or 30
            base_score = (base_score * (100 - entrance_weightage) / 100) + \
                        (flt(self.custom_entrance_score) * entrance_weightage / 100)

        # Category-wise reservation points (for ranking within category)
        self.custom_merit_score = round(base_score, 2)

    def on_submit(self):
        """Actions on application submission"""
        self.validate_application_deadline()
        self.send_acknowledgment()

    def validate_application_deadline(self):
        """Check if application is within deadline"""
        if self.custom_admission_cycle:
            deadline = frappe.db.get_value(
                "Admission Cycle",
                self.custom_admission_cycle,
                "application_deadline"
            )
            if deadline and frappe.utils.getdate() > frappe.utils.getdate(deadline):
                frappe.throw("Application deadline has passed")

    def send_acknowledgment(self):
        """Send application acknowledgment email"""
        if self.student_email_id:
            frappe.sendmail(
                recipients=[self.student_email_id],
                subject=f"Application Received - {self.name}",
                template="admission_acknowledgment",
                args={
                    "applicant_name": self.first_name,
                    "application_number": self.name,
                    "program": self.program
                }
            )
```

#### 1.2 Custom Fields on Student Applicant

**Add to fixtures:**
```json
[
    {
        "dt": "Student Applicant",
        "fieldname": "custom_admission_section",
        "fieldtype": "Section Break",
        "label": "Admission Details",
        "insert_after": "program"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_admission_cycle",
        "fieldtype": "Link",
        "label": "Admission Cycle",
        "options": "Admission Cycle",
        "insert_after": "custom_admission_section"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_application_type",
        "fieldtype": "Select",
        "label": "Application Type",
        "options": "Fresh\nLateral Entry\nTransfer",
        "default": "Fresh",
        "insert_after": "custom_admission_cycle"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_category",
        "fieldtype": "Select",
        "label": "Category",
        "options": "General\nOBC\nSC\nST\nEWS\nPWD",
        "insert_after": "gender"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_category_certificate",
        "fieldtype": "Attach",
        "label": "Category Certificate",
        "depends_on": "eval:doc.custom_category && doc.custom_category !== 'General'",
        "insert_after": "custom_category"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_academic_section",
        "fieldtype": "Section Break",
        "label": "Previous Academic Record",
        "insert_after": "image"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_previous_qualification",
        "fieldtype": "Data",
        "label": "Previous Qualification",
        "insert_after": "custom_academic_section"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_previous_percentage",
        "fieldtype": "Float",
        "label": "Previous Percentage/CGPA",
        "precision": 2,
        "insert_after": "custom_previous_qualification"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_board_university",
        "fieldtype": "Data",
        "label": "Board/University",
        "insert_after": "custom_previous_percentage"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_passing_year",
        "fieldtype": "Int",
        "label": "Year of Passing",
        "insert_after": "custom_board_university"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_entrance_section",
        "fieldtype": "Section Break",
        "label": "Entrance Exam",
        "insert_after": "custom_passing_year"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_entrance_exam",
        "fieldtype": "Data",
        "label": "Entrance Exam Name",
        "insert_after": "custom_entrance_section"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_entrance_roll_number",
        "fieldtype": "Data",
        "label": "Roll Number",
        "insert_after": "custom_entrance_exam"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_entrance_score",
        "fieldtype": "Float",
        "label": "Score/Percentile",
        "insert_after": "custom_entrance_roll_number"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_entrance_rank",
        "fieldtype": "Int",
        "label": "Rank",
        "insert_after": "custom_entrance_score"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_merit_section",
        "fieldtype": "Section Break",
        "label": "Merit Calculation",
        "insert_after": "custom_entrance_rank"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_merit_score",
        "fieldtype": "Float",
        "label": "Merit Score",
        "precision": 2,
        "read_only": 1,
        "insert_after": "custom_merit_section"
    },
    {
        "dt": "Student Applicant",
        "fieldname": "custom_merit_rank",
        "fieldtype": "Int",
        "label": "Merit Rank",
        "read_only": 1,
        "insert_after": "custom_merit_score"
    }
]
```

### Week 2-3: Admission DocTypes

#### 2.1 Admission Cycle
```json
{
    "doctype": "DocType",
    "name": "Admission Cycle",
    "module": "Admissions",
    "fields": [
        {"fieldname": "cycle_name", "fieldtype": "Data", "reqd": 1, "label": "Cycle Name"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "University Academic Year", "reqd": 1},
        {"fieldname": "application_start_date", "fieldtype": "Date", "reqd": 1},
        {"fieldname": "application_deadline", "fieldtype": "Date", "reqd": 1},
        {"fieldname": "counseling_start_date", "fieldtype": "Date"},
        {"fieldname": "admission_deadline", "fieldtype": "Date"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Upcoming\nOpen\nClosed\nCompleted", "default": "Upcoming"},
        {"fieldname": "programs", "fieldtype": "Table", "options": "Admission Cycle Program"}
    ],
    "autoname": "field:cycle_name"
}
```

#### 2.2 Seat Matrix
```json
{
    "doctype": "DocType",
    "name": "Seat Matrix",
    "module": "Admissions",
    "fields": [
        {"fieldname": "admission_cycle", "fieldtype": "Link", "options": "Admission Cycle", "reqd": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "total_seats", "fieldtype": "Int", "reqd": 1},
        {"fieldname": "general_seats", "fieldtype": "Int"},
        {"fieldname": "obc_seats", "fieldtype": "Int"},
        {"fieldname": "sc_seats", "fieldtype": "Int"},
        {"fieldname": "st_seats", "fieldtype": "Int"},
        {"fieldname": "ews_seats", "fieldtype": "Int"},
        {"fieldname": "pwd_seats", "fieldtype": "Int"},
        {"fieldname": "management_seats", "fieldtype": "Int"},
        {"fieldname": "filled_seats", "fieldtype": "Int", "read_only": 1, "default": 0}
    ]
}
```

#### 2.3 Merit List
```json
{
    "doctype": "DocType",
    "name": "Merit List",
    "module": "Admissions",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "admission_cycle", "fieldtype": "Link", "options": "Admission Cycle", "reqd": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "category", "fieldtype": "Select", "options": "General\nOBC\nSC\nST\nEWS\nPWD"},
        {"fieldname": "list_number", "fieldtype": "Int", "label": "Merit List Number", "default": 1},
        {"fieldname": "generation_date", "fieldtype": "Date"},
        {"fieldname": "valid_till", "fieldtype": "Date"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nPublished\nExpired", "default": "Draft"},
        {"fieldname": "applicants", "fieldtype": "Table", "options": "Merit List Applicant"}
    ]
}
```

#### 2.4 Merit List Generation

**File:** `university_erp/admissions/merit_list.py`
```python
import frappe

class MeritListGenerator:
    """Generate merit lists for admission"""

    def __init__(self, admission_cycle, program, category=None):
        self.admission_cycle = admission_cycle
        self.program = program
        self.category = category

    def generate(self):
        """Generate merit list based on merit scores"""
        filters = {
            "custom_admission_cycle": self.admission_cycle,
            "program": self.program,
            "docstatus": 1,
            "application_status": ["not in", ["Rejected", "Admitted"]]
        }

        if self.category:
            filters["custom_category"] = self.category

        applicants = frappe.get_all(
            "Student Applicant",
            filters=filters,
            fields=[
                "name", "first_name", "last_name", "custom_merit_score",
                "custom_category", "custom_previous_percentage",
                "custom_entrance_score"
            ],
            order_by="custom_merit_score desc"
        )

        # Create merit list document
        merit_list = frappe.new_doc("Merit List")
        merit_list.admission_cycle = self.admission_cycle
        merit_list.program = self.program
        merit_list.category = self.category
        merit_list.generation_date = frappe.utils.today()

        for rank, applicant in enumerate(applicants, 1):
            merit_list.append("applicants", {
                "applicant": applicant.name,
                "applicant_name": f"{applicant.first_name} {applicant.last_name or ''}",
                "merit_rank": rank,
                "merit_score": applicant.custom_merit_score,
                "category": applicant.custom_category
            })

            # Update rank on applicant
            frappe.db.set_value(
                "Student Applicant",
                applicant.name,
                "custom_merit_rank",
                rank
            )

        merit_list.insert()
        return merit_list.name

@frappe.whitelist()
def generate_merit_list(admission_cycle, program, category=None):
    """API to generate merit list"""
    generator = MeritListGenerator(admission_cycle, program, category)
    return generator.generate()
```

### Week 3-4: Admission Workflow

#### 3.1 Admission Workflow Definition

**File:** `university_erp/admissions/workflow.py`
```python
import frappe

def setup_admission_workflow():
    """Create admission workflow"""
    if frappe.db.exists("Workflow", "Student Applicant Approval"):
        return

    workflow = frappe.new_doc("Workflow")
    workflow.workflow_name = "Student Applicant Approval"
    workflow.document_type = "Student Applicant"
    workflow.is_active = 1
    workflow.workflow_state_field = "workflow_state"

    # States
    states = [
        {"state": "Draft", "doc_status": 0, "allow_edit": "University Registrar"},
        {"state": "Submitted", "doc_status": 1, "allow_edit": ""},
        {"state": "Under Review", "doc_status": 1, "allow_edit": "University Registrar"},
        {"state": "Document Verification", "doc_status": 1, "allow_edit": "University Registrar"},
        {"state": "Shortlisted", "doc_status": 1, "allow_edit": ""},
        {"state": "Counseling Scheduled", "doc_status": 1, "allow_edit": ""},
        {"state": "Seat Allotted", "doc_status": 1, "allow_edit": "University Registrar"},
        {"state": "Fee Payment Pending", "doc_status": 1, "allow_edit": ""},
        {"state": "Admitted", "doc_status": 1, "allow_edit": ""},
        {"state": "Rejected", "doc_status": 2, "allow_edit": ""},
        {"state": "Withdrawn", "doc_status": 2, "allow_edit": ""}
    ]

    for state in states:
        workflow.append("states", state)

    # Transitions
    transitions = [
        {"state": "Draft", "action": "Submit", "next_state": "Submitted", "allowed": "University Registrar"},
        {"state": "Submitted", "action": "Review", "next_state": "Under Review", "allowed": "University Registrar"},
        {"state": "Under Review", "action": "Verify Documents", "next_state": "Document Verification", "allowed": "University Registrar"},
        {"state": "Document Verification", "action": "Shortlist", "next_state": "Shortlisted", "allowed": "University Registrar"},
        {"state": "Document Verification", "action": "Reject", "next_state": "Rejected", "allowed": "University Registrar"},
        {"state": "Shortlisted", "action": "Schedule Counseling", "next_state": "Counseling Scheduled", "allowed": "University Registrar"},
        {"state": "Counseling Scheduled", "action": "Allot Seat", "next_state": "Seat Allotted", "allowed": "University Registrar"},
        {"state": "Seat Allotted", "action": "Request Fee", "next_state": "Fee Payment Pending", "allowed": "University Registrar"},
        {"state": "Fee Payment Pending", "action": "Confirm Admission", "next_state": "Admitted", "allowed": "University Registrar"},
        {"state": "Fee Payment Pending", "action": "Withdraw", "next_state": "Withdrawn", "allowed": "University Registrar"},
    ]

    for transition in transitions:
        workflow.append("transitions", transition)

    workflow.insert()
    return workflow.name
```

#### 3.2 Applicant to Student Conversion

**File:** `university_erp/admissions/student_creation.py`
```python
import frappe

class StudentCreator:
    """Convert admitted applicant to student"""

    def __init__(self, applicant_name):
        self.applicant = frappe.get_doc("Student Applicant", applicant_name)

    def create_student(self):
        """Create student from applicant"""
        if self.applicant.application_status != "Admitted":
            frappe.throw("Only admitted applicants can be converted to students")

        # Check if student already exists
        existing = frappe.db.exists("Student", {"student_applicant": self.applicant.name})
        if existing:
            frappe.throw(f"Student already exists: {existing}")

        # Generate enrollment number
        enrollment_number = self.generate_enrollment_number()

        # Create student using Education's Student DocType
        student = frappe.new_doc("Student")
        student.first_name = self.applicant.first_name
        student.middle_name = self.applicant.middle_name
        student.last_name = self.applicant.last_name
        student.student_email_id = self.applicant.student_email_id
        student.date_of_birth = self.applicant.date_of_birth
        student.gender = self.applicant.gender
        student.student_mobile_number = self.applicant.student_mobile_number
        student.blood_group = self.applicant.blood_group
        student.image = self.applicant.image
        student.student_applicant = self.applicant.name

        # Custom fields
        student.custom_enrollment_number = enrollment_number
        student.custom_student_status = "Admitted"
        student.custom_category = self.applicant.custom_category
        student.custom_category_certificate = self.applicant.custom_category_certificate
        student.custom_program = self.applicant.program
        student.custom_admission_date = frappe.utils.today()
        student.custom_admission_cycle = self.applicant.custom_admission_cycle

        # Copy guardians
        for guardian in self.applicant.guardians:
            student.append("guardians", {
                "guardian": guardian.guardian,
                "guardian_name": guardian.guardian_name,
                "relation": guardian.relation
            })

        student.insert()

        # Create user account
        self.create_student_user(student)

        # Update applicant status
        frappe.db.set_value(
            "Student Applicant",
            self.applicant.name,
            "student": student.name
        )

        return student.name

    def generate_enrollment_number(self):
        """Generate unique enrollment number"""
        # Format: YEAR/DEPT/NUMBER
        year = frappe.utils.now_datetime().year
        dept_code = frappe.db.get_value(
            "Program",
            self.applicant.program,
            "custom_department_code"
        ) or "GEN"

        # Get next serial
        last_enrollment = frappe.db.sql("""
            SELECT custom_enrollment_number FROM `tabStudent`
            WHERE custom_enrollment_number LIKE %(pattern)s
            ORDER BY custom_enrollment_number DESC LIMIT 1
        """, {"pattern": f"{year}/{dept_code}/%"})

        if last_enrollment:
            last_serial = int(last_enrollment[0][0].split("/")[-1])
            next_serial = last_serial + 1
        else:
            next_serial = 1

        return f"{year}/{dept_code}/{str(next_serial).zfill(3)}"

    def create_student_user(self, student):
        """Create user account for student"""
        if frappe.db.exists("User", student.student_email_id):
            user = frappe.get_doc("User", student.student_email_id)
        else:
            user = frappe.new_doc("User")
            user.email = student.student_email_id
            user.first_name = student.first_name
            user.last_name = student.last_name
            user.send_welcome_email = 1
            user.user_type = "Website User"

        # Add University Student role
        if not user.has_role("University Student"):
            user.append("roles", {"role": "University Student"})

        if user.is_new():
            user.insert(ignore_permissions=True)
        else:
            user.save(ignore_permissions=True)

        # Link user to student
        frappe.db.set_value("Student", student.name, "user", user.name)

@frappe.whitelist()
def create_student_from_applicant(applicant_name):
    """API to create student from applicant"""
    creator = StudentCreator(applicant_name)
    return creator.create_student()
```

### Week 4-5: Student Lifecycle Management

#### 4.1 Student Status Management

**File:** `university_erp/student_info/lifecycle.py`
```python
import frappe

class StudentLifecycle:
    """Manage student lifecycle transitions"""

    VALID_TRANSITIONS = {
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

    def __init__(self, student_name):
        self.student = frappe.get_doc("Student", student_name)

    def can_transition_to(self, new_status):
        """Check if transition is valid"""
        current = self.student.custom_student_status or "Applicant"
        return new_status in self.VALID_TRANSITIONS.get(current, [])

    def transition_to(self, new_status, reason=None):
        """Perform status transition"""
        if not self.can_transition_to(new_status):
            current = self.student.custom_student_status
            frappe.throw(f"Cannot transition from {current} to {new_status}")

        old_status = self.student.custom_student_status

        # Perform transition-specific actions
        self._perform_transition_actions(new_status)

        # Update status
        self.student.custom_student_status = new_status
        self.student.save()

        # Log the transition
        self._log_transition(old_status, new_status, reason)

        return True

    def _perform_transition_actions(self, new_status):
        """Actions specific to each transition"""
        if new_status == "Enrolled":
            self._create_program_enrollment()
        elif new_status == "Active":
            self._activate_student()
        elif new_status == "Graduated":
            self._graduate_student()
        elif new_status == "Alumni":
            self._convert_to_alumni()
        elif new_status == "Suspended":
            self._suspend_student()
        elif new_status == "Dropped":
            self._drop_student()

    def _create_program_enrollment(self):
        """Create program enrollment record"""
        if not frappe.db.exists("Program Enrollment", {
            "student": self.student.name,
            "program": self.student.custom_program
        }):
            enrollment = frappe.new_doc("Program Enrollment")
            enrollment.student = self.student.name
            enrollment.program = self.student.custom_program
            enrollment.enrollment_date = frappe.utils.today()
            enrollment.insert()

    def _activate_student(self):
        """Activate student account"""
        self.student.enabled = 1

    def _graduate_student(self):
        """Process graduation"""
        # Generate final transcript
        from university_erp.examinations.transcript import TranscriptGenerator
        generator = TranscriptGenerator(self.student.name)
        generator.generate_transcript()

        # Update graduation date
        self.student.custom_graduation_date = frappe.utils.today()

    def _convert_to_alumni(self):
        """Create alumni record"""
        if not frappe.db.exists("University Alumni", {"student": self.student.name}):
            alumni = frappe.new_doc("University Alumni")
            alumni.student = self.student.name
            alumni.student_name = self.student.student_name
            alumni.email = self.student.student_email_id
            alumni.program = self.student.custom_program
            alumni.graduation_year = frappe.utils.now_datetime().year
            alumni.insert()

    def _suspend_student(self):
        """Suspend student account"""
        self.student.enabled = 0

    def _drop_student(self):
        """Drop student - disable account"""
        self.student.enabled = 0

    def _log_transition(self, old_status, new_status, reason):
        """Log status transition"""
        frappe.get_doc({
            "doctype": "Student Status Log",
            "student": self.student.name,
            "from_status": old_status,
            "to_status": new_status,
            "transition_date": frappe.utils.now_datetime(),
            "reason": reason,
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)
```

### Week 5-6: Student Portal

#### 5.1 Student Portal Controller

**File:** `university_erp/www/student-portal/index.py`
```python
import frappe
from frappe import _

def get_context(context):
    """Student portal main page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the portal"), frappe.AuthenticationError)

    student = get_student_for_user()
    if not student:
        frappe.throw(_("No student record found for this user"))

    student_doc = frappe.get_doc("Student", student)

    context.no_cache = 1
    context.student = student_doc
    context.current_semester = get_current_semester(student)
    context.enrolled_courses = get_enrolled_courses(student)
    context.attendance_summary = get_attendance_summary(student)
    context.fee_status = get_fee_status(student)
    context.recent_results = get_recent_results(student)
    context.announcements = get_announcements(student_doc.custom_program)
    context.upcoming_events = get_upcoming_events(student)

def get_student_for_user():
    """Get student linked to current user"""
    return frappe.db.get_value("Student", {"user": frappe.session.user})

def get_current_semester(student):
    """Get current academic term"""
    return frappe.db.get_value(
        "Academic Term",
        {
            "term_start_date": ["<=", frappe.utils.today()],
            "term_end_date": [">=", frappe.utils.today()]
        }
    )

def get_enrolled_courses(student):
    """Get courses student is enrolled in"""
    current_term = get_current_semester(student)
    return frappe.get_all(
        "Course Enrollment",
        filters={"student": student, "academic_term": current_term},
        fields=["course", "course_name", "enrollment_date"]
    )

def get_attendance_summary(student):
    """Get attendance percentage for current semester"""
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
    """Get pending fees"""
    return frappe.get_all(
        "Fees",
        filters={"student": student, "outstanding_amount": [">", 0]},
        fields=["name", "fee_structure", "grand_total", "outstanding_amount", "due_date"],
        order_by="due_date asc"
    )

def get_recent_results(student):
    """Get recent assessment results"""
    return frappe.get_all(
        "Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=[
            "course", "custom_grade", "custom_grade_points",
            "custom_credits", "custom_result_status"
        ],
        order_by="creation desc",
        limit=10
    )

def get_announcements(program):
    """Get relevant announcements"""
    return frappe.get_all(
        "University Announcement",
        filters={
            "publish_date": ["<=", frappe.utils.today()],
            "program": ["in", [program, None]]
        },
        fields=["title", "content", "publish_date"],
        order_by="publish_date desc",
        limit=5
    )

def get_upcoming_events(student):
    """Get upcoming events for student"""
    return frappe.get_all(
        "University Event",
        filters={
            "event_date": [">=", frappe.utils.today()],
            "status": "Scheduled"
        },
        fields=["event_name", "event_date", "event_type", "venue"],
        order_by="event_date asc",
        limit=5
    )
```

#### 5.2 Student Portal Template

**File:** `university_erp/www/student-portal/index.html`
```html
{% extends "templates/web.html" %}

{% block page_content %}
<div class="student-portal">
    <div class="portal-header">
        <h1>Welcome, {{ student.student_name }}</h1>
        <p>Enrollment: {{ student.custom_enrollment_number }} | Program: {{ student.custom_program }}</p>
    </div>

    <div class="dashboard-grid">
        <!-- Quick Stats -->
        <div class="stats-row">
            <div class="stat-card">
                <h3>CGPA</h3>
                <span class="stat-value">{{ student.custom_cgpa or "N/A" }}</span>
            </div>
            <div class="stat-card">
                <h3>Credits Earned</h3>
                <span class="stat-value">{{ student.custom_total_credits_earned or 0 }}</span>
            </div>
            <div class="stat-card">
                <h3>Current Semester</h3>
                <span class="stat-value">{{ current_semester or "N/A" }}</span>
            </div>
        </div>

        <!-- Enrolled Courses -->
        <div class="section-card">
            <h2>My Courses</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Attendance</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for course in enrolled_courses %}
                    <tr>
                        <td>{{ course.course_name }}</td>
                        <td>
                            {% set att = attendance_summary | selectattr("course", "equalto", course.course_name) | first %}
                            {{ att.percentage if att else "N/A" }}%
                        </td>
                        <td>
                            {% if att and att.status == "Good" %}
                            <span class="badge badge-success">Good</span>
                            {% else %}
                            <span class="badge badge-warning">Low</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Pending Fees -->
        {% if fee_status %}
        <div class="section-card alert">
            <h2>Pending Fees</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Fee Type</th>
                        <th>Amount Due</th>
                        <th>Due Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for fee in fee_status %}
                    <tr>
                        <td>{{ fee.fee_structure }}</td>
                        <td>₹ {{ fee.outstanding_amount }}</td>
                        <td>{{ fee.due_date }}</td>
                        <td><a href="/pay-fee/{{ fee.name }}" class="btn btn-primary btn-sm">Pay Now</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- Recent Results -->
        <div class="section-card">
            <h2>Recent Results</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Grade</th>
                        <th>Credits</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in recent_results %}
                    <tr>
                        <td>{{ result.course }}</td>
                        <td>{{ result.custom_grade }}</td>
                        <td>{{ result.custom_credits }}</td>
                        <td>
                            {% if result.custom_result_status == "Pass" %}
                            <span class="badge badge-success">Pass</span>
                            {% else %}
                            <span class="badge badge-danger">Fail</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Announcements -->
        <div class="section-card">
            <h2>Announcements</h2>
            {% for announcement in announcements %}
            <div class="announcement">
                <h4>{{ announcement.title }}</h4>
                <p>{{ announcement.content | truncate(200) }}</p>
                <small>{{ announcement.publish_date }}</small>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## Output Checklist

### Code Deliverables
- [x] Student Applicant override class with validation
- [x] Custom fields on Student Applicant deployed
- [x] Admission Cycle DocType created
- [x] Seat Matrix DocType created
- [x] Merit List DocType created
- [x] Merit list generation script working
- [x] Admission workflow configured
- [x] Student creation from applicant working
- [x] Enrollment number generation working
- [x] Student lifecycle management class
- [x] Student Status Log DocType created
- [x] Student portal controller
- [x] Student portal HTML template

### Workflow Deliverables
- [x] Admission workflow active
- [x] Email notifications for workflow transitions
- [x] Merit list publication notifications
- [x] Seat allotment notifications

### Portal Deliverables
- [x] Student portal accessible at /student-portal
- [x] Dashboard shows enrolled courses
- [x] Attendance summary displayed
- [x] Pending fees displayed
- [x] Recent results shown
- [x] Announcements section working

### Testing Checklist
- [x] Application submission works
- [x] Application validation enforces eligibility
- [x] Merit score calculation correct
- [x] Merit list generation creates ranked list
- [x] Workflow transitions work correctly
- [x] Applicant to student conversion works
- [x] Enrollment number format correct
- [x] Student portal loads correctly
- [x] Student can only see own data

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex merit calculation | Medium | Medium | Create comprehensive test cases |
| Workflow deadlocks | Low | High | Define all valid transitions |
| Seat matrix overflow | Medium | High | Add validation on seat allotment |
| Data migration issues | High | Medium | Create migration scripts |

---

## Dependencies for Next Phase

Phase 3 (Academics) requires:
- [ ] Student records created and active ✅
- [ ] Program enrollment working ✅
- [ ] Student lifecycle management active ✅
- [ ] Student portal functional ✅

**Status:** All dependencies met. Phase 3 completed.

---

## Sign-off Criteria

| Criteria | Required By |
|----------|-------------|
| Complete admission cycle tested | QA Lead |
| Merit list generation verified | Registrar |
| Student conversion working | Dev Lead |
| Portal security verified | Security |
| Documentation complete | Tech Writer |

---

## Implementation Summary

### Completed: 2025-12-30

**Phase 2 Implementation Status: ✅ COMPLETED**

All code deliverables have been implemented. The following components were created:

#### DocTypes Created (8 total):
1. **Admission Cycle** - Manages admission periods with programs, dates, and settings
2. **Admission Cycle Program** - Child table for programs in an admission cycle
3. **Seat Matrix** - Category-wise seat allocation (General, OBC, SC, ST, EWS, PWD, Management)
4. **Merit List** - Submittable DocType for ranked applicant lists
5. **Merit List Applicant** - Child table for applicants in merit lists
6. **Admission Criteria** - Eligibility and scoring criteria per program
7. **Student Status Log** - Logs student lifecycle transitions
8. **University Announcement** - Announcements with audience targeting
9. **University Alumni** - Alumni tracking with professional details

#### Python Modules Created (4 total):
1. **admissions/merit_list.py** - MeritListGenerator and MeritListProcessor classes
2. **admissions/student_creation.py** - StudentCreator and BulkStudentCreator classes
3. **admissions/workflow.py** - Admission workflow setup and handlers
4. **student_info/lifecycle.py** - StudentLifecycle class with state machine

#### Student Portal:
- **www/student-portal/index.py** - Portal controller with dashboard data
- **www/student-portal/index.html** - Responsive Bootstrap template

#### API Endpoints (15 total):
- Merit list generation and seat allotment
- Student creation from applicants
- Workflow management
- Student lifecycle transitions
- Alumni search and statistics
- Announcements retrieval

### Files Location:
```
frappe-bench/apps/university_erp/university_erp/
├── admissions/
│   ├── merit_list.py
│   ├── student_creation.py
│   ├── workflow.py
│   └── doctype/ (6 DocTypes)
├── student_info/
│   ├── lifecycle.py
│   └── doctype/ (3 DocTypes)
└── www/student-portal/
```

---

**Previous Phase:** [Phase 1: Foundation & Core Setup](phase_01_foundation.md)
**Next Phase:** [Phase 3: Academics Module](phase_03_academics.md)

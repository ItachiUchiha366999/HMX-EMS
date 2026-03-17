import frappe
from frappe import _
from frappe.utils import flt
from education.education.doctype.student_applicant.student_applicant import StudentApplicant


class UniversityApplicant(StudentApplicant):
    """
    University-specific Student Applicant class extending Frappe Education's Student Applicant.

    Features:
    - Merit score calculation (10th %, 12th %, Entrance Exam)
    - Application number generation
    - Admission status workflow
    - Program preference management
    - Seat allotment
    - Category certificate validation
    """

    def validate(self):
        """Called before saving the document"""
        super().validate()
        self.generate_application_number()
        self.calculate_merit_score()
        self.validate_category_certificate()
        self.validate_program_preferences()

    def before_submit(self):
        """Called before submitting the application"""
        super().before_submit()
        self.set_admission_status()

    def generate_application_number(self):
        """Generate unique application number"""
        if self.custom_application_number:
            return

        # Get admission cycle
        if not self.custom_admission_cycle:
            frappe.throw(_("Admission Cycle is required"))

        # Generate format: CYCLE-YEAR-SEQUENCE
        # Example: UG-2025-00001
        admission_cycle = frappe.get_doc("Admission Cycle", self.custom_admission_cycle)
        year = admission_cycle.academic_year[:4] if admission_cycle.academic_year else "2025"

        # Get last application number for this cycle
        last_app = frappe.get_all(
            "Student Applicant",
            filters={"custom_admission_cycle": self.custom_admission_cycle},
            fields=["custom_application_number"],
            order_by="custom_application_number desc",
            limit=1
        )

        if last_app and last_app[0].custom_application_number:
            # Extract sequence number and increment
            parts = last_app[0].custom_application_number.split("-")
            if len(parts) >= 3:
                sequence = int(parts[-1]) + 1
            else:
                sequence = 1
        else:
            sequence = 1

        # Get cycle code (e.g., "UG" from cycle name)
        cycle_code = "APP"
        if "UG" in admission_cycle.name:
            cycle_code = "UG"
        elif "PG" in admission_cycle.name:
            cycle_code = "PG"

        self.custom_application_number = f"{cycle_code}-{year}-{sequence:05d}"

    def calculate_merit_score(self):
        """
        Calculate merit score based on weighted formula:
        Merit Score = (10th % × 0.2) + (12th % × 0.3) + (Entrance Exam Score × 0.5)

        Adjust weights as per university policy
        """
        percent_10th = self.custom_percentage_10th or 0.0
        percent_12th = self.custom_percentage_12th or 0.0
        entrance_score = self.custom_entrance_exam_score or 0.0

        # Weighted formula
        # 20% weight to 10th, 30% to 12th, 50% to entrance exam
        merit_score = (
            (percent_10th * 0.2) +
            (percent_12th * 0.3) +
            (entrance_score * 0.5)
        )

        self.custom_merit_score = flt(merit_score, 2)

    def validate_category_certificate(self):
        """Validate that reserved category applicants have uploaded certificates"""
        if not self.custom_category:
            return

        reserved_categories = ["SC", "ST", "OBC", "EWS"]

        if self.custom_category in reserved_categories and not self.custom_category_certificate:
            frappe.msgprint(
                _("Category certificate is required for {0} category").format(
                    self.custom_category
                ),
                alert=True,
                indicator="orange"
            )

    def validate_program_preferences(self):
        """Validate program preferences"""
        prefs = [
            self.custom_program_preference_1,
            self.custom_program_preference_2,
            self.custom_program_preference_3
        ]

        # Check for duplicates
        prefs_set = set(p for p in prefs if p)
        if len(prefs_set) != len([p for p in prefs if p]):
            frappe.throw(_("Program preferences cannot have duplicate programs"))

        # At least one preference is required
        if not any(prefs):
            frappe.throw(_("At least one program preference is required"))

    def set_admission_status(self):
        """Set initial admission status on submission"""
        if not self.custom_admission_status:
            self.custom_admission_status = "Submitted"


def allot_seat(applicant_id, program):
    """
    Allot seat to an applicant for a specific program

    Args:
        applicant_id: Student Applicant ID
        program: Program to allot
    """
    applicant = frappe.get_doc("Student Applicant", applicant_id)

    # Validate applicant is eligible
    if applicant.custom_admission_status not in ["Submitted", "Document Verified"]:
        frappe.throw(_("Applicant must be in Submitted or Document Verified status"))

    # Check if program is in applicant's preferences
    prefs = [
        applicant.custom_program_preference_1,
        applicant.custom_program_preference_2,
        applicant.custom_program_preference_3
    ]

    if program not in prefs:
        frappe.throw(_("Program {0} is not in applicant's preferences").format(program))

    # Allot seat
    applicant.custom_seat_allotted = program
    applicant.custom_admission_status = "Seat Allotted"
    applicant.program = program
    applicant.save(ignore_permissions=True)

    frappe.msgprint(
        _("Seat allotted for program {0}").format(program),
        alert=True,
        indicator="green"
    )

    return applicant


def generate_merit_list(admission_cycle, program=None, category=None):
    """
    Generate merit list for an admission cycle

    Args:
        admission_cycle: Admission Cycle ID
        program: Filter by program (optional)
        category: Filter by category (optional)

    Returns:
        List of applicants sorted by merit score
    """
    filters = {
        "custom_admission_cycle": admission_cycle,
        "docstatus": 1,  # Submitted applications only
        "custom_admission_status": ["in", ["Submitted", "Document Verified"]]
    }

    if category:
        filters["custom_category"] = category

    applicants = frappe.get_all(
        "Student Applicant",
        filters=filters,
        fields=[
            "name", "student_name", "custom_application_number",
            "custom_merit_score", "custom_entrance_exam_rank",
            "custom_category", "custom_program_preference_1",
            "custom_program_preference_2", "custom_program_preference_3",
            "custom_percentage_10th", "custom_percentage_12th",
            "custom_entrance_exam_score"
        ],
        order_by="custom_merit_score desc, custom_entrance_exam_rank asc"
    )

    # Filter by program if specified
    if program:
        applicants = [
            app for app in applicants
            if program in [
                app.custom_program_preference_1,
                app.custom_program_preference_2,
                app.custom_program_preference_3
            ]
        ]

    # Assign rank
    for idx, app in enumerate(applicants, start=1):
        app["rank"] = idx

    return applicants


def bulk_seat_allotment(admission_cycle, program, num_seats, category=None):
    """
    Perform bulk seat allotment based on merit

    Args:
        admission_cycle: Admission Cycle ID
        program: Program to allot seats
        num_seats: Number of seats to allot
        category: Category quota (optional)

    Returns:
        Number of seats allotted
    """
    merit_list = generate_merit_list(admission_cycle, program, category)

    allotted_count = 0

    for applicant in merit_list[:num_seats]:
        try:
            allot_seat(applicant.name, program)
            allotted_count += 1
        except Exception as e:
            frappe.logger().error(f"Error allotting seat to {applicant.name}: {str(e)}")
            continue

    frappe.msgprint(
        _("{0} seats allotted for program {1}").format(allotted_count, program),
        alert=True,
        indicator="green"
    )

    return allotted_count


def create_student_from_applicant(applicant_id):
    """
    Create Student record from admitted applicant

    Args:
        applicant_id: Student Applicant ID

    Returns:
        Student doc
    """
    applicant = frappe.get_doc("Student Applicant", applicant_id)

    # Validate applicant has accepted admission
    if applicant.custom_admission_status != "Admission Confirmed":
        frappe.throw(_("Applicant must confirm admission before creating student record"))

    if not applicant.custom_seat_allotted:
        frappe.throw(_("No seat allotted to applicant"))

    # Check if student already created
    if applicant.application_status == "Admitted":
        existing_student = frappe.db.get_value("Student", {"student_applicant": applicant.name})
        if existing_student:
            frappe.throw(_("Student record already exists: {0}").format(existing_student))

    # Create Student using Education app's method
    student = applicant.create_student()

    # Set university-specific fields
    student.custom_program = applicant.custom_seat_allotted
    student.custom_category = applicant.custom_category
    student.custom_student_status = "Active"

    # Generate enrollment number (will be set by Student validate method)
    student.save(ignore_permissions=True)

    # Update applicant status
    applicant.custom_admission_status = "Admitted"
    applicant.save(ignore_permissions=True)

    return student

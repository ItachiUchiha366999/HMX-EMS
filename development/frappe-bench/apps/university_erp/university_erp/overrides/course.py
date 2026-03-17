import frappe
from frappe import _
from education.education.doctype.course.course import Course


class UniversityCourse(Course):
    """
    University-specific Course class extending Frappe Education's Course.

    Features:
    - L-T-P (Lecture-Tutorial-Practical) credit calculation
    - Course code uniqueness validation
    - Assessment weightage validation (must sum to 100%)
    - Course type validation
    """

    def validate(self):
        """Called before saving the document"""
        super().validate()
        self.validate_course_code()
        self.calculate_credits()
        self.validate_assessment_weightage()

    def validate_course_code(self):
        """Validate that course code is unique"""
        if not self.custom_course_code:
            return

        existing = frappe.db.exists(
            "Course",
            {
                "custom_course_code": self.custom_course_code,
                "name": ("!=", self.name)
            }
        )

        if existing:
            frappe.throw(_("Course Code {0} already exists").format(
                self.custom_course_code
            ))

    def calculate_credits(self):
        """
        Calculate credits based on L-T-P formula:
        Credits = L + T + (P/2) + Self Study Credits

        Where:
        - L = Lecture hours per week
        - T = Tutorial hours per week
        - P = Practical hours per week
        - Self Study = Self study credits
        """
        lecture = self.custom_lecture_hours or 0
        tutorial = self.custom_tutorial_hours or 0
        practical = self.custom_practical_hours or 0
        self_study = self.custom_self_study_credits or 0

        # Standard formula: L + T + P/2 + Self Study
        credits = lecture + tutorial + (practical / 2) + self_study

        self.custom_credits = credits

        # Validate reasonable credit values
        if credits > 10:
            frappe.msgprint(
                _("Course credits ({0}) seems unusually high").format(credits),
                alert=True,
                indicator="orange"
            )

    def validate_assessment_weightage(self):
        """Validate that assessment weightages sum to 100%"""
        internal = self.custom_internal_weightage or 0
        external = self.custom_external_weightage or 0
        practical = self.custom_practical_weightage or 0

        total = internal + external + practical

        # Allow some tolerance for rounding
        if abs(total - 100) > 0.01 and total > 0:
            frappe.throw(
                _("Total assessment weightage must be 100%. Current total: {0}%").format(total)
            )

        # Validate minimum internal assessment
        if internal < 20 and self.custom_course_type in ["Core", "Elective"]:
            frappe.msgprint(
                _("Internal weightage ({0}%) is less than recommended minimum of 20%").format(internal),
                alert=True,
                indicator="orange"
            )


def get_course_details(course):
    """Get detailed information about a course"""
    if not course:
        return {}

    course_doc = frappe.get_doc("Course", course)

    return {
        "course_name": course_doc.course_name,
        "course_code": course_doc.custom_course_code,
        "credits": course_doc.custom_credits,
        "course_type": course_doc.custom_course_type,
        "department": course_doc.custom_department,
        "lecture_hours": course_doc.custom_lecture_hours,
        "tutorial_hours": course_doc.custom_tutorial_hours,
        "practical_hours": course_doc.custom_practical_hours,
        "self_study_credits": course_doc.custom_self_study_credits,
        "internal_weightage": course_doc.custom_internal_weightage,
        "external_weightage": course_doc.custom_external_weightage,
        "practical_weightage": course_doc.custom_practical_weightage,
    }


def get_ltp_format(course):
    """
    Get L-T-P format string for a course
    Returns: "L-T-P" e.g., "3-1-2" for 3 lecture, 1 tutorial, 2 practical
    """
    if not course:
        return ""

    course_doc = frappe.get_doc("Course", course)

    lecture = course_doc.custom_lecture_hours or 0
    tutorial = course_doc.custom_tutorial_hours or 0
    practical = course_doc.custom_practical_hours or 0

    return f"{lecture}-{tutorial}-{practical}"


def calculate_contact_hours(course):
    """Calculate total contact hours per week for a course"""
    if not course:
        return 0

    course_doc = frappe.get_doc("Course", course)

    lecture = course_doc.custom_lecture_hours or 0
    tutorial = course_doc.custom_tutorial_hours or 0
    practical = course_doc.custom_practical_hours or 0

    return lecture + tutorial + practical

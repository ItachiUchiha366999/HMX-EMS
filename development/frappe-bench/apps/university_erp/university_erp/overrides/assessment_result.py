import frappe
from frappe import _
from education.education.doctype.assessment_result.assessment_result import AssessmentResult


class UniversityAssessmentResult(AssessmentResult):
    """
    University-specific Assessment Result class extending Frappe Education's Assessment Result.

    Features:
    - 10-point grading system (O=10, A+=9, A=8, B+=7, B=6, C=5, P=4, F=0)
    - Grade points calculation from percentage
    - Credit points calculation (Grade Points × Credits)
    - SGPA calculation
    - Absence handling
    """

    def validate(self):
        """Called before saving the document"""
        super().validate()
        self.calculate_percentage()
        self.calculate_grade_points()
        self.calculate_credit_points()
        self.validate_absence()

    def calculate_percentage(self):
        """Calculate percentage from total_score and maximum_score"""
        if not self.total_score or not self.maximum_score:
            self.custom_percentage = 0.0
            return

        self.custom_percentage = (self.total_score / self.maximum_score) * 100

    def calculate_grade_points(self):
        """
        Calculate grade points based on 10-point scale:
        O  (90-100): 10
        A+ (80-89):  9
        A  (70-79):  8
        B+ (60-69):  7
        B  (55-59):  6
        C  (50-54):  5
        P  (45-49):  4
        F  (0-44):   0
        """
        if self.custom_is_absent:
            self.custom_grade_points = 0.0
            self.grade = "AB"
            return

        percentage = self.custom_percentage or 0.0

        if percentage >= 90:
            self.custom_grade_points = 10.0
            self.grade = "O"
        elif percentage >= 80:
            self.custom_grade_points = 9.0
            self.grade = "A+"
        elif percentage >= 70:
            self.custom_grade_points = 8.0
            self.grade = "A"
        elif percentage >= 60:
            self.custom_grade_points = 7.0
            self.grade = "B+"
        elif percentage >= 55:
            self.custom_grade_points = 6.0
            self.grade = "B"
        elif percentage >= 50:
            self.custom_grade_points = 5.0
            self.grade = "C"
        elif percentage >= 45:
            self.custom_grade_points = 4.0
            self.grade = "P"
        else:
            self.custom_grade_points = 0.0
            self.grade = "F"

    def calculate_credit_points(self):
        """
        Calculate credit points: Grade Points × Course Credits
        This is used for SGPA/CGPA calculation
        """
        # Get course credits
        if not self.course:
            self.custom_credit_points = 0.0
            return

        course = frappe.get_doc("Course", self.course)
        credits = course.custom_credits or 0.0

        self.custom_credits = credits
        self.custom_credit_points = self.custom_grade_points * credits

    def validate_absence(self):
        """Handle absence cases"""
        if self.custom_is_absent:
            self.custom_grade_points = 0.0
            self.custom_credit_points = 0.0
            self.grade = "AB"

            frappe.msgprint(
                _("Student marked as absent. Grade: AB, Grade Points: 0"),
                alert=True,
                indicator="red"
            )


def calculate_sgpa(student, academic_term):
    """
    Calculate Semester Grade Point Average (SGPA) for a student in a term

    SGPA = Σ(Grade Points × Credits) / Σ(Credits)
    """
    if not student or not academic_term:
        return 0.0

    results = frappe.get_all(
        "Assessment Result",
        filters={
            "student": student,
            "academic_term": academic_term,
            "docstatus": 1,  # Only submitted results
            "custom_is_absent": 0  # Exclude absent cases
        },
        fields=["custom_grade_points", "custom_credits"]
    )

    if not results:
        return 0.0

    total_credit_points = sum(r.custom_grade_points * r.custom_credits for r in results)
    total_credits = sum(r.custom_credits for r in results)

    if total_credits > 0:
        return round(total_credit_points / total_credits, 2)

    return 0.0


def calculate_cgpa(student):
    """
    Calculate Cumulative Grade Point Average (CGPA) for a student

    CGPA = Σ(Grade Points × Credits) / Σ(Credits) across all semesters
    """
    if not student:
        return 0.0

    results = frappe.get_all(
        "Assessment Result",
        filters={
            "student": student,
            "docstatus": 1,  # Only submitted results
            "custom_is_absent": 0  # Exclude absent cases
        },
        fields=["custom_grade_points", "custom_credits"]
    )

    if not results:
        return 0.0

    total_credit_points = sum(r.custom_grade_points * r.custom_credits for r in results)
    total_credits = sum(r.custom_credits for r in results)

    if total_credits > 0:
        return round(total_credit_points / total_credits, 2)

    return 0.0


def get_grade_description(grade):
    """Get description for a grade"""
    descriptions = {
        "O": "Outstanding",
        "A+": "Excellent",
        "A": "Very Good",
        "B+": "Good",
        "B": "Above Average",
        "C": "Average",
        "P": "Pass",
        "F": "Fail",
        "AB": "Absent"
    }
    return descriptions.get(grade, "")


def get_student_grade_sheet(student, academic_year=None):
    """Get complete grade sheet for a student"""
    filters = {
        "student": student,
        "docstatus": 1
    }

    if academic_year:
        filters["academic_year"] = academic_year

    results = frappe.get_all(
        "Assessment Result",
        filters=filters,
        fields=[
            "name", "course", "academic_term", "academic_year",
            "custom_percentage", "grade", "custom_grade_points",
            "custom_credits", "custom_credit_points", "custom_is_absent"
        ],
        order_by="academic_year desc, academic_term"
    )

    # Group by academic term
    grade_sheet = {}
    for result in results:
        term = result.academic_term
        if term not in grade_sheet:
            grade_sheet[term] = {
                "results": [],
                "sgpa": 0.0,
                "credits": 0.0
            }

        grade_sheet[term]["results"].append(result)

    # Calculate SGPA for each term
    for term, data in grade_sheet.items():
        total_credit_points = sum(r.custom_credit_points for r in data["results"] if not r.custom_is_absent)
        total_credits = sum(r.custom_credits for r in data["results"] if not r.custom_is_absent)

        if total_credits > 0:
            data["sgpa"] = round(total_credit_points / total_credits, 2)
        data["credits"] = total_credits

    return grade_sheet

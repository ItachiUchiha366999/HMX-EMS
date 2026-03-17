import frappe
from frappe import _
from frappe.model.document import Document
from education.education.doctype.student.student import Student


class UniversityStudent(Student):
    """
    University-specific Student class extending Frappe Education's Student.

    Features:
    - Enrollment number validation (unique)
    - Category certificate validation
    - CGPA calculation from assessment results
    - Student status management
    """

    def validate(self):
        """Called before saving the document"""
        super().validate()
        self.validate_enrollment_number()
        self.validate_category_certificate()
        self.calculate_cgpa()

    def on_update(self):
        """Called after document is updated"""
        # Call parent on_update only if it exists
        if hasattr(super(), 'on_update'):
            super().on_update()
        self.update_student_status()

    def validate_enrollment_number(self):
        """Validate that enrollment number is unique"""
        if not self.custom_enrollment_number:
            return

        # Check if another student has the same enrollment number
        existing = frappe.db.exists(
            "Student",
            {
                "custom_enrollment_number": self.custom_enrollment_number,
                "name": ("!=", self.name)
            }
        )

        if existing:
            frappe.throw(_("Enrollment Number {0} already exists").format(
                self.custom_enrollment_number
            ))

    def validate_category_certificate(self):
        """Validate that reserved category students have uploaded certificates"""
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

    def calculate_cgpa(self):
        """Calculate CGPA from all assessment results"""
        if not self.name:
            return

        # Get all assessment results for this student
        assessment_results = frappe.get_all(
            "Assessment Result",
            filters={
                "student": self.name,
                "docstatus": 1  # Only submitted results
            },
            fields=["custom_grade_points", "custom_credits"]
        )

        if not assessment_results:
            self.custom_cgpa = 0.0
            return

        total_credit_points = 0.0
        total_credits = 0.0

        for result in assessment_results:
            grade_points = result.get("custom_grade_points") or 0.0
            credits = result.get("custom_credits") or 0.0

            total_credit_points += grade_points * credits
            total_credits += credits

        if total_credits > 0:
            self.custom_cgpa = round(total_credit_points / total_credits, 2)
        else:
            self.custom_cgpa = 0.0

    def update_student_status(self):
        """Update student status based on various conditions"""
        # This will be enhanced in later phases
        # For now, just log the update
        frappe.logger().info(f"Student {self.name} updated. Status: {self.custom_student_status}")


# Module-level functions for doc_events hooks

def validate_student(doc, method):
    """Global validate hook for Student DocType"""
    # Additional validation that doesn't fit in the class
    pass


def on_student_update(doc, method):
    """Global on_update hook for Student DocType"""
    # Additional actions on student update
    pass


def get_permission_query_conditions(user):
    """Permission query conditions for Student list view"""
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    # Admins and System Managers can see all students (check FIRST)
    if any(role in roles for role in [
        "System Manager",
        "Administrator",
        "University Admin",
        "University Registrar",
        "Academics User",
        "Education Manager"
    ]):
        return ""  # No restrictions

    # Faculty can see students in their department
    if "University Faculty" in roles:
        # This will be enhanced when department assignments are implemented
        return ""

    # Students can only see their own record (check LAST)
    if "University Student" in roles or "Student" in roles:
        return f'`tabStudent`.`user` = "{user}"'

    # Default: no access
    return "1=0"


def has_permission(doc, user):
    """Row-level permission check for Student"""
    if not user:
        user = frappe.session.user

    # Students can only access their own record
    if "University Student" in frappe.get_roles(user):
        return doc.user == user

    # Faculty and admins have full access
    if any(role in frappe.get_roles(user) for role in [
        "University Faculty",
        "University HOD",
        "University Admin",
        "University Registrar"
    ]):
        return True

    return False


def student_query(doctype, txt, searchfield, start, page_len, filters):
    """Custom query for Student link fields"""
    return frappe.db.sql("""
        SELECT
            name, student_name, custom_enrollment_number
        FROM
            `tabStudent`
        WHERE
            student_name LIKE %(txt)s
            OR custom_enrollment_number LIKE %(txt)s
        ORDER BY
            modified DESC
        LIMIT
            %(start)s, %(page_len)s
    """, {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })

# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class LMSCourse(Document):
    def validate(self):
        self.validate_dates()
        self.validate_max_students()

    def validate_dates(self):
        """Validate course dates"""
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw(_("Course End Date cannot be before Start Date"))

        if self.enrollment_deadline and self.start_date:
            if getdate(self.enrollment_deadline) > getdate(self.start_date):
                frappe.throw(_("Enrollment Deadline should be before Course Start Date"))

    def validate_max_students(self):
        """Validate max students if specified"""
        if self.max_students and self.max_students < 0:
            frappe.throw(_("Maximum Students cannot be negative"))

    def get_enrolled_students(self):
        """Get list of enrolled students for this course"""
        # Get students enrolled in this course through Program Enrollment
        students = frappe.db.sql("""
            SELECT DISTINCT s.name, s.student_name
            FROM `tabStudent` s
            INNER JOIN `tabProgram Enrollment` pe ON pe.student = s.name
            INNER JOIN `tabProgram Course` pc ON pc.parent = pe.program
            WHERE pc.course = %s
            AND pe.academic_term = %s
            AND pe.docstatus = 1
        """, (self.course, self.academic_term), as_dict=True)

        return students

    def update_statistics(self):
        """Update course statistics"""
        students = self.get_enrolled_students()
        self.enrolled_students = len(students)

        # Calculate average completion
        if students:
            total_progress = 0
            for student in students:
                progress = self.get_student_progress(student.name)
                total_progress += progress

            self.completion_rate = total_progress / len(students) if students else 0

        self.db_update()

    def get_student_progress(self, student):
        """Get student's progress in this course"""
        total_content = frappe.db.count("LMS Content", {
            "lms_course": self.name,
            "status": "Published",
            "is_mandatory": 1
        })

        if not total_content:
            return 0

        completed_content = frappe.db.count("LMS Content Progress", {
            "lms_course": self.name,
            "student": student,
            "status": "Completed"
        })

        return (completed_content / total_content) * 100


@frappe.whitelist()
def get_available_courses(academic_term=None, instructor=None):
    """Get list of published LMS courses"""
    filters = {"status": "Published"}

    if academic_term:
        filters["academic_term"] = academic_term

    if instructor:
        filters["instructor"] = instructor

    courses = frappe.get_all("LMS Course",
        filters=filters,
        fields=["name", "course", "course_name", "instructor", "instructor_name",
                "start_date", "end_date", "enrolled_students", "allow_self_enrollment"]
    )

    return courses


@frappe.whitelist()
def enroll_student(lms_course, student):
    """Enroll a student in an LMS course (if self-enrollment is allowed)"""
    course = frappe.get_doc("LMS Course", lms_course)

    if not course.allow_self_enrollment:
        frappe.throw(_("Self enrollment is not allowed for this course"))

    if course.enrollment_deadline and getdate(course.enrollment_deadline) < getdate(today()):
        frappe.throw(_("Enrollment deadline has passed"))

    if course.max_students and course.enrolled_students >= course.max_students:
        frappe.throw(_("Course has reached maximum enrollment capacity"))

    # Check if student is already enrolled
    existing = frappe.db.exists("LMS Enrollment", {
        "lms_course": lms_course,
        "student": student
    })

    if existing:
        frappe.throw(_("Student is already enrolled in this course"))

    # Create enrollment record
    enrollment = frappe.get_doc({
        "doctype": "LMS Enrollment",
        "lms_course": lms_course,
        "student": student,
        "enrollment_date": today()
    })
    enrollment.insert(ignore_permissions=True)

    # Update course statistics
    course.update_statistics()

    return {"message": _("Successfully enrolled in the course")}

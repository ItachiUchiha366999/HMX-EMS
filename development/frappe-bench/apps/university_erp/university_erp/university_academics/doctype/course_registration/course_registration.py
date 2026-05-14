# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CourseRegistration(Document):
    def validate(self):
        """Validate course registration"""
        self.calculate_total_credits()
        self.validate_prerequisites()
        self.validate_no_duplicates()

    def calculate_total_credits(self):
        """Calculate total credits from courses"""
        total = 0.0
        for course in self.courses or []:
            total += course.credits or 0.0
        self.total_credits = total

    def validate_prerequisites(self):
        """Check if student has completed prerequisites"""
        # Will be implemented with CBCS validation
        pass

    def validate_no_duplicates(self):
        """A student cannot register the same course twice in the same term."""
        seen = set()
        for c in self.courses or []:
            key = (c.course, self.academic_term)
            if key in seen:
                frappe.throw(_("Duplicate course in registration: {0}").format(c.course))
            seen.add(key)

    def on_update(self):
        """When workflow_state hits 'Approved', create Course Enrollment rows
        for every course in the registration so they show up on the student's
        portal academics page. Idempotent.
        """
        if getattr(self, "workflow_state", None) != "Approved":
            return

        program_enrollment = frappe.db.get_value(
            "Program Enrollment",
            {"student": self.student, "program": self.program, "docstatus": 1},
            "name",
        ) if self.program else frappe.db.get_value(
            "Program Enrollment",
            {"student": self.student, "academic_term": self.academic_term, "docstatus": 1},
            "name",
        )
        if not program_enrollment:
            frappe.log_error(
                title=f"Course Registration {self.name}",
                message=f"No Program Enrollment for {self.student} — cannot create Course Enrollments.",
            )
            return

        # Pick an enrollment_date inside the term window
        term_start = frappe.db.get_value("Academic Term", self.academic_term, "term_start_date") if self.academic_term else None
        today = frappe.utils.getdate(frappe.utils.nowdate())
        if term_start and frappe.utils.getdate(term_start) > today:
            enroll_date = term_start
        else:
            enroll_date = frappe.utils.nowdate()

        program_name = frappe.db.get_value("Program Enrollment", program_enrollment, "program")
        student_name = frappe.db.get_value("Student", self.student, "student_name")

        created = 0
        for c in self.courses or []:
            if frappe.db.exists("Course Enrollment", {
                "student": self.student,
                "course": c.course,
                "program_enrollment": program_enrollment,
            }):
                continue
            ce = frappe.get_doc({
                "doctype": "Course Enrollment",
                "student": self.student,
                "student_name": student_name,
                "course": c.course,
                "program": program_name,
                "program_enrollment": program_enrollment,
                "enrollment_date": enroll_date,
            })
            ce.flags.ignore_permissions = True
            ce.insert(ignore_permissions=True)
            created += 1

        if created:
            frappe.msgprint(
                _("{0} courses enrolled for {1}.").format(created, student_name),
                indicator="green",
                alert=True,
            )


# =============================================================================
# Public API for the student portal "Register for Semester" button
# =============================================================================

@frappe.whitelist()
def get_registrable_courses(academic_term=None):
    """Return courses the current student can register for in the given term."""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student record not found"), frappe.PermissionError)

    if not academic_term:
        academic_term = frappe.db.get_value(
            "Academic Term", {}, "name", order_by="creation desc",
        )

    pe = frappe.db.get_value(
        "Program Enrollment",
        {"student": student.name, "docstatus": 1},
        ["name", "program"],
        as_dict=True,
        order_by="creation desc",
    )
    if not pe:
        return {"courses": [], "academic_term": academic_term, "program": None}

    already = {r[0] for r in frappe.db.sql(
        "SELECT course FROM `tabCourse Enrollment` WHERE student=%s", student.name
    )}

    available = []
    seen = set()

    program_doc = frappe.get_doc("Program", pe.program)
    for c in program_doc.courses or []:
        if c.course in already or c.course in seen:
            continue
        seen.add(c.course)
        available.append({
            "course": c.course,
            "course_name": getattr(c, "course_name", None) or c.course,
            "credits": 3,
            "required": getattr(c, "required", 0),
        })

    # Always also include Student Group courses (for programs that don't list courses)
    sg_courses = frappe.db.sql("""
        SELECT DISTINCT sg.course, c.course_name
        FROM `tabStudent Group` sg
        JOIN `tabCourse` c ON c.name = sg.course
        WHERE sg.program = %s AND sg.course IS NOT NULL AND sg.course != ''
    """, pe.program, as_dict=True)
    for row in sg_courses:
        if row.course in already or row.course in seen:
            continue
        seen.add(row.course)
        available.append({
            "course": row.course,
            "course_name": row.course_name or row.course,
            "credits": 3,
            "required": 0,
        })

    # Add electives — courses from OTHER programs the student isn't already in.
    # Capped at 10 so the picker stays manageable.
    if len(available) < 10:
        electives = frappe.db.sql("""
            SELECT DISTINCT sg.course, c.course_name
            FROM `tabStudent Group` sg
            JOIN `tabCourse` c ON c.name = sg.course
            WHERE sg.course IS NOT NULL AND sg.course != ''
              AND sg.program != %s
            LIMIT 20
        """, pe.program, as_dict=True)
        for row in electives:
            if row.course in already or row.course in seen:
                continue
            seen.add(row.course)
            available.append({
                "course": row.course,
                "course_name": row.course_name or row.course,
                "credits": 3,
                "required": 0,
            })
            if len(available) >= 10:
                break

    return {
        "courses": available,
        "academic_term": academic_term,
        "program": pe.program,
        "student": student.name,
        "student_name": frappe.db.get_value("Student", student.name, "student_name"),
    }


@frappe.whitelist()
def submit_registration(courses, academic_term=None):
    """Create a Course Registration in Draft state from the student portal."""
    import json
    if isinstance(courses, str):
        courses = json.loads(courses)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("Student record not found"), frappe.PermissionError)
    if not courses:
        frappe.throw(_("Pick at least one course"))

    if not academic_term:
        academic_term = frappe.db.get_value("Academic Term", {}, "name", order_by="creation desc")

    program = frappe.db.get_value(
        "Program Enrollment",
        {"student": student.name, "docstatus": 1},
        "program",
        order_by="creation desc",
    )

    cr = frappe.get_doc({
        "doctype": "Course Registration",
        "student": student.name,
        "student_name": frappe.db.get_value("Student", student.name, "student_name"),
        "academic_term": academic_term,
        "program": program,
        "registration_date": frappe.utils.nowdate(),
        "courses": [
            {
                "course": c.get("course"),
                "course_name": c.get("course_name"),
                "credits": c.get("credits") or 3,
                "course_type": "Core" if c.get("required") else "Elective",
                "is_elective": 0 if c.get("required") else 1,
            }
            for c in courses
        ],
    })
    cr.flags.ignore_permissions = True
    cr.insert(ignore_permissions=True)

    # Immediately push the registration to "Pending Faculty Approval" — students
    # don't have desk access so they can't click the workflow button themselves,
    # and the workflow's "Submit for Approval" transition requires the University
    # Admin role which students don't have. We set the state directly instead;
    # the registrar still has to click Approve/Reject from there.
    cr.db_set("workflow_state", "Pending Faculty Approval", update_modified=False)
    cr.workflow_state = "Pending Faculty Approval"

    return {
        "name": cr.name,
        "total_credits": cr.total_credits,
        "course_count": len(cr.courses),
        "workflow_state": cr.workflow_state,
    }


@frappe.whitelist()
def get_my_registrations():
    """Return all Course Registrations for the current student."""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        return []

    rows = frappe.db.sql("""
        SELECT name, academic_term, program, total_credits, workflow_state, registration_date,
               (SELECT COUNT(*) FROM `tabCourse Registration Item` WHERE parent=cr.name) as course_count
        FROM `tabCourse Registration` cr
        WHERE student = %s
        ORDER BY creation DESC
    """, student.name, as_dict=True)
    return rows

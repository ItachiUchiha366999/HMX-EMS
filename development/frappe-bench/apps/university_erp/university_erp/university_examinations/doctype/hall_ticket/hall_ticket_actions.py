"""Server-side helpers for the Hall Ticket desk-side actions:

- issue_hall_ticket(student): creates a draft Hall Ticket pre-populated with
  one row per enrolled course in the current academic term.
- enter_results(hall_ticket, results): bulk-creates Assessment Result rows
  from a Registrar-supplied dict of course → marks.
"""

import frappe
from frappe import _


@frappe.whitelist()
def issue_hall_ticket(student, academic_term=None, exam_type="Regular"):
    """Create a draft Hall Ticket for the given student.

    Pulls the student's currently-enrolled courses from `Course Enrollment`
    via the latest Program Enrollment. Each enrolled course becomes a row
    in the Hall Ticket Exam child table.
    """
    if not frappe.db.exists("Student", student):
        frappe.throw(_("Student {0} not found").format(student))

    student_doc = frappe.get_doc("Student", student)
    pe = frappe.db.get_value(
        "Program Enrollment",
        {"student": student, "docstatus": 1},
        ["name", "program", "academic_term"],
        as_dict=True,
        order_by="creation desc",
    )
    if not pe:
        frappe.throw(_("No active Program Enrollment for {0}").format(student))

    if not academic_term:
        academic_term = pe.academic_term

    # Don't double-issue
    existing = frappe.db.get_value(
        "Hall Ticket",
        {"student": student, "academic_term": academic_term, "exam_type": exam_type},
        "name",
    )
    if existing:
        frappe.throw(_("Hall Ticket {0} already exists for {1} in {2}").format(
            existing, student, academic_term))

    # Pull enrolled courses
    courses = frappe.db.get_all(
        "Course Enrollment",
        filters={"student": student, "program_enrollment": pe.name},
        fields=["course"],
    )
    if not courses:
        frappe.throw(_("No Course Enrollments for {0}").format(student))

    ht = frappe.get_doc({
        "doctype": "Hall Ticket",
        "student": student,
        "student_name": student_doc.student_name,
        "enrollment_number": getattr(student_doc, "custom_enrollment_number", None) or student,
        "academic_term": academic_term,
        "exam_type": exam_type,
        "issue_date": frappe.utils.nowdate(),
        "verification_code": frappe.generate_hash(length=10).upper(),
        "is_eligible": 1,
        "exams": [],
    })

    # Pick a default room as fallback when no Exam Schedule exists.
    default_room = frappe.db.get_value("Room", {}, "name") or None

    # For each enrolled course, find the matching Exam Schedule (if any)
    # and copy date/time/venue. Otherwise leave blank — registrar fills it.
    for c in courses:
        es = frappe.db.get_value(
            "Exam Schedule",
            {"course": c.course, "academic_term": academic_term, "docstatus": 1},
            ["exam_date", "start_time", "venue"],
            as_dict=True,
            order_by="exam_date asc",
        )
        ht.append("exams", {
            "course": c.course,
            "course_name": c.course,
            "exam_date": es.exam_date if es else frappe.utils.add_days(frappe.utils.nowdate(), 14),
            "exam_time": es.start_time if es else "10:00:00",
            "venue": (es.venue if es else default_room) or default_room,
        })

    ht.flags.ignore_permissions = True
    ht.insert(ignore_permissions=True)

    return {
        "name": ht.name,
        "student": ht.student,
        "exam_count": len(ht.exams),
        "workflow_state": ht.workflow_state,
    }


@frappe.whitelist()
def enter_results(hall_ticket, results):
    """Bulk-create Assessment Result rows from a Hall Ticket.

    `results` is a list of dicts: [{"course": "...", "total_score": 75, "maximum_score": 100}, ...]
    Each row is inserted + submitted as an Assessment Result.
    Idempotent — skips courses that already have a Result for this student+term.
    """
    import json
    if isinstance(results, str):
        results = json.loads(results)

    ht = frappe.get_doc("Hall Ticket", hall_ticket)
    if ht.docstatus != 1 or ht.workflow_state != "Issued":
        frappe.throw(_("Hall Ticket must be in 'Issued' state to enter results"))

    grading_scale = frappe.db.get_value("Grading Scale", {}, "name") or ""

    created = []
    skipped = []
    for r in results:
        course = r.get("course")
        score = float(r.get("total_score") or 0)
        max_score = float(r.get("maximum_score") or 100)

        if frappe.db.exists("Assessment Result", {
            "student": ht.student, "course": course, "academic_term": ht.academic_term,
        }):
            skipped.append(course)
            continue

        # Find the Student Group the student belongs to for this course (Education app
        # validation requires student to be a member of the group named on the AR).
        student_group = frappe.db.sql("""
            SELECT sg.name
            FROM `tabStudent Group` sg
            JOIN `tabStudent Group Student` sgs ON sgs.parent = sg.name
            WHERE sgs.student = %s AND sg.course = %s
            LIMIT 1
        """, (ht.student, course))
        student_group = student_group[0][0] if student_group else None

        program = frappe.db.get_value("Course Enrollment",
            {"student": ht.student, "course": course}, "program") \
            or frappe.db.get_value("Program Enrollment",
                {"student": ht.student, "docstatus": 1}, "program")

        # If no group exists, create a per-course exam group and add the student.
        if not student_group:
            student_group = _ensure_exam_group(course, ht.academic_term, program, ht.student, ht.student_name)

        # Assessment Plan is mandatory on Assessment Result. Find or create one
        # for (course, term, group, exam_type).
        plan = _ensure_assessment_plan(
            course=course,
            academic_term=ht.academic_term,
            program=program,
            student_group=student_group,
            grading_scale=grading_scale,
            exam_name=ht.exam_type,
            max_score=max_score,
        )

        ar = frappe.get_doc({
            "doctype": "Assessment Result",
            "student": ht.student,
            "student_name": ht.student_name,
            "course": course,
            "student_group": student_group,
            "assessment_plan": plan,
            "program": program,
            "academic_year": frappe.db.get_value("Academic Term", ht.academic_term, "academic_year"),
            "academic_term": ht.academic_term,
            "grading_scale": grading_scale,
            "maximum_score": max_score,
            "total_score": score,
            "grade": _grade_for(score, max_score),
            "custom_percentage": round((score / max_score) * 100, 2) if max_score else 0,
            "details": [{
                "assessment_criteria": ht.exam_type or "Final",
                "maximum_score": max_score,
                "score": score,
                "grade": _grade_for(score, max_score),
            }],
        })
        ar.flags.ignore_permissions = True
        ar.insert(ignore_permissions=True)
        try:
            ar.submit()
        except Exception as e:
            frappe.log_error(title=f"Assessment Result submit failed for {ar.name}", message=str(e))
        created.append({"name": ar.name, "course": course, "score": score, "grade": ar.grade})

    return {"created": created, "skipped": skipped, "hall_ticket": ht.name}


def _ensure_exam_group(course, academic_term, program, student, student_name):
    """Find or create a Student Group for (course, term, program) and add student."""
    sg_name = frappe.db.get_value("Student Group", {
        "course": course, "academic_term": academic_term, "program": program,
    }, "name")
    if not sg_name:
        sg = frappe.get_doc({
            "doctype": "Student Group",
            "student_group_name": f"{program}-{course}-{academic_term}"[:140],
            "group_based_on": "Course",
            "course": course,
            "academic_term": academic_term,
            "academic_year": frappe.db.get_value("Academic Term", academic_term, "academic_year"),
            "program": program,
        })
        sg.flags.ignore_permissions = True
        sg.insert(ignore_permissions=True)
        sg_name = sg.name
    if not frappe.db.exists("Student Group Student", {"parent": sg_name, "student": student}):
        sg_doc = frappe.get_doc("Student Group", sg_name)
        sg_doc.append("students", {"student": student, "student_name": student_name, "active": 1})
        sg_doc.flags.ignore_permissions = True
        sg_doc.save(ignore_permissions=True)
    return sg_name


def _ensure_assessment_plan(course, academic_term, program, student_group, grading_scale, exam_name, max_score):
    """Find or create a submitted Assessment Plan for the course/term/group."""
    name = frappe.db.get_value("Assessment Plan", {
        "course": course,
        "academic_term": academic_term,
        "student_group": student_group,
        "assessment_name": exam_name,
    }, "name")
    if name:
        return name

    # Ensure Assessment Criteria master exists for this exam type
    if not frappe.db.exists("Assessment Criteria", exam_name):
        ac = frappe.get_doc({
            "doctype": "Assessment Criteria",
            "assessment_criteria": exam_name,
        })
        ac.flags.ignore_permissions = True
        ac.insert(ignore_permissions=True)

    # Find or create an Assessment Group (Education app uses NestedSet — must be a tree)
    assessment_group = frappe.db.get_value("Assessment Group", {"is_group": 0}, "name")
    if not assessment_group:
        root_name = frappe.db.get_value("Assessment Group", {"is_group": 1}, "name")
        if not root_name:
            root = frappe.get_doc({
                "doctype": "Assessment Group",
                "assessment_group_name": "All Assessment Groups",
                "is_group": 1,
                "parent_assessment_group": None,
            })
            root.flags.ignore_permissions = True
            root.flags.ignore_mandatory = True
            root.insert(ignore_permissions=True)
            root_name = root.name
        ag = frappe.get_doc({
            "doctype": "Assessment Group",
            "assessment_group_name": "Examinations",
            "parent_assessment_group": root_name,
            "is_group": 0,
        })
        ag.flags.ignore_permissions = True
        ag.insert(ignore_permissions=True)
        assessment_group = ag.name

    ap = frappe.get_doc({
        "doctype": "Assessment Plan",
        "assessment_name": exam_name,
        "course": course,
        "program": program,
        "academic_year": frappe.db.get_value("Academic Term", academic_term, "academic_year"),
        "academic_term": academic_term,
        "student_group": student_group,
        "assessment_group": assessment_group,
        "grading_scale": grading_scale,
        "maximum_assessment_score": max_score,
        "schedule_date": frappe.utils.nowdate(),
        "assessment_criteria": [{
            "assessment_criteria": exam_name,
            "maximum_score": max_score,
        }],
    })
    ap.flags.ignore_permissions = True
    ap.flags.ignore_mandatory = True
    ap.insert(ignore_permissions=True)
    try:
        ap.submit()
    except Exception:
        pass
    return ap.name


def _grade_for(score, max_score):
    """Map percentage to a 10-point grade."""
    pct = (score / max_score) * 100 if max_score else 0
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B+"
    if pct >= 60: return "B"
    if pct >= 50: return "C"
    if pct >= 40: return "D"
    return "F"

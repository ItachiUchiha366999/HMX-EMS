# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, getdate


def get_context(context):
    """Placement Portal context for students"""
    context.no_cache = 1
    context.title = _("Placement Portal")

    user = frappe.session.user

    if user == "Guest":
        context.is_logged_in = False
        context.open_jobs = get_public_jobs()
        return

    context.is_logged_in = True

    # Get student record
    student = frappe.db.get_value("Student", {"user": user}, "name")
    if not student:
        context.is_student = False
        context.message = _("This portal is for students only.")
        return

    context.is_student = True
    context.student = frappe.get_doc("Student", student)

    # Get or check resume
    resume = frappe.db.get_value("Student Resume", {"student": student}, "*", as_dict=True)
    context.resume = resume
    context.has_resume = bool(resume)

    if resume:
        context.resume_completeness = calculate_resume_completeness(resume)

    # Get eligible jobs
    context.eligible_jobs = get_eligible_jobs(student, context.student)

    # Get student's applications
    context.applications = get_student_applications(student)

    # Get upcoming drives
    context.upcoming_drives = get_upcoming_drives()

    # Get placement statistics
    context.stats = get_placement_stats(context.student.get("program"))


def get_public_jobs():
    """Get open jobs for non-logged in users"""
    return frappe.db.sql("""
        SELECT
            pjo.name,
            pjo.job_title,
            pc.company_name,
            pjo.job_type,
            pjo.ctc_min,
            pjo.ctc_max,
            pjo.application_deadline,
            pjo.location
        FROM `tabPlacement Job Opening` pjo
        JOIN `tabPlacement Company` pc ON pjo.company = pc.name
        WHERE pjo.status = 'Open'
        AND pjo.application_deadline >= %s
        ORDER BY pjo.application_deadline
        LIMIT 10
    """, (nowdate(),), as_dict=True)


def get_eligible_jobs(student, student_doc):
    """Get jobs student is eligible for"""
    jobs = frappe.db.sql("""
        SELECT
            pjo.name,
            pjo.job_title,
            pjo.company,
            pc.company_name,
            pjo.job_type,
            pjo.ctc_min,
            pjo.ctc_max,
            pjo.application_deadline,
            pjo.location,
            pjo.min_cgpa,
            pjo.max_backlogs,
            pjo.description
        FROM `tabPlacement Job Opening` pjo
        JOIN `tabPlacement Company` pc ON pjo.company = pc.name
        WHERE pjo.status = 'Open'
        AND pjo.application_deadline >= %s
        ORDER BY pjo.application_deadline
    """, (nowdate(),), as_dict=True)

    eligible_jobs = []
    student_cgpa = student_doc.get("cgpa") or 0
    student_backlogs = student_doc.get("active_backlogs") or 0

    for job in jobs:
        # Check CGPA
        if job.min_cgpa and student_cgpa < job.min_cgpa:
            continue

        # Check backlogs
        if job.max_backlogs is not None and student_backlogs > job.max_backlogs:
            continue

        # Check if already applied
        job.already_applied = frappe.db.exists("Placement Application", {
            "student": student,
            "job_opening": job.name,
            "docstatus": ["!=", 2]
        })

        eligible_jobs.append(job)

    return eligible_jobs


def get_student_applications(student):
    """Get student's placement applications"""
    return frappe.db.sql("""
        SELECT
            pa.name,
            pa.job_opening,
            pjo.job_title,
            pc.company_name,
            pa.status,
            pa.application_date,
            pa.current_round,
            pjo.ctc_max as package
        FROM `tabPlacement Application` pa
        JOIN `tabPlacement Job Opening` pjo ON pa.job_opening = pjo.name
        JOIN `tabPlacement Company` pc ON pjo.company = pc.name
        WHERE pa.student = %s
        AND pa.docstatus != 2
        ORDER BY pa.application_date DESC
    """, (student,), as_dict=True)


def get_upcoming_drives():
    """Get upcoming placement drives"""
    return frappe.db.sql("""
        SELECT
            pd.name,
            pc.company_name,
            pd.drive_date,
            pd.venue,
            pd.status,
            pjo.job_title,
            pjo.ctc_max as package
        FROM `tabPlacement Drive` pd
        JOIN `tabPlacement Company` pc ON pd.company = pc.name
        LEFT JOIN `tabPlacement Job Opening` pjo ON pd.job_opening = pjo.name
        WHERE pd.drive_date >= %s
        AND pd.status IN ('Scheduled', 'Registration Open')
        ORDER BY pd.drive_date
        LIMIT 5
    """, (nowdate(),), as_dict=True)


def get_placement_stats(program):
    """Get placement statistics for the program"""
    stats = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT pa.student) as total_placed,
            AVG(pjo.ctc_max) as avg_package,
            MAX(pjo.ctc_max) as highest_package
        FROM `tabPlacement Application` pa
        JOIN `tabPlacement Job Opening` pjo ON pa.job_opening = pjo.name
        WHERE pa.status = 'Offer Accepted'
        AND pa.docstatus = 1
    """, as_dict=True)[0]

    return stats


def calculate_resume_completeness(resume):
    """Calculate resume completeness percentage"""
    fields = ["career_objective", "linkedin_url", "resume_file"]
    filled = sum(1 for f in fields if resume.get(f))

    # Check child tables
    if frappe.db.count("Resume Education", {"parent": resume.name}) > 0:
        filled += 1
    if frappe.db.count("Resume Skill", {"parent": resume.name}) > 0:
        filled += 1
    if frappe.db.count("Resume Project", {"parent": resume.name}) > 0:
        filled += 1

    total = len(fields) + 3  # 3 child tables
    return int(filled / total * 100)


@frappe.whitelist()
def apply_for_job(job_opening):
    """Apply for a job opening"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to apply for jobs"))

    student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    if not student:
        frappe.throw(_("Student record not found"))

    # Check if already applied
    existing = frappe.db.exists("Placement Application", {
        "student": student,
        "job_opening": job_opening,
        "docstatus": ["!=", 2]
    })

    if existing:
        frappe.throw(_("You have already applied for this job"))

    # Check resume
    if not frappe.db.exists("Student Resume", {"student": student}):
        frappe.throw(_("Please complete your resume before applying"))

    # Create application
    application = frappe.get_doc({
        "doctype": "Placement Application",
        "student": student,
        "job_opening": job_opening,
        "application_date": nowdate(),
        "status": "Applied"
    })
    application.insert()

    return {"message": _("Application submitted successfully"), "application": application.name}


@frappe.whitelist()
def withdraw_application(application):
    """Withdraw a placement application"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"))

    student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    app_doc = frappe.get_doc("Placement Application", application)

    if app_doc.student != student:
        frappe.throw(_("You can only withdraw your own applications"))

    if app_doc.status not in ["Applied", "Shortlisted"]:
        frappe.throw(_("Cannot withdraw application at this stage"))

    app_doc.status = "Withdrawn"
    app_doc.save()

    return {"message": _("Application withdrawn successfully")}


@frappe.whitelist()
def register_for_drive(drive):
    """Register for a placement drive"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to register"))

    student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    if not student:
        frappe.throw(_("Student record not found"))

    drive_doc = frappe.get_doc("Placement Drive", drive)

    if drive_doc.status not in ["Scheduled", "Registration Open"]:
        frappe.throw(_("Registration is not open for this drive"))

    # Check if already registered
    if drive_doc.job_opening:
        existing = frappe.db.exists("Placement Application", {
            "student": student,
            "job_opening": drive_doc.job_opening,
            "placement_drive": drive
        })
        if existing:
            frappe.throw(_("You are already registered for this drive"))

        # Create application
        application = frappe.get_doc({
            "doctype": "Placement Application",
            "student": student,
            "job_opening": drive_doc.job_opening,
            "placement_drive": drive,
            "application_date": nowdate(),
            "status": "Applied"
        })
        application.insert()

        return {"message": _("Registered successfully"), "application": application.name}

    frappe.throw(_("No job opening linked to this drive"))

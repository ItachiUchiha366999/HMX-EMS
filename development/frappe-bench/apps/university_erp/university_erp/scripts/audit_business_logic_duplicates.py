# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Business Logic Duplicate Audit Script

Analyzes overlapping business logic between Education/ERPNext and university_erp
in four key domains: Fees, Exams, Attendance, Student Data.

Determines authoritative source per domain and integration pattern.
Appends results to existing DUPLICATE_AUDIT.md.

Usage:
    bench --site university.local execute university_erp.scripts.audit_business_logic_duplicates.run
"""

import os
from datetime import datetime, timezone


def _get_output_path():
    """Get the DUPLICATE_AUDIT.md path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apps_root = os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    return os.path.normpath(os.path.join(
        apps_root, "..", "..", ".planning",
        "phases", "03.1-cross-app-integration-audit-accessibility-testing",
        "DUPLICATE_AUDIT.md"
    ))


def _analyze_fees_overlap():
    """
    Analyze Fees domain overlap.

    Education: Fees doctype (fee creation, collection, GL posting)
    university_erp: UniversityFees override, Bulk Fee Generator, Fee Refund,
                    Fee Payment Order, fee_collection_summary, fee_defaulters reports
    """
    return {
        "domain": "Fees / Finance",
        "education_entities": [
            "Fees doctype (fee creation, submission, GL posting via erpnext.accounts)",
            "Fee Component (child table for fee line items)",
            "Fee Schedule (batch fee generation)",
            "Fee Structure (template for fee calculation)",
        ],
        "university_erp_entities": [
            "UniversityFees override (penalty calculation, scholarship, net amount)",
            "Bulk Fee Generator (batch fee creation)",
            "Fee Refund (refund workflow with approval)",
            "Fee Payment Order (payment gateway integration)",
            "fee_collection_summary report",
            "fee_defaulters report",
            "program_wise_fee_report report",
            "GL posting hooks (gl_integration.py, gl_posting.py)",
            "Custom fields: due_date, penalty, scholarship, net_amount, fee_category",
        ],
        "authoritative_source": "Education (Fees doctype)",
        "secondary_source": "university_erp (extends via override + custom fields)",
        "integration_pattern": "EXTEND -- university_erp subclasses Education's Fees via "
            "override_doctype_class. UniversityFees(Fees) adds penalty, scholarship, "
            "net amount calculation. doc_events hooks add GL posting on submit/cancel. "
            "Education owns the core Fees data model; university_erp extends behavior.",
        "risk": "LOW -- Clean extension pattern. university_erp adds custom_* fields "
            "but does not duplicate core fee logic. Dual GL posting hooks "
            "(gl_integration.py AND gl_posting.py) on Fees.on_submit could cause "
            "double GL entries if not idempotent.",
        "recommendation": "KEEP BOTH -- Education Fees is authoritative for data model. "
            "university_erp extends via override. Verify GL posting hooks are not "
            "creating duplicate entries (both registered in hooks.py on_submit).",
    }


def _analyze_exams_overlap():
    """
    Analyze Exams domain overlap.

    Education: Assessment Plan, Assessment Result, Assessment Criteria, Assessment Group
    university_erp: Online Examination, Internal Assessment, Student Exam Attempt,
                    Question Bank, Answer Sheet, Revaluation Request, Practical Examination
    """
    return {
        "domain": "Examinations / Assessment",
        "education_entities": [
            "Assessment Plan (scheduling assessments for courses)",
            "Assessment Result (student grades, docstatus-controlled)",
            "Assessment Criteria (grading criteria definition)",
            "Assessment Group (grouping students for assessment)",
            "Grading Scale (grade-to-percentage mapping)",
        ],
        "university_erp_entities": [
            "UniversityAssessmentResult override (10-point grading, SGPA/CGPA, grade points)",
            "Online Examination (exam session management, proctoring)",
            "Internal Assessment (continuous evaluation)",
            "Student Exam Attempt (per-student exam attempt tracking)",
            "Question Bank (question paper management)",
            "Question Paper (generated papers from bank)",
            "Answer Sheet (answer tracking and evaluation)",
            "Revaluation Request (grade dispute workflow)",
            "Practical Examination (lab/practical exam management)",
            "Hall Ticket (exam admission control)",
            "Examination (exam scheduling, venue, seating)",
        ],
        "authoritative_source": "Education (Assessment Result for grades), university_erp (exam logistics)",
        "secondary_source": "Complementary -- not duplicative",
        "integration_pattern": "COMPLEMENT -- Education owns grading (Assessment Plan -> "
            "Assessment Result). university_erp adds exam logistics layer on top "
            "(Online Examination -> Student Exam Attempt -> Answer Sheet -> "
            "Assessment Result via override). UniversityAssessmentResult(AssessmentResult) "
            "adds 10-point grading scale and CGPA calculation.",
        "risk": "LOW -- Clear separation. Education = grading data model. "
            "university_erp = exam delivery + logistics. Override extends "
            "Assessment Result with grade points and CGPA.",
        "recommendation": "KEEP BOTH -- Complementary systems. Education Assessment Result "
            "is authoritative for grade data. university_erp exam doctypes handle "
            "logistics that Education does not cover.",
    }


def _analyze_attendance_overlap():
    """
    Analyze Attendance domain overlap.

    Education: Student Attendance doctype
    university_erp: Hostel Attendance, Biometric Attendance Log,
                    faculty_api.submit_attendance creates Student Attendance records
    """
    return {
        "domain": "Attendance",
        "education_entities": [
            "Student Attendance (per-student, per-course daily attendance record)",
            "Student Attendance Tool (bulk attendance marking page)",
        ],
        "university_erp_entities": [
            "Hostel Attendance (hostel-specific attendance, separate from academic)",
            "Biometric Attendance Log (hardware integration for automated attendance)",
            "faculty_api.submit_attendance() -- creates Student Attendance records via API",
            "attendance.py (university_academics) -- attendance summary/analytics",
        ],
        "authoritative_source": "Education (Student Attendance doctype)",
        "secondary_source": "university_erp (creates records in Education's Student Attendance)",
        "integration_pattern": "CREATE-INTO -- university_erp creates records directly in "
            "Education's Student Attendance table via faculty_api.submit_attendance(). "
            "Hostel Attendance is a separate parallel system (different context, not academic). "
            "Biometric Attendance Log is an input source that could feed into Student Attendance.",
        "risk": "MEDIUM -- faculty_api.submit_attendance() creates Student Attendance "
            "records with idempotency check (frappe.db.count before insert). "
            "However, if both Student Attendance Tool and faculty_api are used for "
            "same course/date, duplicates could occur if idempotency check is bypassed.",
        "recommendation": "KEEP BOTH -- Education Student Attendance is authoritative data store. "
            "university_erp provides alternative input channels (API, biometric). "
            "Ensure idempotency check in faculty_api covers all uniqueness constraints.",
    }


def _analyze_student_data_overlap():
    """
    Analyze Student data overlap.

    Education: Student doctype with programs, courses, enrollment
    university_erp: UniversityStudent override, custom fields
    """
    return {
        "domain": "Student Data",
        "education_entities": [
            "Student doctype (core student record -- name, email, enrollment)",
            "Student Group (class/section grouping)",
            "Program Enrollment (student-program mapping)",
            "Course Enrollment (student-course mapping)",
            "Student Applicant (admission pipeline)",
        ],
        "university_erp_entities": [
            "UniversityStudent override (enrollment number validation, CGPA calc, category cert)",
            "UniversityApplicant override (extends Student Applicant)",
            "Custom fields: enrollment_number, cgpa, category, category_certificate, student_status",
            "Permission query conditions (role-based student list visibility)",
            "Student query (custom search in link fields)",
        ],
        "authoritative_source": "Education (Student doctype)",
        "secondary_source": "university_erp (extends via override + custom fields)",
        "integration_pattern": "EXTEND -- university_erp subclasses Education's Student via "
            "override_doctype_class. UniversityStudent(Student) adds enrollment number "
            "uniqueness validation, CGPA auto-calculation from Assessment Results, "
            "category certificate validation. Custom fields add university-specific data.",
        "risk": "LOW -- Clean extension pattern. No data duplication. "
            "Permission query conditions add role-based access control.",
        "recommendation": "KEEP BOTH -- Education Student is authoritative. university_erp "
            "extends with university-specific validation and computed fields.",
    }


def _generate_business_logic_section():
    """Generate the Business Logic Overlaps section for DUPLICATE_AUDIT.md."""
    analyses = [
        _analyze_fees_overlap(),
        _analyze_exams_overlap(),
        _analyze_attendance_overlap(),
        _analyze_student_data_overlap(),
    ]

    lines = []
    lines.append("")
    lines.append("## Business Logic Overlaps")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")
    lines.append("Analysis of overlapping business logic between Education/ERPNext and university_erp "
                  "in four key domains. Each overlap area identifies the authoritative source, "
                  "integration pattern, risk level, and recommendation.")
    lines.append("")

    for analysis in analyses:
        lines.append(f"### {analysis['domain']}")
        lines.append("")

        lines.append("**Education Entities:**")
        for entity in analysis["education_entities"]:
            lines.append(f"- {entity}")
        lines.append("")

        lines.append("**university_erp Entities:**")
        for entity in analysis["university_erp_entities"]:
            lines.append(f"- {entity}")
        lines.append("")

        lines.append(f"**Authoritative Source:** {analysis['authoritative_source']}")
        lines.append(f"**Integration Pattern:** {analysis['integration_pattern']}")
        lines.append(f"**Risk:** {analysis['risk']}")
        lines.append(f"**Recommendation:** {analysis['recommendation']}")
        lines.append("")

    # Authoritative Source Summary
    lines.append("## Authoritative Source Summary")
    lines.append("")
    lines.append("| Domain | Authoritative App | Secondary App | Pattern | Risk |")
    lines.append("|--------|-------------------|---------------|---------|------|")

    summary_rows = [
        ("Fees / Finance", "Education (Fees doctype)", "university_erp (override + custom fields)",
         "EXTEND", "LOW"),
        ("Examinations / Assessment", "Education (Assessment Result) + university_erp (exam logistics)",
         "Complementary", "COMPLEMENT", "LOW"),
        ("Attendance", "Education (Student Attendance)",
         "university_erp (creates records via API)", "CREATE-INTO", "MEDIUM"),
        ("Student Data", "Education (Student doctype)",
         "university_erp (override + custom fields)", "EXTEND", "LOW"),
    ]

    for domain, auth, secondary, pattern, risk in summary_rows:
        lines.append(f"| {domain} | {auth} | {secondary} | {pattern} | {risk} |")
    lines.append("")

    lines.append("### Integration Pattern Legend")
    lines.append("")
    lines.append("| Pattern | Meaning |")
    lines.append("|---------|---------|")
    lines.append("| EXTEND | university_erp subclasses Education doctype via override_doctype_class, adds custom fields |")
    lines.append("| COMPLEMENT | Different apps handle different aspects of the same domain (no duplication) |")
    lines.append("| CREATE-INTO | university_erp creates records directly in Education's tables |")
    lines.append("| REPLACE | university_erp replaces Education functionality (requires migration) |")
    lines.append("")

    return "\n".join(lines)


def run():
    """
    Main entry point. Run via:
        bench --site university.local execute university_erp.scripts.audit_business_logic_duplicates.run
    """
    print("=" * 70)
    print("BUSINESS LOGIC DUPLICATE AUDIT")
    print("=" * 70)

    output_path = _get_output_path()
    print(f"\nOutput file: {output_path}")

    # Generate the business logic section
    print("\nAnalyzing business logic overlaps...")
    business_logic_section = _generate_business_logic_section()

    # Read existing DUPLICATE_AUDIT.md
    existing_content = ""
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            existing_content = f.read()
        print(f"  Read existing file ({len(existing_content)} chars)")
    else:
        print("  No existing DUPLICATE_AUDIT.md found, creating new file")

    # Check if business logic section already exists
    if "## Business Logic Overlaps" in existing_content:
        # Replace existing section
        marker = "## Business Logic Overlaps"
        idx = existing_content.index(marker)
        # Keep everything before the marker
        existing_content = existing_content[:idx].rstrip()
        print("  Replacing existing Business Logic Overlaps section")

    # Append the new section
    updated_content = existing_content + "\n" + business_logic_section

    with open(output_path, "w") as f:
        f.write(updated_content)

    print(f"\nUpdated: {output_path}")
    print("\nDomains analyzed:")
    print("  1. Fees / Finance -- Authoritative: Education, Pattern: EXTEND, Risk: LOW")
    print("  2. Examinations / Assessment -- Authoritative: Education + university_erp, Pattern: COMPLEMENT, Risk: LOW")
    print("  3. Attendance -- Authoritative: Education, Pattern: CREATE-INTO, Risk: MEDIUM")
    print("  4. Student Data -- Authoritative: Education, Pattern: EXTEND, Risk: LOW")
    print("\n" + "=" * 70)
    print("BUSINESS LOGIC DUPLICATE AUDIT COMPLETE")
    print("=" * 70)

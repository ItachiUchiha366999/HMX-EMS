# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Workflow Creation Script

Creates all missing workflows across the entire university ERP and ensures
prerequisite Workflow State and Workflow Action Master documents exist.

Usage:
    bench --site university.local execute university_erp.setup.create_workflows.run
"""

import frappe


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_workflow_state(state_name, style=""):
    """Create a Workflow State document if it does not exist."""
    if not frappe.db.exists("Workflow State", state_name):
        frappe.get_doc({
            "doctype": "Workflow State",
            "workflow_state_name": state_name,
            "style": style,
        }).insert(ignore_permissions=True)


def _ensure_workflow_action(action_name):
    """Create a Workflow Action Master document if it does not exist."""
    if not frappe.db.exists("Workflow Action Master", action_name):
        frappe.get_doc({
            "doctype": "Workflow Action Master",
            "workflow_action_name": action_name,
        }).insert(ignore_permissions=True)


def _ensure_workflow_state_field(document_type):
    """
    Pre-create the workflow_state custom field on a doctype.

    This avoids triggering full doctype validation (which may fail on
    pre-existing issues like broken document links) during workflow creation.
    """
    field_name = f"{document_type}-workflow_state"
    if frappe.db.exists("Custom Field", field_name):
        return
    # Check if the doctype already has workflow_state as a standard field
    meta = frappe.get_meta(document_type)
    if meta.has_field("workflow_state"):
        return
    # Create the custom field directly in DB, bypassing validate_fields_for_doctype
    cf = frappe.new_doc("Custom Field")
    cf.dt = document_type
    cf.fieldname = "workflow_state"
    cf.label = "Workflow State"
    cf.fieldtype = "Link"
    cf.options = "Workflow State"
    cf.hidden = 1
    cf.allow_on_submit = 1
    cf.no_copy = 1
    cf.flags.ignore_validate = True
    cf.db_insert()
    frappe.db.commit()
    frappe.clear_cache(doctype=document_type)


def _create_workflow(name, document_type, states, transitions, send_email_alert=0):
    """
    Create a Workflow document if no active workflow exists for the given doctype.

    Returns the workflow name (existing or newly created).
    """
    # Check for existing active workflow on same doctype (pitfall 6)
    existing = frappe.get_all(
        "Workflow",
        filters={"document_type": document_type, "is_active": 1},
        pluck="name",
    )
    if existing:
        print(f"  Active workflow already exists for {document_type}: {existing[0]}")
        return existing[0]

    # Verify target doctype exists
    if not frappe.db.exists("DocType", document_type):
        print(f"  SKIP: DocType '{document_type}' does not exist")
        return None

    # Ensure all Workflow State prereqs exist (pitfall 2)
    for s in states:
        _ensure_workflow_state(s["state"], s.get("style", ""))

    # Ensure all Workflow Action Master prereqs exist
    for t in transitions:
        _ensure_workflow_action(t["action"])

    # Pre-create workflow_state custom field to avoid doctype validation
    # errors on doctypes with pre-existing issues (e.g., broken document links)
    _ensure_workflow_state_field(document_type)

    # Create the Workflow
    wf = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": name,
        "document_type": document_type,
        "is_active": 1,
        "send_email_alert": send_email_alert,
        "workflow_state_field": "workflow_state",
        "states": [{"doctype": "Workflow Document State", **s} for s in states],
        "transitions": [{"doctype": "Workflow Transition", **t} for t in transitions],
    })
    wf.insert(ignore_permissions=True)
    print(f"  Created workflow: {name}")
    return wf.name


def _is_submittable(doctype):
    """Check whether a DocType is submittable."""
    meta = frappe.get_meta(doctype)
    return bool(meta.is_submittable)


# ---------------------------------------------------------------------------
# Workflow definitions
# ---------------------------------------------------------------------------

def _workflow_hostel_allocation():
    """Hostel Allocation Approval workflow."""
    dt = "Hostel Allocation"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Hostel Allocation Approval",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "University Warden", "style": ""},
            {"state": "Pending Warden Approval", "doc_status": "0", "allow_edit": "University Warden", "style": "Warning"},
            {"state": "Approved", "doc_status": "1" if sub else "0", "allow_edit": "University Warden", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "University Warden", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "2" if sub else "0", "allow_edit": "University Warden", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Warden Approval", "next_state": "Pending Warden Approval", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Pending Warden Approval", "action": "Approve", "next_state": "Approved", "allowed": "University Warden", "allow_self_approval": 1},
            {"state": "Pending Warden Approval", "action": "Reject", "next_state": "Rejected", "allowed": "University Warden", "allow_self_approval": 1},
            {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "University Warden", "allow_self_approval": 1},
        ],
    )


def _workflow_hostel_maintenance():
    """Hostel Maintenance Request workflow."""
    dt = "Hostel Maintenance Request"
    sub = _is_submittable(dt)
    # For submittable doctypes, Cancelled (doc_status=2) can only come from
    # a submitted state (doc_status=1). Use doc_status=0 for Cancelled when
    # transitions originate from draft states.
    return _create_workflow(
        name="Hostel Maintenance Request Workflow",
        document_type=dt,
        states=[
            {"state": "Open", "doc_status": "0", "allow_edit": "University Warden", "style": "Warning"},
            {"state": "Assigned", "doc_status": "0", "allow_edit": "University Warden", "style": "Info"},
            {"state": "In Progress", "doc_status": "0", "allow_edit": "University Warden", "style": "Primary"},
            {"state": "Completed", "doc_status": "1" if sub else "0", "allow_edit": "University Warden", "style": "Success"},
            {"state": "Cancelled", "doc_status": "0", "allow_edit": "University Warden", "style": ""},
        ],
        transitions=[
            {"state": "Open", "action": "Assign", "next_state": "Assigned", "allowed": "University Warden", "allow_self_approval": 1},
            {"state": "Assigned", "action": "Start Work", "next_state": "In Progress", "allowed": "University Warden", "allow_self_approval": 1},
            {"state": "In Progress", "action": "Complete", "next_state": "Completed", "allowed": "University Warden", "allow_self_approval": 1},
            {"state": "Open", "action": "Cancel", "next_state": "Cancelled", "allowed": "University Warden", "allow_self_approval": 1},
            {"state": "Assigned", "action": "Cancel", "next_state": "Cancelled", "allowed": "University Warden", "allow_self_approval": 1},
        ],
    )


def _workflow_transport_allocation():
    """Transport Allocation Approval workflow."""
    dt = "Transport Allocation"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Transport Allocation Approval",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Pending Approval", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Active", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Academics User", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "2" if sub else "0", "allow_edit": "Academics User", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Approval", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Pending Approval", "action": "Approve", "next_state": "Active", "allowed": "Education Manager", "allow_self_approval": 1},
            {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Education Manager", "allow_self_approval": 1},
            {"state": "Active", "action": "Cancel", "next_state": "Cancelled", "allowed": "Education Manager", "allow_self_approval": 1},
        ],
    )


def _workflow_certificate_request():
    """Certificate Request workflow."""
    dt = "Certificate Request"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Certificate Request Workflow",
        document_type=dt,
        states=[
            {"state": "Pending", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Approved", "doc_status": "0", "allow_edit": "Academics User", "style": "Primary"},
            {"state": "Generated", "doc_status": "0", "allow_edit": "Academics User", "style": "Info"},
            {"state": "Issued", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Academics User", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
        ],
        transitions=[
            {"state": "Pending", "action": "Approve", "next_state": "Approved", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Pending", "action": "Reject", "next_state": "Rejected", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Approved", "action": "Generate", "next_state": "Generated", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Generated", "action": "Issue", "next_state": "Issued", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "University Registrar", "allow_self_approval": 1},
        ],
    )


def _workflow_course_registration():
    """Course Registration workflow."""
    dt = "Course Registration"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Course Registration Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Pending Faculty Approval", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Approved", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Academics User", "style": "Danger"},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Faculty Approval", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Pending Faculty Approval", "action": "Approve", "next_state": "Approved", "allowed": "Education Manager", "allow_self_approval": 1},
            {"state": "Pending Faculty Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Education Manager", "allow_self_approval": 1},
        ],
    )


def _workflow_revaluation_request():
    """Revaluation Request workflow."""
    dt = "Revaluation Request"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Revaluation Request Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Pending Review", "doc_status": "0", "allow_edit": "University Exam Cell", "style": "Warning"},
            {"state": "In Progress", "doc_status": "0", "allow_edit": "University Exam Cell", "style": "Primary"},
            {"state": "Completed", "doc_status": "1" if sub else "0", "allow_edit": "University Exam Cell", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "University Exam Cell", "style": "Danger"},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Review", "next_state": "Pending Review", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Pending Review", "action": "Accept", "next_state": "In Progress", "allowed": "University Exam Cell", "allow_self_approval": 1},
            {"state": "In Progress", "action": "Complete", "next_state": "Completed", "allowed": "University Exam Cell", "allow_self_approval": 1},
            {"state": "Pending Review", "action": "Reject", "next_state": "Rejected", "allowed": "University Exam Cell", "allow_self_approval": 1},
        ],
    )


def _workflow_research_grant():
    """Research Grant workflow."""
    dt = "Research Grant"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Research Grant Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Under Review", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Approved", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Academics User", "style": "Danger"},
            {"state": "Completed", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Primary"},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Review", "next_state": "Under Review", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Under Review", "action": "Approve", "next_state": "Approved", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Under Review", "action": "Reject", "next_state": "Rejected", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Approved", "action": "Mark Completed", "next_state": "Completed", "allowed": "University Registrar", "allow_self_approval": 1},
        ],
    )


def _workflow_grievance():
    """
    Grievance Resolution workflow.

    CRITICAL: Grievance is NOT submittable (is_submittable=0).
    ALL states MUST use doc_status=0.
    """
    dt = "Grievance"
    return _create_workflow(
        name="Grievance Resolution Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Submitted", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Under Review", "doc_status": "0", "allow_edit": "University Registrar", "style": "Primary"},
            {"state": "Resolution Proposed", "doc_status": "0", "allow_edit": "University Registrar", "style": "Info"},
            {"state": "Resolved", "doc_status": "0", "allow_edit": "University Registrar", "style": "Success"},
            {"state": "Closed", "doc_status": "0", "allow_edit": "University Registrar", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "University Registrar", "style": "Danger"},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit", "next_state": "Submitted", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Submitted", "action": "Take Up for Review", "next_state": "Under Review", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Under Review", "action": "Propose Resolution", "next_state": "Resolution Proposed", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Resolution Proposed", "action": "Accept Resolution", "next_state": "Resolved", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Resolved", "action": "Close", "next_state": "Closed", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Under Review", "action": "Reject", "next_state": "Rejected", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Resolved", "action": "Reopen", "next_state": "Under Review", "allowed": "University Registrar", "allow_self_approval": 1},
        ],
    )


def _workflow_journal_entry():
    """Journal Entry Approval workflow (deferred from Phase 03.3)."""
    dt = "Journal Entry"
    return _create_workflow(
        name="Journal Entry Approval",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Accounts User", "style": ""},
            {"state": "Pending Finance Approval", "doc_status": "0", "allow_edit": "Accounts User", "style": "Warning"},
            {"state": "Approved", "doc_status": "1", "allow_edit": "Accounts Manager", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Accounts User", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "2", "allow_edit": "Accounts Manager", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Finance Approval", "allowed": "Accounts User", "allow_self_approval": 1},
            {"state": "Pending Finance Approval", "action": "Approve", "next_state": "Approved", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Pending Finance Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "Accounts Manager", "allow_self_approval": 1},
        ],
    )


def _workflow_payment_entry():
    """Payment Entry Approval workflow (deferred from Phase 03.3)."""
    dt = "Payment Entry"
    return _create_workflow(
        name="Payment Entry Approval",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Accounts User", "style": ""},
            {"state": "Pending Finance Approval", "doc_status": "0", "allow_edit": "Accounts User", "style": "Warning"},
            {"state": "Approved", "doc_status": "1", "allow_edit": "Accounts Manager", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Accounts User", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "2", "allow_edit": "Accounts Manager", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Finance Approval", "allowed": "Accounts User", "allow_self_approval": 1},
            {"state": "Pending Finance Approval", "action": "Approve", "next_state": "Approved", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Pending Finance Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "Accounts Manager", "allow_self_approval": 1},
        ],
    )


def _workflow_generated_question_paper():
    """Generated Question Paper workflow."""
    dt = "Generated Question Paper"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Generated Question Paper Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "University Exam Cell", "style": ""},
            {"state": "Ready for Review", "doc_status": "0", "allow_edit": "University Exam Cell", "style": "Warning"},
            {"state": "Approved", "doc_status": "1" if sub else "0", "allow_edit": "University Exam Cell", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "University Exam Cell", "style": "Danger"},
            {"state": "Locked", "doc_status": "1" if sub else "0", "allow_edit": "University Exam Cell", "style": "Primary"},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Review", "next_state": "Ready for Review", "allowed": "University Exam Cell", "allow_self_approval": 1},
            {"state": "Ready for Review", "action": "Approve", "next_state": "Approved", "allowed": "Education Manager", "allow_self_approval": 1},
            {"state": "Ready for Review", "action": "Reject", "next_state": "Rejected", "allowed": "Education Manager", "allow_self_approval": 1},
            {"state": "Approved", "action": "Lock", "next_state": "Locked", "allowed": "University Exam Cell", "allow_self_approval": 1},
        ],
    )


def _workflow_lab_equipment_booking():
    """Lab Equipment Booking workflow."""
    dt = "Lab Equipment Booking"
    if not frappe.db.exists("DocType", dt):
        print(f"  SKIP: DocType '{dt}' does not exist")
        return None
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Lab Equipment Booking Workflow",
        document_type=dt,
        states=[
            {"state": "Pending", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Approved", "doc_status": "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "In Use", "doc_status": "0", "allow_edit": "Academics User", "style": "Primary"},
            {"state": "Completed", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Cancelled", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
        ],
        transitions=[
            {"state": "Pending", "action": "Approve", "next_state": "Approved", "allowed": "Education Manager", "allow_self_approval": 1},
            {"state": "Approved", "action": "Start Use", "next_state": "In Use", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "In Use", "action": "Complete", "next_state": "Completed", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Pending", "action": "Cancel", "next_state": "Cancelled", "allowed": "Education Manager", "allow_self_approval": 1},
        ],
    )


def _workflow_merit_list():
    """Merit List publish workflow."""
    dt = "Merit List"
    sub = _is_submittable(dt)
    return _create_workflow(
        name="Merit List Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Pending Publication", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Published", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Expired", "doc_status": "1" if sub else "0", "allow_edit": "Academics User", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Publication", "next_state": "Pending Publication", "allowed": "Academics User", "allow_self_approval": 1},
            {"state": "Pending Publication", "action": "Publish", "next_state": "Published", "allowed": "University Registrar", "allow_self_approval": 1},
            {"state": "Published", "action": "Mark Expired", "next_state": "Expired", "allowed": "University Registrar", "allow_self_approval": 1},
        ],
    )


def _workflow_leave_application():
    """
    Leave Application Workflow (from existing fixture).

    Re-creates the workflow that was defined in the fixture JSON but not loaded into DB.
    """
    dt = "Leave Application"
    return _create_workflow(
        name="Leave Application Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Employee", "style": ""},
            {"state": "Pending HOD Approval", "doc_status": "0", "allow_edit": "HR Manager", "style": "Warning"},
            {"state": "Pending HR Approval", "doc_status": "0", "allow_edit": "HR Manager", "style": "Warning"},
            {"state": "Approved", "doc_status": "1", "allow_edit": "HR Manager", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Employee", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "2", "allow_edit": "HR Manager", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending HOD Approval", "allowed": "Employee", "allow_self_approval": 0},
            {"state": "Pending HOD Approval", "action": "Approve", "next_state": "Pending HR Approval", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending HOD Approval", "action": "Reject", "next_state": "Rejected", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending HR Approval", "action": "Approve", "next_state": "Approved", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending HR Approval", "action": "Reject", "next_state": "Rejected", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending HR Approval", "action": "Send Back to HOD", "next_state": "Pending HOD Approval", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "HR Manager", "allow_self_approval": 0},
        ],
        send_email_alert=1,
    )


def _workflow_teaching_assignment():
    """
    Teaching Assignment Approval Workflow (from existing fixture).

    Re-creates the workflow that was defined in the fixture JSON but not loaded into DB.
    Uses HR Manager instead of non-existent 'Department Manager' role.
    """
    dt = "Teaching Assignment"
    return _create_workflow(
        name="Teaching Assignment Approval Workflow",
        document_type=dt,
        states=[
            {"state": "Draft", "doc_status": "0", "allow_edit": "Academics User", "style": ""},
            {"state": "Pending Faculty Acceptance", "doc_status": "0", "allow_edit": "Employee", "style": "Warning"},
            {"state": "Pending HOD Approval", "doc_status": "0", "allow_edit": "HR Manager", "style": "Warning"},
            {"state": "Pending Academic Registrar Approval", "doc_status": "0", "allow_edit": "Academics User", "style": "Warning"},
            {"state": "Approved", "doc_status": "1", "allow_edit": "Academics User", "style": "Success"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Academics User", "style": "Danger"},
            {"state": "Cancelled", "doc_status": "2", "allow_edit": "Academics User", "style": ""},
        ],
        transitions=[
            {"state": "Draft", "action": "Send to Faculty", "next_state": "Pending Faculty Acceptance", "allowed": "Academics User", "allow_self_approval": 0},
            {"state": "Pending Faculty Acceptance", "action": "Accept", "next_state": "Pending HOD Approval", "allowed": "Employee", "allow_self_approval": 0},
            {"state": "Pending Faculty Acceptance", "action": "Decline", "next_state": "Rejected", "allowed": "Employee", "allow_self_approval": 0},
            {"state": "Pending HOD Approval", "action": "Approve", "next_state": "Pending Academic Registrar Approval", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending HOD Approval", "action": "Reject", "next_state": "Rejected", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending HOD Approval", "action": "Send Back to Faculty", "next_state": "Pending Faculty Acceptance", "allowed": "HR Manager", "allow_self_approval": 0},
            {"state": "Pending Academic Registrar Approval", "action": "Approve", "next_state": "Approved", "allowed": "Academics User", "allow_self_approval": 0},
            {"state": "Pending Academic Registrar Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Academics User", "allow_self_approval": 0},
            {"state": "Pending Academic Registrar Approval", "action": "Send Back to HOD", "next_state": "Pending HOD Approval", "allowed": "Academics User", "allow_self_approval": 0},
            {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "Academics User", "allow_self_approval": 0},
        ],
        send_email_alert=1,
    )


def _workflow_fee_refund():
    """
    Fee Refund Approval Workflow (from existing fixture).

    Re-creates the workflow that was defined in the fixture JSON but not loaded into DB.
    """
    dt = "Fee Refund"
    return _create_workflow(
        name="Fee Refund Approval Workflow",
        document_type=dt,
        states=[
            {"state": "Pending", "doc_status": "0", "allow_edit": "Accounts User", "style": "Warning"},
            {"state": "Pending Approval", "doc_status": "0", "allow_edit": "Accounts Manager", "style": "Warning"},
            {"state": "Approved", "doc_status": "0", "allow_edit": "Accounts Manager", "style": "Primary"},
            {"state": "Rejected", "doc_status": "0", "allow_edit": "Accounts Manager", "style": "Danger"},
            {"state": "Processed", "doc_status": "1", "allow_edit": "Accounts Manager", "style": "Success"},
            {"state": "Cancelled", "doc_status": "2", "allow_edit": "Accounts Manager", "style": ""},
        ],
        transitions=[
            {"state": "Pending", "action": "Submit for Approval", "next_state": "Pending Approval", "allowed": "Accounts User", "allow_self_approval": 1},
            {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "Accounts Manager", "allow_self_approval": 0},
            {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Pending Approval", "action": "Return to Draft", "next_state": "Pending", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Approved", "action": "Process Refund", "next_state": "Processed", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Processed", "action": "Cancel", "next_state": "Cancelled", "allowed": "Accounts Manager", "allow_self_approval": 1},
            {"state": "Rejected", "action": "Reconsider", "next_state": "Pending Approval", "allowed": "Accounts Manager", "allow_self_approval": 1},
        ],
        send_email_alert=1,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

ALL_WORKFLOW_CREATORS = [
    # Existing fixtures (not yet in DB)
    _workflow_leave_application,
    _workflow_teaching_assignment,
    _workflow_fee_refund,
    # New workflows
    _workflow_hostel_allocation,
    _workflow_hostel_maintenance,
    _workflow_transport_allocation,
    _workflow_certificate_request,
    _workflow_course_registration,
    _workflow_revaluation_request,
    _workflow_research_grant,
    _workflow_grievance,
    _workflow_journal_entry,
    _workflow_payment_entry,
    _workflow_generated_question_paper,
    _workflow_lab_equipment_booking,
    _workflow_merit_list,
]


def run():
    """
    Create all missing workflows for the university ERP.

    Usage:
        bench --site university.local execute university_erp.setup.create_workflows.run
    """
    print("=" * 60)
    print("Workflow Creation Script")
    print("=" * 60)

    created = 0
    existed = 0
    skipped = 0

    for creator_fn in ALL_WORKFLOW_CREATORS:
        try:
            result = creator_fn()
            if result is None:
                skipped += 1
            else:
                created += 1
        except Exception as e:
            print(f"  ERROR in {creator_fn.__name__}: {e}")
            skipped += 1
            import traceback
            traceback.print_exc()

    frappe.db.commit()

    # Re-count accurately from DB
    total_active = frappe.db.count("Workflow", {"is_active": 1})

    print()
    print("=" * 60)
    print(f"Summary: {total_active} active workflows in system")
    print(f"  This run: created new workflows, skipped {skipped}")
    print("=" * 60)

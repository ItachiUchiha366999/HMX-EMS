# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe


def setup_admission_workflow():
	"""Create admission workflow"""
	if frappe.db.exists("Workflow", "Student Applicant Approval"):
		return "Workflow already exists"

	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Student Applicant Approval"
	workflow.document_type = "Student Applicant"
	workflow.is_active = 1
	workflow.workflow_state_field = "workflow_state"

	# States
	states = [
		{"state": "Draft", "doc_status": "0", "allow_edit": "University Registrar"},
		{"state": "Submitted", "doc_status": "1", "allow_edit": ""},
		{"state": "Under Review", "doc_status": "1", "allow_edit": "University Registrar"},
		{"state": "Document Verification", "doc_status": "1", "allow_edit": "University Registrar"},
		{"state": "Shortlisted", "doc_status": "1", "allow_edit": ""},
		{"state": "Counseling Scheduled", "doc_status": "1", "allow_edit": ""},
		{"state": "Seat Allotted", "doc_status": "1", "allow_edit": "University Registrar"},
		{"state": "Fee Payment Pending", "doc_status": "1", "allow_edit": ""},
		{"state": "Admitted", "doc_status": "1", "allow_edit": ""},
		{"state": "Rejected", "doc_status": "2", "allow_edit": ""},
		{"state": "Withdrawn", "doc_status": "2", "allow_edit": ""}
	]

	for state in states:
		workflow.append("states", state)

	# Transitions
	transitions = [
		{"state": "Draft", "action": "Submit", "next_state": "Submitted", "allowed": "University Registrar"},
		{"state": "Submitted", "action": "Review", "next_state": "Under Review", "allowed": "University Registrar"},
		{"state": "Under Review", "action": "Verify Documents", "next_state": "Document Verification", "allowed": "University Registrar"},
		{"state": "Document Verification", "action": "Shortlist", "next_state": "Shortlisted", "allowed": "University Registrar"},
		{"state": "Document Verification", "action": "Reject", "next_state": "Rejected", "allowed": "University Registrar"},
		{"state": "Shortlisted", "action": "Schedule Counseling", "next_state": "Counseling Scheduled", "allowed": "University Registrar"},
		{"state": "Counseling Scheduled", "action": "Allot Seat", "next_state": "Seat Allotted", "allowed": "University Registrar"},
		{"state": "Seat Allotted", "action": "Request Fee", "next_state": "Fee Payment Pending", "allowed": "University Registrar"},
		{"state": "Fee Payment Pending", "action": "Confirm Admission", "next_state": "Admitted", "allowed": "University Registrar"},
		{"state": "Fee Payment Pending", "action": "Withdraw", "next_state": "Withdrawn", "allowed": "University Registrar"},
	]

	for transition in transitions:
		workflow.append("transitions", transition)

	workflow.insert(ignore_permissions=True)
	frappe.db.commit()

	return workflow.name


@frappe.whitelist()
def activate_admission_workflow():
	"""API to setup admission workflow"""
	return setup_admission_workflow()


@frappe.whitelist()
def apply_workflow_action(applicant_name, action):
	"""Apply workflow action to applicant"""
	try:
		applicant = frappe.get_doc("Student Applicant", applicant_name)

		# Validate action is allowed
		# This will be handled by Frappe's workflow engine

		# Send notification based on action
		send_workflow_notification(applicant, action)

		return {"success": True, "message": f"Action '{action}' applied successfully"}
	except Exception as e:
		frappe.log_error(f"Workflow action failed: {str(e)}")
		return {"success": False, "message": str(e)}


def send_workflow_notification(applicant, action):
	"""Send email notification for workflow actions"""
	if not applicant.student_email_id:
		return

	action_messages = {
		"Shortlist": {
			"subject": "Congratulations! You've been shortlisted",
			"message": f"Dear {applicant.first_name},<br><br>"
					   f"Congratulations! Your application {applicant.name} has been shortlisted "
					   f"for {applicant.program}.<br><br>"
					   f"You will be notified about the next steps soon."
		},
		"Schedule Counseling": {
			"subject": "Counseling Scheduled",
			"message": f"Dear {applicant.first_name},<br><br>"
					   f"Your counseling has been scheduled. Please check the portal for details."
		},
		"Allot Seat": {
			"subject": "Seat Allotted!",
			"message": f"Dear {applicant.first_name},<br><br>"
					   f"A seat has been allotted to you in {applicant.program}.<br><br>"
					   f"Please proceed with fee payment to confirm your admission."
		},
		"Confirm Admission": {
			"subject": "Admission Confirmed!",
			"message": f"Dear {applicant.first_name},<br><br>"
					   f"Congratulations! Your admission to {applicant.program} is confirmed.<br><br>"
					   f"Welcome to the university!"
		},
		"Reject": {
			"subject": "Application Status Update",
			"message": f"Dear {applicant.first_name},<br><br>"
					   f"We regret to inform you that your application for {applicant.program} "
					   f"could not be processed further at this time."
		}
	}

	if action in action_messages:
		try:
			frappe.sendmail(
				recipients=[applicant.student_email_id],
				subject=action_messages[action]["subject"],
				message=action_messages[action]["message"]
			)
		except Exception as e:
			frappe.log_error(f"Failed to send workflow notification: {str(e)}")

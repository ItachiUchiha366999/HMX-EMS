# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, today


class StudentLifecycle:
	"""Manage student lifecycle transitions"""

	VALID_TRANSITIONS = {
		"Applicant": ["Admitted", "Rejected", "Withdrawn"],
		"Admitted": ["Enrolled", "Withdrawn"],
		"Enrolled": ["Active"],
		"Active": ["Suspended", "Dropped", "Graduated", "Transfer Out"],
		"Suspended": ["Active", "Dropped"],
		"Graduated": ["Alumni"],
		"Alumni": [],
		"Dropped": [],
		"Rejected": [],
		"Withdrawn": [],
		"Transfer Out": [],
	}

	def __init__(self, student_name):
		self.student = frappe.get_doc("Student", student_name)

	def can_transition_to(self, new_status):
		"""Check if transition is valid"""
		current = self.student.custom_student_status or "Applicant"
		return new_status in self.VALID_TRANSITIONS.get(current, [])

	def transition_to(self, new_status, reason=None, remarks=None):
		"""Perform status transition"""
		if not self.can_transition_to(new_status):
			current = self.student.custom_student_status
			frappe.throw(f"Cannot transition from {current} to {new_status}")

		old_status = self.student.custom_student_status

		# Perform transition-specific actions
		self._perform_transition_actions(new_status)

		# Update status
		self.student.custom_student_status = new_status
		self.student.save(ignore_permissions=True)

		# Log the transition
		self._log_transition(old_status, new_status, reason, remarks)

		frappe.db.commit()

		return True

	def _perform_transition_actions(self, new_status):
		"""Actions specific to each transition"""
		if new_status == "Enrolled":
			self._create_program_enrollment()
		elif new_status == "Active":
			self._activate_student()
		elif new_status == "Graduated":
			self._graduate_student()
		elif new_status == "Alumni":
			self._convert_to_alumni()
		elif new_status == "Suspended":
			self._suspend_student()
		elif new_status == "Dropped":
			self._drop_student()

	def _create_program_enrollment(self):
		"""Create program enrollment record"""
		if not self.student.custom_program:
			return

		if not frappe.db.exists("Program Enrollment", {
			"student": self.student.name,
			"program": self.student.custom_program
		}):
			enrollment = frappe.new_doc("Program Enrollment")
			enrollment.student = self.student.name
			enrollment.student_name = self.student.student_name
			enrollment.program = self.student.custom_program
			enrollment.enrollment_date = today()
			enrollment.insert(ignore_permissions=True)

	def _activate_student(self):
		"""Activate student account"""
		self.student.enabled = 1

	def _graduate_student(self):
		"""Process graduation"""
		# Update graduation date
		self.student.custom_graduation_date = today()

		# Note: Transcript generation will be implemented in Phase 4 (Examinations)

	def _convert_to_alumni(self):
		"""Create alumni record"""
		if not frappe.db.exists("University Alumni", {"student": self.student.name}):
			alumni = frappe.new_doc("University Alumni")
			alumni.student = self.student.name
			alumni.student_name = self.student.student_name
			alumni.email = self.student.student_email_id
			alumni.program = self.student.custom_program
			alumni.graduation_year = now_datetime().year

			try:
				alumni.insert(ignore_permissions=True)

				# Send welcome email
				self._send_alumni_welcome_email(alumni)
			except Exception as e:
				frappe.log_error(f"Failed to create alumni record: {str(e)}")

	def _send_alumni_welcome_email(self, alumni):
		"""Send welcome email to alumni"""
		if not alumni.email:
			return

		try:
			frappe.sendmail(
				recipients=[alumni.email],
				subject="Welcome to the Alumni Network!",
				message=f"""
				<p>Dear {alumni.student_name},</p>

				<p>Congratulations on your graduation!</p>

				<p>You are now part of our prestigious alumni network. Stay connected with us and your batchmates.</p>

				<p>Best regards,<br>
				Alumni Relations Team</p>
				"""
			)
		except Exception as e:
			# Don't fail if email sending fails
			frappe.log_error(f"Failed to send alumni welcome email: {str(e)}")

	def _suspend_student(self):
		"""Suspend student account"""
		self.student.enabled = 0

	def _drop_student(self):
		"""Drop student - disable account"""
		self.student.enabled = 0

	def _log_transition(self, old_status, new_status, reason, remarks):
		"""Log status transition"""
		try:
			log = frappe.get_doc({
				"doctype": "Student Status Log",
				"student": self.student.name,
				"student_name": self.student.student_name,
				"from_status": old_status or "Applicant",
				"to_status": new_status,
				"transition_date": now_datetime(),
				"reason": reason or "",
				"remarks": remarks or "",
				"changed_by": frappe.session.user
			})
			log.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Failed to log status transition: {str(e)}")

	def get_allowed_transitions(self):
		"""Get list of allowed transitions from current status"""
		current = self.student.custom_student_status or "Applicant"
		return self.VALID_TRANSITIONS.get(current, [])


@frappe.whitelist()
def transition_student_status(student_name, new_status, reason=None, remarks=None):
	"""API to transition student status"""
	lifecycle = StudentLifecycle(student_name)
	return lifecycle.transition_to(new_status, reason, remarks)


@frappe.whitelist()
def get_student_status_history(student_name):
	"""Get status transition history for a student"""
	return frappe.get_all(
		"Student Status Log",
		filters={"student": student_name},
		fields=["from_status", "to_status", "transition_date", "reason", "changed_by"],
		order_by="transition_date desc"
	)


@frappe.whitelist()
def get_allowed_status_transitions(student_name):
	"""Get allowed transitions for a student"""
	lifecycle = StudentLifecycle(student_name)
	return lifecycle.get_allowed_transitions()

# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, now_datetime


class StudentCreator:
	"""Convert admitted applicant to student"""

	def __init__(self, applicant_name):
		self.applicant = frappe.get_doc("Student Applicant", applicant_name)

	def create_student(self):
		"""Create student from applicant"""
		if self.applicant.application_status != "Admitted":
			frappe.throw("Only admitted applicants can be converted to students")

		# Check if student already exists
		existing = frappe.db.exists("Student", {"student_applicant": self.applicant.name})
		if existing:
			frappe.throw(f"Student already exists: {existing}")

		# Generate enrollment number
		enrollment_number = self.generate_enrollment_number()

		# Create student using Education's Student DocType
		student = frappe.new_doc("Student")
		student.first_name = self.applicant.first_name
		student.middle_name = self.applicant.middle_name or ""
		student.last_name = self.applicant.last_name or ""
		student.student_email_id = self.applicant.student_email_id
		student.date_of_birth = self.applicant.date_of_birth
		student.gender = self.applicant.gender
		student.student_mobile_number = self.applicant.student_mobile_number
		student.blood_group = self.applicant.blood_group or ""
		student.image = self.applicant.image or ""
		student.student_applicant = self.applicant.name

		# Custom fields
		student.custom_enrollment_number = enrollment_number
		student.custom_student_status = "Admitted"
		student.custom_category = self.applicant.custom_category or "General"
		student.custom_category_certificate = self.applicant.custom_category_certificate or ""
		student.custom_program = self.applicant.program
		student.custom_admission_date = today()
		if hasattr(self.applicant, 'custom_admission_cycle'):
			student.custom_admission_cycle = self.applicant.custom_admission_cycle

		# Copy guardians if exists
		if hasattr(self.applicant, 'guardians') and self.applicant.guardians:
			for guardian in self.applicant.guardians:
				student.append("guardians", {
					"guardian": guardian.guardian,
					"guardian_name": guardian.guardian_name or "",
					"relation": guardian.relation or ""
				})

		student.insert(ignore_permissions=True)

		# Create user account
		self.create_student_user(student)

		# Update applicant status
		frappe.db.set_value(
			"Student Applicant",
			self.applicant.name,
			"student",
			student.name,
			update_modified=False
		)

		frappe.db.commit()

		return student.name

	def generate_enrollment_number(self):
		"""Generate unique enrollment number"""
		# Format: YEAR/DEPT/NUMBER
		year = now_datetime().year

		# Get department code from program
		dept_code = frappe.db.get_value(
			"Program",
			self.applicant.program,
			"custom_department_code"
		) or "GEN"

		# Get next serial
		last_enrollment = frappe.db.sql("""
			SELECT custom_enrollment_number FROM `tabStudent`
			WHERE custom_enrollment_number LIKE %(pattern)s
			ORDER BY custom_enrollment_number DESC LIMIT 1
		""", {"pattern": f"{year}/{dept_code}/%"})

		if last_enrollment and last_enrollment[0][0]:
			last_serial = int(last_enrollment[0][0].split("/")[-1])
			next_serial = last_serial + 1
		else:
			next_serial = 1

		return f"{year}/{dept_code}/{str(next_serial).zfill(4)}"

	def create_student_user(self, student):
		"""Create user account for student"""
		if not student.student_email_id:
			return

		if frappe.db.exists("User", student.student_email_id):
			user = frappe.get_doc("User", student.student_email_id)
		else:
			user = frappe.new_doc("User")
			user.email = student.student_email_id
			user.first_name = student.first_name
			user.last_name = student.last_name or ""
			user.send_welcome_email = 1
			user.user_type = "Website User"

		# Add University Student role
		if not user.has_role("University Student"):
			user.append("roles", {"role": "University Student"})

		if user.is_new():
			user.insert(ignore_permissions=True)
		else:
			user.save(ignore_permissions=True)

		# Link user to student
		frappe.db.set_value("Student", student.name, "user", user.name, update_modified=False)


class BulkStudentCreator:
	"""Create multiple students from merit list"""

	def __init__(self, merit_list_name):
		self.merit_list = frappe.get_doc("Merit List", merit_list_name)

	def create_students(self, limit=None):
		"""Create students for allotted candidates"""
		created_students = []
		failed = []

		# Get allotted applicants
		allotted = [app for app in self.merit_list.applicants if app.seat_allotted]

		if limit:
			allotted = allotted[:limit]

		for applicant_row in allotted:
			try:
				# Update applicant status to Admitted
				frappe.db.set_value(
					"Student Applicant",
					applicant_row.applicant,
					"application_status",
					"Admitted",
					update_modified=False
				)

				# Create student
				creator = StudentCreator(applicant_row.applicant)
				student_name = creator.create_student()
				created_students.append(student_name)

			except Exception as e:
				failed.append({
					"applicant": applicant_row.applicant,
					"error": str(e)
				})
				frappe.log_error(f"Failed to create student for {applicant_row.applicant}: {str(e)}")

		frappe.db.commit()

		result = {
			"created": len(created_students),
			"failed": len(failed),
			"students": created_students
		}

		if failed:
			result["errors"] = failed

		return result


@frappe.whitelist()
def create_student_from_applicant(applicant_name):
	"""API to create student from applicant"""
	creator = StudentCreator(applicant_name)
	return creator.create_student()


@frappe.whitelist()
def create_students_from_merit_list(merit_list_name, limit=None):
	"""API to create students from merit list"""
	creator = BulkStudentCreator(merit_list_name)
	return creator.create_students(int(limit) if limit else None)

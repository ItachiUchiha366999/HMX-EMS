# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.desk.form.linked_with import get_linked_doctypes
from frappe.model.document import Document
from frappe.utils import getdate, today

from university_erp.utils import check_content_completion, check_quiz_completion


class Student(Document):
	def validate(self):
		self.set_title()
		self.validate_dates()
		self.validate_user()

		if self.student_applicant:
			self.check_unique()
			self.update_applicant_status()

		# University-specific validations (absorbed from former UniversityStudent override)
		self.validate_enrollment_number()
		self.validate_category_certificate()
		self.calculate_cgpa()

	def on_update(self):
		# University-specific post-update hook (absorbed from former UniversityStudent override)
		self.update_student_status()

	def set_title(self):
		self.student_name = " ".join(
			filter(None, [self.first_name, self.middle_name, self.last_name])
		)

	def validate_dates(self):
		for sibling in self.siblings:
			if sibling.date_of_birth and getdate(sibling.date_of_birth) > getdate():
				frappe.throw(
					_("Row {0}:Sibling Date of Birth cannot be greater than today.").format(
						sibling.idx
					)
				)

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate():
			frappe.throw(_("Date of Birth cannot be greater than today."))

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate(self.joining_date):
			frappe.throw(_("Date of Birth cannot be greater than Joining Date."))

		if (
			self.joining_date
			and self.date_of_leaving
			and getdate(self.joining_date) > getdate(self.date_of_leaving)
		):
			frappe.throw(_("Joining Date can not be greater than Leaving Date"))

	def validate_user(self):
		"""Create a website user for student creation if not already exists"""
		if not frappe.db.get_single_value(
			"Education Settings", "user_creation_skip"
		) and not frappe.db.exists("User", self.student_email_id):
			student_user = frappe.get_doc(
				{
					"doctype": "User",
					"first_name": self.first_name,
					"last_name": self.last_name,
					"email": self.student_email_id,
					"gender": self.gender,
					"send_welcome_email": 1,
					"user_type": "Website User",
				}
			)
			student_user.add_roles("Student")
			student_user.save(ignore_permissions=True)

			self.user = student_user.name

	def check_unique(self):
		"""Validates if the Student Applicant is Unique"""
		student = frappe.get_all(
			"Student",
			{"student_applicant": self.student_applicant, "name": ["!=", self.name]},
			pluck="name",
		)
		if len(student):
			frappe.throw(
				_("Student {0} exist against student applicant {1}").format(
					student[0], self.student_applicant
				)
			)

	def update_applicant_status(self):
		"""Updates Student Applicant status to Admitted"""
		if self.student_applicant:
			frappe.db.set_value(
				"Student Applicant", self.student_applicant, "application_status", "Admitted"
			)

	def get_all_course_enrollments(self):
		"""Returns a list of course enrollments linked with the current student"""
		course_enrollments = frappe.get_all(
			"Course Enrollment", filters={"student": self.name}, fields=["course", "name"]
		)
		if not course_enrollments:
			return None
		else:
			enrollments = {item["course"]: item["name"] for item in course_enrollments}
			return enrollments

	def get_program_enrollments(self):
		"""Returns a list of course enrollments linked with the current student"""
		program_enrollments = frappe.get_all(
			"Program Enrollment", filters={"student": self.name}, fields=["program"]
		)
		if not program_enrollments:
			return None
		else:
			enrollments = [item["program"] for item in program_enrollments]
			return enrollments

	def get_topic_progress(self, course_enrollment_name, topic):
		"""
		Get Progress Dictionary of a student for a particular topic
		        :param self: Student Object
		        :param course_enrollment_name: Name of the Course Enrollment
		        :param topic: Topic DocType Object
		"""
		contents = topic.get_contents()
		progress = []
		if contents:
			for content in contents:
				if content.doctype in ("Article", "Video"):
					status = check_content_completion(
						content.name, content.doctype, course_enrollment_name
					)
					progress.append(
						{"content": content.name, "content_type": content.doctype, "is_complete": status}
					)
				elif content.doctype == "Quiz":
					status, score, result, time_taken = check_quiz_completion(
						content, course_enrollment_name
					)
					progress.append(
						{
							"content": content.name,
							"content_type": content.doctype,
							"is_complete": status,
							"score": score,
							"result": result,
						}
					)
		return progress

	def enroll_in_program(self, program_name):
		try:
			enrollment = frappe.get_doc(
				{
					"doctype": "Program Enrollment",
					"student": self.name,
					"academic_year": frappe.get_last_doc("Academic Year").name,
					"program": program_name,
					"enrollment_date": frappe.utils.datetime.datetime.now(),
				}
			)
			enrollment.save(ignore_permissions=True)
		except frappe.exceptions.ValidationError:
			enrollment_name = frappe.get_list(
				"Program Enrollment", filters={"student": self.name, "Program": program_name}
			)[0].name
			return frappe.get_doc("Program Enrollment", enrollment_name)
		else:
			enrollment.submit()
			return enrollment

	def enroll_in_course(self, course_name, program_enrollment, enrollment_date=None):
		if enrollment_date is None:
			enrollment_date = frappe.utils.datetime.datetime.now()
		try:
			enrollment = frappe.get_doc(
				{
					"doctype": "Course Enrollment",
					"student": self.name,
					"course": course_name,
					"program_enrollment": program_enrollment,
					"enrollment_date": enrollment_date,
				}
			)
			enrollment.save(ignore_permissions=True)
		except frappe.exceptions.ValidationError:
			enrollment_name = frappe.get_list(
				"Course Enrollment",
				filters={
					"student": self.name,
					"course": course_name,
					"program_enrollment": program_enrollment,
				},
			)[0].name
			return frappe.get_doc("Course Enrollment", enrollment_name)
		else:
			return enrollment

	# =========================================================================
	# University-specific methods (absorbed from former UniversityStudent override)
	# =========================================================================

	def validate_enrollment_number(self):
		"""Validate that enrollment number is unique"""
		if not self.get("custom_enrollment_number"):
			return

		existing = frappe.db.exists(
			"Student",
			{
				"custom_enrollment_number": self.custom_enrollment_number,
				"name": ("!=", self.name),
			},
		)

		if existing:
			frappe.throw(
				_("Enrollment Number {0} already exists").format(self.custom_enrollment_number)
			)

	def validate_category_certificate(self):
		"""Validate that reserved category students have uploaded certificates"""
		if not self.get("custom_category"):
			return

		reserved_categories = ["SC", "ST", "OBC", "EWS"]

		if self.custom_category in reserved_categories and not self.get(
			"custom_category_certificate"
		):
			frappe.msgprint(
				_("Category certificate is required for {0} category").format(
					self.custom_category
				),
				alert=True,
				indicator="orange",
			)

	def calculate_cgpa(self):
		"""Calculate CGPA from all assessment results"""
		if not self.name:
			return

		assessment_results = frappe.get_all(
			"Assessment Result",
			filters={"student": self.name, "docstatus": 1},
			fields=["custom_grade_points", "custom_credits"],
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
		frappe.logger().info(
			f"Student {self.name} updated. Status: {self.get('custom_student_status')}"
		)


def get_timeline_data(doctype, name):
	"""Return timeline for attendance"""
	return dict(
		frappe.db.sql(
			"""select unix_timestamp(`date`), count(*)
		from `tabStudent Attendance` where
			student=%s
			and `date` > date_sub(curdate(), interval 1 year)
			and docstatus = 1 and status = 'Present'
			group by date""",
			name,
		)
	)


# =============================================================================
# Module-level hooks (absorbed from former university_erp.overrides.student)
# =============================================================================


def validate_student(doc, method):
	"""Global validate hook for Student DocType"""
	pass


def on_student_update(doc, method):
	"""Global on_update hook for Student DocType"""
	pass


STUDENT_SELF_ROLES = ("University Student", "Student", "Guardian")


def _is_student_self_only(roles):
	"""True iff the user's read access to Student comes ONLY through the
	self-restricted roles (`University Student`, `Student`, `Guardian`)
	and they have no broader Student-read role.
	"""
	role_set = set(roles)

	if not role_set.intersection(STUDENT_SELF_ROLES):
		return False

	other_roles = role_set.difference(STUDENT_SELF_ROLES)
	if not other_roles:
		return True

	has_broader_read = frappe.db.sql(
		"""
		select 1 from `tabDocPerm`
		where parent = 'Student' and `read` = 1 and role in %s
		limit 1
		""",
		(tuple(other_roles),),
	)
	return not has_broader_read


def get_permission_query_conditions(user):
	"""Restrict Student list view ONLY for users whose access is via the
	student-self roles. Everyone else gets unrestricted access.
	"""
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return ""

	roles = frappe.get_roles(user)

	if _is_student_self_only(roles):
		return f"""(`tabStudent`.`user` = {frappe.db.escape(user)})"""

	return ""


def has_permission(doc, ptype="read", user=None):
	"""Row-level permission for Student."""
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return True

	roles = frappe.get_roles(user)

	if _is_student_self_only(roles):
		target_user = getattr(doc, "user", None) if doc else None
		return target_user == user

	return None


@frappe.whitelist()
def student_query(doctype, txt, searchfield, start, page_len, filters):
	"""Custom Link-field search for Student."""
	if not searchfield:
		searchfield = "name"

	return frappe.db.sql(
		f"""
		select name, student_name, custom_enrollment_number
		from `tabStudent`
		where (`{searchfield}` like %(txt)s
		       or student_name like %(txt)s
		       or ifnull(custom_enrollment_number, '') like %(txt)s)
		order by
		    case when `{searchfield}` like %(prefix)s then 0 else 1 end,
		    modified desc
		limit %(start)s, %(page_len)s
		""",
		{
			"txt": f"%{txt}%",
			"prefix": f"{txt}%",
			"start": start,
			"page_len": page_len,
		},
	)

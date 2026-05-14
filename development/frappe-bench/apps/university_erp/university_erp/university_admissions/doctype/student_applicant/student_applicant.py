# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_years, date_diff, flt, getdate, nowdate


class StudentApplicant(Document):
	def autoname(self):
		from frappe.model.naming import set_name_by_naming_series

		if self.student_admission:
			naming_series = None
			if self.program:
				# set the naming series from the student admission if provided.
				student_admission = get_student_admission_data(self.student_admission, self.program)
				if student_admission:
					naming_series = student_admission.get("applicant_naming_series")
				else:
					naming_series = None
			else:
				frappe.throw(_("Select the program first"))

			if naming_series:
				self.naming_series = naming_series

		set_name_by_naming_series(self)

	def validate(self):
		self.set_title()
		self.validate_dates()
		self.validate_term()

		if self.student_admission and self.program and self.date_of_birth:
			self.validation_from_student_admission()

		# University-specific validations (absorbed from former UniversityApplicant override)
		self.generate_application_number()
		self.calculate_merit_score()
		self.validate_category_certificate()
		self.validate_program_preferences()

	def before_submit(self):
		# University-specific pre-submit (absorbed from former UniversityApplicant override)
		self.set_admission_status()

	def on_update(self):
		"""Drives end-to-end admission journey when workflow_state moves to 'Admitted'.
		Idempotent — safe to call repeatedly.
		"""
		if getattr(self, "workflow_state", None) != "Admitted":
			return

		existing = frappe.db.get_value("Student", {"student_applicant": self.name}, "name")
		if existing:
			return

		program_to_enroll = (
			self.get("custom_seat_allotted")
			or self.program
			or self.get("custom_program_preference_1")
		)
		if not program_to_enroll:
			frappe.msgprint(
				_(
					"Cannot create Student record — no program allotted on applicant {0}"
				).format(self.name),
				indicator="orange",
				alert=True,
			)
			return

		if not self.program:
			self.program = program_to_enroll
		if not self.get("custom_seat_allotted"):
			self.custom_seat_allotted = program_to_enroll
		if self.get("custom_admission_status") not in ("Admission Confirmed", "Admitted"):
			self.custom_admission_status = "Admission Confirmed"

		try:
			student = _create_student_from_applicant(self, program_to_enroll)
		except Exception as e:
			frappe.log_error(message=str(e), title=f"Auto-create Student failed for {self.name}")
			frappe.msgprint(
				_("Could not auto-create Student: {0}").format(str(e)[:120]), indicator="red"
			)
			return

		if student.get("user") and frappe.db.exists("Role", "University Student"):
			user_doc = frappe.get_doc("User", student.user)
			existing_roles = {r.role for r in user_doc.roles}
			if "University Student" not in existing_roles:
				user_doc.append("roles", {"role": "University Student"})
				user_doc.flags.ignore_permissions = True
				user_doc.save(ignore_permissions=True)

		try:
			_ensure_program_enrollment(student.name, program_to_enroll, self.academic_year)
		except Exception as e:
			frappe.log_error(
				message=str(e), title=f"Program Enrollment failed for {student.name}"
			)

		try:
			_ensure_student_group_membership(student.name, program_to_enroll)
		except Exception as e:
			frappe.log_error(
				message=str(e), title=f"Student Group enrollment failed for {student.name}"
			)

		try:
			_ensure_first_fees(student.name, program_to_enroll, self.academic_year)
		except Exception as e:
			frappe.log_error(
				message=str(e), title=f"First Fees generation failed for {student.name}"
			)

		try:
			_ensure_first_invoice(student.name, program_to_enroll, self.academic_year)
		except Exception as e:
			frappe.log_error(
				message=str(e), title=f"First invoice generation failed for {student.name}"
			)

		frappe.msgprint(
			_("Student {0} created from applicant {1}. Portal login enabled.").format(
				student.name, self.name
			),
			indicator="green",
			alert=True,
		)

	def set_title(self):
		self.title = " ".join(
			filter(None, [self.first_name, self.middle_name, self.last_name])
		)

	def validate_dates(self):
		if self.date_of_birth and getdate(self.date_of_birth) >= getdate():
			frappe.throw(_("Date of Birth cannot be greater than today."))

	def validate_term(self):
		if self.academic_year and self.academic_term:
			actual_academic_year = frappe.db.get_value(
				"Academic Term", self.academic_term, "academic_year"
			)
			if actual_academic_year != self.academic_year:
				frappe.throw(
					_("Academic Term {0} does not belong to Academic Year {1}").format(
						self.academic_term, self.academic_year
					)
				)

	def validation_from_student_admission(self):

		student_admission = get_student_admission_data(self.student_admission, self.program)

		if (
			student_admission
			and student_admission.min_age
			and date_diff(
				nowdate(), add_years(getdate(self.date_of_birth), student_admission.min_age)
			)
			< 0
		):
			frappe.throw(
				_("Not eligible for the admission in this program as per Date Of Birth")
			)

		if (
			student_admission
			and student_admission.max_age
			and date_diff(
				nowdate(), add_years(getdate(self.date_of_birth), student_admission.max_age)
			)
			> 0
		):
			frappe.throw(
				_("Not eligible for the admission in this program as per Date Of Birth")
			)

	def on_payment_authorized(self, *args, **kwargs):
		self.db_set("paid", 1)

	# =========================================================================
	# University-specific methods (absorbed from former UniversityApplicant override)
	# =========================================================================

	def generate_application_number(self):
		"""Generate unique application number"""
		if self.get("custom_application_number"):
			return

		if not self.get("custom_admission_cycle"):
			if self.docstatus == 1:
				frappe.throw(_("Admission Cycle is required before submitting"))
			return

		admission_cycle = frappe.get_doc("Admission Cycle", self.custom_admission_cycle)
		year = admission_cycle.academic_year[:4] if admission_cycle.academic_year else "2025"

		last_app = frappe.get_all(
			"Student Applicant",
			filters={"custom_admission_cycle": self.custom_admission_cycle},
			fields=["custom_application_number"],
			order_by="custom_application_number desc",
			limit=1,
		)

		if last_app and last_app[0].custom_application_number:
			parts = last_app[0].custom_application_number.split("-")
			sequence = int(parts[-1]) + 1 if len(parts) >= 3 else 1
		else:
			sequence = 1

		cycle_code = "APP"
		if "UG" in admission_cycle.name:
			cycle_code = "UG"
		elif "PG" in admission_cycle.name:
			cycle_code = "PG"

		self.custom_application_number = f"{cycle_code}-{year}-{sequence:05d}"

	def calculate_merit_score(self):
		"""Merit Score = (10th % x 0.2) + (12th % x 0.3) + (Entrance Score x 0.5)."""
		percent_10th = self.get("custom_percentage_10th") or 0.0
		percent_12th = self.get("custom_percentage_12th") or 0.0
		entrance_score = self.get("custom_entrance_exam_score") or 0.0

		merit_score = (percent_10th * 0.2) + (percent_12th * 0.3) + (entrance_score * 0.5)
		self.custom_merit_score = flt(merit_score, 2)

	def validate_category_certificate(self):
		"""Validate that reserved category applicants have uploaded certificates"""
		if not self.get("custom_category"):
			return

		reserved_categories = ["SC", "ST", "OBC", "EWS"]

		if self.custom_category in reserved_categories and not self.get(
			"custom_category_certificate"
		):
			frappe.msgprint(
				_("Category certificate is required for {0} category").format(self.custom_category),
				alert=True,
				indicator="orange",
			)

	def validate_program_preferences(self):
		"""Validate program preferences"""
		prefs = [
			self.get("custom_program_preference_1"),
			self.get("custom_program_preference_2"),
			self.get("custom_program_preference_3"),
		]

		prefs_set = set(p for p in prefs if p)
		if len(prefs_set) != len([p for p in prefs if p]):
			frappe.throw(_("Program preferences cannot have duplicate programs"))

		if not any(prefs) and self.docstatus == 1:
			frappe.throw(_("At least one program preference is required"))

	def set_admission_status(self):
		"""Set initial admission status on submission"""
		if not self.get("custom_admission_status"):
			self.custom_admission_status = "Submitted"


def get_student_admission_data(student_admission, program):

	admission_programs = frappe.get_all(
		"Student Admission Program",
		{"parenttype": "Student Admission", "parent": student_admission, "program": program},
		["applicant_naming_series", "min_age", "max_age"],
	)

	if admission_programs:
		return admission_programs[0]
	return None


# =============================================================================
# Module-level helpers (absorbed from former university_erp.overrides.student_applicant)
# =============================================================================


def _create_student_from_applicant(applicant, program_name):
	"""Create a Student record from an admitted applicant. Also creates the User."""
	student = frappe.get_doc(
		{
			"doctype": "Student",
			"first_name": applicant.first_name,
			"middle_name": applicant.middle_name,
			"last_name": applicant.last_name,
			"student_email_id": applicant.student_email_id,
			"student_mobile_number": applicant.student_mobile_number,
			"date_of_birth": applicant.date_of_birth,
			"gender": applicant.gender,
			"blood_group": applicant.blood_group,
			"nationality": applicant.nationality,
			"joining_date": frappe.utils.nowdate(),
			"student_applicant": applicant.name,
			"academic_year": applicant.academic_year,
			"academic_term": applicant.academic_term,
			"image": applicant.image,
			"enabled": 1,
		}
	)
	if hasattr(student, "custom_program"):
		student.custom_program = program_name
	if hasattr(student, "custom_category"):
		student.custom_category = applicant.get("custom_category")
	if hasattr(student, "custom_student_status"):
		student.custom_student_status = "Active"

	student.flags.ignore_permissions = True
	student.flags.ignore_mandatory = True
	student.insert(ignore_permissions=True)

	if not student.user:
		if frappe.db.exists("User", applicant.student_email_id):
			student.user = applicant.student_email_id
		else:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": applicant.student_email_id,
					"first_name": applicant.first_name,
					"last_name": applicant.last_name or "",
					"enabled": 1,
					"user_type": "Website User",
					"send_welcome_email": 0,
				}
			)
			user.append("roles", {"role": "Student"})
			user.flags.ignore_permissions = True
			user.flags.no_welcome_mail = True
			user.flags.ignore_password_policy = True
			user.insert(ignore_permissions=True)
			student.user = user.name
		student.save(ignore_permissions=True)

	return student


def _ensure_program_enrollment(student_name, program_name, academic_year):
	"""Create a Program Enrollment + Course Enrollments. Idempotent."""
	if frappe.db.exists(
		"Program Enrollment",
		{"student": student_name, "program": program_name, "academic_year": academic_year},
	):
		return

	term = frappe.db.get_value(
		"Academic Term",
		{"academic_year": academic_year} if academic_year else {},
		"name",
		order_by="creation desc",
	)
	ay_start = (
		frappe.db.get_value("Academic Year", academic_year, "year_start_date")
		if academic_year
		else None
	)
	term_start = (
		frappe.db.get_value("Academic Term", term, "term_start_date") if term else None
	)
	candidates = [d for d in (ay_start, term_start) if d]
	today = frappe.utils.getdate(frappe.utils.nowdate())
	if candidates:
		latest_start = max(frappe.utils.getdate(d) for d in candidates)
		enrollment_date = latest_start if latest_start > today else frappe.utils.nowdate()
	else:
		enrollment_date = frappe.utils.nowdate()

	pe = frappe.get_doc(
		{
			"doctype": "Program Enrollment",
			"student": student_name,
			"program": program_name,
			"academic_year": academic_year,
			"academic_term": term,
			"enrollment_date": enrollment_date,
		}
	)
	program = frappe.get_doc("Program", program_name)
	program_courses = program.courses or []
	if not program_courses:
		sg_courses = frappe.db.sql(
			"""
			SELECT DISTINCT sg.course
			FROM `tabStudent Group` sg
			WHERE sg.program = %s AND sg.course IS NOT NULL AND sg.course != ''
			LIMIT 6
		""",
			program_name,
			as_dict=True,
		)
		for row in sg_courses:
			cname = frappe.db.get_value("Course", row.course, "course_name") or row.course
			pe.append("courses", {"course": row.course, "course_name": cname, "required": 0})
	else:
		for c in program_courses:
			pe.append(
				"courses",
				{
					"course": c.course,
					"course_name": getattr(c, "course_name", None) or c.course,
					"required": getattr(c, "required", 0),
				},
			)
	pe.flags.ignore_permissions = True
	pe.insert(ignore_permissions=True)
	pe.submit()


def _ensure_student_group_membership(student_name, program_name):
	"""Add the student to existing Student Groups for the program."""
	student_doc = frappe.get_doc("Student", student_name)
	groups = frappe.db.get_all(
		"Student Group",
		filters={"program": program_name},
		fields=["name"],
		limit=6,
	)
	for g in groups:
		sg = frappe.get_doc("Student Group", g.name)
		if any(s.student == student_name for s in (sg.students or [])):
			continue
		sg.append(
			"students",
			{"student": student_name, "student_name": student_doc.student_name, "active": 1},
		)
		sg.flags.ignore_permissions = True
		sg.save(ignore_permissions=True)


def _ensure_first_fees(student_name, program_name, academic_year):
	"""Create a Fees record so the portal Fees page shows an outstanding amount."""
	if frappe.db.exists("Fees", {"student": student_name, "academic_year": academic_year}):
		return

	program_enrollment = frappe.db.get_value(
		"Program Enrollment",
		{"student": student_name, "program": program_name, "docstatus": 1},
		"name",
	)
	if not program_enrollment:
		return

	term = frappe.db.get_value(
		"Academic Term",
		{"academic_year": academic_year} if academic_year else {},
		"name",
		order_by="creation desc",
	)

	fee_structure = frappe.db.get_value(
		"Fee Structure",
		{"program": program_name, "academic_year": academic_year},
		"name",
	) or frappe.db.get_value("Fee Structure", {"program": program_name}, "name")

	amount = 0
	if fee_structure:
		amount = frappe.db.get_value("Fee Structure", fee_structure, "total_amount") or 0
	if not amount:
		amount = 50000

	fees = frappe.get_doc(
		{
			"doctype": "Fees",
			"student": student_name,
			"program": program_name,
			"program_enrollment": program_enrollment,
			"academic_year": academic_year,
			"academic_term": term,
			"fee_structure": fee_structure,
			"due_date": frappe.utils.add_days(frappe.utils.nowdate(), 30),
			"posting_date": frappe.utils.nowdate(),
			"components": [{"fees_category": "Tuition Fee", "amount": amount}]
			if frappe.db.exists("Fee Category", "Tuition Fee")
			else [],
			"grand_total": amount,
			"outstanding_amount": amount,
		}
	)
	fees.flags.ignore_permissions = True
	fees.flags.ignore_mandatory = True
	fees.insert(ignore_permissions=True)
	try:
		fees.submit()
	except Exception as e:
		frappe.log_error(message=str(e), title=f"Fees submit failed for {student_name}")


def _ensure_first_invoice(student_name, program_name, academic_year):
	"""Generate the first Sales Invoice for the new student from the program's Fee Structure."""
	student = frappe.get_doc("Student", student_name)
	if not student.get("user"):
		return

	customer = frappe.db.get_value(
		"Customer", {"customer_name": "Student Customer"}, "name"
	) or frappe.db.get_value("Customer", {}, "name")
	if not customer:
		return

	if frappe.db.exists(
		"Sales Invoice", {"customer": customer, "remarks": ["like", f"%{student_name}%"]}
	):
		return

	fee_structure = frappe.db.get_value(
		"Fee Structure",
		{"program": program_name, "academic_year": academic_year},
		["name", "total_amount"],
		as_dict=True,
	) or frappe.db.get_value(
		"Fee Structure", {"program": program_name}, ["name", "total_amount"], as_dict=True
	)

	amount = (fee_structure and fee_structure.total_amount) or 50000

	company = frappe.db.get_value("Company", {}, "name")
	income_account = frappe.db.get_value(
		"Account",
		{"company": company, "account_type": "Income Account", "is_group": 0},
		"name",
	)
	if not income_account:
		income_account = frappe.db.get_value(
			"Account",
			{"company": company, "root_type": "Income", "is_group": 0},
			"name",
		)

	si = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": customer,
			"company": company,
			"due_date": frappe.utils.add_days(frappe.utils.nowdate(), 30),
			"remarks": f"First semester fee for {student_name} ({program_name})",
			"items": [
				{
					"item_name": f"Tuition Fee — {program_name}",
					"description": f"Tuition fee for {program_name} (AY {academic_year})",
					"qty": 1,
					"rate": amount,
					"income_account": income_account,
				}
			],
		}
	)
	si.flags.ignore_permissions = True
	si.flags.ignore_mandatory = True
	si.insert(ignore_permissions=True)
	si.submit()


def allot_seat(applicant_id, program):
	"""Allot seat to an applicant for a specific program."""
	applicant = frappe.get_doc("Student Applicant", applicant_id)

	if applicant.get("custom_admission_status") not in ["Submitted", "Document Verified"]:
		frappe.throw(_("Applicant must be in Submitted or Document Verified status"))

	prefs = [
		applicant.get("custom_program_preference_1"),
		applicant.get("custom_program_preference_2"),
		applicant.get("custom_program_preference_3"),
	]

	if program not in prefs:
		frappe.throw(_("Program {0} is not in applicant's preferences").format(program))

	applicant.custom_seat_allotted = program
	applicant.custom_admission_status = "Seat Allotted"
	applicant.program = program
	applicant.save(ignore_permissions=True)

	frappe.msgprint(
		_("Seat allotted for program {0}").format(program),
		alert=True,
		indicator="green",
	)
	return applicant


def generate_merit_list(admission_cycle, program=None, category=None):
	"""Return applicants sorted by merit score for the given cycle."""
	filters = {
		"custom_admission_cycle": admission_cycle,
		"docstatus": 1,
		"custom_admission_status": ["in", ["Submitted", "Document Verified"]],
	}

	if category:
		filters["custom_category"] = category

	applicants = frappe.get_all(
		"Student Applicant",
		filters=filters,
		fields=[
			"name",
			"student_name",
			"custom_application_number",
			"custom_merit_score",
			"custom_entrance_exam_rank",
			"custom_category",
			"custom_program_preference_1",
			"custom_program_preference_2",
			"custom_program_preference_3",
			"custom_percentage_10th",
			"custom_percentage_12th",
			"custom_entrance_exam_score",
		],
		order_by="custom_merit_score desc, custom_entrance_exam_rank asc",
	)

	if program:
		applicants = [
			app
			for app in applicants
			if program
			in [
				app.custom_program_preference_1,
				app.custom_program_preference_2,
				app.custom_program_preference_3,
			]
		]

	for idx, app in enumerate(applicants, start=1):
		app["rank"] = idx

	return applicants


def bulk_seat_allotment(admission_cycle, program, num_seats, category=None):
	"""Perform bulk seat allotment based on merit."""
	merit_list = generate_merit_list(admission_cycle, program, category)
	allotted_count = 0

	for applicant in merit_list[:num_seats]:
		try:
			allot_seat(applicant.name, program)
			allotted_count += 1
		except Exception as e:
			frappe.logger().error(
				f"Error allotting seat to {applicant.name}: {str(e)}"
			)
			continue

	frappe.msgprint(
		_("{0} seats allotted for program {1}").format(allotted_count, program),
		alert=True,
		indicator="green",
	)
	return allotted_count


def create_student_from_applicant(applicant_id):
	"""Standalone function to create a Student from an admitted applicant."""
	applicant = frappe.get_doc("Student Applicant", applicant_id)

	if applicant.get("custom_admission_status") != "Admission Confirmed":
		frappe.throw(
			_("Applicant must confirm admission before creating student record")
		)

	if not applicant.get("custom_seat_allotted"):
		frappe.throw(_("No seat allotted to applicant"))

	if applicant.application_status == "Admitted":
		existing_student = frappe.db.get_value(
			"Student", {"student_applicant": applicant.name}
		)
		if existing_student:
			frappe.throw(_("Student record already exists: {0}").format(existing_student))

	student = applicant.create_student()
	student.custom_program = applicant.custom_seat_allotted
	student.custom_category = applicant.get("custom_category")
	student.custom_student_status = "Active"
	student.save(ignore_permissions=True)

	applicant.custom_admission_status = "Admitted"
	applicant.save(ignore_permissions=True)

	return student

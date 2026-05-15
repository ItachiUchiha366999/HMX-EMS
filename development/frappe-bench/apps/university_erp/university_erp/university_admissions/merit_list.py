# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, flt


class MeritListGenerator:
	"""Generate merit lists for admission"""

	def __init__(self, admission_cycle, program, category=None):
		self.admission_cycle = admission_cycle
		self.program = program
		self.category = category

	def generate(self):
		"""Generate merit list based on merit scores"""
		filters = {
			"custom_admission_cycle": self.admission_cycle,
			"program": self.program,
			"docstatus": 1,
			"application_status": ["not in", ["Rejected", "Admitted"]]
		}

		if self.category:
			filters["custom_category"] = self.category

		applicants = frappe.get_all(
			"Student Applicant",
			filters=filters,
			fields=[
				"name", "first_name", "last_name", "custom_merit_score",
				"custom_category", "custom_previous_percentage",
				"custom_entrance_score"
			],
			order_by="custom_merit_score desc"
		)

		if not applicants:
			frappe.msgprint(f"No applicants found for {self.program}" +
				(f" in {self.category} category" if self.category else ""))
			return None

		# Create merit list document
		merit_list = frappe.new_doc("Merit List")
		merit_list.admission_cycle = self.admission_cycle
		merit_list.program = self.program
		merit_list.category = self.category
		merit_list.generation_date = today()

		for rank, applicant in enumerate(applicants, 1):
			merit_list.append("applicants", {
				"applicant": applicant.name,
				"applicant_name": f"{applicant.first_name} {applicant.last_name or ''}".strip(),
				"merit_rank": rank,
				"merit_score": applicant.custom_merit_score,
				"category": applicant.custom_category
			})

			# Update rank on applicant
			frappe.db.set_value(
				"Student Applicant",
				applicant.name,
				"custom_merit_rank",
				rank,
				update_modified=False
			)

		merit_list.insert()
		frappe.db.commit()

		return merit_list.name


class MeritListProcessor:
	"""Process merit lists for seat allotment"""

	def __init__(self, merit_list_name):
		self.merit_list = frappe.get_doc("Merit List", merit_list_name)

	def allot_seats(self, count=None):
		"""Allot seats to top candidates"""
		if self.merit_list.docstatus != 1:
			frappe.throw("Merit list must be submitted before seat allotment")

		# Get seat matrix
		seat_matrix = self.get_seat_matrix()
		if not seat_matrix:
			frappe.throw("Seat Matrix not found for this program and cycle")

		# Get available seats
		category_field = self.get_category_field()
		available_seats = seat_matrix.get(category_field) or 0

		if available_seats <= 0:
			frappe.throw(f"No seats available in {self.merit_list.category or 'General'} category")

		# Limit by available seats
		if count:
			seats_to_allot = min(count, available_seats)
		else:
			seats_to_allot = available_seats

		allotted_count = 0
		for applicant in self.merit_list.applicants[:seats_to_allot]:
			if not applicant.seat_allotted:
				# Update applicant
				applicant.seat_allotted = 1

				# Update Student Applicant status
				frappe.db.set_value(
					"Student Applicant",
					applicant.applicant,
					"custom_seat_allotted",
					self.merit_list.program,
					update_modified=False
				)

				allotted_count += 1

		# Save merit list
		self.merit_list.save()

		# Update seat matrix
		self.update_seat_matrix(seat_matrix, allotted_count)

		frappe.db.commit()

		frappe.msgprint(f"Allotted {allotted_count} seats from merit list")
		return allotted_count

	def get_seat_matrix(self):
		"""Get seat matrix for this merit list"""
		seat_matrix_name = frappe.db.get_value(
			"Seat Matrix",
			{
				"admission_cycle": self.merit_list.admission_cycle,
				"program": self.merit_list.program
			}
		)

		if seat_matrix_name:
			return frappe.get_doc("Seat Matrix", seat_matrix_name)
		return None

	def get_category_field(self):
		"""Get field name for category seats"""
		category_map = {
			"General": "general_seats",
			"OBC": "obc_seats",
			"SC": "sc_seats",
			"ST": "st_seats",
			"EWS": "ews_seats",
			"PWD": "pwd_seats"
		}
		return category_map.get(self.merit_list.category, "general_seats")

	def update_seat_matrix(self, seat_matrix, count):
		"""Update filled seats in seat matrix"""
		seat_matrix.filled_seats = (seat_matrix.filled_seats or 0) + count
		seat_matrix.available_seats = seat_matrix.total_seats - seat_matrix.filled_seats
		seat_matrix.save()


@frappe.whitelist()
def generate_merit_list(admission_cycle, program, category=None):
	"""API to generate merit list"""
	generator = MeritListGenerator(admission_cycle, program, category)
	return generator.generate()


@frappe.whitelist()
def allot_seats_from_merit_list(merit_list_name, count=None):
	"""API to allot seats from merit list"""
	processor = MeritListProcessor(merit_list_name)
	return processor.allot_seats(int(count) if count else None)


@frappe.whitelist()
def generate_all_category_merit_lists(admission_cycle, program):
	"""Generate merit lists for all categories"""
	categories = ["General", "OBC", "SC", "ST", "EWS", "PWD"]
	created_lists = []

	for category in categories:
		try:
			generator = MeritListGenerator(admission_cycle, program, category)
			merit_list = generator.generate()
			if merit_list:
				created_lists.append(merit_list)
		except Exception as e:
			frappe.log_error(f"Failed to generate merit list for {category}: {str(e)}")

	return created_lists

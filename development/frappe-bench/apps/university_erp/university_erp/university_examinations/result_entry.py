# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


class ResultEntryTool:
	"""Tool for entering and managing exam results"""

	# 10-Point CBCS Grading Scale
	GRADE_SCALE = [
		{"min": 90.0, "max": 100.0, "grade": "O", "grade_points": 10.0, "description": "Outstanding"},
		{"min": 80.0, "max": 89.99, "grade": "A+", "grade_points": 9.0, "description": "Excellent"},
		{"min": 70.0, "max": 79.99, "grade": "A", "grade_points": 8.0, "description": "Very Good"},
		{"min": 60.0, "max": 69.99, "grade": "B+", "grade_points": 7.0, "description": "Good"},
		{"min": 50.0, "max": 59.99, "grade": "B", "grade_points": 6.0, "description": "Above Average"},
		{"min": 45.0, "max": 49.99, "grade": "C", "grade_points": 5.0, "description": "Average"},
		{"min": 40.0, "max": 44.99, "grade": "P", "grade_points": 4.0, "description": "Pass"},
		{"min": 0.0, "max": 39.99, "grade": "F", "grade_points": 0.0, "description": "Fail"},
	]

	def __init__(self, course, academic_term, exam_type="End-Term"):
		self.course = course
		self.academic_term = academic_term
		self.exam_type = exam_type

	def get_students_for_entry(self):
		"""Get list of students enrolled in the course"""
		students = frappe.get_all(
			"Course Enrollment",
			filters={
				"course": self.course,
				"academic_term": self.academic_term
			},
			fields=["student", "student_name"]
		)

		# Get existing results
		for student in students:
			result = frappe.db.get_value(
				"Assessment Result",
				{
					"student": student.student,
					"course": self.course,
					"custom_exam_type": self.exam_type,
					"custom_academic_term": self.academic_term
				},
				["name", "custom_percentage", "custom_grade", "docstatus"],
				as_dict=True
			)
			student.update(result or {})

		return students

	def save_results(self, results_data):
		"""Save exam results for students"""
		saved = []
		failed = []

		for result in results_data:
			try:
				student = result.get("student")
				percentage = flt(result.get("percentage"))
				is_absent = result.get("is_absent", False)

				# Determine grade
				grade_info = self.determine_grade(percentage) if not is_absent else None

				# Check if result exists
				existing = frappe.db.get_value(
					"Assessment Result",
					{
						"student": student,
						"course": self.course,
						"custom_exam_type": self.exam_type,
						"custom_academic_term": self.academic_term
					}
				)

				if existing:
					# Update existing
					doc = frappe.get_doc("Assessment Result", existing)
				else:
					# Create new
					doc = frappe.new_doc("Assessment Result")
					doc.student = student
					doc.course = self.course
					doc.custom_exam_type = self.exam_type
					doc.custom_academic_term = self.academic_term

				# Set values
				doc.custom_percentage = percentage if not is_absent else 0.0
				doc.custom_is_absent = is_absent

				if is_absent:
					doc.custom_grade = "AB"
					doc.custom_grade_points = 0.0
					doc.custom_result_status = "Absent"
				elif grade_info:
					doc.custom_grade = grade_info["grade"]
					doc.custom_grade_points = grade_info["grade_points"]
					doc.custom_result_status = "Pass" if grade_info["grade"] != "F" else "Fail"

				# Get course credits
				credits = frappe.db.get_value("Course", self.course, "custom_credits")
				doc.custom_credits = credits or 0.0

				if doc.is_new():
					doc.insert(ignore_permissions=True)
				else:
					doc.save(ignore_permissions=True)

				saved.append(doc.name)

			except Exception as e:
				failed.append({
					"student": result.get("student"),
					"error": str(e)
				})
				frappe.log_error(f"Result entry failed: {str(e)}")

		frappe.db.commit()

		return {
			"saved": len(saved),
			"failed": len(failed),
			"results": saved,
			"errors": failed
		}

	def determine_grade(self, percentage):
		"""Determine grade based on percentage"""
		for grade in self.GRADE_SCALE:
			if grade["min"] <= percentage <= grade["max"]:
				return grade
		return self.GRADE_SCALE[-1]  # Return F if not found

	def apply_moderation(self, moderation_percentage):
		"""Apply moderation to all results"""
		results = frappe.get_all(
			"Assessment Result",
			filters={
				"course": self.course,
				"custom_exam_type": self.exam_type,
				"custom_academic_term": self.academic_term,
				"docstatus": 0
			}
		)

		moderated = 0
		for result_name in results:
			doc = frappe.get_doc("Assessment Result", result_name.name)

			if doc.custom_is_absent:
				continue

			# Apply moderation
			original = doc.custom_percentage
			moderated_percentage = min(100.0, original + flt(moderation_percentage))

			doc.custom_percentage = moderated_percentage

			# Recalculate grade
			grade_info = self.determine_grade(moderated_percentage)
			doc.custom_grade = grade_info["grade"]
			doc.custom_grade_points = grade_info["grade_points"]
			doc.custom_result_status = "Pass" if grade_info["grade"] != "F" else "Fail"

			doc.save(ignore_permissions=True)
			moderated += 1

		frappe.db.commit()

		return {
			"moderated": moderated,
			"moderation_applied": moderation_percentage
		}

	def submit_all_results(self):
		"""Submit all results for the course"""
		results = frappe.get_all(
			"Assessment Result",
			filters={
				"course": self.course,
				"custom_exam_type": self.exam_type,
				"custom_academic_term": self.academic_term,
				"docstatus": 0
			}
		)

		submitted = 0
		for result_name in results:
			doc = frappe.get_doc("Assessment Result", result_name.name)
			doc.submit()
			submitted += 1

		frappe.db.commit()

		return {
			"submitted": submitted
		}

	def get_statistics(self):
		"""Get result statistics"""
		results = frappe.get_all(
			"Assessment Result",
			filters={
				"course": self.course,
				"custom_exam_type": self.exam_type,
				"custom_academic_term": self.academic_term
			},
			fields=["custom_grade", "custom_percentage", "custom_is_absent"]
		)

		total = len(results)
		absent = len([r for r in results if r.custom_is_absent])
		present = total - absent

		# Grade distribution
		grade_dist = {}
		percentages = []

		for result in results:
			if not result.custom_is_absent:
				grade = result.custom_grade
				grade_dist[grade] = grade_dist.get(grade, 0) + 1
				percentages.append(result.custom_percentage)

		# Calculate statistics
		stats = {
			"total_students": total,
			"absent": absent,
			"present": present,
			"pass_count": sum([count for grade, count in grade_dist.items() if grade != "F"]),
			"fail_count": grade_dist.get("F", 0),
			"grade_distribution": grade_dist
		}

		if percentages:
			stats["average"] = round(sum(percentages) / len(percentages), 2)
			stats["highest"] = max(percentages)
			stats["lowest"] = min(percentages)

		return stats


@frappe.whitelist()
def get_students_for_result_entry(course, academic_term, exam_type="End-Term"):
	"""API to get students for result entry"""
	tool = ResultEntryTool(course, academic_term, exam_type)
	return tool.get_students_for_entry()


@frappe.whitelist()
def save_exam_results(course, academic_term, exam_type, results_data):
	"""API to save exam results"""
	if isinstance(results_data, str):
		import json
		results_data = json.loads(results_data)

	tool = ResultEntryTool(course, academic_term, exam_type)
	return tool.save_results(results_data)


@frappe.whitelist()
def apply_result_moderation(course, academic_term, exam_type, moderation):
	"""API to apply moderation"""
	tool = ResultEntryTool(course, academic_term, exam_type)
	return tool.apply_moderation(flt(moderation))


@frappe.whitelist()
def submit_course_results(course, academic_term, exam_type):
	"""API to submit all results"""
	tool = ResultEntryTool(course, academic_term, exam_type)
	return tool.submit_all_results()


@frappe.whitelist()
def get_result_statistics(course, academic_term, exam_type):
	"""API to get result statistics"""
	tool = ResultEntryTool(course, academic_term, exam_type)
	return tool.get_statistics()

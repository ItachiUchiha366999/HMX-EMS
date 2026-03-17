#!/bin/bash

# Phase 6 - Update remaining controllers with logic

cd /workspace/development/frappe-bench/apps/university_erp

echo "Updating Faculty Performance Evaluation controller..."
cat > university_erp/university_hr/doctype/faculty_performance_evaluation/faculty_performance_evaluation.py << 'EOF'
# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class FacultyPerformanceEvaluation(Document):
	def validate(self):
		"""Calculate scores before saving"""
		self.fetch_metrics()
		self.calculate_teaching_score()
		self.calculate_research_score()
		self.calculate_service_score()
		self.calculate_total_score()
		self.determine_grade()

	def fetch_metrics(self):
		"""Fetch metrics from Faculty Profile and other sources"""
		if not self.employee:
			return

		# Get faculty profile
		faculty_profile = frappe.db.get_value("Faculty Profile", {"employee": self.employee}, "name")
		if faculty_profile:
			profile = frappe.get_doc("Faculty Profile", faculty_profile)
			self.publications_count = len(profile.publications) if profile.publications else 0
			self.scopus_publications = len([p for p in profile.publications if p.scopus_indexed]) if profile.publications else 0
			self.research_projects_count = len(profile.research_projects) if profile.research_projects else 0

		# Get student feedback average for the year
		feedback_avg = frappe.db.sql("""
			SELECT AVG(overall_rating) as avg_rating
			FROM `tabStudent Feedback`
			WHERE instructor = %s
				AND academic_year = %s
				AND docstatus = 1
		""", (self.employee, self.academic_year), as_dict=True)

		if feedback_avg and feedback_avg[0].avg_rating:
			self.student_feedback_score = flt(feedback_avg[0].avg_rating, 2)

	def calculate_teaching_score(self):
		"""Calculate teaching score (out of 40)"""
		# Teaching completion = 20 points
		if self.classes_scheduled > 0:
			completion_percent = (self.classes_conducted / self.classes_scheduled) * 100
			self.teaching_completion_percent = flt(completion_percent, 2)
			completion_score = (completion_percent / 100) * 20
		else:
			completion_score = 0

		# Student feedback = 15 points (scaled from 5-point rating)
		feedback_score = ((self.student_feedback_score or 0) / 5) * 15

		# Teaching rating = 5 points (scaled from 5-point rating)
		rating_score = ((self.teaching_rating or 0) / 5) * 5

		self.teaching_score = flt(completion_score + feedback_score + rating_score, 2)

	def calculate_research_score(self):
		"""Calculate research score (out of 35)"""
		# Publications = 15 points (1 point per publication, max 15)
		pub_score = min(self.publications_count or 0, 15)

		# Scopus publications = 10 points (2 points per Scopus pub, max 10)
		scopus_score = min((self.scopus_publications or 0) * 2, 10)

		# Research projects = 5 points (2 points per project, max 5)
		project_score = min((self.research_projects_count or 0) * 2, 5)

		# Patents = 3 points (1.5 points per patent, max 3)
		patent_score = min((self.patents_filed or 0) * 1.5, 3)

		# PhD guidance = 2 points (1 point per student, max 2)
		phd_score = min((self.phd_students_guided or 0), 2)

		self.research_score = flt(pub_score + scopus_score + project_score + patent_score + phd_score, 2)

	def calculate_service_score(self):
		"""Calculate service score (out of 25)"""
		# Committee memberships = 10 points (2 points each, max 10)
		committee_score = min((self.committee_memberships or 0) * 2, 10)

		# Student mentoring = 8 points (0.5 points per student, max 8)
		mentoring_score = min((self.student_mentoring or 0) * 0.5, 8)

		# Outreach activities = 7 points (1.5 points each, max 7)
		outreach_score = min((self.outreach_activities or 0) * 1.5, 7)

		self.service_score = flt(committee_score + mentoring_score + outreach_score, 2)

	def calculate_total_score(self):
		"""Calculate total score"""
		self.total_score = flt(
			(self.teaching_score or 0) +
			(self.research_score or 0) +
			(self.service_score or 0),
			2
		)

	def determine_grade(self):
		"""Determine grade based on total score"""
		score = self.total_score or 0
		if score >= 90:
			self.grade = "Outstanding (90-100)"
		elif score >= 80:
			self.grade = "Excellent (80-89)"
		elif score >= 70:
			self.grade = "Very Good (70-79)"
		elif score >= 60:
			self.grade = "Good (60-69)"
		elif score >= 50:
			self.grade = "Satisfactory (50-59)"
		else:
			self.grade = "Needs Improvement (<50)"
EOF

echo "✓ Faculty Performance Evaluation controller updated"

echo "Updating Student Feedback controller..."
cat > university_erp/university_hr/doctype/student_feedback/student_feedback.py << 'EOF'
# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StudentFeedback(Document):
	def validate(self):
		"""Validate feedback before submission"""
		self.validate_ratings()

	def validate_ratings(self):
		"""Ensure all ratings are within 1-5"""
		ratings = [
			self.subject_knowledge,
			self.teaching_methodology,
			self.communication_skills,
			self.availability,
			self.course_coverage,
			self.overall_rating
		]
		for rating in ratings:
			if rating and (rating < 1 or rating > 5):
				frappe.throw(_("All ratings must be between 1 and 5"))


@frappe.whitelist()
def get_pending_feedback(student, academic_term):
	"""Get list of courses for which student hasn't submitted feedback"""
	# Get all enrolled courses
	enrolled_courses = frappe.db.sql("""
		SELECT DISTINCT pe.course, pe.instructor, c.course_name
		FROM `tabProgram Enrollment` pe
		LEFT JOIN `tabCourse` c ON pe.course = c.name
		WHERE pe.student = %s
			AND pe.academic_term = %s
			AND pe.docstatus = 1
	""", (student, academic_term), as_dict=True)

	# Get courses with existing feedback
	existing_feedback = frappe.db.sql("""
		SELECT course, instructor
		FROM `tabStudent Feedback`
		WHERE student = %s
			AND academic_term = %s
			AND docstatus = 1
	""", (student, academic_term), as_dict=True)

	feedback_set = {(f.course, f.instructor) for f in existing_feedback}
	pending = [c for c in enrolled_courses if (c.course, c.instructor) not in feedback_set]

	return pending


@frappe.whitelist()
def get_feedback_summary(instructor, academic_year=None):
	"""Get feedback summary for an instructor"""
	filters = {"instructor": instructor, "docstatus": 1}
	if academic_year:
		filters["academic_year"] = academic_year

	feedbacks = frappe.get_all(
		"Student Feedback",
		filters=filters,
		fields=[
			"subject_knowledge", "teaching_methodology", "communication_skills",
			"availability", "course_coverage", "overall_rating", "course"
		]
	)

	if not feedbacks:
		return {
			"count": 0,
			"averages": {}
		}

	# Calculate averages
	total = len(feedbacks)
	averages = {
		"subject_knowledge": sum([f.subject_knowledge for f in feedbacks]) / total,
		"teaching_methodology": sum([f.teaching_methodology for f in feedbacks]) / total,
		"communication_skills": sum([f.communication_skills for f in feedbacks]) / total,
		"availability": sum([f.availability for f in feedbacks]) / total,
		"course_coverage": sum([f.course_coverage for f in feedbacks]) / total,
		"overall_rating": sum([f.overall_rating for f in feedbacks]) / total
	}

	return {
		"count": total,
		"averages": averages,
		"feedbacks": feedbacks
	}
EOF

echo "✓ Student Feedback controller updated"

echo "Updating UGC Pay Scale controller..."
cat > university_erp/university_hr/doctype/ugc_pay_scale/ugc_pay_scale.py << 'EOF'
# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class UGCPayScale(Document):
	def validate(self):
		"""Calculate gross salary before saving"""
		self.calculate_gross_salary()

	def calculate_gross_salary(self):
		"""Calculate gross monthly salary"""
		basic = flt(self.basic_pay or 0)
		agp = flt(self.agp or 0)
		da_pct = flt(self.da_percentage or 0) / 100
		hra_pct = flt(self.hra_percentage or 0) / 100
		transport = flt(self.transport_allowance or 0)

		da = (basic + agp) * da_pct
		hra = basic * hra_pct

		self.gross_salary = flt(basic + agp + da + hra + transport, 2)
EOF

echo "✓ UGC Pay Scale controller updated"

echo "Updating Workload Distributor controller..."
cat > university_erp/university_hr/doctype/workload_distributor/workload_distributor.py << 'EOF'
# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WorkloadDistributor(Document):
	def onload(self):
		"""Load workload analysis when form loads"""
		self.analyze_workload()

	def analyze_workload(self):
		"""Analyze workload distribution"""
		if not self.academic_term:
			return

		# Get all courses for the term
		filters = {"academic_term": self.academic_term}
		if self.program:
			filters["program"] = self.program

		all_courses = frappe.get_all("Course", filters=filters, fields=["name", "course_name"])
		self.total_courses = len(all_courses)

		# Get assigned courses
		assigned = frappe.get_all(
			"Teaching Assignment",
			filters={"academic_term": self.academic_term, "docstatus": 1},
			fields=["course"]
		)
		assigned_courses = {a.course for a in assigned}
		self.assigned_courses = len(assigned_courses)
		self.unassigned_courses = self.total_courses - self.assigned_courses

		# Get faculty workload
		faculty_workload = frappe.db.sql("""
			SELECT e.name, e.employee_name, e.custom_current_workload
			FROM `tabEmployee` e
			WHERE e.custom_is_faculty = 1
				AND e.status = 'Active'
				{dept_filter}
			ORDER BY e.custom_current_workload DESC
		""".format(dept_filter=f"AND e.department = '{self.department}'" if self.department else ""),
		as_dict=True)

		self.total_faculty = len(faculty_workload)
		self.overloaded_faculty = len([f for f in faculty_workload if (f.custom_current_workload or 0) > 18])
		self.underutilized_faculty = len([f for f in faculty_workload if (f.custom_current_workload or 0) < 12])

		# Generate recommendations HTML
		recommendations = []
		if self.unassigned_courses > 0:
			recommendations.append(f"<li><strong>{self.unassigned_courses} courses</strong> need instructor assignment</li>")

		if self.overloaded_faculty > 0:
			recommendations.append(f"<li><strong>{self.overloaded_faculty} faculty members</strong> are overloaded (>18 hrs/week)</li>")

		if self.underutilized_faculty > 0:
			recommendations.append(f"<li><strong>{self.underutilized_faculty} faculty members</strong> are underutilized (<12 hrs/week)</li>")

		if recommendations:
			self.recommendations = f"<ul>{''.join(recommendations)}</ul>"
		else:
			self.recommendations = "<p><strong>All courses are assigned and faculty workload is balanced.</strong></p>"


@frappe.whitelist()
def get_available_faculty(academic_term, department=None):
	"""Get list of available faculty for assignment"""
	filters = {"custom_is_faculty": 1, "status": "Active"}
	if department:
		filters["department"] = department

	faculty = frappe.get_all(
		"Employee",
		filters=filters,
		fields=["name", "employee_name", "custom_current_workload", "custom_specialization"],
		order_by="custom_current_workload"
	)

	return faculty
EOF

echo "✓ Workload Distributor controller updated"

echo "Updating Faculty Attendance controller..."
cat > university_erp/university_hr/doctype/faculty_attendance/faculty_attendance.py << 'EOF'
# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FacultyAttendance(Document):
	def validate(self):
		"""Calculate scheduled classes for the day"""
		if self.employee and self.attendance_date:
			self.get_scheduled_classes()

	def get_scheduled_classes(self):
		"""Get number of scheduled classes for this faculty on this date"""
		from datetime import datetime
		date_obj = datetime.strptime(str(self.attendance_date), "%Y-%m-%d")
		day_name = date_obj.strftime("%A")

		# Get teaching assignments for this day
		scheduled = frappe.db.sql("""
			SELECT COUNT(*) as count
			FROM `tabTeaching Assignment Schedule` tas
			INNER JOIN `tabTeaching Assignment` ta ON tas.parent = ta.name
			WHERE ta.instructor = %s
				AND ta.docstatus = 1
				AND tas.day = %s
		""", (self.employee, day_name), as_dict=True)

		self.scheduled_classes = scheduled[0].count if scheduled else 0


@frappe.whitelist()
def get_daily_schedule(employee, date):
	"""Get daily teaching schedule for a faculty member"""
	from datetime import datetime
	date_obj = datetime.strptime(str(date), "%Y-%m-%d")
	day_name = date_obj.strftime("%A")

	schedule = frappe.db.sql("""
		SELECT tas.start_time, tas.end_time, tas.room, tas.type,
			   ta.course, ta.course_name, ta.program
		FROM `tabTeaching Assignment Schedule` tas
		INNER JOIN `tabTeaching Assignment` ta ON tas.parent = ta.name
		WHERE ta.instructor = %s
			AND ta.docstatus = 1
			AND tas.day = %s
		ORDER BY tas.start_time
	""", (employee, day_name), as_dict=True)

	return schedule
EOF

echo "✓ Faculty Attendance controller updated"

echo "✓ All Phase 6 controllers updated successfully"

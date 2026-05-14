# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import erpnext
import frappe
from erpnext.accounts.doctype.payment_request.payment_request import (
	make_payment_request,
)
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe import _
from frappe.utils import date_diff, flt, getdate, money_in_words
from frappe.utils.csvutils import getlink


class Fees(AccountsController):
	def set_indicator(self):
		"""Set indicator for portal"""
		if self.outstanding_amount > 0:
			self.indicator_color = "orange"
			self.indicator_title = _("Unpaid")
		else:
			self.indicator_color = "green"
			self.indicator_title = _("Paid")

	def validate(self):
		self.calculate_total()
		self.set_missing_accounts_and_fields()
		self.validate_enrollment()

		# University-specific validations (absorbed from former UniversityFees override)
		self.calculate_penalty()
		self.calculate_net_amount()

	def before_submit(self):
		# University-specific pre-submit (absorbed from former UniversityFees override)
		self.validate_payment()

	def set_missing_accounts_and_fields(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().company
		if not self.currency:
			self.currency = erpnext.get_company_currency(self.company)
		if not (self.receivable_account and self.income_account and self.cost_center):
			accounts_details = frappe.get_all(
				"Company",
				fields=["default_receivable_account", "default_income_account", "cost_center"],
				filters={"name": self.company},
			)[0]
		if not self.receivable_account:
			self.receivable_account = accounts_details.default_receivable_account
		if not self.income_account:
			self.income_account = accounts_details.default_income_account
		if not self.cost_center:
			self.cost_center = accounts_details.cost_center
		if not self.contact_email:
			self.contact_email = self.get_student_emails()

	def validate_enrollment(self):
		enrollment_student = frappe.db.get_value(
			"Program Enrollment", self.program_enrollment, "student"
		)
		if enrollment_student != self.student:
			frappe.throw(
				_("Invalid Enrollment {0} for student {1}").format(
					frappe.bold(self.program_enrollment), frappe.bold(self.student)
				)
			)

	def get_student_emails(self):
		student_emails = frappe.db.sql_list(
			"""
			select g.email_address
			from `tabGuardian` g, `tabStudent Guardian` sg
			where g.name = sg.guardian and sg.parent = %s and sg.parenttype = 'Student'
			and ifnull(g.email_address, '')!=''
		""",
			self.student,
		)

		student_email_id = frappe.db.get_value("Student", self.student, "student_email_id")
		if student_email_id:
			student_emails.append(student_email_id)
		if student_emails:
			return ", ".join(list(set(student_emails)))
		else:
			return None

	def calculate_total(self):
		"""Calculates total amount."""
		self.grand_total = 0
		for d in self.components:
			self.grand_total += d.amount
		self.outstanding_amount = self.grand_total
		self.grand_total_in_words = money_in_words(self.grand_total)

	def on_submit(self):

		self.make_gl_entries()

		if self.send_payment_request and self.contact_email:
			pr = make_payment_request(
				party_type="Student",
				party=self.student,
				dt="Fees",
				dn=self.name,
				recipient_id=self.contact_email,
				submit_doc=True,
				use_dummy_message=True,
			)
			frappe.msgprint(
				_("Payment request {0} created").format(getlink("Payment Request", pr.name))
			)

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

	def make_gl_entries(self):
		if not self.grand_total:
			return
		student_gl_entries = self.get_gl_dict(
			{
				"account": self.receivable_account,
				"party_type": "Student",
				"party": self.student,
				"against": self.income_account,
				"debit": self.grand_total,
				"debit_in_account_currency": self.grand_total,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
			},
			item=self,
		)

		fee_gl_entry = self.get_gl_dict(
			{
				"account": self.income_account,
				"against": self.student,
				"credit": self.grand_total,
				"credit_in_account_currency": self.grand_total,
				"cost_center": self.cost_center,
			},
			item=self,
		)

		from erpnext.accounts.general_ledger import make_gl_entries

		make_gl_entries(
			[student_gl_entries, fee_gl_entry],
			cancel=(self.docstatus == 2),
			update_outstanding="Yes",
			merge_entries=False,
		)

	# =========================================================================
	# University-specific methods (absorbed from former UniversityFees override)
	# =========================================================================

	def calculate_penalty(self):
		"""Calculate late fee penalty if payment is overdue.

		Penalty = Grand Total x (Penalty Percentage / 100) x Number of Periods
		"""
		if not self.get("custom_penalty_applicable"):
			self.custom_penalty_amount = 0.0
			return

		if not self.get("custom_due_date"):
			self.custom_penalty_amount = 0.0
			return

		if self.docstatus == 1 and self.outstanding_amount == 0:
			return

		today = getdate()
		due_date = getdate(self.custom_due_date)

		if today <= due_date:
			self.custom_penalty_amount = 0.0
			return

		days_overdue = date_diff(today, due_date)

		if days_overdue <= 0:
			self.custom_penalty_amount = 0.0
			return

		penalty_period = self.get("custom_penalty_period_days") or 7
		penalty_percentage = self.get("custom_penalty_percentage") or 0.0

		num_periods = (days_overdue // penalty_period) + 1

		grand_total = self.grand_total or 0.0
		penalty = grand_total * (penalty_percentage / 100) * num_periods

		self.custom_penalty_amount = flt(penalty, 2)

		if penalty > 0:
			frappe.msgprint(
				_("Late fee penalty of {0} applied ({1} days overdue)").format(
					frappe.utils.fmt_money(penalty, currency=self.currency), days_overdue
				),
				alert=True,
				indicator="orange",
			)

	def calculate_net_amount(self):
		"""Net Amount = Grand Total - Scholarship + Penalty."""
		grand_total = self.grand_total or 0.0
		scholarship = self.get("custom_scholarship_amount") or 0.0
		penalty = self.get("custom_penalty_amount") or 0.0

		self.custom_net_amount = flt(grand_total - scholarship + penalty, 2)

		if self.docstatus == 0:
			self.outstanding_amount = self.custom_net_amount

	def validate_payment(self):
		"""Validate payment before submission"""
		if self.outstanding_amount > 0:
			frappe.msgprint(
				_(
					"Outstanding amount: {0}. Ensure payment is received before submitting."
				).format(
					frappe.utils.fmt_money(self.outstanding_amount, currency=self.currency)
				),
				alert=True,
				indicator="orange",
			)


def get_fee_list(
	doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"
):
	user = frappe.session.user
	student = frappe.db.sql(
		"select name from `tabStudent` where student_email_id= %s", user
	)
	if student:
		return frappe.db.sql(
			"""
			select name, program, due_date, grand_total - outstanding_amount as paid_amount,
			outstanding_amount, grand_total, currency
			from `tabFees`
			where student= %s and docstatus=1
			order by due_date asc limit {0} , {1}""".format(
				limit_start, limit_page_length
			),
			student,
			as_dict=True,
		)


def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		"no_breadcrumbs": True,
		"title": _("Fees"),
		"get_list": get_fee_list,
		"row_template": "templates/includes/fee/fee_row.html",
	}


# =============================================================================
# Module-level helpers (absorbed from former university_erp.overrides.fees)
# =============================================================================


def calculate_late_fees():
	"""Scheduled task to calculate late fees for all pending fees."""
	overdue_fees = frappe.get_all(
		"Fees",
		filters={
			"docstatus": 1,
			"outstanding_amount": (">", 0),
			"custom_due_date": ("<", getdate()),
			"custom_penalty_applicable": 1,
		},
		fields=["name"],
	)

	for fee in overdue_fees:
		try:
			fee_doc = frappe.get_doc("Fees", fee.name)
			old_penalty = fee_doc.get("custom_penalty_amount") or 0.0

			fee_doc.calculate_penalty()
			fee_doc.calculate_net_amount()

			if fee_doc.custom_penalty_amount != old_penalty:
				fee_doc.save(ignore_permissions=True)

				frappe.logger().info(
					f"Updated penalty for {fee_doc.name}: {old_penalty} -> {fee_doc.custom_penalty_amount}"
				)

		except Exception as e:
			frappe.logger().error(f"Error calculating late fee for {fee.name}: {str(e)}")
			continue


def apply_scholarship(student, scholarship_amount, fee_category=None):
	"""Apply scholarship to student's fees."""
	filters = {"student": student, "docstatus": 0}

	if fee_category:
		filters["custom_fee_category"] = fee_category

	fees_list = frappe.get_all(
		"Fees",
		filters=filters,
		fields=["name", "grand_total"],
		order_by="due_date",
	)

	remaining_scholarship = scholarship_amount

	for fee in fees_list:
		if remaining_scholarship <= 0:
			break

		fee_doc = frappe.get_doc("Fees", fee.name)
		applicable_scholarship = min(remaining_scholarship, fee_doc.grand_total)

		fee_doc.custom_scholarship_amount = applicable_scholarship
		fee_doc.calculate_net_amount()
		fee_doc.save(ignore_permissions=True)

		remaining_scholarship -= applicable_scholarship

		frappe.logger().info(
			f"Applied scholarship of {applicable_scholarship} to {fee_doc.name}"
		)

	return scholarship_amount - remaining_scholarship


def get_fee_summary(student, academic_year=None):
	"""Get fee summary for a student"""
	filters = {"student": student}

	if academic_year:
		filters["academic_year"] = academic_year

	fees_list = frappe.get_all(
		"Fees",
		filters=filters,
		fields=[
			"name",
			"custom_fee_category",
			"due_date",
			"grand_total",
			"custom_scholarship_amount",
			"custom_penalty_amount",
			"custom_net_amount",
			"outstanding_amount",
			"docstatus",
		],
		order_by="due_date",
	)

	summary = {
		"total_fees": 0.0,
		"total_scholarship": 0.0,
		"total_penalty": 0.0,
		"total_paid": 0.0,
		"total_outstanding": 0.0,
		"fees_list": fees_list,
	}

	for fee in fees_list:
		summary["total_fees"] += fee.grand_total or 0.0
		summary["total_scholarship"] += fee.custom_scholarship_amount or 0.0
		summary["total_penalty"] += fee.custom_penalty_amount or 0.0
		summary["total_outstanding"] += fee.outstanding_amount or 0.0

	summary["total_paid"] = summary["total_fees"] - summary["total_outstanding"]

	return summary

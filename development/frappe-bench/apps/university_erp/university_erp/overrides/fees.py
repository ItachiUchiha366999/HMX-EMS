import frappe
from frappe import _
from frappe.utils import getdate, date_diff, flt
from education.education.doctype.fees.fees import Fees


class UniversityFees(Fees):
    """
    University-specific Fees class extending Frappe Education's Fees.

    Features:
    - Penalty calculation for late payment
    - Scholarship amount application
    - Net amount calculation (Grand Total - Scholarship + Penalty)
    - Fee category management
    - Due date tracking
    """

    def validate(self):
        """Called before saving the document"""
        super().validate()
        self.calculate_penalty()
        self.calculate_net_amount()

    def before_submit(self):
        """Called before submitting the fees"""
        super().before_submit()
        self.validate_payment()

    def calculate_penalty(self):
        """
        Calculate late fee penalty if payment is overdue

        Penalty = Grand Total × (Penalty Percentage / 100) × Number of Periods
        where Period = Penalty Period Days (e.g., 7 days)
        """
        if not self.custom_penalty_applicable:
            self.custom_penalty_amount = 0.0
            return

        if not self.custom_due_date:
            self.custom_penalty_amount = 0.0
            return

        # Don't calculate penalty if already paid
        if self.docstatus == 1 and self.outstanding_amount == 0:
            return

        today = getdate()
        due_date = getdate(self.custom_due_date)

        if today <= due_date:
            self.custom_penalty_amount = 0.0
            return

        # Calculate days overdue
        days_overdue = date_diff(today, due_date)

        if days_overdue <= 0:
            self.custom_penalty_amount = 0.0
            return

        # Calculate number of penalty periods
        penalty_period = self.custom_penalty_period_days or 7  # Default 7 days
        penalty_percentage = self.custom_penalty_percentage or 0.0

        num_periods = (days_overdue // penalty_period) + 1

        # Calculate penalty
        grand_total = self.grand_total or 0.0
        penalty = grand_total * (penalty_percentage / 100) * num_periods

        self.custom_penalty_amount = flt(penalty, 2)

        # Alert user about penalty
        if penalty > 0:
            frappe.msgprint(
                _("Late fee penalty of {0} applied ({1} days overdue)").format(
                    frappe.utils.fmt_money(penalty, currency=self.currency),
                    days_overdue
                ),
                alert=True,
                indicator="orange"
            )

    def calculate_net_amount(self):
        """
        Calculate net payable amount:
        Net Amount = Grand Total - Scholarship + Penalty
        """
        grand_total = self.grand_total or 0.0
        scholarship = self.custom_scholarship_amount or 0.0
        penalty = self.custom_penalty_amount or 0.0

        self.custom_net_amount = flt(grand_total - scholarship + penalty, 2)

        # Update outstanding amount to reflect net amount
        if self.docstatus == 0:  # Draft
            self.outstanding_amount = self.custom_net_amount

    def validate_payment(self):
        """Validate payment before submission"""
        # Check if net amount is paid
        if self.outstanding_amount > 0:
            frappe.msgprint(
                _("Outstanding amount: {0}. Ensure payment is received before submitting.").format(
                    frappe.utils.fmt_money(self.outstanding_amount, currency=self.currency)
                ),
                alert=True,
                indicator="orange"
            )


def calculate_late_fees():
    """
    Scheduled task to calculate late fees for all pending fees
    Called daily via hooks.py
    """
    # Get all unpaid fees past due date
    overdue_fees = frappe.get_all(
        "Fees",
        filters={
            "docstatus": 1,  # Submitted
            "outstanding_amount": (">", 0),  # Not fully paid
            "custom_due_date": ("<", getdate()),  # Past due
            "custom_penalty_applicable": 1
        },
        fields=["name"]
    )

    for fee in overdue_fees:
        try:
            fee_doc = frappe.get_doc("Fees", fee.name)
            old_penalty = fee_doc.custom_penalty_amount or 0.0

            # Recalculate penalty
            fee_doc.calculate_penalty()
            fee_doc.calculate_net_amount()

            if fee_doc.custom_penalty_amount != old_penalty:
                fee_doc.save(ignore_permissions=True)

                frappe.logger().info(
                    f"Updated penalty for {fee_doc.name}: {old_penalty} → {fee_doc.custom_penalty_amount}"
                )

        except Exception as e:
            frappe.logger().error(f"Error calculating late fee for {fee.name}: {str(e)}")
            continue


def apply_scholarship(student, scholarship_amount, fee_category=None):
    """
    Apply scholarship to student's fees

    Args:
        student: Student ID
        scholarship_amount: Total scholarship amount
        fee_category: Specific fee category (optional)
    """
    filters = {
        "student": student,
        "docstatus": 0,  # Draft fees
    }

    if fee_category:
        filters["custom_fee_category"] = fee_category

    fees_list = frappe.get_all(
        "Fees",
        filters=filters,
        fields=["name", "grand_total"],
        order_by="due_date"
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

    return scholarship_amount - remaining_scholarship  # Amount applied


def get_fee_summary(student, academic_year=None):
    """Get fee summary for a student"""
    filters = {"student": student}

    if academic_year:
        filters["academic_year"] = academic_year

    fees_list = frappe.get_all(
        "Fees",
        filters=filters,
        fields=[
            "name", "custom_fee_category", "due_date", "grand_total",
            "custom_scholarship_amount", "custom_penalty_amount",
            "custom_net_amount", "outstanding_amount", "docstatus"
        ],
        order_by="due_date"
    )

    summary = {
        "total_fees": 0.0,
        "total_scholarship": 0.0,
        "total_penalty": 0.0,
        "total_paid": 0.0,
        "total_outstanding": 0.0,
        "fees_list": fees_list
    }

    for fee in fees_list:
        summary["total_fees"] += fee.grand_total or 0.0
        summary["total_scholarship"] += fee.custom_scholarship_amount or 0.0
        summary["total_penalty"] += fee.custom_penalty_amount or 0.0
        summary["total_outstanding"] += fee.outstanding_amount or 0.0

    summary["total_paid"] = summary["total_fees"] - summary["total_outstanding"]

    return summary

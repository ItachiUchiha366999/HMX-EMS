# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class FeeRefund(Document):
    def validate(self):
        self.validate_refund_amount()
        self.calculate_net_refund()

    def validate_refund_amount(self):
        """Validate refund amount against paid amount"""
        fees = frappe.get_doc("Fees", self.fees)

        if flt(self.refund_amount) > flt(fees.paid_amount):
            frappe.throw(_("Refund amount cannot exceed paid amount of {0}").format(
                frappe.format_value(fees.paid_amount, {"fieldtype": "Currency"})
            ))

        if flt(self.refund_amount) <= 0:
            frappe.throw(_("Refund amount must be greater than zero"))

        # Check for existing refunds
        existing_refunds = frappe.db.sql("""
            SELECT SUM(net_refund) as total_refunded
            FROM `tabFee Refund`
            WHERE fees = %s AND docstatus = 1 AND name != %s
        """, (self.fees, self.name), as_dict=True)

        total_refunded = flt(existing_refunds[0].total_refunded) if existing_refunds else 0

        if (total_refunded + flt(self.refund_amount)) > flt(fees.paid_amount):
            frappe.throw(_(
                "Total refund amount ({0}) cannot exceed paid amount ({1}). Already refunded: {2}"
            ).format(
                frappe.format_value(total_refunded + flt(self.refund_amount), {"fieldtype": "Currency"}),
                frappe.format_value(fees.paid_amount, {"fieldtype": "Currency"}),
                frappe.format_value(total_refunded, {"fieldtype": "Currency"})
            ))

    def calculate_net_refund(self):
        """Calculate net refund after deductions"""
        self.net_refund = flt(self.refund_amount) - flt(self.deduction_amount)
        if self.net_refund < 0:
            frappe.throw(_("Net refund cannot be negative"))

    def before_submit(self):
        """Validate before submission"""
        if self.status not in ["Approved", "Processed"]:
            frappe.throw(_("Only Approved refunds can be submitted"))

    def on_submit(self):
        """Create payment entry on submit"""
        if self.status == "Approved":
            self.create_payment_entry()
            self.update_fees_status()

    def on_cancel(self):
        """Handle cancellation"""
        if self.payment_entry:
            pe = frappe.get_doc("Payment Entry", self.payment_entry)
            if pe.docstatus == 1:
                pe.cancel()

    def create_payment_entry(self):
        """Create payment entry for refund"""
        settings = frappe.get_single("University Accounts Settings")

        if not settings.fee_collection_account:
            frappe.throw(_("Fee Collection Account not configured in University Accounts Settings"))

        company = settings.company
        if not company:
            frappe.throw(_("Company not configured in University Accounts Settings"))

        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "posting_date": self.refund_date,
            "company": company,
            "party_type": "Student",
            "party": self.student,
            "party_name": self.student_name,
            "paid_amount": self.net_refund,
            "received_amount": self.net_refund,
            "target_exchange_rate": 1,
            "paid_from": settings.fee_collection_account,
            "mode_of_payment": self.get_mode_of_payment(),
            "reference_no": self.name,
            "reference_date": self.refund_date,
            "remarks": f"Fee refund - {self.refund_reason} - {self.fees}"
        })

        # Add bank details if bank transfer
        if self.payment_mode == "Bank Transfer" and self.bank_account:
            payment_entry.remarks += f"\nBank: {self.bank_name}, A/C: {self.bank_account}, IFSC: {self.ifsc_code}"

        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()

        self.db_set("payment_entry", payment_entry.name)
        self.db_set("status", "Processed")
        self.db_set("processed_date", frappe.utils.today())

    def get_mode_of_payment(self):
        """Get mode of payment for payment entry"""
        mode_mapping = {
            "Bank Transfer": "Bank Draft",
            "Cheque": "Cheque",
            "Cash": "Cash",
            "Online Refund": "Online",
            "UPI": "UPI"
        }
        return mode_mapping.get(self.payment_mode, "Cash")

    def update_fees_status(self):
        """Update original fees status if fully refunded"""
        fees = frappe.get_doc("Fees", self.fees)

        total_refunded = frappe.db.sql("""
            SELECT SUM(net_refund) as total
            FROM `tabFee Refund`
            WHERE fees = %s AND docstatus = 1
        """, self.fees, as_dict=True)[0].total or 0

        if flt(total_refunded) >= flt(fees.paid_amount):
            fees.db_set("status", "Refunded")


@frappe.whitelist()
def submit_for_approval(refund_name):
    """Submit refund for approval"""
    refund = frappe.get_doc("Fee Refund", refund_name)

    if refund.status != "Draft":
        frappe.throw(_("Only Draft refunds can be submitted for approval"))

    refund.status = "Pending Approval"
    refund.save()

    return {"success": True, "message": _("Refund submitted for approval")}


@frappe.whitelist()
def approve_refund(refund_name, remarks=None):
    """Approve a refund request"""
    refund = frappe.get_doc("Fee Refund", refund_name)

    if refund.status != "Pending Approval":
        frappe.throw(_("Only pending refunds can be approved"))

    refund.status = "Approved"
    refund.approved_by = frappe.session.user
    refund.approved_date = frappe.utils.today()
    if remarks:
        refund.approval_remarks = remarks
    refund.save()

    return {"success": True, "message": _("Refund approved successfully")}


@frappe.whitelist()
def reject_refund(refund_name, remarks=None):
    """Reject a refund request"""
    refund = frappe.get_doc("Fee Refund", refund_name)

    if refund.status not in ["Pending Approval", "Draft"]:
        frappe.throw(_("Only pending or draft refunds can be rejected"))

    refund.status = "Rejected"
    refund.approved_by = frappe.session.user
    refund.approved_date = frappe.utils.today()
    if remarks:
        refund.approval_remarks = remarks
    refund.save()

    return {"success": True, "message": _("Refund rejected")}


@frappe.whitelist()
def get_refund_summary(student=None, from_date=None, to_date=None):
    """Get refund summary"""
    filters = {"docstatus": 1}

    if student:
        filters["student"] = student

    conditions = "WHERE docstatus = 1"
    if student:
        conditions += f" AND student = '{student}'"
    if from_date:
        conditions += f" AND refund_date >= '{from_date}'"
    if to_date:
        conditions += f" AND refund_date <= '{to_date}'"

    summary = frappe.db.sql(f"""
        SELECT
            COUNT(*) as total_refunds,
            SUM(refund_amount) as total_refund_amount,
            SUM(deduction_amount) as total_deductions,
            SUM(net_refund) as total_net_refund
        FROM `tabFee Refund`
        {conditions}
    """, as_dict=True)[0]

    return summary

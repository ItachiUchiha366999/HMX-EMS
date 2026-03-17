# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class PaymentTransaction(Document):
    def validate(self):
        self.validate_amount()
        self.set_student_details()

    def validate_amount(self):
        """Ensure amount is positive"""
        if self.amount and self.amount <= 0:
            frappe.throw(_("Amount must be greater than zero"))

    def set_student_details(self):
        """Fetch student details if not set"""
        if self.student and not self.student_name:
            student = frappe.get_doc("Student", self.student)
            self.student_name = student.student_name
            self.student_email = student.student_email_id

    def on_update(self):
        """Handle status changes"""
        if self.has_value_changed("status"):
            if self.status == "Success":
                self.on_payment_success()
            elif self.status == "Failed":
                self.on_payment_failed()
            elif self.status in ["Refunded", "Partially Refunded"]:
                self.on_payment_refunded()

    def on_payment_success(self):
        """Handle successful payment"""
        # Update reference document if it's a Fee
        if self.reference_doctype == "Fees" and self.reference_name:
            self.update_fee_payment()

        # Send confirmation SMS/Email
        self.send_payment_confirmation()

    def update_fee_payment(self):
        """Update fee document after successful payment"""
        try:
            fee = frappe.get_doc("Fees", self.reference_name)

            # Update outstanding amount
            fee.outstanding_amount = max(0, fee.outstanding_amount - self.amount)

            # If fully paid, submit the fee
            if fee.outstanding_amount <= 0 and fee.docstatus == 0:
                fee.docstatus = 1

            fee.flags.ignore_permissions = True
            fee.save()

            frappe.msgprint(
                _("Fee {0} updated. Outstanding: {1}").format(
                    self.reference_name, fee.outstanding_amount
                ),
                indicator="green"
            )
        except Exception as e:
            frappe.log_error(f"Failed to update fee: {str(e)}", "Payment Transaction")

    def send_payment_confirmation(self):
        """Send payment confirmation notification"""
        try:
            # This will integrate with SMS gateway
            from university_erp.university_integrations.sms_gateway import send_templated_sms

            if self.student:
                student = frappe.get_doc("Student", self.student)
                if student.student_mobile_number:
                    send_templated_sms(
                        "Fee Payment Confirmation",
                        student.student_mobile_number,
                        {
                            "student_name": student.student_name,
                            "amount": self.amount,
                            "transaction_id": self.name
                        }
                    )
        except Exception:
            # SMS sending is not critical, just log
            pass

    def on_payment_failed(self):
        """Handle failed payment"""
        frappe.log_error(
            f"Payment failed for {self.student}: {self.error_message}",
            "Payment Transaction"
        )

    def on_payment_refunded(self):
        """Handle refunded payment"""
        # Reverse fee payment if applicable
        if self.reference_doctype == "Fees" and self.reference_name:
            try:
                fee = frappe.get_doc("Fees", self.reference_name)
                refund_amount = self.refund_amount or self.amount
                fee.outstanding_amount += refund_amount
                fee.flags.ignore_permissions = True
                fee.save()
            except Exception as e:
                frappe.log_error(f"Failed to reverse fee payment: {str(e)}", "Payment Transaction")


@frappe.whitelist()
def get_transaction_status(transaction_name):
    """Get current status of a payment transaction"""
    return frappe.db.get_value(
        "Payment Transaction",
        transaction_name,
        ["status", "gateway_payment_id", "error_message"],
        as_dict=True
    )


@frappe.whitelist()
def get_student_transactions(student, limit=10):
    """Get recent transactions for a student"""
    return frappe.get_all(
        "Payment Transaction",
        filters={"student": student},
        fields=[
            "name", "transaction_date", "amount", "status",
            "payment_gateway", "reference_doctype", "reference_name"
        ],
        order_by="transaction_date desc",
        limit=limit
    )

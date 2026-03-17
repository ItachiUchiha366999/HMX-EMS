# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PaymentOrder(Document):
    def before_insert(self):
        self.creation_date = frappe.utils.now_datetime()

    def validate(self):
        self.validate_amount()

    def validate_amount(self):
        """Validate payment amount"""
        if self.amount <= 0:
            frappe.throw(_("Payment amount must be greater than zero"))

    def on_update(self):
        """Update linked document status on payment completion"""
        if self.status == "Completed" and self.reference_doctype and self.reference_name:
            self.update_reference_document()

    def update_reference_document(self):
        """Update the reference document (e.g., Fees) after successful payment"""
        if self.reference_doctype == "Fees":
            # Fees document will be updated through payment entry
            pass

    def mark_as_completed(self, payment_id, payment_date=None):
        """Mark payment order as completed"""
        self.gateway_payment_id = payment_id
        self.status = "Completed"
        self.payment_date = payment_date or frappe.utils.now_datetime()
        self.save(ignore_permissions=True)

    def mark_as_failed(self, reason):
        """Mark payment order as failed"""
        self.status = "Failed"
        self.failure_reason = reason
        self.retry_count = (self.retry_count or 0) + 1
        self.save(ignore_permissions=True)

    def mark_as_refunded(self, refund_id, refund_amount, reason=None):
        """Mark payment order as refunded"""
        self.status = "Refunded"
        self.refund_id = refund_id
        self.refund_amount = refund_amount
        self.refund_date = frappe.utils.now_datetime()
        self.refund_reason = reason
        self.save(ignore_permissions=True)

    def get_payment_status_from_gateway(self):
        """Fetch payment status from gateway"""
        if self.payment_gateway == "Razorpay":
            return self._get_razorpay_status()
        elif self.payment_gateway == "PayU":
            return self._get_payu_status()
        return None

    def _get_razorpay_status(self):
        """Get payment status from Razorpay"""
        if not self.gateway_order_id:
            return None

        try:
            from university_erp.university_payments.doctype.razorpay_settings.razorpay_settings import get_razorpay_client
            client = get_razorpay_client()
            order = client.order.fetch(self.gateway_order_id)
            return order.get("status")
        except Exception as e:
            frappe.log_error(f"Error fetching Razorpay status: {str(e)}", "Payment Gateway")
            return None

    def _get_payu_status(self):
        """Get payment status from PayU"""
        # PayU status check requires API call with transaction ID
        # Implementation depends on PayU API availability
        return None


@frappe.whitelist()
def get_payment_order_status(payment_order_name):
    """Get payment order status"""
    payment_order = frappe.get_doc("Payment Order", payment_order_name)
    return {
        "status": payment_order.status,
        "payment_id": payment_order.gateway_payment_id,
        "payment_date": payment_order.payment_date,
        "payment_entry": payment_order.payment_entry
    }


@frappe.whitelist()
def cancel_payment_order(payment_order_name, reason=None):
    """Cancel a payment order"""
    payment_order = frappe.get_doc("Payment Order", payment_order_name)

    if payment_order.status not in ["Created", "Pending"]:
        frappe.throw(_("Only Created or Pending payment orders can be cancelled"))

    payment_order.status = "Cancelled"
    payment_order.failure_reason = reason or "Cancelled by user"
    payment_order.save()

    return {"success": True, "message": "Payment order cancelled"}

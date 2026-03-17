# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class BankTransaction(Document):
    def validate(self):
        self.validate_amounts()

    def validate_amounts(self):
        """Validate deposit and withdrawal amounts"""
        if not self.deposit and not self.withdrawal:
            frappe.throw(_("Either Deposit or Withdrawal amount is required"))

        if self.deposit and self.withdrawal:
            frappe.throw(_("Transaction cannot have both deposit and withdrawal"))

    def reconcile_with_payment_entry(self, payment_entry_name, matched_by="Manual"):
        """Reconcile this transaction with a payment entry"""
        self.payment_entry = payment_entry_name
        self.status = "Reconciled"
        self.matched_by = matched_by
        self.save()

        # Update payment entry clearance date
        frappe.db.set_value("Payment Entry", payment_entry_name,
                          "clearance_date", self.date)

    def unreconcile(self):
        """Remove reconciliation"""
        if self.payment_entry:
            frappe.db.set_value("Payment Entry", self.payment_entry,
                              "clearance_date", None)

        self.payment_entry = None
        self.payment_order = None
        self.status = "Pending"
        self.matched_by = None
        self.save()

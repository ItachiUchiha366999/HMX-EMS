# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class LibraryFine(Document):
    """Library Fine with fee integration"""

    def on_update(self):
        """Update member fine totals"""
        self.update_member_fines()

    def update_member_fines(self):
        """Update member's fine totals"""
        member = frappe.get_doc("Library Member", self.member)
        member.update_borrowing_status()
        member.save(ignore_permissions=True)


@frappe.whitelist()
def pay_fine(fine_name, create_fee=False):
    """Mark fine as paid"""
    fine = frappe.get_doc("Library Fine", fine_name)

    if fine.status == "Paid":
        frappe.throw(_("Fine is already paid"))

    fine.status = "Paid"
    fine.paid_date = nowdate()

    if create_fee:
        # Create fee entry for the fine
        member = frappe.get_doc("Library Member", fine.member)
        if member.student:
            fee = frappe.get_doc({
                "doctype": "Fees",
                "student": member.student,
                "posting_date": nowdate(),
                "due_date": nowdate(),
                "custom_fee_type": "Library Fine",
                "components": [{
                    "fees_category": "Library Fine",
                    "description": f"Library fine for {fine.article or 'overdue'}",
                    "amount": fine.fine_amount
                }]
            })
            fee.insert(ignore_permissions=True)
            fine.fee_reference = fee.name

    fine.save()

    return {"message": _("Fine marked as paid")}


@frappe.whitelist()
def waive_fine(fine_name, reason=None):
    """Waive a fine"""
    fine = frappe.get_doc("Library Fine", fine_name)

    if fine.status == "Paid":
        frappe.throw(_("Cannot waive a paid fine"))

    fine.status = "Waived"
    if reason:
        fine.reason = f"{fine.reason or ''}\nWaived: {reason}"

    fine.save()

    return {"message": _("Fine waived successfully")}

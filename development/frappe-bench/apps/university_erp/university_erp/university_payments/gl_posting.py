# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
GL Posting Manager
Handles automated GL entries for university financial transactions
"""

import frappe
from frappe import _
from frappe.utils import flt


class GLPostingManager:
    """Manages automated GL postings for university transactions"""

    def __init__(self):
        self.settings = frappe.get_single("University Accounts Settings")

    def post_fee_collection(self, fees):
        """Create GL entries for fee collection"""
        if not self.settings.auto_post_gl:
            return

        if not self.settings.fee_collection_account or not self.settings.fee_income_account:
            frappe.log_error(
                "Fee collection or income account not configured in University Accounts Settings",
                "GL Posting Error"
            )
            return

        entries = []

        # Debit: Bank/Cash/Payment Gateway Account
        entries.append({
            "account": self.settings.fee_collection_account,
            "debit": flt(fees.paid_amount),
            "credit": 0,
            "party_type": "Student",
            "party": fees.student,
            "against": self.settings.fee_income_account,
            "remarks": f"Fee collection - {fees.name}"
        })

        # Credit: Fee Income Account (per component if configured)
        if hasattr(fees, 'components') and fees.components:
            for component in fees.components:
                income_account = self.get_fee_component_account(component.fees_category)
                cost_center = self.get_fee_component_cost_center(component.fees_category, fees)

                entries.append({
                    "account": income_account,
                    "debit": 0,
                    "credit": flt(component.amount),
                    "party_type": "Student",
                    "party": fees.student,
                    "against": self.settings.fee_collection_account,
                    "remarks": f"{component.fees_category} - {fees.name}",
                    "cost_center": cost_center
                })
        else:
            # Single entry for total amount
            entries.append({
                "account": self.settings.fee_income_account,
                "debit": 0,
                "credit": flt(fees.paid_amount),
                "party_type": "Student",
                "party": fees.student,
                "against": self.settings.fee_collection_account,
                "remarks": f"Fee income - {fees.name}",
                "cost_center": self.get_department_cost_center(fees)
            })

        self.create_gl_entries(entries, fees)

    def post_scholarship_disbursement(self, scholarship):
        """Create GL entries for scholarship disbursement"""
        if not self.settings.auto_post_gl:
            return

        if not self.settings.scholarship_expense_account or not self.settings.scholarship_liability_account:
            return

        entries = []

        # Debit: Scholarship Expense Account
        entries.append({
            "account": self.settings.scholarship_expense_account,
            "debit": flt(scholarship.amount),
            "credit": 0,
            "party_type": "Student",
            "party": scholarship.student,
            "against": self.settings.scholarship_liability_account,
            "remarks": f"Scholarship - {scholarship.name}"
        })

        # Credit: Scholarship Liability Account (or Fee Receivable)
        entries.append({
            "account": self.settings.scholarship_liability_account,
            "debit": 0,
            "credit": flt(scholarship.amount),
            "party_type": "Student",
            "party": scholarship.student,
            "against": self.settings.scholarship_expense_account,
            "remarks": f"Scholarship adjustment - {scholarship.name}"
        })

        self.create_gl_entries(entries, scholarship)

    def post_hostel_fee(self, hostel_fee):
        """Create GL entries for hostel fee"""
        if not self.settings.auto_post_gl:
            return

        if not self.settings.hostel_receivable_account or not self.settings.hostel_income_account:
            return

        entries = []
        total_amount = flt(hostel_fee.total_amount) if hasattr(hostel_fee, 'total_amount') else 0

        # Debit: Hostel Receivable
        entries.append({
            "account": self.settings.hostel_receivable_account,
            "debit": total_amount,
            "credit": 0,
            "party_type": "Student",
            "party": hostel_fee.student,
            "remarks": f"Hostel fee - {hostel_fee.name}"
        })

        # Credit: Room Rent Income
        room_rent = flt(hostel_fee.room_rent) if hasattr(hostel_fee, 'room_rent') else total_amount
        entries.append({
            "account": self.settings.hostel_income_account,
            "debit": 0,
            "credit": room_rent,
            "remarks": f"Room rent - {hostel_fee.name}"
        })

        # Credit: Mess Charges (if applicable)
        mess_charges = flt(hostel_fee.mess_charges) if hasattr(hostel_fee, 'mess_charges') else 0
        if mess_charges and self.settings.mess_income_account:
            entries.append({
                "account": self.settings.mess_income_account,
                "debit": 0,
                "credit": mess_charges,
                "remarks": f"Mess charges - {hostel_fee.name}"
            })

        self.create_gl_entries(entries, hostel_fee)

    def post_transport_fee(self, transport_fee):
        """Create GL entries for transport fee"""
        if not self.settings.auto_post_gl:
            return

        if not self.settings.transport_receivable_account or not self.settings.transport_income_account:
            return

        entries = []
        amount = flt(transport_fee.amount) if hasattr(transport_fee, 'amount') else 0

        # Debit: Transport Receivable
        entries.append({
            "account": self.settings.transport_receivable_account,
            "debit": amount,
            "credit": 0,
            "party_type": "Student",
            "party": transport_fee.student,
            "remarks": f"Transport fee - {transport_fee.name}"
        })

        # Credit: Transport Income
        entries.append({
            "account": self.settings.transport_income_account,
            "debit": 0,
            "credit": amount,
            "remarks": f"Transport income - {transport_fee.name}"
        })

        self.create_gl_entries(entries, transport_fee)

    def post_library_fine(self, library_fine):
        """Create GL entries for library fine"""
        if not self.settings.auto_post_gl:
            return

        if not self.settings.fee_collection_account or not self.settings.library_fine_income_account:
            return

        entries = []
        amount = flt(library_fine.amount) if hasattr(library_fine, 'amount') else 0

        # Debit: Cash/Bank
        entries.append({
            "account": self.settings.fee_collection_account,
            "debit": amount,
            "credit": 0,
            "party_type": "Student",
            "party": library_fine.student if hasattr(library_fine, 'student') else None,
            "remarks": f"Library fine - {library_fine.name}"
        })

        # Credit: Library Fine Income
        entries.append({
            "account": self.settings.library_fine_income_account,
            "debit": 0,
            "credit": amount,
            "remarks": f"Library fine income - {library_fine.name}"
        })

        self.create_gl_entries(entries, library_fine)

    def get_fee_component_account(self, fees_category):
        """Get GL account for fee category"""
        account = self.settings.get_fee_category_account(fees_category)
        return account or self.settings.fee_income_account

    def get_fee_component_cost_center(self, fees_category, fees):
        """Get cost center for fee category"""
        cost_center = self.settings.get_fee_category_cost_center(fees_category)
        if cost_center:
            return cost_center
        return self.get_department_cost_center(fees)

    def get_department_cost_center(self, doc):
        """Get cost center for program/department"""
        if hasattr(doc, 'program') and doc.program:
            department = frappe.db.get_value("Program", doc.program, "department")
            if department:
                cost_center = frappe.db.get_value("Department", department, "cost_center")
                if cost_center:
                    return cost_center
        return self.settings.default_cost_center

    def create_gl_entries(self, entries, voucher):
        """Create GL entries from list"""
        if not entries:
            return

        try:
            from erpnext.accounts.general_ledger import make_gl_entries

            gl_entries = []
            posting_date = voucher.posting_date if hasattr(voucher, 'posting_date') else frappe.utils.today()

            for entry in entries:
                gl_entry = frappe._dict({
                    "posting_date": posting_date,
                    "account": entry["account"],
                    "debit": entry.get("debit", 0),
                    "credit": entry.get("credit", 0),
                    "debit_in_account_currency": entry.get("debit", 0),
                    "credit_in_account_currency": entry.get("credit", 0),
                    "party_type": entry.get("party_type"),
                    "party": entry.get("party"),
                    "against": entry.get("against"),
                    "remarks": entry.get("remarks"),
                    "cost_center": entry.get("cost_center") or self.settings.default_cost_center,
                    "voucher_type": voucher.doctype,
                    "voucher_no": voucher.name,
                    "company": self.settings.company
                })
                gl_entries.append(gl_entry)

            if gl_entries:
                make_gl_entries(gl_entries, cancel=False)

        except ImportError:
            # ERPNext not installed, skip GL posting
            frappe.log_error(
                "ERPNext not installed. GL entries cannot be created.",
                "GL Posting Warning"
            )
        except Exception as e:
            frappe.log_error(
                f"Error creating GL entries for {voucher.doctype} {voucher.name}: {str(e)}",
                "GL Posting Error"
            )


def on_fees_submit(doc, method):
    """Auto post GL entries on fee submission"""
    try:
        gl_manager = GLPostingManager()
        gl_manager.post_fee_collection(doc)
    except Exception as e:
        frappe.log_error(f"Error in fee GL posting: {str(e)}", "GL Posting Error")


def on_fees_cancel(doc, method):
    """Reverse GL entries on fee cancellation"""
    # GL entries are automatically reversed by ERPNext when document is cancelled
    pass


def on_scholarship_submit(doc, method):
    """Auto post GL entries on scholarship submission"""
    try:
        gl_manager = GLPostingManager()
        gl_manager.post_scholarship_disbursement(doc)
    except Exception as e:
        frappe.log_error(f"Error in scholarship GL posting: {str(e)}", "GL Posting Error")


def on_hostel_fee_submit(doc, method):
    """Auto post GL entries on hostel fee submission"""
    try:
        gl_manager = GLPostingManager()
        gl_manager.post_hostel_fee(doc)
    except Exception as e:
        frappe.log_error(f"Error in hostel fee GL posting: {str(e)}", "GL Posting Error")


def on_transport_fee_submit(doc, method):
    """Auto post GL entries on transport fee submission"""
    try:
        gl_manager = GLPostingManager()
        gl_manager.post_transport_fee(doc)
    except Exception as e:
        frappe.log_error(f"Error in transport fee GL posting: {str(e)}", "GL Posting Error")

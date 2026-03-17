# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class UniversityAccountsSettings(Document):
    def validate(self):
        self.validate_accounts()

    def validate_accounts(self):
        """Validate account selections"""
        if self.company:
            # Validate all account fields belong to the selected company
            account_fields = [
                'fee_collection_account', 'fee_income_account', 'fee_receivable_account',
                'late_fee_income_account', 'fee_discount_account',
                'scholarship_expense_account', 'scholarship_liability_account',
                'hostel_receivable_account', 'hostel_income_account', 'mess_income_account',
                'hostel_deposit_account', 'transport_income_account', 'transport_receivable_account',
                'library_fine_income_account', 'library_deposit_account'
            ]

            for field in account_fields:
                account = getattr(self, field, None)
                if account:
                    account_company = frappe.db.get_value("Account", account, "company")
                    if account_company and account_company != self.company:
                        frappe.throw(
                            _("{0} does not belong to company {1}").format(
                                frappe.bold(account),
                                frappe.bold(self.company)
                            )
                        )

    def get_fee_category_account(self, fees_category):
        """Get income account for a specific fee category"""
        for row in self.fee_category_accounts:
            if row.fees_category == fees_category:
                return row.income_account
        return self.fee_income_account

    def get_fee_category_cost_center(self, fees_category):
        """Get cost center for a specific fee category"""
        for row in self.fee_category_accounts:
            if row.fees_category == fees_category and row.cost_center:
                return row.cost_center
        return self.default_cost_center


def get_university_accounts_settings():
    """Get University Accounts Settings singleton"""
    return frappe.get_single("University Accounts Settings")

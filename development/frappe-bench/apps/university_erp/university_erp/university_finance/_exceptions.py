"""
Forked ERPNext exception classes for University Finance module.

These were originally in erpnext/exceptions.py. All classes inherit from
frappe.ValidationError so they integrate with Frappe's error handling.
"""

import frappe


# accounts
class PartyFrozen(frappe.ValidationError):
	pass


class InvalidAccountCurrency(frappe.ValidationError):
	pass


class InvalidCurrency(frappe.ValidationError):
	pass


class PartyDisabled(frappe.ValidationError):
	pass


class InvalidAccountDimensionError(frappe.ValidationError):
	pass


class MandatoryAccountDimensionError(frappe.ValidationError):
	pass

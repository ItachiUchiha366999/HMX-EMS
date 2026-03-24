"""
ERPNext Compatibility Shim for University Finance Module.

Provides the utility functions that were originally in erpnext/__init__.py,
allowing forked accounts code to run independently of the erpnext package.

Stock/warehouse functions are stubbed since the university does not use
perpetual inventory or stock valuation.
"""

import functools
from contextlib import contextmanager

import frappe

__version__ = "0.1.0"


def get_default_company(user=None):
	"""Get default company for user."""
	from frappe.defaults import get_user_default_as_list

	if not user:
		user = frappe.session.user

	companies = get_user_default_as_list("company", user)
	if companies:
		default_company = companies[0]
	else:
		default_company = frappe.db.get_single_value("Global Defaults", "default_company")

	return default_company


def get_default_currency():
	"""Returns the currency of the default company."""
	company = get_default_company()
	if company:
		return frappe.get_cached_value("Company", company, "default_currency")


def get_default_cost_center(company):
	"""Returns the default cost center of the company."""
	if not company:
		return None

	if not frappe.flags.company_cost_center:
		frappe.flags.company_cost_center = {}
	if company not in frappe.flags.company_cost_center:
		frappe.flags.company_cost_center[company] = frappe.get_cached_value(
			"Company", company, "cost_center"
		)
	return frappe.flags.company_cost_center[company]


def get_company_currency(company):
	"""Returns the default company currency."""
	if not frappe.flags.company_currency:
		frappe.flags.company_currency = {}
	if company not in frappe.flags.company_currency:
		frappe.flags.company_currency[company] = frappe.db.get_value(
			"Company", company, "default_currency", cache=True
		)
	return frappe.flags.company_currency[company]


def set_perpetual_inventory(enable=1, company=None):
	"""Stub: University does not use perpetual inventory."""
	pass


def encode_company_abbr(name, company=None, abbr=None):
	"""Returns name encoded with company abbreviation."""
	company_abbr = abbr or frappe.get_cached_value("Company", company, "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != company_abbr.lower():
		parts.append(company_abbr)

	return " - ".join(parts)


def is_perpetual_inventory_enabled(company):
	"""Stub: University does not use perpetual inventory. Always returns False."""
	return False


def get_default_finance_book(company=None):
	"""Get default finance book for company."""
	if not company:
		company = get_default_company()

	if not hasattr(frappe.local, "default_finance_book"):
		frappe.local.default_finance_book = {}

	if company not in frappe.local.default_finance_book:
		frappe.local.default_finance_book[company] = frappe.get_cached_value(
			"Company", company, "default_finance_book"
		)

	return frappe.local.default_finance_book[company]


def get_party_account_type(party_type):
	"""Get account type for a party type."""
	if not hasattr(frappe.local, "party_account_types"):
		frappe.local.party_account_types = {}

	if party_type not in frappe.local.party_account_types:
		frappe.local.party_account_types[party_type] = (
			frappe.db.get_value("Party Type", party_type, "account_type") or ""
		)

	return frappe.local.party_account_types[party_type]


def get_region(company=None):
	"""Return the default country based on flag, company or global settings."""
	if not company:
		company = frappe.local.flags.company

	if company:
		return frappe.get_cached_value("Company", company, "country")

	return frappe.flags.country or frappe.get_system_settings("country")


def allow_regional(fn):
	"""No-op passthrough decorator. University does not use regional overrides."""

	@functools.wraps(fn)
	def caller(*args, **kwargs):
		return fn(*args, **kwargs)

	return caller


def check_app_permission():
	"""Check if user has app permission."""
	from frappe.utils.user import is_website_user

	if frappe.session.user == "Administrator":
		return True

	if is_website_user():
		return False

	return True


# ---------------------------------------------------------------------------
# Stock/Warehouse stubs
# University does not use warehouse accounting or stock valuation.
# These stubs replace imports from erpnext.stock that are referenced
# in utils.py and various doctype controllers.
# ---------------------------------------------------------------------------

def get_warehouse_account_map(company):
	"""Stub: University does not use warehouse accounting."""
	return {}


def get_stock_value_on(warehouses, posting_date, company=None):
	"""Stub: University does not use stock valuation."""
	return 0


# ---------------------------------------------------------------------------
# setup.utils stubs
# The get_exchange_rate function is used by payment_entry, journal_entry,
# bank_reconciliation_tool, and exchange_rate_revaluation.
# ---------------------------------------------------------------------------

def get_exchange_rate(from_currency, to_currency, transaction_date=None, args=None):
	"""Get exchange rate between two currencies.

	Queries Currency Exchange records in the database, falling back to 1.0
	if not found (single-currency university setup).
	"""
	if from_currency == to_currency:
		return 1.0

	if not transaction_date:
		import datetime
		transaction_date = datetime.date.today()

	# Try to get from Currency Exchange doctype
	filters = {
		"from_currency": from_currency,
		"to_currency": to_currency,
	}

	# Get the most recent rate on or before the transaction date
	result = frappe.db.get_value(
		"Currency Exchange",
		filters=filters,
		fieldname="exchange_rate",
		order_by="date desc",
	)

	if result:
		return result

	# Reverse lookup
	filters_reverse = {
		"from_currency": to_currency,
		"to_currency": from_currency,
	}
	result_reverse = frappe.db.get_value(
		"Currency Exchange",
		filters=filters_reverse,
		fieldname="exchange_rate",
		order_by="date desc",
	)

	if result_reverse:
		return 1.0 / result_reverse

	# Default to 1.0 for single-currency university setups
	return 1.0


# ---------------------------------------------------------------------------
# Utility: temporary_flag context manager
# Replaces erpnext.utilities.regional.temporary_flag
# ---------------------------------------------------------------------------

@contextmanager
def temporary_flag(flag_name, value):
	"""Context manager that temporarily sets a flag on frappe.local.flags.

	Used by party.py, accounts_controller.py, and taxes_and_totals.py
	to temporarily set company context for regional operations.
	"""
	old_value = getattr(frappe.local.flags, flag_name, None)
	setattr(frappe.local.flags, flag_name, value)
	try:
		yield
	finally:
		if old_value is None:
			if hasattr(frappe.local.flags, flag_name):
				delattr(frappe.local.flags, flag_name)
		else:
			setattr(frappe.local.flags, flag_name, old_value)

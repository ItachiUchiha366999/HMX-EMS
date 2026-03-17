"""
Bank Reconciliation Page Controller

Provides a UI for reconciling bank statements with system payment entries.
"""
import frappe
from frappe import _


def get_context(context):
    """Get context for bank reconciliation page"""
    context.no_cache = 1

    # Check permissions
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/bank-reconciliation"
        raise frappe.Redirect

    # Check if user has required role
    user_roles = frappe.get_roles()
    allowed_roles = ["System Manager", "Accounts Manager", "Accounts User"]

    if not any(role in user_roles for role in allowed_roles):
        frappe.throw(_("You don't have permission to access this page"), frappe.PermissionError)

    # Get list of bank accounts
    context.bank_accounts = frappe.get_all(
        "Bank Account",
        filters={"is_company_account": 1},
        fields=["name", "account_name", "bank", "account"],
        order_by="account_name"
    )

    return context

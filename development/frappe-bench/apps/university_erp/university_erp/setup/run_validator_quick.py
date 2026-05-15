"""Run just the reports smoke test portion of the validator."""
import frappe


def run():
    frappe.flags.ignore_permissions = True
    from university_erp.setup.seed_validate import validate_all
    validate_all()

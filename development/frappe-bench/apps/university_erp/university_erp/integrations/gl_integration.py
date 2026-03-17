import frappe
from frappe import _


def create_fee_gl_entry(doc, method):
    """
    Create General Ledger entry when Fees are submitted.
    Integrates with ERPNext's accounting module.

    This is a placeholder for Phase 5 (Fees & Finance).
    Will be fully implemented when GL integration is required.

    Args:
        doc: Fees document
        method: Event method (on_submit)
    """
    # Placeholder - will be implemented in Phase 5
    frappe.logger().info(f"GL Entry creation hook called for Fees: {doc.name}")

    # TODO: Phase 5 - Implement GL entry creation
    # 1. Get income account from Fee Category
    # 2. Get receivable account from Student
    # 3. Create Journal Entry with:
    #    - Debit: Student Receivable Account
    #    - Credit: Fee Income Account
    # 4. Handle partial payments
    # 5. Handle scholarship adjustments
    # 6. Handle penalties

    pass


def create_scholarship_gl_entry(student, amount, academic_year):
    """
    Create GL entry for scholarship disbursement.

    Placeholder for Phase 5.

    Args:
        student: Student ID
        amount: Scholarship amount
        academic_year: Academic Year
    """
    # Placeholder
    frappe.logger().info(f"Scholarship GL entry for {student}: {amount}")
    pass


def create_refund_gl_entry(fees_doc, refund_amount):
    """
    Create GL entry for fee refund.

    Placeholder for Phase 5.

    Args:
        fees_doc: Fees document
        refund_amount: Amount to refund
    """
    # Placeholder
    frappe.logger().info(f"Refund GL entry for {fees_doc.name}: {refund_amount}")
    pass

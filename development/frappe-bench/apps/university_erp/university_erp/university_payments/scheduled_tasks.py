# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Scheduled Tasks for University Payments
Runs daily, weekly, and monthly payment-related maintenance tasks.
"""

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate


def auto_reconcile_daily():
    """
    Daily automatic bank reconciliation
    Runs through all company bank accounts and auto-reconciles
    high-confidence matches from the last 7 days.
    """
    frappe.logger("payments").info("Starting daily auto-reconciliation")

    # Get all company bank accounts
    bank_accounts = frappe.get_all(
        "Bank Account",
        filters={"is_company_account": 1},
        pluck="name"
    )

    if not bank_accounts:
        frappe.logger("payments").info("No company bank accounts found for reconciliation")
        return

    from_date = add_days(nowdate(), -7)
    to_date = nowdate()
    min_confidence = 90  # Only auto-reconcile very high confidence matches

    total_reconciled = 0

    for bank_account in bank_accounts:
        try:
            result = auto_reconcile_bank_account(
                bank_account,
                from_date,
                to_date,
                min_confidence
            )
            total_reconciled += result.get("matched", 0)

            if result.get("matched", 0) > 0:
                frappe.logger("payments").info(
                    f"Auto-reconciled {result['matched']} transactions for {bank_account}"
                )
        except Exception as e:
            frappe.log_error(
                f"Error in auto-reconciliation for {bank_account}: {str(e)}",
                "Bank Reconciliation Scheduler"
            )

    frappe.logger("payments").info(
        f"Daily auto-reconciliation completed. Total reconciled: {total_reconciled}"
    )

    return {"total_reconciled": total_reconciled}


def auto_reconcile_bank_account(bank_account, from_date, to_date, min_confidence):
    """Perform auto-reconciliation for a single bank account"""
    from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

    tool = BankReconciliationTool(bank_account, from_date, to_date)
    matches = tool.auto_match()

    reconciled = 0
    for match in matches:
        if match.get("confidence", 0) >= min_confidence:
            try:
                txn = frappe.get_doc("Bank Transaction", match["bank_transaction"])
                txn.reconcile_with_payment_entry(match["payment_entry"], "Auto")
                reconciled += 1
            except Exception as e:
                frappe.log_error(
                    f"Auto-reconcile error for {match['bank_transaction']}: {str(e)}",
                    "Bank Reconciliation"
                )

    if reconciled > 0:
        frappe.db.commit()

    return {"matched": reconciled, "total_suggested": len(matches)}


def check_pending_payments():
    """
    Check for stale pending payments and send alerts
    This can be scheduled weekly to identify stuck payments.
    """
    stale_days = 3
    cutoff_date = add_days(nowdate(), -stale_days)

    # Find pending payment orders older than cutoff
    stale_orders = frappe.get_all(
        "Payment Order",
        filters={
            "status": "Pending",
            "creation": ["<", cutoff_date]
        },
        fields=["name", "student", "student_name", "amount", "creation", "payment_gateway"]
    )

    if stale_orders:
        # Send notification to accounts team
        accounts_users = frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["Accounts Manager", "Accounts User"]]},
            pluck="parent"
        )

        if accounts_users:
            frappe.sendmail(
                recipients=list(set(accounts_users)),
                subject=_("Alert: Stale Pending Payments"),
                message=_(
                    "There are {0} payment orders pending for more than {1} days. "
                    "Please review and take appropriate action."
                ).format(len(stale_orders), stale_days),
                now=True
            )

    return {"stale_orders": len(stale_orders)}


def cleanup_expired_payment_orders():
    """
    Cleanup payment orders that have been pending for too long
    Marks them as expired so students can retry.
    """
    expiry_hours = 24
    from frappe.utils import now_datetime, add_to_date

    cutoff = add_to_date(now_datetime(), hours=-expiry_hours)

    # Find expired pending orders
    expired_orders = frappe.get_all(
        "Payment Order",
        filters={
            "status": "Pending",
            "creation": ["<", cutoff]
        },
        pluck="name"
    )

    expired_count = 0
    for order_name in expired_orders:
        try:
            order = frappe.get_doc("Payment Order", order_name)
            order.status = "Expired"
            order.save(ignore_permissions=True)
            expired_count += 1
        except Exception as e:
            frappe.log_error(
                f"Error expiring payment order {order_name}: {str(e)}",
                "Payment Cleanup"
            )

    if expired_count > 0:
        frappe.db.commit()
        frappe.logger("payments").info(f"Expired {expired_count} stale payment orders")

    return {"expired": expired_count}


def process_webhook_retry():
    """
    Retry processing of failed webhook events
    Some webhook events may fail due to temporary issues.
    """
    # Find failed webhooks from last 24 hours
    from frappe.utils import now_datetime, add_to_date
    cutoff = add_to_date(now_datetime(), hours=-24)

    failed_webhooks = frappe.get_all(
        "Webhook Log",
        filters={
            "status": "Failed",
            "creation": [">", cutoff],
            "retry_count": ["<", 3]  # Max 3 retries
        },
        fields=["name", "payment_gateway", "event_type", "payload"]
    )

    retried = 0
    for webhook in failed_webhooks:
        try:
            if webhook.payment_gateway == "Razorpay":
                from university_erp.university_payments.webhooks.razorpay_webhook import process_webhook_event
                process_webhook_event(webhook.name)
                retried += 1
        except Exception as e:
            frappe.log_error(
                f"Webhook retry failed for {webhook.name}: {str(e)}",
                "Webhook Retry"
            )

    return {"retried": retried}

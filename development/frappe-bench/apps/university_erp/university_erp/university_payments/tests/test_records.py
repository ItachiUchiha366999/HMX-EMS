"""
Test Records for University Payments

Helper functions to create test data for payment-related tests.
"""
import frappe
from frappe.utils import nowdate, add_days, random_string


def create_test_student(student_name=None, email=None):
    """Create a test student for payment tests"""
    if not student_name:
        student_name = f"_Test Student {random_string(5)}"

    if not email:
        email = f"test.{random_string(5)}@university.edu"

    # Check if exists
    existing = frappe.db.get_value("Student", {"student_email_id": email})
    if existing:
        return frappe.get_doc("Student", existing)

    student = frappe.get_doc({
        "doctype": "Student",
        "first_name": "Test",
        "last_name": "Student",
        "student_name": student_name,
        "student_email_id": email,
        "gender": "Male",
        "date_of_birth": "2000-01-01"
    })
    student.insert(ignore_permissions=True)
    return student


def create_test_fee_category(category_name=None):
    """Create a test fee category"""
    if not category_name:
        category_name = f"Test Fee Category {random_string(5)}"

    if frappe.db.exists("Fee Category", category_name):
        return frappe.get_doc("Fee Category", category_name)

    fee_category = frappe.get_doc({
        "doctype": "Fee Category",
        "category_name": category_name,
        "description": "Test fee category for unit tests"
    })
    fee_category.insert(ignore_permissions=True)
    return fee_category


def create_test_fees(student, amount=10000, components=None):
    """Create a test fee document"""
    if not components:
        # Create default fee category
        fee_category = create_test_fee_category("Tuition Fee")
        components = [{
            "fees_category": fee_category.name,
            "amount": amount
        }]

    fees = frappe.get_doc({
        "doctype": "Fees",
        "student": student.name,
        "student_name": student.student_name,
        "due_date": add_days(nowdate(), 30),
        "posting_date": nowdate(),
        "components": components
    })
    fees.insert(ignore_permissions=True)
    fees.submit()
    return fees


def create_test_payment_order(fees, gateway="Razorpay", status="Pending"):
    """Create a test payment order"""
    payment_order = frappe.get_doc({
        "doctype": "Payment Order",
        "reference_doctype": "Fees",
        "reference_name": fees.name,
        "student": fees.student,
        "student_name": fees.student_name,
        "payment_gateway": gateway,
        "gateway_order_id": f"order_{random_string(10)}",
        "amount": fees.outstanding_amount,
        "status": status
    })
    payment_order.insert(ignore_permissions=True)
    return payment_order


def create_completed_payment_order(fees, gateway="Razorpay"):
    """Create a completed payment order with payment entry"""
    payment_order = create_test_payment_order(fees, gateway, status="Pending")

    # Simulate payment completion
    payment_order.gateway_payment_id = f"pay_{random_string(10)}"
    payment_order.status = "Completed"
    payment_order.payment_date = frappe.utils.now_datetime()
    payment_order.save(ignore_permissions=True)

    return payment_order


def create_test_bank_account():
    """Create a test bank account"""
    bank_name = f"Test Bank {random_string(5)}"

    # Create bank if not exists
    if not frappe.db.exists("Bank", bank_name):
        bank = frappe.get_doc({
            "doctype": "Bank",
            "bank_name": bank_name
        })
        bank.insert(ignore_permissions=True)

    # Get company
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        company = frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company", limit=1) else None

    if not company:
        return None

    account_name = f"Test Bank Account - {random_string(5)}"

    if frappe.db.exists("Bank Account", {"account_name": account_name}):
        return frappe.get_doc("Bank Account", {"account_name": account_name})

    # Get a bank GL account or create reference
    bank_gl_account = frappe.db.get_value(
        "Account",
        {"account_type": "Bank", "company": company, "is_group": 0},
        "name"
    )

    bank_account = frappe.get_doc({
        "doctype": "Bank Account",
        "account_name": account_name,
        "bank": bank_name,
        "is_company_account": 1,
        "account": bank_gl_account,
        "company": company
    })
    bank_account.insert(ignore_permissions=True)
    return bank_account


def create_test_bank_transactions(bank_account, count=5):
    """Create test bank transactions for reconciliation"""
    transactions = []

    for i in range(count):
        amount = (i + 1) * 1000

        txn = frappe.get_doc({
            "doctype": "Bank Transaction",
            "bank_account": bank_account.name,
            "date": add_days(nowdate(), -i),
            "description": f"Test transaction {i + 1}",
            "deposit": amount if i % 2 == 0 else 0,
            "withdrawal": amount if i % 2 != 0 else 0,
            "reference_number": f"REF{random_string(8)}",
            "status": "Pending"
        })
        txn.insert(ignore_permissions=True)
        transactions.append(txn)

    return transactions


def create_test_razorpay_settings(enabled=False):
    """Create or get Razorpay settings for tests"""
    settings = frappe.get_single("Razorpay Settings")
    settings.enabled = enabled
    settings.test_mode = 1
    settings.api_key = "rzp_test_dummy_key"
    settings.api_secret = "dummy_secret_for_tests"
    settings.webhook_secret = "dummy_webhook_secret"
    settings.auto_capture = 1
    settings.save(ignore_permissions=True)
    return settings


def create_test_payu_settings(enabled=False):
    """Create or get PayU settings for tests"""
    settings = frappe.get_single("PayU Settings")
    settings.enabled = enabled
    settings.test_mode = 1
    settings.merchant_key = "test_merchant_key"
    settings.merchant_salt = "test_merchant_salt"
    settings.save(ignore_permissions=True)
    return settings


def create_test_university_accounts_settings():
    """Create or get University Accounts Settings for tests"""
    settings = frappe.get_single("University Accounts Settings")

    # Get company
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        companies = frappe.get_all("Company", limit=1)
        company = companies[0].name if companies else None

    if company:
        settings.company = company

        # Try to get accounts
        income_account = frappe.db.get_value(
            "Account",
            {"account_type": "Income Account", "company": company, "is_group": 0},
            "name"
        )
        if income_account:
            settings.fee_income_account = income_account

        receivable_account = frappe.db.get_value(
            "Account",
            {"account_type": "Receivable", "company": company, "is_group": 0},
            "name"
        )
        if receivable_account:
            settings.fee_receivable_account = receivable_account

        settings.auto_post_gl = 1
        settings.save(ignore_permissions=True)

    return settings


def create_test_fee_refund(fees, refund_amount=None):
    """Create a test fee refund"""
    if not refund_amount:
        refund_amount = fees.paid_amount / 2

    refund = frappe.get_doc({
        "doctype": "Fee Refund",
        "student": fees.student,
        "student_name": fees.student_name,
        "fees": fees.name,
        "refund_amount": refund_amount,
        "reason": "Course Withdrawal",
        "refund_mode": "Bank Transfer",
        "status": "Pending"
    })
    refund.insert(ignore_permissions=True)
    return refund


def create_test_webhook_log(gateway="Razorpay", event_type="payment.captured"):
    """Create a test webhook log"""
    import json

    payload = {
        "event": event_type,
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_{random_string(10)}",
                    "order_id": f"order_{random_string(10)}",
                    "amount": 1000000,
                    "status": "captured"
                }
            }
        }
    }

    webhook_log = frappe.get_doc({
        "doctype": "Webhook Log",
        "payment_gateway": gateway,
        "event_type": event_type,
        "event_id": f"evt_{random_string(15)}",
        "payload": json.dumps(payload),
        "status": "Received"
    })
    webhook_log.insert(ignore_permissions=True)
    return webhook_log


def cleanup_test_data():
    """Clean up all test data created during tests"""
    # Delete in order to avoid foreign key issues
    doctypes_to_clean = [
        "Webhook Log",
        "Fee Refund",
        "Payment Order",
        "Bank Transaction",
        "Fees",
        "Student"
    ]

    for doctype in doctypes_to_clean:
        test_records = frappe.get_all(
            doctype,
            filters=[["name", "like", "%_Test%"]],
            pluck="name"
        )
        for record in test_records:
            try:
                frappe.delete_doc(doctype, record, force=True, ignore_permissions=True)
            except Exception:
                pass

    frappe.db.commit()


# Convenience class for test setup/teardown
class PaymentTestSetup:
    """Helper class for setting up payment test data"""

    def __init__(self):
        self.student = None
        self.fees = None
        self.payment_order = None
        self.bank_account = None

    def setup_basic(self):
        """Set up basic test data"""
        self.student = create_test_student()
        self.fees = create_test_fees(self.student)
        return self

    def setup_payment_order(self, gateway="Razorpay"):
        """Set up payment order"""
        if not self.fees:
            self.setup_basic()
        self.payment_order = create_test_payment_order(self.fees, gateway)
        return self

    def setup_bank_reconciliation(self, txn_count=5):
        """Set up bank reconciliation test data"""
        self.bank_account = create_test_bank_account()
        if self.bank_account:
            self.bank_transactions = create_test_bank_transactions(self.bank_account, txn_count)
        return self

    def cleanup(self):
        """Clean up test data"""
        cleanup_test_data()

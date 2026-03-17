# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Unified Payment Gateway Interface
Supports Razorpay, PayU and other payment gateways
"""

import frappe
from frappe import _
import json


class PaymentGateway:
    """Unified payment gateway interface"""

    def __init__(self, gateway="razorpay"):
        self.gateway = gateway.lower()
        self._load_settings()

    def _load_settings(self):
        """Load gateway settings"""
        if self.gateway == "razorpay":
            self.settings = frappe.get_single("Razorpay Settings")
            if not self.settings.enabled:
                frappe.throw(_("Razorpay payment gateway is not enabled"))
            self.client = self.settings.get_client()
        elif self.gateway == "payu":
            self.settings = frappe.get_single("PayU Settings")
            if not self.settings.enabled:
                frappe.throw(_("PayU payment gateway is not enabled"))
        else:
            frappe.throw(_("Unsupported payment gateway: {0}").format(self.gateway))

    def create_order(self, amount, currency="INR", receipt=None, notes=None):
        """Create a payment order"""
        if self.gateway == "razorpay":
            return self._create_razorpay_order(amount, currency, receipt, notes)
        elif self.gateway == "payu":
            return self._create_payu_order(amount, currency, receipt, notes)

    def _create_razorpay_order(self, amount, currency, receipt, notes):
        """Create Razorpay order"""
        order_data = {
            "amount": int(amount * 100),  # Razorpay expects amount in paise
            "currency": currency,
            "receipt": receipt or frappe.generate_hash(length=10),
            "notes": notes or {}
        }

        try:
            order = self.client.order.create(data=order_data)
            return {
                "success": True,
                "order_id": order["id"],
                "amount": amount,
                "currency": currency,
                "key": self.settings.api_key,
                "gateway": "razorpay"
            }
        except Exception as e:
            frappe.log_error(f"Razorpay order creation failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}

    def _create_payu_order(self, amount, currency, receipt, notes):
        """Create PayU order - returns form data for submission"""
        txnid = receipt or f"TXN{frappe.generate_hash(length=10)}"

        params = {
            "key": self.settings.merchant_key,
            "txnid": txnid,
            "amount": str(amount),
            "productinfo": notes.get("productinfo", "Payment") if notes else "Payment",
            "firstname": notes.get("firstname", "") if notes else "",
            "email": notes.get("email", "") if notes else "",
            "phone": notes.get("phone", "") if notes else "",
            "surl": self.settings.success_url,
            "furl": self.settings.failure_url,
            "udf1": notes.get("udf1", "") if notes else "",
            "udf2": notes.get("udf2", "") if notes else "",
            "udf3": notes.get("udf3", "") if notes else "",
            "udf4": notes.get("udf4", "") if notes else "",
            "udf5": notes.get("udf5", "") if notes else ""
        }

        params["hash"] = self.settings.generate_hash(params)

        return {
            "success": True,
            "order_id": txnid,
            "payment_url": self.settings.get_payment_url(),
            "params": params,
            "gateway": "payu"
        }

    def verify_payment(self, payment_data):
        """Verify payment signature"""
        if self.gateway == "razorpay":
            return self._verify_razorpay_payment(payment_data)
        elif self.gateway == "payu":
            return self._verify_payu_payment(payment_data)

    def _verify_razorpay_payment(self, payment_data):
        """Verify Razorpay payment signature"""
        try:
            import razorpay
            params = {
                'razorpay_order_id': payment_data.get('razorpay_order_id'),
                'razorpay_payment_id': payment_data.get('razorpay_payment_id'),
                'razorpay_signature': payment_data.get('razorpay_signature')
            }
            self.client.utility.verify_payment_signature(params)
            return {"verified": True, "payment_id": payment_data.get('razorpay_payment_id')}
        except razorpay.errors.SignatureVerificationError:
            return {"verified": False, "error": "Invalid payment signature"}
        except Exception as e:
            return {"verified": False, "error": str(e)}

    def _verify_payu_payment(self, payment_data):
        """Verify PayU payment response hash"""
        if self.settings.verify_response_hash(payment_data):
            return {
                "verified": True,
                "payment_id": payment_data.get("mihpayid"),
                "status": payment_data.get("status")
            }
        return {"verified": False, "error": "Invalid payment signature"}

    def capture_payment(self, payment_id, amount):
        """Capture an authorized payment (Razorpay only)"""
        if self.gateway == "razorpay":
            try:
                payment = self.client.payment.capture(payment_id, int(amount * 100))
                return {"success": True, "payment": payment}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "Capture not supported for this gateway"}

    def refund_payment(self, payment_id, amount=None, notes=None):
        """Initiate a refund"""
        if self.gateway == "razorpay":
            try:
                refund_data = {"notes": notes or {}}
                if amount:
                    refund_data["amount"] = int(amount * 100)

                refund = self.client.payment.refund(payment_id, refund_data)
                return {"success": True, "refund_id": refund["id"], "refund": refund}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "Refund not supported for this gateway"}

    def get_payment_details(self, payment_id):
        """Get payment details from gateway"""
        if self.gateway == "razorpay":
            try:
                payment = self.client.payment.fetch(payment_id)
                return {"success": True, "payment": payment}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "Not supported for this gateway"}


@frappe.whitelist()
def create_fee_payment_order(fees_name):
    """Create payment order for a fee document"""
    fees = frappe.get_doc("Fees", fees_name)

    if fees.outstanding_amount <= 0:
        frappe.throw(_("No outstanding amount to pay"))

    # Determine which gateway to use
    gateway_setting = frappe.db.get_single_value("University Settings", "default_payment_gateway") or "razorpay"
    gateway = PaymentGateway(gateway_setting)

    # Get student details
    student = frappe.get_doc("Student", fees.student)

    # Create notes for payment
    notes = {
        "fees_name": fees.name,
        "student": fees.student,
        "student_name": fees.student_name,
        "program": fees.program,
        "productinfo": f"Fee Payment - {fees.name}",
        "firstname": student.student_name.split()[0] if student.student_name else "",
        "email": student.student_email_id or "",
        "phone": student.phone or "",
        "udf1": fees.name,
        "udf2": fees.student
    }

    receipt = f"{fees.name}-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
    result = gateway.create_order(
        amount=fees.outstanding_amount,
        currency="INR",
        receipt=receipt,
        notes=notes
    )

    if result.get("success"):
        # Create Payment Order record
        payment_order = frappe.get_doc({
            "doctype": "Payment Order",
            "reference_doctype": "Fees",
            "reference_name": fees.name,
            "payment_gateway": gateway_setting.title(),
            "gateway_order_id": result.get("order_id"),
            "amount": fees.outstanding_amount,
            "currency": "INR",
            "status": "Created",
            "student": fees.student,
            "student_name": fees.student_name
        })
        payment_order.insert(ignore_permissions=True)
        frappe.db.commit()

        result["payment_order"] = payment_order.name
        result["student_name"] = student.student_name
        result["student_email"] = student.student_email_id
        result["description"] = f"Fee Payment - {fees.name}"

    return result


@frappe.whitelist()
def verify_and_process_payment(payment_data):
    """Verify payment and update fee records"""
    payment_data = json.loads(payment_data) if isinstance(payment_data, str) else payment_data

    payment_order = frappe.get_doc("Payment Order", payment_data.get("payment_order"))
    gateway = PaymentGateway(payment_order.payment_gateway.lower())

    # Verify payment
    verification = gateway.verify_payment(payment_data)

    if not verification.get("verified"):
        payment_order.mark_as_failed(verification.get("error"))
        return {"success": False, "error": verification.get("error")}

    # Update payment order
    payment_order.gateway_payment_id = verification.get("payment_id")
    payment_order.status = "Completed"
    payment_order.payment_date = frappe.utils.now_datetime()
    payment_order.save(ignore_permissions=True)

    # Process fee payment
    fees = frappe.get_doc("Fees", payment_order.reference_name)

    # Create Fee Payment Entry
    payment_entry = create_fee_payment_entry(
        fees=fees,
        amount=payment_order.amount,
        payment_id=verification.get("payment_id"),
        payment_gateway=payment_order.payment_gateway
    )

    payment_order.payment_entry = payment_entry.name
    payment_order.save(ignore_permissions=True)

    # Update fees outstanding
    fees.reload()

    # Send receipt email
    settings = frappe.get_single(f"{payment_order.payment_gateway} Settings")
    if hasattr(settings, 'send_receipt') and settings.send_receipt:
        send_payment_receipt(fees, payment_order, payment_entry)

    frappe.db.commit()

    return {
        "success": True,
        "payment_entry": payment_entry.name,
        "new_outstanding": fees.outstanding_amount,
        "message": _("Payment processed successfully")
    }


def create_fee_payment_entry(fees, amount, payment_id, payment_gateway):
    """Create payment entry for fee"""
    settings = frappe.get_single(f"{payment_gateway} Settings")

    # Get company from fees or default
    company = fees.company if hasattr(fees, 'company') and fees.company else frappe.defaults.get_defaults().get("company")

    payment_entry = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "posting_date": frappe.utils.today(),
        "company": company,
        "party_type": "Student",
        "party": fees.student,
        "party_name": fees.student_name,
        "paid_amount": amount,
        "received_amount": amount,
        "target_exchange_rate": 1,
        "paid_to": settings.payment_gateway_account if hasattr(settings, 'payment_gateway_account') and settings.payment_gateway_account else None,
        "mode_of_payment": "Online Payment",
        "reference_no": payment_id,
        "reference_date": frappe.utils.today(),
        "references": [{
            "reference_doctype": "Fees",
            "reference_name": fees.name,
            "allocated_amount": amount
        }],
        "remarks": f"Online payment via {payment_gateway} - {payment_id}"
    })
    payment_entry.insert(ignore_permissions=True)
    payment_entry.submit()

    return payment_entry


def send_payment_receipt(fees, payment_order, payment_entry):
    """Send payment receipt email to student"""
    student = frappe.get_doc("Student", fees.student)

    if not student.student_email_id:
        return

    try:
        # Generate receipt content
        receipt_content = frappe.render_template(
            "university_erp/university_payments/templates/payment_receipt.html",
            {
                "fees": fees,
                "payment_order": payment_order,
                "payment_entry": payment_entry,
                "student": student,
                "company": frappe.defaults.get_defaults().get("company")
            }
        )

        frappe.sendmail(
            recipients=[student.student_email_id],
            subject=f"Payment Receipt - {payment_entry.name}",
            message=receipt_content,
            reference_doctype="Payment Entry",
            reference_name=payment_entry.name
        )
    except Exception as e:
        frappe.log_error(f"Error sending payment receipt: {str(e)}", "Payment Gateway")


@frappe.whitelist()
def get_payment_status(payment_order_name):
    """Get current payment status"""
    payment_order = frappe.get_doc("Payment Order", payment_order_name)
    return {
        "status": payment_order.status,
        "payment_id": payment_order.gateway_payment_id,
        "payment_date": payment_order.payment_date,
        "amount": payment_order.amount
    }


@frappe.whitelist()
def retry_payment(payment_order_name):
    """Retry a failed payment"""
    payment_order = frappe.get_doc("Payment Order", payment_order_name)

    if payment_order.status not in ["Failed", "Cancelled"]:
        frappe.throw(_("Only failed or cancelled payments can be retried"))

    # Create a new payment order
    return create_fee_payment_order(payment_order.reference_name)


@frappe.whitelist(allow_guest=False)
def download_receipt(payment_entry, variant=None):
    """
    Download payment receipt as PDF

    Args:
        payment_entry: Payment Entry name
        variant: Template variant - 'print' for print-optimized, None for default
    """
    pe = frappe.get_doc("Payment Entry", payment_entry)

    # Check permission
    if pe.party_type == "Student":
        student = frappe.get_doc("Student", pe.party)
        if not has_receipt_permission(student):
            frappe.throw(_("You don't have permission to download this receipt"))

    # Get related data
    payment_order = frappe.db.get_value(
        "Payment Order",
        {"payment_entry": payment_entry},
        ["name", "gateway_payment_id", "gateway_order_id", "reference_name", "payment_gateway", "amount"],
        as_dict=True
    )

    fees = None
    if payment_order and payment_order.reference_name:
        fees = frappe.get_doc("Fees", payment_order.reference_name)

    # Get company and address
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    company_address = None
    if company:
        company_address = frappe.db.get_value("Company", company, "company_description")

    # Get student data
    student_data = None
    if pe.party_type == "Student" and pe.party:
        student_data = frappe.get_doc("Student", pe.party)

    # Convert amount to words
    amount_in_words = None
    if payment_order and payment_order.amount:
        amount_in_words = money_in_words(payment_order.amount, "INR")

    # Select template based on variant
    template = "university_erp/university_payments/templates/payment_receipt.html"
    if variant == "print":
        template = "university_erp/university_payments/templates/payment_receipt_print.html"

    # Render receipt HTML
    html = frappe.render_template(
        template,
        {
            "payment_entry": pe,
            "payment_order": payment_order or frappe._dict(),
            "fees": fees,
            "student": student_data,
            "company": company,
            "company_address": company_address,
            "amount_in_words": amount_in_words
        }
    )

    # Generate PDF
    from frappe.utils.pdf import get_pdf

    pdf = get_pdf(html)

    frappe.local.response.filename = f"Receipt_{payment_entry}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"


def money_in_words(amount, currency="INR"):
    """Convert amount to words (Indian format for INR)"""
    from frappe.utils import flt

    amount = flt(amount)

    if amount < 0:
        return "Minus " + money_in_words(abs(amount), currency)

    if amount == 0:
        return "Zero Rupees Only"

    # Number to words mapping
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def num_to_words(n):
        if n < 20:
            return ones[int(n)]
        elif n < 100:
            return tens[int(n) // 10] + (" " + ones[int(n) % 10] if n % 10 else "")
        elif n < 1000:
            return ones[int(n) // 100] + " Hundred" + (" and " + num_to_words(n % 100) if n % 100 else "")
        elif n < 100000:
            return num_to_words(n // 1000) + " Thousand" + (" " + num_to_words(n % 1000) if n % 1000 else "")
        elif n < 10000000:
            return num_to_words(n // 100000) + " Lakh" + (" " + num_to_words(n % 100000) if n % 100000 else "")
        else:
            return num_to_words(n // 10000000) + " Crore" + (" " + num_to_words(n % 10000000) if n % 10000000 else "")

    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))

    result = "Rupees " + num_to_words(rupees)
    if paise:
        result += " and " + num_to_words(paise) + " Paise"
    result += " Only"

    return result


def has_receipt_permission(student):
    """Check if current user can download receipt for student"""
    # System Manager and Accounts can download any receipt
    if "System Manager" in frappe.get_roles() or "Accounts Manager" in frappe.get_roles():
        return True

    # Student can download their own receipts
    if student.user == frappe.session.user:
        return True
    if student.student_email_id == frappe.session.user:
        return True

    # Guardian can download
    guardian_emails = frappe.db.get_all(
        "Student Guardian",
        filters={"parent": student.name},
        pluck="guardian"
    )
    for guardian in guardian_emails:
        email = frappe.db.get_value("Guardian", guardian, "email_address")
        if email == frappe.session.user:
            return True

    return False

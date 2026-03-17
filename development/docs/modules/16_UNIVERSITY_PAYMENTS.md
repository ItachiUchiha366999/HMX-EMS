# University Payments Module

## Overview

The University Payments module handles payment gateway integration (Razorpay, PayU), General Ledger (GL) posting to ERPNext Accounts, fee-account mapping, bank reconciliation, and payment order management. It serves as the financial backend for fee collection.

## Module Location
```
university_erp/university_payments/
```

## DocTypes (8 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Razorpay Settings | Main | Razorpay gateway config |
| PayU Settings | Main | PayU gateway config |
| Payment Order | Main | Payment schedule/order |
| Webhook Log | Main | Gateway webhook logs |
| Fee Category Account | Main | Fee-GL account mapping |
| University Accounts Settings | Main | Accounting configuration |
| Bank Transaction | Main | Bank reconciliation |
| Fee Refund | Main | Refund processing |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                   UNIVERSITY PAYMENTS MODULE                      |
+------------------------------------------------------------------+
|                                                                   |
|  PAYMENT GATEWAYS                                                 |
|  +-------------------+       +-------------------+                |
|  | RAZORPAY SETTINGS |       |   PAYU SETTINGS   |                |
|  +-------------------+       +-------------------+                |
|  | - API Keys        |       | - Merchant Key    |                |
|  | - Webhook Secret  |       | - Salt            |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           +-------------+-------------+                           |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              |   PAYMENT ORDER   |                                |
|              +-------------------+                                |
|              | - Fee reference   |                                |
|              | - Amount          |                                |
|              | - Status          |                                |
|              +-------------------+                                |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              |   WEBHOOK LOG     |                                |
|              +-------------------+                                |
|              | - Raw payload     |                                |
|              | - Processed       |                                |
|              +-------------------+                                |
|                                                                   |
|  GL INTEGRATION                                                   |
|  +-------------------+       +-------------------+                |
|  | UNIVERSITY        |       | FEE CATEGORY      |                |
|  | ACCOUNTS SETTINGS |       |    ACCOUNT        |                |
|  +-------------------+       +-------------------+                |
|  | - Company         |       | - Fee Type        |                |
|  | - Default Accounts|       | - Income Account  |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           +-------------+-------------+                           |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              |   ERPNEXT GL      |                                |
|              +-------------------+                                |
|              | - Journal Entry   |                                |
|              | - GL Entry        |                                |
|              +-------------------+                                |
|                                                                   |
|  RECONCILIATION                                                   |
|  +-------------------+       +-------------------+                |
|  | BANK TRANSACTION  |       |   FEE REFUND      |                |
|  +-------------------+       +-------------------+                |
|  | - Statement import|       | - Refund process  |                |
|  | - Match payments  |       | - GL reversal     |                |
|  +-------------------+       +-------------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## Payment Flow Diagram

```
+------------------------------------------------------------------+
|                     PAYMENT FLOW                                  |
+------------------------------------------------------------------+
|                                                                   |
|  STUDENT                                                          |
|  +-------------------+                                            |
|  | View Fee Invoice  |                                            |
|  | (Outstanding Rs.  |                                            |
|  |  50,000)          |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           v                                                       |
|  +-------------------+     +-------------------+                  |
|  |   Click Pay       |---->|  Create Payment   |                  |
|  |                   |     |      Order        |                  |
|  +-------------------+     +-------------------+                  |
|                                    |                              |
|                                    v                              |
|                     +----------------------------+                |
|                     |    Select Gateway          |                |
|                     +----------------------------+                |
|                            /           \                          |
|                           v             v                         |
|              +----------------+    +----------------+             |
|              |   RAZORPAY    |    |     PAYU       |             |
|              |   Checkout    |    |   Checkout     |             |
|              +----------------+    +----------------+             |
|                     |                    |                        |
|                     v                    v                        |
|              +----------------+    +----------------+             |
|              |   Card/UPI    |    |   Card/UPI     |             |
|              |   Payment     |    |   Payment      |             |
|              +----------------+    +----------------+             |
|                     |                    |                        |
|                     +--------+----------+                         |
|                              |                                    |
|                              v                                    |
|                    +-------------------+                          |
|                    |   WEBHOOK         |                          |
|                    |   Notification    |                          |
|                    +-------------------+                          |
|                              |                                    |
|                              v                                    |
|                    +-------------------+                          |
|                    | Update Payment    |                          |
|                    |    Order          |                          |
|                    +-------------------+                          |
|                              |                                    |
|           +------------------+------------------+                 |
|           |                                     |                 |
|           v                                     v                 |
|  +-------------------+               +-------------------+        |
|  |   SUCCESS         |               |    FAILURE        |        |
|  +-------------------+               +-------------------+        |
|           |                                     |                 |
|           v                                     v                 |
|  +-------------------+               +-------------------+        |
|  | Update Fees       |               | Show Error        |        |
|  | Outstanding = 0   |               | Allow Retry       |        |
|  +-------------------+               +-------------------+        |
|           |                                                       |
|           v                                                       |
|  +-------------------+                                            |
|  |  Create GL Entry  |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           v                                                       |
|  +-------------------+                                            |
|  | Send Receipt      |                                            |
|  +-------------------+                                            |
|                                                                   |
+------------------------------------------------------------------+
```

## DocType Details

### 1. Razorpay Settings
**Purpose**: Razorpay gateway configuration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| is_enabled | Check | Gateway active |
| api_key | Data | Razorpay Key ID |
| api_secret | Password | Key Secret |
| webhook_secret | Password | Webhook verification |
| is_sandbox | Check | Test mode |
| success_url | Data | Success redirect |
| cancel_url | Data | Cancel redirect |

### 2. PayU Settings
**Purpose**: PayU gateway configuration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| is_enabled | Check | Gateway active |
| merchant_key | Data | PayU Merchant Key |
| merchant_salt | Password | PayU Salt |
| is_sandbox | Check | Test mode |
| success_url | Data | Success callback |
| failure_url | Data | Failure callback |
| cancel_url | Data | Cancel callback |

### 3. Payment Order
**Purpose**: Payment request/order records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| order_id | Data | System order ID |
| gateway | Select | Razorpay/PayU |
| gateway_order_id | Data | Gateway's order ID |
| reference_doctype | Link | Fees/Fee Payment |
| reference_name | Dynamic Link | Document reference |
| student | Link (Student) | Payer |
| amount | Currency | Order amount |
| currency | Data | INR |
| status | Select | Created/Paid/Failed/Expired |
| payment_method | Data | Card/UPI/NetBanking |
| gateway_response | JSON | Full response |
| created_on | Datetime | Creation time |
| paid_on | Datetime | Payment time |
| expires_on | Datetime | Order expiry |

### 4. Webhook Log
**Purpose**: Log all gateway webhooks

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| gateway | Select | Razorpay/PayU |
| event_type | Data | payment.captured/payment.failed |
| payload | JSON | Raw webhook payload |
| signature | Data | Webhook signature |
| is_verified | Check | Signature verified |
| is_processed | Check | Processed successfully |
| processing_error | Text | If processing failed |
| received_at | Datetime | Receipt time |
| processed_at | Datetime | Processing time |

### 5. Fee Category Account
**Purpose**: Map fee types to GL accounts

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| fee_category | Link (Fee Category) | Fee type |
| company | Link (Company) | ERPNext company |
| income_account | Link (Account) | Revenue account |
| receivable_account | Link (Account) | AR account |
| cost_center | Link (Cost Center) | Cost center |

### 6. University Accounts Settings
**Purpose**: Central accounting configuration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| company | Link (Company) | ERPNext company |
| student_receivable_account | Link (Account) | Student AR |
| default_income_account | Link (Account) | Default revenue |
| bank_account | Link (Account) | Bank for receipts |
| default_cost_center | Link (Cost Center) | Default CC |
| enable_automatic_gl | Check | Auto GL posting |

### 7. Bank Transaction
**Purpose**: Bank statement reconciliation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| bank_account | Link (Account) | Bank account |
| transaction_date | Date | Transaction date |
| amount | Currency | Transaction amount |
| transaction_type | Select | Credit/Debit |
| reference_number | Data | Bank reference |
| description | Data | Transaction narration |
| matched_payment | Link (Payment Order) | Matched payment |
| is_reconciled | Check | Reconciled |

### 8. Fee Refund
**Purpose**: Process fee refunds

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| original_fees | Link (Fees) | Original fee |
| original_payment | Link (Payment Order) | Original payment |
| refund_amount | Currency | Amount to refund |
| refund_reason | Select | Withdrawal/Overpayment/Error |
| bank_account | Data | Student bank details |
| ifsc_code | Data | IFSC code |
| account_holder | Data | Account name |
| gateway_refund_id | Data | Gateway refund ID |
| refund_date | Date | Processed date |
| status | Select | Pending/Processed/Failed |
| gl_entry | Link (Journal Entry) | Reversal entry |

## GL Posting Implementation

### Fee Submission GL Entry
```python
# university_erp/university_payments/gl_posting.py

def on_fees_submit(doc, method):
    """Create GL entries when fees is submitted"""
    settings = frappe.get_single("University Accounts Settings")

    if not settings.enable_automatic_gl:
        return

    # Get account mapping for fee categories
    gl_entries = []

    for component in doc.components:
        account_mapping = get_fee_category_account(component.fees_category)

        # Debit: Student Receivable
        gl_entries.append({
            "account": account_mapping.receivable_account or settings.student_receivable_account,
            "debit": component.amount,
            "debit_in_account_currency": component.amount,
            "party_type": "Customer",
            "party": get_student_customer(doc.student),
            "against": account_mapping.income_account,
            "voucher_type": "Fees",
            "voucher_no": doc.name,
            "cost_center": account_mapping.cost_center or settings.default_cost_center,
        })

        # Credit: Income Account
        gl_entries.append({
            "account": account_mapping.income_account or settings.default_income_account,
            "credit": component.amount,
            "credit_in_account_currency": component.amount,
            "against": get_student_customer(doc.student),
            "voucher_type": "Fees",
            "voucher_no": doc.name,
            "cost_center": account_mapping.cost_center or settings.default_cost_center,
        })

    # Make GL entries
    from erpnext.accounts.general_ledger import make_gl_entries
    make_gl_entries(gl_entries, cancel=False)

def on_fees_cancel(doc, method):
    """Reverse GL entries when fees is cancelled"""
    from erpnext.accounts.general_ledger import make_reverse_gl_entries
    make_reverse_gl_entries(voucher_type="Fees", voucher_no=doc.name)
```

### Payment Receipt GL Entry
```python
def create_payment_gl_entry(payment_order):
    """Create GL entry when payment is received"""
    settings = frappe.get_single("University Accounts Settings")

    fees = frappe.get_doc("Fees", payment_order.reference_name)

    gl_entries = [
        # Debit: Bank Account
        {
            "account": settings.bank_account,
            "debit": payment_order.amount,
            "debit_in_account_currency": payment_order.amount,
            "against": settings.student_receivable_account,
            "voucher_type": "Payment Order",
            "voucher_no": payment_order.name,
        },
        # Credit: Student Receivable
        {
            "account": settings.student_receivable_account,
            "credit": payment_order.amount,
            "credit_in_account_currency": payment_order.amount,
            "party_type": "Customer",
            "party": get_student_customer(fees.student),
            "against": settings.bank_account,
            "voucher_type": "Payment Order",
            "voucher_no": payment_order.name,
        }
    ]

    from erpnext.accounts.general_ledger import make_gl_entries
    make_gl_entries(gl_entries, cancel=False)
```

## Gateway Integration

### Razorpay Integration
```python
# university_erp/university_payments/razorpay_integration.py

import razorpay

def create_razorpay_order(fees, amount):
    """Create Razorpay order"""
    settings = frappe.get_single("Razorpay Settings")

    if not settings.is_enabled:
        frappe.throw("Razorpay is not enabled")

    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    order_data = {
        "amount": int(amount * 100),  # Paise
        "currency": "INR",
        "receipt": fees,
        "notes": {
            "fees_id": fees,
            "student": frappe.db.get_value("Fees", fees, "student")
        }
    }

    order = client.order.create(data=order_data)

    # Create payment order record
    payment_order = frappe.new_doc("Payment Order")
    payment_order.gateway = "Razorpay"
    payment_order.gateway_order_id = order["id"]
    payment_order.reference_doctype = "Fees"
    payment_order.reference_name = fees
    payment_order.amount = amount
    payment_order.status = "Created"
    payment_order.insert()

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "key": settings.api_key,
        "payment_order": payment_order.name
    }

@frappe.whitelist(allow_guest=True)
def handle_razorpay_webhook():
    """Handle Razorpay webhook"""
    settings = frappe.get_single("Razorpay Settings")
    payload = frappe.request.get_data()
    signature = frappe.request.headers.get("X-Razorpay-Signature")

    # Log webhook
    log = frappe.new_doc("Webhook Log")
    log.gateway = "Razorpay"
    log.payload = payload.decode()
    log.signature = signature
    log.insert()

    # Verify signature
    import hmac
    import hashlib

    expected_signature = hmac.new(
        settings.webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if signature != expected_signature:
        log.is_verified = False
        log.processing_error = "Invalid signature"
        log.save()
        return {"status": "invalid signature"}

    log.is_verified = True

    # Process event
    data = frappe.parse_json(payload.decode())
    event = data.get("event")

    try:
        if event == "payment.captured":
            process_payment_success(data["payload"]["payment"]["entity"])
        elif event == "payment.failed":
            process_payment_failure(data["payload"]["payment"]["entity"])

        log.is_processed = True
    except Exception as e:
        log.processing_error = str(e)

    log.processed_at = frappe.utils.now_datetime()
    log.save()

    return {"status": "ok"}

def process_payment_success(payment):
    """Handle successful payment"""
    order_id = payment.get("order_id")

    payment_order = frappe.get_doc("Payment Order", {"gateway_order_id": order_id})
    payment_order.status = "Paid"
    payment_order.payment_method = payment.get("method")
    payment_order.gateway_response = frappe.as_json(payment)
    payment_order.paid_on = frappe.utils.now_datetime()
    payment_order.save()

    # Update fees outstanding
    fees = frappe.get_doc("Fees", payment_order.reference_name)
    fees.outstanding_amount -= payment_order.amount
    if fees.outstanding_amount <= 0:
        fees.outstanding_amount = 0
    fees.save()

    # Create GL entry
    create_payment_gl_entry(payment_order)

    # Send receipt
    send_payment_receipt(payment_order)
```

### PayU Integration
```python
# university_erp/university_payments/webhooks/payu_callback.py

import hashlib

@frappe.whitelist(allow_guest=True)
def payu_success():
    """Handle PayU success callback"""
    data = frappe.form_dict

    # Log
    log = frappe.new_doc("Webhook Log")
    log.gateway = "PayU"
    log.event_type = "success"
    log.payload = frappe.as_json(data)
    log.insert()

    # Verify hash
    settings = frappe.get_single("PayU Settings")
    if not verify_payu_hash(data, settings.merchant_salt):
        log.is_verified = False
        log.processing_error = "Hash verification failed"
        log.save()
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/payment-failed"
        return

    log.is_verified = True

    # Process payment
    txnid = data.get("txnid")
    payment_order = frappe.get_doc("Payment Order", txnid)
    payment_order.status = "Paid"
    payment_order.gateway_response = frappe.as_json(data)
    payment_order.paid_on = frappe.utils.now_datetime()
    payment_order.save()

    # Update fees
    update_fees_on_payment(payment_order)

    log.is_processed = True
    log.save()

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/payment-success?order={txnid}"

def verify_payu_hash(data, salt):
    """Verify PayU response hash"""
    hash_string = f"{salt}|{data.get('status')}|||||||||||{data.get('email')}|{data.get('firstname')}|{data.get('productinfo')}|{data.get('amount')}|{data.get('txnid')}|{data.get('key')}"
    calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest().lower()
    return calculated_hash == data.get("hash")
```

## API Endpoints

### Payment Initiation
```python
@frappe.whitelist()
def initiate_payment(fees_id, gateway="Razorpay"):
    """Initiate payment for fees"""
    fees = frappe.get_doc("Fees", fees_id)

    if fees.outstanding_amount <= 0:
        frappe.throw("No outstanding amount")

    if gateway == "Razorpay":
        return create_razorpay_order(fees_id, fees.outstanding_amount)
    elif gateway == "PayU":
        return create_payu_order(fees_id, fees.outstanding_amount)

@frappe.whitelist()
def verify_payment(payment_order_id, gateway_payment_id, gateway_signature):
    """Verify payment after client-side completion"""
    payment_order = frappe.get_doc("Payment Order", payment_order_id)

    if payment_order.gateway == "Razorpay":
        is_valid = verify_razorpay_signature(
            payment_order.gateway_order_id,
            gateway_payment_id,
            gateway_signature
        )

        if is_valid:
            payment_order.status = "Paid"
            payment_order.save()
            update_fees_on_payment(payment_order)
            return {"status": "success"}

    return {"status": "failed"}
```

### Refund
```python
@frappe.whitelist()
def process_refund(fee_refund_id):
    """Process fee refund"""
    refund = frappe.get_doc("Fee Refund", fee_refund_id)
    payment_order = frappe.get_doc("Payment Order", refund.original_payment)

    if payment_order.gateway == "Razorpay":
        settings = frappe.get_single("Razorpay Settings")
        client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

        gateway_refund = client.payment.refund(
            payment_order.gateway_response.get("id"),
            int(refund.refund_amount * 100)
        )

        refund.gateway_refund_id = gateway_refund["id"]
        refund.status = "Processed"
        refund.save()

        # Create reversal GL entry
        create_refund_gl_entry(refund)

    return refund
```

## Reports

1. **Payment Collection Report** - Daily/monthly collections
2. **Gateway-wise Report** - Collections by gateway
3. **Outstanding Report** - Pending fees
4. **Refund Report** - Processed refunds
5. **Reconciliation Report** - Bank matching
6. **GL Posting Report** - Posted entries

## Related Files

```
university_erp/
+-- university_payments/
    +-- doctype/
    |   +-- razorpay_settings/
    |   +-- payu_settings/
    |   +-- payment_order/
    |   +-- webhook_log/
    |   +-- fee_category_account/
    |   +-- university_accounts_settings/
    |   +-- bank_transaction/
    |   +-- fee_refund/
    +-- gl_posting.py
    +-- razorpay_integration.py
    +-- webhooks/
        +-- razorpay_webhook.py
        +-- payu_callback.py
```

## See Also

- [University Finance Module](05_UNIVERSITY_FINANCE.md)
- [University Integrations Module](14_UNIVERSITY_INTEGRATIONS.md)
- [Examinations Module](04_EXAMINATIONS.md)

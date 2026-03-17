# University Finance Module

## Overview

The University Finance module manages student fees, scholarships, and fee-related operations. It extends the Education app's Fees functionality with bulk fee generation, scholarship management, and integrates with ERPNext's accounting engine for GL entries.

## Module Location
```
university_erp/fees_finance/
```

## DocTypes (8 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Fee Category | Main | Types of fees (Tuition, Hostel, etc.) |
| Scholarship Type | Main | Scholarship definitions |
| Student Scholarship | Main | Student scholarship awards |
| Fee Payment | Main | Payment records |
| Bulk Fee Generator | Main | Batch fee creation |
| Bulk Fee Generator Student | Child | Students in bulk generation |
| Fee Refund | Main | Refund processing |
| Fee Refund Deduction | Child | Deductions from refund |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                    UNIVERSITY FINANCE MODULE                      |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |   FEE CATEGORY    |       | SCHOLARSHIP TYPE  |                |
|  +-------------------+       +-------------------+                |
|  | - Tuition         |       | - Merit Based     |                |
|  | - Hostel          |       | - Need Based      |                |
|  | - Transport       |       | - Government      |                |
|  | - Library         |       | - Private         |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           v                           v                           |
|  +-------------------+       +-------------------+                |
|  |       FEES        |       |    STUDENT        |                |
|  | (Education App)   |       |   SCHOLARSHIP     |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           +-------------+-------------+                           |
|                         |                                         |
|                         v                                         |
|                +-------------------+                              |
|                |   FEE PAYMENT     |                              |
|                +-------------------+                              |
|                         |                                         |
|           +-------------+-------------+                           |
|           |                           |                           |
|           v                           v                           |
|  +-------------------+       +-------------------+                |
|  |   BULK FEE        |       |   FEE REFUND      |                |
|  |   GENERATOR       |       +-------------------+                |
|  +-------------------+                                            |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Education App Integration
```
+--------------------+       +--------------------+
|  UNIVERSITY        |       |    EDUCATION       |
|    FINANCE         |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| Fee Category ------|------>| Fee Category       |
|   (extends)        |       | (base)             |
|                    |       |                    |
| Fees Override -----|------>| Fees               |
|                    |       | (adds GL posting)  |
|                    |       |                    |
| Scholarship -------|------>| Student            |
|                    |       | Program            |
+--------------------+       +--------------------+
```

### ERPNext Accounting Integration
```
+--------------------+       +--------------------+
|  UNIVERSITY        |       |     ERPNEXT        |
|    FINANCE         |------>|   ACCOUNTS         |
+--------------------+       +--------------------+
|                    |       |                    |
| Fee Submit --------|------>| Journal Entry      |
|                    |       | GL Entry           |
|                    |       |                    |
| Fee Payment -------|------>| Payment Entry      |
|                    |       |                    |
| Fee Refund --------|------>| Credit Note        |
+--------------------+       +--------------------+
```

### Cross-Module Relationships
```
                    +--------------------+
                    | UNIVERSITY FINANCE |
                    +--------------------+
                            /|\
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+----------------+  +----------------+  +----------------+
|   ADMISSIONS   |  |    HOSTEL      |  |   TRANSPORT    |
+----------------+  +----------------+  +----------------+
| Admission fees |  | Hostel fees    |  | Transport fees |
| on enrollment  |  | linked         |  | linked         |
+----------------+  +----------------+  +----------------+
         |                  |                  |
         +------------------+------------------+
                            |
                            v
                   +----------------+
                   |   PAYMENTS     |
                   +----------------+
                   | Razorpay/PayU  |
                   | integration    |
                   +----------------+
```

## DocType Details

### 1. Fee Category
**Purpose**: Define types of fees collected

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| category_name | Data | e.g., "Tuition Fee" |
| category_code | Data | Short code |
| description | Text | Category description |
| is_mandatory | Check | Required for all |
| applies_to | Select | Student/Hostel/Transport |
| default_amount | Currency | Standard amount |
| income_account | Link (Account) | GL income account |
| receivable_account | Link (Account) | Receivable account |

**Standard Categories**:
- Tuition Fee
- Examination Fee
- Library Fee
- Laboratory Fee
- Hostel Fee
- Transport Fee
- Caution Deposit
- Development Fee

### 2. Scholarship Type
**Purpose**: Define scholarship programs

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| scholarship_name | Data | Scholarship name |
| scholarship_type | Select | Merit/Need/Government |
| amount | Currency | Fixed amount |
| percentage | Percent | Percentage of fees |
| eligibility_criteria | Text Editor | Requirements |
| applicable_programs | Table | Eligible programs |
| max_recipients | Int | Maximum awards |
| valid_from | Date | Start date |
| valid_to | Date | End date |
| renewal_criteria | Text | Renewal conditions |

**Scholarship Types**:
- Merit Based (academic performance)
- Need Based (financial need)
- Government (SC/ST/OBC/EWS)
- Private (corporate/alumni funded)
- Sports/Cultural (achievements)

### 3. Student Scholarship
**Purpose**: Award scholarship to student

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student reference |
| scholarship_type | Link | Scholarship type |
| academic_year | Link | Applicable year |
| amount | Currency | Award amount |
| percentage | Percent | Fee reduction % |
| status | Select | Applied/Approved/Disbursed |
| approved_by | Link (User) | Approver |
| approved_date | Date | Approval date |
| disbursement_date | Date | Payment date |
| remarks | Text | Notes |

**Workflow**:
```
Applied --> Under Review --> Approved --> Disbursed
                         \
                          --> Rejected
```

### 4. Fee Payment
**Purpose**: Record fee payments

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Payer |
| fees | Link (Fees) | Fee invoice |
| amount | Currency | Payment amount |
| payment_mode | Select | Cash/Online/DD/Cheque |
| payment_date | Date | Payment date |
| transaction_id | Data | Gateway transaction ID |
| receipt_number | Data | Receipt number |
| bank_name | Data | Bank (if cheque/DD) |
| status | Select | Pending/Completed/Failed |

### 5. Bulk Fee Generator
**Purpose**: Generate fees for multiple students

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| fee_structure | Link (Fee Structure) | Fee template |
| program | Link (Program) | Target program |
| academic_year | Link | Academic year |
| academic_term | Link | Semester |
| student_batch | Data | Batch filter |
| due_date | Date | Payment deadline |
| students | Table | Selected students |
| fees_generated | Int | Count created |
| status | Select | Draft/Processing/Completed |

### 6. Fee Refund
**Purpose**: Process fee refunds

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| fees | Link (Fees) | Original fee |
| refund_amount | Currency | Amount to refund |
| refund_reason | Select | Withdrawal/Transfer/Overpayment |
| deductions | Table | Applicable deductions |
| net_refund | Currency | Final refund amount |
| refund_date | Date | Processing date |
| bank_account | Data | Student bank details |
| status | Select | Pending/Approved/Processed |

**Deduction Types**:
- Processing Fee
- Administrative Charges
- Pro-rata for period attended
- Non-refundable components

## Data Flow Diagrams

### Fee Generation Flow
```
+----------------+     +------------------+     +------------------+
| Fee Structure  |---->| Bulk Fee         |---->| Select Students  |
| (Template)     |     | Generator        |     | (by Program/Batch)|
+----------------+     +------------------+     +------------------+
                                                        |
                                                        v
+----------------+     +------------------+     +------------------+
|    FEES        |<----|    Generate      |<----|   Apply          |
| (Per Student)  |     |    Fee Records   |     | Scholarships     |
+----------------+     +------------------+     +------------------+
```

### Payment Flow
```
+----------------+     +------------------+     +------------------+
|    FEES        |---->| Student Portal   |---->| Payment Gateway  |
| (Outstanding)  |     | Pay Button       |     | (Razorpay/PayU)  |
+----------------+     +------------------+     +------------------+
                                                        |
                                                        v
+----------------+     +------------------+     +------------------+
|   GL ENTRY     |<----|   FEE PAYMENT    |<----|   Webhook        |
| (ERPNext)      |     |   Created        |     |   Confirmation   |
+----------------+     +------------------+     +------------------+
```

### GL Integration Flow
```
+------------------------------------------------------------------+
|                    FEE SUBMISSION GL ENTRIES                      |
+------------------------------------------------------------------+
|                                                                   |
|  DEBIT                              CREDIT                        |
|  +------------------------+        +------------------------+     |
|  | Student Receivable     |        | Fee Income Account     |     |
|  | Account                |        |                        |     |
|  | Rs. 50,000            |        | Rs. 50,000            |     |
|  +------------------------+        +------------------------+     |
|                                                                   |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                    PAYMENT RECEIPT GL ENTRIES                     |
+------------------------------------------------------------------+
|                                                                   |
|  DEBIT                              CREDIT                        |
|  +------------------------+        +------------------------+     |
|  | Bank Account           |        | Student Receivable     |     |
|  |                        |        | Account                |     |
|  | Rs. 50,000            |        | Rs. 50,000            |     |
|  +------------------------+        +------------------------+     |
|                                                                   |
+------------------------------------------------------------------+
```

## Integration Points

### Fees Override for GL Posting
```python
# university_erp/overrides/fees.py

class UniversityFees(Fees):
    """Extended Fees with GL integration"""

    def on_submit(self):
        super().on_submit()
        self.create_gl_entries()

    def create_gl_entries(self):
        """Post to ERPNext General Ledger"""
        from erpnext.accounts.general_ledger import make_gl_entries

        settings = frappe.get_single("University Accounts Settings")

        gl_entries = [
            # Debit Receivable
            {
                "account": settings.student_receivable_account,
                "debit": self.grand_total,
                "party_type": "Customer",
                "party": self.get_student_customer(),
            },
            # Credit Income
            {
                "account": settings.fee_income_account,
                "credit": self.grand_total,
                "cost_center": settings.default_cost_center,
            }
        ]

        make_gl_entries(gl_entries, cancel=False)
```

### With Payment Gateway
```python
# Hook from payment webhooks
doc_events = {
    "Fees": {
        "on_submit": [
            "university_erp.integrations.gl_integration.create_fee_gl_entry",
            "university_erp.university_payments.gl_posting.on_fees_submit",
        ],
    }
}

# Payment confirmation
def on_payment_success(transaction_id, fees_id, amount):
    fee_payment = frappe.new_doc("Fee Payment")
    fee_payment.fees = fees_id
    fee_payment.amount = amount
    fee_payment.transaction_id = transaction_id
    fee_payment.status = "Completed"
    fee_payment.insert()

    # Update fees outstanding
    fees = frappe.get_doc("Fees", fees_id)
    fees.outstanding_amount -= amount
    fees.save()
```

### Scholarship Application
```python
def apply_scholarship(student, fees):
    """Apply student's scholarship to fees"""
    scholarships = frappe.get_all("Student Scholarship", {
        "student": student,
        "status": "Approved",
        "academic_year": fees.academic_year
    })

    total_discount = 0
    for sch in scholarships:
        sch_doc = frappe.get_doc("Student Scholarship", sch.name)
        if sch_doc.percentage:
            discount = fees.grand_total * (sch_doc.percentage / 100)
        else:
            discount = sch_doc.amount
        total_discount += discount

    return total_discount
```

## API Endpoints

### Fee Management
```python
@frappe.whitelist()
def get_student_fees(student, academic_year=None):
    """Get all fees for a student"""
    filters = {"student": student}
    if academic_year:
        filters["academic_year"] = academic_year

    return frappe.get_all("Fees", filters=filters, fields=["*"])

@frappe.whitelist()
def get_fee_summary(student):
    """Get fee summary with outstanding"""
    total_fees = frappe.db.sql("""
        SELECT SUM(grand_total) as total,
               SUM(outstanding_amount) as outstanding
        FROM `tabFees`
        WHERE student = %s AND docstatus = 1
    """, student, as_dict=True)[0]

    return {
        "total_fees": total_fees.total or 0,
        "outstanding": total_fees.outstanding or 0,
        "paid": (total_fees.total or 0) - (total_fees.outstanding or 0)
    }
```

### Bulk Operations
```python
@frappe.whitelist()
def generate_bulk_fees(bulk_fee_generator):
    """Process bulk fee generation"""
    doc = frappe.get_doc("Bulk Fee Generator", bulk_fee_generator)

    for student_row in doc.students:
        fee = create_fee_from_structure(
            student=student_row.student,
            fee_structure=doc.fee_structure,
            due_date=doc.due_date
        )
        # Apply scholarships
        discount = apply_scholarship(student_row.student, fee)
        if discount:
            fee.discount = discount
            fee.save()

    doc.status = "Completed"
    doc.save()
```

## Reports

1. **Fee Collection Report** - Collected vs outstanding
2. **Fee Defaulters Report** - Students with pending fees
3. **Scholarship Report** - Awards by type/program
4. **Revenue Analysis** - Fee income by category
5. **Refund Register** - Processed refunds
6. **Day Book** - Daily collections

## Related Files

```
university_erp/
+-- fees_finance/
|   +-- doctype/
|   |   +-- fee_category/
|   |   +-- scholarship_type/
|   |   +-- student_scholarship/
|   |   +-- fee_payment/
|   |   +-- bulk_fee_generator/
|   |   +-- bulk_fee_generator_student/
|   |   +-- fee_refund/
|   |   +-- fee_refund_deduction/
|   +-- api.py
+-- overrides/
|   +-- fees.py  # GL integration
+-- university_payments/
    +-- gl_posting.py
```

## See Also

- [University Payments Module](16_UNIVERSITY_PAYMENTS.md)
- [University Hostel Module](07_UNIVERSITY_HOSTEL.md)
- [Education App Documentation](../04_education_deep_dive.md)

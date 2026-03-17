# University Library Module

## Overview

The University Library module manages library resources, memberships, book transactions (issue/return), reservations, and fine calculation. It provides comprehensive library management for educational institutions.

## Module Location
```
university_erp/university_library/
```

## DocTypes (7 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Library Category | Main | Book categories |
| Library Subject | Main | Subject classification |
| Library Article | Main | Books and resources |
| Library Member | Main | Library memberships |
| Library Transaction | Main | Issue/return records |
| Library Fine | Main | Overdue fines |
| Book Reservation | Main | Advance booking |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                    UNIVERSITY LIBRARY MODULE                      |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  | LIBRARY CATEGORY  |       |  LIBRARY SUBJECT  |                |
|  +-------------------+       +-------------------+                |
|  | - Textbooks       |       | - Computer Science|                |
|  | - Reference       |       | - Mathematics     |                |
|  | - Journals        |       | - Physics         |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           +-------------+-------------+                           |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              |  LIBRARY ARTICLE  |                                |
|              +-------------------+                                |
|              | - Title           |                                |
|              | - Author          |                                |
|              | - ISBN            |                                |
|              | - Copies          |                                |
|              +-------------------+                                |
|                         |                                         |
|           +-------------+-------------+                           |
|           |             |             |                           |
|           v             v             v                           |
|  +------------+  +------------+  +------------+                   |
|  |  LIBRARY   |  |  LIBRARY   |  |   BOOK     |                   |
|  |   MEMBER   |  | TRANSACTION|  |RESERVATION |                   |
|  +------------+  +------------+  +------------+                   |
|  | - Student  |  | - Issue    |  | - Reserve  |                   |
|  | - Faculty  |  | - Return   |  | - Queue    |                   |
|  +------------+  +------------+  +------------+                   |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              |   LIBRARY FINE    |                                |
|              +-------------------+                                |
|              | - Overdue amount  |                                |
|              | - Payment status  |                                |
|              +-------------------+                                |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Module Dependencies
```
+--------------------+       +--------------------+
|     LIBRARY        |       |    EDUCATION       |
|     (Custom)       |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| Library Member ----|------>| Student            |
|                    |       | Program            |
+--------------------+       +--------------------+

+--------------------+       +--------------------+
|     LIBRARY        |       |  UNIVERSITY HR     |
|     (Custom)       |------>|                    |
+--------------------+       +--------------------+
|                    |       |                    |
| Library Member ----|------>| Faculty Profile    |
| (faculty type)     |       | Employee           |
+--------------------+       +--------------------+
```

### Scheduled Tasks
```python
scheduler_events = {
    "daily": [
        "university_erp.university_erp.notification_service.send_library_overdue_notices",
        "university_erp.university_erp.scheduled_tasks.expire_library_reservations",
    ],
}
```

## DocType Details

### 1. Library Category
**Purpose**: Classification of library materials

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| category_name | Data | e.g., "Textbooks" |
| category_code | Data | Short code |
| description | Text | Category description |
| max_issue_days | Int | Default loan period |
| max_books_allowed | Int | Issue limit |
| fine_per_day | Currency | Overdue fine rate |

**Standard Categories**:
- Textbooks (14 days, Rs. 2/day fine)
- Reference Books (7 days, Rs. 5/day fine)
- Journals/Magazines (7 days, Rs. 3/day fine)
- Newspapers (Same day return)
- Thesis/Dissertations (14 days, Rs. 5/day fine)

### 2. Library Subject
**Purpose**: Subject-wise organization

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| subject_name | Data | Subject area |
| subject_code | Data | Classification code |
| parent_subject | Link (Library Subject) | Hierarchy |
| department | Link (Department) | Related department |

### 3. Library Article
**Purpose**: Book and resource records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| title | Data | Book title |
| article_type | Select | Book/Journal/Magazine/CD |
| author | Data | Author name |
| publisher | Data | Publisher |
| isbn | Data | ISBN number |
| publication_year | Data | Year published |
| edition | Data | Edition number |
| category | Link (Library Category) | Category |
| subject | Link (Library Subject) | Subject |
| total_copies | Int | Total copies owned |
| available_copies | Int | Currently available |
| shelf_location | Data | Physical location |
| price | Currency | Book price |
| status | Select | Available/All Issued/Lost |

**Copy Tracking**:
```
Total Copies = Available + Issued + Reserved + Lost
```

### 4. Library Member
**Purpose**: Library membership records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| member_type | Select | Student/Faculty/Staff |
| student | Link (Student) | If student member |
| employee | Link (Employee) | If faculty/staff |
| member_name | Data | Name |
| membership_id | Data | Library card number |
| valid_from | Date | Membership start |
| valid_to | Date | Membership expiry |
| books_issued | Int | Currently issued |
| max_books | Int | Issue limit |
| total_fines_pending | Currency | Outstanding fines |
| status | Select | Active/Suspended/Expired |

**Member Limits by Type**:
| Type | Max Books | Max Days | Fine/Day |
|------|-----------|----------|----------|
| Student | 4 | 14 | Rs. 2 |
| Faculty | 10 | 30 | Rs. 5 |
| Staff | 3 | 14 | Rs. 2 |

### 5. Library Transaction
**Purpose**: Issue and return records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| transaction_type | Select | Issue/Return/Renew |
| member | Link (Library Member) | Borrower |
| article | Link (Library Article) | Book |
| issue_date | Date | Date issued |
| due_date | Date | Return deadline |
| return_date | Date | Actual return |
| renewed_count | Int | Times renewed |
| status | Select | Issued/Returned/Overdue |
| fine_amount | Currency | If overdue |
| fine_paid | Check | Fine cleared |

**Auto-Naming**: LIB-TXN-.YYYY.-#####

### 6. Library Fine
**Purpose**: Overdue fine records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| member | Link (Library Member) | Member |
| transaction | Link (Library Transaction) | Related transaction |
| article | Link (Library Article) | Book |
| overdue_days | Int | Days late |
| fine_rate | Currency | Rate per day |
| fine_amount | Currency | Total fine |
| paid_amount | Currency | Amount paid |
| payment_date | Date | Payment date |
| status | Select | Pending/Paid/Waived |

**Fine Calculation**:
```
Fine Amount = Overdue Days * Fine Rate per Day
```

### 7. Book Reservation
**Purpose**: Advance book reservation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| member | Link (Library Member) | Requester |
| article | Link (Library Article) | Book |
| reservation_date | Date | Date requested |
| queue_position | Int | Position in queue |
| expected_available | Date | Expected availability |
| notification_sent | Check | Notified when available |
| valid_until | Date | Reservation expiry |
| status | Select | Queued/Available/Issued/Expired |

## Data Flow Diagrams

### Book Issue Flow
```
+----------------+     +------------------+     +------------------+
|   Member       |---->|   Search         |---->|   Check          |
|   Request      |     |   Article        |     |   Availability   |
+----------------+     +------------------+     +------------------+
                                                        |
                        +-------------------------------+
                        |                               |
                        v                               v
               +----------------+              +----------------+
               |   Available    |              | Not Available  |
               +----------------+              +----------------+
                        |                               |
                        v                               v
               +----------------+              +----------------+
               |   Issue Book   |              |   Reserve      |
               +----------------+              +----------------+
                        |
                        v
               +----------------+
               | Transaction    |
               | Created        |
               +----------------+
                        |
                        v
               +----------------+
               | Update         |
               | available_copies|
               +----------------+
```

### Book Return Flow
```
+----------------+     +------------------+     +------------------+
|   Member       |---->|   Scan Barcode/  |---->|   Check Due      |
|   Returns      |     |   Enter ID       |     |   Date           |
+----------------+     +------------------+     +------------------+
                                                        |
                        +-------------------------------+
                        |                               |
                        v                               v
               +----------------+              +----------------+
               |   On Time      |              |   Overdue      |
               +----------------+              +----------------+
                        |                               |
                        v                               v
               +----------------+              +----------------+
               | Mark Returned  |              | Calculate Fine |
               +----------------+              +----------------+
                        |                               |
                        +---------------+---------------+
                                        |
                                        v
                               +----------------+
                               | Update Stock   |
                               +----------------+
                                        |
                                        v
                               +----------------+
                               | Check          |
                               | Reservations   |
                               +----------------+
```

### Reservation Queue
```
Book: "Data Structures" (0 available, 3 copies issued)

Reservation Queue:
+------+----------+------------------+----------------+
| Pos. | Member   | Reserved Date    | Expected Date  |
+------+----------+------------------+----------------+
|  1   | STU-001  | 2024-01-10      | 2024-01-20     |
|  2   | STU-002  | 2024-01-11      | 2024-01-25     |
|  3   | STU-003  | 2024-01-12      | 2024-01-30     |
+------+----------+------------------+----------------+

When book returned:
1. Update available_copies
2. Notify STU-001
3. Hold book for 2 days
4. If not collected, move to STU-002
```

## Integration Points

### With Finance Module
```python
# Fine collection integrates with fees
def collect_library_fine(member, fine_amount, payment_mode):
    """Collect fine and update records"""
    fine = frappe.get_doc("Library Fine", {
        "member": member,
        "status": "Pending"
    })

    fine.paid_amount = fine_amount
    fine.payment_date = frappe.utils.today()
    fine.status = "Paid"
    fine.save()

    # Update member pending fines
    member_doc = frappe.get_doc("Library Member", member)
    member_doc.total_fines_pending -= fine_amount
    member_doc.save()
```

### Stock Management
```python
def update_article_stock(article, transaction_type):
    """Update available copies on transaction"""
    article_doc = frappe.get_doc("Library Article", article)

    if transaction_type == "Issue":
        article_doc.available_copies -= 1
    elif transaction_type == "Return":
        article_doc.available_copies += 1

    # Update status
    if article_doc.available_copies == 0:
        article_doc.status = "All Issued"
    else:
        article_doc.status = "Available"

    article_doc.save()
```

### Scheduled Tasks
```python
# Daily overdue notifications
def send_library_overdue_notices():
    """Send email to members with overdue books"""
    overdue = frappe.get_all("Library Transaction", {
        "status": "Issued",
        "due_date": ("<", frappe.utils.today())
    }, ["member", "article", "due_date"])

    for txn in overdue:
        send_overdue_email(txn)

# Expire reservations
def expire_library_reservations():
    """Expire reservations past their validity"""
    frappe.db.sql("""
        UPDATE `tabBook Reservation`
        SET status = 'Expired'
        WHERE status = 'Available'
        AND valid_until < CURDATE()
    """)
```

## API Endpoints

### Search & Issue
```python
@frappe.whitelist()
def search_articles(query, category=None, subject=None):
    """Search library catalog"""
    filters = {"status": ["!=", "Lost"]}
    if category:
        filters["category"] = category
    if subject:
        filters["subject"] = subject

    return frappe.get_all("Library Article",
        filters=filters,
        or_filters=[
            ["title", "like", f"%{query}%"],
            ["author", "like", f"%{query}%"],
            ["isbn", "like", f"%{query}%"]
        ],
        fields=["name", "title", "author", "available_copies"]
    )

@frappe.whitelist()
def issue_book(member, article):
    """Issue book to member"""
    # Validate member
    member_doc = frappe.get_doc("Library Member", member)
    if member_doc.status != "Active":
        frappe.throw("Membership not active")
    if member_doc.books_issued >= member_doc.max_books:
        frappe.throw("Maximum books already issued")

    # Validate article
    article_doc = frappe.get_doc("Library Article", article)
    if article_doc.available_copies <= 0:
        frappe.throw("Book not available")

    # Create transaction
    category = frappe.get_doc("Library Category", article_doc.category)
    txn = frappe.new_doc("Library Transaction")
    txn.transaction_type = "Issue"
    txn.member = member
    txn.article = article
    txn.issue_date = frappe.utils.today()
    txn.due_date = frappe.utils.add_days(frappe.utils.today(), category.max_issue_days)
    txn.insert()

    return txn
```

### Return & Fine
```python
@frappe.whitelist()
def return_book(transaction):
    """Return book and calculate fine"""
    txn = frappe.get_doc("Library Transaction", transaction)
    txn.return_date = frappe.utils.today()

    # Calculate overdue days
    if txn.return_date > txn.due_date:
        overdue_days = frappe.utils.date_diff(txn.return_date, txn.due_date)
        category = frappe.get_doc("Library Category",
            frappe.db.get_value("Library Article", txn.article, "category"))
        txn.fine_amount = overdue_days * category.fine_per_day

        # Create fine record
        create_library_fine(txn, overdue_days)

    txn.status = "Returned"
    txn.save()

    return txn
```

## Reports

1. **Book Catalog Report** - Complete inventory
2. **Circulation Report** - Issue/return statistics
3. **Overdue Report** - Books past due date
4. **Fine Collection Report** - Fines collected
5. **Member Activity Report** - Member-wise transactions
6. **Popular Books Report** - Most borrowed

## Related Files

```
university_erp/
+-- university_library/
    +-- doctype/
    |   +-- library_category/
    |   +-- library_subject/
    |   +-- library_article/
    |   +-- library_member/
    |   +-- library_transaction/
    |   +-- library_fine/
    |   +-- book_reservation/
    +-- api.py
```

## See Also

- [University Finance Module](05_UNIVERSITY_FINANCE.md)
- [University Integrations Module](14_UNIVERSITY_INTEGRATIONS.md)
- [Student Info Module](03_STUDENT_INFO.md)

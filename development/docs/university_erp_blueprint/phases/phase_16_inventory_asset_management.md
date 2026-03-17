# Phase 16: Inventory & Asset Management

## Overview
This phase implements a complete inventory and asset management system including stock management, purchase requisitions, purchase orders, supplier management, asset tracking, lab equipment management, and consumption tracking.

**Duration**: 5-6 weeks
**Priority**: Medium (Administrative Enhancement)
**Dependencies**: Phase 1 (Foundation), Phase 5 (Finance basics)

---

## Part A: Core Inventory DocTypes

### 1. Inventory Item DocType

```json
{
    "doctype": "DocType",
    "name": "Inventory Item",
    "module": "University ERP",
    "fields": [
        {
            "fieldname": "item_code",
            "fieldtype": "Data",
            "label": "Item Code",
            "reqd": 1,
            "unique": 1
        },
        {
            "fieldname": "item_name",
            "fieldtype": "Data",
            "label": "Item Name",
            "reqd": 1
        },
        {
            "fieldname": "item_group",
            "fieldtype": "Link",
            "label": "Item Group",
            "options": "Inventory Item Group",
            "reqd": 1
        },
        {
            "fieldname": "item_type",
            "fieldtype": "Select",
            "label": "Item Type",
            "options": "Stock Item\nNon-Stock Item\nService\nAsset",
            "default": "Stock Item"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "unit_of_measure",
            "fieldtype": "Link",
            "label": "Unit of Measure",
            "options": "UOM",
            "reqd": 1
        },
        {
            "fieldname": "is_active",
            "fieldtype": "Check",
            "label": "Is Active",
            "default": 1
        },
        {
            "fieldname": "image",
            "fieldtype": "Attach Image",
            "label": "Image"
        },
        {
            "fieldname": "description_section",
            "fieldtype": "Section Break",
            "label": "Description"
        },
        {
            "fieldname": "description",
            "fieldtype": "Text Editor",
            "label": "Description"
        },
        {
            "fieldname": "specifications",
            "fieldtype": "Table",
            "label": "Specifications",
            "options": "Item Specification"
        },
        {
            "fieldname": "inventory_section",
            "fieldtype": "Section Break",
            "label": "Inventory Settings"
        },
        {
            "fieldname": "maintain_stock",
            "fieldtype": "Check",
            "label": "Maintain Stock",
            "default": 1
        },
        {
            "fieldname": "default_warehouse",
            "fieldtype": "Link",
            "label": "Default Warehouse",
            "options": "Warehouse"
        },
        {
            "fieldname": "minimum_stock_level",
            "fieldtype": "Float",
            "label": "Minimum Stock Level"
        },
        {
            "fieldname": "reorder_level",
            "fieldtype": "Float",
            "label": "Reorder Level"
        },
        {
            "fieldname": "reorder_quantity",
            "fieldtype": "Float",
            "label": "Reorder Quantity"
        },
        {
            "fieldname": "column_break_inv",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "lead_time_days",
            "fieldtype": "Int",
            "label": "Lead Time (Days)"
        },
        {
            "fieldname": "shelf_life_days",
            "fieldtype": "Int",
            "label": "Shelf Life (Days)"
        },
        {
            "fieldname": "valuation_method",
            "fieldtype": "Select",
            "label": "Valuation Method",
            "options": "FIFO\nMoving Average\nLIFO",
            "default": "FIFO"
        },
        {
            "fieldname": "pricing_section",
            "fieldtype": "Section Break",
            "label": "Pricing"
        },
        {
            "fieldname": "standard_rate",
            "fieldtype": "Currency",
            "label": "Standard Rate"
        },
        {
            "fieldname": "last_purchase_rate",
            "fieldtype": "Currency",
            "label": "Last Purchase Rate",
            "read_only": 1
        },
        {
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "label": "Valuation Rate",
            "read_only": 1
        },
        {
            "fieldname": "column_break_price",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "total_stock_value",
            "fieldtype": "Currency",
            "label": "Total Stock Value",
            "read_only": 1
        },
        {
            "fieldname": "current_stock",
            "fieldtype": "Float",
            "label": "Current Stock",
            "read_only": 1
        },
        {
            "fieldname": "supplier_section",
            "fieldtype": "Section Break",
            "label": "Default Supplier"
        },
        {
            "fieldname": "default_supplier",
            "fieldtype": "Link",
            "label": "Default Supplier",
            "options": "Supplier"
        },
        {
            "fieldname": "manufacturer",
            "fieldtype": "Data",
            "label": "Manufacturer"
        },
        {
            "fieldname": "manufacturer_part_no",
            "fieldtype": "Data",
            "label": "Manufacturer Part No"
        },
        {
            "fieldname": "accounting_section",
            "fieldtype": "Section Break",
            "label": "Accounting"
        },
        {
            "fieldname": "expense_account",
            "fieldtype": "Link",
            "label": "Expense Account",
            "options": "Account"
        },
        {
            "fieldname": "inventory_account",
            "fieldtype": "Link",
            "label": "Inventory Account",
            "options": "Account"
        }
    ],
    "permissions": [
        {
            "role": "Stock Manager",
            "read": 1, "write": 1, "create": 1, "delete": 1
        },
        {
            "role": "Stock User",
            "read": 1
        }
    ]
}
```

### 2. Inventory Item Group DocType

```json
{
    "doctype": "DocType",
    "name": "Inventory Item Group",
    "module": "University ERP",
    "is_tree": 1,
    "fields": [
        {
            "fieldname": "group_name",
            "fieldtype": "Data",
            "label": "Group Name",
            "reqd": 1
        },
        {
            "fieldname": "parent_group",
            "fieldtype": "Link",
            "label": "Parent Group",
            "options": "Inventory Item Group"
        },
        {
            "fieldname": "is_group",
            "fieldtype": "Check",
            "label": "Is Group"
        },
        {
            "fieldname": "description",
            "fieldtype": "Small Text",
            "label": "Description"
        },
        {
            "fieldname": "default_expense_account",
            "fieldtype": "Link",
            "label": "Default Expense Account",
            "options": "Account"
        },
        {
            "fieldname": "default_warehouse",
            "fieldtype": "Link",
            "label": "Default Warehouse",
            "options": "Warehouse"
        }
    ]
}
```

### 3. Warehouse DocType

```json
{
    "doctype": "DocType",
    "name": "Warehouse",
    "module": "University ERP",
    "is_tree": 1,
    "fields": [
        {
            "fieldname": "warehouse_name",
            "fieldtype": "Data",
            "label": "Warehouse Name",
            "reqd": 1
        },
        {
            "fieldname": "warehouse_type",
            "fieldtype": "Select",
            "label": "Warehouse Type",
            "options": "Main Store\nDepartment Store\nLab Store\nLibrary Store\nHostel Store\nSports Store\nTransit"
        },
        {
            "fieldname": "parent_warehouse",
            "fieldtype": "Link",
            "label": "Parent Warehouse",
            "options": "Warehouse"
        },
        {
            "fieldname": "is_group",
            "fieldtype": "Check",
            "label": "Is Group"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": "Department",
            "options": "Department"
        },
        {
            "fieldname": "custodian",
            "fieldtype": "Link",
            "label": "Custodian",
            "options": "Employee"
        },
        {
            "fieldname": "is_active",
            "fieldtype": "Check",
            "label": "Is Active",
            "default": 1
        },
        {
            "fieldname": "location_section",
            "fieldtype": "Section Break",
            "label": "Location"
        },
        {
            "fieldname": "building",
            "fieldtype": "Data",
            "label": "Building"
        },
        {
            "fieldname": "floor",
            "fieldtype": "Data",
            "label": "Floor"
        },
        {
            "fieldname": "room_number",
            "fieldtype": "Data",
            "label": "Room Number"
        },
        {
            "fieldname": "address",
            "fieldtype": "Small Text",
            "label": "Address"
        },
        {
            "fieldname": "accounting_section",
            "fieldtype": "Section Break",
            "label": "Accounting"
        },
        {
            "fieldname": "account",
            "fieldtype": "Link",
            "label": "Account",
            "options": "Account"
        }
    ]
}
```

### 4. Stock Entry DocType

```json
{
    "doctype": "DocType",
    "name": "Stock Entry",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "entry_type",
            "fieldtype": "Select",
            "label": "Entry Type",
            "options": "Material Receipt\nMaterial Issue\nMaterial Transfer\nManufacture\nRepack\nOpening Stock\nStock Reconciliation",
            "reqd": 1
        },
        {
            "fieldname": "purpose",
            "fieldtype": "Data",
            "label": "Purpose"
        },
        {
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "label": "Posting Date",
            "reqd": 1,
            "default": "Today"
        },
        {
            "fieldname": "posting_time",
            "fieldtype": "Time",
            "label": "Posting Time",
            "default": "Now"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "from_warehouse",
            "fieldtype": "Link",
            "label": "From Warehouse",
            "options": "Warehouse",
            "depends_on": "eval:['Material Issue', 'Material Transfer'].includes(doc.entry_type)"
        },
        {
            "fieldname": "to_warehouse",
            "fieldtype": "Link",
            "label": "To Warehouse",
            "options": "Warehouse",
            "depends_on": "eval:['Material Receipt', 'Material Transfer', 'Opening Stock'].includes(doc.entry_type)"
        },
        {
            "fieldname": "items_section",
            "fieldtype": "Section Break",
            "label": "Items"
        },
        {
            "fieldname": "items",
            "fieldtype": "Table",
            "label": "Items",
            "options": "Stock Entry Item",
            "reqd": 1
        },
        {
            "fieldname": "totals_section",
            "fieldtype": "Section Break",
            "label": "Totals"
        },
        {
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "label": "Total Quantity",
            "read_only": 1
        },
        {
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "label": "Total Amount",
            "read_only": 1
        },
        {
            "fieldname": "column_break_totals",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "total_additional_costs",
            "fieldtype": "Currency",
            "label": "Total Additional Costs",
            "read_only": 1
        },
        {
            "fieldname": "reference_section",
            "fieldtype": "Section Break",
            "label": "Reference"
        },
        {
            "fieldname": "reference_doctype",
            "fieldtype": "Link",
            "label": "Reference Type",
            "options": "DocType"
        },
        {
            "fieldname": "reference_name",
            "fieldtype": "Dynamic Link",
            "label": "Reference Name",
            "options": "reference_doctype"
        },
        {
            "fieldname": "column_break_ref",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "purchase_order",
            "fieldtype": "Link",
            "label": "Purchase Order",
            "options": "Purchase Order",
            "depends_on": "eval:doc.entry_type=='Material Receipt'"
        },
        {
            "fieldname": "material_request",
            "fieldtype": "Link",
            "label": "Material Request",
            "options": "Material Request"
        },
        {
            "fieldname": "remarks",
            "fieldtype": "Small Text",
            "label": "Remarks"
        }
    ],
    "permissions": [
        {
            "role": "Stock Manager",
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1
        },
        {
            "role": "Stock User",
            "read": 1, "write": 1, "create": 1
        }
    ]
}
```

### 5. Stock Entry Item Child Table

```json
{
    "doctype": "DocType",
    "name": "Stock Entry Item",
    "module": "University ERP",
    "istable": 1,
    "fields": [
        {
            "fieldname": "item_code",
            "fieldtype": "Link",
            "label": "Item Code",
            "options": "Inventory Item",
            "reqd": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "item_name",
            "fieldtype": "Data",
            "label": "Item Name",
            "fetch_from": "item_code.item_name",
            "read_only": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "qty",
            "fieldtype": "Float",
            "label": "Quantity",
            "reqd": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "uom",
            "fieldtype": "Link",
            "label": "UOM",
            "options": "UOM",
            "fetch_from": "item_code.unit_of_measure"
        },
        {
            "fieldname": "rate",
            "fieldtype": "Currency",
            "label": "Rate",
            "in_list_view": 1
        },
        {
            "fieldname": "amount",
            "fieldtype": "Currency",
            "label": "Amount",
            "read_only": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "s_warehouse",
            "fieldtype": "Link",
            "label": "Source Warehouse",
            "options": "Warehouse"
        },
        {
            "fieldname": "t_warehouse",
            "fieldtype": "Link",
            "label": "Target Warehouse",
            "options": "Warehouse"
        },
        {
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "label": "Batch No",
            "options": "Batch"
        },
        {
            "fieldname": "serial_no",
            "fieldtype": "Small Text",
            "label": "Serial No"
        },
        {
            "fieldname": "expiry_date",
            "fieldtype": "Date",
            "label": "Expiry Date"
        }
    ]
}
```

---

## Part B: Purchase Management

### 1. Supplier DocType

```json
{
    "doctype": "DocType",
    "name": "Supplier",
    "module": "University ERP",
    "fields": [
        {
            "fieldname": "supplier_name",
            "fieldtype": "Data",
            "label": "Supplier Name",
            "reqd": 1
        },
        {
            "fieldname": "supplier_type",
            "fieldtype": "Select",
            "label": "Supplier Type",
            "options": "Company\nIndividual\nGovernment\nNGO"
        },
        {
            "fieldname": "supplier_group",
            "fieldtype": "Link",
            "label": "Supplier Group",
            "options": "Supplier Group"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "is_active",
            "fieldtype": "Check",
            "label": "Is Active",
            "default": 1
        },
        {
            "fieldname": "supplier_rating",
            "fieldtype": "Rating",
            "label": "Supplier Rating"
        },
        {
            "fieldname": "contact_section",
            "fieldtype": "Section Break",
            "label": "Contact Details"
        },
        {
            "fieldname": "contact_person",
            "fieldtype": "Data",
            "label": "Contact Person"
        },
        {
            "fieldname": "email",
            "fieldtype": "Data",
            "label": "Email",
            "options": "Email"
        },
        {
            "fieldname": "phone",
            "fieldtype": "Data",
            "label": "Phone"
        },
        {
            "fieldname": "mobile",
            "fieldtype": "Data",
            "label": "Mobile"
        },
        {
            "fieldname": "column_break_contact",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "website",
            "fieldtype": "Data",
            "label": "Website"
        },
        {
            "fieldname": "address",
            "fieldtype": "Small Text",
            "label": "Address"
        },
        {
            "fieldname": "city",
            "fieldtype": "Data",
            "label": "City"
        },
        {
            "fieldname": "state",
            "fieldtype": "Data",
            "label": "State"
        },
        {
            "fieldname": "pincode",
            "fieldtype": "Data",
            "label": "PIN Code"
        },
        {
            "fieldname": "tax_section",
            "fieldtype": "Section Break",
            "label": "Tax & Registration"
        },
        {
            "fieldname": "gstin",
            "fieldtype": "Data",
            "label": "GSTIN"
        },
        {
            "fieldname": "pan",
            "fieldtype": "Data",
            "label": "PAN"
        },
        {
            "fieldname": "registration_number",
            "fieldtype": "Data",
            "label": "Registration Number"
        },
        {
            "fieldname": "column_break_tax",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "tax_category",
            "fieldtype": "Link",
            "label": "Tax Category",
            "options": "Tax Category"
        },
        {
            "fieldname": "is_msme",
            "fieldtype": "Check",
            "label": "Is MSME"
        },
        {
            "fieldname": "msme_registration",
            "fieldtype": "Data",
            "label": "MSME Registration No",
            "depends_on": "is_msme"
        },
        {
            "fieldname": "bank_section",
            "fieldtype": "Section Break",
            "label": "Bank Details"
        },
        {
            "fieldname": "bank_name",
            "fieldtype": "Data",
            "label": "Bank Name"
        },
        {
            "fieldname": "bank_account",
            "fieldtype": "Data",
            "label": "Bank Account No"
        },
        {
            "fieldname": "ifsc_code",
            "fieldtype": "Data",
            "label": "IFSC Code"
        },
        {
            "fieldname": "payment_terms",
            "fieldtype": "Link",
            "label": "Default Payment Terms",
            "options": "Payment Terms Template"
        },
        {
            "fieldname": "accounting_section",
            "fieldtype": "Section Break",
            "label": "Accounting"
        },
        {
            "fieldname": "default_currency",
            "fieldtype": "Link",
            "label": "Default Currency",
            "options": "Currency",
            "default": "INR"
        },
        {
            "fieldname": "default_price_list",
            "fieldtype": "Link",
            "label": "Default Price List",
            "options": "Price List"
        },
        {
            "fieldname": "credit_limit",
            "fieldtype": "Currency",
            "label": "Credit Limit"
        }
    ],
    "permissions": [
        {
            "role": "Purchase Manager",
            "read": 1, "write": 1, "create": 1, "delete": 1
        },
        {
            "role": "Purchase User",
            "read": 1, "write": 1, "create": 1
        }
    ]
}
```

### 2. Material Request (Purchase Requisition)

```json
{
    "doctype": "DocType",
    "name": "Material Request",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "material_request_type",
            "fieldtype": "Select",
            "label": "Purpose",
            "options": "Purchase\nMaterial Transfer\nMaterial Issue\nManufacture\nCustomer Provided",
            "default": "Purchase",
            "reqd": 1
        },
        {
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "label": "Transaction Date",
            "reqd": 1,
            "default": "Today"
        },
        {
            "fieldname": "required_by",
            "fieldtype": "Date",
            "label": "Required By"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Draft\nSubmitted\nPartially Ordered\nOrdered\nIssued\nTransferred\nCancelled",
            "default": "Draft",
            "read_only": 1
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": "Department",
            "options": "Department"
        },
        {
            "fieldname": "requested_by",
            "fieldtype": "Link",
            "label": "Requested By",
            "options": "Employee"
        },
        {
            "fieldname": "items_section",
            "fieldtype": "Section Break",
            "label": "Items"
        },
        {
            "fieldname": "items",
            "fieldtype": "Table",
            "label": "Items",
            "options": "Material Request Item",
            "reqd": 1
        },
        {
            "fieldname": "reason_section",
            "fieldtype": "Section Break",
            "label": "Reason & Justification"
        },
        {
            "fieldname": "reason",
            "fieldtype": "Small Text",
            "label": "Reason for Request"
        },
        {
            "fieldname": "justification",
            "fieldtype": "Text Editor",
            "label": "Detailed Justification"
        },
        {
            "fieldname": "warehouse_section",
            "fieldtype": "Section Break",
            "label": "Warehouse"
        },
        {
            "fieldname": "set_warehouse",
            "fieldtype": "Link",
            "label": "Set Target Warehouse",
            "options": "Warehouse"
        },
        {
            "fieldname": "set_from_warehouse",
            "fieldtype": "Link",
            "label": "Set Source Warehouse",
            "options": "Warehouse",
            "depends_on": "eval:doc.material_request_type=='Material Transfer'"
        }
    ],
    "permissions": [
        {
            "role": "Purchase Manager",
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1
        },
        {
            "role": "Purchase User",
            "read": 1, "write": 1, "create": 1
        },
        {
            "role": "Employee",
            "read": 1, "write": 1, "create": 1
        }
    ]
}
```

### 3. Purchase Order DocType

```json
{
    "doctype": "DocType",
    "name": "Purchase Order",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "supplier",
            "fieldtype": "Link",
            "label": "Supplier",
            "options": "Supplier",
            "reqd": 1
        },
        {
            "fieldname": "supplier_name",
            "fieldtype": "Data",
            "label": "Supplier Name",
            "fetch_from": "supplier.supplier_name",
            "read_only": 1
        },
        {
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "label": "Date",
            "reqd": 1,
            "default": "Today"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Draft\nTo Receive and Bill\nTo Bill\nTo Receive\nCompleted\nCancelled\nClosed",
            "default": "Draft",
            "read_only": 1
        },
        {
            "fieldname": "delivery_date",
            "fieldtype": "Date",
            "label": "Required By"
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": "Department",
            "options": "Department"
        },
        {
            "fieldname": "items_section",
            "fieldtype": "Section Break",
            "label": "Items"
        },
        {
            "fieldname": "items",
            "fieldtype": "Table",
            "label": "Items",
            "options": "Purchase Order Item",
            "reqd": 1
        },
        {
            "fieldname": "pricing_section",
            "fieldtype": "Section Break",
            "label": "Pricing"
        },
        {
            "fieldname": "currency",
            "fieldtype": "Link",
            "label": "Currency",
            "options": "Currency",
            "default": "INR"
        },
        {
            "fieldname": "conversion_rate",
            "fieldtype": "Float",
            "label": "Exchange Rate",
            "default": 1
        },
        {
            "fieldname": "price_list",
            "fieldtype": "Link",
            "label": "Price List",
            "options": "Price List"
        },
        {
            "fieldname": "totals_section",
            "fieldtype": "Section Break",
            "label": "Totals"
        },
        {
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "label": "Total Quantity",
            "read_only": 1
        },
        {
            "fieldname": "total",
            "fieldtype": "Currency",
            "label": "Total",
            "read_only": 1
        },
        {
            "fieldname": "column_break_totals",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "discount_amount",
            "fieldtype": "Currency",
            "label": "Discount Amount"
        },
        {
            "fieldname": "taxes_and_charges",
            "fieldtype": "Link",
            "label": "Taxes and Charges Template",
            "options": "Purchase Taxes and Charges Template"
        },
        {
            "fieldname": "total_taxes_and_charges",
            "fieldtype": "Currency",
            "label": "Total Taxes",
            "read_only": 1
        },
        {
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "label": "Grand Total",
            "read_only": 1
        },
        {
            "fieldname": "taxes_section",
            "fieldtype": "Section Break",
            "label": "Taxes"
        },
        {
            "fieldname": "taxes",
            "fieldtype": "Table",
            "label": "Taxes",
            "options": "Purchase Taxes and Charges"
        },
        {
            "fieldname": "terms_section",
            "fieldtype": "Section Break",
            "label": "Terms & Conditions"
        },
        {
            "fieldname": "payment_terms_template",
            "fieldtype": "Link",
            "label": "Payment Terms Template",
            "options": "Payment Terms Template"
        },
        {
            "fieldname": "terms",
            "fieldtype": "Text Editor",
            "label": "Terms and Conditions"
        },
        {
            "fieldname": "reference_section",
            "fieldtype": "Section Break",
            "label": "Reference"
        },
        {
            "fieldname": "material_request",
            "fieldtype": "Link",
            "label": "Material Request",
            "options": "Material Request"
        },
        {
            "fieldname": "quotation",
            "fieldtype": "Link",
            "label": "Supplier Quotation",
            "options": "Supplier Quotation"
        }
    ],
    "permissions": [
        {
            "role": "Purchase Manager",
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1
        },
        {
            "role": "Purchase User",
            "read": 1, "write": 1, "create": 1
        }
    ]
}
```

---

## Part C: Asset Management

### 1. Asset DocType

```json
{
    "doctype": "DocType",
    "name": "Asset",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "asset_name",
            "fieldtype": "Data",
            "label": "Asset Name",
            "reqd": 1
        },
        {
            "fieldname": "asset_code",
            "fieldtype": "Data",
            "label": "Asset Code",
            "unique": 1
        },
        {
            "fieldname": "item_code",
            "fieldtype": "Link",
            "label": "Item Code",
            "options": "Inventory Item"
        },
        {
            "fieldname": "asset_category",
            "fieldtype": "Link",
            "label": "Asset Category",
            "options": "Asset Category",
            "reqd": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Draft\nSubmitted\nIn Use\nIn Maintenance\nDisposed\nScrapped",
            "default": "Draft"
        },
        {
            "fieldname": "is_existing_asset",
            "fieldtype": "Check",
            "label": "Is Existing Asset"
        },
        {
            "fieldname": "image",
            "fieldtype": "Attach Image",
            "label": "Image"
        },
        {
            "fieldname": "details_section",
            "fieldtype": "Section Break",
            "label": "Details"
        },
        {
            "fieldname": "asset_serial_no",
            "fieldtype": "Data",
            "label": "Serial Number"
        },
        {
            "fieldname": "manufacturer",
            "fieldtype": "Data",
            "label": "Manufacturer"
        },
        {
            "fieldname": "model",
            "fieldtype": "Data",
            "label": "Model"
        },
        {
            "fieldname": "column_break_details",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "purchase_date",
            "fieldtype": "Date",
            "label": "Purchase Date"
        },
        {
            "fieldname": "purchase_invoice",
            "fieldtype": "Link",
            "label": "Purchase Invoice",
            "options": "Purchase Invoice"
        },
        {
            "fieldname": "supplier",
            "fieldtype": "Link",
            "label": "Supplier",
            "options": "Supplier"
        },
        {
            "fieldname": "warranty_expiry_date",
            "fieldtype": "Date",
            "label": "Warranty Expiry Date"
        },
        {
            "fieldname": "location_section",
            "fieldtype": "Section Break",
            "label": "Location"
        },
        {
            "fieldname": "location",
            "fieldtype": "Link",
            "label": "Location",
            "options": "Warehouse"
        },
        {
            "fieldname": "department",
            "fieldtype": "Link",
            "label": "Department",
            "options": "Department"
        },
        {
            "fieldname": "custodian",
            "fieldtype": "Link",
            "label": "Custodian",
            "options": "Employee"
        },
        {
            "fieldname": "column_break_location",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "building",
            "fieldtype": "Data",
            "label": "Building"
        },
        {
            "fieldname": "floor",
            "fieldtype": "Data",
            "label": "Floor"
        },
        {
            "fieldname": "room_number",
            "fieldtype": "Data",
            "label": "Room Number"
        },
        {
            "fieldname": "finance_section",
            "fieldtype": "Section Break",
            "label": "Finance"
        },
        {
            "fieldname": "gross_purchase_amount",
            "fieldtype": "Currency",
            "label": "Gross Purchase Amount"
        },
        {
            "fieldname": "opening_accumulated_depreciation",
            "fieldtype": "Currency",
            "label": "Opening Accumulated Depreciation"
        },
        {
            "fieldname": "column_break_finance",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "asset_value",
            "fieldtype": "Currency",
            "label": "Current Value",
            "read_only": 1
        },
        {
            "fieldname": "total_depreciation",
            "fieldtype": "Currency",
            "label": "Total Depreciation",
            "read_only": 1
        },
        {
            "fieldname": "depreciation_section",
            "fieldtype": "Section Break",
            "label": "Depreciation"
        },
        {
            "fieldname": "calculate_depreciation",
            "fieldtype": "Check",
            "label": "Calculate Depreciation"
        },
        {
            "fieldname": "depreciation_method",
            "fieldtype": "Select",
            "label": "Depreciation Method",
            "options": "\nStraight Line\nDouble Declining Balance\nWritten Down Value",
            "depends_on": "calculate_depreciation"
        },
        {
            "fieldname": "total_number_of_depreciations",
            "fieldtype": "Int",
            "label": "Total Number of Depreciations",
            "depends_on": "calculate_depreciation"
        },
        {
            "fieldname": "frequency_of_depreciation",
            "fieldtype": "Int",
            "label": "Frequency of Depreciation (Months)",
            "depends_on": "calculate_depreciation"
        },
        {
            "fieldname": "column_break_dep",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "depreciation_start_date",
            "fieldtype": "Date",
            "label": "Depreciation Start Date",
            "depends_on": "calculate_depreciation"
        },
        {
            "fieldname": "expected_value_after_useful_life",
            "fieldtype": "Currency",
            "label": "Expected Value After Useful Life",
            "depends_on": "calculate_depreciation"
        },
        {
            "fieldname": "rate_of_depreciation",
            "fieldtype": "Percent",
            "label": "Rate of Depreciation",
            "depends_on": "eval:doc.depreciation_method=='Written Down Value'"
        },
        {
            "fieldname": "depreciation_schedule",
            "fieldtype": "Table",
            "label": "Depreciation Schedule",
            "options": "Depreciation Schedule",
            "depends_on": "calculate_depreciation"
        },
        {
            "fieldname": "maintenance_section",
            "fieldtype": "Section Break",
            "label": "Maintenance"
        },
        {
            "fieldname": "maintenance_required",
            "fieldtype": "Check",
            "label": "Maintenance Required"
        },
        {
            "fieldname": "next_maintenance_date",
            "fieldtype": "Date",
            "label": "Next Maintenance Due"
        },
        {
            "fieldname": "maintenance_frequency",
            "fieldtype": "Select",
            "label": "Maintenance Frequency",
            "options": "\nMonthly\nQuarterly\nHalf-yearly\nYearly"
        },
        {
            "fieldname": "accounting_section",
            "fieldtype": "Section Break",
            "label": "Accounting"
        },
        {
            "fieldname": "fixed_asset_account",
            "fieldtype": "Link",
            "label": "Fixed Asset Account",
            "options": "Account"
        },
        {
            "fieldname": "depreciation_expense_account",
            "fieldtype": "Link",
            "label": "Depreciation Expense Account",
            "options": "Account"
        },
        {
            "fieldname": "accumulated_depreciation_account",
            "fieldtype": "Link",
            "label": "Accumulated Depreciation Account",
            "options": "Account"
        }
    ],
    "permissions": [
        {
            "role": "Asset Manager",
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1
        },
        {
            "role": "Asset User",
            "read": 1
        }
    ]
}
```

### 2. Asset Movement DocType

```json
{
    "doctype": "DocType",
    "name": "Asset Movement",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "purpose",
            "fieldtype": "Select",
            "label": "Purpose",
            "options": "Transfer\nIssue\nReceipt",
            "reqd": 1
        },
        {
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "label": "Transaction Date",
            "reqd": 1,
            "default": "Today"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "reference_doctype",
            "fieldtype": "Link",
            "label": "Reference Type",
            "options": "DocType"
        },
        {
            "fieldname": "reference_name",
            "fieldtype": "Dynamic Link",
            "label": "Reference Name",
            "options": "reference_doctype"
        },
        {
            "fieldname": "assets_section",
            "fieldtype": "Section Break",
            "label": "Assets"
        },
        {
            "fieldname": "assets",
            "fieldtype": "Table",
            "label": "Assets",
            "options": "Asset Movement Item",
            "reqd": 1
        },
        {
            "fieldname": "remarks",
            "fieldtype": "Small Text",
            "label": "Remarks"
        }
    ]
}
```

### 3. Asset Maintenance DocType

```json
{
    "doctype": "DocType",
    "name": "Asset Maintenance",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "asset",
            "fieldtype": "Link",
            "label": "Asset",
            "options": "Asset",
            "reqd": 1
        },
        {
            "fieldname": "asset_name",
            "fieldtype": "Data",
            "label": "Asset Name",
            "fetch_from": "asset.asset_name",
            "read_only": 1
        },
        {
            "fieldname": "maintenance_type",
            "fieldtype": "Select",
            "label": "Maintenance Type",
            "options": "Preventive\nCorrective\nEmergency\nCalibration",
            "reqd": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "maintenance_status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Planned\nIn Progress\nCompleted\nCancelled",
            "default": "Planned"
        },
        {
            "fieldname": "priority",
            "fieldtype": "Select",
            "label": "Priority",
            "options": "Low\nMedium\nHigh\nUrgent"
        },
        {
            "fieldname": "schedule_section",
            "fieldtype": "Section Break",
            "label": "Schedule"
        },
        {
            "fieldname": "planned_date",
            "fieldtype": "Date",
            "label": "Planned Date",
            "reqd": 1
        },
        {
            "fieldname": "completion_date",
            "fieldtype": "Date",
            "label": "Completion Date"
        },
        {
            "fieldname": "column_break_schedule",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "assigned_to",
            "fieldtype": "Link",
            "label": "Assigned To",
            "options": "Employee"
        },
        {
            "fieldname": "maintenance_team",
            "fieldtype": "Link",
            "label": "Maintenance Team",
            "options": "Maintenance Team"
        },
        {
            "fieldname": "details_section",
            "fieldtype": "Section Break",
            "label": "Details"
        },
        {
            "fieldname": "description",
            "fieldtype": "Small Text",
            "label": "Issue Description"
        },
        {
            "fieldname": "work_done",
            "fieldtype": "Text Editor",
            "label": "Work Done"
        },
        {
            "fieldname": "parts_replaced",
            "fieldtype": "Table",
            "label": "Parts Replaced",
            "options": "Asset Maintenance Part"
        },
        {
            "fieldname": "cost_section",
            "fieldtype": "Section Break",
            "label": "Cost"
        },
        {
            "fieldname": "labor_cost",
            "fieldtype": "Currency",
            "label": "Labor Cost"
        },
        {
            "fieldname": "parts_cost",
            "fieldtype": "Currency",
            "label": "Parts Cost"
        },
        {
            "fieldname": "column_break_cost",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "other_cost",
            "fieldtype": "Currency",
            "label": "Other Cost"
        },
        {
            "fieldname": "total_cost",
            "fieldtype": "Currency",
            "label": "Total Cost",
            "read_only": 1
        }
    ]
}
```

---

## Part D: Lab Equipment Management

### 1. Lab Equipment DocType

```json
{
    "doctype": "DocType",
    "name": "Lab Equipment",
    "module": "University ERP",
    "fields": [
        {
            "fieldname": "equipment_name",
            "fieldtype": "Data",
            "label": "Equipment Name",
            "reqd": 1
        },
        {
            "fieldname": "equipment_code",
            "fieldtype": "Data",
            "label": "Equipment Code",
            "unique": 1
        },
        {
            "fieldname": "asset",
            "fieldtype": "Link",
            "label": "Linked Asset",
            "options": "Asset"
        },
        {
            "fieldname": "equipment_type",
            "fieldtype": "Select",
            "label": "Equipment Type",
            "options": "Scientific\nComputing\nElectrical\nMechanical\nChemical\nBiological\nGeneral",
            "reqd": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Available\nIn Use\nUnder Maintenance\nOut of Order\nDecommissioned",
            "default": "Available"
        },
        {
            "fieldname": "lab",
            "fieldtype": "Link",
            "label": "Lab",
            "options": "University Laboratory",
            "reqd": 1
        },
        {
            "fieldname": "details_section",
            "fieldtype": "Section Break",
            "label": "Equipment Details"
        },
        {
            "fieldname": "manufacturer",
            "fieldtype": "Data",
            "label": "Manufacturer"
        },
        {
            "fieldname": "model",
            "fieldtype": "Data",
            "label": "Model"
        },
        {
            "fieldname": "serial_number",
            "fieldtype": "Data",
            "label": "Serial Number"
        },
        {
            "fieldname": "purchase_date",
            "fieldtype": "Date",
            "label": "Purchase Date"
        },
        {
            "fieldname": "column_break_details",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "warranty_end",
            "fieldtype": "Date",
            "label": "Warranty End Date"
        },
        {
            "fieldname": "purchase_value",
            "fieldtype": "Currency",
            "label": "Purchase Value"
        },
        {
            "fieldname": "current_value",
            "fieldtype": "Currency",
            "label": "Current Value"
        },
        {
            "fieldname": "calibration_section",
            "fieldtype": "Section Break",
            "label": "Calibration",
            "description": "For equipment requiring periodic calibration"
        },
        {
            "fieldname": "requires_calibration",
            "fieldtype": "Check",
            "label": "Requires Calibration"
        },
        {
            "fieldname": "calibration_frequency",
            "fieldtype": "Select",
            "label": "Calibration Frequency",
            "options": "\nMonthly\nQuarterly\nHalf-yearly\nYearly",
            "depends_on": "requires_calibration"
        },
        {
            "fieldname": "last_calibration_date",
            "fieldtype": "Date",
            "label": "Last Calibration Date",
            "depends_on": "requires_calibration"
        },
        {
            "fieldname": "next_calibration_date",
            "fieldtype": "Date",
            "label": "Next Calibration Due",
            "depends_on": "requires_calibration"
        },
        {
            "fieldname": "calibration_certificate",
            "fieldtype": "Attach",
            "label": "Calibration Certificate",
            "depends_on": "requires_calibration"
        },
        {
            "fieldname": "safety_section",
            "fieldtype": "Section Break",
            "label": "Safety Information"
        },
        {
            "fieldname": "safety_precautions",
            "fieldtype": "Small Text",
            "label": "Safety Precautions"
        },
        {
            "fieldname": "operating_instructions",
            "fieldtype": "Text Editor",
            "label": "Operating Instructions"
        },
        {
            "fieldname": "requires_training",
            "fieldtype": "Check",
            "label": "Requires User Training"
        },
        {
            "fieldname": "usage_section",
            "fieldtype": "Section Break",
            "label": "Usage Tracking"
        },
        {
            "fieldname": "total_usage_hours",
            "fieldtype": "Float",
            "label": "Total Usage Hours",
            "read_only": 1
        },
        {
            "fieldname": "max_usage_hours",
            "fieldtype": "Float",
            "label": "Max Usage Hours per Day"
        },
        {
            "fieldname": "booking_required",
            "fieldtype": "Check",
            "label": "Booking Required",
            "description": "Users must book this equipment in advance"
        }
    ]
}
```

### 2. Lab Equipment Booking

```json
{
    "doctype": "DocType",
    "name": "Lab Equipment Booking",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "equipment",
            "fieldtype": "Link",
            "label": "Equipment",
            "options": "Lab Equipment",
            "reqd": 1
        },
        {
            "fieldname": "equipment_name",
            "fieldtype": "Data",
            "label": "Equipment Name",
            "fetch_from": "equipment.equipment_name",
            "read_only": 1
        },
        {
            "fieldname": "booked_by",
            "fieldtype": "Link",
            "label": "Booked By",
            "options": "User",
            "reqd": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Pending\nApproved\nIn Use\nCompleted\nCancelled",
            "default": "Pending"
        },
        {
            "fieldname": "purpose",
            "fieldtype": "Select",
            "label": "Purpose",
            "options": "Research\nTeaching\nProject Work\nExperiment\nCalibration\nOther",
            "reqd": 1
        },
        {
            "fieldname": "schedule_section",
            "fieldtype": "Section Break",
            "label": "Schedule"
        },
        {
            "fieldname": "booking_date",
            "fieldtype": "Date",
            "label": "Booking Date",
            "reqd": 1
        },
        {
            "fieldname": "start_time",
            "fieldtype": "Time",
            "label": "Start Time",
            "reqd": 1
        },
        {
            "fieldname": "end_time",
            "fieldtype": "Time",
            "label": "End Time",
            "reqd": 1
        },
        {
            "fieldname": "column_break_schedule",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "actual_start_time",
            "fieldtype": "Datetime",
            "label": "Actual Start Time"
        },
        {
            "fieldname": "actual_end_time",
            "fieldtype": "Datetime",
            "label": "Actual End Time"
        },
        {
            "fieldname": "duration_hours",
            "fieldtype": "Float",
            "label": "Duration (Hours)",
            "read_only": 1
        },
        {
            "fieldname": "details_section",
            "fieldtype": "Section Break",
            "label": "Details"
        },
        {
            "fieldname": "project",
            "fieldtype": "Link",
            "label": "Research Project",
            "options": "Research Project"
        },
        {
            "fieldname": "course",
            "fieldtype": "Link",
            "label": "Course",
            "options": "Course"
        },
        {
            "fieldname": "experiment_details",
            "fieldtype": "Small Text",
            "label": "Experiment/Work Details"
        },
        {
            "fieldname": "approval_section",
            "fieldtype": "Section Break",
            "label": "Approval"
        },
        {
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "label": "Approved By",
            "options": "User"
        },
        {
            "fieldname": "approval_date",
            "fieldtype": "Date",
            "label": "Approval Date"
        },
        {
            "fieldname": "remarks",
            "fieldtype": "Small Text",
            "label": "Remarks"
        }
    ]
}
```

---

## Part E: Inventory Manager Class

```python
# inventory_manager.py

import frappe
from frappe import _
from frappe.utils import flt, nowdate, add_days


class InventoryManager:
    """Manage inventory operations"""

    @staticmethod
    def get_stock_balance(item_code, warehouse=None):
        """Get current stock balance for an item"""
        filters = {"item_code": item_code}
        if warehouse:
            filters["warehouse"] = warehouse

        stock = frappe.db.sql("""
            SELECT
                SUM(actual_qty) as qty,
                SUM(stock_value) as value
            FROM `tabStock Ledger Entry`
            WHERE item_code = %(item_code)s
            {warehouse_filter}
            AND is_cancelled = 0
        """.format(
            warehouse_filter="AND warehouse = %(warehouse)s" if warehouse else ""
        ), filters, as_dict=True)

        return {
            "qty": flt(stock[0].qty) if stock else 0,
            "value": flt(stock[0].value) if stock else 0
        }

    @staticmethod
    def get_low_stock_items(warehouse=None):
        """Get items below reorder level"""
        filters = {}
        if warehouse:
            filters["default_warehouse"] = warehouse

        items = frappe.get_all(
            "Inventory Item",
            filters=filters,
            fields=["item_code", "item_name", "reorder_level", "minimum_stock_level", "default_warehouse"]
        )

        low_stock = []
        for item in items:
            if item.reorder_level:
                balance = InventoryManager.get_stock_balance(item.item_code, item.default_warehouse)
                if balance["qty"] <= item.reorder_level:
                    item["current_stock"] = balance["qty"]
                    item["stock_status"] = "Critical" if balance["qty"] <= item.minimum_stock_level else "Low"
                    low_stock.append(item)

        return low_stock

    @staticmethod
    def create_stock_entry(entry_type, items, from_warehouse=None, to_warehouse=None, posting_date=None):
        """Create a stock entry"""
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "entry_type": entry_type,
            "posting_date": posting_date or nowdate(),
            "from_warehouse": from_warehouse,
            "to_warehouse": to_warehouse,
            "items": items
        })
        stock_entry.insert()
        return stock_entry

    @staticmethod
    def process_material_receipt(purchase_order):
        """Create stock entry from purchase order receipt"""
        po = frappe.get_doc("Purchase Order", purchase_order)

        items = []
        for item in po.items:
            items.append({
                "item_code": item.item_code,
                "qty": item.qty - item.received_qty,
                "rate": item.rate,
                "t_warehouse": item.warehouse
            })

        if items:
            stock_entry = InventoryManager.create_stock_entry(
                "Material Receipt",
                items,
                to_warehouse=po.set_warehouse
            )
            stock_entry.purchase_order = purchase_order
            stock_entry.save()
            return stock_entry

    @staticmethod
    def process_material_issue(material_request):
        """Create stock entry for material issue"""
        mr = frappe.get_doc("Material Request", material_request)

        items = []
        for item in mr.items:
            items.append({
                "item_code": item.item_code,
                "qty": item.qty,
                "s_warehouse": item.warehouse
            })

        if items:
            stock_entry = InventoryManager.create_stock_entry(
                "Material Issue",
                items,
                from_warehouse=mr.set_from_warehouse
            )
            stock_entry.material_request = material_request
            stock_entry.save()
            return stock_entry

    @staticmethod
    def get_stock_ledger(item_code=None, warehouse=None, from_date=None, to_date=None):
        """Get stock ledger entries"""
        conditions = ["sle.is_cancelled = 0"]
        values = {}

        if item_code:
            conditions.append("sle.item_code = %(item_code)s")
            values["item_code"] = item_code

        if warehouse:
            conditions.append("sle.warehouse = %(warehouse)s")
            values["warehouse"] = warehouse

        if from_date:
            conditions.append("sle.posting_date >= %(from_date)s")
            values["from_date"] = from_date

        if to_date:
            conditions.append("sle.posting_date <= %(to_date)s")
            values["to_date"] = to_date

        return frappe.db.sql("""
            SELECT
                sle.posting_date,
                sle.item_code,
                sle.warehouse,
                sle.actual_qty,
                sle.qty_after_transaction,
                sle.incoming_rate,
                sle.valuation_rate,
                sle.stock_value,
                sle.voucher_type,
                sle.voucher_no
            FROM `tabStock Ledger Entry` sle
            WHERE {conditions}
            ORDER BY sle.posting_date DESC, sle.creation DESC
        """.format(conditions=" AND ".join(conditions)), values, as_dict=True)

    @staticmethod
    def get_stock_summary_report(warehouse=None):
        """Get stock summary by item"""
        warehouse_filter = ""
        if warehouse:
            warehouse_filter = f"AND sle.warehouse = '{warehouse}'"

        return frappe.db.sql("""
            SELECT
                sle.item_code,
                i.item_name,
                i.item_group,
                SUM(sle.actual_qty) as current_qty,
                SUM(sle.stock_value) as stock_value,
                i.reorder_level,
                i.minimum_stock_level,
                CASE
                    WHEN SUM(sle.actual_qty) <= i.minimum_stock_level THEN 'Critical'
                    WHEN SUM(sle.actual_qty) <= i.reorder_level THEN 'Low'
                    ELSE 'Normal'
                END as stock_status
            FROM `tabStock Ledger Entry` sle
            JOIN `tabInventory Item` i ON i.item_code = sle.item_code
            WHERE sle.is_cancelled = 0
            {warehouse_filter}
            GROUP BY sle.item_code
            ORDER BY i.item_name
        """.format(warehouse_filter=warehouse_filter), as_dict=True)

    @staticmethod
    def auto_create_material_request():
        """Auto-create material requests for items below reorder level"""
        low_stock_items = InventoryManager.get_low_stock_items()

        if not low_stock_items:
            return

        # Group by warehouse
        warehouse_items = {}
        for item in low_stock_items:
            warehouse = item.default_warehouse or "Main Store"
            if warehouse not in warehouse_items:
                warehouse_items[warehouse] = []

            warehouse_items[warehouse].append({
                "item_code": item.item_code,
                "qty": item.reorder_level - item.current_stock,
                "warehouse": warehouse
            })

        # Create material requests
        created = []
        for warehouse, items in warehouse_items.items():
            mr = frappe.get_doc({
                "doctype": "Material Request",
                "material_request_type": "Purchase",
                "transaction_date": nowdate(),
                "set_warehouse": warehouse,
                "reason": "Auto-generated for low stock items",
                "items": items
            })
            mr.insert()
            created.append(mr.name)

        return created


# Stock Ledger Entry (created automatically)
def create_stock_ledger_entry(stock_entry, item, warehouse_field):
    """Create stock ledger entry for stock movements"""
    sle = frappe.get_doc({
        "doctype": "Stock Ledger Entry",
        "item_code": item.item_code,
        "warehouse": item.get(warehouse_field),
        "posting_date": stock_entry.posting_date,
        "posting_time": stock_entry.posting_time,
        "voucher_type": "Stock Entry",
        "voucher_no": stock_entry.name,
        "actual_qty": item.qty if warehouse_field == "t_warehouse" else -item.qty,
        "incoming_rate": item.rate if warehouse_field == "t_warehouse" else 0,
        "valuation_rate": item.rate,
        "stock_value": item.amount if warehouse_field == "t_warehouse" else -item.amount
    })
    sle.insert()
    return sle
```

---

## Part F: Reports

### 1. Stock Balance Report

```python
# reports/stock_balance/stock_balance.py

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Inventory Item", "width": 120},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Inventory Item Group", "width": 120},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 100},
        {"label": _("In Qty"), "fieldname": "in_qty", "fieldtype": "Float", "width": 80},
        {"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Float", "width": 80},
        {"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Valuation Rate"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Balance Value"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 120},
        {"label": _("Reorder Level"), "fieldname": "reorder_level", "fieldtype": "Float", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80}
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("item_code"):
        conditions.append("sle.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")

    if filters.get("warehouse"):
        conditions.append("sle.warehouse = %(warehouse)s")
        values["warehouse"] = filters.get("warehouse")

    if filters.get("item_group"):
        conditions.append("i.item_group = %(item_group)s")
        values["item_group"] = filters.get("item_group")

    values["from_date"] = filters.get("from_date")
    values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    data = frappe.db.sql("""
        SELECT
            sle.item_code,
            i.item_name,
            i.item_group,
            sle.warehouse,
            SUM(CASE WHEN sle.posting_date < %(from_date)s THEN sle.actual_qty ELSE 0 END) as opening_qty,
            SUM(CASE WHEN sle.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) as in_qty,
            SUM(CASE WHEN sle.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sle.actual_qty < 0 THEN ABS(sle.actual_qty) ELSE 0 END) as out_qty,
            SUM(sle.actual_qty) as bal_qty,
            AVG(sle.valuation_rate) as val_rate,
            SUM(sle.stock_value) as bal_val,
            i.reorder_level
        FROM `tabStock Ledger Entry` sle
        JOIN `tabInventory Item` i ON i.item_code = sle.item_code
        WHERE sle.is_cancelled = 0 AND {where_clause}
        GROUP BY sle.item_code, sle.warehouse
        ORDER BY i.item_name
    """.format(where_clause=where_clause), values, as_dict=True)

    # Add status
    for row in data:
        if row.reorder_level and row.bal_qty <= row.reorder_level:
            row["status"] = "Low Stock"
        else:
            row["status"] = "OK"

    return data
```

---

## Implementation Checklist

### Phase 16 Tasks

- [x] **Week 1: Core Inventory Setup** ✅
  - [x] Create Inventory Item DocType
  - [x] Create Item Group DocType
  - [x] Create Warehouse DocType
  - [x] Create UOM DocType
  - [ ] Setup default data

- [x] **Week 2: Stock Entries** ✅
  - [x] Create Stock Entry DocType
  - [x] Create Stock Ledger Entry DocType
  - [x] Implement stock movements
  - [ ] Build valuation logic

- [x] **Week 3: Purchase Management** ✅
  - [x] Create Supplier DocType
  - [x] Create Material Request DocType
  - [x] Create Purchase Order DocType
  - [ ] Build purchase workflow

- [ ] **Week 4: Asset Management**
  - [ ] Create Asset DocType
  - [ ] Create Asset Category DocType
  - [ ] Implement depreciation
  - [ ] Build asset movement

- [ ] **Week 5: Lab Equipment**
  - [ ] Create Lab Equipment DocType
  - [ ] Create Equipment Booking DocType
  - [ ] Build calibration tracking
  - [ ] Create usage reports

- [ ] **Week 6: Reports & Testing**
  - [ ] Build stock reports
  - [ ] Create asset reports
  - [ ] Integration testing
  - [ ] Documentation

---

## Implementation Status

### Completed Components (31%)

#### Core Inventory DocTypes ✅
- Inventory Item Group DocType (Tree Structure)
- Warehouse DocType (Tree Structure)
- Item Specification (Child Table)
- Inventory Item DocType
- Batch DocType
- UOM DocType (already existed)

#### Stock Management DocTypes ✅
- Stock Entry Item (Child Table)
- Stock Entry DocType (Submittable)
- Stock Ledger Entry DocType

#### Purchase Management DocTypes ✅
- Supplier Group DocType (Tree Structure)
- Supplier DocType
- Material Request Item (Child Table)
- Material Request DocType (Submittable)
- Purchase Order Item (Child Table)
- Purchase Taxes and Charges (Child Table)
- Purchase Order DocType (Submittable)

### Pending Components (69%)

- Stock Reconciliation DocType
- Purchase Receipt DocType
- Asset Category DocType
- Asset DocType
- Asset Movement DocType
- Asset Maintenance DocType
- Lab Equipment DocType
- Lab Equipment Booking DocType
- Inventory Manager Class
- Asset Manager Class
- Reports
- Workspace
- Fixtures & Default Data
- Unit Tests

### Files Created

See [PHASE16_TASKS.md](./tasklist/PHASE16_TASKS.md) for complete file listing.

---

**Document Version:** 1.1
**Created:** January 2026
**Updated:** January 2026 (Implementation Status Added - 31%)
**Author:** University ERP Team

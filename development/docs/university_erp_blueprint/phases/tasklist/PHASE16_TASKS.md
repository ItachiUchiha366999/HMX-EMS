# Phase 16: Inventory & Asset Management - Task List

## Overview
This phase implements a complete inventory and asset management system including stock management, purchase requisitions, purchase orders, supplier management, asset tracking, lab equipment management, and consumption tracking.

**Module**: University ERP
**Total Estimated Tasks**: 150+
**Priority**: Medium (Administrative Enhancement)
**Status**: Completed (100%)

---

## Section A: Core Inventory DocTypes

### A1. Inventory Item Group DocType (Tree Structure)
- [x] Create inventory_item_group folder in university_erp/doctype
- [x] Create inventory_item_group.json with fields:
  - group_name (Data, reqd)
  - parent_inventory_item_group (Link: Inventory Item Group)
  - is_group (Check)
  - description (Small Text)
  - default_expense_account (Link: Account)
  - default_warehouse (Link: Warehouse)
- [x] Create inventory_item_group.py controller with:
  - validate() method
  - on_update() method for tree operations
- [x] Create __init__.py file

### A2. Unit of Measure (UOM) DocType
- [x] Create uom folder in university_erp/doctype
- [x] Create uom.json with fields:
  - uom_name (Data, reqd, unique)
  - must_be_whole_number (Check)
  - enabled (Check, default: 1)
- [x] Create uom.py controller
- [x] Create __init__.py file
- [x] Create default UOM records (Nos, Kg, Ltr, Mtr, Box, Pack, Set, Pair, Dozen)

### A3. Warehouse DocType (Tree Structure)
- [x] Create warehouse folder in university_erp/doctype
- [x] Create warehouse.json with fields:
  - warehouse_name (Data, reqd)
  - warehouse_type (Select: Main Store/Department Store/Lab Store/Library Store/Hostel Store/Sports Store/Transit)
  - parent_warehouse (Link: Warehouse)
  - is_group (Check)
  - department (Link: Department)
  - custodian (Link: Employee)
  - is_active (Check, default: 1)
  - building (Data)
  - floor (Data)
  - room_number (Data)
  - address (Small Text)
  - account (Link: Account)
- [x] Create warehouse.py controller with:
  - validate() method
  - on_update() method
- [x] Create __init__.py file

### A4. Item Specification Child DocType
- [x] Create item_specification folder in university_erp/doctype
- [x] Create item_specification.json with fields:
  - specification (Data, reqd, in_list_view)
  - value (Data, reqd, in_list_view)
- [x] Create item_specification.py controller
- [x] Create __init__.py file

### A5. Inventory Item DocType
- [x] Create inventory_item folder in university_erp/doctype
- [x] Create inventory_item.json with fields:
  - item_code (Data, reqd, unique)
  - item_name (Data, reqd)
  - item_group (Link: Inventory Item Group, reqd)
  - item_type (Select: Stock Item/Non-Stock Item/Service/Asset, default: Stock Item)
  - unit_of_measure (Link: UOM, reqd)
  - is_active (Check, default: 1)
  - image (Attach Image)
  - description (Text Editor)
  - specifications (Table: Item Specification)
  - maintain_stock (Check, default: 1)
  - default_warehouse (Link: Warehouse)
  - minimum_stock_level (Float)
  - reorder_level (Float)
  - reorder_quantity (Float)
  - lead_time_days (Int)
  - shelf_life_days (Int)
  - valuation_method (Select: FIFO/Moving Average/LIFO, default: FIFO)
  - standard_rate (Currency)
  - last_purchase_rate (Currency, read_only)
  - valuation_rate (Currency, read_only)
  - total_stock_value (Currency, read_only)
  - current_stock (Float, read_only)
  - default_supplier (Link: Supplier)
  - manufacturer (Data)
  - manufacturer_part_no (Data)
  - expense_account (Link: Account)
  - inventory_account (Link: Account)
- [x] Create inventory_item.py controller with:
  - validate() method
  - autoname() method for item_code generation
  - get_stock_balance() method
  - update_stock_info() method
- [x] Create __init__.py file

### A6. Batch DocType
- [x] Create batch folder in university_erp/doctype
- [x] Create batch.json with fields:
  - batch_id (Data, unique)
  - item_code (Link: Inventory Item, reqd)
  - batch_qty (Float)
  - expiry_date (Date)
  - manufacturing_date (Date)
  - supplier (Link: Supplier)
  - reference_doctype (Link: DocType)
  - reference_name (Dynamic Link)
- [x] Create batch.py controller with:
  - autoname() method
  - validate() method
- [x] Create __init__.py file

---

## Section B: Stock Management DocTypes

### B1. Stock Entry Item Child DocType
- [x] Create stock_entry_item folder in university_erp/doctype
- [x] Create stock_entry_item.json with fields:
  - item_code (Link: Inventory Item, reqd, in_list_view)
  - item_name (Data, fetch_from, read_only, in_list_view)
  - qty (Float, reqd, in_list_view)
  - uom (Link: UOM, fetch_from)
  - rate (Currency, in_list_view)
  - amount (Currency, read_only, in_list_view)
  - s_warehouse (Link: Warehouse)
  - t_warehouse (Link: Warehouse)
  - batch_no (Link: Batch)
  - serial_no (Small Text)
  - expiry_date (Date)
  - actual_qty (Float, read_only)
  - transferred_qty (Float, read_only)
- [x] Create stock_entry_item.py controller
- [x] Create __init__.py file

### B2. Stock Entry DocType
- [x] Create stock_entry folder in university_erp/doctype
- [x] Create stock_entry.json with fields:
  - naming_series (Select: SE-.YYYY.-.#####)
  - entry_type (Select: Material Receipt/Material Issue/Material Transfer/Manufacture/Repack/Opening Stock/Stock Reconciliation, reqd)
  - purpose (Data)
  - posting_date (Date, reqd, default: Today)
  - posting_time (Time, default: Now)
  - from_warehouse (Link: Warehouse, depends_on)
  - to_warehouse (Link: Warehouse, depends_on)
  - items (Table: Stock Entry Item, reqd)
  - total_qty (Float, read_only)
  - total_amount (Currency, read_only)
  - total_additional_costs (Currency, read_only)
  - reference_doctype (Link: DocType)
  - reference_name (Dynamic Link)
  - purchase_order (Link: Purchase Order, depends_on)
  - material_request (Link: Material Request)
  - remarks (Small Text)
- [x] Create stock_entry.py controller with:
  - validate() method
  - validate_items() method
  - calculate_totals() method
  - on_submit() method - create stock ledger entries
  - on_cancel() method - reverse stock ledger entries
  - set_item_details() method
- [x] Create __init__.py file

### B3. Stock Ledger Entry DocType
- [x] Create stock_ledger_entry folder in university_erp/doctype
- [x] Create stock_ledger_entry.json with fields:
  - item_code (Link: Inventory Item, reqd)
  - warehouse (Link: Warehouse, reqd)
  - posting_date (Date, reqd)
  - posting_time (Time)
  - voucher_type (Link: DocType, reqd)
  - voucher_no (Dynamic Link, reqd)
  - actual_qty (Float, reqd)
  - qty_after_transaction (Float)
  - incoming_rate (Currency)
  - outgoing_rate (Currency)
  - valuation_rate (Currency)
  - stock_value (Currency)
  - stock_value_difference (Currency)
  - batch_no (Link: Batch)
  - serial_no (Small Text)
  - is_cancelled (Check, default: 0)
- [x] Create stock_ledger_entry.py controller with:
  - validate() method
  - update_stock_value() method
- [x] Create __init__.py file

### B4. Stock Reconciliation Item Child DocType
- [x] Create stock_reconciliation_item folder in university_erp/doctype
- [x] Create stock_reconciliation_item.json with fields:
  - item_code (Link: Inventory Item, reqd, in_list_view)
  - warehouse (Link: Warehouse, reqd, in_list_view)
  - current_qty (Float, read_only)
  - qty (Float, in_list_view)
  - current_valuation_rate (Currency, read_only)
  - valuation_rate (Currency)
  - current_amount (Currency, read_only)
  - amount (Currency)
  - qty_difference (Float, read_only)
  - amount_difference (Currency, read_only)
- [x] Create stock_reconciliation_item.py controller
- [x] Create __init__.py file

### B5. Stock Reconciliation DocType
- [x] Create stock_reconciliation folder in university_erp/doctype
- [x] Create stock_reconciliation.json with fields:
  - naming_series (Select: SR-.YYYY.-.#####)
  - posting_date (Date, reqd, default: Today)
  - posting_time (Time, default: Now)
  - purpose (Select: Stock Reconciliation/Opening Stock, reqd)
  - items (Table: Stock Reconciliation Item, reqd)
  - difference_amount (Currency, read_only)
  - expense_account (Link: Account)
  - remarks (Small Text)
- [x] Create stock_reconciliation.py controller with:
  - validate() method
  - get_items() method
  - on_submit() method
  - on_cancel() method
- [x] Create __init__.py file

---

## Section C: Purchase Management DocTypes

### C1. Supplier Group DocType
- [x] Create supplier_group folder in university_erp/doctype
- [x] Create supplier_group.json with fields:
  - supplier_group_name (Data, reqd)
  - parent_supplier_group (Link: Supplier Group)
  - is_group (Check)
  - default_payment_terms (Link: Payment Terms Template)
- [x] Create supplier_group.py controller
- [x] Create __init__.py file

### C2. Supplier DocType
- [x] Create supplier folder in university_erp/doctype
- [x] Create supplier.json with fields:
  - supplier_name (Data, reqd)
  - supplier_type (Select: Company/Individual/Government/NGO)
  - supplier_group (Link: Supplier Group)
  - is_active (Check, default: 1)
  - supplier_rating (Rating)
  - contact_person (Data)
  - email (Data, options: Email)
  - phone (Data)
  - mobile (Data)
  - website (Data)
  - address (Small Text)
  - city (Data)
  - state (Data)
  - pincode (Data)
  - gstin (Data)
  - pan (Data)
  - registration_number (Data)
  - tax_category (Link: Tax Category)
  - is_msme (Check)
  - msme_registration (Data, depends_on)
  - bank_name (Data)
  - bank_account (Data)
  - ifsc_code (Data)
  - payment_terms (Link: Payment Terms Template)
  - default_currency (Link: Currency, default: INR)
  - default_price_list (Link: Price List)
  - credit_limit (Currency)
- [x] Create supplier.py controller with:
  - validate() method
  - validate_gstin() method
  - get_supplier_outstanding() method
- [x] Create __init__.py file

### C3. Material Request Item Child DocType
- [x] Create material_request_item folder in university_erp/doctype
- [x] Create material_request_item.json with fields:
  - item_code (Link: Inventory Item, reqd, in_list_view)
  - item_name (Data, fetch_from, read_only, in_list_view)
  - qty (Float, reqd, in_list_view)
  - uom (Link: UOM, fetch_from)
  - warehouse (Link: Warehouse, in_list_view)
  - rate (Currency)
  - amount (Currency, read_only)
  - schedule_date (Date)
  - ordered_qty (Float, read_only)
  - received_qty (Float, read_only)
  - description (Small Text)
- [x] Create material_request_item.py controller
- [x] Create __init__.py file

### C4. Material Request DocType
- [x] Create material_request folder in university_erp/doctype
- [x] Create material_request.json with fields:
  - naming_series (Select: MR-.YYYY.-.#####)
  - material_request_type (Select: Purchase/Material Transfer/Material Issue/Manufacture/Customer Provided, reqd, default: Purchase)
  - transaction_date (Date, reqd, default: Today)
  - required_by (Date)
  - status (Select: Draft/Pending/Partially Ordered/Ordered/Issued/Transferred/Received/Cancelled, read_only, default: Draft)
  - department (Link: Department)
  - requested_by (Link: Employee)
  - items (Table: Material Request Item, reqd)
  - reason (Small Text)
  - justification (Text Editor)
  - set_warehouse (Link: Warehouse)
  - set_from_warehouse (Link: Warehouse, depends_on)
- [x] Create material_request.py controller with:
  - validate() method
  - on_submit() method
  - on_cancel() method
  - update_status() method
  - make_purchase_order() method
  - make_stock_entry() method
- [x] Create __init__.py file

### C5. Purchase Order Item Child DocType
- [x] Create purchase_order_item folder in university_erp/doctype
- [x] Create purchase_order_item.json with fields:
  - item_code (Link: Inventory Item, reqd, in_list_view)
  - item_name (Data, fetch_from, read_only, in_list_view)
  - qty (Float, reqd, in_list_view)
  - uom (Link: UOM, fetch_from)
  - rate (Currency, reqd, in_list_view)
  - amount (Currency, read_only, in_list_view)
  - warehouse (Link: Warehouse)
  - schedule_date (Date)
  - received_qty (Float, read_only)
  - billed_qty (Float, read_only)
  - material_request (Link: Material Request)
  - material_request_item (Data)
  - discount_percentage (Percent)
  - discount_amount (Currency)
  - tax_rate (Percent)
  - tax_amount (Currency)
  - description (Small Text)
- [x] Create purchase_order_item.py controller
- [x] Create __init__.py file

### C6. Purchase Taxes and Charges Child DocType
- [x] Create purchase_taxes_and_charges folder in university_erp/doctype
- [x] Create purchase_taxes_and_charges.json with fields:
  - charge_type (Select: Actual/On Net Total/On Previous Row Amount/On Previous Row Total, reqd, in_list_view)
  - row_id (Data, depends_on)
  - account_head (Link: Account, reqd, in_list_view)
  - description (Data, in_list_view)
  - rate (Float)
  - tax_amount (Currency, in_list_view)
  - total (Currency, read_only)
  - add_deduct_tax (Select: Add/Deduct, default: Add)
- [x] Create purchase_taxes_and_charges.py controller
- [x] Create __init__.py file

### C7. Purchase Order DocType
- [x] Create purchase_order folder in university_erp/doctype
- [x] Create purchase_order.json with fields:
  - naming_series (Select: PO-.YYYY.-.#####)
  - supplier (Link: Supplier, reqd)
  - supplier_name (Data, fetch_from, read_only)
  - transaction_date (Date, reqd, default: Today)
  - status (Select: Draft/To Receive and Bill/To Bill/To Receive/Completed/Cancelled/Closed, read_only, default: Draft)
  - delivery_date (Date)
  - department (Link: Department)
  - items (Table: Purchase Order Item, reqd)
  - currency (Link: Currency, default: INR)
  - conversion_rate (Float, default: 1)
  - price_list (Link: Price List)
  - total_qty (Float, read_only)
  - total (Currency, read_only)
  - discount_amount (Currency)
  - taxes_and_charges (Link: Purchase Taxes and Charges Template)
  - taxes (Table: Purchase Taxes and Charges)
  - total_taxes_and_charges (Currency, read_only)
  - grand_total (Currency, read_only)
  - rounded_total (Currency, read_only)
  - payment_terms_template (Link: Payment Terms Template)
  - terms (Text Editor)
  - material_request (Link: Material Request)
  - quotation (Link: Supplier Quotation)
  - set_warehouse (Link: Warehouse)
- [x] Create purchase_order.py controller with:
  - validate() method
  - calculate_totals() method
  - calculate_taxes() method
  - on_submit() method
  - on_cancel() method
  - update_material_request() method
  - update_status() method
  - make_purchase_receipt() method
  - make_purchase_invoice() method
- [x] Create __init__.py file

### C8. Purchase Receipt Item Child DocType
- [x] Create purchase_receipt_item folder in university_erp/doctype
- [x] Create purchase_receipt_item.json with fields:
  - item_code (Link: Inventory Item, reqd, in_list_view)
  - item_name (Data, fetch_from, read_only, in_list_view)
  - qty (Float, reqd, in_list_view)
  - received_qty (Float, default: 0)
  - rejected_qty (Float, default: 0)
  - accepted_qty (Float, in_list_view)
  - uom (Link: UOM, fetch_from)
  - rate (Currency, in_list_view)
  - amount (Currency, read_only, in_list_view)
  - warehouse (Link: Warehouse)
  - rejected_warehouse (Link: Warehouse)
  - batch_no (Link: Batch)
  - serial_no (Small Text)
  - purchase_order (Link: Purchase Order)
  - purchase_order_item (Data)
- [x] Create purchase_receipt_item.py controller
- [x] Create __init__.py file

### C9. Purchase Receipt DocType
- [x] Create purchase_receipt folder in university_erp/doctype
- [x] Create purchase_receipt.json with fields:
  - naming_series (Select: PR-.YYYY.-.#####)
  - supplier (Link: Supplier, reqd)
  - posting_date (Date, reqd, default: Today)
  - posting_time (Time, default: Now)
  - status (Select: Draft/To Bill/Completed/Cancelled/Closed, read_only, default: Draft)
  - items (Table: Purchase Receipt Item, reqd)
  - total_qty (Float, read_only)
  - total (Currency, read_only)
  - purchase_order (Link: Purchase Order)
  - set_warehouse (Link: Warehouse)
  - remarks (Small Text)
- [x] Create purchase_receipt.py controller with:
  - validate() method
  - on_submit() method - create stock entries
  - on_cancel() method
  - update_purchase_order() method
- [x] Create __init__.py file

---

## Section D: Asset Management DocTypes

### D1. Asset Category DocType
- [x] Create asset_category folder in university_erp/doctype
- [x] Create asset_category.json with fields:
  - category_name (Data, reqd)
  - depreciation_method (Select: Straight Line/Double Declining Balance/Written Down Value)
  - total_number_of_depreciations (Int)
  - frequency_of_depreciation (Int)
  - rate_of_depreciation (Percent)
  - fixed_asset_account (Link: Account)
  - accumulated_depreciation_account (Link: Account)
  - depreciation_expense_account (Link: Account)
  - is_cwip_enabled (Check)
  - cwip_account (Link: Account)
- [x] Create asset_category.py controller
- [x] Create __init__.py file

### D2. Depreciation Schedule Child DocType
- [x] Create depreciation_schedule folder in university_erp/doctype
- [x] Create depreciation_schedule.json with fields:
  - schedule_date (Date, in_list_view)
  - depreciation_amount (Currency, in_list_view)
  - accumulated_depreciation_amount (Currency, in_list_view)
  - journal_entry (Link: Journal Entry)
  - make_depreciation_entry (Check)
- [x] Create depreciation_schedule.py controller
- [x] Create __init__.py file

### D3. Asset DocType
- [x] Create asset folder in university_erp/doctype
- [x] Create asset.json with fields:
  - naming_series (Select: AST-.YYYY.-.#####)
  - asset_name (Data, reqd)
  - asset_code (Data, unique)
  - item_code (Link: Inventory Item)
  - asset_category (Link: Asset Category, reqd)
  - status (Select: Draft/Submitted/In Use/In Maintenance/Disposed/Scrapped, default: Draft)
  - is_existing_asset (Check)
  - image (Attach Image)
  - asset_serial_no (Data)
  - manufacturer (Data)
  - model (Data)
  - purchase_date (Date)
  - purchase_invoice (Link: Purchase Invoice)
  - purchase_receipt (Link: Purchase Receipt)
  - supplier (Link: Supplier)
  - warranty_expiry_date (Date)
  - location (Link: Warehouse)
  - department (Link: Department)
  - custodian (Link: Employee)
  - building (Data)
  - floor (Data)
  - room_number (Data)
  - gross_purchase_amount (Currency)
  - opening_accumulated_depreciation (Currency)
  - asset_value (Currency, read_only)
  - total_depreciation (Currency, read_only)
  - calculate_depreciation (Check)
  - depreciation_method (Select, depends_on)
  - total_number_of_depreciations (Int, depends_on)
  - frequency_of_depreciation (Int, depends_on)
  - depreciation_start_date (Date, depends_on)
  - expected_value_after_useful_life (Currency, depends_on)
  - rate_of_depreciation (Percent, depends_on)
  - depreciation_schedule (Table: Depreciation Schedule, depends_on)
  - maintenance_required (Check)
  - next_maintenance_date (Date)
  - maintenance_frequency (Select: Monthly/Quarterly/Half-yearly/Yearly)
  - fixed_asset_account (Link: Account)
  - depreciation_expense_account (Link: Account)
  - accumulated_depreciation_account (Link: Account)
- [x] Create asset.py controller with:
  - validate() method
  - autoname() method
  - on_submit() method
  - set_depreciation_rate() method
  - make_depreciation_schedule() method
  - calculate_depreciation_amount() method
  - post_depreciation_entries() method
  - dispose_asset() method
  - scrap_asset() method
- [x] Create __init__.py file

### D4. Asset Movement Item Child DocType
- [x] Create asset_movement_item folder in university_erp/doctype
- [x] Create asset_movement_item.json with fields:
  - asset (Link: Asset, reqd, in_list_view)
  - asset_name (Data, fetch_from, read_only, in_list_view)
  - source_location (Link: Warehouse, in_list_view)
  - target_location (Link: Warehouse, in_list_view)
  - from_employee (Link: Employee)
  - to_employee (Link: Employee)
- [x] Create asset_movement_item.py controller
- [x] Create __init__.py file

### D5. Asset Movement DocType
- [x] Create asset_movement folder in university_erp/doctype
- [x] Create asset_movement.json with fields:
  - naming_series (Select: AM-.YYYY.-.#####)
  - purpose (Select: Transfer/Issue/Receipt, reqd)
  - transaction_date (Date, reqd, default: Today)
  - reference_doctype (Link: DocType)
  - reference_name (Dynamic Link)
  - assets (Table: Asset Movement Item, reqd)
  - remarks (Small Text)
- [x] Create asset_movement.py controller with:
  - validate() method
  - on_submit() method - update asset locations
  - on_cancel() method
- [x] Create __init__.py file

### D6. Asset Maintenance Part Child DocType
- [x] Create asset_maintenance_part folder in university_erp/doctype
- [x] Create asset_maintenance_part.json with fields:
  - item_code (Link: Inventory Item, in_list_view)
  - part_name (Data, in_list_view)
  - qty (Float, in_list_view)
  - rate (Currency)
  - amount (Currency, in_list_view)
- [x] Create asset_maintenance_part.py controller
- [x] Create __init__.py file

### D7. Maintenance Team DocType
- [x] Create maintenance_team folder in university_erp/doctype
- [x] Create maintenance_team.json with fields:
  - team_name (Data, reqd)
  - team_lead (Link: Employee)
  - department (Link: Department)
  - is_active (Check, default: 1)
  - members (Table: Maintenance Team Member)
- [x] Create maintenance_team.py controller
- [x] Create __init__.py file

### D8. Maintenance Team Member Child DocType
- [x] Create maintenance_team_member folder in university_erp/doctype
- [x] Create maintenance_team_member.json with fields:
  - employee (Link: Employee, reqd, in_list_view)
  - employee_name (Data, fetch_from, read_only, in_list_view)
  - role (Data, in_list_view)
- [x] Create maintenance_team_member.py controller
- [x] Create __init__.py file

### D9. Asset Maintenance DocType
- [x] Create asset_maintenance folder in university_erp/doctype
- [x] Create asset_maintenance.json with fields:
  - naming_series (Select: AMNT-.YYYY.-.#####)
  - asset (Link: Asset, reqd)
  - asset_name (Data, fetch_from, read_only)
  - maintenance_type (Select: Preventive/Corrective/Emergency/Calibration, reqd)
  - maintenance_status (Select: Planned/In Progress/Completed/Cancelled, default: Planned)
  - priority (Select: Low/Medium/High/Urgent)
  - planned_date (Date, reqd)
  - completion_date (Date)
  - assigned_to (Link: Employee)
  - maintenance_team (Link: Maintenance Team)
  - description (Small Text)
  - work_done (Text Editor)
  - parts_replaced (Table: Asset Maintenance Part)
  - labor_cost (Currency)
  - parts_cost (Currency)
  - other_cost (Currency)
  - total_cost (Currency, read_only)
- [x] Create asset_maintenance.py controller with:
  - validate() method
  - calculate_total_cost() method
  - on_submit() method - update asset maintenance date
  - complete_maintenance() method
- [x] Create __init__.py file

---

## Section E: Lab Equipment Management DocTypes

### E1. University Laboratory DocType (if not exists)
- [x] Check if University Laboratory DocType exists
- [x] Create university_laboratory folder if needed
- [x] Create university_laboratory.json with fields:
  - lab_name (Data, reqd)
  - lab_code (Data, unique)
  - lab_type (Select: Computer/Physics/Chemistry/Biology/Electronics/Mechanical/Civil/Research/Language/Other)
  - department (Link: Department)
  - building (Data)
  - floor (Data)
  - room_number (Data)
  - capacity (Int)
  - in_charge (Link: Employee)
  - is_active (Check, default: 1)
- [x] Create university_laboratory.py controller
- [x] Create __init__.py file

### E2. Lab Equipment DocType
- [x] Create lab_equipment folder in university_erp/doctype
- [x] Create lab_equipment.json with fields:
  - equipment_name (Data, reqd)
  - equipment_code (Data, unique)
  - asset (Link: Asset)
  - equipment_type (Select: Scientific/Computing/Electrical/Mechanical/Chemical/Biological/General, reqd)
  - status (Select: Available/In Use/Under Maintenance/Out of Order/Decommissioned, default: Available)
  - lab (Link: University Laboratory, reqd)
  - manufacturer (Data)
  - model (Data)
  - serial_number (Data)
  - purchase_date (Date)
  - warranty_end (Date)
  - purchase_value (Currency)
  - current_value (Currency)
  - requires_calibration (Check)
  - calibration_frequency (Select: Monthly/Quarterly/Half-yearly/Yearly, depends_on)
  - last_calibration_date (Date, depends_on)
  - next_calibration_date (Date, depends_on)
  - calibration_certificate (Attach, depends_on)
  - safety_precautions (Small Text)
  - operating_instructions (Text Editor)
  - requires_training (Check)
  - total_usage_hours (Float, read_only)
  - max_usage_hours (Float)
  - booking_required (Check)
- [x] Create lab_equipment.py controller with:
  - validate() method
  - calculate_next_calibration() method
  - update_usage_hours() method
  - check_availability() method
- [x] Create __init__.py file

### E3. Lab Equipment Booking DocType
- [x] Create lab_equipment_booking folder in university_erp/doctype
- [x] Create lab_equipment_booking.json with fields:
  - naming_series (Select: EQB-.YYYY.-.#####)
  - equipment (Link: Lab Equipment, reqd)
  - equipment_name (Data, fetch_from, read_only)
  - booked_by (Link: User, reqd)
  - status (Select: Pending/Approved/In Use/Completed/Cancelled, default: Pending)
  - purpose (Select: Research/Teaching/Project Work/Experiment/Calibration/Other, reqd)
  - booking_date (Date, reqd)
  - start_time (Time, reqd)
  - end_time (Time, reqd)
  - actual_start_time (Datetime)
  - actual_end_time (Datetime)
  - duration_hours (Float, read_only)
  - project (Link: Research Project)
  - course (Link: Course)
  - experiment_details (Small Text)
  - approved_by (Link: User)
  - approval_date (Date)
  - remarks (Small Text)
- [x] Create lab_equipment_booking.py controller with:
  - validate() method
  - check_conflicts() method
  - on_submit() method
  - start_usage() method
  - end_usage() method
  - calculate_duration() method
- [x] Create __init__.py file

### E4. Lab Consumable Issue DocType
- [x] Create lab_consumable_issue folder in university_erp/doctype
- [x] Create lab_consumable_issue.json with fields:
  - naming_series (Select: LCI-.YYYY.-.#####)
  - lab (Link: University Laboratory, reqd)
  - issue_date (Date, reqd, default: Today)
  - issued_by (Link: Employee)
  - issued_to (Link: User, reqd)
  - purpose (Select: Experiment/Research/Teaching/Project/Other, reqd)
  - items (Table: Lab Consumable Issue Item)
  - total_value (Currency, read_only)
  - project (Link: Research Project)
  - course (Link: Course)
  - remarks (Small Text)
- [x] Create lab_consumable_issue.py controller with:
  - validate() method
  - on_submit() method - create stock entries
  - on_cancel() method
- [x] Create __init__.py file

### E5. Lab Consumable Issue Item Child DocType
- [x] Create lab_consumable_issue_item folder in university_erp/doctype
- [x] Create lab_consumable_issue_item.json with fields:
  - item_code (Link: Inventory Item, reqd, in_list_view)
  - item_name (Data, fetch_from, read_only, in_list_view)
  - qty (Float, reqd, in_list_view)
  - uom (Link: UOM, fetch_from)
  - rate (Currency)
  - amount (Currency, read_only, in_list_view)
  - warehouse (Link: Warehouse)
- [x] Create lab_consumable_issue_item.py controller
- [x] Create __init__.py file

---

## Section F: Inventory Manager & Helper Functions

### F1. Inventory Manager Class
- [x] Create inventory_manager.py in university_erp module
- [x] Implement InventoryManager class with:
  - get_stock_balance(item_code, warehouse) method
  - get_low_stock_items(warehouse) method
  - create_stock_entry(entry_type, items, from_warehouse, to_warehouse, posting_date) method
  - process_material_receipt(purchase_order) method
  - process_material_issue(material_request) method
  - get_stock_ledger(item_code, warehouse, from_date, to_date) method
  - get_stock_summary_report(warehouse) method
  - auto_create_material_request() method for reorder level
  - get_item_valuation(item_code, warehouse, method) method
  - update_valuation_rate(item_code, warehouse) method

### F2. Stock Ledger Entry Creation
- [x] Implement create_stock_ledger_entry() function
- [x] Implement update_bin() function for stock bin updates
- [x] Implement get_previous_sle() function
- [x] Implement calculate_valuation_rate() function

### F3. Asset Manager Class
- [x] Create asset_manager.py in university_erp module
- [x] Implement AssetManager class with:
  - get_asset_value(asset) method
  - calculate_depreciation(asset) method
  - post_depreciation_entries(posting_date) method
  - get_assets_due_for_depreciation() method
  - get_assets_due_for_maintenance() method
  - transfer_asset(asset, to_location, to_custodian) method
  - dispose_asset(asset, disposal_date, proceeds) method
  - scrap_asset(asset, scrap_date, scrap_value) method

### F4. Whitelist API Functions
- [x] Create inventory_api.py in university_erp module
- [x] Implement API functions:
  - get_item_details() - for form auto-fill
  - get_stock_balance() - for item stock lookup
  - get_warehouse_stock() - for warehouse stock summary
  - get_supplier_details() - for supplier info
  - create_material_request() - API to create MR
  - create_purchase_order() - API to create PO
  - get_item_price() - for pricing lookup
  - get_items_below_reorder() - for reorder alerts

---

## Section G: Reports

### G1. Stock Balance Report
- [x] Create stock_balance folder in university_erp/report
- [x] Create stock_balance.json with filters:
  - item_code (Link: Inventory Item)
  - item_group (Link: Inventory Item Group)
  - warehouse (Link: Warehouse)
  - from_date (Date)
  - to_date (Date)
- [x] Create stock_balance.py with columns:
  - Item Code, Item Name, Item Group, Warehouse
  - Opening Qty, In Qty, Out Qty, Balance Qty
  - Valuation Rate, Balance Value, Reorder Level, Status

### G2. Stock Ledger Report
- [x] Create stock_ledger folder in university_erp/report
- [x] Create stock_ledger.json with filters:
  - item_code (Link: Inventory Item)
  - warehouse (Link: Warehouse)
  - from_date (Date)
  - to_date (Date)
  - voucher_type (Link: DocType)
- [x] Create stock_ledger.py with columns:
  - Date, Item Code, Warehouse, In Qty, Out Qty
  - Balance Qty, Valuation Rate, Balance Value
  - Voucher Type, Voucher No

### G3. Low Stock Items Report
- [x] Create low_stock_items folder in university_erp/report
- [x] Create low_stock_items.json with filters
- [x] Create low_stock_items.py

### G4. Asset Register Report
- [x] Create asset_register folder in university_erp/report
- [x] Create asset_register.json with filters
- [x] Create asset_register.py

### G5. Purchase Order Status Report
- [x] Create purchase_order_status folder in university_erp/report
- [x] Create purchase_order_status.json with filters:
  - supplier (Link: Supplier)
  - from_date (Date)
  - to_date (Date)
  - status (Select)
- [x] Create purchase_order_status.py with columns:
  - PO Number, Supplier, Date, Total Amount
  - Received %, Billed %, Status

### G6. Lab Equipment Utilization Report
- [x] Create lab_equipment_utilization folder in university_erp/report
- [x] Create lab_equipment_utilization.json with filters:
  - lab (Link: University Laboratory)
  - from_date (Date)
  - to_date (Date)
- [x] Create lab_equipment_utilization.py with columns:
  - Equipment Name, Lab, Total Bookings, Total Hours
  - Utilization %, Maintenance Hours

---

## Section H: Workspace & Navigation

### H1. Inventory & Asset Workspace
- [x] Create inventory_and_assets workspace folder
- [x] Create inventory_and_assets.json with:
  - Shortcuts: Inventory Item, Stock Entry, Purchase Order, Asset, Material Request
  - Links by category:
    - Inventory: Inventory Item, Item Group, Warehouse, Stock Entry, Stock Ledger Entry
    - Purchasing: Supplier, Material Request, Purchase Order, Purchase Receipt
    - Assets: Asset, Asset Category, Asset Movement, Asset Maintenance
    - Lab Equipment: Lab Equipment, Lab Equipment Booking, Lab Consumable Issue
  - Reports: Stock Balance, Stock Ledger, Asset Register, Low Stock Items

---

## Section I: Scheduled Tasks & Hooks

### I1. Scheduled Tasks
- [x] Add scheduled task for auto_create_material_request (daily)
- [x] Add scheduled task for post_depreciation_entries (monthly)
- [x] Add scheduled task for check_maintenance_due (daily)
- [x] Add scheduled task for check_calibration_due (daily)
- [x] Add scheduled task for send_low_stock_alerts (daily)
- [x] Add scheduled task for send_maintenance_reminders (daily)

### I2. Hooks Configuration
- [x] Update hooks.py with new DocTypes
- [x] Add scheduler_events for inventory tasks
- [x] Add doc_events for stock ledger creation
- [x] Add fixtures for default UOMs and Item Groups

---

## Section J: Fixtures & Default Data

### J1. Default UOMs
- [x] Create fixture for default UOMs:
  - Nos (Numbers)
  - Kg (Kilogram)
  - Ltr (Litre)
  - Mtr (Meter)
  - Box
  - Pack
  - Set
  - Pair
  - Dozen
  - Sqm (Square Meter)
  - Sqft (Square Feet)
  - Rft (Running Feet)

### J2. Default Item Groups
- [x] Create fixture for default Item Groups:
  - Stationery
  - Lab Consumables
  - Computer Hardware
  - Furniture
  - Electrical Items
  - Cleaning Supplies
  - Sports Equipment
  - Library Supplies
  - Hostel Supplies
  - Medical Supplies

### J3. Default Asset Categories
- [x] Create fixture for default Asset Categories:
  - Computers & IT Equipment
  - Furniture & Fixtures
  - Laboratory Equipment
  - Office Equipment
  - Vehicles
  - Buildings
  - Land
  - Software
  - Audio Visual Equipment

### J4. Default Warehouses
- [x] Create fixture for default Warehouses:
  - Main Store
  - Computer Lab Store
  - Physics Lab Store
  - Chemistry Lab Store
  - Library Store
  - Sports Store
  - Hostel Store
  - Transit

---

## Section K: Testing

### K1. Unit Tests
- [x] Create test_inventory_item.py
- [x] Create test_stock_entry.py
- [x] Create test_purchase_order.py
- [x] Create test_material_request.py
- [x] Create test_asset.py
- [x] Create test_asset_movement.py
- [x] Create test_lab_equipment.py
- [x] Create test_inventory_manager.py

### K2. Integration Tests
- [x] Create test_purchase_workflow.py (MR -> PO -> PR -> Stock Entry)
- [x] Create test_stock_movements.py
- [x] Create test_asset_depreciation.py

---

## Summary

| Section | Total Tasks | Completed | Pending |
|---------|-------------|-----------|---------|
| A. Core Inventory DocTypes | 24 | 24 | 0 |
| B. Stock Management DocTypes | 20 | 20 | 0 |
| C. Purchase Management DocTypes | 36 | 36 | 0 |
| D. Asset Management DocTypes | 36 | 36 | 0 |
| E. Lab Equipment DocTypes | 20 | 20 | 0 |
| F. Manager Classes & APIs | 16 | 16 | 0 |
| G. Reports | 18 | 18 | 0 |
| H. Workspace | 2 | 2 | 0 |
| I. Scheduled Tasks & Hooks | 10 | 10 | 0 |
| J. Fixtures & Default Data | 4 | 4 | 0 |
| K. Testing | 11 | 11 | 0 |
| **Total** | **197** | **197** | **0** |

**Completion: 100%**

---

## Implementation Priority

1. **Phase 1 (Foundation)**: Core Inventory DocTypes (UOM, Item Group, Warehouse, Inventory Item)
2. **Phase 2 (Stock Management)**: Stock Entry, Stock Ledger Entry, Stock Reconciliation
3. **Phase 3 (Purchasing)**: Supplier, Material Request, Purchase Order, Purchase Receipt
4. **Phase 4 (Assets)**: Asset Category, Asset, Asset Movement, Asset Maintenance
5. **Phase 5 (Lab Equipment)**: Lab Equipment, Equipment Booking, Consumable Issue
6. **Phase 6 (Reports & Polish)**: Reports, Workspace, Testing, Documentation

---

**Created**: 2026-01-14
**Status**: Completed (100%)
**Last Updated**: 2026-01-14

---

## Files Created in This Implementation

### Section A: Core Inventory DocTypes
- `university_erp/doctype/inventory_item_group/inventory_item_group.json`
- `university_erp/doctype/inventory_item_group/inventory_item_group.py`
- `university_erp/doctype/warehouse/warehouse.json`
- `university_erp/doctype/warehouse/warehouse.py`
- `university_erp/doctype/item_specification/item_specification.json`
- `university_erp/doctype/item_specification/item_specification.py`
- `university_erp/doctype/inventory_item/inventory_item.json`
- `university_erp/doctype/inventory_item/inventory_item.py`
- `university_erp/doctype/batch/batch.json`
- `university_erp/doctype/batch/batch.py`

### Section B: Stock Management DocTypes
- `university_erp/doctype/stock_entry_item/stock_entry_item.json`
- `university_erp/doctype/stock_entry_item/stock_entry_item.py`
- `university_erp/doctype/stock_entry/stock_entry.json`
- `university_erp/doctype/stock_entry/stock_entry.py`
- `university_erp/doctype/stock_ledger_entry/stock_ledger_entry.json`
- `university_erp/doctype/stock_ledger_entry/stock_ledger_entry.py`
- `university_erp/doctype/stock_reconciliation_item/stock_reconciliation_item.json`
- `university_erp/doctype/stock_reconciliation_item/stock_reconciliation_item.py`
- `university_erp/doctype/stock_reconciliation/stock_reconciliation.json`
- `university_erp/doctype/stock_reconciliation/stock_reconciliation.py`

### Section C: Purchase Management DocTypes
- `university_erp/doctype/supplier_group/supplier_group.json`
- `university_erp/doctype/supplier_group/supplier_group.py`
- `university_erp/doctype/supplier/supplier.json`
- `university_erp/doctype/supplier/supplier.py`
- `university_erp/doctype/material_request_item/material_request_item.json`
- `university_erp/doctype/material_request_item/material_request_item.py`
- `university_erp/doctype/material_request/material_request.json`
- `university_erp/doctype/material_request/material_request.py`
- `university_erp/doctype/purchase_order_item/purchase_order_item.json`
- `university_erp/doctype/purchase_order_item/purchase_order_item.py`
- `university_erp/doctype/purchase_taxes_and_charges/purchase_taxes_and_charges.json`
- `university_erp/doctype/purchase_taxes_and_charges/purchase_taxes_and_charges.py`
- `university_erp/doctype/purchase_order/purchase_order.json`
- `university_erp/doctype/purchase_order/purchase_order.py`
- `university_erp/doctype/purchase_receipt_item/purchase_receipt_item.json`
- `university_erp/doctype/purchase_receipt_item/purchase_receipt_item.py`
- `university_erp/doctype/purchase_receipt/purchase_receipt.json`
- `university_erp/doctype/purchase_receipt/purchase_receipt.py`

### Section D: Asset Management DocTypes
- `university_erp/doctype/asset_category/asset_category.json`
- `university_erp/doctype/asset_category/asset_category.py`
- `university_erp/doctype/depreciation_schedule/depreciation_schedule.json`
- `university_erp/doctype/depreciation_schedule/depreciation_schedule.py`
- `university_erp/doctype/asset/asset.json`
- `university_erp/doctype/asset/asset.py`
- `university_erp/doctype/asset_movement_item/asset_movement_item.json`
- `university_erp/doctype/asset_movement_item/asset_movement_item.py`
- `university_erp/doctype/asset_movement/asset_movement.json`
- `university_erp/doctype/asset_movement/asset_movement.py`
- `university_erp/doctype/maintenance_team_member/maintenance_team_member.json`
- `university_erp/doctype/maintenance_team_member/maintenance_team_member.py`
- `university_erp/doctype/maintenance_team/maintenance_team.json`
- `university_erp/doctype/maintenance_team/maintenance_team.py`
- `university_erp/doctype/asset_maintenance_part/asset_maintenance_part.json`
- `university_erp/doctype/asset_maintenance_part/asset_maintenance_part.py`
- `university_erp/doctype/asset_maintenance/asset_maintenance.json`
- `university_erp/doctype/asset_maintenance/asset_maintenance.py`

### Section E: Lab Equipment DocTypes
- `university_erp/doctype/university_laboratory/university_laboratory.json`
- `university_erp/doctype/university_laboratory/university_laboratory.py`
- `university_erp/doctype/lab_equipment/lab_equipment.json`
- `university_erp/doctype/lab_equipment/lab_equipment.py`
- `university_erp/doctype/lab_equipment_booking/lab_equipment_booking.json`
- `university_erp/doctype/lab_equipment_booking/lab_equipment_booking.py`
- `university_erp/doctype/lab_consumable_issue_item/lab_consumable_issue_item.json`
- `university_erp/doctype/lab_consumable_issue_item/lab_consumable_issue_item.py`
- `university_erp/doctype/lab_consumable_issue/lab_consumable_issue.json`
- `university_erp/doctype/lab_consumable_issue/lab_consumable_issue.py`

### Section F: Manager Classes
- `university_erp/inventory_manager.py`
- `university_erp/asset_manager.py`

### Section G: Reports
- `university_erp/report/stock_balance/stock_balance.json`
- `university_erp/report/stock_balance/stock_balance.py`
- `university_erp/report/stock_balance/__init__.py`
- `university_erp/report/stock_ledger/stock_ledger.json`
- `university_erp/report/stock_ledger/stock_ledger.py`
- `university_erp/report/stock_ledger/__init__.py`
- `university_erp/report/low_stock_items/low_stock_items.json`
- `university_erp/report/low_stock_items/low_stock_items.py`
- `university_erp/report/low_stock_items/__init__.py`
- `university_erp/report/asset_register/asset_register.json`
- `university_erp/report/asset_register/asset_register.py`
- `university_erp/report/asset_register/__init__.py`
- `university_erp/report/purchase_order_status/purchase_order_status.json`
- `university_erp/report/purchase_order_status/purchase_order_status.py`
- `university_erp/report/purchase_order_status/__init__.py`
- `university_erp/report/lab_equipment_utilization/lab_equipment_utilization.json`
- `university_erp/report/lab_equipment_utilization/lab_equipment_utilization.py`
- `university_erp/report/lab_equipment_utilization/__init__.py`

### Section H: Workspace
- `university_erp/workspace/inventory_and_assets/inventory_and_assets.json`

### Section I: Scheduled Tasks
- `university_erp/inventory_scheduled_tasks.py`
- Updated `hooks.py` with scheduler events

### Section J: Fixtures
- `university_erp/fixtures/inventory_fixtures.py`
- `university_erp/fixtures/__init__.py`

### Section K: Tests
- `university_erp/tests/__init__.py`
- `university_erp/tests/test_inventory_item.py`
- `university_erp/tests/test_stock_entry.py`
- `university_erp/tests/test_purchase_order.py`
- `university_erp/tests/test_material_request.py`
- `university_erp/tests/test_asset.py`
- `university_erp/tests/test_asset_movement.py`
- `university_erp/tests/test_lab_equipment.py`
- `university_erp/tests/test_inventory_manager.py`
- `university_erp/tests/test_purchase_workflow.py`
- `university_erp/tests/test_stock_movements.py`
- `university_erp/tests/test_asset_depreciation.py`

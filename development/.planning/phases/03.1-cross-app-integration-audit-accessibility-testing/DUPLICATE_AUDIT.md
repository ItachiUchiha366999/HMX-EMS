# Duplicate Doctype Audit Report

**Generated:** 2026-03-18 23:31:07 UTC
**Apps scanned:** education, erpnext, frappe, hrms, university_erp

## App Doctype Counts

| App | Doctype Count |
|-----|--------------|
| education | 71 |
| erpnext | 501 |
| frappe | 266 |
| hrms | 149 |
| university_erp | 268 |

## Executive Summary

- **Exact Name Matches:** 32 duplicate pairs found
- **Semantic Overlaps:** 260 pairs with 50%+ shared link targets
- **Shared Link Targets:** 75 doctypes referenced by 2+ apps


## Exact Name Matches

| Doctype | App 1 | App 2 | Fields (1) | Fields (2) | Only In 1 | Only In 2 | Type Mismatches | Live Owner | Recommendation |
|---------|-------|-------|-----------|-----------|-----------|-----------|----------------|------------|---------------|
| Asset | erpnext | university_erp | 70 | 58 | 48 | 36 | 0 | University Inventory | Merge schemas |
| Asset Category | erpnext | university_erp | 9 | 17 | 9 | 17 | 0 | University Inventory | Keep university_erp, alias erpnext |
| Asset Maintenance | erpnext | university_erp | 13 | 25 | 11 | 23 | 1 | University Inventory | Keep university_erp, alias erpnext |
| Asset Movement | erpnext | university_erp | 11 | 11 | 5 | 5 | 1 | University Inventory | Merge schemas |
| Asset Movement Item | erpnext | university_erp | 8 | 7 | 2 | 1 | 0 | University Inventory | Keep erpnext, migrate 1 custom fields |
| Bank Transaction | erpnext | university_erp | 35 | 14 | 27 | 6 | 2 | University Payments | Merge schemas |
| Batch | erpnext | university_erp | 26 | 11 | 19 | 4 | 0 | University ERP | Merge schemas |
| Depreciation Schedule | erpnext | university_erp | 7 | 6 | 2 | 1 | 1 | University Inventory | Keep erpnext, migrate 1 custom fields |
| Discussion Reply | frappe | university_erp | 2 | 9 | 2 | 9 | 0 | University LMS | Keep university_erp, alias frappe |
| Grievance Type | hrms | university_erp | 2 | 15 | 1 | 14 | 0 | University Grievance | Keep university_erp, alias hrms |
| Industry Type | erpnext | university_erp | 1 | 2 | 1 | 2 | 0 | University Placement | Keep university_erp, alias erpnext |
| Maintenance Team Member | erpnext | university_erp | 3 | 3 | 3 | 3 | 0 | University Inventory | Merge schemas |
| Material Request | erpnext | university_erp | 39 | 17 | 29 | 7 | 0 | University Inventory | Merge schemas |
| Material Request Item | erpnext | university_erp | 54 | 13 | 43 | 2 | 1 | University Inventory | Keep erpnext, migrate 2 custom fields |
| Payment Order | erpnext | university_erp | 12 | 25 | 11 | 24 | 0 | University Payments | Keep university_erp, alias erpnext |
| Print Heading | erpnext | frappe | 2 | 2 | 0 | 0 | 0 | Setup | Keep erpnext version (more fields) |
| Purchase Order | erpnext | university_erp | 154 | 34 | 131 | 11 | 0 | University Inventory | Merge schemas |
| Purchase Order Item | erpnext | university_erp | 106 | 16 | 94 | 4 | 1 | University Inventory | Merge schemas |
| Purchase Receipt | erpnext | university_erp | 147 | 40 | 121 | 14 | 1 | University Inventory | Merge schemas |
| Purchase Receipt Item | erpnext | university_erp | 127 | 26 | 108 | 7 | 2 | University Inventory | Merge schemas |
| Purchase Taxes and Charges | erpnext | university_erp | 26 | 9 | 18 | 1 | 1 | University Inventory | Keep erpnext, migrate 1 custom fields |
| Push Notification Settings | frappe | university_erp | 5 | 25 | 5 | 25 | 0 | University Integrations | Keep university_erp, alias frappe |
| Quiz Question | education | university_erp | 2 | 10 | 2 | 10 | 0 | University LMS | Keep university_erp, alias education |
| SMS Log | erpnext | university_erp | 10 | 16 | 8 | 14 | 2 | University Integrations | Keep university_erp, alias erpnext |
| Stock Entry | erpnext | university_erp | 79 | 24 | 66 | 11 | 2 | University Inventory | Merge schemas |
| Stock Ledger Entry | erpnext | university_erp | 36 | 22 | 20 | 6 | 4 | University Inventory | Merge schemas |
| Stock Reconciliation | erpnext | university_erp | 24 | 17 | 13 | 6 | 1 | University Inventory | Merge schemas |
| Stock Reconciliation Item | erpnext | university_erp | 33 | 17 | 21 | 5 | 1 | University Inventory | Merge schemas |
| Supplier | erpnext | university_erp | 64 | 36 | 55 | 27 | 0 | University Inventory | Merge schemas |
| Supplier Group | erpnext | university_erp | 10 | 5 | 7 | 2 | 0 | University Inventory | Keep erpnext, migrate 2 custom fields |
| UOM | erpnext | university_erp | 3 | 4 | 0 | 1 | 0 | University Inventory | Keep university_erp, alias erpnext |
| Warehouse | erpnext | university_erp | 32 | 16 | 27 | 11 | 1 | University Inventory | Merge schemas |

### Detailed Schema Differences

#### Asset (erpnext vs university_erp)

**Fields only in erpnext:** accounting_dimensions_section, additional_asset_cost, asset_owner, asset_owner_company, asset_quantity, available_for_use_date, booked_fixed_asset, column_break_23, column_break_24, column_break_3, column_break_33, column_break_48, column_break_51, company, comprehensive_insurance
  ...and 33 more
**Fields only in university_erp:** accounts_section, accumulated_depreciation_account, asset_code, asset_serial_no, asset_value, building, column_break_1, column_break_accounts, column_break_depreciation, column_break_details, column_break_location, column_break_maintenance, column_break_purchase, column_break_valuation, depreciation_expense_account
  ...and 21 more
**Link target diffs:** department: Department vs University Department; location: Location vs Warehouse; item_code: Item vs Inventory Item

#### Asset Category (erpnext vs university_erp)

**Fields only in erpnext:** accounts, asset_category_name, column_break_3, depreciation_options, enable_cwip_accounting, finance_book_detail, finance_books, non_depreciable_category, section_break_2
**Fields only in university_erp:** accounts_section, accumulated_depreciation_account, category_name, column_break_accounts, column_break_depreciation, cwip_account, cwip_section, depreciation_expense_account, depreciation_method, depreciation_section, description, expected_value_after_useful_life, fixed_asset_account, frequency_of_depreciation, is_cwip_enabled
  ...and 2 more

#### Asset Maintenance (erpnext vs university_erp)

**Fields only in erpnext:** asset_category, asset_maintenance_tasks, column_break_3, column_break_9, company, item_code, item_name, maintenance_manager, maintenance_manager_name, section_break_6, section_break_8
**Fields only in university_erp:** amended_from, asset, assigned_to, column_break_1, column_break_costs, column_break_schedule, completion_date, costs_section, description, labor_cost, maintenance_status, maintenance_type, naming_series, other_cost, parts_cost
  ...and 8 more
**Type mismatches:** asset_name: Link vs Data
**Link target diffs:** maintenance_team: Asset Maintenance Team vs Maintenance Team

#### Asset Movement (erpnext vs university_erp)

**Fields only in erpnext:** column_break_4, column_break_9, company, reference, section_break_10
**Fields only in university_erp:** assets_section, column_break_1, naming_series, remarks, remarks_section
**Type mismatches:** transaction_date: Datetime vs Date

#### Asset Movement Item (erpnext vs university_erp)

**Fields only in erpnext:** column_break_2, company
**Fields only in university_erp:** column_break_1
**Link target diffs:** source_location: Location vs Warehouse; target_location: Location vs Warehouse

#### Bank Transaction (erpnext vs university_erp)

**Fields only in erpnext:** allocated_amount, amended_from, bank_party_account_number, bank_party_iban, bank_party_name, column_break_10, column_break_17, column_break_3czf, column_break_7, column_break_oufv, company, currency, excluded_fee, extended_bank_statement_section, included_fee
  ...and 12 more
**Fields only in university_erp:** closing_balance, column_break_1, matched_by, payment_entry, payment_order, status_section
**Type mismatches:** description: Small Text vs Data; reference_number: Small Text vs Data

#### Batch (erpnext vs university_erp)

**Fields only in erpnext:** column_break_23, column_break_24, column_break_3, column_break_9, description, disabled, image, item, item_name, manufacturing_section, parent_batch, produced_qty, qty_to_produce, sb_batch, sb_disabled
  ...and 4 more
**Fields only in university_erp:** column_break_1, details_section, item_code, naming_series

#### Depreciation Schedule (erpnext vs university_erp)

**Fields only in erpnext:** column_break_3, shift
**Fields only in university_erp:** column_break_1
**Type mismatches:** make_depreciation_entry: Button vs Check

#### Discussion Reply (frappe vs university_erp)

**Fields only in frappe:** reply, topic
**Fields only in university_erp:** column_break_1, instructor, is_answer, reply_by_type, reply_content, reply_date, section_content, student, upvotes

#### Grievance Type (hrms vs university_erp)

**Fields only in hrms:** section_break_5
**Fields only in university_erp:** allow_anonymous, category, column_break_1, confidential_handling, default_assignee, default_committee, default_priority, escalation_matrix, grievance_type_name, is_active, requires_evidence, section_break_routing, section_break_settings, sla_days

#### Industry Type (erpnext vs university_erp)

**Fields only in erpnext:** industry
**Fields only in university_erp:** description, industry_name

#### Maintenance Team Member (erpnext vs university_erp)

**Fields only in erpnext:** full_name, maintenance_role, team_member
**Fields only in university_erp:** employee, employee_name, role

#### Material Request (erpnext vs university_erp)

**Fields only in erpnext:** buying_price_list, column_break2, column_break5, column_break_2, column_break_31, column_break_35, company, connections_tab, customer, job_card, last_scanned_warehouse, letter_head, more_info_tab, per_ordered, per_received
  ...and 14 more
**Fields only in university_erp:** column_break_1, department, justification, reason, reason_section, requested_by, required_by

#### Material Request Item (erpnext vs university_erp)

**Fields only in erpnext:** accounting_details_section, accounting_dimensions_section, actual_qty, bom_no, brand, col_break1, col_break2, col_break3, col_break4, col_break_mfg, column_break_12, column_break_glru, conversion_factor, cost_center, dimension_col_break
  ...and 28 more
**Fields only in university_erp:** column_break_1, status_section
**Type mismatches:** description: Text Editor vs Small Text
**Link target diffs:** item_code: Item vs Inventory Item

#### Payment Order (erpnext vs university_erp)

**Fields only in erpnext:** account, amended_from, company, company_bank, company_bank_account, naming_series, party, payment_order_type, posting_date, references, section_break_5
**Fields only in university_erp:** amount, column_break_1, creation_date, currency, failure_reason, failure_section, gateway_order_id, gateway_payment_id, mode_of_payment, payment_date, payment_entry, payment_gateway, payment_section, reference_doctype, reference_name
  ...and 9 more

#### Purchase Order (erpnext vs university_erp)

**Fields only in erpnext:** accounting_dimensions_section, additional_discount_percentage, additional_info_section, address_and_contact_tab, address_display, advance_paid, apply_discount_on, apply_tds, auto_repeat, base_discount_amount, base_grand_total, base_in_words, base_net_total, base_rounded_total, base_rounding_adjustment
  ...and 116 more
**Fields only in university_erp:** column_break_1, column_break_totals, delivery_date, department, material_request, price_list, pricing_section, quotation, reference_section, terms_section, warehouse_section

#### Purchase Order Item (erpnext vs university_erp)

**Fields only in erpnext:** accounting_details, accounting_dimensions_section, actual_qty, against_blanket_order, apply_tds, base_amount, base_net_amount, base_net_rate, base_price_list_rate, base_rate, base_rate_with_margin, billed_amt, blanket_order, blanket_order_rate, bom
  ...and 79 more
**Fields only in university_erp:** billed_qty, column_break_1, reference_section, status_section
**Type mismatches:** description: Text Editor vs Small Text
**Link target diffs:** item_code: Item vs Inventory Item

#### Purchase Receipt (erpnext vs university_erp)

**Fields only in erpnext:** accounting_dimensions_section, additional_discount_percentage, additional_info_section, address_and_contact_tab, address_display, apply_discount_on, apply_putaway_rule, auto_repeat, base_discount_amount, base_grand_total, base_in_words, base_net_total, base_rounded_total, base_rounding_adjustment, base_tax_withholding_net_total
  ...and 106 more
**Fields only in university_erp:** column_break_basic, column_break_grand, column_break_ref, column_break_totals, purchase_order, section_break_grand, section_break_items, section_break_purchase_order, section_break_remarks, section_break_taxes, section_break_terms, section_break_totals, total_rejected_qty, transporter
**Type mismatches:** supplier_address: Link vs Small Text

#### Purchase Receipt Item (erpnext vs university_erp)

**Fields only in erpnext:** accounting_details_section, accounting_dimensions_section, add_serial_batch_bundle, add_serial_batch_for_rejected_qty, allow_zero_valuation_rate, amount_difference_with_purchase_invoice, apply_tds, asset_category, asset_location, barcode, base_amount, base_net_amount, base_net_rate, base_price_list_rate, base_rate
  ...and 93 more
**Fields only in university_erp:** accepted_qty, column_break_qty, column_break_warehouse, expiry_date, section_break_batch, section_break_rate, section_break_reference
**Type mismatches:** serial_no: Text vs Small Text; description: Text Editor vs Small Text
**Link target diffs:** item_code: Item vs Inventory Item

#### Purchase Taxes and Charges (erpnext vs university_erp)

**Fields only in erpnext:** account_currency, accounting_dimensions_section, base_tax_amount, base_tax_amount_after_discount_amount, base_total, category, col_break1, column_break_14, cost_center, dimension_col_break, included_in_paid_amount, included_in_print_rate, is_tax_withholding_account, item_wise_tax_detail, project
  ...and 3 more
**Fields only in university_erp:** column_break_1
**Type mismatches:** description: Small Text vs Data

#### Push Notification Settings (frappe vs university_erp)

**Fields only in frappe:** api_key, api_secret, authentication_credential_section, enable_push_notification_relay, section_break_qgjr
**Fields only in university_erp:** column_break_basic, column_break_firebase, column_break_onesignal, column_break_settings, column_break_vapid, default_badge_url, default_icon_url, enabled, firebase_project_id, firebase_section, firebase_server_key, firebase_service_account, notification_sound, onesignal_api_key, onesignal_app_id
  ...and 10 more

#### Quiz Question (education vs university_erp)

**Fields only in education:** question, question_link
**Fields only in university_erp:** column_break_1, correct_answer, explanation, image, marks, negative_marks, options, question_text, question_type, section_additional

#### SMS Log (erpnext vs university_erp)

**Fields only in erpnext:** column_break0, column_break1, no_of_requested_sms, no_of_sent_sms, requested_numbers, sec_break1, sender_name, sent_to
**Fields only in university_erp:** column_break_basic, delivered_on, delivery_section, delivery_status, error_message, gateway_response, message_id, naming_series, recipient, recipient_name, response_section, sms_gateway, status, template_used
**Type mismatches:** sent_on: Date vs Datetime; message: Small Text vs Text

#### Stock Entry (erpnext vs university_erp)

**Fields only in erpnext:** accounting_dimensions_section, add_to_transit, additional_costs, additional_costs_section, address_display, apply_putaway_rule, asset_repair, bom_info_section, bom_no, cb0, cb1, col2, col5, column_break_22, column_break_e92r
  ...and 51 more
**Fields only in university_erp:** column_break_1, column_break_ref, column_break_totals, entry_type, material_request, reference_doctype, reference_name, reference_section, remarks_section, total_qty, totals_section
**Type mismatches:** remarks: Text vs Small Text; purpose: Select vs Data

#### Stock Ledger Entry (erpnext vs university_erp)

**Fields only in erpnext:** auto_created_serial_and_batch_bundle, column_break_17, column_break_26, column_break_6, company, dependant_sle_voucher_detail_no, fiscal_year, has_batch_no, has_serial_no, is_adjustment_entry, posting_datetime, project, recalculate_rate, section_break_11, section_break_21
  ...and 5 more
**Fields only in university_erp:** batch_section, column_break_1, column_break_qty, naming_series, qty_section, valuation_section
**Type mismatches:** serial_no: Long Text vs Small Text; voucher_type: Link vs Data; voucher_no: Dynamic Link vs Data; batch_no: Data vs Link
**Link target diffs:** item_code: Item vs Inventory Item

#### Stock Reconciliation (erpnext vs university_erp)

**Fields only in erpnext:** accounting_dimensions_section, col1, column_break_12, column_break_13, dimension_col_break, last_scanned_warehouse, sb9, scan_barcode, scan_mode, section_break_22, section_break_8, section_break_9, set_posting_time
**Fields only in university_erp:** column_break_accounts, column_break_basic, remarks, section_break_items, section_break_remarks, section_break_totals
**Type mismatches:** company: Link vs Data

#### Stock Reconciliation Item (erpnext vs university_erp)

**Fields only in erpnext:** add_serial_batch_bundle, allow_zero_valuation_rate, barcode, column_break_11, column_break_16, column_break_6, column_break_9, column_break_eefq, current_serial_and_batch_bundle, current_serial_no, has_item_scanned, item_group, quantity_difference, reconcile_all_serial_batch, section_break_14
  ...and 6 more
**Fields only in university_erp:** column_break_amount, column_break_qty, qty_difference, section_break_batch, section_break_valuation
**Type mismatches:** serial_no: Long Text vs Small Text
**Link target diffs:** item_code: Item vs Inventory Item

#### Supplier (erpnext vs university_erp)

**Fields only in erpnext:** accounting_tab, accounts, address_contacts, address_html, allow_purchase_invoice_creation_without_purchase_order, allow_purchase_invoice_creation_without_purchase_receipt, block_supplier_section, column_break0, column_break1, column_break2, column_break_10, column_break_16, column_break_1mqv, column_break_27, column_break_30
  ...and 40 more
**Fields only in university_erp:** accounting_section, address, bank_account, bank_name, bank_section, city, column_break_1, column_break_bank, column_break_contact, column_break_tax, contact_person, contact_section, credit_limit, email, gstin
  ...and 12 more

#### Supplier Group (erpnext vs university_erp)

**Fields only in erpnext:** accounts, default_payable_account, lft, old_parent, payment_terms, rgt, section_credit_limit
**Fields only in university_erp:** column_break_1, default_payment_terms

#### UOM (erpnext vs university_erp)

**Fields only in university_erp:** column_break_1

#### Warehouse (erpnext vs university_erp)

**Fields only in erpnext:** address_and_contact, address_html, address_line_1, address_line_2, city, column_break0, column_break_10, column_break_3, column_break_4, column_break_qajx, company, contact_html, default_in_transit_warehouse, disabled, email_id
  ...and 12 more
**Fields only in university_erp:** accounting_section, address, building, column_break_1, column_break_location, custodian, department, floor, is_active, location_section, room_number
**Type mismatches:** warehouse_type: Link vs Select

## Semantic Overlaps

Doctypes in different apps sharing 60%+ of their Link field targets (min 3 shared) within domain areas.
Showing top 50 of 260 pairs, sorted by overlap percentage.

| Domain | Doctype (App 1) | Doctype (App 2) | Shared Link Targets | Overlap % | Recommendation |
|--------|----------------|----------------|--------------------|---------:|---------------|
| assessment/grading | Assessment Plan (education) | Exam Schedule (university_erp) | Academic Term, Course, Room | 100.0% | Review for consolidation |
| assessment/grading | Assessment Result (education) | Course Registration (university_erp) | Academic Term, Program, Student | 100.0% | Review for consolidation |
| courses/teaching | Course Scheduling Tool (education) | Exam Schedule (university_erp) | Academic Term, Course, Room | 100.0% | Review for consolidation |
| fees/finance | Fees (education) | Account (erpnext) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Fees (education) | Dunning Type (erpnext) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Fees (education) | Course Registration (university_erp) | Academic Term, Program, Student | 100.0% | Review for consolidation |
| fees/finance | Fees (education) | Bulk Fee Generator (university_erp) | Academic Term, Academic Year, Fee Structure, Program, Student Batch Name | 100.0% | Review for consolidation |
| fees/finance | Fees (education) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Fee Schedule (education) | Account (erpnext) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Fee Schedule (education) | Dunning Type (erpnext) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Fee Schedule (education) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Fee Structure (education) | Dunning Type (erpnext) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Fee Structure (education) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| courses/teaching | Instructor (education) | Employee (erpnext) | Department, Employee, Gender | 100.0% | Review for consolidation |
| courses/teaching | Instructor Log (education) | Workload Distributor (university_erp) | Academic Term, Academic Year, Department, Program | 100.0% | Review for consolidation |
| courses/teaching | Program Enrollment (education) | Course Registration (university_erp) | Academic Term, Program, Student | 100.0% | Review for consolidation |
| fees/finance | Program Enrollment Tool (education) | Bulk Fee Generator (university_erp) | Academic Term, Academic Year, Program, Student Batch Name | 100.0% | Review for consolidation |
| courses/teaching | Student Group Creation Tool (education) | Teaching Assignment (university_erp) | Academic Term, Academic Year, Program | 100.0% | Review for consolidation |
| assessment/grading | Student Group Creation Tool (education) | Internal Assessment (university_erp) | Academic Term, Academic Year, Program | 100.0% | Review for consolidation |
| exams/quizzes | Student Group Creation Tool (education) | Practical Examination (university_erp) | Academic Term, Academic Year, Program | 100.0% | Review for consolidation |
| fees/finance | Student Group Creation Tool (education) | Bulk Fee Generator (university_erp) | Academic Term, Academic Year, Program | 100.0% | Review for consolidation |
| courses/teaching | Student Log (education) | Course Registration (university_erp) | Academic Term, Program, Student | 100.0% | Review for consolidation |
| courses/teaching | Student Report Generation Tool (education) | Course Registration (university_erp) | Academic Term, Program, Student | 100.0% | Review for consolidation |
| fees/finance | Account (erpnext) | Employee Advance (hrms) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Account (erpnext) | Leave Encashment (hrms) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Account (erpnext) | Bulk Salary Structure Assignment (hrms) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Account (erpnext) | Payroll Entry (hrms) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Account (erpnext) | Salary Structure (hrms) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Account (erpnext) | Salary Structure Assignment (hrms) | Account, Company, Currency | 100.0% | Review for consolidation |
| fees/finance | Account Closing Balance (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Account Closing Balance (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Advance Payment Ledger Entry (erpnext) | Additional Salary (hrms) | Company, Currency, DocType | 100.0% | Review for consolidation |
| fees/finance | Advance Taxes and Charges (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Advance Taxes and Charges (erpnext) | Payroll Entry (hrms) | Account, Cost Center, Currency, Project | 100.0% | Review for consolidation |
| fees/finance | Dunning (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| attendance | Dunning Type (erpnext) | Leave Encashment (hrms) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Dunning Type (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | GL Entry (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | GL Entry (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Journal Entry Account (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Loyalty Program (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Loyalty Program (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Opening Invoice Creation Tool (erpnext) | Expense Claim (hrms) | Company, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Opening Invoice Creation Tool (erpnext) | Payroll Entry (hrms) | Company, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Payment Entry (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Payment Entry (erpnext) | Bank Transaction (university_erp) | Bank Account, Payment Entry, Payment Order | 100.0% | Review for consolidation |
| fees/finance | Payment Entry (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Payment Ledger Entry (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| fees/finance | Payment Reconciliation (erpnext) | Expense Taxes and Charges (hrms) | Account, Cost Center, Project | 100.0% | Review for consolidation |
| fees/finance | Payment Reconciliation (erpnext) | University Accounts Settings (university_erp) | Account, Company, Cost Center | 100.0% | Review for consolidation |
| ... | 210 more pairs | | | | |

## Shared Link Targets

Doctypes referenced by Link fields from 2+ different apps.

| Target Doctype | Referenced By (App: count) | Total Incoming Links | Apps |
|---------------|---------------------------|--------------------:|-----:|
| Company | education: 3, erpnext: 131, hrms: 56, university_erp: 1 | 191 | 4 |
| DocType | erpnext: 56, frappe: 75, hrms: 6, university_erp: 11 | 148 | 4 |
| User | education: 2, erpnext: 30, frappe: 33, hrms: 14, university_erp: 41 | 120 | 5 |
| Account | education: 3, erpnext: 73, hrms: 16, university_erp: 11 | 103 | 4 |
| Employee | education: 1, erpnext: 18, hrms: 47, university_erp: 34 | 100 | 4 |
| Warehouse | erpnext: 69, university_erp: 17 | 86 | 2 |
| Currency | education: 2, erpnext: 51, frappe: 3, hrms: 19, university_erp: 5 | 80 | 5 |
| Cost Center | education: 3, erpnext: 63, hrms: 8, university_erp: 3 | 77 | 4 |
| Department | education: 4, erpnext: 10, hrms: 46, university_erp: 13 | 73 | 4 |
| UOM | erpnext: 65, university_erp: 6 | 71 | 2 |
| Project | erpnext: 55, hrms: 6 | 61 | 2 |
| Student | education: 13, university_erp: 40 | 53 | 2 |
| Program | education: 17, university_erp: 35 | 52 | 2 |
| Academic Year | education: 18, university_erp: 22 | 40 | 2 |
| Supplier | erpnext: 32, hrms: 3, university_erp: 5 | 40 | 3 |
| Course | education: 11, university_erp: 27 | 38 | 2 |
| Academic Term | education: 18, university_erp: 15 | 33 | 2 |
| Role | erpnext: 8, frappe: 18, hrms: 2, university_erp: 5 | 33 | 4 |
| Letter Head | education: 3, erpnext: 22, frappe: 1, hrms: 4 | 30 | 4 |
| Designation | erpnext: 3, hrms: 25, university_erp: 1 | 29 | 3 |
| Address | erpnext: 26, frappe: 1 | 27 | 2 |
| Price List | erpnext: 24, university_erp: 2 | 26 | 2 |
| Batch | erpnext: 21, university_erp: 4 | 25 | 2 |
| Asset | erpnext: 17, university_erp: 4 | 21 | 2 |
| Material Request | erpnext: 16, university_erp: 5 | 21 | 2 |
| Print Heading | education: 2, erpnext: 17, hrms: 1 | 20 | 3 |
| Mode of Payment | erpnext: 14, hrms: 4, university_erp: 1 | 19 | 3 |
| Instructor | education: 4, university_erp: 14 | 18 | 2 |
| Country | education: 2, erpnext: 10, frappe: 4, hrms: 1 | 17 | 4 |
| Tax Category | erpnext: 16, university_erp: 1 | 17 | 2 |
| Terms and Conditions | education: 1, erpnext: 15, hrms: 1 | 17 | 3 |
| Purchase Order | erpnext: 12, university_erp: 4 | 16 | 2 |
| Payment Terms Template | erpnext: 12, university_erp: 3 | 15 | 2 |
| Bank Account | erpnext: 12, hrms: 1, university_erp: 1 | 14 | 3 |
| Branch | erpnext: 3, hrms: 10 | 13 | 2 |
| Student Group | education: 10, university_erp: 3 | 13 | 2 |
| Email Template | erpnext: 3, frappe: 7, hrms: 2 | 12 | 3 |
| Language | erpnext: 6, frappe: 5, university_erp: 1 | 12 | 3 |
| Report | frappe: 9, university_erp: 3 | 12 | 2 |
| Student Batch Name | education: 9, university_erp: 3 | 12 | 2 |
| Email Account | erpnext: 3, frappe: 6, hrms: 2 | 11 | 3 |
| Holiday List | erpnext: 6, hrms: 5 | 11 | 2 |
| Room | education: 3, university_erp: 7 | 10 | 2 |
| Supplier Group | erpnext: 8, university_erp: 2 | 10 | 2 |
| Gender | education: 4, erpnext: 3, frappe: 2 | 9 | 3 |
| Purchase Taxes and Charges Template | erpnext: 7, university_erp: 2 | 9 | 2 |
| Shift Type | hrms: 8, university_erp: 1 | 9 | 2 |
| Journal Entry | erpnext: 5, hrms: 2, university_erp: 1 | 8 | 3 |
| Purchase Receipt | erpnext: 6, university_erp: 2 | 8 | 2 |
| Grading Scale | education: 4, university_erp: 3 | 7 | 2 |
| ... | 25 more targets | | |

## Recommendations Summary

### Keep erpnext version (more fields)

- Print Heading

### Keep erpnext, migrate 1 custom fields

- Asset Movement Item
- Depreciation Schedule
- Purchase Taxes and Charges

### Keep erpnext, migrate 2 custom fields

- Material Request Item
- Supplier Group

### Keep university_erp, alias education

- Quiz Question

### Keep university_erp, alias erpnext

- Asset Category
- Asset Maintenance
- Industry Type
- Payment Order
- SMS Log
- UOM

### Keep university_erp, alias frappe

- Discussion Reply
- Push Notification Settings

### Keep university_erp, alias hrms

- Grievance Type

### Merge schemas

- Asset
- Asset Movement
- Bank Transaction
- Batch
- Maintenance Team Member
- Material Request
- Purchase Order
- Purchase Order Item
- Purchase Receipt
- Purchase Receipt Item
- Stock Entry
- Stock Ledger Entry
- Stock Reconciliation
- Stock Reconciliation Item
- Supplier
- Warehouse

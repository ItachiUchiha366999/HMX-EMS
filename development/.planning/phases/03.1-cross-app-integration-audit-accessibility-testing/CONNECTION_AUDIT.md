# Cross-App Connection Audit Report

**Generated:** 2026-03-18 23:34:49 UTC

## Executive Summary

- **Total cross-app Link fields tested:** 1029
- **PASS:** 947
- **FAILURE (broken links):** 1
- **WARNING:** 0
- **SKIP (missing table):** 81
- **ERROR:** 0
- **Total broken link records:** 1
- **Dynamic Link groups with cross-app targets:** 2
- **Orphan record checks with warnings:** 1

**Overall Status: FAILURE** -- broken cross-app links detected

## Cross-App Link Inventory

| Source App | Source Doctype | Field | Type | Target App | Target Doctype | Total Records | Broken Count | Broken % | Status |
|-----------|--------------|-------|------|-----------|---------------|-------------:|------------:|--------:|--------|
| university_erp | PO Attainment | department | Link | erpnext | Department | 1 | 1 | 100.0% | FAILURE |
| education | Course | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| education | Fees | company | Link | erpnext | Company | 30 | 0 | 0.0% | PASS |
| education | Fees | currency | Link | frappe | Currency | 30 | 0 | 0.0% | PASS |
| education | Fees | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| education | Fees | select_print_heading | Link | erpnext | Print Heading | 0 | 0 | 0% | PASS |
| education | Fees | receivable_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| education | Fees | income_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| education | Fees | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| education | Fee Schedule | currency | Link | frappe | Currency | 2 | 0 | 0.0% | PASS |
| education | Fee Schedule | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| education | Fee Schedule | select_print_heading | Link | erpnext | Print Heading | 0 | 0 | 0% | PASS |
| education | Fee Schedule | receivable_account | Link | erpnext | Account | 2 | 0 | 0.0% | PASS |
| education | Fee Schedule | income_account | Link | erpnext | Account | 2 | 0 | 0.0% | PASS |
| education | Fee Schedule | cost_center | Link | erpnext | Cost Center | 2 | 0 | 0.0% | PASS |
| education | Fee Schedule | company | Link | erpnext | Company | 2 | 0 | 0.0% | PASS |
| education | Fee Structure | receivable_account | Link | erpnext | Account | 4 | 0 | 0.0% | PASS |
| education | Fee Structure | income_account | Link | erpnext | Account | 4 | 0 | 0.0% | PASS |
| education | Fee Structure | cost_center | Link | erpnext | Cost Center | 4 | 0 | 0.0% | PASS |
| education | Fee Structure | company | Link | erpnext | Company | 4 | 0 | 0.0% | PASS |
| education | Guardian | user | Link | frappe | User | 1 | 0 | 0.0% | PASS |
| education | Instructor | employee | Link | erpnext | Employee | 10 | 0 | 0.0% | PASS |
| education | Instructor | department | Link | erpnext | Department | 10 | 0 | 0.0% | PASS |
| education | Instructor | gender | Link | frappe | Gender | 10 | 0 | 0.0% | PASS |
| education | Instructor Log | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| education | Program | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| education | Student | user | Link | frappe | User | 30 | 0 | 0.0% | PASS |
| education | Student | gender | Link | frappe | Gender | 30 | 0 | 0.0% | PASS |
| education | Student | country | Link | frappe | Country | 30 | 0 | 0.0% | PASS |
| education | Student Applicant | gender | Link | frappe | Gender | 10 | 0 | 0.0% | PASS |
| education | Student Applicant | country | Link | frappe | Country | 10 | 0 | 0.0% | PASS |
| education | Student Report Generation Tool | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | SKIP |
| education | Student Report Generation Tool | terms | Link | erpnext | Terms and Conditions | 0 | 0 | 0% | SKIP |
| education | Student Sibling | gender | Link | frappe | Gender | 0 | 0 | 0% | PASS |
| erpnext | Account | account_currency | Link | frappe | Currency | 75 | 0 | 0.0% | PASS |
| erpnext | Accounting Dimension | document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Accounting Dimension Detail | reference_document | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Accounts Settings | frozen_accounts_modifier | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Accounts Settings | credit_controller | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Accounts Settings | role_allowed_to_over_bill | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Accounts Settings | role_to_override_stop_action | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Account Closing Balance | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Advance Payment Ledger Entry | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Advance Payment Ledger Entry | against_voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Advance Payment Ledger Entry | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Advance Tax | reference_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Advance Taxes and Charges | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Allowed Dimension | accounting_dimension | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bank Account | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bank Clearance | account_currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| erpnext | Bank Clearance Detail | payment_document | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bank Guarantee | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bank Reconciliation Tool | account_currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| erpnext | Bank Statement Import | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bank Transaction | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Bank Transaction | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bank Transaction Payments | payment_document | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Cashier Closing | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Closed Document | document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Dunning | language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| erpnext | Dunning | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Dunning | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Dunning | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Dunning | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Dunning | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Dunning Letter Text | language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| erpnext | Exchange Rate Revaluation Account | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Exchange Rate Revaluation Account | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | GL Entry | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | GL Entry | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | GL Entry | against_voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | GL Entry | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | GL Entry | transaction_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Journal Entry | total_amount_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Journal Entry | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Journal Entry | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Journal Entry Account | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Journal Entry Account | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Journal Entry Account | advance_voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Loyalty Point Entry | invoice_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Opening Invoice Creation Tool Item | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Party Link | primary_role | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Party Link | secondary_role | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Entry | party_type | Link | frappe | DocType | 10 | 0 | 0.0% | PASS |
| erpnext | Payment Entry | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Payment Entry | paid_from_account_currency | Link | frappe | Currency | 10 | 0 | 0.0% | PASS |
| erpnext | Payment Entry | paid_to_account_currency | Link | frappe | Currency | 10 | 0 | 0.0% | PASS |
| erpnext | Payment Entry | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Payment Entry | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Payment Entry Reference | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Entry Reference | advance_voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Ledger Entry | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Ledger Entry | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Ledger Entry | against_voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Ledger Entry | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Payment Order Reference | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Reconciliation | party_type | Link | frappe | DocType | 0 | 0 | 0% | SKIP |
| erpnext | Payment Reconciliation Allocation | reference_type | Link | frappe | DocType | 0 | 0 | 0% | SKIP |
| erpnext | Payment Reconciliation Allocation | invoice_type | Link | frappe | DocType | 0 | 0 | 0% | SKIP |
| erpnext | Payment Reconciliation Allocation | currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| erpnext | Payment Reconciliation Invoice | currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| erpnext | Payment Reconciliation Payment | reference_type | Link | frappe | DocType | 0 | 0 | 0% | SKIP |
| erpnext | Payment Reconciliation Payment | currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| erpnext | Payment Request | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Request | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Payment Request | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Payment Request | party_account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Pegged Currency Details | source_currency | Link | frappe | Currency | 6 | 0 | 0.0% | PASS |
| erpnext | Pegged Currency Details | pegged_against | Link | frappe | Currency | 6 | 0 | 0.0% | PASS |
| erpnext | POS Closing Entry | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | shipping_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | party_account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | POS Invoice | company_contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | POS Opening Entry | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | POS Profile | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | POS Profile | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | POS Profile | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | POS Profile | print_format | Link | frappe | Print Format | 0 | 0 | 0% | PASS |
| erpnext | POS Profile User | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Pricing Rule | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Process Payment Reconciliation | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Process Payment Reconciliation Log Allocations | reference_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Process Payment Reconciliation Log Allocations | invoice_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Process Payment Reconciliation Log Allocations | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Process Statement Of Accounts | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Process Statement Of Accounts | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Process Statement Of Accounts | sender | Link | frappe | Email Account | 0 | 0 | 0% | PASS |
| erpnext | Process Statement Of Accounts CC | cc | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Promotional Scheme | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | shipping_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | party_account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice | dispatch_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Invoice Advance | reference_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Purchase Taxes and Charges | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Repost Accounting Ledger Items | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Repost Allowed Types | document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Repost Payment Ledger | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Repost Payment Ledger Items | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | shipping_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | party_account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | dispatch_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice | company_contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Sales Invoice Advance | reference_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Sales Taxes and Charges | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Shipping Rule Country | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Subscription | party_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Subscription Invoice | document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Subscription Plan | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Tax Rule | billing_country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Tax Rule | shipping_country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Transaction Deletion Record Details | doctype_name | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Unreconcile Payment | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Unreconcile Payment Entries | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Unreconcile Payment Entries | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Asset Activity | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Asset Maintenance Task | assign_to | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Asset Maintenance Team | maintenance_manager | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Asset Movement | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Team Member | team_member | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Team Member | maintenance_role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| erpnext | Bulk Transaction Log Detail | from_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Bulk Transaction Log Detail | to_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Buying Settings | role_to_override_stop_action | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Buying Settings | fixed_email | Link | frappe | Email Account | 0 | 0 | 0% | SKIP |
| erpnext | Purchase Order | customer_contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | shipping_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | party_account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Order | dispatch_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Request for Quotation | email_template | Link | frappe | Email Template | 0 | 0 | 0% | PASS |
| erpnext | Request for Quotation | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Request for Quotation | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Request for Quotation Supplier | contact | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Supplier | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Supplier | language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| erpnext | Supplier | default_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Supplier | supplier_primary_contact | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Supplier | supplier_primary_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | shipping_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Supplier Quotation | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Appointment | calendar_event | Link | frappe | Event | 0 | 0 | 0% | PASS |
| erpnext | Appointment | appointment_with | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Campaign Email Schedule | email_template | Link | frappe | Email Template | 0 | 0 | 0% | PASS |
| erpnext | Contract | party_user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Contract | signed_by_company | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | CRM Note | added_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Email Campaign | sender | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Lead | lead_owner | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Lead | salutation | Link | frappe | Salutation | 0 | 0 | 0% | PASS |
| erpnext | Lead | gender | Link | frappe | Gender | 0 | 0 | 0% | PASS |
| erpnext | Lead | language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| erpnext | Lead | qualified_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Lead | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | opportunity_from | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | opportunity_owner | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Opportunity | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Prospect | prospect_owner | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Prospect Opportunity | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Prospect Opportunity | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Schedule | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Schedule | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Visit | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Visit | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Maintenance Visit Purpose | prevdoc_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | BOM | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | BOM | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | BOM Creator | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | BOM Creator | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | BOM Update Log | error_log | Link | frappe | Error Log | 0 | 0 | 0% | PASS |
| erpnext | Homepage | slideshow | Link | frappe | Website Slideshow | 0 | 0 | 0% | SKIP |
| erpnext | Project User | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Task | completed_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Timesheet | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Timesheet | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Quality Action Resolution | responsible | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Quality Procedure | process_owner | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Customer | salutation | Link | frappe | Salutation | 0 | 0 | 0% | PASS |
| erpnext | Customer | gender | Link | frappe | Gender | 0 | 0 | 0% | PASS |
| erpnext | Customer | account_manager | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Customer | default_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Customer | language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| erpnext | Customer | customer_primary_contact | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Customer | customer_primary_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Installation Note | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Installation Note | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Quotation | quotation_to | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Quotation | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Quotation | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Quotation | shipping_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Quotation | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Quotation | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Quotation | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Quotation | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Quotation | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Quotation | company_contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Quotation Item | prevdoc_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | shipping_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | party_account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | dispatch_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Sales Order | company_contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Selling Settings | role_to_override_stop_action | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Authorization Rule | system_role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| erpnext | Authorization Rule | system_user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Authorization Rule | approving_role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| erpnext | Authorization Rule | approving_user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Company | default_currency | Link | frappe | Currency | 1 | 0 | 0.0% | PASS |
| erpnext | Company | default_letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Company | country | Link | frappe | Country | 1 | 0 | 0.0% | PASS |
| erpnext | Company | exception_budget_approver_role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| erpnext | Company | default_sales_contact | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Currency Exchange | from_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Currency Exchange | to_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Driver | address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Email Digest Recipient | recipient | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Employee | salutation | Link | frappe | Salutation | 0 | 0 | 0% | PASS |
| erpnext | Employee | gender | Link | frappe | Gender | 15 | 0 | 0.0% | PASS |
| erpnext | Employee | user_id | Link | frappe | User | 3 | 0 | 0.0% | PASS |
| erpnext | Employee | salary_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Global Defaults | country | Link | frappe | Country | 0 | 0 | 0% | SKIP |
| erpnext | Global Defaults | default_currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| erpnext | Party Type | party_type | Link | frappe | DocType | 5 | 0 | 0.0% | PASS |
| erpnext | Transaction Deletion Record Item | doctype_name | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Batch | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | shipping_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | company_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | dispatch_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Delivery Note | company_contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Delivery Settings | dispatch_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| erpnext | Delivery Settings | dispatch_attachment | Link | frappe | Print Format | 0 | 0 | 0% | SKIP |
| erpnext | Delivery Stop | address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Delivery Stop | contact | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Delivery Trip | driver_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Inventory Dimension | reference_document | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Inventory Dimension | document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Item | country_of_origin | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Item Price | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Landed Cost Taxes and Charges | account_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Manufacturer | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Material Request | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Packing Slip | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Price List | currency | Link | frappe | Currency | 2 | 0 | 0.0% | PASS |
| erpnext | Price List Country | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | shipping_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | price_list_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Purchase Receipt | dispatch_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Quality Inspection | inspected_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Quality Inspection | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Repost Item Valuation | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Serial and Batch Bundle | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Shipment | pickup_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Shipment | pickup_contact_name | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Shipment | delivery_address_name | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Shipment | delivery_contact_name | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Shipment | pickup_contact_person | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Stock Entry | source_warehouse_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Stock Entry | target_warehouse_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Stock Entry | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Stock Entry | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Stock Ledger Entry | voucher_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Stock Reposting Settings | notify_reposting_error_to_role | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Stock Settings | stock_auth_role | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Stock Settings | role_allowed_to_create_edit_back_dated_transactions | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Stock Settings | role_allowed_to_over_deliver_receive | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| erpnext | Subcontracting Order | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Order | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Order | shipping_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Order | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Order | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Receipt | supplier_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Receipt | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Receipt | shipping_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Receipt | auto_repeat | Link | frappe | Auto Repeat | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Receipt | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| erpnext | Subcontracting Receipt | billing_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Issue | contact | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Issue | email_account | Link | frappe | Email Account | 0 | 0 | 0% | PASS |
| erpnext | Service Level Agreement | document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Support Search Source | source_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| erpnext | Warranty Claim | resolved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Warranty Claim | contact_person | Link | frappe | Contact | 0 | 0 | 0% | PASS |
| erpnext | Warranty Claim | customer_address | Link | frappe | Address | 0 | 0 | 0% | PASS |
| erpnext | Call Log | employee_user_id | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Voice Call Settings | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Portal User | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| erpnext | Rename Tool | select_doctype | Link | frappe | DocType | 0 | 0 | 0% | SKIP |
| hrms | Appointment Letter | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Appraisal | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Appraisal | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Appraisal | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Appraisal | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Appraisal Cycle | branch | Link | erpnext | Branch | 0 | 0 | 0% | PASS |
| hrms | Appraisal Cycle | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Appraisal Cycle | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Appraisal Cycle | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Appraisee | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Appraisee | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Appraisee | branch | Link | erpnext | Branch | 0 | 0 | 0% | PASS |
| hrms | Attendance | employee | Link | erpnext | Employee | 15 | 0 | 0.0% | PASS |
| hrms | Attendance | company | Link | erpnext | Company | 15 | 0 | 0.0% | PASS |
| hrms | Attendance | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Attendance Request | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Attendance Request | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Attendance Request | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Compensatory Leave Request | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Compensatory Leave Request | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Daily Work Summary Group | holiday_list | Link | erpnext | Holiday List | 0 | 0 | 0% | PASS |
| hrms | Daily Work Summary Group User | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Department Approver | approver | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Employee Advance | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Advance | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Advance | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Advance | advance_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Employee Advance | mode_of_payment | Link | erpnext | Mode of Payment | 0 | 0 | 0% | PASS |
| hrms | Employee Advance | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Attendance Tool | department | Link | erpnext | Department | 0 | 0 | 0% | SKIP |
| hrms | Employee Attendance Tool | branch | Link | erpnext | Branch | 0 | 0 | 0% | SKIP |
| hrms | Employee Attendance Tool | company | Link | erpnext | Company | 0 | 0 | 0% | SKIP |
| hrms | Employee Attendance Tool | designation | Link | erpnext | Designation | 0 | 0 | 0% | SKIP |
| hrms | Employee Boarding Activity | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Employee Boarding Activity | role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| hrms | Employee Boarding Activity | task | Link | erpnext | Task | 0 | 0 | 0% | PASS |
| hrms | Employee Checkin | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Grade | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | resolved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | employee_responsible | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | raised_by | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | reports_to | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | grievance_against_party | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| hrms | Employee Grievance | associated_document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding | project | Link | erpnext | Project | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding | holiday_list | Link | erpnext | Holiday List | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding Template | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding Template | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Onboarding Template | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | reviewer_designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | reviewer | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Employee Performance Feedback | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Promotion | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Promotion | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Promotion | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Promotion | salary_currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Referral | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Referral | for_designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Referral | referrer | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Separation | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Separation | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Separation | project | Link | erpnext | Project | 0 | 0 | 0% | PASS |
| hrms | Employee Separation | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Separation | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Separation Template | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Separation Template | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Separation Template | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Employee Skill Map | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Transfer | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Transfer | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Transfer | new_company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Transfer | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Transfer | new_employee_id | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Exit Interview | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Exit Interview | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Exit Interview | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Exit Interview | ref_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| hrms | Exit Interview | reports_to | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Exit Interview | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | expense_approver | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | project | Link | erpnext | Project | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | task | Link | erpnext | Task | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | mode_of_payment | Link | erpnext | Mode of Payment | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | payable_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Expense Claim | delivery_trip | Link | erpnext | Delivery Trip | 0 | 0 | 0% | PASS |
| hrms | Expense Claim Account | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Expense Claim Account | default_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Expense Claim Advance | advance_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Expense Claim Detail | default_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Expense Claim Detail | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Expense Claim Detail | project | Link | erpnext | Project | 0 | 0 | 0% | PASS |
| hrms | Expense Taxes and Charges | account_head | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Expense Taxes and Charges | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Expense Taxes and Charges | project | Link | erpnext | Project | 0 | 0 | 0% | PASS |
| hrms | Full and Final Asset | reference | Link | erpnext | Asset Movement | 0 | 0 | 0% | PASS |
| hrms | Full and Final Asset | account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Full and Final Outstanding Statement | account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Full and Final Outstanding Statement | reference_document_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| hrms | Full and Final Statement | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Full and Final Statement | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Full and Final Statement | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Full and Final Statement | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Goal | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Goal | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | HR Settings | role_allowed_to_create_backdated_leave_application | Link | frappe | Role | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | leave_approval_notification_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | leave_status_notification_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | feedback_reminder_notification_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | interview_reminder_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | exit_questionnaire_web_form | Link | frappe | Web Form | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | exit_questionnaire_notification_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | sender | Link | frappe | Email Account | 0 | 0 | 0% | SKIP |
| hrms | HR Settings | hiring_sender | Link | frappe | Email Account | 0 | 0 | 0% | SKIP |
| hrms | Interview | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Interviewer | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Interview Detail | interviewer | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Interview Feedback | interviewer | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Interview Round | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Job Applicant | source_name | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Job Applicant | country | Link | frappe | Country | 0 | 0 | 0% | PASS |
| hrms | Job Applicant | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Job Applicant | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Job Offer | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Job Offer | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Job Offer | select_terms | Link | erpnext | Terms and Conditions | 0 | 0 | 0% | PASS |
| hrms | Job Offer | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| hrms | Job Offer | select_print_heading | Link | erpnext | Print Heading | 0 | 0 | 0% | PASS |
| hrms | Job Opening | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Job Opening | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Job Opening | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Job Opening | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Job Opening | location | Link | erpnext | Branch | 0 | 0 | 0% | PASS |
| hrms | Job Opening Template | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Job Opening Template | location | Link | erpnext | Branch | 0 | 0 | 0% | PASS |
| hrms | Job Requisition | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Job Requisition | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Job Requisition | requested_by | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Job Requisition | requested_by_dept | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Job Requisition | requested_by_designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Job Requisition | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Leave Allocation | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Leave Allocation | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Leave Allocation | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Leave Application | employee | Link | erpnext | Employee | 5 | 0 | 0.0% | PASS |
| hrms | Leave Application | department | Link | erpnext | Department | 5 | 0 | 0.0% | PASS |
| hrms | Leave Application | leave_approver | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Leave Application | company | Link | erpnext | Company | 5 | 0 | 0.0% | PASS |
| hrms | Leave Application | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| hrms | Leave Block List | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Leave Block List Allow | allow_user | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Leave Control Panel | company | Link | erpnext | Company | 0 | 0 | 0% | SKIP |
| hrms | Leave Control Panel | branch | Link | erpnext | Branch | 0 | 0 | 0% | SKIP |
| hrms | Leave Control Panel | department | Link | erpnext | Department | 0 | 0 | 0% | SKIP |
| hrms | Leave Control Panel | designation | Link | erpnext | Designation | 0 | 0 | 0% | SKIP |
| hrms | Leave Encashment | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Leave Encashment | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Leave Encashment | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Leave Encashment | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Leave Encashment | payable_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Leave Encashment | expense_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Leave Encashment | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Leave Ledger Entry | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Leave Ledger Entry | transaction_type | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| hrms | Leave Ledger Entry | holiday_list | Link | erpnext | Holiday List | 0 | 0 | 0% | PASS |
| hrms | Leave Ledger Entry | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Leave Period | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Leave Period | optional_holiday_list | Link | erpnext | Holiday List | 0 | 0 | 0% | PASS |
| hrms | Leave Policy Assignment | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Leave Policy Assignment | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | PWA Notification | from_user | Link | frappe | User | 3 | 0 | 0.0% | PASS |
| hrms | PWA Notification | to_user | Link | frappe | User | 3 | 0 | 0.0% | PASS |
| hrms | PWA Notification | reference_document_type | Link | frappe | DocType | 3 | 0 | 0.0% | PASS |
| hrms | Shift Assignment | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Shift Assignment | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Shift Assignment | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Shift Assignment Tool | company | Link | erpnext | Company | 0 | 0 | 0% | SKIP |
| hrms | Shift Assignment Tool | branch | Link | erpnext | Branch | 0 | 0 | 0% | SKIP |
| hrms | Shift Assignment Tool | department | Link | erpnext | Department | 0 | 0 | 0% | SKIP |
| hrms | Shift Assignment Tool | designation | Link | erpnext | Designation | 0 | 0 | 0% | SKIP |
| hrms | Shift Assignment Tool | approver | Link | frappe | User | 0 | 0 | 0% | SKIP |
| hrms | Shift Request | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Shift Request | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Shift Request | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Shift Request | approver | Link | frappe | User | 0 | 0 | 0% | PASS |
| hrms | Shift Schedule Assignment | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Shift Schedule Assignment | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Shift Type | holiday_list | Link | erpnext | Holiday List | 0 | 0 | 0% | PASS |
| hrms | Staffing Plan | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Staffing Plan | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Staffing Plan Detail | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Training Event | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Training Event | supplier | Link | erpnext | Supplier | 0 | 0 | 0% | PASS |
| hrms | Training Event Employee | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Training Event Employee | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Training Feedback | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Training Feedback | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Training Program | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Training Program | supplier | Link | erpnext | Supplier | 0 | 0 | 0% | PASS |
| hrms | Training Result Employee | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Training Result Employee | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Travel Request | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Travel Request | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Travel Request | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Vehicle Log | license_plate | Link | erpnext | Vehicle | 0 | 0 | 0% | PASS |
| hrms | Vehicle Log | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Vehicle Log | supplier | Link | erpnext | Supplier | 0 | 0 | 0% | PASS |
| hrms | Additional Salary | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Additional Salary | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Additional Salary | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Additional Salary | ref_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| hrms | Additional Salary | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Bulk Salary Structure Assignment | payroll_payable_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| hrms | Bulk Salary Structure Assignment | branch | Link | erpnext | Branch | 0 | 0 | 0% | SKIP |
| hrms | Bulk Salary Structure Assignment | department | Link | erpnext | Department | 0 | 0 | 0% | SKIP |
| hrms | Bulk Salary Structure Assignment | designation | Link | erpnext | Designation | 0 | 0 | 0% | SKIP |
| hrms | Bulk Salary Structure Assignment | company | Link | erpnext | Company | 0 | 0 | 0% | SKIP |
| hrms | Bulk Salary Structure Assignment | currency | Link | frappe | Currency | 0 | 0 | 0% | SKIP |
| hrms | Employee Benefit Application | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Application | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Application | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Application | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Claim | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Claim | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Claim | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Benefit Claim | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Cost Center | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Employee Incentive | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Incentive | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Incentive | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Incentive | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Other Income | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Other Income | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Declaration | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Declaration | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Declaration | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Declaration | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Proof Submission | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Proof Submission | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Proof Submission | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Employee Tax Exemption Proof Submission | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Gratuity | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Gratuity | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Gratuity | expense_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Gratuity | mode_of_payment | Link | erpnext | Mode of Payment | 0 | 0 | 0% | PASS |
| hrms | Gratuity | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Gratuity | payable_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Gratuity | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Income Tax Slab | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Income Tax Slab | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Payroll Employee Detail | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Payroll Employee Detail | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | branch | Link | erpnext | Branch | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | project | Link | erpnext | Project | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | payment_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | bank_account | Link | erpnext | Bank Account | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Payroll Entry | payroll_payable_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Payroll Period | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Payroll Settings | sender | Link | frappe | Email Account | 0 | 0 | 0% | SKIP |
| hrms | Payroll Settings | email_template | Link | frappe | Email Template | 0 | 0 | 0% | SKIP |
| hrms | Retention Bonus | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Retention Bonus | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Retention Bonus | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Retention Bonus | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Salary Component Account | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Salary Component Account | account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | branch | Link | erpnext | Branch | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | journal_entry | Link | erpnext | Journal Entry | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| hrms | Salary Slip | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Salary Slip Loan | loan_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Salary Slip Loan | interest_income_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Salary Slip Timesheet | time_sheet | Link | erpnext | Timesheet | 0 | 0 | 0% | PASS |
| hrms | Salary Structure | company | Link | erpnext | Company | 2 | 0 | 0.0% | PASS |
| hrms | Salary Structure | letter_head | Link | frappe | Letter Head | 0 | 0 | 0% | PASS |
| hrms | Salary Structure | mode_of_payment | Link | erpnext | Mode of Payment | 0 | 0 | 0% | PASS |
| hrms | Salary Structure | payment_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Salary Structure | currency | Link | frappe | Currency | 2 | 0 | 0.0% | PASS |
| hrms | Salary Structure Assignment | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Salary Structure Assignment | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| hrms | Salary Structure Assignment | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| hrms | Salary Structure Assignment | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Salary Structure Assignment | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| hrms | Salary Structure Assignment | payroll_payable_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| hrms | Salary Withholding | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| hrms | Salary Withholding | company | Link | erpnext | Company | 0 | 0 | 0% | PASS |
| hrms | Salary Withholding Cycle | journal_entry | Link | erpnext | Journal Entry | 0 | 0 | 0% | PASS |
| university_erp | Faculty Profile | employee | Link | erpnext | Employee | 10 | 0 | 0.0% | PASS |
| university_erp | Faculty Profile | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Faculty Profile | designation | Link | erpnext | Designation | 0 | 0 | 0% | PASS |
| university_erp | Leave Affected Course | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Leave Affected Course | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Leave Affected Course | substitute_faculty | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Student Feedback | student | Link | education | Student | 10 | 0 | 0.0% | PASS |
| university_erp | Student Feedback | academic_year | Link | education | Academic Year | 10 | 0 | 0.0% | PASS |
| university_erp | Student Feedback | academic_term | Link | education | Academic Term | 10 | 0 | 0.0% | PASS |
| university_erp | Student Feedback | course | Link | education | Course | 10 | 0 | 0.0% | PASS |
| university_erp | Student Feedback | instructor | Link | erpnext | Employee | 10 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | academic_year | Link | education | Academic Year | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | academic_term | Link | education | Academic Term | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | course | Link | education | Course | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | program | Link | education | Program | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | instructor | Link | erpnext | Employee | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | instructor_department | Link | erpnext | Department | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | room | Link | education | Room | 12 | 0 | 0.0% | PASS |
| university_erp | Teaching Assignment | co_instructor | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Teaching Assignment Schedule | room | Link | education | Room | 24 | 0 | 0.0% | PASS |
| university_erp | Temporary Teaching Assignment | leave_application | Link | hrms | Leave Application | 0 | 0 | 0% | PASS |
| university_erp | Temporary Teaching Assignment | original_instructor | Link | erpnext | Employee | 3 | 0 | 0.0% | PASS |
| university_erp | Temporary Teaching Assignment | substitute_instructor | Link | erpnext | Employee | 3 | 0 | 0.0% | PASS |
| university_erp | Temporary Teaching Assignment | course | Link | education | Course | 3 | 0 | 0.0% | PASS |
| university_erp | Temporary Teaching Assignment | program | Link | education | Program | 3 | 0 | 0.0% | PASS |
| university_erp | Workload Distributor | academic_year | Link | education | Academic Year | 1 | 0 | 0.0% | PASS |
| university_erp | Workload Distributor | academic_term | Link | education | Academic Term | 1 | 0 | 0.0% | PASS |
| university_erp | Workload Distributor | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Workload Distributor | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Course Prerequisite | prerequisite_course | Link | education | Course | 5 | 0 | 0.0% | PASS |
| university_erp | Course Registration | student | Link | education | Student | 10 | 0 | 0.0% | PASS |
| university_erp | Course Registration | academic_term | Link | education | Academic Term | 10 | 0 | 0.0% | PASS |
| university_erp | Course Registration | program | Link | education | Program | 10 | 0 | 0.0% | PASS |
| university_erp | Course Registration Item | course | Link | education | Course | 50 | 0 | 0.0% | PASS |
| university_erp | Elective Course Group | program | Link | education | Program | 2 | 0 | 0.0% | PASS |
| university_erp | Elective Course Group Item | course | Link | education | Course | 4 | 0 | 0.0% | PASS |
| university_erp | Admission Criteria | program | Link | education | Program | 3 | 0 | 0.0% | PASS |
| university_erp | Admission Cycle | academic_year | Link | education | Academic Year | 1 | 0 | 0.0% | PASS |
| university_erp | Admission Cycle Program | program | Link | education | Program | 4 | 0 | 0.0% | PASS |
| university_erp | Merit List | program | Link | education | Program | 1 | 0 | 0.0% | PASS |
| university_erp | Merit List Applicant | applicant | Link | education | Student Applicant | 3 | 0 | 0.0% | PASS |
| university_erp | Seat Matrix | program | Link | education | Program | 4 | 0 | 0.0% | PASS |
| university_erp | Custom Dashboard | owner_role | Link | frappe | Role | 1 | 0 | 0.0% | PASS |
| university_erp | Custom Report Definition | primary_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Dashboard Role | role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| university_erp | Dashboard User | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Dashboard Widget | report_name | Link | frappe | Report | 0 | 0 | 0% | PASS |
| university_erp | KPI Definition | responsible_role | Link | frappe | Role | 5 | 0 | 0.0% | PASS |
| university_erp | KPI Definition | data_owner | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | KPI Value | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | KPI Value | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | KPI Value | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Report Access Role | role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| university_erp | Report Join Definition | doctype_link | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Scheduled Report | report | Link | frappe | Report | 0 | 0 | 0% | PASS |
| university_erp | Scheduled Report Recipient | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Emergency Acknowledgment | user | Link | frappe | User | 1 | 0 | 0.0% | PASS |
| university_erp | Emergency Alert | initiated_by | Link | frappe | User | 2 | 0 | 0.0% | PASS |
| university_erp | Emergency Alert | resolved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | NAAC Metric | report_name | Link | frappe | Report | 0 | 0 | 0% | PASS |
| university_erp | NAAC Metric | verified_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | NAAC Metric Year Data | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Notice Target Department | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Notice Target Program | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Notice View Log | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Notification Preference | user | Link | frappe | User | 5 | 0 | 0.0% | PASS |
| university_erp | Notification Preference | preferred_language | Link | frappe | Language | 0 | 0 | 0% | PASS |
| university_erp | Payment Webhook Log | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Payment Webhook Log | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| university_erp | Suggestion | reviewed_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Suggestion | assigned_to | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | University Department | hod | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | University Laboratory | in_charge | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | University Settings | default_academic_year | Link | education | Academic Year | 0 | 0 | 0% | SKIP |
| university_erp | University Settings | default_grading_scale | Link | education | Grading Scale | 0 | 0 | 0% | SKIP |
| university_erp | User Notification | user | Link | frappe | User | 10 | 0 | 0.0% | PASS |
| university_erp | User Notification | link_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | collected_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | exam_center | Link | education | Room | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | room | Link | education | Room | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | invigilator | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | assigned_to | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet | moderated_by | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Answer Sheet Tracking Log | performed_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Exam Invigilator | instructor | Link | education | Instructor | 6 | 0 | 0.0% | PASS |
| university_erp | Exam Schedule | course | Link | education | Course | 6 | 0 | 0.0% | PASS |
| university_erp | Exam Schedule | academic_term | Link | education | Academic Term | 6 | 0 | 0.0% | PASS |
| university_erp | Exam Schedule | venue | Link | education | Room | 6 | 0 | 0.0% | PASS |
| university_erp | Generated Question Paper | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Generated Question Paper | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Generated Question Paper | academic_term | Link | education | Academic Term | 0 | 0 | 0% | PASS |
| university_erp | Generated Question Paper | created_by | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Generated Question Paper | reviewed_by | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Generated Question Paper | approved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Hall Ticket | student | Link | education | Student | 30 | 0 | 0.0% | PASS |
| university_erp | Hall Ticket | academic_term | Link | education | Academic Term | 30 | 0 | 0.0% | PASS |
| university_erp | Hall Ticket Exam | course | Link | education | Course | 70 | 0 | 0.0% | PASS |
| university_erp | Hall Ticket Exam | venue | Link | education | Room | 68 | 0 | 0.0% | PASS |
| university_erp | Internal Assessment | academic_year | Link | education | Academic Year | 12 | 0 | 0.0% | PASS |
| university_erp | Internal Assessment | academic_term | Link | education | Academic Term | 12 | 0 | 0.0% | PASS |
| university_erp | Internal Assessment | course | Link | education | Course | 12 | 0 | 0.0% | PASS |
| university_erp | Internal Assessment | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Internal Assessment | student_group | Link | education | Student Group | 0 | 0 | 0% | PASS |
| university_erp | Internal Assessment | grading_scale | Link | education | Grading Scale | 0 | 0 | 0% | PASS |
| university_erp | Internal Assessment | instructor | Link | education | Instructor | 12 | 0 | 0.0% | PASS |
| university_erp | Internal Assessment | evaluator | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Internal Assessment Score | student | Link | education | Student | 136 | 0 | 0.0% | PASS |
| university_erp | Internal Assessment Score | evaluated_by | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Online Examination | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Online Examination | student_group | Link | education | Student Group | 0 | 0 | 0% | PASS |
| university_erp | Online Examination | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Online Exam Student | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | academic_term | Link | education | Academic Term | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | venue | Link | education | Room | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | grading_scale | Link | education | Grading Scale | 0 | 0 | 0% | PASS |
| university_erp | Practical Examination | coordinator | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Practical Exam Examiner | faculty_member | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Practical Exam Slot | room | Link | education | Room | 0 | 0 | 0% | PASS |
| university_erp | Practical Exam Slot | assigned_examiner | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Practical Exam Student Score | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Practical Exam Student Score | internal_examiner | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Question Bank | course | Link | education | Course | 30 | 0 | 0.0% | PASS |
| university_erp | Question Bank | unit | Link | education | Topic | 0 | 0 | 0% | PASS |
| university_erp | Question Bank | created_by_faculty | Link | education | Instructor | 30 | 0 | 0.0% | PASS |
| university_erp | Question Bank | reviewed_by | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Question Paper Template | course | Link | education | Course | 3 | 0 | 0.0% | PASS |
| university_erp | Revaluation Request | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Revaluation Request | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Revaluation Request | assigned_evaluator | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Student Exam Attempt | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Student Exam Attempt | evaluated_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Student Transcript | student | Link | education | Student | 5 | 0 | 0.0% | PASS |
| university_erp | Student Transcript | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Student Transcript | issued_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Transcript Semester Result | academic_term | Link | education | Academic Term | 0 | 0 | 0% | PASS |
| university_erp | Feedback Course Filter | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Feedback Department Filter | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Feedback Form | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Feedback Form | academic_term | Link | education | Academic Term | 0 | 0 | 0% | PASS |
| university_erp | Feedback Program Filter | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Feedback Response | student | Link | education | Student | 10 | 0 | 0.0% | PASS |
| university_erp | Feedback Response | faculty | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Feedback Response | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Feedback Response | instructor | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Bulk Fee Generator | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Bulk Fee Generator | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Bulk Fee Generator | semester | Link | education | Academic Term | 0 | 0 | 0% | PASS |
| university_erp | Bulk Fee Generator | fee_structure | Link | education | Fee Structure | 0 | 0 | 0% | PASS |
| university_erp | Bulk Fee Generator | student_batch | Link | education | Student Batch Name | 0 | 0 | 0% | PASS |
| university_erp | Bulk Fee Generator Student | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Student Scholarship | student | Link | education | Student | 5 | 0 | 0.0% | PASS |
| university_erp | Student Scholarship | fee_category | Link | education | Fee Category | 0 | 0 | 0% | PASS |
| university_erp | Grievance | grievance_type | Link | hrms | Grievance Type | 2 | 0 | 0.0% | PASS |
| university_erp | Grievance | student | Link | education | Student | 2 | 0 | 0.0% | PASS |
| university_erp | Grievance | faculty | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Grievance | guardian | Link | education | Guardian | 0 | 0 | 0% | PASS |
| university_erp | Grievance | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Grievance | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Grievance | assigned_to | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance | resolved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Action | taken_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Committee | chairperson | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Committee | secretary | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Communication | sent_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Escalation Log | escalated_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Escalation Log | previous_assignee | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Escalation Log | new_assignee | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Grievance Escalation Rule | assignee | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Hostel Allocation | student | Link | education | Student | 15 | 0 | 0.0% | PASS |
| university_erp | Hostel Allocation | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Hostel Allocation | academic_year | Link | education | Academic Year | 15 | 0 | 0.0% | PASS |
| university_erp | Hostel Allocation | fee_reference | Link | education | Fees | 0 | 0 | 0% | PASS |
| university_erp | Hostel Attendance | student | Link | education | Student | 30 | 0 | 0.0% | PASS |
| university_erp | Hostel Attendance Record | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Hostel Building | warden | Link | erpnext | Employee | 3 | 0 | 0.0% | PASS |
| university_erp | Hostel Building | assistant_warden | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Hostel Bulk Attendance | marked_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Hostel Maintenance Request | requested_by | Link | education | Student | 2 | 0 | 0.0% | PASS |
| university_erp | Hostel Maintenance Request | assigned_to | Link | erpnext | Employee | 2 | 0 | 0.0% | PASS |
| university_erp | Hostel Mess | mess_incharge | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Hostel Room Occupant | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Hostel Visitor | student | Link | education | Student | 5 | 0 | 0.0% | PASS |
| university_erp | Hostel Visitor | approved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Mess Menu | prepared_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Mess Menu | approved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Biometric Attendance Log | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Biometric Attendance Log | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Biometric Attendance Log | attendance_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Biometric Device | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Biometric Device | default_shift | Link | hrms | Shift Type | 0 | 0 | 0% | PASS |
| university_erp | Certificate Request | student | Link | education | Student | 2 | 0 | 0.0% | PASS |
| university_erp | Certificate Request | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Certificate Request | approved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Certificate Template | approver_role | Link | frappe | Role | 0 | 0 | 0% | PASS |
| university_erp | Certificate Template | approval_workflow | Link | frappe | Workflow | 0 | 0 | 0% | PASS |
| university_erp | DigiLocker Issued Document | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | DigiLocker Issued Document | issued_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | DigiLocker Issued Document | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Email Queue Extended | email_queue_reference | Link | frappe | Email Queue | 0 | 0 | 0% | PASS |
| university_erp | Payment Transaction | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Payment Transaction | reference_doctype | Link | frappe | DocType | 0 | 0 | 0% | PASS |
| university_erp | Payment Transaction | currency | Link | frappe | Currency | 0 | 0 | 0% | PASS |
| university_erp | Push Notification Log | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | User Device Token | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item | unit_of_measure | Link | erpnext | UOM | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item | default_warehouse | Link | erpnext | Warehouse | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item | default_supplier | Link | erpnext | Supplier | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item | expense_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item | inventory_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item Group | default_expense_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| university_erp | Inventory Item Group | default_warehouse | Link | erpnext | Warehouse | 0 | 0 | 0% | PASS |
| university_erp | Lab Consumable Issue | issued_by | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Lab Consumable Issue | issued_to | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Lab Consumable Issue | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Lab Consumable Issue Item | uom | Link | erpnext | UOM | 0 | 0 | 0% | PASS |
| university_erp | Lab Consumable Issue Item | warehouse | Link | erpnext | Warehouse | 0 | 0 | 0% | PASS |
| university_erp | Lab Equipment | asset | Link | erpnext | Asset | 0 | 0 | 0% | PASS |
| university_erp | Lab Equipment Booking | booked_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Lab Equipment Booking | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | Lab Equipment Booking | approved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Maintenance Team | team_lead | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Stock Entry Item | uom | Link | erpnext | UOM | 0 | 0 | 0% | PASS |
| university_erp | Stock Entry Item | s_warehouse | Link | erpnext | Warehouse | 0 | 0 | 0% | PASS |
| university_erp | Stock Entry Item | t_warehouse | Link | erpnext | Warehouse | 0 | 0 | 0% | PASS |
| university_erp | Stock Entry Item | batch_no | Link | erpnext | Batch | 0 | 0 | 0% | PASS |
| university_erp | Library Fine | fee_reference | Link | education | Fees | 0 | 0 | 0% | PASS |
| university_erp | Library Member | student | Link | education | Student | 10 | 0 | 0.0% | PASS |
| university_erp | Library Member | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Assignment Submission | student | Link | education | Student | 20 | 0 | 0.0% | PASS |
| university_erp | Assignment Submission | graded_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | LMS Content Progress | student | Link | education | Student | 30 | 0 | 0.0% | PASS |
| university_erp | LMS Course | course | Link | education | Course | 6 | 0 | 0.0% | PASS |
| university_erp | LMS Course | academic_term | Link | education | Academic Term | 6 | 0 | 0.0% | PASS |
| university_erp | LMS Course | instructor | Link | erpnext | Employee | 6 | 0 | 0.0% | PASS |
| university_erp | LMS Discussion | student | Link | education | Student | 3 | 0 | 0.0% | PASS |
| university_erp | LMS Discussion | instructor | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Quiz Attempt | student | Link | education | Student | 15 | 0 | 0.0% | PASS |
| university_erp | Accreditation Criterion | responsible_person | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Accreditation Cycle | coordinator | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Accreditation Department Link | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Accreditation Program Link | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Accreditation Team Member | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Assessment Rubric | course | Link | education | Course | 3 | 0 | 0.0% | PASS |
| university_erp | Assessment Rubric | created_by | Link | education | Instructor | 0 | 0 | 0% | PASS |
| university_erp | Committee Member | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Course Outcome | course | Link | education | Course | 15 | 0 | 0.0% | PASS |
| university_erp | Course Outcome | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | CO Attainment | course | Link | education | Course | 6 | 0 | 0.0% | PASS |
| university_erp | CO Attainment | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | CO Attainment | academic_term | Link | education | Academic Term | 6 | 0 | 0.0% | PASS |
| university_erp | CO Attainment | academic_year | Link | education | Academic Year | 6 | 0 | 0.0% | PASS |
| university_erp | CO Attainment | student_group | Link | education | Student Group | 0 | 0 | 0% | PASS |
| university_erp | CO Attainment | instructor | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | CO PO Mapping | course | Link | education | Course | 3 | 0 | 0.0% | PASS |
| university_erp | CO PO Mapping | program | Link | education | Program | 3 | 0 | 0.0% | PASS |
| university_erp | CO PO Mapping | academic_term | Link | education | Academic Term | 3 | 0 | 0.0% | PASS |
| university_erp | CO PO Mapping | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | CO PO Mapping | prepared_by | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | CO PO Mapping | approved_by | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | OBE Survey | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | OBE Survey | course | Link | education | Course | 0 | 0 | 0% | PASS |
| university_erp | OBE Survey | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | OBE Survey | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | OBE Survey | batch | Link | education | Student Batch Name | 0 | 0 | 0% | PASS |
| university_erp | PO Attainment | program | Link | education | Program | 1 | 0 | 0.0% | PASS |
| university_erp | PO Attainment | academic_year | Link | education | Academic Year | 1 | 0 | 0.0% | PASS |
| university_erp | PO Attainment | batch | Link | education | Student Batch Name | 0 | 0 | 0% | PASS |
| university_erp | PO Attainment | prepared_by | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Program Educational Objective | program | Link | education | Program | 4 | 0 | 0.0% | PASS |
| university_erp | Program Educational Objective | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Program Outcome | program | Link | education | Program | 12 | 0 | 0.0% | PASS |
| university_erp | Program Outcome | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Survey Template | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Unit Distribution Rule | unit | Link | education | Topic | 0 | 0 | 0% | PASS |
| university_erp | Fee Category Account | fees_category | Link | education | Fee Category | 0 | 0 | 0% | PASS |
| university_erp | Fee Category Account | income_account | Link | erpnext | Account | 0 | 0 | 0% | PASS |
| university_erp | Fee Category Account | cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | PASS |
| university_erp | Fee Refund | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Fee Refund | fees | Link | education | Fees | 0 | 0 | 0% | PASS |
| university_erp | Fee Refund | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Fee Refund | payment_entry | Link | erpnext | Payment Entry | 0 | 0 | 0% | PASS |
| university_erp | Fee Refund | approved_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | PayU Settings | fee_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | PayU Settings | payment_gateway_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | Razorpay Settings | fee_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | Razorpay Settings | payment_gateway_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | company | Link | erpnext | Company | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | default_cost_center | Link | erpnext | Cost Center | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | fee_collection_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | fee_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | fee_receivable_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | late_fee_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | fee_discount_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | scholarship_expense_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | scholarship_liability_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | hostel_receivable_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | hostel_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | mess_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | hostel_deposit_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | transport_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | transport_receivable_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | library_fine_income_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | University Accounts Settings | library_deposit_account | Link | erpnext | Account | 0 | 0 | 0% | SKIP |
| university_erp | Job Eligible Program | program | Link | education | Program | 5 | 0 | 0.0% | PASS |
| university_erp | Placement Application | student | Link | education | Student | 8 | 0 | 0.0% | PASS |
| university_erp | Placement Company | industry_type | Link | erpnext | Industry Type | 5 | 0 | 0.0% | PASS |
| university_erp | Placement Drive | academic_year | Link | education | Academic Year | 0 | 0 | 0% | PASS |
| university_erp | Placement Drive | coordinator | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Student Resume | student | Link | education | Student | 5 | 0 | 0.0% | PASS |
| university_erp | Student Resume | verified_by | Link | frappe | User | 5 | 0 | 0.0% | PASS |
| university_erp | Alumni | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Alumni | user | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | Alumni | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Alumni | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Placement Profile | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Placement Profile | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Publication Author | employee | Link | erpnext | Employee | 5 | 0 | 0.0% | PASS |
| university_erp | Research Project | principal_investigator | Link | erpnext | Employee | 3 | 0 | 0.0% | PASS |
| university_erp | Research Project | department | Link | erpnext | Department | 0 | 0 | 0% | PASS |
| university_erp | Research Publication | corresponding_author | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Research Team Member | employee | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Student Status Log | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | Student Status Log | changed_by | Link | frappe | User | 0 | 0 | 0% | PASS |
| university_erp | University Alumni | student | Link | education | Student | 0 | 0 | 0% | PASS |
| university_erp | University Alumni | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | University Announcement | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Transport Allocation | student | Link | education | Student | 10 | 0 | 0.0% | PASS |
| university_erp | Transport Allocation | program | Link | education | Program | 0 | 0 | 0% | PASS |
| university_erp | Transport Allocation | academic_year | Link | education | Academic Year | 10 | 0 | 0.0% | PASS |
| university_erp | Transport Allocation | fee_reference | Link | education | Fees | 0 | 0 | 0% | PASS |
| university_erp | Transport Route | driver | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Transport Trip Log | driver | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Transport Vehicle | driver | Link | erpnext | Employee | 0 | 0 | 0% | PASS |
| university_erp | Transport Vehicle | conductor | Link | erpnext | Employee | 0 | 0 | 0% | PASS |

## Broken Link Details

First 10 broken records per link type:

### PO Attainment.department -> Department

**1 broken** out of 1 records (100.0%)

| Source Record | Broken Value |
|-------------|-------------|
| B.Tech Computer Science-2025-26-POATT | Computer Science |

## Dynamic Link Analysis

Dynamic Link fields resolving to cross-app doctypes:

### Payment Entry.party (companion: party_type)

| Target Doctype | Target App | Record Count | Broken Count | Status |
|---------------|-----------|------------:|------------:|--------|
| Student | education | 10 | 0 | PASS |

### Comment.reference_name (companion: reference_doctype)

| Target Doctype | Target App | Record Count | Broken Count | Status |
|---------------|-----------|------------:|------------:|--------|
| Hostel Room | university_erp | 250 | 0 | PASS |
| Hostel Attendance | university_erp | 140 | 0 | PASS |
| Student | education | 27 | 0 | PASS |
| Hostel Visitor | university_erp | 24 | 0 | PASS |
| Library Article | university_erp | 12 | 0 | PASS |
| Room | education | 12 | 0 | PASS |
| Hostel Maintenance Request | university_erp | 10 | 0 | PASS |
| Library Subject | university_erp | 10 | 0 | PASS |
| Supplier Group | erpnext | 8 | 0 | PASS |
| Instructor | education | 6 | 0 | PASS |
| Hostel Building | university_erp | 6 | 0 | PASS |
| Library Category | university_erp | 5 | 0 | PASS |
| Exam Schedule | university_erp | 4 | 0 | PASS |
| Library Transaction | university_erp | 4 | 0 | PASS |

## Orphan Record Analysis

| Doctype | Total Records | Orphan Count | Expected Reference | Severity |
|---------|-------------:|------------:|-------------------|----------|
| Employee | 15 | 15 | Salary Structure Assignment.employee | WARNING |

## Severity Classification

| Level | Meaning |
|-------|---------|
| FAILURE | Broken links found -- field references a non-existent record |
| WARNING | Potential issue -- target table missing or orphan records |
| PASS | All links resolve correctly |
| SKIP | Source table does not exist in database |
| ERROR | Query failed -- investigate manually |

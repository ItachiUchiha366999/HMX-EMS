# Report & Dashboard Audit Results

**Generated:** 2026-03-18 23:41:15
**Site:** university.local

## Executive Summary

- **Total Reports Tested:** 279
- **Reports Passing:** 189
- **Reports Failing:** 90
- **Unregistered Report Files:** 1
- **Analytics API Endpoints:** 9 (8 PASS, 1 FAIL, 0 DEGRADED)
- **Dashboard Accuracy Checks:** 1 (0 PASS, 0 WARNING, 0 FAIL)

## Report Results

| # | Report Name | Module | Type | Pass 1 | Pass 2 | Rows | Columns | Error |
|---|-------------|--------|------|--------|--------|------|---------|-------|
| 1 | Question Bank Analysis | University Examinations | Script Report | PASS | N/A | 6 | 12 |  |
| 2 | Internal Assessment Summary | University Examinations | Script Report | PASS | N/A | 0 | 7 |  |
| 3 | Examination Result Analysis | University Examinations | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: No module named 'university_erp.university_examinations.report.examination_result_analysis.e |
| 4 | CO Attainment Report | University OBE | Script Report | PASS | N/A | 15 | 9 |  |
| 5 | CO PO Attainment | University OBE | Script Report | PASS | N/A | 15 | 6 |  |
| 6 | NIRF Parameter Report | University OBE | Script Report | PASS | N/A | 0 | 6 |  |
| 7 | NAAC Criterion Progress | University OBE | Script Report | PASS | N/A | 8 | 8 |  |
| 8 | Program Outcome Attainment | University OBE | Script Report | PASS | N/A | 12 | 8 |  |
| 9 | Student Performance Analysis | University Analytics | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 's.program' in 'SELECT'") \| Pass 2: (1054, "Unknown column 's.progra |
| 10 | Stock Ledger | University Inventory | Script Report | PASS | N/A | 0 | 12 |  |
| 11 | Stock Balance | University Inventory | Script Report | PASS | N/A | 0 | 0 |  |
| 12 | Asset Register | University Inventory | Script Report | PASS | N/A | 0 | 12 |  |
| 13 | Low Stock Items | University Inventory | Script Report | PASS | N/A | 0 | 10 |  |
| 14 | Feedback Analysis | University Feedback | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'ff.title' in 'SELECT'") \| Pass 2: (1054, "Unknown column 'ff.title' |
| 15 | Grievance Summary | University Grievance | Script Report | PASS | N/A | 3 | 7 |  |
| 16 | Purchase Order Status | University Inventory | Script Report | PASS | N/A | 0 | 12 |  |
| 17 | SLA Compliance Report | University Grievance | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'g.submission_date' in 'SELECT'") \| Pass 2: (1054, "Unknown column ' |
| 18 | Communication Analytics | University Analytics | Script Report | PASS | N/A | 0 | 6 |  |
| 19 | Faculty Feedback Report | University Feedback | Script Report | PASS | N/A | 0 | 8 |  |
| 20 | Lab Equipment Utilization | University Inventory | Script Report | PASS | N/A | 0 | 10 |  |
| 21 | Refund Report | University Payments | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'fr.reason' in 'SELECT'") \| Pass 2: (1054, "Unknown column 'fr.reaso |
| 22 | Daily Collection Report | University Payments | Script Report | PASS | N/A | 0 | 9 |  |
| 23 | Gateway Reconciliation Report | University Payments | Script Report | PASS | N/A | 0 | 11 |  |
| 24 | SMS Delivery Report | University Integrations | Script Report | PASS | N/A | 0 | 8 |  |
| 25 | CO-PO Mapping Matrix | University OBE | Script Report | PASS | N/A | 0 | 4 |  |
| 26 | PO Attainment Report | University OBE | Script Report | PASS | N/A | 12 | 10 |  |
| 27 | Survey Analysis Report | University OBE | Script Report | PASS | N/A | 0 | 10 |  |
| 28 | Payment Transaction Report | University Integrations | Script Report | PASS | N/A | 0 | 10 |  |
| 29 | Program Attainment Summary | University OBE | Script Report | PASS | N/A | 1 | 11 |  |
| 30 | Certificate Issuance Report | University Integrations | Script Report | PASS | N/A | 2 | 11 |  |
| 31 | Visitor Log | University Hostel | Script Report | PASS | N/A | 5 | 12 |  |
| 32 | Quiz Analytics | University LMS | Script Report | PASS | N/A | 15 | 9 |  |
| 33 | Course Progress | University LMS | Script Report | PASS | N/A | 0 | 8 |  |
| 34 | Maintenance Summary | University Hostel | Script Report | PASS | N/A | 2 | 12 |  |
| 35 | Publication Statistics | University Research | Script Report | PASS | N/A | 5 | 8 |  |
| 36 | Faculty Research Output | University Research | Script Report | PASS | N/A | 6 | 9 |  |
| 37 | Grant Utilization Report | University Research | Script Report | PASS | N/A | 3 | 10 |  |
| 38 | Assignment Submission Report | University LMS | Script Report | PASS | N/A | 20 | 8 |  |
| 39 | Overdue Books | University Library | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Field <strong>library_fine_per_day</strong> does not exist on <strong>University Settings</s |
| 40 | Placement Trend | University Placement | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'pjo.package_offered' in 'SELECT'") \| Pass 2: (1054, "Unknown column |
| 41 | Hostel Occupancy | University Hostel | Script Report | PASS | N/A | 4 | 9 |  |
| 42 | Faculty Directory | Faculty Management | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'e.custom_employee_category' in 'SELECT'") \| Pass 2: (1054, "Unknown |
| 43 | Room Availability | University Hostel | Script Report | PASS | N/A | 31 | 11 |  |
| 44 | Library Collection | University Library | Script Report | PASS | N/A | 4 | 6 |  |
| 45 | Library Circulation | University Library | Script Report | PASS | N/A | 9 | 5 |  |
| 46 | Route Wise Students | University Transport | Script Report | PASS | N/A | 10 | 8 |  |
| 47 | Vehicle Utilization | University Transport | Script Report | PASS | N/A | 4 | 9 |  |
| 48 | Placement Statistics | University Placement | Script Report | PASS | N/A | 1 | 10 |  |
| 49 | Department HR Summary | Faculty Management | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'e.custom_employee_category' in 'SELECT'") \| Pass 2: (1054, "Unknown |
| 50 | Company Wise Placement | University Placement | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'pjo.package_offered' in 'SELECT'") \| Pass 2: (1054, "Unknown column |
| 51 | Program Wise Placement | University Placement | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'pa.program' in 'SELECT'") \| Pass 2: (1054, "Unknown column 'pa.prog |
| 52 | Faculty Workload Summary | Faculty Management | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'e.custom_is_faculty' in 'WHERE'") \| Pass 2: (1054, "Unknown column  |
| 53 | Hostel Attendance Report | University Hostel | Script Report | PASS | N/A | 15 | 7 |  |
| 54 | Leave Utilization Report | Faculty Management | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'la.custom_total_classes_affected' in 'SELECT'") \| Pass 2: (1054, "U |
| 55 | Member Borrowing History | University Library | Script Report | PASS | N/A | 0 | 9 |  |
| 56 | Transport Fee Collection | University Transport | Script Report | PASS | N/A | 4 | 6 |  |
| 57 | Fee Defaulters | University Finance | Script Report | PASS | N/A | 0 | 10 |  |
| 58 | Fee Collection Summary | University Finance | Script Report | PASS | N/A | 4 | 6 |  |
| 59 | Program-wise Fee Report | University Finance | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: No module named 'university_erp.university_finance.report.program_wise_fee_report' \| Pass 2 |
| 60 | Stock Qty vs Batch Qty | Stock | Script Report | PASS | N/A | 0 | 6 |  |
| 61 | General Ledger | Accounts | Script Report | PASS | N/A | 0 | 0 |  |
| 62 | Quotation Trends | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 63 | Delivery Note Trends | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 64 | Sales Order Trends | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 65 | Sales Invoice Trends | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 66 | Purchase Order Trends | Buying | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 67 | Purchase Receipt Trends | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 68 | Purchase Invoice Trends | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year is mandatory \| Pass 2: Fiscal Year is mandatory |
| 69 | Trial Balance (Simple) | Accounts | Query Report | FAIL | PASS | 0 | 7 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 70 | Sales Partners Commission | Accounts | Query Report | PASS | N/A | 0 | 5 |  |
| 71 | Calculated Discount Mismatch | Accounts | Script Report | PASS | N/A | 0 | 5 |  |
| 72 | Serial No Warranty Expiry | Stock | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 73 | Available Serial No | Stock | Script Report | FAIL | PASS | 0 | 19 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 74 | Prepared Report Analytics | Core | Script Report | PASS | N/A | 0 | 6 |  |
| 75 | Incorrect Serial and Batch Bundle | Stock | Script Report | PASS | N/A | 0 | 5 |  |
| 76 | Gross Profit | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object is not iterable \| Pass 2: 'NoneType' object is not iterable |
| 77 | Serial No Status | Stock | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 78 | Serial No Service Contract Expiry | Stock | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 79 | Invalid Ledger Entries | Accounts | Script Report | FAIL | PASS | 0 | 2 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 80 | Cheques and Deposits Incorrectly cleared | Accounts | Script Report | PASS | N/A | 0 | 6 |  |
| 81 | Item-wise Purchase History | Buying | Script Report | FAIL | PASS | 0 | 18 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 82 | Available Batch Report | Stock | Script Report | FAIL | PASS | 0 | 5 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 83 | Leave Ledger | HR | Script Report | PASS | N/A | 0 | 15 |  |
| 84 | Completed Work Orders | Manufacturing | Query Report | PASS | N/A | 0 | 6 |  |
| 85 | Lost Quotations | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object has no attribute 'lower' \| Pass 2: 'NoneType' object has no attribute 'lo |
| 86 | Employee Leave Balance | HR | Script Report | FAIL | PASS | 75 | 8 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 87 | Income Tax Deductions | Payroll | Script Report | PASS | N/A | 0 | 7 |  |
| 88 | Asset Depreciation Ledger | Accounts | Script Report | PASS | N/A | 0 | 13 |  |
| 89 | Stock Ledger Variance | Stock | Script Report | PASS | N/A | 0 | 33 |  |
| 90 | Shift Attendance | HR | Script Report | PASS | N/A | 0 | 17 |  |
| 91 | Reserved Stock | Stock | Script Report | FAIL | PASS | 0 | 16 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 92 | General and Payment Ledger Comparison | Accounts | Script Report | PASS | N/A | 0 | 8 |  |
| 93 | Asset Activity | Assets | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 94 | Asset Depreciations and Balances | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 95 | Fixed Asset Register | Assets | Script Report | PASS | N/A | 0 | 15 |  |
| 96 | Serial and Batch Summary | Stock | Script Report | PASS | N/A | 0 | 13 |  |
| 97 | Financial Ratios | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 1 \| Pass 2: 1 |
| 98 | Voucher-wise Balance | Accounts | Script Report | PASS | N/A | 0 | 4 |  |
| 99 | Appraisal Overview | HR | Script Report | PASS | N/A | 0 | 11 |  |
| 100 | Audit System Hooks | Custom | Script Report | PASS | N/A | 269 | 8 |  |
| 101 | Warehouse Wise Stock Balance | Stock | Script Report | PASS | N/A | 5 | 2 |  |
| 102 | Database Storage Usage By Tables | Core | Script Report | PASS | N/A | 1231 | 4 |  |
| 103 | Professional Tax Deductions | Payroll | Script Report | PASS | N/A | 0 | 0 |  |
| 104 | Provident Fund Deductions | Payroll | Script Report | PASS | N/A | 0 | 0 |  |
| 105 | Employee Hours Utilization Based On Timesheet | HR | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date must come before To Date \| Pass 2: The metrics for this report are calculated bas |
| 106 | Unpaid Expense Claim | HR | Script Report | PASS | N/A | 0 | 6 |  |
| 107 | Project Profitability | HR | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: The metrics for this report are calculated based on the <strong>Standard Working Hours</stro |
| 108 | Payment Ledger | Accounts | Script Report | PASS | N/A | 0 | 10 |  |
| 109 | Lost Opportunity | CRM | Script Report | FAIL | PASS | 0 | 8 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 110 | FIFO Queue vs Qty After Transaction Comparison | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Any one of following filters required: warehouse, Item Code, Item Group \| Pass 2: Any one o |
| 111 | Income Tax Computation | Payroll | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: No employees found with selected filters and active salary structure \| Pass 2: No employees |
| 112 | BOM Operations Time | Manufacturing | Script Report | PASS | N/A | 0 | 8 |  |
| 113 | Payment Terms Status for Sales Order | Selling | Script Report | PASS | N/A | 0 | 12 |  |
| 114 | Stock Ledger Invariant Check | Stock | Script Report | PASS | N/A | 0 | 31 |  |
| 115 | Deferred Revenue and Expense | Accounts | Script Report | PASS | N/A | 2 | 13 |  |
| 116 | Employee Exits | HR | Script Report | PASS | N/A | 0 | 11 |  |
| 117 | Work Order Consumed Materials | Manufacturing | Script Report | PASS | N/A | 0 | 12 |  |
| 118 | Process Loss Report | Manufacturing | Script Report | PASS | N/A | 0 | 9 |  |
| 119 | TDS Computation Summary | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: '>' not supported between instances of 'NoneType' and 'NoneType' \| Pass 2: Date 19-03-2025  |
| 120 | Tax Withholding Details | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: '>' not supported between instances of 'NoneType' and 'NoneType' \| Pass 2: No <strong>Tax W |
| 121 | Opportunity Summary by Sales Stage | CRM | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: None \| Pass 2: None |
| 122 | VAT Audit Report | Regional | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please set VAT Accounts in <a href="http://localhost:8000/app/south-africa-vat-settings/">So |
| 123 | Sales Pipeline Analytics | CRM | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date is mandatory \| Pass 2: None |
| 124 | Incorrect Stock Value Report | Stock | Script Report | PASS | N/A | 0 | 10 |  |
| 125 | COGS By Item Group | Stock | Script Report | FAIL | PASS | 0 | 2 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 126 | Subcontract Order Summary | Buying | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: can only concatenate str (not "NoneType") to str \| Pass 2: can only concatenate str (not "N |
| 127 | Vehicle Expenses | HR | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date and To Date are mandatory \| Pass 2: Date 19-03-2025 is not in any active Fiscal Y |
| 128 | Incorrect Serial No Valuation | Stock | Script Report | PASS | N/A | 1 | 11 |  |
| 129 | Incorrect Balance Qty After Transaction | Stock | Script Report | PASS | N/A | 0 | 9 |  |
| 130 | Serial No Ledger | Stock | Script Report | PASS | N/A | 0 | 12 |  |
| 131 | Delayed Tasks Summary | Projects | Script Report | PASS | N/A | 0 | 10 |  |
| 132 | Dimension-wise Accounts Balance Report | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year None is required \| Pass 2: Fiscal Year None is required |
| 133 | Billed Items To Be Received | Accounts | Script Report | PASS | N/A | 0 | 10 |  |
| 134 | Cost of Poor Quality Report | Manufacturing | Script Report | PASS | N/A | 0 | 10 |  |
| 135 | Job Card Summary | Manufacturing | Script Report | PASS | N/A | 0 | 12 |  |
| 136 | Production Plan Summary | Manufacturing | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Production Plan None not found \| Pass 2: Production Plan None not found |
| 137 | Issue Summary | Support | Script Report | PASS | N/A | 0 | 15 |  |
| 138 | Issue Analytics | Support | Script Report | PASS | N/A | 0 | 2 |  |
| 139 | POS Register | Accounts | Script Report | PASS | N/A | 0 | 0 |  |
| 140 | UAE VAT 201 | Regional | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 's.vat_emirate' in 'SELECT'") \| Pass 2: (1054, "Unknown column 's.va |
| 141 | First Response Time for Opportunity | CRM | Script Report | PASS | N/A | 0 | 2 |  |
| 142 | First Response Time for Issues | Support | Script Report | PASS | N/A | 0 | 2 |  |
| 143 | Program wise Fee Collection | Education | Script Report | PASS | N/A | 5 | 4 |  |
| 144 | YouTube Interactions | Utilities | Script Report | PASS | N/A | 0 | 0 |  |
| 145 | Lead Details | CRM | Script Report | PASS | N/A | 0 | 16 |  |
| 146 | Stock Qty vs Serial No Count | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Warehouse: None does not belong to None \| Pass 2: Warehouse: None does not belong to Hanuma |
| 147 | Requested Items to Order and Receive | Buying | Script Report | PASS | N/A | 0 | 0 |  |
| 148 | Student Batch-Wise Attendance | Education | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select date \| Pass 2: Please select date |
| 149 | Student and Guardian Contact Details | Education | Script Report | PASS | N/A | 0 | 14 |  |
| 150 | Absent Student Report | Education | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select date \| Pass 2: Please select date |
| 151 | Student Monthly Attendance Sheet | Education | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'month' \| Pass 2: 'month' |
| 152 | Assessment Plan Status | Education | Script Report | PASS | N/A | 10 | 8 |  |
| 153 | Course wise Assessment Report | Education | Script Report | PASS | N/A | 0 | 2 |  |
| 154 | Student Fee Collection | Education | Query Report | PASS | N/A | 31 | 5 |  |
| 155 | Final Assessment Grades | Education | Script Report | PASS | N/A | 0 | 3 |  |
| 156 | Sales Analytics | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'value_quantity' \| Pass 2: 'value_quantity' |
| 157 | Salary Payments Based On Payment Mode | Payroll | Script Report | PASS | N/A | 0 | 0 |  |
| 158 | Salary Payments via ECS | Payroll | Script Report | PASS | N/A | 0 | 9 |  |
| 159 | Sales Order Analysis | Selling | Script Report | PASS | N/A | 0 | 0 |  |
| 160 | Bank Remittance | Payroll | Script Report | PASS | N/A | 0 | 9 |  |
| 161 | Salary Register | Payroll | Script Report | PASS | N/A | 0 | 0 |  |
| 162 | Purchase Order Analysis | Buying | Script Report | PASS | N/A | 0 | 0 |  |
| 163 | Exponential Smoothing Forecasting | Manufacturing | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: unsupported operand type(s) for +: 'NoneType' and 'str' \| Pass 2: unsupported operand type( |
| 164 | Recruitment Analytics | HR | Script Report | PASS | N/A | 0 | 9 |  |
| 165 | Item Shortage Report | Stock | Script Report | PASS | N/A | 0 | 0 |  |
| 166 | Employee Analytics | HR | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'company' \| Pass 2: 'NoneType' object has no attribute 'lower' |
| 167 | Project Summary | Projects | Script Report | PASS | N/A | 0 | 10 |  |
| 168 | Quality Inspection Summary | Manufacturing | Script Report | PASS | N/A | 0 | 10 |  |
| 169 | Downtime Analysis | Manufacturing | Script Report | PASS | N/A | 0 | 8 |  |
| 170 | Work Order Summary | Manufacturing | Script Report | PASS | N/A | 0 | 12 |  |
| 171 | Website Analytics | Website | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object has no attribute 'fieldname' \| Pass 2: 'NoneType' object has no attribute |
| 172 | Production Planning Report | Manufacturing | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object has no attribute 'startswith' \| Pass 2: 'NoneType' object has no attribut |
| 173 | Review | Quality Management | Query Report | FAIL | FAIL | 0 | 0 | Pass 1: (1054, "Unknown column 'tabQuality Action.document_type' in 'SELECT'") \| Pass 2: (1054, "Un |
| 174 | Territory-wise Sales | Selling | Script Report | PASS | N/A | 3 | 5 |  |
| 175 | Stock and Account Value Comparison | Stock | Script Report | PASS | N/A | 0 | 8 |  |
| 176 | Item-wise Sales History | Selling | Script Report | FAIL | PASS | 0 | 19 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 177 | Lead Conversion Time | CRM | Script Report | PASS | N/A | 0 | 4 |  |
| 178 | Employee Leave Balance Summary | HR | Script Report | PASS | N/A | 0 | 8 |  |
| 179 | Procurement Tracker | Buying | Script Report | PASS | N/A | 0 | 19 |  |
| 180 | Delayed Order Report | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object has no attribute 'startswith' \| Pass 2: 'NoneType' object has no attribut |
| 181 | Delayed Item Report | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object has no attribute 'startswith' \| Pass 2: 'NoneType' object has no attribut |
| 182 | Customer-wise Item Price | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select a Customer \| Pass 2: Please select a Customer |
| 183 | Project Billing Summary | Projects | Script Report | FAIL | PASS | 0 | 6 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 184 | Employee Billing Summary | Projects | Script Report | FAIL | PASS | 0 | 6 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 185 | BOM Explorer | Manufacturing | Script Report | PASS | N/A | 0 | 7 |  |
| 186 | Subcontracted Raw Materials To Be Transferred | Buying | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: '>=' not supported between instances of 'NoneType' and 'NoneType' \| Pass 2: can only concat |
| 187 | Subcontracted Item To Be Received | Buying | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: '>=' not supported between instances of 'NoneType' and 'NoneType' \| Pass 2: can only concat |
| 188 | Inactive Sales Items | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'based_on' \| Pass 2: 'based_on' |
| 189 | Territory Target Variance Based On Item Group | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Start Year and End Year are mandatory \| Pass 2: Start Year and End Year are mandatory |
| 190 | Sales Person Target Variance Based On Item Group | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Start Year and End Year are mandatory \| Pass 2: Start Year and End Year are mandatory |
| 191 | Sales Partner Target Variance based on Item Group | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Start Year and End Year are mandatory \| Pass 2: Start Year and End Year are mandatory |
| 192 | Sales Partner Transaction Summary | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select the document type first \| Pass 2: Please select the document type first |
| 193 | Share Ledger | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select date \| Pass 2: Please select date |
| 194 | Campaign Efficiency | CRM | Script Report | FAIL | PASS | 0 | 9 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 195 | Sales Partner Commission Summary | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select the document type first \| Pass 2: Please select the document type first |
| 196 | Product Bundle Balance | Stock | Script Report | PASS | N/A | 0 | 10 |  |
| 197 | Purchase Analytics | Buying | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'value_quantity' \| Pass 2: 'value_quantity' |
| 198 | Stock Analytics | Stock | Script Report | FAIL | PASS | 0 | 18 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 199 | Production Analytics | Manufacturing | Script Report | FAIL | PASS | 7 | 14 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 200 | Supplier Ledger Summary | Accounts | Script Report | FAIL | PASS | 0 | 0 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 201 | Gross and Net Profit Report | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date and To Date are mandatory \| Pass 2: From Date and To Date are mandatory |
| 202 | IRS 1099 | Regional | Script Report | PASS | N/A | 0 | 0 |  |
| 203 | Account Balance | Accounts | Script Report | PASS | N/A | 75 | 3 |  |
| 204 | Transaction Log Report | Core | Script Report | PASS | N/A | 0 | 6 |  |
| 205 | Customer Ledger Summary | Accounts | Script Report | FAIL | PASS | 0 | 0 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 206 | Pending SO Items For Purchase Request | Selling | Script Report | PASS | N/A | 0 | 12 |  |
| 207 | Batch-Wise Balance History | Stock | Script Report | FAIL | PASS | 0 | 12 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 208 | Work Orders in Progress | Manufacturing | Query Report | PASS | N/A | 0 | 6 |  |
| 209 | Sales Person Commission Summary | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select the document type first \| Pass 2: Please select the document type first |
| 210 | Balance Sheet | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date and To Date are mandatory \| Pass 2: From Date and To Date are mandatory |
| 211 | Permitted Documents For User | Core | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: DocType None not found \| Pass 2: DocType None not found |
| 212 | BOM Variance Report | Manufacturing | Script Report | PASS | N/A | 0 | 8 |  |
| 213 | BOM Stock Calculated | Manufacturing | Script Report | PASS | N/A | 0 | 9 |  |
| 214 | Daily Work Summary Replies | HR | Script Report | PASS | N/A | 0 | 0 |  |
| 215 | Address And Contacts | Selling | Script Report | PASS | N/A | 0 | 17 |  |
| 216 | Customers Without Any Sales Transactions | Selling | Query Report | PASS | N/A | 0 | 4 |  |
| 217 | Item-wise Price List Rate | Stock | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 218 | Consolidated Financial Statement | Accounts | Script Report | PASS | N/A | 0 | 0 |  |
| 219 | Employee Advance Summary | HR | Script Report | PASS | N/A | 0 | 9 |  |
| 220 | Item Balance (Simple) | Stock | Query Report | PASS | N/A | 0 | 7 |  |
| 221 | Open Work Orders | Manufacturing | Query Report | PASS | N/A | 0 | 6 |  |
| 222 | Issued Items Against Work Order | Manufacturing | Query Report | PASS | N/A | 0 | 14 |  |
| 223 | Work Order Stock Report | Manufacturing | Script Report | PASS | N/A | 0 | 11 |  |
| 224 | Warehouse wise Item Balance Age and Value | Stock | Script Report | FAIL | PASS | 0 | 11 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 225 | Share Balance | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select date \| Pass 2: Please select date |
| 226 | Item Price Stock | Stock | Script Report | PASS | N/A | 0 | 9 |  |
| 227 | Item Variant Details | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Item None not found \| Pass 2: Item None not found |
| 228 | Delivered Items To Be Billed | Accounts | Script Report | PASS | N/A | 0 | 12 |  |
| 229 | Received Items To Be Billed | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'NoneType' object has no attribute 'precision' \| Pass 2: 'NoneType' object has no attribute |
| 230 | Sales Payment Summary | Accounts | Script Report | PASS | N/A | 0 | 6 |  |
| 231 | Asset Maintenance | Assets | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 232 | Support Hour Distribution | Support | Script Report | PASS | N/A | 1 | 9 |  |
| 233 | Total Stock Summary | Stock | Script Report | PASS | N/A | 0 | 4 |  |
| 234 | BOM Stock Report | Manufacturing | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Quantity to Produce should be greater than zero. \| Pass 2: Quantity to Produce should be gr |
| 235 | ToDo | Desk | Script Report | PASS | N/A | 0 | 7 |  |
| 236 | Lead Owner Efficiency | CRM | Script Report | PASS | N/A | 0 | 9 |  |
| 237 | Addresses And Contacts | Contacts | Script Report | PASS | N/A | 0 | 14 |  |
| 238 | Prospects Engaged But Not Converted | CRM | Script Report | PASS | N/A | 0 | 7 |  |
| 239 | Accounts Receivable Summary | Accounts | Script Report | PASS | N/A | 0 | 16 |  |
| 240 | Accounts Receivable | Accounts | Script Report | PASS | N/A | 0 | 23 |  |
| 241 | Project wise Stock Tracking | Projects | Script Report | PASS | N/A | 0 | 11 |  |
| 242 | BOM Search | Stock | Script Report | PASS | N/A | 0 | 2 |  |
| 243 | Bank Clearance Summary | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'account' \| Pass 2: 'account' |
| 244 | Bank Reconciliation Statement | Accounts | Script Report | PASS | N/A | 0 | 10 |  |
| 245 | Budget Variance Report | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'period' \| Pass 2: 'period' |
| 246 | Customer Acquisition and Loyalty | Selling | Script Report | FAIL | PASS | 3 | 7 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 247 | Employee Birthday | HR | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'company' \| Pass 2: 'month' |
| 248 | Item Prices | Stock | Script Report | PASS | N/A | 0 | 11 |  |
| 249 | Item-wise Purchase Register | Accounts | Script Report | FAIL | PASS | 0 | 19 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 250 | Item-wise Sales Register | Accounts | Script Report | PASS | N/A | 0 | 22 |  |
| 251 | Itemwise Recommended Reorder Level | Stock | Script Report | FAIL | PASS | 0 | 12 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 252 | Monthly Attendance Sheet | HR | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select Filter Based On \| Pass 2: Please select Filter Based On |
| 253 | Payment Period Based On Invoice Date | Accounts | Script Report | FAIL | PASS | 0 | 16 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 254 | Purchase Register | Accounts | Script Report | PASS | N/A | 0 | 21 |  |
| 255 | Sales Register | Accounts | Script Report | PASS | N/A | 0 | 23 |  |
| 256 | Stock Ageing | Stock | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'to_date' \| Pass 2: 'NoneType' object has no attribute 'split' |
| 257 | Stock Projected Qty | Stock | Script Report | PASS | N/A | 0 | 20 |  |
| 258 | Supplier-Wise Sales Analytics | Stock | Script Report | PASS | N/A | 0 | 11 |  |
| 259 | Profit and Loss Statement | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date and To Date are mandatory \| Pass 2: From Date and To Date are mandatory |
| 260 | Trial Balance | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year None is required \| Pass 2: Fiscal Year None is required |
| 261 | Customer Credit Balance | Selling | Script Report | FAIL | PASS | 0 | 7 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 262 | Accounts Payable Summary | Accounts | Script Report | PASS | N/A | 0 | 15 |  |
| 263 | Available Stock for Packing Items | Selling | Script Report | PASS | N/A | 0 | 6 |  |
| 264 | Accounts Payable | Accounts | Script Report | PASS | N/A | 0 | 22 |  |
| 265 | Trial Balance for Party | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year None is required \| Pass 2: Fiscal Year None is required |
| 266 | Cash Flow | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: From Date and To Date are mandatory \| Pass 2: From Date and To Date are mandatory |
| 267 | Inactive Customers | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: 'Days Since Last Order' must be greater than or equal to zero \| Pass 2: 'Days Since Last Or |
| 268 | Requested Items To Be Transferred | Stock | Query Report | PASS | N/A | 0 | 9 |  |
| 269 | Items To Be Requested | Stock | Query Report | PASS | N/A | 0 | 7 |  |
| 270 | Daily Timesheet Summary | Projects | Script Report | PASS | N/A | 0 | 10 |  |
| 271 | Material Requests for which Supplier Quotations are not created | Stock | Query Report | PASS | N/A | 0 | 7 |  |
| 272 | Employees working on a holiday | HR | Script Report | FAIL | PASS | 0 | 5 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 273 | Supplier Quotation Comparison | Buying | Script Report | PASS | N/A | 0 | 0 |  |
| 274 | Profitability Analysis | Accounts | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Fiscal Year None is required \| Pass 2: Fiscal Year None is required |
| 275 | Sales Person-wise Transaction Summary | Selling | Script Report | FAIL | FAIL | 0 | 0 | Pass 1: Please select the document type first \| Pass 2: Please select the document type first |
| 276 | Employee Information | HR | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 277 | Document Share Report | Core | Report Builder | FAIL | FAIL | 0 | 0 | Pass 1: object of type 'NoneType' has no len() \| Pass 2: object of type 'NoneType' has no len() |
| 278 | Batch Item Expiry Status | Stock | Script Report | FAIL | PASS | 0 | 7 | Pass 1 failed, Pass 2 OK with defaults: ['academic_year', 'from_date', 'to_date', 'company'] |
| 279 | Maintenance Schedules | Support | Query Report | PASS | N/A | 0 | 9 |  |

## Failed Reports Detail

### Examination Result Analysis
- **Module:** University Examinations
- **Type:** Script Report
- **Error:** Pass 1: No module named 'university_erp.university_examinations.report.examination_result_analysis.examinati | Pass 2: No module named 'university_erp.university_examinations.report.examination_result_analysis.examinati

### Student Performance Analysis
- **Module:** University Analytics
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 's.program' in 'SELECT'") | Pass 2: (1054, "Unknown column 's.program' in 'SELECT'")

### Feedback Analysis
- **Module:** University Feedback
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'ff.title' in 'SELECT'") | Pass 2: (1054, "Unknown column 'ff.title' in 'SELECT'")

### SLA Compliance Report
- **Module:** University Grievance
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'g.submission_date' in 'SELECT'") | Pass 2: (1054, "Unknown column 'g.submission_date' in 'SELECT'")

### Refund Report
- **Module:** University Payments
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'fr.reason' in 'SELECT'") | Pass 2: (1054, "Unknown column 'fr.reason' in 'SELECT'")

### Overdue Books
- **Module:** University Library
- **Type:** Script Report
- **Error:** Pass 1: Field <strong>library_fine_per_day</strong> does not exist on <strong>University Settings</strong> | Pass 2: Field <strong>library_fine_per_day</strong> does not exist on <strong>University Settings</strong>

### Placement Trend
- **Module:** University Placement
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'pjo.package_offered' in 'SELECT'") | Pass 2: (1054, "Unknown column 'pjo.package_offered' in 'SELECT'")

### Faculty Directory
- **Module:** Faculty Management
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'e.custom_employee_category' in 'SELECT'") | Pass 2: (1054, "Unknown column 'e.custom_employee_category' in 'SELECT'")

### Department HR Summary
- **Module:** Faculty Management
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'e.custom_employee_category' in 'SELECT'") | Pass 2: (1054, "Unknown column 'e.custom_employee_category' in 'SELECT'")

### Company Wise Placement
- **Module:** University Placement
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'pjo.package_offered' in 'SELECT'") | Pass 2: (1054, "Unknown column 'pjo.package_offered' in 'SELECT'")

### Program Wise Placement
- **Module:** University Placement
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'pa.program' in 'SELECT'") | Pass 2: (1054, "Unknown column 'pa.program' in 'SELECT'")

### Faculty Workload Summary
- **Module:** Faculty Management
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'e.custom_is_faculty' in 'WHERE'") | Pass 2: (1054, "Unknown column 'e.custom_is_faculty' in 'WHERE'")

### Leave Utilization Report
- **Module:** Faculty Management
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 'la.custom_total_classes_affected' in 'SELECT'") | Pass 2: (1054, "Unknown column 'la.custom_total_classes_affected' in 'SELECT'")

### Program-wise Fee Report
- **Module:** University Finance
- **Type:** Script Report
- **Error:** Pass 1: No module named 'university_erp.university_finance.report.program_wise_fee_report' | Pass 2: No module named 'university_erp.university_finance.report.program_wise_fee_report'

### Quotation Trends
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Delivery Note Trends
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Sales Order Trends
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Sales Invoice Trends
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Purchase Order Trends
- **Module:** Buying
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Purchase Receipt Trends
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Purchase Invoice Trends
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year is mandatory | Pass 2: Fiscal Year is mandatory

### Serial No Warranty Expiry
- **Module:** Stock
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Gross Profit
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object is not iterable | Pass 2: 'NoneType' object is not iterable

### Serial No Status
- **Module:** Stock
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Serial No Service Contract Expiry
- **Module:** Stock
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Lost Quotations
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object has no attribute 'lower' | Pass 2: 'NoneType' object has no attribute 'lower'

### Asset Activity
- **Module:** Assets
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Asset Depreciations and Balances
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Financial Ratios
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: 1 | Pass 2: 1

### Employee Hours Utilization Based On Timesheet
- **Module:** HR
- **Type:** Script Report
- **Error:** Pass 1: From Date must come before To Date | Pass 2: The metrics for this report are calculated based on <strong>Standard Working Hours</strong>. Please 

### Project Profitability
- **Module:** HR
- **Type:** Script Report
- **Error:** Pass 1: The metrics for this report are calculated based on the <strong>Standard Working Hours</strong>. Ple | Pass 2: The metrics for this report are calculated based on the <strong>Standard Working Hours</strong>. Ple

### FIFO Queue vs Qty After Transaction Comparison
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: Any one of following filters required: warehouse, Item Code, Item Group | Pass 2: Any one of following filters required: warehouse, Item Code, Item Group

### Income Tax Computation
- **Module:** Payroll
- **Type:** Script Report
- **Error:** Pass 1: No employees found with selected filters and active salary structure | Pass 2: No employees found with selected filters and active salary structure

### TDS Computation Summary
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: '>' not supported between instances of 'NoneType' and 'NoneType' | Pass 2: Date 19-03-2025 is not in any active Fiscal Year

### Tax Withholding Details
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: '>' not supported between instances of 'NoneType' and 'NoneType' | Pass 2: No <strong>Tax Withholding</strong> Accounts found for this company.

### Opportunity Summary by Sales Stage
- **Module:** CRM
- **Type:** Script Report
- **Error:** Pass 1: None | Pass 2: None

### VAT Audit Report
- **Module:** Regional
- **Type:** Script Report
- **Error:** Pass 1: Please set VAT Accounts in <a href="http://localhost:8000/app/south-africa-vat-settings/">South Afri | Pass 2: Please set VAT Accounts in <a href="http://localhost:8000/app/south-africa-vat-settings/">South Afri

### Sales Pipeline Analytics
- **Module:** CRM
- **Type:** Script Report
- **Error:** Pass 1: From Date is mandatory | Pass 2: None

### Subcontract Order Summary
- **Module:** Buying
- **Type:** Script Report
- **Error:** Pass 1: can only concatenate str (not "NoneType") to str | Pass 2: can only concatenate str (not "NoneType") to str

### Vehicle Expenses
- **Module:** HR
- **Type:** Script Report
- **Error:** Pass 1: From Date and To Date are mandatory | Pass 2: Date 19-03-2025 is not in any active Fiscal Year

### Dimension-wise Accounts Balance Report
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year None is required | Pass 2: Fiscal Year None is required

### Production Plan Summary
- **Module:** Manufacturing
- **Type:** Script Report
- **Error:** Pass 1: Production Plan None not found | Pass 2: Production Plan None not found

### UAE VAT 201
- **Module:** Regional
- **Type:** Script Report
- **Error:** Pass 1: (1054, "Unknown column 's.vat_emirate' in 'SELECT'") | Pass 2: (1054, "Unknown column 's.vat_emirate' in 'SELECT'")

### Stock Qty vs Serial No Count
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: Warehouse: None does not belong to None | Pass 2: Warehouse: None does not belong to Hanumatrix

### Student Batch-Wise Attendance
- **Module:** Education
- **Type:** Script Report
- **Error:** Pass 1: Please select date | Pass 2: Please select date

### Absent Student Report
- **Module:** Education
- **Type:** Script Report
- **Error:** Pass 1: Please select date | Pass 2: Please select date

### Student Monthly Attendance Sheet
- **Module:** Education
- **Type:** Script Report
- **Error:** Pass 1: 'month' | Pass 2: 'month'

### Sales Analytics
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: 'value_quantity' | Pass 2: 'value_quantity'

### Exponential Smoothing Forecasting
- **Module:** Manufacturing
- **Type:** Script Report
- **Error:** Pass 1: unsupported operand type(s) for +: 'NoneType' and 'str' | Pass 2: unsupported operand type(s) for +: 'NoneType' and 'str'

### Employee Analytics
- **Module:** HR
- **Type:** Script Report
- **Error:** Pass 1: 'company' | Pass 2: 'NoneType' object has no attribute 'lower'

### Website Analytics
- **Module:** Website
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object has no attribute 'fieldname' | Pass 2: 'NoneType' object has no attribute 'fieldname'

### Production Planning Report
- **Module:** Manufacturing
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object has no attribute 'startswith' | Pass 2: 'NoneType' object has no attribute 'startswith'

### Review
- **Module:** Quality Management
- **Type:** Query Report
- **Error:** Pass 1: (1054, "Unknown column 'tabQuality Action.document_type' in 'SELECT'") | Pass 2: (1054, "Unknown column 'tabQuality Action.document_type' in 'SELECT'")

### Delayed Order Report
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object has no attribute 'startswith' | Pass 2: 'NoneType' object has no attribute 'startswith'

### Delayed Item Report
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object has no attribute 'startswith' | Pass 2: 'NoneType' object has no attribute 'startswith'

### Customer-wise Item Price
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Please select a Customer | Pass 2: Please select a Customer

### Subcontracted Raw Materials To Be Transferred
- **Module:** Buying
- **Type:** Script Report
- **Error:** Pass 1: '>=' not supported between instances of 'NoneType' and 'NoneType' | Pass 2: can only concatenate str (not "NoneType") to str

### Subcontracted Item To Be Received
- **Module:** Buying
- **Type:** Script Report
- **Error:** Pass 1: '>=' not supported between instances of 'NoneType' and 'NoneType' | Pass 2: can only concatenate str (not "NoneType") to str

### Inactive Sales Items
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: 'based_on' | Pass 2: 'based_on'

### Territory Target Variance Based On Item Group
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Start Year and End Year are mandatory | Pass 2: Start Year and End Year are mandatory

### Sales Person Target Variance Based On Item Group
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Start Year and End Year are mandatory | Pass 2: Start Year and End Year are mandatory

### Sales Partner Target Variance based on Item Group
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Start Year and End Year are mandatory | Pass 2: Start Year and End Year are mandatory

### Sales Partner Transaction Summary
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Please select the document type first | Pass 2: Please select the document type first

### Share Ledger
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Please select date | Pass 2: Please select date

### Sales Partner Commission Summary
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Please select the document type first | Pass 2: Please select the document type first

### Purchase Analytics
- **Module:** Buying
- **Type:** Script Report
- **Error:** Pass 1: 'value_quantity' | Pass 2: 'value_quantity'

### Gross and Net Profit Report
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: From Date and To Date are mandatory | Pass 2: From Date and To Date are mandatory

### Sales Person Commission Summary
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Please select the document type first | Pass 2: Please select the document type first

### Balance Sheet
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: From Date and To Date are mandatory | Pass 2: From Date and To Date are mandatory

### Permitted Documents For User
- **Module:** Core
- **Type:** Script Report
- **Error:** Pass 1: DocType None not found | Pass 2: DocType None not found

### Item-wise Price List Rate
- **Module:** Stock
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Share Balance
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Please select date | Pass 2: Please select date

### Item Variant Details
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: Item None not found | Pass 2: Item None not found

### Received Items To Be Billed
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: 'NoneType' object has no attribute 'precision' | Pass 2: 'NoneType' object has no attribute 'precision'

### Asset Maintenance
- **Module:** Assets
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### BOM Stock Report
- **Module:** Manufacturing
- **Type:** Script Report
- **Error:** Pass 1: Quantity to Produce should be greater than zero. | Pass 2: Quantity to Produce should be greater than zero.

### Bank Clearance Summary
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: 'account' | Pass 2: 'account'

### Budget Variance Report
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: 'period' | Pass 2: 'period'

### Employee Birthday
- **Module:** HR
- **Type:** Script Report
- **Error:** Pass 1: 'company' | Pass 2: 'month'

### Monthly Attendance Sheet
- **Module:** HR
- **Type:** Script Report
- **Error:** Pass 1: Please select Filter Based On | Pass 2: Please select Filter Based On

### Stock Ageing
- **Module:** Stock
- **Type:** Script Report
- **Error:** Pass 1: 'to_date' | Pass 2: 'NoneType' object has no attribute 'split'

### Profit and Loss Statement
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: From Date and To Date are mandatory | Pass 2: From Date and To Date are mandatory

### Trial Balance
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year None is required | Pass 2: Fiscal Year None is required

### Trial Balance for Party
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year None is required | Pass 2: Fiscal Year None is required

### Cash Flow
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: From Date and To Date are mandatory | Pass 2: From Date and To Date are mandatory

### Inactive Customers
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: 'Days Since Last Order' must be greater than or equal to zero | Pass 2: 'Days Since Last Order' must be greater than or equal to zero

### Profitability Analysis
- **Module:** Accounts
- **Type:** Script Report
- **Error:** Pass 1: Fiscal Year None is required | Pass 2: Fiscal Year None is required

### Sales Person-wise Transaction Summary
- **Module:** Selling
- **Type:** Script Report
- **Error:** Pass 1: Please select the document type first | Pass 2: Please select the document type first

### Employee Information
- **Module:** HR
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

### Document Share Report
- **Module:** Core
- **Type:** Report Builder
- **Error:** Pass 1: object of type 'NoneType' has no len() | Pass 2: object of type 'NoneType' has no len()

## Unregistered Reports

These `.py` report files exist on disk but are not registered in the Report doctype:

| # | Report Directory | File Path |
|---|-----------------|-----------|
| 1 | co_po_mapping_matrix | /workspace/development/frappe-bench/apps/university_erp/university_erp/university_obe/report/co_po_mapping_matrix/co_po_mapping_matrix.py |

## Analytics API Results

| Endpoint | Status | Response Type | Notes |
|----------|--------|---------------|-------|
| get_available_dashboards | PASS | list | 1 items |
| get_dashboard | PASS | dict |  |
| get_quick_stats | FAIL | error | (1054, "Unknown column 'status' in 'WHERE'") |
| get_all_kpis | PASS | list | 5 items |
| get_kpi_value | PASS | dict |  |
| get_kpi_trend | PASS | list | 0 items |
| get_kpi_comparison | PASS | dict |  |
| execute_custom_report | PASS | dict | No Custom Report Definitions found |
| calculate_kpi_now | PASS | dict |  |

## Dashboard Accuracy

Comparison of `get_overview_metrics()` values against direct SQL counts.

| Metric | Dashboard Value | Direct SQL Value | Difference | Status |
|--------|----------------|-----------------|------------|--------|
| get_overview_metrics() | ERROR | N/A | N/A | FAIL: (1054, "Unknown column 'status' in 'WHERE'") |

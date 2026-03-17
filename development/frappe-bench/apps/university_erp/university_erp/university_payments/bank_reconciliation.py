# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Bank Reconciliation Tool
Matches bank transactions with system payment entries
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate
import csv
import io


class BankReconciliationTool:
    """Tool for reconciling bank statements with system records"""

    def __init__(self, bank_account, from_date, to_date):
        self.bank_account = bank_account
        self.from_date = getdate(from_date) if from_date else None
        self.to_date = getdate(to_date) if to_date else None

    def get_bank_transactions(self):
        """Get bank transactions from statement"""
        filters = {
            "bank_account": self.bank_account,
            "status": ["!=", "Reconciled"]
        }

        if self.from_date and self.to_date:
            filters["date"] = ["between", [self.from_date, self.to_date]]

        return frappe.get_all(
            "Bank Transaction",
            filters=filters,
            fields=["name", "date", "description", "deposit", "withdrawal", "reference_number", "status"],
            order_by="date asc"
        )

    def get_system_entries(self):
        """Get payment entries from system"""
        if not self.bank_account:
            return []

        entries = frappe.db.sql("""
            SELECT
                pe.name,
                pe.posting_date,
                pe.reference_no,
                pe.reference_date,
                pe.paid_amount,
                pe.received_amount,
                pe.payment_type,
                pe.party,
                pe.party_name,
                pe.mode_of_payment,
                pe.paid_from,
                pe.paid_to
            FROM `tabPayment Entry` pe
            WHERE pe.docstatus = 1
            AND pe.posting_date BETWEEN %s AND %s
            AND (pe.paid_from = %s OR pe.paid_to = %s)
            AND pe.clearance_date IS NULL
            ORDER BY pe.posting_date ASC
        """, (self.from_date, self.to_date, self.bank_account, self.bank_account), as_dict=True)

        return entries

    def auto_match(self):
        """Auto-match bank transactions with system entries"""
        bank_txns = self.get_bank_transactions()
        system_entries = self.get_system_entries()

        matches = []
        matched_entries = set()

        for txn in bank_txns:
            best_match = None
            best_confidence = 0

            for entry in system_entries:
                if entry.name in matched_entries:
                    continue

                if self.is_match(txn, entry):
                    confidence = self.calculate_confidence(txn, entry)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = entry

            if best_match and best_confidence >= 50:
                matches.append({
                    "bank_transaction": txn.name,
                    "bank_date": txn.date,
                    "bank_amount": flt(txn.deposit) or flt(txn.withdrawal),
                    "bank_description": txn.description,
                    "payment_entry": best_match.name,
                    "payment_date": best_match.posting_date,
                    "payment_amount": flt(best_match.paid_amount),
                    "party": best_match.party_name,
                    "match_type": self.get_match_type(txn, best_match),
                    "confidence": best_confidence,
                    "confirmed": False
                })
                matched_entries.add(best_match.name)

        return matches

    def is_match(self, bank_txn, payment_entry):
        """Check if bank transaction matches payment entry"""
        # Amount match
        txn_amount = flt(bank_txn.deposit) or flt(bank_txn.withdrawal)
        entry_amount = flt(payment_entry.paid_amount)

        # Allow small tolerance for rounding
        if abs(txn_amount - entry_amount) > 1:
            return False

        # Type match - deposit should match Receive, withdrawal should match Pay
        if bank_txn.deposit and payment_entry.payment_type != "Receive":
            return False
        if bank_txn.withdrawal and payment_entry.payment_type != "Pay":
            return False

        return True

    def get_match_type(self, bank_txn, payment_entry):
        """Determine match type"""
        if bank_txn.reference_number and payment_entry.reference_no:
            if bank_txn.reference_number == payment_entry.reference_no:
                return "Reference Match"

        date_diff = abs((getdate(bank_txn.date) - getdate(payment_entry.posting_date)).days)
        if date_diff == 0:
            return "Exact Date Match"
        elif date_diff <= 1:
            return "Date Match (1 day)"
        elif date_diff <= 3:
            return "Date Match (3 days)"

        return "Amount Match"

    def calculate_confidence(self, bank_txn, payment_entry):
        """Calculate match confidence percentage"""
        confidence = 50  # Base confidence for amount match

        # Reference match
        if bank_txn.reference_number and payment_entry.reference_no:
            if bank_txn.reference_number == payment_entry.reference_no:
                confidence += 40

        # Date match
        date_diff = abs((getdate(bank_txn.date) - getdate(payment_entry.posting_date)).days)
        if date_diff == 0:
            confidence += 10
        elif date_diff == 1:
            confidence += 5
        elif date_diff > 3:
            confidence -= 10

        # Description contains party name
        if payment_entry.party_name and bank_txn.description:
            if payment_entry.party_name.lower() in bank_txn.description.lower():
                confidence += 5

        return min(max(confidence, 0), 100)

    def reconcile(self, matches):
        """Perform reconciliation"""
        reconciled = []

        for match in matches:
            if match.get("confirmed"):
                try:
                    # Update bank transaction
                    bank_txn = frappe.get_doc("Bank Transaction", match["bank_transaction"])
                    bank_txn.reconcile_with_payment_entry(match["payment_entry"], "Auto")

                    reconciled.append({
                        "bank_transaction": match["bank_transaction"],
                        "payment_entry": match["payment_entry"],
                        "status": "Success"
                    })
                except Exception as e:
                    reconciled.append({
                        "bank_transaction": match["bank_transaction"],
                        "payment_entry": match["payment_entry"],
                        "status": "Failed",
                        "error": str(e)
                    })

        frappe.db.commit()
        return reconciled


class BankStatementImporter:
    """Import bank statements from various formats"""

    BANK_TEMPLATES = {
        "HDFC Bank": {
            "date_column": "Date",
            "description_column": "Narration",
            "withdrawal_column": "Withdrawal Amt.",
            "deposit_column": "Deposit Amt.",
            "balance_column": "Closing Balance",
            "reference_column": "Chq./Ref.No.",
            "date_format": "%d/%m/%y"
        },
        "ICICI Bank": {
            "date_column": "Transaction Date",
            "description_column": "Transaction Remarks",
            "withdrawal_column": "Withdrawal Amount (INR )",
            "deposit_column": "Deposit Amount (INR )",
            "balance_column": "Balance (INR )",
            "reference_column": "Cheque Number",
            "date_format": "%d-%m-%Y"
        },
        "SBI": {
            "date_column": "Txn Date",
            "description_column": "Description",
            "withdrawal_column": "Debit",
            "deposit_column": "Credit",
            "balance_column": "Balance",
            "reference_column": "Ref No./Cheque No.",
            "date_format": "%d %b %Y"
        },
        "Axis Bank": {
            "date_column": "Tran Date",
            "description_column": "PARTICULARS",
            "withdrawal_column": "DR",
            "deposit_column": "CR",
            "balance_column": "BAL",
            "reference_column": "CHQ.NO.",
            "date_format": "%d-%m-%Y"
        },
        "Generic": {
            "date_column": "Date",
            "description_column": "Description",
            "withdrawal_column": "Debit",
            "deposit_column": "Credit",
            "balance_column": "Balance",
            "reference_column": "Reference",
            "date_format": "%Y-%m-%d"
        }
    }

    def __init__(self, bank_account, bank_name=None):
        self.bank_account = bank_account
        self.bank_name = bank_name or "Generic"
        self.template = self.BANK_TEMPLATES.get(self.bank_name, self.BANK_TEMPLATES["Generic"])

    def import_csv(self, file_content):
        """Import from CSV file"""
        transactions = []

        # Try to detect encoding
        try:
            content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            content = file_content.decode('latin-1')

        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            txn = self.parse_row(row)
            if txn:
                transactions.append(txn)

        return self.create_transactions(transactions)

    def parse_row(self, row):
        """Parse a row from bank statement"""
        from datetime import datetime

        try:
            date_str = row.get(self.template["date_column"], "").strip()
            if not date_str:
                return None

            # Try multiple date formats
            date = None
            date_formats = [
                self.template["date_format"],
                "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
                "%d/%m/%y", "%d-%m-%y",
                "%d %b %Y", "%d-%b-%Y"
            ]

            for fmt in date_formats:
                try:
                    date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue

            if not date:
                return None

            withdrawal = self.parse_amount(row.get(self.template["withdrawal_column"], ""))
            deposit = self.parse_amount(row.get(self.template["deposit_column"], ""))

            if not withdrawal and not deposit:
                return None

            return {
                "date": date,
                "description": row.get(self.template["description_column"], "").strip(),
                "withdrawal": withdrawal,
                "deposit": deposit,
                "reference_number": row.get(self.template["reference_column"], "").strip(),
                "closing_balance": self.parse_amount(row.get(self.template["balance_column"], ""))
            }
        except Exception as e:
            frappe.log_error(f"Error parsing row: {str(e)}", "Bank Statement Import")
            return None

    def parse_amount(self, amount_str):
        """Parse amount string to float"""
        if not amount_str:
            return 0

        # Remove currency symbols, commas, spaces
        amount_str = str(amount_str).replace(",", "").replace("₹", "").replace("INR", "")
        amount_str = amount_str.replace("Rs.", "").replace("Rs", "").strip()

        # Handle negative amounts
        is_negative = amount_str.startswith("-") or amount_str.startswith("(")
        amount_str = amount_str.replace("-", "").replace("(", "").replace(")", "")

        try:
            amount = float(amount_str) if amount_str else 0
            return -amount if is_negative else amount
        except ValueError:
            return 0

    def create_transactions(self, transactions):
        """Create Bank Transaction documents"""
        created = []
        duplicates = 0
        errors = []

        for txn in transactions:
            try:
                # Check for duplicate
                existing = frappe.db.exists("Bank Transaction", {
                    "bank_account": self.bank_account,
                    "date": txn["date"],
                    "deposit": txn["deposit"],
                    "withdrawal": txn["withdrawal"],
                    "reference_number": txn["reference_number"] or ""
                })

                if existing:
                    duplicates += 1
                    continue

                doc = frappe.get_doc({
                    "doctype": "Bank Transaction",
                    "bank_account": self.bank_account,
                    "date": txn["date"],
                    "description": txn["description"],
                    "deposit": txn["deposit"],
                    "withdrawal": txn["withdrawal"],
                    "reference_number": txn["reference_number"],
                    "closing_balance": txn["closing_balance"],
                    "status": "Pending"
                })
                doc.insert(ignore_permissions=True)
                created.append(doc.name)

            except Exception as e:
                errors.append(str(e))

        frappe.db.commit()

        return {
            "created": len(created),
            "duplicates": duplicates,
            "errors": len(errors),
            "transactions": created,
            "error_messages": errors[:5]  # Return first 5 errors
        }


@frappe.whitelist()
def get_reconciliation_data(bank_account, from_date, to_date):
    """Get reconciliation data"""
    tool = BankReconciliationTool(bank_account, from_date, to_date)

    return {
        "bank_transactions": tool.get_bank_transactions(),
        "system_entries": tool.get_system_entries(),
        "suggested_matches": tool.auto_match()
    }


@frappe.whitelist()
def perform_reconciliation(matches):
    """Perform reconciliation with confirmed matches"""
    import json
    matches = json.loads(matches) if isinstance(matches, str) else matches

    # Create tool without date filters for reconciliation
    tool = BankReconciliationTool(None, None, None)
    return tool.reconcile(matches)


@frappe.whitelist()
def import_bank_statement(bank_account, file_url, bank_name=None):
    """Import bank statement from uploaded file"""
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    content = file_doc.get_content()

    importer = BankStatementImporter(bank_account, bank_name)

    if file_url.endswith(".csv"):
        return importer.import_csv(content)
    else:
        frappe.throw(_("Unsupported file format. Please upload a CSV file."))


@frappe.whitelist()
def get_supported_banks():
    """Get list of supported bank formats"""
    return list(BankStatementImporter.BANK_TEMPLATES.keys())


@frappe.whitelist()
def manual_reconcile(bank_transaction, payment_entry):
    """Manually reconcile a bank transaction with payment entry"""
    txn = frappe.get_doc("Bank Transaction", bank_transaction)
    txn.reconcile_with_payment_entry(payment_entry, "Manual")
    return {"success": True, "message": _("Transaction reconciled successfully")}


@frappe.whitelist()
def unreconcile_transaction(bank_transaction):
    """Remove reconciliation from a bank transaction"""
    txn = frappe.get_doc("Bank Transaction", bank_transaction)
    txn.unreconcile()
    return {"success": True, "message": _("Reconciliation removed")}


@frappe.whitelist()
def auto_reconcile(bank_account, from_date, to_date, min_confidence=80):
    """Auto-reconcile transactions with high confidence matches"""
    tool = BankReconciliationTool(bank_account, from_date, to_date)
    matches = tool.auto_match()

    reconciled = 0
    for match in matches:
        if match.get("confidence", 0) >= int(min_confidence):
            try:
                txn = frappe.get_doc("Bank Transaction", match["bank_transaction"])
                txn.reconcile_with_payment_entry(match["payment_entry"], "Auto")
                reconciled += 1
            except Exception as e:
                frappe.log_error(f"Auto-reconcile error: {str(e)}", "Bank Reconciliation")

    return {
        "matched": reconciled,
        "total_suggested": len(matches)
    }


@frappe.whitelist()
def import_statement_data(bank_account, bank_format, file_content):
    """Import bank statement from raw file content"""
    # Map format to bank name
    bank_mapping = {
        "hdfc": "HDFC Bank",
        "icici": "ICICI Bank",
        "sbi": "SBI",
        "axis": "Axis Bank",
        "generic": "Generic"
    }

    bank_name = bank_mapping.get(bank_format, "Generic")
    importer = BankStatementImporter(bank_account, bank_name)

    # Convert string content to bytes if needed
    if isinstance(file_content, str):
        file_content = file_content.encode('utf-8')

    return importer.import_csv(file_content)

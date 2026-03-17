# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Integration tests for stock movements and inventory tracking
"""

import frappe
import unittest
from frappe.utils import flt, nowdate


class TestStockMovements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create UOM
        if not frappe.db.exists("UOM", "Test UOM SM"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM SM"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

        # Create Item Group
        if not frappe.db.exists("Inventory Item Group", "Test Item Group SM"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group SM"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Warehouses
        for wh in ["SM Warehouse A", "SM Warehouse B", "SM Warehouse C"]:
            if not frappe.db.exists("Warehouse", wh):
                doc = frappe.new_doc("Warehouse")
                doc.warehouse_name = wh
                doc.warehouse_type = "Main Store"
                doc.is_group = 0
                doc.is_active = 1
                doc.insert(ignore_permissions=True)

        # Create Items
        for i in range(1, 4):
            item_code = f"TEST-SM-ITEM-{i}"
            if not frappe.db.exists("Inventory Item", item_code):
                doc = frappe.new_doc("Inventory Item")
                doc.item_code = item_code
                doc.item_name = f"Test SM Item {i}"
                doc.item_group = "Test Item Group SM"
                doc.unit_of_measure = "Test UOM SM"
                doc.maintain_stock = 1
                doc.standard_rate = 100 * i
                doc.insert(ignore_permissions=True)

    def test_stock_balance_after_receipt(self):
        """Test stock balance updates correctly after material receipt"""
        # Initial receipt
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.append("items", {
            "item_code": "TEST-SM-ITEM-1",
            "qty": 100,
            "rate": 100,
            "t_warehouse": "SM Warehouse A"
        })
        se.insert(ignore_permissions=True)
        se.submit()

        # Check stock balance
        balance = get_stock_balance("TEST-SM-ITEM-1", "SM Warehouse A")
        self.assertGreaterEqual(flt(balance), 100)

        # Clean up
        se.cancel()
        frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_stock_balance_after_issue(self):
        """Test stock balance updates correctly after material issue"""
        # First receipt stock
        se_receipt = frappe.new_doc("Stock Entry")
        se_receipt.entry_type = "Material Receipt"
        se_receipt.posting_date = nowdate()
        se_receipt.append("items", {
            "item_code": "TEST-SM-ITEM-2",
            "qty": 200,
            "rate": 200,
            "t_warehouse": "SM Warehouse A"
        })
        se_receipt.insert(ignore_permissions=True)
        se_receipt.submit()

        # Issue stock
        se_issue = frappe.new_doc("Stock Entry")
        se_issue.entry_type = "Material Issue"
        se_issue.posting_date = nowdate()
        se_issue.append("items", {
            "item_code": "TEST-SM-ITEM-2",
            "qty": 50,
            "s_warehouse": "SM Warehouse A"
        })
        se_issue.insert(ignore_permissions=True)
        se_issue.submit()

        # Check balance
        balance = get_stock_balance("TEST-SM-ITEM-2", "SM Warehouse A")
        self.assertGreaterEqual(flt(balance), 150)

        # Clean up
        se_issue.cancel()
        se_receipt.cancel()
        frappe.delete_doc("Stock Entry", se_issue.name, force=True)
        frappe.delete_doc("Stock Entry", se_receipt.name, force=True)

    def test_inter_warehouse_transfer(self):
        """Test stock transfer between warehouses"""
        # Receipt in source warehouse
        se_receipt = frappe.new_doc("Stock Entry")
        se_receipt.entry_type = "Material Receipt"
        se_receipt.posting_date = nowdate()
        se_receipt.append("items", {
            "item_code": "TEST-SM-ITEM-3",
            "qty": 100,
            "rate": 300,
            "t_warehouse": "SM Warehouse A"
        })
        se_receipt.insert(ignore_permissions=True)
        se_receipt.submit()

        # Transfer to another warehouse
        se_transfer = frappe.new_doc("Stock Entry")
        se_transfer.entry_type = "Material Transfer"
        se_transfer.posting_date = nowdate()
        se_transfer.append("items", {
            "item_code": "TEST-SM-ITEM-3",
            "qty": 60,
            "s_warehouse": "SM Warehouse A",
            "t_warehouse": "SM Warehouse B"
        })
        se_transfer.insert(ignore_permissions=True)
        se_transfer.submit()

        # Check balances
        balance_a = get_stock_balance("TEST-SM-ITEM-3", "SM Warehouse A")
        balance_b = get_stock_balance("TEST-SM-ITEM-3", "SM Warehouse B")

        self.assertGreaterEqual(flt(balance_a), 40)
        self.assertGreaterEqual(flt(balance_b), 60)

        # Clean up
        se_transfer.cancel()
        se_receipt.cancel()
        frappe.delete_doc("Stock Entry", se_transfer.name, force=True)
        frappe.delete_doc("Stock Entry", se_receipt.name, force=True)

    def test_multiple_warehouse_stock(self):
        """Test stock tracking across multiple warehouses"""
        stock_entries = []

        # Create stock in multiple warehouses
        warehouses = ["SM Warehouse A", "SM Warehouse B", "SM Warehouse C"]
        for i, wh in enumerate(warehouses):
            se = frappe.new_doc("Stock Entry")
            se.entry_type = "Material Receipt"
            se.posting_date = nowdate()
            se.append("items", {
                "item_code": "TEST-SM-ITEM-1",
                "qty": 50 * (i + 1),
                "rate": 100,
                "t_warehouse": wh
            })
            se.insert(ignore_permissions=True)
            se.submit()
            stock_entries.append(se)

        # Check total stock across all warehouses
        total_stock = 0
        for wh in warehouses:
            total_stock += get_stock_balance("TEST-SM-ITEM-1", wh)

        self.assertGreaterEqual(flt(total_stock), 300)  # 50 + 100 + 150

        # Clean up
        for se in reversed(stock_entries):
            se.cancel()
            frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_stock_ledger_entries_created(self):
        """Test that stock ledger entries are created correctly"""
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.append("items", {
            "item_code": "TEST-SM-ITEM-1",
            "qty": 75,
            "rate": 100,
            "t_warehouse": "SM Warehouse A"
        })
        se.insert(ignore_permissions=True)
        se.submit()

        # Check SLE was created
        sle = frappe.get_all(
            "Stock Ledger Entry",
            filters={
                "voucher_type": "Stock Entry",
                "voucher_no": se.name,
                "docstatus": 1
            },
            fields=["actual_qty", "warehouse", "item_code"]
        )

        self.assertTrue(len(sle) > 0)
        self.assertEqual(sle[0]["item_code"], "TEST-SM-ITEM-1")
        self.assertEqual(sle[0]["warehouse"], "SM Warehouse A")
        self.assertEqual(flt(sle[0]["actual_qty"]), 75)

        # Clean up
        se.cancel()
        frappe.delete_doc("Stock Entry", se.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()


def get_stock_balance(item_code, warehouse):
    """Helper to get stock balance"""
    balance = frappe.db.sql("""
        SELECT SUM(actual_qty) as qty
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s AND warehouse = %s
        AND docstatus < 2 AND is_cancelled = 0
    """, (item_code, warehouse))

    return flt(balance[0][0]) if balance and balance[0][0] else 0

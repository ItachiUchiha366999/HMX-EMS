# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt, nowdate, now_datetime


class TestStockEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create UOM
        if not frappe.db.exists("UOM", "Test UOM SE"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM SE"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

        # Create Item Group
        if not frappe.db.exists("Inventory Item Group", "Test Item Group SE"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group SE"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Warehouses
        for wh in ["Test Source Warehouse", "Test Target Warehouse"]:
            if not frappe.db.exists("Warehouse", wh):
                doc = frappe.new_doc("Warehouse")
                doc.warehouse_name = wh
                doc.warehouse_type = "Main Store"
                doc.is_group = 0
                doc.is_active = 1
                doc.insert(ignore_permissions=True)

        # Create Test Item
        if not frappe.db.exists("Inventory Item", "TEST-STOCK-ITEM"):
            doc = frappe.new_doc("Inventory Item")
            doc.item_code = "TEST-STOCK-ITEM"
            doc.item_name = "Test Stock Item"
            doc.item_group = "Test Item Group SE"
            doc.unit_of_measure = "Test UOM SE"
            doc.maintain_stock = 1
            doc.standard_rate = 100
            doc.insert(ignore_permissions=True)

    def test_material_receipt(self):
        """Test Material Receipt stock entry"""
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.to_warehouse = "Test Target Warehouse"
        se.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 10,
            "rate": 100,
            "t_warehouse": "Test Target Warehouse"
        })
        se.insert(ignore_permissions=True)
        se.submit()

        self.assertEqual(se.docstatus, 1)
        self.assertEqual(se.total_qty, 10)
        self.assertEqual(se.total_amount, 1000)

        # Check stock ledger entry created
        sle = frappe.get_all(
            "Stock Ledger Entry",
            filters={"voucher_no": se.name, "docstatus": 1},
            fields=["actual_qty", "warehouse"]
        )
        self.assertTrue(len(sle) > 0)

        # Cancel and clean up
        se.cancel()
        frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_material_issue(self):
        """Test Material Issue stock entry"""
        # First create stock via Material Receipt
        se_receipt = frappe.new_doc("Stock Entry")
        se_receipt.entry_type = "Material Receipt"
        se_receipt.posting_date = nowdate()
        se_receipt.to_warehouse = "Test Source Warehouse"
        se_receipt.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 20,
            "rate": 100,
            "t_warehouse": "Test Source Warehouse"
        })
        se_receipt.insert(ignore_permissions=True)
        se_receipt.submit()

        # Now create Material Issue
        se_issue = frappe.new_doc("Stock Entry")
        se_issue.entry_type = "Material Issue"
        se_issue.posting_date = nowdate()
        se_issue.from_warehouse = "Test Source Warehouse"
        se_issue.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 5,
            "s_warehouse": "Test Source Warehouse"
        })
        se_issue.insert(ignore_permissions=True)
        se_issue.submit()

        self.assertEqual(se_issue.docstatus, 1)
        self.assertEqual(se_issue.total_qty, 5)

        # Clean up
        se_issue.cancel()
        se_receipt.cancel()
        frappe.delete_doc("Stock Entry", se_issue.name, force=True)
        frappe.delete_doc("Stock Entry", se_receipt.name, force=True)

    def test_material_transfer(self):
        """Test Material Transfer between warehouses"""
        # Create stock in source warehouse
        se_receipt = frappe.new_doc("Stock Entry")
        se_receipt.entry_type = "Material Receipt"
        se_receipt.posting_date = nowdate()
        se_receipt.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 15,
            "rate": 100,
            "t_warehouse": "Test Source Warehouse"
        })
        se_receipt.insert(ignore_permissions=True)
        se_receipt.submit()

        # Transfer stock
        se_transfer = frappe.new_doc("Stock Entry")
        se_transfer.entry_type = "Material Transfer"
        se_transfer.posting_date = nowdate()
        se_transfer.from_warehouse = "Test Source Warehouse"
        se_transfer.to_warehouse = "Test Target Warehouse"
        se_transfer.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 10,
            "s_warehouse": "Test Source Warehouse",
            "t_warehouse": "Test Target Warehouse"
        })
        se_transfer.insert(ignore_permissions=True)
        se_transfer.submit()

        self.assertEqual(se_transfer.docstatus, 1)

        # Clean up
        se_transfer.cancel()
        se_receipt.cancel()
        frappe.delete_doc("Stock Entry", se_transfer.name, force=True)
        frappe.delete_doc("Stock Entry", se_receipt.name, force=True)

    def test_stock_entry_cancellation(self):
        """Test that cancellation reverses stock"""
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 50,
            "rate": 100,
            "t_warehouse": "Test Target Warehouse"
        })
        se.insert(ignore_permissions=True)
        se.submit()

        # Cancel
        se.cancel()
        self.assertEqual(se.docstatus, 2)

        # Clean up
        frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_calculate_totals(self):
        """Test automatic calculation of totals"""
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 10,
            "rate": 150,
            "t_warehouse": "Test Target Warehouse"
        })
        se.append("items", {
            "item_code": "TEST-STOCK-ITEM",
            "qty": 5,
            "rate": 200,
            "t_warehouse": "Test Target Warehouse"
        })
        se.insert(ignore_permissions=True)

        self.assertEqual(se.total_qty, 15)
        self.assertEqual(se.total_amount, 2500)  # (10*150) + (5*200)

        # Clean up
        frappe.delete_doc("Stock Entry", se.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

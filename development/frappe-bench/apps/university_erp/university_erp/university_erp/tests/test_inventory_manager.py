# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt, nowdate, add_days
from university_erp.university_erp.inventory_manager import InventoryManager


class TestInventoryManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()
        cls.manager = InventoryManager()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create UOM
        if not frappe.db.exists("UOM", "Test UOM IM"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM IM"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

        # Create Item Group
        if not frappe.db.exists("Inventory Item Group", "Test Item Group IM"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group IM"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Warehouse
        if not frappe.db.exists("Warehouse", "Test Warehouse IM"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test Warehouse IM"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

        # Create Test Item
        if not frappe.db.exists("Inventory Item", "TEST-IM-ITEM"):
            doc = frappe.new_doc("Inventory Item")
            doc.item_code = "TEST-IM-ITEM"
            doc.item_name = "Test IM Item"
            doc.item_group = "Test Item Group IM"
            doc.unit_of_measure = "Test UOM IM"
            doc.maintain_stock = 1
            doc.standard_rate = 100
            doc.reorder_level = 10
            doc.reorder_quantity = 50
            doc.insert(ignore_permissions=True)

    def test_get_stock_balance(self):
        """Test getting stock balance"""
        # Create some stock first
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.append("items", {
            "item_code": "TEST-IM-ITEM",
            "qty": 100,
            "rate": 100,
            "t_warehouse": "Test Warehouse IM"
        })
        se.insert(ignore_permissions=True)
        se.submit()

        # Test get_stock_balance
        balance = self.manager.get_stock_balance("TEST-IM-ITEM", "Test Warehouse IM")
        self.assertGreaterEqual(flt(balance), 100)

        # Clean up
        se.cancel()
        frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_get_low_stock_items(self):
        """Test getting low stock items"""
        # This tests the method exists and returns a list
        low_stock = self.manager.get_low_stock_items("Test Warehouse IM")
        self.assertIsInstance(low_stock, list)

    def test_create_stock_entry(self):
        """Test creating stock entry via manager"""
        items = [{
            "item_code": "TEST-IM-ITEM",
            "qty": 25,
            "rate": 100
        }]

        se = self.manager.create_stock_entry(
            entry_type="Material Receipt",
            items=items,
            to_warehouse="Test Warehouse IM",
            posting_date=nowdate()
        )

        self.assertTrue(se)
        self.assertEqual(se.entry_type, "Material Receipt")

        # Clean up
        if se.docstatus == 1:
            se.cancel()
        frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_get_stock_ledger(self):
        """Test getting stock ledger entries"""
        # Create stock entry
        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Receipt"
        se.posting_date = nowdate()
        se.append("items", {
            "item_code": "TEST-IM-ITEM",
            "qty": 50,
            "rate": 100,
            "t_warehouse": "Test Warehouse IM"
        })
        se.insert(ignore_permissions=True)
        se.submit()

        # Get stock ledger
        ledger = self.manager.get_stock_ledger(
            item_code="TEST-IM-ITEM",
            warehouse="Test Warehouse IM",
            from_date=add_days(nowdate(), -7),
            to_date=nowdate()
        )

        self.assertIsInstance(ledger, list)

        # Clean up
        se.cancel()
        frappe.delete_doc("Stock Entry", se.name, force=True)

    def test_get_stock_summary_report(self):
        """Test stock summary report generation"""
        summary = self.manager.get_stock_summary_report("Test Warehouse IM")
        self.assertIsInstance(summary, list)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt, nowdate


class TestInventoryItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_uom()
        cls.create_test_item_group()
        cls.create_test_warehouse()

    @classmethod
    def create_test_uom(cls):
        """Create test UOM"""
        if not frappe.db.exists("UOM", "Test UOM"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

    @classmethod
    def create_test_item_group(cls):
        """Create test item group"""
        if not frappe.db.exists("Inventory Item Group", "Test Item Group"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

    @classmethod
    def create_test_warehouse(cls):
        """Create test warehouse"""
        if not frappe.db.exists("Warehouse", "Test Warehouse"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test Warehouse"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

    def test_create_inventory_item(self):
        """Test creating an inventory item"""
        item = frappe.new_doc("Inventory Item")
        item.item_name = "Test Item"
        item.item_group = "Test Item Group"
        item.unit_of_measure = "Test UOM"
        item.item_type = "Stock Item"
        item.maintain_stock = 1
        item.default_warehouse = "Test Warehouse"
        item.insert(ignore_permissions=True)

        self.assertTrue(frappe.db.exists("Inventory Item", item.name))

        # Clean up
        frappe.delete_doc("Inventory Item", item.name, force=True)

    def test_item_code_generation(self):
        """Test automatic item code generation"""
        item = frappe.new_doc("Inventory Item")
        item.item_name = "Auto Code Item"
        item.item_group = "Test Item Group"
        item.unit_of_measure = "Test UOM"
        item.insert(ignore_permissions=True)

        self.assertTrue(item.item_code)
        self.assertTrue(item.item_code.startswith("ITEM-"))

        # Clean up
        frappe.delete_doc("Inventory Item", item.name, force=True)

    def test_reorder_level_validation(self):
        """Test that reorder level triggers alerts"""
        item = frappe.new_doc("Inventory Item")
        item.item_name = "Reorder Test Item"
        item.item_group = "Test Item Group"
        item.unit_of_measure = "Test UOM"
        item.maintain_stock = 1
        item.reorder_level = 10
        item.reorder_quantity = 50
        item.insert(ignore_permissions=True)

        self.assertEqual(item.reorder_level, 10)
        self.assertEqual(item.reorder_quantity, 50)

        # Clean up
        frappe.delete_doc("Inventory Item", item.name, force=True)

    def test_valuation_method(self):
        """Test default valuation method"""
        item = frappe.new_doc("Inventory Item")
        item.item_name = "Valuation Test Item"
        item.item_group = "Test Item Group"
        item.unit_of_measure = "Test UOM"
        item.insert(ignore_permissions=True)

        self.assertEqual(item.valuation_method, "FIFO")

        # Clean up
        frappe.delete_doc("Inventory Item", item.name, force=True)

    def test_item_specifications(self):
        """Test adding specifications to item"""
        item = frappe.new_doc("Inventory Item")
        item.item_name = "Spec Test Item"
        item.item_group = "Test Item Group"
        item.unit_of_measure = "Test UOM"
        item.append("specifications", {
            "specification": "Color",
            "value": "Blue"
        })
        item.append("specifications", {
            "specification": "Size",
            "value": "Large"
        })
        item.insert(ignore_permissions=True)

        self.assertEqual(len(item.specifications), 2)

        # Clean up
        frappe.delete_doc("Inventory Item", item.name, force=True)

    def test_duplicate_item_code(self):
        """Test that duplicate item codes are not allowed"""
        item1 = frappe.new_doc("Inventory Item")
        item1.item_code = "UNIQUE-001"
        item1.item_name = "First Item"
        item1.item_group = "Test Item Group"
        item1.unit_of_measure = "Test UOM"
        item1.insert(ignore_permissions=True)

        item2 = frappe.new_doc("Inventory Item")
        item2.item_code = "UNIQUE-001"
        item2.item_name = "Second Item"
        item2.item_group = "Test Item Group"
        item2.unit_of_measure = "Test UOM"

        with self.assertRaises(frappe.exceptions.DuplicateEntryError):
            item2.insert(ignore_permissions=True)

        # Clean up
        frappe.delete_doc("Inventory Item", item1.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

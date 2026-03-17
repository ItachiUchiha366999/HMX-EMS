# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt, nowdate, add_days


class TestPurchaseOrder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create UOM
        if not frappe.db.exists("UOM", "Test UOM PO"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM PO"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

        # Create Item Group
        if not frappe.db.exists("Inventory Item Group", "Test Item Group PO"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group PO"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Supplier Group
        if not frappe.db.exists("Supplier Group", "Test Supplier Group"):
            doc = frappe.new_doc("Supplier Group")
            doc.supplier_group_name = "Test Supplier Group"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Supplier
        if not frappe.db.exists("Supplier", "Test Supplier PO"):
            doc = frappe.new_doc("Supplier")
            doc.supplier_name = "Test Supplier PO"
            doc.supplier_type = "Company"
            doc.supplier_group = "Test Supplier Group"
            doc.insert(ignore_permissions=True)

        # Create Item
        if not frappe.db.exists("Inventory Item", "TEST-PO-ITEM"):
            doc = frappe.new_doc("Inventory Item")
            doc.item_code = "TEST-PO-ITEM"
            doc.item_name = "Test PO Item"
            doc.item_group = "Test Item Group PO"
            doc.unit_of_measure = "Test UOM PO"
            doc.maintain_stock = 1
            doc.standard_rate = 500
            doc.insert(ignore_permissions=True)

        # Create Warehouse
        if not frappe.db.exists("Warehouse", "Test PO Warehouse"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test PO Warehouse"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

    def test_create_purchase_order(self):
        """Test creating a purchase order"""
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Supplier PO"
        po.transaction_date = nowdate()
        po.delivery_date = add_days(nowdate(), 7)
        po.append("items", {
            "item_code": "TEST-PO-ITEM",
            "qty": 10,
            "rate": 500,
            "warehouse": "Test PO Warehouse"
        })
        po.insert(ignore_permissions=True)

        self.assertTrue(frappe.db.exists("Purchase Order", po.name))
        self.assertEqual(po.status, "Draft")

        # Clean up
        frappe.delete_doc("Purchase Order", po.name, force=True)

    def test_purchase_order_totals(self):
        """Test automatic calculation of totals"""
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Supplier PO"
        po.transaction_date = nowdate()
        po.append("items", {
            "item_code": "TEST-PO-ITEM",
            "qty": 10,
            "rate": 500,
            "warehouse": "Test PO Warehouse"
        })
        po.append("items", {
            "item_code": "TEST-PO-ITEM",
            "qty": 5,
            "rate": 600,
            "warehouse": "Test PO Warehouse"
        })
        po.insert(ignore_permissions=True)

        self.assertEqual(po.total_qty, 15)
        self.assertEqual(po.total, 8000)  # (10*500) + (5*600)
        self.assertEqual(po.grand_total, 8000)

        # Clean up
        frappe.delete_doc("Purchase Order", po.name, force=True)

    def test_purchase_order_submit(self):
        """Test submitting a purchase order"""
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Supplier PO"
        po.transaction_date = nowdate()
        po.delivery_date = add_days(nowdate(), 7)
        po.append("items", {
            "item_code": "TEST-PO-ITEM",
            "qty": 10,
            "rate": 500,
            "warehouse": "Test PO Warehouse"
        })
        po.insert(ignore_permissions=True)
        po.submit()

        self.assertEqual(po.docstatus, 1)
        self.assertEqual(po.status, "To Receive and Bill")

        # Cancel and clean up
        po.cancel()
        frappe.delete_doc("Purchase Order", po.name, force=True)

    def test_purchase_order_item_discount(self):
        """Test item level discount calculation"""
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Supplier PO"
        po.transaction_date = nowdate()
        po.append("items", {
            "item_code": "TEST-PO-ITEM",
            "qty": 10,
            "rate": 500,
            "discount_percentage": 10,
            "warehouse": "Test PO Warehouse"
        })
        po.insert(ignore_permissions=True)

        item = po.items[0]
        expected_discount = 500  # 10% of 5000
        self.assertEqual(flt(item.discount_amount), flt(expected_discount))

        # Clean up
        frappe.delete_doc("Purchase Order", po.name, force=True)

    def test_purchase_order_taxes(self):
        """Test tax calculation in purchase order"""
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Supplier PO"
        po.transaction_date = nowdate()
        po.append("items", {
            "item_code": "TEST-PO-ITEM",
            "qty": 10,
            "rate": 1000,
            "warehouse": "Test PO Warehouse"
        })
        po.append("taxes", {
            "charge_type": "On Net Total",
            "account_head": "GST",
            "description": "GST 18%",
            "rate": 18
        })
        po.insert(ignore_permissions=True)

        expected_tax = 1800  # 18% of 10000
        self.assertEqual(flt(po.total_taxes_and_charges), flt(expected_tax))
        self.assertEqual(flt(po.grand_total), 11800)  # 10000 + 1800

        # Clean up
        frappe.delete_doc("Purchase Order", po.name, force=True)

    def test_purchase_order_validation_no_items(self):
        """Test that PO without items fails validation"""
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Supplier PO"
        po.transaction_date = nowdate()

        with self.assertRaises(frappe.exceptions.ValidationError):
            po.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

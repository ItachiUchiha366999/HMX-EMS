# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt, nowdate, add_days


class TestMaterialRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create UOM
        if not frappe.db.exists("UOM", "Test UOM MR"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM MR"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

        # Create Item Group
        if not frappe.db.exists("Inventory Item Group", "Test Item Group MR"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group MR"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Warehouse
        if not frappe.db.exists("Warehouse", "Test MR Warehouse"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test MR Warehouse"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

        # Create Item
        if not frappe.db.exists("Inventory Item", "TEST-MR-ITEM"):
            doc = frappe.new_doc("Inventory Item")
            doc.item_code = "TEST-MR-ITEM"
            doc.item_name = "Test MR Item"
            doc.item_group = "Test Item Group MR"
            doc.unit_of_measure = "Test UOM MR"
            doc.maintain_stock = 1
            doc.standard_rate = 200
            doc.insert(ignore_permissions=True)

    def test_create_material_request(self):
        """Test creating a material request"""
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.transaction_date = nowdate()
        mr.required_by = add_days(nowdate(), 5)
        mr.append("items", {
            "item_code": "TEST-MR-ITEM",
            "qty": 10,
            "warehouse": "Test MR Warehouse"
        })
        mr.insert(ignore_permissions=True)

        self.assertTrue(frappe.db.exists("Material Request", mr.name))
        self.assertEqual(mr.status, "Draft")

        # Clean up
        frappe.delete_doc("Material Request", mr.name, force=True)

    def test_material_request_types(self):
        """Test different material request types"""
        for mr_type in ["Purchase", "Material Transfer", "Material Issue"]:
            mr = frappe.new_doc("Material Request")
            mr.material_request_type = mr_type
            mr.transaction_date = nowdate()
            mr.append("items", {
                "item_code": "TEST-MR-ITEM",
                "qty": 5,
                "warehouse": "Test MR Warehouse"
            })
            mr.insert(ignore_permissions=True)

            self.assertEqual(mr.material_request_type, mr_type)

            # Clean up
            frappe.delete_doc("Material Request", mr.name, force=True)

    def test_material_request_submit(self):
        """Test submitting a material request"""
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.transaction_date = nowdate()
        mr.required_by = add_days(nowdate(), 5)
        mr.append("items", {
            "item_code": "TEST-MR-ITEM",
            "qty": 10,
            "warehouse": "Test MR Warehouse"
        })
        mr.insert(ignore_permissions=True)
        mr.submit()

        self.assertEqual(mr.docstatus, 1)
        self.assertEqual(mr.status, "Pending")

        # Cancel and clean up
        mr.cancel()
        frappe.delete_doc("Material Request", mr.name, force=True)

    def test_material_request_validation_no_items(self):
        """Test that MR without items fails validation"""
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.transaction_date = nowdate()

        with self.assertRaises(frappe.exceptions.ValidationError):
            mr.insert(ignore_permissions=True)

    def test_material_request_item_rate(self):
        """Test item rate in material request"""
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.transaction_date = nowdate()
        mr.append("items", {
            "item_code": "TEST-MR-ITEM",
            "qty": 10,
            "rate": 250,
            "warehouse": "Test MR Warehouse"
        })
        mr.insert(ignore_permissions=True)

        item = mr.items[0]
        self.assertEqual(flt(item.amount), 2500)  # 10 * 250

        # Clean up
        frappe.delete_doc("Material Request", mr.name, force=True)

    def test_material_request_cancel(self):
        """Test cancelling a material request"""
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.transaction_date = nowdate()
        mr.append("items", {
            "item_code": "TEST-MR-ITEM",
            "qty": 5,
            "warehouse": "Test MR Warehouse"
        })
        mr.insert(ignore_permissions=True)
        mr.submit()
        mr.cancel()

        self.assertEqual(mr.docstatus, 2)
        self.assertEqual(mr.status, "Cancelled")

        # Clean up
        frappe.delete_doc("Material Request", mr.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

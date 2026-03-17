# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Integration tests for the complete purchase workflow:
Material Request -> Purchase Order -> Purchase Receipt -> Stock Entry
"""

import frappe
import unittest
from frappe.utils import flt, nowdate, add_days


class TestPurchaseWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the complete workflow"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create all test dependencies"""
        # Create UOM
        if not frappe.db.exists("UOM", "Test UOM PW"):
            doc = frappe.new_doc("UOM")
            doc.uom_name = "Test UOM PW"
            doc.must_be_whole_number = 1
            doc.enabled = 1
            doc.insert(ignore_permissions=True)

        # Create Item Group
        if not frappe.db.exists("Inventory Item Group", "Test Item Group PW"):
            doc = frappe.new_doc("Inventory Item Group")
            doc.group_name = "Test Item Group PW"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Supplier Group
        if not frappe.db.exists("Supplier Group", "Test Supplier Group PW"):
            doc = frappe.new_doc("Supplier Group")
            doc.supplier_group_name = "Test Supplier Group PW"
            doc.is_group = 0
            doc.insert(ignore_permissions=True)

        # Create Supplier
        if not frappe.db.exists("Supplier", "Test Workflow Supplier"):
            doc = frappe.new_doc("Supplier")
            doc.supplier_name = "Test Workflow Supplier"
            doc.supplier_type = "Company"
            doc.supplier_group = "Test Supplier Group PW"
            doc.insert(ignore_permissions=True)

        # Create Warehouse
        if not frappe.db.exists("Warehouse", "Test Workflow Warehouse"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test Workflow Warehouse"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

        # Create Item
        if not frappe.db.exists("Inventory Item", "TEST-PW-ITEM"):
            doc = frappe.new_doc("Inventory Item")
            doc.item_code = "TEST-PW-ITEM"
            doc.item_name = "Test Workflow Item"
            doc.item_group = "Test Item Group PW"
            doc.unit_of_measure = "Test UOM PW"
            doc.maintain_stock = 1
            doc.standard_rate = 500
            doc.insert(ignore_permissions=True)

    def test_complete_purchase_workflow(self):
        """Test the complete purchase workflow from MR to stock receipt"""
        # Step 1: Create Material Request
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.transaction_date = nowdate()
        mr.required_by = add_days(nowdate(), 7)
        mr.append("items", {
            "item_code": "TEST-PW-ITEM",
            "qty": 100,
            "warehouse": "Test Workflow Warehouse"
        })
        mr.insert(ignore_permissions=True)
        mr.submit()

        self.assertEqual(mr.docstatus, 1)
        self.assertEqual(mr.status, "Pending")

        # Step 2: Create Purchase Order from Material Request
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Workflow Supplier"
        po.transaction_date = nowdate()
        po.delivery_date = add_days(nowdate(), 7)
        po.material_request = mr.name
        po.append("items", {
            "item_code": "TEST-PW-ITEM",
            "qty": 100,
            "rate": 500,
            "warehouse": "Test Workflow Warehouse",
            "material_request": mr.name,
            "material_request_item": mr.items[0].name
        })
        po.insert(ignore_permissions=True)
        po.submit()

        self.assertEqual(po.docstatus, 1)
        self.assertEqual(po.status, "To Receive and Bill")

        # Step 3: Create Purchase Receipt from Purchase Order
        pr = frappe.new_doc("Purchase Receipt")
        pr.supplier = "Test Workflow Supplier"
        pr.posting_date = nowdate()
        pr.purchase_order = po.name
        pr.set_warehouse = "Test Workflow Warehouse"
        pr.append("items", {
            "item_code": "TEST-PW-ITEM",
            "qty": 100,
            "rate": 500,
            "warehouse": "Test Workflow Warehouse",
            "purchase_order": po.name,
            "purchase_order_item": po.items[0].name
        })
        pr.insert(ignore_permissions=True)
        pr.submit()

        self.assertEqual(pr.docstatus, 1)

        # Verify stock was received
        stock_ledger = frappe.get_all(
            "Stock Ledger Entry",
            filters={
                "voucher_type": "Purchase Receipt",
                "voucher_no": pr.name,
                "docstatus": 1
            },
            fields=["actual_qty", "warehouse"]
        )

        # Should have created stock ledger entries
        self.assertTrue(len(stock_ledger) > 0)

        # Clean up in reverse order
        pr.cancel()
        po.cancel()
        mr.cancel()

        frappe.delete_doc("Purchase Receipt", pr.name, force=True)
        frappe.delete_doc("Purchase Order", po.name, force=True)
        frappe.delete_doc("Material Request", mr.name, force=True)

    def test_partial_receipt_workflow(self):
        """Test partial receipt against purchase order"""
        # Create Purchase Order
        po = frappe.new_doc("Purchase Order")
        po.supplier = "Test Workflow Supplier"
        po.transaction_date = nowdate()
        po.delivery_date = add_days(nowdate(), 7)
        po.append("items", {
            "item_code": "TEST-PW-ITEM",
            "qty": 100,
            "rate": 500,
            "warehouse": "Test Workflow Warehouse"
        })
        po.insert(ignore_permissions=True)
        po.submit()

        # Create first partial receipt (50%)
        pr1 = frappe.new_doc("Purchase Receipt")
        pr1.supplier = "Test Workflow Supplier"
        pr1.posting_date = nowdate()
        pr1.purchase_order = po.name
        pr1.append("items", {
            "item_code": "TEST-PW-ITEM",
            "qty": 50,  # Partial receipt
            "rate": 500,
            "warehouse": "Test Workflow Warehouse",
            "purchase_order": po.name,
            "purchase_order_item": po.items[0].name
        })
        pr1.insert(ignore_permissions=True)
        pr1.submit()

        # Create second partial receipt (remaining 50%)
        pr2 = frappe.new_doc("Purchase Receipt")
        pr2.supplier = "Test Workflow Supplier"
        pr2.posting_date = nowdate()
        pr2.purchase_order = po.name
        pr2.append("items", {
            "item_code": "TEST-PW-ITEM",
            "qty": 50,  # Remaining
            "rate": 500,
            "warehouse": "Test Workflow Warehouse",
            "purchase_order": po.name,
            "purchase_order_item": po.items[0].name
        })
        pr2.insert(ignore_permissions=True)
        pr2.submit()

        # Clean up
        pr2.cancel()
        pr1.cancel()
        po.cancel()

        frappe.delete_doc("Purchase Receipt", pr2.name, force=True)
        frappe.delete_doc("Purchase Receipt", pr1.name, force=True)
        frappe.delete_doc("Purchase Order", po.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

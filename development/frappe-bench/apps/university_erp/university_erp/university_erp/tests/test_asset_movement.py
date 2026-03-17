# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import nowdate


class TestAssetMovement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create Asset Category
        if not frappe.db.exists("Asset Category", "Test Asset Category AM"):
            doc = frappe.new_doc("Asset Category")
            doc.category_name = "Test Asset Category AM"
            doc.depreciation_method = "Straight Line"
            doc.total_number_of_depreciations = 5
            doc.frequency_of_depreciation = 12
            doc.insert(ignore_permissions=True)

        # Create Warehouses (Locations)
        for wh in ["Source Location AM", "Target Location AM"]:
            if not frappe.db.exists("Warehouse", wh):
                doc = frappe.new_doc("Warehouse")
                doc.warehouse_name = wh
                doc.warehouse_type = "Main Store"
                doc.is_group = 0
                doc.is_active = 1
                doc.insert(ignore_permissions=True)

        # Create Test Asset
        if not frappe.db.exists("Asset", {"asset_name": "Movement Test Asset"}):
            doc = frappe.new_doc("Asset")
            doc.asset_name = "Movement Test Asset"
            doc.asset_category = "Test Asset Category AM"
            doc.location = "Source Location AM"
            doc.purchase_date = nowdate()
            doc.gross_purchase_amount = 50000
            doc.insert(ignore_permissions=True)
            doc.submit()
            cls.test_asset = doc.name
        else:
            cls.test_asset = frappe.db.get_value(
                "Asset", {"asset_name": "Movement Test Asset"}, "name"
            )

    def test_create_asset_movement(self):
        """Test creating an asset movement"""
        am = frappe.new_doc("Asset Movement")
        am.purpose = "Transfer"
        am.transaction_date = nowdate()
        am.append("assets", {
            "asset": self.test_asset,
            "source_location": "Source Location AM",
            "target_location": "Target Location AM"
        })
        am.insert(ignore_permissions=True)

        self.assertTrue(frappe.db.exists("Asset Movement", am.name))

        # Clean up
        frappe.delete_doc("Asset Movement", am.name, force=True)

    def test_asset_movement_submit(self):
        """Test submitting asset movement updates asset location"""
        # Reset asset location
        frappe.db.set_value("Asset", self.test_asset, "location", "Source Location AM")

        am = frappe.new_doc("Asset Movement")
        am.purpose = "Transfer"
        am.transaction_date = nowdate()
        am.append("assets", {
            "asset": self.test_asset,
            "source_location": "Source Location AM",
            "target_location": "Target Location AM"
        })
        am.insert(ignore_permissions=True)
        am.submit()

        self.assertEqual(am.docstatus, 1)

        # Check asset location was updated
        asset_location = frappe.db.get_value("Asset", self.test_asset, "location")
        self.assertEqual(asset_location, "Target Location AM")

        # Cancel and clean up
        am.cancel()

        # Reset location after cancel
        frappe.db.set_value("Asset", self.test_asset, "location", "Source Location AM")
        frappe.delete_doc("Asset Movement", am.name, force=True)

    def test_asset_movement_cancel(self):
        """Test cancelling asset movement reverts location"""
        # Reset asset location
        frappe.db.set_value("Asset", self.test_asset, "location", "Source Location AM")

        am = frappe.new_doc("Asset Movement")
        am.purpose = "Transfer"
        am.transaction_date = nowdate()
        am.append("assets", {
            "asset": self.test_asset,
            "source_location": "Source Location AM",
            "target_location": "Target Location AM"
        })
        am.insert(ignore_permissions=True)
        am.submit()
        am.cancel()

        self.assertEqual(am.docstatus, 2)

        # Check asset location was reverted
        asset_location = frappe.db.get_value("Asset", self.test_asset, "location")
        self.assertEqual(asset_location, "Source Location AM")

        # Clean up
        frappe.delete_doc("Asset Movement", am.name, force=True)

    def test_asset_movement_purposes(self):
        """Test different movement purposes"""
        for purpose in ["Transfer", "Issue", "Receipt"]:
            am = frappe.new_doc("Asset Movement")
            am.purpose = purpose
            am.transaction_date = nowdate()
            am.append("assets", {
                "asset": self.test_asset,
                "source_location": "Source Location AM",
                "target_location": "Target Location AM"
            })
            am.insert(ignore_permissions=True)

            self.assertEqual(am.purpose, purpose)

            # Clean up
            frappe.delete_doc("Asset Movement", am.name, force=True)

    def test_asset_movement_validation_no_assets(self):
        """Test that movement without assets fails"""
        am = frappe.new_doc("Asset Movement")
        am.purpose = "Transfer"
        am.transaction_date = nowdate()

        with self.assertRaises(frappe.exceptions.ValidationError):
            am.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        # Cancel and delete test asset
        if hasattr(cls, 'test_asset') and frappe.db.exists("Asset", cls.test_asset):
            asset = frappe.get_doc("Asset", cls.test_asset)
            if asset.docstatus == 1:
                asset.cancel()
            frappe.delete_doc("Asset", cls.test_asset, force=True)
        frappe.db.rollback()

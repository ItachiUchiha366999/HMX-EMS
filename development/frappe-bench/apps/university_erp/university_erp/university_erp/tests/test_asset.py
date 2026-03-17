# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt, nowdate, add_days, add_months, getdate


class TestAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create Asset Category
        if not frappe.db.exists("Asset Category", "Test Asset Category"):
            doc = frappe.new_doc("Asset Category")
            doc.category_name = "Test Asset Category"
            doc.depreciation_method = "Straight Line"
            doc.total_number_of_depreciations = 5
            doc.frequency_of_depreciation = 12
            doc.insert(ignore_permissions=True)

        # Create Warehouse (Location)
        if not frappe.db.exists("Warehouse", "Test Asset Location"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test Asset Location"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

    def test_create_asset(self):
        """Test creating an asset"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Test Computer"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.purchase_date = nowdate()
        asset.gross_purchase_amount = 50000
        asset.insert(ignore_permissions=True)

        self.assertTrue(frappe.db.exists("Asset", asset.name))
        self.assertEqual(asset.status, "Draft")

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_asset_code_generation(self):
        """Test automatic asset code generation"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Auto Code Asset"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.purchase_date = nowdate()
        asset.gross_purchase_amount = 25000
        asset.insert(ignore_permissions=True)

        self.assertTrue(asset.name)
        self.assertTrue(asset.name.startswith("AST-"))

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_asset_depreciation_schedule(self):
        """Test depreciation schedule generation"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Depreciating Asset"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 60000
        asset.calculate_depreciation = 1
        asset.depreciation_method = "Straight Line"
        asset.total_number_of_depreciations = 5
        asset.frequency_of_depreciation = 12
        asset.depreciation_start_date = nowdate()
        asset.expected_value_after_useful_life = 0
        asset.insert(ignore_permissions=True)

        # Check depreciation schedule was created
        self.assertEqual(len(asset.depreciation_schedule), 5)

        # Each depreciation should be 12000 (60000 / 5)
        for schedule in asset.depreciation_schedule:
            self.assertEqual(flt(schedule.depreciation_amount), 12000)

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_asset_submit(self):
        """Test submitting an asset"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Submit Test Asset"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.purchase_date = nowdate()
        asset.gross_purchase_amount = 30000
        asset.insert(ignore_permissions=True)
        asset.submit()

        self.assertEqual(asset.docstatus, 1)
        self.assertEqual(asset.status, "Submitted")

        # Cancel and clean up
        asset.cancel()
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_asset_value_calculation(self):
        """Test asset value calculation"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Value Test Asset"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.purchase_date = nowdate()
        asset.gross_purchase_amount = 100000
        asset.opening_accumulated_depreciation = 20000
        asset.insert(ignore_permissions=True)

        expected_value = 80000  # 100000 - 20000
        self.assertEqual(flt(asset.asset_value), flt(expected_value))

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_asset_warranty_tracking(self):
        """Test asset warranty date tracking"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Warranty Test Asset"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.purchase_date = nowdate()
        asset.gross_purchase_amount = 45000
        asset.warranty_expiry_date = add_months(nowdate(), 12)
        asset.insert(ignore_permissions=True)

        self.assertEqual(getdate(asset.warranty_expiry_date), getdate(add_months(nowdate(), 12)))

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_existing_asset(self):
        """Test creating an existing asset"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Existing Asset"
        asset.asset_category = "Test Asset Category"
        asset.location = "Test Asset Location"
        asset.is_existing_asset = 1
        asset.purchase_date = add_months(nowdate(), -24)
        asset.gross_purchase_amount = 80000
        asset.opening_accumulated_depreciation = 32000
        asset.insert(ignore_permissions=True)

        self.assertEqual(asset.is_existing_asset, 1)
        self.assertEqual(flt(asset.asset_value), 48000)  # 80000 - 32000

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

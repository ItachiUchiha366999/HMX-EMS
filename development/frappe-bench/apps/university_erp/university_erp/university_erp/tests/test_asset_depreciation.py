# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Integration tests for asset depreciation calculations
"""

import frappe
import unittest
from frappe.utils import flt, nowdate, add_months, add_days, getdate


class TestAssetDepreciation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.create_test_dependencies()

    @classmethod
    def create_test_dependencies(cls):
        """Create test dependencies"""
        # Create Asset Categories with different depreciation methods
        categories = [
            {
                "category_name": "Test SL Category",
                "depreciation_method": "Straight Line",
                "total_number_of_depreciations": 5,
                "frequency_of_depreciation": 12
            },
            {
                "category_name": "Test WDV Category",
                "depreciation_method": "Written Down Value",
                "rate_of_depreciation": 20,
                "frequency_of_depreciation": 12
            },
            {
                "category_name": "Test DDB Category",
                "depreciation_method": "Double Declining Balance",
                "total_number_of_depreciations": 5,
                "frequency_of_depreciation": 12
            }
        ]

        for cat in categories:
            if not frappe.db.exists("Asset Category", cat["category_name"]):
                doc = frappe.new_doc("Asset Category")
                doc.update(cat)
                doc.insert(ignore_permissions=True)

        # Create Location
        if not frappe.db.exists("Warehouse", "Test Depreciation Location"):
            doc = frappe.new_doc("Warehouse")
            doc.warehouse_name = "Test Depreciation Location"
            doc.warehouse_type = "Main Store"
            doc.is_group = 0
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

    def test_straight_line_depreciation(self):
        """Test straight line depreciation calculation"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "SL Depreciation Test Asset"
        asset.asset_category = "Test SL Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 100000
        asset.calculate_depreciation = 1
        asset.depreciation_method = "Straight Line"
        asset.total_number_of_depreciations = 5
        asset.frequency_of_depreciation = 12
        asset.depreciation_start_date = nowdate()
        asset.expected_value_after_useful_life = 0
        asset.insert(ignore_permissions=True)

        # Check depreciation schedule
        self.assertEqual(len(asset.depreciation_schedule), 5)

        # Each depreciation should be 20000 (100000 / 5)
        for schedule in asset.depreciation_schedule:
            self.assertEqual(flt(schedule.depreciation_amount), 20000)

        # Total depreciation should equal gross purchase amount
        total_depreciation = sum(flt(s.depreciation_amount) for s in asset.depreciation_schedule)
        self.assertEqual(total_depreciation, 100000)

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_straight_line_with_salvage_value(self):
        """Test straight line depreciation with salvage value"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "SL Salvage Test Asset"
        asset.asset_category = "Test SL Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 100000
        asset.calculate_depreciation = 1
        asset.depreciation_method = "Straight Line"
        asset.total_number_of_depreciations = 5
        asset.frequency_of_depreciation = 12
        asset.depreciation_start_date = nowdate()
        asset.expected_value_after_useful_life = 10000  # Salvage value
        asset.insert(ignore_permissions=True)

        # Depreciable amount = 100000 - 10000 = 90000
        # Each depreciation = 90000 / 5 = 18000
        for schedule in asset.depreciation_schedule:
            self.assertEqual(flt(schedule.depreciation_amount), 18000)

        # Total depreciation should be 90000
        total_depreciation = sum(flt(s.depreciation_amount) for s in asset.depreciation_schedule)
        self.assertEqual(total_depreciation, 90000)

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_written_down_value_depreciation(self):
        """Test written down value depreciation calculation"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "WDV Depreciation Test Asset"
        asset.asset_category = "Test WDV Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 100000
        asset.calculate_depreciation = 1
        asset.depreciation_method = "Written Down Value"
        asset.rate_of_depreciation = 20
        asset.frequency_of_depreciation = 12
        asset.depreciation_start_date = nowdate()
        asset.total_number_of_depreciations = 5
        asset.insert(ignore_permissions=True)

        # WDV: First year = 100000 * 20% = 20000
        # Second year = 80000 * 20% = 16000
        # etc.
        expected_values = [20000, 16000, 12800, 10240, 8192]

        for i, schedule in enumerate(asset.depreciation_schedule):
            if i < len(expected_values):
                self.assertAlmostEqual(
                    flt(schedule.depreciation_amount),
                    expected_values[i],
                    places=0
                )

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_accumulated_depreciation(self):
        """Test accumulated depreciation calculation in schedule"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Accumulated Dep Test Asset"
        asset.asset_category = "Test SL Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 50000
        asset.calculate_depreciation = 1
        asset.depreciation_method = "Straight Line"
        asset.total_number_of_depreciations = 5
        asset.frequency_of_depreciation = 12
        asset.depreciation_start_date = nowdate()
        asset.expected_value_after_useful_life = 0
        asset.insert(ignore_permissions=True)

        # Check accumulated depreciation
        expected_accumulated = [10000, 20000, 30000, 40000, 50000]

        for i, schedule in enumerate(asset.depreciation_schedule):
            self.assertEqual(
                flt(schedule.accumulated_depreciation_amount),
                expected_accumulated[i]
            )

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_depreciation_schedule_dates(self):
        """Test depreciation schedule dates are correct"""
        start_date = nowdate()
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Schedule Date Test Asset"
        asset.asset_category = "Test SL Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 60000
        asset.calculate_depreciation = 1
        asset.depreciation_method = "Straight Line"
        asset.total_number_of_depreciations = 5
        asset.frequency_of_depreciation = 12  # Annual
        asset.depreciation_start_date = start_date
        asset.expected_value_after_useful_life = 0
        asset.insert(ignore_permissions=True)

        # Check dates are 12 months apart
        for i, schedule in enumerate(asset.depreciation_schedule):
            expected_date = add_months(start_date, 12 * i)
            self.assertEqual(
                getdate(schedule.schedule_date),
                getdate(expected_date)
            )

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_asset_value_after_depreciation(self):
        """Test asset value updates after depreciation"""
        asset = frappe.new_doc("Asset")
        asset.asset_name = "Value Update Test Asset"
        asset.asset_category = "Test SL Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = add_months(nowdate(), -1)
        asset.gross_purchase_amount = 100000
        asset.opening_accumulated_depreciation = 40000
        asset.insert(ignore_permissions=True)

        # Asset value should be gross - accumulated
        expected_value = 60000
        self.assertEqual(flt(asset.asset_value), expected_value)

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    def test_no_depreciation_for_land(self):
        """Test that assets without depreciation don't generate schedule"""
        # Create a no-depreciation category
        if not frappe.db.exists("Asset Category", "Test No Dep Category"):
            doc = frappe.new_doc("Asset Category")
            doc.category_name = "Test No Dep Category"
            doc.depreciation_method = ""
            doc.total_number_of_depreciations = 0
            doc.insert(ignore_permissions=True)

        asset = frappe.new_doc("Asset")
        asset.asset_name = "No Depreciation Asset"
        asset.asset_category = "Test No Dep Category"
        asset.location = "Test Depreciation Location"
        asset.purchase_date = nowdate()
        asset.gross_purchase_amount = 500000
        asset.calculate_depreciation = 0
        asset.insert(ignore_permissions=True)

        # Should have no depreciation schedule
        self.assertEqual(len(asset.depreciation_schedule), 0)

        # Clean up
        frappe.delete_doc("Asset", asset.name, force=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        frappe.db.rollback()

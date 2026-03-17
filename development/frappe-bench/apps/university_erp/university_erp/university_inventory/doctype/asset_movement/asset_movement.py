# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AssetMovement(Document):
    """Asset Movement - Track asset transfers and movements"""

    def validate(self):
        """Validate asset movement"""
        self.validate_assets()
        self.validate_locations()

    def validate_assets(self):
        """Validate assets in the movement"""
        if not self.assets:
            frappe.throw(_("Please add assets to move"))

        for item in self.assets:
            asset = frappe.get_doc("Asset", item.asset)

            if asset.docstatus != 1:
                frappe.throw(_("Asset {0} is not submitted").format(item.asset))

            if asset.status in ["Disposed", "Scrapped"]:
                frappe.throw(_("Cannot move Asset {0} with status {1}").format(
                    item.asset, asset.status
                ))

    def validate_locations(self):
        """Validate source and target locations"""
        for item in self.assets:
            if self.purpose == "Transfer":
                if not item.target_location:
                    frappe.throw(_("Target Location is required for Transfer for asset {0}").format(
                        item.asset
                    ))

            elif self.purpose == "Issue":
                if not item.to_employee:
                    frappe.throw(_("To Employee is required for Issue for asset {0}").format(
                        item.asset
                    ))

    def on_submit(self):
        """Update asset locations on submit"""
        self.update_asset_locations()

    def on_cancel(self):
        """Reverse asset location updates on cancel"""
        self.reverse_asset_locations()

    def update_asset_locations(self):
        """Update asset locations and custodians"""
        for item in self.assets:
            asset = frappe.get_doc("Asset", item.asset)

            updates = {}

            if self.purpose == "Transfer":
                if item.target_location:
                    updates["location"] = item.target_location
                if item.to_employee:
                    updates["custodian"] = item.to_employee

            elif self.purpose == "Issue":
                if item.to_employee:
                    updates["custodian"] = item.to_employee
                if item.target_location:
                    updates["location"] = item.target_location
                updates["status"] = "In Use"

            elif self.purpose == "Receipt":
                if item.target_location:
                    updates["location"] = item.target_location
                if item.to_employee:
                    updates["custodian"] = item.to_employee

            elif self.purpose == "Return":
                if item.target_location:
                    updates["location"] = item.target_location
                updates["custodian"] = None

            for field, value in updates.items():
                asset.db_set(field, value)

    def reverse_asset_locations(self):
        """Reverse asset locations on cancel"""
        for item in self.assets:
            asset = frappe.get_doc("Asset", item.asset)

            updates = {}

            if self.purpose == "Transfer":
                if item.source_location:
                    updates["location"] = item.source_location
                if item.from_employee:
                    updates["custodian"] = item.from_employee

            elif self.purpose == "Issue":
                if item.source_location:
                    updates["location"] = item.source_location
                if item.from_employee:
                    updates["custodian"] = item.from_employee

            elif self.purpose == "Receipt":
                if item.source_location:
                    updates["location"] = item.source_location

            elif self.purpose == "Return":
                if item.source_location:
                    updates["location"] = item.source_location
                if item.from_employee:
                    updates["custodian"] = item.from_employee

            for field, value in updates.items():
                asset.db_set(field, value)

# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Asset Manager - Helper functions for asset management
"""

import frappe
from frappe import _
from frappe.utils import flt, nowdate, getdate, add_months, date_diff


class AssetManager:
    """Manager class for asset operations"""

    @staticmethod
    def get_asset_value(asset_name):
        """Get current value of an asset

        Args:
            asset_name: Asset name

        Returns:
            dict with gross_value, depreciation, current_value
        """
        asset = frappe.get_doc("Asset", asset_name)

        return {
            "gross_value": flt(asset.gross_purchase_amount),
            "accumulated_depreciation": flt(asset.total_depreciation),
            "current_value": flt(asset.asset_value),
            "expected_value_after_useful_life": flt(asset.expected_value_after_useful_life)
        }

    @staticmethod
    def calculate_depreciation(asset_name):
        """Calculate depreciation for an asset

        Args:
            asset_name: Asset name

        Returns:
            dict with depreciation details
        """
        asset = frappe.get_doc("Asset", asset_name)

        if not asset.calculate_depreciation:
            return {"depreciation_amount": 0, "message": "Depreciation not enabled"}

        depreciable_value = (
            flt(asset.gross_purchase_amount) -
            flt(asset.opening_accumulated_depreciation) -
            flt(asset.expected_value_after_useful_life)
        )

        if depreciable_value <= 0:
            return {"depreciation_amount": 0, "message": "No depreciable value"}

        total_depreciations = asset.total_number_of_depreciations or 1

        if asset.depreciation_method == "Straight Line":
            depreciation_amount = depreciable_value / total_depreciations

        elif asset.depreciation_method == "Double Declining Balance":
            rate = flt(asset.rate_of_depreciation) / 100
            current_value = flt(asset.gross_purchase_amount) - flt(asset.total_depreciation)
            depreciation_amount = current_value * rate

        elif asset.depreciation_method == "Written Down Value":
            rate = flt(asset.rate_of_depreciation) / 100
            current_value = flt(asset.gross_purchase_amount) - flt(asset.total_depreciation)
            depreciation_amount = current_value * rate

        else:
            depreciation_amount = 0

        # Ensure we don't depreciate below expected value
        remaining_value = flt(asset.asset_value) - depreciation_amount
        if remaining_value < flt(asset.expected_value_after_useful_life):
            depreciation_amount = flt(asset.asset_value) - flt(asset.expected_value_after_useful_life)

        return {
            "depreciation_amount": max(0, depreciation_amount),
            "current_value": flt(asset.asset_value),
            "remaining_depreciations": sum(
                1 for s in asset.depreciation_schedule
                if not s.journal_entry
            )
        }

    @staticmethod
    def post_depreciation_entries(posting_date=None):
        """Post depreciation entries for all assets due

        Args:
            posting_date: Date to post entries

        Returns:
            list of created journal entries
        """
        from university_erp.university_erp.doctype.asset.asset import get_assets_due_for_depreciation

        if not posting_date:
            posting_date = nowdate()

        assets = get_assets_due_for_depreciation(posting_date)
        created_entries = []

        for asset_data in assets:
            asset = frappe.get_doc("Asset", asset_data.name)

            for schedule in asset.depreciation_schedule:
                if schedule.journal_entry:
                    continue

                if getdate(schedule.schedule_date) > getdate(posting_date):
                    continue

                if not schedule.make_depreciation_entry:
                    continue

                # Create journal entry (simplified - actual implementation would create proper JE)
                # For now, just mark as posted
                schedule.db_set("journal_entry", f"DEP-{asset.name}-{schedule.idx}")

                asset.total_depreciation = flt(asset.total_depreciation) + flt(schedule.depreciation_amount)
                asset.asset_value = flt(asset.gross_purchase_amount) - flt(asset.total_depreciation)
                asset.db_update()

                created_entries.append({
                    "asset": asset.name,
                    "amount": schedule.depreciation_amount,
                    "schedule_date": schedule.schedule_date
                })

        return created_entries

    @staticmethod
    def get_assets_due_for_depreciation(posting_date=None):
        """Get assets with pending depreciation entries

        Args:
            posting_date: Date to check

        Returns:
            list of assets
        """
        from university_erp.university_erp.doctype.asset.asset import get_assets_due_for_depreciation
        return get_assets_due_for_depreciation(posting_date)

    @staticmethod
    def get_assets_due_for_maintenance():
        """Get assets due for maintenance

        Returns:
            list of assets
        """
        from university_erp.university_erp.doctype.asset.asset import get_assets_due_for_maintenance
        return get_assets_due_for_maintenance()

    @staticmethod
    def transfer_asset(asset_name, to_location=None, to_custodian=None, remarks=None):
        """Transfer an asset to new location/custodian

        Args:
            asset_name: Asset name
            to_location: Target warehouse/location
            to_custodian: Target custodian (employee)
            remarks: Transfer remarks

        Returns:
            Asset Movement document
        """
        asset = frappe.get_doc("Asset", asset_name)

        if asset.status in ["Disposed", "Scrapped"]:
            frappe.throw(_("Cannot transfer a {0} asset").format(asset.status.lower()))

        movement = frappe.new_doc("Asset Movement")
        movement.purpose = "Transfer"
        movement.transaction_date = nowdate()
        movement.remarks = remarks

        movement.append("assets", {
            "asset": asset.name,
            "asset_name": asset.asset_name,
            "source_location": asset.location,
            "target_location": to_location,
            "from_employee": asset.custodian,
            "to_employee": to_custodian
        })

        movement.insert()
        movement.submit()

        return movement

    @staticmethod
    def dispose_asset(asset_name, disposal_date=None, proceeds=0, disposal_account=None, remarks=None):
        """Dispose of an asset

        Args:
            asset_name: Asset name
            disposal_date: Date of disposal
            proceeds: Sale proceeds
            disposal_account: Account for proceeds
            remarks: Disposal remarks

        Returns:
            Asset document
        """
        from university_erp.university_erp.doctype.asset.asset import dispose_asset
        return dispose_asset(asset_name, disposal_date or nowdate(), proceeds, disposal_account)

    @staticmethod
    def scrap_asset(asset_name, scrap_date=None, scrap_value=0, remarks=None):
        """Scrap an asset

        Args:
            asset_name: Asset name
            scrap_date: Date of scrapping
            scrap_value: Scrap value
            remarks: Scrap remarks

        Returns:
            Asset document
        """
        from university_erp.university_erp.doctype.asset.asset import scrap_asset
        return scrap_asset(asset_name, scrap_date or nowdate(), scrap_value)

    @staticmethod
    def get_asset_summary_by_category():
        """Get asset summary grouped by category

        Returns:
            list of category summaries
        """
        return frappe.db.sql("""
            SELECT
                asset_category,
                COUNT(*) as total_assets,
                SUM(gross_purchase_amount) as total_purchase_value,
                SUM(asset_value) as total_current_value,
                SUM(total_depreciation) as total_depreciation,
                SUM(CASE WHEN status = 'In Use' THEN 1 ELSE 0 END) as in_use_count,
                SUM(CASE WHEN status = 'In Maintenance' THEN 1 ELSE 0 END) as in_maintenance_count,
                SUM(CASE WHEN status = 'Disposed' THEN 1 ELSE 0 END) as disposed_count
            FROM `tabAsset`
            WHERE docstatus = 1
            GROUP BY asset_category
            ORDER BY asset_category
        """, as_dict=True)

    @staticmethod
    def get_asset_summary_by_department():
        """Get asset summary grouped by department

        Returns:
            list of department summaries
        """
        return frappe.db.sql("""
            SELECT
                COALESCE(department, 'Unassigned') as department,
                COUNT(*) as total_assets,
                SUM(gross_purchase_amount) as total_purchase_value,
                SUM(asset_value) as total_current_value,
                SUM(total_depreciation) as total_depreciation
            FROM `tabAsset`
            WHERE docstatus = 1
            AND status NOT IN ('Disposed', 'Scrapped')
            GROUP BY department
            ORDER BY total_assets DESC
        """, as_dict=True)

    @staticmethod
    def get_warranty_expiring_assets(days=30):
        """Get assets with warranty expiring soon

        Args:
            days: Number of days to check ahead

        Returns:
            list of assets
        """
        today = nowdate()
        future_date = add_months(today, 1)

        return frappe.db.sql("""
            SELECT
                name, asset_name, asset_category, department,
                warranty_expiry_date,
                DATEDIFF(warranty_expiry_date, %s) as days_remaining
            FROM `tabAsset`
            WHERE docstatus = 1
            AND status IN ('Submitted', 'In Use')
            AND warranty_expiry_date IS NOT NULL
            AND warranty_expiry_date BETWEEN %s AND %s
            ORDER BY warranty_expiry_date
        """, (today, today, future_date), as_dict=True)


# Whitelist API functions

@frappe.whitelist()
def get_asset_details(asset_name):
    """Get asset details"""
    asset = frappe.get_doc("Asset", asset_name)
    value_info = AssetManager.get_asset_value(asset_name)

    return {
        "asset_name": asset.asset_name,
        "asset_category": asset.asset_category,
        "status": asset.status,
        "department": asset.department,
        "location": asset.location,
        "custodian": asset.custodian,
        **value_info
    }


@frappe.whitelist()
def get_depreciation_schedule(asset_name):
    """Get depreciation schedule for an asset"""
    asset = frappe.get_doc("Asset", asset_name)

    return [
        {
            "schedule_date": s.schedule_date,
            "depreciation_amount": s.depreciation_amount,
            "accumulated_depreciation": s.accumulated_depreciation_amount,
            "journal_entry": s.journal_entry,
            "is_posted": bool(s.journal_entry)
        }
        for s in asset.depreciation_schedule
    ]


@frappe.whitelist()
def get_assets_by_location(location):
    """Get assets at a location"""
    return frappe.get_all(
        "Asset",
        filters={
            "location": location,
            "docstatus": 1,
            "status": ["not in", ["Disposed", "Scrapped"]]
        },
        fields=["name", "asset_name", "asset_category", "status", "custodian", "asset_value"]
    )


@frappe.whitelist()
def get_assets_by_custodian(custodian):
    """Get assets assigned to a custodian"""
    return frappe.get_all(
        "Asset",
        filters={
            "custodian": custodian,
            "docstatus": 1,
            "status": ["not in", ["Disposed", "Scrapped"]]
        },
        fields=["name", "asset_name", "asset_category", "status", "location", "asset_value"]
    )


@frappe.whitelist()
def create_maintenance_schedule(asset_name, planned_date, maintenance_type, description=None):
    """Create a maintenance schedule for an asset"""
    maintenance = frappe.new_doc("Asset Maintenance")
    maintenance.asset = asset_name
    maintenance.maintenance_type = maintenance_type
    maintenance.planned_date = planned_date
    maintenance.description = description
    maintenance.insert()

    return maintenance


@frappe.whitelist()
def get_maintenance_history(asset_name):
    """Get maintenance history for an asset"""
    return frappe.get_all(
        "Asset Maintenance",
        filters={"asset": asset_name},
        fields=[
            "name", "maintenance_type", "maintenance_status",
            "planned_date", "completion_date", "total_cost",
            "assigned_to", "work_done"
        ],
        order_by="planned_date desc"
    )

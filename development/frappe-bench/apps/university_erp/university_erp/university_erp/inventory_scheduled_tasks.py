# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Inventory & Asset Scheduled Tasks
"""

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, add_days


def check_low_stock_items():
    """Check for items below reorder level and send alerts"""
    from university_erp.university_erp.inventory_manager import InventoryManager

    low_stock_items = InventoryManager.get_low_stock_items()

    if not low_stock_items:
        return

    # Group items for notification
    items_list = []
    for item in low_stock_items:
        items_list.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "current_stock": item.current_stock,
            "reorder_level": item.reorder_level
        })

    # Send notification to relevant users
    users = get_inventory_managers()

    for user in users:
        frappe.sendmail(
            recipients=[user],
            subject=_("Low Stock Alert - {0} Items Below Reorder Level").format(len(items_list)),
            message=get_low_stock_email_content(items_list),
            now=True
        )

    # Log the check
    frappe.log_error(
        message=f"Low stock check completed. Found {len(items_list)} items below reorder level.",
        title="Low Stock Items Alert"
    )


def check_maintenance_due():
    """Check for assets due for maintenance and send reminders"""
    from university_erp.university_erp.doctype.asset.asset import get_assets_due_for_maintenance

    assets = get_assets_due_for_maintenance()

    if not assets:
        return

    # Group by custodian/department for targeted notifications
    by_custodian = {}
    for asset in assets:
        custodian = asset.get("custodian") or "Unassigned"
        if custodian not in by_custodian:
            by_custodian[custodian] = []
        by_custodian[custodian].append(asset)

    # Send notifications
    for custodian, asset_list in by_custodian.items():
        if custodian != "Unassigned":
            employee = frappe.get_doc("Employee", custodian)
            if employee.user_id:
                frappe.sendmail(
                    recipients=[employee.user_id],
                    subject=_("Asset Maintenance Due - {0} Assets").format(len(asset_list)),
                    message=get_maintenance_email_content(asset_list),
                    now=True
                )

    # Also notify inventory managers
    users = get_inventory_managers()
    for user in users:
        frappe.sendmail(
            recipients=[user],
            subject=_("Assets Due for Maintenance - {0} Assets").format(len(assets)),
            message=get_maintenance_email_content(assets),
            now=True
        )


def check_calibration_due():
    """Check for lab equipment due for calibration"""
    from university_erp.university_erp.doctype.lab_equipment.lab_equipment import get_equipment_due_for_calibration

    equipment = get_equipment_due_for_calibration()

    if not equipment:
        return

    # Send notification to lab managers
    users = get_lab_managers()

    for user in users:
        frappe.sendmail(
            recipients=[user],
            subject=_("Equipment Calibration Due - {0} Items").format(len(equipment)),
            message=get_calibration_email_content(equipment),
            now=True
        )


def post_depreciation_entries():
    """Post depreciation entries for assets"""
    from university_erp.university_erp.asset_manager import AssetManager

    try:
        entries = AssetManager.post_depreciation_entries()

        if entries:
            frappe.log_error(
                message=f"Posted depreciation entries for {len(entries)} assets.",
                title="Depreciation Entries Posted"
            )
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Depreciation Posting Error"
        )


def auto_create_material_requests():
    """Auto-create material requests for items below reorder level"""
    from university_erp.university_erp.inventory_manager import InventoryManager

    try:
        created = InventoryManager.auto_create_material_request()

        if created:
            frappe.log_error(
                message=f"Auto-created {len(created)} material requests.",
                title="Material Requests Auto-Created"
            )
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Auto Material Request Error"
        )


# Helper functions

def get_inventory_managers():
    """Get users with Accounts Manager or System Manager role"""
    return frappe.get_all(
        "Has Role",
        filters={"role": ["in", ["Accounts Manager", "System Manager"]], "parenttype": "User"},
        pluck="parent"
    )


def get_lab_managers():
    """Get users with Academics User role"""
    return frappe.get_all(
        "Has Role",
        filters={"role": ["in", ["Academics User", "System Manager"]], "parenttype": "User"},
        pluck="parent"
    )


def get_low_stock_email_content(items):
    """Generate email content for low stock alert"""
    html = """
    <h3>Low Stock Alert</h3>
    <p>The following items are below their reorder level:</p>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th>Item Code</th>
                <th>Item Name</th>
                <th>Current Stock</th>
                <th>Reorder Level</th>
            </tr>
        </thead>
        <tbody>
    """

    for item in items:
        html += f"""
            <tr>
                <td>{item['item_code']}</td>
                <td>{item['item_name']}</td>
                <td>{item['current_stock']}</td>
                <td>{item['reorder_level']}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    <p>Please create material requests for these items.</p>
    """

    return html


def get_maintenance_email_content(assets):
    """Generate email content for maintenance due alert"""
    html = """
    <h3>Asset Maintenance Due</h3>
    <p>The following assets are due for maintenance:</p>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th>Asset</th>
                <th>Name</th>
                <th>Category</th>
                <th>Next Maintenance</th>
            </tr>
        </thead>
        <tbody>
    """

    for asset in assets:
        html += f"""
            <tr>
                <td>{asset['name']}</td>
                <td>{asset['asset_name']}</td>
                <td>{asset.get('asset_category', '')}</td>
                <td>{asset.get('next_maintenance_date', '')}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    <p>Please schedule maintenance for these assets.</p>
    """

    return html


def get_calibration_email_content(equipment):
    """Generate email content for calibration due alert"""
    html = """
    <h3>Equipment Calibration Due</h3>
    <p>The following lab equipment is due for calibration:</p>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th>Equipment Code</th>
                <th>Equipment Name</th>
                <th>Laboratory</th>
                <th>Next Calibration</th>
            </tr>
        </thead>
        <tbody>
    """

    for eq in equipment:
        html += f"""
            <tr>
                <td>{eq['equipment_code']}</td>
                <td>{eq['equipment_name']}</td>
                <td>{eq['lab']}</td>
                <td>{eq['next_calibration_date']}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    <p>Please arrange calibration for these equipment.</p>
    """

    return html

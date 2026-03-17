# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class AssetMaintenance(Document):
    """Asset Maintenance - Track maintenance activities for assets"""

    def validate(self):
        """Validate asset maintenance"""
        self.validate_asset()
        self.validate_dates()
        self.calculate_parts_cost()
        self.calculate_total_cost()

    def validate_asset(self):
        """Validate asset is in proper state for maintenance"""
        asset = frappe.get_doc("Asset", self.asset)

        if asset.docstatus != 1:
            frappe.throw(_("Asset {0} is not submitted").format(self.asset))

        if asset.status in ["Disposed", "Scrapped"]:
            frappe.throw(_("Cannot create maintenance for {0} asset {1}").format(
                asset.status.lower(), self.asset
            ))

    def validate_dates(self):
        """Validate date fields"""
        if self.completion_date and self.planned_date:
            if getdate(self.completion_date) < getdate(self.planned_date):
                frappe.throw(_("Completion Date cannot be before Planned Date"))

    def calculate_parts_cost(self):
        """Calculate total parts cost from parts replaced"""
        self.parts_cost = 0
        for part in self.parts_replaced:
            part.amount = flt(part.qty) * flt(part.rate)
            self.parts_cost += part.amount

    def calculate_total_cost(self):
        """Calculate total maintenance cost"""
        self.total_cost = (
            flt(self.labor_cost) +
            flt(self.parts_cost) +
            flt(self.other_cost)
        )

    def on_submit(self):
        """On submit actions"""
        if self.maintenance_status == "Completed":
            self.complete_maintenance()

    def on_cancel(self):
        """On cancel actions"""
        self.maintenance_status = "Cancelled"

    def complete_maintenance(self):
        """Mark maintenance as complete and update asset"""
        if not self.completion_date:
            self.completion_date = nowdate()

        self.maintenance_status = "Completed"

        # Update asset maintenance date
        asset = frappe.get_doc("Asset", self.asset)
        asset.update_maintenance_date(getdate(self.completion_date))

        # Update asset status if it was in maintenance
        if asset.status == "In Maintenance":
            asset.db_set("status", "In Use")


@frappe.whitelist()
def start_maintenance(name):
    """Start maintenance - change status to In Progress"""
    doc = frappe.get_doc("Asset Maintenance", name)

    if doc.maintenance_status != "Planned":
        frappe.throw(_("Can only start maintenance that is Planned"))

    doc.maintenance_status = "In Progress"
    doc.db_set("maintenance_status", "In Progress")

    # Update asset status to In Maintenance
    asset = frappe.get_doc("Asset", doc.asset)
    asset.db_set("status", "In Maintenance")

    return doc


@frappe.whitelist()
def complete_maintenance(name, completion_date=None, work_done=None):
    """Complete maintenance"""
    doc = frappe.get_doc("Asset Maintenance", name)

    if doc.maintenance_status not in ["Planned", "In Progress"]:
        frappe.throw(_("Can only complete maintenance that is Planned or In Progress"))

    if work_done:
        doc.work_done = work_done

    doc.completion_date = completion_date or nowdate()
    doc.maintenance_status = "Completed"
    doc.save()

    # Update asset
    asset = frappe.get_doc("Asset", doc.asset)
    asset.update_maintenance_date(getdate(doc.completion_date))

    if asset.status == "In Maintenance":
        asset.db_set("status", "In Use")

    return doc


@frappe.whitelist()
def get_pending_maintenance():
    """Get all pending maintenance activities"""
    return frappe.db.sql("""
        SELECT
            am.name, am.asset, am.asset_name, am.maintenance_type,
            am.priority, am.planned_date, am.assigned_to,
            a.department, a.location
        FROM `tabAsset Maintenance` am
        INNER JOIN `tabAsset` a ON a.name = am.asset
        WHERE am.docstatus = 0
        AND am.maintenance_status IN ('Planned', 'In Progress')
        ORDER BY
            FIELD(am.priority, 'Urgent', 'High', 'Medium', 'Low'),
            am.planned_date
    """, as_dict=True)

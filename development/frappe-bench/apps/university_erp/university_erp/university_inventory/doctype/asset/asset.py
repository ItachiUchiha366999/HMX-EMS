# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_months, date_diff, nowdate, cint


class Asset(Document):
    """Asset - Main asset tracking document with depreciation support"""

    def autoname(self):
        """Generate asset code after naming"""
        from frappe.model.naming import make_autoname
        self.name = make_autoname(self.naming_series, doc=self)
        self.asset_code = self.name

    def validate(self):
        """Validate asset"""
        self.validate_dates()
        self.validate_depreciation_settings()
        self.set_depreciation_rate()
        self.calculate_asset_value()
        self.set_status()

    def validate_dates(self):
        """Validate date fields"""
        if self.purchase_date and self.warranty_expiry_date:
            if getdate(self.warranty_expiry_date) < getdate(self.purchase_date):
                frappe.throw(_("Warranty Expiry Date cannot be before Purchase Date"))

        if self.calculate_depreciation and self.depreciation_start_date:
            if self.purchase_date and getdate(self.depreciation_start_date) < getdate(self.purchase_date):
                frappe.throw(_("Depreciation Start Date cannot be before Purchase Date"))

    def validate_depreciation_settings(self):
        """Validate depreciation configuration"""
        if self.calculate_depreciation:
            if not self.depreciation_method:
                frappe.throw(_("Depreciation Method is required when Calculate Depreciation is enabled"))

            if not self.depreciation_start_date:
                frappe.throw(_("Depreciation Start Date is required when Calculate Depreciation is enabled"))

            if self.depreciation_method in ["Straight Line", "Double Declining Balance"]:
                if not self.total_number_of_depreciations:
                    frappe.throw(_("Total Number of Depreciations is required for {0} method").format(
                        self.depreciation_method
                    ))

            if self.depreciation_method == "Written Down Value":
                if flt(self.rate_of_depreciation) <= 0:
                    frappe.throw(_("Rate of Depreciation is required for Written Down Value method"))

    def set_depreciation_rate(self):
        """Calculate depreciation rate based on method"""
        if not self.calculate_depreciation:
            return

        if self.depreciation_method == "Straight Line":
            if self.total_number_of_depreciations:
                self.rate_of_depreciation = 100 / self.total_number_of_depreciations

        elif self.depreciation_method == "Double Declining Balance":
            if self.total_number_of_depreciations and self.frequency_of_depreciation:
                useful_life_years = (self.total_number_of_depreciations * self.frequency_of_depreciation) / 12
                if useful_life_years > 0:
                    self.rate_of_depreciation = (2 / useful_life_years) * 100

    def calculate_asset_value(self):
        """Calculate current asset value"""
        self.total_depreciation = flt(self.opening_accumulated_depreciation)

        if self.depreciation_schedule:
            for schedule in self.depreciation_schedule:
                if schedule.journal_entry:
                    self.total_depreciation += flt(schedule.depreciation_amount)

        self.asset_value = flt(self.gross_purchase_amount) - flt(self.total_depreciation)

    def set_status(self):
        """Set asset status"""
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            if not self.status or self.status == "Draft":
                self.status = "Submitted"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        """On submit actions"""
        self.status = "In Use"
        if self.calculate_depreciation:
            self.make_depreciation_schedule()
        self.db_set("status", self.status)

    def on_cancel(self):
        """On cancel actions"""
        self.cancel_depreciation_entries()
        self.status = "Cancelled"

    def make_depreciation_schedule(self):
        """Generate depreciation schedule"""
        if not self.calculate_depreciation:
            return

        self.depreciation_schedule = []

        depreciable_value = flt(self.gross_purchase_amount) - flt(self.opening_accumulated_depreciation) - flt(self.expected_value_after_useful_life)

        if depreciable_value <= 0:
            return

        number_of_depreciations = cint(self.total_number_of_depreciations)
        frequency = cint(self.frequency_of_depreciation) or 12

        schedule_date = getdate(self.depreciation_start_date)
        accumulated_depreciation = flt(self.opening_accumulated_depreciation)
        value_after_depreciation = flt(self.gross_purchase_amount) - accumulated_depreciation

        for i in range(number_of_depreciations):
            depreciation_amount = self.get_depreciation_amount(
                depreciable_value,
                value_after_depreciation,
                number_of_depreciations,
                i
            )

            # Ensure we don't depreciate below expected value
            if (value_after_depreciation - depreciation_amount) < flt(self.expected_value_after_useful_life):
                depreciation_amount = value_after_depreciation - flt(self.expected_value_after_useful_life)

            if depreciation_amount <= 0:
                break

            accumulated_depreciation += depreciation_amount
            value_after_depreciation -= depreciation_amount

            self.append("depreciation_schedule", {
                "schedule_date": schedule_date,
                "depreciation_amount": depreciation_amount,
                "accumulated_depreciation_amount": accumulated_depreciation,
                "make_depreciation_entry": 1
            })

            schedule_date = add_months(schedule_date, frequency)

        self.save()

    def get_depreciation_amount(self, depreciable_value, value_after_depreciation, total_depreciations, period):
        """Calculate depreciation amount for a period"""
        if self.depreciation_method == "Straight Line":
            return flt(depreciable_value) / total_depreciations

        elif self.depreciation_method == "Double Declining Balance":
            rate = flt(self.rate_of_depreciation) / 100
            return flt(value_after_depreciation) * rate

        elif self.depreciation_method == "Written Down Value":
            rate = flt(self.rate_of_depreciation) / 100
            return flt(value_after_depreciation) * rate

        return 0

    def cancel_depreciation_entries(self):
        """Cancel all depreciation journal entries"""
        for schedule in self.depreciation_schedule:
            if schedule.journal_entry:
                je = frappe.get_doc("Journal Entry", schedule.journal_entry)
                if je.docstatus == 1:
                    je.cancel()

    def update_maintenance_date(self, maintenance_date):
        """Update last maintenance date and calculate next"""
        self.last_maintenance_date = maintenance_date

        if self.maintenance_frequency:
            months_map = {
                "Monthly": 1,
                "Quarterly": 3,
                "Half-yearly": 6,
                "Yearly": 12
            }
            months = months_map.get(self.maintenance_frequency, 12)
            self.next_maintenance_date = add_months(maintenance_date, months)

        self.db_update()


@frappe.whitelist()
def make_asset_movement(source_name, target_doc=None):
    """Create Asset Movement from Asset"""
    asset = frappe.get_doc("Asset", source_name)

    movement = frappe.new_doc("Asset Movement")
    movement.purpose = "Transfer"
    movement.transaction_date = nowdate()
    movement.append("assets", {
        "asset": asset.name,
        "asset_name": asset.asset_name,
        "source_location": asset.location,
        "from_employee": asset.custodian
    })

    return movement


@frappe.whitelist()
def dispose_asset(asset_name, disposal_date, proceeds=0, disposal_account=None):
    """Dispose of an asset"""
    asset = frappe.get_doc("Asset", asset_name)

    if asset.status == "Disposed":
        frappe.throw(_("Asset {0} is already disposed").format(asset_name))

    if asset.status == "Scrapped":
        frappe.throw(_("Cannot dispose a scrapped asset"))

    # Update asset status
    asset.status = "Disposed"
    asset.db_set("status", "Disposed")

    frappe.msgprint(_("Asset {0} has been disposed").format(asset_name))

    return asset


@frappe.whitelist()
def scrap_asset(asset_name, scrap_date, scrap_value=0):
    """Scrap an asset"""
    asset = frappe.get_doc("Asset", asset_name)

    if asset.status == "Scrapped":
        frappe.throw(_("Asset {0} is already scrapped").format(asset_name))

    if asset.status == "Disposed":
        frappe.throw(_("Cannot scrap a disposed asset"))

    # Update asset status
    asset.status = "Scrapped"
    asset.db_set("status", "Scrapped")

    frappe.msgprint(_("Asset {0} has been scrapped").format(asset_name))

    return asset


@frappe.whitelist()
def get_assets_due_for_depreciation(posting_date=None):
    """Get assets with pending depreciation entries"""
    if not posting_date:
        posting_date = nowdate()

    assets = frappe.db.sql("""
        SELECT DISTINCT a.name, a.asset_name, a.asset_category
        FROM `tabAsset` a
        INNER JOIN `tabDepreciation Schedule` ds ON ds.parent = a.name
        WHERE a.docstatus = 1
        AND a.status IN ('Submitted', 'In Use')
        AND a.calculate_depreciation = 1
        AND ds.schedule_date <= %s
        AND ds.journal_entry IS NULL
        AND ds.make_depreciation_entry = 1
    """, posting_date, as_dict=True)

    return assets


@frappe.whitelist()
def get_assets_due_for_maintenance():
    """Get assets due for maintenance"""
    today = nowdate()

    assets = frappe.db.sql("""
        SELECT name, asset_name, asset_category, department,
               next_maintenance_date, maintenance_frequency, custodian
        FROM `tabAsset`
        WHERE docstatus = 1
        AND status IN ('Submitted', 'In Use')
        AND maintenance_required = 1
        AND next_maintenance_date <= %s
        ORDER BY next_maintenance_date
    """, today, as_dict=True)

    return assets

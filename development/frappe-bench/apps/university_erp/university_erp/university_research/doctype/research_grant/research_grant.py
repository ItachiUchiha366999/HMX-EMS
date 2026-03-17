# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class ResearchGrant(Document):
    def validate(self):
        self.validate_amounts()
        self.update_utilization()

    def validate_amounts(self):
        """Validate grant amounts"""
        if self.sanctioned_amount and self.disbursed_amount:
            if self.disbursed_amount > self.sanctioned_amount:
                frappe.throw(_("Disbursed Amount cannot exceed Sanctioned Amount"))

        if self.sanctioned_amount and self.utilized_amount:
            if self.utilized_amount > self.sanctioned_amount:
                frappe.throw(_("Utilized Amount cannot exceed Sanctioned Amount"))

    def update_utilization(self):
        """Update utilization totals from child table"""
        if self.utilization_details:
            total_utilized = sum(u.utilized_amount or 0 for u in self.utilization_details)
            self.utilized_amount = total_utilized

            # Update balance for each utilization row
            for u in self.utilization_details:
                u.balance = (u.allocated_amount or 0) - (u.utilized_amount or 0)


@frappe.whitelist()
def get_grant_summary(funding_agency=None, grant_type=None, status=None):
    """Get grant summary"""
    filters = {}

    if funding_agency:
        filters["funding_agency"] = funding_agency

    if grant_type:
        filters["grant_type"] = grant_type

    if status:
        filters["status"] = status

    grants = frappe.get_all("Research Grant",
        filters=filters,
        fields=["name", "grant_title", "funding_agency", "grant_type", "status",
                "sanctioned_amount", "disbursed_amount", "utilized_amount",
                "validity_from", "validity_to", "utilization_certificate_submitted"]
    )

    # Calculate totals
    total_sanctioned = sum(g.sanctioned_amount or 0 for g in grants)
    total_disbursed = sum(g.disbursed_amount or 0 for g in grants)
    total_utilized = sum(g.utilized_amount or 0 for g in grants)

    return {
        "grants": grants,
        "summary": {
            "total_grants": len(grants),
            "total_sanctioned": total_sanctioned,
            "total_disbursed": total_disbursed,
            "total_utilized": total_utilized,
            "utilization_percent": (total_utilized / total_disbursed * 100) if total_disbursed else 0
        }
    }

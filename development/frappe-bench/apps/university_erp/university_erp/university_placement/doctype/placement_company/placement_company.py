# Copyright (c) 2026, University ERP and contributors
import frappe
from frappe.model.document import Document

class PlacementCompany(Document):
    """Placement Company master with statistics tracking"""

    def update_stats(self):
        """Update placement statistics"""
        stats = frappe.db.sql("""
            SELECT COUNT(*) as total_hires, AVG(offered_ctc) as avg_package, MAX(offered_ctc) as highest_package
            FROM `tabPlacement Application`
            WHERE company = %s AND status = 'Placed'
        """, (self.name,), as_dict=True)[0]

        self.total_hires = stats.total_hires or 0
        self.avg_package = stats.avg_package or 0
        self.highest_package = stats.highest_package or 0
        self.save(ignore_permissions=True)

@frappe.whitelist()
def get_company_placements(company):
    """Get placement history for a company"""
    return frappe.db.sql("""
        SELECT pa.student, s.student_name, pa.job_opening, pj.job_title, pa.offered_ctc, pa.placement_date
        FROM `tabPlacement Application` pa
        JOIN `tabStudent` s ON pa.student = s.name
        JOIN `tabPlacement Job Opening` pj ON pa.job_opening = pj.name
        WHERE pa.company = %s AND pa.status = 'Placed'
        ORDER BY pa.placement_date DESC
    """, (company,), as_dict=True)

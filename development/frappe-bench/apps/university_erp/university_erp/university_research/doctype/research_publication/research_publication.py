# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ResearchPublication(Document):
    def validate(self):
        self.validate_authors()

    def validate_authors(self):
        """Validate authors list"""
        if not self.authors:
            frappe.throw(_("At least one author is required"))

        # Check for duplicate employees
        employees = [a.employee for a in self.authors if a.employee]
        if len(employees) != len(set(employees)):
            frappe.throw(_("Duplicate employees in author list"))


@frappe.whitelist()
def get_faculty_publications(employee=None, publication_type=None, from_date=None, to_date=None):
    """Get publications for a faculty member"""
    filters = {}

    if publication_type:
        filters["publication_type"] = publication_type

    if from_date:
        filters["publication_date"] = [">=", from_date]

    if to_date:
        filters["publication_date"] = ["<=", to_date]

    publications = frappe.get_all("Research Publication",
        filters=filters,
        fields=["name", "title", "publication_type", "publication_date", "status",
                "journal_name", "is_scopus_indexed", "is_wos_indexed", "citations"]
    )

    if employee:
        # Filter by author
        result = []
        for pub in publications:
            authors = frappe.get_all("Publication Author",
                filters={"parent": pub.name, "employee": employee}
            )
            if authors:
                result.append(pub)
        return result

    return publications

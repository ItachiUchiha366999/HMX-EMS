import frappe
from frappe import _
from frappe.model.document import Document


class UniversityDepartment(Document):
    """University Department DocType"""

    def validate(self):
        """Validate department details"""
        self.validate_parent_department()
        self.validate_hod()

    def validate_parent_department(self):
        """Prevent circular reference in parent department"""
        if self.parent_department == self.name:
            frappe.throw(_("Department cannot be its own parent"))

        # Check for circular reference
        if self.parent_department:
            parent = frappe.get_doc("University Department", self.parent_department)
            if parent.parent_department == self.name:
                frappe.throw(_("Circular reference detected in department hierarchy"))

    def validate_hod(self):
        """Validate Head of Department"""
        if self.hod:
            # Check if HOD is a valid employee
            if not frappe.db.exists("Employee", self.hod):
                frappe.throw(_("Invalid Employee ID for HOD"))

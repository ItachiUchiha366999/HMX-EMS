# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CertificateTemplate(Document):
    def validate(self):
        self.set_numbering_prefix()

    def set_numbering_prefix(self):
        """Auto-set numbering prefix from certificate type if not set"""
        if not self.numbering_prefix and self.certificate_type:
            # Extract first 3 letters
            prefix = ''.join(word[0] for word in self.certificate_type.split()[:3]).upper()
            self.numbering_prefix = prefix

    def get_next_certificate_number(self):
        """Generate next certificate number based on format"""
        from frappe.utils import nowdate

        today = nowdate()
        year = today[:4]
        month = today[5:7]
        day = today[8:10]

        # Get count for this template and year
        count = frappe.db.count(
            "Certificate Request",
            filters={
                "certificate_template": self.name,
                "certificate_number": ["like", f"%{year}%"]
            }
        ) + 1

        # Apply numbering format
        number = self.numbering_series or "{prefix}/{YYYY}/{#####}"
        number = number.replace("{prefix}", self.numbering_prefix or "CERT")
        number = number.replace("{YYYY}", year)
        number = number.replace("{MM}", month)
        number = number.replace("{DD}", day)

        # Handle sequence number
        if "{#####}" in number:
            number = number.replace("{#####}", str(count).zfill(5))
        elif "{####}" in number:
            number = number.replace("{####}", str(count).zfill(4))
        elif "{###}" in number:
            number = number.replace("{###}", str(count).zfill(3))

        return number

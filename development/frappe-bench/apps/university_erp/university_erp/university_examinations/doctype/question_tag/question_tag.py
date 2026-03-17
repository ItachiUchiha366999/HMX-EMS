"""
Question Tag DocType Controller

Tags for categorizing questions in the question bank
"""

import frappe
from frappe.model.document import Document


class QuestionTag(Document):
    """Controller for Question Tag DocType"""

    def validate(self):
        """Validate the question tag"""
        self.validate_tag_name()

    def validate_tag_name(self):
        """Ensure tag name is properly formatted"""
        if self.tag_name:
            self.tag_name = self.tag_name.strip()

    def before_save(self):
        """Actions before saving"""
        # Convert tag name to title case for consistency
        if self.tag_name:
            self.tag_name = self.tag_name.title()

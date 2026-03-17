# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


class LMSContent(Document):
    def validate(self):
        self.validate_content_type()
        self.validate_availability()
        self.validate_prerequisite()

    def validate_content_type(self):
        """Validate that content fields match content type"""
        if self.content_type == "Video" and not self.video_url:
            frappe.throw(_("Video URL is required for Video content type"))

        if self.content_type in ["Document", "Slides"] and not self.document_file:
            frappe.throw(_("Document/File is required for {0} content type").format(self.content_type))

        if self.content_type == "Link" and not self.external_link:
            frappe.throw(_("External Link is required for Link content type"))

        if self.content_type == "Text" and not self.text_content:
            frappe.throw(_("Text Content is required for Text content type"))

        if self.content_type == "Scorm" and not self.scorm_package:
            frappe.throw(_("SCORM Package is required for SCORM content type"))

    def validate_availability(self):
        """Validate availability dates"""
        if self.available_from and self.available_until:
            if get_datetime(self.available_from) > get_datetime(self.available_until):
                frappe.throw(_("Available Until cannot be before Available From"))

    def validate_prerequisite(self):
        """Validate prerequisite content"""
        if self.prerequisite_content:
            if self.prerequisite_content == self.name:
                frappe.throw(_("Content cannot be its own prerequisite"))

            prereq = frappe.get_doc("LMS Content", self.prerequisite_content)
            if prereq.lms_course != self.lms_course:
                frappe.throw(_("Prerequisite content must be from the same course"))

    def is_available(self):
        """Check if content is currently available"""
        if self.status != "Published":
            return False

        current_time = now_datetime()

        if self.available_from and get_datetime(self.available_from) > current_time:
            return False

        if self.available_until and get_datetime(self.available_until) < current_time:
            return False

        return True

    def check_prerequisite(self, student):
        """Check if student has completed prerequisite"""
        if not self.prerequisite_content:
            return True

        progress = frappe.db.exists("LMS Content Progress", {
            "content": self.prerequisite_content,
            "student": student,
            "status": "Completed"
        })

        return bool(progress)


@frappe.whitelist()
def get_course_content(lms_course, student=None):
    """Get all published content for a course"""
    contents = frappe.get_all("LMS Content",
        filters={
            "lms_course": lms_course,
            "status": "Published"
        },
        fields=["name", "title", "module", "sequence", "content_type",
                "duration_minutes", "is_mandatory", "prerequisite_content",
                "available_from", "available_until"],
        order_by="sequence"
    )

    if student:
        for content in contents:
            progress = frappe.db.get_value("LMS Content Progress", {
                "content": content.name,
                "student": student
            }, ["status", "progress_percent", "completed_on"], as_dict=True)

            content["progress"] = progress or {"status": "Not Started", "progress_percent": 0}

    return contents

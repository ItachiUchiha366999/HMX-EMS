# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LMSContentProgress(Document):
    def before_insert(self):
        self.first_accessed = now_datetime()
        self.last_accessed = now_datetime()
        self.access_count = 1

    def validate(self):
        if self.progress_percent >= 100 and self.status != "Completed":
            self.status = "Completed"
            self.completed_on = now_datetime()
        elif self.progress_percent > 0 and self.status == "Not Started":
            self.status = "In Progress"

    def update_progress(self, progress_percent, time_spent=0):
        """Update content progress"""
        self.progress_percent = min(progress_percent, 100)
        self.time_spent_minutes += time_spent
        self.last_accessed = now_datetime()
        self.access_count += 1

        if self.progress_percent >= 100 and self.status != "Completed":
            self.status = "Completed"
            self.completed_on = now_datetime()
        elif self.progress_percent > 0 and self.status == "Not Started":
            self.status = "In Progress"

        self.save(ignore_permissions=True)


@frappe.whitelist()
def track_content_progress(content, student, progress_percent, time_spent=0):
    """Track student progress on content"""
    progress_percent = float(progress_percent)
    time_spent = int(time_spent) if time_spent else 0

    # Check if content is available
    content_doc = frappe.get_doc("LMS Content", content)
    if not content_doc.is_available():
        frappe.throw(_("This content is not currently available"))

    # Check prerequisite
    if not content_doc.check_prerequisite(student):
        frappe.throw(_("Please complete the prerequisite content first"))

    # Get or create progress record
    progress_name = frappe.db.exists("LMS Content Progress", {
        "content": content,
        "student": student
    })

    if progress_name:
        progress = frappe.get_doc("LMS Content Progress", progress_name)
        progress.update_progress(progress_percent, time_spent)
    else:
        progress = frappe.get_doc({
            "doctype": "LMS Content Progress",
            "content": content,
            "student": student,
            "lms_course": content_doc.lms_course,
            "progress_percent": progress_percent,
            "time_spent_minutes": time_spent,
            "status": "In Progress" if progress_percent > 0 else "Not Started"
        })
        progress.insert(ignore_permissions=True)

    return {
        "status": progress.status,
        "progress_percent": progress.progress_percent,
        "completed": progress.status == "Completed"
    }


@frappe.whitelist()
def get_course_progress(lms_course, student):
    """Get student's overall progress in a course"""
    total_content = frappe.db.count("LMS Content", {
        "lms_course": lms_course,
        "status": "Published",
        "is_mandatory": 1
    })

    if not total_content:
        return {"total": 0, "completed": 0, "progress": 0}

    completed_content = frappe.db.count("LMS Content Progress", {
        "lms_course": lms_course,
        "student": student,
        "status": "Completed"
    })

    # Get detailed progress
    progress_records = frappe.get_all("LMS Content Progress",
        filters={
            "lms_course": lms_course,
            "student": student
        },
        fields=["content", "status", "progress_percent", "time_spent_minutes"]
    )

    total_time = sum(p.time_spent_minutes for p in progress_records)

    return {
        "total_content": total_content,
        "completed_content": completed_content,
        "progress_percent": (completed_content / total_content) * 100 if total_content else 0,
        "total_time_minutes": total_time,
        "details": progress_records
    }


@frappe.whitelist()
def mark_content_complete(content, student):
    """Mark content as complete"""
    return track_content_progress(content, student, 100, 0)

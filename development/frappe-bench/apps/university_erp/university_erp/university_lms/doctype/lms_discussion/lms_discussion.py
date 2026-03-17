# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LMSDiscussion(Document):
    def validate(self):
        self.update_stats()

    def update_stats(self):
        """Update discussion statistics"""
        self.reply_count = len(self.replies) if self.replies else 0
        if self.replies:
            self.last_reply_on = max(r.reply_date for r in self.replies if r.reply_date)


@frappe.whitelist()
def get_course_discussions(lms_course, include_replies=False):
    """Get discussions for a course"""
    discussions = frappe.get_all("LMS Discussion",
        filters={"lms_course": lms_course},
        fields=["name", "title", "created_by_type", "student", "instructor",
                "is_pinned", "is_locked", "reply_count", "view_count",
                "last_reply_on", "creation"],
        order_by="is_pinned desc, last_reply_on desc"
    )

    if include_replies:
        for disc in discussions:
            disc["replies"] = frappe.get_all("Discussion Reply",
                filters={"parent": disc.name},
                fields=["reply_by_type", "student", "instructor", "reply_content",
                        "reply_date", "is_answer", "upvotes"],
                order_by="reply_date"
            )

    return discussions


@frappe.whitelist()
def add_discussion_reply(discussion_name, reply_content, reply_by_type, student=None, instructor=None):
    """Add a reply to a discussion"""
    discussion = frappe.get_doc("LMS Discussion", discussion_name)

    if discussion.is_locked:
        frappe.throw(_("This discussion is locked and cannot receive new replies"))

    discussion.append("replies", {
        "reply_by_type": reply_by_type,
        "student": student,
        "instructor": instructor,
        "reply_content": reply_content,
        "reply_date": now_datetime()
    })

    discussion.save(ignore_permissions=True)

    return {"message": _("Reply added successfully"), "reply_count": discussion.reply_count}


@frappe.whitelist()
def increment_view_count(discussion_name):
    """Increment view count for a discussion"""
    frappe.db.sql("""
        UPDATE `tabLMS Discussion`
        SET view_count = view_count + 1
        WHERE name = %s
    """, discussion_name)
    frappe.db.commit()

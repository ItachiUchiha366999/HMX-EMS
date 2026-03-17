# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today


def get_context(context):
    """Get context for notice detail page"""
    context.no_cache = 1

    # Get notice name from path
    notice_name = frappe.form_dict.get("notice") or frappe.form_dict.get("name")

    if not notice_name:
        # Try to get from path
        path = frappe.local.request.path
        if "/notice-board/" in path:
            notice_name = path.split("/notice-board/")[-1]

    if not notice_name:
        frappe.throw(_("Notice not found"), frappe.DoesNotExistError)

    # Get notice
    notice = frappe.get_doc("Notice Board", notice_name)

    # Check if notice is published
    if notice.docstatus != 1:
        frappe.throw(_("Notice not found"), frappe.DoesNotExistError)

    # Check if notice is expired
    if notice.expiry_date and notice.expiry_date < today():
        frappe.throw(_("This notice has expired"), frappe.DoesNotExistError)

    # Check user permission
    from university_erp.university_erp.doctype.notice_board.notice_board import is_notice_for_user
    if not is_notice_for_user(notice, frappe.session.user):
        frappe.throw(_("You don't have permission to view this notice"), frappe.PermissionError)

    # Increment view count
    notice.increment_view_count()

    # Get related notices (same type)
    related_notices = frappe.get_all(
        "Notice Board",
        filters={
            "docstatus": 1,
            "notice_type": notice.notice_type,
            "name": ["!=", notice.name],
            "publish_date": ["<=", today()]
        },
        or_filters=[
            ["expiry_date", "is", "not set"],
            ["expiry_date", ">=", today()]
        ],
        fields=["name", "title", "notice_type", "publish_date"],
        order_by="publish_date desc",
        limit=3
    )

    context.notice = notice
    context.related_notices = related_notices
    context.title = notice.title


def get_list_context(context):
    """For route matching"""
    context.row_template = "university_erp/www/notice-board/notice.html"
    context.get_list = get_notice
    return context


def get_notice(doctype, txt, filters, limit_start, limit_page_length=20, order_by=None):
    """Get single notice for list context"""
    return []

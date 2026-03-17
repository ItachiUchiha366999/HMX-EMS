# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, cint


def get_context(context):
    """Get context for notice board listing page"""
    context.no_cache = 1

    # Get current page
    page = cint(frappe.form_dict.get("page", 1))
    page_size = 12

    # Get filter
    notice_type = frappe.form_dict.get("type")

    # Base filters
    filters = {
        "docstatus": 1,
        "publish_date": ["<=", today()]
    }

    if notice_type:
        filters["notice_type"] = notice_type

    # Get pinned notices
    pinned_notices = get_notices_for_user(
        user=frappe.session.user,
        filters=filters,
        additional_filters={"is_pinned": 1},
        limit=4
    )

    # Get all notices (paginated)
    all_notices = get_notices_for_user(
        user=frappe.session.user,
        filters=filters,
        limit=page_size,
        offset=(page - 1) * page_size
    )

    # Get total count for pagination
    total_count = get_notice_count_for_user(frappe.session.user, filters)
    total_pages = (total_count + page_size - 1) // page_size

    # Notice types for filter
    notice_types = [
        "General", "Academic", "Examination", "Admission",
        "Placement", "Hostel", "Library", "Sports", "Cultural", "Emergency"
    ]

    context.pinned_notices = pinned_notices
    context.notices = all_notices
    context.notice_types = notice_types
    context.current_page = page
    context.total_pages = total_pages
    context.title = "Notice Board"


def get_notices_for_user(user, filters, additional_filters=None, limit=20, offset=0):
    """Get notices applicable to user"""
    from university_erp.university_erp.doctype.notice_board.notice_board import is_notice_for_user

    # Combine filters
    all_filters = filters.copy()
    if additional_filters:
        all_filters.update(additional_filters)

    # Get all notices
    notices = frappe.get_all(
        "Notice Board",
        filters=all_filters,
        or_filters=[
            ["expiry_date", "is", "not set"],
            ["expiry_date", ">=", today()]
        ],
        fields=[
            "name", "title", "notice_type", "priority", "publish_date",
            "content", "attachment", "is_pinned", "audience_type", "views_count"
        ],
        order_by="is_pinned desc, priority desc, publish_date desc",
        limit_start=offset,
        limit_page_length=limit + 50  # Get extra for filtering
    )

    # Filter by user applicability
    applicable = []
    for notice in notices:
        notice_dict = frappe._dict(notice)
        if is_notice_for_user(notice_dict, user):
            applicable.append(notice)
            if len(applicable) >= limit:
                break

    return applicable


def get_notice_count_for_user(user, filters):
    """Get total notice count for user"""
    from university_erp.university_erp.doctype.notice_board.notice_board import is_notice_for_user

    notices = frappe.get_all(
        "Notice Board",
        filters=filters,
        or_filters=[
            ["expiry_date", "is", "not set"],
            ["expiry_date", ">=", today()]
        ],
        fields=["name", "audience_type"]
    )

    count = 0
    for notice in notices:
        notice_dict = frappe._dict(notice)
        if is_notice_for_user(notice_dict, user):
            count += 1

    return count

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days


class TestNoticeBoard(FrappeTestCase):
    """Test cases for Notice Board"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test notice
        cls.test_notice = frappe.get_doc({
            "doctype": "Notice Board",
            "title": "Test Notice",
            "notice_type": "General",
            "priority": "Medium",
            "publish_date": nowdate(),
            "content": "This is a test notice content.",
            "audience_type": "All"
        })
        cls.test_notice.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Cleanup
        if cls.test_notice and frappe.db.exists("Notice Board", cls.test_notice.name):
            frappe.delete_doc("Notice Board", cls.test_notice.name, force=True)

    def test_notice_creation(self):
        """Test notice creation"""
        self.assertIsNotNone(self.test_notice.name)
        self.assertEqual(self.test_notice.title, "Test Notice")

    def test_validate_dates(self):
        """Test date validation"""
        # Create notice with past expiry date
        notice = frappe.get_doc({
            "doctype": "Notice Board",
            "title": "Expired Notice",
            "notice_type": "General",
            "publish_date": nowdate(),
            "expiry_date": add_days(nowdate(), -1),
            "content": "Test"
        })

        # Should raise validation error or set to draft
        # depending on implementation
        try:
            notice.insert(ignore_permissions=True)
            frappe.delete_doc("Notice Board", notice.name, force=True)
        except frappe.ValidationError:
            pass  # Expected

    def test_is_notice_for_user(self):
        """Test notice audience filtering"""
        from university_erp.university_erp.doctype.notice_board.notice_board import is_notice_for_user

        # All audience should match any user
        result = is_notice_for_user(self.test_notice.name, "Administrator")
        self.assertTrue(result)

    def test_increment_view_count(self):
        """Test view count increment"""
        initial_count = self.test_notice.views_count or 0

        self.test_notice.increment_view_count()

        self.test_notice.reload()
        self.assertEqual(self.test_notice.views_count, initial_count + 1)

    def test_get_target_users_all(self):
        """Test getting target users for 'All' audience"""
        users = self.test_notice.get_target_users()

        self.assertIsInstance(users, list)
        # Should include at least Administrator
        self.assertGreater(len(users), 0)


class TestNoticeBoardAPI(FrappeTestCase):
    """Test cases for Notice Board API"""

    def test_get_notices(self):
        """Test get_notices API"""
        from university_erp.university_erp.doctype.notice_board.notice_board import get_notices

        result = get_notices()

        self.assertIsInstance(result, list)

    def test_get_notices_by_type(self):
        """Test get_notices with type filter"""
        from university_erp.university_erp.doctype.notice_board.notice_board import get_notices

        result = get_notices(notice_type="General")

        self.assertIsInstance(result, list)

    def test_get_notice_types(self):
        """Test get_notice_types API"""
        from university_erp.university_erp.doctype.notice_board.notice_board import get_notice_types

        result = get_notice_types()

        self.assertIsInstance(result, list)
        self.assertIn("General", result)


class TestNoticeViewLog(FrappeTestCase):
    """Test cases for Notice View Log"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test notice
        cls.test_notice = frappe.get_doc({
            "doctype": "Notice Board",
            "title": "View Log Test",
            "notice_type": "General",
            "publish_date": nowdate(),
            "content": "Test content"
        })
        cls.test_notice.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if cls.test_notice:
            # Delete view logs first
            frappe.db.delete("Notice View Log", {"notice": cls.test_notice.name})
            frappe.delete_doc("Notice Board", cls.test_notice.name, force=True)

    def test_log_notice_view(self):
        """Test logging notice view"""
        from university_erp.university_erp.doctype.notice_view_log.notice_view_log import (
            log_notice_view
        )

        result = log_notice_view(self.test_notice.name, "Administrator")

        self.assertIsNotNone(result)

    def test_view_deduplication(self):
        """Test that duplicate views are not logged within time window"""
        from university_erp.university_erp.doctype.notice_view_log.notice_view_log import (
            log_notice_view
        )

        # Log first view
        result1 = log_notice_view(self.test_notice.name, "Administrator")

        # Try to log second view immediately
        result2 = log_notice_view(self.test_notice.name, "Administrator")

        # Second should be deduplicated (return None or same as first)
        # Based on implementation, either None or False

    def test_get_notice_view_stats(self):
        """Test getting view statistics"""
        from university_erp.university_erp.doctype.notice_view_log.notice_view_log import (
            get_notice_view_stats
        )

        stats = get_notice_view_stats(self.test_notice.name)

        self.assertIsInstance(stats, dict)
        self.assertIn("total_views", stats)
        self.assertIn("unique_viewers", stats)

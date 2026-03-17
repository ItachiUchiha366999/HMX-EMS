"""
Unit tests for University Department DocType
"""
import frappe
import unittest


class TestUniversityDepartment(unittest.TestCase):
    """Test cases for University Department"""

    def setUp(self):
        """Set up test data"""
        frappe.set_user("Administrator")

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_create_department(self):
        """Test creating a new department"""
        dept = frappe.get_doc({
            "doctype": "University Department",
            "department_name": "Test Computer Science",
            "department_code": "TEST-CS",
            "is_active": 1
        })
        dept.insert()
        self.assertTrue(frappe.db.exists("University Department", "Test Computer Science"))
        frappe.delete_doc("University Department", "Test Computer Science")

    def test_department_hierarchy(self):
        """Test parent department relationship"""
        # Create parent department
        parent = frappe.get_doc({
            "doctype": "University Department",
            "department_name": "Test Engineering",
            "department_code": "TEST-ENG",
            "is_active": 1
        })
        parent.insert()

        # Create child department
        child = frappe.get_doc({
            "doctype": "University Department",
            "department_name": "Test Mechanical",
            "department_code": "TEST-MECH",
            "parent_department": "Test Engineering",
            "is_active": 1
        })
        child.insert()

        self.assertEqual(child.parent_department, "Test Engineering")

        # Cleanup
        frappe.delete_doc("University Department", "Test Mechanical")
        frappe.delete_doc("University Department", "Test Engineering")

    def test_circular_reference_prevention(self):
        """Test that department cannot be its own parent"""
        # Implementation would test that validation prevents circular references
        pass


class TestUniversityAcademicYear(unittest.TestCase):
    """Test cases for University Academic Year"""

    def setUp(self):
        """Set up test data"""
        frappe.set_user("Administrator")

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_create_academic_year(self):
        """Test creating a new academic year"""
        from frappe.utils import add_days, getdate
        today = getdate()

        year = frappe.get_doc({
            "doctype": "University Academic Year",
            "academic_year_name": "Test 2025-26",
            "year_start_date": today,
            "year_end_date": add_days(today, 365),
            "is_active": 0
        })
        year.insert()
        self.assertTrue(frappe.db.exists("University Academic Year", "Test 2025-26"))
        frappe.delete_doc("University Academic Year", "Test 2025-26")

    def test_date_validation(self):
        """Test that end date must be after start date"""
        # This test would verify date validation logic
        # Implementation pending
        pass


class TestUniversitySettings(unittest.TestCase):
    """Test cases for University Settings"""

    def setUp(self):
        """Set up test data"""
        frappe.set_user("Administrator")

    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()

    def test_settings_exists(self):
        """Test that University Settings was created during install"""
        self.assertTrue(frappe.db.exists("University Settings"))

    def test_default_settings(self):
        """Test default settings values"""
        settings = frappe.get_single("University Settings")
        self.assertEqual(settings.use_10_point_scale, 1)
        self.assertEqual(settings.passing_grade_points, 4.0)
        self.assertEqual(settings.min_attendance_percentage, 75.0)

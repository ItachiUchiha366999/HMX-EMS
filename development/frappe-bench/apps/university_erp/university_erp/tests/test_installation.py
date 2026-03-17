"""
Unit tests for university_erp app installation and fixtures
"""
import frappe
import unittest


class TestInstallation(unittest.TestCase):
    """Test cases for app installation"""

    def setUp(self):
        """Set up test data"""
        frappe.set_user("Administrator")

    def test_app_installed(self):
        """Test that university_erp app is installed"""
        installed_apps = frappe.get_installed_apps()
        self.assertIn("university_erp", installed_apps)

    def test_university_roles_created(self):
        """Test that all 11 university roles were created"""
        expected_roles = [
            "University Admin",
            "University Registrar",
            "University Finance",
            "University HR Admin",
            "University HOD",
            "University Exam Cell",
            "University Faculty",
            "University Student",
            "University Librarian",
            "University Warden",
            "University Placement Officer"
        ]

        for role_name in expected_roles:
            self.assertTrue(
                frappe.db.exists("Role", role_name),
                f"Role {role_name} should exist"
            )

    def test_custom_fields_created(self):
        """Test that custom fields were created on Education DocTypes"""
        # Test Student custom fields
        student_fields = frappe.get_all(
            "Custom Field",
            filters={"dt": "Student", "module": "University ERP"},
            fields=["fieldname"]
        )
        self.assertGreater(len(student_fields), 0, "Student should have custom fields")

        # Test Program custom fields
        program_fields = frappe.get_all(
            "Custom Field",
            filters={"dt": "Program", "module": "University ERP"},
            fields=["fieldname"]
        )
        self.assertGreater(len(program_fields), 0, "Program should have custom fields")

        # Test Course custom fields
        course_fields = frappe.get_all(
            "Custom Field",
            filters={"dt": "Course", "module": "University ERP"},
            fields=["fieldname"]
        )
        self.assertGreater(len(course_fields), 0, "Course should have custom fields")

    def test_grading_scale_created(self):
        """Test that University 10-Point Scale was created"""
        self.assertTrue(
            frappe.db.exists("Grading Scale", "University 10-Point Scale"),
            "University 10-Point Scale should exist"
        )

        scale = frappe.get_doc("Grading Scale", "University 10-Point Scale")
        self.assertEqual(len(scale.intervals), 8, "Should have 8 grade intervals")

        # Verify grade codes
        grade_codes = [interval.grade_code for interval in scale.intervals]
        expected_grades = ["O", "A+", "A", "B+", "B", "C", "P", "F"]
        self.assertEqual(grade_codes, expected_grades)

    def test_erpnext_workspaces_hidden(self):
        """Test that ERPNext workspaces are hidden"""
        hidden_workspaces = [
            "Manufacturing",
            "Stock",
            "Selling",
            "Buying",
            "CRM",
            "Projects",
            "Assets",
            "Quality",
            "Support"
        ]

        for workspace_name in hidden_workspaces:
            if frappe.db.exists("Workspace", workspace_name):
                public = frappe.db.get_value("Workspace", workspace_name, "public")
                self.assertEqual(
                    public, 0,
                    f"Workspace {workspace_name} should be hidden (public=0)"
                )

    def test_core_doctypes_created(self):
        """Test that core university DocTypes were created"""
        core_doctypes = [
            "University Department",
            "University Academic Year",
            "University Settings"
        ]

        for doctype_name in core_doctypes:
            self.assertTrue(
                frappe.db.exists("DocType", doctype_name),
                f"DocType {doctype_name} should exist"
            )

    def test_override_classes_configured(self):
        """Test that override classes are properly configured in hooks"""
        from university_erp import hooks

        self.assertIn("Student", hooks.override_doctype_class)
        self.assertIn("Program", hooks.override_doctype_class)
        self.assertIn("Course", hooks.override_doctype_class)
        self.assertIn("Assessment Result", hooks.override_doctype_class)
        self.assertIn("Fees", hooks.override_doctype_class)
        self.assertIn("Student Applicant", hooks.override_doctype_class)


class TestCustomFields(unittest.TestCase):
    """Test specific custom field configurations"""

    def setUp(self):
        """Set up test data"""
        frappe.set_user("Administrator")

    def test_student_enrollment_number_field(self):
        """Test that Student has custom_enrollment_number field"""
        field = frappe.db.get_value(
            "Custom Field",
            {"dt": "Student", "fieldname": "custom_enrollment_number"},
            ["label", "fieldtype", "unique", "reqd"],
            as_dict=True
        )
        self.assertIsNotNone(field)
        self.assertEqual(field.fieldtype, "Data")
        self.assertEqual(field.unique, 1)
        self.assertEqual(field.reqd, 1)

    def test_program_cbcs_fields(self):
        """Test that Program has CBCS-related fields"""
        cbcs_fields = frappe.get_all(
            "Custom Field",
            filters={
                "dt": "Program",
                "fieldname": ["in", ["custom_credit_system", "custom_min_credits_graduation"]]
            },
            fields=["fieldname"]
        )
        self.assertEqual(len(cbcs_fields), 2, "Should have 2 CBCS fields")

    def test_course_ltp_fields(self):
        """Test that Course has L-T-P structure fields"""
        ltp_fields = frappe.get_all(
            "Custom Field",
            filters={
                "dt": "Course",
                "fieldname": ["in", [
                    "custom_lecture_hours",
                    "custom_tutorial_hours",
                    "custom_practical_hours"
                ]]
            },
            fields=["fieldname"]
        )
        self.assertEqual(len(ltp_fields), 3, "Should have 3 L-T-P fields")

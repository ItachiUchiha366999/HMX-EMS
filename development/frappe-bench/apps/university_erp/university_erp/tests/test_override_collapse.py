"""Tests: overrides/ directory removed and override_doctype_class entries gone from hooks.py.

Expected RED until Wave 3 (plan 05 collapses overrides into forked controllers).
"""
import importlib
import os
import unittest


class TestOverrideCollapse(unittest.TestCase):
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_overrides_dir_removed(self):
        overrides_dir = os.path.join(self.BASE, "overrides")
        self.assertFalse(
            os.path.isdir(overrides_dir),
            "university_erp/overrides/ should be removed after plan 05",
        )

    def test_hooks_no_override_doctype_class_for_education(self):
        hooks_path = os.path.join(self.BASE, "hooks.py")
        with open(hooks_path) as fh:
            content = fh.read()
        for dt in [
            "Student",
            "Course",
            "Program",
            "Fees",
            "Assessment Result",
            "Student Applicant",
        ]:
            self.assertNotIn(
                f'"{dt}": "university_erp.overrides',
                content,
                f"hooks.py still has override_doctype_class entry for {dt}",
            )

    def test_forked_student_has_university_methods(self):
        m = importlib.import_module(
            "university_erp.university_student_info.doctype.student.student"
        )
        self.assertTrue(hasattr(m.Student, "validate_enrollment_number"))
        self.assertTrue(hasattr(m.Student, "calculate_cgpa"))

    def test_forked_fees_has_university_methods(self):
        m = importlib.import_module(
            "university_erp.university_finance.doctype.fees.fees"
        )
        self.assertTrue(
            hasattr(m.Fees, "calculate_penalty") or hasattr(m.Fees, "calculate_net_amount")
        )

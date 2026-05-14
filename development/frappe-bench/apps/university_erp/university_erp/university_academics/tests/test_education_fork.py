"""Tests: forked Education doctypes are owned by University Academics and CRUD-accessible.

Skeleton — populated by plan 03.3.1-02/03/04 after fork lands.
"""
import unittest

import frappe


class TestEducationForkAcademics(unittest.TestCase):
    MODULE = "University Academics"
    DOCTYPES: list = [
        "Academic Term",
        "Academic Year",
        "Assessment Criteria",
        "Assessment Criteria Group",
        "Assessment Group",
        "Assessment Plan",
        "Assessment Plan Criteria",
        "Assessment Result",
        "Assessment Result Detail",
        "Assessment Result Tool",
        "Course",
        "Course Activity",
        "Course Assessment Criteria",
        "Course Enrollment",
        "Course Schedule",
        "Course Scheduling Tool",
        "Course Topic",
        "Education Settings",
        "Grading Scale",
        "Grading Scale Interval",
        "Program",
        "Program Course",
        "Program Enrollment",
        "Program Enrollment Course",
        "Program Enrollment Fee",
        "Program Enrollment Tool",
        "Program Enrollment Tool Student",
        "Topic",
        "Topic Content",
    ]

    def test_doctypes_owned_by_module(self):
        if not self.DOCTYPES:
            self.skipTest(
                "No doctypes registered yet -- populated by subsequent plan"
            )
        for dt in self.DOCTYPES:
            mod = frappe.db.get_value("DocType", dt, "module")
            self.assertEqual(
                mod, self.MODULE, f"{dt} module={mod}, expected {self.MODULE}"
            )

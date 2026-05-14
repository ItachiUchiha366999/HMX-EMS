"""Tests: forked Education doctypes are owned by University Student Info and CRUD-accessible.

Skeleton — populated by plan 03.3.1-02/03/04 after fork lands.
"""
import unittest

import frappe


class TestEducationForkStudentInfo(unittest.TestCase):
    MODULE = "University Student Info"
    DOCTYPES: list = [
        "Student",
        "Student Group",
        "Student Group Creation Tool",
        "Student Group Creation Tool Course",
        "Student Group Instructor",
        "Student Group Student",
        "Student Attendance",
        "Student Attendance Tool",
        "Student Log",
        "Student Leave Application",
        "Student Language",
        "Student Sibling",
        "Student Siblings",
        "Student Guardian",
        "Guardian",
        "Guardian Interest",
        "Guardian Student",
        "Room",
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

"""Tests: forked Education doctypes are owned by Faculty Management and CRUD-accessible.

Skeleton — populated by plan 03.3.1-02/03/04 after fork lands.
"""
import unittest

import frappe


class TestEducationForkFacultyManagement(unittest.TestCase):
    MODULE = "Faculty Management"
    DOCTYPES: list = [
        # filled in by plan 02/03/04 after fork
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

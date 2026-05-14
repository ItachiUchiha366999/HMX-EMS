"""Tests: all 9 forked Education reports execute without ImportError.

Expected RED until Wave 3 (plan 07 forks reports into destination modules).
"""
import unittest

import frappe

REPORTS = [
    "Absent Student Report",
    "Assessment Plan Status",
    "Course wise Assessment Report",
    "Final Assessment Grades",
    "Program wise Fee Collection",
    "Student and Guardian Contact Details",
    "Student Batch-Wise Attendance",
    "Student Fee Collection",
    "Student Monthly Attendance Sheet",
]


class TestEducationReports(unittest.TestCase):
    def test_all_reports_importable(self):
        from frappe.desk.query_report import run

        failures = []
        for name in REPORTS:
            if not frappe.db.exists("Report", name):
                failures.append(f"{name}: Report record not found in DB")
                continue
            try:
                run(name, filters={})
            except ImportError as e:
                failures.append(f"{name}: ImportError {e}")
            except Exception:
                # Mandatory-filter or data errors acceptable; ImportError is the blocker.
                pass
        self.assertEqual(
            failures, [], "Report execution failures:\n" + "\n".join(failures)
        )

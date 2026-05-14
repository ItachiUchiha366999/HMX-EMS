"""Tests: zero 'from education.' imports remain in university_erp.

Expected to be RED pre-fork (6 violations in overrides/*.py); turns GREEN after
Wave 3 (plan 05 collapses overrides into forked controllers).
"""
import os
import re
import unittest


class TestEducationImportIntegrity(unittest.TestCase):
    def test_no_from_education_imports(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        violations = []
        for root, dirs, files in os.walk(base):
            dirs[:] = [
                d for d in dirs
                if d not in ("__pycache__", "_archived", "_archived_reports", "tests")
            ]
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(root, f)
                try:
                    with open(path) as fh:
                        for lineno, line in enumerate(fh, 1):
                            if re.search(r"from education\.|\bimport education\b", line):
                                rel = os.path.relpath(path, base)
                                violations.append(f"{rel}:{lineno}: {line.strip()}")
                except (OSError, UnicodeDecodeError):
                    continue
        self.assertEqual(
            violations,
            [],
            "'from education' imports found:\n" + "\n".join(violations),
        )

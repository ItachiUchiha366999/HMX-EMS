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
        # Files exempted because they LEGITIMATELY mention 'education' inside
        # docstrings, comments, or string-literal replacement rules — they do
        # not perform a runtime `from education.` import. Mirrors the
        # exclusion list in scripts/verify_education_removable.py.
        exempt_files = {
            "scripts/fork_education_module.py",
            "scripts/verify_education_removable.py",
        }
        # Match only true python import statements at the start of a logical
        # line (allow leading whitespace for try/conditional imports):
        #   from education.X import ...
        #   import education
        #   import education.X
        import_re = re.compile(
            r"^\s*(?:from\s+education(?:\.|\s)|import\s+education(?:\.|\s|$))"
        )
        for root, dirs, files in os.walk(base):
            dirs[:] = [
                d for d in dirs
                if d not in ("__pycache__", "_archived", "_archived_reports", "tests")
            ]
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(root, f)
                rel = os.path.relpath(path, base)
                if rel in exempt_files:
                    continue
                try:
                    with open(path) as fh:
                        for lineno, line in enumerate(fh, 1):
                            if import_re.match(line):
                                violations.append(f"{rel}:{lineno}: {line.strip()}")
                except (OSError, UnicodeDecodeError):
                    continue
        self.assertEqual(
            violations,
            [],
            "'from education' imports found:\n" + "\n".join(violations),
        )

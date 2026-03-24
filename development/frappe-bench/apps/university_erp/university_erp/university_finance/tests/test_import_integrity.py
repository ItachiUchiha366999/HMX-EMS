import os
import re
import unittest


class TestImportIntegrity(unittest.TestCase):
    """Verify no remaining erpnext.accounts imports in university_finance."""

    # Build pattern dynamically to avoid self-detection when scanning test files
    _FORBIDDEN_PREFIX = "from " + "erpnext" + ".accounts."
    _FORBIDDEN_PATTERN = re.compile(r"^from erpnext\.accounts\.", re.MULTILINE)

    def test_no_erpnext_accounts_imports(self):
        """No .py file under university_finance/ imports from erpnext.accounts."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        violations = []

        for root, dirs, files in os.walk(base_dir):
            # Skip _archived, __pycache__, and tests (this file)
            dirs[:] = [d for d in dirs if d not in ("_archived", "_archived_reports", "__pycache__", "tests")]
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    with open(filepath) as fh:
                        content = fh.read()
                    matches = self._FORBIDDEN_PATTERN.findall(content)
                    if matches:
                        rel = os.path.relpath(filepath, base_dir)
                        violations.append(f"{rel}: {matches}")

        self.assertEqual(
            violations, [],
            "Found forbidden imports in university_finance:\n"
            + "\n".join(violations)
        )

    def test_no_bare_erpnext_import_in_controllers(self):
        """No controller file uses bare 'import erpnext'."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        controllers_dir = os.path.join(base_dir, "controllers")
        if not os.path.exists(controllers_dir):
            self.skipTest("controllers/ not found")

        violations = []
        for f in os.listdir(controllers_dir):
            if f.endswith(".py"):
                filepath = os.path.join(controllers_dir, f)
                with open(filepath) as fh:
                    for lineno, line in enumerate(fh, 1):
                        if re.match(r"^import erpnext\s*$", line):
                            violations.append(f"{f}:{lineno}")

        self.assertEqual(violations, [], f"Bare 'import erpnext' found: {violations}")

    def test_no_erpnext_accounts_in_university_erp_outside_finance(self):
        """No university_erp Python file outside university_finance/ references erpnext.accounts."""
        # Walk university_erp root, excluding university_finance/
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        violations = []

        for root, dirs, files in os.walk(app_dir):
            # Skip university_finance entirely
            if "university_finance" in root:
                continue
            dirs[:] = [d for d in dirs if d not in ("__pycache__", "scripts")]
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    with open(filepath) as fh:
                        content = fh.read()
                    matches = self._FORBIDDEN_PATTERN.findall(content)
                    if matches:
                        rel = os.path.relpath(filepath, app_dir)
                        violations.append(f"{rel}: {matches}")

        self.assertEqual(
            violations, [],
            "Found forbidden imports outside university_finance:\n"
            + "\n".join(violations)
        )

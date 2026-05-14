"""
verify_education_removable.py

Phase 03.3.1 removal verifier. Walks university_erp/ for any remaining
`from education.` or `import education` references. Will report violations
PRE-COLLAPSE (the 6 overrides/*.py files) — that is the baseline. After
Wave 3 (override collapse + import rewrites), this script MUST report 0.

Run from frappe-bench/apps/university_erp/:
    python -m university_erp.scripts.verify_education_removable

Exits 0 if no violations, 1 otherwise.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))  # frappe-bench/apps/university_erp
UNI_ERP_PKG = os.path.join(APP_ROOT, "university_erp")  # inner package

EXCLUDED_DIRS = {"__pycache__", "_archived", "_archived_reports"}
FROM_RE = re.compile(r"^\s*from\s+education\.")
IMPORT_RE = re.compile(r"^\s*import\s+education\b")


def verify_education_removable() -> int:
    """Walk university_erp/ and report all 'from education.' / 'import education' usages.

    Returns:
        Total violation count (each matched line counts once).
    """
    if not os.path.isdir(UNI_ERP_PKG):
        print(f"ERROR: package root not found: {UNI_ERP_PKG}", file=sys.stderr)
        return -1

    violations = 0
    for root, dirs, files in os.walk(UNI_ERP_PKG):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path) as fh:
                    for lineno, line in enumerate(fh, 1):
                        if FROM_RE.search(line) or IMPORT_RE.search(line):
                            rel = os.path.relpath(path, APP_ROOT)
                            print(f"{rel}:{lineno}: {line.rstrip()}")
                            violations += 1
            except (OSError, UnicodeDecodeError):
                continue
    return violations


if __name__ == "__main__":
    n = verify_education_removable()
    print(f"\nTotal violations: {n}")
    sys.exit(1 if n else 0)

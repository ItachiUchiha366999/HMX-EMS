# Coding Conventions

**Analysis Date:** 2026-03-17

## Naming Patterns

**Files:**
- Document classes: `snake_case.py` (e.g., `academic_year.py`, `student_leave_application.py`)
- Test files: `test_*.py` (e.g., `test_academic_year.py`, `test_student.py`)
- Configuration files: `*.py` in config directories (e.g., `config/desktop.py`, `config/docs.py`)
- Dashboard files: `*_dashboard.py` (e.g., `academic_year_dashboard.py`)

**Classes:**
- Document classes: `PascalCase` inheriting from `Document` (e.g., `AcademicYear`, `Student`, `ProgramEnrollment`)
- Test classes: `TestPascalCase` inheriting from `unittest.TestCase` (e.g., `TestAcademicYear`, `TestStudent`)

**Functions:**
- Module-level functions: `snake_case` (e.g., `get_course`, `mark_attendance`, `enroll_student`)
- Methods within classes: `snake_case` (e.g., `validate_dates()`, `check_unique()`, `get_program_enrollments()`)
- Frappe whitelisted API endpoints: `@frappe.whitelist()` decorator with `snake_case` function names (e.g., `get_fee_structure()`, `mark_assessment_result()`)

**Variables:**
- Instance variables and local variables: `snake_case` (e.g., `student_group`, `course_schedule`, `from_date`)
- Doctype names: Use uppercase in strings (e.g., `"Academic Year"`, `"Student Group"`)
- Test data dictionary keys: `snake_case` (e.g., `"program_name"`, `"from_date"`, `"to_date"`)

**Constants:**
- Configuration/test data: `UPPERCASE` (e.g., `test_data`, test dependencies arrays)
- Or as dictionary keys with `snake_case` in test data structures

## Code Style

**Formatting:**
- Tool: `black` (code formatter)
- Configuration: `.pre-commit-config.yaml` defines black hook
- Additional dependencies: `click==8.0.4` for black

**Linting:**
- Tool: `flake8` with `flake8-bugbear`
- Configuration: `.github/helper/flake8.conf`
- Max line length: 200 characters
- Many PEP 8 style rules ignored (see configuration file for full list of ignored error codes)

**Pre-commit Hooks:**
- Location: `/workspace/development/frappe-bench/apps/education/.pre-commit-config.yaml`
- Enabled checks:
  - `trailing-whitespace`
  - `check-yaml`
  - `no-commit-to-branch` (prevents commits to `develop`)
  - `check-merge-conflict`
  - `check-ast`
  - `black` (automatic code formatting)
  - `flake8` (linting)

## Import Organization

**Order:**
1. Standard library imports (e.g., `import json`, `import datetime`, `import unittest`)
2. Third-party imports (e.g., `import frappe`)
3. Frappe framework imports (e.g., `from frappe import _`, `from frappe.model.document import Document`)
4. Application imports (e.g., `from education.education.utils import ...`, `from education.education.doctype.student.test_student import create_student`)

**Path Aliases:**
- Uses full package paths: `from education.education.doctype.<doctype>.test_<doctype> import <function>`
- No abbreviated imports observed; always explicit

**Common Import Patterns:**
```python
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, nowdate, flt, cstr
from frappe.desk.form.linked_with import get_linked_doctypes
from frappe.email.doctype.email_group.email_group import add_subscribers
from frappe.model.mapper import get_mapped_doc
from erpnext import get_default_company
```

## Error Handling

**Patterns:**
- Use `frappe.throw()` for validation errors with internationalized messages via `_()` (e.g., `frappe.throw(_("Error message"))`)
- Catch `frappe.ValidationError` and `frappe.DoesNotExistError` for specific Frappe exceptions
- Try-except blocks wrap operations that may fail (e.g., document creation, enrollment operations)
- Return `None` explicitly when data not found rather than raising exceptions in helper functions
- Use `frappe.db.exists()` to check if records exist before operations
- Use `frappe.db.rollback()` in tests to clean up state

**Examples from codebase:**
```python
# Throwing validation errors
frappe.throw(_("Error message format"))

# Catching specific exceptions
try:
    enrollment = frappe.get_doc({...}).save()
except frappe.exceptions.ValidationError:
    enrollment_name = frappe.get_list("Program Enrollment", filters={...})[0].name

# Returning None for not found
def get_student(email):
    try:
        student_id = frappe.get_all("Student", {"student_email_id": email}, ["name"])[0].name
        return frappe.get_doc("Student", student_id)
    except IndexError:
        return None
```

## Logging

**Framework:** Frappe's built-in messaging system

**Patterns:**
- `frappe.msgprint(_("Message text"))` - Display user-facing messages
- `frappe.msgprint(message, title="Title", indicator="green")` - Styled messages with title and color indicator
- No explicit logging library imports; relies on Frappe's msgprint for user feedback
- No debug logging observed in main codebase

**Example:**
```python
frappe.msgprint(
    _("Attendance has been marked successfully.")
)

frappe.msgprint(
    _("Course {0} has been added to all programs").format(frappe.bold(course)),
    title=_("Programs updated"),
    indicator="green"
)
```

## Comments

**When to Comment:**
- Method-level docstrings describing purpose and parameters are standard
- Copyright headers at top of every file
- License comments (e.g., "# For license information, please see license.txt")
- Inline comments explaining non-obvious logic (e.g., validation reasons)
- Commented-out code (e.g., `# test_records = frappe.get_test_records('Course')`) indicates conditional test data

**JSDoc/Docstrings:**
- Python docstrings used for function documentation
- Format: Triple-quoted strings with description and parameter documentation
- Parameters documented with `:param name: Description`
- Return values documented with `:return: Description` or implicit in docstring

**Example:**
```python
def get_course(program):
    """Return list of courses for a particular program
    :param program: Program
    """
    courses = frappe.db.sql(...)
    return courses

def check_attendance_records_exist(course_schedule=None, student_group=None, date=None):
    """Check if Attendance Records are made against the specified Course Schedule or Student Group for given date.

    :param course_schedule: Course Schedule.
    :param student_group: Student Group.
    :param date: Date.
    """
```

## Function Design

**Size:** Functions vary from 2-50 lines; validation methods and API endpoints tend toward 15-30 lines

**Parameters:**
- Use keyword arguments with defaults for optional parameters
- Group related parameters together
- Pass dictionaries/objects rather than many individual parameters where appropriate
- Frappe API functions often accept optional parameters with sensible defaults

**Return Values:**
- Return specific data types: lists of dictionaries, single documents, boolean flags, or None
- API functions decorated with `@frappe.whitelist()` return JSON-serializable types
- Helper functions return None when no data found (e.g., `get_result()` returns None if not found)

**Validation Methods:**
- Follow pattern: `def validate_<aspect>(self):` within Document classes
- Called sequentially during `validate()` method
- Throw errors rather than returning boolean values
- Examples: `validate_dates()`, `validate_duplication()`, `validate_term_against_year()`

## Module Design

**Exports:**
- Document classes exported via class definition
- Public API functions decorated with `@frappe.whitelist()` for frontend access
- Module-level functions available for cross-module imports
- Test helper functions (prefixed with verbs: `create_`, `make_`, `get_`) exported from test modules

**Barrel Files:**
- No barrel files (index.py with re-exports) observed in main codebase
- Each module imports directly from specific files

**Organization by DocType:**
- Standard structure: `/education/doctype/<doctype_name>/`
- Contents:
  - `<doctype_name>.py` - Main Document class
  - `test_<doctype_name>.py` - Test cases and test data factories
  - `<doctype_name>_dashboard.py` - Dashboard customization (when present)
  - `__init__.py` - Package marker
  - Additional JSON configuration files for Frappe DocType definition

---

*Convention analysis: 2026-03-17*

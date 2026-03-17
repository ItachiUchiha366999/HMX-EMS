# Testing Patterns

**Analysis Date:** 2026-03-17

## Test Framework

**Runner:**
- Framework: `unittest` (Python standard library)
- No separate test runner configuration detected (uses Python's built-in unittest discovery)
- Frappe provides test infrastructure via `frappe.get_test_records()`

**Assertion Library:**
- Standard `unittest.TestCase` assertions (no external assertion library)
- Common assertions: `self.assertEqual()`, `self.assertTrue()`, `self.assertRaises()`

**Run Commands:**
- Test discovery: Frappe bench test command (not directly documented in this codebase)
- Pytest/coverage tools: Not detected in this codebase
- Tests run via standard unittest or Frappe's test infrastructure

## Test File Organization

**Location:**
- Pattern: Co-located with source - each DocType has tests in same directory
- Structure: `education/education/doctype/<doctype_name>/test_<doctype_name>.py`
- Examples:
  - `education/education/doctype/academic_year/test_academic_year.py`
  - `education/education/doctype/student/test_student.py`
  - `education/education/doctype/course/test_course.py`

**Naming:**
- Pattern: `test_<doctype_name>.py`
- All test files follow consistent naming convention

**Structure:**
```
education/education/doctype/<doctype>/
├── <doctype>.py              # Main document class
├── test_<doctype>.py         # Test cases
├── <doctype>_dashboard.py    # Optional dashboard
├── __init__.py
└── <doctype>.json            # Frappe DocType definition
```

## Test Structure

**Suite Organization:**

```python
# Copyright headers
import unittest
import frappe
from frappe.utils import getdate

# Optional: Import test helpers and dependencies
from education.education.doctype.student.test_student import create_student
from education.education.doctype.program.test_program import make_program_and_linked_courses

# Optional: Test data declaration
test_records = frappe.get_test_records("Student")
test_data = {
    "program_name": "_Test Program",
    "description": "_Test Program",
    # ...
}

class TestDocTypeName(unittest.TestCase):
    def setUp(self):
        # Create test fixtures
        # Prepare database state
        pass

    def test_feature_one(self):
        # Test case implementation
        pass

    def test_feature_two(self):
        # Test case implementation
        pass

    def tearDown(self):
        # Clean up test data
        # Rollback database changes
        pass

# Optional: Test helper functions
def create_test_fixture():
    pass

def make_test_record(**kwargs):
    pass
```

**Patterns:**

1. **Setup Method:**
   - Create test data and fixtures
   - Set up preconditions for tests
   - Example from `test_student.py`:
   ```python
   def setUp(self):
       create_student({
           "first_name": "_Test Name",
           "last_name": "_Test Last Name",
           "email": "_test_student@example.com",
       })
       make_program_and_linked_courses(
           "_Test Program 1", ["_Test Course 1", "_Test Course 2"]
       )
   ```

2. **Teardown Method:**
   - Clean up created records
   - Rollback database state
   - Example from `test_student.py`:
   ```python
   def tearDown(self):
       for entry in frappe.db.get_all("Course Enrollment"):
           frappe.delete_doc("Course Enrollment", entry.name)

       for entry in frappe.db.get_all("Program Enrollment"):
           doc = frappe.get_doc("Program Enrollment", entry.name)
           doc.cancel()
           doc.delete()
   ```

3. **Test Methods:**
   - Named: `test_<feature_description>(self)`
   - Use assertion methods: `self.assertEqual()`, `self.assertTrue()`, `self.assertRaises()`
   - Use `frappe.db.rollback()` within test to reset state
   - Example from `test_academic_year.py`:
   ```python
   def test_date_validation(self):
       year = frappe.get_doc({
           "doctype": "Academic Year",
           "year_start_date": "13-02-2023",
           "year_end_date": "27-01-2023",
       })
       self.assertRaises(frappe.ValidationError, year.insert)
   ```

## Mocking

**Framework:** Frappe's database mocking (no external mocking library like unittest.mock detected)

**Patterns:**

1. **Creating Test Objects:**
   ```python
   doc = frappe.get_doc({
       "doctype": "DocTypeName",
       "field1": "value1",
       "field2": "value2",
   })
   doc.insert()  # or doc.save()
   doc.submit()  # if needed
   ```

2. **Fetching Test Data:**
   ```python
   # Get existing test record
   student = frappe.get_doc("Student", student_id)

   # Check existence
   attendance = frappe.db.exists("Student Attendance", {
       "leave_application": leave_application.name,
       "status": "Absent"
   })

   # Get value
   student_name = frappe.db.get_value("Student", student_id, "student_name")

   # Get all matching records
   courses = frappe.db.get_all("Course")
   ```

3. **Using Frappe's Random Test Data:**
   ```python
   from frappe.utils.make_random import get_random

   student = get_random("Student")
   ```

4. **Test Data Rollback:**
   ```python
   # Clear data between tests
   frappe.db.sql("""delete from `tabStudent Leave Application`""")

   # Rollback database state
   frappe.db.rollback()
   ```

**What to Mock:**
- External database records (use `frappe.new_doc()` and insert)
- Business objects (Document instances)
- Test data required by assertions

**What NOT to Mock:**
- Frappe's core ORM methods (`get_doc()`, `get_all()`, `db.sql()`)
- Date utilities (`getdate()`, `today()`, `add_days()`)
- Actually use real implementations with test data

## Fixtures and Factories

**Test Data:**

1. **Test Record Functions:**
   ```python
   def create_student(student_dict):
       student = get_student(student_dict["email"])
       if not student:
           student = frappe.get_doc({
               "doctype": "Student",
               "first_name": student_dict["first_name"],
               "last_name": student_dict["last_name"],
               "student_email_id": student_dict["email"],
           }).insert()
       return student

   def get_student(email):
       try:
           student_id = frappe.get_all("Student", {"student_email_id": email}, ["name"])[0].name
           return frappe.get_doc("Student", student_id)
       except IndexError:
           return None
   ```

2. **Parameterized Factory Functions:**
   ```python
   def make_course_schedule_test_record(**args):
       args = frappe._dict(args)

       course_schedule = frappe.new_doc("Course Schedule")
       course_schedule.student_group = args.student_group or "Course-TC101-2014-2015"
       course_schedule.course = args.course or "TC101"
       course_schedule.instructor = args.instructor or "_Test Instructor"
       course_schedule.room = args.room or frappe.get_all("Room")[0].name

       if not args.do_not_save:
           course_schedule.save()
       return course_schedule
   ```

**Location:**
- Test helper functions in the same test file (e.g., `create_student()` in `test_student.py`)
- Shared factories imported from other test modules (e.g., `from education.education.doctype.student.test_student import create_student`)
- Factories prefixed with verbs: `create_`, `make_`, `get_`

**Pattern for Reusable Test Data:**
```python
test_data = {
    "program_name": "_Test Program",
    "description": "_Test Program",
    "course": [
        {
            "course_name": "_Test Course 1",
            "topic": [
                {
                    "topic_name": "_Test Topic 1-1",
                    "content": [
                        {"type": "Article", "name": "_Test Article 1-1"},
                    ],
                },
            ],
        }
    ],
}

def setup_program():
    # Build complex structures from test_data
    pass
```

## Coverage

**Requirements:** Not enforced in codebase (no coverage configuration detected)

**View Coverage:**
- No coverage tool integration detected (pytest-cov, coverage.py not configured)

## Test Types

**Unit Tests:**
- Scope: Individual Document class methods and validation logic
- Approach: Create minimal test fixtures, assert on Document state and side effects
- Example from `test_academic_year.py`:
  ```python
  def test_date_validation(self):
      year = frappe.get_doc({
          "doctype": "Academic Year",
          "year_start_date": "13-02-2023",
          "year_end_date": "27-01-2023",
      })
      self.assertRaises(frappe.ValidationError, year.insert)
  ```

**Integration Tests:**
- Scope: Document interactions, cross-module operations
- Approach: Create linked records, test workflow state changes
- Example from `test_student_leave_application.py`:
  ```python
  def test_attendance_record_creation(self):
      leave_application = create_leave_application()
      attendance_record = frappe.db.exists(
          "Student Attendance",
          {"leave_application": leave_application.name, "status": "Absent"},
      )
      self.assertTrue(attendance_record)
  ```

**E2E Tests:**
- Not used in this codebase
- No separate E2E framework configured

## Common Patterns

**Async Testing:**
- Not detected in codebase (no async operations in Education module tests)

**Error Testing:**
```python
def test_holiday(self):
    # Test that ValidationError is raised
    self.assertRaises(frappe.ValidationError, leave_application.save)

    # Or capture exception and inspect
    try:
        leave_application.save()
    except frappe.ValidationError as e:
        self.assertTrue("error message" in str(e))
```

**Database State Testing:**
```python
# Assert database record exists
attendance_record = frappe.db.exists(
    "Student Attendance",
    {"leave_application": leave_application.name, "status": "Absent"},
)
self.assertTrue(attendance_record)

# Assert specific field value
status = frappe.db.get_value("Student Attendance", attendance.name, "status")
self.assertEqual(status, "Absent")

# Assert no records match criteria
result = frappe.db.exists("Student Attendance", {"leave_application": name})
self.assertIsNone(result)
```

**Test Isolation:**
```python
def test_case_1(self):
    # Create test data
    create_leave_application()

    # Assertions
    self.assertTrue(...)

    # Rollback to isolate from next test
    frappe.db.rollback()

def test_case_2(self):
    # Previous test's rollback ensures clean state
    pass
```

**Test Data Creation Pattern:**
```python
# Simple creation
student = create_student({
    "email": "_test@example.com",
    "first_name": "Test",
    "last_name": "User"
})

# Conditional creation (avoid duplicates)
student = get_student(email)
if not student:
    student = create_student(...)

# Programmatic setup
for course in ["_Test Course 1", "_Test Course 2"]:
    make_course_and_linked_topic(course, [topics])
```

---

*Testing analysis: 2026-03-17*

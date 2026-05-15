# -*- coding: utf-8 -*-
# Copyright (c) 2024, University and contributors
# License: MIT

"""
University ERP Utility Functions

This module provides utility functions used across the University ERP application,
including Jinja template filters and helper functions.
"""

import frappe
from frappe import _


def format_enrollment_number(enrollment_number):
    """
    Format enrollment number for display.

    Jinja filter for formatting enrollment numbers in templates.

    Args:
        enrollment_number (str): Raw enrollment number

    Returns:
        str: Formatted enrollment number

    Example:
        {{ "2024001001" | format_enrollment_number }}
        Output: "2024/001/001"
    """
    if not enrollment_number:
        return ""

    # If already formatted, return as-is
    if "/" in str(enrollment_number):
        return enrollment_number

    enrollment_str = str(enrollment_number)

    # Format: YYYY/XXX/NNN (Year/Department Code/Serial)
    if len(enrollment_str) >= 10:
        year = enrollment_str[:4]
        dept = enrollment_str[4:7]
        serial = enrollment_str[7:]
        return f"{year}/{dept}/{serial}"

    return enrollment_number


def calculate_cgpa(student=None, student_name=None):
    """
    Calculate Cumulative Grade Point Average for a student.

    Jinja filter for calculating CGPA in templates.

    Args:
        student: Student document object or None
        student_name: Student name (docname) if student is None

    Returns:
        float: CGPA rounded to 2 decimal places, or 0.0 if no results

    Example:
        {{ student | calculate_cgpa }}
        {{ calculate_cgpa(student_name="STU-2024-00001") }}
    """
    if student:
        student_name = student.name if hasattr(student, 'name') else student

    if not student_name:
        return 0.0

    # Get all assessment results for the student
    results = frappe.get_all(
        "Assessment Result",
        filters={
            "student": student_name,
            "docstatus": 1  # Only submitted results
        },
        fields=["grade", "total_score", "maximum_score"]
    )

    if not results:
        return 0.0

    # Grade to grade point mapping (10-point scale)
    grade_points = {
        "O": 10.0,   # Outstanding
        "A+": 9.0,
        "A": 8.5,
        "B+": 8.0,
        "B": 7.5,
        "C+": 7.0,
        "C": 6.5,
        "D": 6.0,
        "E": 5.0,   # Pass
        "F": 0.0,   # Fail
        "P": 7.0,   # Pass (for pass/fail courses)
        "W": None,  # Withdrawn (not counted)
        "I": None,  # Incomplete (not counted)
    }

    total_points = 0.0
    count = 0

    for result in results:
        grade = result.get("grade", "").upper()
        if grade in grade_points and grade_points[grade] is not None:
            total_points += grade_points[grade]
            count += 1

    if count == 0:
        return 0.0

    cgpa = total_points / count
    return round(cgpa, 2)


def get_academic_year(date=None):
    """
    Get the academic year for a given date.

    Args:
        date: Date to check (defaults to today)

    Returns:
        str: Academic year in format "YYYY-YY" (e.g., "2024-25")
    """
    from datetime import date as dt_date
    import frappe.utils

    if date is None:
        date = frappe.utils.today()

    if isinstance(date, str):
        date = frappe.utils.getdate(date)

    # Academic year typically starts in July/August
    # Adjust based on your institution's calendar
    if date.month >= 7:  # July onwards
        start_year = date.year
    else:  # January to June
        start_year = date.year - 1

    end_year = start_year + 1
    return f"{start_year}-{str(end_year)[-2:]}"


def get_current_semester():
    """
    Get the current semester based on current date.

    Returns:
        str: "Odd" or "Even"
    """
    from datetime import date

    today = date.today()
    month = today.month

    # Odd semester: July to December
    # Even semester: January to June
    if 7 <= month <= 12:
        return "Odd"
    else:
        return "Even"


def format_currency_inr(amount):
    """
    Format amount in Indian Rupee format.

    Args:
        amount: Number to format

    Returns:
        str: Formatted amount with INR symbol

    Example:
        {{ 150000 | format_currency_inr }}
        Output: "₹1,50,000"
    """
    if not amount:
        return "₹0"

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return str(amount)

    # Handle negative numbers
    sign = ""
    if amount < 0:
        sign = "-"
        amount = abs(amount)

    # Split into integer and decimal parts
    int_part = int(amount)
    decimal_part = amount - int_part

    # Format integer part with Indian numbering system
    s = str(int_part)
    result = ""

    if len(s) > 3:
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result if len(s) > 2 else s + "," + result
            s = s[:-2]
    else:
        result = s

    # Add decimal part if exists
    if decimal_part > 0:
        result += f".{int(decimal_part * 100):02d}"

    return f"{sign}₹{result}"


def get_student_status_badge(status):
    """
    Get Bootstrap badge class for student status.

    Args:
        status: Student status string

    Returns:
        str: Badge HTML class
    """
    status_map = {
        "Active": "badge-success",
        "Enrolled": "badge-success",
        "Graduated": "badge-info",
        "Alumni": "badge-info",
        "On Leave": "badge-warning",
        "Suspended": "badge-danger",
        "Expelled": "badge-danger",
        "Withdrawn": "badge-secondary",
        "Pending": "badge-warning",
    }
    return status_map.get(status, "badge-secondary")


def days_until(target_date):
    """
    Calculate days until a target date.

    Args:
        target_date: Target date

    Returns:
        int: Number of days (negative if past)
    """
    from datetime import date
    import frappe.utils

    if isinstance(target_date, str):
        target_date = frappe.utils.getdate(target_date)

    today = date.today()
    delta = target_date - today
    return delta.days


def get_website_user_home_page(user):
    """
    Get home page for website user based on role.

    This function is called after login to determine where to redirect the user.
    Students are redirected to the student portal, REGARDLESS of other roles.

    Args:
        user (str): Username/email of logged-in user

    Returns:
        str: URL path to redirect to (WITHOUT leading slash - Frappe adds it)
    """
    try:
        # Never redirect Administrator or System Managers
        if user in ["Administrator", "administrator"]:
            return None

        # Check if user has Student role
        if frappe.db.exists("User", user):
            roles = frappe.get_roles(user)

            # Don't redirect System Managers - they should go to desk
            if "System Manager" in roles:
                return None

            # If user has Student role, redirect to student portal
            # This takes precedence over any other role (except System Manager)
            if "Student" in roles:
                # Return path without leading slash - Frappe's auth.py adds "/" + get_home_page()
                return "student_portal"
    except Exception as e:
        frappe.log_error(f"Error in get_website_user_home_page: {str(e)}", "Student Redirect")

    # Default: return None to use default home page
    return None


def format_time(time_value, format_string=None):
    """
    Format time value for display in templates.

    Jinja filter for formatting time values.

    Args:
        time_value: Time value to format (string, datetime.time, or timedelta)
        format_string: Optional format string (e.g., 'h:mm a' for 12-hour format)

    Returns:
        str: Formatted time string

    Example:
        {{ "10:30:00" | format_time }}
        {{ "14:30:00" | format_time("h:mm a") }}  # Output: "2:30 PM"
    """
    if not time_value:
        return ""

    try:
        # Use frappe's built-in format_time if available
        from frappe.utils import format_time as frappe_format_time
        return frappe_format_time(time_value, format_string)
    except Exception:
        # Fallback to simple string representation
        if isinstance(time_value, str):
            # Try to parse and format
            from datetime import datetime
            try:
                if len(str(time_value).split(':')) >= 2:
                    # Parse time string
                    time_obj = datetime.strptime(str(time_value), "%H:%M:%S").time()

                    # Format based on format_string
                    if format_string and 'a' in format_string.lower():
                        # 12-hour format with AM/PM
                        hour = time_obj.hour
                        minute = time_obj.minute
                        period = "AM" if hour < 12 else "PM"
                        hour_12 = hour % 12
                        if hour_12 == 0:
                            hour_12 = 12
                        return f"{hour_12}:{minute:02d} {period}"
                    else:
                        # 24-hour format
                        return f"{time_obj.hour:02d}:{time_obj.minute:02d}"
            except Exception:
                pass

        return str(time_value)


def on_session_creation(login_manager):
    """
    Hook called when a user session is created (after login).

    Redirects students to the student portal immediately after login,
    preventing the "Not Permitted" flash on /app.

    Args:
        login_manager: Frappe LoginManager object
    """
    try:
        user = login_manager.user

        # Never redirect Administrator
        if user in ["Administrator", "administrator", "Guest"]:
            return

        # Get user roles
        roles = frappe.get_roles(user)

        # Don't redirect System Managers - they need desk access
        if "System Manager" in roles:
            return

        if "Student" in roles:
            # Set redirect_to — takes priority over last_visited in localStorage
            frappe.local.response["redirect_to"] = "/student_portal"
            frappe.local.response["home_page"] = "/student_portal"

    except Exception as e:
        # Log error but don't break login
        frappe.log_error(f"on_session_creation error: {str(e)}", "Student Redirect")


# ---------------------------------------------------------------------------
# Education utils migrated into university_erp (Phase 03.3.1 Plan 06, Wave 4)
# Source: frappe-bench/apps/education/education/utils.py
# Only the symbols referenced by forked controllers are migrated here.
# ---------------------------------------------------------------------------


class OverlapError(frappe.ValidationError):
    """Raised when Course Schedule / Assessment Plan time slots overlap."""
    pass


def validate_overlap_for(doc, doctype, fieldname, value=None):
    """Checks overlap for specified field."""
    existing = get_overlap_for(doc, doctype, fieldname, value)
    if existing:
        frappe.throw(
            _("This {0} conflicts with {1} for {2} {3}").format(
                doc.doctype,
                existing.name,
                doc.meta.get_label(fieldname) if not value else fieldname,
                value or doc.get(fieldname),
            ),
            OverlapError,
        )


def get_overlap_for(doc, doctype, fieldname, value=None):
    """Returns overlapping document for specified field."""
    existing = frappe.db.sql(
        """select name, from_time, to_time from `tab{0}`
        where `{1}`=%(val)s and schedule_date = %(schedule_date)s and
        (
            (from_time > %(from_time)s and from_time < %(to_time)s) or
            (to_time > %(from_time)s and to_time < %(to_time)s) or
            (%(from_time)s > from_time and %(from_time)s < to_time) or
            (%(from_time)s = from_time and %(to_time)s = to_time))
        and name!=%(name)s and docstatus!=2""".format(doctype, fieldname),
        {
            "schedule_date": doc.schedule_date,
            "val": value or doc.get(fieldname),
            "from_time": doc.from_time,
            "to_time": doc.to_time,
            "name": doc.name or "No Name",
        },
        as_dict=True,
    )
    return existing[0] if existing else None


def validate_duplicate_student(students):
    """Reject duplicate Student rows in a child table."""
    unique_students = []
    for stud in students:
        if stud.student in unique_students:
            frappe.throw(
                _("Student {0} - {1} appears Multiple times in row {2} & {3}").format(
                    stud.student,
                    stud.student_name,
                    unique_students.index(stud.student) + 1,
                    stud.idx,
                )
            )
        else:
            unique_students.append(stud.student)
    return None


def check_content_completion(content_name, content_type, enrollment_name):
    """LMS helper — returns True if a Course Activity exists for the content."""
    activity = frappe.get_all(
        "Course Activity",
        filters={
            "enrollment": enrollment_name,
            "content_type": content_type,
            "content": content_name,
        },
    )
    return bool(activity)


def check_quiz_completion(quiz, enrollment_name):
    """LMS helper — returns (status, score, result, time_taken) for a Quiz Activity."""
    attempts = frappe.get_all(
        "Quiz Activity",
        filters={"enrollment": enrollment_name, "quiz": quiz.name},
        fields=["name", "activity_date", "score", "status", "time_taken"],
    )
    status = False if quiz.max_attempts == 0 else bool(len(attempts) >= quiz.max_attempts)
    score = None
    result = None
    time_taken = None
    if attempts:
        if quiz.grading_basis == "Last Highest Score":
            attempts = sorted(attempts, key=lambda i: int(i.score), reverse=True)
        score = attempts[0]["score"]
        result = attempts[0]["status"]
        time_taken = attempts[0]["time_taken"]
        if result == "Pass":
            status = True
    return status, score, result, time_taken

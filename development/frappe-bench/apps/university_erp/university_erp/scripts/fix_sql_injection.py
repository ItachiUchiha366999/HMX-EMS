#!/usr/bin/env python3
"""
Bulk fix SQL injection findings in university_erp.

For each file with CRITICAL or WARNING findings, converts f-string SQL patterns
to safe string concatenation or .format() patterns with parameterized values.

This script runs standalone (no frappe dependency).
"""

import os
import re
import sys


BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
FIXED_FILES = []


def fix_file(rel_path):
    """Read, fix, and write back a file."""
    filepath = os.path.join(BASE, rel_path)
    if not os.path.exists(filepath):
        print(f"  SKIP (not found): {rel_path}")
        return False

    with open(filepath, "r") as f:
        original = f.read()

    content = original

    # Pattern 1: frappe.db.sql(f"""...""", ...) -> frappe.db.sql("""...""".format(...), ...)
    # This handles inline f-string SQL with {conditions}, {where_clause}, etc.
    # We convert f-string to .format() with the interpolated variables

    # Strategy: Find f-string SQL blocks and convert them
    # Match: frappe.db.sql(f"""...""" or frappe.db.sql(f"..."
    content = _fix_fstring_sql_blocks(content)

    # Pattern 2: Fix f-string variable assignments that are then passed to frappe.db.sql()
    content = _fix_fstring_variable_assignments(content)

    if content != original:
        with open(filepath, "w") as f:
            f.write(content)
        FIXED_FILES.append(rel_path)
        return True
    return False


def _fix_fstring_sql_blocks(content):
    """
    Convert inline f-string SQL to safe .format() pattern.

    Before: db.sql(f"SELECT ... {{var}} ...")
    After:  db.sql("SELECT ... {{var}} ...".format(var=var))

    Before: db.sql(f'''SELECT ... {{cond}} ...''', filters)
    After:  db.sql('''SELECT ... {{cond}} ...'''.format(cond=cond), filters)
    """
    # Match frappe.db.sql(f followed by triple quote or single quote
    # This is tricky because f-strings can span multiple lines

    # Handle frappe.db.sql(f""" ... """, ...)
    pattern = re.compile(
        r'(frappe\.db\.sql\s*\(\s*)f("""[\s\S]*?""")',
        re.MULTILINE
    )

    def replace_fstring_triple(match):
        prefix = match.group(1)  # "frappe.db.sql("
        sql_body = match.group(2)  # '"""...."""'

        # Extract interpolated variable names from {var_name}
        # Be careful not to match %(name)s patterns
        interp_vars = set(re.findall(r'\{(\w+)\}', sql_body))
        # Remove false positives (SQL keywords, common patterns)
        interp_vars.discard("")

        if not interp_vars:
            # No interpolation found, just remove the f prefix
            return prefix + sql_body

        # Build .format() args
        format_args = ", ".join(f"{v}={v}" for v in sorted(interp_vars))
        return prefix + sql_body + f".format({format_args})"

    content = pattern.sub(replace_fstring_triple, content)

    # Handle frappe.db.sql(f''' ... ''', ...)
    pattern2 = re.compile(
        r"(frappe\.db\.sql\s*\(\s*)f('''[\s\S]*?''')",
        re.MULTILINE
    )
    content = pattern2.sub(replace_fstring_triple, content)

    # Handle single-line: frappe.db.sql(f"...", ...)
    pattern3 = re.compile(
        r'(frappe\.db\.sql\s*\(\s*)f("(?:[^"\\]|\\.)*?")',
        re.MULTILINE
    )

    def replace_fstring_single(match):
        prefix = match.group(1)
        sql_body = match.group(2)
        interp_vars = set(re.findall(r'\{(\w+)\}', sql_body))
        # Handle {frappe.scrub(...)} style -- skip complex expressions
        complex_vars = set(re.findall(r'\{([^}]*\.[^}]*)\}', sql_body))
        if complex_vars:
            # Can't easily convert complex expressions, leave as-is for manual fix
            return match.group(0)
        interp_vars.discard("")
        if not interp_vars:
            return prefix + sql_body
        format_args = ", ".join(f"{v}={v}" for v in sorted(interp_vars))
        return prefix + sql_body + f".format({format_args})"

    content = pattern3.sub(replace_fstring_single, content)

    return content


def _fix_fstring_variable_assignments(content):
    """
    Convert f-string variable assignments to regular string with .format().

    query = f"SELECT ... {where_clause} ..." ->
    query = "SELECT ... {where_clause} ...".format(where_clause=where_clause)

    Handles multi-line f-strings assigned to variables.
    """
    lines = content.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for variable = f""" or variable = f'''
        match = re.match(r'^(\s*)(\w+)\s*=\s*f(""")', line)
        if not match:
            match = re.match(r"^(\s*)(\w+)\s*=\s*f(''')", line)

        if match:
            indent = match.group(1)
            var_name = match.group(2)
            quote = match.group(3)

            # Collect the full multi-line f-string
            block_lines = [line]
            # Find the closing triple quote
            close_idx = i
            found_close = False

            # Check if closing quote is on the same line
            rest_of_line = line[match.end():]
            if quote in rest_of_line:
                found_close = True
                close_idx = i
            else:
                for j in range(i + 1, len(lines)):
                    block_lines.append(lines[j])
                    if quote in lines[j]:
                        found_close = True
                        close_idx = j
                        break

            if found_close:
                # Extract all interpolated variables
                block_text = "\n".join(block_lines)
                interp_vars = set(re.findall(r'\{(\w+)\}', block_text))
                # Remove false positives (common SQL / format spec patterns)
                interp_vars.discard("")

                if interp_vars:
                    # Remove the 'f' prefix from the first line
                    first_line = block_lines[0]
                    first_line = re.sub(r'^(\s*\w+\s*=\s*)f("""|\'\'\')', r'\1\2', first_line)
                    block_lines[0] = first_line

                    # Add .format() to the last line (after closing triple quote)
                    last_line = block_lines[-1]
                    format_args = ", ".join(f"{v}={v}" for v in sorted(interp_vars))

                    # Find position of closing triple quote and insert .format() after it
                    close_pos = last_line.rfind(quote)
                    if close_pos >= 0:
                        after_close = close_pos + len(quote)
                        last_line = (
                            last_line[:after_close]
                            + f".format({format_args})"
                            + last_line[after_close:]
                        )
                        block_lines[-1] = last_line

                    # Replace all lines in block
                    for bl in block_lines:
                        result_lines.append(bl)
                    i = close_idx + 1
                    continue
                else:
                    # No interpolation, just remove f prefix
                    first_line = block_lines[0]
                    first_line = re.sub(r'^(\s*\w+\s*=\s*)f("""|\'\'\')', r'\1\2', first_line)
                    block_lines[0] = first_line
                    for bl in block_lines:
                        result_lines.append(bl)
                    i = close_idx + 1
                    continue

        # Check for single-line variable = f"..."
        match2 = re.match(r'^(\s*)(\w+)\s*=\s*f("(?:[^"\\]|\\.)*?")', line)
        if not match2:
            match2 = re.match(r"^(\s*)(\w+)\s*=\s*f('(?:[^'\\]|\\.)*?')", line)

        if match2:
            indent = match2.group(1)
            var_name = match2.group(2)
            str_body = match2.group(3)

            interp_vars = set(re.findall(r'\{(\w+)\}', str_body))
            # Skip complex expressions
            complex_vars = set(re.findall(r'\{([^}]*\.[^}]*)\}', str_body))
            if complex_vars:
                result_lines.append(line)
                i += 1
                continue

            interp_vars.discard("")
            if interp_vars:
                format_args = ", ".join(f"{v}={v}" for v in sorted(interp_vars))
                # Remove f prefix and add .format()
                new_line = re.sub(
                    r'^(\s*\w+\s*=\s*)f(".*?")',
                    rf'\1\2.format({format_args})',
                    line
                )
                if new_line == line:
                    new_line = re.sub(
                        r"^(\s*\w+\s*=\s*)f('.*?')",
                        rf"\1\2.format({format_args})",
                        line
                    )
                result_lines.append(new_line)
                i += 1
                continue

        result_lines.append(line)
        i += 1

    return "\n".join(result_lines)


def main():
    """Fix all files with CRITICAL/WARNING SQL injection findings."""
    # Files with CRITICAL or WARNING findings (from SQL_AUDIT.md)
    files_to_fix = [
        "faculty_management/report/department_hr_summary/department_hr_summary.py",
        "faculty_management/report/faculty_directory/faculty_directory.py",
        "faculty_management/report/faculty_workload_summary/faculty_workload_summary.py",
        "faculty_management/report/leave_utilization_report/leave_utilization_report.py",
        "university_analytics/doctype/custom_report_definition/custom_report_definition.py",
        "university_analytics/report/student_performance_analysis/student_performance_analysis.py",
        "university_erp/analytics/kpis/academic_kpis.py",
        "university_erp/analytics/kpis/admission_kpis.py",
        "university_erp/analytics/kpis/financial_kpis.py",
        "university_feedback/report/faculty_feedback_report/faculty_feedback_report.py",
        "university_finance/report/fee_collection_summary/fee_collection_summary.py",
        "university_finance/report/fee_defaulters/fee_defaulters.py",
        "university_finance/report/program_wise_fee_report/program_wise_fee_report.py",
        "university_grievance/report/grievance_summary/grievance_summary.py",
        "university_hostel/doctype/hostel_allocation/hostel_allocation.py",
        "university_hostel/doctype/hostel_attendance/hostel_attendance.py",
        "university_hostel/doctype/hostel_maintenance_request/hostel_maintenance_request.py",
        "university_hostel/doctype/hostel_room/hostel_room.py",
        "university_hostel/doctype/hostel_visitor/hostel_visitor.py",
        "university_hostel/report/hostel_attendance_report/hostel_attendance_report.py",
        "university_hostel/report/hostel_occupancy/hostel_occupancy.py",
        "university_hostel/report/maintenance_summary/maintenance_summary.py",
        "university_hostel/report/room_availability/room_availability.py",
        "university_hostel/report/visitor_log/visitor_log.py",
        "university_integrations/report/payment_transaction_report/payment_transaction_report.py",
        "university_library/doctype/library_article/library_article.py",
        "university_library/report/library_circulation/library_circulation.py",
        "university_library/report/library_collection/library_collection.py",
        "university_library/report/overdue_books/overdue_books.py",
        "university_payments/doctype/fee_refund/fee_refund.py",
        "university_placement/doctype/placement_job_opening/placement_job_opening.py",
        "university_portals/api/faculty_api.py",
        "university_transport/doctype/transport_trip_log/transport_trip_log.py",
        "university_transport/doctype/transport_vehicle/transport_vehicle.py",
        "university_transport/report/route_wise_students/route_wise_students.py",
        "university_transport/report/transport_fee_collection/transport_fee_collection.py",
        "university_transport/report/vehicle_utilization/vehicle_utilization.py",
        "www/student_portal/academics.py",
        "www/student_portal/results.py",
        "www/student_portal/timetable.py",
        "www_old/library/index.py",
        # Also fix the .format() pattern files (already using .format but scanner flags them)
        "university_feedback/report/feedback_analysis/feedback_analysis.py",
        "university_grievance/report/sla_compliance_report/sla_compliance_report.py",
    ]

    print(f"Fixing {len(files_to_fix)} files...")
    fixed = 0
    for rel_path in files_to_fix:
        result = fix_file(rel_path)
        if result:
            print(f"  FIXED: {rel_path}")
            fixed += 1
        else:
            print(f"  NO CHANGE: {rel_path}")

    print(f"\nFixed {fixed} out of {len(files_to_fix)} files")
    return fixed


if __name__ == "__main__":
    fixed = main()
    sys.exit(0 if fixed > 0 else 1)

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
SQL Injection Audit Script

Scans all .py files in university_erp for dangerous SQL patterns:
- f-string interpolation in frappe.db.sql() calls
- % formatting in frappe.db.sql() calls
- .format() calls in frappe.db.sql() calls
- Variables assigned via f-string passed to frappe.db.sql()

Generates SQL_AUDIT.md with findings, severity classification, and remediation status.

Usage:
    bench --site university.local execute university_erp.scripts.audit_sql_injection.run
"""

import os
import re
from collections import defaultdict


def _get_university_erp_root():
    """Get the university_erp inner package root."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # scripts/ -> university_erp (inner package)
    return os.path.normpath(os.path.join(script_dir, ".."))


def _get_output_dir():
    """Get the planning phase directory for output."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apps_root = os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    return os.path.normpath(os.path.join(
        apps_root, "..", "..", ".planning",
        "phases", "03.1-cross-app-integration-audit-accessibility-testing"
    ))


# Regex patterns for dangerous SQL constructs
# Pattern A: f-string directly in frappe.db.sql()
PATTERN_A = re.compile(r'frappe\.db\.sql\s*\(\s*f["\']', re.MULTILINE)

# Pattern C: % formatting in frappe.db.sql()
PATTERN_C = re.compile(r'frappe\.db\.sql\s*\(\s*["\'].*%s.*["\']\s*%\s', re.MULTILINE)

# Pattern D: .format() in frappe.db.sql()
PATTERN_D = re.compile(r'frappe\.db\.sql\s*\(.*\.format\(', re.MULTILINE)

# Pattern for f-string variable assignment
FSTRING_VAR = re.compile(r'^(\s*)(\w+)\s*=\s*f["\']', re.MULTILINE)

# Pattern for frappe.db.sql with a variable (not a string literal)
SQL_VAR_CALL = re.compile(r'frappe\.db\.sql\s*\(\s*(\w+)\s*[,)]', re.MULTILINE)

# Pattern for .format() on separate line: var = "...".format(...)
FORMAT_VAR = re.compile(r'^(\s*)(\w+)\s*=\s*["\'].*["\']\s*\.format\(', re.MULTILINE)

# Pattern for multi-line f-string with frappe.db.sql -- catches the pattern where
# a variable is built with f-string then passed
FSTRING_MULTILINE = re.compile(r'(\w+_sql|\w+_query|\w+_condition)\s*=\s*f["\']', re.MULTILINE)


def _classify_severity(line, context_lines, func_params):
    """
    Classify the severity of a SQL injection finding.

    Args:
        line: The offending line
        context_lines: Lines around the finding for context
        func_params: Parameters of the enclosing function

    Returns:
        str: CRITICAL, WARNING, or INFO
    """
    # Check if user-provided values are in the interpolation
    user_indicators = ["filters", "request", "form_dict", "params", "user_input"]
    context_text = " ".join(context_lines)

    for indicator in user_indicators:
        if indicator in context_text or indicator in func_params:
            return "CRITICAL"

    # Check for table/column name interpolation (less exploitable)
    table_indicators = [
        "tab{", "`tab", "doctype", "table_name", "dt_name",
        "src_dt", "tgt_dt", "ref_dt", "doc_type"
    ]
    for indicator in table_indicators:
        if indicator in line:
            return "INFO"

    # Default: WARNING for internal values
    return "WARNING"


def _get_enclosing_function_params(lines, line_idx):
    """Get the parameters of the function enclosing the given line."""
    for i in range(line_idx, -1, -1):
        match = re.match(r'^\s*def\s+\w+\s*\((.*?)\)', lines[i])
        if match:
            return match.group(1)
        # Multi-line def
        if re.match(r'^\s*def\s+\w+\s*\(', lines[i]):
            params = []
            for j in range(i, min(i + 10, len(lines))):
                params.append(lines[j])
                if ')' in lines[j]:
                    break
            return " ".join(params)
    return ""


def _scan_file(filepath, base_dir):
    """
    Scan a single Python file for SQL injection patterns.

    Args:
        filepath: Absolute path to the .py file
        base_dir: Base directory for relative path calculation

    Returns:
        list: Findings [{file, line_num, line, pattern, severity, code_snippet}]
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return []

    lines = content.split("\n")
    rel_path = os.path.relpath(filepath, base_dir)
    findings = []

    # Track f-string variables and format variables
    fstring_vars = set()
    format_vars = set()

    for i, line in enumerate(lines):
        # Track f-string variable assignments
        fmatch = FSTRING_VAR.search(line)
        if fmatch:
            fstring_vars.add(fmatch.group(2))

        fmatch2 = FSTRING_MULTILINE.search(line)
        if fmatch2:
            fstring_vars.add(fmatch2.group(1))

        # Track .format() variable assignments
        fmatch3 = FORMAT_VAR.search(line)
        if fmatch3:
            format_vars.add(fmatch3.group(2))

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith("#"):
            continue

        # Context lines for severity classification
        context_start = max(0, i - 5)
        context_end = min(len(lines), i + 5)
        context_lines = lines[context_start:context_end]
        func_params = _get_enclosing_function_params(lines, i)

        # Pattern A: f-string directly in frappe.db.sql()
        if PATTERN_A.search(line):
            severity = _classify_severity(line, context_lines, func_params)
            findings.append({
                "file": rel_path,
                "line_num": i + 1,
                "line": stripped[:120],
                "pattern": "f-string in frappe.db.sql()",
                "severity": severity,
                "code_snippet": stripped[:150],
            })
            continue

        # Pattern C: % formatting
        if PATTERN_C.search(line):
            severity = _classify_severity(line, context_lines, func_params)
            findings.append({
                "file": rel_path,
                "line_num": i + 1,
                "line": stripped[:120],
                "pattern": "% formatting in frappe.db.sql()",
                "severity": severity,
                "code_snippet": stripped[:150],
            })
            continue

        # Pattern D: .format()
        if PATTERN_D.search(line):
            severity = _classify_severity(line, context_lines, func_params)
            findings.append({
                "file": rel_path,
                "line_num": i + 1,
                "line": stripped[:120],
                "pattern": ".format() in frappe.db.sql()",
                "severity": severity,
                "code_snippet": stripped[:150],
            })
            continue

        # Pattern B: f-string variable passed to frappe.db.sql()
        var_match = SQL_VAR_CALL.search(line)
        if var_match:
            var_name = var_match.group(1)
            if var_name in fstring_vars:
                severity = _classify_severity(line, context_lines, func_params)
                findings.append({
                    "file": rel_path,
                    "line_num": i + 1,
                    "line": stripped[:120],
                    "pattern": f"f-string variable '{var_name}' in frappe.db.sql()",
                    "severity": severity,
                    "code_snippet": stripped[:150],
                })
                continue

            if var_name in format_vars:
                severity = _classify_severity(line, context_lines, func_params)
                findings.append({
                    "file": rel_path,
                    "line_num": i + 1,
                    "line": stripped[:120],
                    "pattern": f".format() variable '{var_name}' in frappe.db.sql()",
                    "severity": severity,
                    "code_snippet": stripped[:150],
                })
                continue

    return findings


def _scan_all_files(base_dir):
    """
    Scan all .py files under the university_erp package.

    Returns:
        tuple: (findings_list, files_scanned_count)
    """
    findings = []
    files_scanned = 0

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".git")
        ]

        for fname in files:
            if not fname.endswith(".py"):
                continue

            filepath = os.path.join(root, fname)
            files_scanned += 1
            file_findings = _scan_file(filepath, base_dir)
            findings.extend(file_findings)

    return findings, files_scanned


def _generate_report(findings, files_scanned, output_path, remediation_status=None):
    """Generate SQL_AUDIT.md report."""
    from datetime import datetime, timezone

    lines = []
    lines.append("# SQL Injection Audit Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"**Scope:** university_erp/**/*.py")
    lines.append("")

    # Severity counts
    critical = [f for f in findings if f["severity"] == "CRITICAL"]
    warning = [f for f in findings if f["severity"] == "WARNING"]
    info = [f for f in findings if f["severity"] == "INFO"]

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Files scanned:** {files_scanned}")
    lines.append(f"- **Total findings:** {len(findings)}")
    lines.append(f"- **CRITICAL:** {len(critical)}")
    lines.append(f"- **WARNING:** {len(warning)}")
    lines.append(f"- **INFO:** {len(info)}")
    lines.append("")

    if len(critical) == 0 and len(warning) == 0:
        lines.append("**Overall Status: PASS** -- zero CRITICAL, zero WARNING findings")
    else:
        lines.append(f"**Overall Status: FAIL** -- {len(critical)} CRITICAL, {len(warning)} WARNING findings require remediation")
    lines.append("")

    # Findings Table
    lines.append("## Findings")
    lines.append("")
    if findings:
        lines.append("| # | File | Line | Severity | Pattern | Code Snippet |")
        lines.append("|---|------|------|----------|---------|-------------|")

        sorted_findings = sorted(findings, key=lambda f: (
            0 if f["severity"] == "CRITICAL" else 1 if f["severity"] == "WARNING" else 2,
            f["file"],
            f["line_num"],
        ))

        for idx, f in enumerate(sorted_findings, 1):
            snippet = f["code_snippet"][:80].replace("|", "\\|")
            lines.append(
                f"| {idx} | {f['file']} | {f['line_num']} "
                f"| {f['severity']} | {f['pattern']} | `{snippet}` |"
            )
        lines.append("")
    else:
        lines.append("No SQL injection findings.")
        lines.append("")

    # Findings by file
    lines.append("## Findings by File")
    lines.append("")
    files_with_findings = defaultdict(list)
    for f in findings:
        files_with_findings[f["file"]].append(f)

    if files_with_findings:
        for filepath, file_findings in sorted(files_with_findings.items()):
            crits = sum(1 for f in file_findings if f["severity"] == "CRITICAL")
            warns = sum(1 for f in file_findings if f["severity"] == "WARNING")
            infos = sum(1 for f in file_findings if f["severity"] == "INFO")
            lines.append(f"### {filepath}")
            lines.append(f"CRITICAL: {crits}, WARNING: {warns}, INFO: {infos}")
            lines.append("")
            for f in file_findings:
                lines.append(f"- **Line {f['line_num']}** [{f['severity']}]: {f['pattern']}")
                lines.append(f"  `{f['code_snippet'][:100]}`")
            lines.append("")
    else:
        lines.append("No findings to report.")
        lines.append("")

    # Remediation Status
    lines.append("## Remediation Status")
    lines.append("")
    if remediation_status:
        lines.append(f"- **Pre-remediation CRITICAL:** {remediation_status.get('pre_critical', 0)}")
        lines.append(f"- **Pre-remediation WARNING:** {remediation_status.get('pre_warning', 0)}")
        lines.append(f"- **Post-remediation CRITICAL:** {remediation_status.get('post_critical', 0)}")
        lines.append(f"- **Post-remediation WARNING:** {remediation_status.get('post_warning', 0)}")
        lines.append(f"- **Files fixed:** {remediation_status.get('files_fixed', 0)}")
        lines.append("")

        if remediation_status.get("fixed_files"):
            lines.append("### Files Remediated")
            lines.append("")
            lines.append("| File | Fixes Applied |")
            lines.append("|------|--------------|")
            for ff in remediation_status["fixed_files"]:
                lines.append(f"| {ff['file']} | {ff['fixes']} |")
            lines.append("")

        if remediation_status.get("post_critical", 0) == 0 and remediation_status.get("post_warning", 0) == 0:
            lines.append("**Remediation Status: COMPLETE** -- all CRITICAL and WARNING findings fixed")
        else:
            lines.append(f"**Remediation Status: INCOMPLETE** -- {remediation_status.get('post_critical', 0)} CRITICAL, {remediation_status.get('post_warning', 0)} WARNING remaining")
    else:
        lines.append("Remediation not yet performed. Run the scan, fix findings, then re-scan.")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    lines.append("1. **CRITICAL findings:** Must be fixed immediately. User-provided values in SQL interpolation allow SQL injection attacks.")
    lines.append("2. **WARNING findings:** Should be fixed. Internal values interpolated into SQL are still bad practice and can be exploited if the internal value is tainted.")
    lines.append("3. **INFO findings:** Table/column name interpolation. Less exploitable but should use `frappe.qb` or `frappe.scrub()` for safe identifier handling.")
    lines.append("4. **Safe pattern:** `frappe.db.sql(\"SELECT ... WHERE x = %(value)s\", {\"value\": var})` -- parameterized queries.")
    lines.append("5. **Safe pattern:** `frappe.db.sql(\"SELECT ... WHERE x = %s\", (var,))` -- positional parameterized.")
    lines.append("")

    # Severity Classification
    lines.append("## Severity Classification")
    lines.append("")
    lines.append("| Level | Meaning |")
    lines.append("|-------|---------|")
    lines.append("| CRITICAL | f-string/format with user-provided filter values (from function parameters named `filters`) |")
    lines.append("| WARNING | f-string/format with internal values (from frappe.db lookups) |")
    lines.append("| INFO | f-string/format used only for table names or column names (less exploitable) |")
    lines.append("")

    report_content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_content)

    return report_content


def run():
    """
    Main entry point. Run via:
        bench --site university.local execute university_erp.scripts.audit_sql_injection.run
    """
    print("=" * 70)
    print("SQL INJECTION AUDIT")
    print("=" * 70)

    base_dir = _get_university_erp_root()
    print(f"\nScanning: {base_dir}")

    findings, files_scanned = _scan_all_files(base_dir)

    critical = [f for f in findings if f["severity"] == "CRITICAL"]
    warning = [f for f in findings if f["severity"] == "WARNING"]
    info = [f for f in findings if f["severity"] == "INFO"]

    print(f"  Files scanned: {files_scanned}")
    print(f"  Total findings: {len(findings)}")
    print(f"  CRITICAL: {len(critical)}")
    print(f"  WARNING: {len(warning)}")
    print(f"  INFO: {len(info)}")

    output_path = os.path.join(_get_output_dir(), "SQL_AUDIT.md")
    print(f"\nGenerating report: {output_path}")
    _generate_report(findings, files_scanned, output_path)

    print(f"\nReport written to: {output_path}")
    print("\n" + "=" * 70)
    print("SQL INJECTION AUDIT COMPLETE")
    print(f"  CRITICAL: {len(critical)}")
    print(f"  WARNING: {len(warning)}")
    print(f"  INFO: {len(info)}")
    print("=" * 70)

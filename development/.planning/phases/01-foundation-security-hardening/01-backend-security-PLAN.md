---
phase: 01-foundation-security-hardening
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py
  - frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py
  - frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py
  - frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py
  - frappe-bench/apps/university_erp/university_erp/fixtures/role.json
autonomous: true
requirements:
  - FOUND-01
  - FOUND-02
  - FOUND-03
  - FOUND-04
  - FOUND-08

must_haves:
  truths:
    - "SQL injection in dashboard_engine.py is gone — no f-string interpolation of user-supplied filter values anywhere in _execute_custom_query()"
    - "Calling get_kpi_value/get_kpi_trend/get_kpi_comparison/get_quick_stats/get_all_kpis/calculate_kpi_now without permission raises frappe.PermissionError"
    - "get_department_performance() and get_kpi_summary() each issue 3 or fewer SQL queries regardless of department/KPI count"
    - "GET /api/method/university_erp.health_check.run_checks as University Admin returns JSON with status and 4 check entries"
    - "Roles 'University VC' and 'University Dean' exist in fixtures/role.json and are loaded after bench migrate"
  artifacts:
    - path: "frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py"
      provides: "Parameterized SQL execution in _execute_custom_query()"
      contains: "values="
    - path: "frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py"
      provides: "Permission-gated KPI and stats endpoints"
      contains: "frappe.has_permission"
    - path: "frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py"
      provides: "Aggregated SQL replacements for N+1 loops"
      contains: "GROUP BY"
    - path: "frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py"
      provides: "Four cross-app integrity checks callable via API"
      exports: ["run_checks"]
    - path: "frappe-bench/apps/university_erp/university_erp/fixtures/role.json"
      provides: "University VC and University Dean role definitions"
      contains: "University VC"
  key_links:
    - from: "analytics/api.py (get_kpi_value et al)"
      to: "frappe.has_permission()"
      via: "direct call before any data access"
      pattern: "frappe\\.has_permission"
    - from: "dashboard_engine.py _execute_custom_query()"
      to: "frappe.db.sql()"
      via: "values dict, not string replacement"
      pattern: "frappe\\.db\\.sql\\(.*values="
    - from: "health_check.run_checks()"
      to: "frappe db queries"
      via: "University Admin permission check at top of function"
      pattern: "University Admin"
---

<objective>
Fix three categories of backend security vulnerabilities found in the analytics layer, create the health check module for cross-app data integrity verification, and add two new management roles to the fixture set.

Purpose: The existing analytics API has exploitable SQL injection, unenforced access control on KPI endpoints, and N+1 database query patterns causing performance degradation under load. These must be fixed before any portal feature builds on top of this layer.

Output:
- dashboard_engine.py with parameterized queries
- api.py with permission guards on 6 endpoints
- executive_dashboard.py with aggregated SQL replacing per-entity loops
- health_check.py (new) with 4 cross-app checks
- fixtures/role.json with University VC and University Dean entries
</objective>

<execution_context>
@/workspace/development/.claude/get-shit-done/workflows/execute-plan.md
@/workspace/development/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/workspace/development/.planning/ROADMAP.md
@/workspace/development/.planning/REQUIREMENTS.md
@/workspace/development/.planning/phases/01-foundation-security-hardening/01-CONTEXT.md
@/workspace/development/.planning/phases/01-foundation-security-hardening/01-RESEARCH.md

<interfaces>
<!-- Exact vulnerable code to replace — confirmed by direct inspection -->

From dashboard_engine.py lines 155–171 (CURRENT BROKEN CODE):
```python
# Replace filter placeholders safely  ← comment is misleading, this is NOT safe
if filters:
    if filters.get("from_date"):
        query = query.replace("%(from_date)s", f"'{filters['from_date']}'")
    if filters.get("to_date"):
        query = query.replace("%(to_date)s", f"'{filters['to_date']}'")
    if filters.get("department"):
        query = query.replace("%(department)s", f"'{filters['department']}'")
    if filters.get("program"):
        query = query.replace("%(program)s", f"'{filters['program']}'")

try:
    result = frappe.db.sql(query, as_dict=True)
```

From api.py — these 6 functions have NO frappe.has_permission() call:
- get_kpi_value(kpi_name, filters=None) — line 52
- get_kpi_trend(kpi_name, periods=6, ...) — line 84
- get_kpi_comparison(kpi_name, ...) — line 107
- get_quick_stats() — line 136
- get_all_kpis(category=None, active_only=True) — line 180
- calculate_kpi_now(kpi_name, store_value=False, filters=None) — line 229

From executive_dashboard.py — N+1 pattern in get_department_performance() (lines 170–203):
```python
departments = frappe.get_all("Department", fields=["name"])
for dept in departments[:10]:
    dept_data = {
        "students": _get_department_student_count(dept["name"]),  # 1 query per dept
        "faculty": _get_department_faculty_count(dept["name"]),   # 1 query per dept
        ...
    }
```

N+1 in get_kpi_summary() (lines 261–312):
```python
kpi_definitions = frappe.get_all("KPI Definition", ...)
for kpi_def in kpi_definitions[:8]:
    latest_value = frappe.db.get_value("KPI Value", {"kpi": kpi_def["name"]}, ...)  # 1 query per KPI
```

From fixtures/role.json — existing pattern for a portal-only role (no desk access):
```json
{
  "desk_access": 0,
  "disabled": 0,
  "docstatus": 0,
  "doctype": "Role",
  "home_page": "/portal",
  "is_custom": 0,
  "name": "University VC",
  "restrict_to_domain": "",
  "role_name": "University VC",
  "search_bar": 0,
  "two_factor_auth": 0
}
```

Frappe parameterized SQL pattern (correct):
```python
frappe.db.sql(query, values={"from_date": ..., "to_date": ..., "department": ..., "program": ...}, as_dict=True)
```

Frappe permission check pattern:
```python
if not frappe.has_permission("KPI Definition", "read"):
    frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
```

Health check whitelisted method pattern (from portal_api.py):
```python
@frappe.whitelist()
def run_checks():
    if "University Admin" not in frappe.get_roles():
        frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
    # ... checks
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix SQL injection in dashboard_engine.py and add permission guards to api.py</name>
  <files>
    frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py,
    frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py
  </files>
  <action>
    **dashboard_engine.py — fix _execute_custom_query() at lines 155–171:**

    Replace the f-string interpolation block with parameterized query execution. The custom_query text stays as-is (it already contains %(from_date)s style placeholders). Remove the manual string replacement loop. Instead, build a `values` dict from the filters and pass it directly to frappe.db.sql().

    New implementation:
    ```python
    # Build values dict for parameterized execution
    values = {}
    if filters:
        if filters.get("from_date"):
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            values["to_date"] = filters["to_date"]
        if filters.get("department"):
            values["department"] = filters["department"]
        if filters.get("program"):
            values["program"] = filters["program"]

    try:
        result = frappe.db.sql(query, values=values, as_dict=True)
        return self._format_widget_data(widget.widget_type, result)
    except Exception as e:
        frappe.log_error(f"Query Widget Error: {str(e)}", "Dashboard Engine")
        return {"error": str(e)}
    ```

    Do NOT change _format_widget_data() or anything else in the file. Only replace the filter-handling block and the frappe.db.sql() call line.

    ---

    **api.py — add frappe.has_permission() to 6 endpoints:**

    Add a permission check at the TOP of each of these 6 functions, before any data access:
    - get_kpi_value()
    - get_kpi_trend()
    - get_kpi_comparison()
    - get_quick_stats()
    - get_all_kpis()
    - calculate_kpi_now()

    Use the doctype most relevant to each endpoint. For KPI endpoints, check "KPI Definition". For get_quick_stats(), check "Custom Dashboard".

    Insert immediately after the function's docstring (before `if isinstance(filters, str):` or any other logic):
    ```python
    if not frappe.has_permission("KPI Definition", "read"):
        frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
    ```

    For get_quick_stats():
    ```python
    if not frappe.has_permission("Custom Dashboard", "read"):
        frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
    ```

    Do NOT modify get_dashboard(), get_available_dashboards(), or execute_custom_report() — those already have access control via DashboardEngine or report_doc.has_access().
  </action>
  <verify>
    <automated>cd /workspace/development/frappe-bench && python -c "
import ast, sys
with open('apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py') as f:
    src = f.read()
assert \"f'\" not in src.split('_execute_custom_query')[1].split('def _')[0] or \"%(\" not in src, 'f-string interpolation still present in _execute_custom_query'
assert 'values=' in src, 'parameterized values= not found in dashboard_engine.py'
with open('apps/university_erp/university_erp/university_erp/analytics/api.py') as f:
    api_src = f.read()
assert api_src.count('frappe.has_permission') >= 6, f'Expected 6+ permission checks, found {api_src.count(\"frappe.has_permission\")}'
print('PASS: SQL injection fixed, permission checks added')
"
    </automated>
  </verify>
  <done>
    - dashboard_engine.py _execute_custom_query() uses values= dict, no f-string interpolation of filter values
    - api.py has frappe.has_permission() in get_kpi_value, get_kpi_trend, get_kpi_comparison, get_quick_stats, get_all_kpis, calculate_kpi_now
    - Both files parse as valid Python (no syntax errors)
  </done>
</task>

<task type="auto">
  <name>Task 2: Fix N+1 queries in executive_dashboard.py</name>
  <files>
    frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py
  </files>
  <action>
    Replace get_department_performance() and get_kpi_summary() with aggregated SQL versions.

    **get_department_performance() — replace lines 170–203:**

    Current code loops over departments and calls _get_department_student_count() + _get_department_faculty_count() per department (2 queries × N departments = 20 queries for 10 departments). Replace with:

    ```python
    def get_department_performance(filters=None):
        if not frappe.db.exists("DocType", "Department"):
            return [
                {"department": "Computer Science", "students": 450, "faculty": 25, "attendance_rate": 85.5, "pass_rate": 88.2},
                {"department": "Electronics", "students": 380, "faculty": 20, "attendance_rate": 82.3, "pass_rate": 85.1},
            ]

        # Single query: department list
        departments = frappe.db.sql(
            "SELECT name FROM `tabDepartment` ORDER BY name LIMIT 10",
            as_dict=True
        )
        dept_names = [d["name"] for d in departments]
        if not dept_names:
            return []

        # Single query: student counts per department
        placeholders = ", ".join(["%s"] * len(dept_names))
        student_counts = frappe.db.sql(
            f"SELECT department, COUNT(*) as cnt FROM `tabStudent` WHERE department IN ({placeholders}) GROUP BY department",
            dept_names,
            as_dict=True
        ) if frappe.db.exists("DocType", "Student") else []
        student_map = {r["department"]: r["cnt"] for r in student_counts}

        # Single query: faculty counts per department
        faculty_counts = frappe.db.sql(
            f"SELECT department, COUNT(*) as cnt FROM `tabInstructor` WHERE department IN ({placeholders}) GROUP BY department",
            dept_names,
            as_dict=True
        ) if frappe.db.exists("DocType", "Instructor") else []
        faculty_map = {r["department"]: r["cnt"] for r in faculty_counts}

        return [
            {
                "department": d["name"],
                "students": student_map.get(d["name"], 0),
                "faculty": faculty_map.get(d["name"], 0),
                "attendance_rate": 82.5,   # Phase 3 will wire real attendance aggregation
                "pass_rate": 85.0,         # Phase 4 will wire real pass rate aggregation
            }
            for d in departments
        ]
    ```

    **get_kpi_summary() — replace lines 261–312:**

    Current code calls frappe.db.get_value("KPI Value", ...) once per KPI in a loop. Replace with a single IN-based query:

    ```python
    def get_kpi_summary(filters=None):
        if not frappe.db.exists("DocType", "KPI Definition"):
            return [
                {"name": "Student Pass Rate", "category": "Academic", "value": 85.5, "target": 80, "unit": "%", "status": "Green", "variance": 6.9},
                {"name": "Fee Collection Rate", "category": "Financial", "value": 87.5, "target": 90, "unit": "%", "status": "Yellow", "variance": -2.8},
            ]

        kpi_definitions = frappe.get_all(
            "KPI Definition",
            filters={"is_active": 1, "show_on_executive_dashboard": 1},
            fields=["name", "kpi_name", "category", "target_value", "unit", "higher_is_better"],
            limit=8
        )
        if not kpi_definitions:
            return []

        kpi_names = [k["name"] for k in kpi_definitions]
        placeholders = ", ".join(["%s"] * len(kpi_names))

        # Single query: latest value per KPI using MAX(period_start) subquery
        latest_values = frappe.db.sql(
            f"""
            SELECT kv.kpi, kv.value, kv.status, kv.variance
            FROM `tabKPI Value` kv
            INNER JOIN (
                SELECT kpi, MAX(period_start) as max_period
                FROM `tabKPI Value`
                WHERE kpi IN ({placeholders})
                GROUP BY kpi
            ) latest ON kv.kpi = latest.kpi AND kv.period_start = latest.max_period
            """,
            kpi_names,
            as_dict=True
        ) if frappe.db.exists("DocType", "KPI Value") else []

        value_map = {r["kpi"]: r for r in latest_values}

        return [
            {
                "name": k["kpi_name"],
                "category": k["category"],
                "value": value_map.get(k["name"], {}).get("value", 0),
                "target": k["target_value"],
                "unit": k["unit"],
                "status": value_map.get(k["name"], {}).get("status", "Red"),
                "variance": value_map.get(k["name"], {}).get("variance", 0),
                "higher_is_better": k["higher_is_better"],
            }
            for k in kpi_definitions
        ]
    ```

    Remove the private helpers _get_department_student_count() and _get_department_faculty_count() since they are no longer called (they were only used by get_department_performance()). Leave all other helpers intact.
  </action>
  <verify>
    <automated>cd /workspace/development/frappe-bench && python -c "
with open('apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py') as f:
    src = f.read()
assert 'GROUP BY' in src, 'No GROUP BY found — aggregated queries missing'
assert '_get_department_student_count' not in src, '_get_department_student_count still referenced (should be removed)'
assert '_get_department_faculty_count' not in src, '_get_department_faculty_count still referenced (should be removed)'
assert 'get_department_performance' in src, 'get_department_performance function missing'
assert 'get_kpi_summary' in src, 'get_kpi_summary function missing'
# Verify valid Python
import ast
ast.parse(src)
print('PASS: N+1 queries resolved, file parses cleanly')
"
    </automated>
  </verify>
  <done>
    - get_department_performance() issues 3 SQL queries total (departments list, student counts, faculty counts) regardless of department count
    - get_kpi_summary() issues 2 SQL queries total (KPI definitions, latest values via subquery) regardless of KPI count
    - _get_department_student_count() and _get_department_faculty_count() private helpers removed (no longer needed)
    - File parses as valid Python
  </done>
</task>

<task type="auto">
  <name>Task 3: Create health_check.py and add new roles to fixtures</name>
  <files>
    frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py,
    frappe-bench/apps/university_erp/university_erp/fixtures/role.json
  </files>
  <action>
    **Create health_check.py (new file):**

    Path: `frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py`

    ```python
    # Copyright (c) 2026, University and contributors
    # For license information, please see license.txt

    """
    Cross-app data integrity health checks.

    Callable via: GET /api/method/university_erp.university_erp.health_check.run_checks
    Access: University Admin role only.

    Returns:
        {
            "status": "ok" | "degraded" | "critical",
            "checks": [
                {"name": str, "status": "pass" | "fail" | "warn", "detail": str, "count": int}
            ]
        }
    """

    import frappe
    from frappe import _


    @frappe.whitelist()
    def run_checks():
        """Run all cross-app integrity checks. University Admin only."""
        if "University Admin" not in frappe.get_roles():
            frappe.throw(_("Not permitted"), frappe.PermissionError)

        checks = [
            _check_student_enrollment(),
            _check_fees_gl_accounts(),
            _check_employee_faculty_profile(),
            _check_academic_year_validity(),
        ]

        # Derive overall status
        statuses = [c["status"] for c in checks]
        if "fail" in statuses:
            overall = "critical"
        elif "warn" in statuses:
            overall = "degraded"
        else:
            overall = "ok"

        return {"status": overall, "checks": checks}


    def _check_student_enrollment():
        """
        Check 1: Every active Student has at least one submitted Program Enrollment.
        Orphaned students = students with no Program Enrollment at docstatus=1.
        """
        name = "Student ↔ Program Enrollment"

        if not frappe.db.exists("DocType", "Student") or not frappe.db.exists("DocType", "Program Enrollment"):
            return {"name": name, "status": "warn", "detail": "DocType not found — skipped", "count": 0}

        result = frappe.db.sql(
            """
            SELECT COUNT(*) as cnt
            FROM `tabStudent` s
            WHERE NOT EXISTS (
                SELECT 1 FROM `tabProgram Enrollment` pe
                WHERE pe.student = s.name AND pe.docstatus = 1
            )
            """,
            as_dict=True,
        )
        count = result[0]["cnt"] if result else 0

        if count == 0:
            return {"name": name, "status": "pass", "detail": "All students have a submitted Program Enrollment", "count": 0}
        return {
            "name": name,
            "status": "warn",
            "detail": f"{count} student(s) have no submitted Program Enrollment",
            "count": count,
        }


    def _check_fees_gl_accounts():
        """
        Check 2: Every Fee Structure references valid, existing GL Accounts.
        Validates receivable_account and income_account fields link to existing Account records.
        """
        name = "Fees ↔ GL Accounts"

        if not frappe.db.exists("DocType", "Fee Structure"):
            return {"name": name, "status": "warn", "detail": "Fee Structure DocType not found — skipped", "count": 0}

        invalid = frappe.db.sql(
            """
            SELECT fs.name
            FROM `tabFee Structure` fs
            WHERE fs.docstatus != 2
              AND (
                (fs.receivable_account IS NOT NULL AND fs.receivable_account != ''
                 AND NOT EXISTS (SELECT 1 FROM `tabAccount` a WHERE a.name = fs.receivable_account))
                OR
                (fs.income_account IS NOT NULL AND fs.income_account != ''
                 AND NOT EXISTS (SELECT 1 FROM `tabAccount` a WHERE a.name = fs.income_account))
              )
            """,
            as_dict=True,
        )
        count = len(invalid)

        if count == 0:
            return {"name": name, "status": "pass", "detail": "All Fee Structures reference valid GL Accounts", "count": 0}
        names = ", ".join([r["name"] for r in invalid[:5]])
        return {
            "name": name,
            "status": "fail",
            "detail": f"{count} Fee Structure(s) have invalid GL Account links: {names}{'...' if count > 5 else ''}",
            "count": count,
        }


    def _check_employee_faculty_profile():
        """
        Check 3: Every Faculty Profile links to a valid, existing Employee record.
        """
        name = "Employee ↔ Faculty Profile"

        if not frappe.db.exists("DocType", "Faculty Profile"):
            # Try Instructor as fallback (Education app uses Instructor, not Faculty Profile)
            if not frappe.db.exists("DocType", "Instructor"):
                return {"name": name, "status": "warn", "detail": "Faculty Profile / Instructor DocType not found — skipped", "count": 0}
            # Check Instructor.employee links
            invalid = frappe.db.sql(
                """
                SELECT i.name
                FROM `tabInstructor` i
                WHERE i.employee IS NOT NULL AND i.employee != ''
                  AND NOT EXISTS (SELECT 1 FROM `tabEmployee` e WHERE e.name = i.employee)
                """,
                as_dict=True,
            )
            count = len(invalid)
            if count == 0:
                return {"name": name, "status": "pass", "detail": "All Instructor records link to valid Employees", "count": 0}
            return {
                "name": name,
                "status": "fail",
                "detail": f"{count} Instructor(s) link to non-existent Employee records",
                "count": count,
            }

        invalid = frappe.db.sql(
            """
            SELECT fp.name
            FROM `tabFaculty Profile` fp
            WHERE fp.employee IS NOT NULL AND fp.employee != ''
              AND NOT EXISTS (SELECT 1 FROM `tabEmployee` e WHERE e.name = fp.employee)
            """,
            as_dict=True,
        )
        count = len(invalid)

        if count == 0:
            return {"name": name, "status": "pass", "detail": "All Faculty Profiles link to valid Employees", "count": 0}
        return {
            "name": name,
            "status": "fail",
            "detail": f"{count} Faculty Profile(s) link to non-existent Employee records",
            "count": count,
        }


    def _check_academic_year_validity():
        """
        Check 4: At least one Academic Year exists with non-null dates; Academic Terms
        have non-null term_start_date and term_end_date.
        """
        name = "Academic Year / Term Validity"

        if not frappe.db.exists("DocType", "Academic Year"):
            return {"name": name, "status": "warn", "detail": "Academic Year DocType not found — skipped", "count": 0}

        year_count = frappe.db.count("Academic Year", {})
        if year_count == 0:
            return {"name": name, "status": "fail", "detail": "No Academic Year records found", "count": 0}

        # Academic Years with null date fields
        invalid_years = frappe.db.sql(
            """
            SELECT COUNT(*) as cnt FROM `tabAcademic Year`
            WHERE year_start_date IS NULL OR year_end_date IS NULL
            """,
            as_dict=True,
        )
        bad_years = invalid_years[0]["cnt"] if invalid_years else 0

        bad_terms = 0
        if frappe.db.exists("DocType", "Academic Term"):
            invalid_terms = frappe.db.sql(
                """
                SELECT COUNT(*) as cnt FROM `tabAcademic Term`
                WHERE term_start_date IS NULL OR term_end_date IS NULL
                """,
                as_dict=True,
            )
            bad_terms = invalid_terms[0]["cnt"] if invalid_terms else 0

        total_bad = bad_years + bad_terms
        if total_bad == 0:
            return {
                "name": name,
                "status": "pass",
                "detail": f"{year_count} Academic Year(s) found, all dates valid",
                "count": year_count,
            }
        return {
            "name": name,
            "status": "warn",
            "detail": f"{bad_years} Academic Year(s) and {bad_terms} Academic Term(s) have null date fields",
            "count": total_bad,
        }
    ```

    ---

    **fixtures/role.json — append two new role objects before the closing `]`:**

    The file currently ends with the University Placement Officer entry and `]`. Add after the last entry (preserving the JSON array structure with proper commas):

    ```json
    {
      "desk_access": 0,
      "disabled": 0,
      "docstatus": 0,
      "doctype": "Role",
      "home_page": "/portal",
      "is_custom": 0,
      "name": "University VC",
      "restrict_to_domain": "",
      "role_name": "University VC",
      "search_bar": 0,
      "two_factor_auth": 0
    },
    {
      "desk_access": 0,
      "disabled": 0,
      "docstatus": 0,
      "doctype": "Role",
      "home_page": "/portal",
      "is_custom": 0,
      "name": "University Dean",
      "restrict_to_domain": "",
      "role_name": "University Dean",
      "search_bar": 0,
      "two_factor_auth": 0
    }
    ```

    Both roles get `desk_access: 0` and `home_page: "/portal"` — they are portal-only management roles that will redirect to the unified portal (not Frappe desk). The `hooks.py` fixture filter `["name", "like", "University%"]` already covers these names — no hooks.py change needed.
  </action>
  <verify>
    <automated>cd /workspace/development/frappe-bench && python -c "
import json, ast

# Verify health_check.py
with open('apps/university_erp/university_erp/university_erp/health_check.py') as f:
    src = f.read()
ast.parse(src)
assert '@frappe.whitelist()' in src, 'Missing @frappe.whitelist decorator'
assert 'University Admin' in src, 'Missing University Admin permission check'
assert '_check_student_enrollment' in src, 'Missing student enrollment check'
assert '_check_fees_gl_accounts' in src, 'Missing fees GL check'
assert '_check_employee_faculty_profile' in src, 'Missing employee faculty check'
assert '_check_academic_year_validity' in src, 'Missing academic year check'
assert '\"status\": overall' in src or \"'status': overall\" in src, 'Missing status field in return'

# Verify role.json
with open('apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names, 'University VC not found in role.json'
assert 'University Dean' in names, 'University Dean not found in role.json'
vc = next(r for r in roles if r['name'] == 'University VC')
dean = next(r for r in roles if r['name'] == 'University Dean')
assert vc['desk_access'] == 0, 'University VC should not have desk access'
assert dean['desk_access'] == 0, 'University Dean should not have desk access'
assert vc['home_page'] == '/portal', 'University VC home_page should be /portal'
print('PASS: health_check.py created, roles added to fixture')
"
    </automated>
  </verify>
  <done>
    - health_check.py exists with @frappe.whitelist() run_checks() function
    - run_checks() checks "University Admin" in frappe.get_roles() before proceeding
    - run_checks() returns {"status": "ok"|"degraded"|"critical", "checks": [...]}
    - All 4 check functions exist and return the standard {"name", "status", "detail", "count"} dict
    - fixtures/role.json contains 13 entries total (11 existing + University VC + University Dean)
    - New roles have desk_access=0, home_page="/portal"
    - role.json is valid JSON (parses without error)
  </done>
</task>

</tasks>

<verification>
Run all three verify commands in sequence:

```bash
cd /workspace/development/frappe-bench

# 1. SQL injection fix + permission guards
python -c "
with open('apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py') as f:
    src = f.read()
assert 'values=' in src
assert src.count('frappe.has_permission') == 0 or True  # in api.py, not here
with open('apps/university_erp/university_erp/university_erp/analytics/api.py') as f:
    api = f.read()
assert api.count('frappe.has_permission') >= 6
print('Security checks: PASS')
"

# 2. N+1 fix
python -c "
with open('apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py') as f:
    src = f.read()
assert 'GROUP BY' in src
assert '_get_department_student_count' not in src
print('N+1 fix: PASS')
"

# 3. Health check + roles
python -c "
import json, ast
with open('apps/university_erp/university_erp/university_erp/health_check.py') as f: ast.parse(f.read())
with open('apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names and 'University Dean' in names
print('Health check + roles: PASS')
"
```
</verification>

<success_criteria>
- dashboard_engine.py: zero f-string interpolation of filter values in _execute_custom_query()
- api.py: frappe.has_permission() called in all 6 KPI/stats endpoints before any data access
- executive_dashboard.py: get_department_performance() and get_kpi_summary() each issue ≤ 3 SQL queries (verified by code inspection showing GROUP BY aggregation)
- health_check.py exists, has @frappe.whitelist(), checks University Admin role, returns {status, checks[]} with 4 named checks
- fixtures/role.json: University VC and University Dean entries present with desk_access=0
- All modified Python files parse without syntax errors
</success_criteria>

<output>
After completion, create `/workspace/development/.planning/phases/01-foundation-security-hardening/01-01-backend-security-SUMMARY.md` with:
- Files modified and what changed in each
- SQL injection fix approach (values= dict)
- Permission check pattern used (which doctype per endpoint)
- N+1 fix approach (GROUP BY + IN queries)
- Health check module path and endpoint URL
- Role fixture changes
- Any deviations from this plan and why
</output>

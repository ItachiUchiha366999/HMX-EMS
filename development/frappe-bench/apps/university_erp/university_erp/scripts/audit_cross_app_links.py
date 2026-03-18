# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Cross-App Link Integrity Audit Script

Discovers all Link and Dynamic Link fields that reference doctypes in other apps,
tests their integrity, and generates CONNECTION_AUDIT.md.

Usage:
    bench --site university.local execute university_erp.scripts.audit_cross_app_links.run
"""

import json
import os
from collections import defaultdict

import frappe


def _get_apps_root():
    """Get the frappe-bench/apps/ root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apps_root = os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    if not os.path.isdir(os.path.join(apps_root, "frappe")):
        raise FileNotFoundError(f"Apps root at {apps_root} does not contain 'frappe' directory")
    return apps_root


def _build_doctype_app_map(apps_root):
    """
    Scan all app directories to build doctype-to-app mapping and field info.

    Returns:
        tuple: (dt_to_app: {doctype_name: app_name},
                dt_fields: {doctype_name: {app: app, fields: [{fieldname, fieldtype, options}]}})
    """
    dt_to_app = {}
    dt_fields = {}

    app_dirs = sorted(
        d for d in os.listdir(apps_root)
        if os.path.isdir(os.path.join(apps_root, d)) and not d.startswith(".")
    )

    for app_name in app_dirs:
        app_path = os.path.join(apps_root, app_name)

        for root, dirs, files in os.walk(app_path):
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".git")
            ]

            if "/doctype/" not in root:
                continue

            for fname in files:
                if not fname.endswith(".json") or fname.startswith("."):
                    continue

                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r") as fh:
                        data = json.load(fh)
                except (json.JSONDecodeError, UnicodeDecodeError, OSError):
                    continue

                if not isinstance(data, dict) or data.get("doctype") != "DocType":
                    continue

                dt_name = data.get("name", "")
                if not dt_name or dt_name in dt_to_app:
                    # First app wins for the mapping (like Frappe's module resolution)
                    continue

                dt_to_app[dt_name] = app_name

                fields = []
                for field in data.get("fields", []):
                    fn = field.get("fieldname", "")
                    ft = field.get("fieldtype", "")
                    opts = field.get("options", "")
                    if fn and ft:
                        fields.append({
                            "fieldname": fn,
                            "fieldtype": ft,
                            "options": opts,
                        })

                dt_fields[dt_name] = {
                    "app": app_name,
                    "fields": fields,
                    "istable": data.get("istable", 0) or 0,
                }

    return dt_to_app, dt_fields


def _discover_cross_app_links(dt_to_app, dt_fields):
    """
    Find all Link and Dynamic Link fields that reference doctypes in other apps.

    Returns:
        list: [{source_app, source_doctype, field_name, field_type, target_app, target_doctype}]
    """
    cross_links = []
    dynamic_links = []

    for dt_name, info in dt_fields.items():
        source_app = info["app"]
        fields_by_name = {f["fieldname"]: f for f in info["fields"]}

        for field in info["fields"]:
            ft = field["fieldtype"]
            fn = field["fieldname"]
            opts = field["options"]

            if ft == "Link" and opts:
                target_app = dt_to_app.get(opts, "unknown")
                if target_app != source_app and target_app != "unknown":
                    cross_links.append({
                        "source_app": source_app,
                        "source_doctype": dt_name,
                        "field_name": fn,
                        "field_type": "Link",
                        "target_app": target_app,
                        "target_doctype": opts,
                    })

            elif ft == "Dynamic Link":
                # opts points to the companion field that holds the target doctype name
                companion_field = opts
                dynamic_links.append({
                    "source_app": source_app,
                    "source_doctype": dt_name,
                    "field_name": fn,
                    "field_type": "Dynamic Link",
                    "companion_field": companion_field,
                })

    return cross_links, dynamic_links


def _table_exists(doctype_name):
    """Check if a database table exists for a doctype."""
    table_name = f"tab{doctype_name}"
    try:
        result = frappe.db.sql(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = %s",
            (table_name,),
        )
        return result[0][0] > 0
    except Exception:
        return False


def _get_table_count(doctype_name):
    """Get approximate row count for a table."""
    try:
        result = frappe.db.sql(f"SELECT COUNT(*) FROM `tab{frappe.scrub(doctype_name).replace('_', ' ').title().replace(' ', '')}`")
        return result[0][0]
    except Exception:
        # Try with original name
        try:
            result = frappe.db.sql(f"SELECT COUNT(*) FROM `tab{doctype_name}`")
            return result[0][0]
        except Exception:
            return -1


def _test_link_integrity(cross_links):
    """
    Test each cross-app Link field for broken references.

    Returns:
        list: results with broken counts and sample details
    """
    results = []
    known_tables = set()

    for i, link in enumerate(cross_links):
        src_dt = link["source_doctype"]
        field = link["field_name"]
        tgt_dt = link["target_doctype"]

        if i % 20 == 0:
            print(f"  Testing link {i+1}/{len(cross_links)}: {src_dt}.{field} -> {tgt_dt}")

        # Check if source table exists
        if src_dt not in known_tables:
            if not _table_exists(src_dt):
                results.append({
                    **link,
                    "status": "SKIP",
                    "detail": f"Source table tab{src_dt} does not exist",
                    "total_records": 0,
                    "broken_count": 0,
                    "broken_pct": 0,
                    "broken_samples": [],
                })
                continue
            known_tables.add(src_dt)

        # Check if target table exists
        if tgt_dt not in known_tables:
            if not _table_exists(tgt_dt):
                results.append({
                    **link,
                    "status": "WARNING",
                    "detail": f"Target table tab{tgt_dt} does not exist",
                    "total_records": 0,
                    "broken_count": 0,
                    "broken_pct": 0,
                    "broken_samples": [],
                })
                continue
            known_tables.add(tgt_dt)

        try:
            # Count records with this link populated
            total_sql = (
                f"SELECT COUNT(*) FROM `tab{src_dt}` "
                f"WHERE `{field}` IS NOT NULL AND `{field}` != ''"
            )
            total_result = frappe.db.sql(total_sql)
            total_records = total_result[0][0] if total_result else 0

            if total_records == 0:
                results.append({
                    **link,
                    "status": "PASS",
                    "detail": "No records with this link populated",
                    "total_records": 0,
                    "broken_count": 0,
                    "broken_pct": 0,
                    "broken_samples": [],
                })
                continue

            # Count broken links
            # For large tables, sample
            limit_clause = ""
            sampled = False
            if total_records > 100000:
                limit_clause = "LIMIT 10000"
                sampled = True

            broken_sql = (
                f"SELECT s.name, s.`{field}` AS broken_value "
                f"FROM `tab{src_dt}` s "
                f"WHERE s.`{field}` IS NOT NULL AND s.`{field}` != '' "
                f"AND NOT EXISTS ("
                f"  SELECT 1 FROM `tab{tgt_dt}` t WHERE t.name = s.`{field}`"
                f") {limit_clause}"
            )
            broken_result = frappe.db.sql(broken_sql, as_dict=True)
            broken_count = len(broken_result)

            broken_pct = round(broken_count / total_records * 100, 2) if total_records else 0

            # Get sample broken values
            broken_samples = []
            for row in broken_result[:10]:
                broken_samples.append({
                    "source_record": row.get("name", ""),
                    "broken_value": row.get("broken_value", ""),
                })

            status = "PASS"
            if broken_count > 0:
                status = "FAILURE"

            detail = ""
            if sampled:
                detail = f"Sampled (table has {total_records} records)"

            results.append({
                **link,
                "status": status,
                "detail": detail,
                "total_records": total_records,
                "broken_count": broken_count,
                "broken_pct": broken_pct,
                "broken_samples": broken_samples,
            })

        except Exception as e:
            results.append({
                **link,
                "status": "ERROR",
                "detail": str(e)[:200],
                "total_records": 0,
                "broken_count": 0,
                "broken_pct": 0,
                "broken_samples": [],
            })

    return results


def _test_dynamic_links(dynamic_links, dt_to_app):
    """
    Test Dynamic Link fields for cross-app references.

    Returns:
        list: results showing which doctypes are resolved through dynamic links
    """
    results = []

    for i, dlink in enumerate(dynamic_links):
        src_dt = dlink["source_doctype"]
        field = dlink["field_name"]
        companion = dlink["companion_field"]

        if i % 10 == 0:
            print(f"  Testing dynamic link {i+1}/{len(dynamic_links)}: {src_dt}.{field} (companion: {companion})")

        if not _table_exists(src_dt):
            continue

        try:
            # Find all distinct doctype values from the companion field
            distinct_sql = (
                f"SELECT `{companion}` AS target_dt, COUNT(*) AS cnt "
                f"FROM `tab{src_dt}` "
                f"WHERE `{companion}` IS NOT NULL AND `{companion}` != '' "
                f"GROUP BY `{companion}` "
                f"ORDER BY cnt DESC "
                f"LIMIT 20"
            )
            groups = frappe.db.sql(distinct_sql, as_dict=True)

            source_app = dlink["source_app"]
            cross_app_targets = []

            for grp in groups:
                target_dt = grp.get("target_dt", "")
                target_app = dt_to_app.get(target_dt, "unknown")
                cnt = grp.get("cnt", 0)

                if target_app != source_app and target_app != "unknown":
                    # This is a cross-app dynamic link
                    # Test integrity for this group
                    broken_count = 0
                    if _table_exists(target_dt):
                        try:
                            broken_sql = (
                                f"SELECT COUNT(*) FROM `tab{src_dt}` s "
                                f"WHERE s.`{companion}` = %s "
                                f"AND s.`{field}` IS NOT NULL AND s.`{field}` != '' "
                                f"AND NOT EXISTS ("
                                f"  SELECT 1 FROM `tab{target_dt}` t WHERE t.name = s.`{field}`"
                                f")"
                            )
                            br = frappe.db.sql(broken_sql, (target_dt,))
                            broken_count = br[0][0] if br else 0
                        except Exception:
                            broken_count = -1

                    cross_app_targets.append({
                        "target_doctype": target_dt,
                        "target_app": target_app,
                        "record_count": cnt,
                        "broken_count": broken_count,
                    })

            if cross_app_targets:
                results.append({
                    "source_app": source_app,
                    "source_doctype": src_dt,
                    "field_name": field,
                    "companion_field": companion,
                    "cross_app_targets": cross_app_targets,
                })

        except Exception as e:
            results.append({
                "source_app": dlink["source_app"],
                "source_doctype": src_dt,
                "field_name": field,
                "companion_field": companion,
                "cross_app_targets": [],
                "error": str(e)[:200],
            })

    return results


def _detect_orphan_records(dt_to_app):
    """
    For heavily-referenced doctypes, check if any records have zero incoming links.
    """
    key_doctypes = ["Student", "Employee", "Course", "Program"]
    orphan_results = []

    for dt_name in key_doctypes:
        if dt_name not in dt_to_app:
            continue
        if not _table_exists(dt_name):
            continue

        total = 0
        try:
            result = frappe.db.sql(f"SELECT COUNT(*) FROM `tab{dt_name}`")
            total = result[0][0] if result else 0
        except Exception:
            continue

        if total == 0:
            continue

        # Check for expected incoming links based on doctype
        incoming_checks = {
            "Student": [("Program Enrollment", "student")],
            "Employee": [("Salary Structure Assignment", "employee")],
            "Course": [("Program Course", "course")],
            "Program": [("Program Enrollment", "program")],
        }

        checks = incoming_checks.get(dt_name, [])
        for ref_dt, ref_field in checks:
            if not _table_exists(ref_dt):
                continue

            try:
                orphan_sql = (
                    f"SELECT COUNT(*) FROM `tab{dt_name}` d "
                    f"WHERE NOT EXISTS ("
                    f"  SELECT 1 FROM `tab{ref_dt}` r WHERE r.`{ref_field}` = d.name"
                    f")"
                )
                result = frappe.db.sql(orphan_sql)
                orphan_count = result[0][0] if result else 0

                if orphan_count > 0:
                    orphan_results.append({
                        "doctype": dt_name,
                        "total_records": total,
                        "orphan_count": orphan_count,
                        "expected_ref": f"{ref_dt}.{ref_field}",
                        "severity": "WARNING",
                    })

            except Exception:
                pass

    return orphan_results


def _generate_report(link_results, dynamic_results, orphan_results, output_path):
    """Generate CONNECTION_AUDIT.md report."""
    lines = []
    lines.append("# Cross-App Connection Audit Report")
    lines.append("")

    from datetime import datetime, timezone
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")

    # Counts
    total_links = len(link_results)
    failures = [r for r in link_results if r["status"] == "FAILURE"]
    warnings = [r for r in link_results if r["status"] == "WARNING"]
    passes = [r for r in link_results if r["status"] == "PASS"]
    skips = [r for r in link_results if r["status"] == "SKIP"]
    errors = [r for r in link_results if r["status"] == "ERROR"]
    total_broken = sum(r["broken_count"] for r in link_results)

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Total cross-app Link fields tested:** {total_links}")
    lines.append(f"- **PASS:** {len(passes)}")
    lines.append(f"- **FAILURE (broken links):** {len(failures)}")
    lines.append(f"- **WARNING:** {len(warnings)}")
    lines.append(f"- **SKIP (missing table):** {len(skips)}")
    lines.append(f"- **ERROR:** {len(errors)}")
    lines.append(f"- **Total broken link records:** {total_broken}")
    lines.append(f"- **Dynamic Link groups with cross-app targets:** {len(dynamic_results)}")
    lines.append(f"- **Orphan record checks with warnings:** {len(orphan_results)}")
    lines.append("")

    # Severity summary
    if failures:
        lines.append("**Overall Status: FAILURE** -- broken cross-app links detected")
    elif warnings or orphan_results:
        lines.append("**Overall Status: WARNING** -- no broken links but orphan records or missing tables detected")
    else:
        lines.append("**Overall Status: PASS** -- all cross-app links resolve correctly")
    lines.append("")

    # Cross-App Link Inventory
    lines.append("## Cross-App Link Inventory")
    lines.append("")
    lines.append("| Source App | Source Doctype | Field | Type | Target App | Target Doctype | Total Records | Broken Count | Broken % | Status |")
    lines.append("|-----------|--------------|-------|------|-----------|---------------|-------------:|------------:|--------:|--------|")

    # Sort: failures first, then by broken count
    sorted_results = sorted(link_results, key=lambda r: (
        0 if r["status"] == "FAILURE" else 1 if r["status"] == "WARNING" else 2,
        -r["broken_count"],
    ))

    for r in sorted_results:
        lines.append(
            f"| {r['source_app']} | {r['source_doctype']} | {r['field_name']} | {r['field_type']} "
            f"| {r['target_app']} | {r['target_doctype']} | {r['total_records']} "
            f"| {r['broken_count']} | {r['broken_pct']}% | {r['status']} |"
        )
    lines.append("")

    # Broken Link Details
    lines.append("## Broken Link Details")
    lines.append("")
    if failures:
        lines.append("First 10 broken records per link type:")
        lines.append("")
        for r in failures:
            if r["broken_samples"]:
                lines.append(f"### {r['source_doctype']}.{r['field_name']} -> {r['target_doctype']}")
                lines.append("")
                lines.append(f"**{r['broken_count']} broken** out of {r['total_records']} records ({r['broken_pct']}%)")
                lines.append("")
                lines.append("| Source Record | Broken Value |")
                lines.append("|-------------|-------------|")
                for sample in r["broken_samples"][:10]:
                    lines.append(f"| {sample['source_record']} | {sample['broken_value']} |")
                lines.append("")
    else:
        lines.append("No broken links detected.")
        lines.append("")

    # Dynamic Link Analysis
    lines.append("## Dynamic Link Analysis")
    lines.append("")
    if dynamic_results:
        lines.append("Dynamic Link fields resolving to cross-app doctypes:")
        lines.append("")
        for dr in dynamic_results:
            if dr.get("error"):
                lines.append(f"### {dr['source_doctype']}.{dr['field_name']} -- ERROR: {dr['error']}")
                lines.append("")
                continue

            lines.append(f"### {dr['source_doctype']}.{dr['field_name']} (companion: {dr['companion_field']})")
            lines.append("")
            lines.append("| Target Doctype | Target App | Record Count | Broken Count | Status |")
            lines.append("|---------------|-----------|------------:|------------:|--------|")
            for ct in dr["cross_app_targets"]:
                status = "FAILURE" if ct["broken_count"] > 0 else ("ERROR" if ct["broken_count"] < 0 else "PASS")
                lines.append(
                    f"| {ct['target_doctype']} | {ct['target_app']} | {ct['record_count']} "
                    f"| {ct['broken_count']} | {status} |"
                )
            lines.append("")
    else:
        lines.append("No cross-app Dynamic Link references found.")
        lines.append("")

    # Orphan Records
    lines.append("## Orphan Record Analysis")
    lines.append("")
    if orphan_results:
        lines.append("| Doctype | Total Records | Orphan Count | Expected Reference | Severity |")
        lines.append("|---------|-------------:|------------:|-------------------|----------|")
        for o in orphan_results:
            lines.append(
                f"| {o['doctype']} | {o['total_records']} | {o['orphan_count']} "
                f"| {o['expected_ref']} | {o['severity']} |"
            )
        lines.append("")
    else:
        lines.append("No orphan records detected for key doctypes.")
        lines.append("")

    # Severity Classification Legend
    lines.append("## Severity Classification")
    lines.append("")
    lines.append("| Level | Meaning |")
    lines.append("|-------|---------|")
    lines.append("| FAILURE | Broken links found -- field references a non-existent record |")
    lines.append("| WARNING | Potential issue -- target table missing or orphan records |")
    lines.append("| PASS | All links resolve correctly |")
    lines.append("| SKIP | Source table does not exist in database |")
    lines.append("| ERROR | Query failed -- investigate manually |")
    lines.append("")

    report_content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_content)

    return report_content


def run():
    """
    Main entry point. Run via:
        bench --site university.local execute university_erp.scripts.audit_cross_app_links.run
    """
    print("=" * 70)
    print("CROSS-APP LINK INTEGRITY AUDIT")
    print("=" * 70)

    # 1. Build doctype-to-app mapping from disk
    apps_root = _get_apps_root()
    print(f"\nScanning apps in: {apps_root}")
    dt_to_app, dt_fields = _build_doctype_app_map(apps_root)
    print(f"  Mapped {len(dt_to_app)} doctypes across {len(set(dt_to_app.values()))} apps")

    # 2. Discover cross-app links
    print("\nDiscovering cross-app Link and Dynamic Link fields...")
    cross_links, dynamic_links = _discover_cross_app_links(dt_to_app, dt_fields)
    print(f"  Found {len(cross_links)} cross-app Link fields")
    print(f"  Found {len(dynamic_links)} Dynamic Link fields to analyze")

    # 3. Test link integrity
    print("\nTesting Link field integrity...")
    link_results = _test_link_integrity(cross_links)

    failures = [r for r in link_results if r["status"] == "FAILURE"]
    print(f"  Tested {len(link_results)} links: {len(failures)} failures")

    # 4. Test dynamic links
    print("\nTesting Dynamic Link fields...")
    dynamic_results = _test_dynamic_links(dynamic_links, dt_to_app)
    print(f"  Analyzed {len(dynamic_results)} dynamic link groups with cross-app targets")

    # 5. Detect orphan records
    print("\nChecking for orphan records...")
    orphan_results = _detect_orphan_records(dt_to_app)
    print(f"  Found {len(orphan_results)} orphan record warnings")

    # 6. Generate report
    output_path = os.path.normpath(os.path.join(
        apps_root, "..", "..", ".planning",
        "phases", "03.1-cross-app-integration-audit-accessibility-testing",
        "CONNECTION_AUDIT.md"
    ))
    print(f"\nGenerating report: {output_path}")
    _generate_report(link_results, dynamic_results, orphan_results, output_path)

    print(f"\nReport written to: {output_path}")
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    total_broken = sum(r["broken_count"] for r in link_results)
    print(f"  Cross-app links tested: {len(link_results)}")
    print(f"  Failures: {len(failures)}")
    print(f"  Total broken records: {total_broken}")
    print(f"  Dynamic link groups: {len(dynamic_results)}")
    print(f"  Orphan warnings: {len(orphan_results)}")
    print("=" * 70)

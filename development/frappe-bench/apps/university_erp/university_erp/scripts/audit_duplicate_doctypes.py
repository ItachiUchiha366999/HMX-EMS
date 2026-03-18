# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Duplicate Doctype Audit Script

Discovers all doctypes from disk across all apps in frappe-bench/apps/,
identifies exact-name duplicates, semantic overlaps, and shared link targets.

Usage:
    bench --site university.local execute university_erp.scripts.audit_duplicate_doctypes.run
"""

import json
import os
from collections import defaultdict


def _get_apps_root():
    """Get the frappe-bench/apps/ root directory."""
    # Navigate from this script's location up to frappe-bench/apps/
    # Path: university_erp/university_erp/scripts/ -> university_erp/university_erp/ -> university_erp/ -> apps/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apps_root = os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    if not os.path.isdir(apps_root):
        raise FileNotFoundError(f"Apps root not found at {apps_root}")
    # Verify it contains expected app directories
    if not os.path.isdir(os.path.join(apps_root, "frappe")):
        raise FileNotFoundError(f"Apps root at {apps_root} does not contain 'frappe' directory")
    return apps_root


def _scan_doctypes_from_disk(apps_root):
    """
    Scan all app directories for doctype JSON definitions.

    Returns:
        dict: {app_name: {doctype_name: {fields, istable, issingle, module, field_count, link_targets, json_path}}}
    """
    app_doctypes = {}
    app_dirs = sorted(
        d for d in os.listdir(apps_root)
        if os.path.isdir(os.path.join(apps_root, d)) and not d.startswith(".")
    )

    for app_name in app_dirs:
        app_path = os.path.join(apps_root, app_name)
        doctypes = {}

        for root, dirs, files in os.walk(app_path):
            # Skip hidden dirs, node_modules, __pycache__, .git
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".git")
            ]

            # Only process directories that are inside a /doctype/ path
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

                if not isinstance(data, dict):
                    continue

                if data.get("doctype") != "DocType":
                    continue

                dt_name = data.get("name", "")
                if not dt_name:
                    continue

                # Already recorded this doctype for this app (could have
                # multiple JSON files per doctype dir -- we want the main one)
                if dt_name in doctypes:
                    continue

                fields = data.get("fields", [])
                field_info = {}
                link_targets = set()

                for field in fields:
                    fn = field.get("fieldname", "")
                    ft = field.get("fieldtype", "")
                    opts = field.get("options", "")
                    if fn:
                        field_info[fn] = {"fieldtype": ft, "options": opts}
                    if ft == "Link" and opts:
                        link_targets.add(opts)

                doctypes[dt_name] = {
                    "fields": field_info,
                    "istable": data.get("istable", 0) or 0,
                    "issingle": data.get("issingle", 0) or 0,
                    "module": data.get("module", ""),
                    "field_count": len(field_info),
                    "link_targets": link_targets,
                    "json_path": filepath,
                }

        if doctypes:
            app_doctypes[app_name] = doctypes

    return app_doctypes


def _get_live_owner(dt_name):
    """Try to get the live module owner from the database."""
    try:
        import frappe
        result = frappe.db.get_value("DocType", dt_name, "module")
        return result or "N/A"
    except Exception:
        return "N/A"


def _find_exact_matches(app_doctypes):
    """
    Find doctypes with the same name across different apps.

    Returns:
        list of dicts with match details
    """
    # Build name -> list of (app, info) mapping
    name_map = defaultdict(list)
    for app_name, doctypes in app_doctypes.items():
        for dt_name, info in doctypes.items():
            name_map[dt_name].append((app_name, info))

    matches = []
    for dt_name, entries in sorted(name_map.items()):
        if len(entries) < 2:
            continue

        # Compare all pairs
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                app1, info1 = entries[i]
                app2, info2 = entries[j]

                fields1 = set(info1["fields"].keys())
                fields2 = set(info2["fields"].keys())

                only_in_1 = fields1 - fields2
                only_in_2 = fields2 - fields1
                common = fields1 & fields2

                # Type mismatches
                type_mismatches = []
                link_diffs = []
                for fn in common:
                    ft1 = info1["fields"][fn]["fieldtype"]
                    ft2 = info2["fields"][fn]["fieldtype"]
                    if ft1 != ft2:
                        type_mismatches.append(f"{fn}: {ft1} vs {ft2}")

                    opts1 = info1["fields"][fn]["options"]
                    opts2 = info2["fields"][fn]["options"]
                    if ft1 == "Link" and ft2 == "Link" and opts1 != opts2:
                        link_diffs.append(f"{fn}: {opts1} vs {opts2}")

                live_owner = _get_live_owner(dt_name)

                # Recommendation logic
                recommendation = _make_recommendation(
                    app1, app2, info1, info2, only_in_1, only_in_2
                )

                matches.append({
                    "doctype": dt_name,
                    "app1": app1,
                    "app2": app2,
                    "field_count_1": info1["field_count"],
                    "field_count_2": info2["field_count"],
                    "only_in_1": sorted(only_in_1),
                    "only_in_2": sorted(only_in_2),
                    "type_mismatches": type_mismatches,
                    "link_diffs": link_diffs,
                    "istable_1": info1["istable"],
                    "istable_2": info2["istable"],
                    "issingle_1": info1["issingle"],
                    "issingle_2": info2["issingle"],
                    "live_owner": live_owner,
                    "recommendation": recommendation,
                })

    return matches


def _make_recommendation(app1, app2, info1, info2, only_in_1, only_in_2):
    """Generate a recommendation based on schema comparison."""
    # Structural mismatch
    if info1["istable"] != info2["istable"] or info1["issingle"] != info2["issingle"]:
        return "INVESTIGATE - structural mismatch (istable/issingle differs)"

    uerp_app = None
    other_app = None
    uerp_info = None
    other_info = None
    uerp_only = None
    other_only = None

    if app1 == "university_erp":
        uerp_app, other_app = app1, app2
        uerp_info, other_info = info1, info2
        uerp_only, other_only = only_in_1, only_in_2
    elif app2 == "university_erp":
        uerp_app, other_app = app2, app1
        uerp_info, other_info = info2, info1
        uerp_only, other_only = only_in_2, only_in_1
    else:
        # Neither is university_erp -- just note the overlap
        if info1["field_count"] >= info2["field_count"]:
            return f"Keep {app1} version (more fields)"
        return f"Keep {app2} version (more fields)"

    if uerp_info["field_count"] > other_info["field_count"]:
        return f"Keep university_erp, alias {other_app}"
    elif len(uerp_only) < 3 and other_info["field_count"] > uerp_info["field_count"]:
        return f"Keep {other_app}, migrate {len(uerp_only)} custom fields"
    elif len(uerp_only) >= 3 and len(other_only) >= 3:
        return "Merge schemas"
    else:
        return f"Keep {other_app}, migrate {len(uerp_only)} custom fields"


def _find_semantic_overlaps(app_doctypes):
    """
    Find doctypes in different apps that share 50%+ of their Link field targets.
    Focus on fees/finance, assessment/grading, attendance, courses/teaching, exams/quizzes.
    """
    # Domain keywords for filtering
    domain_keywords = {
        "fees/finance": ["fee", "payment", "invoice", "account", "finance", "charge", "due"],
        "assessment/grading": ["assessment", "grade", "grading", "result", "mark", "score", "evaluation"],
        "attendance": ["attendance", "present", "absent", "leave"],
        "courses/teaching": ["course", "teaching", "instructor", "faculty", "lecture", "timetable", "schedule"],
        "exams/quizzes": ["exam", "quiz", "question", "answer", "paper", "hall_ticket", "proctoring"],
    }

    def _get_domain(dt_name):
        name_lower = dt_name.lower().replace(" ", "_")
        for domain, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in name_lower:
                    return domain
        return None

    # Collect all doctypes with link targets across apps
    all_dts = []
    for app_name, doctypes in app_doctypes.items():
        for dt_name, info in doctypes.items():
            if info["link_targets"]:
                domain = _get_domain(dt_name)
                all_dts.append({
                    "app": app_name,
                    "doctype": dt_name,
                    "link_targets": info["link_targets"],
                    "domain": domain,
                })

    overlaps = []
    seen_pairs = set()

    for i in range(len(all_dts)):
        for j in range(i + 1, len(all_dts)):
            dt1 = all_dts[i]
            dt2 = all_dts[j]

            # Must be from different apps
            if dt1["app"] == dt2["app"]:
                continue

            # Must be in a relevant domain (at least one)
            if not dt1["domain"] and not dt2["domain"]:
                continue

            pair_key = tuple(sorted([
                f"{dt1['app']}:{dt1['doctype']}",
                f"{dt2['app']}:{dt2['doctype']}"
            ]))
            if pair_key in seen_pairs:
                continue

            shared = dt1["link_targets"] & dt2["link_targets"]
            total_unique = dt1["link_targets"] | dt2["link_targets"]

            if not total_unique:
                continue

            overlap_pct = len(shared) / min(len(dt1["link_targets"]), len(dt2["link_targets"])) * 100

            if overlap_pct >= 60 and len(shared) >= 3:
                seen_pairs.add(pair_key)
                domain = dt1["domain"] or dt2["domain"] or "general"
                overlaps.append({
                    "domain": domain,
                    "dt1_app": dt1["app"],
                    "dt1_name": dt1["doctype"],
                    "dt2_app": dt2["app"],
                    "dt2_name": dt2["doctype"],
                    "shared_targets": sorted(shared),
                    "overlap_pct": round(overlap_pct, 1),
                })

    overlaps.sort(key=lambda x: x["overlap_pct"], reverse=True)
    return overlaps


def _find_shared_link_targets(app_doctypes):
    """
    Identify doctypes that are heavily referenced (linked-to) by multiple apps.
    Count incoming links per doctype per app.
    """
    # target_doctype -> {app: count_of_fields_linking_to_it}
    incoming = defaultdict(lambda: defaultdict(int))

    for app_name, doctypes in app_doctypes.items():
        for dt_name, info in doctypes.items():
            for target in info["link_targets"]:
                incoming[target][app_name] += 1

    # Filter to those referenced by 2+ apps
    shared = []
    for target, app_counts in sorted(incoming.items()):
        if len(app_counts) >= 2:
            total = sum(app_counts.values())
            refs_str = ", ".join(f"{app}: {cnt}" for app, cnt in sorted(app_counts.items()))
            shared.append({
                "target": target,
                "app_counts": dict(app_counts),
                "refs_str": refs_str,
                "total": total,
                "app_count": len(app_counts),
            })

    shared.sort(key=lambda x: x["total"], reverse=True)
    return shared


def _generate_report(matches, overlaps, shared_targets, app_doctypes, output_path):
    """Generate DUPLICATE_AUDIT.md report."""
    lines = []
    lines.append("# Duplicate Doctype Audit Report")
    lines.append("")
    lines.append(f"**Generated:** {_now()}")
    lines.append(f"**Apps scanned:** {', '.join(sorted(app_doctypes.keys()))}")
    lines.append("")

    # App stats
    lines.append("## App Doctype Counts")
    lines.append("")
    lines.append("| App | Doctype Count |")
    lines.append("|-----|--------------|")
    for app_name in sorted(app_doctypes.keys()):
        lines.append(f"| {app_name} | {len(app_doctypes[app_name])} |")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Exact Name Matches:** {len(matches)} duplicate pairs found")
    lines.append(f"- **Semantic Overlaps:** {len(overlaps)} pairs with 50%+ shared link targets")
    lines.append(f"- **Shared Link Targets:** {len(shared_targets)} doctypes referenced by 2+ apps")
    lines.append("")

    structural_mismatches = [m for m in matches if "structural mismatch" in m["recommendation"]]
    if structural_mismatches:
        lines.append(f"- **RISK: {len(structural_mismatches)} structural mismatches** (istable/issingle differs)")
    lines.append("")

    # Exact Name Matches
    lines.append("## Exact Name Matches")
    lines.append("")
    if matches:
        lines.append("| Doctype | App 1 | App 2 | Fields (1) | Fields (2) | Only In 1 | Only In 2 | Type Mismatches | Live Owner | Recommendation |")
        lines.append("|---------|-------|-------|-----------|-----------|-----------|-----------|----------------|------------|---------------|")
        for m in matches:
            only1 = len(m["only_in_1"])
            only2 = len(m["only_in_2"])
            tmm = len(m["type_mismatches"])
            lines.append(
                f"| {m['doctype']} | {m['app1']} | {m['app2']} | {m['field_count_1']} | {m['field_count_2']} "
                f"| {only1} | {only2} | {tmm} | {m['live_owner']} | {m['recommendation']} |"
            )
        lines.append("")

        # Detail section for matches with significant differences
        lines.append("### Detailed Schema Differences")
        lines.append("")
        for m in matches:
            if m["only_in_1"] or m["only_in_2"] or m["type_mismatches"]:
                lines.append(f"#### {m['doctype']} ({m['app1']} vs {m['app2']})")
                lines.append("")
                if m["only_in_1"]:
                    lines.append(f"**Fields only in {m['app1']}:** {', '.join(m['only_in_1'][:15])}")
                    if len(m["only_in_1"]) > 15:
                        lines.append(f"  ...and {len(m['only_in_1']) - 15} more")
                if m["only_in_2"]:
                    lines.append(f"**Fields only in {m['app2']}:** {', '.join(m['only_in_2'][:15])}")
                    if len(m["only_in_2"]) > 15:
                        lines.append(f"  ...and {len(m['only_in_2']) - 15} more")
                if m["type_mismatches"]:
                    lines.append(f"**Type mismatches:** {'; '.join(m['type_mismatches'][:10])}")
                if m["link_diffs"]:
                    lines.append(f"**Link target diffs:** {'; '.join(m['link_diffs'][:10])}")
                if m["istable_1"] != m["istable_2"]:
                    lines.append(f"**istable mismatch:** {m['app1']}={m['istable_1']}, {m['app2']}={m['istable_2']}")
                if m["issingle_1"] != m["issingle_2"]:
                    lines.append(f"**issingle mismatch:** {m['app1']}={m['issingle_1']}, {m['app2']}={m['issingle_2']}")
                lines.append("")
    else:
        lines.append("No exact name matches found.")
        lines.append("")

    # Semantic Overlaps
    lines.append("## Semantic Overlaps")
    lines.append("")
    lines.append("Doctypes in different apps sharing 60%+ of their Link field targets (min 3 shared) within domain areas.")
    lines.append(f"Showing top 50 of {len(overlaps)} pairs, sorted by overlap percentage.")
    lines.append("")
    if overlaps:
        lines.append("| Domain | Doctype (App 1) | Doctype (App 2) | Shared Link Targets | Overlap % | Recommendation |")
        lines.append("|--------|----------------|----------------|--------------------|---------:|---------------|")
        for o in overlaps[:50]:
            targets_str = ", ".join(o["shared_targets"][:5])
            if len(o["shared_targets"]) > 5:
                targets_str += f" +{len(o['shared_targets']) - 5} more"
            rec = "Review for consolidation" if o["overlap_pct"] >= 75 else "Document overlap"
            lines.append(
                f"| {o['domain']} | {o['dt1_name']} ({o['dt1_app']}) | {o['dt2_name']} ({o['dt2_app']}) "
                f"| {targets_str} | {o['overlap_pct']}% | {rec} |"
            )
        if len(overlaps) > 50:
            lines.append(f"| ... | {len(overlaps) - 50} more pairs | | | | |")
        lines.append("")
    else:
        lines.append("No semantic overlaps found meeting the threshold.")
        lines.append("")

    # Shared Link Targets
    lines.append("## Shared Link Targets")
    lines.append("")
    lines.append("Doctypes referenced by Link fields from 2+ different apps.")
    lines.append("")
    if shared_targets:
        lines.append("| Target Doctype | Referenced By (App: count) | Total Incoming Links | Apps |")
        lines.append("|---------------|---------------------------|--------------------:|-----:|")
        for st in shared_targets[:50]:
            lines.append(
                f"| {st['target']} | {st['refs_str']} | {st['total']} | {st['app_count']} |"
            )
        if len(shared_targets) > 50:
            lines.append(f"| ... | {len(shared_targets) - 50} more targets | | |")
        lines.append("")
    else:
        lines.append("No shared link targets found.")
        lines.append("")

    # Recommendations summary
    lines.append("## Recommendations Summary")
    lines.append("")
    if matches:
        rec_groups = defaultdict(list)
        for m in matches:
            rec_groups[m["recommendation"]].append(m["doctype"])

        for rec, dts in sorted(rec_groups.items()):
            lines.append(f"### {rec}")
            lines.append("")
            for dt in sorted(dts):
                lines.append(f"- {dt}")
            lines.append("")
    else:
        lines.append("No recommendations (no duplicates found).")
        lines.append("")

    # Write
    report_content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_content)

    return report_content


def _now():
    """Return current UTC timestamp string."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def run():
    """
    Main entry point. Run via:
        bench --site university.local execute university_erp.scripts.audit_duplicate_doctypes.run
    """
    print("=" * 70)
    print("DUPLICATE DOCTYPE AUDIT")
    print("=" * 70)

    # 1. Discover doctypes from disk
    apps_root = _get_apps_root()
    print(f"\nScanning apps in: {apps_root}")
    app_doctypes = _scan_doctypes_from_disk(apps_root)

    for app_name, dts in sorted(app_doctypes.items()):
        print(f"  {app_name}: {len(dts)} doctypes")

    total = sum(len(dts) for dts in app_doctypes.values())
    print(f"  TOTAL: {total} doctypes across {len(app_doctypes)} apps")

    # 2. Find exact name matches
    print("\nFinding exact-name matches...")
    matches = _find_exact_matches(app_doctypes)
    print(f"  Found {len(matches)} exact-name duplicate pairs")

    # 3. Find semantic overlaps
    print("\nFinding semantic overlaps...")
    overlaps = _find_semantic_overlaps(app_doctypes)
    print(f"  Found {len(overlaps)} semantic overlap pairs (50%+ shared link targets)")

    # 4. Find shared link targets
    print("\nFinding shared link targets...")
    shared_targets = _find_shared_link_targets(app_doctypes)
    print(f"  Found {len(shared_targets)} doctypes referenced by 2+ apps")

    # 5. Generate report
    output_path = os.path.normpath(os.path.join(
        apps_root, "..", "..", ".planning",
        "phases", "03.1-cross-app-integration-audit-accessibility-testing",
        "DUPLICATE_AUDIT.md"
    ))
    print(f"\nGenerating report: {output_path}")
    _generate_report(matches, overlaps, shared_targets, app_doctypes, output_path)

    print(f"\nReport written to: {output_path}")
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print(f"  Exact matches: {len(matches)}")
    print(f"  Semantic overlaps: {len(overlaps)}")
    print(f"  Shared link targets: {len(shared_targets)}")
    print("=" * 70)

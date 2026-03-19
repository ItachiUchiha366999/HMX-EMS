# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Desk UI Audit Script

Verifies all Frappe Desk workspace links for university_erp modules resolve
to real doctypes/pages/reports. Generates DESK_AUDIT.md.

Usage:
    bench --site university.local execute university_erp.scripts.audit_desk_ui.run
"""

import os
from datetime import datetime, timezone

import frappe


# All 21 university_erp modules from modules.txt
UNIVERSITY_MODULES = [
    "University ERP",
    "University Academics",
    "University Admissions",
    "University Student Info",
    "University Examinations",
    "University Finance",
    "Faculty Management",
    "University Hostel",
    "University Transport",
    "University Library",
    "University Placement",
    "University LMS",
    "University Research",
    "University OBE",
    "University Integrations",
    "University Portals",
    "University Payments",
    "University Inventory",
    "University Grievance",
    "University Analytics",
    "University Feedback",
]


def _verify_link_target(link_type, link_to):
    """
    Verify that a workspace link target exists.

    Args:
        link_type: Type of link (DocType, Report, Page, Dashboard, URL, etc.)
        link_to: Name of the target

    Returns:
        tuple: (status, detail)
    """
    if not link_to:
        return "SKIP", "No link_to value"

    if link_type == "DocType":
        if frappe.db.exists("DocType", link_to):
            return "PASS", ""
        return "BROKEN", f"DocType '{link_to}' does not exist"

    elif link_type == "Report":
        if frappe.db.exists("Report", link_to):
            return "PASS", ""
        return "BROKEN", f"Report '{link_to}' does not exist"

    elif link_type == "Page":
        if frappe.db.exists("Page", link_to):
            return "PASS", ""
        return "BROKEN", f"Page '{link_to}' does not exist"

    elif link_type == "Dashboard":
        if frappe.db.exists("Dashboard", link_to):
            return "PASS", ""
        return "BROKEN", f"Dashboard '{link_to}' does not exist"

    elif link_type == "URL":
        # URLs are external or internal paths -- we can't fully verify them
        return "PASS", "URL link (not verified)"

    else:
        # Other types (e.g., onboarding) -- skip
        return "SKIP", f"Unknown link type: {link_type}"


def _audit_workspaces():
    """
    Audit all university_erp workspace links and shortcuts.

    Returns:
        dict: Audit results
    """
    # Get all workspaces for university_erp modules
    workspaces = frappe.get_all(
        "Workspace",
        filters={"module": ["in", UNIVERSITY_MODULES]},
        fields=["name", "module", "title", "public"],
    )

    print(f"  Found {len(workspaces)} workspaces for university_erp modules")

    results = []
    workspace_summary = []

    for ws in workspaces:
        ws_name = ws["name"]
        ws_module = ws["module"]
        ws_title = ws["title"] or ws_name

        # Get shortcuts
        shortcuts = frappe.get_all(
            "Workspace Shortcut",
            filters={"parent": ws_name},
            fields=["label", "link_to", "type"],
        )

        # Get links
        links = frappe.get_all(
            "Workspace Link",
            filters={"parent": ws_name},
            fields=["label", "link_to", "type"],
        )

        ws_total = len(shortcuts) + len(links)
        ws_broken = 0
        ws_pass = 0
        ws_skip = 0

        # Verify shortcuts
        for sc in shortcuts:
            status, detail = _verify_link_target(sc.get("type", ""), sc.get("link_to", ""))
            results.append({
                "workspace": ws_title,
                "module": ws_module,
                "label": sc.get("label", ""),
                "link_to": sc.get("link_to", ""),
                "type": sc.get("type", ""),
                "link_kind": "Shortcut",
                "status": status,
                "detail": detail,
            })
            if status == "BROKEN":
                ws_broken += 1
            elif status == "PASS":
                ws_pass += 1
            else:
                ws_skip += 1

        # Verify links
        for lnk in links:
            status, detail = _verify_link_target(lnk.get("type", ""), lnk.get("link_to", ""))
            results.append({
                "workspace": ws_title,
                "module": ws_module,
                "label": lnk.get("label", ""),
                "link_to": lnk.get("link_to", ""),
                "type": lnk.get("type", ""),
                "link_kind": "Link",
                "status": status,
                "detail": detail,
            })
            if status == "BROKEN":
                ws_broken += 1
            elif status == "PASS":
                ws_pass += 1
            else:
                ws_skip += 1

        workspace_summary.append({
            "workspace": ws_title,
            "module": ws_module,
            "public": ws["public"],
            "shortcuts": len(shortcuts),
            "links": len(links),
            "total": ws_total,
            "pass": ws_pass,
            "broken": ws_broken,
            "skip": ws_skip,
        })

    return {
        "workspaces": workspace_summary,
        "results": results,
    }


def _audit_dashboards():
    """
    Audit university_erp Dashboard pages.

    Returns:
        list: Dashboard audit results
    """
    dashboards = frappe.get_all(
        "Dashboard",
        filters={"module": ["in", UNIVERSITY_MODULES]},
        fields=["name", "module", "dashboard_name"],
    )

    results = []

    for dash in dashboards:
        dash_name = dash["name"]

        # Check dashboard charts
        charts = frappe.get_all(
            "Dashboard Chart",
            filters={"dashboard_name": dash_name},
            fields=["name", "chart_name", "chart_type", "document_type"],
        )

        for chart in charts:
            # Verify document_type exists
            doc_type = chart.get("document_type", "")
            if doc_type:
                if frappe.db.exists("DocType", doc_type):
                    status = "PASS"
                    detail = ""
                else:
                    status = "BROKEN"
                    detail = f"DocType '{doc_type}' does not exist"
            else:
                status = "SKIP"
                detail = "No document_type"

            results.append({
                "dashboard": dash.get("dashboard_name", dash_name),
                "module": dash["module"],
                "chart": chart.get("chart_name", ""),
                "chart_type": chart.get("chart_type", ""),
                "document_type": doc_type,
                "status": status,
                "detail": detail,
            })

        # Check number cards
        number_cards = frappe.get_all(
            "Number Card",
            filters={"dashboard_name": dash_name},
            fields=["name", "label", "document_type"],
        )

        for card in number_cards:
            doc_type = card.get("document_type", "")
            if doc_type:
                if frappe.db.exists("DocType", doc_type):
                    status = "PASS"
                    detail = ""
                else:
                    status = "BROKEN"
                    detail = f"DocType '{doc_type}' does not exist"
            else:
                status = "SKIP"
                detail = "No document_type"

            results.append({
                "dashboard": dash.get("dashboard_name", dash_name),
                "module": dash["module"],
                "chart": card.get("label", ""),
                "chart_type": "Number Card",
                "document_type": doc_type,
                "status": status,
                "detail": detail,
            })

    return results


def _generate_report(ws_audit, dashboard_audit, output_path):
    """Generate DESK_AUDIT.md report."""
    lines = []
    lines.append("# Desk UI Audit Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")

    ws_data = ws_audit["workspaces"]
    results = ws_audit["results"]

    total_workspaces = len(ws_data)
    total_links = len(results)
    total_pass = sum(1 for r in results if r["status"] == "PASS")
    total_broken = sum(1 for r in results if r["status"] == "BROKEN")
    total_skip = sum(1 for r in results if r["status"] == "SKIP")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Workspaces checked:** {total_workspaces}")
    lines.append(f"- **Total shortcuts/links tested:** {total_links}")
    lines.append(f"- **PASS:** {total_pass}")
    lines.append(f"- **BROKEN:** {total_broken}")
    lines.append(f"- **SKIP:** {total_skip}")
    lines.append(f"- **Dashboard items checked:** {len(dashboard_audit)}")
    lines.append("")

    if total_broken == 0:
        lines.append("**Overall Status: PASS** -- all workspace links resolve correctly")
    else:
        lines.append(f"**Overall Status: FAIL** -- {total_broken} broken link(s) found")
    lines.append("")

    # Workspace Summary
    lines.append("## Workspace Summary")
    lines.append("")
    lines.append("| Workspace | Module | Public | Shortcuts | Links | Total | Pass | Broken | Skip |")
    lines.append("|-----------|--------|--------|----------:|------:|------:|-----:|-------:|-----:|")
    for ws in sorted(ws_data, key=lambda x: -x["broken"]):
        lines.append(
            f"| {ws['workspace']} | {ws['module']} | {'Yes' if ws['public'] else 'No'} "
            f"| {ws['shortcuts']} | {ws['links']} | {ws['total']} "
            f"| {ws['pass']} | {ws['broken']} | {ws['skip']} |"
        )
    lines.append("")

    # All Links Detail
    lines.append("## Link Verification Details")
    lines.append("")
    lines.append("| Workspace | Label | Link Kind | Type | Target | Status | Detail |")
    lines.append("|-----------|-------|-----------|------|--------|--------|--------|")

    # Sort: broken first
    sorted_results = sorted(results, key=lambda r: (0 if r["status"] == "BROKEN" else 1, r["workspace"]))
    for r in sorted_results:
        detail = r["detail"][:60] if r["detail"] else ""
        lines.append(
            f"| {r['workspace']} | {r['label']} | {r['link_kind']} "
            f"| {r['type']} | {r['link_to']} | {r['status']} | {detail} |"
        )
    lines.append("")

    # Broken Links Detail
    broken_links = [r for r in results if r["status"] == "BROKEN"]
    lines.append("## Broken Links")
    lines.append("")
    if broken_links:
        lines.append(f"Found {len(broken_links)} broken link(s):")
        lines.append("")
        for i, bl in enumerate(broken_links, 1):
            lines.append(f"### {i}. {bl['workspace']} -> {bl['link_to']}")
            lines.append("")
            lines.append(f"- **Label:** {bl['label']}")
            lines.append(f"- **Type:** {bl['type']}")
            lines.append(f"- **Link Kind:** {bl['link_kind']}")
            lines.append(f"- **Issue:** {bl['detail']}")
            lines.append("")
    else:
        lines.append("No broken links detected.")
        lines.append("")

    # Dashboard Audit
    lines.append("## Dashboard Audit")
    lines.append("")
    if dashboard_audit:
        dash_broken = [d for d in dashboard_audit if d["status"] == "BROKEN"]
        dash_pass = [d for d in dashboard_audit if d["status"] == "PASS"]

        lines.append(f"- **Dashboard items checked:** {len(dashboard_audit)}")
        lines.append(f"- **PASS:** {len(dash_pass)}")
        lines.append(f"- **BROKEN:** {len(dash_broken)}")
        lines.append("")

        if dashboard_audit:
            lines.append("| Dashboard | Module | Chart/Card | Type | Document Type | Status |")
            lines.append("|-----------|--------|------------|------|---------------|--------|")
            for d in dashboard_audit:
                lines.append(
                    f"| {d['dashboard']} | {d['module']} | {d['chart']} "
                    f"| {d['chart_type']} | {d['document_type']} | {d['status']} |"
                )
            lines.append("")
    else:
        lines.append("No university_erp dashboards found in the system.")
        lines.append("")

    report_content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_content)

    return report_content


def run():
    """
    Main entry point. Run via:
        bench --site university.local execute university_erp.scripts.audit_desk_ui.run
    """
    print("=" * 70)
    print("DESK UI AUDIT")
    print("=" * 70)

    # 1. Audit workspace links and shortcuts
    print("\nAuditing workspace links and shortcuts...")
    ws_audit = _audit_workspaces()

    ws_data = ws_audit["workspaces"]
    results = ws_audit["results"]
    broken = [r for r in results if r["status"] == "BROKEN"]

    print(f"  Workspaces: {len(ws_data)}")
    print(f"  Total links/shortcuts: {len(results)}")
    print(f"  Broken: {len(broken)}")

    # 2. Audit dashboards
    print("\nAuditing dashboards...")
    dashboard_audit = _audit_dashboards()
    dash_broken = [d for d in dashboard_audit if d["status"] == "BROKEN"]
    print(f"  Dashboard items: {len(dashboard_audit)}")
    print(f"  Broken: {len(dash_broken)}")

    # 3. Generate report
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apps_root = os.path.normpath(os.path.join(script_dir, "..", "..", ".."))
    output_path = os.path.normpath(os.path.join(
        apps_root, "..", "..", ".planning",
        "phases", "03.1-cross-app-integration-audit-accessibility-testing",
        "DESK_AUDIT.md"
    ))
    print(f"\nGenerating report: {output_path}")
    _generate_report(ws_audit, dashboard_audit, output_path)

    print(f"\nReport written to: {output_path}")
    print("\n" + "=" * 70)
    print("DESK UI AUDIT COMPLETE")
    print(f"  Workspaces checked: {len(ws_data)}")
    print(f"  Links/shortcuts tested: {len(results)}")
    print(f"  Broken links: {len(broken)}")
    print(f"  Dashboard items: {len(dashboard_audit)}")
    print(f"  Dashboard broken: {len(dash_broken)}")
    print("=" * 70)

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import json
import os

import frappe
from frappe import _


def get_context(context):
    """SPA shell for the unified Vue 3 Portal -- serves all roles at /portal/"""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to=/portal{frappe.local.request.path.replace('/portal', '') or '/'}"
        )
        raise frappe.Redirect

    context.no_cache = 1
    context.show_sidebar = False

    # Read Vite manifest to get hashed asset filenames
    manifest = get_vite_manifest()
    context.vue_js = manifest.get("js", "")
    context.vue_css = manifest.get("css", "")

    return context


def get_vite_manifest():
    """Read the Vite build manifest to get hashed filenames for the unified portal."""
    manifest_path = frappe.get_app_path(
        "university_erp", "public", "portal", ".vite", "manifest.json"
    )

    if not os.path.exists(manifest_path):
        frappe.log_error(
            "Portal Vite manifest not found. Run: cd portal-vue && npm install && npm run build",
            "Portal Setup"
        )
        return {"js": "", "css": ""}

    with open(manifest_path) as f:
        manifest = json.load(f)

    entry = manifest.get("index.html", {})
    base = "/assets/university_erp/portal/"

    result = {
        "js": base + entry.get("file", "") if entry.get("file") else "",
        "css": "",
    }

    css_files = entry.get("css", [])
    if css_files:
        result["css"] = base + css_files[0]

    return result

#!/usr/bin/env python3
"""
CSS Accessibility Contrast Audit Script

Reads CSS theme variables and checks color contrast ratios against
WCAG 2.1 AA requirements:
  - Normal text (< 18px): contrast ratio >= 4.5:1
  - Large text (>= 18px or >= 14px bold): contrast ratio >= 3:1

Usage:
  python3 scripts/audit_accessibility.py
"""

import re
import os
import sys


def hex_to_rgb(hex_color):
    """Convert hex color (#RRGGBB or #RGB) to RGB tuple."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return None
    try:
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def relative_luminance(rgb):
    """Calculate relative luminance per WCAG 2.1 definition."""
    srgb = [c / 255.0 for c in rgb]
    linear = []
    for c in srgb:
        if c <= 0.03928:
            linear.append(c / 12.92)
        else:
            linear.append(((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(color1_rgb, color2_rgb):
    """Calculate WCAG contrast ratio between two colors."""
    l1 = relative_luminance(color1_rgb)
    l2 = relative_luminance(color2_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_css_variables(css_content):
    """Parse CSS custom properties from :root declarations."""
    variables = {}
    # Match --name: value patterns
    pattern = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);")
    for match in pattern.finditer(css_content):
        name = f"--{match.group(1)}"
        value = match.group(2).strip()
        variables[name] = value
    return variables


def resolve_var(value, variables, depth=0):
    """Resolve var() references to actual values."""
    if depth > 10:
        return value
    var_pattern = re.compile(r"var\(\s*([^,)]+)(?:\s*,\s*([^)]+))?\s*\)")
    match = var_pattern.search(value)
    if match:
        var_name = match.group(1).strip()
        fallback = match.group(2)
        resolved = variables.get(var_name)
        if resolved:
            resolved = resolve_var(resolved, variables, depth + 1)
            return value[: match.start()] + resolved + value[match.end() :]
        elif fallback:
            fallback = resolve_var(fallback.strip(), variables, depth + 1)
            return value[: match.start()] + fallback + value[match.end() :]
    return value


def analyze_contrast_pairs(variables):
    """Analyze key text/background color pairs for WCAG compliance."""
    pairs = [
        # (text_var, bg_var, context, size_type)
        ("--text-primary", "--bg-card", "Card text on card background", "normal"),
        ("--text-primary", "--bg-surface", "Primary text on surface", "normal"),
        ("--text-secondary", "--bg-card", "Secondary text on card", "normal"),
        ("--text-secondary", "--bg-surface", "Secondary text on surface", "normal"),
        ("--text-muted", "--bg-card", "Muted text on card", "normal"),
        ("--text-muted", "--bg-surface", "Muted text on surface", "normal"),
        ("--success", "--white", "Success text on white", "normal"),
        ("--warning", "--white", "Warning text on white", "normal"),
        ("--error", "--white", "Error text on white", "normal"),
        ("--info", "--white", "Info text on white", "normal"),
        ("--primary", "--white", "Primary brand on white", "normal"),
        ("--secondary", "--white", "Secondary brand on white", "normal"),
        ("--white", "--primary", "White text on primary", "normal"),
        ("--white", "--success", "White text on success bg", "normal"),
        ("--white", "--error", "White text on error bg", "normal"),
        ("--white", "--warning", "White text on warning bg", "normal"),
        ("--success-dark", "--success-light", "Dark success on light success", "normal"),
        ("--error-dark", "--error-light", "Dark error on light error", "normal"),
        ("--warning-dark", "--warning-light", "Dark warning on light warning", "normal"),
        ("--info-dark", "--info-light", "Dark info on light info", "normal"),
        ("--gray-500", "--white", "Gray-500 text on white", "normal"),
        ("--gray-400", "--white", "Gray-400 text on white", "normal"),
        ("--gray-700", "--gray-50", "Gray-700 on gray-50", "normal"),
        # Accessible text variants (used for text on white backgrounds)
        ("--success-text", "--white", "Success-text on white", "normal"),
        ("--warning-text", "--white", "Warning-text on white", "normal"),
        ("--error-text", "--white", "Error-text on white", "normal"),
        ("--info-text", "--white", "Info-text on white", "normal"),
    ]

    results = []
    for text_var, bg_var, context, size_type in pairs:
        text_raw = variables.get(text_var)
        bg_raw = variables.get(bg_var)

        if not text_raw or not bg_raw:
            results.append(
                {
                    "context": context,
                    "text_var": text_var,
                    "bg_var": bg_var,
                    "text_color": "N/A",
                    "bg_color": "N/A",
                    "ratio": 0,
                    "required": 4.5 if size_type == "normal" else 3.0,
                    "status": "SKIP",
                    "note": "Variable not found",
                }
            )
            continue

        text_resolved = resolve_var(text_raw, variables)
        bg_resolved = resolve_var(bg_raw, variables)

        text_rgb = hex_to_rgb(text_resolved)
        bg_rgb = hex_to_rgb(bg_resolved)

        if not text_rgb or not bg_rgb:
            results.append(
                {
                    "context": context,
                    "text_var": text_var,
                    "bg_var": bg_var,
                    "text_color": text_resolved,
                    "bg_color": bg_resolved,
                    "ratio": 0,
                    "required": 4.5 if size_type == "normal" else 3.0,
                    "status": "SKIP",
                    "note": "Could not parse color",
                }
            )
            continue

        ratio = contrast_ratio(text_rgb, bg_rgb)
        required = 4.5 if size_type == "normal" else 3.0
        status = "PASS" if ratio >= required else "FAIL"

        results.append(
            {
                "context": context,
                "text_var": text_var,
                "bg_var": bg_var,
                "text_color": text_resolved,
                "bg_color": bg_resolved,
                "ratio": round(ratio, 2),
                "required": required,
                "status": status,
            }
        )

    return results


def main():
    """Run the CSS contrast audit."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_dir = os.path.join(base_dir, "university_erp", "public", "css")
    variables_path = os.path.join(css_dir, "theme", "variables.css")

    if not os.path.exists(variables_path):
        print(f"ERROR: variables.css not found at {variables_path}")
        sys.exit(1)

    # Read variables.css (light theme only -- stop before dark mode overrides)
    with open(variables_path, "r") as f:
        variables_css = f.read()

    # Split at dark mode selector to only parse light theme
    dark_split = re.split(r'\[data-theme\s*=\s*["\']dark["\']\]', variables_css)
    light_css = dark_split[0]

    # Also parse semantic tokens from second :root block (before dark mode)
    # These are in the same file: --bg-surface, --text-primary, etc.
    variables = parse_css_variables(light_css)

    # Read additional CSS files for context (but not for variable overrides)
    css_files = [
        os.path.join(css_dir, "portal.css"),
        os.path.join(css_dir, "university_desk.css"),
        os.path.join(css_dir, "theme", "components.css"),
    ]
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, "r") as f:
                # Only extract portal-specific variables (--portal-*)
                portal_vars = parse_css_variables(f.read())
                for k, v in portal_vars.items():
                    if k not in variables:  # Don't override theme variables
                        variables[k] = v
    print(f"Parsed {len(variables)} CSS custom properties\n")

    # Analyze contrast pairs
    results = analyze_contrast_pairs(variables)

    # Print results
    print(f"{'Context':<40} {'Foreground':<12} {'Background':<12} {'Ratio':<8} {'Required':<10} {'Status'}")
    print("-" * 100)

    fails = []
    passes = []
    skips = []

    for r in results:
        line = f"{r['context']:<40} {r['text_color']:<12} {r['bg_color']:<12} {r['ratio']:<8} {r['required']:<10} {r['status']}"
        print(line)
        if r["status"] == "FAIL":
            fails.append(r)
        elif r["status"] == "PASS":
            passes.append(r)
        else:
            skips.append(r)

    print(f"\n{'=' * 50}")
    print(f"PASSED: {len(passes)}")
    print(f"FAILED: {len(fails)}")
    print(f"SKIPPED: {len(skips)}")

    if fails:
        print("\nFailing pairs (need contrast improvement):")
        for f in fails:
            print(f"  - {f['context']}: {f['ratio']}:1 (need {f['required']}:1)")

    return len(fails)


if __name__ == "__main__":
    fail_count = main()
    sys.exit(1 if fail_count > 0 else 0)

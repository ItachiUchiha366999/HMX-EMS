"""
audit_education_doctypes.py

Phase 03.3.1 — Wave 1 audit.

Walks frappe-bench/apps/education/education/education/doctype/, cross-references each
doctype directory against DOCTYPE_MODULE_MAP (the locked fork destination map), and emits
.planning/phases/03.3.1-.../DOCTYPE_MAPPING.md — the definitive 71-row mapping table that
plans 02-06 read as ground truth.

Also resolves two RESEARCH.md open questions inline:
  1. Quiz Question table-name collision (Education vs university_lms)
  2. student_sibling vs student_siblings duplication

And performs a destination-collision pre-flight (D-04 schema-merge gate).

Run from frappe-bench/apps/university_erp/:
    python -m university_erp.scripts.audit_education_doctypes
"""

import json
import os
import sys

# Repository root resolution: this file lives at
#   frappe-bench/apps/university_erp/university_erp/scripts/audit_education_doctypes.py
# Repo root = parents[4]
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", "..", ".."))

EDU_DOCTYPE_ROOT = os.path.join(
    REPO_ROOT, "frappe-bench", "apps", "education", "education", "education", "doctype"
)
UNI_ERP_ROOT = os.path.join(
    REPO_ROOT, "frappe-bench", "apps", "university_erp", "university_erp"
)
PHASE_DIR = os.path.join(
    REPO_ROOT,
    ".planning",
    "phases",
    "03.3.1-fork-education-app-into-university-erp-audit-each-doctype-fields-features-and-workflows-then-fork-into-custom-app",
)
MAPPING_OUT = os.path.join(PHASE_DIR, "DOCTYPE_MAPPING.md")

# --------------------------------------------------------------------------- #
# DOCTYPE_MODULE_MAP — locked destination map, mirrors RESEARCH.md
# Plans 02/03/04 import this dict (also re-declared in fork_education_module.py).
# --------------------------------------------------------------------------- #
DOCTYPE_MODULE_MAP = {
    # === University Academics ===
    "academic_term": "University Academics",
    "academic_year": "University Academics",
    "article": "University Academics",
    "assessment_criteria": "University Academics",
    "assessment_criteria_group": "University Academics",
    "assessment_group": "University Academics",
    "assessment_plan": "University Academics",
    "assessment_plan_criteria": "University Academics",
    "assessment_result": "University Academics",
    "assessment_result_detail": "University Academics",
    "assessment_result_tool": "University Academics",
    "course": "University Academics",
    "course_activity": "University Academics",
    "course_assessment_criteria": "University Academics",
    "course_enrollment": "University Academics",
    "course_schedule": "University Academics",
    "course_scheduling_tool": "University Academics",
    "course_topic": "University Academics",
    "education_settings": "University Academics",  # relabel "Academics Settings"
    "grading_scale": "University Academics",
    "grading_scale_interval": "University Academics",
    "program": "University Academics",
    "program_course": "University Academics",
    "program_enrollment": "University Academics",
    "program_enrollment_course": "University Academics",
    "program_enrollment_fee": "University Academics",
    "program_enrollment_tool": "University Academics",
    "program_enrollment_tool_student": "University Academics",
    "topic": "University Academics",
    "topic_content": "University Academics",
    # Quiz suite — archive candidates (kept in this map so fork script knows destination
    # if archive=False is forced later)
    "quiz": "University Academics",
    "question": "University Academics",
    "quiz_question": "University Academics",
    "quiz_activity": "University Academics",
    "quiz_result": "University Academics",
    "options": "University Academics",
    # === University Student Info ===
    "student": "University Student Info",
    "student_group": "University Student Info",
    "student_group_creation_tool": "University Student Info",
    "student_group_creation_tool_course": "University Student Info",
    "student_group_instructor": "University Student Info",
    "student_group_student": "University Student Info",
    "student_attendance": "University Student Info",
    "student_attendance_tool": "University Student Info",
    "student_log": "University Student Info",
    "student_leave_application": "University Student Info",
    "student_language": "University Student Info",
    "student_sibling": "University Student Info",
    "student_siblings": "University Student Info",
    "student_report_generation_tool": "University Student Info",
    "guardian": "University Student Info",
    "guardian_interest": "University Student Info",
    "guardian_student": "University Student Info",
    "student_guardian": "University Student Info",
    "room": "University Student Info",
    # === University Admissions ===
    "student_applicant": "University Admissions",
    "student_admission": "University Admissions",
    "student_admission_program": "University Admissions",
    "student_category": "University Admissions",
    "student_batch_name": "University Admissions",
    # === Faculty Management ===
    "instructor": "Faculty Management",
    "instructor_log": "Faculty Management",
    # === University Finance ===
    "fees": "University Finance",
    "fee_category": "University Finance",
    "fee_component": "University Finance",
    "fee_schedule": "University Finance",
    "fee_schedule_program": "University Finance",
    "fee_schedule_student_group": "University Finance",
    "fee_structure": "University Finance",
    "program_fee": "University Finance",
    # === University Hostel ===
    "school_house": "University Hostel",  # relabel "Hostel House"
}

# Doctypes whose Education suite usage audit shows zero references in university_erp.
# Per RESEARCH ARCHIVE_CANDIDATES (HIGH/MEDIUM confidence).
ARCHIVE_CANDIDATES = {
    "quiz",
    "question",
    "quiz_question",
    "quiz_activity",
    "quiz_result",
    "options",
    "article",
    "student_report_generation_tool",
}

# Doctypes whose university_erp `overrides/*.py` collapses into the forked controller.
OVERRIDE_COLLAPSE = {
    "student",
    "course",
    "program",
    "fees",
    "assessment_result",
    "student_applicant",
}

# Relabels per D-03.
RELABELS = {
    "school_house": "Hostel House",
    "education_settings": "Academics Settings",
}

# Child-table -> parent map (for the "Parent if child" column). Drawn from RESEARCH Pitfall 2.
CHILD_PARENT = {
    "assessment_plan_criteria": "Assessment Plan",
    "assessment_result_detail": "Assessment Result",
    "course_assessment_criteria": "Course",
    "course_topic": "Course",
    "fee_component": "Fees / Fee Structure",
    "fee_schedule_program": "Fee Schedule",
    "fee_schedule_student_group": "Fee Schedule",
    "grading_scale_interval": "Grading Scale",
    "guardian_interest": "Guardian",
    "guardian_student": "Guardian",
    "instructor_log": "Instructor",
    "options": "Question",
    "program_course": "Program",
    "program_enrollment_course": "Program Enrollment",
    "program_enrollment_fee": "Program Enrollment",
    "program_enrollment_tool_student": "Program Enrollment Tool",
    "program_fee": "Program",
    "quiz_question": "Quiz",
    "quiz_result": "Quiz Activity",
    "student_admission_program": "Student Admission",
    "student_group_creation_tool_course": "Student Group Creation Tool",
    "student_group_instructor": "Student Group",
    "student_group_student": "Student Group",
    "student_guardian": "Student",
    "student_sibling": "Student",
    "student_siblings": "Student",
    "topic_content": "Topic",
}


def module_to_dirname(mod_display: str) -> str:
    return mod_display.lower().replace(" ", "_")


def _verdict_for(dt_dir: str) -> str:
    if dt_dir in ARCHIVE_CANDIDATES:
        return "ARCHIVE candidate"
    if dt_dir in OVERRIDE_COLLAPSE:
        return "FORK + MERGE override"
    if dt_dir in RELABELS:
        return f'FORK + RELABEL ("{RELABELS[dt_dir]}")'
    return "FORK"


def _rationale_for(dt_dir: str, istable: int) -> str:
    if dt_dir in ARCHIVE_CANDIDATES:
        return "Audit shows zero references in university_erp"
    if dt_dir in OVERRIDE_COLLAPSE:
        return "Collapses an existing university_erp override class"
    if dt_dir in RELABELS:
        return f'Relabel to "{RELABELS[dt_dir]}" per D-03'
    if istable:
        return f"Child table of {CHILD_PARENT.get(dt_dir, 'parent doctype')}"
    return "Core doctype; required by university_erp consumers"


def _scan_education_doctypes():
    """Return list of (dt_dir, name, istable, current_module) for every directory under
    EDU_DOCTYPE_ROOT that contains <dt>.json."""
    rows = []
    for entry in sorted(os.listdir(EDU_DOCTYPE_ROOT)):
        if entry in ("__pycache__", "__init__.py"):
            continue
        subdir = os.path.join(EDU_DOCTYPE_ROOT, entry)
        if not os.path.isdir(subdir):
            continue
        json_path = os.path.join(subdir, f"{entry}.json")
        if not os.path.exists(json_path):
            continue
        with open(json_path) as f:
            doc = json.load(f)
        rows.append(
            (
                entry,
                doc.get("name", entry),
                int(doc.get("istable", 0)),
                doc.get("module", ""),
            )
        )
    return rows


def _resolve_quiz_question_collision():
    edu_json = os.path.join(EDU_DOCTYPE_ROOT, "quiz_question", "quiz_question.json")
    lms_json = os.path.join(
        UNI_ERP_ROOT, "university_lms", "doctype", "quiz_question", "quiz_question.json"
    )
    if not os.path.exists(edu_json):
        return "Quiz Question collision: Education quiz_question.json not found (skipped)."
    if not os.path.exists(lms_json):
        return (
            "Quiz Question collision: university_lms quiz_question.json not found; "
            "no collision possible."
        )
    edu_name = json.load(open(edu_json)).get("name")
    lms_name = json.load(open(lms_json)).get("name")
    if edu_name == lms_name == "Quiz Question":
        return (
            f"**Quiz Question table-name COLLISION CONFIRMED** — "
            f"Education `name=\"{edu_name}\"`, university_lms `name=\"{lms_name}\"`. "
            f"Both define `tabQuiz Question`. **Resolution:** Education's quiz suite is already a "
            f"RESEARCH ARCHIVE candidate (zero references in university_erp). "
            f"Plan 02 moves `quiz`, `question`, `quiz_question`, `quiz_activity`, `quiz_result`, "
            f"`options` to `university_academics/_archived/` instead of `doctype/`. "
            f"Archived doctypes are not registered with Frappe, so the `tabQuiz Question` collision "
            f"never materializes. university_lms's Quiz Question remains the only Quiz Question doctype."
        )
    return (
        f"No collision — Education quiz_question name=\"{edu_name}\", "
        f"university_lms quiz_question name=\"{lms_name}\"; both fork safely."
    )


def _resolve_student_sibling_duplication():
    p1 = os.path.join(EDU_DOCTYPE_ROOT, "student_sibling", "student_sibling.json")
    p2 = os.path.join(EDU_DOCTYPE_ROOT, "student_siblings", "student_siblings.json")
    f1 = [f.get("fieldname") for f in json.load(open(p1)).get("fields", [])]
    f2 = [f.get("fieldname") for f in json.load(open(p2)).get("fields", [])]
    if f1 == f2:
        return (
            f"`student_sibling` vs `student_siblings`: **IDENTICAL schemas** "
            f"({len(f1)} fields each). Fork both, deprecate `student_sibling` in a follow-up."
        )
    only1 = [x for x in f1 if x not in f2]
    only2 = [x for x in f2 if x not in f1]
    return (
        f"`student_sibling` vs `student_siblings`: **DISTINCT schemas**.\n"
        f"  - `student_sibling` fields ({len(f1)}): {f1}\n"
        f"  - `student_siblings` fields ({len(f2)}): {f2}\n"
        f"  - Only in `student_sibling`: {only1}\n"
        f"  - Only in `student_siblings`: {only2}\n"
        f"  - **Resolution:** Fork both. `student_sibling` is the richer schema "
        f"(institute / program / DOB / student-link) used by Student doctype; "
        f"`student_siblings` is a sparse legacy table. Keep both in `university_student_info`; "
        f"deprecation decision deferred to a follow-up."
    )


def _destination_collisions(rows):
    """Return list of (dt_dir, dst_path, fields_only_in_dst) for destinations that already exist."""
    collisions = []
    for dt_dir, _name, _istable, _mod in rows:
        target_mod = DOCTYPE_MODULE_MAP.get(dt_dir)
        if not target_mod:
            continue
        mod_dir = module_to_dirname(target_mod)
        dst_path = os.path.join(
            UNI_ERP_ROOT, mod_dir, "doctype", dt_dir, f"{dt_dir}.json"
        )
        if not os.path.exists(dst_path):
            continue
        src_path = os.path.join(EDU_DOCTYPE_ROOT, dt_dir, f"{dt_dir}.json")
        dst_fields = {
            f.get("fieldname") for f in json.load(open(dst_path)).get("fields", [])
        }
        src_fields = {
            f.get("fieldname") for f in json.load(open(src_path)).get("fields", [])
        }
        only_in_dst = sorted(dst_fields - src_fields)
        collisions.append((dt_dir, os.path.relpath(dst_path, REPO_ROOT), only_in_dst))
    return collisions


def audit_education_doctypes():
    rows = _scan_education_doctypes()
    unmapped = [r for r in rows if r[0] not in DOCTYPE_MODULE_MAP]
    quiz_resolution = _resolve_quiz_question_collision()
    sib_resolution = _resolve_student_sibling_duplication()
    dest_collisions = _destination_collisions(rows)

    os.makedirs(PHASE_DIR, exist_ok=True)
    lines = []
    lines.append("# Education Doctype Mapping (Phase 03.3.1)")
    lines.append("")
    lines.append(
        "_Generated by `university_erp.scripts.audit_education_doctypes`. "
        "Source of truth for plans 03.3.1-02..06._"
    )
    lines.append("")
    lines.append(f"**Doctype directories scanned:** {len(rows)}")
    lines.append(f"**Mapped to a destination module:** {len(rows) - len(unmapped)}")
    lines.append(f"**UNMAPPED (must be 0):** {len(unmapped)}")
    lines.append("")
    lines.append(
        "| # | DocType | EduDir | istable | TargetModule | Verdict | Parent | Rationale |"
    )
    lines.append(
        "|---|---------|--------|---------|--------------|---------|--------|-----------|"
    )
    for i, (dt_dir, name, istable, _mod) in enumerate(rows, 1):
        target = DOCTYPE_MODULE_MAP.get(dt_dir, "UNMAPPED")
        verdict = _verdict_for(dt_dir) if target != "UNMAPPED" else "UNMAPPED"
        parent = CHILD_PARENT.get(dt_dir, "—") if istable else "—"
        rationale = _rationale_for(dt_dir, istable)
        lines.append(
            f"| {i} | {name} | {dt_dir} | {istable} | {target} | {verdict} | {parent} | {rationale} |"
        )
    lines.append("")
    lines.append("## UNMAPPED")
    lines.append("")
    if unmapped:
        for dt_dir, name, istable, _mod in unmapped:
            lines.append(f"- `{dt_dir}` (name=\"{name}\", istable={istable})")
    else:
        lines.append("None — every Education doctype directory has a locked destination module.")
    lines.append("")
    lines.append("## Open Questions Resolved")
    lines.append("")
    lines.append("### 1. Quiz Question table-name collision (Education vs university_lms)")
    lines.append("")
    lines.append(quiz_resolution)
    lines.append("")
    lines.append("### 2. `student_sibling` vs `student_siblings` duplication")
    lines.append("")
    lines.append(sib_resolution)
    lines.append("")
    lines.append("## Destination Collisions (D-04 merge required)")
    lines.append("")
    if not dest_collisions:
        lines.append(
            "None — no university_erp doctypes at fork destinations. "
            "D-04 merge satisfied by override collapse in Plan 05."
        )
    else:
        lines.append(
            "| DocType | Destination Path | university_erp-only fieldnames | Merge Strategy |"
        )
        lines.append(
            "|---------|------------------|---------------------------------|----------------|"
        )
        for dt_dir, dst_path, only_in_dst in dest_collisions:
            extras = ", ".join(only_in_dst) if only_in_dst else "(none)"
            lines.append(
                f"| {dt_dir} | `{dst_path}` | {extras} | "
                f"Pre-fork: extract university_erp-only fields → re-inject into forked JSON "
                f"via post-copy patch in plan 02/03/04 fork script step |"
            )
    lines.append("")
    lines.append("## DOCTYPE_MODULE_MAP (verbatim — mirrored in fork_education_module.py)")
    lines.append("")
    lines.append("```python")
    lines.append("DOCTYPE_MODULE_MAP = {")
    for dt_dir, mod in DOCTYPE_MODULE_MAP.items():
        lines.append(f'    "{dt_dir}": "{mod}",')
    lines.append("}")
    lines.append("```")
    lines.append("")

    with open(MAPPING_OUT, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"DOCTYPE_MAPPING written: {MAPPING_OUT}")
    print(f"Rows: {len(rows)}; Unmapped: {len(unmapped)}; Destination collisions: {len(dest_collisions)}")
    if unmapped:
        print("UNMAPPED entries:", [r[0] for r in unmapped])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(audit_education_doctypes())

"""
fork_education_module.py

Phase 03.3.1 fork script. Plans 02/03/04 import this module and invoke
`fork_subset(...)` with the doctype subset they own. Plan 06 invokes
`run_full_fork()` at the end for completeness.

Pattern mirrors `fork_accounts_module.py` (Phase 03.3-01) but with a PER-DOCTYPE
destination map instead of a single-module target.

Run from frappe-bench/apps/university_erp/:
    python -m university_erp.scripts.fork_education_module
"""

import json
import os
import shutil

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(os.path.abspath(__file__))
# scripts/ -> university_erp/ -> university_erp/ (app root)
APP_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
# app root -> apps/ -> bench root
BENCH_APPS = os.path.abspath(os.path.join(APP_ROOT, ".."))
EDU_DOCTYPE_SRC = os.path.join(
    BENCH_APPS, "education", "education", "education", "doctype"
)
UNI_ERP_PKG = os.path.join(APP_ROOT, "university_erp")  # the inner package

# --------------------------------------------------------------------------- #
# DOCTYPE_MODULE_MAP — locked destination map; mirrors DOCTYPE_MAPPING.md
# Keep this list in sync with audit_education_doctypes.DOCTYPE_MODULE_MAP.
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
    "education_settings": "University Academics",
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
    "school_house": "University Hostel",
}

# Per RESEARCH.md ARCHIVE_CANDIDATES — copied under `_archived/` instead of `doctype/`.
ARCHIVE_DOCTYPES = {
    "quiz",
    "question",
    "quiz_question",
    "quiz_activity",
    "quiz_result",
    "options",
    "article",
    "student_report_generation_tool",
}


def module_to_dirname(mod_display: str) -> str:
    return mod_display.lower().replace(" ", "_")


def _clean_destination(dst: str) -> None:
    """Strip test_*.py and __pycache__ from a copied doctype directory."""
    for root, dirs, files in os.walk(dst):
        for f in files:
            if f.startswith("test_") or f.endswith(".pyc"):
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                dirs.remove(d)


def copy_doctype_to_module(dt_dir: str, target_module_display: str, archive: bool = False) -> str:
    """Copy education/doctype/<dt_dir> to university_erp/<mod_dir>/{doctype|_archived}/<dt_dir>.

    Rewrites the destination JSON's `module` field to `target_module_display`.
    Returns the destination directory path.
    """
    src = os.path.join(EDU_DOCTYPE_SRC, dt_dir)
    if not os.path.isdir(src):
        raise FileNotFoundError(f"Source doctype not found: {src}")

    mod_dir = module_to_dirname(target_module_display)
    sub = "_archived" if archive else "doctype"
    dst_root = os.path.join(UNI_ERP_PKG, mod_dir, sub)
    os.makedirs(dst_root, exist_ok=True)
    dst = os.path.join(dst_root, dt_dir)

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    _clean_destination(dst)

    json_file = os.path.join(dst, f"{dt_dir}.json")
    if os.path.exists(json_file):
        with open(json_file) as f:
            doc = json.load(f)
        doc["module"] = target_module_display
        with open(json_file, "w") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
    return dst


def rewrite_imports_in_file(filepath: str) -> None:
    """Rewrite `from education.education.doctype.<dt>.` and `import education.education.doctype.<dt>.`
    to point at the forked destination. Falls back to module-prefix catch-alls last."""
    with open(filepath) as f:
        content = f.read()
    original = content

    # Per-doctype specific redirects (longest/most specific first)
    for dt, mod in DOCTYPE_MODULE_MAP.items():
        mod_dir = module_to_dirname(mod)
        content = content.replace(
            f"from education.education.doctype.{dt}.",
            f"from university_erp.{mod_dir}.doctype.{dt}.",
        )
        content = content.replace(
            f"import education.education.doctype.{dt}.",
            f"import university_erp.{mod_dir}.doctype.{dt}.",
        )

    # Catch-alls (applied AFTER the specific replacements)
    content = content.replace("from education.education.", "from university_erp.")
    content = content.replace("from education.utils", "from university_erp.utils")

    if content != original:
        with open(filepath, "w") as f:
            f.write(content)


def _walk_and_rewrite_module(mod_display: str) -> None:
    """Walk both doctype/ and _archived/ subtrees of a module and rewrite all .py imports."""
    mod_dir = module_to_dirname(mod_display)
    for sub in ("doctype", "_archived"):
        root_path = os.path.join(UNI_ERP_PKG, mod_dir, sub)
        if not os.path.isdir(root_path):
            continue
        for root, _dirs, files in os.walk(root_path):
            for fn in files:
                if fn.endswith(".py"):
                    rewrite_imports_in_file(os.path.join(root, fn))


def fork_subset(doctype_names) -> list:
    """Fork a subset of Education doctypes. Plans 02/03/04 call this with their domain subset.

    Args:
        doctype_names: iterable of doctype dir names (keys of DOCTYPE_MODULE_MAP)

    Returns:
        list of destination paths that were created/overwritten.
    """
    copied = []
    affected_modules = set()
    for dt in doctype_names:
        if dt not in DOCTYPE_MODULE_MAP:
            raise KeyError(f"Doctype '{dt}' not in DOCTYPE_MODULE_MAP")
        mod = DOCTYPE_MODULE_MAP[dt]
        dst = copy_doctype_to_module(dt, mod, archive=(dt in ARCHIVE_DOCTYPES))
        copied.append(dst)
        affected_modules.add(mod)
    # Rewrite imports across all touched modules (covers cross-doctype refs)
    for mod in affected_modules:
        _walk_and_rewrite_module(mod)
    return copied


def run_full_fork() -> None:
    """Fork ALL 71 doctypes per DOCTYPE_MODULE_MAP. Archives go under _archived/."""
    for dt, mod in DOCTYPE_MODULE_MAP.items():
        copy_doctype_to_module(dt, mod, archive=(dt in ARCHIVE_DOCTYPES))
    for mod in set(DOCTYPE_MODULE_MAP.values()):
        _walk_and_rewrite_module(mod)
    print(f"Forked {len(DOCTYPE_MODULE_MAP)} doctypes; archived {len(ARCHIVE_DOCTYPES)}.")


if __name__ == "__main__":
    run_full_fork()

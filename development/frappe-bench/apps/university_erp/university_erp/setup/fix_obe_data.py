"""Fix OBE data issues:
1. CO Attainment: set academic_year where NULL
2. Survey PO Rating: seed child rows for each OBE Survey
"""
import frappe
import uuid
import random
from frappe.utils import nowdate


def run():
    frappe.flags.ignore_permissions = True
    random.seed(2026)

    # 1. Fix CO Attainment academic_year
    frappe.db.sql(
        "UPDATE `tabCO Attainment` SET academic_year='2026-2027' WHERE academic_year IS NULL OR academic_year=''"
    )
    fixed = frappe.db.sql(
        "SELECT COUNT(*) as cnt FROM `tabCO Attainment` WHERE academic_year='2026-2027'",
        as_dict=True
    )[0].cnt
    print(f"CO Attainment: set academic_year on {fixed} records")

    # 2. Seed Survey PO Rating rows for each submitted OBE Survey
    surveys = frappe.db.sql(
        "SELECT name, program FROM `tabOBE Survey` WHERE status IN ('Submitted', 'Verified')",
        as_dict=True
    )
    print(f"\nFound {len(surveys)} submitted OBE Surveys")

    # Check Survey PO Rating columns
    cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabSurvey PO Rating`", as_dict=True)]
    print(f"Survey PO Rating cols: {cols}")

    total_inserted = 0
    for survey in surveys:
        # Get POs for this program
        pos = frappe.db.sql(
            "SELECT name, po_code, po_title FROM `tabProgram Outcome` WHERE program=%s ORDER BY is_pso, po_number",
            survey.program, as_dict=True
        )
        if not pos:
            # Try without program filter (use first 12 POs)
            pos = frappe.db.sql(
                "SELECT name, po_code, po_title FROM `tabProgram Outcome` ORDER BY creation LIMIT 12",
                as_dict=True
            )

        if not pos:
            print(f"  {survey.name}: no POs found, skipping")
            continue

        # Check if already has rating rows
        existing = frappe.db.count("Survey PO Rating", {"parent": survey.name})
        if existing > 0:
            print(f"  {survey.name}: already has {existing} rating rows, skipping")
            continue

        # Insert rating rows
        for idx, po in enumerate(pos, 1):
            # Generate realistic rating (1-5 scale, biased toward 3-5)
            rating = random.choices([1, 2, 3, 4, 5], weights=[2, 5, 20, 40, 33])[0]
            row_name = uuid.uuid4().hex[:10]

            frappe.db.sql("""
                INSERT INTO `tabSurvey PO Rating`
                (name, creation, modified, modified_by, owner, docstatus, idx,
                 program_outcome, po_code, rating, parent, parentfield, parenttype)
                VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator', 0, %s,
                        %s, %s, %s, %s, 'po_ratings', 'OBE Survey')
            """, (row_name, idx, po.name, po.po_code, rating, survey.name))
            total_inserted += 1

        print(f"  {survey.name} ({survey.program}): inserted {len(pos)} PO rating rows")

    frappe.db.commit()
    print(f"\nTotal Survey PO Rating rows inserted: {total_inserted}")

    # Verify
    verify = frappe.db.sql(
        "SELECT os.name, COUNT(spr.name) as ratings "
        "FROM `tabOBE Survey` os "
        "LEFT JOIN `tabSurvey PO Rating` spr ON spr.parent = os.name "
        "WHERE os.status IN ('Submitted','Verified') "
        "GROUP BY os.name",
        as_dict=True
    )
    print("\nVerification:")
    for r in verify:
        print(f"  {r['name']}: {r['ratings']} rating rows")

    # Test the Survey Analysis report logic manually
    print("\n=== Testing Survey Analysis query ===")
    survey_names = [s.name for s in surveys]
    if survey_names:
        ratings = frappe.db.sql(
            "SELECT program_outcome, po_code, rating FROM `tabSurvey PO Rating` WHERE parent=%s LIMIT 5",
            survey_names[0], as_dict=True
        )
        print(f"Sample ratings for {survey_names[0]}: {ratings}")

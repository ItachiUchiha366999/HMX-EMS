"""Probe data needed for OBE reports to find correct default filter values."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # CO Attainment Report — needs: course, academic_year, academic_term (all optional)
    print("=== CO Attainment ===")
    co_att = frappe.db.sql("""
        SELECT ca.name, ca.course, ca.academic_year, ca.academic_term, ca.docstatus,
               COUNT(cfa.name) as final_entries
        FROM `tabCO Attainment` ca
        LEFT JOIN `tabCO Final Attainment` cfa ON cfa.parent = ca.name
        WHERE ca.docstatus = 1
        GROUP BY ca.name
        ORDER BY ca.creation DESC
        LIMIT 5
    """, as_dict=True)
    print(f"  Submitted CO Attainments: {len(co_att)}")
    for r in co_att:
        print(f"    {r['name']}: course={r['course']}, ay={r['academic_year']}, term={r['academic_term']}, final_entries={r['final_entries']}")

    # CO PO Mapping Matrix — needs: program + course (mandatory)
    print("\n=== CO PO Mapping ===")
    co_po = frappe.db.sql("""
        SELECT cp.name, cp.course, cp.program, cp.academic_term, cp.docstatus,
               COUNT(cpe.name) as entries
        FROM `tabCO PO Mapping` cp
        LEFT JOIN `tabCO PO Mapping Entry` cpe ON cpe.parent = cp.name
        WHERE cp.docstatus = 1
        GROUP BY cp.name
        ORDER BY cp.creation DESC
        LIMIT 5
    """, as_dict=True)
    print(f"  Submitted CO PO Mappings: {len(co_po)}")
    for r in co_po:
        print(f"    {r['name']}: course={r['course']}, program={r['program']}, entries={r['entries']}")

    # Program Attainment Summary — needs: academic_year (optional)
    print("\n=== PO Attainment ===")
    po_att = frappe.db.sql("""
        SELECT name, program, academic_year, total_pos, pos_achieved, overall_attainment, nba_compliance_score, status
        FROM `tabPO Attainment`
        WHERE docstatus = 1
        LIMIT 5
    """, as_dict=True)
    print(f"  Submitted PO Attainments: {len(po_att)}")
    for r in po_att:
        print(f"    {r['name']}: {r['program']}, ay={r['academic_year']}, "
              f"nba={r['nba_compliance_score']}, status={r['status']}")

    # Survey Analysis — needs: program, survey_type, academic_year (all optional)
    print("\n=== OBE Survey ===")
    surveys = frappe.db.sql("""
        SELECT os.name, os.program, os.survey_type, os.academic_year, os.status,
               COUNT(spr.name) as rating_rows
        FROM `tabOBE Survey` os
        LEFT JOIN `tabSurvey PO Rating` spr ON spr.parent = os.name
        WHERE os.status IN ('Submitted', 'Verified')
        GROUP BY os.name
        ORDER BY os.creation DESC
        LIMIT 5
    """, as_dict=True)
    print(f"  Submitted/Verified OBE Surveys: {len(surveys)}")
    for r in surveys:
        print(f"    {r['name']}: program={r['program']}, type={r['survey_type']}, "
              f"ay={r['academic_year']}, status={r['status']}, rating_rows={r['rating_rows']}")

    # Check Survey PO Rating child table
    spr_count = frappe.db.count("Survey PO Rating")
    print(f"\n  Survey PO Rating rows total: {spr_count}")

    spr_sample = frappe.db.sql(
        "SELECT * FROM `tabSurvey PO Rating` LIMIT 3", as_dict=True
    )
    print(f"  Survey PO Rating sample: {spr_sample}")

    # Check OBE Survey fields
    obe_cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabOBE Survey`", as_dict=True)]
    print(f"\n  OBE Survey cols: {obe_cols}")

    # Check Feedback Response for survey data
    fr_count = frappe.db.count("Feedback Response")
    print(f"\n  Feedback Response rows: {fr_count}")
    fr_sample = frappe.db.sql(
        "SELECT * FROM `tabFeedback Response` LIMIT 2", as_dict=True
    )
    print(f"  Feedback Response sample: {fr_sample}")

"""Probe exact DB values needed for each report's default filters."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    print("=== CO Attainment Report ===")
    co_att = frappe.db.sql("""
        SELECT ca.name, ca.course, ca.academic_year, ca.academic_term, ca.docstatus,
               COUNT(cfa.name) as final_entries
        FROM `tabCO Attainment` ca
        LEFT JOIN `tabCO Final Attainment` cfa ON cfa.parent = ca.name
        WHERE ca.docstatus = 1
        GROUP BY ca.name ORDER BY ca.creation DESC LIMIT 3
    """, as_dict=True)
    for r in co_att:
        print(f"  course={r['course']!r}, ay={r['academic_year']!r}, term={r['academic_term']!r}, entries={r['final_entries']}")

    print("\n=== CO-PO Mapping Matrix ===")
    co_po = frappe.db.sql("""
        SELECT cp.course, cp.program, cp.academic_term, COUNT(cpe.name) as entries
        FROM `tabCO PO Mapping` cp
        LEFT JOIN `tabCO PO Mapping Entry` cpe ON cpe.parent = cp.name
        WHERE cp.docstatus = 1
        GROUP BY cp.name ORDER BY entries DESC LIMIT 5
    """, as_dict=True)
    for r in co_po:
        print(f"  program={r['program']!r}, course={r['course']!r}, term={r['academic_term']!r}, entries={r['entries']}")

    print("\n=== Program Attainment Summary ===")
    po_att = frappe.db.sql("""
        SELECT program, academic_year, department, total_pos, pos_achieved, overall_attainment, nba_compliance_score, status
        FROM `tabPO Attainment` WHERE docstatus=1 ORDER BY nba_compliance_score DESC LIMIT 5
    """, as_dict=True)
    for r in po_att:
        print(f"  program={r['program']!r}, ay={r['academic_year']!r}, dept={r['department']!r}, nba={r['nba_compliance_score']}")

    print("\n=== Survey Analysis Report ===")
    surveys = frappe.db.sql("""
        SELECT os.name, os.program, os.survey_type, os.academic_year, os.status,
               COUNT(spr.name) as ratings
        FROM `tabOBE Survey` os
        LEFT JOIN `tabSurvey PO Rating` spr ON spr.parent = os.name
        WHERE os.status IN ('Submitted','Verified')
        GROUP BY os.name ORDER BY ratings DESC LIMIT 5
    """, as_dict=True)
    for r in surveys:
        print(f"  program={r['program']!r}, type={r['survey_type']!r}, ay={r['academic_year']!r}, ratings={r['ratings']}")

    print("\n=== Internal Assessment Summary ===")
    ia = frappe.db.sql("""
        SELECT ia.course, ia.academic_year, ia.academic_term,
               COUNT(ias.name) as score_rows
        FROM `tabInternal Assessment` ia
        LEFT JOIN `tabInternal Assessment Score` ias ON ias.parent = ia.name
        WHERE ia.docstatus=1
        GROUP BY ia.name ORDER BY score_rows DESC LIMIT 5
    """, as_dict=True)
    for r in ia:
        print(f"  course={r['course']!r}, ay={r['academic_year']!r}, term={r['academic_term']!r}, scores={r['score_rows']}")

    print("\n=== PO Attainment Report ===")
    po_rep = frappe.db.sql("""
        SELECT pa.name, pa.program, pa.academic_year,
               COUNT(pae.name) as entry_rows
        FROM `tabPO Attainment` pa
        LEFT JOIN `tabPO Attainment Entry` pae ON pae.parent = pa.name
        WHERE pa.docstatus=1
        GROUP BY pa.name ORDER BY entry_rows DESC LIMIT 3
    """, as_dict=True)
    for r in po_rep:
        print(f"  name={r['name']!r}, program={r['program']!r}, ay={r['academic_year']!r}, entries={r['entry_rows']}")

    print("\n=== Placement Reports ===")
    pd = frappe.db.sql("""
        SELECT pd.name, pd.company, pd.academic_year,
               COUNT(pa.name) as apps, SUM(pa.status='Placed') as placed
        FROM `tabPlacement Drive` pd
        LEFT JOIN `tabPlacement Application` pa ON pa.placement_drive = pd.name
        WHERE pd.docstatus < 2
        GROUP BY pd.name ORDER BY placed DESC LIMIT 3
    """, as_dict=True)
    for r in pd:
        print(f"  drive={r['name']!r}, company={r['company']!r}, ay={r['academic_year']!r}, apps={r['apps']}, placed={r['placed']}")

    print("\n=== Hostel Occupancy ===")
    hb = frappe.db.sql("""
        SELECT hb.name, hb.hostel_name, COUNT(hr.name) as rooms,
               SUM(CASE WHEN ha.name IS NOT NULL THEN 1 ELSE 0 END) as occupied
        FROM `tabHostel Building` hb
        LEFT JOIN `tabHostel Room` hr ON hr.hostel_building = hb.name
        LEFT JOIN `tabHostel Allocation` ha ON ha.hostel_room = hr.name AND ha.docstatus=1
        GROUP BY hb.name ORDER BY occupied DESC LIMIT 3
    """, as_dict=True)
    for r in hb:
        print(f"  hostel={r['name']!r}, name={r['hostel_name']!r}, rooms={r['rooms']}, occupied={r['occupied']}")

    print("\n=== Examination Result Analysis ===")
    era = frappe.db.sql("""
        SELECT es.name, es.exam_name, es.academic_year, es.academic_term,
               COUNT(sea.name) as attempts
        FROM `tabExam Schedule` es
        LEFT JOIN `tabStudent Exam Attempt` sea ON sea.exam_schedule = es.name
        WHERE es.docstatus = 1
        GROUP BY es.name ORDER BY attempts DESC LIMIT 3
    """, as_dict=True)
    for r in era:
        print(f"  exam={r['name']!r}, name={r['exam_name']!r}, ay={r['academic_year']!r}, attempts={r['attempts']}")

    print("\n=== Library Circulation ===")
    lt = frappe.db.sql("""
        SELECT transaction_type, COUNT(*) as cnt, MIN(transaction_date) as min_d, MAX(transaction_date) as max_d
        FROM `tabLibrary Transaction` GROUP BY transaction_type
    """, as_dict=True)
    for r in lt:
        print(f"  type={r['transaction_type']!r}, cnt={r['cnt']}, from={r['min_d']}, to={r['max_d']}")

    print("\n=== Exact Academic Year / Term names in DB ===")
    ays = frappe.db.sql("SELECT name FROM `tabAcademic Year` ORDER BY name", as_dict=True)
    print("  AYs:", [r['name'] for r in ays])
    ats = frappe.db.sql("SELECT name, academic_year FROM `tabAcademic Term` ORDER BY name", as_dict=True)
    print("  Terms:", [(r['name'], r['academic_year']) for r in ats])

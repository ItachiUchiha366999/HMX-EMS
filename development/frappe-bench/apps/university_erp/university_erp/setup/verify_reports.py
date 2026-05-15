"""Verify placement and OBE reports return data with their exact query logic."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # --- Company Wise Placement ---
    print("=== Company Wise Placement ===")
    company_data = frappe.db.sql("""
        SELECT
            pa.company,
            COUNT(DISTINCT pa.student) as students_applied,
            SUM(CASE WHEN pa.status = 'Placed' THEN 1 ELSE 0 END) as placed,
            AVG(CASE WHEN pa.status = 'Placed' THEN pa.offered_ctc ELSE NULL END) as avg_ctc,
            MAX(pa.offered_ctc) as max_ctc
        FROM `tabPlacement Application` pa
        INNER JOIN `tabPlacement Company` pc ON pa.company = pc.name
        WHERE pa.docstatus < 2
        GROUP BY pa.company
        ORDER BY placed DESC
        LIMIT 5
    """, as_dict=True)
    print(f"  Rows: {len(company_data)}")
    for r in company_data:
        print(f"  {r['company']}: applied={r['students_applied']}, placed={r['placed']}, avg_ctc={r['avg_ctc']}")

    # --- Program Wise Placement ---
    print("\n=== Program Wise Placement ===")
    prog_data = frappe.db.sql("""
        SELECT
            s.custom_program as program,
            COUNT(DISTINCT pa.student) as students_applied,
            SUM(CASE WHEN pa.status = 'Placed' THEN 1 ELSE 0 END) as placed,
            COUNT(DISTINCT s.name) as total_students
        FROM `tabPlacement Application` pa
        INNER JOIN `tabStudent` s ON pa.student = s.name
        WHERE pa.docstatus < 2
        GROUP BY s.custom_program
        ORDER BY placed DESC
        LIMIT 5
    """, as_dict=True)
    print(f"  Rows: {len(prog_data)}")
    for r in prog_data:
        print(f"  {r['program']}: applied={r['students_applied']}, placed={r['placed']}")

    # --- Placement Trend ---
    print("\n=== Placement Trend ===")
    trend_data = frappe.db.sql("""
        SELECT
            pd.academic_year,
            COUNT(DISTINCT pa.student) as total_students_placed,
            AVG(pa.offered_ctc) as avg_package,
            MAX(pa.offered_ctc) as highest_package
        FROM `tabPlacement Drive` pd
        INNER JOIN `tabPlacement Application` pa ON pa.placement_drive = pd.name
        WHERE pa.status = 'Placed'
        AND pd.docstatus < 2
        GROUP BY pd.academic_year
        ORDER BY pd.academic_year
    """, as_dict=True)
    print(f"  Rows: {len(trend_data)}")
    for r in trend_data:
        print(f"  {r['academic_year']}: placed={r['total_students_placed']}, avg_pkg={r['avg_package']}")

    # --- Program Attainment Summary ---
    print("\n=== Program Attainment Summary ===")
    po_data = frappe.db.sql("""
        SELECT program, department, academic_year, total_pos, pos_achieved, overall_attainment, nba_compliance_score, status
        FROM `tabPO Attainment`
        WHERE docstatus=1
        LIMIT 3
    """, as_dict=True)
    print(f"  Rows: {len(po_data)}")
    for r in po_data:
        print(f"  {r['program']}: total_pos={r['total_pos']}, pos_achieved={r['pos_achieved']}, "
              f"overall={r['overall_attainment']}, nba={r['nba_compliance_score']}, status={r['status']}")

    # --- NAAC Criterion Progress ---
    print("\n=== NAAC Criterion Progress ===")
    naac_count = frappe.db.count("NAAC Metric")
    print(f"  NAAC Metric rows: {naac_count}")
    naac_sample = frappe.db.sql(
        "SELECT criterion, status, score FROM `tabNAAC Metric` LIMIT 3",
        as_dict=True
    )
    print(f"  Sample: {naac_sample}")

    # --- NIRF Parameter Report ---
    print("\n=== NIRF Parameter Report ===")
    nirf_data = frappe.db.sql(
        "SELECT name, ranking_year, category FROM `tabNIRF Data` LIMIT 3",
        as_dict=True
    )
    print(f"  NIRF Data rows: {frappe.db.count('NIRF Data')}")
    print(f"  Sample: {nirf_data}")

    # --- Internal Assessment Summary ---
    print("\n=== Internal Assessment Summary ===")
    ia_sample = frappe.db.sql("""
        SELECT course, academic_year, academic_term, docstatus
        FROM `tabInternal Assessment`
        WHERE docstatus=1
        LIMIT 3
    """, as_dict=True)
    print(f"  IA rows (submitted): {frappe.db.count('Internal Assessment', {'docstatus': 1})}")
    print(f"  Sample: {ia_sample}")

    score_count = frappe.db.count("Internal Assessment Score")
    print(f"  IA Score child rows: {score_count}")

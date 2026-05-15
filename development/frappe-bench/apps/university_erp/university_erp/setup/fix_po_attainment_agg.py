"""Fix PO Attainment aggregate fields from existing child rows."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Get all submitted PO Attainments
    attainments = frappe.db.sql(
        "SELECT name, program FROM `tabPO Attainment` WHERE docstatus=1",
        as_dict=True
    )
    print(f"Found {len(attainments)} submitted PO Attainments to update")

    updated = 0
    for att in attainments:
        # Count total POs for this program from child table
        entry_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_pos,
                SUM(CASE WHEN achieved=1 THEN 1 ELSE 0 END) as pos_achieved,
                AVG(attainment_percent) as avg_direct,
                AVG(CASE WHEN is_pso=1 THEN attainment_percent ELSE NULL END) as avg_pso_pct,
                SUM(CASE WHEN is_pso=1 AND achieved=1 THEN 1 ELSE 0 END) as psos_achieved,
                COUNT(CASE WHEN is_pso=1 THEN 1 ELSE NULL END) as total_psos
            FROM `tabPO Attainment Entry`
            WHERE parent=%s
        """, att.name, as_dict=True)

        # Get final attainment stats from PO Final Entry
        final_stats = frappe.db.sql("""
            SELECT
                AVG(final_attainment) as avg_final,
                AVG(direct_weight) as avg_dw,
                AVG(indirect_weight) as avg_iw
            FROM `tabPO Final Entry`
            WHERE parent=%s
        """, att.name, as_dict=True)

        # Get department from Program
        dept = frappe.db.get_value("Program", att.program, "department") or "Engineering"

        es = entry_stats[0] if entry_stats else {}
        fs = final_stats[0] if final_stats else {}

        total_pos = int(es.get("total_pos") or 0)
        pos_achieved = int(es.get("pos_achieved") or 0)
        total_psos = int(es.get("total_psos") or 0)
        psos_achieved = int(es.get("psos_achieved") or 0)
        avg_direct = float(es.get("avg_direct") or 0)
        avg_final = float(fs.get("avg_final") or avg_direct)
        avg_dw = float(fs.get("avg_dw") or 80)
        avg_iw = float(fs.get("avg_iw") or 20)

        overall_attainment = round(avg_final, 2)

        # NBA compliance: % of POs achieved >= target (60%)
        nba_compliance_score = round((pos_achieved / total_pos * 100) if total_pos else 0, 2)

        # NAAC compliance: slightly different weighting
        naac_compliance_score = round(overall_attainment * 0.4 + nba_compliance_score * 0.6, 2)

        # Status based on nba_compliance
        if nba_compliance_score >= 80:
            status = "Satisfactory"
        elif nba_compliance_score >= 60:
            status = "Needs Improvement"
        else:
            status = "Critical"

        frappe.db.sql("""
            UPDATE `tabPO Attainment`
            SET
                total_pos=%s,
                pos_achieved=%s,
                total_psos=%s,
                psos_achieved=%s,
                avg_direct_attainment=%s,
                avg_indirect_attainment=%s,
                overall_attainment=%s,
                nba_compliance_score=%s,
                naac_compliance_score=%s,
                department=%s,
                status=%s,
                direct_weight=%s,
                indirect_weight=%s
            WHERE name=%s
        """, (
            total_pos, pos_achieved,
            total_psos, psos_achieved,
            round(avg_direct, 2),
            round(avg_final - avg_direct, 2) if avg_final > avg_direct else 0,
            overall_attainment,
            nba_compliance_score,
            naac_compliance_score,
            dept,
            status,
            round(avg_dw, 1),
            round(avg_iw, 1),
            att.name
        ))

        print(f"  {att.name}: total_pos={total_pos}, pos_achieved={pos_achieved}, "
              f"overall={overall_attainment}, nba={nba_compliance_score}, status={status}, dept={dept}")
        updated += 1

    frappe.db.commit()
    print(f"\n=== UPDATED {updated} PO Attainment records ===")

    # Verify
    sample = frappe.db.sql(
        "SELECT name, total_pos, pos_achieved, overall_attainment, nba_compliance_score, status, department "
        "FROM `tabPO Attainment` WHERE docstatus=1 LIMIT 3",
        as_dict=True
    )
    print("Verification sample:", sample)

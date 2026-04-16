"""
Seed CO Final Attainment rows (for CO Attainment Report)
and PO Attainment records with child entries (for PO Attainment Report + Program Attainment Summary).
"""
import frappe
from datetime import date
import random
random.seed(42)

frappe.init(site='university.local', sites_path='/workspace/development/frappe-bench/sites')
frappe.connect()
frappe.set_user('Administrator')
TODAY = date.today()

# ── Part A: CO Final Attainment rows for each CO Attainment ──────────────────
# Each CO Attainment needs a co_final_attainment child table row per CO
# so the CO Attainment Report can find data.

co_attainments = frappe.get_all('CO Attainment', filters={'docstatus': 1},
    fields=['name', 'course', 'academic_term'])
print(f'CO Attainment records: {len(co_attainments)}')

# Check parentfield name
cfa_check = frappe.db.sql("SHOW COLUMNS FROM `tabCO Final Attainment`", as_dict=True)
print('CO Final Attainment cols:', [c['Field'] for c in cfa_check])

# Get meta for CO Attainment table fields
ca_meta = frappe.get_meta('CO Attainment')
table_fields = {f.options: f.fieldname for f in ca_meta.fields if f.fieldtype == 'Table'}
print('CO Attainment table fields:', table_fields)
final_parentfield = table_fields.get('CO Final Attainment', 'co_final_attainment')

for ca in co_attainments:
    # Get the direct attainment rows for this CO Attainment
    direct_rows = frappe.get_all('CO Direct Attainment',
        filters={'parent': ca.name},
        fields=['course_outcome', 'co_code', 'attainment_percent', 'attainment_level',
                'target_percent', 'total_students', 'students_above_target'])

    if not direct_rows:
        continue

    # Clear existing final rows for this parent
    frappe.db.sql(f"DELETE FROM `tabCO Final Attainment` WHERE parent=%s", ca.name)
    frappe.db.commit()

    for dr in direct_rows:
        direct_att = dr.attainment_percent or 0
        indirect_att = random.uniform(55, 75)  # simulate survey/indirect
        direct_weight = 70
        indirect_weight = 30
        final_att = round((direct_att * direct_weight / 100) + (indirect_att * indirect_weight / 100), 2)
        target = dr.target_percent or 60
        achieved = 1 if final_att >= target else 0
        gap = round(max(0, target - final_att), 2)

        # Get co_statement from Course Outcome
        co_doc = frappe.db.get_value('Course Outcome', dr.course_outcome, 'co_statement')

        frappe.db.sql(f"""INSERT INTO `tabCO Final Attainment`
            (name, parent, parenttype, parentfield, idx,
             course_outcome, co_code, co_statement,
             direct_attainment, direct_weight, indirect_attainment, indirect_weight,
             final_attainment, target_attainment, achieved, gap)
            VALUES (%s, %s, 'CO Attainment', %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s)""",
            (frappe.generate_hash(length=10), ca.name, final_parentfield,
             direct_rows.index(dr) + 1,
             dr.course_outcome, dr.co_code or f'CO{direct_rows.index(dr)+1}',
             co_doc or f'Course outcome for {dr.course_outcome}',
             round(direct_att, 2), direct_weight,
             round(indirect_att, 2), indirect_weight,
             final_att, target, achieved, gap))
    frappe.db.commit()
    print(f'  CO Final Attainment rows added for {ca.name}: {len(direct_rows)}')

total_cfa = frappe.db.sql("SELECT COUNT(*) FROM `tabCO Final Attainment`")[0][0]
print(f'Total CO Final Attainment rows: {total_cfa}')

# ── Part B: PO Attainment (1 record for B.Tech CS) ───────────────────────────
program = 'B.Tech Computer Science'
academic_year = '2025-26'

# Clear existing
frappe.db.sql("DELETE FROM `tabPO Attainment` WHERE program=%s AND academic_year=%s", (program, academic_year))
frappe.db.sql("DELETE FROM `tabPO Attainment Entry` WHERE parent LIKE %s", (f'{program}%',))
frappe.db.sql("DELETE FROM `tabPO Final Entry` WHERE parent LIKE %s", (f'{program}%',))
frappe.db.sql("DELETE FROM `tabPO Indirect Entry` WHERE parent LIKE %s", (f'{program}%',))
frappe.db.commit()

# Get POs
pos = frappe.get_all('Program Outcome',
    filters={'program': program, 'status': 'Active'},
    fields=['name', 'po_code', 'po_number', 'po_title', 'is_pso', 'nba_attribute', 'target_attainment'],
    order_by='po_number')
print(f'\nProgram Outcomes for {program}: {len(pos)}')

# Check PO Attainment meta for table fields
pa_meta = frappe.get_meta('PO Attainment')
pa_tables = {f.options: f.fieldname for f in pa_meta.fields if f.fieldtype == 'Table'}
print('PO Attainment table fields:', pa_tables)

# Create PO Attainment doc
doc = frappe.new_doc('PO Attainment')
doc.program = program
doc.academic_year = academic_year
doc.calculation_date = TODAY
doc.status = 'Calculated'
doc.direct_weight = 80
doc.indirect_weight = 20

# Build attainment values per PO
po_attainments = {}
for po in pos:
    # Count contributing COs
    contributing = frappe.db.sql("""
        SELECT COUNT(DISTINCT cpe.course_outcome)
        FROM `tabCO PO Mapping Entry` cpe
        JOIN `tabCO PO Mapping` cpm ON cpe.parent = cpm.name
        WHERE cpe.program_outcome = %s AND cpm.docstatus = 1
    """, po.name)[0][0] or 0

    direct_att = round(random.uniform(55, 80), 2)
    target = po.target_attainment or 60
    achieved = 1 if direct_att >= target else 0

    po_attainments[po.name] = {
        'direct': direct_att, 'target': target,
        'achieved': achieved, 'contributing': contributing
    }

# Add PO Attainment Entry rows (direct attainment per PO)
entry_pf = pa_tables.get('PO Attainment Entry', 'po_attainment_entries')
for i, po in enumerate(pos):
    vals = po_attainments[po.name]
    doc.append(entry_pf if entry_pf in [f.fieldname for f in pa_meta.fields] else 'po_attainment_entries', {
        'program_outcome': po.name,
        'po_code': po.po_code or f'PO{po.po_number}',
        'po_title': po.po_title,
        'is_pso': po.is_pso,
        'contributing_courses': vals['contributing'],
        'attainment_level': round(vals['direct'] / 100 * 3, 2),
        'attainment_percent': vals['direct'],
        'target_attainment': vals['target'],
        'achieved': vals['achieved'],
        'gap': round(max(0, vals['target'] - vals['direct']), 2),
    })

# Add PO Final Entry rows
final_pf = pa_tables.get('PO Final Entry', 'po_final_entries')
all_achieved = 0
for po in pos:
    vals = po_attainments[po.name]
    indirect_att = round(random.uniform(50, 75), 2)
    final_att = round((vals['direct'] * 80 / 100) + (indirect_att * 20 / 100), 2)
    target = vals['target']
    achieved = 1 if final_att >= target else 0
    if achieved:
        all_achieved += 1
    doc.append(final_pf if final_pf in [f.fieldname for f in pa_meta.fields] else 'po_final_entries', {
        'program_outcome': po.name,
        'po_code': po.po_code or f'PO{po.po_number}',
        'po_title': po.po_title,
        'is_pso': po.is_pso,
        'direct_attainment': vals['direct'],
        'direct_weight': 80,
        'indirect_attainment': indirect_att,
        'indirect_weight': 20,
        'final_attainment': final_att,
        'target_attainment': target,
        'achieved': achieved,
        'gap': round(max(0, target - final_att), 2),
    })

# Set summary fields
pos_only = [p for p in pos if not p.is_pso]
psos_only = [p for p in pos if p.is_pso]
doc.total_pos = len(pos_only)
doc.pos_achieved = sum(1 for p in pos_only if po_attainments[p.name]['achieved'])
doc.total_psos = len(psos_only)
doc.psos_achieved = sum(1 for p in psos_only if po_attainments[p.name]['achieved'])
doc.avg_direct_attainment = round(sum(po_attainments[p.name]['direct'] for p in pos) / len(pos), 2)
doc.avg_indirect_attainment = round(random.uniform(55, 70), 2)
doc.overall_attainment = round((doc.avg_direct_attainment * 80 / 100) + (doc.avg_indirect_attainment * 20 / 100), 2)
doc.nba_compliance_score = round(random.uniform(65, 85), 1)
doc.naac_compliance_score = round(random.uniform(60, 80), 1)
doc.department = 'Computer Science'

doc.flags.ignore_validate = True
doc.flags.ignore_links = True
doc.flags.ignore_mandatory = True
doc.insert(ignore_permissions=True)
frappe.db.set_value('PO Attainment', doc.name, 'docstatus', 1)
frappe.db.commit()
print(f'\nPO Attainment created: {doc.name}')

# ── Summary ───────────────────────────────────────────────────────────────────
print('\n=== RESULTS ===')
print(f'CO Final Attainment rows: {frappe.db.sql("SELECT COUNT(*) FROM `tabCO Final Attainment`")[0][0]} (need 30)')
print(f'PO Attainment records: {frappe.db.count("PO Attainment")} (need 1)')
print(f'PO Attainment Entry rows: {frappe.db.sql("SELECT COUNT(*) FROM `tabPO Attainment Entry`")[0][0]} (need 12)')
print(f'PO Final Entry rows: {frappe.db.sql("SELECT COUNT(*) FROM `tabPO Final Entry`")[0][0]} (need 12)')

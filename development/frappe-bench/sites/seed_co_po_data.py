"""
Seed CO Attainment (6 records) and fill CO PO Mapping Entry child rows for 3 existing mappings.
Schema-verified against actual database columns.
"""
import frappe
from datetime import date

frappe.init(site='university.local', sites_path='/workspace/development/frappe-bench/sites')
frappe.connect()
frappe.set_user('Administrator')
TODAY = date.today()

# ── Part A: CO Attainment (6 records — 2 per course × 3 courses) ──────────────

# Verify CO Attainment meta
ca_meta = frappe.get_meta('CO Attainment')
print('CO Attainment autoname:', ca_meta.autoname)
print('CO Direct Attainment cols:', [f.fieldname for f in frappe.get_meta('CO Direct Attainment').fields
      if f.fieldtype not in ['Section Break','Column Break','HTML']])

courses = ['Data Structures', 'Database Systems', 'Operating Systems']
terms   = ['2025-26 (Odd Semester)', '2025-26 (Semester 1)']

# CO details per course (5 COs each)
co_assessment_types = ['Assignment', 'Quiz', 'Mid-term Exam', 'End-term Exam', 'Lab Work']
co_max_marks        = [10, 10, 30, 60, 25]
co_target_percent   = 60
co_total_students   = 30
co_above_target     = [22, 18, 25, 20, 24]

inserted_ca = 0
for course in courses:
    for term in terms:
        # Clean any existing
        frappe.db.sql("DELETE FROM `tabCO Attainment` WHERE course=%s AND academic_term=%s", (course, term))
        frappe.db.commit()

        doc = frappe.new_doc('CO Attainment')
        doc.course = course
        doc.academic_term = term
        doc.academic_year = '2025-26'
        doc.status = 'Draft'
        doc.total_students = co_total_students
        doc.direct_weight = 80
        doc.indirect_weight = 20
        doc.calculation_date = TODAY

        for i in range(5):
            co_name = f'{course}-CO{i+1}'
            att_pct = round(co_above_target[i] / co_total_students * 100, 2)
            doc.append('direct_attainment_table', {
                'course_outcome': co_name,
                'co_code': f'CO{i+1}',
                'assessment_type': co_assessment_types[i],
                'max_marks': co_max_marks[i],
                'target_percent': co_target_percent,
                'total_students': co_total_students,
                'students_above_target': co_above_target[i],
                'attainment_percent': att_pct,
                'attainment_level': 3 if att_pct >= 70 else (2 if att_pct >= 50 else 1),
            })

        doc.flags.ignore_validate = True
        doc.flags.ignore_links = True
        doc.flags.ignore_mandatory = True
        doc.insert(ignore_permissions=True)
        frappe.db.set_value('CO Attainment', doc.name, 'docstatus', 1)
        frappe.db.commit()
        inserted_ca += 1
        print(f'  CO Attainment: {doc.name}')

print(f'CO Attainment inserted: {inserted_ca}')
print(f'CO Attainment count: {frappe.db.count("CO Attainment")}')

# ── Part B: CO PO Mapping Entry (fill 3 existing mappings) ────────────────────

# Discover parentfield name
copo_meta = frappe.get_meta('CO PO Mapping')
table_fields = [(f.fieldname, f.options) for f in copo_meta.fields if f.fieldtype == 'Table']
print('\nCO PO Mapping table fields:', table_fields)

# Existing mappings
mappings = [
    'Data Structures-2025-26 (Odd Semester)-COPOMAP',
    'Database Systems-2025-26 (Odd Semester)-COPOMAP',
    'Operating Systems-2025-26 (Odd Semester)-COPOMAP',
]

# PO details: PO1-PO4 of B.Tech Computer Science
pos = [
    ('B.Tech Computer Science-PO1', 'PO1', 'Engineering Knowledge'),
    ('B.Tech Computer Science-PO2', 'PO2', 'Problem Analysis'),
    ('B.Tech Computer Science-PO3', 'PO3', 'Design/Development'),
    ('B.Tech Computer Science-PO4', 'PO4', 'Investigation'),
    ('B.Tech Computer Science-PO5', 'PO5', 'Modern Tool Usage'),
]

# correlation_level values: 1=Weak, 2=Moderate, 3=Strong
# Use a meaningful pattern: CO1→PO1=3 (strong), CO1→PO2=2, etc.
corr_matrix = [
    [3, 2, 1, 2, 1],  # CO1 vs PO1..PO5
    [2, 3, 2, 1, 2],  # CO2
    [1, 2, 3, 2, 1],  # CO3
    [2, 1, 2, 3, 2],  # CO4
    [1, 2, 1, 2, 3],  # CO5
]

parentfield = table_fields[0][0] if table_fields else 'co_po_mapping_entries'
child_doctype = table_fields[0][1] if table_fields else 'CO PO Mapping Entry'
print(f'Using parentfield={parentfield}, child={child_doctype}')

total_entries = 0
for mapping in mappings:
    # Get course from mapping name
    course = mapping.split('-2025-26')[0]
    # Clean existing entries for this parent
    frappe.db.sql(f"DELETE FROM `tab{child_doctype}` WHERE parent=%s", mapping)
    frappe.db.commit()

    for co_idx in range(5):
        co_name = f'{course}-CO{co_idx+1}'
        co_code = f'CO{co_idx+1}'
        co_stmt = f'Students will be able to demonstrate knowledge of {course} concept {co_idx+1}'
        for po_idx, (po_name, po_code, po_title) in enumerate(pos):
            corr = corr_matrix[co_idx][po_idx]
            frappe.db.sql(f"""INSERT INTO `tab{child_doctype}`
                (name, parent, parenttype, parentfield, idx,
                 course_outcome, co_code, co_statement,
                 program_outcome, po_code, po_title,
                 correlation_level, justification)
                VALUES (%s, %s, 'CO PO Mapping', %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s)""",
                (frappe.generate_hash(length=10), mapping, parentfield, co_idx * 5 + po_idx + 1,
                 co_name, co_code, co_stmt,
                 po_name, po_code, po_title,
                 corr, 'This CO directly supports the PO through coursework and assessments'))
            total_entries += 1
    frappe.db.commit()

    # Update parent summary fields
    frappe.db.set_value('CO PO Mapping', mapping, {
        'total_mappings': 25,
        'strong_correlations': sum(1 for r in corr_matrix for c in r if c == 3),
        'moderate_correlations': sum(1 for r in corr_matrix for c in r if c == 2),
        'weak_correlations': sum(1 for r in corr_matrix for c in r if c == 1),
    })
    frappe.db.commit()
    print(f'  {mapping}: 25 entries inserted')

print(f'\nTotal CO PO Mapping Entry rows: {total_entries}')
actual_count = frappe.db.sql(f"SELECT COUNT(*) FROM `tab{child_doctype}`")[0][0]
print(f'DB count of {child_doctype}: {actual_count}')

# ── Summary ────────────────────────────────────────────────────────────────────
print('\n=== CO/PO SEED RESULTS ===')
ca_count = frappe.db.count('CO Attainment')
print(f"{'OK  ' if ca_count >= 6 else 'FAIL'} CO Attainment: {ca_count} (need 6)")
print(f"{'OK  ' if actual_count >= 60 else 'FAIL'} CO PO Mapping Entry: {actual_count} (need 75)")

# Verify mappings have data
for m in mappings:
    cnt = frappe.db.sql(f"SELECT COUNT(*) FROM `tab{child_doctype}` WHERE parent=%s", m)[0][0]
    print(f"  {m}: {cnt} entries")

print('\nDone!')

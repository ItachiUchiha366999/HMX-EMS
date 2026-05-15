"""Fix placement data — ensure applications span multiple programs."""
import frappe


def run():
    frappe.flags.ignore_permissions = True

    # Check current distribution of placement apps by student program
    dist = frappe.db.sql("""
        SELECT s.custom_program, COUNT(pa.name) as apps, SUM(pa.status='Placed') as placed
        FROM `tabPlacement Application` pa
        INNER JOIN `tabStudent` s ON pa.student = s.name
        GROUP BY s.custom_program
        ORDER BY apps DESC
    """, as_dict=True)
    print("Current prog distribution:", dist)

    # Check how many students per program have apps
    student_prog = frappe.db.sql("""
        SELECT s.custom_program, COUNT(DISTINCT pa.student) as unique_students
        FROM `tabPlacement Application` pa
        INNER JOIN `tabStudent` s ON pa.student = s.name
        GROUP BY s.custom_program
    """, as_dict=True)
    print("Unique students per program:", student_prog)

    # What students are in placement apps?
    app_students = frappe.db.sql(
        "SELECT DISTINCT student FROM `tabPlacement Application` LIMIT 10",
        as_dict=True
    )
    print("App students sample:", [r['student'] for r in app_students])

    # What program do those students have?
    for r in app_students[:5]:
        prog = frappe.db.get_value("Student", r['student'], "custom_program")
        print(f"  {r['student']} -> custom_program={prog}")

    # Check Placement Company - Program link (for Company Wise report)
    pc_data = frappe.db.sql(
        "SELECT name FROM `tabPlacement Company` LIMIT 5",
        as_dict=True
    )
    print("Placement Companies:", [r['name'] for r in pc_data])

    # Check what the Placement Drive column for student field is
    cols = [c['Field'] for c in frappe.db.sql("DESCRIBE `tabPlacement Application`", as_dict=True)]
    print("Placement Application cols:", cols)

    # Check how Company Wise Placement report actually works
    # It groups by pa.company and JOINs pc.name
    # Check if Placement Company = company names used in applications
    app_companies = frappe.db.sql(
        "SELECT DISTINCT company FROM `tabPlacement Application` WHERE company IS NOT NULL",
        as_dict=True
    )
    pc_names = frappe.db.sql(
        "SELECT name FROM `tabPlacement Company`",
        as_dict=True
    )
    print("App companies:", [r['company'] for r in app_companies])
    print("Placement Company names:", [r['name'] for r in pc_names])

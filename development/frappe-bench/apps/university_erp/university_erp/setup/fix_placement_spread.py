"""Fix placement applications to span multiple programs."""
import frappe
import random


def run():
    frappe.flags.ignore_permissions = True
    random.seed(42)

    # Get students from each program (not just CSE)
    programs = frappe.db.sql("""
        SELECT s.name, s.student_name, s.custom_program
        FROM `tabStudent` s
        WHERE s.custom_program IS NOT NULL
        AND s.enabled = 1
        ORDER BY s.custom_program, s.name
        LIMIT 100
    """, as_dict=True)

    # Group by program
    by_prog = {}
    for s in programs:
        prog = s['custom_program']
        if prog not in by_prog:
            by_prog[prog] = []
        by_prog[prog].append(s)

    print("Students per program:", {p: len(v) for p, v in by_prog.items()})

    # Get existing placement applications
    apps = frappe.db.sql(
        "SELECT name, student, company, job_opening, placement_drive, status, offered_ctc "
        "FROM `tabPlacement Application` ORDER BY name",
        as_dict=True
    )
    print(f"Total apps: {len(apps)}")

    # Get programs list (excluding MBA since placement drives are likely engineering)
    target_progs = [p for p in by_prog.keys() if len(by_prog[p]) >= 5]
    print("Target programs:", target_progs)

    # Reassign apps to students from different programs
    # We have 80 apps, distribute ~16 per program (5 programs)
    all_target_students = []
    for prog in target_progs:
        # Take up to 16 students from each program
        students = by_prog[prog][:16]
        all_target_students.extend(students)

    random.shuffle(all_target_students)

    # Distribute apps across these students
    # Each app gets assigned to one student (cycling through)
    updates = []
    for i, app in enumerate(apps):
        student = all_target_students[i % len(all_target_students)]
        updates.append((student['name'], student['student_name'], app['name']))

    print(f"Will reassign {len(updates)} apps to {len(all_target_students)} students across {len(target_progs)} programs")

    # Apply updates
    for student_id, student_name, app_name in updates:
        frappe.db.sql(
            "UPDATE `tabPlacement Application` SET student=%s, student_name=%s WHERE name=%s",
            (student_id, student_name, app_name)
        )

    frappe.db.commit()

    # Verify
    dist = frappe.db.sql("""
        SELECT s.custom_program, COUNT(pa.name) as apps, SUM(pa.status='Placed') as placed
        FROM `tabPlacement Application` pa
        INNER JOIN `tabStudent` s ON pa.student = s.name
        GROUP BY s.custom_program
        ORDER BY apps DESC
    """, as_dict=True)
    print("New distribution:", dist)

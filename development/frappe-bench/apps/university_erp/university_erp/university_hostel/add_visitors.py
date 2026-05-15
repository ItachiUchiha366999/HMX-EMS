"""Add visitor records for hostel module demo"""
import frappe
from frappe.utils import today


def add_visitors():
    """Add visitor records directly"""

    # Get allocations
    allocations = frappe.db.sql("""
        SELECT
            ha.student,
            s.student_name,
            hr.hostel_building as building,
            hb.building_name,
            ha.room
        FROM `tabHostel Allocation` ha
        JOIN `tabStudent` s ON ha.student = s.name
        JOIN `tabHostel Room` hr ON ha.room = hr.name
        JOIN `tabHostel Building` hb ON hr.hostel_building = hb.name
        WHERE ha.status = 'Active' AND ha.docstatus = 1
    """, as_dict=True)

    print(f"Found {len(allocations)} active allocations")

    visitor_data = [
        ("Rajendra Sharma", "Parent", "Aadhar", "1234-5678-9012", "Family visit"),
        ("Sunita Devi", "Parent", "Voter ID", "ABC1234567", "Dropping supplies"),
        ("Mohit Kumar", "Sibling", "Driving License", "DL-1234567890", "Weekend visit"),
        ("Neha Gupta", "Friend", "Aadhar", "9876-5432-1098", "Birthday celebration"),
        ("Anil Verma", "Guardian", "PAN", "ABCDE1234F", "Meeting with student"),
        ("Priya Kapoor", "Relative", "Passport", "J1234567", "Family gathering"),
        ("Suresh Reddy", "Parent", "Aadhar", "5678-1234-9012", "Monthly visit"),
        ("Kamla Devi", "Parent", "Voter ID", "XYZ9876543", "Bringing home food"),
        ("Ramesh Yadav", "Parent", "Aadhar", "4567-8901-2345", "Academic discussion"),
        ("Geeta Devi", "Parent", "Voter ID", "DEF7891234", "General visit"),
        ("Vikash Singh", "Sibling", "Aadhar", "2345-6789-0123", "Surprise visit"),
        ("Meena Kumari", "Parent", "Voter ID", "GHI4567890", "Exam preparation help"),
        ("Rajan Tiwari", "Guardian", "Driving License", "DL-9876543210", "Fee payment discussion"),
        ("Sita Ram", "Parent", "Aadhar", "3456-7890-1234", "Birthday celebration"),
        ("Poonam Gupta", "Relative", "Voter ID", "JKL1234567", "Festival visit"),
    ]

    created = 0
    for i, alloc in enumerate(allocations):
        v = visitor_data[i % len(visitor_data)]
        name = f"VIS-2026-{str(90000 + i).zfill(5)}"

        if frappe.db.exists("Hostel Visitor", name):
            print(f"  Skipping {name} - already exists")
            continue

        status = "Checked Out" if i % 3 == 0 else "Checked In"
        checkout_time = f"{18 + i % 2}:30:00" if status == "Checked Out" else None

        frappe.db.sql("""
            INSERT INTO `tabHostel Visitor` (
                name, owner, creation, modified, modified_by, docstatus,
                visitor_name, visitor_mobile, relationship, visitor_id_type, visitor_id_number,
                student, student_name, building, building_name, room,
                visit_date, check_in_time, check_out_time, expected_checkout_time, purpose, status
            ) VALUES (
                %s, 'Administrator', NOW(), NOW(), 'Administrator', 0,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """, (
            name, v[0], f"+91 98765{str(90000 + i).zfill(5)}", v[1], v[2], v[3],
            alloc.student, alloc.student_name, alloc.building, alloc.building_name, alloc.room,
            today(), f"{10 + i % 6}:30:00", checkout_time, f"{17 + i % 3}:00:00", v[4], status
        ))
        created += 1
        print(f"  Created visitor: {v[0]} for {alloc.student_name} ({status})")

    frappe.db.commit()
    print(f"\nCreated {created} visitors")
    print(f"Total visitors in system: {frappe.db.count('Hostel Visitor')}")

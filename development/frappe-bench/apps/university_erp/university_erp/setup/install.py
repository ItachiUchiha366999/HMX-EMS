import frappe
from frappe import _


def after_install():
    """
    Called after university_erp app is installed on a site.

    Tasks:
    1. Hide ERPNext workspaces
    2. Create university roles (via fixtures)
    3. Setup custom fields (via fixtures)
    4. Create default grading scale
    5. Create University Settings
    """
    frappe.logger().info("Starting University ERP post-installation setup...")

    hide_erpnext_workspaces()
    create_default_grading_scale()
    create_university_settings()
    # Education install.py migration (Phase 03.3.1 Plan 06, Wave 4)
    setup_education_fixtures()
    create_student_role()
    create_parent_assessment_group()

    frappe.logger().info("University ERP installation completed successfully!")
    frappe.msgprint(
        _("University ERP installed successfully! Please configure University Settings."),
        alert=True,
        indicator="green"
    )


def hide_erpnext_workspaces():
    """Hide irrelevant ERPNext workspaces from UI"""
    workspaces_to_hide = [
        "Home",
        "Manufacturing",
        "Stock",
        "Selling",
        "Buying",
        "CRM",
        "Projects",
        "Assets",
        "Quality",
        "Support"
    ]

    for workspace in workspaces_to_hide:
        try:
            if frappe.db.exists("Workspace", workspace):
                frappe.db.set_value("Workspace", workspace, "public", 0)
                frappe.logger().info(f"Hidden workspace: {workspace}")
        except Exception as e:
            frappe.logger().error(f"Error hiding workspace {workspace}: {str(e)}")

    frappe.db.commit()
    frappe.logger().info("ERPNext workspaces hidden successfully")


def create_default_grading_scale():
    """Create University 10-Point grading scale"""
    if frappe.db.exists("Grading Scale", "University 10-Point Scale"):
        frappe.logger().info("University 10-Point Scale already exists")
        return

    try:
        grading_scale = frappe.get_doc({
            "doctype": "Grading Scale",
            "grading_scale_name": "University 10-Point Scale",
            "description": "10-Point grading scale for university (O=10, A+=9, A=8, B+=7, B=6, C=5, P=4, F=0)",
            "intervals": [
                {
                    "grade_code": "O",
                    "threshold": 90.0,
                    "grade_description": "Outstanding"
                },
                {
                    "grade_code": "A+",
                    "threshold": 80.0,
                    "grade_description": "Excellent"
                },
                {
                    "grade_code": "A",
                    "threshold": 70.0,
                    "grade_description": "Very Good"
                },
                {
                    "grade_code": "B+",
                    "threshold": 60.0,
                    "grade_description": "Good"
                },
                {
                    "grade_code": "B",
                    "threshold": 55.0,
                    "grade_description": "Above Average"
                },
                {
                    "grade_code": "C",
                    "threshold": 50.0,
                    "grade_description": "Average"
                },
                {
                    "grade_code": "P",
                    "threshold": 45.0,
                    "grade_description": "Pass"
                },
                {
                    "grade_code": "F",
                    "threshold": 0.0,
                    "grade_description": "Fail"
                }
            ]
        })

        grading_scale.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("Created University 10-Point Scale grading scale")

    except Exception as e:
        frappe.logger().error(f"Error creating grading scale: {str(e)}")


def create_university_settings():
    """Create default University Settings if not exists"""
    if frappe.db.exists("University Settings"):
        frappe.logger().info("University Settings already exists")
        return

    try:
        settings = frappe.get_doc({
            "doctype": "University Settings",
            "university_name": "University",
            "university_code": "UNI",
            "use_10_point_scale": 1,
            "cgpa_calculation_method": "Weighted Average",
            "passing_grade_points": 4.0,
            "min_attendance_percentage": 75.0,
            "max_courses_per_semester": 8,
            "enrollment_number_format": "UNI-{YYYY}-{#####}",
            "application_number_format": "APP-{YYYY}-{#####}",
            "enable_late_fee": 1,
            "late_fee_percentage": 2.0,
            "late_fee_period_days": 7,
            "enable_online_payment": 1
        })

        # Set default grading scale
        if frappe.db.exists("Grading Scale", "University 10-Point Scale"):
            settings.default_grading_scale = "University 10-Point Scale"

        settings.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("Created University Settings")

    except Exception as e:
        frappe.logger().error(f"Error creating University Settings: {str(e)}")


def setup_permissions():
    """Setup role permissions for university DocTypes"""
    # This will be enhanced as more DocTypes are added
    pass


# ---------------------------------------------------------------------------
# Education install.py logic migrated into university_erp (Phase 03.3.1 Plan 06)
# Source: frappe-bench/apps/education/education/install.py
# Idempotent — safe to re-run on existing sites.
# ---------------------------------------------------------------------------

def setup_education_fixtures():
    """Create Party Type 'Student' (Receivable) — migrated from Education.

    Education's install.py registered Student as a Receivable party type so
    Fees can post GL entries against Student-as-party. Idempotent.
    """
    records = [
        {"doctype": "Party Type", "party_type": "Student", "account_type": "Receivable"}
    ]
    for record in records:
        if not frappe.db.exists("Party Type", record.get("party_type")):
            try:
                doc = frappe.get_doc(record)
                doc.insert(ignore_permissions=True)
                frappe.logger().info("Created Party Type: Student")
            except Exception as e:
                frappe.logger().error(f"Error creating Party Type Student: {str(e)}")


def create_parent_assessment_group():
    """Create root Assessment Group 'All Assessment Groups' — from Education install.py."""
    if frappe.db.exists("Assessment Group", "All Assessment Groups"):
        frappe.logger().info("Assessment Group 'All Assessment Groups' already exists")
        return
    try:
        doc = frappe.get_doc(
            {
                "doctype": "Assessment Group",
                "assessment_group_name": "All Assessment Groups",
                "is_group": 1,
            }
        )
        doc.flags.ignore_permissions = True
        doc.insert(ignore_mandatory=True)
        frappe.logger().info("Created Assessment Group: All Assessment Groups")
    except Exception as e:
        frappe.logger().error(f"Error creating parent Assessment Group: {str(e)}")


def create_student_role():
    """Create 'Student' role — migrated from Education install.py."""
    if frappe.db.exists("Role", "Student"):
        frappe.logger().info("Role 'Student' already exists")
        return
    try:
        doc = frappe.get_doc({"doctype": "Role", "role_name": "Student", "desk_access": 0})
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.logger().info("Created Role: Student")
    except Exception as e:
        frappe.logger().error(f"Error creating Student role: {str(e)}")

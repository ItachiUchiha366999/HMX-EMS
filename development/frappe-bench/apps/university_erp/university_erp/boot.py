import frappe


def boot_session(bootinfo):
    """
    Called when user logs in.
    Adds university-specific data to bootinfo for client-side use.

    Args:
        bootinfo: Dictionary that gets sent to client
    """
    if frappe.session.user == "Guest":
        return

    # Add university settings to bootinfo
    bootinfo.university_settings = get_university_settings_for_boot()

    # Add user's university roles
    bootinfo.university_roles = get_university_roles(frappe.session.user)

    # Add current academic year
    bootinfo.current_academic_year = get_current_academic_year()

    # Add payment gateway settings (for users with payment permissions)
    bootinfo.payment_settings = get_payment_settings_for_boot()


def get_university_settings_for_boot():
    """Get relevant university settings for client"""
    try:
        if not frappe.db.exists("University Settings"):
            return {}

        settings = frappe.get_single("University Settings")

        return {
            "university_name": settings.university_name,
            "university_code": settings.university_code,
            "use_10_point_scale": settings.use_10_point_scale,
            "passing_grade_points": settings.passing_grade_points,
            "min_attendance_percentage": settings.min_attendance_percentage,
            "max_courses_per_semester": settings.max_courses_per_semester,
        }

    except Exception as e:
        frappe.logger().error(f"Error fetching university settings for boot: {str(e)}")
        return {}


def get_university_roles(user):
    """Get list of university-specific roles for the user"""
    if not user or user == "Guest":
        return []

    university_role_prefix = "University"
    all_roles = frappe.get_roles(user)

    university_roles = [role for role in all_roles if role.startswith(university_role_prefix)]

    return university_roles


def get_current_academic_year():
    """Get the currently active academic year"""
    try:
        active_year = frappe.db.get_value(
            "University Academic Year",
            {"is_active": 1},
            "name"
        )

        return active_year

    except Exception as e:
        frappe.logger().error(f"Error fetching current academic year: {str(e)}")
        return None


def get_payment_settings_for_boot():
    """
    Get payment gateway settings for client-side caching.
    Only returns non-sensitive configuration data.
    Returns settings for all users (students need to know which gateways are enabled).
    """
    settings = {
        "gateways_enabled": [],
        "default_gateway": None,
        "currency": "INR",
        "auto_capture": True
    }

    try:
        # Check Razorpay settings
        if frappe.db.exists("DocType", "Razorpay Settings"):
            razorpay = frappe.get_single("Razorpay Settings")
            if razorpay.enabled:
                settings["gateways_enabled"].append({
                    "name": "Razorpay",
                    "test_mode": razorpay.test_mode,
                    "key_id": razorpay.api_key if not razorpay.test_mode else None,
                    "auto_capture": razorpay.auto_capture
                })
                if not settings["default_gateway"]:
                    settings["default_gateway"] = "Razorpay"
                settings["auto_capture"] = razorpay.auto_capture

        # Check PayU settings
        if frappe.db.exists("DocType", "PayU Settings"):
            payu = frappe.get_single("PayU Settings")
            if payu.enabled:
                settings["gateways_enabled"].append({
                    "name": "PayU",
                    "test_mode": payu.test_mode
                })
                if not settings["default_gateway"]:
                    settings["default_gateway"] = "PayU"

        # Get University Accounts Settings
        if frappe.db.exists("DocType", "University Accounts Settings"):
            accounts_settings = frappe.get_single("University Accounts Settings")
            settings["company"] = accounts_settings.company
            settings["auto_post_gl"] = accounts_settings.auto_post_gl

    except Exception as e:
        frappe.logger().error(f"Error fetching payment settings for boot: {str(e)}")

    return settings

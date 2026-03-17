"""
Jinja environment customization for University ERP
"""

import frappe
from frappe.utils import format_time as frappe_format_time


def setup_jinja_env(jenv):
    """
    Add custom methods to Jinja environment.
    This makes format_time available as frappe.format_time in templates.
    """
    # Add format_time to the frappe object in Jinja context
    if not hasattr(jenv.globals.get('frappe', frappe._dict()), 'format_time'):
        # Get the frappe object from globals or use the module
        frappe_obj = jenv.globals.get('frappe', frappe)

        # Add format_time method
        if hasattr(frappe_obj, '__dict__'):
            frappe_obj.format_time = frappe_format_time
        else:
            # If frappe is a module, we need to add it differently
            # Create a wrapper dict that includes format_time
            class FrappeWrapper:
                def __getattr__(self, name):
                    if name == 'format_time':
                        return frappe_format_time
                    return getattr(frappe, name)

            jenv.globals['frappe'] = FrappeWrapper()

    return jenv

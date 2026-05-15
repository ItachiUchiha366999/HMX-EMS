# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HostelMess(Document):
    """Hostel Mess management with menu planning"""

    def validate(self):
        self.validate_menu()
        self.calculate_daily_rate()

    def validate_menu(self):
        """Validate menu items for duplicate entries"""
        if not self.menu:
            return

        seen = set()
        for item in self.menu:
            key = (item.day, item.meal_type)
            if key in seen:
                frappe.throw(
                    f"Duplicate menu entry for {item.day} - {item.meal_type}"
                )
            seen.add(key)

    def calculate_daily_rate(self):
        """Calculate daily rate from monthly charge"""
        if self.monthly_charge and not self.daily_rate:
            self.daily_rate = self.monthly_charge / 30


@frappe.whitelist()
def get_mess_menu(mess, day=None):
    """Get mess menu for a specific day or full week"""
    filters = {"parent": mess}
    if day:
        filters["day"] = day

    return frappe.get_all(
        "Mess Menu Item",
        filters=filters,
        fields=["day", "meal_type", "menu_items", "special_item"],
        order_by="field(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), field(meal_type, 'Breakfast', 'Lunch', 'Snacks', 'Dinner')"
    )


@frappe.whitelist()
def get_today_menu(mess):
    """Get today's menu for a mess"""
    import datetime
    today = datetime.datetime.now().strftime("%A")
    return get_mess_menu(mess, today)

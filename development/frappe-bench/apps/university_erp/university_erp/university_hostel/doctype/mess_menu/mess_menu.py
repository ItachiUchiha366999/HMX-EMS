# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


class MessMenu(Document):
    """Weekly Mess Menu management"""

    def validate(self):
        self.validate_dates()
        self.calculate_week_end()
        self.validate_duplicate_menu()
        self.validate_menu_items()

    def validate_dates(self):
        """Validate week start date is a Monday"""
        if self.week_start_date:
            start_date = getdate(self.week_start_date)
            if start_date.weekday() != 0:  # 0 = Monday
                frappe.throw(_("Week Start Date must be a Monday"))

    def calculate_week_end(self):
        """Calculate week end date (Sunday)"""
        if self.week_start_date:
            self.week_end_date = add_days(self.week_start_date, 6)

    def validate_duplicate_menu(self):
        """Check for duplicate menu for same mess and week"""
        if self.is_new():
            existing = frappe.db.exists(
                "Mess Menu",
                {
                    "mess": self.mess,
                    "week_start_date": self.week_start_date,
                    "name": ["!=", self.name]
                }
            )
            if existing:
                frappe.throw(
                    _("Menu for {0} starting {1} already exists: {2}").format(
                        self.mess_name or self.mess,
                        self.week_start_date,
                        existing
                    )
                )

    def validate_menu_items(self):
        """Validate that all days and meals are covered"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meals = ["Breakfast", "Lunch", "Snacks", "Dinner"]

        covered = set()
        for item in self.menu_items or []:
            covered.add((item.day, item.meal_type))

        missing = []
        for day in days:
            for meal in meals:
                if (day, meal) not in covered:
                    missing.append(f"{day} {meal}")

        if missing and self.status == "Published":
            frappe.msgprint(
                _("Missing menu items for: {0}").format(", ".join(missing[:5])),
                indicator="orange"
            )

    def on_update(self):
        """Clear cache when menu is updated"""
        if self.status == "Published":
            frappe.cache().delete_value(f"today_menu_{self.mess}")


@frappe.whitelist()
def get_today_menu(mess=None):
    """Get today's menu for a mess or all messes"""
    current_date = getdate(today())
    day_name = current_date.strftime("%A")

    filters = {"status": "Published"}
    if mess:
        filters["mess"] = mess

    # Find menu for current week
    menus = frappe.get_all(
        "Mess Menu",
        filters=filters,
        fields=["name", "mess", "mess_name", "mess_type", "week_start_date", "week_end_date", "special_notes"]
    )

    result = []
    for menu in menus:
        if getdate(menu.week_start_date) <= current_date <= getdate(menu.week_end_date):
            # Get today's items
            items = frappe.db.sql("""
                SELECT meal_type, menu_items, special_item
                FROM `tabMess Menu Item`
                WHERE parent = %s AND day = %s
                ORDER BY FIELD(meal_type, 'Breakfast', 'Lunch', 'Snacks', 'Dinner')
            """, (menu.name, day_name), as_dict=True)

            result.append({
                "mess": menu.mess,
                "mess_name": menu.mess_name,
                "mess_type": menu.mess_type,
                "date": current_date,
                "day": day_name,
                "special_notes": menu.special_notes,
                "items": items
            })

    return result


@frappe.whitelist()
def get_week_menu(mess, week_start_date=None):
    """Get full week menu for a mess"""
    if not week_start_date:
        # Get current week's Monday
        current_date = getdate(today())
        days_since_monday = current_date.weekday()
        week_start_date = add_days(current_date, -days_since_monday)

    menu = frappe.db.get_value(
        "Mess Menu",
        {"mess": mess, "week_start_date": week_start_date, "status": "Published"},
        ["name", "mess_name", "mess_type", "week_start_date", "week_end_date", "special_notes"],
        as_dict=True
    )

    if not menu:
        return None

    # Get all items grouped by day
    items = frappe.db.sql("""
        SELECT day, meal_type, menu_items, special_item
        FROM `tabMess Menu Item`
        WHERE parent = %s
        ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
                 FIELD(meal_type, 'Breakfast', 'Lunch', 'Snacks', 'Dinner')
    """, menu.name, as_dict=True)

    # Group by day
    menu_by_day = {}
    for item in items:
        if item.day not in menu_by_day:
            menu_by_day[item.day] = []
        menu_by_day[item.day].append(item)

    menu["menu_by_day"] = menu_by_day
    return menu


@frappe.whitelist()
def publish_menu(menu_name):
    """Publish a menu"""
    menu = frappe.get_doc("Mess Menu", menu_name)
    menu.status = "Published"
    menu.save()
    return menu.status


@frappe.whitelist()
def archive_menu(menu_name):
    """Archive a menu"""
    menu = frappe.get_doc("Mess Menu", menu_name)
    menu.status = "Archived"
    menu.save()
    return menu.status

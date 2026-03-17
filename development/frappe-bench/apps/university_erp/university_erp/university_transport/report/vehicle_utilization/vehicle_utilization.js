// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Vehicle Utilization"] = {
    "filters": [
        {
            "fieldname": "vehicle_type",
            "label": __("Vehicle Type"),
            "fieldtype": "Select",
            "options": "\nBus\nMini Bus\nVan\nCar"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nAvailable\nIn Service\nUnder Maintenance\nOut of Service"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        }
    ]
};

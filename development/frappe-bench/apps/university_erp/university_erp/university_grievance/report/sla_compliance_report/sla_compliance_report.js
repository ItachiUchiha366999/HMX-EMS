// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["SLA Compliance Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "category",
            "label": __("Category"),
            "fieldtype": "Select",
            "options": "\nAcademic\nAdministrative\nFinancial\nInfrastructure\nHostel\nTransport\nLibrary\nExamination\nFaculty Related\nRagging\nHarassment\nDiscrimination\nOther"
        },
        {
            "fieldname": "grievance_type",
            "label": __("Grievance Type"),
            "fieldtype": "Link",
            "options": "Grievance Type"
        },
        {
            "fieldname": "assigned_to",
            "label": __("Assigned To"),
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "sla_status",
            "label": __("SLA Status"),
            "fieldtype": "Select",
            "options": "\nWithin SLA\nAt Risk\nBreached"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "sla_compliance_rate") {
            if (data && data[column.fieldname] >= 90) {
                value = "<span style='color: green; font-weight: bold;'>" + value + "</span>";
            } else if (data && data[column.fieldname] >= 70) {
                value = "<span style='color: orange;'>" + value + "</span>";
            } else {
                value = "<span style='color: red; font-weight: bold;'>" + value + "</span>";
            }
        }

        if (column.fieldname === "sla_status") {
            if (data && data[column.fieldname] === "Within SLA") {
                value = "<span style='color: green;'>" + value + "</span>";
            } else if (data && data[column.fieldname] === "At Risk") {
                value = "<span style='color: orange;'>" + value + "</span>";
            } else if (data && data[column.fieldname] === "Breached") {
                value = "<span style='color: red; font-weight: bold;'>" + value + "</span>";
            }
        }

        if (column.fieldname === "breached_count") {
            if (data && data[column.fieldname] > 0) {
                value = "<span style='color: red; font-weight: bold;'>" + value + "</span>";
            }
        }

        return value;
    }
};

// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Certificate Issuance Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPending\nApproved\nRejected\nGenerated\nIssued",
            "reqd": 0
        },
        {
            "fieldname": "certificate_template",
            "label": __("Certificate Type"),
            "fieldtype": "Link",
            "options": "Certificate Template",
            "reqd": 0
        },
        {
            "fieldname": "student",
            "label": __("Student"),
            "fieldtype": "Link",
            "options": "Student",
            "reqd": 0
        },
        {
            "fieldname": "program",
            "label": __("Program"),
            "fieldtype": "Link",
            "options": "Program",
            "reqd": 0
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "status") {
            if (data.status === "Issued") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (data.status === "Generated") {
                value = `<span class="indicator-pill purple">${value}</span>`;
            } else if (data.status === "Approved") {
                value = `<span class="indicator-pill blue">${value}</span>`;
            } else if (data.status === "Pending") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            } else if (data.status === "Rejected") {
                value = `<span class="indicator-pill red">${value}</span>`;
            }
        }

        return value;
    },

    "onload": function(report) {
        report.page.add_inner_button(__("Download Summary"), function() {
            frappe.query_report.export_report("Excel");
        });
    }
};

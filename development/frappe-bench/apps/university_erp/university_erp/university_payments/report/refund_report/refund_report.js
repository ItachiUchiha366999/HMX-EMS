frappe.query_reports["Refund Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPending\nApproved\nProcessed\nRejected"
        },
        {
            "fieldname": "reason",
            "label": __("Reason"),
            "fieldtype": "Select",
            "options": "\nCourse Withdrawal\nFee Revision\nExcess Payment\nScholarship Adjustment\nOther"
        },
        {
            "fieldname": "student",
            "label": __("Student"),
            "fieldtype": "Link",
            "options": "Student"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "status") {
            if (data.status === "Processed") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (data.status === "Approved") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            } else if (data.status === "Pending") {
                value = `<span class="indicator-pill yellow">${value}</span>`;
            } else if (data.status === "Rejected") {
                value = `<span class="indicator-pill red">${value}</span>`;
            }
        }

        return value;
    }
};

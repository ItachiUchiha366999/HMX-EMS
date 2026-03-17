frappe.query_reports["Daily Collection Report"] = {
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
            "fieldname": "payment_gateway",
            "label": __("Payment Gateway"),
            "fieldtype": "Select",
            "options": "\nRazorpay\nPayU"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "status") {
            if (data.status === "Completed") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (data.status === "Failed") {
                value = `<span class="indicator-pill red">${value}</span>`;
            } else if (data.status === "Pending") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            }
        }

        return value;
    }
};

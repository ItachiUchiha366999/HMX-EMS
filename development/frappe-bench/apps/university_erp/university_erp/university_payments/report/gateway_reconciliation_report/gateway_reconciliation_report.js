frappe.query_reports["Gateway Reconciliation Report"] = {
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
            "fieldname": "status",
            "label": __("Payment Status"),
            "fieldtype": "Select",
            "options": "\nPending\nCompleted\nFailed\nRefunded"
        },
        {
            "fieldname": "reconciliation_status",
            "label": __("Reconciliation Status"),
            "fieldtype": "Select",
            "options": "\nMatched\nAmount Mismatch\nMissing Entry\nFailed Payment\nPending"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "reconciliation_status") {
            if (data.reconciliation_status === "Matched") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (data.reconciliation_status === "Amount Mismatch") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            } else if (data.reconciliation_status === "Missing Entry") {
                value = `<span class="indicator-pill red">${value}</span>`;
            } else if (data.reconciliation_status === "Pending") {
                value = `<span class="indicator-pill yellow">${value}</span>`;
            } else if (data.reconciliation_status === "Failed Payment") {
                value = `<span class="indicator-pill grey">${value}</span>`;
            }
        }

        if (column.fieldname === "difference" && data.difference !== 0) {
            value = `<span style="color: red; font-weight: bold;">${value}</span>`;
        }

        return value;
    }
};

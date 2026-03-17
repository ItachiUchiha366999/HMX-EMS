frappe.query_reports["Payment Transaction Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nInitiated\nPending\nSuccess\nFailed\nRefunded\nCancelled"
        },
        {
            fieldname: "payment_gateway",
            label: __("Payment Gateway"),
            fieldtype: "Select",
            options: "\nRazorpay\nPayU\nPaytm\nCCAvenue\nStripe"
        },
        {
            fieldname: "student",
            label: __("Student"),
            fieldtype: "Link",
            options: "Student"
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "status") {
            if (data.status === "Success") {
                value = `<span class="badge badge-success">${value}</span>`;
            } else if (data.status === "Failed") {
                value = `<span class="badge badge-danger">${value}</span>`;
            } else if (data.status === "Pending" || data.status === "Initiated") {
                value = `<span class="badge badge-warning">${value}</span>`;
            } else if (data.status === "Refunded") {
                value = `<span class="badge badge-info">${value}</span>`;
            }
        }

        return value;
    }
};

// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["SMS Delivery Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
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
            "options": "\nQueued\nSent\nDelivered\nFailed",
            "reqd": 0
        },
        {
            "fieldname": "sms_gateway",
            "label": __("SMS Gateway"),
            "fieldtype": "Select",
            "options": "\nMSG91\nTwilio\nTextLocal\nFast2SMS",
            "reqd": 0
        },
        {
            "fieldname": "recipient",
            "label": __("Recipient"),
            "fieldtype": "Data",
            "reqd": 0
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "status") {
            if (data.status === "Delivered") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (data.status === "Sent") {
                value = `<span class="indicator-pill blue">${value}</span>`;
            } else if (data.status === "Failed") {
                value = `<span class="indicator-pill red">${value}</span>`;
            } else if (data.status === "Queued") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            }
        }

        return value;
    }
};

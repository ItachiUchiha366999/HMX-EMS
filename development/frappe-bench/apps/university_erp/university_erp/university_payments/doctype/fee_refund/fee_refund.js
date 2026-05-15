// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fee Refund", {
    onload: function (frm) {
        // When the user picks an Original Fee, only show Fees that belong
        // to the selected Student. If no Student is set yet, show all Fees.
        frm.set_query("fees", function () {
            const filters = { docstatus: 1 };
            if (frm.doc.student) {
                filters.student = frm.doc.student;
            }
            return { filters };
        });
    },

    student: function (frm) {
        // Re-apply the Fees filter when student changes,
        // and clear an existing Fee selection that no longer matches.
        if (frm.doc.fees) {
            frm.set_value("fees", "");
        }
    },

    refund_amount: function (frm) {
        update_net_refund(frm);
    },
    deduction_amount: function (frm) {
        update_net_refund(frm);
    },
});

function update_net_refund(frm) {
    const refund = flt(frm.doc.refund_amount);
    const deduction = flt(frm.doc.deduction_amount);
    frm.set_value("net_refund", refund - deduction);
}

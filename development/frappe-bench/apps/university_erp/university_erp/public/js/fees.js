/**
 * Fees doctype — adds a "Record Offline Payment" desk-side button so the
 * cashier never has to leave the standard Frappe desk to take a counter
 * payment. Only appears when the Fees doc is submitted and has outstanding > 0.
 */
frappe.ui.form.on("Fees", {
    refresh(frm) {
        if (frm.is_new()) return;
        if (frm.doc.docstatus !== 1) return;
        if (!(frm.doc.outstanding_amount > 0)) return;

        // Only finance staff get the button
        const roles = new Set(frappe.user_roles || []);
        if (!(roles.has("University Finance") || roles.has("System Manager") || roles.has("Administrator"))) {
            return;
        }

        frm.add_custom_button(__("Record Offline Payment"), () => show_payment_dialog(frm), __("Create"));
        frm.page.set_inner_btn_group_as_primary(__("Create"));
    },
});


function show_payment_dialog(frm) {
    // Fetch the residual quote (outstanding − any approved-but-pending scholarship)
    // so the dialog defaults to what the student can actually pay.
    frappe.call({
        method: "university_erp.university_finance.payment_recorder.get_payment_quote",
        args: { fee_name: frm.doc.name },
        callback(r) {
            const q = r.message || {};
            const outstanding = q.outstanding_amount || frm.doc.outstanding_amount || 0;
            const scholarship = q.pending_scholarship_amount || 0;
            const residual = q.student_residual != null ? q.student_residual : outstanding;
            const max_acceptable = scholarship > 0 ? residual : outstanding;

            const fmt = (v) => frappe.format(v, { fieldtype: "Currency" });

            // Information block at the top of the dialog
            let infoHtml = `<div class="text-muted small" style="margin-bottom:8px;">
                <div>Outstanding: <b>${fmt(outstanding)}</b> of ${fmt(q.grand_total || frm.doc.grand_total)}</div>
                <div>Fee: <code>${frm.doc.name}</code></div>`;

            if (scholarship > 0) {
                infoHtml += `
                <div style="margin-top:8px; padding:8px 12px; border-radius:6px;
                            background:#fef3c7; color:#92400e; border:1px solid #fde68a;">
                    <strong>⚠ Scholarship pending disbursement: ${fmt(scholarship)}</strong><br>
                    This slice is reserved for the funding body. The student can only pay
                    up to <b>${fmt(residual)}</b> right now.
                </div>`;
            }
            infoHtml += `</div>`;

            const d = new frappe.ui.Dialog({
                title: __("Record Payment for {0}", [frm.doc.student_name || frm.doc.student]),
                fields: [
                    { fieldname: "info", fieldtype: "HTML", options: infoHtml },
                    {
                        fieldname: "amount",
                        label: __("Amount"),
                        fieldtype: "Currency",
                        reqd: 1,
                        default: max_acceptable,
                        description: scholarship > 0
                            ? __("Maximum: {0} (excluding pending scholarship)", [fmt(max_acceptable)])
                            : __("Cannot exceed outstanding amount"),
                    },
                    {
                        fieldname: "mode_of_payment",
                        label: __("Mode of Payment"),
                        fieldtype: "Link",
                        options: "Mode of Payment",
                        reqd: 1,
                        default: "Cash",
                    },
                    {
                        fieldname: "reference_no",
                        label: __("Reference # (cheque / UPI ref / bank ref)"),
                        fieldtype: "Data",
                        description: __("Optional but recommended for traceability"),
                    },
                ],
                primary_action_label: __("Record Payment"),
                primary_action(values) {
                    // Client-side guard so the dialog catches over-payment before
                    // it round-trips to the backend (which also validates).
                    if (values.amount > max_acceptable + 0.001) {
                        frappe.msgprint({
                            title: __("Amount exceeds residual"),
                            indicator: "red",
                            message: __("Cannot accept ₹{0} — the maximum the student can pay right now is ₹{1} (₹{2} is reserved for an approved scholarship pending disbursement).",
                                [Number(values.amount).toFixed(0), Number(max_acceptable).toFixed(0), Number(scholarship).toFixed(0)]),
                        });
                        return;
                    }

                    d.disable_primary_action();
                    frappe.call({
                        method: "university_erp.university_finance.payment_recorder.record_offline_payment",
                        args: {
                            fee_name: frm.doc.name,
                            amount: values.amount,
                            mode_of_payment: values.mode_of_payment,
                            reference_no: values.reference_no || null,
                        },
                        callback(rr) {
                            if (rr.message) {
                                const m = rr.message;
                                frappe.show_alert({
                                    message: __("Payment {0} recorded ({1}). {2}", [
                                        m.payment_entry,
                                        fmt(m.amount),
                                        m.fully_paid ? __("Fee fully paid ✓")
                                            : __("Remaining: {0}", [fmt(m.remaining_outstanding)]),
                                    ]),
                                    indicator: "green",
                                }, 7);
                                d.hide();
                                frm.reload_doc();
                            }
                        },
                        error() { d.enable_primary_action(); },
                    });
                },
            });
            d.show();
        },
    });
}

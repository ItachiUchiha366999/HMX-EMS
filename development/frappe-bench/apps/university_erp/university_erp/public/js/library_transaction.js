/**
 * Library Transaction — adds a "Mark Returned" desk-side action so the
 * librarian can close out an issue. Auto-creates a Library Fine if returned late.
 */
frappe.ui.form.on("Library Transaction", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.docstatus !== 1) return;
        if (frm.doc.status === "Returned" || frm.doc.return_date) return;

        const roles = new Set(frappe.user_roles || []);
        if (!(roles.has("University Librarian") || roles.has("University Admin")
              || roles.has("System Manager") || roles.has("Administrator"))) {
            return;
        }

        frm.add_custom_button(__("Mark Returned"), () => show_return_dialog(frm), __("Actions"));
        frm.page.set_inner_btn_group_as_primary(__("Actions"));
    },
});

function show_return_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Return '{0}'", [frm.doc.article_title]),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small" style="margin-bottom:8px;">
                    Member: <b>${frm.doc.member_name || frm.doc.member}</b><br>
                    Issue date: ${frm.doc.issue_date}<br>
                    Due date: <b>${frm.doc.due_date}</b><br>
                    Returning after due date will create a Library Fine automatically.
                </div>`,
            },
            {
                fieldname: "return_date",
                label: __("Return Date"),
                fieldtype: "Date",
                default: frappe.datetime.get_today(),
                reqd: 1,
            },
            {
                fieldname: "fine_per_day",
                label: __("Fine per overdue day (₹)"),
                fieldtype: "Currency",
                default: 5,
                description: __("Only applied if return_date is after due_date"),
            },
        ],
        primary_action_label: __("Confirm Return"),
        primary_action(values) {
            d.disable_primary_action();
            frappe.call({
                method: "university_erp.university_library.doctype.library_transaction.library_transaction_actions.return_article",
                args: {
                    transaction: frm.doc.name,
                    return_date: values.return_date,
                    fine_per_day: values.fine_per_day,
                },
                callback(r) {
                    if (r.message) {
                        const m = r.message;
                        let msg;
                        if (m.overdue_days > 0) {
                            msg = __("Returned. {0} day(s) overdue — Library Fine {1} for ₹{2} created.",
                                [m.overdue_days, m.fine_name, m.fine_amount]);
                        } else {
                            msg = __("Returned on time ✓ No fine.");
                        }
                        frappe.show_alert({ message: msg, indicator: m.overdue_days > 0 ? "orange" : "green" }, 6);
                        d.hide();
                        frm.reload_doc();
                    }
                },
                error() { d.enable_primary_action(); },
            });
        },
    });
    d.show();
}

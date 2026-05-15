/**
 * Library Article — adds an "Issue Book" desk-side action so the librarian
 * can issue a copy to a student in one click. Also creates the Library Member
 * record automatically if missing.
 */
frappe.ui.form.on("Library Article", {
    refresh(frm) {
        if (frm.is_new()) return;

        const roles = new Set(frappe.user_roles || []);
        if (!(roles.has("University Librarian") || roles.has("University Admin")
              || roles.has("System Manager") || roles.has("Administrator"))) {
            return;
        }

        if ((frm.doc.available_copies || 0) > 0) {
            frm.add_custom_button(__("Issue Book"), () => show_issue_dialog(frm), __("Create"));
            frm.page.set_inner_btn_group_as_primary(__("Create"));
        }
    },
});

function show_issue_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Issue '{0}' to a student", [frm.doc.title]),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small" style="margin-bottom:8px;">
                    Available copies: <b>${frm.doc.available_copies}</b> / ${frm.doc.total_copies}<br>
                    Author: ${frm.doc.author || "—"}
                </div>`,
            },
            {
                fieldname: "student",
                label: __("Student"),
                fieldtype: "Link",
                options: "Student",
                reqd: 1,
                description: __("Library Member is auto-created if missing"),
            },
            {
                fieldname: "due_in_days",
                label: __("Loan period (days)"),
                fieldtype: "Int",
                default: 14,
                reqd: 1,
            },
        ],
        primary_action_label: __("Issue Book"),
        primary_action(values) {
            d.disable_primary_action();
            frappe.call({
                method: "university_erp.university_library.doctype.library_transaction.library_transaction_actions.issue_article",
                args: {
                    article: frm.doc.name,
                    student: values.student,
                    due_in_days: values.due_in_days,
                },
                callback(r) {
                    if (r.message) {
                        const m = r.message;
                        const memberMsg = m.member_created ? " (Library Member auto-created)" : "";
                        frappe.show_alert({
                            message: __("Transaction {0} created. Due {1}.{2}", [m.transaction, m.due_date, memberMsg]),
                            indicator: "green",
                        }, 6);
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

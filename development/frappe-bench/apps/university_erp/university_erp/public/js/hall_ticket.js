/**
 * Hall Ticket — adds an "Enter Results" desk-side action so the registrar
 * can bulk-enter Assessment Results for every course on the hall ticket
 * after the exam is over. Only appears when the hall ticket is Issued.
 */
frappe.ui.form.on("Hall Ticket", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.docstatus !== 1) return;
        if (frm.doc.workflow_state !== "Issued") return;

        const roles = new Set(frappe.user_roles || []);
        if (!(roles.has("University Registrar") || roles.has("University Exam Cell")
              || roles.has("System Manager") || roles.has("Administrator"))) {
            return;
        }

        frm.add_custom_button(__("Enter Results"), () => show_results_dialog(frm), __("Create"));
    },
});


function show_results_dialog(frm) {
    if (!frm.doc.exams || frm.doc.exams.length === 0) {
        frappe.msgprint(__("This hall ticket has no exams"));
        return;
    }

    const d = new frappe.ui.Dialog({
        title: __("Enter Results for {0}", [frm.doc.student_name]),
        size: "large",
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small" style="margin-bottom:8px;">
                    Enter marks out of 100 for each course. Grade is computed automatically
                    (90+ A+, 80+ A, 70+ B+, 60+ B, 50+ C, 40+ D, &lt;40 F). Submitting creates one
                    Assessment Result per course.
                </div>`,
            },
            {
                fieldname: "results",
                fieldtype: "Table",
                label: __("Results"),
                cannot_add_rows: true,
                cannot_delete_rows: true,
                in_place_edit: true,
                data: frm.doc.exams.map(e => ({
                    course: e.course,
                    course_name: e.course_name || e.course,
                    total_score: 0,
                    maximum_score: 100,
                })),
                fields: [
                    {fieldname: "course", fieldtype: "Data", label: __("Course"), in_list_view: 1, read_only: 1, columns: 5},
                    {fieldname: "total_score", fieldtype: "Float", label: __("Marks"), in_list_view: 1, columns: 2},
                    {fieldname: "maximum_score", fieldtype: "Float", label: __("Max"), in_list_view: 1, columns: 2, default: 100},
                ],
            },
        ],
        primary_action_label: __("Submit Results"),
        primary_action(values) {
            const rows = values.results || [];
            if (rows.some(r => r.total_score == null || r.total_score < 0 || r.total_score > r.maximum_score)) {
                frappe.msgprint(__("Each row's marks must be between 0 and the max score"));
                return;
            }
            d.disable_primary_action();
            frappe.call({
                method: "university_erp.university_examinations.doctype.hall_ticket.hall_ticket_actions.enter_results",
                args: {
                    hall_ticket: frm.doc.name,
                    results: rows,
                },
                callback(r) {
                    if (r.message) {
                        const m = r.message;
                        frappe.show_alert({
                            message: __("{0} Assessment Results created. {1}", [
                                m.created.length,
                                m.skipped.length ? `Skipped ${m.skipped.length} (already existed).` : "",
                            ]),
                            indicator: "green",
                        }, 5);
                        d.hide();
                        frm.reload_doc();
                    }
                },
                error() {
                    d.enable_primary_action();
                },
            });
        },
    });
    d.show();
}

/**
 * Student Applicant — adds an explicit "Allot Seat" action button so the
 * Registrar doesn't have to manually edit the Custom Seat Allotted field
 * before clicking the workflow's Admit transition.
 *
 * The button only appears when the applicant is in the `Shortlisted`
 * workflow state and a seat hasn't been allotted yet.
 */
frappe.ui.form.on("Student Applicant", {
    refresh(frm) {
        if (frm.is_new()) return;

        const state = frm.doc.workflow_state;
        const allotted = frm.doc.custom_seat_allotted;

        // Show "Allot Seat" only when shortlisted and no seat yet
        if (state === "Shortlisted" && !allotted) {
            frm.add_custom_button(__("Allot Seat"), () => show_allot_seat_dialog(frm), __("Actions"));
            frm.page.set_inner_btn_group_as_primary(__("Actions"));
        }

        // After admission, surface the linked Student record for one-click navigation
        if (state === "Admitted") {
            frappe.db.get_value("Student", { student_applicant: frm.doc.name }, "name").then(r => {
                const student = r.message && r.message.name;
                if (student) {
                    frm.add_custom_button(__("Open Student Record"), () => {
                        frappe.set_route("Form", "Student", student);
                    }, __("Actions"));
                }
            });
        }
    },
});


function show_allot_seat_dialog(frm) {
    const prefs = [
        frm.doc.custom_program_preference_1,
        frm.doc.custom_program_preference_2,
        frm.doc.custom_program_preference_3,
    ].filter(Boolean);

    if (prefs.length === 0) {
        frappe.msgprint({
            title: __("No program preferences"),
            message: __("This applicant has no program preferences set. Cannot allot a seat."),
            indicator: "red",
        });
        return;
    }

    const d = new frappe.ui.Dialog({
        title: __("Allot Seat to {0}", [frm.doc.first_name + " " + (frm.doc.last_name || "")]),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small">
                    Merit score: <b>${frm.doc.custom_merit_score || 0}</b><br>
                    Category: <b>${frm.doc.custom_category || "—"}</b>
                </div>`,
            },
            {
                fieldname: "program",
                fieldtype: "Select",
                label: __("Program to allot"),
                options: prefs.join("\n"),
                default: prefs[0],
                reqd: 1,
                description: __("Pick one of the applicant's preferences"),
            },
        ],
        primary_action_label: __("Allot Seat"),
        primary_action(values) {
            frm.set_value("custom_seat_allotted", values.program);
            frm.set_value("program", values.program);
            frm.set_value("custom_admission_status", "Seat Allotted");
            frm.save().then(() => {
                frappe.show_alert({
                    message: __("Seat allotted: {0}. You can now click Admit.", [values.program]),
                    indicator: "green",
                });
                d.hide();
            });
        },
    });
    d.show();
}

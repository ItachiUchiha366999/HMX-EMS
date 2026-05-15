/**
 * Placement Application — workflow helpers for the Placement Officer.
 *
 * The Schedule Interview transition requires interview_date / time / venue.
 * The Mark Offer Received transition requires offered_ctc.
 * Rather than have the user fail save then come back to fill fields,
 * we intercept the workflow buttons and pop a dialog first.
 */
frappe.ui.form.on("Placement Application", {
    refresh(frm) {
        if (frm.is_new()) return;

        const roles = new Set(frappe.user_roles || []);
        if (!(roles.has("University Placement Officer") || roles.has("University Admin")
              || roles.has("System Manager") || roles.has("Administrator"))) {
            return;
        }

        // Add "Schedule Interview" helper when in Shortlisted state
        if (frm.doc.workflow_state === "Shortlisted") {
            frm.add_custom_button(__("Schedule Interview"), () => show_schedule_dialog(frm), __("Actions"));
        }
        // Add "Record Offer" helper when in Interview Scheduled state
        if (frm.doc.workflow_state === "Interview Scheduled") {
            frm.add_custom_button(__("Record Offer"), () => show_offer_dialog(frm), __("Actions"));
        }
    },
});


function show_schedule_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Schedule Interview for {0}", [frm.doc.student_name]),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small" style="margin-bottom:8px;">
                    Pick interview date / time / venue. The application will move to <b>Interview Scheduled</b>
                    and the student sees the interview info on the portal.
                </div>`,
            },
            { fieldname: "interview_date", label: __("Interview Date"), fieldtype: "Date", reqd: 1,
              default: frappe.datetime.add_days(frappe.datetime.get_today(), 7) },
            { fieldname: "interview_time", label: __("Interview Time"), fieldtype: "Time", reqd: 1,
              default: "10:00:00" },
            { fieldname: "interview_venue", label: __("Venue"), fieldtype: "Data", reqd: 1,
              default: "Auditorium A" },
            { fieldname: "interview_round", label: __("Round (e.g. Technical, HR)"), fieldtype: "Data" },
        ],
        primary_action_label: __("Schedule"),
        primary_action(values) {
            d.disable_primary_action();
            frm.set_value("interview_date", values.interview_date);
            frm.set_value("interview_time", values.interview_time);
            frm.set_value("interview_venue", values.interview_venue);
            if (values.interview_round) frm.set_value("interview_round", values.interview_round);
            frm.save().then(() => {
                frappe.xcall("frappe.model.workflow.apply_workflow", {
                    doc: frm.doc,
                    action: "Schedule Interview",
                }).then(() => {
                    frappe.show_alert({ message: __("Interview scheduled."), indicator: "green" }, 5);
                    d.hide();
                    frm.reload_doc();
                }).catch(() => d.enable_primary_action());
            }).catch(() => d.enable_primary_action());
        },
    });
    d.show();
}


function show_offer_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Record Offer for {0}", [frm.doc.student_name]),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small" style="margin-bottom:8px;">
                    Enter the offered CTC. The application will move to <b>Offer Received</b>
                    and the student can accept or decline from the portal.
                </div>`,
            },
            { fieldname: "package_offered", label: __("Offered Package (₹/year)"), fieldtype: "Currency", reqd: 1 },
            { fieldname: "remarks", label: __("Remarks"), fieldtype: "Small Text" },
        ],
        primary_action_label: __("Record Offer"),
        primary_action(values) {
            d.disable_primary_action();
            frm.set_value("package_offered", values.package_offered);
            if (values.remarks) frm.set_value("remarks", values.remarks);
            frm.save().then(() => {
                frappe.xcall("frappe.model.workflow.apply_workflow", {
                    doc: frm.doc,
                    action: "Mark Offer Received",
                }).then(() => {
                    // Mirror to the offered_ctc column that some reports key off
                    frappe.db.set_value("Placement Application", frm.doc.name, "offered_ctc", values.package_offered).then(() => {
                        frappe.show_alert({ message: __("Offer recorded — awaiting student acceptance."), indicator: "green" }, 5);
                        d.hide();
                        frm.reload_doc();
                    });
                }).catch(() => d.enable_primary_action());
            }).catch(() => d.enable_primary_action());
        },
    });
    d.show();
}

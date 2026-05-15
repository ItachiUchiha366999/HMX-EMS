/**
 * Student doctype — adds an "Issue Hall Ticket" desk-side action so the
 * registrar can issue a complete exam hall ticket for a student in one click.
 * Pulls the student's enrolled courses for the current term automatically.
 */
frappe.ui.form.on("Student", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.docstatus !== 0) return;

        const roles = new Set(frappe.user_roles || []);
        const examCell = roles.has("University Registrar") || roles.has("University Exam Cell")
            || roles.has("System Manager") || roles.has("Administrator");
        const hostelStaff = roles.has("University Admin") || roles.has("University Warden")
            || roles.has("University Registrar") || roles.has("System Manager") || roles.has("Administrator");

        if (examCell) {
            frm.add_custom_button(__("Issue Hall Ticket"), () => show_ht_dialog(frm), __("Create"));
        }
        if (hostelStaff) {
            frm.add_custom_button(__("Allot Hostel Room"), () => show_hostel_dialog(frm), __("Create"));
        }
        const transportStaff = roles.has("University Admin") || roles.has("University Registrar")
            || roles.has("University Transport") || roles.has("System Manager") || roles.has("Administrator");
        if (transportStaff) {
            frm.add_custom_button(__("Allot Transport Route"), () => show_transport_dialog(frm), __("Create"));
        }
    },
});

function show_transport_dialog(frm) {
    frappe.call({
        method: "university_erp.university_transport.doctype.transport_allocation.transport_allocation_actions.list_active_routes",
        args: {},
        callback(r) {
            const routes = (r.message || []);
            if (!routes.length) {
                frappe.msgprint(__("No active transport routes. Create routes first under /app/transport-route."));
                return;
            }
            const routeOpts = routes.map(rt =>
                `${rt.name} | ${rt.start_point || "—"} → ${rt.end_point || "—"} · ₹${rt.monthly_fare || 0}/mo · vehicle ${rt.assigned_vehicle || "TBD"}`
            );

            const d = new frappe.ui.Dialog({
                title: __("Allot Transport Route to {0}", [frm.doc.student_name]),
                fields: [
                    {
                        fieldname: "info",
                        fieldtype: "HTML",
                        options: `<div class="text-muted small" style="margin-bottom:8px;">
                            Pick a route. Vehicle, fare, and pickup/drop times come from the route master.
                            The allocation lands in <b>Pending Approval</b>; the registrar approves on the form.
                        </div>`,
                    },
                    {
                        fieldname: "route_label",
                        label: __("Route"),
                        fieldtype: "Select",
                        options: routeOpts.join("\n"),
                        reqd: 1,
                        default: routeOpts[0],
                    },
                    {
                        fieldname: "pickup_stop",
                        label: __("Pickup Stop"),
                        fieldtype: "Data",
                        description: __("Optional — student's home pickup point"),
                    },
                    {
                        fieldname: "drop_stop",
                        label: __("Drop Stop"),
                        fieldtype: "Data",
                        description: __("Optional — usually the campus stop"),
                    },
                    {
                        fieldname: "from_date",
                        label: __("From Date"),
                        fieldtype: "Date",
                        default: frappe.datetime.get_today(),
                        reqd: 1,
                    },
                    {
                        fieldname: "to_date",
                        label: __("To Date"),
                        fieldtype: "Date",
                        default: frappe.datetime.add_months(frappe.datetime.get_today(), 12),
                    },
                ],
                primary_action_label: __("Allot Route"),
                primary_action(values) {
                    d.disable_primary_action();
                    const route_id = values.route_label.split(" | ")[0];
                    frappe.call({
                        method: "university_erp.university_transport.doctype.transport_allocation.transport_allocation_actions.allot_transport",
                        args: {
                            student: frm.doc.name,
                            route: route_id,
                            pickup_stop: values.pickup_stop || null,
                            drop_stop: values.drop_stop || null,
                            from_date: values.from_date,
                            to_date: values.to_date,
                        },
                        callback(rr) {
                            if (rr.message) {
                                frappe.show_alert({
                                    message: __("Allocation {0} created (route {1}). Awaiting registrar approval.",
                                        [rr.message.name, rr.message.route_name]),
                                    indicator: "green",
                                }, 5);
                                d.hide();
                                setTimeout(() => frappe.set_route("Form", "Transport Allocation", rr.message.name), 800);
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

function show_hostel_dialog(frm) {
    frappe.call({
        method: "university_erp.university_hostel.doctype.hostel_allocation.hostel_allocation_actions.list_available_rooms",
        args: {},
        callback(r) {
            const rooms = (r.message || []);
            if (!rooms.length) {
                frappe.msgprint(__("No rooms with available beds. Add beds or release allocations first."));
                return;
            }
            const roomOpts = rooms.map(rm =>
                `${rm.name} | ${rm.building_name || rm.hostel_building} · floor ${rm.floor || "—"} · ${rm.room_type} · beds ${rm.available_beds}/${rm.capacity}`
            );
            const d = new frappe.ui.Dialog({
                title: __("Allot Hostel Room to {0}", [frm.doc.student_name]),
                fields: [
                    {
                        fieldname: "info",
                        fieldtype: "HTML",
                        options: `<div class="text-muted small" style="margin-bottom:8px;">
                            Pick a room with at least one available bed. The allocation lands in
                            <b>Pending Warden Approval</b>. Warden then approves on the Hostel Allocation form.
                        </div>`,
                    },
                    {
                        fieldname: "room_label",
                        label: __("Room"),
                        fieldtype: "Select",
                        options: roomOpts.join("\n"),
                        reqd: 1,
                        default: roomOpts[0],
                    },
                    {
                        fieldname: "from_date",
                        label: __("From Date"),
                        fieldtype: "Date",
                        default: frappe.datetime.get_today(),
                        reqd: 1,
                    },
                    {
                        fieldname: "to_date",
                        label: __("To Date"),
                        fieldtype: "Date",
                        default: frappe.datetime.add_months(frappe.datetime.get_today(), 12),
                    },
                ],
                primary_action_label: __("Allot Room"),
                primary_action(values) {
                    d.disable_primary_action();
                    const room_id = values.room_label.split(" | ")[0];
                    frappe.call({
                        method: "university_erp.university_hostel.doctype.hostel_allocation.hostel_allocation_actions.allot_room",
                        args: {
                            student: frm.doc.name,
                            room: room_id,
                            from_date: values.from_date,
                            to_date: values.to_date,
                        },
                        callback(rr) {
                            if (rr.message) {
                                frappe.show_alert({
                                    message: __("Allocation {0} created (room {1}). Awaiting warden approval.", [rr.message.name, rr.message.room]),
                                    indicator: "green",
                                }, 5);
                                d.hide();
                                setTimeout(() => frappe.set_route("Form", "Hostel Allocation", rr.message.name), 800);
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


function show_ht_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Issue Hall Ticket for {0}", [frm.doc.student_name]),
        fields: [
            {
                fieldname: "info",
                fieldtype: "HTML",
                options: `<div class="text-muted small" style="margin-bottom:8px;">
                    Pulls the student's enrolled courses for the chosen term and creates
                    a draft Hall Ticket. Walk it through the workflow afterwards.
                </div>`,
            },
            {
                fieldname: "academic_term",
                label: __("Academic Term"),
                fieldtype: "Link",
                options: "Academic Term",
                reqd: 1,
                description: __("Defaults to the student's most-recent program enrollment term"),
            },
            {
                fieldname: "exam_type",
                label: __("Exam Type"),
                fieldtype: "Select",
                options: "Regular\nMid-Term\nSupplementary\nMakeup",
                default: "Regular",
                reqd: 1,
            },
        ],
        primary_action_label: __("Create Hall Ticket"),
        primary_action(values) {
            d.disable_primary_action();
            frappe.call({
                method: "university_erp.university_examinations.doctype.hall_ticket.hall_ticket_actions.issue_hall_ticket",
                args: {
                    student: frm.doc.name,
                    academic_term: values.academic_term,
                    exam_type: values.exam_type,
                },
                callback(r) {
                    if (r.message) {
                        const m = r.message;
                        frappe.show_alert({
                            message: __("Hall Ticket {0} created with {1} exams. Opening it...", [m.name, m.exam_count]),
                            indicator: "green",
                        }, 5);
                        d.hide();
                        setTimeout(() => frappe.set_route("Form", "Hall Ticket", m.name), 800);
                    }
                },
                error() {
                    d.enable_primary_action();
                },
            });
        },
    });

    // Pre-fill term from active program enrollment
    frappe.db.get_value("Program Enrollment",
        {student: frm.doc.name, docstatus: 1},
        "academic_term").then(r => {
            if (r.message && r.message.academic_term) {
                d.set_value("academic_term", r.message.academic_term);
            }
            d.show();
        });
}

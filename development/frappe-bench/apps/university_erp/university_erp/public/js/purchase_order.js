/**
 * University Inventory — Purchase Order client-side calculator.
 *
 * Server-side `set_item_details` + `calculate_totals` + `calculate_taxes` only
 * fire on save. Without these client-side hooks the user sees ₹0 in the
 * Amount column and Totals section until they click Save, which is confusing.
 *
 * This script:
 *   - Recomputes `amount` for an item row whenever qty or rate changes
 *   - Rolls up Total Quantity, Total, and Grand Total live
 *   - Applies the same tax-charge logic the controller uses
 */
frappe.ui.form.on("Purchase Order", {
    onload(frm) {
        // Reuse the same recalc pipeline whenever any totals input changes
        ["discount_amount"].forEach((f) => {
            frm.fields_dict[f] && frm.fields_dict[f].$wrapper.on("change", () => recalc_all(frm));
        });
    },

    refresh(frm) {
        recalc_all(frm);
    },

    discount_amount(frm) {
        recalc_all(frm);
    },

    validate(frm) {
        // Final pass before save — server will recompute again, but make
        // sure the in-memory values match expectation
        recalc_all(frm);
    },
});

frappe.ui.form.on("Purchase Order Item", {
    qty(frm, cdt, cdn)  { recalc_row(frm, cdt, cdn); recalc_totals(frm); },
    rate(frm, cdt, cdn) { recalc_row(frm, cdt, cdn); recalc_totals(frm); },
    items_remove(frm)   { recalc_totals(frm); },
    items_add(frm)      { recalc_totals(frm); },
});

frappe.ui.form.on("Purchase Taxes and Charges", {
    rate(frm)             { recalc_taxes(frm); },
    tax_amount(frm)       { recalc_taxes(frm); },
    charge_type(frm)      { recalc_taxes(frm); },
    add_deduct_tax(frm)   { recalc_taxes(frm); },
    taxes_remove(frm)     { recalc_taxes(frm); },
    taxes_add(frm)        { recalc_taxes(frm); },
});

function recalc_row(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row) return;
    const qty = flt(row.qty);
    const rate = flt(row.rate);
    row.amount = qty * rate;
    frm.refresh_field("items");
}

function recalc_totals(frm) {
    let total_qty = 0;
    let total = 0;
    (frm.doc.items || []).forEach((row) => {
        // Defensive: in case a row was added but qty/rate haven't been set
        const qty = flt(row.qty);
        const rate = flt(row.rate);
        row.amount = qty * rate;
        total_qty += qty;
        total += row.amount;
    });
    frm.set_value("total_qty", total_qty);
    frm.set_value("total", total);
    recalc_taxes(frm);
}

function recalc_taxes(frm) {
    const total = flt(frm.doc.total);
    const discount = flt(frm.doc.discount_amount);
    const net_total = total - discount;
    let cumulative_total = net_total;
    let total_taxes = 0;

    const taxes = frm.doc.taxes || [];
    taxes.forEach((tax, idx) => {
        const rate = flt(tax.rate);
        let tax_amount = 0;

        if (tax.charge_type === "Actual") {
            tax_amount = rate;
        } else if (tax.charge_type === "On Net Total") {
            tax_amount = (net_total * rate) / 100;
        } else if (tax.charge_type === "On Previous Row Amount") {
            const ref = taxes[parseInt(tax.row_id, 10) - 1];
            tax_amount = ref ? (flt(ref.tax_amount) * rate) / 100 : 0;
        } else if (tax.charge_type === "On Previous Row Total") {
            const ref = taxes[parseInt(tax.row_id, 10) - 1];
            tax_amount = ref ? (flt(ref.total) * rate) / 100 : 0;
        }

        tax.tax_amount = tax_amount;
        if (tax.add_deduct_tax === "Deduct") {
            cumulative_total -= tax_amount;
            total_taxes -= tax_amount;
        } else {
            cumulative_total += tax_amount;
            total_taxes += tax_amount;
        }
        tax.total = cumulative_total;
    });

    frm.set_value("total_taxes_and_charges", total_taxes);
    const grand_total = total - discount + total_taxes;
    frm.set_value("grand_total", grand_total);
    frm.set_value("rounded_total", Math.round(grand_total));
    frm.refresh_field("taxes");
}

function recalc_all(frm) {
    recalc_totals(frm);
}

function flt(v) {
    const n = Number(v);
    return isNaN(n) ? 0 : n;
}

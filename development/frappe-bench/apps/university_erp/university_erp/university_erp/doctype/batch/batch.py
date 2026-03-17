# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class Batch(Document):
    """Batch - Batch tracking for inventory items"""

    def autoname(self):
        """Generate batch ID"""
        if self.naming_series:
            from frappe.model.naming import make_autoname
            self.name = make_autoname(self.naming_series, doc=self)
            self.batch_id = self.name

    def validate(self):
        """Validate batch"""
        self.validate_dates()

    def validate_dates(self):
        """Validate manufacturing and expiry dates"""
        if self.manufacturing_date and self.expiry_date:
            if getdate(self.manufacturing_date) > getdate(self.expiry_date):
                frappe.throw(_("Manufacturing Date cannot be after Expiry Date"))

    def update_batch_qty(self):
        """Update batch quantity from stock ledger"""
        qty = frappe.db.sql("""
            SELECT SUM(actual_qty) as qty
            FROM `tabStock Ledger Entry`
            WHERE batch_no = %s AND is_cancelled = 0
        """, self.name)[0][0] or 0

        self.batch_qty = flt(qty)
        self.db_set("batch_qty", self.batch_qty)

    def on_trash(self):
        """Validate before deletion"""
        if frappe.db.exists("Stock Ledger Entry", {"batch_no": self.name}):
            frappe.throw(
                _("Cannot delete batch {0} as it has stock transactions").format(self.name)
            )


def get_batch_qty(batch_no, warehouse=None):
    """Get batch quantity"""
    conditions = "batch_no = %(batch_no)s AND is_cancelled = 0"
    values = {"batch_no": batch_no}

    if warehouse:
        conditions += " AND warehouse = %(warehouse)s"
        values["warehouse"] = warehouse

    qty = frappe.db.sql("""
        SELECT SUM(actual_qty) as qty
        FROM `tabStock Ledger Entry`
        WHERE {conditions}
    """.format(conditions=conditions), values)[0][0] or 0

    return flt(qty)


@frappe.whitelist()
def get_batches_for_item(item_code, warehouse=None, include_expired=False):
    """Get available batches for an item"""
    conditions = ["item_code = %(item_code)s"]
    values = {"item_code": item_code}

    if not include_expired:
        conditions.append("(expiry_date IS NULL OR expiry_date >= %(today)s)")
        values["today"] = nowdate()

    batches = frappe.get_all(
        "Batch",
        filters=" AND ".join(conditions),
        fields=["name", "batch_id", "expiry_date", "manufacturing_date", "batch_qty"],
        order_by="expiry_date asc, creation asc"
    )

    # Update quantities from stock ledger
    for batch in batches:
        batch["qty"] = get_batch_qty(batch.name, warehouse)

    # Filter out zero quantity batches
    batches = [b for b in batches if flt(b.qty) > 0]

    return batches


@frappe.whitelist()
def create_batch(item_code, batch_id=None, expiry_date=None, manufacturing_date=None,
                 supplier=None, reference_doctype=None, reference_name=None):
    """Create a new batch"""
    batch = frappe.get_doc({
        "doctype": "Batch",
        "item_code": item_code,
        "expiry_date": expiry_date,
        "manufacturing_date": manufacturing_date,
        "supplier": supplier,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name
    })

    if batch_id:
        batch.batch_id = batch_id

    batch.insert(ignore_permissions=True)

    return batch.name

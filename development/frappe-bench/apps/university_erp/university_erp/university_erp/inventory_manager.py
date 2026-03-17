# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Inventory Manager - Helper functions for inventory management
"""

import frappe
from frappe import _
from frappe.utils import flt, nowdate, getdate, add_days


class InventoryManager:
    """Manager class for inventory operations"""

    @staticmethod
    def get_stock_balance(item_code, warehouse=None):
        """Get current stock balance for an item

        Args:
            item_code: Item code
            warehouse: Optional warehouse filter

        Returns:
            dict with qty and value
        """
        filters = {"item_code": item_code, "is_cancelled": 0}
        if warehouse:
            filters["warehouse"] = warehouse

        # Get latest stock ledger entry
        sle = frappe.db.sql("""
            SELECT
                SUM(actual_qty) as qty,
                MAX(qty_after_transaction) as balance_qty,
                AVG(valuation_rate) as valuation_rate
            FROM `tabStock Ledger Entry`
            WHERE item_code = %(item_code)s
            {warehouse_filter}
            AND is_cancelled = 0
        """.format(
            warehouse_filter="AND warehouse = %(warehouse)s" if warehouse else ""
        ), {
            "item_code": item_code,
            "warehouse": warehouse
        }, as_dict=True)

        if sle and sle[0].qty:
            return {
                "qty": flt(sle[0].qty),
                "valuation_rate": flt(sle[0].valuation_rate),
                "value": flt(sle[0].qty) * flt(sle[0].valuation_rate)
            }

        return {"qty": 0, "valuation_rate": 0, "value": 0}

    @staticmethod
    def get_stock_balance_by_warehouse(item_code):
        """Get stock balance for an item across all warehouses

        Args:
            item_code: Item code

        Returns:
            list of dicts with warehouse, qty, value
        """
        return frappe.db.sql("""
            SELECT
                warehouse,
                SUM(actual_qty) as qty,
                AVG(valuation_rate) as valuation_rate,
                SUM(actual_qty) * AVG(valuation_rate) as value
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s
            AND is_cancelled = 0
            GROUP BY warehouse
            HAVING SUM(actual_qty) != 0
            ORDER BY warehouse
        """, item_code, as_dict=True)

    @staticmethod
    def get_low_stock_items(warehouse=None):
        """Get items below reorder level

        Args:
            warehouse: Optional warehouse filter

        Returns:
            list of items below reorder level
        """
        items = frappe.db.sql("""
            SELECT
                ii.name as item_code,
                ii.item_name,
                ii.item_group,
                ii.reorder_level,
                ii.reorder_quantity,
                ii.default_warehouse,
                COALESCE(SUM(sle.actual_qty), 0) as current_stock
            FROM `tabInventory Item` ii
            LEFT JOIN `tabStock Ledger Entry` sle ON sle.item_code = ii.name
                AND sle.is_cancelled = 0
                {warehouse_filter}
            WHERE ii.maintain_stock = 1
            AND ii.is_active = 1
            AND ii.reorder_level > 0
            GROUP BY ii.name
            HAVING current_stock <= ii.reorder_level
            ORDER BY (ii.reorder_level - current_stock) DESC
        """.format(
            warehouse_filter="AND sle.warehouse = %(warehouse)s" if warehouse else ""
        ), {"warehouse": warehouse}, as_dict=True)

        return items

    @staticmethod
    def create_stock_entry(entry_type, items, from_warehouse=None, to_warehouse=None,
                          posting_date=None, reference_doctype=None, reference_name=None):
        """Create a stock entry

        Args:
            entry_type: Type of entry (Material Receipt, Issue, Transfer, etc.)
            items: List of item dicts with item_code, qty, rate
            from_warehouse: Source warehouse for issue/transfer
            to_warehouse: Target warehouse for receipt/transfer
            posting_date: Posting date
            reference_doctype: Reference document type
            reference_name: Reference document name

        Returns:
            Stock Entry document
        """
        se = frappe.new_doc("Stock Entry")
        se.entry_type = entry_type
        se.posting_date = posting_date or nowdate()

        if from_warehouse:
            se.from_warehouse = from_warehouse
        if to_warehouse:
            se.to_warehouse = to_warehouse

        if reference_doctype and reference_name:
            se.reference_doctype = reference_doctype
            se.reference_name = reference_name

        for item in items:
            row = se.append("items", {
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "rate": item.get("rate", 0)
            })

            if item.get("s_warehouse"):
                row.s_warehouse = item.get("s_warehouse")
            elif from_warehouse:
                row.s_warehouse = from_warehouse

            if item.get("t_warehouse"):
                row.t_warehouse = item.get("t_warehouse")
            elif to_warehouse:
                row.t_warehouse = to_warehouse

            if item.get("batch_no"):
                row.batch_no = item.get("batch_no")

        return se

    @staticmethod
    def process_material_receipt(purchase_order):
        """Create material receipt from purchase order

        Args:
            purchase_order: Purchase Order name

        Returns:
            Stock Entry document
        """
        from university_erp.university_erp.doctype.purchase_order.purchase_order import make_stock_entry
        return make_stock_entry(purchase_order)

    @staticmethod
    def process_material_issue(material_request):
        """Create material issue from material request

        Args:
            material_request: Material Request name

        Returns:
            Stock Entry document
        """
        from university_erp.university_erp.doctype.material_request.material_request import make_stock_entry
        return make_stock_entry(material_request)

    @staticmethod
    def get_stock_ledger(item_code, warehouse=None, from_date=None, to_date=None):
        """Get stock ledger entries for an item

        Args:
            item_code: Item code
            warehouse: Optional warehouse filter
            from_date: Start date
            to_date: End date

        Returns:
            list of stock ledger entries
        """
        filters = {"item_code": item_code, "is_cancelled": 0}

        if warehouse:
            filters["warehouse"] = warehouse

        date_filter = ""
        if from_date:
            date_filter += " AND posting_date >= %(from_date)s"
        if to_date:
            date_filter += " AND posting_date <= %(to_date)s"

        return frappe.db.sql("""
            SELECT
                name, posting_date, posting_time, warehouse,
                actual_qty, qty_after_transaction, incoming_rate,
                outgoing_rate, valuation_rate, stock_value,
                voucher_type, voucher_no, batch_no
            FROM `tabStock Ledger Entry`
            WHERE item_code = %(item_code)s
            AND is_cancelled = 0
            {warehouse_filter}
            {date_filter}
            ORDER BY posting_date, posting_time, name
        """.format(
            warehouse_filter="AND warehouse = %(warehouse)s" if warehouse else "",
            date_filter=date_filter
        ), {
            "item_code": item_code,
            "warehouse": warehouse,
            "from_date": from_date,
            "to_date": to_date
        }, as_dict=True)

    @staticmethod
    def get_stock_summary_report(warehouse=None):
        """Get stock summary for all items

        Args:
            warehouse: Optional warehouse filter

        Returns:
            list of items with stock summary
        """
        return frappe.db.sql("""
            SELECT
                sle.item_code,
                ii.item_name,
                ii.item_group,
                sle.warehouse,
                SUM(sle.actual_qty) as qty,
                AVG(sle.valuation_rate) as valuation_rate,
                SUM(sle.actual_qty) * AVG(sle.valuation_rate) as value,
                ii.reorder_level,
                CASE
                    WHEN SUM(sle.actual_qty) <= 0 THEN 'Out of Stock'
                    WHEN SUM(sle.actual_qty) <= ii.reorder_level THEN 'Low Stock'
                    ELSE 'In Stock'
                END as stock_status
            FROM `tabStock Ledger Entry` sle
            INNER JOIN `tabInventory Item` ii ON ii.name = sle.item_code
            WHERE sle.is_cancelled = 0
            {warehouse_filter}
            GROUP BY sle.item_code, sle.warehouse
            ORDER BY ii.item_name, sle.warehouse
        """.format(
            warehouse_filter="AND sle.warehouse = %(warehouse)s" if warehouse else ""
        ), {"warehouse": warehouse}, as_dict=True)

    @staticmethod
    def auto_create_material_request():
        """Create material requests for items below reorder level

        Returns:
            list of created material request names
        """
        low_stock_items = InventoryManager.get_low_stock_items()
        created_requests = []

        # Group by default warehouse
        warehouse_items = {}
        for item in low_stock_items:
            warehouse = item.default_warehouse or "Main Store"
            if warehouse not in warehouse_items:
                warehouse_items[warehouse] = []
            warehouse_items[warehouse].append(item)

        for warehouse, items in warehouse_items.items():
            mr = frappe.new_doc("Material Request")
            mr.material_request_type = "Purchase"
            mr.transaction_date = nowdate()
            mr.set_warehouse = warehouse
            mr.reason = "Auto-generated for items below reorder level"

            for item in items:
                mr.append("items", {
                    "item_code": item.item_code,
                    "qty": item.reorder_quantity or (item.reorder_level - item.current_stock),
                    "warehouse": warehouse,
                    "schedule_date": add_days(nowdate(), 7)
                })

            mr.insert()
            created_requests.append(mr.name)
            frappe.msgprint(_("Material Request {0} created for warehouse {1}").format(
                mr.name, warehouse
            ))

        return created_requests

    @staticmethod
    def get_item_valuation(item_code, warehouse=None, method="FIFO"):
        """Get item valuation

        Args:
            item_code: Item code
            warehouse: Warehouse
            method: Valuation method (FIFO, Moving Average, LIFO)

        Returns:
            dict with qty, rate, value
        """
        stock = InventoryManager.get_stock_balance(item_code, warehouse)
        return stock

    @staticmethod
    def update_valuation_rate(item_code, warehouse):
        """Update valuation rate for an item in warehouse

        Args:
            item_code: Item code
            warehouse: Warehouse
        """
        stock = InventoryManager.get_stock_balance(item_code, warehouse)

        # Update item master
        frappe.db.set_value("Inventory Item", item_code, {
            "valuation_rate": stock.get("valuation_rate", 0),
            "current_stock": stock.get("qty", 0),
            "total_stock_value": stock.get("value", 0)
        })


# Whitelist API functions

@frappe.whitelist()
def get_item_details(item_code, warehouse=None):
    """Get item details for form auto-fill"""
    item = frappe.get_cached_doc("Inventory Item", item_code)

    stock = InventoryManager.get_stock_balance(item_code, warehouse)

    return {
        "item_code": item.item_code,
        "item_name": item.item_name,
        "item_group": item.item_group,
        "uom": item.unit_of_measure,
        "rate": item.standard_rate or item.valuation_rate or 0,
        "stock_qty": stock.get("qty", 0),
        "valuation_rate": stock.get("valuation_rate", 0),
        "default_warehouse": item.default_warehouse
    }


@frappe.whitelist()
def get_stock_balance(item_code, warehouse=None):
    """Get stock balance for item"""
    return InventoryManager.get_stock_balance(item_code, warehouse)


@frappe.whitelist()
def get_warehouse_stock(warehouse):
    """Get stock summary for a warehouse"""
    return InventoryManager.get_stock_summary_report(warehouse)


@frappe.whitelist()
def get_supplier_details(supplier):
    """Get supplier info"""
    return frappe.get_cached_doc("Supplier", supplier).as_dict()


@frappe.whitelist()
def get_items_below_reorder(warehouse=None):
    """Get items below reorder level"""
    return InventoryManager.get_low_stock_items(warehouse)


@frappe.whitelist()
def get_item_price(item_code, price_list=None):
    """Get item price from price list or item master"""
    item = frappe.get_cached_doc("Inventory Item", item_code)

    # For now, return from item master
    # Can be extended to support price lists
    return {
        "rate": item.standard_rate or item.last_purchase_rate or 0,
        "valuation_rate": item.valuation_rate or 0
    }

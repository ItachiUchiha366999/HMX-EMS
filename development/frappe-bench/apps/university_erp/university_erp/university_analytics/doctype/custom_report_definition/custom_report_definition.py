# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class CustomReportDefinition(Document):
    def validate(self):
        """Validate report definition"""
        self.validate_columns()
        self.validate_chart_config()

    def validate_columns(self):
        """Ensure at least one column is defined"""
        if not self.columns:
            frappe.throw(_("At least one column must be defined"))

    def validate_chart_config(self):
        """Validate chart configuration JSON"""
        if self.include_chart and self.chart_config:
            try:
                json.loads(self.chart_config)
            except json.JSONDecodeError:
                frappe.throw(_("Chart Config must be valid JSON"))

    def build_query(self, filters=None):
        """
        Build SQL query from definition

        Args:
            filters: Dict of filter values

        Returns:
            tuple: (query_string, values)
        """
        # Build SELECT clause
        select_fields = []
        for col in self.columns:
            field = col.field_name
            if col.aggregation and col.aggregation != "None":
                field = f"{col.aggregation}({col.field_name})"
            if col.field_label != col.field_name:
                field = f"{field} as `{col.field_label}`"
            select_fields.append(field)

        select_clause = ", ".join(select_fields)

        # Build FROM clause with joins
        from_clause = f"`tab{self.primary_doctype}`"

        if self.joins:
            for join in self.joins:
                join_type = join.join_type or "LEFT"
                from_clause += f" {join_type} JOIN `tab{join.doctype_link}` ON "
                from_clause += f"`tab{self.primary_doctype}`.{join.parent_field} = "
                from_clause += f"`tab{join.doctype_link}`.{join.join_field}"

        # Build WHERE clause
        where_conditions = []
        values = {}

        if filters:
            for filter_def in self.filters:
                field_name = filter_def.field_name
                if field_name in filters and filters[field_name]:
                    where_conditions.append(f"`{field_name}` = %({field_name})s")
                    values[field_name] = filters[field_name]

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Build GROUP BY clause
        group_by_clause = ""
        if self.group_by_fields:
            group_by_clause = f"GROUP BY {self.group_by_fields}"
            if self.having_clause:
                group_by_clause += f" HAVING {self.having_clause}"

        # Build ORDER BY clause
        order_by_clause = ""
        if self.sort_by:
            order_by_clause = f"ORDER BY {self.sort_by} {self.sort_order or 'ASC'}"

        # Build LIMIT clause
        limit_clause = ""
        if self.row_limit:
            limit_clause = f"LIMIT {cint(self.row_limit)}"

        # Combine query
        query = """
            SELECT {select_clause}
            FROM {from_clause}
            WHERE {where_clause}
            {group_by_clause}
            {order_by_clause}
            {limit_clause}
        """.format(from_clause=from_clause, group_by_clause=group_by_clause, limit_clause=limit_clause, order_by_clause=order_by_clause, select_clause=select_clause, where_clause=where_clause)

        return query.strip(), values

    def execute(self, filters=None):
        """
        Execute the custom report

        Args:
            filters: Dict of filter values

        Returns:
            dict: Report data with columns and rows
        """
        query, values = self.build_query(filters)

        try:
            data = frappe.db.sql(query, values, as_dict=True)
        except Exception as e:
            frappe.log_error(f"Custom Report Error: {str(e)}", "Custom Report Definition")
            frappe.throw(_("Error executing report: {0}").format(str(e)))

        columns = []
        for col in self.columns:
            columns.append({
                "fieldname": col.field_label or col.field_name,
                "label": col.field_label,
                "fieldtype": col.field_type or "Data",
                "width": col.width or 150,
                "options": col.link_to
            })

        return {
            "columns": columns,
            "data": data
        }

    def generate_chart(self, data):
        """
        Generate chart configuration from data

        Args:
            data: List of data rows

        Returns:
            dict: Chart configuration
        """
        if not self.include_chart or not data:
            return None

        if self.chart_config:
            config = json.loads(self.chart_config)
        else:
            config = {}

        # Auto-generate basic chart config if not provided
        if not config.get("data"):
            labels = []
            values = []

            label_field = self.columns[0].field_label if self.columns else None
            value_field = self.columns[1].field_label if len(self.columns) > 1 else None

            if label_field and value_field:
                for row in data[:10]:  # Limit to 10 items
                    labels.append(str(row.get(label_field, "")))
                    values.append(float(row.get(value_field, 0) or 0))

                config = {
                    "type": self.chart_type.lower() if self.chart_type else "bar",
                    "data": {
                        "labels": labels,
                        "datasets": [{
                            "values": values
                        }]
                    }
                }

        return config

    def has_access(self, user=None):
        """
        Check if user has access to this report

        Args:
            user: User to check. Defaults to current user.

        Returns:
            bool: True if user has access
        """
        if not user:
            user = frappe.session.user

        if user == "Administrator":
            return True

        if self.is_public:
            return True

        if self.allowed_roles:
            user_roles = frappe.get_roles(user)
            for allowed_role in self.allowed_roles:
                if allowed_role.role in user_roles:
                    return True

        return False

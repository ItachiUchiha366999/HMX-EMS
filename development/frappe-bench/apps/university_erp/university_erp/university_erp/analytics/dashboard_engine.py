# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, now_datetime


class DashboardEngine:
    """
    Engine class for dashboard data retrieval and widget rendering
    """

    def get_dashboard_data(self, dashboard_name, filters=None):
        """
        Get data for all widgets in a dashboard

        Args:
            dashboard_name: Name of Custom Dashboard
            filters: Optional dict with date_range, department, program filters

        Returns:
            dict: Widget data keyed by widget index
        """
        dashboard = frappe.get_doc("Custom Dashboard", dashboard_name)

        if not dashboard.has_access():
            frappe.throw(_("You don't have access to this dashboard"))

        # Increment view count
        dashboard.increment_view_count()

        widget_data = {}

        for idx, widget in enumerate(dashboard.widgets):
            try:
                widget_data[idx] = self.get_widget_data(widget, filters)
            except Exception as e:
                widget_data[idx] = {
                    "error": str(e),
                    "widget_title": widget.widget_title
                }

        return {
            "dashboard_name": dashboard.dashboard_name,
            "dashboard_type": dashboard.dashboard_type,
            "layout_type": dashboard.layout_type,
            "columns": dashboard.columns,
            "refresh_interval": dashboard.refresh_interval,
            "widgets": widget_data,
            "last_updated": now_datetime()
        }

    def get_widget_data(self, widget, filters=None):
        """
        Get data for a single widget

        Args:
            widget: Dashboard Widget child table row
            filters: Optional filters

        Returns:
            dict: Widget data with type, title, and data
        """
        data = None

        if widget.data_source == "Report":
            data = self._get_report_data(widget, filters)
        elif widget.data_source == "Query":
            data = self._execute_query(widget, filters)
        elif widget.data_source == "Method":
            data = self._execute_method(widget, filters)
        elif widget.data_source == "Static":
            data = self._get_static_data(widget)

        return {
            "widget_title": widget.widget_title,
            "widget_type": widget.widget_type,
            "data_source": widget.data_source,
            "chart_type": widget.chart_type,
            "color": widget.color,
            "icon": widget.icon,
            "position": {
                "row": widget.position_row,
                "col": widget.position_col,
                "width": widget.width,
                "height": widget.height
            },
            "drill_down_link": widget.drill_down_link,
            "data": data
        }

    def _get_report_data(self, widget, filters=None):
        """
        Get data from a Frappe Report

        Args:
            widget: Widget configuration
            filters: Optional filters

        Returns:
            dict: Report data
        """
        if not widget.report_name:
            return None

        try:
            report = frappe.get_doc("Report", widget.report_name)

            # Build filters
            report_filters = {}
            if filters:
                if filters.get("from_date"):
                    report_filters["from_date"] = filters["from_date"]
                if filters.get("to_date"):
                    report_filters["to_date"] = filters["to_date"]
                if filters.get("department"):
                    report_filters["department"] = filters["department"]
                if filters.get("program"):
                    report_filters["program"] = filters["program"]

            # Execute report
            result = frappe.desk.query_report.run(
                widget.report_name,
                filters=report_filters,
                user=frappe.session.user
            )

            return {
                "columns": result.get("columns", []),
                "data": result.get("result", [])[:20],  # Limit rows for widgets
                "chart": result.get("chart"),
                "summary": result.get("report_summary")
            }
        except Exception as e:
            frappe.log_error(f"Report Widget Error: {str(e)}", "Dashboard Engine")
            return {"error": str(e)}

    def _execute_query(self, widget, filters=None):
        """
        Execute custom SQL query for widget

        Args:
            widget: Widget configuration
            filters: Optional filters

        Returns:
            list: Query results
        """
        if not widget.custom_query:
            return None

        query = widget.custom_query

        # Replace filter placeholders safely
        if filters:
            if filters.get("from_date"):
                query = query.replace("%(from_date)s", f"'{filters['from_date']}'")
            if filters.get("to_date"):
                query = query.replace("%(to_date)s", f"'{filters['to_date']}'")
            if filters.get("department"):
                query = query.replace("%(department)s", f"'{filters['department']}'")
            if filters.get("program"):
                query = query.replace("%(program)s", f"'{filters['program']}'")

        try:
            result = frappe.db.sql(query, as_dict=True)
            return self._format_widget_data(widget.widget_type, result)
        except Exception as e:
            frappe.log_error(f"Query Widget Error: {str(e)}", "Dashboard Engine")
            return {"error": str(e)}

    def _execute_method(self, widget, filters=None):
        """
        Execute Python method for widget data

        Args:
            widget: Widget configuration
            filters: Optional filters

        Returns:
            mixed: Method result
        """
        if not widget.method_path:
            return None

        try:
            method = frappe.get_attr(widget.method_path)
            result = method(filters)
            return self._format_widget_data(widget.widget_type, result)
        except Exception as e:
            frappe.log_error(f"Method Widget Error: {str(e)}", "Dashboard Engine")
            return {"error": str(e)}

    def _get_static_data(self, widget):
        """
        Get static/manual data for widget

        Args:
            widget: Widget configuration

        Returns:
            dict: Static data
        """
        # Static data could be stored in widget configuration
        return {
            "type": "static",
            "message": "Static data widget"
        }

    def _format_widget_data(self, widget_type, data):
        """
        Format data based on widget type

        Args:
            widget_type: Type of widget
            data: Raw data

        Returns:
            dict: Formatted data for widget
        """
        if not data:
            return None

        if widget_type == "Number Card":
            # Single value display
            if isinstance(data, list) and len(data) > 0:
                first_row = data[0]
                if isinstance(first_row, dict):
                    # Get first numeric value
                    for key, value in first_row.items():
                        if isinstance(value, (int, float)):
                            return {"value": value, "label": key}
                return {"value": first_row}
            return {"value": data}

        elif widget_type == "Progress Card":
            if isinstance(data, list) and len(data) > 0:
                row = data[0]
                return {
                    "value": flt(row.get("value", 0)),
                    "target": flt(row.get("target", 100)),
                    "percentage": (flt(row.get("value", 0)) / flt(row.get("target", 100))) * 100
                        if flt(row.get("target", 100)) > 0 else 0
                }
            return {"value": 0, "target": 100, "percentage": 0}

        elif widget_type in ["Chart", "Bar", "Line", "Pie", "Donut", "Area"]:
            # Format for chart display
            if isinstance(data, list):
                labels = []
                values = []
                for row in data:
                    if isinstance(row, dict):
                        keys = list(row.keys())
                        if len(keys) >= 2:
                            labels.append(str(row.get(keys[0], "")))
                            values.append(flt(row.get(keys[1], 0)))
                return {
                    "labels": labels,
                    "datasets": [{"values": values}]
                }
            return data

        elif widget_type == "Table":
            # Return as table data
            if isinstance(data, list):
                columns = []
                if len(data) > 0 and isinstance(data[0], dict):
                    columns = [{"label": k, "fieldname": k} for k in data[0].keys()]
                return {
                    "columns": columns,
                    "data": data[:20]  # Limit rows
                }
            return {"columns": [], "data": []}

        elif widget_type == "List":
            # Return as simple list
            if isinstance(data, list):
                return {"items": data[:10]}
            return {"items": []}

        elif widget_type == "Gauge":
            if isinstance(data, list) and len(data) > 0:
                row = data[0]
                return {
                    "value": flt(row.get("value", 0)),
                    "min": flt(row.get("min", 0)),
                    "max": flt(row.get("max", 100))
                }
            return {"value": 0, "min": 0, "max": 100}

        elif widget_type == "Trend":
            # Format for trend chart
            if isinstance(data, list):
                return {
                    "data": data,
                    "trend": self._calculate_trend(data)
                }
            return {"data": [], "trend": "stable"}

        elif widget_type == "Comparison":
            # Format for comparison display
            return data

        return data

    def _calculate_trend(self, data):
        """
        Calculate trend direction from data

        Args:
            data: List of data points

        Returns:
            str: "up", "down", or "stable"
        """
        if not data or len(data) < 2:
            return "stable"

        try:
            # Get first and last values
            if isinstance(data[0], dict):
                first_val = flt(list(data[0].values())[0] if data[0] else 0)
                last_val = flt(list(data[-1].values())[0] if data[-1] else 0)
            else:
                first_val = flt(data[0])
                last_val = flt(data[-1])

            if last_val > first_val:
                return "up"
            elif last_val < first_val:
                return "down"
            else:
                return "stable"
        except Exception:
            return "stable"

    def get_available_dashboards(self, user=None):
        """
        Get list of dashboards accessible by user

        Args:
            user: User to check. Defaults to current user.

        Returns:
            list: List of accessible dashboards
        """
        if not user:
            user = frappe.session.user

        if user == "Administrator":
            return frappe.get_all(
                "Custom Dashboard",
                filters={"is_active": 1},
                fields=["name", "dashboard_name", "dashboard_type", "description"]
            )

        user_roles = frappe.get_roles(user)

        # Get public dashboards
        dashboards = frappe.get_all(
            "Custom Dashboard",
            filters={"is_active": 1, "is_public": 1},
            fields=["name", "dashboard_name", "dashboard_type", "description"]
        )

        # Get dashboards by user access
        user_dashboards = frappe.db.sql("""
            SELECT DISTINCT cd.name, cd.dashboard_name, cd.dashboard_type, cd.description
            FROM `tabCustom Dashboard` cd
            INNER JOIN `tabDashboard User` du ON du.parent = cd.name
            WHERE cd.is_active = 1 AND du.user = %s
        """, user, as_dict=True)

        # Get dashboards by role access
        if user_roles:
            role_dashboards = frappe.db.sql("""
                SELECT DISTINCT cd.name, cd.dashboard_name, cd.dashboard_type, cd.description
                FROM `tabCustom Dashboard` cd
                INNER JOIN `tabDashboard Role` dr ON dr.parent = cd.name
                WHERE cd.is_active = 1 AND dr.role IN %s
            """, [user_roles], as_dict=True)
            dashboards.extend(role_dashboards)

        dashboards.extend(user_dashboards)

        # Remove duplicates
        seen = set()
        unique_dashboards = []
        for d in dashboards:
            if d["name"] not in seen:
                seen.add(d["name"])
                unique_dashboards.append(d)

        return unique_dashboards

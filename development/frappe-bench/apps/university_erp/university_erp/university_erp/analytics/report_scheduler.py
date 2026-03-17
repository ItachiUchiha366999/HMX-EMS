# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import json
import os
import frappe
from frappe import _
from frappe.utils import (
    now_datetime,
    getdate,
    add_days,
    add_months,
    get_first_day,
    get_last_day,
    cint
)


class ReportScheduler:
    """
    Scheduler class for automated report generation and distribution
    """

    def run_scheduled_reports(self):
        """
        Run all scheduled reports that are due

        Returns:
            list: Results of executed reports
        """
        now = now_datetime()

        due_reports = frappe.get_all(
            "Scheduled Report",
            filters={
                "is_enabled": 1,
                "next_run": ["<=", now]
            },
            pluck="name"
        )

        results = []

        for report_name in due_reports:
            try:
                result = self.execute_report(report_name)
                results.append({
                    "report": report_name,
                    "status": "Success",
                    "result": result
                })
            except Exception as e:
                frappe.log_error(f"Scheduled Report Error: {str(e)}", "Report Scheduler")
                results.append({
                    "report": report_name,
                    "status": "Failed",
                    "error": str(e)
                })
                # Update report status
                frappe.db.set_value("Scheduled Report", report_name, {
                    "last_run": now,
                    "last_run_status": "Failed"
                })

        return results

    def execute_report(self, scheduled_report_name):
        """
        Execute a scheduled report

        Args:
            scheduled_report_name: Name of Scheduled Report document

        Returns:
            dict: Execution result with file_url and status
        """
        scheduled_report = frappe.get_doc("Scheduled Report", scheduled_report_name)

        # Build filters
        filters = self._apply_dynamic_filters(scheduled_report)

        # Execute the Frappe report
        report_data = frappe.desk.query_report.run(
            scheduled_report.report,
            filters=filters,
            user="Administrator"
        )

        # Generate output file
        file_url = self._generate_output(
            scheduled_report,
            report_data
        )

        # Send/store report
        if scheduled_report.delivery_method in ["Email", "Both"]:
            self._send_email(scheduled_report, file_url)

        if scheduled_report.delivery_method in ["File Storage", "Both"]:
            self._store_file(scheduled_report, file_url)

        # Update report status
        scheduled_report.last_run = now_datetime()
        scheduled_report.last_run_status = "Success"
        scheduled_report.run_count = cint(scheduled_report.run_count) + 1
        scheduled_report.calculate_next_run()
        scheduled_report.save(ignore_permissions=True)

        return {
            "status": "Success",
            "file_url": file_url,
            "rows": len(report_data.get("result", []))
        }

    def _apply_dynamic_filters(self, scheduled_report):
        """
        Apply dynamic date filters based on current date

        Args:
            scheduled_report: Scheduled Report document

        Returns:
            dict: Filters to apply
        """
        filters = {}

        if scheduled_report.filters:
            try:
                filters = json.loads(scheduled_report.filters)
            except json.JSONDecodeError:
                pass

        if not scheduled_report.dynamic_filters:
            return filters

        today = getdate()

        if scheduled_report.frequency == "Daily":
            filters["from_date"] = add_days(today, -1)
            filters["to_date"] = add_days(today, -1)

        elif scheduled_report.frequency == "Weekly":
            # Previous week (Monday to Sunday)
            last_monday = add_days(today, -today.weekday() - 7)
            last_sunday = add_days(last_monday, 6)
            filters["from_date"] = last_monday
            filters["to_date"] = last_sunday

        elif scheduled_report.frequency == "Monthly":
            # Previous month
            first_of_month = get_first_day(today)
            last_month_end = add_days(first_of_month, -1)
            last_month_start = get_first_day(last_month_end)
            filters["from_date"] = last_month_start
            filters["to_date"] = last_month_end

        elif scheduled_report.frequency == "Quarterly":
            # Previous quarter
            current_quarter = (today.month - 1) // 3
            if current_quarter == 0:
                prev_quarter_start = today.replace(year=today.year - 1, month=10, day=1)
                prev_quarter_end = today.replace(year=today.year - 1, month=12, day=31)
            else:
                prev_quarter_start = today.replace(month=(current_quarter - 1) * 3 + 1, day=1)
                prev_quarter_end = add_days(
                    today.replace(month=current_quarter * 3 + 1, day=1),
                    -1
                )
            filters["from_date"] = prev_quarter_start
            filters["to_date"] = prev_quarter_end

        return filters

    def _generate_output(self, scheduled_report, report_data):
        """
        Generate report output in specified format

        Args:
            scheduled_report: Scheduled Report document
            report_data: Report execution result

        Returns:
            str: File URL or path
        """
        output_format = scheduled_report.output_format or "PDF"
        report_name = scheduled_report.report_name.replace(" ", "_")
        timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_name}_{timestamp}"

        columns = report_data.get("columns", [])
        data = report_data.get("result", [])

        if output_format == "Excel":
            return self._generate_excel(filename, columns, data)
        elif output_format == "CSV":
            return self._generate_csv(filename, columns, data)
        elif output_format == "HTML":
            return self._generate_html(filename, columns, data, scheduled_report)
        else:  # PDF
            return self._generate_pdf(filename, columns, data, scheduled_report)

    def _generate_excel(self, filename, columns, data):
        """Generate Excel file"""
        import io
        from frappe.utils.xlsxutils import make_xlsx

        # Prepare data for xlsx
        xlsx_data = []

        # Header row
        header = [col.get("label", col.get("fieldname", "")) for col in columns]
        xlsx_data.append(header)

        # Data rows
        for row in data:
            if isinstance(row, dict):
                row_data = [row.get(col.get("fieldname", ""), "") for col in columns]
            elif isinstance(row, (list, tuple)):
                row_data = list(row)
            else:
                row_data = [row]
            xlsx_data.append(row_data)

        xlsx_file = make_xlsx(xlsx_data, "Report")

        # Save file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{filename}.xlsx",
            "content": xlsx_file.getvalue(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)

        return file_doc.file_url

    def _generate_csv(self, filename, columns, data):
        """Generate CSV file"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        header = [col.get("label", col.get("fieldname", "")) for col in columns]
        writer.writerow(header)

        # Data rows
        for row in data:
            if isinstance(row, dict):
                row_data = [row.get(col.get("fieldname", ""), "") for col in columns]
            elif isinstance(row, (list, tuple)):
                row_data = list(row)
            else:
                row_data = [row]
            writer.writerow(row_data)

        # Save file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{filename}.csv",
            "content": output.getvalue().encode(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)

        return file_doc.file_url

    def _generate_html(self, filename, columns, data, scheduled_report):
        """Generate HTML file"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{scheduled_report.report_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <h1>{scheduled_report.report_name}</h1>
            <p>Generated on: {now_datetime()}</p>
            <table>
                <thead>
                    <tr>
        """

        # Header
        for col in columns:
            label = col.get("label", col.get("fieldname", ""))
            html_content += f"<th>{label}</th>"
        html_content += "</tr></thead><tbody>"

        # Data
        for row in data:
            html_content += "<tr>"
            for col in columns:
                if isinstance(row, dict):
                    value = row.get(col.get("fieldname", ""), "")
                elif isinstance(row, (list, tuple)):
                    idx = columns.index(col)
                    value = row[idx] if idx < len(row) else ""
                else:
                    value = str(row)
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"

        html_content += """
                </tbody>
            </table>
            <div class="footer">
                <p>This is an automated report generated by University ERP</p>
            </div>
        </body>
        </html>
        """

        # Save file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{filename}.html",
            "content": html_content.encode(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)

        return file_doc.file_url

    def _generate_pdf(self, filename, columns, data, scheduled_report):
        """Generate PDF file"""
        from frappe.utils.pdf import get_pdf

        # Generate HTML first
        html_content = f"""
        <h1>{scheduled_report.report_name}</h1>
        <p>Generated on: {now_datetime()}</p>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #4CAF50; color: white;">
        """

        # Header
        for col in columns:
            label = col.get("label", col.get("fieldname", ""))
            html_content += f'<th style="border: 1px solid #ddd; padding: 8px;">{label}</th>'
        html_content += "</tr></thead><tbody>"

        # Data (limit rows for PDF)
        for row in data[:500]:
            html_content += "<tr>"
            for col in columns:
                if isinstance(row, dict):
                    value = row.get(col.get("fieldname", ""), "")
                elif isinstance(row, (list, tuple)):
                    idx = columns.index(col)
                    value = row[idx] if idx < len(row) else ""
                else:
                    value = str(row)
                html_content += f'<td style="border: 1px solid #ddd; padding: 8px;">{value}</td>'
            html_content += "</tr>"

        html_content += "</tbody></table>"

        # Convert to PDF
        pdf_content = get_pdf(html_content)

        # Save file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{filename}.pdf",
            "content": pdf_content,
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)

        return file_doc.file_url

    def _send_email(self, scheduled_report, file_url):
        """
        Send report via email

        Args:
            scheduled_report: Scheduled Report document
            file_url: URL to report file
        """
        scheduled_report.send_report(file_url)

    def _store_file(self, scheduled_report, file_url):
        """
        Store report in designated folder

        Args:
            scheduled_report: Scheduled Report document
            file_url: URL to report file
        """
        if not scheduled_report.storage_folder:
            return

        # File is already stored via File doctype
        # Just log the storage location
        frappe.log_error(
            f"Report stored: {scheduled_report.report_name} at {file_url}",
            "Report Storage"
        )

    def _calculate_next_run(self, scheduled_report):
        """
        Calculate next run time for scheduled report

        Args:
            scheduled_report: Scheduled Report document
        """
        scheduled_report.calculate_next_run()

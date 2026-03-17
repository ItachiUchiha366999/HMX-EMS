# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
    add_days,
    add_months,
    get_datetime,
    get_first_day,
    now_datetime,
    getdate,
    cint
)


class ScheduledReport(Document):
    def validate(self):
        """Validate scheduled report configuration"""
        self.validate_schedule()
        self.validate_recipients()
        self.validate_filters()

    def validate_schedule(self):
        """Validate schedule configuration"""
        if self.frequency == "Weekly" and not self.day_of_week:
            frappe.throw(_("Day of Week is required for Weekly frequency"))

        if self.frequency in ["Monthly", "Quarterly"] and not self.day_of_month:
            frappe.throw(_("Day of Month is required for {0} frequency").format(self.frequency))

        if self.day_of_month:
            if cint(self.day_of_month) < 1 or cint(self.day_of_month) > 28:
                frappe.throw(_("Day of Month should be between 1 and 28"))

    def validate_recipients(self):
        """Validate recipients are configured for email delivery"""
        if self.delivery_method in ["Email", "Both"]:
            if not self.recipients:
                frappe.throw(_("At least one recipient is required for Email delivery"))

    def validate_filters(self):
        """Validate filters JSON"""
        if self.filters:
            try:
                json.loads(self.filters)
            except json.JSONDecodeError:
                frappe.throw(_("Filters must be valid JSON"))

    def before_save(self):
        """Calculate next run time"""
        if self.is_enabled:
            self.calculate_next_run()

    def execute_report(self):
        """
        Execute the scheduled report

        Returns:
            dict: Result with status, file_url, and any errors
        """
        from university_erp.university_erp.analytics.report_scheduler import ReportScheduler

        scheduler = ReportScheduler()
        return scheduler.execute_report(self.name)

    def calculate_next_run(self):
        """Calculate the next run datetime based on frequency and schedule"""
        from datetime import datetime, timedelta
        import pytz

        tz = pytz.timezone(self.timezone or "Asia/Kolkata")
        now = datetime.now(tz)

        # Parse time of day
        time_parts = str(self.time_of_day).split(":")
        target_hour = int(time_parts[0]) if time_parts else 8
        target_minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        if self.frequency == "Daily":
            next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)

        elif self.frequency == "Weekly":
            days_map = {
                "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                "Friday": 4, "Saturday": 5, "Sunday": 6
            }
            target_day = days_map.get(self.day_of_week, 0)
            days_ahead = target_day - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=7)

        elif self.frequency == "Monthly":
            day = min(cint(self.day_of_month), 28)
            next_run = now.replace(day=day, hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if next_run <= now:
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)

        elif self.frequency == "Quarterly":
            day = min(cint(self.day_of_month), 28)
            # Find next quarter start month (1, 4, 7, 10)
            current_quarter = (now.month - 1) // 3
            next_quarter_month = ((current_quarter + 1) % 4) * 3 + 1
            next_quarter_year = now.year if next_quarter_month > now.month else now.year + 1
            next_run = now.replace(
                year=next_quarter_year,
                month=next_quarter_month,
                day=day,
                hour=target_hour,
                minute=target_minute,
                second=0,
                microsecond=0
            )

        else:
            next_run = now + timedelta(days=1)

        self.next_run = next_run.astimezone(pytz.UTC).replace(tzinfo=None)

    def send_report(self, file_url, report_data=None):
        """
        Send the report to recipients

        Args:
            file_url: URL or path to the generated report file
            report_data: Optional report data for inline HTML
        """
        if not self.recipients:
            return

        to_list = []
        cc_list = []

        for recipient in self.recipients:
            if recipient.cc:
                cc_list.append(recipient.email)
            else:
                to_list.append(recipient.email)

        subject = f"Scheduled Report: {self.report_name}"
        message = f"""
        <p>Dear User,</p>
        <p>Please find attached the scheduled report: <strong>{self.report_name}</strong></p>
        <p>Report: {self.report}</p>
        <p>Generated on: {now_datetime()}</p>
        <p>Best regards,<br>University ERP</p>
        """

        frappe.sendmail(
            recipients=to_list,
            cc=cc_list,
            subject=subject,
            message=message,
            attachments=[{"file_url": file_url}] if file_url else None
        )

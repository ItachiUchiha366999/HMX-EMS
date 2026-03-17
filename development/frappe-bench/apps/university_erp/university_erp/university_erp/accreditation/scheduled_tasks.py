# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Scheduled Tasks for Accreditation Module
"""

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate


def daily_attainment_update():
    """
    Daily task to update CO and PO attainment calculations

    This task:
    1. Gets all active courses with Course Outcomes
    2. Calculates CO attainment for each
    3. Updates PO attainment for programs
    """
    frappe.logger().info("Starting daily attainment update")

    try:
        from university_erp.university_erp.accreditation.attainment_calculator import (
            COPOAttainmentCalculator
        )

        # Get courses with active COs
        courses = frappe.db.sql("""
            SELECT DISTINCT course FROM `tabCourse Outcome`
            WHERE status = 'Active'
        """, as_dict=True)

        for course_row in courses:
            try:
                calculator = COPOAttainmentCalculator(course_row.course)
                calculator.calculate_overall_attainment()
            except Exception as e:
                frappe.log_error(
                    f"Error calculating attainment for course {course_row.course}: {str(e)}",
                    "Attainment Calculation Error"
                )

        # Update PO attainment for all programs
        programs = frappe.get_all("Program", {"is_published": 1}, pluck="name")

        for program in programs:
            try:
                # Get courses for this program
                program_courses = frappe.get_all("Program Course",
                    filters={"parent": program},
                    pluck="course"
                )

                if program_courses:
                    calculator = COPOAttainmentCalculator(program_courses[0])
                    calculator.calculate_po_attainment(program)
            except Exception as e:
                frappe.log_error(
                    f"Error calculating PO attainment for program {program}: {str(e)}",
                    "PO Attainment Calculation Error"
                )

        frappe.db.commit()
        frappe.logger().info("Completed daily attainment update")

    except Exception as e:
        frappe.log_error(str(e), "Daily Attainment Update Error")


def weekly_naac_data_collection():
    """
    Weekly task to collect NAAC metric data

    This task:
    1. Gets active accreditation cycles
    2. Collects auto-calculated metric data
    3. Updates metric values
    """
    frappe.logger().info("Starting weekly NAAC data collection")

    try:
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        # Get active accreditation cycles
        active_cycles = frappe.get_all("Accreditation Cycle",
            filters={"status": ["in", ["Data Collection", "SSR Preparation"]]},
            pluck="name"
        )

        for cycle_name in active_cycles:
            try:
                collector = NAACDataCollector(cycle_name)

                # Get metrics that need auto-calculation
                metrics = frappe.get_all("NAAC Metric",
                    filters={
                        "accreditation_cycle": cycle_name,
                        "data_source": "Auto Calculated",
                        "status": ["in", ["Not Started", "Data Collection", "In Progress"]]
                    },
                    fields=["name", "metric_number"]
                )

                for metric in metrics:
                    try:
                        data = collector.collect_metric_by_number(metric.metric_number)

                        if data and data.get("value"):
                            frappe.db.set_value("NAAC Metric", metric.name, {
                                "calculated_value": data.get("value"),
                                "status": "In Progress"
                            })
                    except Exception as e:
                        frappe.log_error(
                            f"Error collecting metric {metric.metric_number}: {str(e)}",
                            "NAAC Metric Collection Error"
                        )

                frappe.db.commit()

            except Exception as e:
                frappe.log_error(
                    f"Error processing cycle {cycle_name}: {str(e)}",
                    "NAAC Data Collection Error"
                )

        frappe.logger().info("Completed weekly NAAC data collection")

    except Exception as e:
        frappe.log_error(str(e), "Weekly NAAC Data Collection Error")


def monthly_progress_notification():
    """
    Monthly task to send accreditation progress notifications

    This task:
    1. Gets active accreditation cycles
    2. Calculates progress for each
    3. Sends notification to coordinators
    """
    frappe.logger().info("Starting monthly progress notification")

    try:
        # Get active accreditation cycles
        active_cycles = frappe.get_all("Accreditation Cycle",
            filters={"status": ["not in", ["Accredited", "Not Accredited", "Withdrawn"]]},
            fields=["name", "cycle_name", "coordinator", "overall_progress", "ssr_submission_deadline"]
        )

        for cycle in active_cycles:
            try:
                # Get detailed progress
                cycle_doc = frappe.get_doc("Accreditation Cycle", cycle.name)
                summary = cycle_doc.get_criterion_summary()

                # Send notification to coordinator
                if cycle.coordinator:
                    subject = f"Accreditation Progress Update: {cycle.cycle_name}"

                    message = f"""
                    <h3>Monthly Accreditation Progress Report</h3>
                    <p><strong>Cycle:</strong> {cycle.cycle_name}</p>
                    <p><strong>Overall Progress:</strong> {cycle.overall_progress or 0:.1f}%</p>

                    <h4>Criterion Summary:</h4>
                    <ul>
                        <li>Total Criteria: {summary.get('total', 0)}</li>
                        <li>Completed: {summary.get('completed', 0)}</li>
                        <li>In Progress: {summary.get('in_progress', 0)}</li>
                        <li>Not Started: {summary.get('not_started', 0)}</li>
                    </ul>

                    <p><strong>Total Score:</strong> {summary.get('total_score', 0):.2f} / {summary.get('max_score', 0):.2f}</p>
                    """

                    if cycle.ssr_submission_deadline:
                        days_remaining = (getdate(cycle.ssr_submission_deadline) - getdate(today())).days
                        if days_remaining > 0:
                            message += f"<p><strong>SSR Deadline:</strong> {cycle.ssr_submission_deadline} ({days_remaining} days remaining)</p>"
                        else:
                            message += f"<p style='color:red;'><strong>SSR Deadline Passed:</strong> {cycle.ssr_submission_deadline}</p>"

                    frappe.sendmail(
                        recipients=[cycle.coordinator],
                        subject=subject,
                        message=message,
                        now=True
                    )

            except Exception as e:
                frappe.log_error(
                    f"Error sending notification for cycle {cycle.name}: {str(e)}",
                    "Progress Notification Error"
                )

        frappe.logger().info("Completed monthly progress notification")

    except Exception as e:
        frappe.log_error(str(e), "Monthly Progress Notification Error")


def check_deadline_reminders():
    """
    Daily task to check and send deadline reminders

    This task:
    1. Checks upcoming SSR submission deadlines
    2. Checks upcoming peer team visit dates
    3. Sends reminders to coordinators
    """
    frappe.logger().info("Starting deadline reminder check")

    try:
        today_date = getdate(today())
        reminder_days = [30, 14, 7, 3, 1]  # Days before deadline to send reminders

        for days in reminder_days:
            target_date = add_days(today_date, days)

            # Check SSR submission deadlines
            cycles_ssr = frappe.get_all("Accreditation Cycle",
                filters={
                    "ssr_submission_deadline": target_date,
                    "status": ["in", ["Data Collection", "SSR Preparation"]]
                },
                fields=["name", "cycle_name", "coordinator", "ssr_submission_deadline"]
            )

            for cycle in cycles_ssr:
                if cycle.coordinator:
                    frappe.sendmail(
                        recipients=[cycle.coordinator],
                        subject=f"SSR Submission Deadline Reminder - {days} days remaining",
                        message=f"""
                        <p>This is a reminder that the SSR submission deadline for <strong>{cycle.cycle_name}</strong>
                        is on <strong>{cycle.ssr_submission_deadline}</strong> ({days} days from today).</p>

                        <p>Please ensure all metrics are completed and verified before the deadline.</p>
                        """,
                        now=True
                    )

            # Check peer team visit dates
            cycles_visit = frappe.get_all("Accreditation Cycle",
                filters={
                    "peer_team_visit_date": target_date,
                    "status": ["in", ["SSR Submitted", "Peer Team Visit Scheduled"]]
                },
                fields=["name", "cycle_name", "coordinator", "peer_team_visit_date"]
            )

            for cycle in cycles_visit:
                if cycle.coordinator:
                    frappe.sendmail(
                        recipients=[cycle.coordinator],
                        subject=f"Peer Team Visit Reminder - {days} days remaining",
                        message=f"""
                        <p>This is a reminder that the Peer Team Visit for <strong>{cycle.cycle_name}</strong>
                        is scheduled for <strong>{cycle.peer_team_visit_date}</strong> ({days} days from today).</p>

                        <p>Please ensure all preparations are complete.</p>
                        """,
                        now=True
                    )

        frappe.logger().info("Completed deadline reminder check")

    except Exception as e:
        frappe.log_error(str(e), "Deadline Reminder Check Error")

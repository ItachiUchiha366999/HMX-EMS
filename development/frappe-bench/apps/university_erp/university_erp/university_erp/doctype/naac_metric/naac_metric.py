# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class NAACMetric(Document):
    def validate(self):
        self.validate_metric_number()
        self.set_criterion_from_metric()
        self.calculate_value()

    def validate_metric_number(self):
        """Validate metric number format"""
        if self.metric_number:
            parts = self.metric_number.split(".")
            if len(parts) < 2:
                frappe.throw(_("Metric number should be in format X.X.X (e.g., 1.1.1)"))

    def set_criterion_from_metric(self):
        """Auto-set criterion based on metric number"""
        if self.metric_number and not self.criterion:
            criterion_num = self.metric_number.split(".")[0]
            criterion_map = {
                "1": "1. Curricular Aspects",
                "2": "2. Teaching-Learning and Evaluation",
                "3": "3. Research, Innovations and Extension",
                "4": "4. Infrastructure and Learning Resources",
                "5": "5. Student Support and Progression",
                "6": "6. Governance, Leadership and Management",
                "7": "7. Institutional Values and Best Practices"
            }
            self.criterion = criterion_map.get(criterion_num, "")

    def calculate_value(self):
        """Calculate the metric value from year-wise data"""
        if not self.year_wise_data:
            return

        if self.data_source == "Manual Entry":
            # For manual entry, take the average or latest value
            values = [flt(row.value) for row in self.year_wise_data if row.value]
            if values:
                self.calculated_value = sum(values) / len(values)
        elif self.data_source == "Auto Calculated":
            # Calculate using numerator/denominator if available
            total_numerator = sum([flt(row.numerator) for row in self.year_wise_data if row.numerator])
            total_denominator = sum([flt(row.denominator) for row in self.year_wise_data if row.denominator])
            if total_denominator > 0:
                self.calculated_value = (total_numerator / total_denominator) * 100

    def update_status(self, new_status):
        """Update metric status"""
        valid_transitions = {
            "Not Started": ["Data Collection", "In Progress"],
            "Data Collection": ["In Progress", "Not Started"],
            "In Progress": ["Completed", "Data Collection"],
            "Completed": ["Verified", "In Progress"],
            "Verified": ["Submitted", "Completed"],
            "Submitted": ["Verified"]
        }

        if new_status not in valid_transitions.get(self.status, []):
            frappe.throw(_(f"Cannot change status from {self.status} to {new_status}"))

        self.status = new_status
        if new_status == "Verified":
            self.verified_by = frappe.session.user
            self.verification_date = today()

        self.save()


@frappe.whitelist()
def collect_metric_data(metric_name):
    """Collect data for a specific NAAC metric"""
    metric = frappe.get_doc("NAAC Metric", metric_name)

    if metric.data_source != "Auto Calculated":
        frappe.throw(_("Only Auto Calculated metrics can be collected automatically"))

    # Get the accreditation cycle period
    cycle = frappe.get_doc("Accreditation Cycle", metric.accreditation_cycle)

    # Import and use the data collector
    from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector
    collector = NAACDataCollector(cycle.name)

    # Collect data based on metric number
    data = collector.collect_metric_by_number(metric.metric_number)

    if data:
        metric.calculated_value = data.get("value", 0)
        metric.save()

    return data

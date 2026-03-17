# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
SSR (Self Study Report) Generator for NAAC Accreditation

Generates comprehensive SSR documents for NAAC accreditation submission.
"""

import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
from frappe.utils import today, getdate
from typing import Dict, List
import json


class SSRGenerator:
    """
    Self Study Report (SSR) Generator for NAAC
    """

    def __init__(self, accreditation_cycle: str):
        self.cycle = frappe.get_doc("Accreditation Cycle", accreditation_cycle)
        self.metrics = self._load_all_metrics()

    def _load_all_metrics(self) -> Dict:
        """Load all metrics for the cycle"""
        metrics = {}
        all_metrics = frappe.get_all("NAAC Metric",
            filters={"accreditation_cycle": self.cycle.name},
            fields=["*"]
        )

        for m in all_metrics:
            metrics[m.metric_number] = m

        return metrics

    def generate_ssr(self, output_format: str = "html") -> str:
        """
        Generate complete SSR document

        Args:
            output_format: 'html' or 'pdf'

        Returns:
            Generated document path
        """
        # Generate each section
        sections = {
            "executive_summary": self._generate_executive_summary(),
            "profile": self._generate_institutional_profile(),
            "criteria": self._generate_all_criteria(),
            "evaluative_report": self._generate_evaluative_report(),
            "declaration": self._generate_declaration(),
            "annexures": self._generate_annexures()
        }

        # Render template
        html = self._render_ssr_html(sections)

        if output_format == "pdf":
            return self._generate_pdf(html)
        else:
            return self._save_html(html)

    def _render_ssr_html(self, sections: Dict) -> str:
        """Render SSR HTML from sections"""
        institution = self._get_institution_details()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Self Study Report - {institution.get('name', 'Institution')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 10px; }}
                h2 {{ color: #2c5282; margin-top: 30px; }}
                h3 {{ color: #4a5568; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4a5568; color: white; }}
                .metric {{ background-color: #f7fafc; padding: 15px; margin: 10px 0; border-left: 4px solid #4299e1; }}
                .score {{ font-size: 1.2em; font-weight: bold; color: #2b6cb0; }}
                .criterion {{ page-break-before: always; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #718096; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SELF STUDY REPORT</h1>
                <h2>{institution.get('name', 'Institution Name')}</h2>
                <p>{institution.get('address', '')}</p>
                <p>Submitted to: National Assessment and Accreditation Council (NAAC)</p>
                <p>Cycle: {self.cycle.cycle_number or ''} | Year: {self.cycle.assessment_year}</p>
            </div>

            <h2>Executive Summary</h2>
            <div>{self._format_executive_summary(sections['executive_summary'])}</div>

            <h2>Institutional Profile</h2>
            <div>{self._format_institutional_profile(sections['profile'])}</div>

            {self._format_all_criteria(sections['criteria'])}

            <h2>Evaluative Report</h2>
            <div>{self._format_evaluative_report(sections['evaluative_report'])}</div>

            <h2>Declaration</h2>
            <div>{self._format_declaration(sections['declaration'])}</div>

            <h2>Annexures</h2>
            <div>{self._format_annexures(sections['annexures'])}</div>

            <div class="footer">
                <p>Generated on: {today()}</p>
                <p>University ERP - Accreditation Module</p>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_executive_summary(self) -> Dict:
        """Generate Executive Summary section"""
        return {
            "introduction": self._get_introduction(),
            "vision_mission": self._get_vision_mission(),
            "highlights": self._get_highlights(),
            "swoc": self._get_swoc_analysis()
        }

    def _format_executive_summary(self, summary: Dict) -> str:
        """Format executive summary as HTML"""
        html = f"""
        <h3>Introduction</h3>
        <p>{summary.get('introduction', 'Institution introduction text.')}</p>

        <h3>Vision & Mission</h3>
        <p><strong>Vision:</strong> {summary.get('vision_mission', {}).get('vision', '')}</p>
        <p><strong>Mission:</strong> {summary.get('vision_mission', {}).get('mission', '')}</p>

        <h3>Key Highlights</h3>
        <ul>
        """
        for highlight in summary.get('highlights', []):
            html += f"<li>{highlight}</li>"
        html += "</ul>"

        html += """
        <h3>SWOC Analysis</h3>
        <table>
            <tr><th>Strengths</th><th>Weaknesses</th></tr>
            <tr>
                <td>{}</td>
                <td>{}</td>
            </tr>
            <tr><th>Opportunities</th><th>Challenges</th></tr>
            <tr>
                <td>{}</td>
                <td>{}</td>
            </tr>
        </table>
        """.format(
            "<br>".join(summary.get('swoc', {}).get('strengths', [])),
            "<br>".join(summary.get('swoc', {}).get('weaknesses', [])),
            "<br>".join(summary.get('swoc', {}).get('opportunities', [])),
            "<br>".join(summary.get('swoc', {}).get('challenges', []))
        )

        return html

    def _generate_institutional_profile(self) -> Dict:
        """Generate institutional profile"""
        return {
            "basic_info": self._get_basic_info(),
            "academic_info": self._get_academic_info(),
            "faculty_info": self._get_faculty_info(),
            "student_info": self._get_student_info(),
            "infrastructure_info": self._get_infrastructure_info()
        }

    def _format_institutional_profile(self, profile: Dict) -> str:
        """Format institutional profile as HTML"""
        basic = profile.get('basic_info', {})
        academic = profile.get('academic_info', {})
        faculty = profile.get('faculty_info', {})
        student = profile.get('student_info', {})

        html = f"""
        <h3>Basic Information</h3>
        <table>
            <tr><td><strong>Type of Institution</strong></td><td>{basic.get('type', '')}</td></tr>
            <tr><td><strong>Established</strong></td><td>{basic.get('established', '')}</td></tr>
            <tr><td><strong>Affiliating University</strong></td><td>{basic.get('affiliated_to', '')}</td></tr>
        </table>

        <h3>Academic Information</h3>
        <table>
            <tr><td><strong>Programs Offered</strong></td><td>{academic.get('total_programs', 0)}</td></tr>
            <tr><td><strong>Departments</strong></td><td>{academic.get('total_departments', 0)}</td></tr>
        </table>

        <h3>Faculty Information</h3>
        <table>
            <tr><td><strong>Total Faculty</strong></td><td>{faculty.get('total', 0)}</td></tr>
            <tr><td><strong>With PhD</strong></td><td>{faculty.get('with_phd', 0)}</td></tr>
        </table>

        <h3>Student Information</h3>
        <table>
            <tr><td><strong>Total Students</strong></td><td>{student.get('total', 0)}</td></tr>
            <tr><td><strong>Female Students</strong></td><td>{student.get('female', 0)}</td></tr>
        </table>
        """

        return html

    def _generate_all_criteria(self) -> Dict:
        """Generate all 7 criteria sections"""
        criteria = {}

        for i in range(1, 8):
            criteria[f"criterion_{i}"] = self._generate_criterion(i)

        return criteria

    def _generate_criterion(self, criterion_number: int) -> Dict:
        """Generate a single criterion section"""
        criterion_metrics = {k: v for k, v in self.metrics.items()
                           if k.startswith(str(criterion_number))}

        return {
            "number": criterion_number,
            "name": self._get_criterion_name(criterion_number),
            "metrics": criterion_metrics,
            "key_indicators": self._get_key_indicators(criterion_number),
            "qualitative_response": self._get_qualitative_response(criterion_number)
        }

    def _format_all_criteria(self, criteria: Dict) -> str:
        """Format all criteria as HTML"""
        html = ""

        for i in range(1, 8):
            criterion = criteria.get(f"criterion_{i}", {})
            html += f"""
            <div class="criterion">
                <h2>Criterion {criterion.get('number', i)}: {criterion.get('name', '')}</h2>

                <h3>Key Indicators</h3>
            """

            for key, metric in criterion.get('metrics', {}).items():
                html += f"""
                <div class="metric">
                    <h4>{key}: {metric.get('metric_description', '')[:100] if metric.get('metric_description') else ''}</h4>
                    <p class="score">Value: {metric.get('calculated_value', metric.get('score', 0))}</p>
                    <p>Status: {metric.get('status', 'Not Started')}</p>
                </div>
                """

            html += f"""
                <h3>Narrative</h3>
                <p>{criterion.get('qualitative_response', '')}</p>
            </div>
            """

        return html

    def _get_criterion_name(self, number: int) -> str:
        """Get criterion name"""
        names = {
            1: "Curricular Aspects",
            2: "Teaching-Learning and Evaluation",
            3: "Research, Innovations and Extension",
            4: "Infrastructure and Learning Resources",
            5: "Student Support and Progression",
            6: "Governance, Leadership and Management",
            7: "Institutional Values and Best Practices"
        }
        return names.get(number, "")

    def _generate_evaluative_report(self) -> Dict:
        """Generate evaluative report for departments"""
        departments = frappe.get_all("Department",
            filters={"is_academic": 1} if frappe.db.has_column("Department", "is_academic") else {},
            fields=["name", "department_name"],
            limit=20
        )

        reports = []
        for dept in departments:
            reports.append({
                "department": dept.department_name or dept.name,
                "programs": self._get_department_programs(dept.name),
                "faculty": self._get_department_faculty(dept.name)
            })

        return {"departments": reports}

    def _format_evaluative_report(self, report: Dict) -> str:
        """Format evaluative report as HTML"""
        html = "<h3>Department-wise Report</h3>"

        for dept in report.get('departments', []):
            html += f"""
            <h4>{dept.get('department', '')}</h4>
            <p>Programs: {len(dept.get('programs', []))}</p>
            <p>Faculty: {len(dept.get('faculty', []))}</p>
            """

        return html

    def _generate_declaration(self) -> Dict:
        """Generate declaration section"""
        return {
            "head_of_institution": self._get_head_details(),
            "iqac_coordinator": self._get_iqac_coordinator_details(),
            "declaration_date": today()
        }

    def _format_declaration(self, declaration: Dict) -> str:
        """Format declaration as HTML"""
        return f"""
        <p>I certify that the data included in this Self Study Report (SSR) are true to the best of my knowledge.</p>

        <table>
            <tr>
                <td><strong>Head of Institution</strong></td>
                <td>{declaration.get('head_of_institution', {}).get('name', '')}</td>
            </tr>
            <tr>
                <td><strong>IQAC Coordinator</strong></td>
                <td>{declaration.get('iqac_coordinator', {}).get('name', '')}</td>
            </tr>
            <tr>
                <td><strong>Date</strong></td>
                <td>{declaration.get('declaration_date', today())}</td>
            </tr>
        </table>
        """

    def _generate_annexures(self) -> List:
        """Generate annexures list"""
        annexures = []

        # Collect all documents from metrics
        for metric_num, metric in self.metrics.items():
            if metric.get("name"):
                docs = frappe.get_all("NAAC Metric Document",
                    filters={"parent": metric.name},
                    fields=["document_name", "file_url"]
                )
                for doc in docs:
                    annexures.append({
                        "metric": metric_num,
                        "name": doc.document_name,
                        "url": doc.file_url
                    })

        return annexures

    def _format_annexures(self, annexures: List) -> str:
        """Format annexures as HTML"""
        if not annexures:
            return "<p>No annexures attached.</p>"

        html = "<table><tr><th>Metric</th><th>Document</th><th>Link</th></tr>"
        for ann in annexures:
            html += f"""
            <tr>
                <td>{ann.get('metric', '')}</td>
                <td>{ann.get('name', '')}</td>
                <td><a href='{ann.get('url', '#')}'>View</a></td>
            </tr>
            """
        html += "</table>"
        return html

    def _get_institution_details(self) -> Dict:
        """Get institution details"""
        # Try to get from University Settings or Company
        name = frappe.db.get_single_value("Education Settings", "institution_name") if \
            frappe.db.exists("DocType", "Education Settings") else ""

        if not name:
            name = frappe.db.get_single_value("System Settings", "site_name") or "University"

        return {
            "name": name,
            "address": "",
            "website": frappe.utils.get_url(),
            "established": "",
            "type": "University"
        }

    def _generate_pdf(self, html: str) -> str:
        """Generate PDF from HTML"""
        pdf = get_pdf(html, {
            "page-size": "A4",
            "margin-top": "15mm",
            "margin-bottom": "15mm",
            "margin-left": "10mm",
            "margin-right": "10mm"
        })

        filename = f"SSR_{self.cycle.name}_{today()}.pdf"
        file_path = f"/files/{filename}"

        # Save file
        site_path = frappe.get_site_path("public", "files", filename)
        with open(site_path, "wb") as f:
            f.write(pdf)

        return file_path

    def _save_html(self, html: str) -> str:
        """Save HTML document"""
        filename = f"SSR_{self.cycle.name}_{today()}.html"
        file_path = frappe.get_site_path("public", "files", filename)

        with open(file_path, "w") as f:
            f.write(html)

        return f"/files/{filename}"

    # Helper methods with default implementations
    def _get_introduction(self) -> str:
        return "The institution is committed to providing quality education..."

    def _get_vision_mission(self) -> Dict:
        return {"vision": "To be a center of excellence...", "mission": "To provide quality education..."}

    def _get_highlights(self) -> List:
        return ["Established academic programs", "Qualified faculty", "Modern infrastructure"]

    def _get_swoc_analysis(self) -> Dict:
        return {
            "strengths": ["Strong academics", "Experienced faculty"],
            "weaknesses": ["Limited research output"],
            "opportunities": ["Industry partnerships", "New programs"],
            "challenges": ["Competition", "Funding constraints"]
        }

    def _get_basic_info(self) -> Dict:
        return {"type": "University", "established": "", "affiliated_to": ""}

    def _get_academic_info(self) -> Dict:
        total_programs = frappe.db.count("Program", {"is_published": 1})
        total_departments = frappe.db.count("Department")
        return {"total_programs": total_programs, "total_departments": total_departments}

    def _get_faculty_info(self) -> Dict:
        total = frappe.db.count("Instructor", {"status": "Active"})
        with_phd = frappe.db.count("Instructor", {
            "status": "Active",
            "highest_qualification": ["in", ["Ph.D.", "PhD"]]
        })
        return {"total": total, "with_phd": with_phd}

    def _get_student_info(self) -> Dict:
        total = frappe.db.count("Student", {"enabled": 1})
        female = frappe.db.count("Student", {"enabled": 1, "gender": "Female"})
        return {"total": total, "female": female}

    def _get_infrastructure_info(self) -> Dict:
        return {}

    def _get_key_indicators(self, criterion: int) -> List:
        return []

    def _get_qualitative_response(self, criterion: int) -> str:
        return ""

    def _get_department_programs(self, dept: str) -> List:
        return frappe.get_all("Program", filters={"department": dept}, pluck="name")

    def _get_department_faculty(self, dept: str) -> List:
        return frappe.get_all("Instructor", filters={"department": dept}, pluck="name")

    def _get_head_details(self) -> Dict:
        return {"name": "Head of Institution"}

    def _get_iqac_coordinator_details(self) -> Dict:
        if self.cycle.coordinator:
            user = frappe.get_doc("User", self.cycle.coordinator)
            return {"name": user.full_name}
        return {"name": "IQAC Coordinator"}


@frappe.whitelist()
def generate_ssr(accreditation_cycle: str, output_format: str = "html") -> str:
    """
    API to generate SSR document

    Args:
        accreditation_cycle: Accreditation Cycle name
        output_format: 'html' or 'pdf'

    Returns:
        Path to generated document
    """
    generator = SSRGenerator(accreditation_cycle)
    return generator.generate_ssr(output_format)

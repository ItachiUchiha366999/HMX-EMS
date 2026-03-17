# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class NIRFData(Document):
    def validate(self):
        self.calculate_scores()

    def calculate_scores(self):
        """Calculate NIRF scores for each parameter"""
        # TLR Score (30% weightage)
        self.tlr_score = self._calculate_tlr_score()

        # RP Score (30% weightage)
        self.rp_score = self._calculate_rp_score()

        # GO Score (20% weightage)
        self.go_score = self._calculate_go_score()

        # OI Score (10% weightage)
        self.oi_score = self._calculate_oi_score()

        # PR Score (10% weightage)
        self.pr_score = flt(self.pr_peer_perception)

        # Total Score
        self.total_score = (
            flt(self.tlr_score) +
            flt(self.rp_score) +
            flt(self.go_score) +
            flt(self.oi_score) +
            flt(self.pr_score)
        )

    def _calculate_tlr_score(self):
        """Calculate Teaching Learning Resources score"""
        score = 0

        # Student Strength contribution
        if self.ss_student_strength:
            ss_score = min(flt(self.ss_student_strength) / 5000 * 5, 5)
            score += ss_score

        # Faculty Student Ratio contribution
        if self.fsr_faculty_ratio:
            fsr_score = min(20 / flt(self.fsr_faculty_ratio) * 10, 10) if flt(self.fsr_faculty_ratio) > 0 else 0
            score += fsr_score

        # Faculty with PhD contribution
        if self.fqe_faculty_qualification:
            fqe_score = min(flt(self.fqe_faculty_qualification) / 100 * 10, 10)
            score += fqe_score

        # Financial Resources contribution
        if self.fru_financial_resources:
            fru_score = min(flt(self.fru_financial_resources) / 1000 * 5, 5)
            score += fru_score

        return round(score, 2)

    def _calculate_rp_score(self):
        """Calculate Research and Professional Practice score"""
        score = 0

        # Publications contribution
        if self.pu_publications:
            pu_score = min(flt(self.pu_publications) / 500 * 10, 10)
            score += pu_score

        # Quality Publications contribution
        if self.qp_quality_publications:
            qp_score = min(flt(self.qp_quality_publications) / 200 * 10, 10)
            score += qp_score

        # Patents contribution
        if self.ipr_patents:
            ipr_score = min(flt(self.ipr_patents) / 50 * 5, 5)
            score += ipr_score

        # Funded Projects contribution
        if self.fppp_projects:
            fppp_score = min(flt(self.fppp_projects) / 500 * 5, 5)
            score += fppp_score

        return round(score, 2)

    def _calculate_go_score(self):
        """Calculate Graduation Outcomes score"""
        score = 0

        # University Exam Results contribution
        if self.gue_university_exams:
            gue_score = min(flt(self.gue_university_exams) / 100 * 10, 10)
            score += gue_score

        # PhD Students contribution
        if self.gphd_phd_students:
            gphd_score = min(flt(self.gphd_phd_students) / 100 * 5, 5)
            score += gphd_score

        # Median Salary contribution
        if self.gms_median_salary:
            gms_score = min(flt(self.gms_median_salary) / 10 * 5, 5)
            score += gms_score

        return round(score, 2)

    def _calculate_oi_score(self):
        """Calculate Outreach and Inclusivity score"""
        score = 0

        # Region Diversity contribution
        if self.rd_region_diversity:
            rd_score = min(flt(self.rd_region_diversity) / 100 * 2.5, 2.5)
            score += rd_score

        # Women Diversity contribution
        if self.wd_women_diversity:
            wd_score = min(flt(self.wd_women_diversity) / 50 * 2.5, 2.5)
            score += wd_score

        # Economically Backward contribution
        if self.escs_economically_backward:
            escs_score = min(flt(self.escs_economically_backward) / 50 * 2.5, 2.5)
            score += escs_score

        # Disabled Facilities contribution
        if self.pcs_facilities_disabled:
            pcs_score = min(flt(self.pcs_facilities_disabled) / 100 * 2.5, 2.5)
            score += pcs_score

        return round(score, 2)

    def collect_data(self):
        """Collect NIRF data from various sources"""
        # Student Strength
        self.ss_student_strength = frappe.db.count("Student", {"enabled": 1})

        # Faculty data
        faculty_count = frappe.db.count("Instructor", {"status": "Active"})
        if faculty_count > 0:
            self.fsr_faculty_ratio = round(self.ss_student_strength / faculty_count, 2)

            # PhD faculty
            phd_faculty = frappe.db.count("Instructor", {
                "status": "Active",
                "highest_qualification": ["in", ["Ph.D.", "PhD"]]
            })
            self.fqe_faculty_qualification = round((phd_faculty / faculty_count) * 100, 2)

        # Women Diversity
        female_students = frappe.db.count("Student", {"enabled": 1, "gender": "Female"})
        if self.ss_student_strength > 0:
            self.wd_women_diversity = round((female_students / self.ss_student_strength) * 100, 2)

        self.save()


@frappe.whitelist()
def collect_nirf_data(nirf_data_name):
    """API to collect NIRF data"""
    nirf = frappe.get_doc("NIRF Data", nirf_data_name)
    nirf.collect_data()
    return {"status": "success", "total_score": nirf.total_score}

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
API Endpoints for Accreditation Module
"""

import frappe
from frappe import _


@frappe.whitelist()
def calculate_co_attainment(course, academic_year=None):
    """
    Calculate Course Outcome attainment for a course

    Args:
        course: Course name/ID
        academic_year: Optional academic year

    Returns:
        Dict with CO-wise attainment data
    """
    from university_erp.university_erp.accreditation.attainment_calculator import (
        COPOAttainmentCalculator
    )

    calculator = COPOAttainmentCalculator(course, academic_year)
    return calculator.calculate_overall_attainment()


@frappe.whitelist()
def calculate_po_attainment(program, academic_year=None):
    """
    Calculate Program Outcome attainment for a program

    Args:
        program: Program name/ID
        academic_year: Optional academic year

    Returns:
        Dict with PO-wise attainment data
    """
    from university_erp.university_erp.accreditation.attainment_calculator import (
        calculate_program_attainment
    )

    return calculate_program_attainment(program, academic_year)


@frappe.whitelist()
def get_copo_matrix(course, program, academic_term=None):
    """
    Get CO-PO mapping matrix with attainment values

    Args:
        course: Course name/ID
        program: Program name/ID
        academic_term: Optional academic term

    Returns:
        Dict with matrix data for display
    """
    from university_erp.university_erp.accreditation.attainment_calculator import (
        get_copo_matrix as _get_copo_matrix
    )

    return _get_copo_matrix(course, program, academic_term)


@frappe.whitelist()
def collect_naac_data(accreditation_cycle):
    """
    Collect NAAC data for all metrics in an accreditation cycle

    Args:
        accreditation_cycle: Accreditation Cycle name

    Returns:
        Dict with collected data for all criteria
    """
    from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

    collector = NAACDataCollector(accreditation_cycle)
    return collector.collect_all_metrics()


@frappe.whitelist()
def collect_naac_metric(accreditation_cycle, metric_number):
    """
    Collect data for a specific NAAC metric

    Args:
        accreditation_cycle: Accreditation Cycle name
        metric_number: Metric number like "1.1.1"

    Returns:
        Dict with metric data
    """
    from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

    collector = NAACDataCollector(accreditation_cycle)
    return collector.collect_metric_by_number(metric_number)


@frappe.whitelist()
def generate_ssr(accreditation_cycle, output_format="html"):
    """
    Generate SSR document for NAAC accreditation

    Args:
        accreditation_cycle: Accreditation Cycle name
        output_format: 'html' or 'pdf'

    Returns:
        Path to generated document
    """
    from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

    generator = SSRGenerator(accreditation_cycle)
    return generator.generate_ssr(output_format)


@frappe.whitelist()
def get_accreditation_progress(accreditation_cycle):
    """
    Get overall progress for an accreditation cycle

    Args:
        accreditation_cycle: Accreditation Cycle name

    Returns:
        Dict with progress summary
    """
    cycle = frappe.get_doc("Accreditation Cycle", accreditation_cycle)
    return cycle.get_criterion_summary()


@frappe.whitelist()
def get_nirf_summary(ranking_year=None, category=None):
    """
    Get NIRF data summary

    Args:
        ranking_year: Optional ranking year
        category: Optional category (Overall, Engineering, etc.)

    Returns:
        Dict with NIRF summary
    """
    filters = {}
    if ranking_year:
        filters["ranking_year"] = ranking_year
    if category:
        filters["category"] = category

    nirf_data = frappe.get_all("NIRF Data",
        filters=filters,
        fields=["name", "ranking_year", "category", "total_score",
                "rank_obtained", "band", "status"],
        order_by="ranking_year desc",
        limit=10
    )

    return nirf_data


@frappe.whitelist()
def collect_nirf_data(nirf_data_name):
    """
    Collect and calculate NIRF data

    Args:
        nirf_data_name: NIRF Data document name

    Returns:
        Dict with status and score
    """
    nirf = frappe.get_doc("NIRF Data", nirf_data_name)
    nirf.collect_data()
    return {"status": "success", "total_score": nirf.total_score}


@frappe.whitelist()
def get_accreditation_dashboard_data():
    """
    Get data for accreditation dashboard

    Returns:
        Dict with dashboard data
    """
    # Active accreditation cycles
    active_cycles = frappe.get_all("Accreditation Cycle",
        filters={"status": ["not in", ["Accredited", "Not Accredited", "Withdrawn"]]},
        fields=["name", "accreditation_body", "cycle_name", "status", "overall_progress"],
        order_by="modified desc",
        limit=5
    )

    # NAAC metrics summary
    total_metrics = frappe.db.count("NAAC Metric")
    completed_metrics = frappe.db.count("NAAC Metric", {"status": ["in", ["Completed", "Verified", "Submitted"]]})

    # PO attainment summary
    pos = frappe.get_all("Program Outcome",
        filters={"status": "Active"},
        fields=["current_attainment", "target_attainment"]
    )
    total_pos = len(pos)
    attained_pos = sum(1 for po in pos if (po.current_attainment or 0) >= (po.target_attainment or 60))

    # Recent NIRF submissions
    recent_nirf = frappe.get_all("NIRF Data",
        fields=["name", "ranking_year", "category", "total_score", "rank_obtained"],
        order_by="ranking_year desc",
        limit=3
    )

    return {
        "active_cycles": active_cycles,
        "naac_metrics": {
            "total": total_metrics,
            "completed": completed_metrics,
            "progress": round((completed_metrics / total_metrics * 100) if total_metrics > 0 else 0, 1)
        },
        "po_attainment": {
            "total": total_pos,
            "attained": attained_pos,
            "percentage": round((attained_pos / total_pos * 100) if total_pos > 0 else 0, 1)
        },
        "recent_nirf": recent_nirf
    }

# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

from university_erp.university_erp.analytics.kpis.academic_kpis import (
    student_pass_percentage,
    average_cgpa,
    student_attendance_rate,
    faculty_student_ratio,
    course_completion_rate
)

from university_erp.university_erp.analytics.kpis.financial_kpis import (
    fee_collection_rate,
    revenue_per_student,
    outstanding_fees_percentage,
    scholarship_utilization
)

from university_erp.university_erp.analytics.kpis.admission_kpis import (
    admission_conversion_rate,
    seat_fill_rate,
    average_application_processing_time,
    application_rejection_rate
)

__all__ = [
    # Academic KPIs
    "student_pass_percentage",
    "average_cgpa",
    "student_attendance_rate",
    "faculty_student_ratio",
    "course_completion_rate",
    # Financial KPIs
    "fee_collection_rate",
    "revenue_per_student",
    "outstanding_fees_percentage",
    "scholarship_utilization",
    # Admission KPIs
    "admission_conversion_rate",
    "seat_fill_rate",
    "average_application_processing_time",
    "application_rejection_rate"
]

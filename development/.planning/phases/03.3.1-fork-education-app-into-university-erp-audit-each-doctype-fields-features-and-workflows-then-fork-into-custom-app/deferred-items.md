## [03.3.1-06] Pre-existing missing module: communication_analytics report

`bench migrate` reports:
- university_erp.university_erp.report.communication_analytics.communication_analytics.generate_weekly_communication_report is not a valid method: No module named 'university_erp.university_erp.report.communication_analytics'
- ...generate_monthly_communication_report (same)

Out of scope for the Education fork — this is a scheduled task in university_erp hooks pointing to a never-created report. Defer to a follow-up cleanup plan.

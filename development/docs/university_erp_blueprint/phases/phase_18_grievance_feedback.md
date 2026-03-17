# Phase 18: Grievance & Feedback Management System

## Overview

This phase implements a comprehensive grievance redressal and feedback management system including student grievances, faculty complaints, parent concerns, suggestion boxes, satisfaction surveys, and complaint escalation workflows.

**Duration:** 4 Weeks
**Priority:** Medium-High
**Dependencies:** Phase 1 (Foundation), Phase 13 (Portals)

## Gap Analysis Reference

From IMPLEMENTATION_GAP_ANALYSIS.md:
- Grievance Management: 15% complete (Basic DocType only)
- Feedback Collection: 0% (Missing)
- Complaint Escalation Workflow: 0% (Missing)
- Satisfaction Surveys: 0% (Missing)
- Anonymous Feedback: 0% (Missing)
- Response Tracking: 0% (Missing)

---

## 1. Core DocTypes

### 1.1 Grievance

```json
{
  "doctype": "DocType",
  "name": "Grievance",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "GRV-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "subject",
      "fieldtype": "Data",
      "label": "Subject",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "grievance_type",
      "fieldtype": "Link",
      "label": "Grievance Type",
      "options": "Grievance Type",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "category",
      "fieldtype": "Select",
      "label": "Category",
      "options": "\nAcademic\nAdministrative\nFinancial\nInfrastructure\nHostel\nTransport\nLibrary\nExamination\nFaculty Related\nRagging\nHarassment\nDiscrimination\nOther",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "priority",
      "fieldtype": "Select",
      "label": "Priority",
      "options": "\nLow\nMedium\nHigh\nUrgent",
      "default": "Medium",
      "reqd": 1
    },
    {
      "fieldname": "submitted_by_type",
      "fieldtype": "Select",
      "label": "Submitted By Type",
      "options": "\nStudent\nFaculty\nParent\nStaff\nAlumni\nOther",
      "reqd": 1
    },
    {
      "fieldname": "is_anonymous",
      "fieldtype": "Check",
      "label": "Anonymous Submission"
    },
    {
      "fieldname": "section_break_submitter",
      "fieldtype": "Section Break",
      "label": "Submitter Details",
      "depends_on": "eval:!doc.is_anonymous"
    },
    {
      "fieldname": "student",
      "fieldtype": "Link",
      "label": "Student",
      "options": "Student",
      "depends_on": "eval:doc.submitted_by_type == 'Student'"
    },
    {
      "fieldname": "faculty",
      "fieldtype": "Link",
      "label": "Faculty Member",
      "options": "Faculty Member",
      "depends_on": "eval:doc.submitted_by_type == 'Faculty'"
    },
    {
      "fieldname": "parent",
      "fieldtype": "Link",
      "label": "Parent/Guardian",
      "options": "Guardian",
      "depends_on": "eval:doc.submitted_by_type == 'Parent'"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "contact_email",
      "fieldtype": "Data",
      "label": "Contact Email",
      "options": "Email"
    },
    {
      "fieldname": "contact_phone",
      "fieldtype": "Data",
      "label": "Contact Phone"
    },
    {
      "fieldname": "department",
      "fieldtype": "Link",
      "label": "Department",
      "options": "Department"
    },
    {
      "fieldname": "section_break_details",
      "fieldtype": "Section Break",
      "label": "Grievance Details"
    },
    {
      "fieldname": "description",
      "fieldtype": "Text Editor",
      "label": "Description",
      "reqd": 1
    },
    {
      "fieldname": "against_person",
      "fieldtype": "Data",
      "label": "Against (if applicable)",
      "description": "Name of person/department the grievance is against"
    },
    {
      "fieldname": "incident_date",
      "fieldtype": "Date",
      "label": "Date of Incident"
    },
    {
      "fieldname": "incident_location",
      "fieldtype": "Data",
      "label": "Location of Incident"
    },
    {
      "fieldname": "witnesses",
      "fieldtype": "Small Text",
      "label": "Witnesses (if any)"
    },
    {
      "fieldname": "section_break_evidence",
      "fieldtype": "Section Break",
      "label": "Supporting Documents"
    },
    {
      "fieldname": "attachments",
      "fieldtype": "Table",
      "label": "Attachments",
      "options": "Grievance Attachment"
    },
    {
      "fieldname": "section_break_assignment",
      "fieldtype": "Section Break",
      "label": "Assignment & Handling"
    },
    {
      "fieldname": "assigned_to",
      "fieldtype": "Link",
      "label": "Assigned To",
      "options": "User"
    },
    {
      "fieldname": "assigned_committee",
      "fieldtype": "Link",
      "label": "Assigned Committee",
      "options": "Grievance Committee"
    },
    {
      "fieldname": "assignment_date",
      "fieldtype": "Datetime",
      "label": "Assignment Date",
      "read_only": 1
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "expected_resolution_date",
      "fieldtype": "Date",
      "label": "Expected Resolution Date"
    },
    {
      "fieldname": "current_escalation_level",
      "fieldtype": "Int",
      "label": "Current Escalation Level",
      "default": 1,
      "read_only": 1
    },
    {
      "fieldname": "escalation_history",
      "fieldtype": "Table",
      "label": "Escalation History",
      "options": "Grievance Escalation Log"
    },
    {
      "fieldname": "section_break_resolution",
      "fieldtype": "Section Break",
      "label": "Resolution"
    },
    {
      "fieldname": "resolution_notes",
      "fieldtype": "Text Editor",
      "label": "Resolution Notes"
    },
    {
      "fieldname": "action_taken",
      "fieldtype": "Table",
      "label": "Actions Taken",
      "options": "Grievance Action"
    },
    {
      "fieldname": "resolved_by",
      "fieldtype": "Link",
      "label": "Resolved By",
      "options": "User"
    },
    {
      "fieldname": "resolution_date",
      "fieldtype": "Datetime",
      "label": "Resolution Date"
    },
    {
      "fieldname": "column_break_4",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "resolution_type",
      "fieldtype": "Select",
      "label": "Resolution Type",
      "options": "\nResolved\nPartially Resolved\nNo Action Required\nWithdrawn\nReferred to External Authority\nDismissed"
    },
    {
      "fieldname": "satisfaction_rating",
      "fieldtype": "Rating",
      "label": "Complainant Satisfaction Rating"
    },
    {
      "fieldname": "satisfaction_feedback",
      "fieldtype": "Small Text",
      "label": "Satisfaction Feedback"
    },
    {
      "fieldname": "section_break_communication",
      "fieldtype": "Section Break",
      "label": "Communication Log"
    },
    {
      "fieldname": "communications",
      "fieldtype": "Table",
      "label": "Communications",
      "options": "Grievance Communication"
    },
    {
      "fieldname": "section_break_status",
      "fieldtype": "Section Break",
      "label": "Status"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Draft\nSubmitted\nUnder Review\nAssigned\nIn Progress\nPending Information\nEscalated\nResolved\nClosed\nReopened",
      "default": "Draft",
      "in_list_view": 1
    },
    {
      "fieldname": "column_break_5",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "sla_status",
      "fieldtype": "Select",
      "label": "SLA Status",
      "options": "\nWithin SLA\nAt Risk\nBreached",
      "read_only": 1
    },
    {
      "fieldname": "days_open",
      "fieldtype": "Int",
      "label": "Days Open",
      "read_only": 1
    },
    {
      "fieldname": "reopened_count",
      "fieldtype": "Int",
      "label": "Times Reopened",
      "default": 0,
      "read_only": 1
    }
  ],
  "permissions": [
    {"role": "Student", "read": 1, "write": 1, "create": 1, "if_owner": 1},
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1, "if_owner": 1},
    {"role": "Grievance Officer", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Academic Admin", "read": 1, "write": 1}
  ],
  "track_changes": 1
}
```

### 1.2 Grievance Type

```json
{
  "doctype": "DocType",
  "name": "Grievance Type",
  "module": "University ERP",
  "fields": [
    {
      "fieldname": "grievance_type_name",
      "fieldtype": "Data",
      "label": "Type Name",
      "reqd": 1,
      "unique": 1
    },
    {
      "fieldname": "category",
      "fieldtype": "Select",
      "label": "Category",
      "options": "\nAcademic\nAdministrative\nFinancial\nInfrastructure\nHostel\nTransport\nLibrary\nExamination\nFaculty Related\nRagging\nHarassment\nDiscrimination\nOther",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "default_priority",
      "fieldtype": "Select",
      "label": "Default Priority",
      "options": "\nLow\nMedium\nHigh\nUrgent",
      "default": "Medium"
    },
    {
      "fieldname": "sla_days",
      "fieldtype": "Int",
      "label": "SLA (Days)",
      "default": 7,
      "description": "Maximum days for resolution"
    },
    {
      "fieldname": "allow_anonymous",
      "fieldtype": "Check",
      "label": "Allow Anonymous Submission"
    },
    {
      "fieldname": "section_break_routing",
      "fieldtype": "Section Break",
      "label": "Auto-Routing"
    },
    {
      "fieldname": "default_assignee",
      "fieldtype": "Link",
      "label": "Default Assignee",
      "options": "User"
    },
    {
      "fieldname": "default_committee",
      "fieldtype": "Link",
      "label": "Default Committee",
      "options": "Grievance Committee"
    },
    {
      "fieldname": "escalation_matrix",
      "fieldtype": "Table",
      "label": "Escalation Matrix",
      "options": "Grievance Escalation Rule"
    },
    {
      "fieldname": "section_break_settings",
      "fieldtype": "Section Break",
      "label": "Settings"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Is Active",
      "default": 1
    },
    {
      "fieldname": "requires_evidence",
      "fieldtype": "Check",
      "label": "Requires Supporting Evidence"
    },
    {
      "fieldname": "confidential_handling",
      "fieldtype": "Check",
      "label": "Requires Confidential Handling"
    }
  ],
  "permissions": [
    {"role": "Grievance Officer", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
  ]
}
```

### 1.3 Grievance Committee

```json
{
  "doctype": "DocType",
  "name": "Grievance Committee",
  "module": "University ERP",
  "fields": [
    {
      "fieldname": "committee_name",
      "fieldtype": "Data",
      "label": "Committee Name",
      "reqd": 1,
      "unique": 1
    },
    {
      "fieldname": "committee_type",
      "fieldtype": "Select",
      "label": "Committee Type",
      "options": "\nGeneral Grievance\nAnti-Ragging\nSexual Harassment (ICC)\nSC/ST Cell\nWomen Cell\nDisciplinary\nAcademic Appeals\nFinancial Aid",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Is Active",
      "default": 1
    },
    {
      "fieldname": "meeting_frequency",
      "fieldtype": "Select",
      "label": "Meeting Frequency",
      "options": "\nAs Needed\nWeekly\nFortnightly\nMonthly"
    },
    {
      "fieldname": "section_break_members",
      "fieldtype": "Section Break",
      "label": "Committee Members"
    },
    {
      "fieldname": "chairperson",
      "fieldtype": "Link",
      "label": "Chairperson",
      "options": "User",
      "reqd": 1
    },
    {
      "fieldname": "secretary",
      "fieldtype": "Link",
      "label": "Secretary",
      "options": "User"
    },
    {
      "fieldname": "members",
      "fieldtype": "Table",
      "label": "Members",
      "options": "Committee Member"
    },
    {
      "fieldname": "section_break_categories",
      "fieldtype": "Section Break",
      "label": "Handles Categories"
    },
    {
      "fieldname": "grievance_categories",
      "fieldtype": "Table MultiSelect",
      "label": "Grievance Categories",
      "options": "Committee Category Link"
    },
    {
      "fieldname": "section_break_contact",
      "fieldtype": "Section Break",
      "label": "Contact Information"
    },
    {
      "fieldname": "email",
      "fieldtype": "Data",
      "label": "Committee Email",
      "options": "Email"
    },
    {
      "fieldname": "phone",
      "fieldtype": "Data",
      "label": "Contact Phone"
    },
    {
      "fieldname": "office_location",
      "fieldtype": "Data",
      "label": "Office Location"
    }
  ],
  "permissions": [
    {"role": "Grievance Officer", "read": 1, "write": 1, "create": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
  ]
}
```

### 1.4 Feedback Form

```json
{
  "doctype": "DocType",
  "name": "Feedback Form",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "FF-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "form_title",
      "fieldtype": "Data",
      "label": "Form Title",
      "reqd": 1
    },
    {
      "fieldname": "form_type",
      "fieldtype": "Select",
      "label": "Form Type",
      "options": "\nCourse Feedback\nFaculty Feedback\nFacility Feedback\nEvent Feedback\nService Feedback\nGeneral Survey\nExit Survey\nAlumni Survey",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "target_audience",
      "fieldtype": "Select",
      "label": "Target Audience",
      "options": "\nStudents\nFaculty\nParents\nAlumni\nStaff\nAll",
      "reqd": 1
    },
    {
      "fieldname": "academic_year",
      "fieldtype": "Link",
      "label": "Academic Year",
      "options": "Academic Year"
    },
    {
      "fieldname": "academic_term",
      "fieldtype": "Link",
      "label": "Academic Term",
      "options": "Academic Term"
    },
    {
      "fieldname": "section_break_schedule",
      "fieldtype": "Section Break",
      "label": "Schedule"
    },
    {
      "fieldname": "start_date",
      "fieldtype": "Datetime",
      "label": "Start Date",
      "reqd": 1
    },
    {
      "fieldname": "end_date",
      "fieldtype": "Datetime",
      "label": "End Date",
      "reqd": 1
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_mandatory",
      "fieldtype": "Check",
      "label": "Is Mandatory"
    },
    {
      "fieldname": "allow_anonymous",
      "fieldtype": "Check",
      "label": "Allow Anonymous Responses"
    },
    {
      "fieldname": "allow_multiple_responses",
      "fieldtype": "Check",
      "label": "Allow Multiple Responses"
    },
    {
      "fieldname": "section_break_questions",
      "fieldtype": "Section Break",
      "label": "Questions"
    },
    {
      "fieldname": "sections",
      "fieldtype": "Table",
      "label": "Form Sections",
      "options": "Feedback Form Section"
    },
    {
      "fieldname": "section_break_filters",
      "fieldtype": "Section Break",
      "label": "Target Filters"
    },
    {
      "fieldname": "programs",
      "fieldtype": "Table MultiSelect",
      "label": "Programs",
      "options": "Feedback Program Filter"
    },
    {
      "fieldname": "departments",
      "fieldtype": "Table MultiSelect",
      "label": "Departments",
      "options": "Feedback Department Filter"
    },
    {
      "fieldname": "courses",
      "fieldtype": "Table MultiSelect",
      "label": "Courses (for course/faculty feedback)",
      "options": "Feedback Course Filter"
    },
    {
      "fieldname": "section_break_settings",
      "fieldtype": "Section Break",
      "label": "Settings"
    },
    {
      "fieldname": "show_progress",
      "fieldtype": "Check",
      "label": "Show Progress Bar",
      "default": 1
    },
    {
      "fieldname": "randomize_questions",
      "fieldtype": "Check",
      "label": "Randomize Question Order"
    },
    {
      "fieldname": "show_section_scores",
      "fieldtype": "Check",
      "label": "Show Section Scores to Admin"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "thank_you_message",
      "fieldtype": "Text Editor",
      "label": "Thank You Message"
    },
    {
      "fieldname": "reminder_days",
      "fieldtype": "Int",
      "label": "Send Reminder After (Days)",
      "default": 3
    },
    {
      "fieldname": "section_break_status",
      "fieldtype": "Section Break",
      "label": "Status"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Draft\nScheduled\nActive\nPaused\nClosed\nArchived",
      "default": "Draft"
    },
    {
      "fieldname": "total_responses",
      "fieldtype": "Int",
      "label": "Total Responses",
      "read_only": 1,
      "default": 0
    },
    {
      "fieldname": "response_rate",
      "fieldtype": "Percent",
      "label": "Response Rate",
      "read_only": 1
    }
  ],
  "permissions": [
    {"role": "Academic Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "HOD", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.5 Feedback Form Section (Child Table)

```json
{
  "doctype": "DocType",
  "name": "Feedback Form Section",
  "module": "University ERP",
  "istable": 1,
  "fields": [
    {
      "fieldname": "section_title",
      "fieldtype": "Data",
      "label": "Section Title",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "section_description",
      "fieldtype": "Small Text",
      "label": "Description"
    },
    {
      "fieldname": "questions",
      "fieldtype": "Table",
      "label": "Questions",
      "options": "Feedback Question"
    }
  ]
}
```

### 1.6 Feedback Question (Child Table)

```json
{
  "doctype": "DocType",
  "name": "Feedback Question",
  "module": "University ERP",
  "istable": 1,
  "fields": [
    {
      "fieldname": "question_text",
      "fieldtype": "Text",
      "label": "Question",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "question_type",
      "fieldtype": "Select",
      "label": "Type",
      "options": "\nRating (1-5)\nRating (1-10)\nMultiple Choice\nCheckbox\nShort Text\nLong Text\nYes/No\nLikert Scale",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "is_required",
      "fieldtype": "Check",
      "label": "Required",
      "default": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "options",
      "fieldtype": "Small Text",
      "label": "Options (one per line)",
      "depends_on": "eval:in_list(['Multiple Choice', 'Checkbox', 'Likert Scale'], doc.question_type)"
    },
    {
      "fieldname": "help_text",
      "fieldtype": "Small Text",
      "label": "Help Text"
    },
    {
      "fieldname": "weightage",
      "fieldtype": "Float",
      "label": "Weightage",
      "default": 1,
      "description": "For calculating weighted scores"
    },
    {
      "fieldname": "category",
      "fieldtype": "Data",
      "label": "Category/Tag",
      "description": "For grouping in reports"
    }
  ]
}
```

### 1.7 Feedback Response

```json
{
  "doctype": "DocType",
  "name": "Feedback Response",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "FR-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "feedback_form",
      "fieldtype": "Link",
      "label": "Feedback Form",
      "options": "Feedback Form",
      "reqd": 1
    },
    {
      "fieldname": "respondent_type",
      "fieldtype": "Select",
      "label": "Respondent Type",
      "options": "\nStudent\nFaculty\nParent\nAlumni\nStaff\nAnonymous",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "student",
      "fieldtype": "Link",
      "label": "Student",
      "options": "Student",
      "depends_on": "eval:doc.respondent_type == 'Student'"
    },
    {
      "fieldname": "faculty",
      "fieldtype": "Link",
      "label": "Faculty",
      "options": "Faculty Member",
      "depends_on": "eval:doc.respondent_type == 'Faculty'"
    },
    {
      "fieldname": "is_anonymous",
      "fieldtype": "Check",
      "label": "Anonymous Response",
      "read_only": 1
    },
    {
      "fieldname": "section_break_context",
      "fieldtype": "Section Break",
      "label": "Context",
      "depends_on": "eval:doc.feedback_form && doc.feedback_form.form_type"
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course"
    },
    {
      "fieldname": "instructor",
      "fieldtype": "Link",
      "label": "Instructor",
      "options": "Faculty Member"
    },
    {
      "fieldname": "section_break_answers",
      "fieldtype": "Section Break",
      "label": "Responses"
    },
    {
      "fieldname": "answers",
      "fieldtype": "Table",
      "label": "Answers",
      "options": "Feedback Answer"
    },
    {
      "fieldname": "section_break_scores",
      "fieldtype": "Section Break",
      "label": "Calculated Scores"
    },
    {
      "fieldname": "overall_score",
      "fieldtype": "Float",
      "label": "Overall Score",
      "read_only": 1
    },
    {
      "fieldname": "section_scores",
      "fieldtype": "Table",
      "label": "Section Scores",
      "options": "Feedback Section Score",
      "read_only": 1
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "nps_score",
      "fieldtype": "Int",
      "label": "NPS Score",
      "read_only": 1
    },
    {
      "fieldname": "nps_category",
      "fieldtype": "Data",
      "label": "NPS Category",
      "read_only": 1
    },
    {
      "fieldname": "section_break_meta",
      "fieldtype": "Section Break",
      "label": "Metadata"
    },
    {
      "fieldname": "submission_datetime",
      "fieldtype": "Datetime",
      "label": "Submitted At",
      "read_only": 1
    },
    {
      "fieldname": "time_taken_seconds",
      "fieldtype": "Int",
      "label": "Time Taken (seconds)",
      "read_only": 1
    },
    {
      "fieldname": "ip_address",
      "fieldtype": "Data",
      "label": "IP Address",
      "read_only": 1
    },
    {
      "fieldname": "device_info",
      "fieldtype": "Small Text",
      "label": "Device Info",
      "read_only": 1
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "In Progress\nSubmitted\nValid\nInvalid",
      "default": "In Progress"
    }
  ],
  "permissions": [
    {"role": "Academic Admin", "read": 1},
    {"role": "HOD", "read": 1},
    {"role": "Student", "read": 1, "write": 1, "create": 1, "if_owner": 1}
  ]
}
```

### 1.8 Suggestion Box

```json
{
  "doctype": "DocType",
  "name": "Suggestion",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "SUG-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "subject",
      "fieldtype": "Data",
      "label": "Subject",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "category",
      "fieldtype": "Select",
      "label": "Category",
      "options": "\nAcademic Improvement\nInfrastructure\nServices\nEvents & Activities\nPolicy Suggestion\nTechnology\nOther",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_anonymous",
      "fieldtype": "Check",
      "label": "Submit Anonymously",
      "default": 0
    },
    {
      "fieldname": "submitted_by_type",
      "fieldtype": "Select",
      "label": "Submitted By Type",
      "options": "\nStudent\nFaculty\nStaff\nParent\nAlumni\nOther"
    },
    {
      "fieldname": "section_break_details",
      "fieldtype": "Section Break",
      "label": "Suggestion Details"
    },
    {
      "fieldname": "suggestion",
      "fieldtype": "Text Editor",
      "label": "Your Suggestion",
      "reqd": 1
    },
    {
      "fieldname": "expected_benefit",
      "fieldtype": "Text",
      "label": "Expected Benefits"
    },
    {
      "fieldname": "implementation_idea",
      "fieldtype": "Text",
      "label": "Implementation Ideas (if any)"
    },
    {
      "fieldname": "attachments",
      "fieldtype": "Table",
      "label": "Attachments",
      "options": "Suggestion Attachment"
    },
    {
      "fieldname": "section_break_review",
      "fieldtype": "Section Break",
      "label": "Review"
    },
    {
      "fieldname": "reviewed_by",
      "fieldtype": "Link",
      "label": "Reviewed By",
      "options": "User"
    },
    {
      "fieldname": "review_date",
      "fieldtype": "Date",
      "label": "Review Date"
    },
    {
      "fieldname": "review_comments",
      "fieldtype": "Text",
      "label": "Review Comments"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "feasibility",
      "fieldtype": "Select",
      "label": "Feasibility Assessment",
      "options": "\nHighly Feasible\nFeasible\nNeeds Further Study\nNot Feasible"
    },
    {
      "fieldname": "priority",
      "fieldtype": "Select",
      "label": "Priority",
      "options": "\nLow\nMedium\nHigh"
    },
    {
      "fieldname": "section_break_implementation",
      "fieldtype": "Section Break",
      "label": "Implementation",
      "depends_on": "eval:doc.status == 'Approved' || doc.status == 'Implemented'"
    },
    {
      "fieldname": "implementation_plan",
      "fieldtype": "Text Editor",
      "label": "Implementation Plan"
    },
    {
      "fieldname": "assigned_to",
      "fieldtype": "Link",
      "label": "Assigned To",
      "options": "User"
    },
    {
      "fieldname": "target_date",
      "fieldtype": "Date",
      "label": "Target Implementation Date"
    },
    {
      "fieldname": "implementation_status",
      "fieldtype": "Text",
      "label": "Implementation Status Update"
    },
    {
      "fieldname": "section_break_status",
      "fieldtype": "Section Break",
      "label": "Status"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "New\nUnder Review\nApproved\nRejected\nIn Implementation\nImplemented\nDeferred",
      "default": "New",
      "in_list_view": 1
    },
    {
      "fieldname": "votes",
      "fieldtype": "Int",
      "label": "Upvotes",
      "default": 0,
      "read_only": 1
    }
  ],
  "permissions": [
    {"role": "Student", "read": 1, "write": 1, "create": 1},
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1},
    {"role": "Academic Admin", "read": 1, "write": 1, "delete": 1}
  ]
}
```

---

## 2. Grievance Management System

### 2.1 Grievance Manager Class

```python
# university_erp/university_erp/grievance/grievance_manager.py

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, date_diff, today
from datetime import datetime
from typing import Dict, List, Optional

class GrievanceManager:
    """
    Manager class for handling grievance operations
    """

    @staticmethod
    def submit_grievance(data: Dict) -> str:
        """
        Submit a new grievance

        Args:
            data: Grievance data dictionary

        Returns:
            Grievance name
        """
        grievance = frappe.new_doc("Grievance")

        # Set basic fields
        grievance.subject = data.get("subject")
        grievance.grievance_type = data.get("grievance_type")
        grievance.category = data.get("category")
        grievance.priority = data.get("priority", "Medium")
        grievance.description = data.get("description")
        grievance.is_anonymous = data.get("is_anonymous", False)
        grievance.submitted_by_type = data.get("submitted_by_type")

        # Set submitter details
        if not grievance.is_anonymous:
            if data.get("student"):
                grievance.student = data.get("student")
            elif data.get("faculty"):
                grievance.faculty = data.get("faculty")
            elif data.get("parent"):
                grievance.parent = data.get("parent")

            grievance.contact_email = data.get("contact_email")
            grievance.contact_phone = data.get("contact_phone")

        # Set incident details
        grievance.against_person = data.get("against_person")
        grievance.incident_date = data.get("incident_date")
        grievance.incident_location = data.get("incident_location")
        grievance.witnesses = data.get("witnesses")
        grievance.department = data.get("department")

        # Get SLA from grievance type
        gtype = frappe.get_doc("Grievance Type", grievance.grievance_type)
        grievance.expected_resolution_date = add_days(today(), gtype.sla_days)

        grievance.status = "Submitted"
        grievance.insert()

        # Handle attachments
        for attachment in data.get("attachments", []):
            grievance.append("attachments", {
                "file_name": attachment.get("file_name"),
                "file_url": attachment.get("file_url"),
                "description": attachment.get("description")
            })

        if data.get("attachments"):
            grievance.save()

        # Auto-assign based on grievance type
        GrievanceManager.auto_assign(grievance.name)

        # Send acknowledgment
        GrievanceManager.send_acknowledgment(grievance.name)

        return grievance.name

    @staticmethod
    def auto_assign(grievance_name: str):
        """
        Auto-assign grievance based on type configuration
        """
        grievance = frappe.get_doc("Grievance", grievance_name)
        gtype = frappe.get_doc("Grievance Type", grievance.grievance_type)

        if gtype.default_committee:
            grievance.assigned_committee = gtype.default_committee
            grievance.status = "Assigned"
        elif gtype.default_assignee:
            grievance.assigned_to = gtype.default_assignee
            grievance.status = "Assigned"

        grievance.assignment_date = now_datetime()
        grievance.save()

        # Log assignment
        grievance.append("communications", {
            "communication_type": "System",
            "message": f"Grievance auto-assigned to {grievance.assigned_to or grievance.assigned_committee}",
            "timestamp": now_datetime()
        })
        grievance.save()

    @staticmethod
    def send_acknowledgment(grievance_name: str):
        """
        Send acknowledgment to grievance submitter
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        if grievance.is_anonymous:
            return  # Can't send to anonymous

        recipient = None
        if grievance.contact_email:
            recipient = grievance.contact_email
        elif grievance.student:
            recipient = frappe.db.get_value("Student", grievance.student, "student_email_id")
        elif grievance.faculty:
            recipient = frappe.db.get_value("Faculty Member", grievance.faculty, "email")

        if recipient:
            frappe.sendmail(
                recipients=[recipient],
                subject=f"Grievance Submitted - {grievance.name}",
                template="grievance_acknowledgment",
                args={
                    "grievance": grievance,
                    "tracking_id": grievance.name,
                    "expected_resolution": grievance.expected_resolution_date
                }
            )

    @staticmethod
    def add_response(grievance_name: str, message: str,
                    response_type: str = "Response", attachments: list = None):
        """
        Add a response/communication to grievance
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        grievance.append("communications", {
            "communication_type": response_type,
            "message": message,
            "timestamp": now_datetime(),
            "sent_by": frappe.session.user
        })

        # Add attachments if any
        if attachments:
            for att in attachments:
                grievance.append("attachments", att)

        grievance.save()

        # Notify complainant if not anonymous
        if not grievance.is_anonymous:
            GrievanceManager._notify_complainant(grievance, message)

    @staticmethod
    def escalate(grievance_name: str, reason: str = None):
        """
        Escalate grievance to next level
        """
        grievance = frappe.get_doc("Grievance", grievance_name)
        gtype = frappe.get_doc("Grievance Type", grievance.grievance_type)

        current_level = grievance.current_escalation_level
        next_level = current_level + 1

        # Find escalation rule for next level
        next_assignee = None
        for rule in gtype.escalation_matrix:
            if rule.level == next_level:
                next_assignee = rule.assignee
                break

        if not next_assignee:
            frappe.throw(_("No escalation path defined for level {0}").format(next_level))

        # Log escalation
        grievance.append("escalation_history", {
            "from_level": current_level,
            "to_level": next_level,
            "escalated_at": now_datetime(),
            "escalated_by": frappe.session.user,
            "reason": reason,
            "previous_assignee": grievance.assigned_to,
            "new_assignee": next_assignee
        })

        grievance.current_escalation_level = next_level
        grievance.assigned_to = next_assignee
        grievance.status = "Escalated"
        grievance.save()

        # Notify new assignee
        frappe.sendmail(
            recipients=[next_assignee],
            subject=f"Grievance Escalated - {grievance.name}",
            template="grievance_escalation",
            args={
                "grievance": grievance,
                "reason": reason
            }
        )

        return grievance.current_escalation_level

    @staticmethod
    def resolve(grievance_name: str, resolution_notes: str,
               resolution_type: str, actions: list = None):
        """
        Resolve a grievance
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        grievance.resolution_notes = resolution_notes
        grievance.resolution_type = resolution_type
        grievance.resolved_by = frappe.session.user
        grievance.resolution_date = now_datetime()
        grievance.status = "Resolved"

        # Add actions taken
        if actions:
            for action in actions:
                grievance.append("action_taken", {
                    "action_description": action.get("description"),
                    "action_date": action.get("date") or today(),
                    "taken_by": action.get("taken_by") or frappe.session.user
                })

        grievance.save()

        # Notify complainant
        if not grievance.is_anonymous:
            GrievanceManager._notify_resolution(grievance)

        return grievance.name

    @staticmethod
    def reopen(grievance_name: str, reason: str):
        """
        Reopen a resolved grievance
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        if grievance.status not in ["Resolved", "Closed"]:
            frappe.throw(_("Only resolved or closed grievances can be reopened"))

        grievance.reopened_count = (grievance.reopened_count or 0) + 1
        grievance.status = "Reopened"

        grievance.append("communications", {
            "communication_type": "System",
            "message": f"Grievance reopened. Reason: {reason}",
            "timestamp": now_datetime()
        })

        # Reset resolution fields
        grievance.satisfaction_rating = None
        grievance.satisfaction_feedback = None

        grievance.save()

        return grievance.name

    @staticmethod
    def record_satisfaction(grievance_name: str, rating: int, feedback: str = None):
        """
        Record complainant satisfaction after resolution
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        grievance.satisfaction_rating = rating
        grievance.satisfaction_feedback = feedback

        if rating >= 4:
            grievance.status = "Closed"
        else:
            # Low satisfaction might trigger review
            grievance.append("communications", {
                "communication_type": "System",
                "message": f"Low satisfaction rating ({rating}/5) recorded. Review may be required.",
                "timestamp": now_datetime()
            })

        grievance.save()

    @staticmethod
    def check_sla_status():
        """
        Check SLA status for all open grievances (scheduled job)
        """
        open_grievances = frappe.get_all("Grievance",
            filters={
                "status": ["in", ["Submitted", "Under Review", "Assigned", "In Progress", "Escalated"]]
            },
            fields=["name", "expected_resolution_date", "grievance_type", "current_escalation_level"]
        )

        for g in open_grievances:
            days_to_sla = date_diff(g.expected_resolution_date, today())

            if days_to_sla < 0:
                # SLA Breached
                frappe.db.set_value("Grievance", g.name, "sla_status", "Breached")

                # Auto-escalate if configured
                gtype = frappe.get_cached_doc("Grievance Type", g.grievance_type)
                auto_escalate = any(
                    r.auto_escalate_on_sla_breach
                    for r in gtype.escalation_matrix
                    if r.level == g.current_escalation_level + 1
                )

                if auto_escalate:
                    GrievanceManager.escalate(g.name, "Auto-escalated due to SLA breach")

            elif days_to_sla <= 2:
                # At Risk
                frappe.db.set_value("Grievance", g.name, "sla_status", "At Risk")
            else:
                frappe.db.set_value("Grievance", g.name, "sla_status", "Within SLA")

            # Update days open
            creation_date = frappe.db.get_value("Grievance", g.name, "creation")
            days_open = date_diff(today(), creation_date)
            frappe.db.set_value("Grievance", g.name, "days_open", days_open)

    @staticmethod
    def get_grievance_stats(filters: Dict = None) -> Dict:
        """
        Get grievance statistics
        """
        base_filters = filters or {}

        total = frappe.db.count("Grievance", base_filters)

        status_counts = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabGrievance`
            GROUP BY status
        """, as_dict=True)

        category_counts = frappe.db.sql("""
            SELECT category, COUNT(*) as count
            FROM `tabGrievance`
            GROUP BY category
            ORDER BY count DESC
        """, as_dict=True)

        avg_resolution_time = frappe.db.sql("""
            SELECT AVG(TIMESTAMPDIFF(DAY, creation, resolution_date)) as avg_days
            FROM `tabGrievance`
            WHERE resolution_date IS NOT NULL
        """)[0][0] or 0

        sla_compliance = frappe.db.sql("""
            SELECT
                SUM(CASE WHEN sla_status != 'Breached' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as compliance
            FROM `tabGrievance`
            WHERE status IN ('Resolved', 'Closed')
        """)[0][0] or 0

        return {
            "total": total,
            "by_status": {s.status: s.count for s in status_counts},
            "by_category": category_counts[:5],
            "avg_resolution_days": round(avg_resolution_time, 1),
            "sla_compliance_percent": round(sla_compliance, 1)
        }

    @staticmethod
    def _notify_complainant(grievance, message):
        """Send notification to complainant"""
        recipient = None
        if grievance.contact_email:
            recipient = grievance.contact_email
        elif grievance.student:
            recipient = frappe.db.get_value("Student", grievance.student, "student_email_id")

        if recipient:
            frappe.sendmail(
                recipients=[recipient],
                subject=f"Update on Grievance - {grievance.name}",
                template="grievance_update",
                args={"grievance": grievance, "update_message": message}
            )

    @staticmethod
    def _notify_resolution(grievance):
        """Notify complainant of resolution"""
        recipient = None
        if grievance.contact_email:
            recipient = grievance.contact_email
        elif grievance.student:
            recipient = frappe.db.get_value("Student", grievance.student, "student_email_id")

        if recipient:
            frappe.sendmail(
                recipients=[recipient],
                subject=f"Grievance Resolved - {grievance.name}",
                template="grievance_resolved",
                args={
                    "grievance": grievance,
                    "feedback_link": f"/grievance-feedback?grievance={grievance.name}"
                }
            )


# Scheduled Jobs

def daily_sla_check():
    """Daily job to check SLA status"""
    GrievanceManager.check_sla_status()

def send_pending_reminders():
    """Send reminders for pending grievances"""
    pending = frappe.get_all("Grievance",
        filters={
            "status": ["in", ["Assigned", "In Progress"]],
            "sla_status": "At Risk"
        },
        fields=["name", "assigned_to", "subject"]
    )

    for g in pending:
        if g.assigned_to:
            frappe.sendmail(
                recipients=[g.assigned_to],
                subject=f"Reminder: Grievance {g.name} requires attention",
                template="grievance_reminder",
                args={"grievance_name": g.name, "subject": g.subject}
            )
```

---

## 3. Feedback Management System

### 3.1 Feedback Manager Class

```python
# university_erp/university_erp/feedback/feedback_manager.py

import frappe
from frappe import _
from frappe.utils import now_datetime, cint, flt
from typing import Dict, List, Optional
import json

class FeedbackManager:
    """
    Manager class for feedback forms and responses
    """

    @staticmethod
    def create_course_feedback_forms(academic_term: str):
        """
        Auto-create course feedback forms for all courses in a term
        """
        courses = frappe.get_all("Course Schedule",
            filters={"academic_term": academic_term},
            fields=["course", "instructor"],
            distinct=True
        )

        created = 0
        for course_data in courses:
            # Check if feedback form already exists
            existing = frappe.db.exists("Feedback Form", {
                "form_type": "Course Feedback",
                "academic_term": academic_term,
                "courses": [["Feedback Course Filter", "course", "=", course_data.course]]
            })

            if not existing:
                form = FeedbackManager.create_standard_course_feedback(
                    course_data.course,
                    academic_term
                )
                created += 1

        return created

    @staticmethod
    def create_standard_course_feedback(course: str, academic_term: str) -> str:
        """
        Create a standard course feedback form
        """
        course_doc = frappe.get_doc("Course", course)

        form = frappe.new_doc("Feedback Form")
        form.form_title = f"Course Feedback - {course_doc.course_name}"
        form.form_type = "Course Feedback"
        form.target_audience = "Students"
        form.academic_term = academic_term
        form.allow_anonymous = True
        form.is_mandatory = True

        # Add standard sections and questions
        form.append("sections", {
            "section_title": "Course Content",
            "section_description": "Rate the course content and structure",
            "questions": [
                {"question_text": "The course objectives were clearly defined", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content"},
                {"question_text": "The course content was relevant and up-to-date", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content"},
                {"question_text": "The course materials were helpful", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content"},
                {"question_text": "The difficulty level was appropriate", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content"}
            ]
        })

        form.append("sections", {
            "section_title": "Teaching Effectiveness",
            "section_description": "Rate the instructor's teaching",
            "questions": [
                {"question_text": "The instructor explained concepts clearly", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching"},
                {"question_text": "The instructor was well prepared for classes", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching"},
                {"question_text": "The instructor encouraged student participation", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching"},
                {"question_text": "The instructor was available for doubts and queries", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching"}
            ]
        })

        form.append("sections", {
            "section_title": "Assessment",
            "section_description": "Rate the assessment methods",
            "questions": [
                {"question_text": "Assignments were relevant to course content", "question_type": "Rating (1-5)", "is_required": 1, "category": "Assessment"},
                {"question_text": "Feedback on assignments was helpful", "question_type": "Rating (1-5)", "is_required": 1, "category": "Assessment"},
                {"question_text": "Examinations covered the syllabus appropriately", "question_type": "Rating (1-5)", "is_required": 1, "category": "Assessment"}
            ]
        })

        form.append("sections", {
            "section_title": "Overall Experience",
            "questions": [
                {"question_text": "Overall, I am satisfied with this course", "question_type": "Rating (1-5)", "is_required": 1, "category": "Overall"},
                {"question_text": "I would recommend this course to other students", "question_type": "Rating (1-5)", "is_required": 1, "category": "Overall"},
                {"question_text": "On a scale of 0-10, how likely are you to recommend this course?", "question_type": "Rating (1-10)", "is_required": 1, "category": "NPS"},
                {"question_text": "What did you like most about this course?", "question_type": "Long Text", "is_required": 0, "category": "Comments"},
                {"question_text": "What improvements would you suggest?", "question_type": "Long Text", "is_required": 0, "category": "Comments"}
            ]
        })

        form.append("courses", {"course": course})

        form.thank_you_message = "<p>Thank you for your valuable feedback! Your responses will help us improve the course.</p>"
        form.status = "Draft"

        form.insert()
        return form.name

    @staticmethod
    def submit_response(feedback_form: str, answers: List[Dict],
                       context: Dict = None, is_anonymous: bool = False) -> str:
        """
        Submit a feedback response

        Args:
            feedback_form: Feedback form name
            answers: List of {question_id, answer} dicts
            context: {course, instructor} for course feedback
            is_anonymous: Whether response is anonymous

        Returns:
            Response document name
        """
        form = frappe.get_doc("Feedback Form", feedback_form)

        # Validate form is active
        if form.status != "Active":
            frappe.throw(_("This feedback form is not currently active"))

        # Check if already submitted
        if not form.allow_multiple_responses:
            existing = FeedbackManager._check_existing_response(
                feedback_form,
                context
            )
            if existing:
                frappe.throw(_("You have already submitted feedback for this"))

        response = frappe.new_doc("Feedback Response")
        response.feedback_form = feedback_form
        response.is_anonymous = is_anonymous or form.allow_anonymous

        # Set respondent
        if not response.is_anonymous:
            student = frappe.db.get_value("Student", {"user": frappe.session.user})
            if student:
                response.respondent_type = "Student"
                response.student = student
            else:
                faculty = frappe.db.get_value("Faculty Member", {"user": frappe.session.user})
                if faculty:
                    response.respondent_type = "Faculty"
                    response.faculty = faculty
        else:
            response.respondent_type = "Anonymous"

        # Set context
        if context:
            response.course = context.get("course")
            response.instructor = context.get("instructor")

        # Add answers
        for ans in answers:
            response.append("answers", {
                "question_id": ans.get("question_id"),
                "answer_value": json.dumps(ans.get("answer")) if isinstance(ans.get("answer"), (list, dict)) else str(ans.get("answer")),
                "question_text": ans.get("question_text")
            })

        response.submission_datetime = now_datetime()
        response.ip_address = frappe.local.request_ip
        response.device_info = frappe.request.headers.get("User-Agent", "")[:200]
        response.status = "Submitted"

        response.insert()

        # Calculate scores
        FeedbackManager.calculate_response_scores(response.name)

        # Update form statistics
        FeedbackManager.update_form_statistics(feedback_form)

        return response.name

    @staticmethod
    def calculate_response_scores(response_name: str):
        """
        Calculate various scores for a feedback response
        """
        response = frappe.get_doc("Feedback Response", response_name)
        form = frappe.get_doc("Feedback Form", response.feedback_form)

        total_score = 0
        total_weight = 0
        section_scores = {}
        nps_score = None

        # Build question lookup
        questions = {}
        for section in form.sections:
            section_scores[section.section_title] = {"total": 0, "count": 0, "weight": 0}
            for q in section.questions:
                questions[q.name] = {
                    "section": section.section_title,
                    "type": q.question_type,
                    "weight": q.weightage or 1,
                    "category": q.category
                }

        # Process answers
        for ans in response.answers:
            q_info = questions.get(ans.question_id)
            if not q_info:
                continue

            # Calculate numeric score
            score = FeedbackManager._get_numeric_score(
                ans.answer_value,
                q_info["type"]
            )

            if score is not None:
                # Overall score
                total_score += score * q_info["weight"]
                total_weight += q_info["weight"]

                # Section score
                section = q_info["section"]
                section_scores[section]["total"] += score * q_info["weight"]
                section_scores[section]["weight"] += q_info["weight"]
                section_scores[section]["count"] += 1

                # NPS score
                if q_info["category"] == "NPS":
                    nps_score = int(score)

        # Save overall score
        if total_weight > 0:
            response.overall_score = (total_score / total_weight) * 100

        # Save section scores
        response.section_scores = []
        for section_name, scores in section_scores.items():
            if scores["weight"] > 0:
                avg = (scores["total"] / scores["weight"]) * 100
                response.append("section_scores", {
                    "section_name": section_name,
                    "score": avg,
                    "responses_count": scores["count"]
                })

        # NPS calculation
        if nps_score is not None:
            response.nps_score = nps_score
            if nps_score >= 9:
                response.nps_category = "Promoter"
            elif nps_score >= 7:
                response.nps_category = "Passive"
            else:
                response.nps_category = "Detractor"

        response.status = "Valid"
        response.save()

    @staticmethod
    def _get_numeric_score(answer: str, question_type: str) -> Optional[float]:
        """Convert answer to numeric score (0-1 scale)"""
        try:
            if question_type == "Rating (1-5)":
                return (float(answer) - 1) / 4  # Normalize to 0-1
            elif question_type == "Rating (1-10)":
                return (float(answer) - 1) / 9
            elif question_type == "Yes/No":
                return 1.0 if answer.lower() in ["yes", "true", "1"] else 0.0
            elif question_type == "Likert Scale":
                # Assume 5-point Likert
                likert_map = {
                    "strongly disagree": 0,
                    "disagree": 0.25,
                    "neutral": 0.5,
                    "agree": 0.75,
                    "strongly agree": 1.0
                }
                return likert_map.get(answer.lower(), 0.5)
        except:
            pass
        return None

    @staticmethod
    def _check_existing_response(feedback_form: str, context: Dict) -> bool:
        """Check if user already submitted response"""
        filters = {"feedback_form": feedback_form}

        student = frappe.db.get_value("Student", {"user": frappe.session.user})
        if student:
            filters["student"] = student
        else:
            faculty = frappe.db.get_value("Faculty Member", {"user": frappe.session.user})
            if faculty:
                filters["faculty"] = faculty

        if context:
            if context.get("course"):
                filters["course"] = context.get("course")
            if context.get("instructor"):
                filters["instructor"] = context.get("instructor")

        return frappe.db.exists("Feedback Response", filters)

    @staticmethod
    def update_form_statistics(feedback_form: str):
        """Update form response statistics"""
        form = frappe.get_doc("Feedback Form", feedback_form)

        total_responses = frappe.db.count("Feedback Response", {
            "feedback_form": feedback_form,
            "status": ["in", ["Submitted", "Valid"]]
        })

        form.total_responses = total_responses

        # Calculate response rate
        target_count = FeedbackManager._get_target_count(form)
        if target_count > 0:
            form.response_rate = (total_responses / target_count) * 100

        form.save()

    @staticmethod
    def _get_target_count(form) -> int:
        """Get expected number of respondents"""
        if form.target_audience == "Students":
            if form.courses:
                return frappe.db.count("Course Enrollment",
                    filters={"course": ["in", [c.course for c in form.courses]]}
                )
            elif form.programs:
                return frappe.db.count("Program Enrollment",
                    filters={"program": ["in", [p.program for p in form.programs]]}
                )
        return 0

    @staticmethod
    def get_feedback_analysis(feedback_form: str) -> Dict:
        """
        Get comprehensive feedback analysis

        Returns:
            Analysis dictionary with scores, trends, comments
        """
        form = frappe.get_doc("Feedback Form", feedback_form)

        responses = frappe.get_all("Feedback Response",
            filters={
                "feedback_form": feedback_form,
                "status": "Valid"
            },
            fields=["name", "overall_score", "nps_score", "nps_category",
                   "course", "instructor", "submission_datetime"]
        )

        if not responses:
            return {"message": "No responses yet"}

        # Overall metrics
        avg_score = sum(r.overall_score or 0 for r in responses) / len(responses)

        # NPS calculation
        promoters = len([r for r in responses if r.nps_category == "Promoter"])
        detractors = len([r for r in responses if r.nps_category == "Detractor"])
        nps = ((promoters - detractors) / len(responses)) * 100 if responses else 0

        # Question-wise analysis
        question_scores = FeedbackManager._get_question_analysis(feedback_form)

        # Section-wise analysis
        section_scores = frappe.db.sql("""
            SELECT fss.section_name, AVG(fss.score) as avg_score
            FROM `tabFeedback Section Score` fss
            JOIN `tabFeedback Response` fr ON fss.parent = fr.name
            WHERE fr.feedback_form = %s AND fr.status = 'Valid'
            GROUP BY fss.section_name
        """, feedback_form, as_dict=True)

        # Comments extraction
        comments = FeedbackManager._extract_comments(feedback_form)

        return {
            "total_responses": len(responses),
            "average_score": round(avg_score, 2),
            "nps_score": round(nps, 1),
            "nps_breakdown": {
                "promoters": promoters,
                "passives": len([r for r in responses if r.nps_category == "Passive"]),
                "detractors": detractors
            },
            "section_scores": section_scores,
            "question_scores": question_scores,
            "positive_comments": comments["positive"][:10],
            "improvement_suggestions": comments["suggestions"][:10]
        }

    @staticmethod
    def _get_question_analysis(feedback_form: str) -> List[Dict]:
        """Get question-wise score analysis"""
        return frappe.db.sql("""
            SELECT
                fa.question_text,
                AVG(CAST(fa.answer_value AS DECIMAL(10,2))) as avg_score,
                COUNT(*) as responses
            FROM `tabFeedback Answer` fa
            JOIN `tabFeedback Response` fr ON fa.parent = fr.name
            JOIN `tabFeedback Question` fq ON fa.question_id = fq.name
            WHERE fr.feedback_form = %s
            AND fr.status = 'Valid'
            AND fq.question_type IN ('Rating (1-5)', 'Rating (1-10)')
            GROUP BY fa.question_text
            ORDER BY avg_score ASC
        """, feedback_form, as_dict=True)

    @staticmethod
    def _extract_comments(feedback_form: str) -> Dict:
        """Extract and categorize text comments"""
        comments = frappe.db.sql("""
            SELECT fa.answer_value, fq.category
            FROM `tabFeedback Answer` fa
            JOIN `tabFeedback Response` fr ON fa.parent = fr.name
            JOIN `tabFeedback Question` fq ON fa.question_id = fq.name
            WHERE fr.feedback_form = %s
            AND fr.status = 'Valid'
            AND fq.question_type IN ('Short Text', 'Long Text')
            AND fa.answer_value != ''
        """, feedback_form, as_dict=True)

        positive = []
        suggestions = []

        for c in comments:
            if c.category == "Comments":
                positive.append(c.answer_value)
            else:
                suggestions.append(c.answer_value)

        return {"positive": positive, "suggestions": suggestions}


# API Endpoints

@frappe.whitelist()
def get_pending_feedback_forms():
    """Get pending feedback forms for current user"""
    student = frappe.db.get_value("Student", {"user": frappe.session.user})

    if not student:
        return []

    # Get student's enrolled courses
    enrollments = frappe.get_all("Course Enrollment",
        filters={"student": student},
        pluck="course"
    )

    forms = frappe.get_all("Feedback Form",
        filters={
            "status": "Active",
            "target_audience": "Students"
        },
        fields=["name", "form_title", "form_type", "end_date", "is_mandatory"]
    )

    pending = []
    for form in forms:
        # Check if already responded
        responded = frappe.db.exists("Feedback Response", {
            "feedback_form": form.name,
            "student": student,
            "status": ["in", ["Submitted", "Valid"]]
        })

        if not responded:
            pending.append(form)

    return pending


@frappe.whitelist()
def submit_feedback(feedback_form: str, answers: str,
                   course: str = None, instructor: str = None,
                   is_anonymous: bool = False):
    """API to submit feedback response"""
    answers_list = json.loads(answers)
    context = {}
    if course:
        context["course"] = course
    if instructor:
        context["instructor"] = instructor

    return FeedbackManager.submit_response(
        feedback_form,
        answers_list,
        context,
        is_anonymous
    )
```

---

## 4. Reports

### 4.1 Grievance Summary Report

```python
# university_erp/university_erp/grievance/report/grievance_summary/grievance_summary.py

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary

def get_columns():
    return [
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 150},
        {"label": "Total", "fieldname": "total", "fieldtype": "Int", "width": 80},
        {"label": "Open", "fieldname": "open", "fieldtype": "Int", "width": 80},
        {"label": "Resolved", "fieldname": "resolved", "fieldtype": "Int", "width": 90},
        {"label": "Avg Days", "fieldname": "avg_days", "fieldtype": "Float", "width": 90},
        {"label": "SLA Compliance %", "fieldname": "sla_compliance", "fieldtype": "Percent", "width": 120},
        {"label": "Avg Satisfaction", "fieldname": "satisfaction", "fieldtype": "Float", "width": 110}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += f" AND creation >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND creation <= '{filters.get('to_date')}'"
    if filters.get("category"):
        conditions += f" AND category = '{filters.get('category')}'"

    return frappe.db.sql(f"""
        SELECT
            category,
            COUNT(*) as total,
            SUM(CASE WHEN status NOT IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as open,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved,
            AVG(CASE WHEN resolution_date IS NOT NULL
                THEN TIMESTAMPDIFF(DAY, creation, resolution_date) END) as avg_days,
            AVG(CASE WHEN status IN ('Resolved', 'Closed') AND sla_status != 'Breached'
                THEN 100 ELSE 0 END) as sla_compliance,
            AVG(satisfaction_rating) as satisfaction
        FROM `tabGrievance`
        WHERE 1=1 {conditions}
        GROUP BY category
        ORDER BY total DESC
    """, as_dict=True)

def get_chart(data):
    return {
        "data": {
            "labels": [d.category for d in data],
            "datasets": [
                {"name": "Total", "values": [d.total for d in data]},
                {"name": "Open", "values": [d.open for d in data]}
            ]
        },
        "type": "bar"
    }

def get_summary(data):
    total = sum(d.total for d in data)
    open_count = sum(d.open for d in data)
    avg_satisfaction = sum(d.satisfaction or 0 for d in data) / len(data) if data else 0

    return [
        {"label": "Total Grievances", "value": total, "indicator": "Blue"},
        {"label": "Open", "value": open_count, "indicator": "Orange" if open_count > 10 else "Green"},
        {"label": "Avg Satisfaction", "value": f"{avg_satisfaction:.1f}/5", "indicator": "Green" if avg_satisfaction >= 4 else "Red"}
    ]
```

### 4.2 Faculty Feedback Report

```python
# university_erp/university_erp/feedback/report/faculty_feedback_report/faculty_feedback_report.py

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Faculty", "fieldname": "instructor", "fieldtype": "Link", "options": "Faculty Member", "width": 200},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": "Courses", "fieldname": "courses", "fieldtype": "Int", "width": 80},
        {"label": "Responses", "fieldname": "responses", "fieldtype": "Int", "width": 100},
        {"label": "Avg Score", "fieldname": "avg_score", "fieldtype": "Percent", "width": 100},
        {"label": "Content", "fieldname": "content_score", "fieldtype": "Percent", "width": 90},
        {"label": "Teaching", "fieldname": "teaching_score", "fieldtype": "Percent", "width": 90},
        {"label": "NPS", "fieldname": "nps", "fieldtype": "Float", "width": 80}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("academic_term"):
        conditions += f" AND ff.academic_term = '{filters.get('academic_term')}'"
    if filters.get("department"):
        conditions += f" AND fm.department = '{filters.get('department')}'"

    return frappe.db.sql(f"""
        SELECT
            fr.instructor,
            fm.department,
            COUNT(DISTINCT fr.course) as courses,
            COUNT(*) as responses,
            AVG(fr.overall_score) as avg_score,
            AVG(CASE WHEN fss.section_name LIKE '%Content%' THEN fss.score END) as content_score,
            AVG(CASE WHEN fss.section_name LIKE '%Teaching%' THEN fss.score END) as teaching_score,
            (SUM(CASE WHEN fr.nps_category = 'Promoter' THEN 1 ELSE 0 END) -
             SUM(CASE WHEN fr.nps_category = 'Detractor' THEN 1 ELSE 0 END)) * 100.0 / COUNT(*) as nps
        FROM `tabFeedback Response` fr
        JOIN `tabFeedback Form` ff ON fr.feedback_form = ff.name
        JOIN `tabFaculty Member` fm ON fr.instructor = fm.name
        LEFT JOIN `tabFeedback Section Score` fss ON fss.parent = fr.name
        WHERE fr.status = 'Valid'
        AND ff.form_type = 'Course Feedback'
        {conditions}
        GROUP BY fr.instructor, fm.department
        ORDER BY avg_score DESC
    """, as_dict=True)

def get_chart(data):
    return {
        "data": {
            "labels": [d.instructor[:20] for d in data[:10]],
            "datasets": [
                {"name": "Overall Score", "values": [d.avg_score or 0 for d in data[:10]]},
                {"name": "Teaching Score", "values": [d.teaching_score or 0 for d in data[:10]]}
            ]
        },
        "type": "bar"
    }
```

---

## 5. Portal Integration

### 5.1 Student Grievance Page

```python
# university_erp/www/student-portal/grievances.py

import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.AuthenticationError)

    student = frappe.db.get_value("Student", {"user": frappe.session.user})
    if not student:
        frappe.throw(_("Student profile not found"))

    context.no_cache = 1
    context.student = student

    # Get grievance types
    context.grievance_types = frappe.get_all("Grievance Type",
        filters={"is_active": 1},
        fields=["name", "grievance_type_name", "category", "allow_anonymous"]
    )

    # Get my grievances
    context.my_grievances = frappe.get_all("Grievance",
        filters={"student": student},
        fields=["name", "subject", "category", "status", "priority",
               "creation", "expected_resolution_date", "sla_status"],
        order_by="creation desc",
        limit=20
    )

    # Stats
    context.stats = {
        "total": len(context.my_grievances),
        "open": len([g for g in context.my_grievances if g.status not in ["Resolved", "Closed"]]),
        "resolved": len([g for g in context.my_grievances if g.status in ["Resolved", "Closed"]])
    }
```

### 5.2 Feedback Portal Page

```python
# university_erp/www/student-portal/feedback.py

import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.AuthenticationError)

    student = frappe.db.get_value("Student", {"user": frappe.session.user})
    if not student:
        frappe.throw(_("Student profile not found"))

    context.no_cache = 1
    context.student = student

    # Get pending feedback forms
    context.pending_forms = get_pending_forms(student)

    # Get submitted responses
    context.submitted = frappe.get_all("Feedback Response",
        filters={"student": student, "status": ["in", ["Submitted", "Valid"]]},
        fields=["name", "feedback_form", "submission_datetime"],
        order_by="submission_datetime desc"
    )

    # Enrich with form details
    for resp in context.submitted:
        form = frappe.get_cached_doc("Feedback Form", resp.feedback_form)
        resp.form_title = form.form_title
        resp.form_type = form.form_type


def get_pending_forms(student):
    """Get feedback forms pending for this student"""
    # Get student's enrollments
    enrollments = frappe.get_all("Course Enrollment",
        filters={"student": student},
        fields=["course", "program"]
    )

    courses = [e.course for e in enrollments]
    programs = list(set(e.program for e in enrollments if e.program))

    # Get active forms
    forms = frappe.get_all("Feedback Form",
        filters={
            "status": "Active",
            "target_audience": "Students"
        },
        fields=["name", "form_title", "form_type", "end_date", "is_mandatory"]
    )

    pending = []
    for form in forms:
        form_doc = frappe.get_cached_doc("Feedback Form", form.name)

        # Check if form applies to this student
        applies = False
        if not form_doc.courses and not form_doc.programs:
            applies = True
        elif form_doc.courses:
            form_courses = [c.course for c in form_doc.courses]
            applies = any(c in form_courses for c in courses)
        elif form_doc.programs:
            form_programs = [p.program for p in form_doc.programs]
            applies = any(p in form_programs for p in programs)

        if not applies:
            continue

        # Check if already submitted
        submitted = frappe.db.exists("Feedback Response", {
            "feedback_form": form.name,
            "student": student,
            "status": ["in", ["Submitted", "Valid"]]
        })

        if not submitted:
            pending.append(form)

    return pending
```

---

## 6. Implementation Checklist

### Week 1: Grievance Core
- [ ] Create Grievance DocType
- [ ] Create Grievance Type DocType
- [ ] Create Grievance Committee DocType
- [ ] Implement GrievanceManager class
- [ ] Create submission workflow
- [ ] Implement auto-assignment
- [ ] Add acknowledgment notifications

### Week 2: Grievance Features
- [ ] Implement escalation workflow
- [ ] Create SLA monitoring
- [ ] Add communication logging
- [ ] Build resolution workflow
- [ ] Implement satisfaction feedback
- [ ] Create grievance tracking page
- [ ] Add anonymous submission support

### Week 3: Feedback System
- [ ] Create Feedback Form DocType
- [ ] Create Feedback Question structures
- [ ] Create Feedback Response DocType
- [ ] Implement FeedbackManager class
- [ ] Build form builder interface
- [ ] Create response submission API
- [ ] Implement score calculation

### Week 4: Reports & Integration
- [ ] Create Grievance Summary report
- [ ] Create Faculty Feedback report
- [ ] Create Course Feedback report
- [ ] Build feedback analysis dashboard
- [ ] Create Suggestion Box module
- [ ] Integrate with student portal
- [ ] Add notification triggers

---

## 7. Security & Privacy

### 7.1 Data Protection
- Anonymous submissions stored without identifiable info
- Feedback data aggregated for reports
- Individual responses visible only to authorized roles
- Grievance access restricted to involved parties

### 7.2 Permission Matrix

| Role | Grievance | Feedback Form | Feedback Response |
|------|-----------|---------------|-------------------|
| Student | Create Own, Read Own | Read Active | Create, Read Own |
| Faculty | Create Own, Read Own | Create, Read | Read (aggregated) |
| Grievance Officer | Full Access | Read | Read (aggregated) |
| Academic Admin | Read All | Full Access | Read All |
| HOD | Read Dept | Create, Read | Read Dept |

---

## 8. Email Templates

### 8.1 Grievance Acknowledgment
```html
<h3>Grievance Received</h3>
<p>Dear {{ grievance.student_name or "Complainant" }},</p>
<p>Your grievance has been received and registered with the following details:</p>
<ul>
    <li><strong>Tracking ID:</strong> {{ tracking_id }}</li>
    <li><strong>Subject:</strong> {{ grievance.subject }}</li>
    <li><strong>Category:</strong> {{ grievance.category }}</li>
    <li><strong>Expected Resolution:</strong> {{ expected_resolution }}</li>
</ul>
<p>You can track the status of your grievance using the tracking ID above.</p>
```

### 8.2 Feedback Reminder
```html
<h3>Feedback Pending</h3>
<p>Dear Student,</p>
<p>You have pending feedback to submit:</p>
<ul>
    <li><strong>{{ form.form_title }}</strong></li>
    <li>Due Date: {{ form.end_date }}</li>
</ul>
<p>Your feedback is valuable for improving our academic programs.</p>
<a href="{{ feedback_link }}">Submit Feedback Now</a>
```

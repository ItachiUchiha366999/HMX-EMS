# Phase 17: Advanced Examination & Question Bank System

## Overview

This phase implements a comprehensive examination management system with question bank, online examination platform, answer sheet tracking, and automated evaluation features.

**Duration:** 6 Weeks
**Priority:** High
**Dependencies:** Phase 4 (Academic Module), Phase 6 (Examination Base)

## Gap Analysis Reference

From IMPLEMENTATION_GAP_ANALYSIS.md:
- Question Bank DocType: 0% (Missing)
- Question Paper Generator: 0% (Missing)
- Answer Sheet Tracking: 0% (Missing)
- Online Examination Platform: 0% (Missing)
- Internal Assessment tracking: 55% (Partial)
- Practical/Viva Exam scheduling: 0% (Missing)

---

## 1. Core DocTypes

### 1.1 Question Bank

```json
{
  "doctype": "DocType",
  "name": "Question Bank",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "QB-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "question_text",
      "fieldtype": "Text Editor",
      "label": "Question",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "question_type",
      "fieldtype": "Select",
      "label": "Question Type",
      "options": "\nMultiple Choice (MCQ)\nMultiple Select (MSQ)\nTrue/False\nShort Answer\nLong Answer\nNumerical\nFill in the Blanks\nMatch the Following\nCase Study\nDiagram Based",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "unit",
      "fieldtype": "Link",
      "label": "Unit/Topic",
      "options": "Course Unit"
    },
    {
      "fieldname": "section_break_difficulty",
      "fieldtype": "Section Break",
      "label": "Classification"
    },
    {
      "fieldname": "difficulty_level",
      "fieldtype": "Select",
      "label": "Difficulty Level",
      "options": "\nEasy\nMedium\nHard\nVery Hard",
      "reqd": 1
    },
    {
      "fieldname": "blooms_taxonomy",
      "fieldtype": "Select",
      "label": "Bloom's Taxonomy Level",
      "options": "\nRemember (L1)\nUnderstand (L2)\nApply (L3)\nAnalyze (L4)\nEvaluate (L5)\nCreate (L6)",
      "reqd": 1
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "course_outcome",
      "fieldtype": "Link",
      "label": "Course Outcome (CO)",
      "options": "Course Outcome"
    },
    {
      "fieldname": "program_outcome",
      "fieldtype": "Link",
      "label": "Program Outcome (PO)",
      "options": "Program Outcome"
    },
    {
      "fieldname": "marks",
      "fieldtype": "Int",
      "label": "Default Marks",
      "reqd": 1
    },
    {
      "fieldname": "section_break_options",
      "fieldtype": "Section Break",
      "label": "Answer Options",
      "depends_on": "eval:in_list(['Multiple Choice (MCQ)', 'Multiple Select (MSQ)', 'True/False', 'Match the Following'], doc.question_type)"
    },
    {
      "fieldname": "options",
      "fieldtype": "Table",
      "label": "Options",
      "options": "Question Option"
    },
    {
      "fieldname": "section_break_answer",
      "fieldtype": "Section Break",
      "label": "Answer/Solution"
    },
    {
      "fieldname": "correct_answer",
      "fieldtype": "Text Editor",
      "label": "Correct Answer/Model Answer"
    },
    {
      "fieldname": "answer_explanation",
      "fieldtype": "Text Editor",
      "label": "Answer Explanation"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "negative_marking",
      "fieldtype": "Check",
      "label": "Enable Negative Marking"
    },
    {
      "fieldname": "negative_marks",
      "fieldtype": "Float",
      "label": "Negative Marks",
      "depends_on": "negative_marking"
    },
    {
      "fieldname": "partial_marking",
      "fieldtype": "Check",
      "label": "Allow Partial Marking"
    },
    {
      "fieldname": "section_break_media",
      "fieldtype": "Section Break",
      "label": "Media & Attachments"
    },
    {
      "fieldname": "question_image",
      "fieldtype": "Attach Image",
      "label": "Question Image"
    },
    {
      "fieldname": "question_diagram",
      "fieldtype": "Attach",
      "label": "Diagram/Figure"
    },
    {
      "fieldname": "audio_file",
      "fieldtype": "Attach",
      "label": "Audio File (for listening tests)"
    },
    {
      "fieldname": "section_break_meta",
      "fieldtype": "Section Break",
      "label": "Metadata"
    },
    {
      "fieldname": "created_by_faculty",
      "fieldtype": "Link",
      "label": "Created By",
      "options": "Faculty Member",
      "read_only": 1
    },
    {
      "fieldname": "reviewed_by",
      "fieldtype": "Link",
      "label": "Reviewed By",
      "options": "Faculty Member"
    },
    {
      "fieldname": "column_break_4",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Draft\nPending Review\nApproved\nRejected\nRetired",
      "default": "Draft"
    },
    {
      "fieldname": "times_used",
      "fieldtype": "Int",
      "label": "Times Used",
      "read_only": 1,
      "default": 0
    },
    {
      "fieldname": "last_used_date",
      "fieldtype": "Date",
      "label": "Last Used Date",
      "read_only": 1
    },
    {
      "fieldname": "average_score_percentage",
      "fieldtype": "Percent",
      "label": "Average Score %",
      "read_only": 1
    },
    {
      "fieldname": "section_break_tags",
      "fieldtype": "Section Break",
      "label": "Tags & Keywords"
    },
    {
      "fieldname": "tags",
      "fieldtype": "Table MultiSelect",
      "label": "Tags",
      "options": "Question Tag Link"
    },
    {
      "fieldname": "keywords",
      "fieldtype": "Small Text",
      "label": "Keywords (comma separated)"
    }
  ],
  "permissions": [
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1},
    {"role": "HOD", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Examination Controller", "read": 1, "write": 1}
  ]
}
```

### 1.2 Question Option (Child Table)

```json
{
  "doctype": "DocType",
  "name": "Question Option",
  "module": "University ERP",
  "istable": 1,
  "fields": [
    {
      "fieldname": "option_label",
      "fieldtype": "Data",
      "label": "Option Label",
      "in_list_view": 1,
      "columns": 1
    },
    {
      "fieldname": "option_text",
      "fieldtype": "Text Editor",
      "label": "Option Text",
      "in_list_view": 1,
      "columns": 4
    },
    {
      "fieldname": "option_image",
      "fieldtype": "Attach Image",
      "label": "Option Image"
    },
    {
      "fieldname": "is_correct",
      "fieldtype": "Check",
      "label": "Is Correct",
      "in_list_view": 1,
      "columns": 1
    },
    {
      "fieldname": "partial_marks_percentage",
      "fieldtype": "Percent",
      "label": "Partial Marks %",
      "description": "For MSQ - percentage of marks for this option"
    },
    {
      "fieldname": "match_with",
      "fieldtype": "Data",
      "label": "Match With",
      "description": "For Match the Following type"
    }
  ]
}
```

### 1.3 Question Paper Template

```json
{
  "doctype": "DocType",
  "name": "Question Paper Template",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "QPT-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "template_name",
      "fieldtype": "Data",
      "label": "Template Name",
      "reqd": 1,
      "unique": 1
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1
    },
    {
      "fieldname": "exam_type",
      "fieldtype": "Select",
      "label": "Exam Type",
      "options": "\nMidterm\nEnd Semester\nQuiz\nClass Test\nRe-examination\nSupplementary\nPractical\nViva",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "total_marks",
      "fieldtype": "Int",
      "label": "Total Marks",
      "reqd": 1
    },
    {
      "fieldname": "duration_minutes",
      "fieldtype": "Int",
      "label": "Duration (Minutes)",
      "reqd": 1
    },
    {
      "fieldname": "passing_percentage",
      "fieldtype": "Percent",
      "label": "Passing Percentage",
      "default": 40
    },
    {
      "fieldname": "section_break_structure",
      "fieldtype": "Section Break",
      "label": "Paper Structure"
    },
    {
      "fieldname": "sections",
      "fieldtype": "Table",
      "label": "Sections",
      "options": "Question Paper Section"
    },
    {
      "fieldname": "section_break_distribution",
      "fieldtype": "Section Break",
      "label": "Distribution Rules"
    },
    {
      "fieldname": "unit_wise_distribution",
      "fieldtype": "Table",
      "label": "Unit-wise Distribution",
      "options": "Unit Distribution Rule"
    },
    {
      "fieldname": "bloom_distribution",
      "fieldtype": "Table",
      "label": "Bloom's Taxonomy Distribution",
      "options": "Bloom Distribution Rule"
    },
    {
      "fieldname": "section_break_settings",
      "fieldtype": "Section Break",
      "label": "Settings"
    },
    {
      "fieldname": "shuffle_questions",
      "fieldtype": "Check",
      "label": "Shuffle Questions"
    },
    {
      "fieldname": "shuffle_options",
      "fieldtype": "Check",
      "label": "Shuffle Options"
    },
    {
      "fieldname": "show_calculator",
      "fieldtype": "Check",
      "label": "Show Calculator"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "allow_review",
      "fieldtype": "Check",
      "label": "Allow Review Before Submit"
    },
    {
      "fieldname": "show_marks_per_question",
      "fieldtype": "Check",
      "label": "Show Marks Per Question",
      "default": 1
    },
    {
      "fieldname": "instructions",
      "fieldtype": "Text Editor",
      "label": "Instructions"
    }
  ],
  "permissions": [
    {"role": "Examination Controller", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "HOD", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.4 Question Paper Section (Child Table)

```json
{
  "doctype": "DocType",
  "name": "Question Paper Section",
  "module": "University ERP",
  "istable": 1,
  "fields": [
    {
      "fieldname": "section_name",
      "fieldtype": "Data",
      "label": "Section Name",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "question_type",
      "fieldtype": "Select",
      "label": "Question Type",
      "options": "\nMultiple Choice (MCQ)\nMultiple Select (MSQ)\nTrue/False\nShort Answer\nLong Answer\nNumerical\nFill in the Blanks\nCase Study",
      "in_list_view": 1
    },
    {
      "fieldname": "total_questions",
      "fieldtype": "Int",
      "label": "Total Questions",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "questions_to_attempt",
      "fieldtype": "Int",
      "label": "Questions to Attempt",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "marks_per_question",
      "fieldtype": "Float",
      "label": "Marks Per Question",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "section_marks",
      "fieldtype": "Float",
      "label": "Section Total Marks",
      "read_only": 1
    },
    {
      "fieldname": "compulsory",
      "fieldtype": "Check",
      "label": "Compulsory Section"
    },
    {
      "fieldname": "negative_marking",
      "fieldtype": "Check",
      "label": "Negative Marking"
    },
    {
      "fieldname": "negative_marks",
      "fieldtype": "Float",
      "label": "Negative Marks"
    },
    {
      "fieldname": "section_instructions",
      "fieldtype": "Small Text",
      "label": "Section Instructions"
    }
  ]
}
```

### 1.5 Generated Question Paper

```json
{
  "doctype": "DocType",
  "name": "Generated Question Paper",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "QP-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "paper_title",
      "fieldtype": "Data",
      "label": "Paper Title",
      "reqd": 1
    },
    {
      "fieldname": "examination",
      "fieldtype": "Link",
      "label": "Examination",
      "options": "Examination"
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "template",
      "fieldtype": "Link",
      "label": "Template Used",
      "options": "Question Paper Template"
    },
    {
      "fieldname": "academic_year",
      "fieldtype": "Link",
      "label": "Academic Year",
      "options": "Academic Year",
      "reqd": 1
    },
    {
      "fieldname": "academic_term",
      "fieldtype": "Link",
      "label": "Academic Term",
      "options": "Academic Term"
    },
    {
      "fieldname": "section_break_details",
      "fieldtype": "Section Break",
      "label": "Paper Details"
    },
    {
      "fieldname": "total_marks",
      "fieldtype": "Int",
      "label": "Total Marks",
      "reqd": 1
    },
    {
      "fieldname": "duration_minutes",
      "fieldtype": "Int",
      "label": "Duration (Minutes)",
      "reqd": 1
    },
    {
      "fieldname": "exam_date",
      "fieldtype": "Date",
      "label": "Exam Date"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "set_code",
      "fieldtype": "Data",
      "label": "Set Code",
      "description": "A, B, C, D for multiple sets"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Draft\nReady for Review\nApproved\nLocked\nUsed",
      "default": "Draft"
    },
    {
      "fieldname": "section_break_questions",
      "fieldtype": "Section Break",
      "label": "Questions"
    },
    {
      "fieldname": "paper_sections",
      "fieldtype": "Table",
      "label": "Paper Sections",
      "options": "Question Paper Content Section"
    },
    {
      "fieldname": "section_break_approval",
      "fieldtype": "Section Break",
      "label": "Approval"
    },
    {
      "fieldname": "created_by",
      "fieldtype": "Link",
      "label": "Created By",
      "options": "Faculty Member",
      "read_only": 1
    },
    {
      "fieldname": "reviewed_by",
      "fieldtype": "Link",
      "label": "Reviewed By",
      "options": "Faculty Member"
    },
    {
      "fieldname": "approved_by",
      "fieldtype": "Link",
      "label": "Approved By",
      "options": "User"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "review_date",
      "fieldtype": "Datetime",
      "label": "Review Date"
    },
    {
      "fieldname": "approval_date",
      "fieldtype": "Datetime",
      "label": "Approval Date"
    },
    {
      "fieldname": "review_comments",
      "fieldtype": "Text",
      "label": "Review Comments"
    },
    {
      "fieldname": "section_break_print",
      "fieldtype": "Section Break",
      "label": "Print Settings"
    },
    {
      "fieldname": "header_logo",
      "fieldtype": "Attach Image",
      "label": "Header Logo"
    },
    {
      "fieldname": "university_name",
      "fieldtype": "Data",
      "label": "University Name"
    },
    {
      "fieldname": "department_name",
      "fieldtype": "Data",
      "label": "Department Name"
    },
    {
      "fieldname": "instructions",
      "fieldtype": "Text Editor",
      "label": "Instructions"
    }
  ],
  "permissions": [
    {"role": "Examination Controller", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1},
    {"role": "HOD", "read": 1, "write": 1, "create": 1, "delete": 1}
  ]
}
```

### 1.6 Question Paper Content Section (Child Table)

```json
{
  "doctype": "DocType",
  "name": "Question Paper Content Section",
  "module": "University ERP",
  "istable": 1,
  "fields": [
    {
      "fieldname": "section_name",
      "fieldtype": "Data",
      "label": "Section",
      "in_list_view": 1
    },
    {
      "fieldname": "section_instructions",
      "fieldtype": "Small Text",
      "label": "Instructions"
    },
    {
      "fieldname": "questions",
      "fieldtype": "Table",
      "label": "Questions",
      "options": "Question Paper Question Item"
    }
  ]
}
```

### 1.7 Online Examination

```json
{
  "doctype": "DocType",
  "name": "Online Examination",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "OE-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "exam_title",
      "fieldtype": "Data",
      "label": "Examination Title",
      "reqd": 1
    },
    {
      "fieldname": "exam_type",
      "fieldtype": "Select",
      "label": "Exam Type",
      "options": "\nMidterm\nEnd Semester\nQuiz\nClass Test\nPractice Test\nMock Test",
      "reqd": 1
    },
    {
      "fieldname": "question_paper",
      "fieldtype": "Link",
      "label": "Question Paper",
      "options": "Generated Question Paper",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1,
      "fetch_from": "question_paper.course"
    },
    {
      "fieldname": "student_group",
      "fieldtype": "Link",
      "label": "Student Group",
      "options": "Student Group"
    },
    {
      "fieldname": "program",
      "fieldtype": "Link",
      "label": "Program",
      "options": "Program"
    },
    {
      "fieldname": "section_break_schedule",
      "fieldtype": "Section Break",
      "label": "Schedule"
    },
    {
      "fieldname": "start_datetime",
      "fieldtype": "Datetime",
      "label": "Start Date & Time",
      "reqd": 1
    },
    {
      "fieldname": "end_datetime",
      "fieldtype": "Datetime",
      "label": "End Date & Time",
      "reqd": 1
    },
    {
      "fieldname": "duration_minutes",
      "fieldtype": "Int",
      "label": "Duration (Minutes)",
      "reqd": 1,
      "fetch_from": "question_paper.duration_minutes"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "late_submission_minutes",
      "fieldtype": "Int",
      "label": "Grace Period (Minutes)",
      "default": 0
    },
    {
      "fieldname": "auto_submit",
      "fieldtype": "Check",
      "label": "Auto Submit on Time Expiry",
      "default": 1
    },
    {
      "fieldname": "section_break_settings",
      "fieldtype": "Section Break",
      "label": "Exam Settings"
    },
    {
      "fieldname": "shuffle_questions",
      "fieldtype": "Check",
      "label": "Shuffle Questions for Each Student"
    },
    {
      "fieldname": "shuffle_options",
      "fieldtype": "Check",
      "label": "Shuffle Options"
    },
    {
      "fieldname": "one_question_per_page",
      "fieldtype": "Check",
      "label": "One Question Per Page"
    },
    {
      "fieldname": "allow_back_navigation",
      "fieldtype": "Check",
      "label": "Allow Back Navigation",
      "default": 1
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "show_timer",
      "fieldtype": "Check",
      "label": "Show Timer",
      "default": 1
    },
    {
      "fieldname": "show_question_palette",
      "fieldtype": "Check",
      "label": "Show Question Palette",
      "default": 1
    },
    {
      "fieldname": "allow_review_marking",
      "fieldtype": "Check",
      "label": "Allow Mark for Review",
      "default": 1
    },
    {
      "fieldname": "show_calculator",
      "fieldtype": "Check",
      "label": "Show Calculator"
    },
    {
      "fieldname": "section_break_proctoring",
      "fieldtype": "Section Break",
      "label": "Proctoring Settings"
    },
    {
      "fieldname": "enable_proctoring",
      "fieldtype": "Check",
      "label": "Enable Proctoring"
    },
    {
      "fieldname": "webcam_required",
      "fieldtype": "Check",
      "label": "Webcam Required",
      "depends_on": "enable_proctoring"
    },
    {
      "fieldname": "capture_snapshots",
      "fieldtype": "Check",
      "label": "Capture Random Snapshots",
      "depends_on": "enable_proctoring"
    },
    {
      "fieldname": "snapshot_interval_seconds",
      "fieldtype": "Int",
      "label": "Snapshot Interval (Seconds)",
      "depends_on": "capture_snapshots",
      "default": 60
    },
    {
      "fieldname": "column_break_4",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "full_screen_mode",
      "fieldtype": "Check",
      "label": "Force Full Screen Mode"
    },
    {
      "fieldname": "disable_copy_paste",
      "fieldtype": "Check",
      "label": "Disable Copy/Paste",
      "default": 1
    },
    {
      "fieldname": "disable_right_click",
      "fieldtype": "Check",
      "label": "Disable Right Click",
      "default": 1
    },
    {
      "fieldname": "tab_switch_warning",
      "fieldtype": "Check",
      "label": "Warn on Tab Switch",
      "default": 1
    },
    {
      "fieldname": "max_tab_switches",
      "fieldtype": "Int",
      "label": "Max Tab Switches Allowed",
      "default": 3
    },
    {
      "fieldname": "section_break_access",
      "fieldtype": "Section Break",
      "label": "Access Control"
    },
    {
      "fieldname": "requires_password",
      "fieldtype": "Check",
      "label": "Requires Password"
    },
    {
      "fieldname": "exam_password",
      "fieldtype": "Password",
      "label": "Exam Password",
      "depends_on": "requires_password"
    },
    {
      "fieldname": "ip_restriction",
      "fieldtype": "Check",
      "label": "Restrict by IP"
    },
    {
      "fieldname": "allowed_ip_ranges",
      "fieldtype": "Small Text",
      "label": "Allowed IP Ranges",
      "depends_on": "ip_restriction",
      "description": "One IP or range per line (e.g., 192.168.1.0/24)"
    },
    {
      "fieldname": "column_break_5",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "max_attempts",
      "fieldtype": "Int",
      "label": "Maximum Attempts",
      "default": 1
    },
    {
      "fieldname": "show_result_immediately",
      "fieldtype": "Check",
      "label": "Show Result Immediately"
    },
    {
      "fieldname": "show_correct_answers",
      "fieldtype": "Check",
      "label": "Show Correct Answers After Submit"
    },
    {
      "fieldname": "section_break_eligible",
      "fieldtype": "Section Break",
      "label": "Eligible Students"
    },
    {
      "fieldname": "eligible_students",
      "fieldtype": "Table",
      "label": "Eligible Students",
      "options": "Online Exam Student"
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
      "options": "Draft\nScheduled\nLive\nCompleted\nCancelled",
      "default": "Draft"
    },
    {
      "fieldname": "total_registered",
      "fieldtype": "Int",
      "label": "Total Registered",
      "read_only": 1
    },
    {
      "fieldname": "total_appeared",
      "fieldtype": "Int",
      "label": "Total Appeared",
      "read_only": 1
    },
    {
      "fieldname": "total_submitted",
      "fieldtype": "Int",
      "label": "Total Submitted",
      "read_only": 1
    }
  ],
  "permissions": [
    {"role": "Examination Controller", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.8 Student Exam Attempt

```json
{
  "doctype": "DocType",
  "name": "Student Exam Attempt",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "SEA-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "online_examination",
      "fieldtype": "Link",
      "label": "Online Examination",
      "options": "Online Examination",
      "reqd": 1
    },
    {
      "fieldname": "student",
      "fieldtype": "Link",
      "label": "Student",
      "options": "Student",
      "reqd": 1
    },
    {
      "fieldname": "attempt_number",
      "fieldtype": "Int",
      "label": "Attempt Number",
      "default": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "start_time",
      "fieldtype": "Datetime",
      "label": "Start Time"
    },
    {
      "fieldname": "end_time",
      "fieldtype": "Datetime",
      "label": "End Time"
    },
    {
      "fieldname": "time_taken_minutes",
      "fieldtype": "Int",
      "label": "Time Taken (Minutes)",
      "read_only": 1
    },
    {
      "fieldname": "section_break_answers",
      "fieldtype": "Section Break",
      "label": "Answers"
    },
    {
      "fieldname": "answers",
      "fieldtype": "Table",
      "label": "Answers",
      "options": "Student Answer"
    },
    {
      "fieldname": "section_break_scoring",
      "fieldtype": "Section Break",
      "label": "Scoring"
    },
    {
      "fieldname": "total_questions",
      "fieldtype": "Int",
      "label": "Total Questions"
    },
    {
      "fieldname": "attempted",
      "fieldtype": "Int",
      "label": "Attempted"
    },
    {
      "fieldname": "correct",
      "fieldtype": "Int",
      "label": "Correct"
    },
    {
      "fieldname": "incorrect",
      "fieldtype": "Int",
      "label": "Incorrect"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "marks_obtained",
      "fieldtype": "Float",
      "label": "Marks Obtained"
    },
    {
      "fieldname": "total_marks",
      "fieldtype": "Float",
      "label": "Total Marks"
    },
    {
      "fieldname": "percentage",
      "fieldtype": "Percent",
      "label": "Percentage"
    },
    {
      "fieldname": "negative_marks_applied",
      "fieldtype": "Float",
      "label": "Negative Marks Applied"
    },
    {
      "fieldname": "section_break_proctoring",
      "fieldtype": "Section Break",
      "label": "Proctoring Data"
    },
    {
      "fieldname": "proctoring_snapshots",
      "fieldtype": "Table",
      "label": "Proctoring Snapshots",
      "options": "Proctoring Snapshot"
    },
    {
      "fieldname": "tab_switches",
      "fieldtype": "Int",
      "label": "Tab Switches Detected",
      "default": 0
    },
    {
      "fieldname": "proctoring_violations",
      "fieldtype": "Int",
      "label": "Proctoring Violations",
      "default": 0
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "ip_address",
      "fieldtype": "Data",
      "label": "IP Address",
      "read_only": 1
    },
    {
      "fieldname": "browser_info",
      "fieldtype": "Small Text",
      "label": "Browser Info",
      "read_only": 1
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
      "options": "Not Started\nIn Progress\nSubmitted\nAuto Submitted\nEvaluated\nDisqualified",
      "default": "Not Started"
    },
    {
      "fieldname": "submit_type",
      "fieldtype": "Select",
      "label": "Submit Type",
      "options": "\nManual\nAuto (Time Expired)\nAuto (Violation)",
      "read_only": 1
    },
    {
      "fieldname": "column_break_4",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "evaluated_by",
      "fieldtype": "Link",
      "label": "Evaluated By",
      "options": "User"
    },
    {
      "fieldname": "evaluation_date",
      "fieldtype": "Datetime",
      "label": "Evaluation Date"
    },
    {
      "fieldname": "remarks",
      "fieldtype": "Text",
      "label": "Remarks"
    }
  ],
  "permissions": [
    {"role": "Student", "read": 1, "if_owner": 1},
    {"role": "Faculty Member", "read": 1, "write": 1},
    {"role": "Examination Controller", "read": 1, "write": 1}
  ]
}
```

### 1.9 Answer Sheet Tracking

```json
{
  "doctype": "DocType",
  "name": "Answer Sheet",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "AS-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "examination",
      "fieldtype": "Link",
      "label": "Examination",
      "options": "Examination",
      "reqd": 1
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1
    },
    {
      "fieldname": "student",
      "fieldtype": "Link",
      "label": "Student",
      "options": "Student",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "roll_number",
      "fieldtype": "Data",
      "label": "Roll Number",
      "fetch_from": "student.roll_number"
    },
    {
      "fieldname": "seat_number",
      "fieldtype": "Data",
      "label": "Seat Number"
    },
    {
      "fieldname": "barcode",
      "fieldtype": "Data",
      "label": "Barcode/QR Code",
      "unique": 1
    },
    {
      "fieldname": "section_break_collection",
      "fieldtype": "Section Break",
      "label": "Collection"
    },
    {
      "fieldname": "collected_by",
      "fieldtype": "Link",
      "label": "Collected By",
      "options": "User"
    },
    {
      "fieldname": "collection_datetime",
      "fieldtype": "Datetime",
      "label": "Collection Date & Time"
    },
    {
      "fieldname": "total_pages",
      "fieldtype": "Int",
      "label": "Total Pages"
    },
    {
      "fieldname": "additional_sheets",
      "fieldtype": "Int",
      "label": "Additional Sheets Used",
      "default": 0
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "exam_center",
      "fieldtype": "Link",
      "label": "Exam Center",
      "options": "Exam Center"
    },
    {
      "fieldname": "room",
      "fieldtype": "Link",
      "label": "Room",
      "options": "Room"
    },
    {
      "fieldname": "invigilator",
      "fieldtype": "Link",
      "label": "Invigilator",
      "options": "Faculty Member"
    },
    {
      "fieldname": "section_break_evaluation",
      "fieldtype": "Section Break",
      "label": "Evaluation Tracking"
    },
    {
      "fieldname": "assigned_to",
      "fieldtype": "Link",
      "label": "Assigned Evaluator",
      "options": "Faculty Member"
    },
    {
      "fieldname": "assignment_date",
      "fieldtype": "Datetime",
      "label": "Assignment Date"
    },
    {
      "fieldname": "evaluation_started",
      "fieldtype": "Datetime",
      "label": "Evaluation Started"
    },
    {
      "fieldname": "evaluation_completed",
      "fieldtype": "Datetime",
      "label": "Evaluation Completed"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "moderated_by",
      "fieldtype": "Link",
      "label": "Moderated By",
      "options": "Faculty Member"
    },
    {
      "fieldname": "moderation_date",
      "fieldtype": "Datetime",
      "label": "Moderation Date"
    },
    {
      "fieldname": "section_break_scoring",
      "fieldtype": "Section Break",
      "label": "Scoring"
    },
    {
      "fieldname": "question_scores",
      "fieldtype": "Table",
      "label": "Question-wise Scores",
      "options": "Answer Sheet Score"
    },
    {
      "fieldname": "total_marks",
      "fieldtype": "Float",
      "label": "Total Marks Possible"
    },
    {
      "fieldname": "marks_obtained",
      "fieldtype": "Float",
      "label": "Marks Obtained"
    },
    {
      "fieldname": "percentage",
      "fieldtype": "Percent",
      "label": "Percentage"
    },
    {
      "fieldname": "grade",
      "fieldtype": "Data",
      "label": "Grade"
    },
    {
      "fieldname": "column_break_4",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "marks_after_moderation",
      "fieldtype": "Float",
      "label": "Marks After Moderation"
    },
    {
      "fieldname": "grace_marks",
      "fieldtype": "Float",
      "label": "Grace Marks Applied",
      "default": 0
    },
    {
      "fieldname": "section_break_scanned",
      "fieldtype": "Section Break",
      "label": "Scanned Copy"
    },
    {
      "fieldname": "scanned_copy",
      "fieldtype": "Attach",
      "label": "Scanned Copy (PDF)"
    },
    {
      "fieldname": "scan_date",
      "fieldtype": "Datetime",
      "label": "Scan Date"
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
      "options": "Collected\nIn Transit\nReceived at Evaluation Center\nAssigned for Evaluation\nEvaluation In Progress\nEvaluated\nPending Moderation\nModerated\nResult Published\nRevaluation Requested\nRevaluation Done",
      "default": "Collected"
    },
    {
      "fieldname": "column_break_5",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "current_location",
      "fieldtype": "Data",
      "label": "Current Location"
    },
    {
      "fieldname": "tracking_history",
      "fieldtype": "Table",
      "label": "Tracking History",
      "options": "Answer Sheet Tracking Log"
    }
  ],
  "permissions": [
    {"role": "Examination Controller", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Faculty Member", "read": 1, "write": 1}
  ]
}
```

### 1.10 Practical Examination

```json
{
  "doctype": "DocType",
  "name": "Practical Examination",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "PE-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "examination",
      "fieldtype": "Link",
      "label": "Main Examination",
      "options": "Examination"
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1
    },
    {
      "fieldname": "practical_type",
      "fieldtype": "Select",
      "label": "Practical Type",
      "options": "\nLab Practical\nProject Demo\nViva Voce\nField Work\nWorkshop\nClinical",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "batch",
      "fieldtype": "Link",
      "label": "Batch",
      "options": "Student Batch Name"
    },
    {
      "fieldname": "student_group",
      "fieldtype": "Link",
      "label": "Student Group",
      "options": "Student Group"
    },
    {
      "fieldname": "section_break_schedule",
      "fieldtype": "Section Break",
      "label": "Schedule"
    },
    {
      "fieldname": "exam_date",
      "fieldtype": "Date",
      "label": "Exam Date",
      "reqd": 1
    },
    {
      "fieldname": "start_time",
      "fieldtype": "Time",
      "label": "Start Time"
    },
    {
      "fieldname": "end_time",
      "fieldtype": "Time",
      "label": "End Time"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "lab",
      "fieldtype": "Link",
      "label": "Lab/Venue",
      "options": "Room"
    },
    {
      "fieldname": "max_students_per_slot",
      "fieldtype": "Int",
      "label": "Max Students Per Slot"
    },
    {
      "fieldname": "slot_duration_minutes",
      "fieldtype": "Int",
      "label": "Slot Duration (Minutes)"
    },
    {
      "fieldname": "section_break_examiners",
      "fieldtype": "Section Break",
      "label": "Examiners"
    },
    {
      "fieldname": "internal_examiner",
      "fieldtype": "Link",
      "label": "Internal Examiner",
      "options": "Faculty Member",
      "reqd": 1
    },
    {
      "fieldname": "external_examiner",
      "fieldtype": "Link",
      "label": "External Examiner",
      "options": "External Examiner"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "additional_examiners",
      "fieldtype": "Table",
      "label": "Additional Examiners",
      "options": "Practical Exam Examiner"
    },
    {
      "fieldname": "section_break_marks",
      "fieldtype": "Section Break",
      "label": "Marking Scheme"
    },
    {
      "fieldname": "total_marks",
      "fieldtype": "Int",
      "label": "Total Marks",
      "reqd": 1
    },
    {
      "fieldname": "passing_marks",
      "fieldtype": "Int",
      "label": "Passing Marks"
    },
    {
      "fieldname": "evaluation_criteria",
      "fieldtype": "Table",
      "label": "Evaluation Criteria",
      "options": "Practical Evaluation Criteria"
    },
    {
      "fieldname": "section_break_slots",
      "fieldtype": "Section Break",
      "label": "Student Slots"
    },
    {
      "fieldname": "student_slots",
      "fieldtype": "Table",
      "label": "Student Slots",
      "options": "Practical Exam Slot"
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
      "options": "Draft\nScheduled\nIn Progress\nCompleted\nCancelled",
      "default": "Draft"
    },
    {
      "fieldname": "instructions",
      "fieldtype": "Text Editor",
      "label": "Instructions"
    }
  ],
  "permissions": [
    {"role": "Examination Controller", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.11 Internal Assessment

```json
{
  "doctype": "DocType",
  "name": "Internal Assessment",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "IA-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "assessment_name",
      "fieldtype": "Data",
      "label": "Assessment Name",
      "reqd": 1
    },
    {
      "fieldname": "assessment_type",
      "fieldtype": "Select",
      "label": "Assessment Type",
      "options": "\nClass Test\nQuiz\nAssignment\nProject\nPresentation\nLab Work\nSeminar\nGroup Discussion\nCase Study",
      "reqd": 1
    },
    {
      "fieldname": "course",
      "fieldtype": "Link",
      "label": "Course",
      "options": "Course",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "student_group",
      "fieldtype": "Link",
      "label": "Student Group",
      "options": "Student Group"
    },
    {
      "fieldname": "academic_year",
      "fieldtype": "Link",
      "label": "Academic Year",
      "options": "Academic Year",
      "reqd": 1
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
      "fieldname": "assessment_date",
      "fieldtype": "Date",
      "label": "Assessment Date"
    },
    {
      "fieldname": "due_date",
      "fieldtype": "Date",
      "label": "Due Date"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "weightage_percentage",
      "fieldtype": "Percent",
      "label": "Weightage in Final Grade"
    },
    {
      "fieldname": "max_marks",
      "fieldtype": "Float",
      "label": "Maximum Marks",
      "reqd": 1
    },
    {
      "fieldname": "section_break_criteria",
      "fieldtype": "Section Break",
      "label": "Evaluation Criteria"
    },
    {
      "fieldname": "rubric",
      "fieldtype": "Link",
      "label": "Rubric",
      "options": "Assessment Rubric"
    },
    {
      "fieldname": "criteria",
      "fieldtype": "Table",
      "label": "Criteria",
      "options": "Assessment Criteria Item"
    },
    {
      "fieldname": "section_break_co",
      "fieldtype": "Section Break",
      "label": "Outcome Mapping"
    },
    {
      "fieldname": "course_outcomes",
      "fieldtype": "Table MultiSelect",
      "label": "Course Outcomes Assessed",
      "options": "Assessment CO Link"
    },
    {
      "fieldname": "section_break_scores",
      "fieldtype": "Section Break",
      "label": "Student Scores"
    },
    {
      "fieldname": "student_scores",
      "fieldtype": "Table",
      "label": "Student Scores",
      "options": "Internal Assessment Score"
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
      "options": "Draft\nPublished\nIn Progress\nGrading\nCompleted",
      "default": "Draft"
    },
    {
      "fieldname": "graded_by",
      "fieldtype": "Link",
      "label": "Graded By",
      "options": "Faculty Member"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "average_score",
      "fieldtype": "Float",
      "label": "Average Score",
      "read_only": 1
    },
    {
      "fieldname": "highest_score",
      "fieldtype": "Float",
      "label": "Highest Score",
      "read_only": 1
    },
    {
      "fieldname": "lowest_score",
      "fieldtype": "Float",
      "label": "Lowest Score",
      "read_only": 1
    }
  ],
  "permissions": [
    {"role": "Faculty Member", "read": 1, "write": 1, "create": 1},
    {"role": "Examination Controller", "read": 1, "write": 1}
  ]
}
```

---

## 2. Question Paper Generator

### 2.1 Question Paper Generator Class

```python
# university_erp/university_erp/examination/question_paper_generator.py

import frappe
from frappe import _
from frappe.utils import cint, flt, random_string
import random
from typing import List, Dict, Optional

class QuestionPaperGenerator:
    """
    Automated question paper generator based on templates
    """

    def __init__(self, template_name: str):
        self.template = frappe.get_doc("Question Paper Template", template_name)
        self.selected_questions = []
        self.section_questions = {}

    def generate_paper(self, set_code: str = None,
                      exam_date: str = None) -> str:
        """
        Generate a question paper from template

        Args:
            set_code: Optional set identifier (A, B, C, D)
            exam_date: Date of examination

        Returns:
            Generated Question Paper name
        """
        # Validate template
        self._validate_template()

        # Get question pool
        question_pool = self._get_question_pool()

        # Select questions for each section
        for section in self.template.sections:
            self._select_questions_for_section(section, question_pool)

        # Create question paper document
        paper = self._create_question_paper(set_code, exam_date)

        # Update question usage statistics
        self._update_question_stats()

        return paper.name

    def _validate_template(self):
        """Validate template has enough questions available"""
        for section in self.template.sections:
            available = frappe.db.count("Question Bank", {
                "course": self.template.course,
                "question_type": section.question_type,
                "status": "Approved"
            })

            if available < section.total_questions:
                frappe.throw(_(
                    f"Not enough {section.question_type} questions available. "
                    f"Need {section.total_questions}, have {available}"
                ))

    def _get_question_pool(self) -> Dict[str, List]:
        """Get available questions grouped by type"""
        pool = {}

        # Get all approved questions for the course
        questions = frappe.get_all("Question Bank",
            filters={
                "course": self.template.course,
                "status": "Approved"
            },
            fields=["name", "question_type", "difficulty_level",
                   "blooms_taxonomy", "unit", "marks", "times_used",
                   "last_used_date"]
        )

        # Group by type
        for q in questions:
            qtype = q.question_type
            if qtype not in pool:
                pool[qtype] = []
            pool[qtype].append(q)

        return pool

    def _select_questions_for_section(self, section, pool: Dict):
        """Select questions for a section based on rules"""
        qtype = section.question_type
        available = pool.get(qtype, [])

        # Apply distribution rules
        selected = []

        # Unit-wise distribution
        if self.template.unit_wise_distribution:
            selected = self._select_by_unit(
                available,
                section.total_questions
            )

        # Bloom's taxonomy distribution
        elif self.template.bloom_distribution:
            selected = self._select_by_bloom(
                available,
                section.total_questions
            )

        # Random selection if no rules
        else:
            selected = self._weighted_random_select(
                available,
                section.total_questions
            )

        # Shuffle if required
        if self.template.shuffle_questions:
            random.shuffle(selected)

        self.section_questions[section.section_name] = selected

    def _select_by_unit(self, questions: List, count: int) -> List:
        """Select questions ensuring unit coverage"""
        selected = []
        unit_rules = {r.unit: r.percentage for r in self.template.unit_wise_distribution}

        for unit, percentage in unit_rules.items():
            unit_count = int(count * percentage / 100)
            unit_questions = [q for q in questions if q.unit == unit]

            # Sort by usage (prefer less used questions)
            unit_questions.sort(key=lambda x: (x.times_used, x.last_used_date or ""))

            selected.extend(unit_questions[:unit_count])

        # Fill remaining with random
        remaining = count - len(selected)
        if remaining > 0:
            unused = [q for q in questions if q not in selected]
            selected.extend(random.sample(unused, min(remaining, len(unused))))

        return selected[:count]

    def _select_by_bloom(self, questions: List, count: int) -> List:
        """Select questions by Bloom's taxonomy levels"""
        selected = []
        bloom_rules = {r.level: r.percentage for r in self.template.bloom_distribution}

        for level, percentage in bloom_rules.items():
            level_count = int(count * percentage / 100)
            level_questions = [q for q in questions if q.blooms_taxonomy == level]

            level_questions.sort(key=lambda x: (x.times_used, x.last_used_date or ""))
            selected.extend(level_questions[:level_count])

        remaining = count - len(selected)
        if remaining > 0:
            unused = [q for q in questions if q not in selected]
            selected.extend(random.sample(unused, min(remaining, len(unused))))

        return selected[:count]

    def _weighted_random_select(self, questions: List, count: int) -> List:
        """
        Weighted random selection preferring less-used questions
        """
        # Calculate weights (inverse of usage)
        max_usage = max([q.times_used for q in questions] or [1])
        weights = [(max_usage - q.times_used + 1) for q in questions]

        selected = []
        available = questions.copy()
        available_weights = weights.copy()

        for _ in range(min(count, len(questions))):
            if not available:
                break

            # Weighted random choice
            total_weight = sum(available_weights)
            r = random.uniform(0, total_weight)
            cumulative = 0

            for i, (q, w) in enumerate(zip(available, available_weights)):
                cumulative += w
                if cumulative >= r:
                    selected.append(q)
                    available.pop(i)
                    available_weights.pop(i)
                    break

        return selected

    def _create_question_paper(self, set_code: str, exam_date: str):
        """Create the question paper document"""
        paper = frappe.new_doc("Generated Question Paper")
        paper.paper_title = f"{self.template.template_name} - {set_code or 'Main'}"
        paper.course = self.template.course
        paper.template = self.template.name
        paper.total_marks = self.template.total_marks
        paper.duration_minutes = self.template.duration_minutes
        paper.exam_date = exam_date
        paper.set_code = set_code
        paper.created_by = frappe.session.user
        paper.instructions = self.template.instructions
        paper.status = "Draft"

        # Add sections with questions
        for section in self.template.sections:
            paper.append("paper_sections", {
                "section_name": section.section_name,
                "section_instructions": section.section_instructions,
                "questions": self._format_section_questions(
                    section.section_name,
                    section.marks_per_question
                )
            })

        paper.insert()
        return paper

    def _format_section_questions(self, section_name: str, marks: float) -> List:
        """Format questions for the paper section"""
        questions = self.section_questions.get(section_name, [])
        formatted = []

        for i, q in enumerate(questions, 1):
            formatted.append({
                "question": q.name,
                "question_number": i,
                "marks": marks
            })

        return formatted

    def _update_question_stats(self):
        """Update usage statistics for selected questions"""
        today = frappe.utils.today()

        for section_questions in self.section_questions.values():
            for q in section_questions:
                frappe.db.set_value("Question Bank", q.name, {
                    "times_used": q.times_used + 1,
                    "last_used_date": today
                })


def generate_multiple_sets(template_name: str, num_sets: int = 4,
                          exam_date: str = None) -> List[str]:
    """
    Generate multiple question paper sets

    Args:
        template_name: Template to use
        num_sets: Number of sets (default 4: A, B, C, D)
        exam_date: Examination date

    Returns:
        List of generated paper names
    """
    set_codes = ['A', 'B', 'C', 'D', 'E', 'F'][:num_sets]
    papers = []

    for code in set_codes:
        generator = QuestionPaperGenerator(template_name)
        paper_name = generator.generate_paper(code, exam_date)
        papers.append(paper_name)

    return papers
```

---

## 3. Online Examination Platform

### 3.1 Exam Controller Class

```python
# university_erp/university_erp/examination/online_exam_controller.py

import frappe
from frappe import _
from frappe.utils import now_datetime, time_diff_in_seconds, cint
from datetime import datetime, timedelta
import json
import hashlib

class OnlineExamController:
    """
    Controller for managing online examinations
    """

    def __init__(self, exam_name: str):
        self.exam = frappe.get_doc("Online Examination", exam_name)

    def validate_access(self, student: str) -> Dict:
        """
        Validate if student can access the exam

        Returns:
            Dict with status and message
        """
        # Check if student is eligible
        eligible = any(s.student == student for s in self.exam.eligible_students)
        if not eligible:
            return {
                "status": "error",
                "message": _("You are not eligible for this examination")
            }

        # Check exam timing
        now = now_datetime()
        if now < self.exam.start_datetime:
            return {
                "status": "error",
                "message": _("Examination has not started yet"),
                "starts_at": self.exam.start_datetime
            }

        if now > self.exam.end_datetime:
            return {
                "status": "error",
                "message": _("Examination has ended")
            }

        # Check previous attempts
        attempts = frappe.db.count("Student Exam Attempt", {
            "online_examination": self.exam.name,
            "student": student,
            "status": ["in", ["Submitted", "Auto Submitted", "Evaluated"]]
        })

        if attempts >= self.exam.max_attempts:
            return {
                "status": "error",
                "message": _("Maximum attempts exhausted")
            }

        # Check IP restriction
        if self.exam.ip_restriction:
            client_ip = frappe.local.request_ip
            if not self._is_ip_allowed(client_ip):
                return {
                    "status": "error",
                    "message": _("Access denied from your IP address")
                }

        return {"status": "success"}

    def _is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is in allowed ranges"""
        import ipaddress

        try:
            client_ip = ipaddress.ip_address(ip)
            allowed_ranges = self.exam.allowed_ip_ranges.split('\n')

            for range_str in allowed_ranges:
                range_str = range_str.strip()
                if not range_str:
                    continue

                try:
                    network = ipaddress.ip_network(range_str, strict=False)
                    if client_ip in network:
                        return True
                except ValueError:
                    continue

            return False
        except:
            return False

    def start_exam(self, student: str, password: str = None) -> Dict:
        """
        Start examination for a student

        Args:
            student: Student ID
            password: Exam password if required

        Returns:
            Exam attempt details
        """
        # Validate password
        if self.exam.requires_password:
            if not password or password != self.exam.exam_password:
                frappe.throw(_("Invalid exam password"))

        # Create or get existing attempt
        existing_attempt = frappe.db.get_value("Student Exam Attempt", {
            "online_examination": self.exam.name,
            "student": student,
            "status": "In Progress"
        })

        if existing_attempt:
            return self._resume_attempt(existing_attempt)

        # Create new attempt
        attempt = frappe.new_doc("Student Exam Attempt")
        attempt.online_examination = self.exam.name
        attempt.student = student
        attempt.start_time = now_datetime()
        attempt.status = "In Progress"
        attempt.ip_address = frappe.local.request_ip
        attempt.browser_info = frappe.request.headers.get("User-Agent", "")[:500]

        # Get attempt number
        prev_attempts = frappe.db.count("Student Exam Attempt", {
            "online_examination": self.exam.name,
            "student": student
        })
        attempt.attempt_number = prev_attempts + 1

        # Get question paper and prepare questions
        questions = self._prepare_questions(student)
        attempt.total_questions = len(questions)

        attempt.insert()

        # Calculate end time for this student
        end_time = min(
            datetime.now() + timedelta(minutes=self.exam.duration_minutes),
            self.exam.end_datetime
        )

        return {
            "attempt_id": attempt.name,
            "questions": questions,
            "duration_minutes": self.exam.duration_minutes,
            "end_time": end_time,
            "settings": self._get_exam_settings()
        }

    def _prepare_questions(self, student: str) -> List[Dict]:
        """Prepare questions for student (with shuffling if enabled)"""
        paper = frappe.get_doc("Generated Question Paper", self.exam.question_paper)
        questions = []

        for section in paper.paper_sections:
            section_questions = []

            for q_item in section.questions:
                question = frappe.get_doc("Question Bank", q_item.question)

                q_data = {
                    "id": question.name,
                    "section": section.section_name,
                    "number": q_item.question_number,
                    "type": question.question_type,
                    "text": question.question_text,
                    "marks": q_item.marks,
                    "image": question.question_image,
                    "negative_marks": question.negative_marks if question.negative_marking else 0
                }

                # Add options for MCQ/MSQ
                if question.question_type in ["Multiple Choice (MCQ)", "Multiple Select (MSQ)", "True/False"]:
                    options = [{"id": o.option_label, "text": o.option_text, "image": o.option_image}
                              for o in question.options]

                    # Shuffle options if enabled
                    if self.exam.shuffle_options:
                        import random
                        random.seed(f"{student}-{question.name}")  # Consistent per student
                        random.shuffle(options)

                    q_data["options"] = options

                section_questions.append(q_data)

            # Shuffle questions within section if enabled
            if self.exam.shuffle_questions:
                import random
                random.seed(f"{student}-{section.section_name}")
                random.shuffle(section_questions)

            questions.extend(section_questions)

        return questions

    def _get_exam_settings(self) -> Dict:
        """Get exam settings for frontend"""
        return {
            "one_question_per_page": self.exam.one_question_per_page,
            "allow_back_navigation": self.exam.allow_back_navigation,
            "show_timer": self.exam.show_timer,
            "show_question_palette": self.exam.show_question_palette,
            "allow_review_marking": self.exam.allow_review_marking,
            "show_calculator": self.exam.show_calculator,
            "full_screen_mode": self.exam.full_screen_mode,
            "disable_copy_paste": self.exam.disable_copy_paste,
            "disable_right_click": self.exam.disable_right_click,
            "proctoring_enabled": self.exam.enable_proctoring,
            "webcam_required": self.exam.webcam_required,
            "tab_switch_warning": self.exam.tab_switch_warning,
            "max_tab_switches": self.exam.max_tab_switches
        }

    def save_answer(self, attempt_id: str, question_id: str,
                   answer: any, marked_for_review: bool = False) -> Dict:
        """
        Save student's answer

        Args:
            attempt_id: Exam attempt ID
            question_id: Question ID
            answer: Student's answer
            marked_for_review: Whether marked for review

        Returns:
            Save status
        """
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

        # Validate attempt is still in progress
        if attempt.status != "In Progress":
            frappe.throw(_("Exam attempt is not active"))

        # Check time
        if self._is_time_expired(attempt):
            self._auto_submit(attempt)
            return {"status": "time_expired", "message": _("Time has expired")}

        # Find or create answer entry
        existing = None
        for ans in attempt.answers:
            if ans.question == question_id:
                existing = ans
                break

        if existing:
            existing.answer = json.dumps(answer) if isinstance(answer, (list, dict)) else str(answer)
            existing.marked_for_review = marked_for_review
            existing.answer_time = now_datetime()
        else:
            attempt.append("answers", {
                "question": question_id,
                "answer": json.dumps(answer) if isinstance(answer, (list, dict)) else str(answer),
                "marked_for_review": marked_for_review,
                "answer_time": now_datetime()
            })

        attempt.attempted = len([a for a in attempt.answers if a.answer])
        attempt.save()

        return {"status": "saved"}

    def _is_time_expired(self, attempt) -> bool:
        """Check if exam time has expired"""
        elapsed = time_diff_in_seconds(now_datetime(), attempt.start_time)
        allowed = self.exam.duration_minutes * 60 + (self.exam.late_submission_minutes or 0) * 60
        return elapsed > allowed or now_datetime() > self.exam.end_datetime

    def submit_exam(self, attempt_id: str, force: bool = False) -> Dict:
        """
        Submit examination

        Args:
            attempt_id: Exam attempt ID
            force: Force submit even if time remaining

        Returns:
            Submission result
        """
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

        if attempt.status not in ["In Progress", "Not Started"]:
            frappe.throw(_("Exam already submitted"))

        attempt.end_time = now_datetime()
        attempt.time_taken_minutes = int(
            time_diff_in_seconds(attempt.end_time, attempt.start_time) / 60
        )
        attempt.status = "Submitted"
        attempt.submit_type = "Manual"

        # Auto-evaluate MCQ/MSQ
        if self._can_auto_evaluate():
            self._auto_evaluate(attempt)

        attempt.save()

        # Update exam statistics
        self._update_exam_stats()

        result = {
            "status": "submitted",
            "attempt_id": attempt.name
        }

        if self.exam.show_result_immediately:
            result["score"] = {
                "marks_obtained": attempt.marks_obtained,
                "total_marks": attempt.total_marks,
                "percentage": attempt.percentage,
                "correct": attempt.correct,
                "incorrect": attempt.incorrect
            }

        return result

    def _auto_submit(self, attempt):
        """Auto submit on time expiry"""
        attempt.end_time = now_datetime()
        attempt.time_taken_minutes = self.exam.duration_minutes
        attempt.status = "Auto Submitted"
        attempt.submit_type = "Auto (Time Expired)"

        if self._can_auto_evaluate():
            self._auto_evaluate(attempt)

        attempt.save()

    def _can_auto_evaluate(self) -> bool:
        """Check if exam can be auto-evaluated"""
        paper = frappe.get_doc("Generated Question Paper", self.exam.question_paper)

        for section in paper.paper_sections:
            for q_item in section.questions:
                question = frappe.get_cached_doc("Question Bank", q_item.question)
                if question.question_type in ["Long Answer", "Case Study"]:
                    return False

        return True

    def _auto_evaluate(self, attempt):
        """Auto-evaluate objective questions"""
        total_marks = 0
        marks_obtained = 0
        correct = 0
        incorrect = 0
        negative_applied = 0

        for ans in attempt.answers:
            question = frappe.get_cached_doc("Question Bank", ans.question)
            q_marks = self._get_question_marks(ans.question)
            total_marks += q_marks

            is_correct, partial_marks = self._check_answer(question, ans.answer)

            if is_correct:
                marks_obtained += q_marks
                correct += 1
                ans.marks_obtained = q_marks
                ans.is_correct = True
            elif partial_marks > 0:
                marks_obtained += partial_marks
                ans.marks_obtained = partial_marks
                ans.is_correct = False
            else:
                if question.negative_marking:
                    negative_applied += question.negative_marks
                incorrect += 1
                ans.marks_obtained = 0
                ans.is_correct = False

        attempt.total_marks = total_marks
        attempt.marks_obtained = marks_obtained - negative_applied
        attempt.negative_marks_applied = negative_applied
        attempt.correct = correct
        attempt.incorrect = incorrect
        attempt.percentage = (attempt.marks_obtained / total_marks * 100) if total_marks > 0 else 0
        attempt.status = "Evaluated"
        attempt.evaluation_date = now_datetime()

    def _check_answer(self, question, answer: str) -> tuple:
        """
        Check if answer is correct

        Returns:
            (is_correct: bool, partial_marks: float)
        """
        if not answer:
            return False, 0

        try:
            student_answer = json.loads(answer) if answer.startswith('[') else answer
        except:
            student_answer = answer

        if question.question_type == "Multiple Choice (MCQ)":
            correct_option = None
            for opt in question.options:
                if opt.is_correct:
                    correct_option = opt.option_label
                    break

            return student_answer == correct_option, 0

        elif question.question_type == "Multiple Select (MSQ)":
            correct_options = set(opt.option_label for opt in question.options if opt.is_correct)
            student_options = set(student_answer) if isinstance(student_answer, list) else {student_answer}

            if student_options == correct_options:
                return True, 0

            # Partial marking
            if question.partial_marking:
                correct_selected = len(student_options & correct_options)
                incorrect_selected = len(student_options - correct_options)
                total_correct = len(correct_options)

                if incorrect_selected == 0:
                    partial = (correct_selected / total_correct) * question.marks
                    return False, partial

            return False, 0

        elif question.question_type == "True/False":
            return student_answer.lower() == question.correct_answer.strip().lower(), 0

        elif question.question_type == "Numerical":
            try:
                student_val = float(student_answer)
                correct_val = float(question.correct_answer.strip())
                # Allow 1% tolerance for numerical answers
                tolerance = abs(correct_val * 0.01)
                return abs(student_val - correct_val) <= tolerance, 0
            except:
                return False, 0

        elif question.question_type == "Fill in the Blanks":
            correct_answers = [a.strip().lower() for a in question.correct_answer.split(',')]
            return student_answer.strip().lower() in correct_answers, 0

        return False, 0

    def record_proctoring_event(self, attempt_id: str, event_type: str,
                               snapshot: str = None, details: dict = None):
        """
        Record proctoring event

        Args:
            attempt_id: Exam attempt ID
            event_type: Type of event (snapshot, tab_switch, violation, etc.)
            snapshot: Base64 image data
            details: Additional details
        """
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

        if event_type == "tab_switch":
            attempt.tab_switches = (attempt.tab_switches or 0) + 1

            if attempt.tab_switches > self.exam.max_tab_switches:
                attempt.proctoring_violations = (attempt.proctoring_violations or 0) + 1

                # Auto-disqualify if too many violations
                if attempt.proctoring_violations >= 3:
                    attempt.status = "Disqualified"
                    attempt.remarks = "Disqualified due to multiple proctoring violations"

        elif event_type == "snapshot" and snapshot:
            attempt.append("proctoring_snapshots", {
                "timestamp": now_datetime(),
                "snapshot_image": snapshot,
                "event_type": "Random Capture"
            })

        elif event_type == "violation":
            attempt.proctoring_violations = (attempt.proctoring_violations or 0) + 1
            attempt.append("proctoring_snapshots", {
                "timestamp": now_datetime(),
                "event_type": details.get("violation_type", "Unknown"),
                "remarks": details.get("description", "")
            })

        attempt.save()


# API Endpoints

@frappe.whitelist()
def start_examination(exam_name: str, password: str = None):
    """API to start an examination"""
    student = get_current_student()

    controller = OnlineExamController(exam_name)

    # Validate access
    validation = controller.validate_access(student)
    if validation.get("status") != "success":
        return validation

    return controller.start_exam(student, password)


@frappe.whitelist()
def save_exam_answer(attempt_id: str, question_id: str,
                    answer: str, marked_for_review: bool = False):
    """API to save an answer"""
    exam_name = frappe.db.get_value("Student Exam Attempt", attempt_id, "online_examination")
    controller = OnlineExamController(exam_name)
    return controller.save_answer(attempt_id, question_id, answer, marked_for_review)


@frappe.whitelist()
def submit_examination(attempt_id: str):
    """API to submit examination"""
    exam_name = frappe.db.get_value("Student Exam Attempt", attempt_id, "online_examination")
    controller = OnlineExamController(exam_name)
    return controller.submit_exam(attempt_id)


@frappe.whitelist()
def report_proctoring_event(attempt_id: str, event_type: str,
                           snapshot: str = None, details: str = None):
    """API to report proctoring events"""
    exam_name = frappe.db.get_value("Student Exam Attempt", attempt_id, "online_examination")
    controller = OnlineExamController(exam_name)

    details_dict = json.loads(details) if details else {}
    controller.record_proctoring_event(attempt_id, event_type, snapshot, details_dict)

    return {"status": "recorded"}


def get_current_student():
    """Get current logged in student"""
    return frappe.db.get_value("Student", {"user": frappe.session.user})
```

---

## 4. Answer Sheet Management

### 4.1 Answer Sheet Manager

```python
# university_erp/university_erp/examination/answer_sheet_manager.py

import frappe
from frappe import _
from frappe.utils import now_datetime, random_string
import qrcode
import io
import base64

class AnswerSheetManager:
    """
    Manager for physical answer sheet tracking
    """

    @staticmethod
    def generate_barcode(answer_sheet_name: str) -> str:
        """
        Generate unique barcode for answer sheet

        Args:
            answer_sheet_name: Answer sheet document name

        Returns:
            Barcode string
        """
        # Create unique barcode combining exam, student, and random
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        barcode = f"AS-{sheet.examination[:5]}-{sheet.roll_number}-{random_string(4).upper()}"

        frappe.db.set_value("Answer Sheet", answer_sheet_name, "barcode", barcode)

        return barcode

    @staticmethod
    def generate_qr_code(answer_sheet_name: str) -> str:
        """
        Generate QR code for answer sheet

        Returns:
            Base64 encoded QR code image
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        qr_data = {
            "id": sheet.name,
            "barcode": sheet.barcode,
            "exam": sheet.examination,
            "course": sheet.course,
            "roll": sheet.roll_number
        }

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def bulk_create_answer_sheets(examination: str, course: str) -> int:
        """
        Create answer sheets for all registered students

        Args:
            examination: Examination ID
            course: Course ID

        Returns:
            Number of sheets created
        """
        # Get enrolled students
        students = frappe.get_all("Examination Entry",
            filters={
                "examination": examination,
                "course": course,
                "status": "Confirmed"
            },
            fields=["student", "roll_number", "seat_number"]
        )

        count = 0
        for student in students:
            # Check if sheet already exists
            existing = frappe.db.exists("Answer Sheet", {
                "examination": examination,
                "course": course,
                "student": student.student
            })

            if not existing:
                sheet = frappe.new_doc("Answer Sheet")
                sheet.examination = examination
                sheet.course = course
                sheet.student = student.student
                sheet.roll_number = student.roll_number
                sheet.seat_number = student.seat_number
                sheet.status = "Collected"
                sheet.insert()

                # Generate barcode
                AnswerSheetManager.generate_barcode(sheet.name)
                count += 1

        return count

    @staticmethod
    def update_tracking(answer_sheet_name: str, action: str,
                       location: str = None, user: str = None, remarks: str = None):
        """
        Update answer sheet tracking

        Args:
            answer_sheet_name: Answer sheet ID
            action: Tracking action
            location: Current location
            user: User performing action
            remarks: Additional remarks
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        sheet.append("tracking_history", {
            "action": action,
            "timestamp": now_datetime(),
            "location": location,
            "performed_by": user or frappe.session.user,
            "remarks": remarks
        })

        if location:
            sheet.current_location = location

        # Update status based on action
        status_mapping = {
            "Collected": "Collected",
            "Dispatched": "In Transit",
            "Received": "Received at Evaluation Center",
            "Assigned": "Assigned for Evaluation",
            "Evaluation Started": "Evaluation In Progress",
            "Evaluation Completed": "Evaluated",
            "Sent for Moderation": "Pending Moderation",
            "Moderation Completed": "Moderated"
        }

        if action in status_mapping:
            sheet.status = status_mapping[action]

        sheet.save()

    @staticmethod
    def assign_for_evaluation(answer_sheets: list, evaluator: str) -> int:
        """
        Assign multiple answer sheets to an evaluator

        Args:
            answer_sheets: List of answer sheet names
            evaluator: Faculty member to assign

        Returns:
            Number of sheets assigned
        """
        count = 0
        for sheet_name in answer_sheets:
            sheet = frappe.get_doc("Answer Sheet", sheet_name)

            if sheet.status in ["Received at Evaluation Center", "Collected"]:
                sheet.assigned_to = evaluator
                sheet.assignment_date = now_datetime()
                sheet.status = "Assigned for Evaluation"
                sheet.save()

                AnswerSheetManager.update_tracking(
                    sheet_name,
                    "Assigned",
                    f"Evaluator: {evaluator}",
                    remarks=f"Assigned to {evaluator}"
                )
                count += 1

        return count

    @staticmethod
    def record_evaluation(answer_sheet_name: str, question_scores: list,
                         evaluator: str, remarks: str = None):
        """
        Record evaluation scores for answer sheet

        Args:
            answer_sheet_name: Answer sheet ID
            question_scores: List of {question_number, marks_obtained, max_marks, comments}
            evaluator: Evaluator ID
            remarks: Overall remarks
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        # Clear existing scores
        sheet.question_scores = []

        total_marks = 0
        marks_obtained = 0

        for score in question_scores:
            sheet.append("question_scores", {
                "question_number": score.get("question_number"),
                "max_marks": score.get("max_marks"),
                "marks_obtained": score.get("marks_obtained"),
                "comments": score.get("comments")
            })

            total_marks += score.get("max_marks", 0)
            marks_obtained += score.get("marks_obtained", 0)

        sheet.total_marks = total_marks
        sheet.marks_obtained = marks_obtained
        sheet.percentage = (marks_obtained / total_marks * 100) if total_marks > 0 else 0

        sheet.evaluation_started = sheet.evaluation_started or now_datetime()
        sheet.evaluation_completed = now_datetime()
        sheet.status = "Evaluated"

        if remarks:
            sheet.remarks = remarks

        sheet.save()

        AnswerSheetManager.update_tracking(
            answer_sheet_name,
            "Evaluation Completed",
            remarks=f"Marks: {marks_obtained}/{total_marks}"
        )

    @staticmethod
    def request_revaluation(answer_sheet_name: str, student: str, reason: str):
        """
        Request revaluation for an answer sheet

        Args:
            answer_sheet_name: Answer sheet ID
            student: Student requesting
            reason: Reason for revaluation
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        # Validate student owns this sheet
        if sheet.student != student:
            frappe.throw(_("You can only request revaluation for your own answer sheet"))

        # Check if revaluation already requested
        if sheet.status == "Revaluation Requested":
            frappe.throw(_("Revaluation already requested"))

        # Create revaluation request
        request = frappe.new_doc("Revaluation Request")
        request.answer_sheet = answer_sheet_name
        request.student = student
        request.reason = reason
        request.original_marks = sheet.marks_obtained
        request.status = "Pending"
        request.insert()

        sheet.status = "Revaluation Requested"
        sheet.save()

        return request.name


class EvaluationWorkflow:
    """
    Workflow management for answer sheet evaluation
    """

    @staticmethod
    def get_evaluator_workload(evaluator: str) -> Dict:
        """
        Get current workload for an evaluator

        Args:
            evaluator: Faculty member ID

        Returns:
            Workload statistics
        """
        assigned = frappe.db.count("Answer Sheet", {
            "assigned_to": evaluator,
            "status": ["in", ["Assigned for Evaluation", "Evaluation In Progress"]]
        })

        completed_today = frappe.db.count("Answer Sheet", {
            "assigned_to": evaluator,
            "evaluation_completed": [">=", frappe.utils.today()],
            "status": "Evaluated"
        })

        total_completed = frappe.db.count("Answer Sheet", {
            "assigned_to": evaluator,
            "status": ["in", ["Evaluated", "Moderated"]]
        })

        return {
            "pending": assigned,
            "completed_today": completed_today,
            "total_completed": total_completed
        }

    @staticmethod
    def auto_assign_sheets(examination: str, course: str) -> Dict:
        """
        Auto-assign answer sheets to available evaluators

        Args:
            examination: Examination ID
            course: Course ID

        Returns:
            Assignment summary
        """
        # Get unassigned sheets
        unassigned = frappe.get_all("Answer Sheet",
            filters={
                "examination": examination,
                "course": course,
                "status": "Received at Evaluation Center",
                "assigned_to": ["is", "not set"]
            },
            pluck="name"
        )

        if not unassigned:
            return {"message": "No unassigned sheets", "assigned": 0}

        # Get available evaluators for this course
        evaluators = frappe.get_all("Course Instructor",
            filters={"course": course},
            fields=["instructor"]
        )

        if not evaluators:
            return {"message": "No evaluators available", "assigned": 0}

        # Get workload for each evaluator
        evaluator_loads = {}
        for e in evaluators:
            workload = EvaluationWorkflow.get_evaluator_workload(e.instructor)
            evaluator_loads[e.instructor] = workload["pending"]

        # Distribute sheets evenly
        assignments = {e: [] for e in evaluator_loads}

        for sheet in unassigned:
            # Assign to evaluator with least pending
            min_evaluator = min(evaluator_loads, key=evaluator_loads.get)
            assignments[min_evaluator].append(sheet)
            evaluator_loads[min_evaluator] += 1

        # Perform assignments
        total_assigned = 0
        for evaluator, sheets in assignments.items():
            count = AnswerSheetManager.assign_for_evaluation(sheets, evaluator)
            total_assigned += count

        return {
            "message": f"Assigned {total_assigned} sheets",
            "assigned": total_assigned,
            "distribution": {e: len(s) for e, s in assignments.items()}
        }
```

---

## 5. Reports

### 5.1 Question Bank Analysis Report

```python
# university_erp/university_erp/examination/report/question_bank_analysis.py

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Course", "fieldname": "course", "fieldtype": "Link", "options": "Course", "width": 200},
        {"label": "Total Questions", "fieldname": "total", "fieldtype": "Int", "width": 120},
        {"label": "MCQ", "fieldname": "mcq", "fieldtype": "Int", "width": 80},
        {"label": "Short Answer", "fieldname": "short", "fieldtype": "Int", "width": 100},
        {"label": "Long Answer", "fieldname": "long", "fieldtype": "Int", "width": 100},
        {"label": "Easy", "fieldname": "easy", "fieldtype": "Int", "width": 80},
        {"label": "Medium", "fieldname": "medium", "fieldtype": "Int", "width": 80},
        {"label": "Hard", "fieldname": "hard", "fieldtype": "Int", "width": 80},
        {"label": "Approved", "fieldname": "approved", "fieldtype": "Int", "width": 90},
        {"label": "Pending Review", "fieldname": "pending", "fieldtype": "Int", "width": 110},
        {"label": "Avg Usage", "fieldname": "avg_usage", "fieldtype": "Float", "width": 100}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("course"):
        conditions += f" AND course = '{filters.get('course')}'"

    data = frappe.db.sql(f"""
        SELECT
            course,
            COUNT(*) as total,
            SUM(CASE WHEN question_type = 'Multiple Choice (MCQ)' THEN 1 ELSE 0 END) as mcq,
            SUM(CASE WHEN question_type = 'Short Answer' THEN 1 ELSE 0 END) as short,
            SUM(CASE WHEN question_type = 'Long Answer' THEN 1 ELSE 0 END) as long,
            SUM(CASE WHEN difficulty_level = 'Easy' THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN difficulty_level = 'Medium' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN difficulty_level = 'Hard' THEN 1 ELSE 0 END) as hard,
            SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'Pending Review' THEN 1 ELSE 0 END) as pending,
            AVG(times_used) as avg_usage
        FROM `tabQuestion Bank`
        WHERE 1=1 {conditions}
        GROUP BY course
        ORDER BY total DESC
    """, as_dict=True)

    return data

def get_chart(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.course for d in data[:10]],
            "datasets": [
                {"name": "Total Questions", "values": [d.total for d in data[:10]]},
                {"name": "Approved", "values": [d.approved for d in data[:10]]}
            ]
        },
        "type": "bar"
    }
```

### 5.2 Online Exam Performance Report

```python
# university_erp/university_erp/examination/report/online_exam_performance.py

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    chart = get_chart(data)

    return columns, data, None, chart, summary

def get_columns():
    return [
        {"label": "Exam", "fieldname": "exam", "fieldtype": "Link", "options": "Online Examination", "width": 200},
        {"label": "Course", "fieldname": "course", "fieldtype": "Link", "options": "Course", "width": 150},
        {"label": "Total Students", "fieldname": "total", "fieldtype": "Int", "width": 110},
        {"label": "Appeared", "fieldname": "appeared", "fieldtype": "Int", "width": 90},
        {"label": "Submitted", "fieldname": "submitted", "fieldtype": "Int", "width": 90},
        {"label": "Avg Score", "fieldname": "avg_score", "fieldtype": "Percent", "width": 100},
        {"label": "Highest", "fieldname": "highest", "fieldtype": "Percent", "width": 90},
        {"label": "Lowest", "fieldname": "lowest", "fieldtype": "Percent", "width": 90},
        {"label": "Pass %", "fieldname": "pass_rate", "fieldtype": "Percent", "width": 90},
        {"label": "Avg Time (min)", "fieldname": "avg_time", "fieldtype": "Int", "width": 110}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("examination"):
        conditions += f" AND oe.name = '{filters.get('examination')}'"
    if filters.get("course"):
        conditions += f" AND oe.course = '{filters.get('course')}'"

    data = frappe.db.sql(f"""
        SELECT
            oe.name as exam,
            oe.course,
            oe.total_registered as total,
            oe.total_appeared as appeared,
            oe.total_submitted as submitted,
            AVG(sea.percentage) as avg_score,
            MAX(sea.percentage) as highest,
            MIN(sea.percentage) as lowest,
            (SUM(CASE WHEN sea.percentage >= 40 THEN 1 ELSE 0 END) / COUNT(*) * 100) as pass_rate,
            AVG(sea.time_taken_minutes) as avg_time
        FROM `tabOnline Examination` oe
        LEFT JOIN `tabStudent Exam Attempt` sea ON sea.online_examination = oe.name
        WHERE oe.status = 'Completed' {conditions}
        GROUP BY oe.name, oe.course, oe.total_registered, oe.total_appeared, oe.total_submitted
        ORDER BY oe.start_datetime DESC
    """, as_dict=True)

    return data

def get_summary(data):
    if not data:
        return []

    total_exams = len(data)
    total_students = sum(d.total or 0 for d in data)
    avg_attendance = sum(d.appeared or 0 for d in data) / sum(d.total or 1 for d in data) * 100
    overall_avg = sum(d.avg_score or 0 for d in data) / len(data)

    return [
        {"label": "Total Exams", "value": total_exams, "indicator": "Blue"},
        {"label": "Total Students", "value": total_students, "indicator": "Blue"},
        {"label": "Avg Attendance", "value": f"{avg_attendance:.1f}%", "indicator": "Green" if avg_attendance > 80 else "Orange"},
        {"label": "Overall Avg Score", "value": f"{overall_avg:.1f}%", "indicator": "Green" if overall_avg > 50 else "Red"}
    ]

def get_chart(data):
    return {
        "data": {
            "labels": [d.exam[:20] for d in data[:10]],
            "datasets": [
                {"name": "Avg Score", "values": [d.avg_score or 0 for d in data[:10]]},
                {"name": "Pass Rate", "values": [d.pass_rate or 0 for d in data[:10]]}
            ]
        },
        "type": "line"
    }
```

---

## 6. Student Portal Integration

### 6.1 Exam Portal Page

```python
# university_erp/www/student-portal/online-exam.py

import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access examinations"), frappe.AuthenticationError)

    student = frappe.db.get_value("Student", {"user": frappe.session.user})
    if not student:
        frappe.throw(_("Student profile not found"))

    context.no_cache = 1
    context.student = frappe.get_doc("Student", student)

    # Get available examinations
    context.upcoming_exams = get_upcoming_exams(student)
    context.live_exams = get_live_exams(student)
    context.past_exams = get_past_exams(student)
    context.exam_results = get_exam_results(student)

def get_upcoming_exams(student):
    """Get upcoming examinations for student"""
    return frappe.db.sql("""
        SELECT
            oe.name, oe.exam_title, oe.course, oe.start_datetime,
            oe.end_datetime, oe.duration_minutes, oe.exam_type,
            c.course_name
        FROM `tabOnline Examination` oe
        JOIN `tabOnline Exam Student` oes ON oes.parent = oe.name
        JOIN `tabCourse` c ON c.name = oe.course
        WHERE oes.student = %s
        AND oe.status = 'Scheduled'
        AND oe.start_datetime > NOW()
        ORDER BY oe.start_datetime
    """, student, as_dict=True)

def get_live_exams(student):
    """Get currently live examinations"""
    return frappe.db.sql("""
        SELECT
            oe.name, oe.exam_title, oe.course, oe.start_datetime,
            oe.end_datetime, oe.duration_minutes, oe.exam_type,
            c.course_name,
            sea.name as attempt_id, sea.status as attempt_status,
            sea.start_time
        FROM `tabOnline Examination` oe
        JOIN `tabOnline Exam Student` oes ON oes.parent = oe.name
        JOIN `tabCourse` c ON c.name = oe.course
        LEFT JOIN `tabStudent Exam Attempt` sea ON sea.online_examination = oe.name
            AND sea.student = %s AND sea.status = 'In Progress'
        WHERE oes.student = %s
        AND oe.status = 'Live'
        AND NOW() BETWEEN oe.start_datetime AND oe.end_datetime
        ORDER BY oe.end_datetime
    """, (student, student), as_dict=True)

def get_past_exams(student):
    """Get completed examinations"""
    return frappe.db.sql("""
        SELECT
            oe.name, oe.exam_title, oe.course, oe.start_datetime,
            oe.duration_minutes, oe.exam_type, c.course_name,
            sea.marks_obtained, sea.total_marks, sea.percentage,
            sea.status as attempt_status, sea.time_taken_minutes
        FROM `tabOnline Examination` oe
        JOIN `tabOnline Exam Student` oes ON oes.parent = oe.name
        JOIN `tabCourse` c ON c.name = oe.course
        LEFT JOIN `tabStudent Exam Attempt` sea ON sea.online_examination = oe.name
            AND sea.student = %s
        WHERE oes.student = %s
        AND oe.status = 'Completed'
        ORDER BY oe.start_datetime DESC
        LIMIT 20
    """, (student, student), as_dict=True)

def get_exam_results(student):
    """Get detailed exam results"""
    return frappe.db.sql("""
        SELECT
            sea.name, sea.online_examination, oe.exam_title,
            oe.course, c.course_name,
            sea.marks_obtained, sea.total_marks, sea.percentage,
            sea.correct, sea.incorrect, sea.attempted, sea.total_questions,
            sea.time_taken_minutes, sea.status,
            oe.show_correct_answers
        FROM `tabStudent Exam Attempt` sea
        JOIN `tabOnline Examination` oe ON oe.name = sea.online_examination
        JOIN `tabCourse` c ON c.name = oe.course
        WHERE sea.student = %s
        AND sea.status IN ('Submitted', 'Auto Submitted', 'Evaluated')
        ORDER BY sea.end_time DESC
        LIMIT 20
    """, student, as_dict=True)
```

### 6.2 Exam Interface HTML

```html
<!-- university_erp/www/student-portal/online-exam.html -->
{% extends "templates/student_portal_base.html" %}

{% block title %}Online Examinations{% endblock %}

{% block page_content %}
<div class="exam-portal">
    <!-- Live Exams Alert -->
    {% if live_exams %}
    <div class="alert alert-warning mb-4">
        <i class="fa fa-exclamation-triangle"></i>
        <strong>Live Examinations:</strong> You have {{ live_exams | length }} examination(s) currently in progress.
    </div>
    {% endif %}

    <!-- Live Exams -->
    {% if live_exams %}
    <div class="card mb-4">
        <div class="card-header bg-danger text-white">
            <h5 class="mb-0"><i class="fa fa-play-circle"></i> Live Examinations</h5>
        </div>
        <div class="card-body">
            {% for exam in live_exams %}
            <div class="exam-item live-exam p-3 mb-3 border rounded">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h5 class="mb-1">{{ exam.exam_title }}</h5>
                        <p class="text-muted mb-0">
                            {{ exam.course_name }} | {{ exam.exam_type }}
                        </p>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="countdown" data-end="{{ exam.end_datetime }}">
                            <span class="time-remaining"></span>
                        </div>
                        <small class="text-muted">Time Remaining</small>
                    </div>
                    <div class="col-md-3 text-right">
                        {% if exam.attempt_id %}
                        <a href="/student-portal/exam-interface?attempt={{ exam.attempt_id }}"
                           class="btn btn-warning btn-lg">
                            <i class="fa fa-arrow-right"></i> Resume Exam
                        </a>
                        {% else %}
                        <button class="btn btn-success btn-lg start-exam-btn"
                                data-exam="{{ exam.name }}"
                                data-requires-password="{{ exam.requires_password }}">
                            <i class="fa fa-play"></i> Start Exam
                        </button>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Upcoming Exams -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0"><i class="fa fa-calendar"></i> Upcoming Examinations</h5>
        </div>
        <div class="card-body">
            {% if upcoming_exams %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Examination</th>
                            <th>Course</th>
                            <th>Type</th>
                            <th>Date & Time</th>
                            <th>Duration</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for exam in upcoming_exams %}
                        <tr>
                            <td>{{ exam.exam_title }}</td>
                            <td>{{ exam.course_name }}</td>
                            <td><span class="badge badge-info">{{ exam.exam_type }}</span></td>
                            <td>{{ frappe.format(exam.start_datetime, 'Datetime') }}</td>
                            <td>{{ exam.duration_minutes }} mins</td>
                            <td><span class="badge badge-secondary">Scheduled</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-muted text-center py-4">No upcoming examinations</p>
            {% endif %}
        </div>
    </div>

    <!-- Past Exams & Results -->
    <div class="card">
        <div class="card-header">
            <h5 class="mb-0"><i class="fa fa-history"></i> Past Examinations & Results</h5>
        </div>
        <div class="card-body">
            {% if exam_results %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Examination</th>
                            <th>Course</th>
                            <th>Score</th>
                            <th>Questions</th>
                            <th>Time Taken</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in exam_results %}
                        <tr>
                            <td>{{ result.exam_title }}</td>
                            <td>{{ result.course_name }}</td>
                            <td>
                                <strong>{{ result.marks_obtained }}/{{ result.total_marks }}</strong>
                                <br>
                                <span class="badge {% if result.percentage >= 40 %}badge-success{% else %}badge-danger{% endif %}">
                                    {{ "%.1f"|format(result.percentage) }}%
                                </span>
                            </td>
                            <td>
                                <span class="text-success">{{ result.correct }} correct</span> /
                                <span class="text-danger">{{ result.incorrect }} wrong</span>
                            </td>
                            <td>{{ result.time_taken_minutes }} mins</td>
                            <td>
                                <span class="badge
                                    {% if result.status == 'Evaluated' %}badge-success
                                    {% elif result.status == 'Auto Submitted' %}badge-warning
                                    {% else %}badge-info{% endif %}">
                                    {{ result.status }}
                                </span>
                            </td>
                            <td>
                                {% if result.show_correct_answers %}
                                <a href="/student-portal/exam-review?attempt={{ result.name }}"
                                   class="btn btn-sm btn-outline-primary">
                                    View Answers
                                </a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-muted text-center py-4">No examination history</p>
            {% endif %}
        </div>
    </div>
</div>

<!-- Exam Password Modal -->
<div class="modal fade" id="examPasswordModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Enter Exam Password</h5>
                <button type="button" class="close" data-dismiss="modal">
                    <span>&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <input type="password" class="form-control" id="examPassword"
                       placeholder="Enter password provided by your instructor">
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="confirmStartExam">Start Exam</button>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Countdown timers
    document.querySelectorAll('.countdown').forEach(function(el) {
        const endTime = new Date(el.dataset.end);
        setInterval(function() {
            const now = new Date();
            const diff = endTime - now;
            if (diff > 0) {
                const hours = Math.floor(diff / 3600000);
                const mins = Math.floor((diff % 3600000) / 60000);
                const secs = Math.floor((diff % 60000) / 1000);
                el.querySelector('.time-remaining').textContent =
                    `${hours}h ${mins}m ${secs}s`;
            } else {
                el.querySelector('.time-remaining').textContent = 'Ended';
            }
        }, 1000);
    });

    // Start exam button
    let selectedExam = null;
    document.querySelectorAll('.start-exam-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            selectedExam = this.dataset.exam;
            if (this.dataset.requiresPassword === '1') {
                $('#examPasswordModal').modal('show');
            } else {
                startExam(selectedExam);
            }
        });
    });

    document.getElementById('confirmStartExam').addEventListener('click', function() {
        const password = document.getElementById('examPassword').value;
        startExam(selectedExam, password);
    });

    function startExam(examName, password = null) {
        frappe.call({
            method: 'university_erp.university_erp.examination.online_exam_controller.start_examination',
            args: { exam_name: examName, password: password },
            callback: function(r) {
                if (r.message && r.message.status === 'success') {
                    window.location.href = `/student-portal/exam-interface?attempt=${r.message.attempt_id}`;
                } else {
                    frappe.msgprint(r.message.message || 'Failed to start exam');
                }
            }
        });
    }
});
</script>
{% endblock %}
```

---

## 7. Implementation Checklist

### Week 1: Question Bank Setup
- [ ] Create Question Bank DocType
- [ ] Create Question Option child table
- [ ] Create Question Tag DocType
- [ ] Implement question CRUD operations
- [ ] Create question import from CSV/Excel
- [ ] Build question preview functionality
- [ ] Add image/media upload for questions

### Week 2: Question Paper Generator
- [ ] Create Question Paper Template DocType
- [ ] Create Question Paper Section child table
- [ ] Build QuestionPaperGenerator class
- [ ] Implement distribution rules (unit-wise, bloom's)
- [ ] Create multiple set generation
- [ ] Build question paper preview/print
- [ ] Add question paper approval workflow

### Week 3: Online Examination Platform
- [ ] Create Online Examination DocType
- [ ] Create Student Exam Attempt DocType
- [ ] Create Student Answer child table
- [ ] Build OnlineExamController class
- [ ] Implement exam start/resume functionality
- [ ] Build answer save mechanism
- [ ] Implement auto-submit on time expiry

### Week 4: Exam Interface & Proctoring
- [ ] Create exam interface HTML/JS
- [ ] Implement question navigation
- [ ] Build timer and countdown
- [ ] Add mark for review functionality
- [ ] Implement basic proctoring (tab switch detection)
- [ ] Add webcam snapshot capture
- [ ] Build full-screen mode enforcement

### Week 5: Answer Sheet & Evaluation
- [ ] Create Answer Sheet DocType
- [ ] Create Answer Sheet Score child table
- [ ] Build barcode/QR generation
- [ ] Implement tracking workflow
- [ ] Create evaluation interface for faculty
- [ ] Build auto-evaluation for MCQ
- [ ] Implement moderation workflow

### Week 6: Internal Assessment & Reports
- [ ] Create Internal Assessment DocType
- [ ] Create Assessment Criteria child tables
- [ ] Build assessment entry interface
- [ ] Create Question Bank Analysis report
- [ ] Create Online Exam Performance report
- [ ] Build CO/PO attainment calculation
- [ ] Student portal integration

---

## 8. Integration Points

### 8.1 With Existing Modules
- **Course Module**: Questions linked to courses and units
- **Student Module**: Exam registration and results
- **Faculty Module**: Question creation and evaluation
- **Examination Module**: Integration with exam schedule
- **Result Module**: Marks transfer to final results

### 8.2 With Phase 19 (Analytics)
- Question difficulty analysis
- Student performance trends
- CO-PO attainment metrics
- Exam statistics dashboard

### 8.3 With Phase 20 (Accreditation)
- Bloom's taxonomy mapping
- Course outcome assessment
- Question paper audit trail
- Student performance documentation

---

## 9. Security Considerations

1. **Exam Security**
   - Password-protected exams
   - IP restriction capabilities
   - Question shuffling per student
   - Secure answer storage

2. **Proctoring**
   - Tab switch detection
   - Copy/paste prevention
   - Right-click disable
   - Webcam monitoring (optional)

3. **Data Protection**
   - Question bank access control
   - Answer encryption
   - Audit trail for all actions
   - Result access restrictions

4. **Anti-Cheating**
   - Question randomization
   - Option shuffling
   - Time-based submission
   - Multiple question sets

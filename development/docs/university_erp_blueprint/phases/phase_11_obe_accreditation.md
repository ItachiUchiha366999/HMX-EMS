# Phase 11: Outcome-Based Education (OBE) & Accreditation Module

## Overview

This phase implements the Outcome-Based Education framework required for NAAC/NBA accreditation. It includes Course Outcomes (CO), Program Outcomes (PO), Program Educational Objectives (PEO), CO-PO mapping, and attainment calculation.

**Duration:** 3-4 weeks
**Priority:** High (Required for accreditation)
**Dependencies:** Phase 3 (Academics), Phase 4 (Examinations)

---

## Prerequisites

- Phase 3 Academics complete (Course, Program DocTypes)
- Phase 4 Examinations complete (Assessment Results)
- Grading system configured
- Assessment plans functional

---

## Week 1: Outcome Definitions

### 1.1 Program Educational Objective (PEO) DocType

```json
{
    "doctype": "DocType",
    "name": "Program Educational Objective",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:{program}-PEO-{idx}",
    "fields": [
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1, "in_list_view": 1},
        {"fieldname": "idx", "fieldtype": "Int", "label": "PEO Number", "reqd": 1, "in_list_view": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "label": "Effective From"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nRevised\nArchived", "default": "Active"},

        {"fieldname": "section_peo", "fieldtype": "Section Break", "label": "PEO Statement"},
        {"fieldname": "peo_statement", "fieldtype": "Text", "label": "PEO Statement", "reqd": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Detailed Description"},

        {"fieldname": "section_keywords", "fieldtype": "Section Break", "label": "Keywords & Tags"},
        {"fieldname": "bloom_level", "fieldtype": "Select", "options": "Remember\nUnderstand\nApply\nAnalyze\nEvaluate\nCreate", "label": "Primary Bloom's Level"},
        {"fieldname": "keywords", "fieldtype": "Small Text", "label": "Keywords"},

        {"fieldname": "section_mapping", "fieldtype": "Section Break", "label": "Stakeholder Alignment"},
        {"fieldname": "industry_relevance", "fieldtype": "Small Text", "label": "Industry Relevance"},
        {"fieldname": "societal_need", "fieldtype": "Small Text", "label": "Societal Need Addressed"}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Instructor", "read": 1}
    ]
}
```

### 1.2 Program Outcome (PO) DocType

```json
{
    "doctype": "DocType",
    "name": "Program Outcome",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:{program}-PO-{po_number}",
    "fields": [
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1, "in_list_view": 1},
        {"fieldname": "po_number", "fieldtype": "Int", "label": "PO Number", "reqd": 1, "in_list_view": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "po_code", "fieldtype": "Data", "label": "PO Code", "description": "e.g., PO1, PO2, PSO1"},
        {"fieldname": "is_pso", "fieldtype": "Check", "label": "Program Specific Outcome (PSO)"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "label": "Effective From"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nRevised\nArchived", "default": "Active"},

        {"fieldname": "section_po", "fieldtype": "Section Break", "label": "PO Statement"},
        {"fieldname": "po_title", "fieldtype": "Data", "label": "PO Title", "reqd": 1, "in_list_view": 1},
        {"fieldname": "po_statement", "fieldtype": "Text", "label": "PO Statement", "reqd": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Detailed Description"},

        {"fieldname": "section_nba", "fieldtype": "Section Break", "label": "NBA Graduate Attributes"},
        {"fieldname": "nba_attribute", "fieldtype": "Select", "options": "\nEngineering Knowledge\nProblem Analysis\nDesign/Development of Solutions\nConduct Investigations\nModern Tool Usage\nEngineer and Society\nEnvironment and Sustainability\nEthics\nIndividual and Team Work\nCommunication\nProject Management and Finance\nLife-long Learning", "label": "NBA Graduate Attribute"},

        {"fieldname": "section_bloom", "fieldtype": "Section Break", "label": "Taxonomy"},
        {"fieldname": "bloom_level", "fieldtype": "Select", "options": "Remember\nUnderstand\nApply\nAnalyze\nEvaluate\nCreate", "label": "Bloom's Level"},
        {"fieldname": "action_verbs", "fieldtype": "Small Text", "label": "Action Verbs Used"},

        {"fieldname": "section_mapping", "fieldtype": "Section Break", "label": "PEO Mapping"},
        {"fieldname": "peo_mapping", "fieldtype": "Table", "options": "PO PEO Mapping"},

        {"fieldname": "section_attainment", "fieldtype": "Section Break", "label": "Target Attainment"},
        {"fieldname": "target_attainment", "fieldtype": "Percent", "label": "Target Attainment %", "default": 60}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Instructor", "read": 1}
    ]
}
```

### 1.3 Course Outcome (CO) DocType

```json
{
    "doctype": "DocType",
    "name": "Course Outcome",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:{course}-CO-{co_number}",
    "fields": [
        {"fieldname": "course", "fieldtype": "Link", "options": "Course", "reqd": 1, "in_list_view": 1},
        {"fieldname": "co_number", "fieldtype": "Int", "label": "CO Number", "reqd": 1, "in_list_view": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "co_code", "fieldtype": "Data", "label": "CO Code", "read_only": 1},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "label": "Effective From"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nRevised\nArchived", "default": "Active"},

        {"fieldname": "section_co", "fieldtype": "Section Break", "label": "CO Statement"},
        {"fieldname": "co_statement", "fieldtype": "Text", "label": "CO Statement", "reqd": 1, "in_list_view": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Detailed Description"},

        {"fieldname": "section_bloom", "fieldtype": "Section Break", "label": "Bloom's Taxonomy"},
        {"fieldname": "bloom_level", "fieldtype": "Select", "options": "Remember\nUnderstand\nApply\nAnalyze\nEvaluate\nCreate", "label": "Bloom's Level", "reqd": 1, "in_list_view": 1},
        {"fieldname": "bloom_level_number", "fieldtype": "Int", "label": "Level (1-6)", "read_only": 1},
        {"fieldname": "action_verb", "fieldtype": "Data", "label": "Action Verb"},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "knowledge_dimension", "fieldtype": "Select", "options": "Factual\nConceptual\nProcedural\nMetacognitive", "label": "Knowledge Dimension"},

        {"fieldname": "section_syllabus", "fieldtype": "Section Break", "label": "Syllabus Mapping"},
        {"fieldname": "syllabus_units", "fieldtype": "Small Text", "label": "Covered Units/Modules"},
        {"fieldname": "topics_covered", "fieldtype": "Text", "label": "Topics Covered"},

        {"fieldname": "section_assessment", "fieldtype": "Section Break", "label": "Assessment"},
        {"fieldname": "assessment_methods", "fieldtype": "MultiSelect", "options": "Written Exam\nAssignment\nQuiz\nProject\nLab Work\nPresentation\nViva\nMid-term\nEnd-term", "label": "Assessment Methods"},
        {"fieldname": "weightage", "fieldtype": "Percent", "label": "Weightage in Course"},

        {"fieldname": "section_attainment", "fieldtype": "Section Break", "label": "Target Attainment"},
        {"fieldname": "target_attainment", "fieldtype": "Percent", "label": "Target Attainment %", "default": 60}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Instructor", "read": 1, "write": 1, "create": 1}
    ]
}
```

**Python Controller:**
```python
# university_erp/university_erp/doctype/course_outcome/course_outcome.py
import frappe
from frappe.model.document import Document

class CourseOutcome(Document):
    def validate(self):
        self.set_co_code()
        self.set_bloom_level_number()

    def set_co_code(self):
        """Generate CO code"""
        course_code = frappe.db.get_value("Course", self.course, "course_code") or self.course[:6]
        self.co_code = f"{course_code}.CO{self.co_number}"

    def set_bloom_level_number(self):
        """Set numeric Bloom's level"""
        levels = {
            "Remember": 1,
            "Understand": 2,
            "Apply": 3,
            "Analyze": 4,
            "Evaluate": 5,
            "Create": 6
        }
        self.bloom_level_number = levels.get(self.bloom_level, 1)


@frappe.whitelist()
def get_course_outcomes(course):
    """Get all COs for a course"""
    return frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_number", "co_code", "co_statement", "bloom_level", "target_attainment"],
        order_by="co_number"
    )
```

---

## Week 2: CO-PO Mapping

### 2.1 CO PO Mapping DocType

```json
{
    "doctype": "DocType",
    "name": "CO PO Mapping",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:{course}-{academic_term}-COPOM",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "course", "fieldtype": "Link", "options": "Course", "reqd": 1, "in_list_view": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "reqd": 1, "in_list_view": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year"},
        {"fieldname": "prepared_by", "fieldtype": "Link", "options": "Employee", "label": "Prepared By"},
        {"fieldname": "approved_by", "fieldtype": "Link", "options": "Employee", "label": "Approved By"},

        {"fieldname": "section_mapping", "fieldtype": "Section Break", "label": "CO-PO Correlation Matrix"},
        {"fieldname": "mapping_table", "fieldtype": "Table", "options": "CO PO Mapping Entry", "reqd": 1},

        {"fieldname": "section_justification", "fieldtype": "Section Break", "label": "Justification"},
        {"fieldname": "mapping_justification", "fieldtype": "Text Editor", "label": "Mapping Justification"},

        {"fieldname": "section_stats", "fieldtype": "Section Break", "label": "Statistics"},
        {"fieldname": "avg_correlation", "fieldtype": "Float", "label": "Average Correlation", "read_only": 1},
        {"fieldname": "strong_correlations", "fieldtype": "Int", "label": "Strong Correlations (3)", "read_only": 1},
        {"fieldname": "moderate_correlations", "fieldtype": "Int", "label": "Moderate Correlations (2)", "read_only": 1},
        {"fieldname": "weak_correlations", "fieldtype": "Int", "label": "Weak Correlations (1)", "read_only": 1}
    ],
    "permissions": [
        {"role": "Instructor", "read": 1, "write": 1, "create": 1, "submit": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}
    ]
}
```

### 2.2 CO PO Mapping Entry (Child Table)

```json
{
    "doctype": "DocType",
    "name": "CO PO Mapping Entry",
    "module": "University ERP",
    "istable": 1,
    "fields": [
        {"fieldname": "course_outcome", "fieldtype": "Link", "options": "Course Outcome", "reqd": 1, "in_list_view": 1},
        {"fieldname": "co_statement", "fieldtype": "Data", "fetch_from": "course_outcome.co_statement", "read_only": 1},
        {"fieldname": "program_outcome", "fieldtype": "Link", "options": "Program Outcome", "reqd": 1, "in_list_view": 1},
        {"fieldname": "po_code", "fieldtype": "Data", "fetch_from": "program_outcome.po_code", "read_only": 1, "in_list_view": 1},
        {"fieldname": "correlation_level", "fieldtype": "Select", "options": "0 - No Correlation\n1 - Low\n2 - Medium\n3 - High", "reqd": 1, "in_list_view": 1},
        {"fieldname": "justification", "fieldtype": "Small Text", "label": "Justification"}
    ]
}
```

**Python Controller:**
```python
# university_erp/university_erp/doctype/co_po_mapping/co_po_mapping.py
import frappe
from frappe.model.document import Document

class COPOMapping(Document):
    def validate(self):
        self.calculate_statistics()

    def calculate_statistics(self):
        """Calculate mapping statistics"""
        if not self.mapping_table:
            return

        total = 0
        count = 0
        strong = moderate = weak = 0

        for entry in self.mapping_table:
            level = int(entry.correlation_level.split(" - ")[0]) if entry.correlation_level else 0
            if level > 0:
                total += level
                count += 1
                if level == 3:
                    strong += 1
                elif level == 2:
                    moderate += 1
                elif level == 1:
                    weak += 1

        self.avg_correlation = round(total / count, 2) if count else 0
        self.strong_correlations = strong
        self.moderate_correlations = moderate
        self.weak_correlations = weak


@frappe.whitelist()
def generate_mapping_matrix(course, program, academic_term):
    """Generate CO-PO mapping matrix template"""
    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_code", "co_statement"],
        order_by="co_number"
    )

    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_code", "po_title"],
        order_by="po_number"
    )

    return {
        "course_outcomes": cos,
        "program_outcomes": pos
    }


@frappe.whitelist()
def get_co_po_matrix(course, academic_term):
    """Get CO-PO correlation matrix for display"""
    mapping = frappe.get_doc("CO PO Mapping", {"course": course, "academic_term": academic_term})

    if not mapping:
        return None

    # Build matrix
    matrix = {}
    for entry in mapping.mapping_table:
        co = entry.course_outcome
        po = entry.po_code
        level = int(entry.correlation_level.split(" - ")[0]) if entry.correlation_level else 0

        if co not in matrix:
            matrix[co] = {}
        matrix[co][po] = level

    return matrix
```

---

## Week 3: Attainment Calculation

### 3.1 CO Attainment DocType

```json
{
    "doctype": "DocType",
    "name": "CO Attainment",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:COA-{course}-{academic_term}",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "course", "fieldtype": "Link", "options": "Course", "reqd": 1, "in_list_view": 1},
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "reqd": 1, "in_list_view": 1},
        {"fieldname": "student_group", "fieldtype": "Link", "options": "Student Group"},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "instructor", "fieldtype": "Link", "options": "Employee"},
        {"fieldname": "calculation_date", "fieldtype": "Date", "default": "Today"},
        {"fieldname": "total_students", "fieldtype": "Int", "label": "Total Students", "read_only": 1},

        {"fieldname": "section_direct", "fieldtype": "Section Break", "label": "Direct Attainment (70%)"},
        {"fieldname": "direct_attainment_table", "fieldtype": "Table", "options": "CO Direct Attainment"},
        {"fieldname": "direct_weight", "fieldtype": "Percent", "label": "Direct Weight", "default": 70},

        {"fieldname": "section_indirect", "fieldtype": "Section Break", "label": "Indirect Attainment (30%)"},
        {"fieldname": "indirect_attainment_table", "fieldtype": "Table", "options": "CO Indirect Attainment"},
        {"fieldname": "indirect_weight", "fieldtype": "Percent", "label": "Indirect Weight", "default": 30},

        {"fieldname": "section_final", "fieldtype": "Section Break", "label": "Final CO Attainment"},
        {"fieldname": "final_attainment_table", "fieldtype": "Table", "options": "CO Final Attainment"},

        {"fieldname": "section_summary", "fieldtype": "Section Break", "label": "Summary"},
        {"fieldname": "overall_attainment", "fieldtype": "Percent", "label": "Overall CO Attainment", "read_only": 1},
        {"fieldname": "cos_achieved", "fieldtype": "Int", "label": "COs Achieved", "read_only": 1},
        {"fieldname": "total_cos", "fieldtype": "Int", "label": "Total COs", "read_only": 1}
    ],
    "permissions": [
        {"role": "Instructor", "read": 1, "write": 1, "create": 1, "submit": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}
    ]
}
```

### 3.2 CO Direct Attainment (Child Table)

```json
{
    "doctype": "DocType",
    "name": "CO Direct Attainment",
    "module": "University ERP",
    "istable": 1,
    "fields": [
        {"fieldname": "course_outcome", "fieldtype": "Link", "options": "Course Outcome", "reqd": 1, "in_list_view": 1},
        {"fieldname": "co_code", "fieldtype": "Data", "fetch_from": "course_outcome.co_code", "read_only": 1},
        {"fieldname": "assessment_type", "fieldtype": "Select", "options": "Internal\nMid-term\nEnd-term\nAssignment\nQuiz\nLab\nProject", "in_list_view": 1},
        {"fieldname": "max_marks", "fieldtype": "Float", "label": "Max Marks", "in_list_view": 1},
        {"fieldname": "target_percent", "fieldtype": "Percent", "label": "Target %", "default": 60},
        {"fieldname": "students_above_target", "fieldtype": "Int", "label": "Students Above Target"},
        {"fieldname": "total_students", "fieldtype": "Int", "label": "Total Students"},
        {"fieldname": "attainment_percent", "fieldtype": "Percent", "label": "Attainment %", "read_only": 1, "in_list_view": 1},
        {"fieldname": "attainment_level", "fieldtype": "Float", "label": "Level (0-3)", "read_only": 1}
    ]
}
```

### 3.3 PO Attainment DocType

```json
{
    "doctype": "DocType",
    "name": "PO Attainment",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:POA-{program}-{academic_year}",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1, "in_list_view": 1},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "reqd": 1, "in_list_view": 1},
        {"fieldname": "batch", "fieldtype": "Link", "options": "Student Batch Name"},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "calculation_date", "fieldtype": "Date", "default": "Today"},
        {"fieldname": "prepared_by", "fieldtype": "Link", "options": "Employee"},

        {"fieldname": "section_direct", "fieldtype": "Section Break", "label": "Direct PO Attainment"},
        {"fieldname": "direct_po_attainment", "fieldtype": "Table", "options": "PO Attainment Entry"},

        {"fieldname": "section_indirect", "fieldtype": "Section Break", "label": "Indirect PO Attainment"},
        {"fieldname": "indirect_po_attainment", "fieldtype": "Table", "options": "PO Indirect Entry"},

        {"fieldname": "section_final", "fieldtype": "Section Break", "label": "Final PO Attainment"},
        {"fieldname": "final_po_attainment", "fieldtype": "Table", "options": "PO Final Entry"},

        {"fieldname": "section_summary", "fieldtype": "Section Break", "label": "Summary"},
        {"fieldname": "pos_achieved", "fieldtype": "Int", "label": "POs Achieved", "read_only": 1},
        {"fieldname": "total_pos", "fieldtype": "Int", "label": "Total POs", "read_only": 1},
        {"fieldname": "overall_attainment", "fieldtype": "Percent", "label": "Overall PO Attainment", "read_only": 1}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}
    ]
}
```

**Attainment Calculation Functions:**
```python
# university_erp/university_erp/obe/attainment.py
import frappe
from frappe.utils import flt

def calculate_co_attainment(course, academic_term, student_group=None):
    """Calculate CO attainment from assessment results"""

    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_code", "co_number", "target_attainment"]
    )

    # Get assessment results
    filters = {
        "course": course,
        "docstatus": 1
    }

    if student_group:
        # Get students in group
        students = frappe.get_all(
            "Student Group Student",
            filters={"parent": student_group},
            pluck="student"
        )
        filters["student"] = ["in", students]

    results = frappe.get_all(
        "Assessment Result",
        filters=filters,
        fields=["student", "total_score", "maximum_score", "assessment_plan"]
    )

    attainment_data = []
    total_students = len(set(r.student for r in results))

    for co in cos:
        target_percent = co.target_attainment or 60

        # Count students above target for this CO
        # (In real implementation, CO-wise marks would be tracked)
        students_above = sum(
            1 for r in results
            if (r.total_score / r.maximum_score * 100) >= target_percent
        )

        attainment_percent = (students_above / total_students * 100) if total_students else 0

        # Calculate attainment level (0-3 scale)
        if attainment_percent >= 70:
            level = 3
        elif attainment_percent >= 55:
            level = 2
        elif attainment_percent >= 40:
            level = 1
        else:
            level = 0

        attainment_data.append({
            "course_outcome": co.name,
            "co_code": co.co_code,
            "target_percent": target_percent,
            "students_above_target": students_above,
            "total_students": total_students,
            "attainment_percent": round(attainment_percent, 2),
            "attainment_level": level
        })

    return attainment_data


def calculate_po_attainment(program, academic_year):
    """Calculate PO attainment from CO attainments"""

    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_code", "po_number", "target_attainment"]
    )

    # Get all CO-PO mappings for this program
    mappings = frappe.db.sql("""
        SELECT
            cpm.course,
            cpme.course_outcome,
            cpme.program_outcome,
            cpme.correlation_level,
            coa.attainment_level
        FROM `tabCO PO Mapping` cpm
        JOIN `tabCO PO Mapping Entry` cpme ON cpme.parent = cpm.name
        LEFT JOIN `tabCO Attainment` coa ON coa.course = cpm.course
        WHERE cpm.program = %s
        AND cpm.docstatus = 1
    """, (program,), as_dict=True)

    po_attainment = {}

    for po in pos:
        # Get all COs mapped to this PO
        po_mappings = [m for m in mappings if m.program_outcome == po.name]

        if not po_mappings:
            continue

        weighted_sum = 0
        weight_total = 0

        for m in po_mappings:
            correlation = int(m.correlation_level.split(" - ")[0]) if m.correlation_level else 0
            attainment = m.attainment_level or 0

            weighted_sum += correlation * attainment
            weight_total += correlation

        po_level = round(weighted_sum / weight_total, 2) if weight_total else 0
        po_percent = (po_level / 3) * 100

        po_attainment[po.name] = {
            "po_code": po.po_code,
            "attainment_level": po_level,
            "attainment_percent": round(po_percent, 2),
            "target": po.target_attainment or 60,
            "achieved": po_percent >= (po.target_attainment or 60)
        }

    return po_attainment


@frappe.whitelist()
def generate_attainment_report(program, academic_year):
    """Generate comprehensive attainment report"""
    po_data = calculate_po_attainment(program, academic_year)

    achieved = sum(1 for p in po_data.values() if p["achieved"])
    total = len(po_data)

    return {
        "program": program,
        "academic_year": academic_year,
        "po_attainment": po_data,
        "pos_achieved": achieved,
        "total_pos": total,
        "overall_attainment": round((achieved / total * 100), 2) if total else 0
    }
```

---

## Week 4: Reports & Alumni Survey

### 4.1 OBE Reports

**CO-PO Attainment Matrix Report:**
```python
# university_erp/university_erp/report/co_po_attainment_matrix/co_po_attainment_matrix.py
import frappe

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns(filters):
    columns = [
        {"fieldname": "co_code", "label": "CO", "fieldtype": "Data", "width": 100},
        {"fieldname": "co_statement", "label": "CO Statement", "fieldtype": "Data", "width": 250}
    ]

    # Add PO columns dynamically
    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": filters.get("program"), "status": "Active"},
        fields=["po_code"],
        order_by="po_number"
    )

    for po in pos:
        columns.append({
            "fieldname": po.po_code,
            "label": po.po_code,
            "fieldtype": "Int",
            "width": 60
        })

    columns.append({"fieldname": "avg_correlation", "label": "Avg", "fieldtype": "Float", "width": 60})

    return columns

def get_data(filters):
    mappings = frappe.get_all(
        "CO PO Mapping Entry",
        filters={"parenttype": "CO PO Mapping"},
        fields=["course_outcome", "program_outcome", "correlation_level", "parent"]
    )

    # Build data rows
    data = []
    # ... implementation
    return data

def get_chart(data):
    return {
        "type": "heatmap",
        "title": "CO-PO Correlation Matrix"
    }
```

**Program Attainment Report:**
```python
# university_erp/university_erp/report/program_attainment_report/program_attainment_report.py
def execute(filters=None):
    columns = [
        {"fieldname": "po_code", "label": "PO", "fieldtype": "Data", "width": 80},
        {"fieldname": "po_title", "label": "PO Statement", "fieldtype": "Data", "width": 250},
        {"fieldname": "target", "label": "Target %", "fieldtype": "Percent", "width": 100},
        {"fieldname": "direct_attainment", "label": "Direct (70%)", "fieldtype": "Percent", "width": 100},
        {"fieldname": "indirect_attainment", "label": "Indirect (30%)", "fieldtype": "Percent", "width": 100},
        {"fieldname": "final_attainment", "label": "Final %", "fieldtype": "Percent", "width": 100},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100}
    ]

    data = []
    # ... implementation with calculation
    return columns, data
```

### 4.2 Alumni/Employer Survey DocType

```json
{
    "doctype": "DocType",
    "name": "OBE Survey",
    "module": "University ERP",
    "naming_rule": "Expression",
    "autoname": "expr:SRV-.YYYY.-.#####",
    "fields": [
        {"fieldname": "survey_type", "fieldtype": "Select", "options": "Alumni\nEmployer\nStudent Exit\nCourse End", "reqd": 1, "in_list_view": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year"},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "survey_date", "fieldtype": "Date", "default": "Today"},
        {"fieldname": "respondent_name", "fieldtype": "Data", "label": "Respondent Name"},
        {"fieldname": "respondent_email", "fieldtype": "Data", "label": "Email"},

        {"fieldname": "section_po", "fieldtype": "Section Break", "label": "PO Attainment Rating"},
        {"fieldname": "po_ratings", "fieldtype": "Table", "options": "Survey PO Rating"},

        {"fieldname": "section_feedback", "fieldtype": "Section Break", "label": "General Feedback"},
        {"fieldname": "overall_satisfaction", "fieldtype": "Rating", "label": "Overall Satisfaction"},
        {"fieldname": "strengths", "fieldtype": "Text", "label": "Program Strengths"},
        {"fieldname": "improvements", "fieldtype": "Text", "label": "Suggested Improvements"},
        {"fieldname": "additional_comments", "fieldtype": "Text", "label": "Additional Comments"}
    ],
    "permissions": [
        {"role": "Guest", "read": 1, "write": 1, "create": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "delete": 1}
    ]
}
```

---

## Output Checklist

### DocTypes Created
- [x] Program Educational Objective (PEO) ✅
- [x] Program Outcome (PO) ✅
- [x] PO PEO Mapping (child table) ✅
- [x] Course Outcome (CO) ✅
- [x] CO PO Mapping ✅
- [x] CO PO Mapping Entry (child table) ✅
- [x] CO Attainment ✅
- [x] CO Direct Attainment (child table) ✅
- [x] CO Indirect Attainment (child table) ✅
- [x] CO Final Attainment (child table) ✅
- [x] PO Attainment ✅
- [x] PO Attainment Entry (child table) ✅
- [x] PO Indirect Entry (child table) ✅ *(additional)*
- [x] PO Final Entry (child table) ✅ *(additional)*
- [x] OBE Survey ✅
- [x] Survey PO Rating (child table) ✅
- [x] Survey Question Item (child table) ✅ *(additional)*
- [x] Survey Template ✅ *(additional)*

### Reports Created
- [x] CO-PO Mapping Matrix ✅
- [x] CO Attainment Report ✅
- [x] PO Attainment Report ✅
- [x] Program Attainment Summary ✅
- [x] Survey Analysis Report ✅

### API Endpoints
- [x] get_course_outcomes() ✅
- [x] generate_mapping_matrix() ✅
- [x] calculate_co_attainment() ✅
- [x] calculate_po_attainment() ✅
- [x] generate_attainment_report() ✅
- [x] populate_mapping_entries() ✅ *(additional)*
- [x] calculate_direct_attainment() ✅ *(additional)*
- [x] calculate_indirect_attainment() ✅ *(additional)*
- [x] calculate_all_attainments() ✅ *(additional)*
- [x] populate_course_outcomes() ✅ *(additional)*
- [x] fetch_assessment_results() ✅ *(additional)*
- [x] calculate_from_co_attainments() ✅ *(additional)*
- [x] populate_program_outcomes() ✅ *(additional)*
- [x] fetch_survey_attainments() ✅ *(additional)*
- [x] calculate_all_po_attainments() ✅ *(additional)*
- [x] get_survey_form() ✅ *(additional - guest access)*
- [x] submit_survey() ✅ *(additional - guest access)*
- [x] get_survey_statistics() ✅ *(additional)*
- [x] get_program_surveys() ✅ *(additional)*

### Integrations
- [x] Assessment Result → CO Attainment calculation ✅
- [x] CO Attainment → PO Attainment rollup ✅
- [x] Survey responses → Indirect attainment ✅
- [x] CO-PO Mapping → Attainment weighting ✅ *(additional)*
- [x] NBA/NAAC Compliance Scoring ✅ *(additional)*

---

## Estimated Timeline

| Week | Focus Area | Deliverables |
|------|-----------|--------------|
| 1 | Outcome Definitions | PEO, PO, CO DocTypes |
| 2 | CO-PO Mapping | Mapping DocType, Matrix generation |
| 3 | Attainment Calculation | CO & PO Attainment, Calculation logic |
| 4 | Reports & Survey | Reports, Alumni/Employer survey |

**Total Duration: 3-4 weeks**

---

## Implementation Summary

### ✅ Phase 11 Complete - January 2026

**Implementation Statistics:**
- **Total DocTypes:** 18 (10 regular + 8 child tables)
- **Submittable DocTypes:** 3 (CO PO Mapping, CO Attainment, PO Attainment)
- **Script Reports:** 5 (with charts and formatters)
- **API Endpoints:** 19 whitelisted functions
- **Total Files Created:** 73

**Module Location:** `university_erp/university_obe/`

### Key Implementation Highlights

#### Bloom's Taxonomy Integration
- 6 cognitive levels: Remember, Understand, Apply, Analyze, Evaluate, Create
- Knowledge dimensions: Factual, Conceptual, Procedural, Metacognitive
- Auto-calculation of level numbers (1-6)

#### NBA Graduate Attributes (12)
1. Engineering Knowledge
2. Problem Analysis
3. Design/Development of Solutions
4. Conduct Investigations
5. Modern Tool Usage
6. Engineer and Society
7. Environment and Sustainability
8. Ethics
9. Individual and Team Work
10. Communication
11. Project Management and Finance
12. Life-long Learning

#### Attainment Calculation Logic
- **CO Attainment:** Direct (70%) + Indirect (30%)
- **PO Attainment:** Direct (80%) + Indirect (20%)
- **Attainment Levels:** 0-3 scale based on percentage thresholds
  - Level 3: ≥70%
  - Level 2: 60-69%
  - Level 1: 50-59%
  - Level 0: <50%

#### Survey System
- 4 Survey types: Alumni, Employer, Student Exit, Course End
- Guest-accessible APIs for external survey submission
- Survey templates for standardized questions
- Automatic statistics calculation

#### Compliance Scoring
- NBA Compliance Score: Based on PO1-PO12 achievement
- NAAC Compliance Score: Based on all outcomes including PSOs
- Real-time calculation on document save

### Workspace
- University OBE workspace with shortcuts, links, and reports
- Quick access to New PEO, PO, CO, and CO-PO Mapping
- Organized sections for Outcome Definitions, Mapping, Attainment, and Surveys

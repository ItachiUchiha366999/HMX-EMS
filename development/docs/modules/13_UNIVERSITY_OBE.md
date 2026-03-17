# University OBE Module

## Overview

The University OBE (Outcome-Based Education) module implements outcome measurement and attainment tracking for accreditation purposes (NAAC/NBA). It manages Course Outcomes (CO), Program Outcomes (PO), Program Educational Objectives (PEO), and their attainment calculations.

## Module Location
```
university_erp/university_obe/
```

## DocTypes (18 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Program Educational Objective | Main | Program-level objectives |
| Program Outcome | Main | Graduate attributes |
| PO PEO Mapping | Main | PO to PEO alignment |
| Course Outcome | Main | Course-level outcomes |
| CO PO Mapping | Main | CO to PO alignment |
| CO PO Mapping Entry | Child | Individual mapping |
| CO Direct Attainment | Main | Direct assessment attainment |
| CO Indirect Attainment | Main | Survey-based attainment |
| CO Final Attainment | Main | Combined CO attainment |
| CO Attainment | Main | Overall CO calculation |
| PO Attainment | Main | Program outcome attainment |
| PO Attainment Entry | Child | PO-wise values |
| PO Indirect Entry | Child | Indirect PO values |
| PO Final Entry | Child | Final PO values |
| Survey Template | Main | Survey design |
| Survey Question Item | Child | Survey questions |
| OBE Survey | Main | Published surveys |
| Survey PO Rating | Child | PO ratings from survey |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                      UNIVERSITY OBE MODULE                        |
+------------------------------------------------------------------+
|                                                                   |
|  +---------------------+                                          |
|  | Program Educational |                                          |
|  |    Objectives (PEO) |                                          |
|  +---------------------+                                          |
|           ^                                                       |
|           | (PO-PEO Mapping)                                      |
|           |                                                       |
|  +---------------------+                                          |
|  |  Program Outcomes   |                                          |
|  |        (PO)         |                                          |
|  +---------------------+                                          |
|           ^                                                       |
|           | (CO-PO Mapping)                                       |
|           |                                                       |
|  +---------------------+       +---------------------+            |
|  |  Course Outcomes    |<------|   EDUCATION APP    |            |
|  |        (CO)         |       |      Course        |            |
|  +---------------------+       +---------------------+            |
|           |                                                       |
|           +------------------+------------------+                  |
|           |                  |                  |                  |
|           v                  v                  v                  |
|  +-------------+     +-------------+     +-------------+          |
|  |CO DIRECT    |     |CO INDIRECT  |     |CO FINAL     |          |
|  |ATTAINMENT   |     |ATTAINMENT   |     |ATTAINMENT   |          |
|  +-------------+     +-------------+     +-------------+          |
|  | From:       |     | From:       |     | Combined:   |          |
|  | - Exams     |     | - Surveys   |     | 80% Direct  |          |
|  | - Assignments|    | - Feedback  |     | 20% Indirect|          |
|  +-------------+     +-------------+     +-------------+          |
|                              |                                    |
|                              v                                    |
|                    +-------------------+                          |
|                    |   PO ATTAINMENT   |                          |
|                    +-------------------+                          |
|                    | Calculated from   |                          |
|                    | all course COs    |                          |
|                    +-------------------+                          |
|                                                                   |
+------------------------------------------------------------------+
```

## OBE Hierarchy

```
+------------------------------------------------------------------+
|                         OBE HIERARCHY                             |
+------------------------------------------------------------------+
|                                                                   |
|  INSTITUTIONAL LEVEL                                              |
|  +---------------------+                                          |
|  |   Vision & Mission  |                                          |
|  +---------------------+                                          |
|           |                                                       |
|           v                                                       |
|  PROGRAM LEVEL                                                    |
|  +---------------------+       +---------------------+            |
|  | PEO (3-5)           |<----->| PO (12 Graduate     |            |
|  | Program Educational |       |    Attributes)      |            |
|  | Objectives          |       +---------------------+            |
|  +---------------------+                                          |
|           |                           |                           |
|           |                           |                           |
|  COURSE LEVEL                         |                           |
|  +---------------------+              |                           |
|  | CO (4-6 per course) |<-------------+                           |
|  | Course Outcomes     |   (CO-PO Mapping)                        |
|  +---------------------+                                          |
|           |                                                       |
|           v                                                       |
|  ASSESSMENT LEVEL                                                 |
|  +---------------------+       +---------------------+            |
|  | Direct Assessment   |       | Indirect Assessment |            |
|  | - Exams             |       | - Course End Survey |            |
|  | - Assignments       |       | - Exit Survey       |            |
|  | - Quizzes           |       | - Employer Survey   |            |
|  +---------------------+       +---------------------+            |
|                                                                   |
+------------------------------------------------------------------+
```

## DocType Details

### 1. Program Educational Objective (PEO)
**Purpose**: Define what graduates achieve 3-5 years after graduation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| peo_code | Data | e.g., "PEO1" |
| program | Link (Program) | Degree program |
| title | Data | Short title |
| description | Text | Detailed description |
| keywords | Data | Key terms |
| mapped_pos | Table MultiSelect | Related POs |

**Example PEOs** (B.Tech Computer Science):
- PEO1: Apply computing skills in industry/research
- PEO2: Lead teams with ethical responsibility
- PEO3: Pursue lifelong learning and adapt to technology changes

### 2. Program Outcome (PO)
**Purpose**: Define graduate attributes (12 NBA-defined outcomes)

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| po_code | Data | e.g., "PO1" |
| program | Link (Program) | Degree program |
| title | Data | e.g., "Engineering Knowledge" |
| description | Text | Detailed description |
| bloom_level | Select | Remember to Create |
| attainment_target | Float | Target level (usually 2.0-3.0) |

**Standard 12 POs** (NBA Engineering):
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
12. Lifelong Learning

### 3. PO PEO Mapping
**Purpose**: Map Program Outcomes to Program Educational Objectives

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| program | Link (Program) | Degree program |
| mapping_matrix | Table | PO to PEO correlation |

**Mapping Matrix**:
```
        | PEO1 | PEO2 | PEO3 |
--------|------|------|------|
PO1     |  3   |  1   |  2   |
PO2     |  3   |  2   |  1   |
PO3     |  2   |  1   |  3   |
...
(3 = High, 2 = Medium, 1 = Low, 0 = No mapping)
```

### 4. Course Outcome (CO)
**Purpose**: Define learning outcomes for each course

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| co_code | Data | e.g., "CO1" |
| course | Link (Course) | Academic course |
| academic_term | Link (Academic Term) | Semester |
| title | Data | CO statement |
| bloom_level | Select | Cognitive level |
| assessment_methods | Multi Select | How assessed |
| attainment_target | Float | Target level |

**Example COs** (Data Structures Course):
- CO1: Understand fundamental data structures
- CO2: Analyze time and space complexity
- CO3: Implement tree and graph algorithms
- CO4: Apply appropriate data structures to problems

### 5. CO PO Mapping
**Purpose**: Map Course Outcomes to Program Outcomes

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Course |
| academic_term | Link (Academic Term) | Semester |
| program | Link (Program) | Program |
| mapping_entries | Table | CO to PO correlations |

### 6. CO PO Mapping Entry (Child Table)
**Purpose**: Individual CO-PO correlation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course_outcome | Data | CO code |
| po1 | Int | Correlation (0-3) |
| po2 | Int | Correlation (0-3) |
| ... | Int | ... |
| po12 | Int | Correlation (0-3) |

### 7. CO Direct Attainment
**Purpose**: Calculate CO attainment from assessments

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Course |
| course_outcome | Link (Course Outcome) | CO |
| academic_term | Link (Academic Term) | Semester |
| student_group | Link (Student Group) | Section |
| assessment_type | Select | Exam/Assignment/Quiz |
| max_marks | Float | Maximum score |
| target_percentage | Float | Target % |
| students_above_target | Int | Count above target |
| total_students | Int | Total students |
| attainment_level | Float | Calculated level |

### 8. CO Indirect Attainment
**Purpose**: CO attainment from surveys

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Course |
| course_outcome | Link (Course Outcome) | CO |
| academic_term | Link (Academic Term) | Semester |
| survey | Link (OBE Survey) | Survey reference |
| average_rating | Float | Avg student rating |
| attainment_level | Float | Calculated level |

### 9. CO Final Attainment
**Purpose**: Combined CO attainment

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Course |
| course_outcome | Link (Course Outcome) | CO |
| academic_term | Link (Academic Term) | Semester |
| direct_attainment | Float | Direct component |
| indirect_attainment | Float | Indirect component |
| direct_weightage | Percent | Usually 80% |
| indirect_weightage | Percent | Usually 20% |
| final_attainment | Float | Weighted average |
| target | Float | Target level |
| is_achieved | Check | Target met |

### 10. PO Attainment
**Purpose**: Calculate Program Outcome attainment

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| program | Link (Program) | Degree program |
| academic_year | Link (Academic Year) | Year |
| batch | Data | Student batch |
| po_entries | Table | PO-wise attainment |
| indirect_entries | Table | From exit survey |
| final_entries | Table | Final values |

### 11-12. Survey DocTypes
**Purpose**: Collect indirect assessment data

**Survey Template Fields**:
| Field | Type | Description |
|-------|------|-------------|
| template_name | Data | Survey name |
| survey_type | Select | Course End/Exit/Employer |
| questions | Table | Question items |

**OBE Survey Fields**:
| Field | Type | Description |
|-------|------|-------------|
| survey_template | Link | Template |
| course | Link (Course) | If course survey |
| program | Link (Program) | If program survey |
| start_date | Date | Open date |
| end_date | Date | Close date |
| responses_count | Int | Submissions |

## Data Flow Diagrams

### CO Attainment Calculation
```
+------------------------------------------------------------------+
|               CO ATTAINMENT CALCULATION FLOW                      |
+------------------------------------------------------------------+
|                                                                   |
|  DIRECT ASSESSMENT (80%)                                          |
|  +-------------------+     +-------------------+                  |
|  | Assessment Result |---->| Calculate         |                  |
|  | - Exam marks      |     | % Above Target    |                  |
|  | - Assignment marks|     +-------------------+                  |
|  +-------------------+              |                             |
|                                     v                             |
|                            +-------------------+                  |
|                            | Attainment Level  |                  |
|                            | Level 3: >=70%    |                  |
|                            | Level 2: >=60%    |                  |
|                            | Level 1: >=50%    |                  |
|                            +-------------------+                  |
|                                     |                             |
|  INDIRECT ASSESSMENT (20%)          |                             |
|  +-------------------+              |                             |
|  | Course End Survey |              |                             |
|  | Student ratings   |              |                             |
|  | (1-5 scale)       |              |                             |
|  +-------------------+              |                             |
|           |                         |                             |
|           v                         v                             |
|  +-------------------+     +-------------------+                  |
|  | Survey Attainment |---->| FINAL CO          |                  |
|  | Avg rating to     |     | ATTAINMENT        |                  |
|  | level conversion  |     | = 0.8*Direct +    |                  |
|  +-------------------+     |   0.2*Indirect    |                  |
|                            +-------------------+                  |
|                                                                   |
+------------------------------------------------------------------+
```

### PO Attainment from COs
```
+------------------------------------------------------------------+
|                  PO ATTAINMENT CALCULATION                        |
+------------------------------------------------------------------+
|                                                                   |
|  Course 1        Course 2        Course 3        Course n         |
|  +--------+      +--------+      +--------+      +--------+       |
|  |CO1: 2.5|      |CO1: 2.8|      |CO1: 2.3|      |CO1: 2.6|       |
|  |CO2: 2.7|      |CO2: 2.5|      |CO2: 2.9|      |CO2: 2.4|       |
|  |CO3: 2.4|      |CO3: 2.6|      |CO3: 2.5|      |CO3: 2.7|       |
|  +--------+      +--------+      +--------+      +--------+       |
|       |              |              |              |               |
|       +------+-------+-------+------+-------+------+              |
|              |               |               |                    |
|              v               v               v                    |
|  +----------------------------------------------------------+    |
|  |         CO-PO MAPPING MATRIX (Weighted Average)           |    |
|  |                                                           |    |
|  |  For each PO:                                             |    |
|  |  PO_attainment = Sum(CO_attainment * mapping_weight) /    |    |
|  |                  Sum(mapping_weight)                      |    |
|  +----------------------------------------------------------+    |
|              |               |               |                    |
|              v               v               v                    |
|         +--------+      +--------+      +--------+                |
|         | PO1:   |      | PO2:   |      | PO12:  |                |
|         | 2.58   |      | 2.62   |      | 2.45   |                |
|         +--------+      +--------+      +--------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## Integration Points

### With Assessment Results
```python
# Calculate CO direct attainment from exam results
def calculate_co_direct_attainment(course, academic_term, course_outcome, assessment_type):
    """Calculate direct attainment for CO"""
    # Get all assessment results
    results = frappe.get_all("Assessment Result", {
        "course": course,
        "assessment_type": assessment_type,
        "academic_term": academic_term
    }, ["student", "total_score", "maximum_score"])

    # Get CO target percentage (usually 60%)
    target_percentage = frappe.db.get_value("Course Outcome", course_outcome, "attainment_target") or 60

    total_students = len(results)
    students_above_target = 0

    for result in results:
        percentage = (result.total_score / result.maximum_score) * 100
        if percentage >= target_percentage:
            students_above_target += 1

    # Calculate attainment level
    achievement_percentage = (students_above_target / total_students) * 100

    if achievement_percentage >= 70:
        attainment_level = 3
    elif achievement_percentage >= 60:
        attainment_level = 2
    elif achievement_percentage >= 50:
        attainment_level = 1
    else:
        attainment_level = 0

    # Create direct attainment record
    return create_co_direct_attainment(
        course, course_outcome, academic_term,
        assessment_type, attainment_level,
        students_above_target, total_students
    )
```

### With LMS Module
```python
# Quiz/Assignment scores feed into CO attainment
def sync_lms_to_co_attainment(lms_course, assessment_type):
    """Sync LMS assessment scores to CO attainment"""
    academic_course = frappe.db.get_value("LMS Course", lms_course, "course")

    if assessment_type == "quiz":
        scores = get_quiz_scores(lms_course)
    else:
        scores = get_assignment_scores(lms_course)

    # Map to course outcomes and calculate attainment
    course_outcomes = frappe.get_all("Course Outcome", {"course": academic_course})

    for co in course_outcomes:
        calculate_co_direct_attainment(
            academic_course,
            frappe.db.get_value("LMS Course", lms_course, "academic_term"),
            co.name,
            assessment_type
        )
```

### PO Attainment Calculation
```python
def calculate_po_attainment(program, academic_year, batch):
    """Calculate PO attainment from all course COs"""
    # Get all courses in program
    courses = get_program_courses(program, batch)

    # Initialize PO sums
    po_sums = {f"PO{i}": {"weighted_sum": 0, "weight_sum": 0} for i in range(1, 13)}

    for course in courses:
        # Get CO-PO mapping
        mapping = frappe.get_doc("CO PO Mapping", {"course": course})

        # Get CO final attainments
        co_attainments = frappe.get_all("CO Final Attainment", {
            "course": course
        }, ["course_outcome", "final_attainment"])

        for co_att in co_attainments:
            # Get mapping entry for this CO
            mapping_entry = get_mapping_entry(mapping, co_att.course_outcome)

            for i in range(1, 13):
                weight = getattr(mapping_entry, f"po{i}") or 0
                if weight > 0:
                    po_sums[f"PO{i}"]["weighted_sum"] += co_att.final_attainment * weight
                    po_sums[f"PO{i}"]["weight_sum"] += weight

    # Calculate final PO attainments
    po_attainments = {}
    for po, values in po_sums.items():
        if values["weight_sum"] > 0:
            po_attainments[po] = values["weighted_sum"] / values["weight_sum"]
        else:
            po_attainments[po] = 0

    return po_attainments
```

## API Endpoints

### CO Management
```python
@frappe.whitelist()
def get_course_outcomes(course):
    """Get all COs for a course"""
    return frappe.get_all("Course Outcome", {
        "course": course
    }, ["*"])

@frappe.whitelist()
def get_co_attainment_status(course, academic_term):
    """Get CO attainment status for course"""
    cos = frappe.get_all("Course Outcome", {"course": course})

    attainment_data = []
    for co in cos:
        final = frappe.get_value("CO Final Attainment", {
            "course": course,
            "course_outcome": co.name,
            "academic_term": academic_term
        }, ["final_attainment", "target", "is_achieved"])

        attainment_data.append({
            "co": co.name,
            "co_code": co.co_code,
            "attainment": final[0] if final else 0,
            "target": final[1] if final else 2.0,
            "achieved": final[2] if final else False
        })

    return attainment_data
```

### PO Attainment
```python
@frappe.whitelist()
def get_po_attainment(program, academic_year):
    """Get PO attainment for program"""
    po_att = frappe.get_doc("PO Attainment", {
        "program": program,
        "academic_year": academic_year
    })

    return {
        "direct": {e.po: e.attainment for e in po_att.po_entries},
        "indirect": {e.po: e.attainment for e in po_att.indirect_entries},
        "final": {e.po: e.attainment for e in po_att.final_entries}
    }
```

## Reports

1. **CO Attainment Report** - Course-wise CO attainment
2. **PO Attainment Report** - Program-wise PO status
3. **CO-PO Mapping Matrix** - Visual correlation matrix
4. **Gap Analysis Report** - COs/POs below target
5. **Attainment Trend** - Year-over-year improvement
6. **NBA SAR Data** - Self Assessment Report data

## Related Files

```
university_erp/
+-- university_obe/
    +-- doctype/
    |   +-- program_educational_objective/
    |   +-- program_outcome/
    |   +-- po_peo_mapping/
    |   +-- course_outcome/
    |   +-- co_po_mapping/
    |   +-- co_po_mapping_entry/
    |   +-- co_direct_attainment/
    |   +-- co_indirect_attainment/
    |   +-- co_final_attainment/
    |   +-- co_attainment/
    |   +-- po_attainment/
    |   +-- po_attainment_entry/
    |   +-- po_indirect_entry/
    |   +-- po_final_entry/
    |   +-- survey_template/
    |   +-- survey_question_item/
    |   +-- obe_survey/
    |   +-- survey_po_rating/
    +-- api.py
    +-- attainment_calculator.py
```

## See Also

- [Examinations Module](04_EXAMINATIONS.md)
- [University LMS Module](11_UNIVERSITY_LMS.md)
- [Academics Module](01_ACADEMICS.md)

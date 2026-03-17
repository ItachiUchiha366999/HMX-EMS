# Admissions Module

## Overview

The Admissions module manages the complete student admission lifecycle from application to enrollment. It extends the Education app's Student Applicant functionality with merit list generation, seat matrix management, and admission cycle tracking.

## Module Location
```
university_erp/admissions/
```

## DocTypes (6 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Admission Cycle | Main | Academic year admission period |
| Admission Cycle Program | Child | Programs offered in cycle |
| Seat Matrix | Main | Category-wise seat allocation |
| Merit List | Main | Ranked applicant lists |
| Merit List Applicant | Child | Individual applicant in list |
| Admission Criteria | Main | Eligibility rules |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                      ADMISSIONS MODULE                            |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+                                            |
|  |  ADMISSION CYCLE  |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           +------------------+                                    |
|           |                  |                                    |
|           v                  v                                    |
|  +-------------------+  +-------------------+                     |
|  | Admission Cycle   |  |   SEAT MATRIX     |                     |
|  |    Program        |  +-------------------+                     |
|  | (Child Table)     |         |                                  |
|  +-------------------+         |                                  |
|           |                    |                                  |
|           v                    v                                  |
|  +-------------------+  +-------------------+                     |
|  | Student Applicant |  |    MERIT LIST     |                     |
|  | (Education App)   |  +-------------------+                     |
|  +-------------------+         |                                  |
|           |                    v                                  |
|           |            +-------------------+                      |
|           |            | Merit List        |                      |
|           |            |   Applicant       |                      |
|           |            | (Child Table)     |                      |
|           |            +-------------------+                      |
|           |                    |                                  |
|           +--------------------+                                  |
|                    |                                              |
|                    v                                              |
|           +-------------------+                                   |
|           |     STUDENT       |                                   |
|           | (Education App)   |                                   |
|           +-------------------+                                   |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Dependencies on Education App
```
+-------------------+       +-------------------+
|    ADMISSIONS     |       |    EDUCATION      |
|     (Custom)      |------>|      (App)        |
+-------------------+       +-------------------+
| Admission Cycle   |       | Student Applicant |
| extends-----------|------>| (Override class)  |
|                   |       |                   |
| Merit List        |       | Program           |
| references--------|------>| Academic Year     |
|                   |       |                   |
| Enrollment        |       | Student           |
| creates-----------|------>| (final record)    |
+-------------------+       +-------------------+
```

### Admissions Flow
```
+------------------+     +------------------+     +------------------+
| ADMISSION CYCLE  |---->| STUDENT          |---->|   MERIT LIST     |
|                  |     | APPLICANT        |     |                  |
| - Open/Close     |     | (Education App)  |     | - Generate       |
| - Programs       |     | - Extended fields|     | - Publish        |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
                         +------------------+     +------------------+
                         |     STUDENT      |<----|   SEAT MATRIX    |
                         | (Education App)  |     |                  |
                         | - Enrolled       |     | - Allocate       |
                         +------------------+     +------------------+
```

## DocType Details

### 1. Admission Cycle
**Purpose**: Defines an admission period with programs and dates

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| cycle_name | Data | e.g., "2024-25 Admissions" |
| academic_year | Link (Academic Year) | Target year |
| start_date | Date | Cycle start |
| end_date | Date | Cycle end |
| application_start | Date | Applications open |
| application_end | Date | Applications close |
| programs | Table | Programs offered |
| status | Select | Draft/Open/Closed |

**Workflow**:
```
Draft --> Open (Applications Active) --> Closed (Processing)
                                              |
                                              v
                                         Merit Lists
                                         Generated
```

### 2. Admission Cycle Program (Child Table)
**Purpose**: Program-specific admission settings

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| program | Link (Program) | Degree program |
| intake | Int | Total seats |
| entrance_exam | Data | Required exam |
| minimum_score | Float | Cutoff score |
| fees | Currency | Program fees |

### 3. Seat Matrix
**Purpose**: Category-wise seat allocation per program

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| admission_cycle | Link | Admission cycle |
| program | Link (Program) | Degree program |
| total_seats | Int | Total intake |
| general_seats | Int | General category |
| obc_seats | Int | OBC category |
| sc_seats | Int | SC category |
| st_seats | Int | ST category |
| ews_seats | Int | EWS category |
| pwd_seats | Int | PWD category |
| filled_seats | Int | Seats filled (calculated) |

**Seat Distribution Diagram**:
```
+----------------------------------------------------+
|                    SEAT MATRIX                      |
|                 Total: 120 seats                    |
+----------------------------------------------------+
|                                                     |
|  +----------+  +-----+  +----+  +----+  +----+     |
|  | GENERAL  |  | OBC |  | SC |  | ST |  | EWS|     |
|  |    50%   |  | 27% |  | 15%|  | 7.5%|  | 10%|    |
|  |  60 seats|  | 32  |  | 18 |  |  9  |  | 12 |    |
|  +----------+  +-----+  +----+  +----+  +----+     |
|                                                     |
+----------------------------------------------------+
```

### 4. Merit List
**Purpose**: Ranked list of applicants for admission

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| admission_cycle | Link | Admission cycle |
| program | Link (Program) | For specific program |
| category | Select | General/OBC/SC/ST/EWS |
| list_number | Int | 1st/2nd/3rd list |
| generated_date | Date | Generation date |
| applicants | Table | Ranked applicants |
| status | Select | Draft/Published |

**Submittable**: Yes (publishing the list)

### 5. Merit List Applicant (Child Table)
**Purpose**: Individual applicant entry with ranking

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| applicant | Link (Student Applicant) | Applicant reference |
| applicant_name | Data | Name (fetched) |
| merit_rank | Int | Position in list |
| entrance_score | Float | Exam score |
| admission_status | Select | Offered/Accepted/Rejected |

### 6. Admission Criteria
**Purpose**: Define eligibility requirements

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| program | Link (Program) | Applicable program |
| minimum_percentage | Float | Academic minimum |
| required_subjects | Small Text | Mandatory subjects |
| entrance_exam | Data | Required exam |
| minimum_score | Float | Exam cutoff |
| age_limit | Int | Maximum age |

## Data Flow Diagrams

### Complete Admission Flow
```
+----------------+     +------------------+     +------------------+
|   APPLICANT    |---->|     SUBMIT       |---->|   VERIFICATION   |
|   (Web Form)   |     |   APPLICATION    |     |   (Documents)    |
+----------------+     +------------------+     +------------------+
                                                        |
                                                        v
+----------------+     +------------------+     +------------------+
|    PUBLISH     |<----|    GENERATE      |<----|    PROCESS       |
|  MERIT LIST    |     |   MERIT LIST     |     |   APPLICATIONS   |
+----------------+     +------------------+     +------------------+
        |
        v
+----------------+     +------------------+     +------------------+
|    ACCEPT/     |---->|    ALLOCATE      |---->|    CREATE        |
|    CONFIRM     |     |      SEAT        |     |    STUDENT       |
+----------------+     +------------------+     +------------------+
```

### Applicant to Student Conversion
```
+--------------------+          +--------------------+
|  Student Applicant |          |      Student       |
| (Education App)    |   --->   | (Education App)    |
+--------------------+          +--------------------+
| - first_name       |          | - first_name       |
| - last_name        |          | - last_name        |
| - email            |          | - student_email    |
| - program          |          | - enrolled program |
| - [Custom Fields]  |          | - enrollment_no    |
|   - category       |          |   (generated)      |
|   - entrance_score |          | - category         |
|   - merit_rank     |          | - admission_date   |
+--------------------+          +--------------------+
```

## Integration Points

### Student Applicant Override
```python
# university_erp/overrides/student_applicant.py

class UniversityApplicant(StudentApplicant):
    """Extended Student Applicant with admission fields"""

    def validate(self):
        super().validate()
        self.validate_admission_cycle()
        self.check_eligibility()

    def on_update_after_submit(self):
        if self.application_status == "Approved":
            self.create_student_record()
```

### Custom Fields on Student Applicant
```python
custom_fields = [
    {"dt": "Student Applicant", "fieldname": "admission_cycle",
     "fieldtype": "Link", "options": "Admission Cycle"},
    {"dt": "Student Applicant", "fieldname": "category",
     "fieldtype": "Select", "options": "General\nOBC\nSC\nST\nEWS"},
    {"dt": "Student Applicant", "fieldname": "entrance_exam",
     "fieldtype": "Data"},
    {"dt": "Student Applicant", "fieldname": "entrance_score",
     "fieldtype": "Float"},
    {"dt": "Student Applicant", "fieldname": "merit_rank",
     "fieldtype": "Int", "read_only": 1},
]
```

### With Finance Module
```python
# Upon admission confirmation, fees are generated
def on_admission_confirm(student):
    from university_erp.fees_finance.api import generate_admission_fees
    generate_admission_fees(student)
```

## API Endpoints

### Merit List Generation
```python
@frappe.whitelist()
def generate_merit_list(admission_cycle, program, category=None):
    """Generate merit list from applications"""
    applicants = get_eligible_applicants(admission_cycle, program, category)
    ranked = rank_by_score(applicants)
    return create_merit_list(ranked)
```

### Seat Allocation
```python
@frappe.whitelist()
def allocate_seat(applicant, program, category):
    """Allocate seat to applicant from seat matrix"""
    seat_matrix = get_seat_matrix(program, category)
    if seat_matrix.available_seats > 0:
        confirm_admission(applicant)
        decrement_seats(seat_matrix)
```

## Reports

1. **Application Summary Report** - Applications by program/category
2. **Merit List Report** - Published merit lists
3. **Seat Status Report** - Filled vs available seats
4. **Admission Funnel Report** - Applications to enrollments

## Related Files

```
university_erp/
+-- admissions/
    +-- doctype/
    |   +-- admission_cycle/
    |   +-- admission_cycle_program/
    |   +-- seat_matrix/
    |   +-- merit_list/
    |   +-- merit_list_applicant/
    |   +-- admission_criteria/
    +-- api.py
    +-- merit_list_generator.py
+-- overrides/
    +-- student_applicant.py
```

## See Also

- [Student Info Module](03_STUDENT_INFO.md)
- [University Finance Module](05_UNIVERSITY_FINANCE.md)
- [Education App Documentation](../04_education_deep_dive.md)

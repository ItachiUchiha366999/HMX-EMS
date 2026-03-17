# Examinations Module

## Overview

The Examinations module manages exam scheduling, hall ticket generation, and student transcripts. It extends the Education app's Assessment functionality with university-specific examination workflows including invigilator assignment and comprehensive transcript generation.

## Module Location
```
university_erp/examinations/
```

## DocTypes (6 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Exam Schedule | Main | Examination timetable |
| Exam Invigilator | Child | Invigilator assignments |
| Hall Ticket | Main | Student exam admit cards |
| Hall Ticket Exam | Child | Exams on hall ticket |
| Student Transcript | Main | Complete academic record |
| Transcript Semester Result | Child | Semester-wise grades |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                     EXAMINATIONS MODULE                           |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |   EXAM SCHEDULE   |       |   HALL TICKET     |                |
|  +-------------------+       +-------------------+                |
|  | - Term/Year       |       | - Student         |                |
|  | - Exam Type       |       | - Examination     |                |
|  | - Dates           |       | - Eligible Courses|                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           v                           v                           |
|  +-------------------+       +-------------------+                |
|  | Exam Invigilator  |       | Hall Ticket Exam  |                |
|  | (Child Table)     |       | (Child Table)     |                |
|  +-------------------+       +-------------------+                |
|                                       |                           |
|                                       v                           |
|                              +-------------------+                |
|                              | Assessment Result |                |
|                              | (Education App)   |                |
|                              +-------------------+                |
|                                       |                           |
|                                       v                           |
|                              +-------------------+                |
|                              |STUDENT TRANSCRIPT |                |
|                              +-------------------+                |
|                              | - CGPA            |                |
|                              | - Total Credits   |                |
|                              | - Semester Results|                |
|                              +-------------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Education App Integration
```
+--------------------+       +--------------------+
|    EXAMINATIONS    |       |    EDUCATION       |
|      (Custom)      |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| Hall Ticket -------|------>| Student            |
|                    |       | Course             |
|                    |       | Academic Term      |
|                    |       |                    |
| Transcript --------|------>| Assessment Result  |
|   (reads from)     |       | (grade data)       |
|                    |       |                    |
+--------------------+       +--------------------+
```

### Cross-Module Relationships
```
                    +--------------------+
                    |   EXAMINATIONS     |
                    +--------------------+
                            /|\
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+----------------+  +----------------+  +----------------+
|   ACADEMICS    |  | UNIVERSITY HR  |  | INTEGRATIONS   |
+----------------+  +----------------+  +----------------+
| Course Reg ->  |  | Faculty ->     |  | DigiLocker ->  |
| Hall Ticket    |  | Invigilator    |  | Transcript     |
| eligibility    |  | assignment     |  | issuance       |
+----------------+  +----------------+  +----------------+
```

## DocType Details

### 1. Exam Schedule
**Purpose**: Master examination timetable

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| examination_name | Data | e.g., "End Sem Dec 2024" |
| exam_type | Select | Internal/Mid/End/Supplementary |
| academic_year | Link | Academic Year |
| academic_term | Link | Semester/Term |
| program | Link (Program) | Applicable program |
| start_date | Date | Exam period start |
| end_date | Date | Exam period end |
| exam_entries | Table | Course-wise schedule |
| invigilators | Table | Assigned invigilators |
| status | Select | Scheduled/Ongoing/Completed |

**Exam Entry Fields** (Child):
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Exam course |
| exam_date | Date | Specific date |
| start_time | Time | Exam start |
| end_time | Time | Exam end |
| venue | Link (Classroom) | Exam hall |

### 2. Exam Invigilator (Child Table)
**Purpose**: Invigilator duty assignment

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| instructor | Link (Instructor) | Faculty member |
| exam_date | Date | Duty date |
| venue | Link (Classroom) | Assigned room |
| duty_type | Select | Chief/Assistant |
| start_time | Time | Duty start |
| end_time | Time | Duty end |

### 3. Hall Ticket
**Purpose**: Student examination admit card

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student reference |
| student_name | Data | Name (fetched) |
| examination | Link (Exam Schedule) | Exam reference |
| hall_ticket_number | Data | Unique ticket ID |
| eligible_courses | Table | Courses student can appear |
| photo | Attach Image | Student photograph |
| signature | Attach Image | Student signature |
| status | Select | Draft/Issued/Revoked |
| issued_date | Date | Issue date |

**Auto-Naming**: HT-.YYYY.-#####

**Eligibility Check**:
```python
def check_eligibility(student, courses):
    """Verify student can appear for exams"""
    for course in courses:
        # Check attendance threshold (75%)
        attendance = get_attendance_percentage(student, course)
        if attendance < 75:
            frappe.throw(f"Attendance below 75% for {course}")

        # Check fee payment
        if has_pending_fees(student):
            frappe.throw("Fee payment pending")

        # Check course registration
        if not is_registered(student, course):
            frappe.throw(f"Not registered for {course}")
```

### 4. Hall Ticket Exam (Child Table)
**Purpose**: Individual exam entry on hall ticket

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Exam course |
| course_name | Data | Course name |
| exam_date | Date | Exam date |
| exam_time | Data | Time slot |
| venue | Data | Exam hall |
| seat_number | Data | Assigned seat |

### 5. Student Transcript
**Purpose**: Official academic record

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student reference |
| student_name | Data | Full name |
| enrollment_number | Data | Enrollment ID |
| program | Link (Program) | Degree program |
| transcript_number | Data | Unique transcript ID |
| generated_date | Date | Generation date |
| cgpa | Float | Cumulative GPA |
| total_credits | Int | Credits earned |
| degree_class | Select | First/Second/Pass |
| semester_results | Table | Semester-wise results |
| digilocker_uri | Data | DigiLocker reference |
| status | Select | Draft/Issued |

**Degree Classification**:
| CGPA Range | Class |
|------------|-------|
| >= 8.0 | First Class with Distinction |
| >= 6.5 | First Class |
| >= 5.5 | Second Class |
| >= 5.0 | Pass |
| < 5.0 | Fail |

### 6. Transcript Semester Result (Child Table)
**Purpose**: Semester-wise academic performance

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| academic_term | Link | Semester |
| courses_enrolled | Int | Number of courses |
| credits_earned | Float | Credits completed |
| sgpa | Float | Semester GPA |
| result_status | Select | Pass/Fail/ATKT |
| courses | Table | Course-wise grades |

## Data Flow Diagrams

### Hall Ticket Generation Flow
```
+----------------+     +------------------+     +------------------+
| Course         |---->| Attendance       |---->| Fee Payment      |
| Registration   |     | Check (>=75%)    |     | Verification     |
+----------------+     +------------------+     +------------------+
                                                        |
                                                        v
+----------------+     +------------------+     +------------------+
| HALL TICKET    |<----|   Generate       |<----|   Eligible       |
|   Issued       |     |   Hall Ticket    |     |   Courses        |
+----------------+     +------------------+     +------------------+
        |
        v
+----------------+
|  Print/PDF     |
|  Download      |
+----------------+
```

### Transcript Generation Flow
```
+------------------+     +------------------+     +------------------+
|  Assessment      |---->|   Calculate      |---->|   Calculate      |
|  Results         |     |   SGPA per       |     |   CGPA           |
| (All Semesters)  |     |   Semester       |     |   Overall        |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
+------------------+     +------------------+     +------------------+
|  Issue to        |<----|   Generate       |<----|   Determine      |
|  DigiLocker      |     |   Transcript     |     |   Degree Class   |
+------------------+     +------------------+     +------------------+
```

### CGPA Calculation
```
SGPA (Semester GPA):
+-----------------------------------------------+
|         Sum(Grade Points * Credits)           |
| SGPA = --------------------------------        |
|              Sum(Credits)                     |
+-----------------------------------------------+

CGPA (Cumulative GPA):
+-----------------------------------------------+
|       Sum(SGPA * Semester Credits)            |
| CGPA = ----------------------------------      |
|           Sum(All Credits)                    |
+-----------------------------------------------+
```

## Integration Points

### Assessment Result Override
```python
# university_erp/overrides/assessment_result.py

class UniversityAssessmentResult(AssessmentResult):
    """Extended with university grading"""

    def validate(self):
        super().validate()
        self.calculate_university_grade()

    def calculate_university_grade(self):
        """Calculate grade points based on grading scale"""
        percentage = (self.total_score / self.maximum_score) * 100

        # Grade mapping
        if percentage >= 90: self.grade, self.grade_points = 'O', 10
        elif percentage >= 80: self.grade, self.grade_points = 'A+', 9
        elif percentage >= 70: self.grade, self.grade_points = 'A', 8
        elif percentage >= 60: self.grade, self.grade_points = 'B+', 7
        elif percentage >= 50: self.grade, self.grade_points = 'B', 6
        elif percentage >= 40: self.grade, self.grade_points = 'P', 5
        else: self.grade, self.grade_points = 'F', 0

        # Credit points = Grade Points * Course Credits
        self.credit_points = self.grade_points * self.credits
```

### With DigiLocker Integration
```python
# Issue transcript to DigiLocker
def issue_to_digilocker(transcript):
    from university_erp.university_integrations.digilocker import issue_document

    response = issue_document(
        document_type="Academic Transcript",
        student_aadhaar=transcript.student_aadhaar,
        document_data=transcript.as_dict()
    )

    transcript.digilocker_uri = response.get("uri")
    transcript.save()
```

### With Finance Module
```python
# Hall ticket requires fee clearance
def check_fee_clearance(student):
    pending = frappe.db.count("Fees", {
        "student": student,
        "outstanding_amount": (">", 0)
    })
    return pending == 0
```

## API Endpoints

### Hall Ticket
```python
@frappe.whitelist()
def generate_hall_ticket(student, examination):
    """Generate hall ticket for student"""
    # Check eligibility
    courses = get_registered_courses(student, examination)
    validate_eligibility(student, courses)

    # Create hall ticket
    ht = frappe.new_doc("Hall Ticket")
    ht.student = student
    ht.examination = examination
    for course in courses:
        ht.append("eligible_courses", {"course": course})
    ht.insert()
    return ht

@frappe.whitelist()
def get_hall_ticket_pdf(hall_ticket):
    """Generate PDF for hall ticket"""
    return frappe.get_print("Hall Ticket", hall_ticket, "Hall Ticket Format")
```

### Transcript
```python
@frappe.whitelist()
def generate_transcript(student):
    """Generate academic transcript"""
    results = get_all_assessment_results(student)
    semester_results = calculate_semester_results(results)
    cgpa = calculate_cgpa(semester_results)
    degree_class = determine_degree_class(cgpa)

    transcript = frappe.new_doc("Student Transcript")
    transcript.student = student
    transcript.cgpa = cgpa
    transcript.degree_class = degree_class
    for sem in semester_results:
        transcript.append("semester_results", sem)
    transcript.insert()
    return transcript
```

## Reports

1. **Exam Schedule Report** - Timetable view
2. **Hall Ticket Status Report** - Issued/pending
3. **Result Analysis Report** - Pass/fail statistics
4. **CGPA Distribution Report** - Grade distribution
5. **Invigilator Duty Report** - Faculty assignments
6. **Transcript Register** - Issued transcripts

## Related Files

```
university_erp/
+-- examinations/
    +-- doctype/
    |   +-- exam_schedule/
    |   |   +-- exam_schedule.json
    |   |   +-- exam_schedule.py
    |   +-- exam_invigilator/
    |   +-- hall_ticket/
    |   |   +-- hall_ticket.json
    |   |   +-- hall_ticket.py
    |   +-- hall_ticket_exam/
    |   +-- student_transcript/
    |   |   +-- student_transcript.json
    |   |   +-- student_transcript.py
    |   +-- transcript_semester_result/
    +-- api.py
    +-- grading.py
    +-- transcript_generator.py
+-- overrides/
    +-- assessment_result.py
```

## See Also

- [Academics Module](01_ACADEMICS.md)
- [University OBE Module](13_UNIVERSITY_OBE.md)
- [University Integrations Module](14_UNIVERSITY_INTEGRATIONS.md)
- [Education App Documentation](../04_education_deep_dive.md)

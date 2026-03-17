# Academics Module

## Overview

The Academics module manages course registration, timetabling, teaching assignments, and CBCS (Choice Based Credit System) implementation. It extends the Education app's core functionality with university-specific academic workflows.

## Module Location
```
university_erp/academics/
```

## DocTypes (8 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Course Registration | Main | Student semester course enrollment |
| Course Registration Item | Child | Individual course in registration |
| Teaching Assignment | Main | Faculty-course-section mapping |
| Timetable Slot | Main | Class schedule slots |
| University Classroom | Main | Physical classroom resources |
| Course Prerequisite | Main | Course prerequisite definitions |
| Elective Course Group | Main | Grouping of elective courses |
| Elective Course Group Item | Child | Individual elective in group |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                      ACADEMICS MODULE                             |
+------------------------------------------------------------------+
|                                                                   |
|  +-----------------------+       +-----------------------+        |
|  |  COURSE REGISTRATION  |       |  TEACHING ASSIGNMENT  |        |
|  +-----------------------+       +-----------------------+        |
|           |                               |                       |
|           v                               v                       |
|  +-----------------------+       +-----------------------+        |
|  |    Course Reg Item    |       |      Instructor       |        |
|  |    (Child Table)      |       |   (Education App)     |        |
|  +-----------------------+       +-----------------------+        |
|           |                               |                       |
|           +---------------+---------------+                       |
|                           |                                       |
|                           v                                       |
|                  +-----------------+                              |
|                  |     COURSE      |                              |
|                  | (Education App) |                              |
|                  +-----------------+                              |
|                           |                                       |
|           +---------------+---------------+                       |
|           |               |               |                       |
|           v               v               v                       |
|  +------------+   +-------------+   +------------+                |
|  |  TIMETABLE |   |  CLASSROOM  |   | ELECTIVE   |                |
|  |    SLOT    |   |             |   |   GROUP    |                |
|  +------------+   +-------------+   +------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Dependencies on Education App
```
+-------------------+       +-------------------+
|     ACADEMICS     |       |    EDUCATION      |
|     (Custom)      |------>|      (App)        |
+-------------------+       +-------------------+
| Course            |       | Student           |
| Registration -----|------>| Program           |
| Teaching          |       | Course            |
| Assignment -------|------>| Student Group     |
| Timetable Slot ---|------>| Academic Term     |
|                   |       | Instructor        |
+-------------------+       +-------------------+
```

### Connected University ERP Modules
```
                    +-------------------+
                    |     ACADEMICS     |
                    +-------------------+
                           /|\
            +--------------+--------------+
            |              |              |
            v              v              v
    +----------+    +------------+   +----------+
    |EXAMINAT- |    |     LMS    |   |   OBE    |
    |  IONS    |    |            |   |          |
    +----------+    +------------+   +----------+
    Hall Ticket     LMS Course       Course
    references      linked to        Outcomes
    courses         courses          mapped
```

## DocType Details

### 1. Course Registration
**Purpose**: Records student course enrollment for each semester/term

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student record reference |
| academic_term | Link (Academic Term) | Semester/term |
| program | Link (Program) | Degree program (auto-fetched) |
| courses | Table | Child table of courses |
| total_credits | Float | Sum of enrolled course credits |
| registration_date | Date | Date of registration |

**Submittable**: Yes

**Permissions**:
- University Admin: Full access
- University Faculty: Full access
- University Registrar: Create, Read, Write, Export

**Workflow**:
```
Draft --> Submit --> [Approved Registration]
                          |
                          v
                    Enrollment in
                    Student Attendance
```

### 2. Course Registration Item (Child Table)
**Purpose**: Individual course entry in registration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Course selection |
| credits | Float | Course credits |
| course_type | Select | Core/Elective/Open Elective |

### 3. Teaching Assignment
**Purpose**: Maps instructors to courses and student groups

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| instructor | Link (Instructor) | Faculty member |
| course | Link (Course) | Course taught |
| academic_term | Link (Academic Term) | Term of assignment |
| student_group | Link (Student Group) | Section assigned |
| teaching_type | Select | Lecture/Tutorial/Practical |
| weekly_hours | Float | Hours per week |
| is_active | Check | Active status |

**Use Cases**:
- Workload calculation
- Timetable generation
- Attendance tracking authorization

### 4. Timetable Slot
**Purpose**: Defines class schedule slots

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| day | Select | Day of week |
| start_time | Time | Class start time |
| end_time | Time | Class end time |
| course | Link (Course) | Course scheduled |
| instructor | Link (Instructor) | Teacher |
| classroom | Link (University Classroom) | Room assigned |
| student_group | Link (Student Group) | Section |

### 5. University Classroom
**Purpose**: Physical classroom inventory

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| classroom_name | Data | Room identifier |
| building | Data | Building name |
| floor | Data | Floor number |
| capacity | Int | Seating capacity |
| has_projector | Check | Projector available |
| has_ac | Check | Air conditioning |
| room_type | Select | Lecture Hall/Lab/Seminar |

### 6. Course Prerequisite
**Purpose**: Define course dependency chains

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course | Link (Course) | Main course |
| prerequisite_course | Link (Course) | Required prior course |
| is_mandatory | Check | Strict requirement |

### 7. Elective Course Group
**Purpose**: Groups elective courses for selection

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| group_name | Data | Group identifier |
| program | Link (Program) | Applicable program |
| semester | Int | Semester number |
| elective_type | Select | DSE/GE/SEC/VAC |
| min_selection | Int | Minimum courses to pick |
| max_selection | Int | Maximum courses to pick |
| courses | Table | Child table of electives |

## Data Flow Diagrams

### Course Registration Flow
```
+----------+     +---------------+     +------------------+
| Student  |---->| Course        |---->| Course Reg Item  |
| Portal   |     | Registration  |     | (Selected Courses)|
+----------+     +---------------+     +------------------+
                       |
                       v
              +------------------+
              | Validate Credits |
              | Check Prereqs    |
              +------------------+
                       |
                       v
              +------------------+
              |     Submit       |
              | Registration     |
              +------------------+
                       |
                       v
              +------------------+
              | Auto-enroll in   |
              | Student Group    |
              | for Attendance   |
              +------------------+
```

### Teaching Assignment Flow
```
+----------------+     +-------------------+
| HOD/Admin      |---->| Teaching          |
| Creates        |     | Assignment        |
+----------------+     +-------------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+---------------+    +----------------+    +----------------+
| Timetable     |    | Workload       |    | Attendance     |
| Generation    |    | Calculation    |    | Authorization  |
+---------------+    +----------------+    +----------------+
```

## Integration Points

### With Education App
```python
# Course Registration links to Education DocTypes
course_registration.student -> education.Student
course_registration.academic_term -> education.Academic Term
course_registration.program -> education.Program
course_reg_item.course -> education.Course

# Teaching Assignment links
teaching_assignment.instructor -> education.Instructor
teaching_assignment.course -> education.Course
teaching_assignment.student_group -> education.Student Group
```

### With University HR Module
```python
# Teaching assignment feeds workload calculation
university_hr.workload_distributor <- academics.teaching_assignment
university_hr.faculty_profile.current_workload <- sum(weekly_hours)
```

### With Examinations Module
```python
# Course registration determines exam eligibility
examinations.hall_ticket.eligible_courses <- course_registration.courses
```

### With LMS Module
```python
# LMS courses linked to academic courses
university_lms.lms_course.course -> education.Course
university_lms.lms_course inherits from course_registration enrollments
```

## API Endpoints

### Course Registration
```python
# Get student's current registration
frappe.call({
    method: "university_erp.academics.api.get_student_registration",
    args: { student: "STU-001", academic_term: "2024-25 Odd" }
})

# Submit course registration
frappe.call({
    method: "frappe.client.submit",
    args: { doc: course_registration_doc }
})
```

### Teaching Assignment
```python
# Get instructor's assignments
frappe.call({
    method: "university_erp.academics.api.get_instructor_courses",
    args: { instructor: "INS-001", academic_term: "2024-25 Odd" }
})
```

## Reports

1. **Course Registration Report** - Students enrolled per course
2. **Teaching Workload Report** - Hours per instructor
3. **Classroom Utilization Report** - Room usage statistics
4. **Elective Selection Report** - Popular elective choices

## Related Files

```
university_erp/
+-- academics/
    +-- doctype/
    |   +-- course_registration/
    |   |   +-- course_registration.json
    |   |   +-- course_registration.py
    |   +-- course_registration_item/
    |   +-- teaching_assignment/
    |   +-- timetable_slot/
    |   +-- university_classroom/
    |   +-- course_prerequisite/
    |   +-- elective_course_group/
    |   +-- elective_course_group_item/
    +-- api.py
    +-- reports/
```

## See Also

- [Education App Documentation](../04_education_deep_dive.md)
- [Examinations Module](04_EXAMINATIONS.md)
- [University LMS Module](11_UNIVERSITY_LMS.md)
- [University OBE Module](13_UNIVERSITY_OBE.md)

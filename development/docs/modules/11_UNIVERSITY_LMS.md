# University LMS Module

## Overview

The University LMS (Learning Management System) module provides online learning capabilities including course content management, assignments, quizzes, discussions, and progress tracking. It complements classroom teaching with digital learning resources.

## Module Location
```
university_erp/university_lms/
```

## DocTypes (15 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| LMS Course | Main | Online course container |
| LMS Course Module | Child | Course chapters/modules |
| LMS Content | Main | Learning materials |
| LMS Content Progress | Main | Content completion tracking |
| LMS Assignment | Main | Assignment definitions |
| Assignment Rubric Item | Child | Grading rubric |
| Assignment Submission | Main | Student submissions |
| Submission File | Child | Uploaded files |
| Submission Rubric Score | Child | Rubric-wise grades |
| LMS Quiz | Main | Quiz definitions |
| Quiz Question | Child | Quiz questions |
| Quiz Answer | Child | Answer options |
| Quiz Attempt | Main | Student quiz attempts |
| LMS Discussion | Main | Discussion forums |
| Discussion Reply | Child | Forum replies |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                       UNIVERSITY LMS MODULE                       |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+                                            |
|  |    LMS COURSE     |                                            |
|  +-------------------+                                            |
|  | - Course link     |                                            |
|  | - Instructor      |                                            |
|  | - Modules         |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           v                                                       |
|  +-------------------+                                            |
|  | LMS Course Module |                                            |
|  +-------------------+                                            |
|  | - Week/Chapter    |                                            |
|  | - Sequence        |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           +------------------+------------------+                  |
|           |                  |                  |                  |
|           v                  v                  v                  |
|  +-------------+     +-------------+     +-------------+          |
|  | LMS CONTENT |     |LMS ASSIGNMENT|    |  LMS QUIZ   |          |
|  +-------------+     +-------------+     +-------------+          |
|  | - Video     |     | - Rubric    |     | - Questions |          |
|  | - Document  |     | - Due date  |     | - Time limit|          |
|  | - Link      |     +-------------+     +-------------+          |
|  +-------------+           |                   |                  |
|        |                   v                   v                  |
|        v            +-------------+     +-------------+           |
|  +-------------+    | SUBMISSION  |     |QUIZ ATTEMPT |           |
|  |  PROGRESS   |    +-------------+     +-------------+           |
|  +-------------+    | - Files     |     | - Answers   |           |
|  | - Completed |    | - Score     |     | - Score     |           |
|  +-------------+    +-------------+     +-------------+           |
|                                                                   |
|  +-------------------+                                            |
|  |  LMS DISCUSSION   |                                            |
|  +-------------------+                                            |
|  | - Topics          |                                            |
|  | - Replies         |                                            |
|  +-------------------+                                            |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Education App Integration
```
+--------------------+       +--------------------+
|     LMS            |       |    EDUCATION       |
|     (Custom)       |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| LMS Course --------|------>| Course             |
|                    |       | (links to academic |
|                    |       |  course)           |
|                    |       |                    |
| Enrollment --------|------>| Student            |
|                    |       | Course Enrollment  |
|                    |       |                    |
| Assignment score---|------>| Assessment Result  |
| Quiz score --------|------>| (can feed grades)  |
+--------------------+       +--------------------+
```

### Cross-Module Relationships
```
                    +--------------------+
                    |        LMS         |
                    +--------------------+
                            /|\
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+----------------+  +----------------+  +----------------+
|   ACADEMICS    |  |      OBE       |  |   UNIVERSITY   |
+----------------+  +----------------+  |      HR        |
| Course ->      |  | Quiz/Assignment|  +----------------+
| LMS Course     |  | -> CO Attainment| | Instructor ->  |
| link           |  |               |  | Faculty Profile|
+----------------+  +----------------+  +----------------+
```

## DocType Details

### 1. LMS Course
**Purpose**: Online course container

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| course_title | Data | Display title |
| course | Link (Course) | Academic course link |
| academic_term | Link (Academic Term) | Semester |
| instructor | Link (Instructor) | Course teacher |
| description | Text Editor | Course description |
| learning_outcomes | Text Editor | What students learn |
| modules | Table | Course modules |
| published | Check | Available to students |
| enrollment_type | Select | Open/Restricted |
| start_date | Date | Course start |
| end_date | Date | Course end |
| total_students | Int | Enrolled count |

### 2. LMS Course Module (Child Table)
**Purpose**: Course chapters/units

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| module_title | Data | Chapter title |
| module_order | Int | Sequence number |
| description | Text | Module overview |
| is_published | Check | Available |
| unlock_date | Date | When accessible |

### 3. LMS Content
**Purpose**: Learning materials

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| content_title | Data | Title |
| lms_course | Link (LMS Course) | Parent course |
| module | Data | Module/chapter |
| content_type | Select | Video/Document/Link/Text |
| content_order | Int | Sequence |
| video_url | Data | Video link (YouTube/Vimeo) |
| document | Attach | PDF/PPT/DOC |
| external_link | Data | External URL |
| text_content | Text Editor | Rich text |
| duration | Int | Estimated minutes |
| is_mandatory | Check | Required to complete |
| is_published | Check | Available |

**Content Types**:
- Video (embedded or uploaded)
- Document (PDF, PPT, DOC)
- External Link
- Rich Text Content
- Interactive Content

### 4. LMS Content Progress
**Purpose**: Track content completion

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| lms_course | Link (LMS Course) | Course |
| content | Link (LMS Content) | Content item |
| started_on | Datetime | First access |
| completed_on | Datetime | Completion time |
| time_spent | Int | Minutes spent |
| is_completed | Check | Marked complete |

### 5. LMS Assignment
**Purpose**: Assignment definitions

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| assignment_title | Data | Title |
| lms_course | Link (LMS Course) | Course |
| module | Data | Module |
| description | Text Editor | Instructions |
| due_date | Datetime | Deadline |
| total_marks | Float | Maximum score |
| rubric | Table | Grading criteria |
| allow_late_submission | Check | Accept late work |
| late_penalty | Percent | Penalty per day |
| max_files | Int | File upload limit |
| allowed_file_types | Data | e.g., "pdf,doc,docx" |
| is_published | Check | Available |

### 6. Assignment Rubric Item (Child Table)
**Purpose**: Grading criteria

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| criterion | Data | Evaluation point |
| description | Text | Detailed expectations |
| max_score | Float | Points for criterion |

### 7. Assignment Submission
**Purpose**: Student submissions

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Submitter |
| assignment | Link (LMS Assignment) | Assignment |
| submission_date | Datetime | Submitted on |
| submission_text | Text Editor | Text answer |
| files | Table | Uploaded files |
| is_late | Check | Past deadline |
| late_days | Int | Days late |
| total_score | Float | Awarded score |
| rubric_scores | Table | Criterion-wise |
| feedback | Text | Instructor feedback |
| status | Select | Submitted/Graded/Returned |
| graded_by | Link (User) | Grader |
| graded_on | Datetime | Grading date |

### 8. LMS Quiz
**Purpose**: Quiz definitions

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| quiz_title | Data | Title |
| lms_course | Link (LMS Course) | Course |
| module | Data | Module |
| description | Text | Instructions |
| questions | Table | Quiz questions |
| total_marks | Float | Maximum score |
| time_limit | Int | Minutes allowed |
| attempts_allowed | Int | Max attempts |
| show_answers | Check | Show after submit |
| shuffle_questions | Check | Random order |
| shuffle_answers | Check | Random options |
| start_date | Datetime | Available from |
| end_date | Datetime | Available until |
| is_published | Check | Available |

### 9. Quiz Question (Child Table)
**Purpose**: Individual questions

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| question_text | Text | Question |
| question_type | Select | MCQ/True-False/Short Answer |
| marks | Float | Points |
| answers | Table | Answer options |
| correct_answer | Data | For short answer |
| explanation | Text | Answer explanation |

### 10. Quiz Answer (Child Table)
**Purpose**: MCQ options

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| answer_text | Data | Option text |
| is_correct | Check | Correct answer |

### 11. Quiz Attempt
**Purpose**: Student quiz attempts

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Test taker |
| quiz | Link (LMS Quiz) | Quiz |
| attempt_number | Int | Which attempt |
| started_on | Datetime | Start time |
| submitted_on | Datetime | Submit time |
| time_taken | Int | Minutes used |
| responses | JSON | Question responses |
| score | Float | Total score |
| percentage | Float | Percentage |
| is_passed | Check | Pass/Fail |
| status | Select | In Progress/Completed |

### 12. LMS Discussion
**Purpose**: Discussion forums

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| topic_title | Data | Discussion topic |
| lms_course | Link (LMS Course) | Course |
| module | Data | Module (optional) |
| description | Text Editor | Topic description |
| created_by | Link (User) | Author |
| replies | Table | Responses |
| is_pinned | Check | Pin to top |
| is_locked | Check | No new replies |
| reply_count | Int | Total replies |

## Data Flow Diagrams

### Content Consumption Flow
```
+----------------+     +------------------+     +------------------+
|   Student      |---->|   Access LMS     |---->|   Select         |
|   Login        |     |   Course         |     |   Module         |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+             |
|   Progress     |<----|   Mark           |<------------+
|   Updated      |     |   Completed      |
+----------------+     +------------------+
```

### Assignment Flow
```
+----------------+     +------------------+     +------------------+
| Instructor     |---->| Create           |---->|   Publish        |
| Creates        |     | Assignment       |     |   Assignment     |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+            |
|   Score        |<----|   Grade          |<-----------+
|   Recorded     |     |   Submission     |
+----------------+     +------------------+
        ^                                             |
        |                                             v
+----------------+     +------------------+     +------------------+
|   Feedback     |     |   Review         |<----|   Student        |
|   Provided     |---->|   Submission     |     |   Submits        |
+----------------+     +------------------+     +------------------+
```

### Quiz Flow
```
+----------------+     +------------------+     +------------------+
|   Student      |---->|   Start Quiz     |---->|   Answer         |
|   Accesses     |     |   (Timer Starts) |     |   Questions      |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+            |
|   View Score   |<----|   Auto-Grade     |<-----------+
|   & Feedback   |     |   MCQ/TF         |     |   Submit         |
+----------------+     +------------------+     +------------------+
```

### Progress Tracking
```
+------------------------------------------------------------------+
|                    STUDENT PROGRESS DASHBOARD                     |
+------------------------------------------------------------------+
|                                                                   |
|  Course: Data Structures (CSE201)                                 |
|  Progress: 65% Complete                                           |
|                                                                   |
|  +------------------+------------------+------------------+       |
|  |     Content      |   Assignments    |     Quizzes      |       |
|  +------------------+------------------+------------------+       |
|  | 8/10 Completed   | 2/3 Submitted    | 1/2 Attempted    |       |
|  | Videos: 5/6      | Avg: 78%         | Avg: 85%         |       |
|  | Docs: 3/4        |                  |                  |       |
|  +------------------+------------------+------------------+       |
|                                                                   |
+------------------------------------------------------------------+
```

## Integration Points

### With Academics Module
```python
# Link LMS course to academic course
def create_lms_course_from_academic(course, academic_term, instructor):
    """Create LMS course for academic course"""
    lms_course = frappe.new_doc("LMS Course")
    lms_course.course = course
    lms_course.course_title = frappe.db.get_value("Course", course, "course_name")
    lms_course.academic_term = academic_term
    lms_course.instructor = instructor
    lms_course.insert()

    # Auto-enroll registered students
    enrollments = get_course_enrollments(course, academic_term)
    for enrollment in enrollments:
        enroll_student_in_lms(lms_course.name, enrollment.student)

    return lms_course
```

### With OBE Module
```python
# Quiz scores feed into CO attainment
def calculate_quiz_co_attainment(quiz, course_outcome):
    """Calculate CO attainment from quiz performance"""
    attempts = frappe.get_all("Quiz Attempt", {
        "quiz": quiz,
        "status": "Completed"
    }, ["student", "percentage"])

    attainment_data = []
    for attempt in attempts:
        attainment_data.append({
            "student": attempt.student,
            "score": attempt.percentage,
            "max_score": 100
        })

    return calculate_attainment(attainment_data, course_outcome)
```

### With Assessment Results
```python
# Sync LMS scores to Education assessments
def sync_lms_to_assessment(lms_course, component_type="quiz"):
    """Sync LMS quiz/assignment scores to Assessment Result"""
    if component_type == "quiz":
        scores = get_quiz_scores(lms_course)
    else:
        scores = get_assignment_scores(lms_course)

    for score in scores:
        create_or_update_assessment_result(
            student=score.student,
            course=lms_course.course,
            assessment_type=component_type,
            score=score.score,
            max_score=score.max_score
        )
```

## API Endpoints

### Course Access
```python
@frappe.whitelist()
def get_student_courses(student):
    """Get enrolled LMS courses"""
    enrollments = frappe.get_all("Course Enrollment", {
        "student": student,
        "status": "Active"
    }, ["course"])

    lms_courses = []
    for enrollment in enrollments:
        lms = frappe.get_all("LMS Course", {
            "course": enrollment.course,
            "published": 1
        })
        lms_courses.extend(lms)

    return lms_courses

@frappe.whitelist()
def get_course_content(lms_course, student):
    """Get course content with progress"""
    contents = frappe.get_all("LMS Content", {
        "lms_course": lms_course,
        "is_published": 1
    }, ["*"], order_by="content_order")

    for content in contents:
        progress = frappe.db.get_value("LMS Content Progress", {
            "student": student,
            "content": content.name
        }, ["is_completed", "time_spent"])

        content["is_completed"] = progress[0] if progress else False
        content["time_spent"] = progress[1] if progress else 0

    return contents
```

### Quiz API
```python
@frappe.whitelist()
def start_quiz_attempt(quiz, student):
    """Start new quiz attempt"""
    quiz_doc = frappe.get_doc("LMS Quiz", quiz)

    # Check attempts remaining
    attempts = frappe.db.count("Quiz Attempt", {
        "quiz": quiz,
        "student": student
    })
    if attempts >= quiz_doc.attempts_allowed:
        frappe.throw("Maximum attempts reached")

    attempt = frappe.new_doc("Quiz Attempt")
    attempt.quiz = quiz
    attempt.student = student
    attempt.attempt_number = attempts + 1
    attempt.started_on = frappe.utils.now_datetime()
    attempt.status = "In Progress"
    attempt.insert()

    return {
        "attempt": attempt.name,
        "questions": get_quiz_questions(quiz, quiz_doc.shuffle_questions)
    }

@frappe.whitelist()
def submit_quiz(attempt, responses):
    """Submit quiz and calculate score"""
    attempt_doc = frappe.get_doc("Quiz Attempt", attempt)
    quiz_doc = frappe.get_doc("LMS Quiz", attempt_doc.quiz)

    # Grade responses
    score = 0
    for question_id, answer in responses.items():
        question = get_question(question_id)
        if is_correct(question, answer):
            score += question.marks

    attempt_doc.responses = json.dumps(responses)
    attempt_doc.score = score
    attempt_doc.percentage = (score / quiz_doc.total_marks) * 100
    attempt_doc.submitted_on = frappe.utils.now_datetime()
    attempt_doc.status = "Completed"
    attempt_doc.save()

    return attempt_doc
```

## Reports

1. **Course Progress Report** - Completion by student
2. **Assignment Submissions** - Submission status
3. **Quiz Performance** - Score distribution
4. **Content Engagement** - Time spent analytics
5. **Discussion Activity** - Forum participation
6. **Instructor Dashboard** - Course overview

## Related Files

```
university_erp/
+-- university_lms/
    +-- doctype/
    |   +-- lms_course/
    |   +-- lms_course_module/
    |   +-- lms_content/
    |   +-- lms_content_progress/
    |   +-- lms_assignment/
    |   +-- assignment_rubric_item/
    |   +-- assignment_submission/
    |   +-- submission_file/
    |   +-- submission_rubric_score/
    |   +-- lms_quiz/
    |   +-- quiz_question/
    |   +-- quiz_answer/
    |   +-- quiz_attempt/
    |   +-- lms_discussion/
    |   +-- discussion_reply/
    +-- api.py
```

## See Also

- [Academics Module](01_ACADEMICS.md)
- [University OBE Module](13_UNIVERSITY_OBE.md)
- [Examinations Module](04_EXAMINATIONS.md)

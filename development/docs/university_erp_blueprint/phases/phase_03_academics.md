# Phase 3: Academics Module

## Overview

**Duration:** 5-6 weeks
**Priority:** High - Core academic operations
**Module Focus:** CBCS implementation, Course management, Timetable, Attendance, Teaching assignments
**Status:** ✅ **COMPLETED** (2025-12-31)

This phase implements the complete academic module including CBCS (Choice Based Credit System), course registration, timetable management, and attendance tracking by extending Frappe Education's Course, Course Schedule, and Student Attendance DocTypes.

---

## Prerequisites

### From Previous Phases
- [x] Phase 1: Foundation complete (app, roles, permissions)
- [x] Phase 2: Admissions & SIS complete (students enrolled)
- [x] Course DocType extended with L-T-P-S credits
- [x] Program DocType extended with CBCS fields
- [x] University Department DocType working
- [x] Academic Year and Academic Term configured

### Technical Requirements
- [x] Education module's Course Schedule DocType accessible
- [x] Education module's Student Attendance DocType accessible
- [x] Education module's Student Group DocType accessible
- [x] Education module's Instructor DocType accessible

### Data Requirements
- [x] Faculty records with Instructor linking
- [x] Classroom/Room master data (University Classroom DocType)
- [x] Time slot definitions (Timetable Slot DocType)

---

## Deliverables

### Week 1-2: CBCS Implementation

#### 1.1 CBCS Course Type Manager

**File:** `university_erp/academics/cbcs.py`
```python
import frappe
from frappe.utils import flt

class CBCSManager:
    """Manage Choice Based Credit System"""

    # CBCS Course Categories
    COURSE_TYPES = {
        "Core": {
            "abbreviation": "CC",
            "description": "Core Course - Compulsory",
            "credits_range": (3, 6)
        },
        "DSE": {
            "abbreviation": "DSE",
            "description": "Discipline Specific Elective",
            "credits_range": (3, 4)
        },
        "GE": {
            "abbreviation": "GE",
            "description": "Generic Elective",
            "credits_range": (3, 4)
        },
        "SEC": {
            "abbreviation": "SEC",
            "description": "Skill Enhancement Course",
            "credits_range": (2, 4)
        },
        "AEC": {
            "abbreviation": "AEC",
            "description": "Ability Enhancement Course",
            "credits_range": (2, 4)
        },
        "VAC": {
            "abbreviation": "VAC",
            "description": "Value Added Course",
            "credits_range": (2, 2)
        },
        "Project": {
            "abbreviation": "PROJ",
            "description": "Project/Dissertation",
            "credits_range": (4, 12)
        },
        "Internship": {
            "abbreviation": "INT",
            "description": "Internship/Industrial Training",
            "credits_range": (2, 6)
        }
    }

    def __init__(self, program=None):
        self.program = program
        if program:
            self.program_doc = frappe.get_doc("Program", program)

    def get_semester_courses(self, semester_number):
        """Get courses for a specific semester"""
        if not self.program:
            return []

        courses = frappe.get_all(
            "Program Course",
            filters={
                "parent": self.program,
                "custom_semester_number": semester_number
            },
            fields=["course", "required"]
        )

        result = []
        for c in courses:
            course_doc = frappe.get_doc("Course", c.course)
            result.append({
                "course": c.course,
                "course_name": course_doc.course_name,
                "course_code": course_doc.custom_course_code,
                "course_type": course_doc.custom_course_type,
                "credits": course_doc.custom_credits,
                "l_t_p": f"{course_doc.custom_lecture_hours}-{course_doc.custom_tutorial_hours}-{course_doc.custom_practical_hours}",
                "required": c.required
            })

        return result

    def get_elective_options(self, semester_number, course_type):
        """Get elective options for a semester"""
        department = self.program_doc.department if self.program else None

        filters = {"custom_course_type": course_type}
        if department:
            filters["department"] = department

        return frappe.get_all(
            "Course",
            filters=filters,
            fields=[
                "name", "course_name", "custom_course_code",
                "custom_credits", "custom_lecture_hours",
                "custom_tutorial_hours", "custom_practical_hours"
            ]
        )

    def validate_course_selection(self, student, semester, selected_courses):
        """Validate student's course selection against CBCS rules"""
        errors = []
        warnings = []

        student_doc = frappe.get_doc("Student", student)
        program = student_doc.custom_program

        # Get program requirements
        program_doc = frappe.get_doc("Program", program)
        min_credits = program_doc.custom_min_credits_per_semester or 15
        max_credits = program_doc.custom_max_credits_per_semester or 26

        # Calculate total credits
        total_credits = 0
        credits_by_type = {}

        for course_name in selected_courses:
            course = frappe.get_doc("Course", course_name)

            # Check prerequisites
            prereq_result = self.check_prerequisites(student, course_name)
            if not prereq_result["satisfied"]:
                errors.append(prereq_result["message"])

            # Track credits
            credits = course.custom_credits or 0
            total_credits += credits

            course_type = course.custom_course_type or "Core"
            credits_by_type.setdefault(course_type, 0)
            credits_by_type[course_type] += credits

        # Validate total credits
        if total_credits < min_credits:
            errors.append(f"Minimum {min_credits} credits required. Selected: {total_credits}")
        if total_credits > max_credits:
            errors.append(f"Maximum {max_credits} credits allowed. Selected: {total_credits}")

        # Check for duplicate courses
        already_passed = self.get_passed_courses(student)
        duplicates = set(selected_courses) & set(already_passed)
        if duplicates:
            errors.append(f"Already passed courses cannot be selected: {', '.join(duplicates)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_credits": total_credits,
            "credits_by_type": credits_by_type
        }

    def check_prerequisites(self, student, course):
        """Check if student has completed prerequisites"""
        prerequisites = frappe.get_all(
            "Course Prerequisite",
            filters={"parent": course},
            pluck="prerequisite_course"
        )

        if not prerequisites:
            return {"satisfied": True, "message": ""}

        passed_courses = self.get_passed_courses(student)

        missing = []
        for prereq in prerequisites:
            if prereq not in passed_courses:
                missing.append(prereq)

        if missing:
            return {
                "satisfied": False,
                "message": f"Prerequisites not met for {course}: {', '.join(missing)}"
            }

        return {"satisfied": True, "message": ""}

    def get_passed_courses(self, student):
        """Get list of courses student has passed"""
        results = frappe.get_all(
            "Assessment Result",
            filters={
                "student": student,
                "docstatus": 1,
                "custom_result_status": "Pass"
            },
            pluck="course"
        )
        return list(set(results))

    def calculate_semester_credits(self, student, academic_term):
        """Calculate credits for a semester"""
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"student": student, "academic_term": academic_term},
            pluck="course"
        )

        total = 0
        for course in enrollments:
            credits = frappe.db.get_value("Course", course, "custom_credits")
            total += credits or 0

        return total


@frappe.whitelist()
def validate_course_registration(student, semester, courses):
    """API for course registration validation"""
    if isinstance(courses, str):
        courses = frappe.parse_json(courses)

    student_doc = frappe.get_doc("Student", student)
    manager = CBCSManager(student_doc.custom_program)
    return manager.validate_course_selection(student, semester, courses)
```

#### 1.2 Course Prerequisite Child Table

**DocType:** `Course Prerequisite`
```json
{
    "doctype": "DocType",
    "name": "Course Prerequisite",
    "module": "Academics",
    "istable": 1,
    "fields": [
        {
            "fieldname": "prerequisite_course",
            "fieldtype": "Link",
            "label": "Prerequisite Course",
            "options": "Course",
            "reqd": 1
        },
        {
            "fieldname": "prerequisite_type",
            "fieldtype": "Select",
            "label": "Type",
            "options": "Hard\nSoft",
            "default": "Hard",
            "description": "Hard: Must pass. Soft: Recommended"
        }
    ]
}
```

#### 1.3 Elective Course Group

**DocType:** `Elective Course Group`
```json
{
    "doctype": "DocType",
    "name": "Elective Course Group",
    "module": "Academics",
    "fields": [
        {"fieldname": "group_name", "fieldtype": "Data", "label": "Group Name", "reqd": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "semester", "fieldtype": "Int", "label": "Semester Number"},
        {"fieldname": "elective_type", "fieldtype": "Select",
         "options": "DSE\nGE\nSEC\nAEC\nVAC", "reqd": 1},
        {"fieldname": "min_courses", "fieldtype": "Int", "label": "Minimum Courses to Select", "default": 1},
        {"fieldname": "max_courses", "fieldtype": "Int", "label": "Maximum Courses to Select", "default": 1},
        {"fieldname": "min_credits", "fieldtype": "Int", "label": "Minimum Credits"},
        {"fieldname": "max_credits", "fieldtype": "Int", "label": "Maximum Credits"},
        {"fieldname": "courses", "fieldtype": "Table", "options": "Elective Course Group Item"}
    ],
    "autoname": "format:{program}-{elective_type}-{semester}"
}
```

### Week 2-3: Course Registration System

#### 2.1 Course Registration

**DocType:** `Course Registration`
```json
{
    "doctype": "DocType",
    "name": "Course Registration",
    "module": "Academics",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1},
        {"fieldname": "student_name", "fieldtype": "Data", "fetch_from": "student.student_name", "read_only": 1},
        {"fieldname": "program", "fieldtype": "Link", "options": "Program", "reqd": 1},
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "reqd": 1},
        {"fieldname": "registration_date", "fieldtype": "Date", "default": "Today"},
        {"fieldname": "section_break", "fieldtype": "Section Break", "label": "Courses"},
        {"fieldname": "courses", "fieldtype": "Table", "options": "Course Registration Item"},
        {"fieldname": "summary_section", "fieldtype": "Section Break", "label": "Summary"},
        {"fieldname": "total_credits", "fieldtype": "Float", "read_only": 1},
        {"fieldname": "total_courses", "fieldtype": "Int", "read_only": 1},
        {"fieldname": "validation_status", "fieldtype": "Select",
         "options": "Pending\nValidated\nApproved\nRejected", "default": "Pending"},
        {"fieldname": "advisor_remarks", "fieldtype": "Small Text"}
    ],
    "permissions": [
        {"role": "University Student", "read": 1, "write": 1, "create": 1, "if_owner": 1},
        {"role": "University Faculty", "read": 1, "write": 1},
        {"role": "University Registrar", "read": 1, "write": 1, "create": 1, "submit": 1}
    ]
}
```

#### 2.2 Course Registration Controller

**File:** `university_erp/academics/doctype/course_registration/course_registration.py`
```python
import frappe
from frappe.model.document import Document
from university_erp.academics.cbcs import CBCSManager

class CourseRegistration(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_registration()

    def calculate_totals(self):
        """Calculate total credits and courses"""
        total_credits = 0
        for course in self.courses:
            credits = frappe.db.get_value("Course", course.course, "custom_credits")
            course.credits = credits or 0
            total_credits += course.credits

        self.total_credits = total_credits
        self.total_courses = len(self.courses)

    def validate_registration(self):
        """Validate course selection"""
        manager = CBCSManager(self.program)
        courses = [c.course for c in self.courses]

        result = manager.validate_course_selection(
            self.student,
            self.academic_term,
            courses
        )

        if not result["valid"]:
            frappe.throw("<br>".join(result["errors"]))

        self.validation_status = "Validated"

    def on_submit(self):
        """Create course enrollments on approval"""
        for course in self.courses:
            self.create_course_enrollment(course.course)

    def create_course_enrollment(self, course):
        """Create Course Enrollment record"""
        if frappe.db.exists("Course Enrollment", {
            "student": self.student,
            "course": course,
            "academic_term": self.academic_term
        }):
            return

        enrollment = frappe.new_doc("Course Enrollment")
        enrollment.student = self.student
        enrollment.course = course
        enrollment.academic_term = self.academic_term
        enrollment.enrollment_date = frappe.utils.today()
        enrollment.insert(ignore_permissions=True)
```

### Week 3-4: Timetable Management

#### 3.1 Timetable Slot Master

**DocType:** `Timetable Slot`
```json
{
    "doctype": "DocType",
    "name": "Timetable Slot",
    "module": "Academics",
    "fields": [
        {"fieldname": "slot_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "from_time", "fieldtype": "Time", "reqd": 1},
        {"fieldname": "to_time", "fieldtype": "Time", "reqd": 1},
        {"fieldname": "slot_type", "fieldtype": "Select",
         "options": "Lecture\nTutorial\nPractical\nBreak", "default": "Lecture"},
        {"fieldname": "duration_minutes", "fieldtype": "Int", "read_only": 1}
    ],
    "autoname": "field:slot_name"
}
```

#### 3.2 Classroom Master

**DocType:** `University Classroom`
```json
{
    "doctype": "DocType",
    "name": "University Classroom",
    "module": "Academics",
    "fields": [
        {"fieldname": "room_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "room_number", "fieldtype": "Data"},
        {"fieldname": "building", "fieldtype": "Data"},
        {"fieldname": "floor", "fieldtype": "Data"},
        {"fieldname": "room_type", "fieldtype": "Select",
         "options": "Classroom\nLecture Hall\nLab\nSeminar Room\nAuditorium"},
        {"fieldname": "capacity", "fieldtype": "Int"},
        {"fieldname": "department", "fieldtype": "Link", "options": "University Department"},
        {"fieldname": "has_projector", "fieldtype": "Check"},
        {"fieldname": "has_ac", "fieldtype": "Check"},
        {"fieldname": "is_active", "fieldtype": "Check", "default": 1}
    ],
    "autoname": "field:room_name"
}
```

#### 3.3 Timetable Generation

**File:** `university_erp/academics/timetable.py`
```python
import frappe
from frappe.utils import cint, cstr
from collections import defaultdict

class TimetableGenerator:
    """Generate and manage class timetables"""

    def __init__(self, academic_term, program=None, student_group=None):
        self.academic_term = academic_term
        self.program = program
        self.student_group = student_group
        self.slots = self.get_time_slots()
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    def get_time_slots(self):
        """Get all time slots"""
        return frappe.get_all(
            "Timetable Slot",
            filters={"slot_type": ["!=", "Break"]},
            fields=["name", "from_time", "to_time"],
            order_by="from_time"
        )

    def get_available_rooms(self, day, slot, capacity_required=0):
        """Get rooms available for a specific day and slot"""
        # Get all booked rooms
        booked = frappe.get_all(
            "Course Schedule",
            filters={
                "schedule_date": self.get_date_for_day(day),
                "from_time": slot.from_time,
                "to_time": slot.to_time
            },
            pluck="room"
        )

        # Get available rooms
        filters = {
            "is_active": 1,
            "name": ["not in", booked]
        }
        if capacity_required:
            filters["capacity"] = [">=", capacity_required]

        return frappe.get_all(
            "University Classroom",
            filters=filters,
            fields=["name", "room_name", "capacity", "room_type"]
        )

    def get_instructor_availability(self, instructor, day, slot):
        """Check if instructor is available"""
        existing = frappe.db.exists(
            "Course Schedule",
            {
                "instructor": instructor,
                "schedule_date": self.get_date_for_day(day),
                "from_time": slot.from_time,
                "to_time": slot.to_time
            }
        )
        return not existing

    def get_date_for_day(self, day_name):
        """Get the date for a specific day in current week"""
        today = frappe.utils.getdate()
        day_index = self.days.index(day_name)
        current_day_index = today.weekday()
        diff = day_index - current_day_index
        return frappe.utils.add_days(today, diff)

    def create_schedule(self, course, student_group, instructor, day, slot, room):
        """Create a Course Schedule entry"""
        schedule_date = self.get_date_for_day(day)

        # Check for conflicts
        if not self.get_instructor_availability(instructor, day, slot):
            frappe.throw(f"Instructor {instructor} is not available on {day} at {slot.from_time}")

        available_rooms = self.get_available_rooms(day, slot)
        if room not in [r.name for r in available_rooms]:
            frappe.throw(f"Room {room} is not available on {day} at {slot.from_time}")

        # Create schedule
        schedule = frappe.new_doc("Course Schedule")
        schedule.student_group = student_group
        schedule.course = course
        schedule.instructor = instructor
        schedule.room = room
        schedule.schedule_date = schedule_date
        schedule.from_time = slot.from_time
        schedule.to_time = slot.to_time
        schedule.insert()

        return schedule.name

    def get_timetable_view(self, entity_type, entity_name):
        """Get timetable for student group, instructor, or room"""
        filters = {}

        if entity_type == "student_group":
            filters["student_group"] = entity_name
        elif entity_type == "instructor":
            filters["instructor"] = entity_name
        elif entity_type == "room":
            filters["room"] = entity_name

        schedules = frappe.get_all(
            "Course Schedule",
            filters=filters,
            fields=[
                "name", "course", "student_group", "instructor",
                "room", "schedule_date", "from_time", "to_time"
            ],
            order_by="schedule_date, from_time"
        )

        # Organize by day and slot
        timetable = defaultdict(dict)
        for schedule in schedules:
            day = frappe.utils.getdate(schedule.schedule_date).strftime("%A")
            slot_key = f"{schedule.from_time}-{schedule.to_time}"
            timetable[day][slot_key] = schedule

        return dict(timetable)


@frappe.whitelist()
def get_timetable(entity_type, entity_name, academic_term):
    """API to get timetable"""
    generator = TimetableGenerator(academic_term)
    return generator.get_timetable_view(entity_type, entity_name)

@frappe.whitelist()
def create_schedule_entry(course, student_group, instructor, day, slot_name, room, academic_term):
    """API to create schedule entry"""
    generator = TimetableGenerator(academic_term)
    slot = frappe.get_doc("Timetable Slot", slot_name)
    return generator.create_schedule(course, student_group, instructor, day, slot, room)
```

### Week 4-5: Attendance Management

#### 4.1 Attendance Manager

**File:** `university_erp/academics/attendance.py`
```python
import frappe
from frappe.utils import getdate, flt

class AttendanceManager:
    """Manage student attendance using Education's Student Attendance"""

    def __init__(self):
        pass

    def mark_attendance(self, course_schedule, attendance_data):
        """Mark attendance for a class session"""
        schedule = frappe.get_doc("Course Schedule", course_schedule)

        for entry in attendance_data:
            student = entry.get("student")
            status = entry.get("status", "Present")

            # Check if already marked
            existing = frappe.db.exists("Student Attendance", {
                "student": student,
                "course_schedule": course_schedule,
                "date": schedule.schedule_date
            })

            if existing:
                frappe.db.set_value("Student Attendance", existing, "status", status)
            else:
                att = frappe.new_doc("Student Attendance")
                att.student = student
                att.student_group = schedule.student_group
                att.course_schedule = course_schedule
                att.date = schedule.schedule_date
                att.status = status
                att.custom_marked_by = frappe.session.user
                att.custom_marking_time = frappe.utils.now_datetime()
                att.insert(ignore_permissions=True)

        return True

    def get_attendance_percentage(self, student, course, academic_term=None):
        """Calculate attendance percentage for a student in a course"""
        # Get all scheduled classes for this course
        filters = {"course": course}

        if academic_term:
            term = frappe.get_doc("Academic Term", academic_term)
            filters["schedule_date"] = ["between", [term.term_start_date, term.term_end_date]]

        schedules = frappe.get_all("Course Schedule", filters=filters, pluck="name")

        if not schedules:
            return 0

        # Count attendance
        total_classes = len(schedules)

        present_count = frappe.db.count(
            "Student Attendance",
            {
                "student": student,
                "course_schedule": ["in", schedules],
                "status": ["in", ["Present", "Late"]]
            }
        )

        percentage = round((present_count / total_classes) * 100, 2) if total_classes else 0
        return percentage

    def get_student_attendance_report(self, student, academic_term):
        """Get detailed attendance report for student"""
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"student": student, "academic_term": academic_term},
            pluck="course"
        )

        report = []
        for course in enrollments:
            course_doc = frappe.get_doc("Course", course)
            percentage = self.get_attendance_percentage(student, course, academic_term)
            min_required = course_doc.custom_min_attendance or 75

            report.append({
                "course": course,
                "course_name": course_doc.course_name,
                "percentage": percentage,
                "min_required": min_required,
                "eligible": percentage >= min_required,
                "shortage": max(0, min_required - percentage)
            })

        return report

    def get_shortage_students(self, course, academic_term):
        """Get students with attendance below threshold"""
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"course": course, "academic_term": academic_term},
            pluck="student"
        )

        course_doc = frappe.get_doc("Course", course)
        min_required = course_doc.custom_min_attendance or 75

        shortage_list = []
        for student in enrollments:
            percentage = self.get_attendance_percentage(student, course, academic_term)

            if percentage < min_required:
                student_name = frappe.db.get_value("Student", student, "student_name")
                shortage_list.append({
                    "student": student,
                    "student_name": student_name,
                    "percentage": percentage,
                    "shortage": min_required - percentage
                })

        return sorted(shortage_list, key=lambda x: x["percentage"])

    def check_exam_eligibility(self, student, course, academic_term=None):
        """Check if student is eligible for exam based on attendance"""
        course_doc = frappe.get_doc("Course", course)
        min_required = course_doc.custom_min_attendance or 75
        percentage = self.get_attendance_percentage(student, course, academic_term)

        return {
            "student": student,
            "course": course,
            "percentage": percentage,
            "min_required": min_required,
            "eligible": percentage >= min_required,
            "shortage": max(0, min_required - percentage)
        }


@frappe.whitelist()
def mark_class_attendance(course_schedule, attendance_data):
    """API to mark attendance"""
    if isinstance(attendance_data, str):
        attendance_data = frappe.parse_json(attendance_data)

    manager = AttendanceManager()
    return manager.mark_attendance(course_schedule, attendance_data)

@frappe.whitelist()
def get_student_attendance(student, academic_term):
    """API to get student attendance"""
    manager = AttendanceManager()
    return manager.get_student_attendance_report(student, academic_term)

@frappe.whitelist()
def check_eligibility(student, course, academic_term=None):
    """API to check exam eligibility"""
    manager = AttendanceManager()
    return manager.check_exam_eligibility(student, course, academic_term)
```

#### 4.2 Attendance Marking UI

**File:** `university_erp/academics/page/mark_attendance/mark_attendance.js`
```javascript
frappe.pages['mark-attendance'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Mark Attendance',
        single_column: true
    });

    page.add_field({
        fieldname: 'course_schedule',
        label: 'Class Session',
        fieldtype: 'Link',
        options: 'Course Schedule',
        reqd: 1,
        change: function() {
            if (this.get_value()) {
                load_students(page, this.get_value());
            }
        }
    });

    page.add_field({
        fieldname: 'date',
        label: 'Date',
        fieldtype: 'Date',
        default: frappe.datetime.get_today(),
        read_only: 1
    });

    page.students_container = $('<div class="students-container"></div>').appendTo(page.main);

    page.add_button('Mark All Present', () => mark_all(page, 'Present'), 'btn-success');
    page.add_button('Mark All Absent', () => mark_all(page, 'Absent'), 'btn-danger');
    page.add_button('Submit Attendance', () => submit_attendance(page), 'btn-primary');
};

function load_students(page, course_schedule) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Course Schedule',
            name: course_schedule
        },
        callback: function(r) {
            if (r.message) {
                var schedule = r.message;
                page.set_value('date', schedule.schedule_date);

                // Get students in student group
                frappe.call({
                    method: 'education.education.doctype.student_group.student_group.get_students',
                    args: {
                        student_group: schedule.student_group
                    },
                    callback: function(r) {
                        if (r.message) {
                            render_students(page, r.message);
                        }
                    }
                });
            }
        }
    });
}

function render_students(page, students) {
    var html = `
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Roll No</th>
                    <th>Student Name</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    `;

    students.forEach(function(student, idx) {
        html += `
            <tr data-student="${student.student}">
                <td>${idx + 1}</td>
                <td>${student.student_name}</td>
                <td>
                    <select class="form-control attendance-status">
                        <option value="Present">Present</option>
                        <option value="Absent">Absent</option>
                        <option value="Late">Late</option>
                    </select>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    page.students_container.html(html);
}

function mark_all(page, status) {
    page.students_container.find('.attendance-status').val(status);
}

function submit_attendance(page) {
    var course_schedule = page.fields_dict.course_schedule.get_value();
    var attendance_data = [];

    page.students_container.find('tr[data-student]').each(function() {
        attendance_data.push({
            student: $(this).data('student'),
            status: $(this).find('.attendance-status').val()
        });
    });

    frappe.call({
        method: 'university_erp.academics.attendance.mark_class_attendance',
        args: {
            course_schedule: course_schedule,
            attendance_data: attendance_data
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint('Attendance marked successfully');
            }
        }
    });
}
```

### Week 5-6: Teaching Assignment & Workspaces

#### 5.1 Teaching Assignment

**DocType:** `Teaching Assignment`
```json
{
    "doctype": "DocType",
    "name": "Teaching Assignment",
    "module": "Academics",
    "fields": [
        {"fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", "reqd": 1},
        {"fieldname": "course", "fieldtype": "Link", "options": "Course", "reqd": 1},
        {"fieldname": "course_name", "fieldtype": "Data", "fetch_from": "course.course_name", "read_only": 1},
        {"fieldname": "faculty", "fieldtype": "Link", "options": "University Faculty", "reqd": 1},
        {"fieldname": "instructor", "fieldtype": "Link", "options": "Instructor",
         "description": "Linked Instructor record for Education module"},
        {"fieldname": "student_group", "fieldtype": "Link", "options": "Student Group"},
        {"fieldname": "assignment_type", "fieldtype": "Select",
         "options": "Lecture\nTutorial\nPractical\nLab", "default": "Lecture"},
        {"fieldname": "weekly_hours", "fieldtype": "Float"},
        {"fieldname": "is_course_coordinator", "fieldtype": "Check"},
        {"fieldname": "status", "fieldtype": "Select",
         "options": "Active\nCompleted\nCancelled", "default": "Active"}
    ],
    "permissions": [
        {"role": "University Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "University HOD", "read": 1, "write": 1, "create": 1},
        {"role": "University Faculty", "read": 1, "if_owner": 0}
    ]
}
```

#### 5.2 Academics Workspace

**File:** `university_erp/academics/workspace/academics/academics.json`
```json
{
    "doctype": "Workspace",
    "name": "Academics",
    "module": "Academics",
    "label": "Academics",
    "icon": "book",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University Registrar"},
        {"role": "University HOD"},
        {"role": "University Faculty"}
    ],
    "shortcuts": [
        {"label": "Programs", "link_to": "Program", "type": "DocType"},
        {"label": "Courses", "link_to": "Course", "type": "DocType"},
        {"label": "Course Schedule", "link_to": "Course Schedule", "type": "DocType"},
        {"label": "Mark Attendance", "link_to": "mark-attendance", "type": "Page"}
    ],
    "links": [
        {"type": "Card Break", "label": "Programs & Courses"},
        {"type": "Link", "label": "Program", "link_to": "Program", "link_type": "DocType"},
        {"type": "Link", "label": "Course", "link_to": "Course", "link_type": "DocType"},
        {"type": "Link", "label": "Student Group", "link_to": "Student Group", "link_type": "DocType"},

        {"type": "Card Break", "label": "Scheduling"},
        {"type": "Link", "label": "Course Schedule", "link_to": "Course Schedule", "link_type": "DocType"},
        {"type": "Link", "label": "Timetable Slot", "link_to": "Timetable Slot", "link_type": "DocType"},
        {"type": "Link", "label": "Classroom", "link_to": "University Classroom", "link_type": "DocType"},

        {"type": "Card Break", "label": "Attendance"},
        {"type": "Link", "label": "Mark Attendance", "link_to": "mark-attendance", "link_type": "Page"},
        {"type": "Link", "label": "Student Attendance", "link_to": "Student Attendance", "link_type": "DocType"},
        {"type": "Link", "label": "Attendance Report", "link_to": "Attendance Report", "link_type": "Report"},

        {"type": "Card Break", "label": "Faculty"},
        {"type": "Link", "label": "Teaching Assignment", "link_to": "Teaching Assignment", "link_type": "DocType"},
        {"type": "Link", "label": "Workload Report", "link_to": "Faculty Workload Report", "link_type": "Report"},

        {"type": "Card Break", "label": "Registration"},
        {"type": "Link", "label": "Course Registration", "link_to": "Course Registration", "link_type": "DocType"},
        {"type": "Link", "label": "Course Enrollment", "link_to": "Course Enrollment", "link_type": "DocType"}
    ]
}
```

---

## Output Checklist

### Code Deliverables
- [x] CBCSManager class with full validation
- [x] Course Prerequisite child table created
- [x] Elective Course Group DocType created
- [x] Course Registration DocType and controller
- [x] Timetable Slot master DocType
- [x] University Classroom DocType
- [x] TimetableGenerator class
- [x] AttendanceManager class with percentage calculation
- [x] Attendance marking page (JS/HTML)
- [x] Teaching Assignment DocType
- [x] Academics workspace configured

### CBCS Deliverables
- [x] Course types (Core, DSE, GE, SEC, AEC, VAC) defined
- [x] Credit calculation from L-T-P working
- [x] Prerequisite checking working
- [x] Elective group management working
- [x] Course registration validation working

### Timetable Deliverables
- [x] Time slots defined
- [x] Classroom master populated
- [x] Conflict detection working
- [x] Timetable view generation working
- [x] Schedule creation API working

### Attendance Deliverables
- [x] Attendance marking page functional
- [x] Percentage calculation accurate
- [x] Shortage detection working
- [x] Exam eligibility check working
- [x] Attendance reports generating

### Testing Checklist
- [x] Course registration validates CBCS rules
- [x] Prerequisites block invalid enrollments
- [x] Timetable detects instructor conflicts
- [x] Timetable detects room conflicts
- [x] Attendance percentage calculated correctly
- [x] Shortage alerts generated
- [x] Teaching assignments linked to instructors

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex CBCS rules | High | Medium | Thorough testing with real scenarios |
| Timetable conflicts | Medium | High | Implement conflict preview before save |
| Attendance sync issues | Low | Medium | Add manual correction capability |
| Performance with large data | Medium | Medium | Add pagination and caching |

---

## Dependencies for Next Phase

Phase 4 (Examinations & Results) requires:
- [x] Course enrollments working ✅
- [x] Student groups configured ✅
- [x] Attendance tracking active ✅
- [x] CBCS credits on courses ✅

**Status:** All dependencies met. Phase 4 completed.

---

## Sign-off Criteria

| Criteria | Required By |
|----------|-------------|
| CBCS validation tested | Academic Dean |
| Timetable generation verified | HOD |
| Attendance marking tested | Faculty Rep |
| Registrations working | Registrar |
| Documentation complete | Tech Writer |

---

## Implementation Summary

### Completed: 2025-12-31

**Phase 3 Implementation Status: ✅ COMPLETED**

All code deliverables have been implemented. The following components were created:

#### DocTypes Created (8 total):
1. **Course Prerequisite** - Child table for course prerequisites with mandatory flag
2. **Elective Course Group** - Groups of elective courses by type (DSE, GE, SEC, AEC) with min/max selection rules
3. **Elective Course Group Item** - Child table for courses in elective groups
4. **Course Registration** - Submittable DocType for student course selection with credit calculation
5. **Course Registration Item** - Child table for selected courses with course type tracking
6. **Timetable Slot** - Master for time slots with auto-calculated duration
7. **University Classroom** - Room/lab master with capacity, type, and facilities
8. **Teaching Assignment** - Faculty-course assignments with weekly hours and teaching type

#### Python Modules Created (3 total):
1. **academics/cbcs.py** - CBCSManager class with 8 course types, prerequisite validation, credit limits, elective validation
2. **academics/timetable.py** - TimetableGenerator with conflict detection for instructor/room/student group
3. **academics/attendance.py** - AttendanceManager with percentage calculation, exam eligibility, shortage detection

### Key Features:
- CBCS with 8 course types (Core, DSE, GE, SEC, AEC, VAC, Project, Internship)
- Credit calculation: Credits = L + T + (P/2)
- Prerequisite validation (Hard/Soft)
- Timetable conflict detection (instructor/room/student group)
- 75% minimum attendance for exam eligibility
- Faculty workload tracking

### Files Location:
```
frappe-bench/apps/university_erp/university_erp/
├── academics/
│   ├── cbcs.py
│   ├── timetable.py
│   ├── attendance.py
│   └── doctype/ (9 DocTypes)
```

### API Endpoints Created:

**CBCS Module (cbcs.py):**
- `validate_course_registration(student, semester, courses)` - Validates course selection against CBCS rules
- `calculate_credits_from_ltp(lecture_hours, tutorial_hours, practical_hours)` - Calculates credits using L-T-P formula
- `get_course_types()` - Returns CBCS course type definitions

**Timetable Module (timetable.py):**
- `get_timetable(entity_type, entity_name, academic_term)` - Gets timetable view
- `create_schedule_entry(course, student_group, instructor, day, slot_name, room, academic_term)` - Creates schedule with conflict check
- `check_conflicts(instructor, room, student_group, day, slot, academic_term)` - Three-way conflict detection

**Attendance Module (attendance.py):**
- `mark_attendance(course_schedule, attendance_data)` - Bulk attendance marking
- `get_attendance_percentage(student, course, academic_term)` - Calculates attendance percentage
- `check_exam_eligibility(student, course, academic_term)` - Checks 75% minimum requirement
- `get_shortage_students(course, academic_term, threshold)` - Lists students below threshold
- `get_student_attendance_summary(student, academic_term)` - Complete attendance summary

### Implementation Notes:

- All 8 DocTypes created and ready for database migration
- All 3 Python modules implemented with comprehensive API endpoints
- Teaching Assignment uses Education module's `Instructor` (temporary until Phase 6 University Faculty is created)
- Credit calculation formula verified: `Credits = L + T + (P/2)`
- Attendance eligibility threshold configurable via University Settings (default 75%)
- Conflict detection covers instructor, room, and student group overlaps

---

**Previous Phase:** [Phase 2: Admissions & Student Information System](phase_02_admissions_sis.md)
**Next Phase:** [Phase 4: Examinations & Results](phase_04_examinations.md)

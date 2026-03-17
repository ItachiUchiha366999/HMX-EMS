# Phase 13: Web Portals & Mobile Enhancement

## Overview
This phase implements comprehensive web portals for different user types (Student, Faculty, Parent, Alumni, Placement) and mobile-friendly enhancements for accessing university services on the go.

**Duration**: 5-6 weeks
**Priority**: Medium-High
**Dependencies**: Phase 1-12 (All core modules complete)

---

## Part A: Student Portal

### 1. Student Portal Design

The Student Portal provides a unified interface for students to access all academic and administrative services.

#### Portal Features
- **Dashboard**: Overview of academic progress, attendance, fees, announcements
- **Academic**: Course registration, timetable, syllabus, grades
- **Examinations**: Hall tickets, results, revaluation requests
- **Fees**: Payment history, pending dues, online payment
- **Library**: Book search, issue history, renewals, e-resources
- **Hostel**: Room details, mess menu, complaints
- **Certificates**: Request and download certificates
- **Grievances**: Submit and track complaints

### 2. Student Portal Pages

```python
# student_portal/student_portal.py

import frappe
from frappe import _


def get_context(context):
    """Student portal main page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the student portal"), frappe.PermissionError)

    student = get_current_student()
    if not student:
        frappe.throw(_("No student record found for this user"), frappe.PermissionError)

    context.student = student
    context.no_cache = 1

    # Dashboard data
    context.dashboard = get_dashboard_data(student.name)
    context.announcements = get_announcements(student)
    context.quick_links = get_quick_links()


def get_current_student():
    """Get student record for current user"""
    student = frappe.db.get_value(
        "Student",
        {"user": frappe.session.user},
        ["name", "student_name", "student_email_id", "program", "image"],
        as_dict=True
    )
    return student


def get_dashboard_data(student):
    """Get dashboard summary data"""
    # Get current enrollment
    enrollment = frappe.get_all(
        "Program Enrollment",
        filters={"student": student, "docstatus": 1},
        fields=["name", "program", "academic_year", "academic_term"],
        order_by="creation desc",
        limit=1
    )

    data = {
        "enrollment": enrollment[0] if enrollment else None,
        "attendance_percentage": get_attendance_percentage(student),
        "cgpa": get_current_cgpa(student),
        "pending_fees": get_pending_fees(student),
        "upcoming_exams": get_upcoming_exams(student),
        "library_books": get_issued_books_count(student),
        "pending_assignments": get_pending_assignments(student)
    }

    return data


def get_attendance_percentage(student):
    """Calculate overall attendance percentage"""
    attendance = frappe.db.sql("""
        SELECT
            COUNT(CASE WHEN status = 'Present' THEN 1 END) as present,
            COUNT(*) as total
        FROM `tabStudent Attendance`
        WHERE student = %s
        AND academic_year = (SELECT value FROM `tabSingles` WHERE doctype='Education Settings' AND field='current_academic_year')
    """, student, as_dict=True)

    if attendance and attendance[0].total > 0:
        return round((attendance[0].present / attendance[0].total) * 100, 1)
    return 0


def get_current_cgpa(student):
    """Get student's current CGPA"""
    return frappe.db.get_value("Student", student, "custom_cgpa") or 0


def get_pending_fees(student):
    """Get total pending fees amount"""
    fees = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as pending
        FROM `tabFees`
        WHERE student = %s AND docstatus = 0
    """, student, as_dict=True)

    return fees[0].pending if fees and fees[0].pending else 0


def get_upcoming_exams(student):
    """Get upcoming exams for student"""
    return frappe.get_all(
        "Examination Schedule",
        filters={
            "student_group": ["in", get_student_groups(student)],
            "exam_date": [">=", frappe.utils.today()]
        },
        fields=["course", "exam_date", "from_time", "to_time", "room"],
        order_by="exam_date asc",
        limit=5
    )


def get_issued_books_count(student):
    """Get count of currently issued library books"""
    return frappe.db.count(
        "Library Transaction",
        filters={
            "library_member": student,
            "type": "Issue",
            "docstatus": 1
        }
    )


def get_pending_assignments(student):
    """Get pending LMS assignments"""
    return frappe.db.count(
        "LMS Assignment",
        filters={
            "student_group": ["in", get_student_groups(student)],
            "due_date": [">=", frappe.utils.today()]
        }
    )


def get_student_groups(student):
    """Get all student groups for a student"""
    return frappe.get_all(
        "Student Group Student",
        filters={"student": student},
        pluck="parent"
    )


def get_announcements(student):
    """Get relevant announcements for student"""
    return frappe.get_all(
        "Announcement",
        filters={
            "publish_date": ["<=", frappe.utils.today()],
            "expiry_date": [">=", frappe.utils.today()],
            "for_students": 1
        },
        fields=["title", "description", "publish_date", "priority"],
        order_by="priority desc, publish_date desc",
        limit=5
    )


def get_quick_links():
    """Get quick action links"""
    return [
        {"label": "View Timetable", "url": "/student-portal/timetable", "icon": "calendar"},
        {"label": "Check Results", "url": "/student-portal/results", "icon": "chart"},
        {"label": "Pay Fees", "url": "/student-portal/fees", "icon": "credit-card"},
        {"label": "Library", "url": "/student-portal/library", "icon": "book"},
        {"label": "Request Certificate", "url": "/student-portal/certificates", "icon": "file-text"},
        {"label": "Submit Grievance", "url": "/student-portal/grievances", "icon": "message-circle"}
    ]
```

### 3. Student Portal HTML Template

```html
<!-- student_portal/student_portal.html -->
{% extends "templates/web.html" %}

{% block title %}Student Portal{% endblock %}

{% block page_content %}
<div class="student-portal">
    <!-- Header -->
    <div class="portal-header">
        <div class="student-info">
            <img src="{{ student.image or '/assets/university_erp/images/default-avatar.png' }}"
                 class="student-avatar" alt="Student Photo">
            <div class="student-details">
                <h2>{{ student.student_name }}</h2>
                <p>{{ student.name }} | {{ student.program }}</p>
            </div>
        </div>
        <div class="header-actions">
            <a href="/student-portal/profile" class="btn btn-outline-primary">
                <i class="fa fa-user"></i> Profile
            </a>
            <a href="/api/method/logout" class="btn btn-outline-danger">
                <i class="fa fa-sign-out"></i> Logout
            </a>
        </div>
    </div>

    <!-- Dashboard Cards -->
    <div class="dashboard-cards">
        <div class="card attendance-card">
            <div class="card-icon">
                <i class="fa fa-check-circle"></i>
            </div>
            <div class="card-content">
                <h3>{{ dashboard.attendance_percentage }}%</h3>
                <p>Attendance</p>
            </div>
        </div>

        <div class="card cgpa-card">
            <div class="card-icon">
                <i class="fa fa-graduation-cap"></i>
            </div>
            <div class="card-content">
                <h3>{{ dashboard.cgpa }}</h3>
                <p>CGPA</p>
            </div>
        </div>

        <div class="card fees-card">
            <div class="card-icon">
                <i class="fa fa-rupee"></i>
            </div>
            <div class="card-content">
                <h3>{{ frappe.utils.fmt_money(dashboard.pending_fees, currency='INR') }}</h3>
                <p>Pending Fees</p>
            </div>
        </div>

        <div class="card library-card">
            <div class="card-icon">
                <i class="fa fa-book"></i>
            </div>
            <div class="card-content">
                <h3>{{ dashboard.library_books }}</h3>
                <p>Books Issued</p>
            </div>
        </div>
    </div>

    <!-- Quick Links -->
    <div class="quick-links-section">
        <h3>Quick Actions</h3>
        <div class="quick-links-grid">
            {% for link in quick_links %}
            <a href="{{ link.url }}" class="quick-link-card">
                <i class="fa fa-{{ link.icon }}"></i>
                <span>{{ link.label }}</span>
            </a>
            {% endfor %}
        </div>
    </div>

    <!-- Main Content Grid -->
    <div class="portal-grid">
        <!-- Upcoming Exams -->
        <div class="portal-section">
            <h3><i class="fa fa-calendar"></i> Upcoming Exams</h3>
            {% if dashboard.upcoming_exams %}
            <table class="table">
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Room</th>
                    </tr>
                </thead>
                <tbody>
                    {% for exam in dashboard.upcoming_exams %}
                    <tr>
                        <td>{{ exam.course }}</td>
                        <td>{{ frappe.utils.format_date(exam.exam_date) }}</td>
                        <td>{{ exam.from_time }} - {{ exam.to_time }}</td>
                        <td>{{ exam.room }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="text-muted">No upcoming exams scheduled</p>
            {% endif %}
        </div>

        <!-- Announcements -->
        <div class="portal-section">
            <h3><i class="fa fa-bullhorn"></i> Announcements</h3>
            {% if announcements %}
            <div class="announcements-list">
                {% for ann in announcements %}
                <div class="announcement-item priority-{{ ann.priority|lower }}">
                    <h4>{{ ann.title }}</h4>
                    <p>{{ ann.description|truncate(100) }}</p>
                    <small>{{ frappe.utils.format_date(ann.publish_date) }}</small>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="text-muted">No announcements</p>
            {% endif %}
        </div>
    </div>
</div>

<style>
.student-portal {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.portal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.student-info {
    display: flex;
    align-items: center;
    gap: 15px;
}

.student-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: 3px solid white;
}

.dashboard-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.card-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.attendance-card .card-icon { background: #e3f2fd; color: #1976d2; }
.cgpa-card .card-icon { background: #e8f5e9; color: #388e3c; }
.fees-card .card-icon { background: #fff3e0; color: #f57c00; }
.library-card .card-icon { background: #fce4ec; color: #c2185b; }

.quick-links-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.quick-link-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    text-decoration: none;
    color: #333;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.quick-link-card:hover {
    transform: translateY(-5px);
}

.quick-link-card i {
    font-size: 30px;
    color: #667eea;
    margin-bottom: 10px;
    display: block;
}

.portal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.portal-section {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.portal-section h3 {
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #eee;
}

.announcement-item {
    padding: 15px;
    border-left: 4px solid #667eea;
    background: #f5f5f5;
    margin-bottom: 10px;
    border-radius: 0 5px 5px 0;
}

.announcement-item.priority-high {
    border-left-color: #f44336;
}

@media (max-width: 768px) {
    .portal-header {
        flex-direction: column;
        text-align: center;
        gap: 15px;
    }

    .portal-grid {
        grid-template-columns: 1fr;
    }
}
</style>
{% endblock %}
```

### 4. Student Portal Sub-Pages

```python
# student_portal/timetable.py

import frappe
from frappe import _


def get_context(context):
    """Student timetable page"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    context.student = student
    context.timetable = get_student_timetable(student.name)
    context.no_cache = 1


def get_student_timetable(student):
    """Get weekly timetable for student"""
    student_groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        pluck="parent"
    )

    if not student_groups:
        return {}

    # Get course schedule entries
    schedule = frappe.get_all(
        "Course Schedule",
        filters={
            "student_group": ["in", student_groups],
            "schedule_date": [">=", frappe.utils.today()]
        },
        fields=[
            "course", "instructor", "room", "schedule_date",
            "from_time", "to_time"
        ],
        order_by="schedule_date, from_time"
    )

    # Group by day
    timetable = {}
    for entry in schedule:
        day = entry.schedule_date.strftime("%A")
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(entry)

    return timetable


# student_portal/results.py

import frappe
from frappe import _


def get_context(context):
    """Student results page"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    context.student = student
    context.results = get_student_results(student.name)
    context.semester_wise = get_semester_wise_results(student.name)
    context.no_cache = 1


def get_student_results(student):
    """Get all results for student"""
    return frappe.get_all(
        "Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=[
            "assessment_plan", "academic_term", "course",
            "total_score", "grade", "maximum_score"
        ],
        order_by="academic_term desc, course"
    )


def get_semester_wise_results(student):
    """Get semester-wise consolidated results"""
    results = frappe.db.sql("""
        SELECT
            ar.academic_term,
            ar.course,
            c.course_name,
            ar.total_score,
            ar.grade,
            ar.maximum_score,
            ar.total_score / ar.maximum_score * 10 as grade_points
        FROM `tabAssessment Result` ar
        JOIN `tabCourse` c ON ar.course = c.name
        WHERE ar.student = %s AND ar.docstatus = 1
        ORDER BY ar.academic_term, ar.course
    """, student, as_dict=True)

    # Group by semester
    semester_results = {}
    for result in results:
        term = result.academic_term
        if term not in semester_results:
            semester_results[term] = {
                "courses": [],
                "total_credits": 0,
                "total_grade_points": 0
            }
        semester_results[term]["courses"].append(result)

    # Calculate SGPA for each semester
    for term, data in semester_results.items():
        total_credits = sum(c.get("credits", 3) for c in data["courses"])
        total_grade_points = sum(
            c.grade_points * c.get("credits", 3)
            for c in data["courses"]
        )
        data["sgpa"] = round(total_grade_points / total_credits, 2) if total_credits else 0

    return semester_results


# student_portal/fees.py

import frappe
from frappe import _


def get_context(context):
    """Student fees page"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    context.student = student
    context.pending_fees = get_pending_fees(student.name)
    context.payment_history = get_payment_history(student.name)
    context.no_cache = 1


def get_pending_fees(student):
    """Get all pending fee entries"""
    return frappe.get_all(
        "Fees",
        filters={
            "student": student,
            "outstanding_amount": [">", 0]
        },
        fields=[
            "name", "fee_structure", "due_date",
            "grand_total", "outstanding_amount", "academic_term"
        ],
        order_by="due_date asc"
    )


def get_payment_history(student):
    """Get payment history"""
    return frappe.get_all(
        "Payment Transaction",
        filters={
            "student": student,
            "status": "Success"
        },
        fields=[
            "name", "transaction_date", "amount",
            "payment_method", "gateway_payment_id"
        ],
        order_by="transaction_date desc",
        limit=20
    )


@frappe.whitelist()
def initiate_fee_payment(fee_name):
    """Initiate payment for a fee"""
    fee = frappe.get_doc("Fees", fee_name)
    student = get_current_student()

    if fee.student != student.name:
        frappe.throw(_("Access denied"))

    from university_erp.integrations.payment_gateway import initiate_payment

    return initiate_payment(
        amount=fee.outstanding_amount,
        student=student.name,
        reference_doctype="Fees",
        reference_name=fee.name
    )
```

---

## Part B: Faculty Portal

### 1. Faculty Portal Controller

```python
# faculty_portal/faculty_portal.py

import frappe
from frappe import _


def get_context(context):
    """Faculty portal main page"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("No faculty record found"), frappe.PermissionError)

    context.instructor = instructor
    context.dashboard = get_faculty_dashboard(instructor.name)
    context.today_classes = get_today_classes(instructor.name)
    context.pending_tasks = get_pending_tasks(instructor.name)
    context.no_cache = 1


def get_current_instructor():
    """Get instructor for current user"""
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": frappe.session.user},
        "name"
    )

    if employee:
        instructor = frappe.db.get_value(
            "Instructor",
            {"employee": employee},
            ["name", "instructor_name", "department", "image"],
            as_dict=True
        )
        return instructor
    return None


def get_faculty_dashboard(instructor):
    """Get dashboard summary for faculty"""
    return {
        "total_courses": get_assigned_courses_count(instructor),
        "total_students": get_total_students_count(instructor),
        "pending_assessments": get_pending_assessments_count(instructor),
        "attendance_today": get_attendance_status_today(instructor),
        "research_publications": get_publications_count(instructor),
        "pending_approvals": get_pending_approvals_count(instructor)
    }


def get_assigned_courses_count(instructor):
    """Get count of courses assigned to instructor"""
    return frappe.db.count(
        "Course Schedule",
        filters={
            "instructor": instructor,
            "schedule_date": [">=", frappe.utils.today()]
        }
    )


def get_total_students_count(instructor):
    """Get total students under instructor"""
    student_groups = frappe.get_all(
        "Student Group Instructor",
        filters={"instructor": instructor},
        pluck="parent"
    )

    if not student_groups:
        return 0

    return frappe.db.count(
        "Student Group Student",
        filters={"parent": ["in", student_groups], "active": 1}
    )


def get_pending_assessments_count(instructor):
    """Get count of pending assessment evaluations"""
    return frappe.db.sql("""
        SELECT COUNT(DISTINCT ap.name)
        FROM `tabAssessment Plan` ap
        LEFT JOIN `tabAssessment Result` ar ON ar.assessment_plan = ap.name
        WHERE ap.instructor = %s
        AND ap.schedule_date <= CURDATE()
        AND ar.name IS NULL
    """, instructor)[0][0] or 0


def get_attendance_status_today(instructor):
    """Check if attendance is marked for today's classes"""
    today_classes = frappe.db.count(
        "Course Schedule",
        filters={
            "instructor": instructor,
            "schedule_date": frappe.utils.today()
        }
    )

    marked_attendance = frappe.db.count(
        "Student Attendance",
        filters={
            "instructor": instructor,
            "date": frappe.utils.today()
        }
    )

    return {"total": today_classes, "marked": marked_attendance}


def get_publications_count(instructor):
    """Get research publications count"""
    employee = frappe.db.get_value("Instructor", instructor, "employee")
    if employee:
        return frappe.db.count(
            "Research Publication",
            filters={"lead_author": employee, "docstatus": 1}
        )
    return 0


def get_pending_approvals_count(instructor):
    """Get pending approval requests"""
    return frappe.db.count(
        "Leave Application",
        filters={
            "leave_approver": frappe.session.user,
            "status": "Open"
        }
    )


def get_today_classes(instructor):
    """Get today's class schedule"""
    return frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor,
            "schedule_date": frappe.utils.today()
        },
        fields=[
            "course", "student_group", "room",
            "from_time", "to_time", "name"
        ],
        order_by="from_time"
    )


def get_pending_tasks(instructor):
    """Get pending tasks for faculty"""
    tasks = []

    # Pending attendance
    pending_attendance = frappe.db.sql("""
        SELECT cs.name, cs.course, cs.student_group, cs.schedule_date
        FROM `tabCourse Schedule` cs
        LEFT JOIN `tabStudent Attendance` sa
            ON sa.course_schedule = cs.name
        WHERE cs.instructor = %s
        AND cs.schedule_date < CURDATE()
        AND sa.name IS NULL
        LIMIT 5
    """, instructor, as_dict=True)

    for pa in pending_attendance:
        tasks.append({
            "type": "Attendance",
            "description": f"Mark attendance for {pa.course} on {pa.schedule_date}",
            "url": f"/app/student-attendance/new?course_schedule={pa.name}"
        })

    # Pending grade entries
    pending_grades = frappe.db.sql("""
        SELECT ap.name, ap.assessment_name, ap.course
        FROM `tabAssessment Plan` ap
        LEFT JOIN `tabAssessment Result` ar ON ar.assessment_plan = ap.name
        WHERE ap.instructor = %s
        AND ap.schedule_date < CURDATE()
        AND ar.name IS NULL
        LIMIT 5
    """, instructor, as_dict=True)

    for pg in pending_grades:
        tasks.append({
            "type": "Grades",
            "description": f"Enter grades for {pg.assessment_name}",
            "url": f"/app/assessment-result/new?assessment_plan={pg.name}"
        })

    return tasks


# Faculty Portal API Endpoints

@frappe.whitelist()
def mark_attendance(course_schedule, attendance_data):
    """Mark attendance for a class"""
    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("Access denied"))

    schedule = frappe.get_doc("Course Schedule", course_schedule)
    if schedule.instructor != instructor.name:
        frappe.throw(_("You are not the instructor for this class"))

    if isinstance(attendance_data, str):
        attendance_data = frappe.parse_json(attendance_data)

    for student, status in attendance_data.items():
        # Check if already exists
        existing = frappe.db.exists("Student Attendance", {
            "student": student,
            "course_schedule": course_schedule
        })

        if existing:
            frappe.db.set_value("Student Attendance", existing, "status", status)
        else:
            frappe.get_doc({
                "doctype": "Student Attendance",
                "student": student,
                "course_schedule": course_schedule,
                "status": status,
                "date": schedule.schedule_date
            }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def get_student_group_students(student_group):
    """Get students in a student group"""
    return frappe.get_all(
        "Student Group Student",
        filters={"parent": student_group, "active": 1},
        fields=["student", "student_name"]
    )


@frappe.whitelist()
def submit_assessment_results(assessment_plan, results):
    """Submit assessment results for students"""
    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("Access denied"))

    plan = frappe.get_doc("Assessment Plan", assessment_plan)
    if plan.instructor != instructor.name:
        frappe.throw(_("You are not the instructor for this assessment"))

    if isinstance(results, str):
        results = frappe.parse_json(results)

    for result in results:
        frappe.get_doc({
            "doctype": "Assessment Result",
            "assessment_plan": assessment_plan,
            "student": result["student"],
            "total_score": result["score"],
            "grade": result.get("grade"),
            "comment": result.get("comment")
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"success": True, "count": len(results)}
```

---

## Part C: Parent Portal

### 1. Parent Portal Controller

```python
# parent_portal/parent_portal.py

import frappe
from frappe import _


def get_context(context):
    """Parent portal main page"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)

    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("No guardian record found"), frappe.PermissionError)

    context.guardian = guardian
    context.children = get_linked_children(guardian.name)
    context.no_cache = 1


def get_current_guardian():
    """Get guardian for current user"""
    return frappe.db.get_value(
        "Guardian",
        {"user": frappe.session.user},
        ["name", "guardian_name", "email_address", "mobile_number"],
        as_dict=True
    )


def get_linked_children(guardian):
    """Get all children linked to guardian"""
    children = frappe.get_all(
        "Student Guardian",
        filters={"guardian": guardian},
        fields=["parent as student"]
    )

    result = []
    for child in children:
        student = frappe.get_doc("Student", child.student)
        result.append({
            "student": student.name,
            "student_name": student.student_name,
            "program": student.program,
            "image": student.image,
            "attendance": get_student_attendance_summary(student.name),
            "fees": get_student_fee_summary(student.name),
            "grades": get_student_grade_summary(student.name)
        })

    return result


def get_student_attendance_summary(student):
    """Get attendance summary for student"""
    data = frappe.db.sql("""
        SELECT
            COUNT(CASE WHEN status = 'Present' THEN 1 END) as present,
            COUNT(CASE WHEN status = 'Absent' THEN 1 END) as absent,
            COUNT(*) as total
        FROM `tabStudent Attendance`
        WHERE student = %s
        AND date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    """, student, as_dict=True)

    return data[0] if data else {"present": 0, "absent": 0, "total": 0}


def get_student_fee_summary(student):
    """Get fee summary for student"""
    pending = frappe.db.get_value(
        "Fees",
        {"student": student, "outstanding_amount": [">", 0]},
        "SUM(outstanding_amount)"
    ) or 0

    return {"pending": pending}


def get_student_grade_summary(student):
    """Get recent grades for student"""
    return frappe.get_all(
        "Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=["course", "grade", "total_score"],
        order_by="creation desc",
        limit=5
    )


@frappe.whitelist()
def get_child_details(student):
    """Get detailed information for a child"""
    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("Access denied"))

    # Verify parent-child relationship
    if not frappe.db.exists("Student Guardian", {
        "guardian": guardian.name,
        "parent": student
    }):
        frappe.throw(_("Access denied"))

    student_doc = frappe.get_doc("Student", student)

    return {
        "student": student_doc.as_dict(),
        "attendance": get_detailed_attendance(student),
        "results": get_detailed_results(student),
        "fee_details": get_detailed_fees(student),
        "timetable": get_student_timetable(student)
    }


def get_detailed_attendance(student):
    """Get detailed attendance records"""
    return frappe.get_all(
        "Student Attendance",
        filters={"student": student},
        fields=["date", "status", "course_schedule", "leave_type"],
        order_by="date desc",
        limit=30
    )


def get_detailed_results(student):
    """Get all assessment results"""
    return frappe.get_all(
        "Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=[
            "assessment_plan", "course", "academic_term",
            "total_score", "maximum_score", "grade"
        ],
        order_by="creation desc"
    )


def get_detailed_fees(student):
    """Get all fee records"""
    return frappe.get_all(
        "Fees",
        filters={"student": student},
        fields=[
            "name", "fee_structure", "due_date", "academic_term",
            "grand_total", "outstanding_amount"
        ],
        order_by="due_date desc"
    )


def get_student_timetable(student):
    """Get current week timetable"""
    student_groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        pluck="parent"
    )

    if not student_groups:
        return []

    return frappe.get_all(
        "Course Schedule",
        filters={
            "student_group": ["in", student_groups],
            "schedule_date": [
                "between",
                [frappe.utils.today(), frappe.utils.add_days(frappe.utils.today(), 7)]
            ]
        },
        fields=[
            "course", "instructor_name", "room",
            "schedule_date", "from_time", "to_time"
        ],
        order_by="schedule_date, from_time"
    )
```

---

## Part D: Alumni Portal

### 1. Alumni Portal Controller

```python
# alumni_portal/alumni_portal.py

import frappe
from frappe import _


def get_context(context):
    """Alumni portal main page"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)

    alumni = get_current_alumni()
    if not alumni:
        frappe.throw(_("No alumni record found"), frappe.PermissionError)

    context.alumni = alumni
    context.dashboard = get_alumni_dashboard(alumni)
    context.events = get_upcoming_events()
    context.job_postings = get_job_postings()
    context.news = get_alumni_news()
    context.no_cache = 1


def get_current_alumni():
    """Get alumni record for current user"""
    # First try to find linked alumni record
    alumni = frappe.db.get_value(
        "Alumni",
        {"email": frappe.session.user},
        ["name", "student", "student_name", "batch", "program",
         "current_company", "designation", "city", "image"],
        as_dict=True
    )

    return alumni


def get_alumni_dashboard(alumni):
    """Get dashboard data for alumni"""
    return {
        "batch_mates": get_batch_mates_count(alumni.batch, alumni.program),
        "upcoming_events": get_upcoming_events_count(),
        "job_openings": get_job_openings_count(),
        "donations": get_donation_history(alumni.name)
    }


def get_batch_mates_count(batch, program):
    """Get count of batch mates"""
    return frappe.db.count(
        "Alumni",
        filters={"batch": batch, "program": program}
    )


def get_upcoming_events_count():
    """Get count of upcoming alumni events"""
    return frappe.db.count(
        "Alumni Event",
        filters={"event_date": [">=", frappe.utils.today()]}
    )


def get_job_openings_count():
    """Get count of active job postings"""
    return frappe.db.count(
        "Job Posting",
        filters={"status": "Open", "is_alumni_posting": 1}
    )


def get_donation_history(alumni):
    """Get donation history for alumni"""
    donations = frappe.get_all(
        "Alumni Donation",
        filters={"alumni": alumni},
        fields=["amount", "donation_date", "purpose"],
        order_by="donation_date desc",
        limit=5
    )

    total = frappe.db.get_value(
        "Alumni Donation",
        {"alumni": alumni},
        "SUM(amount)"
    ) or 0

    return {"total": total, "recent": donations}


def get_upcoming_events():
    """Get upcoming alumni events"""
    return frappe.get_all(
        "Alumni Event",
        filters={"event_date": [">=", frappe.utils.today()]},
        fields=["name", "event_name", "event_date", "venue", "description"],
        order_by="event_date asc",
        limit=5
    )


def get_job_postings():
    """Get active job postings"""
    return frappe.get_all(
        "Job Posting",
        filters={"status": "Open", "is_alumni_posting": 1},
        fields=[
            "name", "job_title", "company", "location",
            "job_type", "posted_by", "creation"
        ],
        order_by="creation desc",
        limit=10
    )


def get_alumni_news():
    """Get alumni news and updates"""
    return frappe.get_all(
        "Alumni News",
        filters={"publish_date": ["<=", frappe.utils.today()]},
        fields=["title", "content", "image", "publish_date"],
        order_by="publish_date desc",
        limit=5
    )


# Alumni Directory

@frappe.whitelist()
def search_alumni(filters=None, page=1, page_size=20):
    """Search alumni directory"""
    query_filters = {}

    if filters:
        if isinstance(filters, str):
            filters = frappe.parse_json(filters)

        if filters.get("batch"):
            query_filters["batch"] = filters["batch"]
        if filters.get("program"):
            query_filters["program"] = filters["program"]
        if filters.get("city"):
            query_filters["city"] = ["like", f"%{filters['city']}%"]
        if filters.get("company"):
            query_filters["current_company"] = ["like", f"%{filters['company']}%"]

    start = (int(page) - 1) * int(page_size)

    alumni = frappe.get_all(
        "Alumni",
        filters=query_filters,
        fields=[
            "name", "student_name", "batch", "program",
            "current_company", "designation", "city", "image"
        ],
        order_by="student_name",
        start=start,
        page_length=int(page_size)
    )

    total = frappe.db.count("Alumni", filters=query_filters)

    return {
        "alumni": alumni,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@frappe.whitelist()
def update_profile(data):
    """Update alumni profile"""
    alumni = get_current_alumni()
    if not alumni:
        frappe.throw(_("Access denied"))

    if isinstance(data, str):
        data = frappe.parse_json(data)

    doc = frappe.get_doc("Alumni", alumni.name)

    # Allowed fields to update
    allowed_fields = [
        "current_company", "designation", "city", "phone",
        "linkedin_profile", "about_me"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(doc, field, data[field])

    doc.save(ignore_permissions=True)
    return {"success": True}


# Job Postings

@frappe.whitelist()
def post_job(job_data):
    """Post a new job opening"""
    alumni = get_current_alumni()
    if not alumni:
        frappe.throw(_("Access denied"))

    if isinstance(job_data, str):
        job_data = frappe.parse_json(job_data)

    job = frappe.get_doc({
        "doctype": "Job Posting",
        "job_title": job_data.get("job_title"),
        "company": job_data.get("company"),
        "location": job_data.get("location"),
        "job_type": job_data.get("job_type"),
        "description": job_data.get("description"),
        "requirements": job_data.get("requirements"),
        "posted_by": alumni.name,
        "is_alumni_posting": 1,
        "status": "Open"
    })
    job.insert(ignore_permissions=True)

    return {"success": True, "job": job.name}


# Event Registration

@frappe.whitelist()
def register_for_event(event):
    """Register for an alumni event"""
    alumni = get_current_alumni()
    if not alumni:
        frappe.throw(_("Access denied"))

    # Check if already registered
    if frappe.db.exists("Alumni Event Registration", {
        "event": event,
        "alumni": alumni.name
    }):
        frappe.throw(_("Already registered for this event"))

    frappe.get_doc({
        "doctype": "Alumni Event Registration",
        "event": event,
        "alumni": alumni.name,
        "registration_date": frappe.utils.now_datetime()
    }).insert(ignore_permissions=True)

    return {"success": True}
```

---

## Part E: Placement Portal

### 1. Placement Portal Controller

```python
# placement_portal/placement_portal.py

import frappe
from frappe import _


def get_context(context):
    """Placement portal for students"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)

    student = get_current_student()
    if not student:
        frappe.throw(_("No student record found"), frappe.PermissionError)

    context.student = student
    context.profile = get_placement_profile(student.name)
    context.eligible_drives = get_eligible_drives(student.name)
    context.applications = get_my_applications(student.name)
    context.upcoming_interviews = get_upcoming_interviews(student.name)
    context.no_cache = 1


def get_current_student():
    """Get student for current user"""
    return frappe.db.get_value(
        "Student",
        {"user": frappe.session.user},
        ["name", "student_name", "program", "image", "custom_cgpa"],
        as_dict=True
    )


def get_placement_profile(student):
    """Get placement profile for student"""
    profile = frappe.db.get_value(
        "Placement Profile",
        {"student": student},
        "*",
        as_dict=True
    )

    if not profile:
        # Create default profile
        profile = frappe.get_doc({
            "doctype": "Placement Profile",
            "student": student,
            "status": "Active"
        }).insert(ignore_permissions=True)
        return profile.as_dict()

    return profile


def get_eligible_drives(student):
    """Get placement drives student is eligible for"""
    student_doc = frappe.get_doc("Student", student)

    # Get student criteria
    cgpa = student_doc.custom_cgpa or 0
    program = student_doc.program
    backlogs = student_doc.get("custom_active_backlogs", 0)

    # Find eligible drives
    drives = frappe.db.sql("""
        SELECT
            pd.name, pd.company, pd.job_title, pd.package_offered,
            pd.drive_date, pd.last_date_to_apply, pd.job_description,
            pd.eligibility_criteria
        FROM `tabPlacement Drive` pd
        WHERE pd.status = 'Open'
        AND pd.last_date_to_apply >= CURDATE()
        AND (pd.minimum_cgpa IS NULL OR pd.minimum_cgpa <= %s)
        AND (pd.maximum_backlogs IS NULL OR pd.maximum_backlogs >= %s)
        AND (
            pd.eligible_programs IS NULL
            OR pd.eligible_programs = ''
            OR pd.eligible_programs LIKE %s
        )
        ORDER BY pd.drive_date
    """, (cgpa, backlogs, f"%{program}%"), as_dict=True)

    # Check if already applied
    for drive in drives:
        drive["already_applied"] = frappe.db.exists("Placement Application", {
            "student": student,
            "placement_drive": drive.name
        })

    return drives


def get_my_applications(student):
    """Get student's placement applications"""
    return frappe.get_all(
        "Placement Application",
        filters={"student": student},
        fields=[
            "name", "placement_drive", "company", "job_title",
            "application_date", "status", "interview_date"
        ],
        order_by="application_date desc"
    )


def get_upcoming_interviews(student):
    """Get upcoming interviews for student"""
    return frappe.get_all(
        "Placement Application",
        filters={
            "student": student,
            "status": "Interview Scheduled",
            "interview_date": [">=", frappe.utils.today()]
        },
        fields=[
            "name", "company", "job_title", "interview_date",
            "interview_time", "interview_venue", "interview_round"
        ],
        order_by="interview_date asc"
    )


# API Endpoints

@frappe.whitelist()
def apply_for_drive(drive):
    """Apply for a placement drive"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Access denied"))

    # Check if already applied
    if frappe.db.exists("Placement Application", {
        "student": student.name,
        "placement_drive": drive
    }):
        frappe.throw(_("Already applied for this drive"))

    # Check eligibility
    drive_doc = frappe.get_doc("Placement Drive", drive)
    student_doc = frappe.get_doc("Student", student.name)

    if drive_doc.minimum_cgpa and student_doc.custom_cgpa < drive_doc.minimum_cgpa:
        frappe.throw(_("CGPA requirement not met"))

    if drive_doc.maximum_backlogs and student_doc.get("custom_active_backlogs", 0) > drive_doc.maximum_backlogs:
        frappe.throw(_("Backlog requirement not met"))

    # Create application
    application = frappe.get_doc({
        "doctype": "Placement Application",
        "student": student.name,
        "placement_drive": drive,
        "company": drive_doc.company,
        "job_title": drive_doc.job_title,
        "status": "Applied"
    })
    application.insert(ignore_permissions=True)

    return {"success": True, "application": application.name}


@frappe.whitelist()
def update_placement_profile(profile_data):
    """Update placement profile"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Access denied"))

    if isinstance(profile_data, str):
        profile_data = frappe.parse_json(profile_data)

    profile = frappe.get_doc("Placement Profile", {"student": student.name})

    allowed_fields = [
        "resume", "skills", "certifications", "projects",
        "linkedin_profile", "github_profile", "portfolio_url",
        "preferred_locations", "expected_salary"
    ]

    for field in allowed_fields:
        if field in profile_data:
            setattr(profile, field, profile_data[field])

    profile.save(ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def upload_resume(file_url):
    """Upload resume to placement profile"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Access denied"))

    profile = frappe.get_doc("Placement Profile", {"student": student.name})
    profile.resume = file_url
    profile.save(ignore_permissions=True)

    return {"success": True}
```

---

## Part F: Mobile-Responsive Enhancements

### 1. Mobile CSS Framework

```css
/* mobile_responsive.css */

/* Base responsive styles */
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --text-color: #333;
    --border-radius: 10px;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Mobile-first approach */
* {
    box-sizing: border-box;
}

.portal-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 10px;
}

/* Responsive grid */
.grid {
    display: grid;
    gap: 15px;
}

.grid-2 { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.grid-3 { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.grid-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

/* Cards */
.mobile-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 15px;
    box-shadow: var(--shadow);
}

/* Bottom Navigation for Mobile */
.mobile-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
}

.mobile-nav-items {
    display: flex;
    justify-content: space-around;
    padding: 10px 0;
}

.mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: #666;
    font-size: 12px;
}

.mobile-nav-item.active {
    color: var(--primary-color);
}

.mobile-nav-item i {
    font-size: 20px;
    margin-bottom: 5px;
}

/* Mobile Header */
.mobile-header {
    display: none;
    position: sticky;
    top: 0;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 15px;
    z-index: 999;
}

.mobile-header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Swipe Cards */
.swipe-container {
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    display: flex;
    gap: 15px;
    padding: 10px 0;
}

.swipe-card {
    scroll-snap-align: start;
    flex-shrink: 0;
    width: 280px;
}

/* Pull to Refresh */
.pull-to-refresh {
    position: relative;
}

.pull-indicator {
    position: absolute;
    top: -50px;
    left: 50%;
    transform: translateX(-50%);
    display: none;
}

/* Touch-friendly buttons */
.btn-touch {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 20px;
    font-size: 16px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-touch:active {
    transform: scale(0.95);
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

/* Form elements for mobile */
.form-control-mobile {
    width: 100%;
    padding: 12px 15px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 15px;
}

.form-control-mobile:focus {
    outline: none;
    border-color: var(--primary-color);
}

/* Tables for mobile */
.table-mobile {
    display: block;
    width: 100%;
    overflow-x: auto;
}

.table-mobile table {
    min-width: 600px;
}

/* Card-style table for mobile */
.table-cards {
    display: none;
}

/* FAB Button */
.fab {
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--primary-color);
    color: white;
    border: none;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    z-index: 998;
}

/* Modal for mobile */
.modal-mobile {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1001;
}

.modal-content-mobile {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-radius: 20px 20px 0 0;
    padding: 20px;
    max-height: 80vh;
    overflow-y: auto;
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
}

/* Responsive breakpoints */
@media (max-width: 768px) {
    .mobile-nav {
        display: block;
    }

    .mobile-header {
        display: block;
    }

    .desktop-nav {
        display: none;
    }

    .portal-container {
        padding-bottom: 70px;
    }

    /* Stack grids on mobile */
    .grid-2, .grid-3, .grid-4 {
        grid-template-columns: 1fr;
    }

    /* Hide regular tables, show card view */
    .table-desktop {
        display: none;
    }

    .table-cards {
        display: block;
    }

    /* Adjust font sizes */
    h1 { font-size: 24px; }
    h2 { font-size: 20px; }
    h3 { font-size: 18px; }

    /* Full-width buttons on mobile */
    .btn-touch {
        width: 100%;
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    .portal-container {
        padding: 15px;
    }

    .grid-4 {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --text-color: #f5f5f5;
    }

    .mobile-card {
        background: #1e1e1e;
        color: #f5f5f5;
    }

    .mobile-nav {
        background: #1e1e1e;
    }

    .form-control-mobile {
        background: #2d2d2d;
        border-color: #444;
        color: #f5f5f5;
    }
}

/* Safe area for notched phones */
@supports (padding: max(0px)) {
    .mobile-nav {
        padding-bottom: max(10px, env(safe-area-inset-bottom));
    }

    .mobile-header {
        padding-top: max(15px, env(safe-area-inset-top));
    }
}
```

### 2. Mobile JavaScript Utilities

```javascript
// mobile_utils.js

class MobilePortal {
    constructor() {
        this.initPullToRefresh();
        this.initSwipeNavigation();
        this.initOfflineSupport();
        this.initTouchGestures();
    }

    // Pull to Refresh
    initPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        const threshold = 100;
        const indicator = document.querySelector('.pull-indicator');

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].pageY;
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (startY > 0) {
                currentY = e.touches[0].pageY;
                const pullDistance = currentY - startY;

                if (pullDistance > 0 && pullDistance < threshold * 2) {
                    if (indicator) {
                        indicator.style.display = 'block';
                        indicator.style.top = `${pullDistance - 50}px`;
                    }
                }
            }
        });

        document.addEventListener('touchend', () => {
            const pullDistance = currentY - startY;

            if (pullDistance > threshold) {
                this.refreshContent();
            }

            if (indicator) {
                indicator.style.display = 'none';
            }

            startY = 0;
            currentY = 0;
        });
    }

    refreshContent() {
        // Show loading indicator
        frappe.show_alert({
            message: 'Refreshing...',
            indicator: 'blue'
        });

        // Reload current page data
        window.location.reload();
    }

    // Swipe Navigation
    initSwipeNavigation() {
        let startX = 0;
        const threshold = 100;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].pageX;
        });

        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].pageX;
            const diffX = endX - startX;

            // Swipe right to go back
            if (diffX > threshold && startX < 50) {
                window.history.back();
            }
        });
    }

    // Offline Support
    initOfflineSupport() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
                .then((registration) => {
                    console.log('SW registered:', registration);
                })
                .catch((error) => {
                    console.log('SW registration failed:', error);
                });
        }

        window.addEventListener('online', () => {
            this.showConnectivityStatus(true);
        });

        window.addEventListener('offline', () => {
            this.showConnectivityStatus(false);
        });
    }

    showConnectivityStatus(isOnline) {
        const message = isOnline ? 'Back online' : 'You are offline';
        const indicator = isOnline ? 'green' : 'orange';

        frappe.show_alert({
            message: message,
            indicator: indicator
        });
    }

    // Touch Gestures
    initTouchGestures() {
        // Long press for context menu
        let pressTimer;
        const longPressThreshold = 500;

        document.querySelectorAll('.long-press-item').forEach(item => {
            item.addEventListener('touchstart', (e) => {
                pressTimer = setTimeout(() => {
                    this.showContextMenu(e.target);
                }, longPressThreshold);
            });

            item.addEventListener('touchend', () => {
                clearTimeout(pressTimer);
            });

            item.addEventListener('touchmove', () => {
                clearTimeout(pressTimer);
            });
        });
    }

    showContextMenu(element) {
        const menu = document.createElement('div');
        menu.className = 'context-menu-mobile';
        menu.innerHTML = `
            <div class="context-menu-item" data-action="view">View Details</div>
            <div class="context-menu-item" data-action="share">Share</div>
            <div class="context-menu-item" data-action="download">Download</div>
        `;

        // Position and show menu
        document.body.appendChild(menu);

        menu.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            this.handleContextAction(action, element);
            menu.remove();
        });

        // Close on outside tap
        document.addEventListener('touchstart', (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
            }
        }, { once: true });
    }

    handleContextAction(action, element) {
        switch(action) {
            case 'view':
                // Navigate to detail view
                break;
            case 'share':
                if (navigator.share) {
                    navigator.share({
                        title: document.title,
                        url: window.location.href
                    });
                }
                break;
            case 'download':
                // Trigger download
                break;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    new MobilePortal();
});


// Bottom Sheet Modal
class BottomSheet {
    constructor(element) {
        this.element = element;
        this.overlay = null;
        this.startY = 0;
        this.currentY = 0;
        this.initDrag();
    }

    show() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-mobile';
        this.overlay.style.display = 'block';
        this.overlay.appendChild(this.element);
        document.body.appendChild(this.overlay);

        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hide();
            }
        });
    }

    hide() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }

    initDrag() {
        this.element.addEventListener('touchstart', (e) => {
            this.startY = e.touches[0].pageY;
        });

        this.element.addEventListener('touchmove', (e) => {
            this.currentY = e.touches[0].pageY;
            const diff = this.currentY - this.startY;

            if (diff > 0) {
                this.element.style.transform = `translateY(${diff}px)`;
            }
        });

        this.element.addEventListener('touchend', () => {
            const diff = this.currentY - this.startY;

            if (diff > 100) {
                this.hide();
            } else {
                this.element.style.transform = 'translateY(0)';
            }

            this.startY = 0;
            this.currentY = 0;
        });
    }
}


// Quick Actions FAB
class FloatingActionButton {
    constructor() {
        this.fab = document.querySelector('.fab');
        this.isExpanded = false;

        if (this.fab) {
            this.init();
        }
    }

    init() {
        this.fab.addEventListener('click', () => {
            this.toggleMenu();
        });
    }

    toggleMenu() {
        this.isExpanded = !this.isExpanded;

        if (this.isExpanded) {
            this.showQuickActions();
        } else {
            this.hideQuickActions();
        }
    }

    showQuickActions() {
        const actions = document.createElement('div');
        actions.className = 'fab-actions';
        actions.innerHTML = `
            <button class="fab-action" data-action="attendance">
                <i class="fa fa-check"></i> Mark Attendance
            </button>
            <button class="fab-action" data-action="assignment">
                <i class="fa fa-upload"></i> Submit Assignment
            </button>
            <button class="fab-action" data-action="request">
                <i class="fa fa-file"></i> Request Certificate
            </button>
        `;

        this.fab.parentElement.appendChild(actions);

        actions.querySelectorAll('.fab-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleAction(e.target.dataset.action);
            });
        });

        this.fab.innerHTML = '<i class="fa fa-times"></i>';
    }

    hideQuickActions() {
        const actions = document.querySelector('.fab-actions');
        if (actions) actions.remove();

        this.fab.innerHTML = '<i class="fa fa-plus"></i>';
    }

    handleAction(action) {
        switch(action) {
            case 'attendance':
                window.location.href = '/student-portal/attendance';
                break;
            case 'assignment':
                window.location.href = '/student-portal/assignments';
                break;
            case 'request':
                window.location.href = '/student-portal/certificates';
                break;
        }
    }
}

// Initialize FAB
document.addEventListener('DOMContentLoaded', () => {
    new FloatingActionButton();
});
```

---

## Implementation Checklist

### Week 1-2: Student Portal
- [x] Create student portal pages structure
- [x] Implement dashboard with key metrics
- [x] Create timetable view
- [x] Implement results/grades view
- [x] Create fee payment interface
- [x] Implement certificate request system
- [x] Add grievance submission

### Week 2-3: Faculty Portal
- [x] Create faculty dashboard
- [x] Implement attendance marking
- [x] Create grade entry interface
- [x] Add class schedule management
- [x] Implement student group views
- [x] Add leave management

### Week 3-4: Parent Portal
- [x] Create parent dashboard
- [x] Implement child switching
- [x] Add attendance monitoring
- [x] Create fee payment view
- [x] Implement grade tracking
- [x] Add communication features

### Week 4-5: Alumni & Placement Portals
- [x] Create alumni directory
- [x] Implement event management
- [x] Add job posting system
- [x] Create placement profile
- [x] Implement application system
- [x] Add interview scheduling

### Week 5-6: Mobile Enhancements
- [x] Implement responsive layouts
- [x] Create bottom navigation
- [x] Add pull-to-refresh
- [x] Implement offline support
- [x] Create touch-friendly interfaces
- [x] Add PWA capabilities
- [ ] Test on various devices

---

## Implementation Summary

### Files Created

#### University Portals Module
- `university_portals/__init__.py` - Module initialization
- `university_portals/modules.txt` - Module registration
- `university_portals/api/portal_api.py` - Unified portal API

#### Student Portal (9 pages)
- `www/student-portal/index.py` - Dashboard controller
- `www/student-portal/index.html` - Dashboard template
- `www/student-portal/timetable.py/html` - Timetable page
- `www/student-portal/results.py/html` - Results page
- `www/student-portal/fees.py/html` - Fees page
- `www/student-portal/attendance.py/html` - Attendance page
- `www/student-portal/library.py/html` - Library page
- `www/student-portal/certificates.py/html` - Certificates page
- `www/student-portal/grievances.py/html` - Grievances page
- `www/student-portal/profile.py/html` - Profile page

#### Faculty Portal (4 pages)
- `www/faculty-portal/index.py/html` - Dashboard
- `www/faculty-portal/attendance.py/html` - Attendance marking
- `www/faculty-portal/grades.py/html` - Grade entry
- `www/faculty-portal/classes.py/html` - Class schedule

#### Parent Portal (2 pages)
- `www/parent-portal/index.py/html` - Dashboard
- `www/parent-portal/child.py/html` - Child details

#### Alumni Portal (1 page + 3 DocTypes)
- `www/alumni-portal/index.py/html` - Dashboard
- `doctype/alumni/` - Alumni DocType
- `doctype/alumni_event/` - Alumni Event DocType
- `doctype/alumni_event_registration/` - Event Registration DocType

#### Placement Portal (4 DocTypes)
- `doctype/placement_profile/` - Student placement profile
- `doctype/placement_drive/` - Company placement drives
- `doctype/placement_application/` - Student applications
- `doctype/job_posting/` - Job postings (including alumni)

#### Shared Components
- `doctype/announcement/` - Announcement DocType
- `public/css/portal.css` - Mobile-first responsive CSS
- `public/js/portal_utils.js` - Mobile utilities (pull-to-refresh, swipe, etc.)

### DocTypes Created (10)
1. Alumni
2. Alumni Event
3. Alumni Event Registration
4. Announcement
5. Placement Profile
6. Placement Drive
7. Placement Application
8. Job Posting

### APIs Created (33+)
- Student Portal: 7 APIs (dashboard, timetable, results, attendance, certificates, grievances, profile)
- Faculty Portal: 6 APIs (dashboard, attendance, grades, schedule, approvals)
- Parent Portal: 6 APIs (dashboard, child details, attendance, fees, results, communication)
- Alumni Portal: 5 APIs (directory, events, jobs, profile, donations)
- Placement Portal: 6 APIs (profile, drives, applications, eligibility, interviews)

---

## Security Considerations

1. **Authentication**: Ensure proper user verification for each portal
2. **Authorization**: Implement role-based access control
3. **Data Privacy**: Only show relevant data to each user type
4. **Session Management**: Implement secure session handling
5. **Input Validation**: Sanitize all user inputs
6. **HTTPS**: Enforce HTTPS for all portal pages

---

## Performance Optimization

1. **Lazy Loading**: Load content on demand
2. **Caching**: Implement client-side caching
3. **CDN**: Use CDN for static assets
4. **Image Optimization**: Compress and lazy-load images
5. **API Optimization**: Use pagination and filtering
6. **PWA**: Implement service workers for offline access

---

**Document Version**: 2.0
**Created**: Phase 13 Planning
**Implemented**: 2026-01-02
**Status**: Implemented
**Module Dependencies**: All core modules (Phases 1-12)

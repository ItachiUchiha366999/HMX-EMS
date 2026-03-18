/**
 * Shared test fixtures for faculty portal component tests.
 * Used by all faculty test files for consistent mock data.
 */
import { vi } from 'vitest'

export const mockFacultyDashboard = {
  today_classes: [
    {
      name: 'CS-SCH-001',
      course: 'CS201',
      course_name: 'Data Structures',
      room: 'Room 301',
      start_time: '09:00:00',
      end_time: '10:00:00',
      section: 'Section A',
      schedule_date: '2026-03-18',
      is_marked: false,
      student_count: 60,
    },
    {
      name: 'CS-SCH-002',
      course: 'CS301',
      course_name: 'Algorithms',
      room: 'Room 205',
      start_time: '11:00:00',
      end_time: '12:00:00',
      section: 'Section B',
      schedule_date: '2026-03-18',
      is_marked: true,
      student_count: 45,
    },
    {
      name: 'CS-SCH-003',
      course: 'CS401',
      course_name: 'Machine Learning',
      room: 'Lab 102',
      start_time: '14:00:00',
      end_time: '16:00:00',
      section: 'Section A',
      schedule_date: '2026-03-18',
      is_marked: false,
      student_count: 35,
    },
  ],
  pending_tasks: {
    unmarked_attendance: 3,
    pending_grades: 2,
    pending_leave_requests: 4,
    classes_today: 5,
  },
  announcements: [
    {
      name: 'NB-001',
      title: 'Mid-Semester Exam Schedule Published',
      category: 'Academic',
      posting_date: '2026-03-17',
      content: 'The mid-semester examination schedule for Spring 2026 has been published. Please check the exam portal for details.',
    },
    {
      name: 'NB-002',
      title: 'Campus Maintenance Notice',
      category: 'Administrative',
      posting_date: '2026-03-16',
      content: 'Building B will undergo maintenance on March 20. Classes will be relocated to Building C.',
    },
    {
      name: 'NB-003',
      title: 'Emergency Drill Scheduled',
      category: 'Emergency',
      posting_date: '2026-03-15',
      content: 'An emergency evacuation drill is scheduled for March 19 at 2 PM. All faculty and students must participate.',
    },
  ],
}

export const mockTodayClasses = [
  {
    name: 'CS-SCH-001',
    course: 'CS201',
    course_name: 'Data Structures',
    room: 'Room 301',
    start_time: '09:00:00',
    end_time: '10:00:00',
    section: 'Section A',
    schedule_date: '2026-03-18',
    is_marked: false,
    student_count: 60,
  },
  {
    name: 'CS-SCH-002',
    course: 'CS301',
    course_name: 'Algorithms',
    room: 'Room 205',
    start_time: '11:00:00',
    end_time: '12:00:00',
    section: 'Section B',
    schedule_date: '2026-03-18',
    is_marked: true,
    student_count: 45,
  },
  {
    name: 'CS-SCH-003',
    course: 'CS401',
    course_name: 'Machine Learning',
    room: 'Lab 102',
    start_time: '14:00:00',
    end_time: '16:00:00',
    section: 'Section A',
    schedule_date: '2026-03-18',
    is_marked: false,
    student_count: 35,
  },
]

export const mockStudentsForAttendance = [
  { student: 'EDU-STU-001', student_name: 'Arun Kumar', roll_no: '2021CS001', enrollment_no: 'EN2021001', image: null },
  { student: 'EDU-STU-002', student_name: 'Bhavya Sharma', roll_no: '2021CS002', enrollment_no: 'EN2021002', image: null },
  { student: 'EDU-STU-003', student_name: 'Chetan Reddy', roll_no: '2021CS003', enrollment_no: 'EN2021003', image: null },
  { student: 'EDU-STU-004', student_name: 'Deepa Nair', roll_no: '2021CS004', enrollment_no: 'EN2021004', image: null },
  { student: 'EDU-STU-005', student_name: 'Esha Patel', roll_no: '2021CS005', enrollment_no: 'EN2021005', image: null },
  { student: 'EDU-STU-006', student_name: 'Farhan Ali', roll_no: '2021CS006', enrollment_no: 'EN2021006', image: null },
  { student: 'EDU-STU-007', student_name: 'Gauri Deshmukh', roll_no: '2021CS007', enrollment_no: 'EN2021007', image: null },
  { student: 'EDU-STU-008', student_name: 'Harish Verma', roll_no: '2021CS008', enrollment_no: 'EN2021008', image: null },
  { student: 'EDU-STU-009', student_name: 'Isha Gupta', roll_no: '2021CS009', enrollment_no: 'EN2021009', image: null },
  { student: 'EDU-STU-010', student_name: 'Jayesh Mehta', roll_no: '2021CS010', enrollment_no: 'EN2021010', image: null },
]

export const mockWeeklyTimetable = {
  week_start: '2026-03-16',
  days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  slots: [
    { day: 'Mon', start_time: '09:00:00', end_time: '10:00:00', course: 'CS201', course_name: 'Data Structures', room: 'Room 301', section: 'Section A' },
    { day: 'Mon', start_time: '11:00:00', end_time: '12:00:00', course: 'CS301', course_name: 'Algorithms', room: 'Room 205', section: 'Section B' },
    { day: 'Wed', start_time: '09:00:00', end_time: '10:00:00', course: 'CS201', course_name: 'Data Structures', room: 'Room 301', section: 'Section A' },
    { day: 'Wed', start_time: '14:00:00', end_time: '16:00:00', course: 'CS401', course_name: 'Machine Learning', room: 'Lab 102', section: 'Section A' },
    { day: 'Fri', start_time: '09:00:00', end_time: '10:00:00', course: 'CS201', course_name: 'Data Structures', room: 'Room 301', section: 'Section A' },
    { day: 'Fri', start_time: '11:00:00', end_time: '12:00:00', course: 'CS301', course_name: 'Algorithms', room: 'Room 205', section: 'Section B' },
  ],
}

export const mockAnnouncements = {
  data: [
    {
      name: 'NB-001',
      title: 'Mid-Semester Exam Schedule Published',
      category: 'Academic',
      posting_date: '2026-03-17',
      content: 'The mid-semester examination schedule for Spring 2026 has been published. Please check the exam portal for details.',
    },
    {
      name: 'NB-002',
      title: 'Campus Maintenance Notice',
      category: 'Administrative',
      posting_date: '2026-03-16',
      content: 'Building B will undergo maintenance on March 20. Classes will be relocated to Building C.',
    },
    {
      name: 'NB-003',
      title: 'Emergency Drill Scheduled',
      category: 'Emergency',
      posting_date: '2026-03-15',
      content: 'An emergency evacuation drill is scheduled for March 19 at 2 PM. All faculty and students must participate.',
    },
    {
      name: 'NB-004',
      title: 'Library Extended Hours',
      category: 'Administrative',
      posting_date: '2026-03-14',
      content: 'The library will have extended hours from March 20 to April 5 for mid-semester preparation.',
    },
    {
      name: 'NB-005',
      title: 'Faculty Development Program',
      category: 'Academic',
      posting_date: '2026-03-13',
      content: 'A faculty development program on innovative teaching methods will be conducted on March 25.',
    },
  ],
  total_count: 5,
}

// ==================== Plan 03 Mock Fixtures (Leave, LMS, Research, OBE, Workload) ====================

export const mockLeaveBalance = [
  { leave_type: 'Casual Leave', total: 12, used: 4, balance: 8 },
  { leave_type: 'Medical Leave', total: 10, used: 3, balance: 7 },
  { leave_type: 'Earned Leave', total: 20, used: 15, balance: 5 },
]

export const mockStudentLeaveRequests = {
  data: [
    { name: 'SLA-001', student_name: 'Arun Kumar', roll_no: '2021CS001', from_date: '2026-03-20', to_date: '2026-03-22', reason: 'Family function', status: 'Open' },
    { name: 'SLA-002', student_name: 'Bhavya Sharma', roll_no: '2021CS002', from_date: '2026-03-21', to_date: '2026-03-21', reason: 'Medical appointment', status: 'Open' },
    { name: 'SLA-003', student_name: 'Chetan Reddy', roll_no: '2021CS003', from_date: '2026-03-22', to_date: '2026-03-24', reason: 'Personal emergency', status: 'Open' },
  ],
  total_count: 3,
}

export const mockLmsCourses = {
  available: true,
  courses: [
    { name: 'LMS-CS201', title: 'Data Structures', lesson_count: 12, assignment_count: 3, quiz_count: 2 },
    { name: 'LMS-CS301', title: 'Algorithms', lesson_count: 8, assignment_count: 2, quiz_count: 1 },
  ],
}

export const mockLmsCourseContent = {
  lessons: [
    { name: 'LSN-001', title: 'Introduction to Arrays', content: 'Arrays are...', idx: 1 },
    { name: 'LSN-002', title: 'Linked Lists', content: 'A linked list...', idx: 2 },
  ],
  assignments: [
    { name: 'ASN-001', title: 'Array Operations', due_date: '2026-03-25', status: 'Active' },
  ],
  quizzes: [
    { name: 'QZ-001', title: 'Data Structures Basics', question_count: 10, status: 'Active' },
  ],
}

export const mockPublications = {
  total: 12,
  by_type: { Journal: 6, Conference: 4, Book: 2 },
  publications: [
    { name: 'PUB-001', title: 'Deep Learning for NLP Applications', type: 'Journal', journal_conference: 'International Journal of AI', publication_date: '2025-06-15', doi_isbn: '10.1234/ai.2025.001', impact_factor: 3.2, scopus_indexed: 1 },
    { name: 'PUB-002', title: 'Efficient Graph Algorithms', type: 'Conference', journal_conference: 'IEEE ICSE 2025', publication_date: '2025-09-10', doi_isbn: '10.1109/icse.2025.002', impact_factor: 0, scopus_indexed: 1 },
    { name: 'PUB-003', title: 'Modern Data Structures', type: 'Book', journal_conference: 'Springer Publishing', publication_date: '2024-01-20', doi_isbn: '978-3-030-12345-6', impact_factor: 0, scopus_indexed: 0 },
  ],
}

export const mockCopoMatrix = {
  course: 'CS201',
  cos: ['CO1', 'CO2', 'CO3'],
  pos: ['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6'],
  matrix: [
    [2.8, 1.5, 0, 3.0, 0, 0],
    [0, 2.1, 2.4, 0, 1.8, 0],
    [3.0, 0, 0, 2.5, 2.0, 1.2],
  ],
}

export const mockCopoStudentDetail = {
  co: 'CO1',
  students: [
    { student: 'EDU-STU-001', student_name: 'Arun Kumar', attainment_value: 2.9 },
    { student: 'EDU-STU-002', student_name: 'Bhavya Sharma', attainment_value: 2.7 },
    { student: 'EDU-STU-003', student_name: 'Chetan Reddy', attainment_value: 1.5 },
  ],
}

export const mockWorkloadSummary = {
  personal: { hours_per_week: 18, total_courses: 4, total_credits: 12, total_students: 240 },
  department_avg: { hours_per_week: 16, total_courses: 3, total_credits: 10, total_students: 180 },
  heatmap: [
    { day: 'Mon', timeslot: '09:00', occupied: true, course_name: 'Data Structures' },
    { day: 'Mon', timeslot: '11:00', occupied: true, course_name: 'Algorithms' },
    { day: 'Wed', timeslot: '09:00', occupied: true, course_name: 'Data Structures' },
    { day: 'Wed', timeslot: '14:00', occupied: true, course_name: 'Machine Learning' },
    { day: 'Fri', timeslot: '09:00', occupied: true, course_name: 'Data Structures' },
    { day: 'Fri', timeslot: '11:00', occupied: true, course_name: 'Algorithms' },
  ],
}

export const mockLeaveHistory = {
  data: [
    { name: 'LA-001', leave_type: 'Casual Leave', from_date: '2026-02-10', to_date: '2026-02-11', description: 'Personal work', status: 'Approved', posting_date: '2026-02-08' },
    { name: 'LA-002', leave_type: 'Medical Leave', from_date: '2026-01-15', to_date: '2026-01-17', description: 'Fever', status: 'Approved', posting_date: '2026-01-14' },
  ],
  total_count: 2,
}

// ==================== Plan 02 Mock Fixtures (Grades, Students) ====================

export const mockStudentsForGrading = {
  students: [
    {
      student: 'EDU-STU-001',
      student_name: 'Arun Kumar',
      roll_no: '2021CS001',
      grades: [
        { assessment_name: 'IA-1', marks: 78, grade: 'B+', docstatus: 0 },
        { assessment_name: 'IA-2', marks: 82, grade: 'A', docstatus: 0 },
        { assessment_name: 'Mid-Sem', marks: 71, grade: 'B', docstatus: 0 },
      ],
    },
    {
      student: 'EDU-STU-002',
      student_name: 'Bhavya Sharma',
      roll_no: '2021CS002',
      grades: [
        { assessment_name: 'IA-1', marks: 85, grade: 'A', docstatus: 0 },
        { assessment_name: 'IA-2', marks: null, grade: null, docstatus: 0 },
        { assessment_name: 'Mid-Sem', marks: 90, grade: 'A+', docstatus: 0 },
      ],
    },
    {
      student: 'EDU-STU-003',
      student_name: 'Chetan Reddy',
      roll_no: '2021CS003',
      grades: [
        { assessment_name: 'IA-1', marks: 35, grade: 'F', docstatus: 0 },
        { assessment_name: 'IA-2', marks: 38, grade: 'F', docstatus: 0 },
        { assessment_name: 'Mid-Sem', marks: 32, grade: 'F', docstatus: 0 },
      ],
    },
  ],
  assessments: [
    { name: 'IA-1', assessment_type: 'Internal Assessment', max_marks: 100 },
    { name: 'IA-2', assessment_type: 'Internal Assessment', max_marks: 100 },
    { name: 'Mid-Sem', assessment_type: 'Mid Semester', max_marks: 100 },
  ],
}

export const mockGradeAnalytics = {
  distribution: { 'A+': 3, A: 5, 'B+': 8, B: 12, C: 10, D: 5, F: 5 },
  average: 72.3,
  pass_count: 48,
  fail_count: 12,
  at_risk_count: 5,
  at_risk_threshold: 40,
}

export const mockStudentList = {
  data: [
    { student: 'EDU-STU-001', student_name: 'Arun Kumar', roll_no: '2021CS001', enrollment_no: 'EN2021001', image: null, attendance_percentage: 92, current_grade: 'B+' },
    { student: 'EDU-STU-002', student_name: 'Bhavya Sharma', roll_no: '2021CS002', enrollment_no: 'EN2021002', image: null, attendance_percentage: 88, current_grade: 'A' },
    { student: 'EDU-STU-003', student_name: 'Chetan Reddy', roll_no: '2021CS003', enrollment_no: 'EN2021003', image: null, attendance_percentage: 55, current_grade: 'F' },
    { student: 'EDU-STU-004', student_name: 'Deepa Nair', roll_no: '2021CS004', enrollment_no: 'EN2021004', image: null, attendance_percentage: 72, current_grade: 'B' },
    { student: 'EDU-STU-005', student_name: 'Esha Patel', roll_no: '2021CS005', enrollment_no: 'EN2021005', image: null, attendance_percentage: 95, current_grade: 'A+' },
  ],
  total_count: 60,
}

export const mockStudentDetail = {
  attendance_history: [
    { date: '2026-03-01', status: 'Present' },
    { date: '2026-03-02', status: 'Present' },
    { date: '2026-03-03', status: 'Absent' },
    { date: '2026-03-04', status: 'Present' },
    { date: '2026-03-05', status: 'Present' },
  ],
  assessment_marks: [
    { assessment_name: 'IA-1', marks: 78, max_marks: 100, grade: 'B+' },
    { assessment_name: 'IA-2', marks: 82, max_marks: 100, grade: 'A' },
    { assessment_name: 'Mid-Sem', marks: 71, max_marks: 100, grade: 'B' },
  ],
  grade_trend: [
    { assessment_name: 'IA-1', marks_percentage: 78 },
    { assessment_name: 'IA-2', marks_percentage: 82 },
    { assessment_name: 'Mid-Sem', marks_percentage: 71 },
  ],
}

export const mockPerformanceAnalytics = {
  grade_distribution: {
    labels: ['A+', 'A', 'B+', 'B', 'C', 'D', 'F'],
    data: [3, 5, 8, 12, 10, 5, 5],
  },
  attendance_correlation: {
    labels: ['0-50%', '50-60%', '60-75%', '75-90%', '90-100%'],
    data: [2.1, 4.5, 6.2, 7.1, 8.5],
  },
  assessment_trend: {
    labels: ['IA-1', 'IA-2', 'Mid-Sem'],
    series: [{ name: 'Class Average', data: [68.5, 72.1, 70.3] }],
  },
  batch_comparison: {
    current: { average: 72.3, pass_rate: 80 },
    previous: { average: 68.1, pass_rate: 75 },
  },
}

/**
 * Creates a mock useFacultyApi with vi.fn() for all methods.
 * Usage: vi.mock('../../composables/useFacultyApi.js', () => ({ useFacultyApi: mockUseFacultyApi }))
 */
export function mockUseFacultyApi() {
  return {
    getDashboard: vi.fn().mockResolvedValue(mockFacultyDashboard),
    getTodayClasses: vi.fn().mockResolvedValue(mockTodayClasses),
    getWeeklyTimetable: vi.fn().mockResolvedValue(mockWeeklyTimetable),
    getStudentsForAttendance: vi.fn().mockResolvedValue(mockStudentsForAttendance),
    submitAttendance: vi.fn().mockResolvedValue({ present: 54, absent: 6, percentage: 90.0, total: 60 }),
    getAnnouncements: vi.fn().mockResolvedValue(mockAnnouncements),
    getStudentsForGrading: vi.fn().mockResolvedValue(mockStudentsForGrading),
    saveDraftGrade: vi.fn().mockResolvedValue({ grade: 'B+', marks: 78, status: 'saved' }),
    submitGrades: vi.fn().mockResolvedValue({ submitted_count: 3, message: 'Grades submitted' }),
    getGradeAnalytics: vi.fn().mockResolvedValue(mockGradeAnalytics),
    getStudentList: vi.fn().mockResolvedValue(mockStudentList),
    getStudentDetail: vi.fn().mockResolvedValue(mockStudentDetail),
    getPerformanceAnalytics: vi.fn().mockResolvedValue(mockPerformanceAnalytics),
    getLeaveBalance: vi.fn().mockResolvedValue(mockLeaveBalance),
    applyLeave: vi.fn().mockResolvedValue({ name: 'LA-003', status: 'Open', message: 'Leave request submitted' }),
    getLeaveHistory: vi.fn().mockResolvedValue(mockLeaveHistory),
    getStudentLeaveRequests: vi.fn().mockResolvedValue(mockStudentLeaveRequests),
    approveStudentLeave: vi.fn().mockResolvedValue({ status: 'Approved', message: 'Leave request approved' }),
    rejectStudentLeave: vi.fn().mockResolvedValue({ status: 'Rejected', message: 'Leave request rejected' }),
    getLmsCourses: vi.fn().mockResolvedValue(mockLmsCourses),
    getLmsCourseContent: vi.fn().mockResolvedValue(mockLmsCourseContent),
    saveLmsContent: vi.fn().mockResolvedValue({ name: 'LSN-003', message: 'Content saved' }),
    deleteLmsContent: vi.fn().mockResolvedValue({ message: 'Content deleted' }),
    getPublications: vi.fn().mockResolvedValue(mockPublications),
    getCopoMatrix: vi.fn().mockResolvedValue(mockCopoMatrix),
    getCopoStudentDetail: vi.fn().mockResolvedValue(mockCopoStudentDetail),
    getWorkloadSummary: vi.fn().mockResolvedValue(mockWorkloadSummary),
    loading: { value: false },
    error: { value: null },
  }
}

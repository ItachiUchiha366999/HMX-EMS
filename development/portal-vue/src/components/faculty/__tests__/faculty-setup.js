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
    getStudentsForGrading: vi.fn().mockResolvedValue([]),
    saveDraftGrade: vi.fn().mockResolvedValue({ success: true }),
    submitGrades: vi.fn().mockResolvedValue({ success: true }),
    getGradeAnalytics: vi.fn().mockResolvedValue({}),
    getStudentList: vi.fn().mockResolvedValue([]),
    getStudentDetail: vi.fn().mockResolvedValue({}),
    getPerformanceAnalytics: vi.fn().mockResolvedValue({}),
    getLeaveBalance: vi.fn().mockResolvedValue([]),
    applyLeave: vi.fn().mockResolvedValue({ success: true }),
    getLeaveHistory: vi.fn().mockResolvedValue([]),
    getStudentLeaveRequests: vi.fn().mockResolvedValue([]),
    approveStudentLeave: vi.fn().mockResolvedValue({ success: true }),
    rejectStudentLeave: vi.fn().mockResolvedValue({ success: true }),
    getLmsCourses: vi.fn().mockResolvedValue([]),
    getLmsCourseContent: vi.fn().mockResolvedValue({}),
    saveLmsContent: vi.fn().mockResolvedValue({ success: true }),
    deleteLmsContent: vi.fn().mockResolvedValue({ success: true }),
    getPublications: vi.fn().mockResolvedValue([]),
    getCopoMatrix: vi.fn().mockResolvedValue({}),
    getCopoStudentDetail: vi.fn().mockResolvedValue({}),
    getWorkloadSummary: vi.fn().mockResolvedValue({}),
    loading: { value: false },
    error: { value: null },
  }
}

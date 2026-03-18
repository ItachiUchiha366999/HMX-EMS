import { useFrappe } from './useFrappe'

export function useFacultyApi() {
  const { call, loading, error } = useFrappe()
  const BASE = 'university_erp.university_portals.api.faculty_api'

  const getDashboard = () => call(`${BASE}.get_faculty_dashboard`, {}, { method: 'GET' })
  const getTodayClasses = () => call(`${BASE}.get_today_classes`, {}, { method: 'GET' })
  const getWeeklyTimetable = (weekStart) => call(`${BASE}.get_weekly_timetable`, weekStart ? { week_start: weekStart } : {}, { method: 'GET' })
  const getStudentsForAttendance = (courseSchedule) => call(`${BASE}.get_students_for_attendance`, { course_schedule: courseSchedule }, { method: 'GET' })
  const submitAttendance = (courseSchedule, attendanceData) => call(`${BASE}.submit_attendance`, { course_schedule: courseSchedule, attendance_data: JSON.stringify(attendanceData) })
  const getAnnouncements = (params = {}) => call(`${BASE}.get_announcements`, params, { method: 'GET' })

  // Grade endpoints (used by Plan 02)
  const getStudentsForGrading = (course, assessmentPlan) => call(`${BASE}.get_students_for_grading`, { course, assessment_plan: assessmentPlan }, { method: 'GET' })
  const saveDraftGrade = (data) => call(`${BASE}.save_draft_grade`, data)
  const submitGrades = (course, assessmentPlan) => call(`${BASE}.submit_grades`, { course, assessment_plan: assessmentPlan })
  const getGradeAnalytics = (course, assessmentPlan) => call(`${BASE}.get_grade_analytics`, { course, assessment_plan: assessmentPlan }, { method: 'GET' })
  const getStudentList = (params) => call(`${BASE}.get_student_list`, params, { method: 'GET' })
  const getStudentDetail = (student, course) => call(`${BASE}.get_student_detail`, { student, course }, { method: 'GET' })
  const getPerformanceAnalytics = (course) => call(`${BASE}.get_performance_analytics`, { course }, { method: 'GET' })

  // Leave endpoints (used by Plan 03)
  const getLeaveBalance = () => call(`${BASE}.get_leave_balance`, {}, { method: 'GET' })
  const applyLeave = (data) => call(`${BASE}.apply_leave`, data)
  const getLeaveHistory = (params = {}) => call(`${BASE}.get_leave_history`, params, { method: 'GET' })
  const getStudentLeaveRequests = (params = {}) => call(`${BASE}.get_student_leave_requests`, params, { method: 'GET' })
  const approveStudentLeave = (name) => call(`${BASE}.approve_student_leave`, { name })
  const rejectStudentLeave = (name, reason) => call(`${BASE}.reject_student_leave`, { name, reason })

  // LMS endpoints (used by Plan 03)
  const getLmsCourses = () => call(`${BASE}.get_lms_courses`, {}, { method: 'GET' })
  const getLmsCourseContent = (course) => call(`${BASE}.get_lms_course_content`, { course }, { method: 'GET' })
  const saveLmsContent = (data) => call(`${BASE}.save_lms_content`, data)
  const deleteLmsContent = (doctype, name) => call(`${BASE}.delete_lms_content`, { doctype, name })

  // Research + OBE endpoints (used by Plan 03)
  const getPublications = () => call(`${BASE}.get_publications`, {}, { method: 'GET' })
  const getCopoMatrix = (course) => call(`${BASE}.get_copo_matrix`, { course }, { method: 'GET' })
  const getCopoStudentDetail = (course, co) => call(`${BASE}.get_copo_student_detail`, { course, co }, { method: 'GET' })

  // Workload endpoint (used by Plan 03)
  const getWorkloadSummary = () => call(`${BASE}.get_workload_summary`, {}, { method: 'GET' })

  return {
    getDashboard, getTodayClasses, getWeeklyTimetable,
    getStudentsForAttendance, submitAttendance, getAnnouncements,
    getStudentsForGrading, saveDraftGrade, submitGrades, getGradeAnalytics,
    getStudentList, getStudentDetail, getPerformanceAnalytics,
    getLeaveBalance, applyLeave, getLeaveHistory,
    getStudentLeaveRequests, approveStudentLeave, rejectStudentLeave,
    getLmsCourses, getLmsCourseContent, saveLmsContent, deleteLmsContent,
    getPublications, getCopoMatrix, getCopoStudentDetail,
    getWorkloadSummary,
    loading, error
  }
}

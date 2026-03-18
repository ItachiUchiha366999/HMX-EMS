import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock useFrappe before importing useFacultyApi
const mockCall = vi.fn()
vi.mock('../useFrappe.js', () => ({
  useFrappe: () => ({
    call: mockCall,
    loading: { value: false },
    error: { value: null },
  }),
}))

import { useFacultyApi } from '../useFacultyApi.js'

describe('useFacultyApi', () => {
  let api

  beforeEach(() => {
    mockCall.mockReset()
    mockCall.mockResolvedValue({})
    api = useFacultyApi()
  })

  it('getDashboard calls useFrappe.call with correct method path', async () => {
    await api.getDashboard()
    expect(mockCall).toHaveBeenCalledWith(
      'university_erp.university_portals.api.faculty_api.get_faculty_dashboard',
      {},
      { method: 'GET' }
    )
  })

  it('submitAttendance sends course_schedule and JSON-stringified attendance_data', async () => {
    const attendanceData = [
      { student: 'STU-001', status: 'Present' },
      { student: 'STU-002', status: 'Absent' },
    ]
    await api.submitAttendance('CS-001', attendanceData)
    expect(mockCall).toHaveBeenCalledWith(
      'university_erp.university_portals.api.faculty_api.submit_attendance',
      {
        course_schedule: 'CS-001',
        attendance_data: JSON.stringify(attendanceData),
      }
    )
  })

  it('getTodayClasses uses GET method', async () => {
    await api.getTodayClasses()
    expect(mockCall).toHaveBeenCalledWith(
      'university_erp.university_portals.api.faculty_api.get_today_classes',
      {},
      { method: 'GET' }
    )
  })

  it('getWeeklyTimetable passes week_start param when provided', async () => {
    await api.getWeeklyTimetable('2026-03-16')
    expect(mockCall).toHaveBeenCalledWith(
      'university_erp.university_portals.api.faculty_api.get_weekly_timetable',
      { week_start: '2026-03-16' },
      { method: 'GET' }
    )
  })

  it('getStudentsForAttendance uses GET method with course_schedule param', async () => {
    await api.getStudentsForAttendance('CS-001')
    expect(mockCall).toHaveBeenCalledWith(
      'university_erp.university_portals.api.faculty_api.get_students_for_attendance',
      { course_schedule: 'CS-001' },
      { method: 'GET' }
    )
  })

  it('getAnnouncements passes filter params using GET', async () => {
    await api.getAnnouncements({ category: 'Academic', start: 0, page_length: 10 })
    expect(mockCall).toHaveBeenCalledWith(
      'university_erp.university_portals.api.faculty_api.get_announcements',
      { category: 'Academic', start: 0, page_length: 10 },
      { method: 'GET' }
    )
  })

  it('exports loading and error refs', () => {
    expect(api.loading).toBeDefined()
    expect(api.error).toBeDefined()
  })
})

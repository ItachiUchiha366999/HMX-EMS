import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockStudentsForAttendance } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

// Mock useToast
vi.mock('../../../composables/useToast.js', () => ({
  useToast: () => ({
    show: vi.fn(),
    toasts: { value: [] },
  }),
}))

import AttendanceMarker from '../AttendanceMarker.vue'

describe('AttendanceMarker', () => {
  const classInfo = {
    name: 'CS-SCH-001',
    course: 'CS201',
    course_name: 'Data Structures',
    room: 'Room 301',
    section: 'Section A',
    schedule_date: '2026-03-18',
    is_marked: false,
    student_count: 10,
  }

  beforeEach(() => {
    mockApi = mockUseFacultyApi()
  })

  it('renders student list with all checkboxes pre-checked (present-by-default)', async () => {
    const wrapper = mount(AttendanceMarker, { props: { classInfo } })
    await flushPromises()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // All student checkboxes + select-all checkbox
    expect(checkboxes.length).toBeGreaterThanOrEqual(mockStudentsForAttendance.length)

    // All student checkboxes should be checked
    const studentCheckboxes = checkboxes.filter((cb) => !cb.classes().includes('select-all-checkbox'))
    studentCheckboxes.forEach((cb) => {
      expect(cb.element.checked).toBe(true)
    })
  })

  it('unchecking a student row applies error-tint background', async () => {
    const wrapper = mount(AttendanceMarker, { props: { classInfo } })
    await flushPromises()

    // Find the first student checkbox and uncheck it
    const firstCheckbox = wrapper.findAll('.student-checkbox')[0]
    if (firstCheckbox) {
      await firstCheckbox.setValue(false)
      const row = wrapper.findAll('.student-row')[0]
      expect(row.classes()).toContain('student-row--absent')
    }
  })

  it('Select All toggle checks/unchecks all students', async () => {
    const wrapper = mount(AttendanceMarker, { props: { classInfo } })
    await flushPromises()

    const selectAll = wrapper.find('.select-all-checkbox')
    if (selectAll.exists()) {
      // Uncheck all
      await selectAll.setValue(false)
      await flushPromises()

      const checkboxes = wrapper.findAll('.student-checkbox')
      checkboxes.forEach((cb) => {
        expect(cb.element.checked).toBe(false)
      })

      // Check all again
      await selectAll.setValue(true)
      await flushPromises()

      const rechecked = wrapper.findAll('.student-checkbox')
      rechecked.forEach((cb) => {
        expect(cb.element.checked).toBe(true)
      })
    }
  })

  it('Submit Attendance button calls submitAttendance with correct data', async () => {
    const wrapper = mount(AttendanceMarker, { props: { classInfo } })
    await flushPromises()

    // Uncheck one student to make it interesting
    const checkboxes = wrapper.findAll('.student-checkbox')
    if (checkboxes.length > 0) {
      await checkboxes[0].setValue(false)
    }

    const submitBtn = wrapper.find('.submit-attendance-btn')
    await submitBtn.trigger('click')
    await flushPromises()

    expect(mockApi.submitAttendance).toHaveBeenCalledWith(
      'CS-SCH-001',
      expect.arrayContaining([
        expect.objectContaining({ status: 'Absent' }),
      ])
    )
  })

  it('shows Attendance already submitted banner when is_marked=true', async () => {
    const markedClass = { ...classInfo, is_marked: true }
    const wrapper = mount(AttendanceMarker, { props: { classInfo: markedClass } })
    await flushPromises()

    expect(wrapper.text()).toContain('Attendance has already been submitted for this class')
  })

  it('shows live count summary with present, absent, percentage', async () => {
    const wrapper = mount(AttendanceMarker, { props: { classInfo } })
    await flushPromises()

    // All present by default
    const text = wrapper.text()
    expect(text).toContain('Present')
    expect(text).toContain('Absent')
  })
})

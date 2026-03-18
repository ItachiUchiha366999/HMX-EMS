import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { mockTodayClasses } from './faculty-setup.js'

import TimetableToday from '../TimetableToday.vue'

describe('TimetableToday', () => {
  it('renders class list with time, course name, room, section', () => {
    const wrapper = mount(TimetableToday, {
      props: { classes: mockTodayClasses, loading: false },
    })

    const text = wrapper.text()
    expect(text).toContain('Data Structures')
    expect(text).toContain('Room 301')
    expect(text).toContain('Section A')
    // Time formatting
    expect(text).toContain('09:00')
  })

  it('highlights current class with primary-tint background', () => {
    // Use a class with time range that includes current time
    const now = new Date()
    const hour = String(now.getHours()).padStart(2, '0')
    const nextHour = String(now.getHours() + 1).padStart(2, '0')

    const currentClasses = [
      {
        name: 'CS-CURR',
        course: 'CS201',
        course_name: 'Current Class',
        room: 'Room 301',
        start_time: `${hour}:00:00`,
        end_time: `${nextHour}:00:00`,
        section: 'Section A',
        schedule_date: new Date().toISOString().split('T')[0],
        is_marked: false,
        student_count: 60,
      },
    ]

    const wrapper = mount(TimetableToday, {
      props: { classes: currentClasses, loading: false },
    })

    const currentItem = wrapper.find('.timetable-item--current')
    expect(currentItem.exists()).toBe(true)
  })

  it('shows Mark Attendance button for unmarked classes', () => {
    const wrapper = mount(TimetableToday, {
      props: { classes: mockTodayClasses, loading: false },
    })

    const markButtons = wrapper.findAll('.btn-primary')
    expect(markButtons.length).toBeGreaterThan(0)
    expect(markButtons[0].text()).toContain('Mark Attendance')
  })

  it('shows Marked text for already-marked classes', () => {
    const wrapper = mount(TimetableToday, {
      props: { classes: mockTodayClasses, loading: false },
    })

    const text = wrapper.text()
    expect(text).toContain('Marked')
  })

  it('emits mark-attendance when button is clicked', async () => {
    const wrapper = mount(TimetableToday, {
      props: { classes: mockTodayClasses, loading: false },
    })

    const markButton = wrapper.find('.btn-primary')
    await markButton.trigger('click')

    expect(wrapper.emitted('mark-attendance')).toBeTruthy()
    expect(wrapper.emitted('mark-attendance')[0][0]).toHaveProperty('name')
  })

  it('shows empty state when no classes', () => {
    const wrapper = mount(TimetableToday, {
      props: { classes: [], loading: false },
    })

    expect(wrapper.text()).toContain('No classes scheduled')
  })
})

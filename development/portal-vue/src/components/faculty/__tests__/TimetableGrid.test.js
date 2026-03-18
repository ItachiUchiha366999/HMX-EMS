import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockWeeklyTimetable } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

import TimetableGrid from '../TimetableGrid.vue'

describe('TimetableGrid', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
  })

  it('renders weekly grid with days as columns and time slots as rows', async () => {
    const wrapper = mount(TimetableGrid)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Mon')
    expect(text).toContain('Tue')
    expect(text).toContain('Wed')
    expect(text).toContain('Thu')
    expect(text).toContain('Fri')
  })

  it('marks occupied slots with course name and room', async () => {
    const wrapper = mount(TimetableGrid)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Data Structures')
    expect(text).toContain('Room 301')
  })

  it('calls getWeeklyTimetable on mount', async () => {
    mount(TimetableGrid)
    await flushPromises()

    expect(mockApi.getWeeklyTimetable).toHaveBeenCalled()
  })

  it('shows empty state when no slots', async () => {
    mockApi.getWeeklyTimetable = vi.fn().mockResolvedValue({
      week_start: '2026-03-16',
      days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
      slots: [],
    })

    const wrapper = mount(TimetableGrid)
    await flushPromises()

    expect(wrapper.text()).toContain('No classes scheduled')
  })
})

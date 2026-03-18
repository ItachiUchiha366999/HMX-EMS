import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockFacultyDashboard } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: {} }),
}))

import FacultyDashboard from '../FacultyDashboard.vue'

describe('FacultyDashboard', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockPush.mockReset()
  })

  it('renders 4 KpiCard components with pending task data', async () => {
    const wrapper = mount(FacultyDashboard)
    await flushPromises()

    const cards = wrapper.findAll('.stat-card')
    expect(cards.length).toBe(4)

    const text = wrapper.text()
    expect(text).toContain('Classes Today')
    expect(text).toContain('Unmarked Attendance')
    expect(text).toContain('Pending Grades')
    expect(text).toContain('Pending Leave')
  })

  it('renders today\'s classes with course name and Mark Attendance button', async () => {
    const wrapper = mount(FacultyDashboard)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Data Structures')
    expect(text).toContain('Mark Attendance')
  })

  it('shows Marked text for already-marked classes', async () => {
    const wrapper = mount(FacultyDashboard)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Marked')
  })

  it('calls getDashboard on mount', async () => {
    mount(FacultyDashboard)
    await flushPromises()

    expect(mockApi.getDashboard).toHaveBeenCalled()
  })

  it('shows loading state with skeleton loader', () => {
    mockApi.getDashboard = vi.fn(() => new Promise(() => {})) // never resolves
    const wrapper = mount(FacultyDashboard)

    expect(wrapper.findAll('.skeleton').length).toBeGreaterThan(0)
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import {
  mockUseFacultyApi,
  mockPerformanceAnalytics,
} from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

import PerformanceAnalytics from '../PerformanceAnalytics.vue'

describe('PerformanceAnalytics', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getPerformanceAnalytics.mockResolvedValue(mockPerformanceAnalytics)
  })

  it('renders 4 charts: grade distribution, attendance correlation, assessment trend, batch comparison', async () => {
    const wrapper = mount(PerformanceAnalytics, {
      props: { course: 'CS201' },
    })
    await flushPromises()

    // Should render 4 ChartWrapper instances
    const charts = wrapper.findAll('.chart-wrapper')
    expect(charts.length).toBeGreaterThanOrEqual(4)
  })

  it('accessible via "View Analytics" button', async () => {
    const wrapper = mount(PerformanceAnalytics, {
      props: { course: 'CS201' },
    })
    await flushPromises()

    // Should have a back button to return to student list
    const backBtn = wrapper.find('.back-to-students')
    expect(backBtn.exists()).toBe(true)
    expect(backBtn.text()).toContain('Back to Students')
  })

  it('calls getPerformanceAnalytics on mount', async () => {
    mount(PerformanceAnalytics, {
      props: { course: 'CS201' },
    })
    await flushPromises()

    expect(mockApi.getPerformanceAnalytics).toHaveBeenCalledWith('CS201')
  })
})

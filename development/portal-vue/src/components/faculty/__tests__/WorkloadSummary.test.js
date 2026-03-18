import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockWorkloadSummary } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

// Mock ChartWrapper
vi.mock('../../shared/ChartWrapper.vue', () => ({
  default: {
    name: 'ChartWrapper',
    template: '<div class="chart-wrapper-mock"><slot /></div>',
    props: ['type', 'series', 'categories', 'height', 'title', 'loading'],
  },
}))

// Mock KpiCard
vi.mock('../../shared/KpiCard.vue', () => ({
  default: {
    name: 'KpiCard',
    template: '<div class="stat-card"><slot /></div>',
    props: ['label', 'value', 'trend', 'status', 'icon', 'loading'],
  },
}))

import WorkloadSummary from '../WorkloadSummary.vue'

describe('WorkloadSummary', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getWorkloadSummary.mockResolvedValue(mockWorkloadSummary)
  })

  it('renders 4 KpiCard components with personal value and department average', async () => {
    const wrapper = mount(WorkloadSummary)
    await flushPromises()

    const cards = wrapper.findAll('.stat-card')
    expect(cards.length).toBe(4)

    const text = wrapper.text()
    expect(text).toContain('Dept avg')
  })

  it('renders ChartWrapper heatmap with day x timeslot grid', async () => {
    const wrapper = mount(WorkloadSummary)
    await flushPromises()

    expect(wrapper.find('.chart-wrapper-mock').exists()).toBe(true)
  })

  it('shows "No workload data" empty state when no data', async () => {
    mockApi.getWorkloadSummary.mockResolvedValue({
      personal: { hours_per_week: 0, total_courses: 0, total_credits: 0, total_students: 0 },
      department_avg: { hours_per_week: 0, total_courses: 0, total_credits: 0, total_students: 0 },
      heatmap: [],
    })
    const wrapper = mount(WorkloadSummary)
    await flushPromises()

    expect(wrapper.text()).toContain('No workload data')
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockCopoMatrix, mockCopoStudentDetail } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

// Mock ChartWrapper as it depends on ApexCharts
vi.mock('../../shared/ChartWrapper.vue', () => ({
  default: {
    name: 'ChartWrapper',
    template: '<div class="chart-wrapper-mock"><slot /></div>',
    props: ['type', 'series', 'categories', 'height', 'title', 'loading'],
  },
}))

import ObeAttainment from '../ObeAttainment.vue'

describe('ObeAttainment', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getCopoMatrix.mockResolvedValue(mockCopoMatrix)
    mockApi.getCopoStudentDetail.mockResolvedValue(mockCopoStudentDetail)
  })

  it('renders ChartWrapper heatmap with CO rows and PO columns', async () => {
    const wrapper = mount(ObeAttainment, {
      props: { courses: [{ name: 'CS201', course_name: 'Data Structures' }] },
    })
    await flushPromises()

    expect(mockApi.getCopoMatrix).toHaveBeenCalledWith('CS201')
    expect(wrapper.find('.chart-wrapper-mock').exists()).toBe(true)
  })

  it('clicking a CO row calls getCopoStudentDetail and shows student-level DataTable', async () => {
    const wrapper = mount(ObeAttainment, {
      props: { courses: [{ name: 'CS201', course_name: 'Data Structures' }] },
    })
    await flushPromises()

    // Click on a CO row
    const coRow = wrapper.findAll('.co-row')[0]
    await coRow.trigger('click')
    await flushPromises()

    expect(mockApi.getCopoStudentDetail).toHaveBeenCalledWith('CS201', 'CO1')
    expect(wrapper.text()).toContain('Arun Kumar')
    expect(wrapper.text()).toContain('Back to Matrix')
  })

  it('shows "No attainment data" empty state when no data', async () => {
    mockApi.getCopoMatrix.mockResolvedValue({ course: 'CS201', cos: [], pos: [], matrix: [] })
    const wrapper = mount(ObeAttainment, {
      props: { courses: [{ name: 'CS201', course_name: 'Data Structures' }] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('No attainment data')
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import {
  mockUseFacultyApi,
  mockStudentList,
  mockStudentDetail,
} from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ query: {} }),
}))

import StudentListView from '../StudentListView.vue'
import StudentDetailPanel from '../StudentDetailPanel.vue'

describe('StudentListView', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getStudentList.mockResolvedValue(mockStudentList)
    mockApi.getStudentDetail.mockResolvedValue(mockStudentDetail)
  })

  it('renders DataTable with avatar, name, roll, attendance %, grade columns', async () => {
    const wrapper = mount(StudentListView, {
      props: { course: 'CS201' },
    })
    await flushPromises()

    const text = wrapper.text()
    // Should show student data
    expect(text).toContain('Arun Kumar')
    expect(text).toContain('2021CS001')
    // Should have attendance percentages
    expect(text).toContain('92')
    // Should have grade
    expect(text).toContain('B+')
  })

  it('expand icon click shows StudentDetailPanel inline', async () => {
    const wrapper = mount(StudentListView, {
      props: { course: 'CS201' },
    })
    await flushPromises()

    // Find expand buttons
    const expandBtns = wrapper.findAll('.student-expand-btn')
    expect(expandBtns.length).toBeGreaterThan(0)

    // Click first expand button
    await expandBtns[0].trigger('click')
    await flushPromises()

    // Should render StudentDetailPanel
    expect(wrapper.findComponent(StudentDetailPanel).exists()).toBe(true)
  })

  it('attendance percentage uses color coding (>= 75% success, 60-74% warning, < 60% error)', async () => {
    const wrapper = mount(StudentListView, {
      props: { course: 'CS201' },
    })
    await flushPromises()

    const html = wrapper.html()
    // 92% should be success
    expect(html).toContain('attendance--success')
    // 72% should be warning
    expect(html).toContain('attendance--warning')
    // 55% should be error
    expect(html).toContain('attendance--error')
  })
})

describe('StudentDetailPanel', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getStudentDetail.mockResolvedValue(mockStudentDetail)
  })

  it('renders attendance history chart and assessment marks table', async () => {
    const wrapper = mount(StudentDetailPanel, {
      props: { student: 'EDU-STU-001', course: 'CS201' },
    })
    await flushPromises()

    const text = wrapper.text()
    // Should show assessment marks
    expect(text).toContain('IA-1')
    expect(text).toContain('78')
    // Should have chart wrapper
    expect(wrapper.find('.chart-wrapper').exists()).toBe(true)
  })
})

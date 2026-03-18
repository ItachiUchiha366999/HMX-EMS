import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockStudentLeaveRequests } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

import StudentLeaveQueue from '../StudentLeaveQueue.vue'

describe('StudentLeaveQueue', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getStudentLeaveRequests.mockResolvedValue(mockStudentLeaveRequests)
  })

  it('renders DataTable with student name, dates, reason, approve/reject buttons', async () => {
    const wrapper = mount(StudentLeaveQueue)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Arun Kumar')
    expect(text).toContain('Family function')
    expect(text).toContain('Approve')
    expect(text).toContain('Reject')
  })

  it('clicking "Approve" calls approveStudentLeave with correct name', async () => {
    const wrapper = mount(StudentLeaveQueue)
    await flushPromises()

    const approveBtn = wrapper.findAll('.btn-approve')[0]
    await approveBtn.trigger('click')
    await flushPromises()

    expect(mockApi.approveStudentLeave).toHaveBeenCalledWith('SLA-001')
  })

  it('clicking "Reject" shows inline reason input + "Confirm Reject" button', async () => {
    const wrapper = mount(StudentLeaveQueue)
    await flushPromises()

    const rejectBtn = wrapper.findAll('.btn-reject')[0]
    await rejectBtn.trigger('click')

    expect(wrapper.text()).toContain('Confirm Reject')
    expect(wrapper.find('.reject-reason-input').exists()).toBe(true)
  })

  it('multi-select + "Approve Selected" calls approveStudentLeave for each selected', async () => {
    const wrapper = mount(StudentLeaveQueue)
    await flushPromises()

    // Select checkboxes
    const checkboxes = wrapper.findAll('.student-leave-checkbox')
    await checkboxes[0].setValue(true)
    await checkboxes[1].setValue(true)

    const bulkBtn = wrapper.find('.btn-approve-selected')
    expect(bulkBtn.text()).toContain('Approve Selected')
    await bulkBtn.trigger('click')
    await flushPromises()

    expect(mockApi.approveStudentLeave).toHaveBeenCalledTimes(2)
  })

  it('shows "No pending requests" empty state when no data', async () => {
    mockApi.getStudentLeaveRequests.mockResolvedValue({ data: [], total_count: 0 })
    const wrapper = mount(StudentLeaveQueue)
    await flushPromises()

    expect(wrapper.text()).toContain('No pending requests')
    expect(wrapper.text()).toContain('There are no student leave requests awaiting your approval.')
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockLeaveBalance } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

import LeaveBalanceCards from '../LeaveBalanceCards.vue'

describe('LeaveBalanceCards', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getLeaveBalance.mockResolvedValue(mockLeaveBalance)
  })

  it('renders 3 KpiCard-style cards with leave type, used/total value', async () => {
    const wrapper = mount(LeaveBalanceCards)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Casual Leave')
    expect(text).toContain('4 / 12')
    expect(text).toContain('Medical Leave')
    expect(text).toContain('3 / 10')
    expect(text).toContain('Earned Leave')
    expect(text).toContain('15 / 20')
  })

  it('shows progress bar with color coding (green < 75%, warning 75-90%, red > 90%)', async () => {
    const wrapper = mount(LeaveBalanceCards)
    await flushPromises()

    const progressBars = wrapper.findAll('.leave-progress-fill')
    expect(progressBars.length).toBe(3)

    // Casual Leave: 4/12 = 33% -> green (success)
    expect(progressBars[0].classes()).toContain('leave-progress-fill--success')
    // Medical Leave: 3/10 = 30% -> green (success)
    expect(progressBars[1].classes()).toContain('leave-progress-fill--success')
    // Earned Leave: 15/20 = 75% -> warning
    expect(progressBars[2].classes()).toContain('leave-progress-fill--warning')
  })

  it('"Apply for Leave" button triggers apply event', async () => {
    const wrapper = mount(LeaveBalanceCards)
    await flushPromises()

    const btn = wrapper.find('.btn-primary')
    expect(btn.text()).toContain('Apply for Leave')

    await btn.trigger('click')
    expect(wrapper.emitted('apply')).toBeTruthy()
  })
})

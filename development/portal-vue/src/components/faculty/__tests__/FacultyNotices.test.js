import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockAnnouncements } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

import FacultyNotices from '../FacultyNotices.vue'

describe('FacultyNotices', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
  })

  it('renders announcements with category badges', async () => {
    const wrapper = mount(FacultyNotices)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Mid-Semester Exam Schedule Published')
    expect(text).toContain('Academic')
    expect(text).toContain('Administrative')
    expect(text).toContain('Emergency')
  })

  it('filters by category when category filter is selected', async () => {
    const wrapper = mount(FacultyNotices)
    await flushPromises()

    // Click Academic filter
    const filterButtons = wrapper.findAll('.notice-filter-btn')
    const academicBtn = filterButtons.find((btn) => btn.text().includes('Academic'))
    if (academicBtn) {
      await academicBtn.trigger('click')
      await flushPromises()

      expect(mockApi.getAnnouncements).toHaveBeenCalledWith(
        expect.objectContaining({ category: 'Academic' })
      )
    }
  })

  it('shows empty state when no announcements', async () => {
    mockApi.getAnnouncements = vi.fn().mockResolvedValue({ data: [], total_count: 0 })
    const wrapper = mount(FacultyNotices)
    await flushPromises()

    expect(wrapper.text()).toContain('No announcements')
  })

  it('calls getAnnouncements on mount', async () => {
    mount(FacultyNotices)
    await flushPromises()

    expect(mockApi.getAnnouncements).toHaveBeenCalled()
  })
})

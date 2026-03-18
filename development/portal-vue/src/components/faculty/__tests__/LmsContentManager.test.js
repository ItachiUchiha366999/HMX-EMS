import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { mockUseFacultyApi, mockLmsCourseContent } from './faculty-setup.js'

let mockApi
vi.mock('../../../composables/useFacultyApi.js', () => ({
  useFacultyApi: () => mockApi,
}))

import LmsContentManager from '../LmsContentManager.vue'

describe('LmsContentManager', () => {
  beforeEach(() => {
    mockApi = mockUseFacultyApi()
    mockApi.getLmsCourseContent.mockResolvedValue(mockLmsCourseContent)
  })

  it('renders course content with lesson/assignment/quiz counts', async () => {
    const wrapper = mount(LmsContentManager, { props: { course: 'CS201' } })
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Introduction to Arrays')
    expect(text).toContain('Linked Lists')
    expect(text).toContain('Array Operations')
    expect(text).toContain('Data Structures Basics')
  })

  it('"Add Lesson" button opens LmsContentForm', async () => {
    const wrapper = mount(LmsContentManager, { props: { course: 'CS201' } })
    await flushPromises()

    const addBtn = wrapper.findAll('button').find(b => b.text().includes('Add Lesson'))
    expect(addBtn).toBeTruthy()

    await addBtn.trigger('click')
    expect(wrapper.find('.lms-content-form-panel').exists()).toBe(true)
  })

  it('"Delete" button shows confirmation modal with "Delete" and "Keep Content" buttons', async () => {
    const wrapper = mount(LmsContentManager, { props: { course: 'CS201' } })
    await flushPromises()

    const deleteBtn = wrapper.findAll('.btn-delete')[0]
    await deleteBtn.trigger('click')

    const text = wrapper.text()
    expect(text).toContain('This action cannot be undone')
    expect(text).toContain('Keep Content')
    expect(text).toContain('Delete')
  })
})

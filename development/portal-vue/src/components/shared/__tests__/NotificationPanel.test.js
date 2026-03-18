import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NotificationPanel from '../NotificationPanel.vue'

const sampleItems = [
  { id: 1, title: 'Grade Posted', body: 'Math 101', read: false, timestamp: '2h ago', category: 'grade' },
  { id: 2, title: 'Assignment Due', body: 'CS 201 Lab', read: true, timestamp: '5h ago', category: 'assignment' },
]

describe('NotificationPanel', () => {
  it('renders notification items from items prop', () => {
    const wrapper = mount(NotificationPanel, {
      props: { items: sampleItems },
    })
    expect(wrapper.text()).toContain('Grade Posted')
    expect(wrapper.text()).toContain('Math 101')
    expect(wrapper.text()).toContain('Assignment Due')
  })

  it('shows unread indicator for unread items', () => {
    const wrapper = mount(NotificationPanel, {
      props: { items: sampleItems },
    })
    const unreadItems = wrapper.findAll('.notification-item--unread')
    expect(unreadItems.length).toBe(1)
  })

  it('emits dismiss event with item id when dismissed', async () => {
    const wrapper = mount(NotificationPanel, {
      props: { items: sampleItems },
    })
    const dismissBtns = wrapper.findAll('.notification-item button')
    expect(dismissBtns.length).toBeGreaterThan(0)
    await dismissBtns[0].trigger('click')
    expect(wrapper.emitted('dismiss')).toBeTruthy()
    expect(wrapper.emitted('dismiss')[0][0]).toBe(1)
  })

  it('emits mark-all-read event when Mark all read clicked', async () => {
    const wrapper = mount(NotificationPanel, {
      props: { items: sampleItems },
    })
    const markAllBtn = wrapper.findAll('button').find(b => b.text().includes('Mark all read'))
    expect(markAllBtn).toBeDefined()
    await markAllBtn.trigger('click')
    expect(wrapper.emitted('mark-all-read')).toBeTruthy()
  })

  it('shows empty state when items array is empty', () => {
    const wrapper = mount(NotificationPanel, {
      props: { items: [] },
    })
    expect(wrapper.text()).toContain('All caught up')
  })
})

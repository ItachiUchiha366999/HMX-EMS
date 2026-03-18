import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import KpiCard from '../KpiCard.vue'
import SkeletonLoader from '../SkeletonLoader.vue'

describe('KpiCard', () => {
  it('renders value and label from props', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'Attendance', value: '92%', trend: 12.5, status: 'good', icon: 'groups' },
    })
    expect(wrapper.text()).toContain('Attendance')
    expect(wrapper.text()).toContain('92%')
    expect(wrapper.text()).toContain('+12.5%')
  })

  it('shows trend arrow icon based on trend prop', () => {
    const up = mount(KpiCard, {
      props: { label: 'Test', value: '100', trend: 5.2, status: 'good' },
    })
    expect(up.text()).toContain('trending_up')

    const down = mount(KpiCard, {
      props: { label: 'Test', value: '100', trend: -5.2, status: 'critical' },
    })
    expect(down.text()).toContain('trending_down')

    const flat = mount(KpiCard, {
      props: { label: 'Test', value: '100', trend: 0, status: 'warning' },
    })
    expect(flat.text()).toContain('trending_flat')
  })

  it('applies status color class based on status prop', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'Test', value: '100', trend: 0, status: 'good' },
    })
    expect(wrapper.find('.kpi-card--good').exists()).toBe(true)

    const critical = mount(KpiCard, {
      props: { label: 'Test', value: '100', trend: -1, status: 'critical' },
    })
    expect(critical.find('.kpi-card--critical').exists()).toBe(true)
  })

  it('shows skeleton when loading prop is true', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'Test', value: '100', loading: true },
    })
    expect(wrapper.findComponent(SkeletonLoader).exists()).toBe(true)
    expect(wrapper.find('.stat-value').exists()).toBe(false)
  })

  it('renders icon in tinted background', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'Test', value: '100', status: 'good', icon: 'groups' },
    })
    const iconArea = wrapper.find('.stat-icon')
    expect(iconArea.exists()).toBe(true)
    expect(iconArea.text()).toContain('groups')
  })
})
